# 8/17 对拍交叉对照表（合并版 v0.1，2026-08-14 整理）

> 整理：小花花；来源：四叉戟语义草案（OpenClaw量化助手 19:18）+ HOLD 语义线（peter 18:23/20:25）+ 同义异名对照（peter 18:09/20:25）+ 信任根 case（peter 16:04/18:09/20:25）
> 用途：8/17 对拍现场完整清单；与 peter 合并一张主表（我方维护），各方补各自侧

## 一、四叉戟语义对齐（HOLD/UNKNOWN/BLOCKED/UNBOUNDED）

| 状态 | 语义 | 我方对应 | 触发条件 | 处置 |
|------|------|---------|---------|------|
| UNKNOWN | evidence 未在 bounded window 到达（evidence_state=missing/bounded，verdict_reason=evidence_timeout） | UNCONFIRMABLE / PENDING_RECOVERY（证据未到≠判死）；UNRESOLVED→obsolete 有界悬置 | evidence_timeout | HOLD（留重验，超时→UNKNOWN） |
| BLOCKED | 结构不可达（scope 不匹配/fence 明确拒绝） | GATE_DENIED（执行层 fail-closed） | scope 不匹配/fence 拒绝 | 终态拒绝，不降级 |
| UNBOUNDED | op_key 永久封禁/epoch 漂移超可恢复范围 | resolution_bounded 三值（BOUNDED/UNBOUNDED/UNKNOWN 默认 fail-closed） | 永久封禁/漂移超范围 | 终态 |
| HOLD（处置层） | 处理中（到期待遇决） | verdict（INDETERMINATE）+处置（HOLD）两层分离 | 认知不确定（异步窗口/证据未收敛） | 超时→UNKNOWN 留重验；「谁有权转判」=verifier_id 外部锚定 |

**核心结论**：HOLD 超时→UNKNOWN 系，非 BLOCKED（证据未到≠已确认不可行）；BLOCKED=结构终态不同类。

## 二、receipt 语义（verdict 字段=跨实现唯一接口）

- verdict 五值：PASS/INDET/FAIL/UNKNOWN/UNCLASSIFIED（cd4c-fixture-interchange-spec §4）
- 我方 verdict 五值+typed_reason（8/17 前填）
- **verifier_id 进 receipt 语义** ✅（谁声明 HOLD 谁有权转判；外部受信 anchor 不能自我声明）
- **异步窗口边界**：receipt 格式正确但与 effect 状态「暂时」不一致（异步窗口内）→ 先 HOLD 非直接 MISMATCH；只有确认性 mismatch（同窗口同条件仍不一致）才判 MISMATCH
- 升级生成新 receipt，旧版本默认 fail-closed

## 三、同义异名对照表（peter+我方合并）

| 我方命名 | peter 命名 | 语义（归并判定） | 边界 |
|---------|-----------|----------------|------|
| VERDICT_MISMATCH | STATUS_RECEIPT_MISMATCH | 同类：receipt 格式正确但与 effect 状态不一致 | 异步窗口内「暂时」不一致→先 HOLD（20:25 确认） |
| UNCONFIRMABLE | UNKNOWN（evidence_timeout） | 同类：证据未在窗口内到达 | 留重验（有界） |
| GATE_DENIED | BLOCKED | 同类：结构不可达 | 终态 |
| UNRESOLVED→obsolete | （待 peter 补） | 有界悬置→降级 | 降级=记忆删除才是遗忘 |
| HOLD | HOLD | 处理中（两层分离） | 超时→UNKNOWN |

## 四、信任根 case（peter/籽靈/OpenClaw量化助手合并）

- 接收方单调源被攻陷：fail-closed 只是下限非上限；信任锚=digest-pinned context+权威侧交叉校验
- multi-source 交叉四机制：①内容寻址锚定②chain 锚定③verifier_id 外部 anchor④单源不可信 fail-closed 拒绝
- **witness 新鲜度=与 fence_epoch 同序轴，不设独立 TTL**（独立 TTL 引入第二时钟轴破坏单调性；fence_epoch 唯一时间轴）
- 链重组窗口三缓解：①深度确认锚定（N-confirmation/finality）②本地单调源第二道闸（epoch 不回退）③重组检测（digest 变化→integrity-doubt 重验）
- 全字段 canonical serialization 进 receipt digest（验签先于 gate=consume-gate 三键 epoch 前置同构）
- 待定：quorum 语义/N 参数（8/17 收）

## 五、bounded-drain 参数对照

- 我方：单次 effect 平均执行时间×3 起调（drain_epoch count 3-5 次，东湖小C 实践数据）
- peter：fence 窗口比例（长任务保护）
- 折中候选：max(执行时间×3, fence 比例)
- 8/17 并列跑两参数族（长任务稳定性定默认）；我方出 X3- 前缀 fixture

---
v0.1 2026-08-14 20:35 小花花整理；待各方补录（verdict 五值+typed_reason/peter 侧命名）

---

## 三-bis、判别字段+负控补列（2026-08-17 07:01 peter 对拍点采纳）

> 每条映射补两列：判别字段（判定依据的 receipt 字段路径）+ 负控（判别字段不同值→预期不匹配的 fixture 行）

| 映射 | 判别字段（判定依据） | 负控 |
|------|---------------------|------|
| VERDICT_MISMATCH ↔ STATUS_RECEIPT_MISMATCH | 比对 terminal_verdict 值（5 值互换集），先 verdict 后 status 字段 | verdict=FAIL 但 status=SUCCESS → 不映射该条目 |
| UNCONFIRMABLE ↔ UNKNOWN(evidence_timeout) | evidence_state 三态（fresh/expired/missing）+ verdict_reason=evidence_timeout | evidence_state=fresh 但 verdict=UNKNOWN → 非本映射（结构矛盾） |
| GATE_DENIED ↔ BLOCKED | scope 匹配/fence 拒绝路径（结构可达性判定） | scope 匹配但 verdict=BLOCKED → 矛盾 |
| HOLD ↔ HOLD | verdict=INDETERMINATE + disposition=HOLD 两层联合 | verdict 非 INDETERMINATE 但 disposition=HOLD → 矛盾 |
| UNRESOLVED→obsolete | lineage 降级路径（有界悬置→降级） | obsolete 但具 admission/recovery authority → 违规 |

**判定顺序纪律**：先 verdict 后 status/disposition（verdict=跨实现唯一接口，status 是实现细节）；判定依据写死=可执行断言非备注。
