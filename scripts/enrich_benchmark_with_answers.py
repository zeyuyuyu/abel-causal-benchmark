#!/usr/bin/env python3
"""
完善 Benchmark，添加完整的答案结构
1. 从 FutureX 提取选项 (A, B, C...)
2. 为所有 case 添加 answer 字段
3. 创建评分标准
"""

import json
import re
import sys
from typing import Dict, List, Optional


def load_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data: dict, path: str):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {path}")


def extract_options_from_prompt(prompt: str) -> List[Dict[str, str]]:
    """从 FutureX prompt 中提取选项"""
    options = []
    # 匹配 "A. the outcome be ..." 格式
    pattern = r'([A-Z])\.\s*the outcome be ([^\n]+)'
    matches = re.findall(pattern, prompt)
    
    for letter, description in matches:
        options.append({
            'id': letter,
            'text': description.strip(),
            'type': 'outcome'
        })
    
    return options


def enrich_futurex_case(case: dict, futurex_data: dict) -> dict:
    """丰富 FutureX case 的答案信息"""
    # 查找对应的 FutureX 原始数据
    futurex_id = case.get('futurex_metadata', {}).get('original_id', '')
    
    original_case = None
    for fx in futurex_data.get('cases', []):
        if fx.get('id') == futurex_id:
            original_case = fx
            break
    
    if not original_case:
        return case
    
    # 提取选项
    prompt = original_case.get('prompt', '')
    options = extract_options_from_prompt(prompt)
    
    # 添加 answer 结构
    case['answer'] = {
        'type': 'multiple_choice' if options else 'prediction',
        'options': options,
        'ground_truth': {
            'status': 'pending',  # FutureX 问题通常还未 resolve
            'expected_resolve_date': original_case.get('end_time'),
            'source': 'FutureX_Challenge_D25',
            'resolution_url': original_case.get('slug', '')
        },
        'scoring_method': 'exact_match' if options else 'directional_accuracy'
    }
    
    return case


def enrich_original_case(case: dict) -> dict:
    """丰富原始 case 的答案信息"""
    # 根据 case 类型添加合适的答案结构
    cap_primitive = case.get('cap_primitive', '')
    
    if cap_primitive == 'predict':
        case['answer'] = {
            'type': 'continuous',
            'prediction_type': 'float',
            'ground_truth': case.get('ground_truth_check', {
                'source': 'yahoo_finance',
                'delay_hours': 24,
                'metric': 'directional_accuracy'
            }),
            'scoring_method': 'directional_accuracy',
            'acceptable_error': 0.05
        }
    
    elif cap_primitive == 'intervene':
        case['answer'] = {
            'type': 'causal_effect',
            'prediction_type': 'float',
            'ground_truth': {
                'source': 'simulation',
                'metric': 'effect_magnitude'
            },
            'scoring_method': 'effect_accuracy',
            'acceptable_error': 0.10
        }
    
    elif cap_primitive == 'path':
        case['answer'] = {
            'type': 'path_structure',
            'prediction_type': 'list',
            'ground_truth': {
                'source': 'graph_topology',
                'metric': 'path_accuracy'
            },
            'scoring_method': 'path_similarity',
            'acceptable_error': None
        }
    
    elif cap_primitive == 'attest':
        case['answer'] = {
            'type': 'comparison',
            'prediction_type': 'ranking',
            'ground_truth': {
                'source': 'historical_correlation',
                'metric': 'correlation_accuracy'
            },
            'scoring_method': 'rank_correlation',
            'acceptable_error': None
        }
    
    else:
        case['answer'] = {
            'type': 'unknown',
            'ground_truth': {
                'source': 'manual_verification',
                'metric': 'expert_judgment'
            },
            'scoring_method': 'expert_evaluation'
        }
    
    return case


