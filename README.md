# FutureX Causal Prediction Benchmark V2

[![CI](https://github.com/abel-ai/futurex-causal-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/abel-ai/futurex-causal-benchmark/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive benchmark for testing **causal reasoning capabilities** against **forward-looking financial prediction questions**.

> **What's New in V2**: 35 questions (up from 25), 10 intervention scenarios, complete CAP (Causal Agent Protocol) mapping, and enhanced CEVS scoring.

## 🎯 Purpose

FutureX Benchmark tests whether causal graph systems can provide **"causal emotional value"** - predictions that are:
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
```

### Run Benchmark

```bash
# Validate questions
futurex-benchmark validate \
  --questions src/futurex_benchmark/references/benchmark_questions_v2_enhanced.json

# Run against your causal graph API
futurex-benchmark run \
  --base-url "https://your-cg-api.com" \
  --questions src/futurex_benchmark/references/benchmark_questions_v2_enhanced.json \
  --output-dir ./results
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
3. Validate: `futurex-benchmark validate --questions your_file.json`
4. Test run against your API
5. Submit PR with context on why this question tests unique causal value

## 📚 Documentation

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

If you use this benchmark in research:

```bibtex
@software{futurex_benchmark_2025,
  title = {FutureX Causal Prediction Benchmark V2},
  author = {Abel AI Team},
  year = {2025},
  url = {https://github.com/abel-ai/futurex-causal-benchmark},
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

- Issues: [GitHub Issues](https://github.com/abel-ai/futurex-causal-benchmark/issues)
- Discussions: [GitHub Discussions](https://github.com/abel-ai/futurex-causal-benchmark/discussions)
- Email: team@abel.ai

---

**Built with ❤️ by the Abel AI Team**
