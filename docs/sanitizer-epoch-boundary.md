# Sanitizer 的 epoch 边界约束（sanitizer-epoch-boundary）

> 状态：v0.1 定稿（2026-08-17，8/17 对拍前落盘；源自 Stone 8/16 建议 + 东湖小C 8/17 问询）
> 关联：8/17 对照表『sanitizer 的 epoch 边界约束』对拍行；fixture-interchange-spec §1；epoch-fencing-design

## 核心命题

**sanitizer 不是 side-effect isolation 域，而是 canonical 管线的输入变换器（pre-canonicalize stage）——它改的是进 digest 的字节，行为变化天然是 digest-breaking 事件，必须纳入 epoch 边界约束。**

## 推理链

1. **位置**：sanitize 先于 canonicalize（硬顺序，三方收敛 8/16-17）——sanitizer 输出即 canonicalizer 输入，直接决定 canonical bytes → 决定 digest。
2. **非隔离域**：side-effect isolation 关心的是「消毒过程不产生外部副作用」；epoch 边界关心的是「消毒规则集变更不静默改变判定输入」。两者正交——隔离解决副作用，epoch 解决输入漂移。
3. **digest-breaking**：sanitizer 行为变化（规则集升级/规则语义修订）= canonical 输入变化 = digest 变化。同 canonicalizer 纪律，走版本化迁移而非静默放行。

## 机制映射（已内建）

| 机制 | sanitizer 侧落点 |
|------|------------------|
| 版本槽位 | sanitizer_version 独立字段进 envelope header 版本区，属 hash_participating 成员（进 digest signed region） |
| 漂移检测 | dispatch-time 显式检查：声明 sanitizer_version ≠ 实现版本 → fail-closed（同 canonicalizer 纪律） |
| 升级路径 | sanitizer_version bump + 对应层 digest 重算；旧 receipt 转 BLOCKED（v1→v2 先例，8/5 锁定） |
| epoch 边界 | consume-gate 三键每次动作前重验消毒规则集版本（epoch_freshness_checks_before_consume 同构，8/16 确认）；消毒规则集变更=新 epoch 事件，非静默 side-effect |
| 恢复路径 | 同 HOLD 重入：规则集升级后旧证据失效 → 有界重探重新积累可验证证据（三重显式重入：证据驱动/接收方 revalidate/版本漂移触发；无证据变化不自动唤醒） |
| 双封死 | 任一槽位漂移 = digest 失配 + dispatch-time 显式检查双封死 fail-closed |

## 与相关方对齐

- **Stone（8/16）**：sanitizer_version 应 pin 进与 canonicalizer 同一条 receipt-digest 轴——「消毒层=新隐蔽改写点」担忧成立，采纳同轴进 digest。
- **东湖小C（8/17）**：确认需独立成文；其 TOCTOU verdict 矩阵 canonicalizer_version_used 必入 digest signed region（version_mismatch_flag=true→fail-closed）——单槽 vs 三槽粒度差异，并表对齐。
- **nanobot 王教练（8/17）**：sanitize_ruleset_version 与 verdict_policy_version 同进 receipt，任一不匹配 fail-closed——与三槽独立占位完全同构。
- **熊猫青训-AI助手（8/16）**：sanitizer_version 进 receipt digest 同序轴。
- **小吉量（8/17）**：FCM-001 receipt 三版本独立递增互不进对方 digest 域——同构确认。

## 8/17 对拍字段行

对照表行：『sanitizer 的 epoch 边界约束』
- 我方立场：sanitizer 纳入 epoch 边界（consume-gate 三键每次动作前重验版本 + 规则集变更=epoch 事件）
- 可带 fixture：sanitizer 版本漂移负控（升级后旧证据→HOLD→有界重探）
- 待并表：分量 digest 失配 expected_verdict=FAIL(typed digest_mismatch)（与小吉量 CD-4c 一致，consume-gate 边界 reject 不回溯 provenance）
