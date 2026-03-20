#!/usr/bin/env python3
"""
修复 Benchmark 问题以兼容 CAP API v2
基于 Abel CAP Reference 实现的研究成果

关键改进:
1. 将 intervene.do 改为 extensions.abel.intervene_time_lag
   - 支持自定义 horizon_steps (避免 event count 超限)
   - 使用更合理的默认值 (12-24)
2. 将 attest 改为 predict + 客户端比较模式
3. 更新所有参数格式以匹配标准 CAP 协议
"""

import json
import sys
from pathlib import Path


def load_benchmark(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def save_benchmark(data: dict, path: str):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {path}")


def fix_intervene_questions_v2(questions: list) -> list:
    """
    修复干预问题 - 使用 extensions.abel.intervene_time_lag
    这样可以使用自定义 horizon_steps 避免 event count 超限
    """
    fixed = []
    intervene_count = 0
    
    # 已知有有效干预关系的节点对
    # 基于参考实现中的 intervene_time_lag 示例
    valid_intervention_pairs = {
        # treatment_node -> 可能的 outcome_nodes (已知有效的短链路)
        "PEAKUSD": ["NVDA", "BTCUSD", "ETHUSD"],  # 峰值价格驱动
        "DXY": ["BTCUSD", "GLD", "SLV"],  # 美元指数
        "VIX": ["SPY", "QQQ"],  # 波动率
        "ETHUSD": ["SOLUSD", "AVAXUSD"],  # ETH 影响生态币
        "BTCUSD": ["MSTR", "COIN"],  # BTC 影响概念股
    }
    
    for q in questions:
        if q.get("cap_primitive") == "intervene":
            intervene_count += 1
            cap_input = q.get("cap_request", {}).get("input", {})
            
            # 获取当前参数
            target = cap_input.get("target_node", "")
            intervention = cap_input.get("intervention", {})
            treatment_node = intervention.get("node", "").replace("_close", "")
            delta = intervention.get("delta", 0.05)
            
            # 确定 horizon_steps (优先使用较小的值避免超限)
            # 参考实现中 intervene_time_lag 支持 1-168
            horizon_steps = min(cap_input.get("horizon_steps", 12), 12)  # 限制为 12
            
            # 验证节点对是否有效
            valid_pair = False
            if treatment_node in valid_intervention_pairs:
                if target in valid_intervention_pairs[treatment_node]:
                    valid_pair = True
                    print(f"  ✓ B{intervene_count}: Valid pair {treatment_node} -> {target}")
                else:
                    print(f"  ⚠ B{intervene_count}: Unverified pair {treatment_node} -> {target}")
            else:
                print(f"  ⚠ B{intervene_count}: Treatment {treatment_node} not in known drivers")
            
            # 更新为 extensions.abel.intervene_time_lag 格式
            # 这是 Abel 扩展，支持自定义 horizon_steps
            q["cap_request"] = {
                "verb": "extensions.abel.intervene_time_lag",
                "params": {
                    "treatment_node": f"{treatment_node}_close",
                    "treatment_value": float(delta),
                    "outcome_node": f"{target}_close",
                    "horizon_steps": horizon_steps,  # 可自定义！
                    "model": "linear"
                },
                "options": {
                    "timeout_ms": 30000
                }
            }
            
            # 标记更新
            q["context"] = f"[CAP-v2] {q.get('context', '')}"
            q["_v2_fixed"] = True
            q["_v2_change"] = "intervene.do → extensions.abel.intervene_time_lag"
            
        fixed.append(q)
    
    print(f"\n🔄 Fixed {intervene_count} intervene questions")
    return fixed


def fix_attest_questions_v2(questions: list) -> list:
    """
    修复 attest 问题 - 改为 predict + 客户端比较
    CAP 没有标准的 attest verb，需要用其他方式实现
    """
    fixed = []
    attest_count = 0
    converted_count = 0
    
    for q in questions:
        if q.get("cap_primitive") == "attest":
            attest_count += 1
            cap_input = q.get("cap_request", {}).get("input", {})
            
            # 获取节点列表
            nodes = cap_input.get("nodes") or cap_input.get("tickers") or []
            
            if nodes and len(nodes) >= 2:
                # 方案: 改为 predict 主节点，然后客户端比较
                primary_node = nodes[0]
                comparison_nodes = nodes[1:]
                
                q["cap_request"] = {
                    "verb": "observe.predict",
                    "params": {
                        "target_node": f"{primary_node}_close",
                    },
                    "options": {
                        "timeout_ms": 30000
                    }
                }
                
                # 存储比较信息供客户端使用
                q["_attest_comparison"] = {
                    "primary_node": primary_node,
                    "comparison_nodes": comparison_nodes,
                    "analysis_type": "driver_overlap",
                    "client_side_calculation": True
                }
                
                q["context"] = f"[Attest→Predict-v2] {q.get('context', '')}"
                q["_v2_fixed"] = True
                q["_v2_change"] = "attest → observe.predict + client comparison"
                converted_count += 1
                print(f"  ✓ Converted attest: {primary_node} vs {comparison_nodes}")
            else:
                print(f"  ⚠ Attest question {q.get('id')} has insufficient nodes: {nodes}")
        
        fixed.append(q)
    
    print(f"\n🔄 Fixed {converted_count}/{attest_count} attest questions")
    return fixed


def fix_predict_questions_v2(questions: list) -> list:
    """
    修复 predict 问题 - 使用标准 CAP 格式
    """
    fixed = []
    predict_count = 0
    
    for q in questions:
        if q.get("cap_primitive") == "predict":
            predict_count += 1
            cap_input = q.get("cap_request", {}).get("input", {})
            
            target = cap_input.get("target_node", "")
            
            # 更新为标准 CAP 格式
            q["cap_request"] = {
                "verb": "observe.predict",
                "params": {
                    "target_node": f"{target}_close" if not target.endswith("_close") else target,
                },
                "options": {
                    "timeout_ms": 30000
                }
            }
            
            q["_v2_fixed"] = True
            q["_v2_change"] = "standardized predict format"
        
        fixed.append(q)
    
    print(f"\n🔄 Standardized {predict_count} predict questions")
    return fixed


def fix_path_questions_v2(questions: list) -> list:
    """
    修复 path 问题 - 使用标准 CAP 格式
    """
    fixed = []
    path_count = 0
    
    for q in questions:
        if q.get("cap_primitive") == "path":
            path_count += 1
            cap_input = q.get("cap_request", {}).get("input", {})
            
            source = cap_input.get("source_node", "")
            target = cap_input.get("target_node", "")
            max_depth = cap_input.get("max_depth", 2)
            
            # 更新为标准 CAP graph.paths 格式
            q["cap_request"] = {
                "verb": "graph.paths",
                "params": {
                    "source_node_id": f"{source}_close" if not source.endswith("_close") else source,
                    "target_node_id": f"{target}_close" if not target.endswith("_close") else target,
                    "max_depth": max_depth,
                    "max_paths": 3
                },
                "options": {
                    "timeout_ms": 30000
                }
            }
            
            q["_v2_fixed"] = True
            q["_v2_change"] = "standardized path format"
        
        fixed.append(q)
    
    print(f"\n🔄 Standardized {path_count} path questions")
    return fixed


def update_benchmark_metadata(data: dict) -> dict:
    """
    更新 benchmark 元数据
    """
    data["benchmark_version"] = "v2.1-cap-compatible"
    data["cap_version"] = "0.2.2"
    data["release_date"] = "2026-03-20"
    data["description"] = "Abel Causal Benchmark V2.1 - CAP API v0.2.2 Compatible. Fixed intervene and attest questions based on reference implementation."
    
    # 更新支持的 primitives
    data["primitives_supported"] = [
        "observe.predict",
        "intervene.do",
        "extensions.abel.intervene_time_lag",  # 新增
        "graph.neighbors",
        "graph.markov_blanket",
        "graph.paths",
        "traverse.parents",
        "traverse.children",
        "extensions.abel.markov_blanket",
        "extensions.abel.validate_connectivity",
        "extensions.abel.counterfactual_preview"
    ]
    
    # 添加修复说明
    data["cap_compatibility_notes"] = {
        "intervene_fix": "Changed from intervene.do to extensions.abel.intervene_time_lag to support custom horizon_steps",
        "attest_fix": "Changed from attest to observe.predict with client-side comparison",
        "reasoning": "Based on Abel CAP Reference Implementation study (CAP_REFERENCE_LEARNING.md)"
    }
    
    return data


def generate_fix_report(questions: list) -> dict:
    """
    生成修复报告
    """
    report = {
        "total_questions": len(questions),
        "v2_fixed": 0,
        "changes": {}
    }
    
    for q in questions:
        if q.get("_v2_fixed"):
            report["v2_fixed"] += 1
            change = q.get("_v2_change", "unknown")
            report["changes"][change] = report["changes"].get(change, 0) + 1
    
    return report


def main():
    input_path = "src/abel_benchmark/references/benchmark_questions_v2_cap_fixed.json"
    output_path = "src/abel_benchmark/references/benchmark_questions_v2_cap_compatible.json"
    
    print("=" * 70)
    print("Abel Causal Benchmark - CAP v2 Compatibility Fix")
    print("=" * 70)
    print()
    
    # 加载 benchmark
    print(f"📂 Loading: {input_path}")
    data = load_benchmark(input_path)
    questions = data.get("questions", [])
    print(f"   Total questions: {len(questions)}")
    print()
    
    # 修复各类问题
    print("🔧 Fixing intervene questions...")
    questions = fix_intervene_questions_v2(questions)
    print()
    
    print("🔧 Fixing attest questions...")
    questions = fix_attest_questions_v2(questions)
    print()
    
    print("🔧 Fixing predict questions...")
    questions = fix_predict_questions_v2(questions)
    print()
    
    print("🔧 Fixing path questions...")
    questions = fix_path_questions_v2(questions)
    print()
    
    # 更新元数据
    print("📝 Updating metadata...")
    data = update_benchmark_metadata(data)
    data["questions"] = questions
    print()
    
    # 生成报告
    report = generate_fix_report(questions)
    print("📊 Fix Report:")
    print(f"   Total: {report['total_questions']}")
    print(f"   V2 Fixed: {report['v2_fixed']}")
    print("   Changes:")
    for change, count in report["changes"].items():
        print(f"     - {change}: {count}")
    print()
    
    # 保存
    save_benchmark(data, output_path)
    
    print("=" * 70)
    print("✅ Done! Benchmark fixed for CAP v2 compatibility")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
