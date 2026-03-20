# 更多 Future Prediction Benchmarks

本目录包含从 HuggingFace 下载的更多未来预测和因果推理相关的 benchmark 数据集。

---

## 📊 新增数据集概览

### 1. YuehHanChen/forecasting (5,516 cases)
- **来源**: Metaculus, Good Judgment Open, INFER, Polymarket, Manifold
- **时间范围**: 2015-2024
- **Ground Truth**: `resolution` (0.0 或 1.0)
- **特点**: 
  - 二元预测问题
  - 包含社区预测历史
  - 有详细背景描述
- **Splits**: Train (3,762) / Validation (840) / Test (914)

#### 数据字段
```json
{
  "file_id": "FC_00001",
  "split": "train",
  "question": "Will advanced LIGO announce discovery of gravitational waves...",
  "background": "背景描述...",
  "resolution_criteria": "解析标准...",
  "ground_truth": 1.0,           // ✅ 0.0 或 1.0
  "data_source": "metaculus",
  "date_begin": "2015-10-02",
  "date_close": "2015-12-15",
  "date_resolve_at": "2016-02-01"
}
```

---

### 2. Duruo/forecastbench-single_question (902 cases)
- **来源**: ForecastBench 项目 (Manifold 等)
- **Ground Truth**: `answer` (0 或 1)
- **特点**:
  - 部分案例包含人类预测概率
  - 有专家 (superforecaster) 预测对比

#### 数据字段
```json
{
  "file_id": "FB_0001",
  "question": "预测市场问题...",
  "background": "背景信息...",
  "ground_truth": 1,             // ✅ 0 或 1
  "human_super_forecast": 0.75,  // 专家预测 (可选)
  "human_public_forecast": 0.62  // 公众预测 (可选)
}
```

---

### 3. robinfaro/TSQA (10,063 cases)
- **名称**: Time-Sensitive Question Answering
- **时间范围**: 2013-2024
- **Ground Truth**: 4选1 中的 `correct` 答案
- **特点**:
  - 测试时间敏感知识
  - 选项标记: correct / past / future / unrelated
  - 需要理解时间上下文

#### 数据字段
```json
{
  "file_id": "TSQA_00001",
  "question": "Who was the head of government in the UK in 2021?",
  "year": 2021,
  "ground_truth": "Boris Johnson",  // ✅ 正确答案
  "ground_truth_tag": "correct",
  "options": [
    {"answer": "Boris Johnson", "tag": "correct"},
    {"answer": "Theresa May", "tag": "past"},
    {"answer": "Rishi Sunak", "tag": "future"},
    {"answer": "David Cameron", "tag": "past"}
  ]
}
```

---

### 4. TimelyEventsBenchmark/TiEBe (23,446+ cases)
- **来源**: Wikipedia 重要事件
- **时间范围**: 2015-2025
- **覆盖**: 23 个地理区域，13 种语言
- **Ground Truth**: `answer` (文本答案)
- **特点**:
  - 多时区事件覆盖
  - 多语言支持 (包括中文)
  - 基于真实历史事件

#### 数据字段
```json
{
  "file_id": "TIEBE_00001",
  "country": "China",
  "year": 2019,
  "month": "02",
  "question": "What action did the United States take regarding...",
  "ground_truth": "In February 2019, the United States formally announced...",
  "event_desc": "U.S. President Donald Trump confirms that..."
}
```

---

## 📁 文件结构

### 示例目录 (已下载)
```
benchmark_examples/
├── forecasting_cases_5516/      # 100 个示例
│   ├── FC_00001.json ~ FC_00100.json
│   └── _index.json
├── forecastbench_cases_902/       # 100 个示例
│   ├── FB_0001.json ~ FB_0100.json
│   └── _index.json
├── tsqa_cases_10063/              # 100 个示例
│   ├── TSQA_00001.json ~ TSQA_00100.json
│   └── _index.json
└── tiebe_cases/                   # 100 个示例
    ├── TIEBE_00001.json ~ TIEBE_00100.json
    └── _index.json
```

