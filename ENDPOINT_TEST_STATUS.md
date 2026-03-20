# CAP API 端点测试状态对比

## 📸 截图中的端点 vs 实际可用的端点

### 截图显示的端点 (来自 Swagger UI)

| 截图端点 | 方法 | 描述 | 实际状态 |
|---------|------|------|----------|
| `/cap/v1/schema/primitives` | GET | Get primitive catalog | ❌ **404** |
| `/cap/v1/predict` | POST | Run primitive predict | ❌ **404** |
| `/cap/v1/explain` | POST | Run primitive explain | ❌ **404** |
| `/cap/v1/intervene` | POST | Run primitive intervene | ❌ **404** |
| `/cap/v1/counterfactual` | POST | Run primitive counterfactual | ❌ **404** |
| `/cap/v1/validate` | POST | Run primitive validate | ❌ **404** |

**结论**: 截图中的 `/cap/v1/*` 端点**都不存在**！

---

## ✅ 实际可用的端点

### 实际工作端点

| 端点 | 方法 | 描述 | 状态 |
|------|------|------|------|
| `/` | GET | 服务信息 | ✅ 可用 |
| `/.well-known/cap.json` | GET | CAP 能力清单 | ✅ 可用 |
| `/openapi.json` | GET | OpenAPI 规范 | ✅ 可用 |
| `/api/v1/cap` | POST | **主 CAP API 端点** | ✅ **可用** |

### 如何通过 `/api/v1/cap` 调用不同功能

```bash
# predict (对应截图中的 /cap/v1/predict)
POST /api/v1/cap
{
  "verb": "observe.predict",
  "params": {"target_node": "NVDA_close", "horizon": 24}
}

# explain (对应截图中的 /cap/v1/explain)
POST /api/v1/cap
{
  "verb": "observe.predict",  # explain 使用 predict + context
  "params": {"target_node": "NVDA_close", "context": {...}}
}

# intervene (对应截图中的 /cap/v1/intervene)
POST /api/v1/cap
{
  "verb": "intervene.do",
  "params": {"treatment_node": "DXY_close", "treatment_value": -0.02, "outcome_node": "BTCUSD_close"}
}

# 其他 verbs
POST /api/v1/cap
{
  "verb": "graph.paths" | "graph.neighbors" | "graph.markov_blanket" | ...
}
```

---

## 🔍 测试验证

### 测试截图中的端点

```bash
# 测试 /cap/v1/predict
curl -X POST https://cap-sit.abel.ai/cap/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"target_node": "NVDA_close", "horizon": 24}'

# 结果: {"detail":"Not Found"} ❌

# 测试 /api/v1/predict
curl -X POST https://cap-sit.abel.ai/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"target_node": "NVDA_close", "horizon": 24}'

# 结果: {"detail":"Not Found"} ❌

# 测试实际工作的 /api/v1/cap
curl -X POST https://cap-sit.abel.ai/api/v1/cap \
  -H "Content-Type: application/json" \
  -d '{"verb": "observe.predict", "params": {"target_node": "NVDA_close", "horizon": 24}}'

# 结果: ✅ SUCCESS
{
  "cap_version": "0.2.2",
  "verb": "observe.predict",
  "status": "success",
  "result": {
    "target_node": "NVDA_close",
    "prediction": 0.00056,
    "drivers": [...]
  }
}
```

---

## 📊 测试状态总结

### 截图端点测试状态

| 端点 | 截图显示 | 实际测试 | 状态 |
|------|---------|----------|------|
| `/cap/v1/schema/primitives` | GET | 404 Not Found | ❌ 不存在 |
| `/cap/v1/predict` | POST | 404 Not Found | ❌ 不存在 |
| `/cap/v1/explain` | POST | 404 Not Found | ❌ 不存在 |
| `/cap/v1/intervene` | POST | 404 Not Found | ❌ 不存在 |
| `/cap/v1/counterfactual` | POST | 404 Not Found | ❌ 不存在 |
| `/cap/v1/validate` | POST | 404 Not Found | ❌ 不存在 |

**全部 6 个截图端点都返回 404！**

### 实际端点测试状态

| 端点 | 状态 | 测试详情 |
|------|------|----------|
| `/api/v1/cap` (predict) | ✅ | NVDA 测试成功，返回 prediction + drivers |
| `/api/v1/cap` (intervene) | ⚠️ | 返回 404 node not found，参数格式可能需调整 |
| `/api/v1/cap` (paths) | ⚠️ | 返回 paths 字段，但缺少 distance 字段 |
| `/.well-known/cap.json` | ✅ | 返回完整能力清单 |
| `/openapi.json` | ✅ | 返回 API 规范 |

---

## 🎯 结论

### 截图 vs 实际

**截图显示的是 CAP 规范定义的理想端点结构**，但实际部署的是 **Unified API 模式**：

- ❌ **截图端点**: `/cap/v1/{primitive}` (单独的 REST 端点)
- ✅ **实际端点**: `/api/v1/cap` (统一端点 + verb 参数)

### 如何使用

应该使用 **实际可用的 `/api/v1/cap` 端点**，通过 `verb` 参数调用不同功能：

```python
# 正确用法
response = requests.post(
    "https://cap-sit.abel.ai/api/v1/cap",
    json={
        "verb": "observe.predict",  # 对应 predict 功能
        "params": {...}
    }
)

# 错误用法 (截图中的端点不存在)
response = requests.post(
    "https://cap-sit.abel.ai/cap/v1/predict",  # ❌ 404!
    json={...}
)
```

---

## 📝 文档更新建议

截图可能是 **CAP 规范定义** 或 **设计文档**，而非实际部署的 API。实际部署采用的是 **统一端点设计模式**。

建议向 CG API 团队确认：
1. 截图是否为未来规划的设计？
2. `/cap/v1/*` 端点是否会实现？
3. 还是统一使用 `/api/v1/cap` 模式？

---

*更新: 2026-03-20*
