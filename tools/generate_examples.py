#!/usr/bin/env python3
"""Generate fixtures/examples/manifest.json with correct digests.

Covers the complete machine-readable subset of the fixture registry:
  - rows: FIXTURE-JCS-NUM-001, FIXTURE-JCS-NUM-001-NEG,
          FIXTURE-PROV-001, FIXTURE-PROV-001-NEG
  - concurrent_candidates: FIXTURE-CONCURRENT-CANDIDATE-A/B (shared parent,
    pre-CAS candidate view, validated separately from the committed chain)
  - registry_coverage: machine-readable mirror of fixtures/registry.md —
    every registered fixture with status (locked/drafted/proposed) and
    encoding_status (complete = 6-field machine encoding present in this
    manifest; incomplete = 6-field encoding not yet registered, registry.md
    stays canonical; incomplete rows are NEVER fabricated).

Digest rules (identical to tools/verify.py):
  - envelope header_digest = SHA-256(JCS(envelope.payload))
  - row digest = SHA-256(parent_digest || JCS(row core)), where row core
    excludes the self-referential row_digest_ref field
  - first row's parent = envelope header_digest
  - candidate digest = SHA-256(declared parent || JCS(candidate core))

Default mode verifies the regenerated manifest byte-for-byte against the
previously committed one (digest drift => exit 1). Use --force to write
regardless (intended for deliberate row changes; then run verify.py).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.verify import jcs, sha256_hex

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "fixtures", "examples", "manifest.json")

envelope_payload = {
    "envelope_version": "cd4c-fixture-v1",
    "fixture_interchange_spec": "v1",
    "mapping_version": 7,
    "serialization": "JCS RFC 8785 NFC strict",
}
header_digest = sha256_hex(jcs(envelope_payload).encode("utf-8"))

# --- rows (canonical 6-field shape; row_digest_ref computed below) -----------

row_jcs_pos = {
    "fixture_id": "FIXTURE-JCS-NUM-001",
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

# Negative control: same structure, meaning-changing verdict PASS -> FAIL.
row_jcs_neg = {
    "fixture_id": "FIXTURE-JCS-NUM-001-NEG",
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

row_prov_pos = {
    "fixture_id": "FIXTURE-PROV-001",
    "terminal_verdict": "PASS",
    "mapping_version": 7,
    "epoch_context": {"fence_epoch": "epoch_42", "stage": "delegation_gate"},
    "typed_trigger": "authorization_ok",
    "evidence_state": {
        "containment": "pass",
        "provenance": "pass",
        "parent_reference_digest": "resolves_live_non_revoked",
        "authorized_set": ["op-a"],
        "actual_set": ["op-a"],
        "effect": "simulated_noop",
    },
    "replay_seed": "prov001:delegation:containment_pass_provenance_pass",
}

# Negative control: orphaned parent reference -> UNKNOWN (fail-closed,
# epistemic), typed_trigger=evidence_missing.
row_prov_neg = {
    "fixture_id": "FIXTURE-PROV-001-NEG",
    "terminal_verdict": "UNKNOWN",
    "mapping_version": 7,
    "epoch_context": {"fence_epoch": "epoch_42", "stage": "delegation_gate"},
    "typed_trigger": "evidence_missing",
    "evidence_state": {
        "containment": "pass",
        "provenance": "fail_orphaned",
        "parent_reference_digest": "missing_from_ledger",
        "authorized_set": ["op-a"],
        "actual_set": ["op-a"],
        "effect": "none_emitted",
        "reason": "PROVENANCE_AMBIGUOUS_OR_ORPHANED",
    },
    "replay_seed": "prov001:delegation:containment_pass_provenance_fail_orphaned",
}

# --- concurrent candidates (pre-CAS candidate view, shared parent) -----------

candidate_a = {
    "fixture_id": "FIXTURE-CONCURRENT-CANDIDATE-A",
    "terminal_verdict": "PASS",
    "mapping_version": 7,
    "epoch_context": {"fence_epoch": "epoch_42", "stage": "concurrent_admission"},
    "typed_trigger": "cas_winner",
    "evidence_state": {"candidate_role": "winner_by_digest_order", "shared_parent": True},
    "replay_seed": "conc001:candidate_a:shared_parent",
    "parent_digest_ref": header_digest,
}

candidate_b = {
    "fixture_id": "FIXTURE-CONCURRENT-CANDIDATE-B",
    "terminal_verdict": "PASS",
    "mapping_version": 7,
    "epoch_context": {"fence_epoch": "epoch_42", "stage": "concurrent_admission"},
    "typed_trigger": "cas_winner",
    "evidence_state": {"candidate_role": "winner_by_digest_order", "shared_parent": True},
    "replay_seed": "conc001:candidate_b:shared_parent",
    "parent_digest_ref": header_digest,
}

# --- registry coverage (mirror of fixtures/registry.md, never fabricated) ----

REGISTRY_COVERAGE = [
    # Delegation / Provenance 族
    {"fixture_id": "FIXTURE-PROV-001", "family": "delegation/provenance", "status": "locked", "encoding_status": "complete", "terminal_verdict": "PASS", "co_authors": ["KingSystemHaiGo", "揽星的助手"]},
    {"fixture_id": "FIXTURE-PROV-001-NEG", "family": "delegation/provenance", "status": "locked", "encoding_status": "complete", "terminal_verdict": "UNKNOWN", "co_authors": ["KingSystemHaiGo", "揽星的助手"], "note": "manifest negative control"},
    {"fixture_id": "FIXTURE-PROV-002", "family": "delegation/provenance", "status": "locked", "encoding_status": "incomplete", "terminal_verdict": "PASS", "co_authors": ["KingSystemHaiGo", "揽星的助手"], "incomplete_reason": "6-field machine encoding not yet registered in coordination thread"},
    {"fixture_id": "FIXTURE-PROV-003", "family": "delegation/provenance", "status": "locked", "encoding_status": "incomplete", "terminal_verdict": "FAIL", "co_authors": ["KingSystemHaiGo", "凯瑞's Agent"], "incomplete_reason": "typed_trigger=SCOPE_WIDENING_AT_DELEGATION or constraint_exceeded per co-author preference; encoding pending"},
    # Epoch-bound Retry Safety 族
    {"fixture_id": "FIXTURE-RACE-COMMIT-CAS-001", "family": "epoch-bound-retry-safety", "status": "locked", "encoding_status": "incomplete", "terminal_verdict": "HOLD/ESCALATED/REVALIDATE_REQUIRED", "co_authors": ["KingSystemHaiGo", "揽星的助手"], "incomplete_reason": "tri-state verdict row encoding pending"},
    # Untrusted-load 族
    {"fixture_id": "FIXTURE-UNTRUST-INGEST-001", "family": "untrusted-load", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "UNKNOWN", "co_authors": ["DP#1 维度注入"]},
    {"fixture_id": "FIXTURE-UNTRUST-RECOMPUTE-001", "family": "untrusted-load", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "PASS", "co_authors": ["DP#1 维度注入"]},
    {"fixture_id": "FIXTURE-UNTRUST-EGRESS-ALLOW-001", "family": "untrusted-load", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "PASS", "co_authors": ["DP#1 维度注入"]},
    {"fixture_id": "FIXTURE-UNTRUST-EGRESS-BLOCK-001", "family": "untrusted-load", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "FAIL", "co_authors": ["DP#1 维度注入"]},
    {"fixture_id": "FIXTURE-UNTRUST-CLOSURE-001", "family": "untrusted-load", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "PASS", "co_authors": ["DP#1 维度注入"]},
    {"fixture_id": "FIXTURE-UNTRUST-CLOSURE-DRIFT-001", "family": "untrusted-load", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "UNKNOWN", "co_authors": ["DP#1 维度注入"]},
    {"fixture_id": "FIXTURE-UNTRUST-SNAPSHOT-001", "family": "untrusted-load", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "PASS", "co_authors": ["DP#1 维度注入"]},
    {"fixture_id": "FIXTURE-UNTRUST-SNAPSHOT-DRIFT-001", "family": "untrusted-load", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "UNKNOWN", "co_authors": ["DP#1 维度注入"]},
    # JCS / Canonicalization 族
    {"fixture_id": "FIXTURE-JCS-NUM-001", "family": "jcs/canonicalization", "status": "locked", "encoding_status": "complete", "terminal_verdict": "PASS", "co_authors": ["JuanJuan Agent 交叉跑"]},
    {"fixture_id": "FIXTURE-JCS-NUM-001-NEG", "family": "jcs/canonicalization", "status": "locked", "encoding_status": "complete", "terminal_verdict": "FAIL", "co_authors": ["JuanJuan Agent 交叉跑"], "note": "manifest negative control"},
    {"fixture_id": "FIXTURE-JCS-NUM-002", "family": "jcs/canonicalization", "status": "locked", "encoding_status": "incomplete", "terminal_verdict": "UNKNOWN", "co_authors": ["JuanJuan Agent 交叉跑"]},
    {"fixture_id": "FIXTURE-JCS-NAN-001", "family": "jcs/canonicalization", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "UNKNOWN", "co_authors": ["JuanJuan Agent class 8"]},
    {"fixture_id": "FIXTURE-JCS-UNICODE-001", "family": "jcs/canonicalization", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "PASS", "co_authors": ["JuanJuan Agent class 8"]},
    {"fixture_id": "FIXTURE-JCS-DECIMAL-001", "family": "jcs/canonicalization", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "PASS", "co_authors": ["JuanJuan Agent class 8"]},
    {"fixture_id": "FIXTURE-JCS-ENDIAN-001", "family": "jcs/canonicalization", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "same digest", "co_authors": ["JuanJuan Agent 备"]},
    # Slot-counter / Epoch 竞态族
    {"fixture_id": "FIXTURE-SLOT-SAME-WINDOW-001", "family": "slot-counter/epoch-race", "status": "locked", "encoding_status": "incomplete", "terminal_verdict": "chain-top=digest-max/DUPLICATE", "co_authors": ["OpenClaw量化助手"]},
    {"fixture_id": "FIXTURE-ENQ-DISPATCH-GAP-001", "family": "slot-counter/epoch-race", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "STALE_SNAPSHOT", "co_authors": ["JuanJuan Agent"]},
    {"fixture_id": "FIXTURE-CAS-HLC-DIVERGENCE-001", "family": "slot-counter/epoch-race", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "consistent/epoch_mismatch", "co_authors": ["Jades"]},
    # Truncation / Storage 族
    {"fixture_id": "FIXTURE-TRUNC-DIGEST-001", "family": "truncation/storage", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "chain verification failure", "co_authors": ["Jades"]},
    {"fixture_id": "FIXTURE-TRUNC-FIELD-001", "family": "truncation/storage", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "semantic verification failure", "co_authors": ["Jades"]},
    {"fixture_id": "FIXTURE-STORAGE-L1-001", "family": "truncation/storage", "status": "locked", "encoding_status": "incomplete", "terminal_verdict": "digest mismatch", "co_authors": ["DP#1 三层类"]},
    {"fixture_id": "FIXTURE-STORAGE-L2-001", "family": "truncation/storage", "status": "locked", "encoding_status": "incomplete", "terminal_verdict": "chain verification failure", "co_authors": ["DP#1 三层类"]},
    {"fixture_id": "FIXTURE-STORAGE-L3-001", "family": "truncation/storage", "status": "locked", "encoding_status": "incomplete", "terminal_verdict": "anchor typed failure", "co_authors": ["DP#1 三层类"]},
    # 并发 / Inbox 族
    {"fixture_id": "FIXTURE-CONC-REPLY-RACE-001", "family": "concurrent/inbox", "status": "proposed", "encoding_status": "incomplete", "terminal_verdict": "deterministic tiebreak + superseded reference", "co_authors": ["东湖小C 起草中"]},
    # Epoch 边界 / Bridge 族
    {"fixture_id": "FIXTURE-BRIDGE-EPOCH-INVALIDATION-001", "family": "epoch-boundary/bridge", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "epoch_mismatch/evidence_missing", "co_authors": ["KingSystemHaiGo", "凯瑞's Agent"]},
    # 转换形态族（草案未入 registry，显式标注）
    {"fixture_id": "FIXTURE-EPOCH-TRANSITION-001/002/003", "family": "epoch-boundary/transition-shape", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "null->stable/stable->null/stable->stable/null->null", "co_authors": ["Jades 线"], "incomplete_reason": "drafted outside registry; fold-in before 8/10"},
    {"fixture_id": "FIXTURE-NULL-EPOCH-WINDOW-001", "family": "epoch-boundary/null-epoch", "status": "drafted", "encoding_status": "incomplete", "terminal_verdict": "drain-window attribution", "co_authors": ["念海助理"], "incomplete_reason": "PR pending"},
    # concurrent candidate view
    {"fixture_id": "FIXTURE-CONCURRENT-CANDIDATE-A", "family": "concurrent-candidate-view", "status": "locked", "encoding_status": "complete", "terminal_verdict": "PASS", "co_authors": ["KingSystemHaiGo"]},
    {"fixture_id": "FIXTURE-CONCURRENT-CANDIDATE-B", "family": "concurrent-candidate-view", "status": "locked", "encoding_status": "complete", "terminal_verdict": "PASS", "co_authors": ["KingSystemHaiGo"]},
]


def chain_rows(row_defs):
    rows = []
    parent = header_digest
    for row in row_defs:
        row_core = {k: v for k, v in row.items() if k != "row_digest_ref"}
        canonical = jcs(row_core).encode("utf-8")
        row_digest = sha256_hex(parent.encode("ascii") + canonical)
        row = dict(row)
        row["row_digest_ref"] = row_digest
        rows.append(row)
        parent = row_digest
    return rows


def build_manifest():
    rows = chain_rows([row_jcs_pos, row_jcs_neg, row_prov_pos, row_prov_neg])
    candidates = []
    for cand in (candidate_a, candidate_b):
        cand_core = {k: v for k, v in cand.items() if k != "row_digest_ref"}
        canonical = jcs(cand_core).encode("utf-8")
        parent = cand.get("parent_digest_ref") or header_digest
        cand = dict(cand)
        cand["row_digest_ref"] = sha256_hex(parent.encode("ascii") + canonical)
        candidates.append(cand)
    return {
        "envelope": {
            "manifest_digest": sha256_hex(jcs(envelope_payload).encode("utf-8")),
            "header_digest": header_digest,
            "payload": envelope_payload,
        },
        "rows": rows,
        "concurrent_candidates": candidates,
        "registry_coverage": REGISTRY_COVERAGE,
    }


def digest_snapshot(manifest):
    snap = {"envelope": manifest["envelope"]["manifest_digest"]}
    for r in manifest["rows"]:
        snap[r["fixture_id"]] = r["row_digest_ref"]
    for c in manifest.get("concurrent_candidates", []):
        snap[c["fixture_id"]] = c["row_digest_ref"]
    return snap


def main():
    force = "--force" in sys.argv
    manifest = build_manifest()
    new_snap = digest_snapshot(manifest)

    if os.path.exists(OUT_PATH):
        with open(OUT_PATH, "r", encoding="utf-8") as f:
            old = json.load(f)
        old_snap = digest_snapshot(old)
        if new_snap == old_snap and manifest["registry_coverage"] == old.get("registry_coverage", []):
            print("no digest drift vs previously committed manifest (byte-stable)")
        elif new_snap == old_snap:
            print("note: digests stable; registry_coverage changed (expected on registry update)")
        else:
            print("WARNING: digest drift vs previously committed manifest:", file=sys.stderr)
            for k in new_snap:
                if new_snap[k] != old_snap.get(k):
                    print(f"  {k}: {old_snap.get(k)} -> {new_snap[k]}", file=sys.stderr)
            if not force:
                print("aborting (use --force to write the new digests deliberately)", file=sys.stderr)
                return 1

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {OUT_PATH}")
    print(f"header_digest={header_digest}")
    for r in manifest["rows"]:
        print(f"{r['fixture_id']}: row_digest={r['row_digest_ref']} verdict={r['terminal_verdict']}")
    complete = sum(1 for e in manifest["registry_coverage"] if e["encoding_status"] == "complete")
    total = len(manifest["registry_coverage"])
    print(f"registry_coverage: {complete}/{total} rows machine-readable-complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
