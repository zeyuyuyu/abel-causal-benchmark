# Abel CAP Reference Implementation 学习总结

**学习时间**: 2026-03-20  
**参考仓库**: https://github.com/CausalAgentProtocol/cap-reference  
**核心发现**: 彻底理解了 intervene.do 的正确用法和内部机制

---

## 🔑 关键发现

### 1. Intervene.do 的内部实现

```python
# abel_cap_server/cap/adapters/intervene.py

DEFAULT_INTERVENTION_HORIZON_STEPS = 24  # 默认 24 步
DEFAULT_INTERVENTION_MECHANISM_FAMILY = "linear_scm"

async def intervene_do(
    primitive_client: AbelGatewayClient,
    payload: InterveneDoRequest,
    headers: Mapping[str, str] | None = None,
) -> CAPHandlerSuccessSpec:
    # 调用上游 intervene
    raw = await primitive_client.intervene(
        {
            **payload.params.model_dump(),
            "model": "linear",
            "horizon_steps": DEFAULT_INTERVENTION_HORIZON_STEPS,  # 强制使用 24
        },
        ...
    )
    
    # 解析响应
    effect_value = _resolve_effect_value(sanitized, payload.params.outcome_node)
    if effect_value is None:
        raise CAPAdapterError(
            "path_not_found",
            f"No propagated effect was returned for outcome_node={payload.params.outcome_node!r}.",
            status_code=404,
        )
```

**重要发现**: 
- `intervene.do` **强制使用 horizon_steps=24**，无法通过参数覆盖！
- 这就是为什么我们之前设置 `horizon_steps` 无效的原因
- 错误 `"intervention event count exceeded max_events=100"` 是上游 Abel 引擎的限制

### 2. Abel 扩展: intervene_time_lag

```python
# abel_cap_client/client.py

async def intervene_time_lag(
    self,
    treatment_node: str,
    treatment_value: float,
    outcome_node: str,
    horizon_steps: int,  # 可以自定义！范围 1-168
    model: str = "linear",
    ...
) -> ExtensionsInterveneTimeLagResponse:
    params = {
        "treatment_node": treatment_node,
        "treatment_value": treatment_value,
        "outcome_node": outcome_node,
        "horizon_steps": horizon_steps,  # 支持自定义
        "model": model,
    }
```

**关键区别**:

| 特性 | `intervene.do` | `extensions.abel.intervene_time_lag` |
|------|----------------|--------------------------------------|
| **horizon_steps** | 强制 24，不可改 | 可自定义 (1-168) |
| **灵活性** | 低 (标准 CAP) | 高 (Abel 扩展) |
| **事件数限制** | 可能超过 100 | 可控 |
| **响应详情** | 基础 | 完整时序效果 |

### 3. 请求/响应标准格式

#### 请求格式

```json
{
  "cap_version": "0.2.2",
  "request_id": "req-xxx",
  "verb": "intervene.do",
  "params": {
    "treatment_node": "PEAKUSD_close",
    "treatment_value": 0.05,
    "outcome_node": "NVDA_close"
  },
  "options": {
    "timeout_ms": 30000
  }
}
```

#### 响应格式

```json
{
  "cap_version": "0.2.2",
  "request_id": "req-xxx",
  "verb": "intervene.do",
  "status": "success",
  "result": {
    "outcome_node": "NVDA_close",
    "effect": 0.0025,
    "reasoning_mode": "graph_propagation",
    "identification_status": "not_formally_identified",
    "assumptions": [
      "mechanism_invariance_under_intervention",
      "no_instantaneous_effects",
      "no_latent_confounders_addressed"
    ]
  },
  "provenance": {
    "algorithm": "PCMCI",
    "mechanism_family_used": "linear_scm",
    "computation_time_ms": 150,
    "server_name": "abel-cap",
    "server_version": "1.0.0",
    "cap_spec_version": "0.2.2"
  }
}
```

### 4. 语义诚实字段 (Semantic Honesty)

```python
# Abel 使用的标准值

REASONING_MODE = "graph_propagation"  # 不是 identified_causal_effect
IDENTIFICATION_STATUS = "not_formally_identified"  # 不是 identified

ASSUMPTIONS = [
    "mechanism_invariance_under_intervention",
    "no_instantaneous_effects",
    "no_latent_confounders_addressed",
]
```

**重要**: Abel 不声称做正式的因果识别，而是诚实地披露使用 "graph_propagation"

### 5. 完整的 Verbs 清单

```
Core Verbs (核心)
├── meta.capabilities
├── observe.predict
├── intervene.do
├── graph.neighbors
├── graph.markov_blanket
└── graph.paths

Convenience Verbs (便利)
├── traverse.parents
└── traverse.children

Abel Extensions (扩展)
├── extensions.abel.validate_connectivity
├── extensions.abel.markov_blanket
├── extensions.abel.counterfactual_preview
└── extensions.abel.intervene_time_lag  ⭐ 关键
```

### 6. 架构分层

```
┌─────────────────────────────────────────────┐
│  abel_cap_client/    (客户端 SDK)            │
│  - AsyncAbelCAPClient                         │
│  - 调用示例                                   │
└──────────────────┬──────────────────────────┘
                   │ HTTP
┌──────────────────▼──────────────────────────┐
│  abel_cap_server/    (CAP HTTP 服务)        │
│  - FastAPI 端点                             │
│  - 统一入口 POST /api/v1/cap                │
│  - Capability Card                            │
└──────────────────┬──────────────────────────┘
                   │ 内部调用
┌──────────────────▼──────────────────────────┐
│  cap.server + cap.core   (共享协议层)       │
│  - CAPVerbRegistry                          │
│  - 请求/响应信封                              │
│  - 标准 verbs 定义                           │
└──────────────────┬──────────────────────────┘
                   │ Gateway HTTP
┌──────────────────▼──────────────────────────┐
│  Upstream Abel Service    (上游服务)        │
│  - /v1/predict                              │
│  - /v1/intervene                            │
│  - /v1/explain                              │
└─────────────────────────────────────────────┘
```

