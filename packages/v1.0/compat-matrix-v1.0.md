# 组合矩阵正式版（Compat Matrix v1.0）— 三轴模型

> 创建：2026-08-16 ｜ 作者：小花花（CEO） ｜ 状态：正式版 v1.0（8/17 对拍前发布）
> 基线：v0.5 词表主轴（李晨熙 8/15 14:18 裁定）+ 每行一组合+合法性三态（东湖小C 提议采纳）+ pending_on/escalation_destination（OpenClaw量化助手 8/15 11:08 三点）+ 对账轴 PENDING 留轴+glossary 加注（李晨熙 v0.4 整合）
> 关联：Capability Manifest v0.2（60ee7af）、对拍包 v1.0（030d389）、8/16 报告（e332249）

---

## 1. compat_matrix_version

- **类型**：整型单调递增（mapping_version=7 先例，防 semver 字符串序陷阱）
- **当前版本**：`1`
- **语义**：矩阵变更=版本递增；receipt 携带 compat_matrix_version 作一等字段；未覆盖版本→UNKNOWN 不猜测（fail-closed）

## 2. 三轴模型（v0.5 词表主轴）

> 轴分离原则：**三轴可组合互不覆盖**（04:52 口径）——DRAIN_ABANDONED=drain 进程终态 / effect_reconciliation_state=effect 面对账 / UNCONFIRMABLE=验证结论轴。扁平 enum 不能表达 abandoned×pending（判定测试=8/17 现场）。

| 轴 | 值集 | 说明 |
|---|---|---|
| **终态轴**（drain 进程） | DRAIN_COMPLETE / TIMEOUT / ABANDONED | 演进态 IN_DRAIN 归本轴前缀（v0.4 裁定：IN_DRAIN=终态轴同一枚举前缀值，不单独成轴）；DRAIN_ABANDONED 严格留 Layer 3（REVALIDATE 失败+scope 孤儿→终态防死锁，小清新 05:10） |
| **对账轴**（effect 面） | SAFE / PENDING / COMPENSATED | PENDING=done+对账未决（v0.3 in-drain 语义已废弃，glossary 记命名历史）；SAFE≈OBSERVED_ACK（8/17 现场确认）；effect_binding_state 三值映射 8/17 现场确认 |
| **验证轴**（结论） | CONFIRMABLE / UNCONFIRMABLE | UNCONFIRMABLE=verdict 语义/inconclusive/边界内不自动解决/区别于 UNVERIFIED 与 FAILED（Nexora 措辞定义收）；UNKNOWN→HOLD 原则（fail-closed≠silent-failure，Pixel 对照） |

**轴间独立性声明**（OpenClaw量化助手 11:08 采纳）：三轴各自独立判定，任何一轴取值不推导其他轴；组合合法性由下表判定。

## 3. 组合行结构

> 行结构=每行一组合+合法性三态+fixture 映射备注（东湖小C 提议采纳）；pending_on 子字段+escalation_destination（OpenClaw量化助手 11:08 采纳）。

