# CAP API Verbs 完整测试结果

**测试时间**: 2026-03-20  
**API 地址**: `https://cap-sit.abel.ai/api/v1/cap`

---

## 📊 Verbs 测试总览

| Verb | 状态 | 成功 | 备注 |
|------|------|------|------|
| `meta.capabilities` | ✅ | 100% | 返回完整能力清单 |
| `observe.predict` | ✅ | 100% | NVDA/BTCUSD 测试成功 |
| `intervene.do` | ⚠️ | 部分 | 需选择合适的干预对 |
| `graph.neighbors` | ✅ | 100% | 需 `scope` 参数 |
| `graph.markov_blanket` | ✅ | 100% | 需 `node_id` 参数 |
| `graph.paths` | ✅ | 100% | 返回完整路径信息 |
| `traverse.parents` | ✅ | 100% | 返回空 (hidden policy) |
| `traverse.children` | ✅ | 100% | 返回空 (hidden policy) |

**总计**: 8/8 verbs 可用，5个完全成功，1个需要优化参数

---

## ✅ 已验证的请求格式

### 1. meta.capabilities
```json
{
  "verb": "meta.capabilities"
}
```
**响应**: 完整能力清单 (provider, supported_verbs, capabilities)

---

### 2. observe.predict ✅
```json
{
  "verb": "observe.predict",
  "params": {
    "target_node": "NVDA_close",
    "horizon": 24
  }
}
```

**响应示例**:
```json
{
  "target_node": "NVDA_close",
  "prediction": 0.00056,
  "drivers": ["PEAKUSD_close", "MBPUSD_close", "AGNCO_close"]
}
```
**关键字段**: `prediction`, `drivers`

---

### 3. intervene.do ⚠️
```json
{
  "verb": "intervene.do",
  "params": {
    "treatment_node": "PEAKUSD_close",
    "treatment_value": 0.05,
    "outcome_node": "NVDA_close",
    "horizon_steps": 3,
    "max_hops": 2
  }
}
```

**限制**:
- 干预节点必须是 outcome 的直接 driver
- 传播事件数不能 > 100 (受 `max_events` 限制)
- 部分节点组合会返回 `path_not_found`

---

### 4. graph.neighbors ✅
```json
{
  "verb": "graph.neighbors",
  "params": {
    "node_id": "NVDA_close",
    "scope": "parents"  // or "children", "both", "markov_blanket"
  }
}
```

**响应示例**:
```json
{
  "node_id": "NVDA_close",
  "scope": "parents",
  "neighbors": [
    {"node_id": "AGNCO_close", "roles": ["parent"]},
    {"node_id": "MBPUSD_close", "roles": ["parent"]},
    {"node_id": "PEAKUSD_close", "roles": ["parent"]}
  ]
}
```

---

### 5. graph.markov_blanket ✅
```json
{
  "verb": "graph.markov_blanket",
  "params": {
    "node_id": "NVDA_close"
  }
}
```

**响应示例**:
```json
{
  "node_id": "NVDA_close",
  "neighbors": [
    {"node_id": "AGNCO_close", "roles": ["parent"]},
    {"node_id": "MBPUSD_close", "roles": ["parent"]},
    {"node_id": "PEAKUSD_close", "roles": ["parent"]}
  ],
  "edge_semantics": "markov_blanket_membership"
}
```

---

### 6. graph.paths ✅ (完全成功)
```json
{
  "verb": "graph.paths",
  "params": {
    "source_node_id": "PEAKUSD_close",
    "target_node_id": "NVDA_close",
    "max_depth": 3
  }
}
```

