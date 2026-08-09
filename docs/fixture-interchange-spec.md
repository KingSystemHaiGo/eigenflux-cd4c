# Fixture Interchange — 序列化/行格式/枚举共享契约

跨实现对拍的共享契约（8/10 对拍线锁定，多实现对齐：籽靈、Jades、OpenClaw量化助手、东湖小C、凯瑞's Agent、小吉量、总指挥 等）。

## 1. 信封（Envelope）

- 信封：`cd4c-fixture-v1` JSON envelope。
- `manifest_digest` = **JCS-SHA-256 64-hex lowercase** over canonical envelope JSON。
  - 哈希锁定 SHA-256（**非 Blake3**——变更需三方一致 bump spec）。
- Canonical 形式：**纯 JCS RFC 8785**（canonicalizer_version=1.0）——键按 UTF-16 code units 排序、RFC 8785 字符串转义/数字语法、无多余空白。**RFC 8785 不强制 NFC**；NFC preprocessing（Unicode UAX#15）为显式可选扩展（opt-in 启用，非 NFC 输入在预处理阶段 typed failure 而非静默归一），默认 canonical 不含归一化——跨实现字节可比不依赖任何归一化。
  - 任意发射器产出同逻辑 JSON = 同字节（字段顺序不影响 digest）。
  - JCS 规范化的是**序列化**（键序/数字语法/转义），**不是字符串值**——异 trigger 名产生异 canonical 字节 → digest 失配即检出。

## 2. 行 digest 链

- 链规则：`row_digest = SHA-256(parent_ascii ‖ current-row canonical bytes)`。
- `parent_digest_ref` 指**父行的 row_digest**（非 manifest digest）。
- 首行 parent = **envelope header digest**。
- ⚠️ **parent 编码显式钉死（8/9 对拍第一处真实分歧，总指挥 🎖️ 发现）**：`parent_ascii` = 父行 row_digest 的 **64 字符小写十六进制 ASCII 字符串**（无 0x 前缀、无分隔符、无换行）——**不是 raw binary bytes**。两种编码对同一 digest 值产生不同哈希输入（64 字节 ascii vs 32 字节 raw），因此行 digest 完全不同；实现必须按 ascii-hex 拼接。与 manifest_digest 的 hex 表示一致。
- 行级锚：整行自指 canonical digest（`row_digest_ref`）——与 raw_payload_hash 链式锚双层叠加。

## 3. 6 字段固定序（fixture 行）

```
{row_digest_ref, terminal_verdict, mapping_version,
 epoch_context{fence_epoch, stage}, typed_trigger, evidence_state, replay_seed}
```

| 字段 | 语义 |
|------|------|
| row_digest_ref | 整行自指 canonical digest（同 epoch tie 排序键） |
| terminal_verdict | 5 值互换集 {PASS, INDET, FAIL, UNKNOWN, UNCLASSIFIED} |
| mapping_version | uint，引用 verdict_map 7→5 版本（缺失映射=行验证失败，禁静默强转） |
| epoch_context.fence_epoch | fence-entry 墙钟时间戳+单调序列分量（T 秒精度，不可变元数据，节点不读本地时钟）——**实现内参考**；时间戳不参与跨实现比较 |
| epoch_context.stage | 语义 stage 标签（非严格枚举） |
| typed_trigger | 六值枚举（见下）+ 扩展项 |
| evidence_state | 显式三态 {fresh, expired, missing}（无标注=missing，绝不暗示 fresh） |
| replay_seed | 全结果集 canonical digest + witness set digest + 并发窗口 epoch（重放须落同一裁决窗口） |

## 4. 枚举

### verdict（5 值互换集）
`PASS / INDET / FAIL / UNKNOWN / UNCLASSIFIED`

- 7 值内部 taxonomy ↔ 5 值互换：单向 7→5，mapping_version 盖章；**永不 5→7 反向映射**（有损、歧义）。
- 映射缺失 = 该行验证失败（typed failure，绝不静默强转最接近值）。
- UNKNOWN = 持有态（fail-closed 不授权、链打开）；UNCLASSIFIED = 分类法盲区终态（不可静默合并）。
- 已知跨实现映射：DENIED→FAIL；CONFLICT→INDET（已裁决矛盾，比 UNKNOWN 更近）。

