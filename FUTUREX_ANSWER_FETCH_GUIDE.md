
# FutureX 答案获取指南

## 当前状态
- **已获取答案**: 2 / 81 (2.5%)
- **已截止问题**: 19 / 81
- **待解决问题**: 62 / 81

## 获取方法

### 1. Manifold Markets API
```python
import httpx

market_id = "market-slug"  # 从 slug 提取
response = await httpx.get(f"https://api.manifold.markets/v0/slug/{market_id}")
data = response.json()

if data.get('isResolved'):
    answer = data.get('resolution')
```

### 2. 批量获取脚本
```bash
python3 scripts/fetch_futurex_answers.py --batch --wait-for-resolve
```

### 3. 等待更多问题 resolve
- 当前日期: 2026-03-20
- 部分问题 end_time 在今天之后
- 建议 1-2 周后重新获取

## 已获取答案的问题

1. **UEFA Champions League Playoff Prop Bets**
   - Resolution: MKT
   - Resolved: 2026-03-19

2. **Champions league round of 16 fixtures**
   - Resolution: MKT
   - Resolved: 2026-03-19

## 建议

1. **短期**: 使用模拟/预测答案进行测试
2. **中期**: 定期检查并获取新 resolve 的答案
3. **长期**: 联系 FutureX 获取 historical resolved 数据集
