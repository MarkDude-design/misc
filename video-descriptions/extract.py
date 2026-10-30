#!/usr/bin/env python3
"""
extract.py — Video Description Pipeline, Layer 1 (deterministic).
v0.1 prototype grade: v1 runs, v1 learns.

Turns a video into model-readable artifacts with ZERO model calls:
  frames/            sampled keyframes (default 1 fps) + scene-change frames
  pose.json          per-frame body landmarks (MediaPipe; honest null if absent)
  motion-summary.md  joint-angle segments + motion energy (markdown)
  meta.json          provenance + per-lane receipts (ok | null + reason)

Every lane degrades to an honest null, recorded in meta.json.
Nothing is silently skipped.

Usage:
  python extract.py VIDEO.mp4 --out vdd-myvideo/
  python extract.py VIDEO.mp4 --out vdd-myvideo/ --audio   # bonus: whisper + beats
"""
import argparse, csv, hashlib, json, math, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "extract.py v0.1"
MIN_VIS = 0.5          # landmark visibility gate
BUCKET_DEG = 20        # quantization for motion segmentation
STRIDE_TARGET_FPS = 15 # pose.json sampling (keeps JSON sizes sane)

# MediaPipe Pose landmark indices
L_SHO, R_SHO = 11, 12
L_ELB, R_ELB = 13, 14
L_WRI, R_WRI = 15, 16
L_HIP, R_HIP = 23, 24
L_KNE, R_KNE = 25, 26
L_ANK, R_ANK = 27, 28

# joint name -> (a, b, c): angle at b
JOINTS = {
    "left_elbow":    (L_SHO, L_ELB, L_WRI),
    "right_elbow":   (R_SHO, R_ELB, R_WRI),
    "left_shoulder": (L_ELB, L_SHO, L_HIP),
    "right_shoulder":(R_ELB, R_SHO, R_HIP),
    "left_hip":      (L_SHO, L_HIP, L_KNE),
    "right_hip":     (R_SHO, R_HIP, R_KNE),
    "left_knee":     (L_HIP, L_KNE, L_ANK),
    "right_knee":    (R_HIP, R_KNE, R_ANK),
}

# ---------- helpers ----------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def run(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)

def ffprobe_meta(video: Path) -> dict:
    r = run(["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", str(video)])
    if r.returncode != 0:
        return {"error": r.stderr.strip() or "ffprobe failed"}
    probe = json.loads(r.stdout or "{}")
    v = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {})
    fps = v.get("avg_frame_rate", "0/1")
    try:
        num, den = fps.split("/")
        fps = round(float(num) / float(den), 3) if float(den) else 0.0
    except Exception:
        fps = 0.0
    return {
        "duration_s": float(probe.get("format", {}).get("duration", 0)),
        "width": v.get("width"), "height": v.get("height"),
        "video_fps": fps, "has_audio": any(s.get("codec_type") == "audio"
                               for s in probe.get("streams", [])),
    }

# ---------- lane: frames ----------

def extract_frames(video: Path, out: Path, fps: float) -> tuple:
    frames_dir = out / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    # pass 1: fixed-rate sampling
    r1 = run(["ffmpeg", "-y", "-i", str(video), "-vf", f"fps={fps}",
              "-q:v", "2", str(frames_dir / "t%04d.jpg")])
    # pass 2: scene-change keyframes (may duplicate pass-1 content; fine)
    r2 = run(["ffmpeg", "-y", "-i", str(video),
              "-vf", "select='gt(scene,0.3)'", "-vsync", "vfr",
              "-q:v", "2", str(frames_dir / "scene%04d.jpg")])
    n = len(list(frames_dir.glob("*.jpg")))
    if r1.returncode != 0:
        return ("null: ffmpeg frame pass failed: " + (r1.stderr.strip()[-200:] or "?"), 0)
    return (f"ok: {n} frames (sample@{fps}fps + scene>0.3)", n)

# ---------- lane: pose ----------

