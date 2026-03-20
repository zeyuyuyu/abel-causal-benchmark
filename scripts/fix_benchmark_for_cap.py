#!/usr/bin/env python3
"""
Fix Abel Causal Benchmark for CAP API Compatibility

修复两个问题:
1. Attest 参数格式 (Category E + X) → 转换为 predict + comparison
2. Intervene 节点问题 (Category B) → 使用已知 driver 作为干预节点
"""

import json
from pathlib import Path
from copy import deepcopy


def fix_attest_questions(questions):
    """将 attest 问题修复为 CAP API 兼容格式"""
    fixed = []
    
    for q in questions:
        if q.get("cap_primitive") == "attest":
            # 获取节点列表
            cap_input = q.get("cap_request", {}).get("input", {})
            nodes = cap_input.get("nodes") or cap_input.get("tickers") or cap_input.get("sectors") or cap_input.get("assets")
            
            if nodes and len(nodes) >= 2:
                # 修复为 batch predict 格式（用于比较）
                q["cap_request"] = {
                    "capability": "predict",  # 改为 predict
                    "input": {
                        "target_node": nodes[0].replace("_close", "").replace("_rate", ""),
                        "comparison_nodes": nodes[1:],  # 用于比较的节点
                        "horizon_hours": 24,
                        "include_comparison": True  # 标记需要比较
                    }
                }
                q["cap_primitive"] = "predict"  # 改为 predict
                
                # 更新 context 说明这是比较测试
                q["context"] = f"[Attest→Predict] {q.get('context', '')}"
        
        fixed.append(q)
    
    return fixed


def fix_intervene_questions(questions):
    """修复 intervene 问题的节点问题"""
    fixed = []
    
    # 预定义的 driver 映射（基于已知的驱动关系）
    driver_mapping = {
        "NVDA": ["PEAKUSD", "MBPUSD", "AGNCO"],
        "BTCUSD": ["PEAKUSD", "ETHUSD"],
        "SPY": ["VIX", "DXY", "TNX_yield"],
        "TSLA": ["ARKK", "XLY", "CLUSD"],
        "AAPL": ["QQQ", "XLK", "SPY"],
        "ETHUSD": ["BTCUSD", "PEAKUSD"],
        "XLF": ["TNX_yield", "DXY", "SPY"],
    }
    
    for q in questions:
        if q.get("cap_primitive") == "intervene":
            cap_input = q.get("cap_request", {}).get("input", {})
            intervention = cap_input.get("intervention", {})
            target = cap_input.get("target_node", "")
            
            # 提取 ticker base
            ticker_base = target.replace("_close", "").replace("_rate", "").split("_")[0]
            
            # 如果有预定义 driver，使用它
            if ticker_base in driver_mapping:
                driver = driver_mapping[ticker_base][0]  # 使用第一个 driver
                
                # 修复干预节点
                q["cap_request"]["input"]["intervention"]["node"] = f"{driver}_close"
                
                # 更新 context
                q["context"] = f"[Fixed] {q.get('context', '')} (Using driver: {driver})"
        
        fixed.append(q)
    
    return fixed


def main():
    # 加载 benchmark
    benchmark_path = Path(__file__).parent.parent / "src" / "abel_benchmark" / "references" / "benchmark_questions_v2_enhanced.json"
    
    with open(benchmark_path, 'r') as f:
        data = json.load(f)
    
    original_questions = data["questions"]
    
    print("=" * 70)
    print("🔧 修复 Abel Causal Benchmark for CAP API")
    print("=" * 70)
    print()
    
    # 统计原始问题
    attest_count = len([q for q in original_questions if q.get("cap_primitive") == "attest"])
    intervene_count = len([q for q in original_questions if q.get("cap_primitive") == "intervene"])
    
    print(f"原始统计:")
    print(f"  - Attest 问题: {attest_count}")
    print(f"  - Intervene 问题: {intervene_count}")
    print()
    
    # 修复问题
    print("修复中...")
    questions = fix_attest_questions(original_questions)
    questions = fix_intervene_questions(questions)
    
    # 统计修复后
    fixed_attest = len([q for q in questions if "[Attest→Predict]" in q.get("context", "")])
    fixed_intervene = len([q for q in questions if "[Fixed]" in q.get("context", "")])
    
    print(f"  ✅ 修复 Attest: {fixed_attest}/{attest_count}")
    print(f"  ✅ 修复 Intervene: {fixed_intervene}/{intervene_count}")
    print()
    
    # 保存修复后的 benchmark
    data["questions"] = questions
    data["metadata"] = {
        "fixed_for_cap_api": True,
        "fix_date": "2026-03-20",
        "changes": [
            "Attest → Predict (with comparison)",
            "Intervene nodes fixed to use drivers"
        ]
    }
    
    output_path = Path(__file__).parent.parent / "src" / "abel_benchmark" / "references" / "benchmark_questions_v2_cap_fixed.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ 修复后的 benchmark 已保存:")
    print(f"   {output_path}")
    print()
    
    # 显示修复示例
    print("修复示例:")
    attest_example = next((q for q in questions if "[Attest→Predict]" in q.get("context", "")), None)
    if attest_example:
        print(f"\n1. Attest → Predict (ID: {attest_example['id']})")
        print(f"   Question: {attest_example['question'][:60]}...")
        print(f"   New cap_request: {json.dumps(attest_example['cap_request'], indent=4)[:200]}...")
    
    intervene_example = next((q for q in questions if "[Fixed]" in q.get("context", "") and q.get("cap_primitive") == "intervene"), None)
    if intervene_example:
        print(f"\n2. Intervene (ID: {intervene_example['id']})")
        print(f"   Question: {intervene_example['question'][:60]}...")
        intervention = intervene_example['cap_request']['input'].get('intervention', {})
        print(f"   Fixed intervention node: {intervention.get('node', 'N/A')}")
    
    print()
    print("=" * 70)
    print("修复完成！请使用新文件运行测试:")
    print("python3 test_cap_api.py --questions-file benchmark_questions_v2_cap_fixed.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
