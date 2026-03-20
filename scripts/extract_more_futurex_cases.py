#!/usr/bin/env python3
"""
Extract and convert more FutureX cases from various domains

From the FutureX-Past dataset, extract non-financial questions and convert
to Abel Causal Benchmark format as 'cross-domain' causal reasoning tests.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class FutureXCase:
    """FutureX case from various domains"""
    id: str
    domain: str  # election, sports, entertainment, geopolitics, health
    title: str
    prompt: str
    level: int
    end_time: str
    ground_truth: str
    options: List[str]


def extract_diverse_cases() -> List[FutureXCase]:
    """Extract diverse cases from FutureX data"""
    
    # Manually extracted from the Hugging Face viewer data
    # These are real FutureX questions with various domains
    
    cases = [
        # ELECTIONS / POLITICS
        FutureXCase(
            id="694a8b8fbd65d70068ad7db4",
            domain="election",
            title="Portuguese Presidential elections second round",
            prompt="Which candidates will make it to the second round of the Portuguese Presidential elections on 18 Jan 2026?",
            level=2,
            end_time="2026-01-18",
            ground_truth="['B']",
            options=["António José Seguro vs. André Ventura", "Marques Mendes vs. André Ventura", 
                    "Gouveia e Melo vs. António José Seguro", "No second round"]
        ),
        FutureXCase(
            id="69493cb11e67de005c795b7e",
            domain="election",
            title="Portugal Presidential Election second round qualifiers",
            prompt="Who will qualify for the second round of the Portugal Presidential Election?",
            level=2,
            end_time="2026-01-18",
            ground_truth="['C', 'P']",
            options=["André Ventura", "Luís Marques Mendes", "Henrique Gouveia e Melo", 
                    "António José Seguro", "João Cotrim de Figueiredo", "Catarina Martins"]
        ),
        
        # SPORTS
        FutureXCase(
            id="6956690920a2e600672a7867",
            domain="sports",
            title="2026 Australian Open Women's Singles Winner",
            prompt="Which tennis player will win the Women's Singles Final at the 2026 Australian Open?",
            level=2,
            end_time="2026-02-01",
            ground_truth="['F']",
            options=["Mirra Andreeva", "Coco Gauff", "Madison Keys", "Naomi Osaka", 
                    "Elena Rybakina", "Aryna Sabalenka", "Iga Swiatek"]
        ),
        FutureXCase(
            id="6957ba8a03568a006853e820",
            domain="sports",
            title="2025 CAF Cup of Nations (AFCON) Winner",
            prompt="Who will win the 2025 CAF Cup of Nations?",
            level=2,
            end_time="2026-01-18",
            ground_truth="['A']",
            options=["Senegal", "Morocco", "Nigeria", "Egypt"]
        ),
        
        # ENTERTAINMENT / AWARDS
        FutureXCase(
            id="695a5d897b2e6a00694886b9",
            domain="entertainment",
            title="2026 Grammy Best Pop Vocal Album",
            prompt="Who will win the 2026 Grammy for Best Pop Vocal Album?",
            level=1,
            end_time="2026-02-02",
            ground_truth="['D']",
            options=["Justin Bieber - SWAG", "Sabrina Carpenter - Man's Best Friend", 
                    "Miley Cyrus - Something Beautiful", "Lady Gaga - MAYHEM", "Teddy Swims"]
        ),
        FutureXCase(
            id="695a5d897b2e6a00694886af",
            domain="entertainment",
            title="2026 Grammy Record of the Year",
            prompt="Who will win the 2026 Grammy for Record of the Year?",
            level=2,
            end_time="2026-02-02",
            ground_truth="['F']",
            options=["Bad Bunny - DtMF", "Sabrina Carpenter - Manchild", 
                    "Doechii - Anxiety", "Billie Eilish - Wildflower",
                    "Lady Gaga - Abracadabra", "Kendrick Lamar with SZA - Luther"]
        ),
        FutureXCase(
            id="69566c1320a2e600672a78fb",
            domain="entertainment",
            title="Grammys Songwriter of the Year Winner",
            prompt="Who will win Songwriter of the Year at the 68th annual GRAMMY Awards?",
            level=2,
            end_time="2026-02-01",
            ground_truth="['A']",
            options=["Amy Allen", "Laura Veltz", "Edgar Barrera", "Jessie Jo Dillon", 
                    "Tobias Jesso Jr.", "Another person"]
        ),
        
        # GEOPOLITICS
        FutureXCase(
            id="6964eca552029b005bc009f2",
            domain="geopolitics",
            title="Israel strikes Gaza January 2026",
            prompt="Will Israel strike Gaza on specific dates in January 2026?",
            level=2,
            end_time="2026-01-31",
            ground_truth="['C', 'E', 'G', 'H', 'J', 'K', 'L', 'M', 'O', 'U', 'X']",
            options=[f"January {i}" for i in range(1, 32)]
        ),
        
        # PUBLIC HEALTH
        FutureXCase(
            id="6957ba8a03568a006853e82e",
            domain="health",
            title="Measles cases in U.S. by January 31",
            prompt="How many measles cases will there be in the U.S. by January 31, 2026?",
            level=2,
            end_time="2026-01-31",
            ground_truth="['A', 'B', 'C', 'E', 'F', 'G', 'H', 'I']",
            options=["<20", "20-150", "150-300", "300-500", "500-750", ">750"]
        ),
        
        # WEATHER
        FutureXCase(
            id="69639b3e5a6f9800684ed69a",
            domain="weather",
            title="NYC Precipitation January 2026",
            prompt="How much precipitation will NYC have in January 2026?",
            level=2,
            end_time="2026-01-31",
            ground_truth="['C']",
            options=["<3 inches", "3-4 inches", "4-5 inches", "5-6 inches", ">7 inches"]
        ),
        
        # ECONOMICS / POLICY
        FutureXCase(
            id="695a609d7b2e6a00694886f6",
            domain="economics",
            title="Reserve Bank of Australia February Decision",
            prompt="What will the Reserve Bank of Australia decide in February 2026?",
            level=1,
            end_time="2026-02-03",
            ground_truth="['B']",
            options=["Decrease cash rate", "Increase cash rate", "No change"]
        ),
    ]
    
    return cases


def convert_to_causal_format(case: FutureXCase) -> Dict[str, Any]:
    """Convert FutureX case to causal reasoning format"""
    
    # Create a causal reasoning version of the question
    # This tests if CG can provide causal factors even for non-financial domains
    
    domain_contexts = {
        "election": "Social, economic, and political factors influencing electoral outcomes",
        "sports": "Player form, historical performance, and competitive dynamics",
        "entertainment": "Industry trends, critical reception, and commercial performance",
        "geopolitics": "Diplomatic, military, and strategic factor analysis",
        "health": "Epidemiological factors, policy responses, and transmission dynamics",
        "weather": "Meteorological patterns, climate indicators, and seasonal factors",
        "economics": "Macroeconomic indicators, policy decisions, and market expectations"
    }
    
    # Create question with causal framing
    causal_question = f"[{case.domain.upper()}] {case.title}"
    
    # Build options text
    options_text = " | ".join(case.options[:5])  # Limit to first 5 options
    if len(case.options) > 5:
        options_text += f" | ... ({len(case.options) - 5} more)"
    
    abel_question = {
        "id": f"XF_{case.id[:8]}",  # Cross-domain FutureX
        "category": "X",  # Cross-domain category
        "cap_primitive": "attest",  # Using attest for cross-domain comparison
        "question": causal_question,
        "context": f"FutureX-inspired {case.domain} question. {domain_contexts.get(case.domain, 'Multi-factor prediction')}. "
                   f"Options: {options_text}. Original FutureX Level {case.level}.",
        "cap_request": {
            "capability": "attest",
            "input": {
                "domain": case.domain,
                "prediction_type": "discrete_outcome",
                "options": case.options,
                "factors_to_consider": _get_causal_factors(case.domain),
                "analysis_depth": "high"
            }
        },
        "expected_response": {
            "most_likely_outcome": "string",
            "confidence": "float",
            "supporting_factors": ["string"],
            "uncertainty_sources": ["string"],
            "alternative_scenarios": ["string"]
        },
        "ground_truth_check": {
            "source": "futurex_challenge",
            "futurex_id": case.id,
            "original_answer": case.ground_truth,
            "domain": case.domain,
            "metric": "categorical_accuracy"
        },
        "cevs_weight": 0.8,  # Slightly lower weight for non-financial
        "metadata": {
            "futurex_level": case.level,
            "end_time": case.end_time,
            "original_source": "FutureX Challenge D25",
            "domain": case.domain,
            "cross_domain": True
        }
    }
    
    return abel_question


def _get_causal_factors(domain: str) -> List[str]:
    """Get causal factors for each domain"""
    factors = {
        "election": ["polling_trends", "economic_conditions", "media_coverage", "incumbent_advantage"],
        "sports": ["recent_form", "head_to_head_history", "injury_status", "home_advantage", "rankings"],
        "entertainment": ["chart_performance", "critical_reviews", "commercial_success", "industry_recognition"],
        "geopolitics": ["diplomatic_statements", "military_movements", "historical_patterns", "alliance_dynamics"],
        "health": ["transmission_rates", "policy_measures", "seasonal_patterns", "vaccination_rates"],
        "weather": ["seasonal_patterns", "climate_models", "historical_data", "current_conditions"],
        "economics": ["inflation_data", "employment_figures", "market_expectations", "global_conditions"]
    }
    return factors.get(domain, ["historical_trends", "current_indicators"])


def add_cross_domain_questions():
    """Add cross-domain questions to benchmark"""
    
    # Load main benchmark
    main_path = Path(__file__).parent.parent / "src" / "abel_benchmark" / "references" / "benchmark_questions_v2_enhanced.json"
    with open(main_path, 'r') as f:
        benchmark = json.load(f)
    
    # Extract and convert cases
    cases = extract_diverse_cases()
    converted = []
    
    for case in cases:
        abel_q = convert_to_causal_format(case)
        converted.append(abel_q)
    
    # Add Category X (Cross-Domain)
    if "X" not in benchmark['categories']:
        benchmark['categories']['X'] = {
            "name": "cross_domain",
            "description": "Cross-domain causal reasoning - elections, sports, entertainment, geopolitics demonstrating CAP applicability beyond finance",
            "count": len(converted),
            "weight": 0.8,
            "source": "FutureX Challenge D25",
            "domains": list(set(c.domain for c in cases))
        }
    
    # Update stats
    original_total = benchmark['total_questions']
    benchmark['total_questions'] = original_total + len(converted)
    
    # Update description
    benchmark['description'] = (
        "Abel Causal Benchmark V2.2 - Comprehensive with FutureX-inspired questions. "
        f"{benchmark['total_questions']} questions total: 35 original + 7 FutureX financial + {len(converted)} cross-domain. "
        "Tests causal reasoning across finance, elections, sports, entertainment, and geopolitics."
    )
    
    # Append questions
    benchmark['questions'].extend(converted)
    
    # Save
    with open(main_path, 'w') as f:
        json.dump(benchmark, f, indent=2)
    
    print("=" * 70)
    print("✅ Cross-domain FutureX cases added to benchmark!")
    print("=" * 70)
    print()
    print(f"📊 Updated Statistics:")
    print(f"   Original questions: 35")
    print(f"   FutureX financial: 7")
    print(f"   Cross-domain added: {len(converted)}")
    print(f"   TOTAL: {benchmark['total_questions']} questions")
    print()
    print("🌍 Category X (Cross-Domain) added:")
    
    # Group by domain
    by_domain = {}
    for q in converted:
        domain = q['metadata']['domain']
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(q['id'])
    
    for domain, ids in sorted(by_domain.items()):
        print(f"\n   {domain.upper()}:")
        for qid in ids:
            q = next(q for q in converted if q['id'] == qid)
            print(f"      - {qid}: {q['question'][:45]}...")
    
    print()
    
    return benchmark


if __name__ == "__main__":
    print("Extracting cross-domain FutureX cases...")
    add_cross_domain_questions()
