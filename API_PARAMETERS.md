# CG API 调用参数核对文档

**生成时间**: 2026-03-20  
**用途**: 供 CG API 团队核对参数格式

---

## 🔴 需要核对的端点（返回 422）

### 1. `/graph_stats/intervention_impact`

**当前测试请求**:
```
GET /graph_stats/intervention_impact?node=BTCUSD&delta=-0.05&horizon_steps=72&max_hops=3
```

**参数核对表**:

| 参数名 | 当前使用值 | 数据类型 | 是否必需 | 请确认 |
|--------|-----------|----------|----------|--------|
| `node` | BTCUSD | string | ✅ | 用 ticker 还是 node_id? |
| `delta` | -0.05 | float | ✅ | 范围限制? 正负数都支持? |
| `horizon_steps` | 72 | int | ❌ | 单位是小时? 步数? |
| `max_hops` | 3 | int | ❌ | 整数即可? |
| `max_events` | 未使用 | int | ❌ | 是否必需? 默认值? |
| `cg_version` | 未使用 | string | ❌ | 必需参数? |

**期望响应**:
```json
{
  "intervention_effect": float,
  "propagation": [...],
  "affected_nodes": [...],
  "shock_magnitude": float
}
```

**当前响应**: `422 Unprocessable Entity`

---

### 2. `/graph_stats/nodes_connection`

**当前测试请求**:
```
GET /graph_stats/nodes_connection?node_id_1=DXY&node_id_2=BTCUSD&max_depth=3&directed=true
```

**参数核对表**:

| 参数名 | 当前使用值 | 数据类型 | 是否必需 | 请确认 |
|--------|-----------|----------|----------|--------|
| `node_id_1` | DXY | string | ✅ | 参数名正确? 还是 `from`? |
| `node_id_2` | BTCUSD | string | ✅ | 参数名正确? 还是 `to`? |
| `max_depth` | 3 | int | ❌ | 参数名正确? 还是 `depth`? |
| `directed` | true | bool/string | ❌ | boolean (true) 还是 string ("true")? |
| `cg_version` | 未使用 | string | ❌ | 必需参数? |

**期望响应**:
```json
{
  "path": [...],
  "hops": int,
  "tau": int,
  "intermediate_nodes": [...]
}
```

**当前响应**: `422 Unprocessable Entity`

---

## ✅ 已确认可用的端点参数

### 3. `/causal_graph/{ticker}/multi-step-prediction`

**请求格式** (已验证工作):
```
GET /causal_graph/{ticker}/multi-step-prediction?top_factor_num=3&cg_version=CausalNodeV2
```

**参数说明**:
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `ticker` | string (path) | ✅ | NVDA, BTCUSD, SPY 等 |
| `top_factor_num` | int | ❌ | 返回的 top 因子数量，如 3, 5 |
| `cg_version` | string | ❌ | "CausalNodeV2" 或 "CausalNodeTest" |

**实际响应示例** (NVDA):
```json
{
  "ticker": "NVDA",
  "cumulative_prediction": 0.00056,
  "cumulative_prediction_price": 178.62,
  "probability_up": 0.6405,
  "latest_price": 178.52,
  "features": []
}
```

---

### 4. `/causal_graph/{ticker}/prediction`

**请求格式** (已验证工作):
```
GET /causal_graph/{ticker}/prediction?cg_version=CausalNodeV2
```

**参数说明**:
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `ticker` | string (path) | ✅ | NVDA, BTCUSD 等 |
| `cg_version` | string | ❌ | 版本 |

---

### 5. `/causal_graph/mb/{target_node}`

**请求格式** (POST，已验证工作):
```
POST /causal_graph/mb/{target_node}?cg_version=CausalNodeV2
```

**参数说明**:
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `target_node` | string (path) | ✅ | 目标节点，如 NVDA, BTCUSD |
| `cg_version` | string | ❌ | 版本 |

---

## ❌ 未实现端点参数建议

### 6. `/causal_graph/batch/predictions` (404)

**建议请求格式**:
```
GET /causal_graph/batch/predictions?tickers=BTCUSD,ETHUSD&cg_version=CausalNodeV2
```

**建议参数**:
| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `tickers` | string | ✅ | 逗号分隔的 ticker 列表 |
| `cg_version` | string | ❌ | 版本 |

**建议响应**:
```json
{
  "predictions": [
    {"ticker": "BTCUSD", "cumulative_prediction": ..., "probability_up": ...},
    {"ticker": "ETHUSD", "cumulative_prediction": ..., "probability_up": ...}
  ]
}
```

---

## 📊 参数疑问汇总

### 待 CG API 团队确认：

| # | 端点 | 问题 | 当前假设 |
|---|------|------|----------|
| 1 | intervention_impact | `node` 参数格式? | 使用 ticker (BTCUSD) |
| 2 | intervention_impact | `delta` 范围? | 支持 -1.0 到 1.0 |
| 3 | intervention_impact | `horizon_steps` 单位? | 小时数 |
| 4 | nodes_connection | 起始节点参数名? | `node_id_1` |
| 5 | nodes_connection | 目标节点参数名? | `node_id_2` |
| 6 | nodes_connection | 深度参数名? | `max_depth` |
| 7 | nodes_connection | `directed` 格式? | boolean `true` |

---

## 🔧 测试用例

### 测试 1: intervention_impact
```bash
# 测试请求
curl "https://abel-graph-computer-sit.abel.ai/graph_stats/intervention_impact?node=BTCUSD&delta=-0.05&horizon_steps=72"

# 当前响应
HTTP 422 Unprocessable Entity

# 期望响应 (如果参数正确)
HTTP 200 OK
{
  "intervention_effect": float,
  "propagation": [...]
}
```

### 测试 2: nodes_connection
```bash
# 测试请求
curl "https://abel-graph-computer-sit.abel.ai/graph_stats/nodes_connection?node_id_1=DXY&node_id_2=BTCUSD&max_depth=3&directed=true"

# 当前响应
HTTP 422 Unprocessable Entity

# 期望响应 (如果参数正确)
HTTP 200 OK
{
  "path": [...],
  "hops": 2,
  "tau": 3
}
```

---

## 📎 附件

- **完整端点文档**: `CG_API_ENDPOINTS.md`
- **测试脚本**: `test_cap_compatibility.py`
- **测试报告**: `cap_test_all_53/cap_compatibility_report.json`

---

**请 CG API 团队确认以上参数格式，我们可以配合验证修复效果。**
