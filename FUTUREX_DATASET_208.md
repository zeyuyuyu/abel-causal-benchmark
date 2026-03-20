# FutureX 数据集 - 208 Cases (带 Ground Truth)

**来源**: train-00000-of-00001.parquet  
**创建日期**: 2026-03-20  
**总 Cases**: 208  
**全部有 Ground Truth**: ✅

---

## 📊 数据集统计

### Level 分布
| Level | 数量 | 占比 | 说明 |
|-------|------|------|------|
| L1 | 86 | 41% | 简单 |
| L2 | 82 | 39% | 中等 |
| L3 | 14 | 7% | 困难 |
| L4 | 26 | 13% | 专家 |

### Ground Truth 类型
| 类型 | 数量 | 说明 |
|------|------|------|
| 单选 (1个答案) | 163 | 78% |
| 多选 (2-5个答案) | 35 | 17% |
| 多选 (5+个答案) | 10 | 5% |

---

## 📁 文件位置

```
references/futurex_dataset_208_cases.json
```

---

## 📋 数据结构

```json
{
  "metadata": {
    "source_file": "train-00000-of-00001.parquet",
    "total_cases": 208,
    "level_distribution": {
      "L1": 86,
      "L2": 82,
      "L3": 14,
      "L4": 26
    }
  },
  "cases": [
    {
      "id": "694bdd0b43684c005d3473f1",
      "title": "问题标题",
      "level": 2,
      "end_time": "2026-01-18 00:00:00",
      "ground_truth": "['A', 'B', 'C']",
      "options": [
        {"id": "A", "text": "选项A描述"},
        {"id": "B", "text": "选项B描述"},
        ...
      ],
      "prompt_preview": "提示词预览"
    }
  ]
}
```

---

## 💡 使用示例

### Python
```python
import json

# 加载数据集
with open('references/futurex_dataset_208_cases.json') as f:
    data = json.load(f)

cases = data['cases']

# 遍历所有 cases
for case in cases:
    print(f"ID: {case['id']}")
    print(f"Title: {case['title']}")
    print(f"Level: L{case['level']}")
    print(f"Ground Truth: {case['ground_truth']}")
    print(f"Options: {len(case['options'])}")
    
    # 解析 ground truth
    gt = eval(case['ground_truth'])
    print(f"Answers: {gt}")
```

### 筛选特定 Level
```python
# 只获取 L1 的 cases
l1_cases = [c for c in cases if c['level'] == 1]
print(f"L1 cases: {len(l1_cases)}")
```

---

## 🎯 Ground Truth 示例

### 单选
```json
{
  "title": "2025 CAF Cup of Nations (AFCON) Winner",
  "ground_truth": "['A']",
  "options": [
    {"id": "A", "text": "Senegal"},
    {"id": "B", "text": "Morocco"},
    {"id": "C", "text": "Algeria"},
    {"id": "D", "text": "Egypt"}
  ]
}
```

### 多选
```json
{
  "title": "Which candidates will make it to the second round",
  "ground_truth": "['C', 'P']",
  "options": [
    {"id": "A", "text": "Candidate A"},
    {"id": "B", "text": "Candidate B"},
    ...
  ]
}
```

---

## 🔍 与现有 Benchmark 的关系

这个数据集包含 **真实的 ground truth**，可以用来：

1. **验证我们的 test cases** - 对比预测的准确性
2. **扩充 test cases** - 提取金融相关的 cases 加入 benchmark
3. **训练/测试** - 作为有标签的数据集使用

### 金融相关的 Cases (筛选)
```python
finance_keywords = ['stock', 'price', 'market', 'crypto', 'bitcoin', 'rate', 'dollar']
finance_cases = [
    c for c in cases 
    if any(kw in c['title'].lower() for kw in finance_keywords)
]
```

---

## ✅ 优势

- **全部有 Ground Truth** - 208/208 cases
- **多层级** - L1-L4 分布合理
- **多选/单选混合** - 163单选 + 45多选
- **FutureX 官方** - 来自 FutureX Challenge

---

## 📚 相关文件

- `references/futurex_official_81_cases.json` - D25 周数据 (81 cases, 待 resolve)
- `references/futurex_dataset_208_cases.json` - 本数据集 (208 cases, 有 ground truth)
- `test_cases_futurex_style/` - 我们的 benchmark cases (FutureX 风格)

---

**注意**: 这个数据集可以直接用于测试，因为所有 cases 都有确定的 ground truth！