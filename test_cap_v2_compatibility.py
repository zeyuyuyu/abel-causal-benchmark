#!/usr/bin/env python3
"""
测试 CAP v2 兼容的 benchmark 问题
基于 Abel CAP Reference 实现
"""

import asyncio
import json
import sys
from pathlib import Path

import httpx

CAP_BASE_URL = "https://cap-sit.abel.ai"


async def test_intervene_time_lag(client: httpx.AsyncClient, question: dict) -> dict:
    """测试 extensions.abel.intervene_time_lag"""
    cap_request = question.get("cap_request", {})
    
    request_body = {
        "cap_version": "0.2.2",
        "request_id": f"test-{question['id']}",
        "verb": "extensions.abel.intervene_time_lag",
        "params": cap_request.get("params", {}),
        "options": cap_request.get("options", {})
    }
    
    try:
        response = await client.post(
            f"{CAP_BASE_URL}/api/v1/cap",
            json=request_body,
            timeout=60.0
        )
        
        result = {
            "question_id": question["id"],
            "verb": "extensions.abel.intervene_time_lag",
            "status_code": response.status_code,
            "success": response.status_code == 200
        }
        
        if response.status_code == 200:
            data = response.json()
            result["response_status"] = data.get("status")
            
            if data.get("status") == "success":
                result_data = data.get("result", {})
                result["effect"] = result_data.get("outcome_summary", {}).get("final_cumulative_effect")
                result["first_arrive_step"] = result_data.get("outcome_summary", {}).get("first_arrive_step")
                print(f"  ✅ {question['id']}: effect={result.get('effect')}, arrive_step={result.get('first_arrive_step')}")
            else:
                result["error"] = data.get("error", {}).get("message", "Unknown error")
                print(f"  ⚠️  {question['id']}: {result['error']}")
        else:
            result["error"] = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                result["detail"] = error_data.get("error", {}).get("message", "")
                print(f"  ❌ {question['id']}: HTTP {response.status_code} - {result.get('detail', '')}")
            except:
                print(f"  ❌ {question['id']}: HTTP {response.status_code}")
        
        return result
        
    except Exception as e:
        print(f"  ❌ {question['id']}: Exception - {str(e)}")
        return {
            "question_id": question["id"],
            "verb": "extensions.abel.intervene_time_lag",
            "success": False,
            "error": str(e)
        }


