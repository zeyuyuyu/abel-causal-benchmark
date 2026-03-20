# Abel Causal Benchmark - 多维度分类系统

**创建时间**: 2026-03-20  
**版本**: v2.5-futurex-d25-multidimensional  
**总 Case 数**: 96

---

## 📊 多维度分类架构

每个 benchmark case 按以下 5 个维度分类：

### 维度 1: Domain (领域)
- `finance` - 金融/市场
- `political` - 政治/选举
- `sports` - 体育
- `tech` - 科技/AI
- `entertainment` - 娱乐
- `science` - 科学/教育
- `social` - 社会事件
- `other` - 其他

### 维度 2: CAP Ability (CAP 能力)
- `full` - 完全可用 (节点在图中)
- `partial` - 部分可用 (领域相关，节点需验证)
- `none` - 不可用
- `llm_only` - 仅 LLM

### 维度 3: Data Availability (数据可用性)
- `realtime` - 实时数据
- `historical` - 历史数据
- `unavailable` - 不可用

### 维度 4: Time Horizon (时间范围)
- `short_term` - 短期 (几天到几周)
- `medium_term` - 中期 (几周到几个月)
- `long_term` - 长期 (几个月到几年)

### 维度 5: Complexity (复杂度)
- `L1` - 简单 (直接预测)
- `L2` - 中等 (多因素)
- `L3` - 复杂 (推理链)
- `L4` - 专家级 (综合判断)

---

## 📈 完整统计

### 按领域分布

| 领域 | 数量 | 占比 | CAP 可用性 |
|------|------|------|-----------|
| finance | 69 | 72% | full/partial |
| tech | 6 | 6% | llm_only |
| political | 6 | 6% | llm_only |
| sports | 5 | 5% | llm_only |
| entertainment | 5 | 5% | llm_only |
| other | 4 | 4% | none |
| science | 1 | 1% | llm_only |

### 按 CAP 能力分布

| 能力 | 数量 | 占比 | 推荐方法 |
|------|------|------|----------|
| full | 17 | 18% | CAP_only |
| partial | 52 | 54% | CAP_first_then_LLM |
| none | 4 | 4% | Hybrid |
| llm_only | 23 | 24% | LLM_only |

### Domain × CAP Ability 交叉矩阵

```
Domain          | Full | Partial | None | LLM Only | Total
----------------|------|---------|------|----------|-------
finance         |   17 |      52 |    0 |        0 |    69
political       |    0 |       0 |    0 |        6 |     6
tech            |    0 |       0 |    0 |        6 |     6
sports          |    0 |       0 |    0 |        5 |     5
entertainment   |    0 |       0 |    0 |        5 |     5
other           |    0 |       0 |    4 |        0 |     4
science         |    0 |       0 |    0 |        1 |     1
----------------|------|---------|------|----------|-------
TOTAL           |   17 |      52 |    4 |       23 |    96
```

---

## 🎯 测试优先级

### 🔴 High Priority (69 cases - 72%)
**金融类问题，CAP 可测试**

特点:
- Domain: finance
- CAP Ability: full / partial
- 包含 FutureX D25 的 7 个金融问题
- 我们自己的金融预测问题

测试方法:
- CAP_only (17 cases)
- CAP_first_then_LLM (52 cases)

### ⚪ Low Priority (27 cases - 28%)
**非金融类，需要 LLM**

特点:
- Domain: political, sports, tech, entertainment, science
- CAP Ability: llm_only / none

测试方法:
- LLM_only (23 cases)
- Hybrid (4 cases)

---

## 🚀 测试阶段策略

### Phase 1: CAP Pure (17 cases)
**目标**: 验证纯 CAP 能力

包含:
- A1 (BTCUSD)
- A4 (TSLA)
- A6 (ETHUSD)
- B1-B2 (Intervention)
- ... (其他 known ticker)

Metrics:
- observe.predict 准确率
- intervene.do 可用性
- graph.paths 准确性

### Phase 2: CAP + LLM Hybrid (52 cases)
**目标**: LLM 决策 + CAP 计算

流程:
1. LLM 分析用户需求
2. LLM 决策是否调用 CAP
3. CAP 执行因果计算
4. LLM 解释并返回结果

测试重点:
- LLM 选择正确的 verb
- LLM 提取正确的参数
- 组合结果的准确性

### Phase 3: LLM Only (23 cases)
**目标**: 纯 LLM 推理能力

类型:
- 政治选举预测
- 体育比赛结果
- 科技发展趋势
- 社会事件预测

### Phase 4: Full Integration (96 cases)
**目标**: 端到端自动化

场景:
- Agent 自动分类问题
- 自动选择最佳方法
- 动态组合 CAP + LLM
- 自适应置信度评估

---

## 📋 示例 Case 分类

### Example 1: A1 (BTCUSD)
```json
{
  "id": "A1",
  "question": "Will BTCUSD go up in the next 5 hours?",
  "multidimensional_classification": {
    "dimensions": {
      "domain": {"value": "finance", "confidence": 0.95},
      "cap_ability": {"value": "full", "reason": "Known ticker in causal graph"},
      "data_availability": "realtime",
      "time_horizon": "short_term",
      "complexity": "L1"
    },
    "recommended_approach": "CAP_only",
    "test_priority": "high"
  }
}
```

### Example 2: Political Election
```json
{
  "id": "B10",
  "question": "Will a new international conflict start next week?",
  "multidimensional_classification": {
    "dimensions": {
      "domain": {"value": "political", "confidence": 0.90},
      "cap_ability": {"value": "llm_only", "reason": "political not supported by causal graph"},
      "data_availability": "unavailable",
      "time_horizon": "short_term",
      "complexity": "L3"
    },
    "recommended_approach": "LLM_only",
    "test_priority": "low"
  }
}
```

---

## 🔧 使用方法

### 查询特定分类的问题

```python
import json

# 加载 benchmark
with open('benchmark_questions_v2_futurex_d25.json') as f:
    data = json.load(f)

# 筛选 high priority 问题
high_priority = [
    q for q in data['questions']
    if q['multidimensional_classification']['test_priority'] == 'high'
]

# 筛选 finance + full CAP
finance_cap = [
    q for q in data['questions']
    if q['multidimensional_classification']['dimensions']['domain']['value'] == 'finance'
    and q['multidimensional_classification']['dimensions']['cap_ability']['value'] == 'full'
]

# 筛选需要 hybrid 方法的问题
hybrid_questions = [
    q for q in data['questions']
    if q['multidimensional_classification']['recommended_approach'] == 'CAP_first_then_LLM'
]
```

### 统计脚本

```bash
# 统计各领域问题数
python3 -c "
import json
data = json.load(open('benchmark_questions_v2_futurex_d25.json'))
for q in data['questions']:
    cat = q['multidimensional_classification']['dimensions']['domain']['value']
    print(cat)
" | sort | uniq -c | sort -rn
```

---

## 📚 相关文档

- `CAP_REFERENCE_LEARNING.md` - CAP 实现研究
- `BENCHMARK_TEST_RESULTS.md` - 测试结果
- `FUTUREX_OFFICIAL_DATA.md` - FutureX D25 分析
- `test_llm_cap_hybrid.py` - 混合测试脚本

---

## 🎯 下一步

1. **Phase 1 测试**: 运行 17 个 CAP_pure cases
2. **创建筛选工具**: 按维度快速筛选问题
3. **可视化**: 生成交互式分类图表
4. **自动化**: Agent 自动分类新加入的问题

---

**总览**: 96 个 cases，72% 可 CAP 测试，28% 需 LLM，多维度分类支持灵活测试策略。
