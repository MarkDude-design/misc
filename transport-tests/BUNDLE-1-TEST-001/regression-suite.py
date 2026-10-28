#!/usr/bin/env python3
"""BUNDLE-1-TEST-001 regression suite — frozen transport contract v0.1.

Positive verification of the canonical envelope plus six tamper
tests (every tamper case must be REJECTED). Stdlib only, no network.

Run from this directory:
    python3 regression-suite.py

Exit 0 = all green. Exit 1 = any failure.

Provenance: canonical envelope + original test vector by Meraki;
regression suite, publication, and verification by Z; per the
LEAD-CYCLE ECONOMICS v0.1 contract freeze (2026-10-28).
"""
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENVELOPE_PATH = HERE / "envelope.txt"

CANONICAL_ENVELOPE_BYTES = 3337
CANONICAL_ENVELOPE_SHA256 = "8b9c68a339cd5bd4f34ad9bd8ac99d342aa2b2c1f6ab22b930c101e3c34e6191"
CANONICAL_PAYLOAD_TOTAL = 2325  # 709 + 772 + 844

B1 = b"===== BEGIN FILE: scratch/bundle-lane/01-transport-contract.md ====="
E1 = b"===== END FILE: scratch/bundle-lane/01-transport-contract.md ====="
B2 = b"===== BEGIN FILE: scratch/bundle-lane/02-test-checklist.md ====="
E2 = b"===== END FILE: scratch/bundle-lane/02-test-checklist.md ====="
B3 = b"===== BEGIN FILE: scratch/bundle-lane/03-entry-point-note.md ====="

BEGIN_PREFIX = "===== BEGIN FILE: "
END_PREFIX = "===== END FILE: "
SUFFIX = " ====="


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify(data: bytes):
    """Parse and verify an envelope. Returns (accepted, reasons)."""
    reasons = []
    if b"\r" in data:
        reasons.append("CR byte found; LF-only required")
        return False, reasons
    lines = data.split(b"\n")
    if not lines or lines[-1] != b"":
        reasons.append("final LF missing after BUNDLE-END")
        return False, reasons
    lines = lines[:-1]
    try:
        mb = lines.index(b"MANIFEST-BEGIN")
        me = lines.index(b"MANIFEST-END")
    except ValueError:
        reasons.append("manifest markers missing")
        return False, reasons
    manifest = []
    for ln in lines[mb + 1:me]:
        parts = ln.decode("utf-8").split(" | ")
        if len(parts) != 4 or parts[0] != "FILE":
            reasons.append("malformed manifest line: " + ln.decode("utf-8", "replace"))
            return False, reasons
        manifest.append((parts[1], int(parts[2]), parts[3]))

    i = me + 1
    order = []
    payloads = {}
    while i < len(lines) and lines[i] != b"BUNDLE-END":
        s = lines[i].decode("utf-8")
        if not s.startswith(BEGIN_PREFIX) or not s.endswith(SUFFIX):
            reasons.append("expected BEGIN or BUNDLE-END, got: " + s[:60])
            return False, reasons
        path = s[len(BEGIN_PREFIX):-len(SUFFIX)]
        order.append(path)
        i += 1
        start = i
        while i < len(lines) and not lines[i].decode("utf-8", "replace").startswith(END_PREFIX):
            i += 1
        if i >= len(lines):
            reasons.append("missing END for " + path)
            return False, reasons
        end_path = lines[i].decode("utf-8")[len(END_PREFIX):-len(SUFFIX)]
        if end_path != path:
            reasons.append("END path mismatch for " + path)
        payloads[path] = b"\n".join(lines[start:i]) + b"\n"
        i += 1
    if i >= len(lines) or lines[i] != b"BUNDLE-END":
        reasons.append("BUNDLE-END missing")
        return False, reasons
    if any(l != b"" for l in lines[i + 1:]):
        reasons.append("trailing content after BUNDLE-END")

    mpaths = [m[0] for m in manifest]
    dupes = sorted(set(p for p in order if order.count(p) > 1))
    if dupes:
        reasons.append("duplicate payloads: " + ", ".join(dupes))
    missing = [p for p in mpaths if p not in order]
    if missing:
        reasons.append("missing files (manifest, not body): " + ", ".join(missing))
    extra = [p for p in order if p not in mpaths]
    if extra:
        reasons.append("extra payloads not in manifest: " + ", ".join(extra))
    if order != mpaths:
        reasons.append("marker order does not match manifest order")
    for p in order:
        if ".." in p or p.startswith("/") or not p.startswith("scratch/bundle-lane/"):
            reasons.append("unsafe path: " + p)
    for path, nbytes, h in manifest:
        payload = payloads.get(path)
        if payload is None:
            continue
        if len(payload) != nbytes:
            reasons.append("byte mismatch: %s (%d vs %d)" % (path, len(payload), nbytes))
        if sha256(payload) != h:
            reasons.append("sha mismatch: " + path)
    return (not reasons), reasons


def reorder_blocks(data: bytes) -> bytes:
    b1 = data.index(B1)
    b2 = data.index(B2)
    b3 = data.index(B3)
    return data[:b1] + data[b2:b3] + data[b1:b2] + data[b3:]


def duplicate_block(data: bytes) -> bytes:
    b2 = data.index(B2)
    e2 = data.index(E2) + len(E2) + 1  # include trailing LF
    return data[:e2] + data[b2:e2] + data[e2:]


def main() -> int:
    data = ENVELOPE_PATH.read_bytes()
    failures = []

    # canonical contract checks (frozen envelope)
    if len(data) != CANONICAL_ENVELOPE_BYTES:
        failures.append("envelope byte count %d != canonical %d" % (len(data), CANONICAL_ENVELOPE_BYTES))
    if sha256(data) != CANONICAL_ENVELOPE_SHA256:
        failures.append("envelope sha256 does not match canonical anchor")
    if not data.endswith(b"BUNDLE-END\n"):
        failures.append("envelope does not end with BUNDLE-END + one final LF")

    # positive verification
    accepted, reasons = verify(data)
    if not accepted:
        failures.append("positive verification FAILED: " + "; ".join(reasons))
    else:
        payload_total = 709 + 772 + 844
        if payload_total != CANONICAL_PAYLOAD_TOTAL:
            failures.append("payload total %d != canonical %d" % (payload_total, CANONICAL_PAYLOAD_TOTAL))
        else:
            print("positive : ACCEPTED  3/3 files, payload total %d B" % payload_total)

    # six tamper cases — every one MUST be rejected
    tamper_cases = [
        ("altered payload char", data.replace(b"A packet is a standalone", b"A packet is a standal0ne")),
        ("manifest entry removed", b"\n".join(l for l in data.split(b"\n") if not l.startswith(b"FILE | scratch/bundle-lane/02-"))),
        ("reordered blocks", reorder_blocks(data)),
        ("duplicated block", duplicate_block(data)),
        ("truncated envelope", data[:data.index(B3)]),
        ("manifest byte-count lie", data.replace(b"| 709 |", b"| 708 |")),
    ]
    for name, tampered in tamper_cases:
        acc, rs = verify(tampered)
        if acc:
            failures.append("tamper case NOT rejected: " + name)
        else:
            print("tamper   : REJECTED  %-26s (%s)" % (name, rs[0]))

    if failures:
        print("\nFAILURES (%d):" % len(failures))
        for f in failures:
            print("  - " + f)
        return 1
    print("\nALL GREEN: canonical envelope verified; 6/6 tamper cases rejected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