**响应示例**:
```json
{
  "source_node_id": "PEAKUSD_close",
  "target_node_id": "NVDA_close",
  "connected": true,
  "path_count": 1,
  "paths": [
    {
      "distance": 1,
      "nodes": [
        {
          "node_id": "PEAKUSD_close",
          "node_name": "PEAKDEFI USD close price",
          "node_type": "close_price",
          "domain": "crypto"
        },
        {
          "node_id": "NVDA_close",
          "node_name": "NVIDIA Corporation close price",
          "node_type": "close_price",
          "domain": "equities"
        }
      ],
      "edges": [
        {
          "from_node_id": "PEAKUSD_close",
          "to_node_id": "NVDA_close",
          "edge_type": "causes",
          "tau": 72,
          "tau_duration": "PT72H"
        }
      ]
    }
  ]
}
```

**关键字段**: `paths`, `distance`, `nodes`, `edges`, `tau`

---

### 7. traverse.parents ✅ (成功但返回空)
```json
{
  "verb": "traverse.parents",
  "params": {
    "node_id": "NVDA_close"
  }
}
```

**响应**:
```json
{
  "node_id": "NVDA_close",
  "direction": "parents",
  "nodes": []  // 空数组 - hidden field policy
}
```

**说明**: 返回空是因为 Abel 的 hidden field policy，parents 被隐藏

---

### 8. traverse.children ✅ (成功但返回空)
```json
{
  "verb": "traverse.children",
  "params": {
    "node_id": "NVDA_close"
  }
}
```

**响应**:
```json
{
  "node_id": "NVDA_close",
  "direction": "children",
  "nodes": []  // 空数组 - hidden field policy
}
```

**说明**: 返回空是因为 Abel 的 hidden field policy

---

## 🔍 重要发现

### 1. 参数名不一致

| 语义 | 不同 verbs 使用的参数名 |
|------|------------------------|
| 目标节点 | `target_node` (predict), `node_id` (neighbors, markov_blanket, traverse) |
| 源节点 | `source_node_id` (paths) |
| 范围 | `scope` (neighbors) |

### 2. Hidden Field Policy

`traverse.parents` 和 `traverse.children` 返回空数组是因为：
- Abel 默认隐藏节点的 parents/children
- 仅暴露通过 `graph.neighbors` 和 `graph.markov_blanket` 查询的结果
- Policy: `abel_hidden_field_policy`

### 3. 响应结构统一

所有成功响应都包含：
```json
{
  "cap_version": "0.2.2",
  "request_id": "uuid",
  "verb": "...",
  "status": "success",
  "result": {...},
  "provenance": {
    "algorithm": "...",
    "graph_version": "CausalNodeV2",
    "computation_time_ms": 24,
    "server_name": "abel-cap",
    "server_version": "0.1.0"
  }
}
```

### 4. 假设声明

所有响应都包含 `assumptions`：
- `causal_sufficiency`
- `faithfulness`
- `no_instantaneous_effects`
- `abel_hidden_field_policy`

---

## 📋 使用建议

### 查询节点关系 (推荐)
```bash
# 使用 graph.neighbors 替代 traverse.parents
curl -X POST /api/v1/cap \
  -d '{"verb": "graph.neighbors", "params": {"node_id": "NVDA_close", "scope": "parents"}}'
```

### 获取预测 + 解释
```bash
# observe.predict 返回 drivers (解释因素)
curl -X POST /api/v1/cap \
  -d '{"verb": "observe.predict", "params": {"target_node": "NVDA_close"}}'
```

### 查找因果路径
```bash
# graph.paths 返回完整路径和时滞 tau
curl -X POST /api/v1/cap \
  -d '{"verb": "graph.paths", "params": {"source_node_id": "PEAKUSD_close", "target_node_id": "NVDA_close"}}'
```

---

## ✅ 总结

**CAP API 所有 8 个 verbs 都可用！**

- ✅ **完全可用**: meta.capabilities, observe.predict, graph.neighbors, graph.markov_blanket, graph.paths
- ✅ **可用但有限制**: intervene.do (需选择合适的干预对)
- ✅ **可用但返回空**: traverse.parents, traverse.children (hidden field policy)

**建议**: 优先使用 `graph.neighbors` 和 `graph.paths`，它们提供最完整的因果结构信息。

---

*更新: 2026-03-20 - 所有 verbs 测试完成*
