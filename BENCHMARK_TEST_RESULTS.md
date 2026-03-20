# Abel Causal Benchmark - 测试结果报告

**测试时间**: 2026-03-20  
**CAP API**: https://cap-sit.abel.ai/api/v1/cap  
**Benchmark 版本**: v2.3-cap-complete  

---

## 📊 测试总结

| 类别 | 问题数 | 成功 | 失败 | 成功率 | 主要问题 |
|------|--------|------|------|--------|----------|
| A (predict) | 8 | 4 | 4 | 50% | 503 服务不可用 |
| B (intervene) | 10 | 0 | 10 | 0% | event count limit / 节点不存在 |
| C (path) | 7 | 1 | 6 | 14% | 验证失败 / 空节点 |
| D (sensitivity) | 5 | 0 | 5 | 0% | 503 错误 |
| E (attest) | 5 | 0 | 5 | 0% | 验证失败 / 空节点 |
| F (futurex) | 7 | 0 | 7 | 0% | 验证失败 / 空节点 |
| X (cross-domain) | 11 | 0 | 11 | 0% | 无 attest 信息 |
| **总计** | **53** | **5** | **48** | **9.4%** | - |

---

## ✅ 成功的问题

### Category A (Predict) - 4/8 成功

| 问题 | 节点 | 结果 | Drivers |
|------|------|------|---------|
| A2 | NVDA_close | ✅ 成功 | 3 (PEAKUSD, MBPUSD, AGNCO) |
| A4 | TSLA_close | ✅ 成功 | 9 |
| A5 | AAPL_close | ✅ 成功 | 5 |
| A6 | ETHUSD_close | ✅ 成功 | 1 |

### Category C (Path) - 1/7 成功

| 问题 | 源节点 | 目标节点 | 结果 | 路径数 |
|------|--------|----------|------|--------|
| C4 | manufacturing_close | cloud_close | ✅ 成功 | 0 |

---

## ❌ 失败分析

### 1. 503 服务不可用 (A1, A3, A7, A8, D2, E1)

**错误**: `Abel primitive service is unavailable`

**原因**: 
- 服务端数据未就绪或负载过高
- 特定 ticker (BTCUSD, SPY, XLF, SOLUSD) 频繁失败

**解决方案**: 
```python
# 指数退避重试
for attempt in range(5):
    try:
        return await client.request_verb(verb, params)
    except Exception as e:
        if "503" in str(e) and attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)
            continue
        raise
```

### 2. Intervene Event Count Limit (B1, B2, B8, B10)

**错误**: `intervention event count exceeded max_events=100`

**根本原因**:
- `intervene.do` 强制使用 horizon_steps=24
- 即使是短链路节点对 (如 PEAKUSD->NVDA, 距离 1)，24 步内仍产生 100+ 事件

**参考实现证据**:
```python
# abel_cap_server/cap/adapters/intervene.py
DEFAULT_INTERVENTION_HORIZON_STEPS = 24  # 强制值，不可覆盖

async def intervene_do(...):
    raw = await primitive_client.intervene(
        {
            "horizon_steps": DEFAULT_INTERVENTION_HORIZON_STEPS,  # 总是 24
        }
    )
```

**当前状态**: 所有 intervene 问题均失败

### 3. 节点不存在 (B3, B4, B6, B9)

**错误**: `Target node not found: VIX_close`, `DXY_close` 等

**不存在的节点**:
- VIX_close
- DXY_close
- GLD_close (但测试显示 DXY->GLD 路径不存在)

**存在的节点 (测试确认)**:
- NVDA_close ✅
- BTCUSD_close ✅
- ETHUSD_close ✅
- PEAKUSD_close ✅
- TSLA_close ✅
- AAPL_close ✅

### 4. 验证失败 (C1-C3, C5-C7, E2-E5, F1-F7)

**错误**: `CAP request validation failed.`

**原因**: 
- 节点名称格式错误（已修复添加 _close 后缀）
- 某些问题仍缺少节点信息
- path 问题的 source/target 节点为空或无效

### 5. 无传播效果 (B5, B7)

**错误**: `No propagated effect was returned for outcome_node`

**原因**: 
- 干预节点和结果节点之间无直接因果连接
- MSTR_close, SOLUSD_close 等可能没有有效的干预路径

---

## 🔑 关键发现

