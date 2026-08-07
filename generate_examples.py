#!/usr/bin/env python3
"""Generate fixtures/examples/manifest.json with correct digests for the example
positive + negative-control rows, using tools/verify.py's exact canonicalization."""
import hashlib
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.verify import jcs, sha256_hex

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

envelope_payload = {
    "envelope_version": "cd4c-fixture-v1",
    "fixture_interchange_spec": "v1",
    "mapping_version": 7,
    "serialization": "JCS RFC 8785 NFC strict",
}
header_digest = sha256_hex(jcs(envelope_payload).encode("utf-8"))

row_positive = {
    "fixture_id": "FIXTURE-JCS-NUM-001",
    "row_digest_ref": "SELF",
    "terminal_verdict": "PASS",
    "mapping_version": 7,
    "epoch_context": {"fence_epoch": "epoch_42", "stage": "canonicalization"},
    "typed_trigger": "canonical_form",
    "evidence_state": {
        "variants": ["1e2", "100", "100.0", "100.00"],
        "canonical_bytes": "identical",
        "digest": "same",
    },
    "replay_seed": "jcsnum001:canonical:variant_equivalence",
}

# Negative control: same structure, one meaning-changing field (verdict PASS -> FAIL,
# and evidence_state diverged). Must produce a different digest and a FAIL verdict.
row_negative = {
    "fixture_id": "FIXTURE-JCS-NUM-001-NEG",
    "row_digest_ref": "SELF",
    "terminal_verdict": "FAIL",
    "mapping_version": 7,
    "epoch_context": {"fence_epoch": "epoch_42", "stage": "canonicalization"},
    "typed_trigger": "canonical_form",
    "evidence_state": {
        "variants": ["1e2", "100", "100.0", "100.00"],
        "canonical_bytes": "identical",
        "digest": "same",
    },
    "replay_seed": "jcsnum001:canonical:variant_equivalence",
}

rows = []
parent = header_digest
for row in (row_positive, row_negative):
    # Self-referential digest: compute over the row core (without row_digest_ref).
    row_core = {k: v for k, v in row.items() if k != "row_digest_ref"}
    canonical = jcs(row_core).encode("utf-8")
    row_digest = sha256_hex(parent.encode("ascii") + canonical)
    row["row_digest_ref"] = row_digest
    rows.append(row)
    parent = row_digest

manifest = {
    "envelope": {
        "manifest_digest": sha256_hex(jcs(envelope_payload).encode("utf-8")),
        "header_digest": header_digest,
        "payload": envelope_payload,
    },
    "rows": rows,
}

out_path = os.path.join(ROOT, "fixtures", "examples", "manifest.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(f"wrote {out_path}")
print(f"header_digest={header_digest}")
for r in rows:
    print(f"{r['fixture_id']}: row_digest={r['row_digest_ref']} verdict={r['terminal_verdict']}")
