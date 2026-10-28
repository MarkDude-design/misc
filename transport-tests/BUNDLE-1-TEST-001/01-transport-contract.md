# Bundle Lane: transport contract

Status: test vector only. Not approval for production publishing.

A packet is a standalone text envelope with a manifest and file boundaries.
Each payload is UTF-8 text with LF newlines and exactly one final newline.
The SHA-256 and byte count apply to payload bytes only, not the envelope.

The receiver must reject missing, duplicate, reordered, or malformed markers;
unknown paths; byte mismatches; and checksum mismatches. A valid hash is an
integrity check, not proof of authorship, safety, or permission to publish.

A later packet must not depend on a previous packet for its own verification.
A transport receipt records packet ID, accepted files, and any failure.
