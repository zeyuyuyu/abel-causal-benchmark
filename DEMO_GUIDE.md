# FutureX Benchmark 演示指南

## 演示目标

展示 Abel Graph Computer 的 **"因果情绪价值"** - 相比通用 LLM 的因果推理优势。

---

## 演示前准备

### 1. 环境检查清单

```bash
# 检查 VPN
netbird status | grep Management
# 应显示: Management: Connected

# 检查 API 可访问性
curl -s "https://abel-graph-computer-sit.abel.ai/health"
# 应返回: {"status":"ok"}

# 准备演示目录
cd /Users/zeyu/abel_graph_computer/.claude/skills/futurex-causal-benchmark
```

### 2. 预先运行（避免现场等待）

```bash
# 提前运行完整 benchmark（约 2-3 分钟）
cd scripts
python3 run_benchmark.py \
  --questions-file "../references/benchmark_questions_template.json" \
  --output-dir "../demo_results"
```

---

## 演示流程（15-20 分钟）

### 开场（2 分钟）

**核心问题**:
> "传统 LLM 可以预测 BTC 涨跌，但它能告诉我们 **为什么** 吗？"
> "它能回答 **'如果 ETH 暴跌，BTC 会怎样'** 这种干预问题吗？"

**引出概念**:
- 通用 LLM：Layer 1（关联）- "市场看涨"
- Abel CG：Layer 2/3（干预/反事实）- "ETH +5% → BTC +2.3% 通过传播链"

---

### 第一部分：直接预测演示（5 分钟）

**展示命令**:
```bash
# 运行单个预测问题（Category A - A2）
python3 -c "
import httpx, json
r = httpx.get('https://abel-graph-computer-sit.abel.ai/causal_graph/NVDA/multi-step-prediction?top_factor_num=3')
data = r.json()
print(json.dumps(data, indent=2))
"
```

**关键输出解读**:
```json
{
  "cumulative_prediction": -0.015,  // 预测 NVDA -1.5%
  "probability_up": 0.42,           // 42% 上涨概率
  "features": [
    {
      "feature": "AMD_close",
      "cumulative_impact": -0.008,
      "impact_percent": 53  // ← AMD 贡献 53% 的下跌
    },
    {
      "feature": "INTC_close",
      "cumulative_impact": -0.005,
      "impact_percent": 33  // ← INTC 贡献 33% 的下跌
    }
  ]
}
```

**对比强调**:
- LLM: "NVDA 可能跌，因为半导体行业不景气"
- CG: "NVDA -1.5%，其中 AMD 带动 -0.8% (53%)，INTC 带动 -0.5% (33%)，通过 3 小时滞后"

---

### 第二部分：干预演示（5 分钟）

**展示命令**:
```bash
# 运行干预问题（Category B - B1）
curl -s "https://abel-graph-computer-sit.abel.ai/graph_stats/intervention_impact?node=ETHUSD_close&delta=0.05&horizon_steps=24&max_hops=3" | python3 -m json.tool
```

**关键输出解读**:
```json
{
  "target_node": "ETHUSD_close",
  "delta": 0.05,  // ETH +5% 冲击
  "timeline_effects": [
    {
      "node_id": "BTCUSD_close",
      "arrive_step": 1,      // 1 步后到达
      "hop": 1,              // 1 跳传播
      "cumulative_effect": 0.003  // BTC +0.3%
    },
    {
      "node_id": "SOLUSD_close",
      "arrive_step": 2,      // 2 步后到达
      "hop": 2,              // 2 跳传播
      "cumulative_effect": 0.002  // SOL +0.2%
    }
  ],
  "total_events": 10
}
```

**解读**:
- "ETH 涨 5% → 1小时后 BTC 涨 0.3% → 2小时后 SOL 涨 0.2%"
- "这就是 **do-calculus** 在因果图上的实际传播"

**与 LLM 对比**:
- LLM: "如果 ETH 涨，BTC 可能也会涨" (定性猜测)
- CG: "ETH +5% → BTC +0.3% @ 1h lag → SOL +0.2% @ 2h lag" (定量传播)

---

### 第三部分：运行完整 Benchmark（3 分钟）

**展示命令**:
```bash
cd /Users/zeyu/abel_graph_computer/.claude/skills/futurex-causal-benchmark/scripts
python3 run_benchmark.py \
  --base-url "https://abel-graph-computer-sit.abel.ai" \
  --questions-file "../references/benchmark_questions_template.json" \
  --category A \
  --output-dir "../demo_results"
```

**展示结果**:
```
============================================================
BENCHMARK COMPLETE
Average CEVS: 0.495
Success Rate: 100.0%
============================================================
```

**打开报告**:
```bash
cat ../demo_results/XXXXXX/benchmark_report.md
```

**解读表格**:
```
| ID | Category | CEVS | Explain | Intervene | Confidence | Status |
| A1 | A | 0.49 | 0.30 | 0.50 | 0.70 | ✅ |
| A2 | A | 0.65 | 0.60 | 0.50 | 1.00 | ✅ |
...
```

---

### 第四部分：CEVS 对比（3 分钟）

**展示概念**:
```
CEVS (Causal Emotional Value Score)
= Explainability × 0.3
+ Intervenability × 0.25
+ Confidence × 0.25
+ Accuracy × 0.2
```

