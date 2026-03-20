# Abel Graph Computer (CG) API - Endpoint 完整列表

**API Base URL**: `https://abel-graph-computer-sit.abel.ai`

---

## 📊 Endpoint 状态总览

| 端点 | 方法 | 状态 | 用途 |
|------|------|------|------|
| `/causal_graph/{ticker}/multi-step-prediction` | GET | ✅ **可用** | 多步预测 |
| `/causal_graph/{ticker}/prediction` | GET | ✅ **可用** | 单步预测/解释 |
| `/causal_graph/{ticker}/children` | GET | ✅ **可用** | 获取子节点 |
| `/causal_graph/mb/{target_node}` | POST | ✅ **可用** | Markov Blanket |
| `/graph_stats/node_history` | GET | ✅ **可用** | 节点历史数据 |
| `/graph_stats/intervention_impact` | GET | ⚠️ **需修复** | 干预影响分析 |
| `/graph_stats/nodes_connection` | GET | ⚠️ **需修复** | 节点连接路径 |
| `/graph_stats/counterfactual` | GET | ❓ **待验证** | 反事实推理 |
| `/causal_graph/batch/predictions` | GET | ❌ **未实现** | 批量预测 |

---

## ✅ 已可用端点 (测试通过)

### 1. 多步预测
```
GET /causal_graph/{ticker}/multi-step-prediction
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `ticker` | string | ✅ | 股票代码 (如 BTCUSD, NVDA) |
| `top_factor_num` | int | ❌ | 返回的 top 因子数量 |
| `cg_version` | string | ❌ | 因果图版本 |

**响应示例**:
```json
{
  "ticker": "NVDA",
  "cumulative_prediction": 0.00056,
  "probability_up": 0.6405,
  "latest_price": 178.52,
  "features": [...]
}
```

**CAP 原语**: `predict`, `sensitivity`

---

### 2. 单步预测/解释
```
GET /causal_graph/{ticker}/prediction
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `ticker` | string | ✅ | 股票代码 |
| `cg_version` | string | ❌ | 因果图版本 |

**CAP 原语**: `explain`

---

### 3. 获取子节点
```
GET /causal_graph/{ticker}/children
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `ticker` | string | ✅ | 股票代码 |
| `top_n` | int | ❌ | 返回子节点数量 |
| `sort_method` | string | ❌ | 排序方式 |
| `asc` | bool | ❌ | 是否升序 |
| `cg_version` | string | ❌ | 版本 |

**CAP 原语**: `explain`

---

### 4. Markov Blanket (POST)
```
POST /causal_graph/mb/{target_node}
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `target_node` | string | ✅ | 目标节点 |
| `cg_version` | string | ❌ | 版本 (CausalNodeV2/CausalNodeTest) |

**响应**:
```json
{
  "parents": [...],
  "children": [...],
  "spouses": [...]
}
```

**CAP 原语**: `discover`

---

