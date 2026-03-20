#!/usr/bin/env python3
"""
Merge FutureX questions into main Abel Causal Benchmark

This script:
1. Loads the main benchmark questions
2. Loads the FutureX imported questions
3. Changes their category to 'F' (FutureX-inspired)
4. Updates total count
5. Saves merged benchmark
"""

import json
from pathlib import Path
from copy import deepcopy


def merge_futurex_questions():
    """Merge FutureX questions into main benchmark"""
    
    # Load main benchmark
    main_path = Path(__file__).parent.parent / "src" / "abel_benchmark" / "references" / "benchmark_questions_v2_enhanced.json"
    with open(main_path, 'r') as f:
        main_benchmark = json.load(f)
    
    # Load FutureX questions
    futurex_path = Path(__file__).parent.parent / "src" / "abel_benchmark" / "references" / "futurex_imported_questions.json"
    with open(futurex_path, 'r') as f:
        futurex_data = json.load(f)
    
    # Get FutureX questions and update category
    futurex_questions = futurex_data['questions']
    
    # Update each question to Category F with new IDs
    updated_questions = []
    for i, q in enumerate(futurex_questions, 1):
        updated_q = deepcopy(q)
        updated_q['id'] = f"F{i}"  # New IDs: F1, F2, F3, etc.
        updated_q['category'] = "F"  # Change to Category F
        updated_q['context'] = f"[FutureX Inspired] {q['context']}"
        updated_questions.append(updated_q)
    
    # Add Category F definition if not exists
    if "F" not in main_benchmark['categories']:
        main_benchmark['categories']['F'] = {
            "name": "futurex_inspired",
            "description": "FutureX Challenge inspired questions - threshold-based predictions and real historical outcomes",
            "count": len(updated_questions),
            "weight": 1.0,
            "source": "FutureX Challenge D25"
        }
    else:
        # Update count
        main_benchmark['categories']['F']['count'] = len(updated_questions)
    
    # Update total questions count
    original_count = main_benchmark['total_questions']
    main_benchmark['total_questions'] = original_count + len(updated_questions)
    
    # Update description
    main_benchmark['description'] = (
        "Abel Causal Benchmark V2.1 - Enhanced with FutureX-inspired questions. "
        "42 questions total: 35 original + 7 FutureX financial predictions. "
        "Tests causal reasoning with real historical outcomes and forward-looking scenarios."
    )
    
    # Append FutureX questions to the questions list
    main_benchmark['questions'].extend(updated_questions)
    
    # Save merged benchmark
    output_path = main_path
    with open(output_path, 'w') as f:
        json.dump(main_benchmark, f, indent=2)
    
    print("=" * 70)
    print("✅ FutureX questions merged into main benchmark!")
    print("=" * 70)
    print()
    print(f"📊 Statistics:")
    print(f"   Original questions: {original_count}")
    print(f"   FutureX questions added: {len(updated_questions)}")
    print(f"   Total questions: {main_benchmark['total_questions']}")
    print()
    print(f"📁 Updated file: {output_path}")
    print()
    print("📝 Category F (FutureX Inspired) added:")
    for q in updated_questions:
        ticker = q['cap_request']['input']['target_node'].replace('_close', '')
        print(f"   - {q['id']}: {q['question'][:50]}... [{ticker}]")
    print()
    
    return main_benchmark


if __name__ == "__main__":
    merge_futurex_questions()
