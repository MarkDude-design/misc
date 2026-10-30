#!/usr/bin/env python3
"""
describe_or.py — Route B describe pass via OpenRouter (video_url, base64).
v0.1 prototype grade.

Stdlib only (no pip). Called by .github/workflows/describe-video.yml or standalone:

  export OPENROUTER_API_KEY=sk-or-v1-THIS-IS-FAKE-REPLACE-ME-0000000000
  python describe_or.py --video clip.mp4 --model qwen/qwen3-vl-plus --out out/

Writes out/describe-draft.md (model's VDD draft) + out/describe-receipt.json
(provenance + usage). Every failure is an honest null written to the receipt
and exit 0 — CI still publishes Layer 1; nothing crashes into a silent skip.
"""
import argparse
import base64
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_B64 = 28 * 1024 * 1024  # base64 guard — trim clips instead of pushing walls

# Mirrors describe-prompts.md "shared system prompt" (motion-first bias).
SYSTEM_PROMPT = (
    "You are analyzing a dance/motion video. SOUND IS OPTIONAL: if audio is "
    "present treat it as bonus context; your primary job is MOTION. Describe: "
    "(1) a plain paragraph of what happens; (2) a timestamped timeline; "
    "(3) each distinct movement/move, named, with instructions detailed enough "
    "that a person who has never seen the video could perform it (body part, "
    "direction, level, weight shift, speed). Do not interpret music unless "
    "nothing else is available. Say 'unknown' rather than guessing."
)


def write_receipt(out: Path, receipt: dict) -> None:
    (out / "describe-receipt.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Route B describe pass (OpenRouter video)")
    ap.add_argument("--video", required=True, type=Path)
    ap.add_argument("--model", default="qwen/qwen3-vl-plus",
                    help="video-capable OpenRouter model (filter models page by video modality)")
    ap.add_argument("--out", default=Path("out"), type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    receipt = {
        "tool": "describe_or.py v0.1",
        "route": "B — OpenRouter video_url (base64)",
        "model": args.model,
        "video": str(args.video),
        "utc": datetime.now(timezone.utc).isoformat(),
    }

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        receipt["status"] = "null: OPENROUTER_API_KEY not set (button ships dark until secret exists)"
        write_receipt(args.out, receipt)
        print(json.dumps(receipt, indent=2))
        sys.exit(0)

    raw = args.video.read_bytes()
    b64 = base64.b64encode(raw).decode()
    receipt["video_bytes"] = len(raw)
    receipt["b64_bytes"] = len(b64)
    if len(b64) > MAX_B64:
        receipt["status"] = (
            f"null: clip too large for base64 lane ({len(b64)} B > {MAX_B64} B) — trim with max_seconds")
        write_receipt(args.out, receipt)
        print(json.dumps(receipt, indent=2))
        sys.exit(0)

    payload = {
        "model": args.model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": SYSTEM_PROMPT},
                {"type": "video_url",
                 "video_url": {"url": "data:video/mp4;base64," + b64}},
            ],
        }],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = body["choices"][0]["message"]["content"]
        (args.out / "describe-draft.md").write_text(text, encoding="utf-8")
        receipt["status"] = "ok"
        receipt["draft_bytes"] = len(text.encode("utf-8"))
        receipt["usage"] = body.get("usage")  # tokens; OR cost shows on the key meter
    except Exception as e:  # noqa: BLE001 — honest null, never a silent skip
        receipt["status"] = "null: " + repr(e)[:300]
    write_receipt(args.out, receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