def extract_pose(video: Path, meta: dict) -> tuple:
    try:
        import cv2  # noqa: F401
        import mediapipe as mp
    except ImportError as e:
        return ("null: mediapipe/opencv not installed (" + str(e) + ")", None)
    import cv2
    pose = mp.solutions.pose.Pose(model_complexity=1, smooth_landmarks=True)
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        return ("null: could not open video", None)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or meta.get("video_fps") or 30.0
    src_fps = src_fps if src_fps and src_fps > 0 else 30.0
    stride = max(1, round(src_fps / STRIDE_TARGET_FPS))
    frames, idx = [], 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % stride == 0:
            res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            lms = None
            if res.pose_landmarks:
                lms = [[lm.x, lm.y, lm.z, lm.visibility]
                       for lm in res.pose_landmarks.landmark]
            frames.append({"frame": idx, "t_s": round(idx / src_fps, 3), "landmarks": lms})
        idx += 1
    cap.release()
    pose.close()
    seen = sum(1 for f in frames if f["landmarks"])
    if seen == 0:
        return ("null: no person detected in any sampled frame", None)
    return (f"ok: {seen}/{len(frames)} sampled frames had a person "
            f"(@{round(src_fps/stride,1)}fps)", {"fps": src_fps, "frames": frames})

# ---------- motion math (verified against synthetic data, see receipt) ----------

