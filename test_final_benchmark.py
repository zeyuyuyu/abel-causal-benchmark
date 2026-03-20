#!/usr/bin/env python3
"""
测试最终版本的 benchmark
针对已知有效的节点对
"""

import asyncio
import json
from pathlib import Path
import httpx

CAP_BASE_URL = "https://cap-sit.abel.ai"

# 测试通过率高的节点
HIGH_SUCCESS_NODES = ["NVDA", "ETHUSD", "PEAKUSD", "VIX", "BTCUSD"]

# 已知有效的干预对
VALID_INTERVENTIONS = [
    ("PEAKUSD", "NVDA", 0.05),
    ("VIX", "SPY", 0.1),
    ("BTCUSD", "MSTR", 0.03),
]


async def test_single_node(client: httpx.AsyncClient, node: str) -> dict:
    """测试单个节点的 predict"""
    try:
        response = await client.post(
            f"{CAP_BASE_URL}/api/v1/cap",
            json={
                "cap_version": "0.2.2",
                "request_id": f"test-{node}",
                "verb": "observe.predict",
                "params": {"target_node": node},
                "options": {"timeout_ms": 30000}
            },
            timeout=60.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                result = data.get("result", {})
                drivers = result.get("drivers", [])
                return {
                    "node": node,
                    "success": True,
                    "drivers": drivers,
                    "driver_count": len(drivers)
                }
        
        return {"node": node, "success": False, "status": response.status_code}
    except Exception as e:
        return {"node": node, "success": False, "error": str(e)}


async def test_intervention(client: httpx.AsyncClient, treatment: str, outcome: str, value: float) -> dict:
    """测试干预"""
    try:
        response = await client.post(
            f"{CAP_BASE_URL}/api/v1/cap",
            json={
                "cap_version": "0.2.2",
                "request_id": f"test-{treatment}-{outcome}",
                "verb": "intervene.do",
                "params": {
                    "treatment_node": treatment,
                    "treatment_value": value,
                    "outcome_node": outcome
                },
                "options": {"timeout_ms": 30000}
            },
            timeout=60.0
        )
        
        result = {
            "treatment": treatment,
            "outcome": outcome,
            "status_code": response.status_code
        }
        
        if response.status_code == 200:
            data = response.json()
            result["response_status"] = data.get("status")
            
            if data.get("status") == "success":
                res = data.get("result", {})
                result["success"] = True
                result["effect"] = res.get("effect")
                print(f"  ✅ {treatment} -> {outcome}: effect={result['effect']}")
            else:
                error = data.get("error", {}).get("message", "Unknown")
                result["error"] = error
                print(f"  ⚠️  {treatment} -> {outcome}: {error[:60]}...")
        else:
            result["success"] = False
            try:
                err = response.json()
                result["error"] = err.get("error", {}).get("message", f"HTTP {response.status_code}")
            except:
                result["error"] = f"HTTP {response.status_code}"
            print(f"  ❌ {treatment} -> {outcome}: {result['error'][:60]}...")
        
        return result
        
    except Exception as e:
        print(f"  ❌ {treatment} -> {outcome}: {str(e)[:60]}")
        return {
            "treatment": treatment,
            "outcome": outcome,
            "success": False,
            "error": str(e)
        }


async def test_paths(client: httpx.AsyncClient, source: str, target: str) -> dict:
    """测试路径查询"""
    try:
        response = await client.post(
            f"{CAP_BASE_URL}/api/v1/cap",
            json={
                "cap_version": "0.2.2",
                "request_id": f"test-path-{source}-{target}",
                "verb": "graph.paths",
                "params": {
                    "source_node_id": source,
                    "target_node_id": target,
                    "max_depth": 3,
                    "max_paths": 3
                },
                "options": {"timeout_ms": 30000}
            },
            timeout=60.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                paths = data.get("result", {}).get("paths", [])
                return {
                    "source": source,
                    "target": target,
                    "success": True,
                    "path_count": len(paths)
                }
        
        return {"source": source, "target": target, "success": False}
    except Exception as e:
        return {"source": source, "target": target, "success": False, "error": str(e)}


async def run_focused_tests():
    """运行聚焦测试 - 只测已知高成功率的场景"""
    print("=" * 70)
    print("Focused CAP Tests - High Success Rate Scenarios")
    print("=" * 70)
    
    results = {
        "predict": [],
        "intervene": [],
        "paths": []
    }
    
    async with httpx.AsyncClient() as client:
        # 1. 测试 Predict
        print("\n📝 Testing Predict (high success nodes)...")
        for node in HIGH_SUCCESS_NODES:
            result = await test_single_node(client, node)
            results["predict"].append(result)
            if result["success"]:
                print(f"  ✅ {node}: {result['driver_count']} drivers")
            else:
                print(f"  ❌ {node}: failed")
        
        # 2. 测试 Intervene
        print("\n🔧 Testing Interventions (valid pairs)...")
        for treatment, outcome, value in VALID_INTERVENTIONS:
            result = await test_intervention(client, treatment, outcome, value)
            results["intervene"].append(result)
        
        # 3. 测试 Paths
        print("\n🔗 Testing Paths...")
        path_pairs = [
            ("NVDA", "BTCUSD"),
            ("VIX", "SPY"),
            ("PEAKUSD", "NVDA"),
        ]
        for source, target in path_pairs:
            result = await test_paths(client, source, target)
            results["paths"].append(result)
            if result["success"]:
                print(f"  ✅ {source} -> {target}: {result['path_count']} paths")
            else:
                print(f"  ⚠️  {source} -> {target}: no paths")
    
    return results


def print_results(results: dict):
    """打印结果"""
    print("\n" + "=" * 70)
    print("Results Summary")
    print("=" * 70)
    
    # Predict
    predict_success = sum(1 for r in results["predict"] if r["success"])
    predict_total = len(results["predict"])
    print(f"\n📝 Predict: {predict_success}/{predict_total} ({predict_success/predict_total*100:.1f}%)")
    for r in results["predict"]:
        status = "✅" if r["success"] else "❌"
        drivers = r.get("driver_count", 0) if r["success"] else "N/A"
        print(f"   {status} {r['node']}: {drivers} drivers")
    
    # Intervene
    intervene_success = sum(1 for r in results["intervene"] if r.get("success"))
    intervene_total = len(results["intervene"])
    print(f"\n🔧 Intervene: {intervene_success}/{intervene_total} ({intervene_success/intervene_total*100:.1f}% if >0)")
    for r in results["intervene"]:
        if r.get("success"):
            print(f"   ✅ {r['treatment']} -> {r['outcome']}: effect={r.get('effect')}")
        else:
            error = r.get("error", "Unknown")[:50]
            print(f"   ❌ {r['treatment']} -> {r['outcome']}: {error}")
    
    # Paths
    path_success = sum(1 for r in results["paths"] if r["success"])
    path_total = len(results["paths"])
    print(f"\n🔗 Paths: {path_success}/{path_total} ({path_success/path_total*100:.1f}%)")
    for r in results["paths"]:
        status = "✅" if r["success"] else "⚠️"
        count = r.get("path_count", 0) if r["success"] else "N/A"
        print(f"   {status} {r['source']} -> {r['target']}: {count} paths")
    
    print("\n" + "=" * 70)


async def main():
    results = await run_focused_tests()
    print_results(results)
    
    # 保存结果
    output_path = "test_results/focused_test_results.json"
    Path(output_path).parent.mkdir(exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📄 Results saved to: {output_path}")
    
    return 0


if __name__ == "__main__":
    asyncio.run(main())
