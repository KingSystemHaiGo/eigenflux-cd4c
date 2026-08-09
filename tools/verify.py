#!/usr/bin/env python3
"""
CD-4c fixture validator — JCS RFC 8785 NFC strict canonicalization + SHA-256 digest chain.

Minimal self-contained implementation (Python stdlib only) covering the 6-field row format
from docs/fixture-interchange-spec.md. This is the executable counterpart of the shared
serialization contract; see fixtures/registry.md for the full fixture list.

Replay command:
    python3 tools/verify.py --manifest fixtures/examples/manifest.json

Exit codes: 0 = all rows verified (digest + verdict), 1 = verification failure,
2 = usage/IO error.
"""
import argparse
import hashlib
import json
import os
import sys
import unicodedata
from decimal import Decimal

# --- JCS RFC 8785 canonicalization (core subset) -----------------------------

# I-JSON interoperable integer range: JSON.parse-safe integers are ±(2^53−1).
# Integers beyond this range are NOT portable across IEEE-754 double platforms
# (they silently lose precision), so they are a typed failure here — never a
# silent coercion. This closes the >2^53 gap flagged 8/9 (Pixel Open World Dev
# alignment); verdict: fail-closed core reject.
IJSON_INT_LIMIT = 2**53 - 1


def _jcs_number(n):
    """RFC 8785 number serialization: integers without exponent/leading zeros,
    decimals with trailing zeros stripped, -0 normalized to 0.

    Fail-closed: integers with |n| > 2^53−1 are outside the I-JSON
    interoperable range and raise a typed ValueError (never silently
    serialized with lost precision)."""
    if isinstance(n, bool):
        return "true" if n else "false"
    if isinstance(n, int):
        if abs(n) > IJSON_INT_LIMIT:
            raise ValueError(
                f"integer out of I-JSON interoperable range ±(2^53−1): {n} "
                "(fail-closed core reject, no silent precision loss)"
            )
        return str(n)
    if isinstance(n, float):
        if n != n or n in (float("inf"), float("-inf")):
            raise ValueError(f"non-finite number is not valid JSON: {n}")
        # -0.0 -> 0
        if n == 0:
            return "0"
        # use Decimal for exact serialization control
        d = Decimal(repr(n))
        return _jcs_decimal(d)
    if isinstance(n, Decimal):
        return _jcs_decimal(n)
    raise TypeError(f"unsupported number type: {type(n)}")


def _jcs_decimal(d):
    s = format(d, "f")  # fixed-point, no exponent
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("", "-"):
        s = "0"
    if s == "-0":
        s = "0"
    return s


def _jcs_string(s):
    # Pure JCS RFC 8785: RFC 8785 does NOT mandate NFC normalization.
    # NFC preprocessing (Unicode UAX#15) is an explicit opt-in extension, not part
    # of the default canonical form. opt_in_nfc() applies it before serialization.
    out = ['"']
    for ch in s:
        o = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\b":
            out.append("\\b")
        elif ch == "\f":
            out.append("\\f")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif o < 0x20:
            out.append(f"\\u{o:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


_NFC_OPT_IN = False


def opt_in_nfc(enable=True):
    """Explicitly opt in to NFC preprocessing (Unicode UAX#15) before canonical
    serialization. Off by default: cross-implementation byte comparability must
    not depend on normalization (RFC 8785 does not mandate it)."""
    global _NFC_OPT_IN
    _NFC_OPT_IN = enable


def _preprocess(value):
    if _NFC_OPT_IN and isinstance(value, str):
        n = unicodedata.normalize("NFC", value)
        if n != value:
            # rejection rule: non-NFC input fails closed rather than silently
            # normalizing, when NFC preprocessing is opted in
            raise ValueError(f"non-NFC string rejected under opt-in NFC preprocessing: {value!r}")
    return value


def jcs(value):
    """Canonical JSON serialization per JCS RFC 8785 (core subset)."""
    value = _preprocess(value)
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, Decimal)):
        return _jcs_number(value)
    if isinstance(value, str):
        return _jcs_string(value)
    if isinstance(value, list):
        return "[" + ",".join(jcs(v) for v in value) + "]"
    if isinstance(value, dict):
        # RFC 8785: object keys sorted by UTF-16 code units
        items = sorted(value.items(), key=lambda kv: _utf16_key(kv[0]))
        return "{" + ",".join(jcs(k) + ":" + jcs(v) for k, v in items) + "}"
    raise TypeError(f"unsupported type: {type(value)}")


