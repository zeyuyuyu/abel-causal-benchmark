#!/usr/bin/env python3
"""
整合所有 FutureX case 到 benchmark
1. 合并 futurex_imported_questions.json (7 个金融问题)
2. 修复 Category F 和 X 的问题格式
3. 添加正确的节点名称
4. 统一使用 CAP 标准格式
"""

import json
import sys
import re
from pathlib import Path


def load_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data: dict, path: str):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {path}")


def extract_ticker_from_question(question: str) -> str:
    """从问题文本中提取 ticker"""
    # 匹配常见的 ticker 模式
    patterns = [
        r'\b(GC)\b',  # Gold
        r'\b(CL)\b',  # Crude Oil
        r'\b(OPEN)\b',  # Opendoor
        r'\b(TSLA)\b',  # Tesla
        r'\b(NVDA)\b',  # Nvidia
        r'\b(BTC)\b',  # Bitcoin
        r'\b(ETH)\b',  # Ethereum
        r'\b(SPY)\b',  # S&P 500
        r'\b(QQQ)\b',  # Nasdaq
        r'\b(GLD)\b',  # Gold ETF
        r'\b(SLV)\b',  # Silver
        r'\b(USO)\b',  # Oil ETF
    ]
    
    for pattern in patterns:
        match = re.search(pattern, question)
        if match:
            ticker = match.group(1)
            # 转换为标准格式
            ticker_map = {
                'GC': 'GCUSD',
                'CL': 'CLUSD',
                'OPEN': 'OPEN',
                'TSLA': 'TSLA',
                'NVDA': 'NVDA',
                'BTC': 'BTCUSD',
                'ETH': 'ETHUSD',
            }
            return ticker_map.get(ticker, ticker)
    
    return None


def fix_futurex_financial_questions(questions: list) -> list:
    """修复 FutureX 金融问题 (Category F)"""
    fixed = []
    
    for q in questions:
        if q.get('category') == 'F':
            cap_request = q.get('cap_request', {})
            params = cap_request.get('params', {})
            
            # 如果没有 target_node，从问题中提取
            if not params.get('target_node'):
                ticker = extract_ticker_from_question(q.get('question', ''))
                if ticker:
                    params['target_node'] = f"{ticker}_close"
                    print(f"  ✓ {q['id']}: Extracted {ticker}_close from question")
                else:
                    print(f"  ⚠ {q['id']}: Could not extract ticker")
            
            # 修复请求格式
            q['cap_request'] = {
                'verb': 'observe.predict',
                'params': params,
                'options': {'timeout_ms': 30000}
            }
            
            # 添加 FutureX 标记
            if 'metadata' not in q:
                q['metadata'] = {}
            q['metadata']['source'] = 'FutureX_Challenge_D25'
            q['metadata']['category'] = 'financial_prediction'
        
        fixed.append(q)
    
    return fixed


def fix_cross_domain_questions(questions: list) -> list:
    """修复跨领域问题 (Category X)"""
    fixed = []
    
    for q in questions:
        if q.get('category') == 'X':
            # 这些是非金融问题，CAP 可能无法直接回答
            # 保留它们用于展示，但标记为需要 LLM 增强
            
            if 'metadata' not in q:
                q['metadata'] = {}
            q['metadata']['requires_llm'] = True
            q['metadata']['category'] = 'cross_domain'
            q['metadata']['cap_compatible'] = False
            
            # 如果有节点信息，修复格式
            cap_request = q.get('cap_request', {})
            if cap_request:
                params = cap_request.get('params', {})
                if 'target_node' in params and params['target_node']:
                    # 添加 _close 后缀
                    if not params['target_node'].endswith('_close'):
                        params['target_node'] = f"{params['target_node']}_close"
                
                q['cap_request'] = {
                    'verb': 'observe.predict',
                    'params': params,
                    'options': {'timeout_ms': 30000}
                }
        
        fixed.append(q)
    
    return fixed


def merge_futurex_imported_questions(base_questions: list, imported_questions: list) -> list:
    """合并 FutureX 导入的问题"""
    merged = base_questions.copy()
    
    # 创建 ID 集合避免重复
    existing_ids = {q.get('id') for q in merged}
    
    for q in imported_questions:
        qid = q.get('id', '')
        if qid and qid not in existing_ids:
            # 修复导入问题的格式
            if 'cap_request' in q:
                old_request = q['cap_request']
                if 'input' in old_request:
                    # 转换旧格式到新格式
                    input_data = old_request['input']
                    target = input_data.get('target_node', '')
                    
                    # 添加 _close 后缀
                    if target and not target.endswith('_close'):
                        target = f"{target}_close"
                    
                    q['cap_request'] = {
                        'verb': 'observe.predict',
                        'params': {'target_node': target},
                        'options': {'timeout_ms': 30000}
                    }
            
            merged.append(q)
            print(f"  ✓ Added {qid}")
        else:
            print(f"  ⚠ Skipped duplicate {qid}")
    
    return merged


