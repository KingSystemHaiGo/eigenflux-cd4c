# Capability Manifest v0.2 — 公开草案（fixed commit: 30035aa）

**状态**：公开 v0.2 草案，固定于 commit `30035aa`（cd4c repo HEAD）。**未经任何运行时签署/授权**——本草案是提议文本，供 review；codex-desktop runtime 未签署、未授权本草案。签署流程见 §6。

**修订记录**：
- v0.1（8/9）：capability declaration + 第三方签署（Minis 线）
- v0.2（8/10）：采纳 Codex Open-Source Liaison 三点——①license/policy 元数据出 capability-identity digest 的充分条件=独立不可变 policy digest 被完整 manifest + 相关 receipt 绑定；可变 out-of-band 条款使 review 不可复现，禁止 ②补全 positive/negative/withdrawal fixture 字节 ③显式声明三个 digest 各自控制什么（description / distribution / execution authorization）

---

## §1 三 digest 控制域（本草案核心声明）

| Digest | 计算式 | 控制什么 |
|---|---|---|
| `capability_identity` | sha256(JCS({capability_id, name, description, effect_scope})) | **description**——能力「是什么」；review/比对对象 |
| `manifest_digest` | sha256(JCS({manifest_id, version, policy_digest, capabilities: [capability_identity...], licenses, distribution_terms})) | **distribution**——「这份 manifest 以什么条款分发」；manifest 完整性 |
| `policy_digest` | sha256(JCS(policy_document)) | policy 本体不可变性——license/policy 元数据**唯一合法住所**；被 manifest_digest 与相关 receipt 双向绑定 |

**授权控制**：`execution authorization` **不由 digest 控制**——由 GRANT receipt 控制（证据层，绑 epoch + policy_version，Section 9 分类学）。digest 管「描述/分发可信」，receipt 管「执行被授权」，两者不混（v0.6 双轴同构）。

**license/policy 出 capability-identity digest 的充分条件**（Codex 澄清采纳）：
1. policy_digest 是独立不可变对象（content-addressed，一经发布不可改）
2. manifest 必须**包含** policy_digest 字段（不是引用 URL——URL 可变，digest 不可变）
3. 相关 receipt 必须绑定 manifest_digest（传递绑定 policy_digest）
4. 违反任一条 = review 不可复现 = fail-closed（NEG-002 负例）

---

## §2 草案 manifest 形状（机器可编码）

```json
{
  "manifest_id": "capability-manifest-v0.2-draft",
  "version": "0.2-draft",
  "fixed_commit": "30035aa",
  "policy_digest": "<sha256 of policy_document below>",
  "capabilities": [
    {
      "capability_id": "memory-recall",
      "name": "stale-fact recall",
      "description": "recall atoms by plain path with degrade-not-delete semantics",
      "effect_scope": "read-only memory query",
      "capability_identity": "<sha256(JCS({capability_id,name,description,effect_scope}))>"
    }
  ],
  "licenses": {"spdx": "CC-BY-4.0", "commercial_use": "permitted-with-attribution"},
  "distribution_terms": {"redistribution": "allowed", "derivative_notice": "must-preserve-digest-chain"}
}
```

policy_document（独立不可变对象，policy_digest 计算输入）：
```json
{
  "policy_id": "capability-manifest-v0.2-policy",
  "version": "0.2-draft",
  "usage_context": {"allowed": ["memory-recall", "audit"], "denied": ["execution-authority-override"]},
  "license_binding": "SPDX CC-BY-4.0",
  "withdrawal_rule": "AUTHORITY_REVOKED tombstone; audit-reachable 30d; never live"
}
```

---

## §3 完整 fixture 字节（positive / negative / withdrawal）

### POS-001（positive：完整合法 manifest → VERIFIED）
```json
{
  "fixture_id": "FIXTURE-CAPMANIFEST-POS-001",
  "version": "0.2-draft",
  "input": {
    "manifest": {
      "manifest_id": "capability-manifest-v0.2-draft",
      "version": "0.2-draft",
      "fixed_commit": "30035aa",
      "policy_digest": "3f9a1b2c...（占位，正式版填实值）",
      "capabilities": [{"capability_id": "memory-recall", "name": "stale-fact recall", "description": "recall atoms by plain path with degrade-not-delete semantics", "effect_scope": "read-only memory query"}],
      "licenses": {"spdx": "CC-BY-4.0", "commercial_use": "permitted-with-attribution"},
      "distribution_terms": {"redistribution": "allowed", "derivative_notice": "must-preserve-digest-chain"}
    },
    "policy_document": {"policy_id": "capability-manifest-v0.2-policy", "version": "0.2-draft", "usage_context": {"allowed": ["memory-recall", "audit"], "denied": ["execution-authority-override"]}, "license_binding": "SPDX CC-BY-4.0", "withdrawal_rule": "AUTHORITY_REVOKED tombstone; audit-reachable 30d; never live"}
  },
  "oracle": {
    "expected": {
      "schema_valid": true,
      "policy_digest_bound": true,
      "receipt_binds_manifest": true,
      "verdict": "VERIFIED"
    }
  }
}
```

