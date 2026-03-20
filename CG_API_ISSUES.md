# Abel Graph Computer API - 问题汇总报告

**报告生成**: 2026-03-20  
**基于**: Abel Causal Benchmark 53 题完整测试  
**测试工具**: `test_cap_compatibility.py`

---

## 📊 测试概览

| 指标 | 数值 |
|------|------|
| 总测试问题 | 53 |
| 成功 | 18 (34%) |
| 失败 | 35 (66%) |
| **API 问题导致失败** | **35** |

---

## 🔴 高优先级问题

### 1. intervention_impact 端点 - 422 Unprocessable Entity

**影响**: Category B (Intervene) 全部 10 题失败

**测试请求**:
```bash
GET /graph_stats/intervention_impact?node=BTCUSD&delta=-0.05&horizon_steps=72&max_hops=3
```

**期望响应**:
```json
{
  "intervention_effect": float,
  "propagation": [...],
  "affected_nodes": [...]
}
```

**实际响应**: `422 Unprocessable Entity`

**建议检查**:
- [ ] `delta` 参数格式（是否需要特定范围？）
- [ ] `node` 参数格式（是否应为 ticker 而非 node_id？）
- [ ] `horizon_steps` 是否必需？
- [ ] 请求参数验证逻辑

**参考问题 ID**: B1-B10

---

### 2. nodes_connection 端点 - 422 Unprocessable Entity

**影响**: Category C (Path) 全部 7 题失败

**测试请求**:
```bash
GET /graph_stats/nodes_connection?node_id_1=DXY&node_id_2=BTCUSD&max_depth=3&directed=true
```

**期望响应**:
```json
{
  "path": [...],
  "hops": int,
  "tau": int,
  "intermediate_nodes": [...]
}
```

**实际响应**: `422 Unprocessable Entity`

**建议检查**:
- [ ] 参数名是否为 `node_id_1` / `node_id_2` 还是 `from` / `to`？
- [ ] `max_depth` 是否必需？
- [ ] `directed` 参数格式（boolean 还是 string？）

**参考问题 ID**: C1-C7

---

## 🟡 中优先级问题

### 3. batch/predictions 端点 - 404 Not Found

**影响**: Category E (Attest) 5 题 + Category X (Cross-Domain) 11 题 = **16 题失败**

**测试请求**:
```bash
GET /causal_graph/batch/predictions?tickers=BTCUSD,ETHUSD&analysis_mode=comparison
```

**实际响应**: `404 Not Found`

**说明**: 该端点**尚未实现**

**临时解决方案**:
- 实现批量查询端点，支持多 ticker 同时预测
- 或提供替代方案（如多次调用 single prediction）

**参考问题 ID**: E1-E5, XF_694a8b8f-XF_695a609d

---

## 🟢 低优先级问题

### 4. Explain 原语 - 部分实现

**影响**: Category D 中 1 题 (D4)

**测试请求**:
```bash
GET /causal_graph/{ticker}/prediction?include_features=true
```

**当前状态**:
- ✅ 端点存在
- ⚠️ 缺少字段: `explanation`, `feature_importance`

**期望响应**:
```json
{
  "cumulative_prediction": float,
  "probability_up": float,
  "explanation": "string",           // 缺少
  "feature_importance": [...]       // 缺少
}
```

**建议**: 添加解释性字段到现有 prediction 响应

**参考问题 ID**: D4

---

## ✅ 已正常工作的端点

以下端点**无需修复**，测试 100% 通过：

| 端点 | 用途 | 通过数 |
|------|------|--------|
| `/causal_graph/{ticker}/multi-step-prediction` | Predict | 15/15 |
| `/causal_graph/{ticker}/prediction` | Explain/Sensitivity | 4/4 |

---

## 🔧 修复优先级建议

### Phase 1 (本周)
1. **Fix intervention_impact 422 错误**
   - 检查参数验证逻辑
   - 与 benchmark 团队确认参数格式

2. **Fix nodes_connection 422 错误**
   - 检查参数名和格式
   - 确认路径查找逻辑

### Phase 2 (下周)
3. **Implement batch/predictions**
   - 新建端点或提供替代方案
   - 支持多 ticker 批量查询

### Phase 3 (可选)
4. **Enhance prediction response**
   - 添加 `explanation` 和 `feature_importance` 字段

---

## 📋 待验证参数格式

请 CG API 团队确认以下参数格式：

### intervention_impact
```
node: "BTCUSD" (ticker) 还是 "BTCUSD_close" (node_id)?
delta: -0.05 (float 范围限制?)
horizon_steps: 72 (hours?)
max_hops: 3 (integer)
```

### nodes_connection
```
node_id_1 vs from: 哪个参数名正确?
node_id_2 vs to: 哪个参数名正确?
max_depth vs depth: 哪个参数名正确?
directed: "true" vs true: string 还是 boolean?
```

### batch/predictions
```
tickers: "BTCUSD,ETHUSD" (comma-separated) 还是 ["BTCUSD", "ETHUSD"] (JSON array)?
cg_version: 必需参数?
```

---

## 📎 附件

- 完整测试报告: `cap_test_all_53/cap_compatibility_report.json`
- Benchmark 问题集: `src/abel_benchmark/references/benchmark_questions_v2_enhanced.json`
- 测试脚本: `test_cap_compatibility.py`

---

## 📞 联系方式

- **Benchmark 团队**: 提供测试用例和验证
- **CG API 团队**: 负责端点修复和实现

---

## 📝 版本历史

- v1.0 (2026-03-20): 初始问题汇总，基于 53 题测试结果
