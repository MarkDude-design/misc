# Q handoff: Historical Panel wrapper

**For Q, from Mark / Meraki · 2026-10-09**

## Smallest useful description

We have a working **local Python inference engine with an optional stdio MCP
server**. It runs actual historical pretrained models, including BERT,
ALBERT, GPT-1/2 and others. A Match Game mode solicits native guesses; a
separate newly written symbolic routine inserts or repeats a word. We want
a thin wrapper that dispatches requests and normalizes results while keeping
the raw output and provenance. You do not need the full repository to propose
that wrapper. No credentials, private prompts, or account configuration are
included in this handoff. Nothing has been published for this review.

**Please build the wrapper around the existing functions; keep model loading
and task-specific framing in the existing engine.** Z will review next.

## 1. Execution surface — already implemented

- Python 3.11/3.12 source modules; not yet a packaged `pip install` project.
- Local CLI and importable functions. Optional local **MCP over stdio**.
- CPU default; CUDA is an explicit option on a compatible installation.
- PyTorch 2.8.0+cpu and Transformers 4.57.1 were used for recorded tests.
  MCP uses `mcp>=1.28,<2` and `mcp.server.fastmcp.FastMCP`.
- Each supervised model invocation launches a child Python process, loads
  one pinned checkpoint, returns JSON and exits. Batches currently run serially.
- Model weights are downloaded during explicit setup and cached. MCP inference
  is cache-only. Weights are not bundled with the source.
- No REST service, WebSocket, Docker image, cloud function, or hosted endpoint
  is implemented. None is necessary for the first wrapper.

From the extracted project directory, inside its installed environment:

```shell
python council.py run --ids bert --text "The chef stirred the soup with his <MASK>." --output results.jsonl
python mcp_server.py
```

The first command appends per-model results to JSONL; stdout is a batch summary,
and progress goes to stderr. Do not parse its stdout as per-model responses.
The second starts the MCP stdio server, not a human-oriented CLI.

The clean local integration point is:

```python
from council import invoke
result = invoke({
    "model_id": "bert",
    "text": "The chef stirred the soup with his <MASK>.",
    "allow_download": False,
}, timeout=120)
```

Use `invoke`, which supervises the child. The lower-level `run_model` function
does not supply timeout supervision.

## 2. Input contract — current engine

`invoke(request: dict, timeout=300) -> dict`

| Request field | Current behavior |
|---|---|
| `model_id` | Required registered ID, e.g. `bert`, `albert`, `gpt2`, `gptneo` |
| `text` | Single input string, 1–20,000 characters if supplied; omitted uses a smoke-test default. Wrapper should require explicit text. |
| `compare` | Optional second string for embedding similarity; engine otherwise uses a fixed default. Wrapper should require it for an intentional comparison. |
| `max_new_tokens` | Integer 1–128, default 32; generation only |
| `max_input_tokens` | Integer 8–512, default 128; also bounded by model context and generation capacity |
| `top_k` | Integer 1–20, default 5; masked candidate count / vector neighbor count, **not sampling top-k** |
| `seed` | Integer 0–2,147,483,647, default 0; passed to Torch; generation remains greedy |
| `device` | `cpu` or `cuda`, default `cpu`; unavailable CUDA fails |
| `allow_download` | Default false; keep false in the wrapper; setup handles downloads |
| `vector_file` | Local genuine vector-file path for vector adapters; not exposed by existing MCP tools |
| `timeout` | Separate `invoke` argument, 1–1800 seconds; not a request-dict field |

The model ID determines the task through `registry.json`. Checkpoint revisions
come from `checkpoints.lock.json`. There is no arbitrary model URL/ID override.
Unknown request fields are not comprehensively rejected by the engine; the
wrapper should reject them rather than imply that they work.

### Current MCP tools

```text
list_historical_models()
historical_model_input(model_id: str, text: str, compare: str | None = None)
match_game_panelist(model_id: str, premise: str, mode: str = "slot")
symbolic_stage_step(verb: str, noun: str, text: str)
```