def _utf16_key(s):
    """Sort key per RFC 8785: lexicographic by UTF-16 code units."""
    return s.encode("utf-16-le")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- Verification logic -------------------------------------------------------

VERDICTS = {"PASS", "INDET", "FAIL", "UNKNOWN", "UNCLASSIFIED"}

# Semantic assertions: beyond byte integrity, the verifier independently derives
# the expected verdict from provenance semantics for the delegation family.
# FIXTURE-PROV-001: positive anchor -> PASS; FIXTURE-PROV-001-NEG: orphaned
# parent -> UNKNOWN (fail-closed, epistemic). A row whose declared verdict
# contradicts the semantics it encodes is rejected even if digests match.
def semantic_verdict(row):
    """Return (expected_verdict, reason) derived from the row's own semantics,
    or (None, None) when the row is not semantically assertable here."""
    ev = row.get("evidence_state")
    if not isinstance(ev, dict):
        return None, None
    fid = row.get("fixture_id", "")
    if fid.startswith("FIXTURE-PROV-001"):
        prov = ev.get("provenance")
        if prov == "pass":
            return "PASS", "provenance pass"
        if prov == "fail_orphaned":
            return "UNKNOWN", "orphaned parent reference -> epistemic fail-closed"
    if fid.startswith("FIXTURE-DISPOSITION-BITFIELD-DIVERGENCE-001"):
        # Adversarial family (凯瑞's Agent request, 8/9): canonical bytes and
        # digests are VALID, but the decoded disposition_reason bits demand a
        # fail-closed gate outcome (UNKNOWN/HOLD), so a declared PASS verdict
        # is a semantic contradiction even though digest checks pass.
        bits = ev.get("disposition_reason_bits", [])
        holding_bits = {
            "stale-epoch", "effect-unverifiable", "receipt-missing",
            "authority-unpinned", "time-source-ambiguous", "chain-broken",
        }
        if any(b in holding_bits for b in bits):
            return "UNKNOWN", (
                f"disposition bits {sorted(bits)} decode to fail-closed holding "
                "-> declared PASS is a semantic contradiction"
            )
    if fid.startswith("FIXTURE-RESTART-UNSAFE-DEDUP-001"):
        # Negative control (Agent Commons Lab 4-cell demand, 8/9): dedup-before-
        # auth with a stale grant must NOT be absorbed as an idempotent replay —
        # digest-valid but the semantics demand FAIL/REJECTED (zero sink, no
        # egress). A declared PASS here is the exact failure mode the 4-cell
        # matrix exists to catch.
        evs = ev if isinstance(ev, dict) else {}
        if evs.get("dedup_before_auth") and evs.get("grant") == "stale":
            return "FAIL", (
                "dedup-before-auth absorbs stale grant -> declared PASS is the "
                "unsafe dedup variant (must reject, zero sink, no egress)"
            )
    return None, None


def check_semantics(row):
    expected, reason = semantic_verdict(row)
    if expected is None:
        return True, None
    declared = row.get("terminal_verdict")
    if declared == expected:
        return True, None
    return False, (
        f"semantic mismatch: {row.get('fixture_id')} declares {declared} "
        f"but provenance semantics derive {expected} ({reason})"
    )


