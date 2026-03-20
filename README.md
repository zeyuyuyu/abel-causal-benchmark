# Abel Causal Benchmark (ACB) V2

[![CI](https://github.com/abel-ai/futurex-causal-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/abel-ai/futurex-causal-benchmark/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive benchmark for testing **causal reasoning capabilities** against **forward-looking financial prediction questions**.

> **What's New in V2**: 35 questions (up from 25), 10 intervention scenarios, complete CAP (Causal Agent Protocol) mapping, and enhanced CEVS scoring for the Abel Graph Computer.

## 🎯 Purpose

Abel Causal Benchmark tests whether causal graph systems can provide **"causal emotional value"** - predictions that are:
- **Explainable**: Show causal paths (Fed Rate → Bond Yield → Tech → NVDA)
- **Intervenable**: Answer "What if Fed cuts 50bp?" quantitatively
- **Confident**: Probability calibrated from graph topology
- **Forward-looking**: Predict events before they happen

## 📊 Benchmark Overview

| Category | Count | Description | Example |
|----------|-------|-------------|---------|
| **A** Predict | 8 | Direct causal predictions | "Will BTCUSD go up in 5 hours?" |
| **B** Intervene ⭐ | 10 | Shock propagation scenarios | "What if Fed cuts 50bp?" |
| **C** Path | 7 | Multi-hop causal chains | "DXY → BTC via which path?" |
| **D** Sensitivity | 5 | Confidence analysis | "What flips this prediction?" |
| **E** Attest | 5 | Comparative analysis | "BTC vs ETH: stronger drivers?" |

**Total: 35 questions** covering crypto, equities, macro, and cross-asset relationships.

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/abel-ai/futurex-causal-benchmark.git
cd futurex-causal-benchmark

# Install
pip install -e ".[dev,viz]"

# Verify installation
abel-benchmark --help
```

### 3-Step Quick Run

```bash
# Step 1: Validate questions format
abel-benchmark validate \
  --questions src/futurex_benchmark/references/benchmark_questions_v2_enhanced.json

# Step 2: Run benchmark against your API
abel-benchmark run \
  --base-url "https://abel-graph-computer-sit.abel.ai" \
  --questions src/futurex_benchmark/references/benchmark_questions_v2_enhanced.json \
  --output-dir ./results/$(date +%Y%m%d_%H%M%S)

# Step 3: View results
cat ./results/*/benchmark_report.md
```

### Expected Output

```
✅ Benchmark complete. Reports saved to: ./results/20250320_143022

📊 Summary:
   Total Questions: 35
   Successful: 35/35 (100%)
   Average CEVS: 0.725

By Category:
   A (Predict):      0.780 (8 questions)
   B (Intervene):    0.520 (10 questions) ⭐
   C (Path):         0.750 (7 questions)
   D (Sensitivity):  0.680 (5 questions)
   E (Attest):       0.710 (5 questions)

Reports generated:
   - benchmark_results.csv
   - benchmark_results.json
   - benchmark_report.md
```

### Programmatic Usage

```python
from futurex_benchmark import calculate_cevs, EnhancedCEVSScorer
import json

# Load questions
with open('src/futurex_benchmark/references/benchmark_questions_v2_enhanced.json') as f:
    questions = json.load(f)['questions']

# Score a response
response = {
    'prediction': 0.05,
    'probability_up': 0.68,
    'features': [
        {'cumulative_impact': 0.02, 'tau': 2},
        {'cumulative_impact': 0.015, 'tau': 1}
    ]
}

question = questions[0]  # A1
cevs = calculate_cevs(response, question)

print(f"CEVS: {cevs.total:.3f}")
print(f"  Explainability: {cevs.explainability:.3f}")
print(f"  Intervenability: {cevs.intervenability:.3f}")
print(f"  Confidence: {cevs.confidence_calibration:.3f}")
```

## 📁 Repository Structure

```
futurex-causal-benchmark/
├── src/futurex_benchmark/        # Python package
│   ├── __init__.py
│   ├── cli.py                    # Command-line interface
│   ├── run_benchmark.py          # Benchmark execution
│   ├── enhanced_cevs_scorer.py   # CEVS scoring (V2)
│   ├── futurex_submitter.py      # Submission utilities
│   └── references/               # Question files
│       ├── benchmark_questions_v2_enhanced.json
│       └── benchmark_questions_cap_format.json
├── tests/                        # Test suite
│   └── test_cevs_scorer.py
├── .github/workflows/             # CI/CD
│   └── ci.yml
├── pyproject.toml               # Package config
├── LICENSE                      # MIT License
└── README.md                    # This file
```

## 🔧 CAP (Causal Agent Protocol) Support

V2 includes complete mapping from CAP primitives to causal graph APIs:

| CAP Primitive | Primary Endpoint | Fallback |
|---------------|------------------|----------|
| `intervene` | `/graph_stats/intervention_impact` | Prediction APIs + manual propagation |
| `predict` | `/causal_graph/{ticker}/multi-step-prediction` | Single-step prediction |
| `path` | `/graph_stats/nodes_connection` | Graph topology queries |
| `explain` | `/causal_graph/{ticker}/prediction` | Feature attribution |
| `attest` | `/causal_graph/batch/predictions` | Multiple ticker comparison |

See `references/benchmark_questions_v2_enhanced.json` for full mapping specification.

## 📈 Scoring: CEVS (Causal Emotional Value Score)

### Components

| Component | Weight | Description |
|-----------|--------|-------------|
| **Explainability** | 30% | Can trace causal paths? |
| **Intervenability** | 25% | Can answer what-if? (35% for Category B) |
| **Confidence** | 25% | Well-calibrated probabilities? |
| **Accuracy** | 20% | Directional correctness vs ground truth |

### Category B (Intervention) Special Scoring

Intervention questions use enhanced scoring:
- **Path Transparency** (40%): Full propagation chain visible?
- **Magnitude Quantification** (30%): Per-node effects quantified?
- **Second-Order Detection** (30%): Indirect impacts captured?

```python
# Example high-scoring intervention response
{
    "prediction": 0.03,
    "shock_magnitude": 0.05,  # Acknowledged
    "propagation_path": [      # 3+ hops
        {"node": "NVDA", "hop": 0, "effect": 0.08, "tau": 0},
        {"node": "LRCX", "hop": 1, "effect": 0.04, "tau": 12},
        {"node": "AMAT", "hop": 1, "effect": 0.03, "tau": 8}
    ],
    "second_order_effects": [...]  # Bonus
}
```

## 🗓️ 2025 Forward-Looking Events

V2 includes questions tied to real 2025 events for post-hoc validation:

| Event | Target Date | Questions | Validation |
|-------|-------------|-----------|------------|
| Fed Rate Decision | March 2025 | B4, C3 | 24h post-announcement |
| Q1 Earnings Season | April 2025 | B3, B6 | Per-announcement |
| Geopolitical Oil Shock | Ongoing | B5 | Oil price spike |
| China Tech Policy | TBD | B10 | Policy announcement |

## 📊 Example Results

```json
{
  "timestamp": "2025-03-20T10:00:00",
  "total_questions": 35,
  "average_cevs": 0.725,
  "by_category": {
    "A": {"average": 0.780, "count": 8},
    "B": {"average": 0.520, "count": 10},
    "C": {"average": 0.750, "count": 7},
    "D": {"average": 0.680, "count": 5},
    "E": {"average": 0.710, "count": 5}
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes
4. Run tests (`pytest tests/ -v`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Adding New Questions

1. Edit `src/futurex_benchmark/references/benchmark_questions_v2_enhanced.json`
2. Follow existing format with CAP primitive specification
3. Validate: `abel-benchmark validate --questions your_file.json`
4. Test run against your API
5. Submit PR with context on why this question tests unique causal value

## 📖 Complete Usage Guide

### Step-by-Step Tutorial

#### 1. Prepare Your Environment

```bash
# Clone and setup
git clone https://github.com/abel-ai/futurex-causal-benchmark.git
cd futurex-causal-benchmark

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev,viz]"

# Verify
abel-benchmark --help
```

#### 2. Configure API Connection

Set your Abel Graph Computer API endpoint:

```bash
# Option 1: Command line
abel-benchmark run --base-url "https://abel-graph-computer-sit.abel.ai" ...

# Option 2: Environment variable
export CG_API_URL="https://abel-graph-computer-sit.abel.ai"
abel-benchmark run --base-url $CG_API_URL ...
```

#### 3. Run Full Benchmark

```bash
# Create results directory
mkdir -p results

# Run complete benchmark
abel-benchmark run \
  --base-url "https://abel-graph-computer-sit.abel.ai" \
  --questions src/futurex_benchmark/references/benchmark_questions_v2_enhanced.json \
  --output-dir "./results/$(date +%Y%m%d_%H%M%S)"
```

**What happens:**
1. Loads 35 questions from JSON
2. For each question, calls appropriate CG API endpoint
3. Scores response using Enhanced CEVS scorer
4. Generates CSV, JSON, and Markdown reports

#### 4. Understanding Results

**CSV Output** (`benchmark_results.csv`):
```csv
question_id,category,question,success,cevs_total,explainability,intervenability,confidence,accuracy
A1,A,Will BTCUSD go up...,True,0.780,0.800,0.600,0.900,0.500
B1,B,What is causal propagation...,True,0.450,0.500,0.400,0.400,0.500
```

**JSON Output** (`benchmark_results.json`):
```json
{
  "timestamp": "2025-03-20T14:30:22",
  "total_questions": 35,
  "successful_executions": 35,
  "average_cevs": 0.725,
  "by_category": {
    "A": {"count": 8, "average_cevs": 0.780},
    "B": {"count": 10, "average_cevs": 0.520}
  },
  "results": [...]
}
```

**Markdown Report** (`benchmark_report.md`):
- Executive summary
- Category-by-category breakdown
- Question-level detailed results
- Recommendations for improvement

#### 5. Category-Specific Deep Dive

**Category A (Predict) - Direct Predictions:**

```python
# Example: A1 - BTCUSD 5-hour prediction
from futurex_benchmark import calculate_cevs

response = {
    "prediction": 0.035,          # Cumulative return prediction
    "probability_up": 0.68,           # Probability of up move
    "features": [
        {"feature": "ETHUSD", "cumulative_impact": 0.02, "tau": 2},
        {"feature": "BTC_momentum", "cumulative_impact": 0.015, "tau": 1}
    ],
    "parents": ["ETHUSD", "SPY", "VIX"]
}

question = {
    "id": "A1",
    "category": "A",
    "question": "Will BTCUSD go up in next 5 hours?"
}

cevs = calculate_cevs(response, question)
print(f"CEVS: {cevs.total:.3f}")  # Should be > 0.6 for good result
```

**Category B (Intervene) - Shock Propagation:**

```python
# Example: B3 - NVDA partnership → supply chain impact
response = {
    "prediction": 0.03,
    "shock_magnitude": 0.08,  # Acknowledged shock
    "propagation_path": [
        {"node": "NVDA", "hop": 0, "effect": 0.08, "tau": 0},
        {"node": "LRCX", "hop": 1, "effect": 0.04, "tau": 12},
        {"node": "AMAT", "hop": 1, "effect": 0.03, "tau": 8}
    ],
    "affected_nodes": ["NVDA", "LRCX", "AMAT", "KLAC"],
    "second_order_effects": [
        {"node": "TSM", "via": "NVDA_demand", "effect": 0.02}
    ]
}

question = {
    "id": "B3",
    "category": "B",
    "question": "If NVDA announced partnership, impact on equipment makers?"
}

cevs = calculate_cevs(response, question)
# High score requires: propagation_path + hop-by-hop + second_order
print(f"Intervenability: {cevs.intervenability:.3f}")  # Target: > 0.6
```

**Category C (Path) - Causal Chain Tracing:**

```python
# Example: C1 - DXY → BTC path
response = {
    "paths": [
        {
            "nodes": ["DXY", "GLD", "BTCUSD"],
            "total_tau": 48,
            "strength": 0.65
        },
        {
            "nodes": ["DXY", "EEM", "BTCUSD"],
            "total_tau": 72,
            "strength": 0.45
        }
    ],
    "shortest_path_length": 2,
    "path_exists": True
}

question = {"id": "C1", "category": "C"}
cevs = calculate_cevs(response, question)
```

#### 6. CAP Primitive Mapping

When your API implements CAP primitives:

```python
from futurex_benchmark.run_benchmark import CAPToCGMapper

mapper = CAPToCGMapper()

# Get API endpoint for CAP primitive
mapping = mapper.get_cg_endpoint("intervene", {
    "target_node": "BTCUSD",
    "intervention": {"delta": 0.05}
})

print(mapping)
# {
#   "endpoint": "/graph_stats/intervention_impact",
#   "params": {"ticker": "BTCUSD", "shock_magnitude": 0.05},
#   "fallbacks": [...]
# }
```

#### 7. Ground Truth Validation

For resolved questions, validate against actual outcomes:

```python
# After March 2025 Fed decision
with open('results/benchmark_results.json') as f:
    results = json.load(f)

# B4: Fed 50bp cut prediction
b4_result = next(r for r in results['results'] if r['question']['id'] == 'B4')

# Compare with actual
actual_fed_cut = 0.50  # Actual was 50bp
predicted_impact = b4_result['cg_result']['response']['intervention_effect']

# Calculate directional accuracy
if (predicted_impact > 0) == (tech_stocks_rose > 0):
    print("✅ Directional accuracy: Correct")
```

#### 8. Debugging Failed Questions

```bash
# Run with verbose logging
abel-benchmark run \
  --base-url $CG_API_URL \
  --questions questions.json \
  --output-dir ./debug \
  --verbose 2>&1 | tee debug.log

# Check specific question
python -c "
import json
with open('debug/benchmark_results.json') as f:
    r = json.load(f)
    failed = [x for x in r['results'] if not x['cg_result']['success']]
    for f in failed:
        print(f'{f[\"question\"][\"id\"]}: {f[\"cg_result\"][\"error\"]}')
"
```

#### 9. Custom Questions

Add your own forward-looking questions:

```python
# custom_question.json
{
  "id": "F1",
  "category": "B",
  "cap_primitive": "intervene",
  "question": "If [YOUR EVENT], what happens to [YOUR TICKER]?",
  "cap_request": {
    "capability": "intervene",
    "input": {
      "target_node": "YOUR_TICKER",
      "intervention": {"delta": 0.10}
    }
  },
  "cevs_weight": 1.5
}
```

```bash
# Validate custom question
abel-benchmark validate --questions custom_question.json

# Add to benchmark
jq -s '.[0] + {questions: (.[0].questions + .[1].questions)}' \
  benchmark_questions_v2_enhanced.json custom_question.json \
  > combined.json
```

#### 10. CI/CD Integration

Add to your `.github/workflows/benchmark.yml`:

```yaml
name: Run FutureX Benchmark
on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly
  workflow_dispatch:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install
        run: pip install -e ".[dev]"
      
      - name: Run benchmark
        env:
          CG_API_URL: ${{ secrets.CG_API_URL }}
        run: |
          abel-benchmark run \
            --base-url $CG_API_URL \
            --questions src/futurex_benchmark/references/benchmark_questions_v2_enhanced.json \
            --output-dir ./results
      
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: ./results/
```

---

## 📚 Additional Documentation

- **SKILL.md**: Detailed skill documentation for Claude/Cursor integration
- **DEMO_GUIDE.md**: Step-by-step demo walkthrough
- **CEVS Scoring**: See `src/futurex_benchmark/enhanced_cevs_scorer.py` docstrings

## 🏆 Success Criteria

A successful benchmark demonstrates:

| Metric | Threshold | Meaning |
|--------|-----------|---------|
| Overall CEVS | > 0.60 | Better than random/correlation-only |
| Category A | > 0.70 | Strong direct prediction capability |
| Category B | > 0.45 | **Critical**: Intervention reasoning works |
| Category C | > 0.65 | Multi-hop chains traceable |

## 📖 Citation

## 🔬 CAP Testing

### Quick Test (No API Required)

```bash
# Dry run to see test structure
python test_cap_compatibility.py --dry-run --limit 5
```

### Test Against Real API

```bash
# Test all CAP primitives
python test_cap_compatibility.py \
  --base-url "https://abel-graph-computer-sit.abel.ai" \
  --output-dir ./cap_test_results

# Test specific primitive (e.g., intervene - the hardest)
python test_cap_compatibility.py \
  --base-url "https://abel-graph-computer-sit.abel.ai" \
  --primitive intervene \
  --category B

# Full benchmark with CAP mapping
python test_cap_with_benchmark.py \
  --base-url "https://abel-graph-computer-sit.abel.ai" \
  --output-dir ./full_cap_results
```

### CAP Test Output

```
CAP Compatibility Summary
======================================================================
Tests Run: 35
Success Rate: 82.9%
Behavior Match: 76.5%

✅ CAP compatibility: EXCELLENT

By Primitive:
  predict:   8/8  (100%) success, 4.2 optional fields avg
  intervene: 7/10 (70%)  success, 2.1 optional fields avg ⚠️
  explain:   5/5  (100%) success
  path:      7/7  (100%) success
  attest:    5/5  (100%) success
```

### Understanding CAP Compatibility

| Level | Success Rate | Meaning |
|-------|--------------|---------|
| 🟢 Excellent | > 80% | Production-ready CAP implementation |
| 🟡 Good | 60-80% | Core primitives work, edge cases need work |
| 🔴 Needs Work | < 60% | Significant gaps in CAP specification |

### CAP Test Reports

After running, check:

```bash
# Summary report
cat cap_compatibility_results/cap_compatibility_report.md

# Detailed JSON for programmatic analysis
cat cap_compatibility_results/cap_compatibility_report.json | jq '.by_primitive'
```

**Key sections in report**:
1. **Executive Summary**: Overall compatibility score
2. **By Primitive**: Per-CAP-primitive breakdown
3. **Issues**: Specific missing fields/behaviors
4. **Recommendations**: Priority fixes

---

## Citation

```bibtex
@software{abel_causal_benchmark_2025,
  title = {Abel Causal Benchmark (ACB) V2},
  author = {Abel AI Team},
  year = {2025},
  url = {https://github.com/abel-ai/abel-causal-benchmark},
  version = {2.0.0}
}
```

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [Abel Graph Computer](https://github.com/abel-ai/abel-graph-computer) - Causal graph reasoning API
- [CAP (Causal Agent Protocol)](https://github.com/abel-ai/cap-spec) - Standard for causal agent interfaces
- [ACDB](https://github.com/abel-ai/abel-causal-benchmark) - Abel Causal Discovery Benchmark (real-world cases)

## 💬 Contact

- Issues: [GitHub Issues](https://github.com/abel-ai/abel-causal-benchmark/issues)
- Discussions: [GitHub Discussions](https://github.com/abel-ai/abel-causal-benchmark/discussions)
- Email: team@abel.ai

---

**Built with ❤️ by the Abel AI Team**
