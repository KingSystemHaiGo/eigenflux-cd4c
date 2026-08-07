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

- 链规则：`row_digest = SHA-256(parent_digest_ref ‖ current-row canonical bytes)`。
- `parent_digest_ref` 指**父行的 row_digest**（非 manifest digest）。
- 首行 parent = **envelope header digest**。
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

## 5. 开销收据（overhead-receipt，每 fixture 一个）

```
{fixture_id, wall_time_ms, receipt_chain_length, evidence_anchor_ops,
 measurement_context{hardware_class, concurrency, epoch_window, jcs_version},
 overhead_digest}
```

- 入链（parent digest ref + canonical bytes → SHA-256）——归一化漂移 = digest 失败，非静默分歧。
- measurement_context 使跨实现比较诚实（墙钟仅同硬件类可比）。

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
