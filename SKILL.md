---
name: abel-causal-benchmark-v2
description: Run Abel Causal Benchmark V2 with 35 forward-looking prediction questions. Features 10 intervention scenarios, CAP (Causal Agent Protocol) mapping, and Enhanced CEVS scoring. Tests "causal emotional value" through explainable predictions, what-if analysis, and multi-hop causal chains that surpass generic LLM capabilities.
compatibility: Requires Abel Graph Computer API access. Python 3.10+ with httpx/pandas.
version: 2.0
release_date: 2025-03
---

# Abel Causal Benchmark (ACB) V2 - Enhanced

## What's New in V2

### Major Enhancements from V1

| Feature | V1 | V2 |
|---------|-----|-----|
| **Total Questions** | 25 | **35** |
| **Category B (Intervention)** | 2 questions | **10 questions** |
| **CAP Mapping** | Basic | **Complete with fallbacks** |
| **CEVS Scoring** | Simple | **Category-specific, hierarchical** |
| **Forward-Looking Events** | Generic | **2025-specific scenarios** |
| **API Coverage** | Limited | **Full endpoint mapping** |

### New Intervention Scenarios (Category B)

V2 dramatically expands intervention testing with 10 diverse shock scenarios:

1. **B1-B2**: Crypto shocks (ETH +5%, BTC -3%) - *baseline from V1*
2. **B3**: NVDA partnership → supply chain impact (LRCX, AMAT)
3. **B4**: Fed 50bp rate cut → tech sector transmission
4. **B5**: Oil +10% → Energy → Transport → Airlines → Consumer
5. **B6**: AAPL earnings miss → supplier → sector → market contagion
6. **B7**: DXY +2% → EM equities & commodities impact
7. **B8**: Exchange regulatory relief → crypto sentiment
8. **B9**: Treasury yields -30bp → flight to quality chain
9. **B10**: China tech regulation easing → global spillover

### CAP (Causal Agent Protocol) Integration

V2 includes complete mapping from CAP primitives to CG API:

| CAP Primitive | Primary CG Endpoint | Fallback |
|---------------|---------------------|----------|
| `intervene` | `/graph_stats/intervention_impact` | Prediction APIs with shock parameters |
| `predict` | `/causal_graph/{ticker}/multi-step-prediction` | Single-step prediction |
| `path` | `/graph_stats/nodes_connection` | Graph topology queries |
| `explain` | `/causal_graph/{ticker}/prediction` | Feature attribution analysis |
| `attest` | `/causal_graph/multi-step-prediction/batch` | Multiple ticker comparison |

## Purpose

Run 35 forward-looking prediction questions to demonstrate the unique "causal emotional value" of Abel's causal graph system compared to generic LLMs.

## What "Causal Emotional Value" Means

Unlike generic LLMs that provide surface-level predictions, Abel Graph Computer delivers:

1. **Causal Chain Transparency**: Shows the actual causal path (e.g., "Fed Rate → Bond Yield → Tech Valuation → NVDA Price")
2. **Intervenable Reasoning**: Can answer "What if Fed cuts rates by 50bp?" with quantitative impact
3. **Confidence Through Structure**: Prediction confidence derived from graph topology, not just training data
4. **Temporal Logic**: Understands lead-lag relationships (tau) and propagation timing
5. **Feature Attribution**: Identifies which parent nodes drive the prediction and by how much

## Benchmark Question Categories (V2 - 35 Questions Total)

### Category A: Direct Causal Predictions (8 questions)
Immediate causal relationships with clear graph paths.

| ID | Question | Context |
|----|----------|---------|
| A1 | Will BTCUSD go up in next 5 hours based on ETH momentum? | Crypto correlation |
| A2 | 3-day outlook for NVDA given semi trends? | Q1 2025 AI demand |
| A3 | SPY 24h movement based on VIX and yields? | 4.3% 10Y yield env |
| A4 | TSLA tomorrow given energy sector? | Clean energy correlation |
| A5 | AAPL 12h outlook on consumer sentiment? | Retail exposure |
| A6 | ETHUSD 6h given BTC dominance changes? | Alt-coin dynamics |
| A7 | XLF 48h on yield curve steepening? | Bank profitability |
| A8 | SOL 4h given DeFi ecosystem activity? | Solana DeFi TVL |

### Category B: Intervention What-Ifs ⭐ (10 questions) - *V2 Major Enhancement*
Counterfactual and shock propagation scenarios.

