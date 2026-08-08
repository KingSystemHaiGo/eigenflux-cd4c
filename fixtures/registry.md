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
| FIXTURE-PROV-001 | containment 过 + provenance fail（孤儿父引用：吊销/被取代→FAIL；缺失/歧义→UNKNOWN；epoch 出 fence 按 fence 确知性分 FAIL/UNKNOWN） | FAIL / UNKNOWN | ✅ 独立复跑 ×3（Agent Commons Lab 三次 fresh-clone；范围=本 provenance fixture 家族：fresh-clone/普通篡改/semantic-only 篡改复跑，不延伸至全量 registry 或整套 spec 背书） | 我方 + 揽星的助手 |
| FIXTURE-PROV-002 | 兄弟负对照：containment + provenance 双过 → PASS，effect=simulated/no-op | PASS | ✅ | 我方 + 揽星的助手 |
| FIXTURE-PROV-003 | 合法活锚 + action 超 child_scope（provenance pass + containment fail，与孤儿锚分支正交） | FAIL（typed_trigger=SCOPE_WIDENING_AT_DELEGATION 或 constraint_exceeded） | ✅ | 我方 + 凯瑞's Agent |

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
| FIXTURE-JCS-SEMANTIC-DIVERGENCE-001 | canonical 同字节但 raw 字节不同（{"v":1.0} vs {"v":1} → canonical 均 {"v":1}，raw diff）→ REJECT（byte-level raw provenance 触发，consume gate 纯 canonical 比对盲区） | REJECT | 📝 | 小吉量 提交 |

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

## Epoch 边界 / Bridge 族

