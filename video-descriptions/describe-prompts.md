# Describe Prompts — Layer 2 (the model passes)

## Shared system prompt (all routes — motion-first bias)
You are analyzing a dance/motion video. SOUND IS OPTIONAL: if audio is
present treat it as bonus context; your primary job is MOTION. Describe:
(1) a plain paragraph of what happens; (2) a timestamped timeline;
(3) each distinct movement/move, named, with instructions detailed enough
that a person who has never seen the video could perform it (body part,
direction, level, weight shift, speed). Do not interpret music unless
nothing else is available. Say "unknown" rather than guessing.

## Route A — Gemini direct (best native video reading)
Gemini accepts video files up to 2GB free / 20GB paid, references
timestamps, and lets you set a custom frame rate. Easiest: AI Studio UI
attach-the-mp4, paste the system prompt. API: Files API upload ->
generateContent with the video file reference.

## Route B — OpenRouter (video_url)
API only. Filter the models page for video input modality (Qwen3-VL
family supports video). Local files go base64. NOTE: Gemini via
OpenRouter accepts YouTube links only — for local files use Route A.
Concrete example (fake key, correct shape — replace before running):

  export OPENROUTER_API_KEY=sk-or-v1-THIS-IS-FAKE-REPLACE-ME-0000000000
  python - <<'EOF'
  import base64, json, os, requests
  key = os.environ["OPENROUTER_API_KEY"]          # pasted once, never in the file
  b64 = base64.b64encode(open("clip.mp4","rb").read()).decode()
  r = requests.post("https://openrouter.ai/api/v1/chat/completions",
      headers={"Authorization": f"Bearer {key}"},
      json={"model": "qwen/qwen3-vl-plus", "messages": [{"role": "user", "content": [
          {"type": "text", "text": "<paste the shared system prompt here>"},
          {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{b64}"}}
      ]}]})
  print(r.json()["choices"][0]["message"]["content"])
  EOF

## Route C — frames-only (any image-capable seat, incl. ChatGPT seats)
Upload the frames/ directory images (t####.jpg = 1 fps timeline,
scene####.jpg = scene changes) in order, plus motion-summary.md and the
system prompt. Frames + the deterministic summary together recover most
of what native video sees — that combination IS the ChatGPT-seat route.

## Iterate loop (dance moves)
After the VDD exists: feed pose.json + vdd.md move inventory to a seat
and ask for NEW keypoint sequences in the same style (new moves authored
as JSON). Render or verify later. Description -> data -> generation.