def verify_manifest(manifest: dict):
    """Verify envelope + row digest chain. Returns (ok, report_lines)."""
    lines = []
    ok = True

    envelope = manifest.get("envelope", {})
    expected_manifest_digest = envelope.get("manifest_digest")
    envelope_canonical = jcs(envelope.get("payload", {})).encode("utf-8")
    actual_manifest_digest = sha256_hex(envelope_canonical)
    lines.append(f"envelope manifest_digest: declared={expected_manifest_digest}")
    lines.append(f"                            computed={actual_manifest_digest}")
    if expected_manifest_digest and expected_manifest_digest != actual_manifest_digest:
        lines.append("  ✗ envelope manifest_digest mismatch")
        ok = False
    else:
        lines.append("  ✓ envelope manifest_digest matches")

    # Candidate view (spec 7b): concurrent candidates share the same parent BEFORE
    # CAS adjudication. They are validated individually against their declared
    # parent (candidate_admission_id = canonical bytes digest), but are NOT part
    # of the committed chain — chain positions are written only after CAS.
    candidates = manifest.get("concurrent_candidates", [])
    for i, row in enumerate(candidates):
        declared = row.get("row_digest_ref")
        row_core = {k: v for k, v in row.items() if k != "row_digest_ref"}
        canonical = jcs(row_core).encode("utf-8")
        parent = row.get("parent_digest_ref") or envelope.get("header_digest")
        computed = sha256_hex(parent.encode("ascii") + canonical)
        ok_i = declared == computed
        lines.append(
            f"candidate[{i}] {row.get('fixture_id', '?')}: digest {'✓' if ok_i else '✗'}"
            f" (parent={parent[:16]}...)"
        )
        if not ok_i:
            ok = False
        sem_ok, sem_msg = check_semantics(row)
        if not sem_ok:
            lines.append(f"  ✗ {sem_msg}")
            ok = False

    parent_digest = envelope.get("header_digest")
    rows = manifest.get("rows", [])
    for i, row in enumerate(rows):
        declared = row.get("row_digest_ref")
        # Fork rejection: parent_digest_ref (if present) must equal the canonical
        # predecessor (the digest this row was chained from). Any other parent
        # means a fork or non-canonical parent selection -> reject.
        declared_parent = row.get("parent_digest_ref")
        if declared_parent is not None and declared_parent != parent_digest:
            lines.append(
                f"row[{i}] {row.get('fixture_id', '?')}: ✗ non-canonical parent "
                f"(declared={declared_parent}, expected={parent_digest})"
            )
            ok = False
        # Self-referential digest: canonical form excludes the row_digest_ref
        # field itself (the field holds the result, it is not part of the input).
        row_core = {k: v for k, v in row.items() if k != "row_digest_ref"}
        canonical = jcs(row_core).encode("utf-8")
        chain_input = (parent_digest or "").encode("ascii") + canonical
        computed = sha256_hex(chain_input)
        status = "✓" if declared == computed else "✗"
        verdict_ok = row.get("terminal_verdict") in VERDICTS
        lines.append(
            f"row[{i}] {row.get('fixture_id', '?')}: digest {status}"
            f" (declared={declared}, computed={computed})"
        )
        if declared != computed:
            ok = False
        if not verdict_ok:
            lines.append(f"  ✗ terminal_verdict not in 5-value set: {row.get('terminal_verdict')}")
            ok = False
        sem_ok, sem_msg = check_semantics(row)
        if not sem_ok:
            lines.append(f"  ✗ {sem_msg}")
            ok = False
        parent_digest = computed

    return ok, lines


def main():
    ap = argparse.ArgumentParser(description="CD-4c fixture validator")
    ap.add_argument(
        "--manifest",
        default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "fixtures",
            "examples",
            "manifest.json",
        ),
        help="path to fixture manifest JSON (default: repo-root fixtures/examples/manifest.json)",
    )
    ap.add_argument(
        "--nfc",
        action="store_true",
        help="opt in to NFC preprocessing (Unicode UAX#15) with non-NFC rejection",
    )
    args = ap.parse_args()
    if args.nfc:
        opt_in_nfc(True)

    try:
        with open(args.manifest, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except OSError as e:
        print(f"error: cannot read manifest: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: manifest is not valid JSON: {e}", file=sys.stderr)
        return 2

    ok, lines = verify_manifest(manifest)
    print(f"manifest: {args.manifest}")
    print("\n".join(lines))
    print("RESULT: " + ("ALL ROWS VERIFIED" if ok else "VERIFICATION FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
