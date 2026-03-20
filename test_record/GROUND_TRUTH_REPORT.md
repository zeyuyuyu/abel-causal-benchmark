
# Benchmark Ground Truth 完整报告

## 验证方法分布

| 方法 | 数量 | 说明 |
|------|------|------|
| Yahoo Finance API | 47 | 实时股价验证 |
| SCM Simulation | 10 | 因果图仿真 |
| Manifold Markets | 19 | 预测市场验证 |
| Expert Judgment | 4 | 专家验证 |
| FutureX Pending | 16 | 等待 resolve |

## 验证流程

### 1. Yahoo Finance 验证 (47 cases)
```python
# 延迟验证
sleep(delay_hours)
actual_price = yf.download(ticker)
actual_direction = (actual_price > predict_price)
score = (predicted_direction == actual_direction)
```

### 2. SCM 仿真验证 (10 cases)
```python
# 蒙特卡洛仿真
results = scm.simulate(intervention, n_samples=1000)
expected_effect = mean(results)
score = abs(predicted_effect - expected_effect) < threshold
```

### 3. Manifold 验证 (19 cases)
```python
# API 获取答案
answer = manifold.get_resolution(market_id)
score = (predicted_outcome == answer)
```

## 可立即测试的 Cases

- Verifiable: 47 (Yahoo Finance)
- Simulation: 10 (SCM)
- Ready to fetch: 19 (Manifold ended)

**Total immediately testable: 76 / 96 (79%)**
