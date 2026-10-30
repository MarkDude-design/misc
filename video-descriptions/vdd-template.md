# VDD: {{VIDEO_NAME}}

## Provenance (receipts-first)
- source: {{VIDEO_PATH_OR_URL}}
- sha256: {{SHA256_FROM_META_JSON}}
- extracted: {{DATE_UTC}} by extract.py v0.1
- describe route(s) used: {{GEMINI_VIDEO | OR_VIDEO | FRAMES_ONLY}} — model: {{MODEL_NAME}}
- pose lane: {{OK_N_FRAMES | HONEST_NULL_REASON}}

## What this video is (plain paragraph, no interpretation yet)
{{ONE_PARAGRAPH_FACTS}}

## Visual timeline (timestamped)
| time | what moves | notes |
|------|-----------|-------|
| 0:00–0:08 | {{...}} | {{...}} |

## Motion transcript (from motion-summary.md — deterministic ground truth)
{{PASTE_OR_LINK_MOTION_SUMMARY}}

## Move inventory (the point of the exercise)
Name each dance move, when it happens, and HOW to do it — written so a
reader who has never seen the video could perform it:
- {{MM:SS}} — {{MOVE_NAME}}: {{body positions, direction, level, weight, timing}}

## Audio (BONUS lane — null is fine)
- transcript: {{... | null: reason}}
- beat grid: {{BPM + downbeat times | null: reason}}

## Honest nulls
{{WHAT_COULD_NOT_BE_EXTRACTED_AND_WHY — from meta.json lanes}}

## Open questions for the next seat
- {{...}}
