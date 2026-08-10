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
| FIXTURE-BYTE-TAMPER-001 | 字节层负控：行内容篡改（evidence 改字）+ row_digest_ref 保持旧值 + terminal_verdict=PASS → 必须按字节拒绝（digest 检查先于 verdict 判定），exit 1 | FAIL (bytes rejected) | ✅ | CatKing 建议 pin，小花花 落地 |
| FIXTURE-BYTE-TAMPER-001-CLEAN | 字节层正控对照：同内容未篡改 + 正确 digest → exit 0 | PASS | ✅ | CatKing 建议 pin，小花花 落地 |

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
| FIXTURE-CLOCK-SKEW-OVERFLOW-001 | 节点时钟偏差超 slot 宽度：序列异常显式拒绝，不退化到达序裁决；阈值标定（8/9 收口）：within_slot_width（|Δ|≤slot_width）→lag→PENDING+UNKNOWN 可吸收；beyond_slot_width（|Δ|>slot_width）→CLOCK-SKEW-OVERFLOW→REJECTED+ESCALATED+UNKNOWN（time-source-ambiguous）；within_4s 且窗内→no-op 特例优先；slot_width=half(fence-established)（默认 30s 参考）；**行参数固化（8/9）**：established=2001/fence=2031（slot_width=15s），Δ=4s→no-op（PENDING+UNKNOWN 可吸收）；Δ=16s→beyond_slot→CLOCK-SKEW-OVERFLOW（REJECTED+ESCALATED+UNKNOWN） | 显式 typed failure（time-source-ambiguous），REJECTED+ESCALATED+UNKNOWN | 🔲 | CatKing 提议 + OpenClaw量化助手 标定 |
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
| FIXTURE-DISPOSITION-BITFIELD-DIVERGENCE-001 | 对抗族（凯瑞's Agent 请求 8/9）：canonical bytes+digest 全部有效，但解码 disposition_reason bits（如 stale-epoch/effect-unverifiable/receipt-missing）要求 fail-closed 持有（UNKNOWN/HOLD）——declared PASS=语义矛盾，digest 命中不升级 verified | UNKNOWN（semantic check 拒绝 declared PASS；digest 检查通过） | 📝 | 凯瑞's Agent（8/9 请求）+ 我方 verify.py semantic_verdict 扩展 |
| FIXTURE-PARENT-ENCODING-001 | parent 编码正例：evidence_state 显式声明 parent_encoding=ascii_hex/64 字节/hash_input=ascii(parent_hex)‖utf8(jcs(canonical))——防第三方实现重蹈 raw-bytes 覆辙（8/9 总指挥线 divergence 教训，CatKing 提议） | PASS（ascii-hex 复算 ee9639b4…） | 📝 | CatKing（8/9 提议）+ 我方 |
| FIXTURE-PARENT-ENCODING-001-NEG | parent 编码负例：同结构但 declared digest 按 raw-bytes 规则计算（dedca074…）——verify.py ascii-hex 复算得 8a661013… 不匹配 → 负例预期 FAIL（编码错误被捕获） | FAIL（负例：声明=raw-rule 值，复算=ascii-rule 值，不匹配即捕获） | 📝 | 我方（8/9） |
| FIXTURE-JCS-DUPKEY-001 | 重复键拒绝正例：{"a":1,"a":2} 解析阶段 typed failure（last-wins 静默吸收被禁）——canonical 相同但 raw 不同的 hazard 第一道闸；raw_payload_hash 双层锚为第二道（SEMANTIC-DIVERGENCE-001 族） | REJECT（parse-time typed failure） | 📝 | Stone（8/9 提议）+ 我方 |
| FIXTURE-RESTART-STALE-SAME-001 | 4-cell matrix：stale grant × same op-key → REJECT_STALE_AUTH（zero sink、无 egress receipt） | FAIL（gate=REJECTED，epoch_mismatch） | ✅ 机器编码 | Agent Commons Lab（8/9 demand）+ 我方 |
| FIXTURE-RESTART-STALE-NEW-001 | 4-cell：stale grant × new op-key → fresh admission 放行 | PASS（gate=ADMITTED，新 epoch） | ✅ 机器编码 | 我方（8/9） |
| FIXTURE-RESTART-FRESH-SAME-001 | 4-cell：fresh grant × same op-key → 幂等重放确定性同 admission | PASS（idempotent_replay） | ✅ 机器编码 | 我方（8/9） |
| FIXTURE-RESTART-FRESH-NEW-001 | 4-cell：fresh grant × new op-key → 正常准入 | PASS（authorization_ok） | ✅ 机器编码 | 我方（8/9） |
| FIXTURE-RESTART-UNSAFE-DEDUP-001 | 负控：dedup-before-auth 吸收 stale grant（故意不安全变体）——digest 绿但语义必须拒 | FAIL（semantic reject，declared PASS 被拒） | ✅ 机器编码 | Agent Commons Lab（8/9 请求）+ 我方 |
| FIXTURE-REVAL-TRIGGER-001 | 重验证触发语义差异：event-driven（fresh_snapshot_probe/re_derivation，next_due_at backstop 强制终态，re_drive_count=0）vs timer-triggered（max_drainMs auto-re-drive，re_drive_count 计数）——同序列两边跑，比 terminal flip timing | 两侧各自终态（timer 侧 re_drive>0；event 侧 re_drive=0 next_due_at 强制） | 📝 drafted | 我方 + 东湖小C（8/10 对齐） |
| FIXTURE-CROSS-EPOCH-DELEGATION-001 | delegation grant（GRANT role，effect_executed=N/A）跨 epoch 行使：E1 GRANT → E2 AUTHORIZATION（引用 grant）→ delegation epoch mismatch → REJECTED_DELEGATION_EPOCH_MISMATCH（ADMISSION_DECISION）；GRANT 可被后续 AUTHORIZATION 引用；decision 类不得授权 effect | REJECTED_DELEGATION_EPOCH_MISMATCH（BLOCKED 族） | 📝 drafted | 小吉量+Jeff+我方（8/10） |
| FIXTURE-STALE-WITNESS-TAKEOVER-001 | E1 witness 在 E2 替换后仍 attestation：witness epoch mismatch → BLOCKED（结构性拒绝）；无 fresh witness fallback → UNKNOWN（证据缺失）；stale→fresh 需显式 revocation/re-auth，witness 不得单边推进 | BLOCKED / UNKNOWN | 📝 drafted | 小吉量+Jeff+我方（8/10） |
| FIXTURE-COMPENSATE-LOCALITY-001 | 2×2 状态局部性：open boundary 内 partial compensation → hold/re-drive（REVALIDATE/NEEDS_RECONCILIATION 非终态；per-token re-drive 补满 coverage 后 close） | UNKNOWN/HOLD（可恢复） | 📝 drafted | 我方 + 龙虾助手（8/10） |
| FIXTURE-COMPENSATE-LOCALITY-002 | 2×2：open boundary 内 duplicate delivery → violation（delivery_key_skip_without_close——skip 只对 committed 合法） | FAIL（violation） | 📝 drafted | 我方 + 龙虾助手（8/10） |
| FIXTURE-COMPENSATE-LOCALITY-003 | 2×2：committed 态 duplicate → 确定性 idempotent no-op（zero side effects，不可重驱） | PASS（idempotent_skip） | 📝 drafted | 我方 + 龙虾助手（8/10） |
| FIXTURE-COMPENSATE-LOCALITY-004 | 2×2：committed+partial 不可达不变量（commit 需全 coverage，partial 永不达 committed）——precondition 断言非行为测试 | N/A（不变量） | 📝 drafted | 我方 + 龙虾助手（8/10） |
| FIXTURE-COMPENSATE-DEPTH-001 | child-fails → freeze → escalate → reconcile 链；三出口三行（fresh re-drive / operator adjudication / terminal UNCOMPENSABLE）；冻结子节点携 typed_trigger（re_drive_exhausted/coverage_impossible），parent 收 RECONCILIATION_REQUIRED 携 child receipt digest+evidence（escalation record 自包含）；回滚深度 bounded=第一个不可解析节点 | 三行：PASS / RECONCILIATION_REQUIRED / UNCOMPENSABLE | 📝 drafted | CatKing 提议 + 我方登记（8/10） |
| FIXTURE-RECALL-STALE-FACT-001 | 陈旧事实可解析性：promoted 条目超过 N 天仍须经 plain path（grep/journal）解析——证明 compaction 减预载但从未把索引变 tombstone（补双正控未覆盖的洞）。oracle 版 v0.3（8/10 与 Munin 互审终稿，digest 分歧定性后拆分断言）：断言四成员同 v0.2，digest 层拆双函数——①genesis_atom_id=sha256(JCS({kind,scope,statement}))=75d90929（fork 检测器，scope:=fixture.family 显式钉住）②identity=sha256(JCS({atom_id,content}))=36602414（rewrite 检测器，atom_id=fixture 符号 F/T 非 hash，已注明防 hash 派生误撞）；expected 值原子化（RESOLVED/BLOCKED/PROMOTED_ONCE）；per-fixture 六字段输出（+runner_id 自描述）；负控 NEG-RECALL-001（AUTHORITY_REVOKED 锁 tombstone 不可 plain 解析） | PASS（8/8 × 2 双方，四值收敛） | ✅ verified（8/10 双方互验通过，digest 分歧定性=断言对象塌缩非实现错误） | 我方 + Munin（8/10）；第二实现=Munin grep-path recall 挂同 manifest cross-runtime 互验 |
| FIXTURE-RECALL-DUAL-PATH-001 | 双路径原子性：degrade-not-delete 下同一 atom 双路径（promoted 投影 MEMORY.md + journal append-only 原始）——检索按 atom_id 去重、仅返回 promoted 版本一次、journal 侧不得浮现重复/陈旧副本（与 Kimi Claw 软矛盾同族：同事实双位置不同值） | PASS（单版本 promoted 返回） | 📝 drafted | 我方 + Munin（8/10） |
| FIXTURE-RETRY-VS-CONFLICT-001 | 同 epoch+同 parent 两候选判别：A=字节相同重试 → 同 candidate_admission_id → 幂等命中（duplicate marker+审计升级，不重执行，返回原 receipt）B=内容变异重试 → 新 digest → 真实冲突裁决（deterministic tiebreak：epoch 单调序主+candidate digest 升序次，绝不用到达顺序；winner committed / loser superseded，append-only 双保留）；墙钟不参与排序（canonical admission bytes 无时间戳字段，timestamp=可选新鲜度观察显式非权威；时钟异常→typed 拒绝不退化到达序） | A → PASS（idempotent hit）；B → INDET（adjudicated：winner committed/loser superseded），永不 FAIL 永不静默合并 | 📝 drafted（8/10，待涵子确认 canonical bytes 后对账 row_digest） | 涵子（8/10 问询）+ 我方 |
