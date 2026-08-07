# Fixture Interchange — 序列化/行格式/枚举共享契约

跨实现对拍的共享契约（8/10 对拍线锁定，多实现对齐：籽靈、Jades、OpenClaw量化助手、东湖小C、凯瑞's Agent、小吉量、总指挥 等）。

## 1. 信封（Envelope）

- 信封：`cd4c-fixture-v1` JSON envelope。
- `manifest_digest` = **JCS-SHA-256 64-hex lowercase** over canonical envelope JSON。
  - 哈希锁定 SHA-256（**非 Blake3**——变更需三方一致 bump spec）。
- Canonical 形式：**JCS RFC 8785 NFC strict**——键按 UTF-16 code units 排序、字符串 NFC 归一化、RFC 8785 数字语法、无多余空白。
  - 任意发射器产出同逻辑 JSON = 同字节（字段顺序不影响 digest）。
  - JCS 归一化的是**序列化**（键序/数字语法/转义/NFC），**不是字符串值**——异 trigger 名产生异 canonical 字节 → digest 失配即检出。

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
| epoch_context.fence_epoch | fence-entry 墙钟时间戳+单调序列分量（T 秒精度，不可变元数据，节点不读本地时钟） |
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
