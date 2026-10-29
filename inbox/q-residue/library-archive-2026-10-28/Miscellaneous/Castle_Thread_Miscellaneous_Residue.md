# Castle Thread — Miscellaneous Residue

Material worth preserving that is not yet a talk seed or active implementation requirement.

## Castle theater status

- Draft PR #19 created the first contained browser stage.
- Six scripted rooms are available.
- The stage uses existing JSON room and character material.
- Controls include character cues, scenery cues, joke reveal/advance, and a scripted Q aside.
- No live model calls, credentials, spending, deployment, saved performances, telemetry, or ledger changes were introduced.
- The implementation was deliberately treated as scaffolding rather than final visual design.
- Mark retains the merge gate.

## Architectural disposition

Retained:

- contained scripted theater;
- existing rooms and characters;
- explicit scripted/live distinction;
- language development before visual refinement;
- one-room-at-a-time writers' room;
- later visual and interaction pass.

Deferred:

- polished visual identity;
- animation;
- richer room-specific scenery;
- object hotspots;
- live model conversation;
- free-text input;
- saved performances;
- runtime orchestration;
- production deployment.

## Writers' room constraints sent toward Bing

- Start with the Courtyard only.
- Produce entrance copy, scenery interactions, character cues, multi-character exchanges, jokes, Q interruptions, and unused fragments.
- Preserve distinct character voices.
- Avoid generic “AI is quirky” humor.
- Avoid corporate chatbot voice.
- Preserve interesting failures and ambiguity.
- Mark new lore as optional.
- Stop after one room so Mark can shape the language before expansion.

## Visual judgment

Mark's judgment:

> Visuals suck; the goal is the words.

Interpretation:

- The current visuals are not accepted as a design direction.
- The interaction route is accepted.
- Visual dissatisfaction does not invalidate the underlying architecture.
- Do not spend current cycles polishing the provisional stage.

## Browser-test limitation

- Local browser scenarios were reported as passing.
- Browser testing was not part of hosted CI.
- Direct Windows `file://` opening remained unverified because the managed browser blocked local-file navigation.
- This was treated as a disclosed, nonblocking limitation for the first slice.

## Unusual-activity incident

Observed message:

> Unusual activity has been detected from your device. Try again later.

Reference ID:

`60d77e07-4445-4a3f-83a7-ef0d88877b98`

Observed effect:

- The first attempt appeared to fail.
- Retry sent the request again.
- Both attempts reached the assistant, producing duplicate prompt responses.

Practical note:

- Retrying an ambiguously failed request may duplicate the action.
- Preserve the reference ID if the warning repeats and support investigation is needed.

## Bishop Swing Lab residue

- Keep the computer lab mixed.
- Two machines become Fedora systems.
- Other systems remain according to community need.
- Fedora is a participant, not a replacement mandate.
- Funding requests may cover refurbished systems, repairs, peripherals, accessibility equipment, workshop materials, or small public activities.
- Do not promise sponsor or Fedora involvement before confirmation.
- Keep installation reversible until hardware and user needs are understood.
- Let actual use justify any larger role.

## Project Spiral residue

- Working branch: figure-eight paired organism.
- Promote paired control/disturbed organisms, impulse control, Mimic Detector, conservation diagnostics, and artifact-first review.
- Carton alternatives: Trojan/Lagrange organism, Lennard-Jones triangle, softened-gravity sandbox, multiple disturbances, automatic clustering, market overlay.
- Quarantine overstatements about indefinite stability, inevitable chaos, harmless softening, and exact escape thresholds.

## Useful process fragments

- Prototypes, not policies.
- Everything before reality checks may wear a wizard hat.
- The Expert should solve one chamber before being invited into the mythology.
- Preserve generative wildness; filter it externally.
- Extract observed behavior before writing model instructions.
- Reconcile facts before using them as test material.
- The smallest useful world should answer one experimental question.

## Archive status

This thread's most reusable active material has been separated into:

1. talk seeds;
2. miscellaneous residue;
3. an empty placeholder for future sorting.

