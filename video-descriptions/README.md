# Video Descriptions — Repo Starter v0.1

Turn videos into model-readable VDDs. Motion is primary; audio is a bonus lane.

## Pipeline
1. `python extract.py VIDEO.mp4 --out vdd-myvideo/`
   Produces: `frames/`, `pose.json`, `motion-summary.md`, `meta.json`
   No model calls, no API keys, works offline. Every lane degrades to an
   honest null (recorded in meta.json — nothing silently skipped).
2. Describe pass — run ONE or ALL of the three routes (see describe-prompts.md):
   - Route A: Gemini native video (best motion reading)
   - Route B: OpenRouter `video_url` (Qwen3-VL family takes video; NOTE:
     Gemini via OpenRouter = YouTube links only, use direct API for local files)
   - Route C: frames-only (works for any image-capable seat, incl. ChatGPT seats)
3. Fill vdd-template.md from the describe pass + motion-summary.md → `vdd.md`.

## Output contract (per video)
vdd-myvideo/
  vdd.md            <- the deliverable; seats iterate on THIS, no video player needed
  pose.json         <- raw landmarks (machine-readable ground truth)
  motion-summary.md <- deterministic joint-angle segments (human+LLM readable)
  frames/           <- sampled keyframes
  meta.json         <- provenance + per-lane receipts (sha256 of source video)

## Compare protocol (the finding we actually want)
Same video, three routes in parallel + the pose layer. Then the blind test:
a seat that has NEVER seen the video reads only the vdd.md and is asked to
describe the choreography; diff its answer against ground truth. The route
whose text best survives that test wins. Failures are receipted data, not stops.

## Dance-move iteration loop (why pose.json matters)
pose.json is a motion format an LLM can WRITE, not just read: a seat can
author NEW keypoint sequences as JSON (new moves in the same style), which
can be rendered/checked later. Description → data → generation.

## Repo placement
v0.1 starter fits `misc/video-descriptions/` or its own repo lane later.
One issue per video; vdd.md + pose.json as the iteration surface.