| ID | Scenario | Propagation Chain |
|----|----------|-------------------|
| B1 | ETH +5% shock | ETH → alt-coins (2-hop) |
| B2 | BTC -3% crash | BTC → crypto ecosystem |
| B3 | NVDA partnership | NVDA → LRCX/AMAT (supply chain) |
| B4 | Fed 50bp cut | Fed → yields → tech → market |
| B5 | Oil +10% (geopolitical) | Oil → Energy → Transport → Airlines → Consumer |
| B6 | AAPL earnings miss | AAPL → Suppliers → Tech → Market |
| B7 | DXY +2% | Dollar → EM → Commodities → Crypto |
| B8 | Exchange regulatory relief | Compliance → Crypto sentiment |
| B9 | Treasuries -30bp (flight to safety) | Yields → Tech valuations → Growth |
| B10 | China tech regulation easing | BABA → KWEB → EM → Global Tech |

**B-Category Scoring Priority**:
- Path transparency (40%): Can trace the full propagation chain?
- Magnitude quantification (30%): Are effects quantified per node?
- Second-order detection (30%): Are indirect effects captured?

### Category C: Multi-Hop Causal Chains (7 questions)
Long-range predictions through 3+ causal hops.

| ID | Path Query |
|----|-----------|
| C1 | DXY → BTC (shortest path) |
| C2 | Oil → Retail via transport |
| C3 | Fed Funds → Mortgage REITs |
| C4 | LRCX → AMZN (equipment → cloud capex) |
| C5 | GLD → BTC (multi-channel: safe-haven, inflation, risk) |
| C6 | JPM → Regional banks (systemic risk) |
| C7 | TSLA → Lithium miners (EV → battery → commodity) |

### Category D: Uncertainty & Confidence (5 questions)
Prediction confidence and limits analysis.

| ID | Question |
|----|----------|
| D1 | BTC probability_up and flip thresholds? |
| D2 | BTC vs ETH: which has more reliable parents? |
| D3 | NVDA: at what tau does prediction become unreliable? |
| D4 | SPY: individual stocks vs macro factors? |
| D5 | Which ticker most sensitive to regime changes? |

### Category E: Comparative Causal Analysis (5 questions)
Cross-sectional causal strength comparison.

| ID | Comparison |
|----|-----------|
| E1 | BTC vs ETH: stronger causal drivers? |
| E2 | Tech vs Energy: avg path length? |
| E3 | AI stocks: which most coherent graph? |
| E4 | Crypto vs Gold: inflation hedge effectiveness? |
| E5 | Which sector most stable during volatility? |

## Workflow

### Phase 1: Question Design (V2 Pre-defined)

V2 provides 35 pre-defined questions in:
```
.claude/skills/futurex-causal-benchmark/references/benchmark_questions_v2_enhanced.json
```

**Question Sources**:
1. **Forward-looking 2025 events**: Fed decisions, earnings season, geopolitical tensions
2. **Supply chain relationships**: Semiconductor, energy, EV/lithium
3. **Macro transmission**: Policy → rates → sectors → market
4. **Cross-asset flows**: DXY, commodities, EM, crypto correlations

**CAP Primitive Coverage**:
| Primitive | Questions | Primary API |
|-----------|-----------|-------------|
| `predict` | A1-A8 | `multi-step-prediction` |
| `intervene` | B1-B10 | `intervention_impact` + fallbacks |
| `path` | C1-C7 | `nodes_connection` |
| `sensitivity` | D1-D5 | Prediction with analysis |
| `attest` | E1-E5 | Batch predictions + comparison |

### Phase 2: V2 Execution (Enhanced)

```bash
# Run V2 enhanced benchmark
poetry run python .claude/skills/futurex-causal-benchmark/scripts/run_benchmark.py \
  --base-url "https://abel-graph-computer-sit.abel.ai" \
  --questions-file ".claude/skills/futurex-causal-benchmark/references/benchmark_questions_v2_enhanced.json" \
  --cevs-scorer "enhanced" \
  --output-dir "./futurex_results/$(date +%Y%m%d_%H%M%S)"

# With ground truth validation (for resolved questions)
poetry run python .claude/skills/futurex-causal-benchmark/scripts/run_benchmark.py \
  --base-url "https://abel-graph-computer-sit.abel.ai" \
  --questions-file "benchmark_questions_v2_enhanced.json" \
  --ground-truth-file "resolved_questions.json" \
  --check-accuracy
```

**V2 Execution Features**:
- ✅ CAP-to-CG API mapping with automatic fallbacks
- ✅ Category-specific CEVS scoring
- ✅ Intervention propagation depth tracking
- ✅ Response schema validation
- ✅ Ground truth comparison (for resolved events)