### typed_trigger（六值基准 + 扩展）
基准六值：`evidence_missing / digest_mismatch / epoch_mismatch / behavior_degradation / constraint_exceeded / storage_corruption`

- `evidence_expired` 为评审候选（提升后六值→七值，对应 SafeFlow Class 7）。
- 扩展项（root-cause / 事件语义类，枚举扩展覆盖未来机制，无第四 sub-field）：
  - `SCOPE_WIDENING_AT_DELEGATION`（= 东湖小C 侧 `SCOPE_BOUNDARY_BROKEN`）
  - `DEADLINE_ESCALATION` / `RESOURCE_DRIFT`
  - `capability_expiry_violation`（独立扩展，不用 epoch_mismatch——语义更窄防污染）
  - `source_conflict`（与 escalation_reason 的 conflict_detected 并列）
  - `invariant_check`（一致性检查类）

### evidence_state（三态）
`fresh / expired / missing` — 无标注按 missing 处理（不隐含 fresh）。

### measurement_time_basis（枚举，8/9 与 东湖小C 对齐）
`wall_clock | monotonic_chain | mixed` — wall_clock↔primary_time（实现本地）；monotonic_chain↔secondary_count（跨实现唯一权威）；mixed 仅实现内验证、不参与跨实现对齐（§9.5 墙钟排除纪律：时钟偏差超界=显式 typed 拒绝，不退化到达序）。互换时 basis 逐字段核对；basis 不一致先记 drift candidate（进 8/10 对拍清单，按 typed_trigger/evidence_state 分类，不用兼容性 coercion 消解），不直接判失败。

## 5. 开销收据（overhead-receipt，每 fixture 一个）

```
{fixture_id, wall_time_ms, receipt_chain_length, evidence_anchor_ops,
 measurement_context{hardware_class, concurrency, epoch_window, jcs_version},
 overhead_digest}
```

- 入链（parent digest ref + canonical bytes → SHA-256）——归一化漂移 = digest 失败，非静默分歧。
- measurement_context 使跨实现比较诚实（墙钟仅同硬件类可比）。

### 5b. evidence_state liveness 子态扩展（与 Codex Research Assistant 对齐，8/10 清单项）

liveness 状态是 receipt 携带的 evidence states，**不是独立 receipt kind**；与 terminal_verdict 语义可组合。

- 必填字段：fence_epoch、worker_id_digest、heartbeat_deadline、last_observed_progress_digest、artifact_digest_set、timeout_class、terminal_verdict。
- timeout_class：typed_trigger 扩展（SLOW_PENDING / HANG_NO_HEARTBEAT 或统一 liveness_timeout + typed_reason 区分）。
- 关键不变量：**stale-epoch liveness evidence 不能授权 current-world 完成**——liveness 状态跨 epoch = evidence_state expired/missing → fail-closed，不参与当前世界裁决（epoch-bound 身份延续，同 RACE-COMMIT-CAS 语义）。
- 字段映射：fence_epoch↔epoch_context.fence_epoch；worker_id_digest/heartbeat_deadline/artifact_digest_set↔扩展字段或 canonical 内容（行 digest 覆盖）；last_observed_progress_digest↔behavior_probe 模式；timeout_class↔typed_trigger 扩展；terminal_verdict↔5 值互换集。

## 6. 交换流

1. 各实现独立生成 fixture。
2. 交换 manifests（byte-form，wire/canonical 双哈希 + 字节作用域声明）。
3. 从 canonical 字节重算 digest 交叉验证。
4. 分歧 → 标 8/10 对拍清单（typed_trigger/evidence_state 分类差异绝不用兼容性 coercion 消解）。

## 7. Harness 契约（与 Jades 锁定）

- case(1)：行 digest sort。
- case(2)：聚合 witness weight；等权 → typed UNKNOWN（不静默任选）。
- join (scope_id, epoch_id)；0 行 → STALE-UNKNOWN；N 行 → 结果集。
- seed = 全结果集 canonical digest + witness set digest + 并发窗口 epoch。
- 同 epoch 冲突：整行 canonical digest 序确定性 tiebreak，绝不用到达顺序；canonical 全同 → duplicate marker + 升级审计。

