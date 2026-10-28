# BUNDLE-1-TEST-001 — canonical transport fixture (contract freeze v0.1)

Frozen envelope rules (LEAD-CYCLE ECONOMICS v0.1, 2026-10-28):

- UTF-8 encoding; LF-only line endings
- Exactly one final LF after `BUNDLE-END`
- Envelope byte count includes that final LF
- Payload hashes exclude envelope delimiters
- Canonical envelope: 3337 bytes (sha256 `8b9c68a339cd5bd4f34ad9bd8ac99d342aa2b2c1f6ab22b930c101e3c34e6191`)
- Canonical combined payloads: 2325 bytes (709 + 772 + 844)

## Files

- `envelope.txt` — canonical 3-file envelope (includes final LF)
- `01..03-*.md` — the three payloads as published (byte-identical to the envelope contents)
- `regression-suite.py` — positive verification + six tamper tests

## Run

    python3 regression-suite.py

Stdlib only. No network. Exit 0 = all green.

## Regression tests (all must reject)

1. Altered payload character → SHA mismatch
2. Manifest entry removed → extra payload not in manifest
3. Reordered blocks → order mismatch vs manifest
4. Duplicated block → duplicate payload
5. Truncated envelope → missing markers
6. Manifest byte-count lie → byte mismatch

Any future parser or clerk for this lane must clear all six before it is
trusted with a real envelope.

## Provenance

Canonical envelope and original test vector: Meraki. Split, verification,
publication, and regression suite: Z. Authorization: Mark. Independent
readback (fetch + re-hash, 3/3 match) performed by Meraki on the published
files. Full route demonstrated: emission → human paste → Z split/verify →
GitHub → independent byte verification.
