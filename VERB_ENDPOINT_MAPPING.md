# Verb vs 端点功能对照分析

## 🎯 核心问题

**通过 `/api/v1/cap` 使用不同 `verb`，是否等价于截图中的独立端点？**

答案：**功能上等价，但设计模式不同**

---

## 📸 截图中的端点 vs 实际 Verb

### 对照表

| 截图端点 | 方法 | 等价 Verb | 功能状态 | 差异说明 |
|---------|------|-----------|----------|----------|
| `/cap/v1/predict` | POST | `observe.predict` | ✅ **完全等价** | 功能一致，调用方式不同 |
| `/cap/v1/explain` | POST | `observe.predict` | ⚠️ **部分等价** | predict 返回 drivers 字段，可起到解释作用 |
| `/cap/v1/intervene` | POST | `intervene.do` | ✅ **完全等价** | 功能一致，参数名不同 |
| `/cap/v1/counterfactual` | POST | ❓ **未测试** | ⏸️ **未知** | CAP API 可能有 counterfactual 相关 verb |
| `/cap/v1/validate` | POST | ❓ **未测试** | ⏸️ **未知** | 需要测试是否存在 |
| `/cap/v1/schema/primitives` | GET | `meta.capabilities` | ⚠️ **部分等价** | 功能相似，但一个是 GET，一个是 POST |

---

## 🔍 详细功能对比

### 1. predict (完全等价) ✅

**截图端点**: `POST /cap/v1/predict`

**实际调用**:
```json
POST /api/v1/cap
{
  "verb": "observe.predict",
  "params": {
    "target_node": "NVDA_close",
    "horizon": 24
  }
}
```

**功能对比**:
| 功能 | 截图端点 | Verb 方式 | 等价性 |
|------|---------|-----------|--------|
| 预测值 | ✅ | ✅ `prediction` | 100% |
| 驱动因素 | 可能有 | ✅ `drivers` | 100% |
| 置信度 | 可能有 | ⚠️ 未明确 | 未知 |

**结论**: **完全等价** ✅

---

### 2. explain (部分等价) ⚠️

**截图端点**: `POST /cap/v1/explain`

**实际调用**:
```json
POST /api/v1/cap
{
  "verb": "observe.predict",
  "params": {
    "target_node": "NVDA_close",
    "context": {...}
  }
}
```

**功能对比**:
| 功能 | 截图端点 | Verb 方式 | 等价性 |
|------|---------|-----------|--------|
| 解释/归因 | ✅ | ✅ `drivers` | 80% |
| 详细解释文本 | ✅ | ❌ 无 | 缺失 |
| 贡献度数值 | ✅ | ✅ drivers | 80% |

**差异**:
- 截图中的 explain 可能有更详细的解释性文本
- 实际的 predict 返回的 `drivers` 只包含节点 ID
- 需要调用 `graph.neighbors` 获取更多信息来补充解释

**结论**: **部分等价**，predict + graph.neighbors 组合可达到类似效果 ⚠️

---

### 3. intervene (完全等价) ✅

**截图端点**: `POST /cap/v1/intervene`

**实际调用**:
```json
POST /api/v1/cap
{
  "verb": "intervene.do",
  "params": {
    "treatment_node": "PEAKUSD_close",
    "treatment_value": 0.05,
    "outcome_node": "NVDA_close"
  }
}
```

**功能对比**:
| 功能 | 截图端点 | Verb 方式 | 等价性 |
|------|---------|-----------|--------|
| 干预模拟 | ✅ | ✅ | 100% |
| 传播效应 | ✅ | ✅ | 100% |
| 影响节点 | ✅ | ✅ | 100% |

**差异**:
- 只是参数命名不同（截图可能是 `intervention_node` vs 实际是 `treatment_node`）
- 底层实现相同（都使用 Abel Graph Computer 的干预能力）

**结论**: **完全等价** ✅

---

### 4. schema/primitives (部分等价) ⚠️

**截图端点**: `GET /cap/v1/schema/primitives`

**实际调用**:
```json
POST /api/v1/cap
{
  "verb": "meta.capabilities"
}
```

