#!/usr/bin/env python3
"""
给所有节点名称添加 _close 后缀
基于 CAP API 要求: target_node must be in '<ticker>_<field>' format
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


def add_close_suffix(node: str) -> str:
    """添加 _close 后缀（如果不存在）"""
    if not node:
        return node
    if node.endswith("_close"):
        return node
    if node.endswith("_rate"):
        return node
    if node.endswith("_volume"):
        return node
    return f"{node}_close"


def fix_predict_nodes(questions: list) -> list:
    """修复 predict 节点"""
    fixed = []
    
    for q in questions:
        if q.get("cap_primitive") == "predict":
            cap_request = q.get("cap_request", {})
            params = cap_request.get("params", {})
            
            if "target_node" in params:
                old_node = params["target_node"]
                params["target_node"] = add_close_suffix(old_node)
                if old_node != params["target_node"]:
                    print(f"  ✓ {q['id']}: {old_node} -> {params['target_node']}")
        
        fixed.append(q)
    
    return fixed


def fix_intervene_nodes(questions: list) -> list:
    """修复 intervene 节点"""
    fixed = []
    
    for q in questions:
        if q.get("cap_primitive") == "intervene":
            cap_request = q.get("cap_request", {})
            params = cap_request.get("params", {})
            
            # 修复 treatment_node
            if "treatment_node" in params:
                old = params["treatment_node"]
                params["treatment_node"] = add_close_suffix(old)
                if old != params["treatment_node"]:
                    print(f"  ✓ {q['id']} treatment: {old} -> {params['treatment_node']}")
            
            # 修复 outcome_node
            if "outcome_node" in params:
                old = params["outcome_node"]
                params["outcome_node"] = add_close_suffix(old)
                if old != params["outcome_node"]:
                    print(f"  ✓ {q['id']} outcome: {old} -> {params['outcome_node']}")
        
        fixed.append(q)
    
    return fixed


def fix_path_nodes(questions: list) -> list:
    """修复 path 节点"""
    fixed = []
    
    for q in questions:
        if q.get("cap_primitive") == "path":
            cap_request = q.get("cap_request", {})
            params = cap_request.get("params", {})
            
            # 修复 source_node_id
            if "source_node_id" in params:
                old = params["source_node_id"]
                params["source_node_id"] = add_close_suffix(old)
                if old != params["source_node_id"]:
                    print(f"  ✓ {q['id']} source: {old} -> {params['source_node_id']}")
            
            # 修复 target_node_id
            if "target_node_id" in params:
                old = params["target_node_id"]
                params["target_node_id"] = add_close_suffix(old)
                if old != params["target_node_id"]:
                    print(f"  ✓ {q['id']} target: {old} -> {params['target_node_id']}")
        
        fixed.append(q)
    
    return fixed


def fix_attest_nodes(questions: list) -> list:
    """修复 attest 节点（改为 predict）"""
    fixed = []
    
    for q in questions:
        if q.get("cap_primitive") == "attest":
            # 检查是否已转为 predict
            cap_request = q.get("cap_request", {})
            if cap_request.get("verb") == "observe.predict":
                params = cap_request.get("params", {})
                if "target_node" in params:
                    old = params["target_node"]
                    params["target_node"] = add_close_suffix(old)
                    if old != params["target_node"]:
                        print(f"  ✓ {q['id']} attest->predict: {old} -> {params['target_node']}")
        
        fixed.append(q)
    
    return fixed


def main():
    input_path = "src/abel_benchmark/references/benchmark_questions_v2_fixed.json"
    output_path = "src/abel_benchmark/references/benchmark_questions_v2_complete.json"
    
    print("=" * 70)
    print("Adding _close suffix to all nodes")
    print("=" * 70)
    print()
    
    # 加载
    print(f"📂 Loading: {input_path}")
    data = load_benchmark(input_path)
    questions = data.get("questions", [])
    print(f"   Total: {len(questions)} questions")
    print()
    
    # 修复各类节点
    print("🔧 Fixing predict nodes...")
    questions = fix_predict_nodes(questions)
    print()
    
    print("🔧 Fixing intervene nodes...")
    questions = fix_intervene_nodes(questions)
    print()
    
    print("🔧 Fixing path nodes...")
    questions = fix_path_nodes(questions)
    print()
    
    print("🔧 Fixing attest nodes...")
    questions = fix_attest_nodes(questions)
    print()
    
    # 更新元数据
    data["benchmark_version"] = "v2.3-cap-complete"
    data["cap_version"] = "0.2.2"
    data["release_date"] = "2026-03-20"
    data["description"] = (
        "Abel Causal Benchmark V2.3 - CAP v0.2.2 Complete. "
        "All nodes use '<ticker>_close' format as required by API."
    )
    data["notes"] = (
        "API requires target_node in '<ticker>_<field>' format. "
        "All nodes updated to use '_close' suffix."
    )
    data["questions"] = questions
    
    # 保存
    save_benchmark(data, output_path)
    
    print("=" * 70)
    print("✅ Done! All nodes updated with _close suffix")
    print(f"   Output: {output_path}")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