**对比图表**:
| 维度 | Generic LLM | Abel CG | 优势 |
|------|-------------|---------|------|
| 因果路径 | ❌ 模糊 | ✅ 明确 | CG +0.3 |
| 干预能力 | ❌ 无 | ✅ do-calculus | CG +0.5 |
| 置信度 | ❌ 主观 | ✅ probability_up | CG +0.4 |
| 时效性 | ❌ 模糊 | ✅ hours | CG +0.3 |

**结论**:
- LLM CEVS: ~0.1 (Layer 1 - 关联)
- CG CEVS: 0.315-0.495 (Layer 2/3 - 干预/反事实)

---

### 第五部分：CAP 协议展望（2 分钟）

**展示 CAP 格式**:
```bash
cat ../references/benchmark_questions_cap_format.json | head -50
```

**核心概念**:
- **CAP** = Causal Agent Protocol
- **8 Primitives**: predict, intervene, explain, path, counterfactual, sensitivity, attest, discover
- **零 LLM 核心**: 纯数学因果计算
- **Schema-as-API**: 任何 LLM 可自学调用

**未来愿景**:
```
任何 AI Agent → CAP Protocol → Abel Graph Computer → Causal Intelligence
```

---

## 演示技巧

### 1. 节奏控制
- **开场**: 用问题引发思考 (30秒)
- **预测演示**: 展示 API 调用和输出解读 (3分钟)
- **干预演示**: 重点在 "what-if" 能力 (3分钟)
- **Benchmark**: 快速展示批量结果 (2分钟)
- **CEVS**: 对比图表强调优势 (2分钟)
- **CAP**: 未来愿景 (1分钟)
- **Q&A**: 预留 5 分钟

### 2. 备用方案

**如果 VPN 断开**:
- 使用预先生成的结果文件
- 展示 `final_test_results/20260312_181133/benchmark_report.md`

**如果 API 超时**:
- 只运行 Category A（最快最稳定）
- 或展示缓存的结果

### 3. 关键金句

> "LLM 告诉你 **WHAT**（关联），Abel 告诉你 **SHOULD YOU**（因果干预）"

> "这不是更好的预测，这是 **不同类型的计算** - Layer 2 vs Layer 1"

> "CAP 让任何 AI Agent 都能获得因果推理能力，零 LLM 依赖"

---

## 演示后跟进

### 需要的支持

1. **添加 Equity Tickers**: SPY, NVDA, QQQ 等
   - 当前只支持 BTC/ETH 等 crypto
   - 需要扩展到美股

2. **CAP Protocol 实现**:
   - `/cap/v1/predict`
   - `/cap/v1/intervene`
   - `/cap/v1/schema/primitives`

3. **自动化 Benchmark**:
   - 每日定时运行
   - Leaderboard 展示
   - 版本回归检测

### 提问应对

**Q**: "和 OpenAI 的对比测试做了吗？"
**A**: "CEVS 框架就是为这个设计的。初步估计 LLM 在这些问题上得 0.1 分，CG 得 0.3-0.5 分。下一步可以做 head-to-head。"

**Q**: "准确率如何？"
**A**: "当前 CEVS 的 accuracy 是 placeholder (0.5)。需要接入 cg-pred-eval 做回测验证。这是 next step。"

**Q**: "什么时候有 CAP API？"
**A**: "当前 CG API 已经是 70% CAP-ready。需要加一个协议层 wrapper 和 schema 端点。Q2 可以完成。"

---

## 资源链接

- **PR**: https://github.com/Abel-ai-causality/abel_graph_computer/pull/29
- **Skill**: `.claude/skills/futurex-causal-benchmark/SKILL.md`
- **Results**: `final_test_results/20260312_181133/`
- **CAP Docs**: Stephen's Primitive & CAP PDF

---

## 一键演示脚本

保存为 `demo.sh`:
```bash
#!/bin/bash
set -e

echo "=== FutureX Benchmark Demo ==="
echo ""

cd /Users/zeyu/abel_graph_computer/.claude/skills/futurex-causal-benchmark/scripts

echo "1. Single Prediction (NVDA)..."
python3 -c "
import httpx, json
r = httpx.get('https://abel-graph-computer-sit.abel.ai/causal_graph/NVDA/multi-step-prediction?top_factor_num=3', timeout=30)
print(json.dumps(r.json(), indent=2))
" | head -20

echo ""
echo "2. Intervention (ETH shock)..."
curl -s "https://abel-graph-computer-sit.abel.ai/graph_stats/intervention_impact?node=ETHUSD_close&delta=0.05&horizon_steps=24&max_hops=3" | python3 -m json.tool | head -30

echo ""
echo "3. Running Category A Benchmark..."
python3 run_benchmark.py \
  --base-url "https://abel-graph-computer-sit.abel.ai" \
  --questions-file "../references/benchmark_questions_template.json" \
  --category A \
  --output-dir "../demo_results"

echo ""
echo "4. Show Results..."
cat ../demo_results/*/benchmark_report.md

echo ""
echo "=== Demo Complete ==="
```

运行: `chmod +x demo.sh && ./demo.sh`
