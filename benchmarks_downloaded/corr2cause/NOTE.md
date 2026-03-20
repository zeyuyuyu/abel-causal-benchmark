# corr2cause 数据集说明

## 数据说明

**原始数据来源**: [causal-nlp/corr2cause](https://huggingface.co/datasets/causal-nlp/corr2cause)

**本仓库包含**:
- `test.csv` - 完整测试集 (2,324 条)
- `train_sample_5k.csv` - 训练集样本 (5,000 条 / 411,468 条)

**完整数据**: 原始 train.csv 包含 411,468 条记录 (366MB)，可从 HuggingFace 下载。

## 下载完整数据

```bash
pip install huggingface-hub
huggingface-cli download causal-nlp/corr2cause \
  --repo-type dataset \
  --local-dir ./corr2cause
```

或 Python:
```python
from huggingface_hub import hf_hub_download
path = hf_hub_download(
    repo_id="causal-nlp/corr2cause",
    filename="train.csv",
    repo_type="dataset"
)
```

## 数据格式

```csv
input,label,num_variables,template
"Premise: Suppose there is a closed system of 4 variables...",0,4,has_collider
```

- **input**: 前提和假设文本
- **label**: 0/1 (是否因果关系成立)
- **num_variables**: 变量数量
- **template**: 任务模板类型
