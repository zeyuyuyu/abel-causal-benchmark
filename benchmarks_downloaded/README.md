# HuggingFace Benchmarks 数据集

本目录包含从 HuggingFace 下载的因果推理和未来预测相关的 benchmark 数据集，**保留源格式**。

---

## 📊 数据集概览

### 1. CausalReasoningBenchmark
**来源**: [syrgkanislab/CausalReasoningBenchmark](https://huggingface.co/datasets/syrgkanislab/CausalReasoningBenchmark)

| 属性 | 值 |
|------|-----|
| **总查询数** | **173** |
| **数据集数量** | 138 |
| **来源** | 85 篇同行评审论文 + 教科书 |
| **Ground Truth** | ✅ 效应值 (effect) + 标准误 (standard_error) |

#### 识别策略分布
| 策略 | 数量 | 占比 |
|------|------|------|
| Difference-in-Differences | 67 | 38.7% |
| Regression Discontinuity | 44 | 25.4% |
| Conditional Exogeneity | 39 | 22.5% |
| Instrumental Variable | 22 | 12.7% |
| RCT | 1 | 0.6% |

#### Ground Truth 效应值统计
- 均值: 27.19
- 中位数: 0.13
- 标准差: 248.05
- 范围: [-42.45, 2735.54]

#### 数据结构 (causal_queries.json/csv)
```json
{
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

#### 评估维度
1. **识别 (Identification)**: 选择正确的因果策略、处理变量、结果变量、控制变量
2. **估计 (Estimation)**: 产生量化的因果效应估计值和标准误

---

### 2. corr2cause
**来源**: [causal-nlp/corr2cause](https://huggingface.co/datasets/causal-nlp/corr2cause)

| 属性 | 值 |
|------|-----|
| **任务类型** | 相关性到因果性推理 |
| **完整训练集** | 411,468 条 (366MB) |
| **测试集** | 2,324 条 |
| **Ground Truth** | ✅ 0/1 标签 |

#### 本仓库包含
- `train_sample_5k.csv` - 训练集样本 (5,000 条)
- `test.csv` - 完整测试集
- `README.md` - 原始说明
- `NOTE.md` - 本仓库说明

#### 数据格式
```csv
input,label,num_variables,template
"Premise: Suppose there is a closed system of 4 variables...",0,4,has_collider
```

- **input**: 前提和假设文本（包含变量相关性描述和假设）
- **label**: 0/1 (假设是否成立)
- **num_variables**: 系统变量数量
- **template**: 任务模板类型

#### 完整数据下载
原始 train.csv (366MB) 可从 HuggingFace 下载：
```bash
huggingface-cli download causal-nlp/corr2cause \
  --repo-type dataset \
  --local-dir ./corr2cause
```

---

## 📁 文件结构

```
benchmarks_downloaded/
├── README.md                          # 本文件
├── CausalReasoningBenchmark/
│   ├── causal_queries.json            # 主要查询文件 (JSON格式)
│   ├── causal_queries.csv             # 主要查询文件 (CSV格式)
│   └── .cache/                        # HuggingFace 缓存
├── corr2cause/
│   ├── train.csv                      # 训练数据
│   ├── test.csv                       # 测试数据
│   ├── README.md                      # 说明
│   └── .cache/                        # HuggingFace 缓存
└── .DS_Store
```

---

## 🔄 下载方法

### 使用 HuggingFace CLI
```bash
# 安装
pip install huggingface-hub

# 下载 CausalReasoningBenchmark
huggingface-cli download syrgkanislab/CausalReasoningBenchmark \
  --repo-type dataset \
  --local-dir ./CausalReasoningBenchmark

# 下载 corr2cause
huggingface-cli download causal-nlp/corr2cause \
  --repo-type dataset \
  --local-dir ./corr2cause
```

### 使用 Python API
```python
from huggingface_hub import hf_hub_download

# 下载文件
path = hf_hub_download(
    repo_id="syrgkanislab/CausalReasoningBenchmark",
    filename="causal_queries.json",
    repo_type="dataset",
    local_dir="./CausalReasoningBenchmark"
)
```

---

## 📊 与 FutureX 的对比

| Benchmark | 类型 | 问题数 | Ground Truth | 更新频率 |
|-----------|------|--------|--------------|----------|
| **FutureX** | 未来事件预测 | 208 (D25) | ✅ 答案 | 每周 |
| **CausalReasoningBenchmark** | 因果推理 | 173 | ✅ 效应值+标准误 | 静态 |
| **corr2cause** | 相关性→因果 | 207K+ | ✅ 标签 | 静态 |

---

## 💡 使用建议

### 评估 LLM + CAP 系统
1. **FutureX cases** (已有) - 测试未来预测能力
2. **CausalReasoningBenchmark** - 测试因果推理的准确性和量化估计能力
3. **corr2cause** - 测试从相关性推断因果性的能力

### 数据特点
- **CausalReasoningBenchmark**: 学术级因果问题，需要识别因果策略并量化效应
- **FutureX**: 真实世界未来事件，有确定答案
- **corr2cause**: 大规模相关性到因果性的二元推理

---

## 📚 引用

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
  publisher = {HuggingFace},
  url = {https://huggingface.co/datasets/causal-nlp/corr2cause}
}
```

---

## ⚠️ 注意事项

1. **缓存文件**: `.cache/` 目录包含 HuggingFace 的下载缓存，可以删除以节省空间
2. **数据格式**: 所有文件保留原始格式（JSON/CSV/Parquet）
3. **Ground Truth**: 所有数据集都包含确定性的 ground truth 答案
4. **授权**: 所有数据集都是公开可用的，无需特殊授权

---

**下载日期**: 2026-03-20  
**下载方式**: huggingface-hub Python API  
**保留源格式**: ✅