def renumber_questions(questions: list) -> list:
    """重新编号问题，确保 ID 唯一"""
    # 按类别分组
    by_category = {}
    for q in questions:
        cat = q.get('category', 'X')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(q)
    
    # 重新编号
    new_questions = []
    for cat in sorted(by_category.keys()):
        cat_questions = by_category[cat]
        for i, q in enumerate(cat_questions, 1):
            old_id = q.get('id', '')
            # 保留有意义的 ID 前缀
            if old_id.startswith('FX_'):
                new_id = f"F{i}_{old_id[3:]}"
            elif old_id.startswith('XF_'):
                new_id = f"X{i}_{old_id[3:]}"
            elif old_id[0] in 'ABCDEF':
                new_id = f"{cat}{i}"
            else:
                new_id = f"{cat}{i}_{old_id}"
            
            q['id'] = new_id
            new_questions.append(q)
    
    return new_questions


def create_integrated_benchmark():
    """创建整合后的 benchmark"""
    print("=" * 70)
    print("Integrating FutureX Cases into Benchmark")
    print("=" * 70)
    print()
    
    # 1. 加载当前 benchmark
    base_path = 'src/abel_benchmark/references/benchmark_questions_v2_complete.json'
    print(f"📂 Loading base benchmark: {base_path}")
    benchmark = load_json(base_path)
    questions = benchmark.get('questions', [])
    print(f"   Base: {len(questions)} questions")
    print()
    
    # 2. 加载 FutureX 导入的问题
    futurex_path = 'src/abel_benchmark/references/futurex_imported_questions.json'
    print(f"📂 Loading FutureX imported: {futurex_path}")
    futurex_data = load_json(futurex_path)
    imported_questions = futurex_data.get('questions', [])
    print(f"   FutureX imported: {len(imported_questions)} questions")
    print()
    
    # 3. 合并问题
    print("🔧 Merging questions...")
    questions = merge_futurex_imported_questions(questions, imported_questions)
    print(f"   Total after merge: {len(questions)} questions")
    print()
    
    # 4. 修复 Category F 问题
    print("🔧 Fixing Category F (Financial) questions...")
    questions = fix_futurex_financial_questions(questions)
    print()
    
    # 5. 修复 Category X 问题
    print("🔧 Fixing Category X (Cross-domain) questions...")
    questions = fix_cross_domain_questions(questions)
    print()
    
    # 6. 重新编号
    print("🔧 Renumbering questions...")
    questions = renumber_questions(questions)
    print()
    
    # 7. 更新元数据
    print("📝 Updating metadata...")
    
    # 统计
    by_category = {}
    for q in questions:
        cat = q.get('category', 'X')
        by_category[cat] = by_category.get(cat, 0) + 1
    
    benchmark['benchmark_version'] = 'v2.4-futurex-integrated'
    benchmark['cap_version'] = '0.2.2'
    benchmark['release_date'] = '2026-03-20'
    benchmark['total_questions'] = len(questions)
    benchmark['description'] = (
        'Abel Causal Benchmark V2.4 - FutureX Integrated. '
        'Includes FutureX Challenge D25 financial questions and cross-domain cases. '
        'Category F: FutureX financial predictions. '
        'Category X: Cross-domain (requires LLM enhancement).'
    )
    
    benchmark['categories'] = {
        'A': {'name': 'predict', 'description': 'Direct causal predictions', 'count': by_category.get('A', 0)},
        'B': {'name': 'intervene', 'description': 'Intervention analysis', 'count': by_category.get('B', 0)},
        'C': {'name': 'path', 'description': 'Causal chain tracing', 'count': by_category.get('C', 0)},
        'D': {'name': 'sensitivity', 'description': 'Uncertainty analysis', 'count': by_category.get('D', 0)},
        'E': {'name': 'attest', 'description': 'Comparative analysis', 'count': by_category.get('E', 0)},
        'F': {'name': 'futurex_financial', 'description': 'FutureX Challenge financial predictions (Gold, Oil, Stocks)', 'count': by_category.get('F', 0), 'source': 'FutureX D25'},
        'X': {'name': 'cross_domain', 'description': 'Cross-domain (Elections, Sports, Entertainment) - requires LLM', 'count': by_category.get('X', 0), 'note': 'CAP-compatible subset marked'}
    }
    
    benchmark['questions'] = questions
    
    print(f"   Final total: {len(questions)} questions")
    print(f"   By category: {dict(sorted(by_category.items()))}")
    print()
    
    # 8. 保存
    output_path = 'src/abel_benchmark/references/benchmark_questions_v2_futurex_integrated.json'
    save_json(benchmark, output_path)
    
    print("=" * 70)
    print("✅ FutureX integration complete!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  - Total questions: {len(questions)}")
    print(f"  - FutureX financial (F): {by_category.get('F', 0)} cases")
    print(f"  - Cross-domain (X): {by_category.get('X', 0)} cases")
    print(f"  - Core causal (A-E): {sum(by_category.get(c, 0) for c in 'ABCDE')} cases")
    print()
    print(f"Output: {output_path}")
    
    return output_path


if __name__ == "__main__":
    try:
        output = create_integrated_benchmark()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
