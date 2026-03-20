# CAP API Schema 文档

## 🌐 服务端点

**基础 URL**: `https://cap-sit.abel.ai`

---

## 1. 服务信息

### GET /
```bash
curl https://cap-sit.abel.ai/
```

**响应**:
```json
{
  "name": "abel-cap",
  "version": "0.1.0",
  "docs": "/docs",
  "openapi": "/openapi.json"
}
```

---

## 2. CAP 能力清单 (Capability Card)

### GET /.well-known/cap.json

**包含信息**:
- **服务名称**: Abel CAP Primitive Adapter
- **版本**: 0.1.0
- **CAP 规范版本**: 0.2.2
- **提供商**: Abel AI
- **端点**: `http://cap-sit.abel.ai/api/v1`
- **合规等级**: Level 2

### 支持的 Verbs

#### Core Verbs
| Verb | 用途 | 状态 |
|------|------|------|
| `meta.capabilities` | 获取能力清单 | ✅ 已验证 |
| `observe.predict` | 预测 | ✅ 已验证 |
| `intervene.do` | 干预 | ⏸️ 待测试 |
| `graph.neighbors` | 邻居节点 | ⏸️ 待测试 |
| `graph.markov_blanket` | Markov Blanket | ⏸️ 待测试 |
| `graph.paths` | 路径查询 | ✅ 已测试 |

#### Convenience Verbs
| Verb | 用途 | 状态 |
|------|------|------|
| `traverse.parents` | 父节点遍历 | ⏸️ 待测试 |
| `traverse.children` | 子节点遍历 | ⏸️ 待测试 |

### 因果引擎能力

```json
{
  "algorithm": "abel_graph_primitives",
  "supports_time_lag": true,
  "supports_instantaneous": false,
  "structural_mechanisms": {
    "available": true,
    "families": ["linear_scm"]
  }
}
```

### 详细能力

| 能力 | 是否支持 |
|------|----------|
| `graph_discovery` | ❌ false |
| `graph_traversal` | ✅ true |
| `temporal_multi_lag` | ✅ true |
| `effect_estimation` | ✅ true |
| `intervention_simulation` | ✅ true |
| `counterfactual_scm` | ❌ false |

---

## 3. OpenAPI 规范

### GET /openapi.json

包含完整的 API 规范和端点定义。

---

## 4. 主要请求端点

### POST /api/v1/cap

**通用请求格式**:
```json
{
  "verb": "<cap_verb>",
  "params": {
    // 具体参数
  }
}
```

---

## 5. 已验证的请求格式

### 5.1 meta.capabilities
```json
{
  "verb": "meta.capabilities"
}
```

### 5.2 observe.predict
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
  "cap_version": "0.2.2",
  "request_id": "...",
  "verb": "observe.predict",
  "status": "success",
  "result": {
    "target_node": "NVDA_close",
    "prediction": 0.00056,
    "drivers": ["PEAKUSD_close", "MBPUSD_close", "AGNCO_close"]
  }
}
```

### 5.3 intervene.do
```json
{
  "verb": "intervene.do",
  "params": {
    "treatment_node": "DXY_close",
    "treatment_value": -0.02,
    "outcome_node": "BTCUSD_close"
  }
}
```

### 5.4 graph.paths
```json
{
  "verb": "graph.paths",
  "params": {
    "source_node_id": "DXY_close",
    "target_node_id": "BTCUSD_close",
    "max_depth": 3
  }
}
```

---

## 6. 参数命名规范

| 语义 | CAP API 参数名 | 备注 |
|------|---------------|------|
| 目标节点 | `target_node` | 格式: `<ticker>_close` |
| 源节点 | `source_node_id` | graph.paths 专用 |
| 目标节点 | `target_node_id` | graph.paths 专用 |
| 干预节点 | `treatment_node` | intervene.do 专用 |
| 干预值 | `treatment_value` | intervene.do 专用 |
| 结果节点 | `outcome_node` | intervene.do 专用 |
| 预测值 | `prediction` | 响应字段 |
| 驱动因素 | `drivers` | 响应字段 |
| 预测时间范围 | `horizon` | 小时数 |
| 最大深度 | `max_depth` | 路径查询 |

---

## 7. 测试状态汇总

| Schema/端点 | 状态 | 备注 |
|------------|------|------|
| `/.well-known/cap.json` | ✅ 可用 | 包含完整能力清单 |
| `/openapi.json` | ✅ 可用 | OpenAPI 规范 |
| `/docs` | ⏸️ 未测试 | 可能为 Swagger UI |
| `/api/v1` (GET) | ✅ 可用 | 返回服务信息 |
| `meta.capabilities` | ✅ 已验证 | 返回能力卡片 |
| `observe.predict` | ✅ 已验证 | NVDA 测试成功 |
| `intervene.do` | ⚠️ 部分 | 404 错误，节点问题 |
| `graph.paths` | ⚠️ 部分 | 返回 paths，缺 distance |

---

## 8. 响应格式

### 成功响应
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
    "computation_time_ms": 26,
    "server_name": "abel-cap",
    "server_version": "0.1.0",
    "cap_spec_version": "0.2.2"
  }
}
```

### 错误响应
```json
{
  "cap_version": "0.2.2",
  "request_id": "uuid",
  "verb": "...",
  "status": "error",
  "error": {
    "code": "invalid_request",
    "message": "...",
    "details": {...}
  }
}
```

---

## 9. 常见错误码

| 错误码 | 含义 |
|--------|------|
| `invalid_request` | 请求参数验证失败 |
| `404` | 节点不存在 |
| `503` | 服务暂时不可用 |

---

*更新: 2026-03-20 - 基于实际测试结果*