async def test_predict(client: httpx.AsyncClient, question: dict) -> dict:
    """测试 observe.predict"""
    cap_request = question.get("cap_request", {})
    
    request_body = {
        "cap_version": "0.2.2",
        "request_id": f"test-{question['id']}",
        "verb": "observe.predict",
        "params": cap_request.get("params", {}),
        "options": cap_request.get("options", {})
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await client.post(
                f"{CAP_BASE_URL}/api/v1/cap",
                json=request_body,
                timeout=60.0
            )
            
            if response.status_code == 503 and attempt < max_retries - 1:
                print(f"  ⏳ {question['id']}: 503, retrying... ({attempt+1}/{max_retries})")
                await asyncio.sleep(2 ** attempt)  # 指数退避
                continue
            
            result = {
                "question_id": question["id"],
                "verb": "observe.predict",
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                result["response_status"] = data.get("status")
                
                if data.get("status") == "success":
                    result_data = data.get("result", {})
                    result["prediction"] = result_data.get("prediction")
                    result["drivers"] = result_data.get("drivers", [])
                    print(f"  ✅ {question['id']}: prediction={result.get('prediction')}, drivers={len(result.get('drivers', []))}")
                else:
                    result["error"] = data.get("error", {}).get("message", "Unknown error")
                    print(f"  ⚠️  {question['id']}: {result['error']}")
            else:
                result["error"] = f"HTTP {response.status_code}"
                print(f"  ❌ {question['id']}: HTTP {response.status_code}")
            
            return result
            
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            print(f"  ❌ {question['id']}: Exception - {str(e)}")
            return {
                "question_id": question["id"],
                "verb": "observe.predict",
                "success": False,
                "error": str(e)
            }


async def test_graph_paths(client: httpx.AsyncClient, question: dict) -> dict:
    """测试 graph.paths"""
    cap_request = question.get("cap_request", {})
    
    request_body = {
        "cap_version": "0.2.2",
        "request_id": f"test-{question['id']}",
        "verb": "graph.paths",
        "params": cap_request.get("params", {}),
        "options": cap_request.get("options", {})
    }
    
    try:
        response = await client.post(
            f"{CAP_BASE_URL}/api/v1/cap",
            json=request_body,
            timeout=60.0
        )
        
        result = {
            "question_id": question["id"],
            "verb": "graph.paths",
            "status_code": response.status_code,
            "success": response.status_code == 200
        }
        
        if response.status_code == 200:
            data = response.json()
            result["response_status"] = data.get("status")
            
            if data.get("status") == "success":
                result_data = data.get("result", {})
                result["paths"] = result_data.get("paths", [])
                print(f"  ✅ {question['id']}: paths={len(result.get('paths', []))}")
            else:
                result["error"] = data.get("error", {}).get("message", "Unknown error")
                print(f"  ⚠️  {question['id']}: {result['error']}")
        else:
            result["error"] = f"HTTP {response.status_code}"
            print(f"  ❌ {question['id']}: HTTP {response.status_code}")
        
        return result
        
    except Exception as e:
        print(f"  ❌ {question['id']}: Exception - {str(e)}")
        return {
            "question_id": question["id"],
            "verb": "graph.paths",
            "success": False,
            "error": str(e)
        }


async def run_benchmark_tests():
    """运行 benchmark 测试"""
    # 加载 benchmark
    benchmark_path = "src/abel_benchmark/references/benchmark_questions_v2_cap_compatible.json"
    with open(benchmark_path) as f:
        benchmark = json.load(f)
    
    questions = benchmark.get("questions", [])
    
    # 按类别分组
    categories = {}
    for q in questions:
        cat = q.get("category", "unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(q)
    
    results = {
        "total_questions": len(questions),
        "categories": {},
        "summary": {
            "success": 0,
            "failed": 0,
            "errors": []
        }
    }
    
    async with httpx.AsyncClient() as client:
        # 先测试 meta.capabilities
        print("\n" + "=" * 70)
        print("Testing meta.capabilities...")
        print("=" * 70)
        
        try:
            response = await client.post(
                f"{CAP_BASE_URL}/api/v1/cap",
                json={
                    "cap_version": "0.2.2",
                    "request_id": "test-capabilities",
                    "verb": "meta.capabilities",
                    "params": {}
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server capabilities: {data.get('result', {}).get('name', 'Unknown')}")
                supported = data.get('result', {}).get('supported_verbs', {})
                print(f"   Core verbs: {supported.get('core', [])}")
                print(f"   Extensions: {list(data.get('result', {}).get('extensions', {}).keys())}")
            else:
                print(f"❌ Failed to get capabilities: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to connect: {str(e)}")
            return results
        
        # 测试各类问题
        print("\n" + "=" * 70)
        print("Testing Intervene Questions (extensions.abel.intervene_time_lag)...")
        print("=" * 70)
        intervene_results = []
        for q in categories.get("B", []):
            result = await test_intervene_time_lag(client, q)
            intervene_results.append(result)
            if result["success"]:
                results["summary"]["success"] += 1
            else:
                results["summary"]["failed"] += 1
                results["summary"]["errors"].append(f"{q['id']}: {result.get('error', 'Unknown')}")
        results["categories"]["B_intervene"] = intervene_results
        
        print("\n" + "=" * 70)
        print("Testing Predict Questions (observe.predict)...")
        print("=" * 70)
        predict_results = []
        for q in categories.get("A", []):
            result = await test_predict(client, q)
            predict_results.append(result)
            if result["success"]:
                results["summary"]["success"] += 1
            else:
                results["summary"]["failed"] += 1
        results["categories"]["A_predict"] = predict_results
        
        # 测试 A 类别的其他 predict 问题
        for cat in ["E", "F", "X"]:
            if cat in categories:
                print(f"\n--- Category {cat} ---")
                cat_predicts = [q for q in categories[cat] if q.get("cap_request", {}).get("verb") == "observe.predict"]
                for q in cat_predicts[:2]:  # 每类只测前2个
                    result = await test_predict(client, q)
                    predict_results.append(result)
                    if result["success"]:
                        results["summary"]["success"] += 1
                    else:
                        results["summary"]["failed"] += 1
        
        print("\n" + "=" * 70)
        print("Testing Path Questions (graph.paths)...")
        print("=" * 70)
        path_results = []
        for q in categories.get("C", []):
            result = await test_graph_paths(client, q)
            path_results.append(result)
            if result["success"]:
                results["summary"]["success"] += 1
            else:
                results["summary"]["failed"] += 1
        results["categories"]["C_path"] = path_results
    
    return results


def print_summary(results: dict):
    """打印测试总结"""
    print("\n" + "=" * 70)
    print("CAP v2 Benchmark Test Summary")
    print("=" * 70)
    
    total = results["summary"]["success"] + results["summary"]["failed"]
    success = results["summary"]["success"]
    failed = results["summary"]["failed"]
    
    if total > 0:
        success_rate = (success / total) * 100
        print(f"\n📊 Results: {success}/{total} passed ({success_rate:.1f}%)")
    
    # 分类统计
    print("\n📋 Category Results:")
    for cat_name, cat_results in results["categories"].items():
        cat_success = sum(1 for r in cat_results if r["success"])
        cat_total = len(cat_results)
        cat_rate = (cat_success / cat_total * 100) if cat_total > 0 else 0
        print(f"   {cat_name}: {cat_success}/{cat_total} ({cat_rate:.1f}%)")
    
    # 错误详情
    if results["summary"]["errors"]:
        print("\n❌ Errors:")
        for error in results["summary"]["errors"][:10]:  # 只显示前10个
            print(f"   - {error}")
        if len(results["summary"]["errors"]) > 10:
            print(f"   ... and {len(results['summary']['errors']) - 10} more")
    
    print("\n" + "=" * 70)


async def main():
    print("=" * 70)
    print("Abel Causal Benchmark - CAP v2 Compatibility Test")
    print("=" * 70)
    
    results = await run_benchmark_tests()
    print_summary(results)
    
    # 保存详细结果
    output_path = "test_results/cap_v2_test_results.json"
    Path(output_path).parent.mkdir(exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Detailed results saved to: {output_path}")
    
    return 0 if results["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
