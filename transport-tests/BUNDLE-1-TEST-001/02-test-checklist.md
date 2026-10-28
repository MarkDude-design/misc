# Three-file transport acceptance test

Packet ID: BUNDLE-1-TEST-001

1. Copy the code-block contents as plain UTF-8 text, excluding the fence.
2. Split deterministically using exact BEGIN and END lines for each path.
3. For every extracted payload, compute UTF-8 byte count and SHA-256.
4. Compare both fields with the manifest. Any mismatch means STOP.
5. Detect missing files, extra payloads, duplicate names, and unsafe paths.
6. Write files only into a disposable local scratch directory.
7. If a GitHub scratch push is separately authorized, refetch raw content and
   compare bytes again before reporting success.
8. Report: packet ID, per-file pass/fail, local hash, remote hash if pushed.

No publication, credit, or authorship claim follows merely from receipt.