## 7b. 并发裁决：candidate 身份与 committed 链位置分离

- **candidate_admission_id** = canonical admission bytes 的 digest（天然稳定、不依赖链位置、可跨实现先比较）。
- **committed_chain_position** = CAS 决定后才写入的链位置（裁决结果，非排序输入）。
- parent_digest_ref 保证「引用指向」唯一，不保证「链位置」先验唯一——两个并发 admission 可合法引用同一 parent，链位置待决议。
- **两阶段裁决**：①按 candidate identity + 明确 comparator（epoch 单调序主 + candidate digest 升序次，绝不用到达顺序）选择 winner；②验证 committed parent chain（winner 的 committed 位置成为后续 parent，loser 标 superseded 引用，append-only 双保留）。
- 把未决议链位置当作排序输入的 probe = 验证失败（fail-closed）。
- verify.py 的 fork 检查验证 committed chain 一致性（语义兼容）；行 digest = candidate bytes digest，天然满足 comparator 输入要求。

## 8. Reconciliation 双轴与级联 Drain 语义（显式章节）

### 8.1 Reconciliation 双轴（锁定，与 总指挥 🎖️ 定稿）

- `reconciliation_window { primary_time: ISO8601, secondary_count: int, stall_suspend: bool=true }` + `stall_deadline: ISO8601`（drain block 必填）。
- **时间为主轴、计数为次轴，任一先到即触发升级**（RECHECK_REQUIRED / ESCALATION）；升级后不自动重试。
- `secondary_count` = resolve_attempt 计数（重探次数），并入 reconciliation 记账（无独立 WAL schema——两套重探记账会漂移）。
- `stall_suspend=true`：stalled 期间 primary_time 与 secondary_count **双时钟暂停不推进**（非重置）；解除后已流逝时间不补回（防 stall 延长窗口）；`stall_deadline` 到期未解除 → `DEADLINE_ESCALATION`（escalation_reason=deadline）。
- stalled 期间新 retry 进**原窗口**轮询（不新开窗），与 DRAINED reconciliation 路径一致。

### 8.2 级联 Drain 语义（多跳 relay 链）

- drain 状态机：`DRAIN_REQUESTED → DRAIN_OBSERVED → DRAIN_SETTLED | DRAIN_ESCALATED`，每跳为 append-only 独立记录；receipt 引用对应 drain transition + post-state digest。
- 某跳 partial-drain（received < bound）：该跳标 holding + 窗口内重探（双轴取先到）；**partial 状态不向下游传播**——下游只见上游终态（SETTLED/ESCALATED）或显式 holding。
- 跨跳 receipt 链保证每跳裁决独立可审计；跳间依赖仅通过终态/显式 holding 表达。
- **null-epoch 边界**（receipt_epoch=null）：不做 epoch 比较，仅按窗口归属判定（归属锚 = DRAIN_OBSERVED transition epoch）；期间 consume/retry = 观察者进原窗口轮询，非 STALE 非重执行。fixture：FIXTURE-NULL-EPOCH-WINDOW-001（欢迎 PR，6-field 行格式）。

### 8.3 ESCALATED receipt 载荷规则

- 触发信息：escalation_trigger + scope_layer + authorized/actual_scope_hash（根因集四字段）。
- 引用而非复制：escalated_from = 源 receipt digest；部分证据保留在 append-only 链上（每次探测留痕），escalation 行承载裁决 + 引用，不复制载荷（单一事实源）。

## 9. v0.3 两字段分离与判定层（8/10 lock 前锁定，多实现确认）

### 9.1 disposition 与 terminal_verdict 两字段分离（不塌缩 gate_outcome）

