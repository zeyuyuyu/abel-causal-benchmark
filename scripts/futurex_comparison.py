#!/usr/bin/env python3
"""
FutureX vs Abel Causal Benchmark Comparison

分析 FutureX Challenge 的问题并与我们的 benchmark 对比，
提取可以添加的金融相关案例。
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class FutureXQuestion:
    """FutureX question structure"""
    id: str
    title: str
    prompt: str
    level: int  # 1-4 difficulty
    end_time: str
    ground_truth: str
    
    def is_financial(self) -> bool:
        """Check if question is financial/market related"""
        financial_keywords = [
            'price', 'stock', 'gold', 'oil', 'crude', 'btc', 'bitcoin',
            'nvidia', 'tesla', 'opendoor', 'market', 'trading', 'settle',
            'index', 'yield', 'rate', 'fed', 'dollar', 'forex', 'fx',
            'usd', 'jpy', 'eur', 'gbp', 'cny', 'commodity', 'futures',
            'option', 'bond', 'treasury', 'spy', 'qqq', 'dxy'
        ]
        text = (self.title + " " + self.prompt).lower()
        return any(kw in text for kw in financial_keywords)
    
    def is_causal_suitable(self) -> bool:
        """Check if question could benefit from causal reasoning"""
        # Questions with propagation chains, interventions, or multi-hop reasoning
        causal_indicators = [
            'if', 'when', 'cause', 'impact', 'effect', 'lead to',
            'result', 'because', 'due to', 'affect', 'influence',
            'transmission', 'chain', 'propagation', 'spillover'
        ]
        text = (self.title + " " + self.prompt).lower()
        return any(ind in text for ind in causal_indicators)


def parse_futurex_from_html(html_file: Path) -> List[FutureXQuestion]:
    """Parse FutureX questions from Hugging Face HTML viewer export"""
    # For now, manually define the financial questions we saw
    # In production, this would parse the actual dataset
    
    financial_questions = [
        FutureXQuestion(
            id="695bb4008b62560069adce53",
            title="Gold (GC) above ___ end of January?",
            prompt="Gold (GC) settle over $X on final trading day of January 2026",
            level=2,
            end_time="2026-02-01",
            ground_truth="['H', 'I', 'J', 'K', 'L']"
        ),
        FutureXQuestion(
            id="695bb4008b62560069adce59",
            title="What will Crude Oil (CL) settle at in January?",
            prompt="Crude Oil price range prediction for January 2026",
            level=2,
            end_time="2026-02-01",
            ground_truth="['F']"
        ),
        FutureXQuestion(
            id="695bb4008b62560069adce04",
            title="What will Opendoor (OPEN) hit in January 2026?",
            prompt="Opendoor stock price level prediction",
            level=2,
            end_time="2026-02-01",
            ground_truth="['E', 'F', 'G', 'H', 'I']"
        ),
        FutureXQuestion(
            id="695bb4008b62560069adce56",
            title="What will Crude Oil (CL) hit__ by end of January?",
            prompt="Crude Oil high/low price prediction",
            level=2,
            end_time="2026-02-01",
            ground_truth="['B', 'C', 'G', 'J']"
        ),
        FutureXQuestion(
            id="695bb4008b62560069adce54",
            title="What will Gold (GC) settle at in January?",
            prompt="Gold price range settlement prediction",
            level=2,
            end_time="2026-02-01",
            ground_truth="['E']"
        ),
        FutureXQuestion(
            id="6957ba8a03568a006853e82e",
            title="Tesla hits $400 or $500 first before end of January 2026?",
            prompt="Tesla stock price threshold prediction",
            level=1,
            end_time="2026-02-01",
            ground_truth="['A']"
        ),
        FutureXQuestion(
            id="6957ba8a03568a006853e82f",
            title="Nvidia hits 170, 200 or neither first by end of January 2026?",
            prompt="Nvidia stock price level prediction",
            level=1,
            end_time="2026-02-01",
            ground_truth="['A']"
        ),
    ]
    
    return financial_questions


def convert_futurex_to_abel_format(fq: FutureXQuestion) -> Dict[str, Any]:
    """Convert FutureX question to Abel Causal Benchmark format"""
    
    # Determine ticker from title
    ticker_map = {
        'gold': 'GCUSD',
        'crude oil': 'CLUSD',
        'oil': 'CLUSD',
        'opendoor': 'OPEN',
        'tesla': 'TSLA',
        'nvidia': 'NVDA',
        'btc': 'BTCUSD',
        'bitcoin': 'BTCUSD',
    }
    
    ticker = None
    title_lower = fq.title.lower()
    for key, value in ticker_map.items():
        if key in title_lower:
            ticker = value
            break
    
    if not ticker:
        ticker = "UNKNOWN"
    
    # Create Abel format question
    abel_question = {
        "id": f"FX_{fq.id[:8]}",  # Prefix with FX to indicate FutureX origin
        "category": "A",  # Default to Predict category
        "cap_primitive": "predict",
        "question": fq.title,
        "context": f"FutureX Challenge D25 - Level {fq.level}. {fq.prompt[:100]}...",
        "cap_request": {
            "capability": "predict",
            "input": {
                "target_node": f"{ticker}_close",
                "horizon_hours": 24 * 30,  # Default to ~1 month
                "features_limit": 5,
                "include_parents": True
            }
        },
        "expected_response": {
            "cumulative_prediction": "float",
            "probability_up": "float",
            "parent_contributions": [
                {"node": "string", "impact": "float", "tau": "int"}
            ]
        },
        "ground_truth_check": {
            "source": "futurex_challenge",
            "futurex_id": fq.id,
            "original_answer": fq.ground_truth,
            "metric": "directional_accuracy"
        },
        "cevs_weight": 1.0,
        "metadata": {
            "futurex_level": fq.level,
            "end_time": fq.end_time,
            "original_source": "FutureX Challenge D25"
        }
    }
    
    return abel_question


def analyze_overlap():
    """Analyze overlap between FutureX and Abel Causal Benchmark"""
    
    # Load Abel questions
    abel_path = Path(__file__).parent.parent / "src" / "abel_benchmark" / "references" / "benchmark_questions_v2_enhanced.json"
    with open(abel_path) as f:
        abel_data = json.load(f)
    
    abel_questions = abel_data['questions']
    abel_tickers = set()
    for q in abel_questions:
        cap_input = q.get('cap_request', {}).get('input', {})
        ticker = cap_input.get('target_node', '')
        if ticker:
            abel_tickers.add(ticker.replace('_close', ''))
    
    # Parse FutureX financial questions
    futurex_questions = parse_futurex_from_html(Path("/tmp/futurex.html"))
    
    print("=" * 70)
    print("FutureX vs Abel Causal Benchmark - Comparison Report")
    print("=" * 70)
    print()
    
    print("## Current Abel Causal Benchmark")
    print(f"- Total questions: {len(abel_questions)}")
    print(f"- Unique tickers: {sorted(abel_tickers)}")
    print()
    
    print("## FutureX Financial Questions (Extracted)")
    print(f"- Total financial questions found: {len(futurex_questions)}")
    print()
    
    print("### FutureX Questions Suitable for Causal Analysis:")
    for fq in futurex_questions:
        is_causal = fq.is_causal_suitable()
        print(f"  - {fq.title}")
        print(f"    Level: {fq.level}, Causal suitable: {is_causal}")
        print(f"    Answer: {fq.ground_truth}")
        print()
    
    # Identify new tickers from FutureX
    futurex_tickers = set()
    for fq in futurex_questions:
        title_lower = fq.title.lower()
        if 'gold' in title_lower:
            futurex_tickers.add('GCUSD')
        elif 'oil' in title_lower or 'crude' in title_lower:
            futurex_tickers.add('CLUSD')
        elif 'opendoor' in title_lower:
            futurex_tickers.add('OPEN')
        elif 'tesla' in title_lower:
            futurex_tickers.add('TSLA')
        elif 'nvidia' in title_lower:
            futurex_tickers.add('NVDA')
    
    new_tickers = futurex_tickers - abel_tickers
    
    print("## New Tickers from FutureX (not in current Abel benchmark):")
    if new_tickers:
        for ticker in sorted(new_tickers):
            print(f"  - {ticker}")
    else:
        print("  All FutureX tickers already covered")
    print()
    
    print("## Recommendations:")
    print("1. Add FutureX financial questions as new category 'F' (FutureX-inspired)")
    print("2. Focus on Level 1-2 questions for better CG API compatibility")
    print("3. Convert binary/multiple-choice format to CAP-compatible format")
    print("4. Add questions with explicit causal chains (Fed → Yields → Tech)")
    print()
    
    return futurex_questions


def generate_futurex_import():
    """Generate importable questions from FutureX"""
    futurex_questions = parse_futurex_from_html(Path("/tmp/futurex.html"))
    
    converted = []
    for fq in futurex_questions:
        abel_q = convert_futurex_to_abel_format(fq)
        converted.append(abel_q)
    
    output = {
        "source": "FutureX Challenge D25",
        "conversion_date": "2026-03-20",
        "description": "FutureX financial questions converted to Abel Causal Benchmark format",
        "questions": converted
    }
    
    output_path = Path(__file__).parent.parent / "src" / "abel_benchmark" / "references" / "futurex_imported_questions.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Exported {len(converted)} FutureX questions to:")
    print(f"   {output_path}")
    
    return converted


if __name__ == "__main__":
    print("Analyzing FutureX Challenge data...")
    questions = analyze_overlap()
    
    print("\n" + "=" * 70)
    print("Converting FutureX questions to Abel format...")
    print("=" * 70)
    converted = generate_futurex_import()
    
    print(f"\n✅ Analysis complete!")
    print(f"   - {len(questions)} FutureX financial questions identified")
    print(f"   - {len(converted)} questions converted to Abel format")
