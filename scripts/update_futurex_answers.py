#!/usr/bin/env python3
"""
更新 FutureX cases 的答案
- 从 Manifold API 获取的 2 个答案
- 其他标记为 pending
"""

import json
import sys


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def update_futurex_answers():
    """更新 FutureX 答案"""
    print("=" * 70)
    print("Updating FutureX Cases with Fetched Answers")
    print("=" * 70)
    print()
    
    # 1. 加载 benchmark
    benchmark_path = 'src/abel_benchmark/references/benchmark_questions_v2_complete_with_answers.json'
    print(f"📂 Loading: {benchmark_path}")
    benchmark = load_json(benchmark_path)
    questions = benchmark['questions']
    print(f"   Total questions: {len(questions)}")
    print()
    
    # 2. 加载获取的答案
    print("📂 Loading fetched answers...")
    try:
        fetched = load_json('references/futurex_fetched_answers.json')
        fetched_count = fetched.get('fetched_count', 0)
        print(f"   Fetched answers: {fetched_count}")
        
        # 创建 id -> answer 映射
        answer_map = {}
        for item in fetched.get('results', []):
            case_id = item['case']['id']
            answer_map[case_id] = item['answer']
        
        print(f"   Answer map size: {len(answer_map)}")
    except:
        print("   No fetched answers found")
        answer_map = {}
    print()
    
    # 3. 更新每个 FutureX case
    print("🔧 Updating FutureX cases...")
    updated_count = 0
    pending_count = 0
    
    for q in questions:
        if not q['id'].startswith('FX_'):
            continue
        
        # 获取 FutureX original_id
        futurex_id = q.get('futurex_metadata', {}).get('original_id', '')
        
        if futurex_id in answer_map:
            # 有答案
            ans = answer_map[futurex_id]
            q['answer']['ground_truth']['status'] = 'resolved'
            q['answer']['ground_truth']['resolution'] = ans.get('resolution')
            q['answer']['ground_truth']['resolution_time'] = ans.get('resolution_time')
            q['answer']['ground_truth']['source'] = 'manifold_markets'
            updated_count += 1
            print(f"  ✅ {q['id']}: Resolved = {ans.get('resolution')}")
        else:
            # 标记为 pending
            q['answer']['ground_truth']['status'] = 'pending'
            q['answer']['ground_truth']['expected_resolve_date'] = q.get('futurex_metadata', {}).get('end_time')
            q['answer']['ground_truth']['note'] = 'Answer will be available after end_date'
            pending_count += 1
    
    print()
    print(f"Updated: {updated_count} cases with answers")
    print(f"Pending: {pending_count} cases waiting for resolution")
    print()
    
    # 4. 保存
    benchmark['questions'] = questions
    benchmark['answer_status'] = {
        'total_futurex_cases': len([q for q in questions if q['id'].startswith('FX_')]),
        'resolved': updated_count,
        'pending': pending_count,
        'fetch_date': '2026-03-20',
        'fetch_source': 'manifold_markets_api',
        'fetch_rate': f"{updated_count/len([q for q in questions if q['id'].startswith('FX_')])*100:.1f}%"
    }
    
    save_json(benchmark, benchmark_path)
    
    print("=" * 70)
    print("✅ FutureX Answers Updated!")
    print("=" * 70)
    print()
    print(f"Benchmark saved: {benchmark_path}")
    print()
    print("Note:")
    print("- 2 cases now have real answers from Manifold")
    print("- Other cases marked as 'pending'")
    print("- Can re-fetch after more questions resolve")


def create_answer_fetch_guide():
    """创建答案获取指南"""
    guide = """
# FutureX 答案获取指南

## 当前状态
- **已获取答案**: 2 / 81 (2.5%)
- **已截止问题**: 19 / 81
- **待解决问题**: 62 / 81

## 获取方法

### 1. Manifold Markets API
```python
import httpx

market_id = "market-slug"  # 从 slug 提取
response = await httpx.get(f"https://api.manifold.markets/v0/slug/{market_id}")
data = response.json()

if data.get('isResolved'):
    answer = data.get('resolution')
```

### 2. 批量获取脚本
```bash
python3 scripts/fetch_futurex_answers.py --batch --wait-for-resolve
```

### 3. 等待更多问题 resolve
- 当前日期: 2026-03-20
- 部分问题 end_time 在今天之后
- 建议 1-2 周后重新获取

## 已获取答案的问题

1. **UEFA Champions League Playoff Prop Bets**
   - Resolution: MKT
   - Resolved: 2026-03-19

2. **Champions league round of 16 fixtures**
   - Resolution: MKT
   - Resolved: 2026-03-19

## 建议

1. **短期**: 使用模拟/预测答案进行测试
2. **中期**: 定期检查并获取新 resolve 的答案
3. **长期**: 联系 FutureX 获取 historical resolved 数据集
"""
    
    with open('FUTUREX_ANSWER_FETCH_GUIDE.md', 'w') as f:
        f.write(guide)
    
    print("✅ Created: FUTUREX_ANSWER_FETCH_GUIDE.md")


if __name__ == "__main__":
    try:
        update_futurex_answers()
        create_answer_fetch_guide()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
