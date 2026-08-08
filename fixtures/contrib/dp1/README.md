# DP1 · Adversarial Fixtures (12 rows, byte-form JCS)

Contribution from OpenClaw 量化助手 (DP#1 slot), 2026-08-07.

## Artifacts

- `manifest.json` — single manifest, 12 rows, byte-form JCS (RFC 8785 NFC strict),
  shape `envelope/rows/concurrent_candidates` (candidates empty: all rows are
  committed-chain rows; no concurrent admission in this batch).
- Source fixtures: `epoch-fence.v1.3` adversarial corpus (f01–f12), `injection_mode=none`
  (pure semantic judgment, no timing injection).

## Row contract

- 6-field fixed order: `{row_digest_ref, terminal_verdict, mapping_version,
  epoch_context{fence_epoch, stage}, typed_trigger, evidence_state, replay_seed}`
  plus explicit `parent_digest_ref` (chain) and `raw_payload_hash` (byte-layer anchor).
- Digest chain: `row_digest = SHA-256(parent_digest_ref ‖ JCS(row minus row_digest_ref))`;
  row 0 parent = `envelope.header_digest`; `header_digest = manifest_digest =
  SHA-256(JCS(envelope.payload))`.
- `raw_payload_hash = SHA-256(JCS(original fixture bytes))` — double-layer anchor with
  `row_digest_ref` (self-referential canonical digest).
- `replay_seed = "<raw_payload_hash>:single-run:<run_id>"` (single-run fixtures;
  witness set empty, window = single run).

## Verdict mapping (5-value interchange set)

| class | rows | terminal_verdict |
|---|---|---|
| structural / format rejection | ADV-012 | FAIL |
| canonicalization typed failure | ADV-006 | UNKNOWN |
| evidence missing (fail-closed) | ADV-005 | UNKNOWN |
| taxonomy blind spot (unknown reason) | ADV-004 | UNKNOWN |
| epoch / context violation | ADV-002, ADV-003, ADV-011 | FAIL |
| coverage cardinality / orphan | ADV-008, ADV-009 | FAIL |
| digest mismatch | ADV-010 | FAIL |
| happy-path | ADV-001, ADV-007 | PASS |

`mapping_version=7` stamped on every row (7→5 one-way fold; no 5→7 reverse mapping).
`evidence_state`: `missing` (ADV-005), `expired` (ADV-011 stale epoch), `fresh` (rest).

## Verification

`python3 tools/verify.py --manifest fixtures/contrib/dp1/manifest.json` → exit 0
(all 12 row digests + envelope digest verified; verdicts in 5-value set).
