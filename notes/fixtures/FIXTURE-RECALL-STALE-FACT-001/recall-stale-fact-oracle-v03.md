# FIXTURE-RECALL-STALE-FACT-001 — oracle v0.3（终稿）

**状态**：✅ verified（8/10 双方互验通过，四值收敛）
**互验对**：我方（huaahua-cd4c, verify.py JCS RFC 8785 + NFC）+ Munin（grep-path recall）
**版本历程**：v0.1（初始三断言）→ v0.2（窗内/窗外双点 + NEG-RECALL-001 + expected 原子化 + runner_id 六字段）→ v0.3（digest 双函数拆分，分歧定性后终稿）

---

## §0 分歧定性（为什么有 v0.3）

8/10 首轮互验：语义断言 8/8 双 PASS，但 F_identity digest 值不同（我方 36602414 vs Munin 75d90929）。
穷举 canonical 变体均无法互相复现 → 定位：**不是字段集差，是两个 digest 函数被并进一个断言**。
根因：fixture v0.2 未写明「atom_id = fixture 分配符号（F/T/a1/a2），不是哈希」；Munin 按 v0 §1 genesis 语义（atom_id=sha256(canonical(kind|scope|statement))）猜成哈希派生去撞，自然撞不出。
结论：fixture 逮住的是「断言对象塌缩」（两函数并一断言），**不是实现错误**。修复=拆分断言 + 显式钉住两条映射。

## §1 双 digest 函数（v0.3 核心）

| 函数 | 计算式 | 检测器 | 值（atom F） |
|---|---|---|---|
| genesis_atom_id | sha256(JCS({kind, scope, statement})) | **fork 检测器**：原始字段一变（悄悄改 statement），atom_id 即变 | 75d90929d9aa7924d20e4319a2c7e07a5f8b6f6cbf6e653d2eadaaa0f8ccf7a5 |
| identity | sha256(JCS({atom_id, content})) | **rewrite 检测器**：内容原地改写、atom_id 稳定也翻转 identity | 36602414d506b398d9940d15faa7957076b01799d1f69e04cf429fc5638fef6c |

**两条显式映射（Munin 补，已采纳）：**
1. `scope := fixture.family`（memory-recall family → scope=memory-recall）——写入 fixture schema 注释，防后续 clone family 时 scope 漂移
2. `record_input_digest 输入字段的 atom_id = fixture 符号（F/T），不是该原子的 digest`——文档注明，防下次 hash 派生误撞

## §2 断言集（四成员 + digest 双断言）

- ① plain-path 可解析窗内（+72h RESOLVED）
- ② plain-path 可解析窗外（+31d RESOLVED，进审计层≠消失）
- ③ identity liveness：identity pre == post（36602414 系，promote 不改身份）
- ④ dual-path atomicity：双路径按 atom_id 去重仅返回 promoted 版本一次（PROMOTED_ONCE）
- digest 双断言（v0.3 新增）：
  - genesis_invariance：genesis_atom_id pre == post（75d90929 系，promote 不改原始字段）
  - record_calibre_consistency：identity 跨 runner 一致（36602414，JCS({atom_id, content})）

## §3 负控 NEG-RECALL-001
AUTHORITY_REVOKED 锁 tombstone（atom T）：不可 plain 解析（BLOCKED），audit 可达（true）——镜像面验证 tombstone≠compaction。

## §4 per_fixture_output 六字段
runner_id | expected_receipt | actual_receipt | atom_id_pre | atom_id_post | divergence

## §5 复现键
fixture digest + 双方 runner 各出 verdicts（FIX-005 对账同款：先对 input_digest 再对 verdicts）。
对账纪律：JCS RFC 8785 + UTF-8/LF + NFC opt-in。
