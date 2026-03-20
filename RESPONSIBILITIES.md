# Abel Causal Benchmark - 职责边界说明

## 🎯 我们的职责（Benchmark 团队）

### ✅ 我们负责

1. **Benchmark 框架**
   - 问题定义（53 个测试问题）
   - CAP 原语映射规范
   - 评分系统（CEVS）
   - 测试脚本和报告生成

2. **测试覆盖**
   - 设计测试用例覆盖所有 CAP 原语
   - 验证 API 响应格式是否符合 CAP 规范
   - 提供测试报告和兼容性分析

3. **问题集维护**
   - 问题的业务逻辑
   - 期望的输入/输出格式
   - ground truth 定义

4. **文档和工具**
   - 使用文档
   - 可视化报告
   - 测试脚本

---

## 🚫 不负责的内容

### ❌ CG API 团队负责

1. **API 端点实现**
   ```
   /causal_graph/{ticker}/multi-step-prediction  ✅ 已实现
   /graph_stats/intervention_impact              ❌ 需修复（422 错误）
   /graph_stats/nodes_connection                 ❌ 需修复（422 错误）
   /causal_graph/batch/predictions               ❌ 需实现（404 不存在）
   ```

2. **参数解析**
   - 请求参数的验证和解析
   - 错误处理和状态码返回

3. **预测算法**
   - 因果图计算
   - Markov blanket 推理
   - 干预分析 (do-calculus)

4. **数据层**
   - 因果图数据维护
   - ticker 节点关系
   - 历史数据更新

---

## 📊 当前状态（我们已完成的工作）

| 类别 | 问题数 | 状态 | 说明 |
|------|--------|------|------|
| A (Predict) | 8 | ✅ **已验证** | API 正常工作 |
| F (FutureX) | 7 | ✅ **已验证** | API 正常工作 |
| B (Intervene) | 10 | ⏸️ **待 CG 修复** | API 返回 422 |
| C (Path) | 7 | ⏸️ **待 CG 修复** | API 返回 422 |
| D (Sensitivity) | 3 | ✅ **已验证** | API 正常工作 |
| E (Attest) | 5 | ⏸️ **待 CG 实现** | API 404 |
| X (Cross-Domain) | 11 | ⏸️ **待 CG 实现** | API 404 |

**总计**: 53 个问题，18 个可测试，35 个待 CG API 修复/实现

---

## 📝 给 CG API 团队的反馈

基于我们的测试，CG API 团队需要：

### 🔧 高优先级修复

1. **intervention_impact 端点 (Category B)**
   - 问题: 422 Unprocessable Entity
   - 建议: 检查 `delta` 和 `node` 参数格式
   - 影响: 10 个干预场景无法测试

2. **nodes_connection 端点 (Category C)**
   - 问题: 422 Unprocessable Entity
   - 建议: 检查 `from`, `to`, `depth` 参数
   - 影响: 7 个路径追踪问题无法测试

### 🆕 需要实现的新端点

3. **batch/predictions 端点 (Category E & X)**
   - 问题: 404 Not Found (端点不存在)
   - 需求: 支持多 ticker 批量查询
   - 影响: 17 个 attest 问题无法测试

---

## ✅ 我们的交付物

### 已完成 ✅

1. **53 题完整 Benchmark**
   - 涵盖 7 个类别
   - 包含 FutureX 和跨领域问题
   - 符合 CAP 规范

2. **测试框架**
   - `test_cap_compatibility.py` - 兼容性测试
   - `test_cap_with_benchmark.py` - 完整 benchmark 运行
   - CEVS 评分系统

3. **可视化报告**
   - 6 张对比图表
   - 详细测试报告 (Markdown + JSON)

4. **问题分类**
   - 明确标注哪些是 API 问题
   - 提供修复建议

---

## 🤝 协作流程

```
[CG API 团队]          [Benchmark 团队]
     │                       │
     ├── 实现 API 端点 ──────│
     │                       │
     │                       ├── 设计测试用例
     │                       │
     │◄─── 运行测试 ─────────│
     │                       │
     ├── 修复问题 ───────────│
     │                       │
     │◄─── 重新测试 ─────────│
     │                       │
     └── API 稳定 ──────────►├── 发布 benchmark
```

---

## 📋 验收标准

### Benchmark 完成标准 ✅

- [x] 53 个问题定义完成
- [x] CAP 原语映射规范
- [x] 测试脚本可运行
- [x] 报告生成正常
- [x] 文档完整

### API 完成标准（CG 团队）⏳

- [ ] `intervention_impact` 端点修复（无 422 错误）
- [ ] `nodes_connection` 端点修复（无 422 错误）
- [ ] `batch/predictions` 端点实现（无 404 错误）
- [ ] 所有 53 题测试通过

---

## 📞 联系信息

- **Benchmark 团队**: 负责测试框架和问题集
- **CG API 团队**: 负责端点实现和修复
- **协调**: 共同确保 CAP 协议兼容性

---

*最后更新: 2026-03-20*
