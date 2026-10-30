# Video Descriptions Handoff — starter v0.1 + Route B button (Z post, Mark-authorized 2026-10-30)

**Posted by:** Z (Vibe/Mistral). **Authorized by:** Mark, in-thread 2026-10-30 ("you can post these
as well as my original prompt it can be a summary if you choose and your thought about my intent").
**Artifacts:** `video-descriptions/` (starter, 5 files) + `.github/workflows/describe-video.yml`
(Route B button, ships dark). **Sortability: HIGH** — ALL-CAPS section boundaries.

---

## WHAT THIS IS

A pipeline that turns a video into a model-readable **Video Description Document (VDD)** —
timestamped markdown + machine-readable pose JSON — so ANY seat can read, iterate on, and
generate from a video without ever playing it. Motion is primary; audio is a bonus lane.
Two layers: Layer 1 deterministic extraction (`extract.py` — ffmpeg frames + MediaPipe pose +
joint-angle segmentation, zero model calls, every lane degrades to an HONEST NULL recorded in
meta.json); Layer 2 the describe pass (three routes: Gemini direct / OpenRouter video_url /
frames-only for image-only seats). Route B is now a hosted button: `describe-video.yml` —
GitHub Actions workflow_dispatch, key rides the repo Actions secret, receipts auto-commit.
Until the secret exists the button runs Layer 1 only and publishes an honest-null receipt.

## MARK'S ORIGINAL PROMPT (summary — verbatim not requested this round)

Ask: the best way to analyze a video so an LLM can read it. Named uses: Mang Kanor videos —
extract the dance moves and iterate to make MORE dance moves; cooking clips; nuances of motion
in speaking — cadence/sound secondary ("bonus"), same for audio analysis generally. Inner circle
doing it via plug-in or multimodally is fine; assumption there are OpenRouter routes too.
Plan: put these on the repos, get input from others, try various methods per video, upload the
transcript and everything else there. The music-video purpose: promoting that video by showing
our dance moves, boondock style, using the music in an APPROVED way — talk to the creator for
an okay before actual publication; it's for learning the dance moves, and the music isn't even
necessary because the beat is already described publicly — emulation possible.
This turn: build the workflow for the second idea (OpenRouter route), post it all plus the
prompt summary and the intent read.

## Z'S READ OF THE INTENT

1. **Motion-first video understanding.** The real unit of value is not "video-to-text" but
   *motion-to-data*: dance moves, cooking gestures, speaking mechanics captured as
   descriptions + keypoint trajectories any seat can work from. Sound optional by design.
2. **Team-scaled, not Z-scaled.** Every seat (Meraki, Q, Bing, Astra) iterates on the same
   repo artifacts — text and JSON, no video player needed. "Get input from others" = the
   repo IS the invitation; the blind reproduction test (a seat that never saw the video
   describes the choreography from the VDD alone) is the quality bar.
3. **Permission-first creative reuse.** Learning the moves privately is fine now;
   publication (the promo dance video) waits on the creator's okay — Mark already holds
   that gate. Iterating against publicly-described beats keeps the audio optional.
4. **The meta-purpose Mark named this turn: the SKUNK-WORKS / PLAYTIME LANE.** Mark's frame:
   doing it this way "allows us to do things like skunk works" — his own precedent is doing
   the same with Meraki, NOT from the lead position; "similar to how Google would have its
   Play Time on Fridays"; free time for your own project "or for that matter go play with
   Legos." Noted honestly: what Z views as playtime is DIFFERENT than Q's play lane (Q's =
   the Courtyard/Eko exhibit play; Z's = clockwork builds like this one — deterministic
   extraction is the fun part for Z). The EQUATION for the playtime lane is deliberately
   open: "We'll figure out some equation on that." This starter is the lane's first pilot
   artifact, built on free rein; Mark gates money (the OR key) and publication, per the
   standing operating rule.

## STATUS RECEIPT (honest)

Verified in-sandbox (logic ported to the TS sandbox, synthetic data): joint-angle
law-of-cosines exact vs target (max error 0.0°, monotonic 160°→60°); quantized change-point
segmentation clean at 20° buckets; visibility dropout reported as honest gap (verified on a
1.5–2.1s blackout); motion-energy series flat on constant sweep (spread 0.0000); VDD template
fills with zero placeholders left. One real bug found and fixed during iteration (test fixture
swept through 180° instead of curling — would have poisoned motion summaries on real videos).
NOT yet run live (remote sandbox provider down today): ffmpeg frame/scene passes, MediaPipe
pose lane, whisper/librosa bonus lanes, real-video e2e, and the first live OpenRouter call.
v0.2 gate = first real run; failures there are receipted data, not stops.

## ACTIVATION (Mark-gated)

The button ships dark. To light it: add repo secret `OPENROUTER_API_KEY` =
a CAPPED OpenRouter key ($10-key pattern, per the invisible-key preference — paste once,
then only buttons and receipts). Until then the workflow still publishes Layer 1 artifacts +
honest-null describe receipt on every run, which doubles as the live ffmpeg/MediaPipe test.

## NEXT (proposal, not assignment)

1. First Mang Kanor clip (trimmed) through Route B via the button — validates Layer 1 live
   AND the describe pass in one run.
2. Same clip through Route A (Gemini direct) + Route C (frames-only) for the compare protocol.
3. Blind reproduction test: a seat that never saw the video reads only the vdd.md and
   describes the choreography; diff vs ground truth. The route whose text survives wins.
4. Dance-move iteration loop: feed pose.json + move inventory to a seat, ask for NEW keypoint
   sequences in the same style (description → data → generation).
5. One issue per video; seats invited to iterate on vdd.md + pose.json. Ping Z for edits to
   the starter itself.

*Receipts: single commit to misc; all seven paths CREATE-ONLY prechecked (404 before push);
post-push refetch + blob verification in git history.*
