# Benchmark Cases - 单独文件格式

本目录包含按 **每个 case 一个文件** 格式组织的 benchmark 数据，**全部带有 Ground Truth**。

---

## 📊 数据集总览

| 数据集 | 来源 | Cases | Ground Truth | 格式 |
|--------|------|-------|--------------|------|
| **futurex_cases_208** | FutureX D25 | 208 | 答案 (A/B/C...) | JSON/文件 |
| **causal_reasoning_cases_173** | CausalReasoningBenchmark | 173 | effect + SE | JSON/文件 |
| **corr2cause_cases** | corr2cause | 1,162 | label (0/1) | JSON/文件 |

**总计**: **1,543 个 cases**，每个都有确定的 Ground Truth！

---

## 📁 文件结构

```
benchmark_root/
├── futurex_cases_208/
│   ├── FX_001.json ~ FX_208.json    # 208 cases
│   └── _index.json                   # 索引文件
│
├── causal_reasoning_cases_173/
│   ├── CR_001.json ~ CR_173.json     # 173 cases
│   └── _index.json                   # 索引文件
│
└── corr2cause_cases/
    ├── C2C_0001.json ~ C2C_1162.json # 1,162 cases
    └── _index_test.json              # 索引文件
```

---

## 🔍 文件格式详解

### 1. FutureX (FX_*.json)

```json
{
  "id": "694bdd0b43684c005d3473f1",
  "prompt": "You are an agent that can predict future events...",
  "end_time": "2026-01-18 00:00:00",
  "level": 2,
  "title": "问题标题",
  "ground_truth": "['A', 'B']",
  "__index_level_0__": 0
}
```

| 字段 | 说明 |
|------|------|
| `id` | 原始 ID |
| `prompt` | 完整提示词（包含选项 A/B/C） |
| `end_time` | 截止时间 |
| `level` | 难度等级 (1-4) |
| `title` | 问题标题 |
| `ground_truth` | 正确答案 (Python list 格式) |

---

### 2. CausalReasoning (CR_*.json)

```json
{
  "file_id": "CR_001",
  "index": 1,
  "dataset_group": "research_papers",
  "causal_question": "For countries that newly experienced...",
  "vague_question": "What happened to mining exploration...",
  "identification_strategy": "Difference-in-Differences",
  "metadata_path": "data/ds_0001/metadata.txt",
  "data_path": "data/ds_0001/data/data.csv",
  "identification_spec": "solutions/.../identification.json",
  "estimation_code": "solutions/.../estimation.py",
  "effect": -0.08348,
  "standard_error": 0.41718
}
```

| 字段 | 说明 |
|------|------|
| `effect` | **Ground Truth** - 因果效应估计值 |
| `standard_error` | **Ground Truth** - 标准误 |
| `identification_strategy` | 识别策略 (DiD/RD/CE/IV/RCT) |
| `causal_question` | 因果问题（正式） |
| `vague_question` | 因果问题（通俗版） |

#### 识别策略分布
| 策略 | 数量 | 占比 |
|------|------|------|
| Difference-in-Differences | 67 | 38.7% |
| Regression Discontinuity | 44 | 25.4% |
| Conditional Exogeneity | 39 | 22.5% |
| Instrumental Variable | 22 | 12.7% |
| RCT | 1 | 0.6% |

---

### 3. corr2cause (C2C_*.json)

```json
{
  "file_id": "C2C_0001",
  "input": "Premise: Suppose there is a closed system of 2 variables, A and B...\nHypothesis: There exists at least one collider...",
  "label": 0,
  "num_variables": 2,
  "template": "has_collider"
}
```

| 字段 | 说明 |
|------|------|
| `input` | 前提 + 假设文本 |
| `label` | **Ground Truth** - 0/1 (假设是否成立) |
| `num_variables` | 变量数量 (2-6) |
| `template` | 任务模板类型 |

#### 标签分布
| label | 数量 | 说明 |
|-------|------|------|
| 0 | 982 | 假设不成立 |
| 1 | 180 | 假设成立 |

#### 模板类型分布
| 模板 | 数量 |
|------|------|
| non-parent ancestor | 195 |
| parent | 194 |
| child | 194 |
| has_collider | 193 |
| non-child descendant | 193 |
| has_confounder | 193 |

---

## 🔄 使用示例

### 加载单个 case
```python
import json

# FutureX
with open('futurex_cases_208/FX_005.json') as f:
    case = json.load(f)
print(f"Title: {case['title']}")
print(f"Ground Truth: {case['ground_truth']}")

# CausalReasoning
with open('causal_reasoning_cases_173/CR_001.json') as f:
    case = json.load(f)
print(f"Effect: {case['effect']}")
print(f"SE: {case['standard_error']}")

# corr2cause
with open('corr2cause_cases/C2C_0001.json') as f:
    case = json.load(f)
print(f"Label: {case['label']}")
print(f"Template: {case['template']}")
```

### 批量加载
```python
import glob
import json

# 加载所有 FutureX cases
cases = []
for filepath in glob.glob('futurex_cases_208/FX_*.json'):
    with open(filepath) as f:
        cases.append(json.load(f))
print(f"Loaded {len(cases)} cases")
```

### 使用索引快速查找
```python
# 加载索引
with open('causal_reasoning_cases_173/_index.json') as f:
    index = json.load(f)

# 筛选 DiD 策略的 cases
did_cases = [c for c in index['cases'] if c['identification_strategy'] == 'Difference-in-Differences']
print(f"DiD cases: {len(did_cases)}")

# 加载特定 case
with open(f"causal_reasoning_cases_173/{did_cases[0]['filename']}") as f:
    case = json.load(f)
```

---

## 🎯 评估维度对比

| Benchmark | 评估重点 | Ground Truth | 复杂度 |
|-----------|----------|--------------|--------|
| **FutureX** | 未来事件预测 | 答案 (离散) | L1-L4 |
| **CausalReasoning** | 因果识别 + 估计 | 效应值 (连续) | 学术论文级 |
| **corr2cause** | 相关性→因果推理 | 二元判断 | 模板化 |

---

## ✅ Ground Truth 验证

所有 cases 都经过验证，**100% 包含 Ground Truth**：

| 数据集 | 总数 | 有 GT | 验证结果 |
|--------|------|-------|----------|
| futurex_cases_208 | 208 | 208/208 | ✅ |
| causal_reasoning_cases_173 | 173 | 173/173 | ✅ |
| corr2cause_cases | 1,162 | 1,162/1,162 | ✅ |

---

## 📚 引用

### FutureX
```bibtex
@misc{zeng2025futurexadvancedlivebenchmark,
  title={FutureX: An Advanced Live Benchmark for LLM Agents in Future Prediction},
  author={Zhiyuan Zeng et al.},
  year={2025},
  eprint={2508.11987},
  archivePrefix={arXiv},
}
```

### CausalReasoningBenchmark
```bibtex
@article{causalreasoningbenchmark2026,
  title={CausalReasoningBenchmark: A Real-World Benchmark for 
         Disentangled Evaluation of Causal Identification and Estimation},
  author={Sawarni, Ayush and Tan, Jiyuan and Syrgkanis, Vasilis},
  journal={arXiv preprint arXiv:2602.20571},
  year={2026}
}
```

### corr2cause
```bibtex
@dataset{causalnlp_corr2cause,
  author = {causal-nlp},
  title = {corr2cause: Correlation to Causation Dataset},
  year = {2024},
  publisher = {HuggingFace}
}
```

---

**创建日期**: 2026-03-20  
**格式**: 每个 case 一个 JSON 文件  
**所有 cases 都有 Ground Truth**: ✅