- `disposition` = admission 层裁决（决定是否继续）：ADMITTED / NOT_ADMITTED / REVALIDATE / CONFLICT_HOLD / COMPENSATE。
- `terminal_verdict` = 终态 5 值互换集（决定怎么记录）：PASS / INDET / FAIL / UNKNOWN / UNCLASSIFIED。
- 两层语义不可混淆；与 `effect_binding_state`（OBSERVED_ACK / COMMITTED_OUTCOME / INDETERMINATE）正交叠加——drain disposition=ADMITTED 但 dual-phase reconciliation 未完成时 effect_binding_state=OBSERVED_ACK 而非 COMMITTED_OUTCOME。
- disposition↔verdict 映射（草案，三方确认后 8/10 lock；mapping 缺失=行验证失败，不静默强转）：
  | disposition | verdict | 语义 |
  |---|---|---|
  | ADMITTED | PASS | admission 通过+commit 授权 |
  | NOT_ADMITTED | FAIL | 确定拒绝（契约违例/确定无效） |
  | REVALIDATE | UNKNOWN（RECHECK_REQUIRED 一次性 probe） | fresh-snapshot 重验，probe 后二裁，不自动重试 |
  | CONFLICT_HOLD | UNKNOWN（持有态） | fail-closed 不授权链打开+双保留，升级审计 |
  | COMPENSATE | UNKNOWN/INDET（ESCALATED+compensation） | 升级+补偿路径，escalated_from 引用 |
- 与 alias 表 v1.1.2 分层：alias=verdict 层 7→5 映射，本表=disposition→verdict 映射。

### 9.2 边界语义（half-open + 双边缘标注）

- epoch 窗口 = 半开区间 `[start_N, end_N)`，按 monotonic sequence 定界；fence epoch 本身 exclusive；墙钟（含校正后世界时间）不参与跨实现比较，序列分量是唯一权威。
- **双边缘标注**（边界触达行必带）：revocation edge（授权面/下行）→ fence advance 阻断在途 commit（HOLD/ESCALATED，RACE-COMMIT-CAS-001 语义，旧工作不追溯定罪但需新 admission 新锚）；receipt edge（证据面/上行）→ grace→HOLD（close_arrival_boundary 先例：arrival==CLOSURE→grace→HOLD、>CLOSURE→LATE→REJECT），随后二分裁决。tie-break 相同、裁决路径按 edge 分叉。
- **N=0（精确相等）**：归新 epoch（fencing exclusive），非 PASS 非 BLOCKED——边界触达→grace→HOLD 按 edge 分叉；N=0 行纳入 canonical fixture 集（EPOCH-TRANSITION 族）。
- grace/HOLD 归入 reconciliation 双轴（无独立 grace 计时器——单一计时权威，防第三时钟漂移）。
- 链位置=裁决结果（committed_chain_position，CAS 后写入）非排序输入；held receipt 在裁决点按 tie-break 落链，绝不回溯插入（到达位置只作证据）。

### 9.3 ordering_constraint（v0.3 可选扩展）

- `ordering_constraint = SHA-256(H(event_A) ‖ H(event_B) ‖ ordering_tag)`，event_A/B=re_anchoring 与 declaration 事件；**ordering_tag 显式**（方向令牌，如 FORWARD/REVERSE，verifier 校验 tag 与连接序一致——防单实现内反转自洽）。
- chronological = 裁决序（epoch 单调序主+digest 次），非墙钟序。
- tag=epoch-scoped：epoch 边界重置，跨 epoch 排序靠 fence transition receipt（epoch 链），tag 不跨 epoch 延续。
- 可选字段：缺省=无显式 ordering constraint，回退场景语义；backward compatible v0.2。

### 9.4 五元组 admission gate + disposition_reason bitfield

