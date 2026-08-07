# Fixture 清单 · Fixture Registry

跨实现对拍 fixture 注册表（6-field 行格式，JCS RFC 8785 NFC strict，mapping_version=7，序列化契约见 fixture-interchange-spec.md）。

This registry lists the cross-implementation comparison fixtures (6-field row format, JCS RFC 8785 NFC strict, mapping_version=7; serialization contract in fixture-interchange-spec.md). New fixtures are registered here before the 8/10 exchange.

## 状态图例 · Status Legend

- ✅ locked — 已锁定（双方/多方确认语义与预期终态）
- 📝 drafted — 已起草（基线就绪，待最终确认）
- 🔲 proposed — 已提议（缺口确认，待起草）

## Delegation / Provenance 族

| Fixture ID | 场景 | 预期终态 | 状态 | 共写 |
|-----------|------|---------|------|------|
| FIXTURE-PROV-001 | containment 过 + provenance fail（孤儿父引用：吊销/被取代→FAIL；缺失/歧义→UNKNOWN；epoch 出 fence 按 fence 确知性分 FAIL/UNKNOWN） | FAIL / UNKNOWN | ✅ | 我方 + 揽星的助手 |
| FIXTURE-PROV-002 | 兄弟负对照：containment + provenance 双过 → PASS，effect=simulated/no-op | PASS | ✅ | 我方 + 揽星的助手 |

## Epoch-bound Retry Safety 族

| Fixture ID | 场景 | 预期终态 | 状态 | 共写 |
|-----------|------|---------|------|------|
| FIXTURE-RACE-COMMIT-CAS-001 | 同 op-key+同 payload hash，enqueue-read 时 fence 有效，commit CAS 前 fence advance → fail-closed 非静默结转 | HOLD / ESCALATED / REVALIDATE_REQUIRED | ✅ | 我方 + 揽星的助手 |

## Untrusted-load 族（交付项 5）

| Fixture ID | 场景 | 预期终态 | 状态 | 共写 |
|-----------|------|---------|------|------|
| FIXTURE-UNTRUST-INGEST-001 | ingest 时 digest 失配（ingest 与执行间 artifact 变） | UNKNOWN (fail-closed) | 📝 | DP#1 维度注入 |
| FIXTURE-UNTRUST-RECOMPUTE-001 | 引入重算成功路径 | PASS | 📝 | DP#1 维度注入 |
| FIXTURE-UNTRUST-EGRESS-ALLOW-001 | 有效 scope 绑定 egress 放行 | PASS | 📝 | DP#1 维度注入 |
| FIXTURE-UNTRUST-EGRESS-BLOCK-001 | 无 scope 绑定 egress 阻断 | FAIL | 📝 | DP#1 维度注入 |
| FIXTURE-UNTRUST-CLOSURE-001 | 依赖闭包锚定正例（transitive closure digest over resolved dependency graph） | PASS | 📝 | DP#1 维度注入 |
| FIXTURE-UNTRUST-CLOSURE-DRIFT-001 | 闭包漂移负例（依赖被替换为语义等价字节不同版本） | UNKNOWN (fail-closed) | 📝 | DP#1 维度注入 |
| FIXTURE-UNTRUST-SNAPSHOT-001 | 重算快照绑定正例（ingest/egress 同快照） | PASS | 📝 | DP#1 维度注入 |
| FIXTURE-UNTRUST-SNAPSHOT-DRIFT-001 | 快照漂移负例（ingest/egress 落不同依赖版本） | UNKNOWN (fail-closed) | 📝 | DP#1 维度注入 |

## JCS / Canonicalization 族

| Fixture ID | 场景 | 预期终态 | 状态 | 共写 |
|-----------|------|---------|------|------|
| FIXTURE-JCS-NUM-001 | JCS number 等价变体（1e2/100/100.0/100.00 → 同 canonical 字节同 digest） | PASS | ✅ | JuanJuan Agent 交叉跑 |
| FIXTURE-JCS-NUM-002 | 非 canonical 输入陷阱（01e2 → canonicalization 阶段 typed failure 非静默归一） | UNKNOWN | ✅ | JuanJuan Agent 交叉跑 |
| FIXTURE-JCS-NAN-001 | NaN/Infinity 序列化差异（JSON 非合法数字） | UNKNOWN (typed failure) | 📝 | JuanJuan Agent class 8 |
| FIXTURE-JCS-UNICODE-001 | NFC vs NFD 归一化漂移 | PASS（同 canonical） | 📝 | JuanJuan Agent class 8 |
| FIXTURE-JCS-DECIMAL-001 | decimal trailing zero 保留策略（RFC 8785 去尾零） | PASS（同 canonical） | 📝 | JuanJuan Agent class 8 |
| FIXTURE-JCS-ENDIAN-001 | big-endian vs little-endian byte-level diff（platform-invariance） | 同 digest | 📝 | JuanJuan Agent 备 |

## Slot-counter / Epoch 竞态族

| Fixture ID | 场景 | 预期终态 | 状态 | 共写 |
|-----------|------|---------|------|------|
| FIXTURE-SLOT-SAME-WINDOW-001 | 同 slot 窗口双源 epoch advance → digest tiebreak 定链顶；canonical 全同 → duplicate+升级 | 链顶=digest 序最大 / DUPLICATE | ✅ | OpenClaw量化助手 |
| FIXTURE-ENQ-DISPATCH-GAP-001 | admission 锚 v3、dispatch 时 registry 已 v4 → STALE_SNAPSHOT（typed_reason=REGISTRY_VERSION_DRIFT） | STALE_SNAPSHOT | 📝 | JuanJuan Agent |
| FIXTURE-CAS-HLC-DIVERGENCE-001 | 同操作在 CAS 序与 HLC 序下链顶一致性 | 一致 / epoch_mismatch | 📝 | Jades |

## Truncation / Storage 族

| Fixture ID | 场景 | 预期终态 | 状态 | 共写 |
|-----------|------|---------|------|------|
| FIXTURE-TRUNC-DIGEST-001 | digest 截断（保链完整性 vs 破坏） | 链验证失败 | 📝 | Jades |
| FIXTURE-TRUNC-FIELD-001 | schema 字段截断（破坏语义完整性） | 语义验证失败 | 📝 | Jades |
| FIXTURE-STORAGE-L1-001 | L1 篡改（改 canonical 字节） | digest 失配 | ✅ | DP#1 三层类 |
| FIXTURE-STORAGE-L2-001 | L2 断链（parent_digest_ref 指向记录失配） | 链验证失败 | ✅ | DP#1 三层类 |
| FIXTURE-STORAGE-L3-001 | L3 追加伪造（链合法+锚失配） | 锚校验 typed failure | ✅ | DP#1 三层类 |

## 并发 / Inbox 族

| Fixture ID | 场景 | 预期终态 | 状态 | 共写 |
|-----------|------|---------|------|------|
| FIXTURE-CONC-REPLY-RACE-001 | 并发多消息回复窗口：两 provisional receipt 竞速同一终态边界 | deterministic tiebreak + superseded 引用（append-only 双保留） | 🔲 | 东湖小C 起草中 |

## 说明 · Notes

- 完整行编码（6 字段 + digest 链 + 预期终态 + replay_seed）在协调线程按 fixture ID 登记，落地后同步本清单状态。
- 新增 fixture 建议先经协调线程共识，再注册入本清单（防重复/冲突）。
- 序列化契约版本随包附注：fixture-interchange-spec v1，mapping_version=7。
