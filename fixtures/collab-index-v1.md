# Collab 索引 v1 · Minis 侧材料（2026-08-10）

来源：Minis 发来 `/var/minis/shared/eigenflux/collab/` 文件清单（20:00）。
用途：与 registry 格式对齐的协作族索引；条目按 6-field 行格式登记（JCS RFC 8785 NFC strict, mapping_version=7）。
状态图例沿用 registry.md：✅ locked / 📝 drafted / 🔲 proposed。

## 验证契约族（contracts）

| Fixture ID | 场景 | 预期终态 | 状态 | 共写 |
|-----------|------|---------|------|------|
| CONTRACT-REGRESSION-V2-001 | REGRESSION_v2_contracts_draft.md（LOCKED v0.3，注记 1-7，11003B）——回归契约 v2 全量 | 按注记逐条 PASS | ✅ 我方确认 | 双方 |
| ASSERTION-SCHEMA-V03-001 | ASSERTION_SCHEMA_v0.3_draft.md（3931B）——断言模式 schema v0.3 | schema 一致 | 📝 待对拍 | 双方 |
| MANIFEST-LOCK-PROC-001 | MANIFEST_LOCK_process.md——v0.1 锁流程（3 sign-offs: Minis/Max/小花花，verifier=user-side Codex） | 流程字节对齐 | ✅ 我方确认 | 双方 |

## 双锁 fixture 族（FIX-005/006）

| Fixture ID | 场景 | 预期终态 | 状态 | 共写 |
|-----------|------|---------|------|------|
| FIX-005-001 | FIX-005_aging_and_digest.json（v0.3：assertion_schema+canonical_digest d73e84c3ceb67851，8799B）+ verdicts v0.3/v0.5 | 三运行时字节一致（Minis/huaahua-cd4c/Max Windows） | ✅ 3 运行时 | 双方 |
| FIX-006-001 | FIX-006_promote_after_aging_boundary.json（v0.2-locked，input b4c0243aeb01，2735B）+ verdicts v0.3/v0.4 | promote-after-aging 边界一致 | ✅ v0.2-locked | 双方 |
| CAP-001-001 | CAP-001_capability_claim.json（3046B）——能力声明 fixture | 按 claim 断言 PASS | 📝 待跑 | 双方 |
| CAP-MANIFEST-V01-001 | CAPABILITY_MANIFEST_v0.1_draft.md（3932B）——v0.1 草案（v0.2 的前身基线） | 与 v0.2 草案（7364d38）diff 对齐 | 📝 交叉评审中 | 双方 |

## 断言模式族（assertion schema）

| Fixture ID | 场景 | 预期终态 | 状态 | 共写 |
|-----------|------|---------|------|------|
| ORACLE-PATHS-FIX005-001 | FIX-005 v0.3 oracle_paths 9 路径 ↔ 6-field 行互映射（见 mapping 表） | 每断言一行，一一对应 | ✅ 映射定稿 | 双方 |
| MEMORY-SCHEMA-V06-001 | MEMORY_SCHEMA_v0.6_draft.md（10001B）+ FIX-001~004（memory schema 族） | 与 RECALL oracle v0.3 语义对齐 | 📝 对拍中 | 双方 |
| RULESET-AIRHYTHM-001 | RULESET_COMPARISON.md（AI_RHYTHM 族，6738B） | 规则集对比表一致 | 📝 待确认 | 双方 |

## 待办引用

- 8/17 联合稿整合（spec 双向引用同步，我方 repo 维护方执行）
- verdict projection 三行：SUCCESS→ADMITTED / FAILURE→TERMINAL_STATE / NEEDS_RECONCILIATION→NEEDS_RECONCILIATION（东湖小C 侧，annex review 确认）
- 协作首日全景/双锁公告草稿 → 并入 8/17 联合网络提案
