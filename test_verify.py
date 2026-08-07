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


def main():
    r = run(MANIFEST)
    assert r.returncode == 0, f"positive manifest should verify, got exit {r.returncode}\n{r.stdout}"
    print("✓ positive manifest verifies")

    m = json.load(open(MANIFEST, encoding="utf-8"))
    tampered = [dict(row) for row in m["rows"]]
    tampered[1]["terminal_verdict"] = "PASS"  # meaning-changing tamper
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

    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
