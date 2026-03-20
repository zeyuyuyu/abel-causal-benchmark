# FutureX Challenge vs Abel Causal Benchmark - Comparison Report

**Generated**: 2026-03-20  
**Analyst**: Abel Causal Benchmark Team

---

## Executive Summary

This report analyzes the relationship between the **FutureX Challenge D25** (a live LLM prediction benchmark) and our **Abel Causal Benchmark (ACB)**.

### Key Findings

| Metric | FutureX Challenge | Abel Causal Benchmark | Overlap |
|--------|------------------|---------------------|---------|
| **Total Questions** | 208 (dataset) | 35 | 7 financial questions identified |
| **Financial Focus** | ~7 questions (3.4%) | 35 questions (100%) | Full coverage |
| **Causal Structure** | Implicit | Explicit (CAP primitives) | ACB adds structure |
| **Question Types** | Multiple choice (A-Z) | Open-ended with causal chains | Different formats |
| **Ground Truth** | Historical outcomes | Historical + 2025 forward-looking | ACB includes future |

---

## FutureX Challenge Overview

### What is FutureX?

FutureX is a **live, dynamic benchmark** designed to evaluate LLM agents' future prediction capabilities. It features:

- **Automated pipeline**: Generates new questions weekly about upcoming real-world events
- **Real-time evaluation**: Scores predictions after events occur
- **Diverse domains**: Politics, sports, entertainment, markets, weather, etc.
- **4 difficulty levels**:
  1. **Level 1**: Basic (Few choices)
  2. **Level 2**: Deep Search (Open-ended, Low Volatility)
  3. **Level 3**: Wide Search (Many choices)
  4. **Level 4**: Super Agent (Open-ended, High Volatility)

### FutureX Question Format

```json
{
  "id": "695bb4008b62560069adce53",
  "title": "Gold (GC) above ___ end of January?",
  "prompt": "Multiple choice question with options A-L...",
  "level": 2,
  "end_time": "2026-02-01",
  "ground_truth": "['H', 'I', 'J', 'K', 'L']"
}
```

**Answer Format**: `\boxed{A}` for single choice, `\boxed{B, C}` for multiple

---

## Abel Causal Benchmark Overview

### What is ACB?

Abel Causal Benchmark is a **causal reasoning benchmark** specifically designed for the Abel Graph Computer:

- **CAP-native**: Built around Causal Agent Protocol primitives
- **Financial focus**: 100% financial markets questions
- **Causal structure**: Every question has explicit causal chains
- **Forward-looking**: Includes 2025-2026 market scenarios
- **35 questions across 5 categories**:
  - **A (Predict)**: 8 questions - Direct causal predictions
  - **B (Intervene)**: 10 questions - What-if shock scenarios
  - **C (Path)**: 7 questions - Multi-hop causal chains
  - **D (Sensitivity)**: 5 questions - Confidence analysis
  - **E (Attest)**: 5 questions - Comparative analysis

### ACB Question Format

```json
{
  "id": "A1",
  "category": "A",
  "cap_primitive": "predict",
  "question": "Will BTCUSD go up in the next 5 hours?",
  "cap_request": {
    "capability": "predict",
    "input": {
      "target_node": "BTCUSD_close",
      "horizon_hours": 5,
      "features_limit": 5
    }
  },
  "expected_response": {
    "cumulative_prediction": "float",
    "probability_up": "float",
    "parent_contributions": [...]
  }
}
```

---

## Detailed Comparison

### Financial Questions Overlap

| Ticker | FutureX | Abel Causal Benchmark | Notes |
|--------|---------|----------------------|-------|
| **GC (Gold)** | ✅ 2 questions | ❌ Not included | FutureX has Gold price predictions |
| **CL (Crude Oil)** | ✅ 2 questions | ✅ Included | ACB has commodity questions |
| **TSLA** | ✅ 1 question | ✅ Included | Both have Tesla questions |
| **NVDA** | ✅ 1 question | ✅ Included | Both have Nvidia questions |
| **OPEN** | ✅ 1 question | ❌ Not included | Opendoor not in ACB |
| **BTC/ETH** | ❌ Not found | ✅ 2 questions | ACB focuses on crypto |
| **SPY** | ❌ Not found | ✅ 1 question | ACB includes ETFs |
| **FX pairs** | ❌ Not found | ✅ DXY, etc. | ACB includes forex |

**New Tickers from FutureX**: `GCUSD` (Gold), `OPEN` (Opendoor)

### Question Structure Comparison

| Aspect | FutureX | Abel Causal Benchmark |
|--------|---------|---------------------|
| **Format** | Multiple choice (A-Z) | Open-ended prediction |
| **Answer Type** | Discrete options | Continuous + probability |
| **Causal Info** | Implicit | Explicit (parents, tau, chains) |
| **Time Horizon** | Varies (days to months) | Hours to days |
| **API Compatibility** | LLM text-based | CG API structured |
| **CAP Primitives** | None | predict, intervene, path, explain, attest |

