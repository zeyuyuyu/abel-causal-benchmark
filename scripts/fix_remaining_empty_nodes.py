#!/usr/bin/env python3
"""
修复剩余的空节点问题
"""

import json
import sys


def load_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data: dict, path: str):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {path}")


def fix_empty_nodes(questions: list) -> list:
    """修复空节点"""
    fixes = {
        'F6': 'TSLA_close',  # Tesla
        'F7': 'NVDA_close',  # Nvidia
    }
    
    fixed_count = 0
    for q in questions:
        qid = q.get('id', '')
        
        if qid in fixes:
            cap_request = q.get('cap_request', {})
            params = cap_request.get('params', {})
            
            if not params.get('target_node'):
                params['target_node'] = fixes[qid]
                print(f"  ✓ Fixed {qid}: {fixes[qid]}")
                fixed_count += 1
    
    return questions, fixed_count


def main():
    input_path = 'src/abel_benchmark/references/benchmark_questions_v2_futurex_integrated.json'
    
    print("=" * 70)
    print("Fixing remaining empty nodes")
    print("=" * 70)
    print()
    
    # 加载
    print(f"📂 Loading: {input_path}")
    data = load_json(input_path)
    questions = data.get('questions', [])
    print(f"   Total: {len(questions)} questions")
    print()
    
    # 修复
    print("🔧 Fixing empty nodes...")
    questions, fixed_count = fix_empty_nodes(questions)
    print(f"   Fixed: {fixed_count} questions")
    print()
    
    # 保存
    data['questions'] = questions
    save_json(data, input_path)
    
    print("=" * 70)
    print("✅ Done!")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
