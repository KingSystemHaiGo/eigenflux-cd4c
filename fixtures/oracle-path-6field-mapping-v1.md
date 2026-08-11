# FIX-005 v0.3 oracle_paths ↔ 6-field 行映射表（定稿 v1）

对拍对：Minis（/var/minis/shared/eigenflux/collab/）+ 小花花（eigenflux-cd4c）。
规则：每个 oracle 断言 → 一行 6-field；一个断言只约束一个不变量 → 一行只承载一个 verdict，不合并维度。
行格式：{row_digest_ref, terminal_verdict, mapping_version, epoch_context{fence_epoch, stage}, typed_trigger, evidence_state, replay_seed}（mapping_version=7）。

## verdict 映射（Minis 侧 → 我方 5 值集，7→5 单向，缺失映射=行验证失败）

| Minis 侧 | 我方 | 备注 |
|---|---|---|
| pass | PASS | |
| fail | FAIL | |
| UNVERIFIED（凯瑞语义） | INDET | 已判定但不确定，非 FAIL |
| 未跑 | UNKNOWN | 无证据，fail-closed 持有 |
| 范围外 | UNCLASSIFIED | 分类法盲区终态 |
| （Minis 侧无） | — | 不反向投影，缺省=行失败 |

## oracle_paths 样本（Minis 提供，9 路径）→ 6-field 行

| # | oracle_path | 预期 verdict | typed_trigger（按场景） | evidence_state | 说明 |
|---|---|---|---|---|---|
| 1 | oracle.expected_retrieval_set.default_recall_at_t1 | PASS | —（无触发） | fresh | 窗内（+72h）可解析 |
| 2 | oracle.expected_retrieval_set.default_recall_at_t7 | PASS | — | fresh | 窗内（+7d）可解析 |
| 3 | oracle.expected_retrieval_set.default_recall_at_t73 | PASS | — | fresh | 窗外（+31d）进审计层≠消失 |
| 4 | oracle.expected_audit.journal_contains | PASS | — | fresh | 审计日志含目标条目 |
| 5 | oracle.expected_audit.appended_only | PASS | — | fresh | 仅追加，无改写 |
| 6 | oracle.expected_audit.no_double_promotion | PASS | — | fresh | 双路径按 atom_id 去重仅一次 |
| 7 | oracle.expected_execution_verdict[0].allowed | PASS | — | fresh | 执行允许 |
| 8 | oracle.expected_execution_verdict[1].allowed | PASS | — | fresh | 执行允许（第二场景） |
| 9 | oracle.negative_control.action | FAIL | invariant_check（负控触发） | fresh | NEG 侧：AUTHORITY_REVOKED→BLOCKED，audit 可达 |

注：负控行 verdict=FAIL 是**设计终态**（同 manifest_neg.json 纪律：declared FAIL 必须 exit 0；declared PASS 必须 exit 1）。

## row_digest 链（双方认可）

- row_digest = SHA-256(parent_ascii_64hex ‖ JCS(current row canonical bytes))，parent_ascii=父行 digest 的 64 字符小写 hex（非 raw binary）。
- 对账时先对 row_digest 链 → 定位「哪一行分歧」，再对 verdict（FIX-005 对账同款纪律）。
- JCS RFC 8785 + UTF-8/LF + NFC opt-in（tools/verify.py）。
