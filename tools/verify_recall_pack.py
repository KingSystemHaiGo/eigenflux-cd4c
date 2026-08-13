#!/usr/bin/env python3
"""recall-replay-pack verifier — digest 域校验（2026-08-13 暖暖复核 EVIDENCE-EXPIRED-002 修正）。

规则（canonicalizer v1 契约）：
  1. per-row digest 域 = canonical bytes（JCS RFC 8785 key-sorted + NFC）
  2. 对每行 JSON: canonicalize → sha256(canonical bytes) 对照 sha256sums.txt 声明
  3. raw/canonical mismatch 时 FAIL（不静默）：若某行 raw bytes != canonical bytes，
     则声明必须匹配 canonical（不允许 raw 口径混入）；否则 FAIL
  4. full-file sha256 对照（字节未变时全文 digest 不变）
Exit codes: 0 = all rows verified, 1 = verification failure
"""
import hashlib, json, sys, unicodedata, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jcs_canonical_gen import canonicalize

def nfc(obj):
    if isinstance(obj, str):
        return unicodedata.normalize('NFC', obj)
    if isinstance(obj, dict):
        return {nfc(k): nfc(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [nfc(x) for x in obj]
    return obj

def main():
    pack_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fixtures', 'recall-replay-pack')
    jsonl = os.path.join(pack_dir, 'recall-replay-pack.jsonl')
    sums = os.path.join(pack_dir, 'sha256sums.txt')

    with open(jsonl, 'rb') as f:
        raw_full = f.read()
    with open(jsonl, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = [l for l in content.split('\n') if l.strip()]

    # full-file check
    full_d = hashlib.sha256(raw_full).hexdigest()
    declared_full = '3476157a3b31a0f1bab29bf2aa3ac1d5b84e183e3dea90de52ea8f9110cca89b'
    print(f"full-file sha256: computed={full_d}")
    ok = True
    if full_d != declared_full:
        print(f"  [FAIL] full-file digest mismatch (declared {declared_full})")
        ok = False
    else:
        print(f"  [OK] full-file digest matches")

    # per-row canonical digest check
    print("\nper-row canonical digest (digest domain = CANONICAL bytes):")
    for i, line in enumerate(lines):
        obj = json.loads(line)
        rid = obj.get('id', f'line{i}')
        canon = canonicalize(nfc(obj))
        canon_d = hashlib.sha256(canon.encode('utf-8')).hexdigest()
        raw_d = hashlib.sha256(line.encode('utf-8')).hexdigest()
        raw_matches_canon = (line == canon)
        print(f"  {rid}: canonical={canon_d[:16]}... raw={raw_d[:16]}... key_sorted={raw_matches_canon}")

    # compare with declared sha256sums.txt (canonical domain)
    print("\nsha256sums.txt declaration check (canonical domain):")
    declared = {}
    for dl in open(sums, 'r', encoding='utf-8'):
        dl = dl.strip()
        if not dl or dl.startswith('#'):
            continue
        parts = dl.split()
        if len(parts) >= 2:
            declared[parts[1].replace('(canonical)', '').strip()] = parts[0]

    for i, line in enumerate(lines):
        obj = json.loads(line)
        rid = obj.get('id', f'line{i}')
        canon_d = hashlib.sha256(canonicalize(nfc(obj)).encode('utf-8')).hexdigest()
        decl = declared.get(rid)
        if decl is None:
            print(f"  [FAIL] {rid}: no declaration in sha256sums.txt")
            ok = False
        elif decl == canon_d:
            print(f"  [OK] {rid}: declared matches canonical")
        else:
            # raw/canonical mismatch → FAIL（不静默）
            raw_d = hashlib.sha256(line.encode('utf-8')).hexdigest()
            print(f"  [FAIL] {rid}: declared={decl[:12]}... != canonical={canon_d[:12]}... (raw={raw_d[:12]}...) — digest domain violation")
            ok = False

    print(f"\nRESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