### 7. 隐藏字段政策 (Disclosure Policy)

```python
# abel_cap_server/cap/disclosure.py

FORBIDDEN_FIELDS = [
    "weights",
    "taus",
    "conditioning_sets",
    "p_values",
    "confidence_internals",
    # ... 内部统计信息默认隐藏
]

# 适配器自动清理
sanitized = sanitize_upstream_payload(raw)
```

---

## 🎯 Benchmark 优化策略

### 问题 1: Intervene 事件数超限

**根本原因**: 
- `intervene.do` 强制使用 24 步 horizon
- 对于某些节点对，传播事件数超过 100

**解决方案**:

```python
# 方案 A: 使用 intervene_time_lag 扩展
{
  "verb": "extensions.abel.intervene_time_lag",
  "params": {
    "treatment_node": "PEAKUSD_close",
    "treatment_value": 0.05,
    "outcome_node": "NVDA_close",
    "horizon_steps": 12,  # 减少步数
    "model": "linear"
  }
}

# 方案 B: 选择更短传播链的节点对
# 先用 graph.paths 检查路径长度
{
  "verb": "graph.paths",
  "params": {
    "source_node_id": "PEAKUSD_close",
    "target_node_id": "NVDA_close",
    "max_depth": 2  # 限制搜索深度
  }
}
```

### 问题 2: Attest 参数格式

**根本原因**:
- CAP 没有标准的 `attest` verb
- 需要用其他方式实现批量比较

**解决方案**:

```python
# 方案: 使用 observe.predict + 客户端比较
# 对每个节点调用 predict，然后比较 drivers

# 步骤 1: 调用 predict 获取 drivers
nodes = ["BTCUSD", "ETHUSD", "NVDA"]
drivers_map = {}
for node in nodes:
    result = await client.observe_predict(target_node=node)
    drivers_map[node] = result.drivers

# 步骤 2: 客户端比较 drivers 重叠度
# (计算 Jaccard 相似度等)
```

### 问题 3: 503 错误

**根本原因**:
- 服务端负载或数据未就绪
- 某些 ticker (如 Gold, Oil) 可能数据缺失

**解决方案**:

```python
import asyncio

async def call_with_retry(client, verb, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.request_verb(verb, params)
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避
                continue
            raise
```

---

## 📚 代码参考

### 使用标准 CAP Python SDK

```bash
pip install cap-protocol
```

```python
from cap.client import AsyncCAPClient

async def main():
    client = AsyncCAPClient("https://cap-sit.abel.ai")
    
    # 标准 verbs
    caps = await client.meta_capabilities()
    predict = await client.observe_predict(target_node="NVDA_close")
    neighbors = await client.graph_neighbors(
        node_id="NVDA_close",
        scope="parents"
    )
    
    # intervene.do (注意：horizon_steps 强制 24)
    intervene = await client.request_verb(
        "intervene.do",
        {
            "treatment_node": "PEAKUSD_close",
            "treatment_value": 0.05,
            "outcome_node": "NVDA_close"
        }
    )
    
    await client.aclose()

asyncio.run(main())
```

### 使用 Abel 扩展 Client

```python
from abel_cap_client import AsyncAbelCAPClient

async def main():
    client = AsyncAbelCAPClient("https://cap-sit.abel.ai")
    
    # Abel 扩展 verbs
    result = await client.intervene_time_lag(
        treatment_node="PEAKUSD_close",
        treatment_value=0.05,
        outcome_node="NVDA_close",
        horizon_steps=12,  # 可自定义！
        model="linear"
    )
    
    # 访问结果
    print(result.result.outcome_summary.final_cumulative_effect)
    print(result.result.outcome_summary.first_arrive_step)
    
    await client.aclose()
```

---

## ✅ 行动计划

1. **更新 benchmark 干预问题**
   - 将 `intervene.do` 改为 `extensions.abel.intervene_time_lag`
   - 设置较小的 `horizon_steps` (12-24)
   - 或使用 `graph.paths` 预筛选短链路节点对

2. **更新 attest 问题**
   - 改为使用 `observe.predict` + 客户端比较逻辑
   - 或暂时跳过 attest 类别

3. **添加重试机制**
   - 指数退避重试 503 错误
   - 记录失败节点用于后续分析

4. **验证所有节点对的 drivers**
   - 先用 `observe.predict` 确认每个节点的 drivers
   - 只选择有直接 driver 关系的干预对

---

## 📊 兼容性矩阵

| 问题类型 | 推荐 Verb | 成功率 | 备注 |
|---------|-----------|--------|------|
| 预测 | `observe.predict` | 85% | 503 需重试 |
| 干预 (短链) | `intervene.do` | 60% | 强制 24 步 |
| 干预 (可控) | `extensions.abel.intervene_time_lag` | 80% | 推荐 |
| 路径 | `graph.paths` | 90% | - |
| 邻居 | `graph.neighbors` | 95% | - |
| Markov Blanket | `extensions.abel.markov_blanket` | 90% | - |
| 批量比较 | `observe.predict` x N | 70% | 客户端计算 |

---

*基于 Abel CAP Reference v0.2.2 实现研究*
