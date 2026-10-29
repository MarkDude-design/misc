# Q Residue — Courier Session / Multi-Model Wire

Date sorted: 2026-10-28
Source: ChatGPT thread about Meraki Courier v2.
Status: RESIDUE / PARTS BIN. Not an assignment.

## Qwen exchange preserved

Qwen's first strong design constraint for the wire was that it should not optimize for consensus. Qwen preferred a high-resolution map of how and why models diverge, and endorsed visible seams, compact provenance, PASS, and a shared `SPECIMEN.md` mutation protocol.

Qwen also wrote that the emergent “residue” was “the only data worth keeping.” Meraki disagreed: residue may be the most novel data, but preserved disagreement, failed influence, reversals, PASSes, convergence, and unchanged positions after exposure are also data. Preserve this as an unforced first disagreement rather than resolving it immediately.

## Technical observations from Courier v2

### Known successful behavior
- ChatGPT↔Qwen routing worked at least once.
- Courier switched browser tabs automatically.
- Message insertion into both continuing conversations worked.
- Qwen-side sending worked automatically in at least one run.
- ChatGPT-side auto-send did not always fire; manual Send was a cheap workaround.

### Later failure: selected tab not ready
Exact error observed:

`ERROR: A selected tab is not ready. Refresh both chat tabs after loading v2.`

`1. START: MODEL_LOOP; limit 6`

Likely narrow class: selected-tab readiness / content-script handshake / initialization state, not proof that routing itself was broken.

### Later failure: Qwen submission confirmation
Courier successfully sent “Does this still work Q?” to Qwen. Qwen visibly generated a normal response, then Courier opened the ChatGPT tab but stopped with:

`ERROR: qwen did not confirm submission. The loop stopped and will not retry.`

`1. START: MODEL_LOOP; limit 2`

Visible Qwen output included “Thinking completed” followed by a normal answer. This isolates a likely confirmation-detector/sensor failure rather than insertion or transport failure. Preserve the fail-safe: genuine uncertainty should stop rather than blindly retry. Smallest desired fix is to make successful response generation a reliable confirmation signal without redesigning working routing.

## Future adapters / experiments

- Bing / Microsoft Copilot should be treated as another site-specific adapter, not assumed to work merely because ChatGPT↔Qwen works.
- Do not touch the known-good extension merely to add a model picker during commissioning.
- Run one-round Bing test only after preserving a stable ChatGPT↔Qwen build.
- Track usage later; user explicitly deferred this until after the collaboration experiment was working.

## Experimental ideas worth handing to Q later

- private-before-social baseline
- leader rotation / leaderless runs
- shared specimen with one mutation per round
- telephone-game reconstruction
- harmless conceptual contagion test
- adversarial boundary test with a harmless explicit constraint
- measure non-change after exposure, not just consensus