### Unique FutureX Questions (Non-Financial)

FutureX includes many non-financial questions that ACB doesn't cover:

1. **Elections**: "Who will win Portuguese Presidential elections?"
2. **Sports**: "Who will win Women's Singles at Australian Open?"
3. **Entertainment**: "Who will win Grammy for Record of the Year?"
4. **Weather**: "Precipitation in NYC in January?"
5. **Geopolitics**: "Will Israel strike Gaza on [date]?"
6. **Public Health**: "Measles cases in U.S. by January 31?"

---

## Imported FutureX Questions

We extracted **7 financial questions** from FutureX and converted them to ACB format:

### Converted Questions

| ID | Question | Ticker | Level | Original Answer |
|----|----------|--------|-------|-----------------|
| FX_695bb400 | Gold above ___ end of January? | GCUSD | 2 | Multiple (H-L) |
| FX_695bb400 | Crude Oil settle at in January? | CLUSD | 2 | F |
| FX_695bb400 | Opendoor hit in January 2026? | OPEN | 2 | Multiple (E-I) |
| FX_695bb400 | Crude Oil hit__ by end of January? | CLUSD | 2 | Multiple (B, C, G, J) |
| FX_695bb400 | Gold settle at in January? | GCUSD | 2 | E |
| FX_6957ba8a | Tesla hits $400 or $500 first? | TSLA | 1 | A ($400 first) |
| FX_6957ba8a | Nvidia hits 170, 200 or neither? | NVDA | 1 | A ($170 first) |

**Location**: `src/abel_benchmark/references/futurex_imported_questions.json`

---

## Recommendations

### 1. Add FutureX Questions to ACB

**Option A**: Create new Category F (FutureX-inspired)
- Add the 7 converted questions
- Expand to include more threshold-based questions
- Benefits: Real historical outcomes, proven difficulty levels

**Option B**: Merge into existing categories
- Gold/Oil → Category A (Predict)
- Tesla/Nvidia → Already covered, add variants

### 2. Enhance ACB with FutureX Features

| FutureX Feature | ACB Enhancement |
|-----------------|-----------------|
| Difficulty levels (1-4) | Add difficulty tags to questions |
| Multiple choice format | Create binary prediction variants |
| Diverse domains | Consider adding non-financial categories |
| Weekly live updates | Establish ACB live update schedule |

### 3. Maintain Differentiation

**Keep ACB's unique strengths**:
- CAP primitive alignment
- Causal chain transparency
- Abel Graph Computer integration
- Forward-looking scenarios

**Don't fully replicate FutureX**:
- Non-financial domains (elections, sports)
- Pure multiple-choice format
- LLM-text-based evaluation

---

## Conclusion

### Relationship Summary

**Abel Causal Benchmark is NOT a copy of FutureX**, but rather:

1. **Complementary**: ACB focuses on causal reasoning; FutureX tests general prediction
2. **Specialized**: ACB is 100% financial; FutureX is 3.4% financial
3. **Structured**: ACB has explicit CAP primitives; FutureX is implicit
4. **Enhanced**: ACB adds causal chains to financial questions FutureX already asks

### The 7 FutureX financial questions have been:

✅ **Extracted** from FutureX-Past dataset  
✅ **Converted** to ACB format with CAP primitives  
✅ **Exported** to `futurex_imported_questions.json`  
✅ **Ready** to be added to main benchmark

### Next Steps

1. **Review** the converted questions for quality
2. **Test** with CG API to ensure compatibility
3. **Decide** whether to add as Category F or merge into existing
4. **Expand** with more threshold-based prediction questions

---

## Appendix: Sample Converted Question

**Original FutureX**:
```
Title: "Gold (GC) above ___ end of January?"
Options: A-L (price levels from $3,600 to $7,000)
Answer: H, I, J, K, L (above $4,200)
```

**Converted to ACB**:
```json
{
  "id": "FX_695bb400",
  "category": "A",
  "cap_primitive": "predict",
  "question": "Gold (GC) above ___ end of January?",
  "context": "FutureX Challenge D25 - Level 2...",
  "cap_request": {
    "capability": "predict",
    "input": {
      "target_node": "GCUSD_close",
      "horizon_hours": 720,
      "features_limit": 5
    }
  },
  "expected_response": {
    "cumulative_prediction": "float",
    "probability_up": "float",
    "parent_contributions": [...]
  },
  "ground_truth_check": {
    "source": "futurex_challenge",
    "original_answer": "['H', 'I', 'J', 'K', 'L']"
  }
}
```

---

**Report Complete**  
*For questions, contact: team@abel.ai*
