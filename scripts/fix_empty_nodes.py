#!/usr/bin/env python3
"""
修复 benchmark 中的空节点问题
"""

import json
import sys


def load_benchmark(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def save_benchmark(data: dict, path: str):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {path}")


# 从原始问题中提取正确的节点
ORIGINAL_NODES = {
    "A1": "BTCUSD",
    "A2": "NVDA",
    "A3": "SPY",
    "A4": "TSLA",
    "A5": "AAPL",
    "A6": "ETHUSD",
    "A7": "XLF",
    "A8": "SOLUSD",
}


def fix_predict_nodes(questions: list) -> list:
    """修复 predict 问题的空节点"""
    fixed = []
    
    for q in questions:
        if q.get("cap_primitive") == "predict":
            qid = q.get("id", "")
            cap_request = q.get("cap_request", {})
            params = cap_request.get("params", {})
            
            # 如果是空节点，使用原始节点
            if not params.get("target_node") and qid in ORIGINAL_NODES:
                params["target_node"] = ORIGINAL_NODES[qid]
                print(f"  ✓ Fixed {qid}: target_node = {ORIGINAL_NODES[qid]}")
            elif not params.get("target_node"):
                # 尝试从 question 文本中提取
                question_text = q.get("question", "")
                # 简单提取大写单词作为节点名
                import re
                tickers = re.findall(r'\b([A-Z]{2,8}USD?)\b', question_text)
                if tickers:
                    params["target_node"] = tickers[0]
                    print(f"  ✓ Fixed {qid}: extracted {tickers[0]} from question")
                else:
                    print(f"  ⚠ {qid}: Could not determine target_node")
        
        fixed.append(q)
    
    return fixed


def fix_path_nodes(questions: list) -> list:
    """修复 path 问题的空节点"""
    fixed = []
    
    for q in questions:
        if q.get("cap_primitive") == "path":
            qid = q.get("id", "")
            cap_request = q.get("cap_request", {})
            params = cap_request.get("params", {})
            
            # 检查空节点
            source = params.get("source_node_id", "")
            target = params.get("target_node_id", "")
            
            if not source or not target:
                # 从 question 提取
                question_text = q.get("question", "")
                import re
                
                # 提取路径相关的节点
                # 例如 "What is the causal path from NVDA to AMD?"
                path_match = re.search(r'from\s+(\w+)\s+to\s+(\w+)', question_text, re.IGNORECASE)
                if path_match:
                    if not source:
                        params["source_node_id"] = path_match.group(1)
                    if not target:
                        params["target_node_id"] = path_match.group(2)
                    print(f"  ✓ Fixed {qid}: {params['source_node_id']} -> {params['target_node_id']}")
                else:
                    # 尝试从 context 提取
                    context = q.get("context", "")
                    path_match2 = re.search(r'from\s+(\w+)\s+to\s+(\w+)', context, re.IGNORECASE)
                    if path_match2:
                        if not source:
                            params["source_node_id"] = path_match2.group(1)
                        if not target:
                            params["target_node_id"] = path_match2.group(2)
                        print(f"  ✓ Fixed {qid} from context: {params['source_node_id']} -> {params['target_node_id']}")
                    else:
                        print(f"  ⚠ {qid}: Could not determine path nodes")
        
        fixed.append(q)
    
    return fixed


def main():
    input_path = "src/abel_benchmark/references/benchmark_questions_v2_final.json"
    output_path = "src/abel_benchmark/references/benchmark_questions_v2_fixed.json"
    
    print("=" * 70)
    print("Fixing Empty Nodes in Benchmark")
    print("=" * 70)
    print()
    
    # 加载
    print(f"📂 Loading: {input_path}")
    data = load_benchmark(input_path)
    questions = data.get("questions", [])
    print(f"   Total: {len(questions)} questions")
    print()
    
    # 修复 predict
    print("🔧 Fixing predict nodes...")
    questions = fix_predict_nodes(questions)
    print()
    
    # 修复 path
    print("🔧 Fixing path nodes...")
    questions = fix_path_nodes(questions)
    print()
    
    # 更新元数据
    data["benchmark_version"] = "v2.2-cap-fixed-nodes"
    data["questions"] = questions
    
    # 保存
    save_benchmark(data, output_path)
    
    print("=" * 70)
    print("✅ Done!")
    print(f"   Output: {output_path}")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