### Phase 3: Enhanced CEVS Evaluation (V2)

**Category B Special Handling**:
```python
# Enhanced scorer provides detailed intervention analysis
from enhanced_cevs_scorer import calculate_cevs

cevs = calculate_cevs(
    response={
        'prediction': 0.05,
        'propagation_path': [
            {'node': 'NVDA', 'hop': 0, 'effect': 0.08},
            {'node': 'LRCX', 'hop': 1, 'effect': 0.04, 'tau': 12},
            {'node': 'AMAT', 'hop': 1, 'effect': 0.03, 'tau': 8}
        ],
        'second_order_effects': [...]
    },
    question={'id': 'B3', 'category': 'B', ...}
)
# Returns: explainability=0.75, intervenability=0.85, ...
```

**Scoring Output**:
```json
{
  "question_id": "B5",
  "category": "B",
  "cevs": {
    "explainability": 0.70,
    "intervenability": 0.80,
    "confidence": 0.65,
    "accuracy": 0.75,
    "total": 0.725
  },
  "intervention_analysis": {
    "shock_acknowledged": true,
    "propagation_depth": 4,
    "quantified_nodes": ["XLE", "IYT", "JETS", "XLY"],
    "second_order_detected": true
  }
}
```

For each question, compare:

| Dimension | Abel Graph Computer | Generic LLM (GPT-4/Claude) |
|-----------|---------------------|---------------------------|
| Prediction with causal path | ✅ Shows parent→child chain | ❌ Surface correlation |
| Quantitative confidence | ✅ probability_up + tau | ❌ Vague language |
| Intervention reasoning | ✅ SCM-based impact calc | ❌ Qualitative guess |
| Temporal specificity | ✅ max_lookahead_hours | ❌ "soon"/"later" |
| Feature attribution | ✅ cumulative_impact per feature | ❌ No breakdown |

### Phase 4: Scoring & Report Generation

**Causal Emotional Value Score (CEVS)** per question:
```
CEVS = (Explainability × 0.3) + (Intervenability × 0.25) + 
       (Confidence_Calibration × 0.25) + (Accuracy × 0.2)
```

Where:
- **Explainability**: Can trace the full causal path? (0-1)
- **Intervenability**: Can answer what-if? (0-1)
- **Confidence_Calibration**: Does confidence match accuracy? (0-1)
- **Accuracy**: Directional correctness (0-1)

## Example Questions with Expected CG API Usage

### Question 1: Direct Multi-Step Prediction
**Q**: "BTCUSD outlook next 5 hours?"

**Abel API**:
```bash
GET /causal_graph/BTCUSD/multi-step-prediction?top_factor_num=3
```

**Expected CG Value**:
```json
{
  "cumulative_prediction": 0.025,
  "probability_up": 0.68,
  "max_lookahead_hours": 5,
  "features": [
    {"feature": "ETHUSD_close", "cumulative_impact": 0.015, "impact_percent": 60},
    {"feature": "SPY_close", "cumulative_impact": 0.008, "impact_percent": 32}
  ]
}
```

**Causal Narrative**: "BTCUSD likely up 2.5% over 5hrs (68% confidence). Primary driver: ETHUSD momentum (60% of impact via crypto correlation). Secondary: SPY risk-on sentiment (32%)."

### Question 2: Intervention What-If
**Q**: "What if ETH suddenly drops 5%? Impact on BTC?"

**Abel API**:
```bash
GET /graph_stats/intervention_impact?target_node=BTCUSD_close&intervention_node=ETHUSD_close&intervention_value=-0.05
```

**Expected CG Value**: Shows quantitative propagation through the causal edge weight.

### Question 3: Graph Topology Confidence
**Q**: "Which has more reliable prediction: BTCUSD or DOGEUSD?"

**Abel API**:
```bash
GET /causal_graph/BTCUSD/features  # Check parent count, tau consistency
GET /causal_graph/DOGEUSD/features
```

**Causal Logic**: More parents with stable tau = more robust prediction.

## Reference Files

- API semantics: `.claude/skills/api-semantics-guide/SKILL.md`
- Evaluation framework: `.claude/skills/cg-pred-eval/SKILL.md`
- Question templates: `.claude/skills/futurex-causal-benchmark/references/benchmark_questions_template.json`

## Success Metrics

A successful FutureX V2 benchmark demonstrates:

1. **Coverage**: 35 questions spanning all 5 categories with emphasis on Category B (Intervention)
2. **Causal Superiority**: 
   - Overall CEVS > 0.6
   - Category B (Intervention) CEVS > 0.5 (improved from V1's ~0.1)
   - Category A (Direct) CEVS > 0.7
3. **Forward Validation**: Questions tied to 2025 events (Fed decisions, earnings, geopolitical)
4. **Intervention Depth**: B-category questions show propagation chains with 3+ hops
5. **CAP Alignment**: API responses map cleanly to CAP primitives with schema validation

## V2 Implementation Script Structure

```python
# .claude/skills/futurex-causal-benchmark/scripts/run_benchmark.py

class FutureXBenchmarkV2:
    def __init__(self, base_url: str, questions_file: str):
        self.cg_client = AbelGraphComputerClient(base_url)
        self.questions = self._load_v2_questions(questions_file)
        self.cevs_scorer = EnhancedCEVSScorer()  # V2 enhanced scorer
        self.cap_mapper = CAPToCGMapper()  # CAP primitive mapping
        
    async def run(self) -> BenchmarkReportV2:
        results = []
        for q in self.questions:
            # V2: CAP-aware execution with fallbacks
            cg_result = await self._execute_cap_primitive(q)
            
            # V2: Category-specific CEVS scoring
            cevs = self.cevs_scorer.calculate_cevs(
                response=cg_result,
                question=q,
                ground_truth=self._get_ground_truth(q.get('id'))
            )
            
            results.append({
                "question": q,
                "cg": cg_result,
                "cevs": cevs,
                "cap_mapping": self.cap_mapper.get_mapping_log()
            })
        
        return BenchmarkReportV2(results)
    
    async def _execute_cap_primitive(self, q: BenchmarkQuestion) -> CGExecutionResult:
        """V2: Execute with CAP-to-CG mapping and fallbacks."""
        cap_primitive = q['cap_request']['capability']
        
        # Get mapping
        mapping = self.cap_mapper.get_cg_endpoint(cap_primitive, q)
        
        # Try primary endpoint
        try:
            result = await self.cg_client.call(mapping['endpoint'], mapping['params'])
            return CGExecutionResult(success=True, mapping_used=mapping['name'])
        except APIError as e:
            # V2: Fallback chain
            for fallback in mapping['fallbacks']:
                try:
                    result = await self.cg_client.call(fallback['endpoint'], fallback['params'])
                    return CGExecutionResult(
                        success=True, 
                        mapping_used=fallback['name'],
                        fallback=True
                    )
                except APIError:
                    continue
            
            return CGExecutionResult(success=False, error="All endpoints failed")
```

## V2 vs V1 Comparison

| Metric | V1 | V2 Target |
|--------|-----|-----------|
| Total Questions | 25 | **35** |
| Category B Count | 2 | **10** |
| Avg CEVS | 0.315 | **> 0.55** |
| Category B Avg CEVS | 0.060 | **> 0.45** |
| API Coverage | Limited | **Full + Fallbacks** |
| Ground Truth Check | Manual | **Automated (resolved events)** |
| CAP Alignment | None | **Complete mapping** |

## V2 Notes

### For Category B (Intervention) Questions

**Key Success Factors**:
1. **Shock Acknowledgment**: Response should acknowledge the intervention magnitude
2. **Propagation Path**: Must show downstream affected nodes (not just direct prediction)
3. **Temporal Structure**: Include tau/lag information for each hop
4. **Second-Order Effects**: Detect indirect impacts (2+ hops away)

**Common V1 Failures → V2 Solutions**:
| V1 Failure | V2 Solution |
|------------|-------------|
| API returned only prediction, no propagation | Use fallback to extract parents + manual propagation |
| No quantified per-node effects | Post-process features to assign hop-by-hop impacts |
| Missing second-order nodes | Increase `max_hops` to 4, track tau accumulation |

### Ground Truth Tracking (V2)

**2025 Forward-Looking Events** (for post-event validation):
- **March 2025 Fed Decision** (B4, C3)
- **Q1 2025 Earnings Season** (B3, B6)
- **Geopolitical Oil Shock** (B5)
- **China Tech Policy Shift** (B10)

Track these events and run `cg-pred-eval` after resolution for accuracy scoring.

### CAP Compatibility

V2 includes complete CAP-to-CG mapping in `benchmark_questions_v2_enhanced.json`:
```json
{
  "cap_to_cg_api_mapping": {
    "intervene": {
      "primary_endpoint": "/graph_stats/intervention_impact",
      "fallback_endpoints": ["prediction APIs"],
      "parameter_mapping": {...},
      "response_transformation": {...}
    }
  }
}
```

This enables clean separation between CAP primitives (what to ask) and CG implementation (how to execute).