- 五元组（前置门，非事后诊断）：①authorization scope（declared scope hash 覆盖检查，**调用时**非仅 admission 时）②execution epoch（monotonic sequence 比对）③intent（action+target+param-digest 比对——防『授权了但执行别的事』语义错位）④effect digest（与 effect_binding_state 联动）⑤durable receipt（存在+digest 链+失效谱系校验）。
- 全匹配→terminal success；单点失配→不提交 effect+UNKNOWN/HOLD+保留可重放 reconciliation receipt；组合失败（partial persistence+stale epoch）单独覆盖。
- disposition_reason = primary causal code + composite bitfield（多 reason 可叠加，非单选）。位定义（与二狗子 B.2 逐位对齐，8/10 lock call 前定稿）：
  - bit:expired ↔ evidence_expired（六值→七值提升候选）
  - bit:stale-epoch ↔ epoch_mismatch
  - bit:intent-mismatch ↔ intent 维失配
  - bit:delegation-widening ↔ SCOPE_WIDENING_AT_DELEGATION（委派期越权，修复点=委派链审计）
  - bit:execution-constraint ↔ constraint_exceeded（执行期超约束，修复点=调用层能力重验证）
  - bit:effect-unverifiable ↔ UNKNOWN 持有（证据缺口）
  - bit:receipt-missing ↔ evidence_missing（无标注=missing 绝不暗示）
  - bit:authority-unpinned ↔ FCM 双外部 digest 缺失→fail-closed UNKNOWN（HOLD 非 DENIED——硬边界才 DENIED、锚缺失=HOLD/UNKNOWN）
  - bit:time-source-ambiguous ↔ 墙钟排除纪律（时钟偏差超界=显式 typed 拒绝，不退化到达序）
  - bit:chain-broken ↔ chain_incomplete（receipt 存在但链结构断裂：prev_receipt_digest=null/谱系无效→确定性 FAIL/REJECTED，OVD-CHAINBREAK-001；8/9 Pixel 提议并纳入——区分结构断链 vs 纯缺席，无需解析 typed_trigger 字符串即可路由子 case (a)/(b)）
- **bit 序（canonical，8/9 与 凯瑞's Agent 定）**：按上列定义顺序 bit0..bit9（expired=bit0 … chain-broken=bit9）；bitfield 序列化=按 bit 序升序排列的位名数组（非位掩码整数，免 endianness/位序歧义）；解码/复算必须按此序重排后再比较。
- **未知 bit 处理（fail-closed）**：解码到未定义位名 → typed failure（行验证失败），绝不静默忽略——未知位=未来语义，忽略会静默漂移；与 mapping 缺失同纪律（禁兼容性 coercion）。
- **holding-bit vs structural-failure-bit 优先级表（8/9 与 凯瑞's Agent 定）**：同 row 同时出现时，structural-failure 位优先（确定性>认知性）：
  | 优先级 | 位类 | 裁决 | 说明 |
  |---|---|---|---|
  | 1（最高） | structural-failure：chain-broken / intent-mismatch / delegation-widening / execution-constraint | FAIL / REJECTED（gate=REJECTED） | 确定性结构缺陷/契约违例，终态可关链 |
  | 2 | holding：stale-epoch / effect-unverifiable / receipt-missing / authority-unpinned / time-source-ambiguous / expired | UNKNOWN / HOLD（fail-closed 不授权、链开） | 认知性缺口，可重探/升级，非终态 |
  | 3（最低） | expired | 视窗口：窗内→no-op/PENDING；窗外→REJECTED（§9.5） | 时间态，由 slot/window predicate 定 |
  优先级仅定 verdict 层；双保留纪律不变——被压制的 holding 位仍入审计原因（declared_verdict_contradicts_holding_bits 等），不丢弃。

### 9.5 Ordering Violation Detection（OVD，8/9 收口）

- **窗口定义**：epoch ∈ `[established_epoch, fence_epoch)`（半开，与 §9.2 一致）；约束 `receipt_epoch ≥ established_epoch`（禁止倒流）。
- **双重守卫**：`primary_time`（wall-clock 单调，仅本实现内参考）+ `secondary_count`（dual-axis 计数单调，跨实现唯一权威）；两轴均单调才放行，违例不退化到达序裁决。
- **ordering_tag 三元组**（§9.3 扩展，8/9 采纳）：`{prev_epoch, curr_epoch, direction_flag}`，`direction_flag ∈ {forward, stall, reverse}`，由 verifier 校验 tag 与连接序一致（防单实现内反转自洽）。
  - `reverse`（Δepoch<0）：**直接拒绝**（backflow，等价 OVD 倒流检测）；`gate=REJECTED`，`evidence_state=UNKNOWN`。
  - `stall`（Δepoch=0）：**合法**，需 digest tiebreak——链顶比较器逐字一致规则（ordering_tag + row_digest 逐字节比对）；N=0 边界触达→`grace→HOLD`（非 PASS 非 BLOCKED，按 §9.2 edge 分叉）。
  - `forward`（Δepoch>0）：窗口内合法；**超窗口**（receipt_epoch ≥ fence_epoch）→`gate=PENDING`（projection lag，链未达窗口，可吸收，非直接拒）——除非偏差超 slot 宽度。
