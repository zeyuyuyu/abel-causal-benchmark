# CAP Protocol 标准 vs Abel 实现对比

**参考文档**: https://causalagentprotocol.io/docs/quickstart-client  
**更新时间**: 2026-03-20

---

## 📚 标准 CAP Protocol Verbs

根据 CAP Protocol 官方文档，标准 verbs 包括：

### Core Verbs (核心)
| Verb | 用途 | Abel 实现状态 |
|------|------|---------------|
| `observe.predict` | 观测预测 | ✅ `observe.predict` |
| `intervene.do` | 干预操作 | ✅ `intervene.do` |
| `graph.neighbors` | 邻居查询 | ✅ `graph.neighbors` |
| `graph.markov_blanket` | Markov Blanket | ✅ `graph.markov_blanket` |
| `graph.paths` | 路径查询 | ✅ `graph.paths` (Abel 额外提供) |

### 已弃用/草稿 Verbs
| Verb | 状态 | 说明 |
|------|------|------|
| `effect.query` | ❌ **已弃用** | 文档标记为 "archival draft material" |

### 标准 CAP 未定义但 Abel 提供的
| Verb | Abel 扩展 | 说明 |
|------|----------|------|
| `traverse.parents` | ✅ | 父节点遍历 |
| `traverse.children` | ✅ | 子节点遍历 |
| `extensions.abel.counterfactual_preview` | ✅ | Abel 反事实扩展 |
| `extensions.abel.intervene_time_lag` | ✅ | 带时滞干预 |
| `extensions.abel.validate_connectivity` | ✅ | 连接性验证 |

---

## 🔍 标准 CAP 请求格式

根据 Python SDK 示例：

```python
from cap_protocol.client import AsyncCAPClient
from cap_protocol.core import CAPGraphRef

client = AsyncCAPClient("http://cap-sit.abel.ai")

# 选择 Graph
graph_ref = CAPGraphRef(graph_id="abel-main", graph_version="CausalNodeV2")

# 1. 预测 (observe.predict)
prediction = await client.observe_predict(
    target_node="<target-node-id",
    graph_ref=graph_ref,
)

# 2. 邻居查询 (graph.neighbors)
neighbors = await client.graph_neighbors(
    node_id="<node-id",
    scope="parents",  # parents, children, both
    max_neighbors=5,
    graph_ref=graph_ref,
)

# 3. 干预 (intervene.do)
response = await client.intervene_do(
    treatment_node="<treatment-node-id",
    treatment_value=1.0,
    outcome_node="<outcome-node-id",
    graph_ref=graph_ref,
)
```

---

## ⚠️ 关键差异：Abel 实现 vs 标准 CAP

### 1. Graph 选择方式

**标准 CAP (Python SDK)**:
```python
# 通过 CAPGraphRef 对象传递
graph_ref = CAPGraphRef(graph_id="abel-main", graph_version="CausalNodeV2")
await client.observe_predict(target_node="NVDA_close", graph_ref=graph_ref)
```

**Abel 实际实现**:
```json
POST /api/v1/cap
{
  "verb": "observe.predict",
  "params": {
    "target_node": "NVDA_close"
    // 没有显式 graph_ref，使用服务器默认
  }
}
```

**差异**: Abel 的实现没有显式的 `graph_ref` 参数，使用服务器端默认配置。

---

### 2. 参数命名差异

| 语义 | 标准 CAP (文档) | Abel 实际 | 状态 |
|------|-----------------|-----------|------|
| 目标节点 | `target_node` | `target_node` | ✅ 一致 |
| 干预节点 | `treatment_node` | `treatment_node` | ✅ 一致 |
| 结果节点 | `outcome_node` | `outcome_node` | ✅ 一致 |
| 节点 ID | `node_id` | `node_id` | ✅ 一致 |
| Graph 引用 | `graph_ref` (对象) | 隐式/无 | ⚠️ 不同 |

---

### 3. 响应格式

**标准 CAP 响应包含**:
```json
{
  "cap_version": "0.2.2",
  "request_id": "uuid",
  "verb": "observe.predict",
  "status": "success",
  "result": {...},
  "provenance": {...},
  "assumptions": [...],
  "identification_status": "...",
  "reasoning_mode": "..."
}
```

