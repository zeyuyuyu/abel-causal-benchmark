# CAP API 测试策略澄清

## 当前测试方式

### 我们的假设
我们目前基于 **CAP 原语 → CG API Endpoint 映射** 进行测试：

```
CAP Primitive    →   CG API Endpoint                           →   Status
─────────────────────────────────────────────────────────────────────────────
predict          →   /causal_graph/{ticker}/multi-step-prediction    ✅ 可用
intervene        →   /graph_stats/intervention_impact               ⚠️ 422
path             →   /graph_stats/nodes_connection                  ⚠️ 422
explain          →   /causal_graph/{ticker}/prediction              ✅ 可用
attest           →   /causal_graph/multi-step-prediction/batch      ✅ 可用
discover         →   /causal_graph/mb/{target}                      ✅ 可用
```

### 测试逻辑
1. **加载 Benchmark 问题** (53 题)
2. **识别 CAP 原语** (predict, intervene, path, etc.)
3. **映射到 CG API Endpoint**
4. **调用 CG API** 并验证响应
5. **检查响应字段** 是否符合 CAP 规范

---

## 问题：是否有专门的 CAP API？

### 可能的情况

**情况 A**: 通过现有 CG API 支持 CAP (当前假设)
- CG API 是底层实现
- CAP 是高层协议规范
- 通过映射关系兼容 CAP

**情况 B**: 有专门的 CAP 服务层
- 独立的 CAP API Gateway
- 例如: `/cap/v1/predict`, `/cap/v1/intervene`
- 专门将 CAP 语义转换为 CG 内部调用

**情况 C**: CAP 只是规范，实现通过 CG API
- CAP 定义接口规范
- 每个实现者 (如 CG) 用自己的方式支持
- 通过映射测试兼容性

---

## 需要确认的问题

### 给用户的问题：

1. **是否有专门的 CAP API Endpoint？**
   ```
   例如:
   - /cap/v1/predict
   - /cap/v1/intervene  
   - /cap/v1/path
   - /cap/v1/attest
   ```

2. **CAP 原语到 CG API 的映射**
   - 当前是 Benchmark 团队自己定义的映射
   - 还是 CG API 团队已经定义好了？
   - 是否有官方映射文档？

3. **测试目标**
   - 测试 A: 验证 CG API 是否符合 CAP 规范 (当前方式)
   - 测试 B: 验证专门的 CAP 服务层 (如果有)
   - 测试 C: 两者都需要验证

---

## 当前测试的局限性

### 如果通过 CG API 测试 CAP：

**优点**:
- 直接测试底层实现
- 验证 CG 是否支持 CAP 语义

**缺点**:
- 需要维护映射关系
- CG API 可能有额外限制 (如 422 错误)
- 不是直接的 CAP 接口

### 如果有专门的 CAP API：

**应该测试**:
```bash
# 专门的 CAP API
GET /cap/v1/predict?ticker=NVDA&horizon=5h
GET /cap/v1/intervene?target=BTCUSD&shock=-5%
GET /cap/v1/path?from=DXY&to=BTCUSD
GET /cap/v1/attest?tickers=BTCUSD,ETHUSD
```

**优点**:
- 直接测试 CAP 语义
- 标准化接口
- 与实现解耦

---

## 建议的测试策略

### 如果存在专门的 CAP API：

```python
# 直接调用 CAP 端点
class CAPAPITester:
    async def test_predict(self, question):
        response = await client.get(
            "/cap/v1/predict",
            params={
                "ticker": question["target"],
                "horizon": question["horizon"],
                "features_limit": question["features"]
            }
        )
        return response
```

### 如果不存在 (当前方式)：

```python
# 通过 CG API 映射测试
class CAPCompatibilityTester:
    # 维护 CAP → CG 映射
    cap_mapping = {
        "predict": "/causal_graph/{ticker}/multi-step-prediction",
        "intervene": "/graph_stats/intervention_impact",
        # ...
    }
```

---

## 下一步

请确认：

1. **是否存在 `/cap/*` 端点？**
2. **官方 CAP 到 CG API 的映射文档？**
3. **我们应该测试哪一层？**
   - A: 直接测试 CG API (当前方式)
   - B: 测试专门的 CAP API (如果有)
   - C: 两者都测试

根据您的回答，我们可以调整测试策略！

---

## ✅ 已确认：存在专门的 CAP API 端点！

从截图中可以看到：

### CAP Primitives (POST)
- `/cap/v1/predict` ✅
- `/cap/v1/explain` ✅
- `/cap/v1/intervene` ✅
- `/cap/v1/counterfactual` ✅
- `/cap/v1/validate` ✅

### Schema Discovery (GET)
- `/cap/v1/schema/primitives` ✅
- `/cap/v1/schema/variables` ✅
- `/cap/v1/schema/neighborhood` ✅
- `/cap/v1/schema/paths` ✅

---

## 🚨 发现：CAP API 需要认证

测试返回 **401 Unauthorized**，说明 CAP API 需要认证。

---

## 下一步

### 需要确认：
1. **CAP API 认证方式？**
   - Header: `Authorization: Bearer <token>`?
   - Header: `X-API-Key: <key>`?
   - 其他方式?

2. **如何获取认证信息？**
   - 环境变量?
   - 配置文件?
   - 动态获取?

3. **CG API vs CAP API 的关系**
   - CG API 是公开端点 (无需认证)
   - CAP API 是受保护端点 (需要认证)
   - 两者都应该测试?