The existing MCP model tools use CPU/cache-only inference and a 120-second
worker timeout. They do not expose every `invoke` parameter. Match Game fixes
`max_new_tokens=32` and `top_k=5`.

Example tool arguments:

```json
{
  "model_id": "albert",
  "premise": "The astronaut was so cheap, he used a <MASK> as a space helmet.",
  "mode": "slot"
}
```

- `slot`: exactly one `<MASK>`; masks go natively to masked models. Base
  decoders see the complete question plus `Answer:`. Supported old chat models
  get a short-answer instruction. Unsupported model/task combinations fail.
- `continue`: a literal prefix, with no blank needed; only base causal
  decoders are accepted. Maximum premise length is 4,000 characters.
- `symbolic_stage_step`: `INSERT` requires exactly one literal `{noun}`
  placeholder; `REPEAT` appends the noun twice. This is a new deterministic
  program, explicitly labeled `historical_model: false`.

### Capability answers

| Capability Q asked about | Current support |
|---|---|
| System prompts | No separate system-prompt channel |
| Multiple messages / conversation history | No message-array API or persistent conversation memory; one string per call |
| Per-model parameters | Only the documented fields, interpreted by task; no temperature/top-p sampling controls |
| Stopping conditions | Model generation EOS, token cap, supervised timeout, external `STOP` file; no caller-defined stop strings |
| Retries | No wrapper-level inference retry policy; downloads/libraries may have their own transport behavior |
| Response formatting | Native structured results; no schema-constrained model generation |
| Streaming | No incremental model-token streaming; completed results only |
| Tool/function calls | Host calls these MCP tools; historical models themselves do not call tools |
| Image/audio | No, text only |

Quirks: a masked prediction may be a subword, not a whole word. Base decoders
often ignore the answer format. Greedy output can repeat. Inputs over the
effective token limit fail instead of silently truncating. Pooling from an
untuned encoder is exploratory. Candidate probabilities and cosine scores
are neither humor scores nor interchangeable confidence measures.

## 3. Output contract — current engine

One native result dict per invocation; there is **no native top-level
`request_id` plus `results[]` envelope**. That is the wrapper's job.

Successful model calls contain:

```text
schema_version, run_id, created_at, status="ok", model_id, lineage,
family_year, authenticity="real_checkpoint", input, input_sha256,
elapsed_seconds, output, provenance
```

`provenance` includes the checkpoint/revision, runtime, device, seed and
`input_tokens` for Transformer calls. `output.kind` determines the payload:

| Kind | Important fields |
|---|---|
| `masked_token_predictions` | `candidates[]`: token_id, token, probability |
| `continuation`, `chat_reply`, `transformed_text` | `text`, `token_count` |
| `cosine_similarity` | `compare`, `cosine`, dimensions, pooling, sentence_tuned |
| `replaced_token_scores` | Token/score list and interpretation note |
| `word_neighbors` | Query word and neighbor/cosine list |

Match Game adds `panel`, including the original premise, framing,
`display_answer`, extraction description and nullable review fields.
The display answer is top-1 for masks, or the first generated line. Full
native output remains available. Earlier evidence records contain fewer
review fields; readers should tolerate absent optional keys.

**Actual result excerpt, with other fields omitted for brevity:**

```json
{
  "status": "ok",
  "model_id": "albert",
  "elapsed_seconds": 3.194,
  "output": {
    "kind": "masked_token_predictions",
    "candidates": [
      {"token_id": 28975, "token": "typewriter", "probability": 0.044118497520685196}
    ]
  }
}
```

That observed response had five candidates, not one; this is an excerpt, not
a complete fixture. Its recorded `provenance.input_tokens` was 17. A masked
prediction has no generated `token_count` to map to `tokens_out`.

