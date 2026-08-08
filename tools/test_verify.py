#!/usr/bin/env python3
"""Self-test for tools/verify.py: positive manifest must verify, tampered negative
control must fail. Run: python3 tools/test_verify.py"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "fixtures", "examples", "manifest.json")


def run(manifest_path):
    return subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "verify.py"), "--manifest", manifest_path],
        capture_output=True,
        text=True,
    )


def _recompute(m):
    """Recompute the full digest chain (envelope header + each row), preserving
    byte integrity, so only the semantic gate can catch a verdict change."""
    import sys as _sys
    _sys.path.insert(0, os.path.join(ROOT, "tools"))
    from verify import jcs, sha256_hex  # noqa: E402

    env = m["envelope"]
    env_digest = sha256_hex(jcs(env["payload"]).encode("utf-8"))
    env["header_digest"] = env_digest
    env["manifest_digest"] = env_digest
    parent = env_digest
    for row in m["rows"]:
        core = {k: v for k, v in row.items() if k != "row_digest_ref"}
        row["row_digest_ref"] = sha256_hex(parent.encode("ascii") + jcs(core).encode("utf-8"))
        parent = row["row_digest_ref"]
    return m


def main():
    r = run(MANIFEST)
    assert r.returncode == 0, f"positive manifest should verify, got exit {r.returncode}\n{r.stdout}"
    print("✓ positive manifest verifies")

    m = json.load(open(MANIFEST, encoding="utf-8"))

    # (a) Meaning-changing tamper WITHOUT digest recompute: proves tamper rejection.
    tampered = [dict(row) for row in m["rows"]]
    tampered[1]["terminal_verdict"] = "PASS"
    m["rows"] = tampered
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(m, f)
        tmp = f.name
    try:
        r = run(tmp)
        assert r.returncode == 1, f"tampered manifest should fail, got exit {r.returncode}\n{r.stdout}"
        print("✓ tampered negative control detected (exit 1)")
    finally:
        os.unlink(tmp)

    # (b) Semantic gate isolation: flip FIXTURE-PROV-001-NEG verdict to PASS and
    # RECOMPUTE the full digest chain, so byte integrity is preserved — only the
    # semantic assertion (orphaned provenance derives UNKNOWN) may reject it.
    m2 = json.load(open(MANIFEST, encoding="utf-8"))
    for row in m2["rows"]:
        if row.get("fixture_id") == "FIXTURE-PROV-001-NEG":
            row["terminal_verdict"] = "PASS"
    m2 = _recompute(m2)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(m2, f)
        tmp = f.name
    try:
        r = run(tmp)
        assert r.returncode == 1, (
            f"semantic-only tamper should fail, got exit {r.returncode}\n{r.stdout}"
        )
        assert "semantic mismatch" in r.stdout, (
            f"expected semantic mismatch in output, got:\n{r.stdout}"
        )
        print("✓ semantic gate isolated (recomputed digests intact, verdict rejected)")
    finally:
        os.unlink(tmp)

    print("ALL TESTS PASSED")


def test_ijson_int_core_reject():
    """>2^53 integers must be a typed failure (fail-closed), never silently
    serialized with precision loss (I-JSON gap closure, 8/9)."""
    import sys as _sys

    _sys.path.insert(0, os.path.join(ROOT, "tools"))
    from verify import IJSON_INT_LIMIT, _jcs_number  # noqa: E402

    # In-range: serialized exactly.
    assert _jcs_number(IJSON_INT_LIMIT) == str(IJSON_INT_LIMIT)
    assert _jcs_number(-IJSON_INT_LIMIT) == str(-IJSON_INT_LIMIT)
    assert _jcs_number(0) == "0"
    assert _jcs_number(42) == "42"

    # Out-of-range: typed failure, never silent coercion.
    for bad in (IJSON_INT_LIMIT + 1, -(IJSON_INT_LIMIT + 1), 2**53, -(2**53), 10**30):
        try:
            _jcs_number(bad)
        except ValueError as e:
            assert "I-JSON" in str(e) or "fail-closed" in str(e), e
        else:
            raise AssertionError(f"expected ValueError for out-of-range int {bad}")
    print("✓ >2^53 integer core reject (fail-closed typed failure)")


if __name__ == "__main__":
    main()
    test_ijson_int_core_reject()
