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
import sys
import unicodedata
from decimal import Decimal

# --- JCS RFC 8785 canonicalization (core subset) -----------------------------

def _jcs_number(n):
    """RFC 8785 number serialization: integers without exponent/leading zeros,
    decimals with trailing zeros stripped, -0 normalized to 0."""
    if isinstance(n, bool):
        return "true" if n else "false"
    if isinstance(n, int):
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
    # NFC normalization per RFC 8785
    s = unicodedata.normalize("NFC", s)
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


def jcs(value):
    """Canonical JSON serialization per JCS RFC 8785 (core subset)."""
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

    parent_digest = envelope.get("header_digest")
    rows = manifest.get("rows", [])
    for i, row in enumerate(rows):
        declared = row.get("row_digest_ref")
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
        parent_digest = computed

    return ok, lines


def main():
    ap = argparse.ArgumentParser(description="CD-4c fixture validator")
    ap.add_argument("--manifest", required=True, help="path to fixture manifest JSON")
    args = ap.parse_args()

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