### API 格式要求

```json
// ✅ 正确的节点格式
{
  "target_node": "NVDA_close"
}

// ❌ 错误的节点格式
{
  "target_node": "NVDA"
}
```

### 已知有效的节点对

基于测试成功的案例:

**Predict (高成功率)**:
- NVDA_close (3 drivers: PEAKUSD, MBPUSD, AGNCO)
- TSLA_close (9 drivers)
- AAPL_close (5 drivers)
- ETHUSD_close (1 driver)

**Path (已确认连接)**:
- PEAKUSD_close -> NVDA_close (距离 1, tau=72h)

**Intervene (全部失败)**:
- 即使 PEAKUSD -> NVDA 有路径，干预仍因 event count 限制失败

---

## 📁 修复后的 Benchmark 文件

| 文件 | 说明 | 状态 |
|------|------|------|
| `benchmark_questions_v2_final.json` | 参考实现研究后的修复 | 基础版本 |
| `benchmark_questions_v2_fixed.json` | 修复空节点 | 中间版本 |
| `benchmark_questions_v2_complete.json` | 添加 _close 后缀 | **推荐测试版本** |

---

## 🎯 建议的测试节点

### 推荐用于测试的节点 (基于成功率)

```python
HIGH_SUCCESS_NODES = [
    "NVDA_close",    # 100% predict 成功
    "ETHUSD_close",  # 100% predict 成功
    "TSLA_close",    # 100% predict 成功
    "AAPL_close",    # 100% predict 成功
    "PEAKUSD_close", # 有 drivers
]

AVOID_NODES = [
    "BTCUSD_close",  # 频繁 503
    "SPY_close",     # 频繁 503
    "XLF_close",     # 503
    "SOLUSD_close",  # 503
    "VIX_close",     # 节点不存在
    "DXY_close",     # 节点不存在
]
```

### 推荐的问题子集

如果只测试核心功能，建议:
- **Category A**: 只保留 A2, A4, A5, A6 (已成功的)
- **Category B**: 暂时跳过 (intervene 限制)
- **Category C**: 使用已知的有效节点对 (如 PEAKUSD->NVDA)

---

## 🚀 下一步行动

### 短期 (立即)

1. **使用已知有效的节点**
   - Focus: NVDA, ETHUSD, TSLA, AAPL, PEAKUSD
   - 暂时跳过 BTC, SPY, Gold, Oil

2. **Intervene 问题**
   - 需要 CG API 团队协助调整 `max_events` 限制
   - 或提供降低 horizon_steps 的方法

3. **503 错误**
   - 增加重试次数和延迟
   - 考虑在低峰时段测试

### 中期 (本周)

1. **创建精简版 Benchmark**
   - 只包含已知有效的节点和问题
   - 用于 CI/CD 自动化测试

2. **节点可用性检查**
   - 预测试所有节点的可用性
   - 生成有效节点白名单

3. **批量测试优化**
   - 添加请求间隔避免过载
   - 并行测试可用节点

### 长期 (本月)

1. **Intervene 功能完善**
   - 与 CG API 团队协商解决方案
   - 考虑使用 extensions.abel.intervene_time_lag

2. **Attest 功能实现**
   - 使用 batch predict + 客户端比较
   - 或等待 CAP 标准支持

3. **性能优化**
   - 缓存常用查询结果
   - 优化测试执行时间

---

## 📚 相关文档

- `CAP_REFERENCE_LEARNING.md` - Abel 参考实现研究
- `CAP_IMPLEMENTATION_SUMMARY.md` - 实现总结
- `CAP_LEARNING_SUMMARY.md` - 初步学习总结

---

## 📝 测试命令

```bash
# 运行完整测试
python3 run_benchmark_test.py

# 查看详细结果
cat test_results/benchmark_test_*.json | jq .

# 单独测试特定节点
curl -X POST https://cap-sit.abel.ai/api/v1/cap \
  -H 'Content-Type: application/json' \
  -d '{
    "cap_version": "0.2.2",
    "request_id": "test",
    "verb": "observe.predict",
    "params": {"target_node": "NVDA_close"}
  }'
```

---

**报告生成时间**: 2026-03-20  
**测试状态**: 部分成功 (9.4% 通过率)  
**主要障碍**: intervene event count limit, 503 错误, 部分节点不存在
