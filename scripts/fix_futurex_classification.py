#!/usr/bin/env python3
"""
修复 FutureX D25 的分类问题
更精确地识别真正的金融/市场类问题
"""

import json
import sys


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def precise_classify(title):
    """更精确的分类"""
    title_lower = title.lower()
    
    # 严格的金融/市场关键词（必须是价格、交易、金融市场相关）
    strict_finance = [
        'gold', 'oil', 'crude', 'lumber', 'commodity',
        'rate', 'fed', 'ecb', 'boe', 'selic', 'interest rate',
        'dollar', 'euro', 'pound', 'yen', 'fx', 'forex',
        'bitcoin', 'btc', 'eth', 'crypto',
        'tesla', 'nvidia', 'tsla', 'nvda', 'stock price',
        'market', 'trading', 'futures', 'volatility',
        'price of', 'closing price', 'settle', 'production'
    ]
    
    # 明确的非金融关键词
    non_finance = [
        'election', 'vote', 'president', 'political', 'party',
        'war', 'gaza', 'israel', 'iran', 'ukraine', 'russia',
        'champion', 'winner', 'tournament', 'cup', 'rugby', 'soccer',
        'baseball', 'sumo', 'olympic', 'sports',
        'usamo', 'amc', 'aime', 'math', 'education',
        'gemini', 'gpt', 'llm', 'ai', 'model', 'leaderboard',
        'movie', 'film', 'album', 'song', 'grammy', 'entertainment'
    ]
    
    # 检查是否有非金融关键词
    if any(kw in title_lower for kw in non_finance):
        return 'other', 'non_financial'
    
    # 检查是否有严格的金融关键词
    if any(kw in title_lower for kw in strict_finance):
        return 'F', 'finance'
    
    # 默认为其他
    return 'other', 'uncertain'


def fix_classification():
    """修复分类"""
    print("=" * 70)
    print("Fixing FutureX D25 Classification")
    print("=" * 70)
    print()
    
    # 加载当前 benchmark
    benchmark_path = 'src/abel_benchmark/references/benchmark_questions_v2_futurex_d25.json'
    print(f"📂 Loading: {benchmark_path}")
    benchmark = load_json(benchmark_path)
    questions = benchmark.get('questions', [])
    
    # 分离原始问题和 FutureX 问题
    original_questions = []
    futurex_questions = []
    
    for q in questions:
        if q['id'].startswith('FX_'):
            futurex_questions.append(q)
        else:
            original_questions.append(q)
    
    print(f"   Original questions: {len(original_questions)}")
    print(f"   FutureX questions: {len(futurex_questions)}")
    print()
    
    # 重新分类 FutureX 问题
    print("🔍 Re-classifying FutureX questions...")
    finance_cases = []
    other_cases = []
    
    for q in futurex_questions:
        title = q.get('question', '')
        cat, cat_type = precise_classify(title)
        
        if cat == 'F':
            finance_cases.append(q)
            q['category'] = 'F'
            q['futurex_metadata']['category'] = 'finance'
            q['futurex_metadata']['cap_ability'] = 'high'
        else:
            other_cases.append(q)
            q['category'] = 'X'  # 移到 X (cross-domain)
            q['futurex_metadata']['category'] = 'other'
            q['futurex_metadata']['cap_ability'] = 'low'
            q['cap_request'] = {
                'verb': 'llm_only',
                'note': 'Requires LLM reasoning - not financial/market related'
            }
    
    print(f"   Financial: {len(finance_cases)}")
    print(f"   Other: {len(other_cases)}")
    print()
    
    # 合并回 benchmark
    all_questions = original_questions + futurex_questions
    benchmark['questions'] = all_questions
    
    # 更新统计
    by_category = {}
    for q in all_questions:
        cat = q.get('category', 'X')
        by_category[cat] = by_category.get(cat, 0) + 1
    
    benchmark['benchmark_version'] = 'v2.5-futurex-d25-corrected'
    benchmark['description'] = (
        'Abel Causal Benchmark V2.5 - FutureX D25 Integrated (Corrected). '
        f'{len(finance_cases)} financial cases from FutureX D25. '
        f'{len(other_cases)} other cases (LLM only).'
    )
    
    # 更新 categories
    benchmark['categories']['F'] = {
        'name': 'futurex_d25_finance',
        'description': f'FutureX D25 Financial Cases - Gold, Oil, Rates, etc. ({len(finance_cases)} cases)',
        'count': by_category.get('F', 0),
        'source': 'FutureX Challenge D25',
        'cap_ability': 'high',
        'expected_success_rate': '40-60%'
    }
    
    benchmark['futurex_d25_summary'] = {
        'total_cases': 81,
        'integrated': len(finance_cases),
        'financial': len(finance_cases),
        'other': len(other_cases),
        'note': 'Only financial cases integrated for CAP testing'
    }
    
    # 保存
    save_json(benchmark, benchmark_path)
    
    print("=" * 70)
    print("✅ Classification Fixed!")
    print("=" * 70)
    print()
    print(f"Final Statistics:")
    print(f"  - Total: {len(all_questions)}")
    print(f"  - Financial (F): {len(finance_cases)}")
    print(f"  - Other (X): {by_category.get('X', 0)}")
    print()
    print("Sample Financial Cases:")
    for q in finance_cases[:5]:
        print(f"  ✓ {q['id']}: {q['question'][:50]}...")
    print()
    
    return finance_cases


if __name__ == "__main__":
    try:
        finance_cases = fix_classification()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
