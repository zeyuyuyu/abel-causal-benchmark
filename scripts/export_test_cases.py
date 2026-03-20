#!/usr/bin/env python3
"""
将 benchmark 中的每个 test case 导出为独立文件
文件命名: {case_id}.json
包含完整 case 信息和 ground truth
"""

import json
import sys
from pathlib import Path


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def export_test_cases():
    """导出所有 test cases"""
    print("=" * 70)
    print("Exporting Test Cases to Individual Files")
    print("=" * 70)
    print()
    
    # 加载 validated benchmark
    benchmark_path = 'src/abel_benchmark/references/benchmark_questions_v2_validated.json'
    print(f"📂 Loading: {benchmark_path}")
    benchmark = load_json(benchmark_path)
    questions = benchmark['questions']
    print(f"   Total cases: {len(questions)}")
    print()
    
    # 创建输出目录
    output_dir = Path('test_cases')
    output_dir.mkdir(exist_ok=True)
    
    # 清空已有文件
    existing_files = list(output_dir.glob('*.json'))
    if existing_files:
        print(f"🗑️  Removing {len(existing_files)} existing files...")
        for f in existing_files:
            f.unlink()
    
    # 导出每个 case
    print("📤 Exporting cases...")
    exported = 0
    
    for q in questions:
        case_id = q.get('id', 'unknown')
        
        # 构建独立的 case 文件
        case_file = {
            'case_id': case_id,
            'category': q.get('category'),
            'cap_primitive': q.get('cap_primitive'),
            'question': q.get('question'),
            'context': q.get('context'),
            'cap_request': q.get('cap_request'),
            'expected_response': q.get('expected_response'),
            'answer': q.get('answer'),
            'ground_truth': q.get('answer', {}).get('ground_truth') if 'answer' in q else None,
            'multidimensional_classification': q.get('multidimensional_classification'),
            'cevs_weight': q.get('cevs_weight', 1.0),
            'scoring_criteria': q.get('scoring_criteria')
        }
        
        # 移除 None 值
        case_file = {k: v for k, v in case_file.items() if v is not None}
        
        # 保存为独立文件
        output_path = output_dir / f"{case_id}.json"
        with open(output_path, 'w') as f:
            json.dump(case_file, f, indent=2, ensure_ascii=False)
        
        exported += 1
    
    print(f"   ✅ Exported: {exported} cases")
    print()
    
    # 创建索引文件
    index = {
        'total_cases': exported,
        'export_date': '2026-03-20',
        'source': 'benchmark_questions_v2_validated.json',
        'cases': [
            {
                'id': q['id'],
                'category': q.get('category'),
                'cap_primitive': q.get('cap_primitive'),
                'domain': q.get('multidimensional_classification', {}).get('dimensions', {}).get('domain', {}).get('value'),
                'file': f"{q['id']}.json"
            }
            for q in questions
        ]
    }
    
    index_path = output_dir / '_index.json'
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"✅ Created index: {index_path}")
    print()
    
    # 统计
    by_category = {}
    for q in questions:
        cat = q.get('category', 'unknown')
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print("📊 Distribution:")
    for cat, count in sorted(by_category.items()):
        print(f"  {cat}: {count}")
    print()
    
    print("=" * 70)
    print("✅ All Test Cases Exported!")
    print("=" * 70)
    print()
    print(f"Location: test_cases/")
    print(f"Format: {case_id}.json")
    print(f"Index: _index.json")
    
    return exported


def create_case_example():
    """创建一个示例 case 文件说明"""
    example = {
        "case_id": "A1",
        "category": "A",
        "cap_primitive": "predict",
        "question": "Will BTCUSD go up in the next 5 hours based on current ETH momentum?",
        "context": "2025-03 Crypto market showing ETH leading BTC correlation",
        "cap_request": {
            "verb": "observe.predict",
            "params": {
                "target_node": "BTCUSD_close"
            },
            "options": {
                "timeout_ms": 30000
            }
        },
        "expected_response": {
            "cumulative_prediction": "float",
            "probability_up": "float",
            "parent_contributions": [
                {
                    "node": "string",
                    "impact": "float",
                    "tau": "int"
                }
            ]
        },
        "ground_truth": {
            "status": "verifiable",
            "source": "yahoo_finance",
            "method": "api_fetch",
            "ticker": "BTCUSD",
            "metric": "directional_accuracy",
            "delay_hours": 6,
            "verification_url": "https://finance.yahoo.com/quote/BTCUSD"
        },
        "multidimensional_classification": {
            "dimensions": {
                "domain": {
                    "value": "finance",
                    "confidence": 1.0
                },
                "cap_ability": {
                    "value": "full",
                    "reason": "Known ticker in causal graph"
                }
            },
            "recommended_approach": "CAP_only",
            "test_priority": "high"
        }
    }
    
    with open('test_cases/_EXAMPLE.json', 'w') as f:
        json.dump(example, f, indent=2)
    
    print("✅ Created example: test_cases/_EXAMPLE.json")


if __name__ == "__main__":
    try:
        count = export_test_cases()
        create_case_example()
        
        print()
        print("📖 Usage:")
        print("  Load single case: json.load(open('test_cases/A1.json'))")
        print("  Load index: json.load(open('test_cases/_index.json'))")
        
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
