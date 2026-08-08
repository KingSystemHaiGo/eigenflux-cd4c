#!/usr/bin/env python3
"""JCS RFC 8785 canonical JSON serializer with self-tests.

Canonical contract (matches tools/verify.py core subset):
  - object keys sorted by UTF-16 code units
  - RFC 8785 string escaping: \b \t \n \f \r short forms for the five named
    control characters; \\uXXXX (lowercase hex) for all other U+0000..U+001F
  - numbers via ES6 Number::toString semantics (Decimal fixed-point, trailing
    zeros stripped, -0 -> 0) — NOT Python json.dumps float formatting
  - no NFC normalization by default (RFC 8785 does not mandate it); NFC is an
    explicit opt-in extension, never silent normalization
"""
import json
from decimal import Decimal


def _escape(s: str) -> str:
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
        if n == 0:
            return "0"
        return _jcs_decimal(Decimal(repr(n)))
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


def _sort_key(k):
    """RFC 8785: lexicographic order by UTF-16 code units."""
    return k.encode("utf-16-le")


def canonicalize(obj) -> str:
    """JCS RFC 8785 canonical serialization (core subset)."""
    if isinstance(obj, dict):
        items = sorted(obj.items(), key=lambda kv: _sort_key(kv[0]))
        return "{" + ",".join(f"{_escape(k)}:{canonicalize(v)}" for k, v in items) + "}"
    if isinstance(obj, list):
        return "[" + ",".join(canonicalize(v) for v in obj) + "]"
    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (int, float, Decimal)):
        return _jcs_number(obj)
    if isinstance(obj, str):
        return _escape(obj)
    raise TypeError(f"unsupported type: {type(obj)}")


if __name__ == "__main__":
    tests = [
        ("empty object key order", {"b": 1, "a": 2}, '{"a":2,"b":1}'),
        ("number 1e2 vs 100", 1e2, "100"),
        ("float formatting", 100.0, "100"),
        ("float 1.50 trailing zeros", 1.50, "1.5"),
        ("negative zero", -0.0, "0"),
        ("control chars short forms", {"s": "\n\t\r\b\f"}, '{"s":"\\n\\t\\r\\b\\f"}'),
        ("other control char escaped", {"s": "\x01"}, '{"s":"\\u0001"}'),
        ("surrogate pair", "\U0001F600", '"\U0001F600"'),
        ("nested arrays", [1, [2, 3], {"c": 1, "b": 2}], '[1,[2,3],{"b":2,"c":1}]'),
    ]
    for name, obj, expected in tests:
        got = canonicalize(obj)
        ok = got == expected
        print(f"{'PASS' if ok else 'FAIL'} {name}: {got}")
        if not ok:
            raise SystemExit(1)
    print("ALL TESTS PASSED")
