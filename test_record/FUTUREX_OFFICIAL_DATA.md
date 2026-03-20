# FutureX Benchmark D25 - 官方数据完整分析

**获取时间**: 2026-03-20  
**数据源**: https://huggingface.co/datasets/futurex-ai/Futurex-Online  
**竞赛**: https://futurex-ai.github.io/

---

## 📊 核心统计

| 指标 | 数值 |
|------|------|
| **总 Case 数** | **81** |
| Level 1 | 21 cases |
| Level 2 | 25 cases |
| Level 3 | 13 cases |
| Level 4 | 22 cases |

---

## 🏷️ 类别分布

| 类别 | 数量 | 占比 | 示例 |
|------|------|------|------|
| other | 63 | 78% | 教育、科学、社会等 |
| finance | 6 | 7% | 油价、利率、价格 |
| tech | 5 | 6% | AI、芯片、技术 |
| political | 5 | 6% | 选举、政治事件 |
| sports | 2 | 2% | 体育赛事 |

---

## 💰 金融类问题 (6 个)

### 适合 CAP 测试的问题:

1. **[L2] How High will Crude Oil Volatility get next week?**
   - ID: 69b5552c6ccead0066d5b472
   - End: 2026-03-20
   - 可能节点: CLUSD (原油)

2. **[L2] What will be the closing price of lumber on 20 March 2026?**
   - ID: 6995b1073ea64b005b11f2a2
   - End: 2026-03-20
   - 可能节点: LUMBER (木材)

3. **[L2] Next target for Brazil's SELIC interest rate**
   - ID: 698c7689b06cd2005cde5b30
   - End: 2026-03-19
   - 可能节点: BRL_rate (巴西利率)

4. **[L1] Bank of England (BoE) Bank Rate change?**
   - ID: 6995b1073ea64b005b11f2a0
   - End: 2026-03-19
   - 可能节点: UK_rate (英国央行利率)

5. **[L1] European Central Bank (ECB) Deposit facility rate change?**
   - ID: 6995b1073ea64b005b11f29e
   - End: 2026-03-19
   - 可能节点: EUR_rate (欧央行利率)

6. **[L1] Outcome of Bank of England MPC rate decision on 19th March?**
   - ID: 69a4319df2cb3b006875e9d3
   - End: 2026-03-20
   - 可能节点: UK_rate (英国央行利率)

---

## 🤖 技术类问题 (5 个)

1. **[L2] Gemini 3.1 Pro METR 50% time horizon**
   - AI 模型能力评估

2. **[L2] Will MTEB Chinese leaderboard be dominated by Chinese labs?**
   - AI 排行榜预测

3. **[L2] How many parameters will Gemini 3.1 have?**
   - 模型参数预测

4. **[L2] USACM 2026 cutoff prediction**
   - 数学竞赛分数线

5. **[L2] Will Top 3 LLMs on Arena all be reasoning models?**
   - AI 模型趋势

---

## 🗳️ 政治类问题 (5 个)

1. **[L2] Dutch 2026 local election**
   - 荷兰地方选举

2. **[L2] Sucre Mayoral Election Winner (Bolivia)**
   - 玻利维亚市长选举

3. **[L2] Will a country leave the EU/EMU by 2026?**
   - 欧盟相关

4. **[L2] Will there be a female US President by 2030?**
   - 美国政治

5. **[L2] Taiwan-related question**
   - 台湾问题

---

## ⚽ 体育类问题 (2 个)

1. **[L2] Six Nations Rugby Champion 2026**
   - 六国橄榄球赛

2. **[L2] 2026 AFC Women's Asian Cup Champion**
   - 女足亚洲杯

---

## 📁 数据文件

```
references/
├── futurex_official_81_cases.json     # 完整的 81 个 cases
├── futurex_imported_questions.json   # 之前导入的 7 个金融问题
└── futurex_d25_questions.json        # FutureX D25 元数据和示例
```

---

## 🔍 与当前 Benchmark 对比

### 我们已有的 FutureX 问题 (18 个独特的):
- Gold (GC) 价格预测
- Crude Oil (CL) 价格预测
- Opendoor (OPEN) 预测
- Tesla (TSLA) 阈值预测
- Nvidia (NVDA) 阈值预测
- 跨领域问题 11 个

### 官方 FutureX D25 新增可用问题:
- **原油价格波动** ✅ 可能可用
- **木材期货价格** ⚠️ 节点不确定
- **央行利率** ❌ 可能不在图中

### 结论:
官方 FutureX D25 的 **81 个问题** 中，**只有约 6-10 个**可以直接用于 CAP benchmark 测试（需要金融/市场相关节点在图中）。

---

## 🎯 建议

### 立即可用的 FutureX Case (适合 CAP):
1. Crude Oil Volatility (CLUSD)
2. Gold price (GCUSD) - 已有
3. Tesla price (TSLA) - 已有
4. Nvidia price (NVDA) - 已有

### 需要验证的 Case:
- 央行利率 (可能不在 Abel 图中)
- 木材期货 (LUMBER 节点不确定)

### 不适合 CAP 的 Case (需要 LLM):
- 政治选举
- 体育赛事
- 社会事件
- 大部分 "other" 类别

---

## 📚 参考

- **FutureX Challenge**: https://futurex-ai.github.io/
- **Dataset**: https://huggingface.co/datasets/futurex-ai/Futurex-Online
- **Manifold Markets**: https://manifold.markets/ (问题来源)
- **Abel 优势领域**: FX/货币、商品价格、贸易流、政策影响

---

**总结**: FutureX D25 官方共有 **81 个 cases**，其中约 **6-10 个**可以直接用于 CAP benchmark 测试。
