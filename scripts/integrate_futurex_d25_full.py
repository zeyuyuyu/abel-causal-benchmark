#!/usr/bin/env python3
"""
将 FutureX D25 完整的 81 个 cases 整合到 Benchmark
按类别分类：
- 金融/市场类 → Category F (未来可测试 CAP)
- 政治/选举 → Category P (政治)
- 体育 → Category S (体育)
- 科技/AI → Category T (科技)
- 其他 → Category O (其他)
"""

import json
import sys
from pathlib import Path


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {path}")


def classify_futurex_case(case):
    """对 FutureX case 进行分类"""
    title = (case.get('title', '') or '').lower()
    slug = (case.get('slug', '') or '').lower()
    text = title + ' ' + slug
    
    # 金融/市场类 (Abel 可能有数据)
    finance_keywords = [
        'stock', 'price', 'gold', 'oil', 'crude', 'lumber', 'commodity',
        'rate', 'interest', 'fed', 'bank', 'ecb', 'boe', 'selic',
        'dollar', 'euro', 'pound', 'yen', 'currency', 'fx',
        'bitcoin', 'crypto', 'btc', 'eth', 'volatility',
        'tesla', 'nvidia', 'tsla', 'nvda', 'apple', 'aapl',
        'market', 'trading', 'futures', 'option'
    ]
    
    # 政治类
    political_keywords = [
        'election', 'president', 'vote', 'political', 'party',
        'trump', 'biden', 'eu', 'brexit', 'taiwan', 'china', 'war',
        'iran', 'israel', 'gaza', 'ukraine', 'russia'
    ]
    
    # 体育类
    sports_keywords = [
        'sport', 'olympic', 'tournament', 'superbowl', 'nba', 'nfl',
        'soccer', 'football', 'rugby', 'tennis', 'golf',
        'winner', 'champion', 'cup', 'league', 'final'
    ]
    
    # 科技/AI 类
    tech_keywords = [
        'ai', 'gpt', 'llm', 'model', 'gemini', 'chatgpt', 'claude',
        'chip', 'semiconductor', 'gpu', 'nvidia', 'tech',
        'algorithm', 'leaderboard', 'benchmark'
    ]
    
    # 检查分类
    if any(kw in text for kw in finance_keywords):
        return 'F', 'finance', 'high'  # 金融类，CAP 可能可用
    elif any(kw in text for kw in political_keywords):
        return 'P', 'political', 'low'  # 政治类，需要 LLM
    elif any(kw in text for kw in sports_keywords):
        return 'S', 'sports', 'none'  # 体育类，CAP 不可用
    elif any(kw in text for kw in tech_keywords):
        return 'T', 'tech', 'medium'  # 科技类，可能需要 LLM
    else:
        return 'O', 'other', 'unknown'  # 其他


def convert_to_benchmark_format(case, category, category_name, cap_ability):
    """转换为 benchmark 格式"""
    level = case.get('level', 'L?')
    
    benchmark_case = {
        "id": f"FX_{case.get('id', 'unknown')[:8]}",
        "category": category,
        "cap_primitive": "predict" if cap_ability in ['high', 'medium'] else "llm_only",
        "question": case.get('title', 'No question'),
        "context": f"FutureX D25 Challenge - Level {level}. Source: {case.get('slug', 'N/A')}",
        "futurex_metadata": {
            "original_id": case.get('id'),
            "level": level,
            "end_time": case.get('end_time'),
            "slug": case.get('slug'),
            "category": category_name,
            "cap_ability": cap_ability
        },
        "cap_request": {
            "verb": "observe.predict",
            "params": {},
            "options": {"timeout_ms": 30000}
        } if cap_ability in ['high', 'medium'] else {
            "verb": "llm_only",
            "params": {},
            "note": "Requires LLM reasoning"
        },
        "cevs_weight": 1.0,
        "scoring": {
            "cap_eligible": cap_ability == 'high',
            "llm_required": cap_ability in ['low', 'none', 'unknown'],
            "hybrid_approach": cap_ability == 'medium'
        }
    }
    
    return benchmark_case