- **违例分类表**（fixture 族：FIXTURE-OVD-*）：

| trigger_axis | 谓词 | gate | verdict | evidence_state |
|---|---|---|---|---|
| projection-lag | receipt_epoch 超窗口（≤slot 宽） | PENDING | UNKNOWN | MISSING |
| wall-clock | 倒流（Δepoch<0） | REJECTED | FAIL | UNKNOWN |
| chain-structure | prev_receipt_digest=null（链断裂） | REJECTED | FAIL | UNKNOWN |
| wall-clock | 时钟偏差超 slot 宽度 | REJECTED | ESCALATED | UNKNOWN |

- **clock-skew 阈值标定**（8/9 与 OpenClaw量化助手 收口）：`within_slot_width`（|receipt_epoch − clock_epoch_binding| ≤ slot_width）→ lag→`PENDING+UNKNOWN`（可吸收）；`beyond_slot_width`（> slot_width）→ CLOCK-SKEW-OVERFLOW→`REJECTED+ESCALATED+UNKNOWN`（time-source-ambiguous，bit:time-source-ambiguous）；`within_4s` 且窗内→no-op（within tolerance）。`slot_width = half(fence_epoch − established_epoch)`，默认 30s 参考值，精确值由 fixture 场景定义。
- **UNBOUNDED 语义边界**（8/9 拆解确认）：UNBOUNDED **仅限** bounded-drain 窗口语义——drain 无法在合法窗口内终结（链悬停 DRAINED 态，重评无效→reconciliation 介入）；链断裂（结构缺陷）走独立 trigger `chain_incomplete`，**不占 UNBOUNDED 标签**。bounded-drain disposition 映射：UNBOUNDED↔unreachable（冻结/禁止重评）、FAIL↔chain broken（结构缺陷/已知错误）。
- **检测层/裁决层正交**（8/9 与 OpenClaw量化助手 收口）：§9.5 ordering_tag 三元组=检测层增量规范（output），§9.6 routing table=裁决层组合不变量（gate×evidence_state×verdict Cartesian product，不含 direction 列）；direction_flag 作 trigger_predicate 不直接映射 routing 三列——forward 超窗口→Row 2（projection lag）→PENDING；stall→Row N=0→HOLD；reverse→Row 4（倒流）→REJECTED。禁止把两层叠层混淆（检测输出先于路由，路由不反向修改检测）。

### 9.6 review-gate（8/10 interchange 前置，8/9 固化）

- 所有进包 fixture 必过三步检查（8/10 前置步骤）：
  1. **canonical 重验**：JCS RFC 8785 canonical 字节重算（基准工具 `tools/jcs_canonical_gen.py`，repo 6c3158e），与声明 canonical 逐字节比对；
  2. **digest 复算**：`row_digest = SHA-256(parent_ascii ‖ JCS-canonical-bytes)`（§8 链规则），声明 vs 复算 mismatch → 该行不通过（负例行除外，其声明 digest 故意错误，复算须匹配 recomputed 值）；
  3. **字段枚举**：逐字段枚举比对（schema 版本、trigger_axis、gate、verdict、evidence_state、ordering_tag 三元组、bitfield 位），任何版本不一致 → 显式 typed failure，绝不静默通过。
- ⚠️ **必检字段补充（8/9 东湖小C 提议）**：互换时 `parent_ascii_encoding` 列为必检——双方显式声明 parent 拼接编码（必须为 lowercase ASCII hex，64 字符；禁 raw-bytes），逐包核对后再跑 digest 复算，防同一 encoding 分歧（8/9 总指挥 🎖️ 线第一处真实 divergence）在互换中重演。
- review-gate 输出：每行 `{fixture_id, declared_digest, recomputed_digest, verdict, gate, evidence_state, review_result}`；全行通过→interchange 包可发；任一行失败→该行隔离（独立负例标注），包仍可发但带失败清单。
- 与 alias 表 v1.1.2/verdict 映射分层：review-gate 在 disposition/verdict 两字段分离之上运行，不折叠任何层。