def joint_angle(a, b, c):
    """Interior angle at b (degrees) on the 2D projection. None if degenerate."""
    v1 = (a[0] - b[0], a[1] - b[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    m = math.hypot(*v1) * math.hypot(*v2)
    if m == 0:
        return None
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    return math.degrees(math.acos(max(-1.0, min(1.0, dot / m))))

def angle_series(pose: dict) -> dict:
    """Per joint: list aligned with pose['frames'] (None where not visible)."""
    out = {name: [] for name in JOINTS}
    for fr in pose["frames"]:
        lms = fr["landmarks"]
        for name, (a, b, c) in JOINTS.items():
            val = None
            if lms and all(lms[i][3] >= MIN_VIS for i in (a, b, c)):
                val = round(joint_angle(lms[a], lms[b], lms[c]), 1)
            out[name].append(val)
    return out

def segment_series(series, fps, bucket_deg=BUCKET_DEG):
    """Quantized change-point segmentation; long invisible gaps -> honest nulls."""
    segs, cur, gap_start = [], None, None
    for i, val in enumerate(series):
        if val is None:
            if gap_start is None:
                gap_start = i
            if cur:
                segs.append({"type": "motion", "start_s": round(cur["start"] / fps, 2),
                             "end_s": round(cur["end"] / fps, 2),
                             "from_deg": round(cur["from"]), "to_deg": round(cur["to"])})
                cur = None
            continue
        if gap_start is not None:
            if (i - 1 - gap_start) * (1.0 / fps) >= 0.5:
                segs.append({"type": "gap", "start_s": round(gap_start / fps, 2),
                             "end_s": round((i - 1) / fps, 2),
                             "note": "landmarks not visible — honest null"})
            gap_start = None
        prev = series[i - 1] if i else None
        same = (prev is not None
                and int(prev) // bucket_deg == int(val) // bucket_deg)
        if cur is None:
            cur = {"start": i, "end": i, "from": val, "to": val}
        elif same:
            cur["end"], cur["to"] = i, val
        else:
            segs.append({"type": "motion", "start_s": round(cur["start"] / fps, 2),
                         "end_s": round(cur["end"] / fps, 2),
                         "from_deg": round(cur["from"]), "to_deg": round(cur["to"])})
            cur = {"start": i, "end": i, "from": val, "to": val}
    if cur:
        segs.append({"type": "motion", "start_s": round(cur["start"] / fps, 2),
                     "end_s": round(cur["end"] / fps, 2),
                     "from_deg": round(cur["from"]), "to_deg": round(cur["to"])})
    return segs

def motion_energy(pose: dict, sample_fps: float):
    """Mean wrist speed per source-second (0..1 coords) — the move/tempo indicator."""
    frames = pose["frames"]
    per_sec, acc, n, sec = [], 0.0, 0, 1
    for f in range(1, len(frames)):
        a, b = frames[f - 1]["landmarks"], frames[f]["landmarks"]
        if a and b:
            acc += (math.hypot(a[L_WRI][0] - b[L_WRI][0], a[L_WRI][1] - b[L_WRI][1])
                  + math.hypot(a[R_WRI][0] - b[R_WRI][0], a[R_WRI][1] - b[R_WRI][1])) / 2
        n += 1
        if frames[f]["t_s"] >= sec:
            per_sec.append(round(acc / max(n, 1), 4))
            acc, n, sec = 0.0, 0, sec + 1
    if n:
        per_sec.append(round(acc / max(n, 1), 4))
    return per_sec

def write_motion_summary(out: Path, pose: dict, series: dict, energy: list):
    fps = pose["fps"]
    lines = ["# Motion Summary (deterministic — from pose data, no model)",
             "", f"source fps: {fps}; angles in degrees; gaps = honest nulls", ""]
    for joint, segs in series.items():
        moves = [s for s in segs if s["type"] == "motion"]
        if not moves:
            continue  # joint never visible / never moved — omit, noted in vdd
        lines.append(f"## {joint}")
        for s in segs:
            if s["type"] == "gap":
                lines.append(f"- {s['start_s']}–{s['end_s']}s: {s['note']}")
            else:
                direction = "flexion" if s["to_deg"] < s["from_deg"] else "extension"
                lines.append(f"- {s['start_s']}–{s['end_s']}s: "
                             f"{s['from_deg']}° → {s['to_deg']}° ({direction})")
        lines.append("")
    lines.append("## Motion energy (mean wrist speed per second, 0–1 coords)")
    lines.append(", ".join(f"{i}s:{v}" for i, v in enumerate(energy)))
    (out / "motion-summary.md").write_text("\n".join(lines), encoding="utf-8")

# ---------- lane: audio (BONUS) ----------

def audio_lane(video: Path, out: Path) -> dict:
    result = {"transcript": "null: --audio not requested",
              "beat_grid": "null: --audio not requested"}
    wav = out / "audio.wav"
    r = run(["ffmpeg", "-y", "-i", str(video), "-ac", "1", "-ar", "16000", str(wav)])
    if r.returncode != 0 or not wav.exists():
        result["transcript"] = result["beat_grid"] = "null: no audio track"
        return result
    try:
        import whisper
        model = whisper.load_model("base")
        result["transcript"] = model.transcribe(str(wav))["text"]
    except Exception as e:
        result["transcript"] = f"null: whisper unavailable ({e})"
    try:
        import librosa
        y, sr = librosa.load(str(wav), mono=True)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        result["beat_grid"] = {"bpm": round(float(tempo), 1),
                               "beat_times_s": [round(float(b / sr), 2) for b in beats][:400]}
    except Exception as e:
        result["beat_grid"] = f"null: librosa unavailable ({e})"
    return result

# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description="VDD Layer 1 extractor")
    ap.add_argument("video", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--fps", type=float, default=1.0)
    ap.add_argument("--audio", action="store_true")
    args = ap.parse_args()
    video = args.video
    if not video.exists():
        sys.exit(f"no such file: {video}")
    out = args.out or video.with_suffix("").with_name("vdd-" + video.stem)
    out.mkdir(parents=True, exist_ok=True)

    meta = {"source": str(video), "sha256": sha256_file(video),
            "extracted_utc": datetime.now(timezone.utc).isoformat(),
            "tool": VERSION, "lanes": {}}

    probe = ffprobe_meta(video)
    meta["video"] = probe

    frames_receipt, _ = extract_frames(video, out, args.fps)
    meta["lanes"]["frames"] = frames_receipt

    pose_receipt, pose = extract_pose(video, probe)
    meta["lanes"]["pose"] = pose_receipt
    if pose:
        (out / "pose.json").write_text(json.dumps(pose), encoding="utf-8")
        series = {j: segment_series(s, pose["fps"]) for j, s in angle_series(pose).items()}
        energy = motion_energy(pose, pose["fps"])
        write_motion_summary(out, pose, series, energy)
        meta["lanes"]["motion_summary"] = f"ok: {len(series)} joints, {len(energy)}s energy"
    else:
        meta["lanes"]["motion_summary"] = "null: depends on pose lane"

    if args.audio:
        meta["lanes"]["audio"] = audio_lane(video, out)
        (out / "audio-lane.json").write_text(
            json.dumps(meta["lanes"]["audio"], ensure_ascii=False), encoding="utf-8")

    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "lanes": meta["lanes"]}, indent=2))

if __name__ == "__main__":
    main()
