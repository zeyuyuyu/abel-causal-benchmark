# Abel Graph Computer API - 问题反馈

**发件人**: Abel Causal Benchmark Team  
**收件人**: CG API Team  
**日期**: 2026-03-20  
**主题**: API 端点问题修复请求

---

## 一句话总结

基于 53 题完整测试，**18 题通过，35 题因 API 问题失败**。

---

## 🔴 需要修复 (高优先级)

### 1. intervention_impact - 422 错误
- **影响**: 10 个干预测试失败 (Category B)
- **问题**: 参数格式验证失败
- **示例请求**:
  ```
  GET /graph_stats/intervention_impact?node=BTCUSD&delta=-0.05&horizon_steps=72
  ```
- **请确认**: `delta` 格式？`node` 用 ticker 还是 node_id？

### 2. nodes_connection - 422 错误
- **影响**: 7 个路径测试失败 (Category C)
- **问题**: 参数格式验证失败
- **示例请求**:
  ```
  GET /graph_stats/nodes_connection?node_id_1=DXY&node_id_2=BTCUSD&max_depth=3
  ```
- **请确认**: 参数名是 `node_id_1` 还是 `from`？`max_depth` 还是 `depth`？

---

## 🟡 需要实现 (中优先级)

### 3. batch/predictions - 404 不存在
- **影响**: 16 个批量测试失败 (Category E + X)
- **问题**: 端点未实现
- **需求**: 支持多 ticker 同时预测
- **示例**:
  ```
  GET /causal_graph/multi-step-prediction/batch?tickers=BTCUSD,ETHUSD
  ```

---

## 🟢 建议优化 (低优先级)

### 4. prediction 响应增强
- **问题**: 缺少解释字段
- **建议**: 添加 `explanation` 和 `feature_importance`
- **影响**: 1 个 explain 测试

---

## ✅ 无需修复 (已正常工作)

| 端点 | 状态 | 通过率 |
|------|------|--------|
| `/causal_graph/{ticker}/multi-step-prediction` | ✅ | 15/15 |
| `/causal_graph/{ticker}/prediction` | ✅ | 4/4 |

---

## 优先级建议

| 优先级 | 问题 | 影响题数 |
|--------|------|----------|
| 🔴 P0 | 修复 intervention_impact 422 | 10 |
| 🔴 P0 | 修复 nodes_connection 422 | 7 |
| 🟡 P1 | 实现 batch/predictions | 16 |
| 🟢 P2 | 增强 prediction 响应 | 1 |

---

**请确认参数格式后，我们可以配合验证修复效果。**

---

## 附件

- **详细报告**: `CG_API_ISSUES.md`
- **测试脚本**: `test_cap_compatibility.py`
- **测试数据**: `cap_test_all_53/cap_compatibility_report.md`