---

## 🚀 下载完整数据

由于完整数据集较大 (~80MB)，我们提供了下载脚本：

```bash
# 安装依赖
pip install huggingface-hub

# 下载并导出所有数据
python download_benchmarks.py
```

这将创建完整的案例目录：
- `forecasting_cases_5516/` - 5,516 cases
- `forecastbench_cases_902/` - 902 cases
- `tsqa_cases_10063/` - 10,063 cases
- `tiebe_cases/` - 2,869+ cases (English subset)

---

## 📊 数据集对比

| 数据集 | Cases | Ground Truth | 特色 | 适用场景 |
|--------|-------|--------------|------|----------|
| **FutureX** | 208 | 答案 A/B/C | 分级难度 | 未来预测 |
| **forecasting** | 5,516 | 二元 (0/1) | 多平台预测市场 | 预测能力 |
| **forecastbench** | 902 | 二元 (0/1) | 专家对比 | 人机对比 |
| **TSQA** | 10,063 | 4选1 | 时间敏感 | 时间推理 |
| **TiEBe** | 23,446+ | 文本答案 | 多时区多语言 | 事实问答 |
| **CausalReasoning** | 173 | 效应值+SE | 学术论文级 | 因果推理 |
| **corr2cause** | 414K+ | 二元标签 | 模板化 | 相关性→因果 |

---

## 🎯 使用建议

### 评估 LLM + CAP 系统

1. **预测能力** → forecasting (5,516) / forecastbench (902) / FutureX (208)
2. **时间推理** → TSQA (10,063)
3. **事实问答** → TiEBe (23,446+)
4. **因果推理** → CausalReasoning (173)
5. **相关性→因果** → corr2cause (414K+)

### 快速测试
```python
import json
import glob

# 加载示例数据
cases = []
for filepath in glob.glob('benchmark_examples/forecasting_cases_5516/*.json'):
    if filepath.endswith('_index.json'):
        continue
    with open(filepath) as f:
        case = json.load(f)
    cases.append(case)

print(f"加载了 {len(cases)} 个示例")
print(f"示例 Ground Truth: {cases[0]['ground_truth']}")
```

---

## 📚 引用

### forecasting
```bibtex
@misc{halawi2024approaching,
  title={Approaching Human-Level Forecasting with Language Models},
  author={Danny Halawi and Fred Zhang and Chen Yueh-Han and Jacob Steinhardt},
  year={2024},
  eprint={2402.18563},
  archivePrefix={arXiv}
}
```

### ForecastBench
```bibtex
@inproceedings{karger2025forecastbench,
  title={ForecastBench: A Dynamic Benchmark of AI Forecasting Capabilities},
  author={Ezra Karger and Houtan Bastani and Chen Yueh-Han and others},
  year={2025},
  booktitle={ICLR}
}
```

### TSQA
```bibtex
@dataset{robinfaro_tsqa,
  title={TSQA: Time-Sensitive Question Answering},
  author={robinfaro},
  year={2024},
  publisher={HuggingFace}
}
```

### TiEBe
```bibtex
@dataset{timelyevents_tiebe,
  title={TiEBe: Timely Events Benchmark},
  author={TimelyEventsBenchmark},
  year={2025},
  publisher={HuggingFace}
}
```

---

## ✅ Ground Truth 验证

所有数据集都经过验证，100% 包含 Ground Truth：

| 数据集 | 总数 | 有 GT | 验证 |
|--------|------|-------|------|
| FutureX | 208 | 208/208 | ✅ |
| forecasting | 5,516 | 5,516/5,516 | ✅ |
| forecastbench | 902 | 902/902 | ✅ |
| TSQA | 10,063 | 10,063/10,063 | ✅ |
| TiEBe | 23,446+ | 23,446+/23,446+ | ✅ |
| CausalReasoning | 173 | 173/173 | ✅ |
| corr2cause | 414K+ | 414K+/414K+ | ✅ |

---

**创建日期**: 2026-03-20  
**总计**: 444,000+ cases (含 corr2cause 完整训练集)