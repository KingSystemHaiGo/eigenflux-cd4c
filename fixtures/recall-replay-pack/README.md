# FIXTURE-RECALL-STALE-FACT-001 — 机器可重放包（公开发布版）

**发布性质**：公开 artifact，供独立重放/复算/衍生/对拍。本包对应 oracle v0.3（
`notes/fixtures/FIXTURE-RECALL-STALE-FACT-001/recall-stale-fact-oracle-v03.md`）。

## 元数据

| 项 | 值 |
|---|---|
| schema / canonicalizer version | canonicalizer v1（JCS RFC 8785 + NFC 强制；UTF-8 + LF） |
| 编码 | raw UTF-8 + LF（每行一个 JSON 对象，无 BOM） |
| per-row SHA-256 | `sha256sums.txt`（逐行原始字节，含行尾 LF） |
| full-file SHA-256 | `3476157a3b31a0f1bab29bf2aa3ac1d5b84e183e3dea90de52ea8f9110cca89b` |
| SPDX license | CC0-1.0（public domain dedication，供复算/衍生/对拍） |
| oracle | v0.3（双 digest：genesis_atom_id=fork 检测器 / identity=rewrite 检测器；四断言 + 负控） |
| 固定 commit | 见本目录 git 提交（pinned commit） |

## 行清单

| # | id | type | expected |
|---|---|---|---|
| 1 | PC-RECALL-001 | positive-control | T_execution_authority=BLOCKED, T_recall_plain_path=BLOCKED, T_audit_reachable=true |
| 2 | NEG-RECALL-001 | negative-control | T_recall_plain_path=BLOCKED, T_audit_reachable=true |
| 3 | NEG-RECALL-001-MW1 | negative-control-missing-witness（缺 coverage_boundary） | INDETERMINATE → HOLD |
| 4 | NEG-RECALL-001-MW4 | negative-control-expired-time-window（三见证齐全但 time_window 过期） | INDETERMINATE → HOLD |

### MW4 语义说明

MW4 与 MW1-3（缺字段）不同：三见证字段**都在**，但 `time_window=[T0,T0+30d]` 且
`now=T0+31d`——覆盖声明已过期（与 freshness_window 30d 联动，memsys v0.5 §6）。
预期：coverage_verdict → EXPIRED → 重验触发 → INDETERMINATE → **HOLD**（fail-closed，
绝不静默保持 ABSENT）。测「字段齐全但值过期」路径，比字段缺失更隐蔽
（陈旧不可发现：显式失效标记优先于隐式猜测）。

## Expected transition（PC / NEG / MW 全链）

- PC-RECALL-001：AUTHORITY_REVOKED → tombstone → recall 路径 BLOCKED
  （recall_authority 保可见 / execution_authority BLOCKED，双权威轴，memsys v0.6 §10）
- NEG-RECALL-001：同输入 → plain path BLOCKED + audit reachable（tombstone ≠ compaction）
- MW1/MW4：missing/expired witness → INDETERMINATE → HOLD（fail-closed 不假绿）
- 终态全链：revoked → superseded → compensate（disposition=COMPENSATE 或 UNCOMPENSABLE 二选一，
  防 old-state revival；TOMBSTONE 无 reverse transition，8/10 锁定）

## Denominator（如实声明）

**无现成分母实证**——本包为 fixture 级验证（独立复跑/重放判定 PASS/FAIL），
非成本统计。revalidation cost 度量（重探频率/cohort aging curve/悬置期限超期率）
为设计层观测指标，需专门跑批；8/17 后列为 oracle spec 数据收集项。
**在独立重放完成前，本 artifact 相关声明保持 AUTHOR_REPORTED 级别。**

## 复算方式

```bash
# 逐行重放（任一 JSON 行 → canonical bytes → 对照 expected）
python3 tools/jcs_canonical_gen.py recall-replay-pack.jsonl  # 或等价 JCS RFC 8785 实现
# 逐行 SHA-256 校验
sha256sum -c sha256sums.txt
```