def integrate_futurex_d25():
    """整合 FutureX D25"""
    print("=" * 70)
    print("Integrating FutureX D25 (81 cases) into Benchmark")
    print("=" * 70)
    print()
    
    # 1. 加载 FutureX D25 数据
    futurex_path = 'references/futurex_official_81_cases.json'
    print(f"📂 Loading FutureX D25: {futurex_path}")
    futurex_data = load_json(futurex_path)
    futurex_cases = futurex_data.get('cases', [])
    print(f"   Total FutureX cases: {len(futurex_cases)}")
    print()
    
    # 2. 分类统计
    print("🔍 Classifying cases...")
    classification = {
        'F': [], 'P': [], 'S': [], 'T': [], 'O': []
    }
    category_names = {
        'F': 'finance',
        'P': 'political',
        'S': 'sports',
        'T': 'tech',
        'O': 'other'
    }
    cap_abilities = {
        'F': 'high',
        'P': 'low',
        'S': 'none',
        'T': 'medium',
        'O': 'unknown'
    }
    
    for case in futurex_cases:
        cat, cat_name, cap_ability = classify_futurex_case(case)
        classification[cat].append(case)
        
        # 转换为 benchmark 格式
        benchmark_case = convert_to_benchmark_format(case, cat, cat_name, cap_ability)
    
    # 3. 打印分类统计
    print("\n📊 Classification Results:")
    for cat in ['F', 'P', 'S', 'T', 'O']:
        count = len(classification[cat])
        name = category_names[cat]
        ability = cap_abilities[cat]
        print(f"  {cat} ({name:12}) - CAP ability: {ability:8} : {count:2} cases")
    print()
    
    # 4. 加载当前 benchmark
    benchmark_path = 'src/abel_benchmark/references/benchmark_questions_v2_complete.json'
    print(f"📂 Loading current benchmark: {benchmark_path}")
    benchmark = load_json(benchmark_path)
    existing_questions = benchmark.get('questions', [])
    print(f"   Existing questions: {len(existing_questions)}")
    print()
    
    # 5. 合并 (只添加金融类 F)
    print("🔧 Merging FutureX financial cases...")
    new_questions = existing_questions.copy()
    
    # 只为金融类创建 benchmark cases
    added_count = 0
    for case in classification['F']:
        benchmark_case = convert_to_benchmark_format(case, 'F', 'finance', 'high')
        new_questions.append(benchmark_case)
        added_count += 1
        print(f"  ✓ Added: {benchmark_case['id']} - {benchmark_case['question'][:50]}...")
    
    print(f"\n   Added {added_count} financial cases from FutureX")
    print()
    
    # 6. 更新元数据
    print("📝 Updating metadata...")
    
    # 统计
    by_category = {}
    for q in new_questions:
        cat = q.get('category', 'X')
        by_category[cat] = by_category.get(cat, 0) + 1
    
    benchmark['benchmark_version'] = 'v2.5-futurex-d25-integrated'
    benchmark['release_date'] = '2026-03-20'
    benchmark['total_questions'] = len(new_questions)
    benchmark['description'] = (
        'Abel Causal Benchmark V2.5 - FutureX D25 Integrated. '
        f'Includes {len(existing_questions)} original + {added_count} FutureX D25 financial cases. '
        'FutureX D25 total: 81 cases (6 finance, 5 political, 2 sports, 5 tech, 63 other)'
    )
    
    # 更新 categories
    benchmark['categories']['F'] = {
        'name': 'futurex_d25_finance',
        'description': f'FutureX D25 Financial Cases ({len(classification["F"])} cases) - Gold, Oil, Interest Rates, etc.',
        'count': by_category.get('F', 0),
        'source': 'FutureX Challenge D25',
        'cap_ability': 'high',
        'expected_success_rate': '40-60%'
    }
    
    # 添加 FutureX 统计
    benchmark['futurex_d25_summary'] = {
        'total_cases': 81,
        'classification': {
            'finance': len(classification['F']),
            'political': len(classification['P']),
            'sports': len(classification['S']),
            'tech': len(classification['T']),
            'other': len(classification['O'])
        },
        'integrated_into_benchmark': len(classification['F']),
        'note': 'Only financial cases integrated (CAP testable). Others require LLM.'
    }
    
    benchmark['questions'] = new_questions
    
    # 7. 保存
    output_path = 'src/abel_benchmark/references/benchmark_questions_v2_futurex_d25.json'
    save_json(benchmark, output_path)
    
    print()
    print("=" * 70)
    print("✅ FutureX D25 Integration Complete!")
    print("=" * 70)
    print()
    print(f"Final Statistics:")
    print(f"  - Total questions: {len(new_questions)}")
    print(f"  - Original: {len(existing_questions)}")
    print(f"  - FutureX D25 added: {added_count} (financial only)")
    print()
    print(f"Category Distribution:")
    for cat, count in sorted(by_category.items()):
        print(f"  - {cat}: {count}")
    print()
    print(f"Output: {output_path}")
    
    return output_path


def create_full_futurex_reference():
    """创建完整的 FutureX D25 参考文件（包含所有 81 个 cases，用于 LLM 测试）"""
    print("\n" + "=" * 70)
    print("Creating Full FutureX D25 Reference File")
    print("=" * 70)
    print()
    
    # 加载 FutureX 数据
    futurex_path = 'references/futurex_official_81_cases.json'
    futurex_data = load_json(futurex_path)
    futurex_cases = futurex_data.get('cases', [])
    
    # 分类所有 cases
    classified_cases = []
    category_names = {
        'F': 'finance', 'P': 'political', 'S': 'sports', 
        'T': 'tech', 'O': 'other'
    }
    
    for case in futurex_cases:
        cat, cat_name, cap_ability = classify_futurex_case(case)
        classified_case = {
            'futurex_id': case.get('id'),
            'title': case.get('title'),
            'level': case.get('level'),
            'end_time': case.get('end_time'),
            'category': cat,
            'category_name': cat_name,
            'cap_ability': cap_ability,
            'test_approach': 'CAP' if cap_ability == 'high' else 'LLM' if cap_ability in ['low', 'none'] else 'Hybrid'
        }
        classified_cases.append(classified_case)
    
    # 保存完整参考
    output = {
        'benchmark_name': 'FutureX Challenge D25 - Full Reference',
        'total_cases': 81,
        'source': 'https://huggingface.co/datasets/futurex-ai/Futurex-Online',
        'classification_summary': {
            'finance': len([c for c in classified_cases if c['category'] == 'F']),
            'political': len([c for c in classified_cases if c['category'] == 'P']),
            'sports': len([c for c in classified_cases if c['category'] == 'S']),
            'tech': len([c for c in classified_cases if c['category'] == 'T']),
            'other': len([c for c in classified_cases if c['category'] == 'O'])
        },
        'cases': classified_cases
    }
    
    output_path = 'references/futurex_d25_classified.json'
    save_json(output, output_path)
    
    print("Classification Summary:")
    for cat_name, count in output['classification_summary'].items():
        print(f"  - {cat_name}: {count}")
    print()
    print(f"Full reference saved: {output_path}")
    
    return output_path


if __name__ == "__main__":
    try:
        # 1. 整合到主 benchmark
        integrate_futurex_d25()
        
        # 2. 创建完整参考文件
        create_full_futurex_reference()
        
        print("\n" + "=" * 70)
        print("All tasks completed successfully!")
        print("=" * 70)
        
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