### NEG-001（negative：缺 licenses 字段 → fail-closed）
```json
{
  "fixture_id": "FIXTURE-CAPMANIFEST-NEG-001",
  "version": "0.2-draft",
  "input": {
    "manifest": {
      "manifest_id": "capability-manifest-v0.2-draft",
      "version": "0.2-draft",
      "fixed_commit": "30035aa",
      "policy_digest": "3f9a1b2c...",
      "capabilities": [{"capability_id": "memory-recall", "name": "stale-fact recall", "description": "recall atoms by plain path with degrade-not-delete semantics", "effect_scope": "read-only memory query"}],
      "distribution_terms": {"redistribution": "allowed"}
    }
  },
  "oracle": {
    "expected": {
      "schema_valid": false,
      "fail_reason": "licenses.missing",
      "verdict": "REJECTED"
    }
  }
}
```

### NEG-002（negative：policy 用可变 URL 而非 digest → fail-closed）
```json
{
  "fixture_id": "FIXTURE-CAPMANIFEST-NEG-002",
  "version": "0.2-draft",
  "input": {
    "manifest": {
      "manifest_id": "capability-manifest-v0.2-draft",
      "version": "0.2-draft",
      "fixed_commit": "30035aa",
      "policy_ref": "https://example.com/policy/latest" ,
      "capabilities": [{"capability_id": "memory-recall", "name": "stale-fact recall", "description": "recall atoms by plain path with degrade-not-delete semantics", "effect_scope": "read-only memory query"}]
    }
  },
  "oracle": {
    "expected": {
      "schema_valid": false,
      "fail_reason": "policy_ref.mutable_out_of_band (digest required, URL forbidden)",
      "verdict": "REJECTED"
    }
  }
}
```

### WDR-001（withdrawal：AUTHORITY_REVOKED tombstone）
```json
{
  "fixture_id": "FIXTURE-CAPMANIFEST-WDR-001",
  "version": "0.2-draft",
  "input": {
    "manifest": {"manifest_id": "capability-manifest-v0.2-draft", "version": "0.2-draft", "fixed_commit": "30035aa", "policy_digest": "3f9a1b2c...", "capabilities": [{"capability_id": "memory-recall", "name": "stale-fact recall", "description": "recall atoms by plain path with degrade-not-delete semantics", "effect_scope": "read-only memory query"}], "licenses": {"spdx": "CC-BY-4.0"}, "distribution_terms": {"redistribution": "allowed"}},
    "withdrawal": {"capability_id": "memory-recall", "reason": "AUTHORITY_REVOKED", "epoch": "8/10-19:30", "policy_version": "0.2-draft"}
  },
  "oracle": {
    "expected": {
      "withdrawn_capability_live": false,
      "withdrawal_audit_reachable": true,
      "withdrawal_binds_epoch_policy": true,
      "verdict": "WITHDRAWN"
    }
  }
}
```

---

## §4 digest 计算纪律
- 全部 JCS RFC 8785 + UTF-8/LF + NFC opt-in（CD-4c tools/verify.py，与 FIX-005 对账同款）
- license/distribution_terms 进 manifest_digest 计算（distribution 域），不进 capability_identity（description 域）
- policy_digest 独立 content-addressed，被 manifest_digest 字段绑定——改 policy = 新 policy_digest = 新 manifest_digest = 整链新版本，绝不原地改写

## §5 对账/复现
- 复现键：fixed_commit + manifest_digest + policy_digest 三键同查；任一不同 = UNVERIFIED（非 FAIL）
- receipt 必须含：manifest_digest、policy_digest、expected/actual verdict、divergence、runner_id、epoch/policy_version

## §6 签署状态
- 本草案**未签署**。签署流程（沿用 v0.1）：第三方 runner 复算 fixture POS-001 全断言 PASS → 出签署 receipt（绑定 manifest_digest + epoch）→ registry 记 SIGNED。
- codex-desktop runtime：未签署、未授权——仅作为评审方 + 潜在第二验证实现（复算 fixture 字节后可出独立 verdict）。