def create_complete_benchmark():
    """创建完整的 benchmark"""
    print("=" * 70)
    print("Enriching Benchmark with Complete Answer Structure")
    print("=" * 70)
    print()
    
    # 1. 加载当前 benchmark
    benchmark_path = 'src/abel_benchmark/references/benchmark_questions_v2_futurex_d25.json'
    print(f"📂 Loading benchmark: {benchmark_path}")
    benchmark = load_json(benchmark_path)
    questions = benchmark.get('questions', [])
    print(f"   Total questions: {len(questions)}")
    print()
    
    # 2. 加载 FutureX 原始数据
    futurex_path = 'references/futurex_official_81_cases.json'
    print(f"📂 Loading FutureX data: {futurex_path}")
    futurex_data = load_json(futurex_path)
    print(f"   FutureX cases: {len(futurex_data.get('cases', []))}")
    print()
    
    # 3. 丰富每个 case
    print("🔧 Enriching cases with answer structure...")
    enriched_count = 0
    
    for q in questions:
        # 如果已经有 answer，跳过
        if 'answer' in q:
            continue
        
        if q['id'].startswith('FX_'):
            # FutureX case
            q = enrich_futurex_case(q, futurex_data)
        else:
            # 原始 case
            q = enrich_original_case(q)
        
        enriched_count += 1
    
    print(f"   Enriched {enriched_count} cases")
    print()
    
    # 4. 统计
    print("📊 Answer Structure Statistics:")
    
    with_answer = sum(1 for q in questions if 'answer' in q)
    with_ground_truth = sum(1 for q in questions if q.get('answer', {}).get('ground_truth'))
    with_options = sum(1 for q in questions if q.get('answer', {}).get('options'))
    
    print(f"   Total questions: {len(questions)}")
    print(f"   With answer structure: {with_answer}")
    print(f"   With ground_truth: {with_ground_truth}")
    print(f"   With multiple choice options: {with_options}")
    print()
    
    # 5. 保存
    benchmark['questions'] = questions
    benchmark['benchmark_version'] = 'v2.6-complete-with-answers'
    benchmark['description'] = (
        'Abel Causal Benchmark V2.6 - Complete with Answer Structure. '
        f'{len(questions)} cases with ground truth, options, and scoring criteria.'
    )
    
    # 添加答案结构说明
    benchmark['answer_structure'] = {
        'types': [
            'continuous',      # 连续值预测 (价格、概率)
            'multiple_choice', # 多选题 (A, B, C)
            'causal_effect',   # 因果效应
            'path_structure',  # 路径结构
            'comparison',      # 比较排名
        ],
        'ground_truth_sources': [
            'yahoo_finance',
            'FutureX_Challenge_D25',
            'simulation',
            'graph_topology',
            'historical_correlation',
            'manual_verification'
        ],
        'scoring_methods': [
            'directional_accuracy',
            'exact_match',
            'effect_accuracy',
            'path_similarity',
            'rank_correlation',
            'expert_evaluation'
        ]
    }
    
    output_path = 'src/abel_benchmark/references/benchmark_questions_v2_complete_with_answers.json'
    save_json(benchmark, output_path)
    
    print("=" * 70)
    print("✅ Complete Benchmark Created!")
    print("=" * 70)
    print()
    print(f"Output: {output_path}")
    print()
    
    # 显示示例
    print("📋 Sample Cases with Answers:")
    sample_cases = [q for q in questions if 'answer' in q][:3]
    for i, q in enumerate(sample_cases, 1):
        print(f"\n{i}. {q['id']}: {q['question'][:50]}...")
        print(f"   Answer type: {q['answer']['type']}")
        if q['answer'].get('options'):
            print(f"   Options: {len(q['answer']['options'])}")
        if q['answer'].get('ground_truth'):
            print(f"   Ground truth: {q['answer']['ground_truth'].get('source', 'N/A')}")
    
    return output_path


def create_answer_summary():
    """创建答案摘要报告"""
    print("\n" + "=" * 70)
    print("Creating Answer Summary Report")
    print("=" * 70)
    print()
    
    benchmark = load_json('src/abel_benchmark/references/benchmark_questions_v2_complete_with_answers.json')
    questions = benchmark['questions']
    
    # 按答案类型统计
    by_type = {}
    by_scoring = {}
    by_source = {}
    
    for q in questions:
        if 'answer' in q:
            ans = q['answer']
            t = ans.get('type', 'unknown')
            s = ans.get('scoring_method', 'unknown')
            src = ans.get('ground_truth', {}).get('source', 'unknown')
            
            by_type[t] = by_type.get(t, 0) + 1
            by_scoring[s] = by_scoring.get(s, 0) + 1
            by_source[src] = by_source.get(src, 0) + 1
    
    report = {
        'benchmark_name': 'Abel Causal Benchmark',
        'version': 'v2.6',
        'total_cases': len(questions),
        'cases_with_answers': sum(by_type.values()),
        'statistics': {
            'by_answer_type': by_type,
            'by_scoring_method': by_scoring,
            'by_ground_truth_source': by_source
        },
        'notes': [
            'FutureX cases have pending ground truth (resolve on end_date)',
            'Finance cases use yahoo_finance for ground truth',
            'Intervention cases use simulation for validation'
        ]
    }
    
    output_path = 'references/benchmark_answer_summary.json'
    save_json(report, output_path)
    
    print("Answer Summary:")
    print(f"  By Type: {by_type}")
    print(f"  By Scoring: {by_scoring}")
    print(f"  By Source: {by_source}")
    print()
    print(f"Report saved: {output_path}")


if __name__ == "__main__":
    try:
        create_complete_benchmark()
        create_answer_summary()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
