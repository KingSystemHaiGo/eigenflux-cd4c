#!/usr/bin/env python3
"""Split manifest.json into positive + negative manifests (Agent Commons Lab
clean-room feedback, 8/9): the negative-control row (UNSAFE-DEDUP-001, declared
PASS but semantically MUST FAIL) made the shared manifest exit 1, which broke
test_verify.py's first assertion (manifest should exit 0). Fix: keep positive
rows in manifest.json (exit 0), move adversarial rows to manifest_neg.json
(exit 1 by design), and re-chain digests per manifest.

Also: STALE-NEW semantic clarification — a new op-key does NOT refresh a stale
grant; it triggers a FULL re-authorization evaluation. Rows declaring
grant=stale + op_key=new must carry fresh_admission=true AND
reauthorization=full_re_evaluation, else semantic FAIL.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "fixtures", "examples", "manifest.json")
MANIFEST_NEG = os.path.join(ROOT, "fixtures", "examples", "manifest_neg.json")

sys.path.insert(0, os.path.join(ROOT, "tools"))
from verify import jcs, sha256_hex  # noqa: E402

NEG_FIXTURES = {"FIXTURE-RESTART-UNSAFE-DEDUP-001"}


def chain(envelope_payload, row_defs):
    """Rebuild digest chain: header digest from envelope payload, then rows."""
    header = sha256_hex(jcs(envelope_payload).encode("utf-8"))
    rows = []
    parent = header
    for row in row_defs:
        core = {k: v for k, v in row.items() if k != "row_digest_ref"}
        row = dict(row)
        row["row_digest_ref"] = sha256_hex(parent.encode("ascii") + jcs(core).encode("utf-8"))
        rows.append(row)
        parent = row["row_digest_ref"]
    return header, rows


def rebuild(src, out, neg_only=False, source=None):
    m = source if source is not None else (lambda: (json.load(open(src, "r", encoding="utf-8"))))()
    payload = m["envelope"]["payload"]
    rows = [r for r in m["rows"] if (r["fixture_id"] in NEG_FIXTURES) == neg_only]
    header, rows = chain(payload, rows)

    out_m = {
        "envelope": {
            "manifest_digest": sha256_hex(jcs(payload).encode("utf-8")),
            "header_digest": header,
            "payload": payload,
        },
        "rows": rows,
        "concurrent_candidates": m.get("concurrent_candidates", []),
        "registry_coverage": m.get("registry_coverage", []),
        "split_note": (
            "negative-control rows split to manifest_neg.json (8/9, Agent Commons Lab "
            "clean-room feedback): adversarial rows declare PASS but semantics demand "
            "FAIL -> they must exit 1 by design, not break the positive manifest contract"
        ),
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(out_m, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {out} ({len(rows)} rows, header={header})")


if __name__ == "__main__":
    with open(MANIFEST, "r", encoding="utf-8") as f:
        original = json.load(f)
    rebuild(MANIFEST, MANIFEST, neg_only=False, source=original)
    rebuild(MANIFEST, MANIFEST_NEG, neg_only=True, source=original)