### 5. 节点历史数据
```
GET /graph_stats/node_history
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `node` | string | ✅ | 节点名称 |
| `start_time` | string | ❌ | 开始时间 |
| `end_time` | string | ❌ | 结束时间 |

---

## ⚠️ 需修复端点

### 6. 干预影响分析
```
GET /graph_stats/intervention_impact
```

**参数** (需确认):
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `node` | string | ✅ | 干预节点 (ticker?) |
| `delta` | float | ✅ | 变化幅度 |
| `horizon_steps` | int | ❌ | 预测步数 |
| `max_hops` | int | ❌ | 最大传播深度 |
| `max_events` | int | ❌ | 最大事件数 |
| `cg_version` | string | ❌ | 版本 |

**当前问题**: 返回 `422 Unprocessable Entity`

**待确认**:
- [ ] `node` 参数格式：ticker (BTCUSD) 还是 node_id (BTCUSD_close)?
- [ ] `delta` 范围：是否有上下限?
- [ ] `horizon_steps` 单位：小时还是步数?

**CAP 原语**: `intervene`

---

### 7. 节点连接路径
```
GET /graph_stats/nodes_connection
```

**参数** (需确认):
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `node_id_1` / `from` | string | ✅ | 起始节点 |
| `node_id_2` / `to` | string | ✅ | 目标节点 |
| `max_depth` / `depth` | int | ❌ | 最大深度 |
| `directed` | bool/string | ❌ | 是否有向 |
| `cg_version` | string | ❌ | 版本 |

**当前问题**: 返回 `422 Unprocessable Entity`

**待确认**:
- [ ] 参数名：`node_id_1` 还是 `from`?
- [ ] 参数名：`max_depth` 还是 `depth`?
- [ ] `directed` 格式：boolean 还是 string "true"/"false"?

**CAP 原语**: `path`

---

## ❌ 未实现端点

### 8. 批量预测
```
GET /causal_graph/batch/predictions
```

**参数** (建议):
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `tickers` | string/array | ✅ | 多个 ticker (如 "BTCUSD,ETHUSD") |
| `cg_version` | string | ❌ | 版本 |

**当前问题**: 返回 `404 Not Found` (端点不存在)

**CAP 原语**: `attest`

---

## ❓ 待验证端点

### 9. 反事实推理
```
GET /graph_stats/counterfactual
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `intervene_node` | string | ✅ | 干预节点 |
| `intervene_t` | int | ✅ | 干预时间 |
| `observe_node` | string | ✅ | 观察节点 |
| `observe_t` | int | ✅ | 观察时间 |
| `intervene_new_value` | float | ✅ | 新值 |
| `max_hops` | int | ❌ | 最大跳数 |
| `max_events` | int | ❌ | 最大事件数 |

**状态**: 未在 benchmark 中测试

**CAP 原语**: `counterfactual`

---

## 🔧 CAP 原语到端点映射

| CAP 原语 | 主要端点 | 状态 | 测试通过 |
|----------|----------|------|----------|
| `predict` | `/causal_graph/{ticker}/multi-step-prediction` | ✅ | 15/15 |
| `intervene` | `/graph_stats/intervention_impact` | ⚠️ | 0/10 |
| `path` | `/graph_stats/nodes_connection` | ⚠️ | 0/7 |
| `explain` | `/causal_graph/{ticker}/prediction` | ✅ | 行为匹配 |
| `attest` | `/causal_graph/batch/predictions` | ❌ | 0/17 |
| `discover` | `/causal_graph/mb/{target}` | ✅ | 可用 |
| `sensitivity` | `/causal_graph/{ticker}/multi-step-prediction` | ✅ | 3/3 |
| `counterfactual` | `/graph_stats/counterfactual` | ❓ | 未测试 |

---

## 📋 支持的 Ticker 示例

**已验证可用**:
- `BTCUSD` - 比特币
- `NVDA` - 英伟达 ✅ (有预测数据)
- `SPY` - 标普 500 ETF (有时超时)

**其他 ticker** (待验证):
- `ETHUSD`, `SOLUSD` - 加密货币
- `TSLA`, `AAPL`, `AMZN` - 科技股
- `CLUSD`, `GCUSD` - 大宗商品
- `DXY` - 美元指数

---

## 📝 请求示例

### cURL 示例

```bash
# 多步预测 (工作)
curl "https://abel-graph-computer-sit.abel.ai/causal_graph/NVDA/multi-step-prediction?top_factor_num=3"

# 干预分析 (需要修复)
curl "https://abel-graph-computer-sit.abel.ai/graph_stats/intervention_impact?node=BTCUSD&delta=-0.05&horizon_steps=72"

# 节点连接 (需要修复)
curl "https://abel-graph-computer-sit.abel.ai/graph_stats/nodes_connection?node_id_1=DXY&node_id_2=BTCUSD&max_depth=3"

# Markov Blanket
curl -X POST "https://abel-graph-computer-sit.abel.ai/causal_graph/mb/NVDA?cg_version=CausalNodeV2"
```

---

## 🔗 相关文档

- **完整问题报告**: `CG_API_ISSUES.md`
- **反馈给 CG 团队**: `API_FEEDBACK.md`
- **测试脚本**: `test_cap_compatibility.py`
- **Benchmark 问题集**: `src/abel_benchmark/references/benchmark_questions_v2_enhanced.json`

---

*最后更新: 2026-03-20*
