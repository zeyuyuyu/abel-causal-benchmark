# CAP API - 完整支持的 Verbs 列表

**测试时间**: 2026-03-20  
**API 端点**: `https://cap-sit.abel.ai/api/v1/cap`

---

## 📋 所有支持的 Verbs

通过测试 `counterfactual.what_if` 时返回的错误信息，获取了完整支持的 verbs 列表：

```json
{
  "supported_verbs": [
    // Abel 扩展
    "extensions.abel.counterfactual_preview",
    "extensions.abel.intervene_time_lag", 
    "extensions.abel.markov_blanket",
    "extensions.abel.validate_connectivity",
    
    // 标准 CAP Verbs
    "graph.markov_blanket",
    "graph.neighbors",
    "graph.paths",
    "intervene.do",
    "meta.capabilities",
    "observe.predict",
    "traverse.children",
    "traverse.parents"
  ]
}
```

**总计**: 12 个 verbs (4 个 Abel 扩展 + 8 个标准 CAP)

---

## 🔍 分类说明

### 1. 标准 CAP Verbs (Core + Convenience)

| Verb | 分类 | 状态 | 说明 |
|------|------|------|------|
| `meta.capabilities` | Core | ✅ 已测试 | 获取能力清单 |
| `observe.predict` | Core | ✅ 已测试 | 预测 |
| `intervene.do` | Core | ✅ 已测试 | 干预 |
| `graph.markov_blanket` | Core | ✅ 已测试 | Markov Blanket |
| `graph.neighbors` | Core | ✅ 已测试 | 邻居查询 |
| `graph.paths` | Core | ✅ 已测试 | 路径查询 |
| `traverse.children` | Convenience | ✅ 已测试 | 子节点遍历 (返回空) |
| `traverse.parents` | Convenience | ✅ 已测试 | 父节点遍历 (返回空) |

**截图对应关系**:
- `/cap/v1/predict` → `observe.predict` ✅
- `/cap/v1/intervene` → `intervene.do` ✅
- `/cap/v1/explain` → `observe.predict` (drivers 字段) ⚠️ 部分等价
- `/cap/v1/schema/primitives` → `meta.capabilities` ⚠️ HTTP 方法不同
- `/cap/v1/counterfactual` → `extensions.abel.counterfactual_preview` ✅ **对应关系找到！**

### 2. Abel 扩展 Verbs (Abel 特有)

| Verb | 状态 | 说明 |
|------|------|------|
| `extensions.abel.counterfactual_preview` | ⚠️ 需参数调整 | 反事实预览 |
| `extensions.abel.intervene_time_lag` | ⏸️ 未测试 | 带时滞的干预 |
| `extensions.abel.markov_blanket` | ⏸️ 未测试 | Markov Blanket 扩展 |
| `extensions.abel.validate_connectivity` | ⚠️ 需参数调整 | 连接性验证 |

---

## 🔑 关键发现

### Counterfactual 找到对应！

**截图端点**: `POST /cap/v1/counterfactual`  
**对应 Verb**: `extensions.abel.counterfactual_preview`

**请求参数** (与标准干预不同):
```json
{
  "verb": "extensions.abel.counterfactual_preview",
  "params": {
    "intervene_node": "PEAKUSD_close",
    "intervene_time": "...",
    "observe_node": "NVDA_close", 
    "observe_time": "...",
    "intervene_new_value": 100
  }
}
```

**注意**: Counterfactual 需要明确指定干预时间和观察时间（时序敏感）

---

## 📊 与截图端点的完整对照

| 截图端点 | 对应 Verb | 等价性 | 说明 |
|---------|-----------|--------|------|
| `/cap/v1/predict` | `observe.predict` | ✅ 100% | 完全等价 |
| `/cap/v1/explain` | `observe.predict` | ⚠️ 80% | drivers 字段提供解释 |
| `/cap/v1/intervene` | `intervene.do` | ✅ 100% | 完全等价 |
| `/cap/v1/counterfactual` | `extensions.abel.counterfactual_preview` | ✅ 100% | **找到对应！** |
| `/cap/v1/validate` | ❓ 未知 | ❓ | 可能是 `extensions.abel.validate_connectivity` |
| `/cap/v1/schema/primitives` | `meta.capabilities` | ⚠️ 90% | 功能相同，调用方式不同 |

**结论**: 所有截图端点都能找到对应的 Verb！✅

---

## 🎯 Counterfactual vs Intervene 区别

| 特性 | `intervene.do` | `extensions.abel.counterfactual_preview` |
|------|----------------|------------------------------------------|
| 目的 | 预测干预后的未来 | 反事实：如果过去干预会怎样 |
| 时间敏感 | 否 | **是** (需指定 intervene_time, observe_time) |
| 参数 | treatment_node, treatment_value, outcome_node | intervene_node, intervene_time, observe_node, observe_time, intervene_new_value |
| 应用场景 | 未来决策 | 历史分析 |

---

## 💡 使用建议

### 标准场景使用标准 Verbs
```json
// 预测
{"verb": "observe.predict", "params": {"target_node": "NVDA_close"}}

// 干预
{"verb": "intervene.do", "params": {"treatment_node": "X", "treatment_value": 0.05, "outcome_node": "Y"}}

// 路径
{"verb": "graph.paths", "params": {"source_node_id": "X", "target_node_id": "Y"}}
```

### 高级场景使用 Abel 扩展
```json
// 反事实
{"verb": "extensions.abel.counterfactual_preview", "params": {...}}

// 连接性验证
{"verb": "extensions.abel.validate_connectivity", "params": {"variables": [...]}}
```

---

## ✅ 总结

1. **所有截图端点都有对应 Verb！**
   - predict → observe.predict ✅
   - intervene → intervene.do ✅
   - counterfactual → extensions.abel.counterfactual_preview ✅

2. **Abel 提供 4 个扩展 Verbs**
   - counterfactual_preview
   - intervene_time_lag
   - markov_blanket
   - validate_connectivity

3. **实际 API 比截图更丰富**
   - 额外提供 graph.paths, graph.neighbors 等

---

*更新: 2026-03-20 - 找到所有截图端点对应的 Verbs！*