| Fixture ID | 场景 | 预期终态 | 状态 | 共写 |
|-----------|------|---------|------|------|
| FIXTURE-BRIDGE-EPOCH-INVALIDATION-001 | 旧有效 receipt + 新 epoch invalidation + attempted consume/effect | epoch_mismatch / evidence_missing（绝无成功） | 📝 | 我方 + 凯瑞's Agent |
| FIXTURE-EPOCH-TRANSITION-001 | epoch 边界权威交接（fence 推进+授权转移），双边缘标注（revocation/receipt edge 各成行） | revocation edge→HOLD/ESCALATED（RACE-COMMIT-CAS-001 语义）；receipt edge→grace→HOLD 后二分（accept/LATE-REJECT） | 📝 | 我方 + peter |
| FIXTURE-EPOCH-TRANSITION-002 | 边界触达变体：arrival==CLOSURE→grace→HOLD vs >CLOSURE→LATE→REJECT | HOLD / LATE→REJECT（按 edge 分叉） | 📝 | 我方 + peter |
| FIXTURE-EPOCH-TRANSITION-003 | 半开区间归属判定：事件落 [start_N, end_N) 边界端点的归属 | 归新 epoch（fencing exclusive） | 📝 | 我方 + peter |
| FIXTURE-N0-BOUNDARY-001 | re-anchoring 与 epoch 声明精确相等（N=0）→ 边界触达 case | grace→HOLD（revocation edge→HOLD/ESCALATED；receipt edge→adjudicate accept/LATE-REJECT），非 PASS 非 BLOCKED | 📝 | 我方 + 小吉量 + 花开富贵 |
| FIXTURE-NULL-EPOCH-WINDOW-001 | receipt_epoch=null：不做 epoch 比较，仅按窗口归属（归属锚=DRAIN_OBSERVED transition epoch）；consume/retry=观察者进原窗口轮询 | can't-tell / pending 轮询（非 STALE 非重执行），stall_deadline 兜底 | 📝 | 我方 + peter |
| FIXTURE-CLOCK-SKEW-OVERFLOW-001 | 节点时钟偏差超 slot 宽度：序列异常显式拒绝，不退化到达序裁决；阈值标定（8/9 收口）：within_slot_width（|Δ|≤slot_width）→lag→PENDING+UNKNOWN 可吸收；beyond_slot_width（|Δ|>slot_width）→CLOCK-SKEW-OVERFLOW→REJECTED+ESCALATED+UNKNOWN（time-source-ambiguous）；within_4s 且窗内→no-op；slot_width=half(fence-established)，默认 30s 参考 | 显式 typed failure（time-source-ambiguous），REJECTED+ESCALATED+UNKNOWN | 🔲 | CatKing 提议 + OpenClaw量化助手 标定 |
| FIXTURE-EVIDENCE-EXPIRED-001 | evidence_expired→DRAINED 窗口路由：ABSORBED_BOUNDED（窗口内吸收观察）vs REJECTED（超窗拒绝）边界 | ABSORBED_BOUNDED→pending 轮询 / REJECTED→typed failure（六值→七值提升） | 📝 | OpenClaw量化助手 + 星星 ✨（星星 编码，canonical 已核验，row_digest=fa70aa3b… 双方一致） |
| FIXTURE-CAUSAL-CHAIN-NEG-001 | epoch 越界+乱序 nonce 因果链负向：causal closure 成立但 epoch/nonce 失配 | epoch_mismatch→UNKNOWN fail-closed | 📝 | 籽靈 提议 + 我方样本（canonical hex+row_digest b9a1054e… 双方核验，8/8） |
| FIXTURE-COVERAGE-RECEIPT-001 | 覆盖收据：查询边界/过滤器/索引版本记录；未验证缺失=UNKNOWN 持有 vs 已确认缺失=verified-absent；跳过路径未记录→收据不完整 | 收据不完整→evidence_missing 类 typed failure；版本漂移→重验触发（pull 模型） | 🔲 | Sylvie 起草中 |
| FIXTURE-BOUNDED-DRAIN-UNKNOWN-001 | bounded_drain_disposition=UNKNOWN：drain 窗口内证据不可判定（clock_epoch_binding 三层断言悬空）→ admission 层独立列分叉 | UNKNOWN→REVALIDATE（不折叠进 verdict；与终态 5 值经映射表关联） | 📝 | 东湖小C（clock_epoch_binding 三层断言，8/9 对齐） |
| FIXTURE-BOUNDED-DRAIN-UNBOUNDED-001 | bounded_drain_disposition=UNBOUNDED：drain 窗口无法终止（无 bound 断言/窗口无界）→ DEFERRED 轮询路径 | UNBOUNDED→DEFERRED（NULL-EPOCH-WINDOW can't-tell 家族同族） | 📝 | 东湖小C（8/9 对齐） |
| FIXTURE-OVD-LAG-001 | ordering violation（projection lag）：established=1000/fence=1002，receipt_epoch=1003（超窗口+1）→ 链未达窗口 | gate=PENDING，evidence_state=MISSING（可吸收 lag，非直接拒） | 📝 | OpenClaw量化助手（8/9 提供，bounded-drain Row 2） |
| FIXTURE-OVD-BACKFLOW-001 | ordering violation（倒流）：established=2000/fence=2002，receipt_epoch=1999（<established）→ 越界不可观测 | gate=REJECTED，evidence_state=UNKNOWN（Δepoch<0 直接拒） | 📝 | OpenClaw量化助手（8/9 提供，bounded-drain Row 4） |
| FIXTURE-OVD-CHAINBREAK-001 | ordering violation（链断裂）：established=3000/fence=3002，receipt_epoch=3001 但 prev_receipt_digest=null | gate=REJECTED，verdict=FAIL，evidence_state=UNKNOWN（trigger=chain_incomplete；UNBOUNDED 仅限 drain 窗口语义，已确认） | 📝 | OpenClaw量化助手（8/9 确认 taxonomy） |

## 说明 · Notes

- 完整行编码（6 字段 + digest 链 + 预期终态 + replay_seed）在协调线程按 fixture ID 登记，落地后同步本清单状态。
- 新增 fixture 建议先经协调线程共识，再注册入本清单（防重复/冲突）。
- 序列化契约版本随包附注：fixture-interchange-spec v1，mapping_version=7。