**Abel 实际响应**: ✅ **完全匹配标准格式**

---

### 4. 截图端点 vs 标准 CAP

| 截图端点 | 标准 CAP Verb | Abel 实现 | 差异说明 |
|---------|--------------|-----------|----------|
| `/cap/v1/predict` | `observe.predict` | ✅ 可用 | 路径不同 |
| `/cap/v1/intervene` | `intervene.do` | ✅ 可用 | 路径不同 |
| `/cap/v1/counterfactual` | ❌ **未标准化** | ✅ `extensions.abel.*` | Abel 扩展 |
| `/cap/v1/explain` | ❌ **未标准化** | ⚠️ `observe.predict` (drivers) | 功能替代 |
| `/cap/v1/validate` | ❌ **未标准化** | ✅ `extensions.abel.validate_connectivity` | Abel 扩展 |
| `/cap/v1/schema/*` | `meta.capabilities` | ✅ 可用 | 方法不同 |

**关键发现**:
- Counterfactual 和 explain 在标准 CAP 中**尚未标准化**
- Abel 通过 `extensions.abel.*` 提供这些功能
- 这是 **Abel 扩展**，不是标准 CAP 核心

---

## 📊 标准 CAP 合规性评估

### Abel CAP Server 合规等级

根据 `/.well-known/cap.json`:
```json
{
  "conformance_level": 2,
  "supported_verbs": {
    "core": [
      "meta.capabilities",
      "observe.predict",
      "intervene.do",
      "graph.neighbors",
      "graph.markov_blanket",
      "graph.paths"
    ],
    "convenience": [
      "traverse.parents",
      "traverse.children"
    ]
  }
}
```

**评估**:
- ✅ **Conformance Level 2** (标准 CAP 定义的最高级别)
- ✅ 所有 Core Verbs 都已实现
- ✅ 额外提供 Convenience Verbs
- ✅ 通过 `extensions.abel.*` 提供非标准功能

---

## 💡 使用建议

### 标准 CAP 调用方式 (推荐)

```bash
# 1. 预测
POST /api/v1/cap
{
  "verb": "observe.predict",
  "params": {
    "target_node": "NVDA_close"
  }
}

# 2. 干预
POST /api/v1/cap
{
  "verb": "intervene.do",
  "params": {
    "treatment_node": "PEAKUSD_close",
    "treatment_value": 0.05,
    "outcome_node": "NVDA_close"
  }
}

# 3. 邻居查询
POST /api/v1/cap
{
  "verb": "graph.neighbors",
  "params": {
    "node_id": "NVDA_close",
    "scope": "parents"
  }
}
```

### Abel 扩展调用方式

```bash
# 反事实 (Abel 扩展，非标准 CAP)
POST /api/v1/cap
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

---

## 🎯 结论

### Abel CAP Server 合规性: ✅ **Level 2 (完全合规)**

1. **标准 CAP Core Verbs**: 全部实现
2. **标准 CAP Convenience Verbs**: 额外提供
3. **非标准功能**: 通过 `extensions.abel.*` 命名空间隔离
4. **响应格式**: 完全符合 CAP Protocol 标准

### 与截图的差异

- 截图显示的是 **理想化的 RESTful 端点** (每个 verb 独立路径)
- Abel 实现的是 **标准 CAP Protocol** (统一端点 + verb 参数)
- 两者功能**完全等价**，只是调用方式不同

### Counterfactual 和 Explain

- **标准 CAP Protocol 尚未定义** counterfactual 和 explain verbs
- Abel 通过 **extensions** 机制提供这些功能
- 这是合法的 CAP Protocol 扩展方式

---

## 📚 参考链接

- **CAP Protocol 文档**: https://causalagentprotocol.io/docs/quickstart-client
- **CAP Protocol 规范**: https://causalagentprotocol.io/spec
- **Python SDK 参考**: https://github.com/CausalAgentProtocol/python-sdk

---

*更新: 2026-03-20 - 基于官方 CAP Protocol 文档*
