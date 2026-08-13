# Minis v0.6 → CD-4c fixture contribution

## Target

- Repository: `https://github.com/KingSystemHaiGo/eigenflux-cd4c`
- Branch: `master`
- Target directory: `fixtures/contrib/minis-v06/`
- Shape: `manifest.json` + optional local `verify.py`
- Mapping version: `7`

## Local verification

```bash
python3 tools/verify.py --manifest fixtures/contrib/minis-v06/manifest.json
```

The official CD-4c verifier was run against this manifest locally:

```text
RESULT: ALL ROWS VERIFIED
row[0] FIX-005: digest ✓
row[1] FIX-006: digest ✓
```

## Envelope and chain

- `manifest_digest = SHA-256(JCS(envelope.payload))`
- `header_digest = manifest_digest`
- `row_digest_ref = SHA-256(parent_digest_ref ASCII hex || JCS(row minus row_digest_ref))`
- Row 0 parent is `header_digest`; row 1 parent is row 0 digest.
- `mapping_version=7` on every row.
- `raw_payload_hash` records the original public fixture byte hash.

## Source anchors

- Fixture source commit: `f3eadfbfceb1eb681cea6052d7be17e27af1abe2`
- Receipt crosswalk commit: `d6c39de2ca4b4d0be4a5565752ddf45759200098`
- Source license: MIT
- Manifest digest: `8f65144eefb1b148e03a1c742a34589867ff694583e5da15ca4b9b52d286509b`
- Schema fingerprint: `286d2aed9e118f149d613a521e832c76327cb49a0d43f8e71e28e43649fbc53a`
- Row chain head: `65c11f52b7c662b23840b8c6587ab186b2e6770a7000ed8fa433cd77bf263314`

## Semantic boundary

The source reports are reproducible on Minis. Historical PASS reports from other runtimes
exist, but the formal cross-runtime claim remains `UNVERIFIED` until complete report objects
and 64-character environment/output digests are independently available.

The source uses two explicit profiles:

- `minis-identity-v1`: semantic identity profile.
- `strict-jcs-transport-v1`: exchange/file profile.

They must not be treated as byte-identical digests. `UNCLASSIFIED` in a 6-field profile and
`MISALIGNED` in the bounded-drain profile are also distinct; special fifth values require
`taxonomy_profile` and `typed_trigger`.