Failures return `status="error"`, `"timeout"`, or `"stopped"`, typically
with `model_id` and `error`; some have `error_type`, elapsed time or
`diagnostics`. They do **not** always have a run ID, timestamp or provenance.
Preflight validation may raise before a result dict exists. MCP can also
return a protocol/tool error. Normalize both exceptions and returned failures.

## 4. Requested wrapper — proposed, not already implemented

Start as an importable Python adapter with a small JSON CLI. Reuse the current
MCP server if another tool is useful; avoid introducing another server/runtime
just to normalize dictionaries. Keep serial execution initially.

Proposed caller input:

```json
{
  "request_id": "req_001",
  "calls": [
    {
      "call_id": "panel_1",
      "operation": "match_game_panelist",
      "arguments": {
        "model_id": "albert",
        "premise": "The astronaut was so cheap, he used a <MASK> as a space helmet.",
        "mode": "slot"
      }
    }
  ]
}
```

Proposed normalized result fields:

| Wrapper field | Mapping / rule |
|---|---|
| `request_id`, `call_id` | Assigned/preserved by wrapper; correlate failures too |
| `model` | Native `model_id`; null for symbolic operations; keep operation name |
| `ok`, `status` | `ok = (status == "ok")`; retain timeout/stopped distinction |
| `text` | Full generated text when native output has it; otherwise null |
| `display_text` | Optional labeled panel display answer; never a replacement for raw data |
| `latency_ms` | Measure complete wrapper dispatch with a monotonic clock |
| `engine_elapsed_ms` | Native elapsed_seconds × 1000 when present; not identical to full call latency |
| `tokens_in` | Native provenance.input_tokens when present; otherwise null |
| `tokens_out` | Native output.token_count for generation; otherwise null |
| `error` | Native failure/exception text, or null on success |
| `output_kind`, `payload` | Preserve native typed output; symbolic output uses an explicitly separate kind |
| `raw` | Preserve the whole native result, including provenance and framing |

Return these entries under `results[]`. Do not invent missing metrics, turn
mask predictions into fake paragraphs, auto-rewrite bad answers, treat the
symbolic branch as a trained model, or count failures as successful inputs.

Set a small configurable batch-size limit; reject unsupported parameters.
Catch errors per call so one failure does not discard previous successes.
Treat `stopped` as a batch stop and mark remaining calls unattempted. Default
to no retries. Do not clear STOP or silently substitute another checkpoint.
Existing per-call timeouts do not implement a whole-batch deadline.

## 5. Small next source request and acceptance checks

If this is enough, propose the wrapper API and implement it. If source is
needed, ask for these ordinary files first, individually or pasted:

1. `council.py` — core and worker supervision.
2. `match_game.py` — framing and symbolic branch.
3. `mcp_server.py` — four existing tool definitions.
4. `registry.json` and `checkpoints.lock.json` — needed for real execution.
5. Dependency files plus one complete success fixture when needed.

The existing code is a local source bundle; no GitHub URL is assumed.
For local IDE work, unzip it into an ordinary folder first. This handoff is
plain Markdown and needs no archive support or repository publication.

Acceptance checks: preserve real ALBERT candidates and metadata; preserve a
decoder's full repeated text; keep vectors/scores typed; normalize a bad ID,
missing cache, timeout and STOP; distinguish unattempted calls; ensure one
failed call does not erase successful results. Use fixtures for normalization
tests and label them fixtures. Then perform one genuine cached-model/MCP call.
Do not report fixture tests as successful model inference.

Recorded validation: 18 distinct checkpoints passed the initial load/output
tests; the Match Game batch made 30 more calls across seven of those models.
The local neural and symbolic MCP tools passed protocol tests. A direct
ALBERT-to-decoder chain is written but not executed after a runtime reset.
Qwen/Mistral host connections and this proposed normalized wrapper have not
been tested. No inference was rerun for this handoff; it was checked against
the current source and preserved evidence.

For Z next: review the wrapper diff and this contract, focusing on honest
output preservation, failure/stop handling, and how the result envelope joins
the existing frontier workflow.