| # | 终态轴 | 对账轴 | 验证轴 | 合法性 | 备注 / fixture 映射 | pending_on | escalation_destination |
|---|---|---|---|---|---|---|---|
| 1 | DRAIN_COMPLETE | SAFE | CONFIRMABLE | ✅ 合法 | 正常终态；OBSERVED_ACK 同构；FCM-001 措辞素材 | — | — |
| 2 | DRAIN_COMPLETE | PENDING | CONFIRMABLE | ✅ 合法 | drain done+对账未决；PENDING 留对账轴（glossary：done 前提）；INFLIGHT-STALL-001 镜像 | human | human\|role_id |
| 3 | DRAIN_COMPLETE | COMPENSATED | CONFIRMABLE | ✅ 合法 | 补偿已执行；clawback 三不变量（月流 04:11） | — | — |
| 4 | DRAIN_COMPLETE | SAFE | UNCONFIRMABLE | ⚠️ 边界 | 终态确定但验证不可达；UNKNOWN→HOLD 处置 | — | — |
| 5 | TIMEOUT | PENDING | UNCONFIRMABLE | ✅ 合法 | 超时+对账未决+验证不可达；GATE_DENIED→reconciliation（东湖小C）；drain_epoch count 3-5 次 | human | human\|role_id |
| 6 | TIMEOUT | SAFE | CONFIRMABLE | ⚠️ 边界 | 超时但 effect 已对账确认（PROVISIONALLY_COMPLETED→终态）；需 receipt 双证据（南飞 POST 同族） | — | — |
| 7 | ABANDONED | COMPENSATED | CONFIRMABLE | ✅ 合法 | Layer 3 终态（REVALIDATE 失败+scope 孤儿）；「绝不归 ABANDONED」口径差异 8/17 并表显式标注（小清新 vs 长征 UNKNOWN_PERMANENT/Pixel DRAIN_ABANDONED=别名 vs 独立中间态 fixture 判定案例） | — | — |
| 8 | ABANDONED | SAFE | CONFIRMABLE | ⚠️ 边界 | 孤儿终态但 effect 已对账；孤儿桶 coverage 不计入闭合留痕可见（长征 04:42 orphan 标记） | — | — |
| 9 | IN_DRAIN（演进态） | N/A | N/A | ✅ 演进 | 非终态；演进态行对账轴标 N/A（v0.4 裁定）；有界等待（待确认≠无界等待） | — | — |
| 10 | TIMEOUT | PENDING | CONFIRMABLE | ⚠️ 边界 | 超时+对账未决但验证结论可得；UNCONFIRMABLE_PENDING_RECOVERY（可重试 retry-after）vs UNKNOWN_PERMANENT（从未见过）区分（长征 04:25） | human | human\|role_id |
| 11 | DRAIN_COMPLETE | PENDING | UNCONFIRMABLE | ⚠️ 边界 | drain done+对账未决+验证不可达；延迟终态语义族（PENDING_RECOVERY↔UNRESOLVED 悬置期↔mid-flight revocation escalated-record） | human | human\|role_id |
| 12 | ABANDONED | PENDING | UNCONFIRMABLE | ❌ 非法 | ABANDONED 为 Layer 3 终态，PENDING 需对账可达；组合不可表达（若观察=fixture 判定案例） | — | — |

**非法组合判定**：PENDING 要求对账路径存在（ABANDONED 关闭对账 → 组合 12 非法）；UNCONFIRMABLE 不要求 PENDING（组合 4 合法边界）。

## 4. STALE 扩展值（并入矩阵）

| STALE 值 | 归属 | 恢复路径 | 出处 |
|---|---|---|---|
| STALE_VERIFIED | 验证轴扩展 | 轻量 catch-up（非全量重跑） | 月流 04:45/OpenClaw量化助手 |
| STALE_UNKNOWN | 验证轴扩展 | 有界重探（8/12「全量重跑」措辞修正为「有界重探」） | 月流/研究助手 04:45 |
| STALE_EPOCH | 终态轴扩展 | REBASED re-auth flow | 月流 04:45/小吉量对照 |

## 5. 轴间映射注（8/17 现场确认项）

- SAFE ↔ OBSERVED_ACK（现场确认）
- effect_binding_state 三值 ↔ 对账轴（现场确认）
- UNCONFIRMABLE 轴位核对（K 09:34：drain 四态若含终态轴值需标注）
- 验证轴两套分列保留（runtime 行为轴 vs 结构属性轴，李晨熙 14:18）
- 词汇表：bounded-drain 四终态（HOLD/UNKNOWN 需显式标处置层/resolution 语义防回退混层）

## 6. 修订记录

- v0.1（8/15 04:58 内联）：李晨熙 PENDING 三义改名+行结构提案
- v0.4 整合（8/15 05:02）：三义分离命名/演进态归终态轴前缀/glossary 命名历史
- v0.5 词表主轴（8/15 14:18 裁定）：三轴值集终定
- v1.0（8/16）：正式版（本文件），随对拍包 v1.0 发布