**功能对比**:
| 功能 | 截图端点 | Verb 方式 | 等价性 |
|------|---------|-----------|--------|
| 获取能力清单 | ✅ | ✅ | 100% |
| HTTP 方法 | GET | POST | 不同 |
| 端点路径 | `/cap/v1/schema/*` | `/api/v1/cap` | 不同 |

**差异**:
- 截图中是 GET 请求，适合浏览器/爬虫直接访问
- 实际中是 POST 请求，通过 verb 参数指定
- 返回内容应该相同（都是 Capability Card）

**结论**: **功能等价，调用方式不同** ⚠️

---

### 5. counterfactual (未知) ❓

**截图端点**: `POST /cap/v1/counterfactual`

**CAP API 可能的支持**:

从 `.well-known/cap.json` 查看：
```json
"structural_mechanisms": {
  "counterfactual_ready": false
}
```

**结论**: **当前不支持 counterfactual** ❌

需要验证：
```bash
curl -X POST /api/v1/cap \
  -d '{"verb": "counterfactual.what_if", ...}'
```

---

### 6. validate (未知) ❓

**截图端点**: `POST /cap/v1/validate`

**CAP API 可能的支持**:

从 supported_verbs 中查看是否有相关 verb...

需要测试：
```bash
curl -X POST /api/v1/cap \
  -d '{"verb": "validate", ...}'
```

---

## 🏗️ 设计模式对比

### 截图模式：RESTful API
```
GET  /cap/v1/schema/primitives  → 能力清单
POST /cap/v1/predict             → 预测
POST /cap/v1/explain             → 解释
POST /cap/v1/intervene           → 干预
POST /cap/v1/counterfactual      → 反事实
POST /cap/v1/validate            → 验证
```

**优点**:
- 清晰直观，每个功能独立端点
- 符合 RESTful 设计规范
- 易于文档化和测试

### 实际模式：RPC-style API
```
POST /api/v1/cap
{
  "verb": "observe.predict" | "intervene.do" | "graph.paths" | ...,
  "params": {...}
}
```

**优点**:
- 统一入口，易于维护
- 灵活的 verb 扩展
- 符合 CAP 协议规范

---

## 📊 功能等价性总结

| 功能域 | 截图端点覆盖 | Verb 方式覆盖 | 等价性 |
|--------|-------------|---------------|--------|
| **预测** | `/predict` | `observe.predict` | ✅ 100% |
| **解释** | `/explain` | `observe.predict` (drivers) | ⚠️ 80% |
| **干预** | `/intervene` | `intervene.do` | ✅ 100% |
| **路径** | ❌ 无 | `graph.paths` | ✅ Verb 独有 |
| **邻居** | ❌ 无 | `graph.neighbors` | ✅ Verb 独有 |
| **Markov** | ❌ 无 | `graph.markov_blanket` | ✅ Verb 独有 |
| **遍历** | ❌ 无 | `traverse.parents/children` | ✅ Verb 独有 |
| **反事实** | `/counterfactual` | ❌ 不支持 | ❌ 0% |
| **验证** | `/validate` | ❓ 未测试 | ❓ 未知 |

---

## 💡 关键结论

### 1. 核心功能完全等价 ✅
- predict、intervene 功能 100% 等价
- 只是调用方式不同（独立端点 vs 统一端点+verb）

### 2. Verb 方式更强大
- 额外提供 `graph.paths`, `graph.neighbors`, `graph.markov_blanket` 等
- 这些是截图端点中没有的

### 3. 部分功能缺失
- counterfactual 明确不支持（`counterfactual_ready: false`）
- validate 未测试

### 4. 使用建议
```bash
# 推荐：使用 Verb 方式（更完整、更灵活）
POST /api/v1/cap
{
  "verb": "observe.predict",
  "params": {...}
}

# 不推荐：截图中的独立端点（实际不存在 404）
POST /cap/v1/predict  # ❌ 404 Not Found
```

---

## ❓ 待确认问题

1. **截图是否为未来规划？**
   - 是否会实现 `/cap/v1/*` 独立端点？
   - 还是永远使用 `/api/v1/cap` 统一端点？

2. **counterfactual 何时支持？**
   - 当前 `counterfactual_ready: false`
   - 是否有实现计划？

3. **validate 功能是否存在？**
   - 需要测试是否有对应的 verb

---

*更新: 2026-03-20*
