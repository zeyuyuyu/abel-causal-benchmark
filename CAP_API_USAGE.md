# CAP API 使用指南 - 已验证可用 ✅

**API 地址**: `https://cap-sit.abel.ai`  
**认证**: Beta 环境有默认认证值，无需额外 API Key  
**端点**: `POST /api/v1/cap`

---

## 🎉 状态：可用！

```bash
# 测试连接
curl https://cap-sit.abel.ai/
# 返回: {"name":"abel-cap","version":"0.1.0","docs":"/docs","openapi":"/openapi.json"}
```

---

## 📋 支持的 CAP Verbs

从 `/.well-known/cap.json` 获取：

### Core Verbs
- ✅ `meta.capabilities` - 获取能力清单
- ✅ `observe.predict` - 预测
- ✅ `intervene.do` - 干预
- ✅ `graph.neighbors` - 邻居节点
- ✅ `graph.markov_blanket` - Markov Blanket
- ✅ `graph.paths` - 路径查询

### Convenience Verbs
- ✅ `traverse.parents` - 父节点遍历
- ✅ `traverse.children` - 子节点遍历

---

## 🔧 请求格式

### 通用格式
```json
POST /api/v1/cap
Content-Type: application/json

{
  "verb": "<cap_verb>",
  "params": {
    // 具体参数
  }
}
```

---

## ✅ 已验证可用的调用

### 1. 获取能力清单
```bash
curl -X POST https://cap-sit.abel.ai/api/v1/cap \
  -H "Content-Type: application/json" \
  -d '{"verb": "meta.capabilities"}'
```

### 2. 预测 (observe.predict)
```bash
curl -X POST https://cap-sit.abel.ai/api/v1/cap \
  -H "Content-Type: application/json" \
  -d '{
    "verb": "observe.predict",
    "params": {
      "target_node": "NVDA_close",
      "horizon": 24
    }
  }'
```

**响应示例**:
```json
{
  "cap_version": "0.2.2",
  "request_id": "f2f248c6-c58c-468b-87e3-3081c59d79c8",
  "verb": "observe.predict",
  "status": "success",
  "result": {
    "target_node": "NVDA_close",
    "prediction": 0.00056,
    "drivers": ["PEAKUSD_close", "MBPUSD_close", "AGNCO_close"]
  },
  "provenance": {
    "algorithm": "primitive.predict",
    "graph_version": "CausalNodeV2",
    "computation_time_ms": 26
  }
}
```

---

## ⚠️ 注意：参数名与预期不同

CAP API 使用的参数名与我们之前的假设不同：

| 我们的假设 | CAP API 实际使用 | 端点 |
|-----------|-----------------|------|
| `target` | `target_node` | observe.predict |
| `source` | `source_node_id` | graph.paths |
| `target` | `target_node_id` | graph.paths |
| `intervention_node` | `treatment_node` | intervene.do |
| `delta` | `treatment_value` | intervene.do |
| `target_node` | `outcome_node` | intervene.do |

**Node 格式**: 必须用 `<ticker>_<field>` 格式，如 `NVDA_close`, `BTCUSD_close`

---

## 🔄 对比：CG API vs CAP API

| 功能 | CG API | CAP API | 状态 |
|------|--------|---------|------|
| Predict | `/causal_graph/{t}/multi-step-prediction` | `observe.predict` | ✅ 两者可用 |
| Drivers | `features` | `drivers` | ✅ 字段名不同 |
| Prediction | `cumulative_prediction` | `prediction` | ✅ 字段名不同 |
| Auth | 无 | 内置 (Beta) | ✅ 都可用 |

---

## 📝 完整示例

### Python 调用示例
```python
import httpx
import asyncio

async def cap_predict():
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://cap-sit.abel.ai/api/v1/cap",
            json={
                "verb": "observe.predict",
                "params": {
                    "target_node": "NVDA_close",
                    "horizon": 24
                }
            }
        )
        return resp.json()

# 结果
{
    "status": "success",
    "result": {
        "prediction": 0.00056,
        "drivers": ["PEAKUSD_close", "MBPUSD_close", "AGNCO_close"]
    }
}
```

---

## 🎯 下一步

1. **更新测试脚本**: 使用正确的 CAP API 参数名
2. **测试所有 verbs**: intervene.do, graph.paths, graph.neighbors 等
3. **对比 CG API 和 CAP API**: 两者结果是否一致

---

## 📚 参考文档

- **CAP Spec**: `https://cap-sit.abel.ai/.well-known/cap.json`
- **OpenAPI**: `https://cap-sit.abel.ai/openapi.json`
- **Docs**: `https://cap-sit.abel.ai/docs`

---

*更新: 2026-03-20 - CAP API 已确认可用！*
