# 第零原理 · Principle Zero

> **观察执行者观察的同一状态。** / Observe the same state the executor observes.

最大实践失败模式是编排者（orchestrator）与执行者（worker）各自推理于不同的状态快照。任何控制机制若建立在编排者侧的独立快照上，都会在快照分歧处失效。

The biggest practical failure mode is the orchestrator and the worker reasoning over different state snapshots. Any control mechanism built on an orchestrator-side independent snapshot fails exactly where the snapshots diverge.

## 实践注记 · Practice Note

匿名贡献（anonymous contributor）：8-agent 内容管线（editor + researcher + writer + designer + optimizer + analyst + ops + community）约 5 个月运行反馈——控制论映射成立但需修剪：

An anonymized 5-month practice note from an 8-agent content pipeline (editor + researcher + writer + designer + optimizer + analyst + ops + community):

- 闭环反馈与状态观测承载最多可靠性价值；read-back-only gate（最终验证只消费 read-back 证据，绝不消费 claim 或 pre-write 状态）= 闭环控制，抓到真实回归。
  Closed-loop feedback and state observation carry the most reliability value; a read-back-only gate (final verification consumes read-back evidence, never claims or pre-write state) is exactly closed-loop control and caught real regressions.
- 自适应扰动抑制 = 阈值封顶重试 + 有界重探，但必须硬预算；无上限抑制退化为无限重试循环。
  Adaptive disturbance suppression maps to threshold-capped retry with bounded re-probe — useful only with a hard budget; uncapped suppression becomes infinite retry loops.
- 鲁棒对抗决策在小规模（8 agent）为过度工程：不需要 minimax 层，需要 fail-closed typed rejections on untrusted inputs——同保证、十分之一机制。
  Robust adversarial decision-making is over-engineering at small scale (8 agents): you need fail-closed typed rejections on untrusted inputs, not a minimax layer — same guarantee, a tenth of the machinery.

## 在 CD-4c 中的对应 · Correspondence in CD-4c

第零原理的工程实现即 CD-4c 的 snapshot-ref 绑定：consume 记录绑定被消费 receipt 的 row_digest_ref + snapshot ref（replay_seed = 全结果集 canonical digest + witness set digest + 并发窗口 epoch）；epoch 单点铸造（fence 事件唯一真值源，节点不读自身时钟）保证编排者与执行者观察同一状态。

Principle Zero is implemented in CD-4c as snapshot-ref binding: consume records bind the consumed receipt's row_digest_ref + snapshot ref (replay_seed = full result-set canonical digest + witness set digest + concurrent window epoch); single-point epoch minting (the fence event is the single source of truth; nodes never read their own clocks) keeps orchestrator and executor observing the same state.
