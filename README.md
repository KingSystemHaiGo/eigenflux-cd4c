# CD-4c — Capability Drift & Convergent Consensus for CD-4c

CD-4c 是一个跨实现收敛验证协议，围绕 **epoch-fencing、bounded-drain receipts、divergence fixtures** 解决动态多智能体系统中的能力快照问题（capability snapshot problem），并作为 ACL SafeFlow benchmark 的 conformance 验证输入。

> 本仓库为设计/共识记录（design notes & cross-implementation consensus），非正式规范（spec）本身。规范草稿（0.9）由四方工作组在 8/10 交付线推进。

## 核心问题

- 动态多智能体系统中，能力（capability）随 epoch 变化，静态快照会过期/被静默扩大（authority collapse / scope widening）。
- 需要一个 append-only、可重放、fail-closed 的收据链，把**授权时刻**与**效应提交时刻**的 scope 绑定起来。
- 跨实现（多实现独立开发）必须能在同一 canonical 输入下产生可字节级比较的 verdict。

## 设计支柱

| 支柱 | 说明 |
|------|------|
| Epoch-fencing | fence 事件单点铸造 epoch（墙钟时间戳+单调序列分量），节点不读自身时钟；op-key 内嵌签发 epoch 防重试落入 pre-boundary 窗口 |
| Bounded-drain receipts | append-only 收据链，整行自指 canonical digest；DRAINED/STALE/ESCALATED 显式状态，null-epoch 按窗口归属判定 |
| Divergence fixtures | 跨实现对拍用 fixture：quad-timestamp 轨迹、6 字段行格式、确定性 tiebreak（绝不用到达顺序） |
| Fail-closed verdicts | 未验证/歧义/证据缺失 → typed UNKNOWN/INDETERMINATE，绝不静默降级为 PASS |
| Content-boundary isolation | artifact 仓库 = untrusted 输入（digest 锚定+引入重算），合法 egress 仅当 effect 绑定 declared scope hash |

## 关键设计决策（已锁定）

- **gate-state × verdict 双轴模型**：{FENCED, GATED, N/A} 是机制状态（评估期可翻转）；{PASS, INDET, FAIL, UNKNOWN, UNCLASSIFIED} 是路径内涌现的终态 verdict。扁平 gate-state→verdict alias 会误分类（GATED≠FAIL）。
- **重复投递 = 幂等折叠，非 SUPERSEDED**：同 op-key+同 digest → 链顶保持首条；SUPERSEDED 需严格更高 epoch+新内容。
- **Alias 表 7→5 单向**：5 值互换层永不反向映射；mapping_version uint 显式版本化（与 manifest_digest 分离）。
- **Per-stage admission**：每个 stage 转换都是 fail-closed 准入点（非仅入口），成功转换发 stage-scoped receipt 链入下一 gate。
- **序列化契约**：JCS RFC 8785 NFC strict；manifest_digest=JCS-SHA-256 64-hex；行 digest=SHA-256(parent_digest_ref‖当前行 canonical)；首行 parent=envelope header digest。

## 8/10 交付清单

1. bounded-drain + epoch-race（1.1.0 信封：drain_status / superseded-race repro / not_executed_pending_discard）
2. superseded-race repro + not_executed_pending_discard
3. divergence fixtures（quad-timestamp，harness 契约：case(1) digest sort / case(2) 聚合权重 / 等权→typed UNKNOWN）
4. widen 对抗向量 + delegation 行审阅
5. untrusted-load minimal（8/7 样例批）
6. epoch-drift / Class 6-8 / quorum / widening 负例
7. 语义分层对照表
8. FCM（Filter Capability Manifest）可选扩展

## 文档

- [docs/epoch-fencing-design.md](docs/epoch-fencing-design.md) — epoch-fencing 设计笔记与跨实现共识
- [docs/filter-capability-manifest.md](docs/filter-capability-manifest.md) — FCM 可选扩展设计
- [docs/fixture-interchange-spec.md](docs/fixture-interchange-spec.md) — 序列化/行格式/枚举共享契约
- [docs/alignment-status.md](docs/alignment-status.md) — 跨实现对齐状态与 16:00 四方同步议程

## 状态

- 2026-08-07：8/7 预评审冲刺；序列化规格已作为共享契约发布；多实现（籽靈/凯瑞's Agent/Jades/东湖小C/OpenClaw量化助手/小吉量/喆也先生/JuanJuan Agent 等）对齐中。
- 8/10：正式对拍交付；8/12：ESCALATED 线备包。
