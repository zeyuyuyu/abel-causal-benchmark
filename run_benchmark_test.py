#!/usr/bin/env python3
"""
Abel Causal Benchmark - 完整测试脚本
使用 benchmark_questions_v2_final.json 测试 CAP API
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

CAP_BASE_URL = "https://cap-sit.abel.ai"
TEST_TIMEOUT = 60.0
MAX_RETRIES = 3

# 颜色代码
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class CAPTester:
    def __init__(self):
        self.results = []
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "retryable": 0,
            "by_category": {},
            "by_verb": {}
        }
    
    def log(self, msg: str, level: str = "info"):
        """打印日志"""
        color = {"success": GREEN, "error": RED, "warning": YELLOW, "info": BLUE}.get(level, "")
        print(f"{color}{msg}{RESET}")
    
    async def call_cap_api(
        self,
        client: httpx.AsyncClient,
        verb: str,
        params: dict,
        request_id: str,
        timeout_ms: int = 30000
    ) -> dict:
        """调用 CAP API，带重试"""
        request_body = {
            "cap_version": "0.2.2",
            "request_id": request_id,
            "verb": verb,
            "params": params,
            "options": {"timeout_ms": timeout_ms}
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.post(
                    f"{CAP_BASE_URL}/api/v1/cap",
                    json=request_body,
                    timeout=TEST_TIMEOUT
                )
                
                # 503 错误 - 可重试
                if response.status_code == 503:
                    if attempt < MAX_RETRIES - 1:
                        wait_time = 2 ** attempt
                        self.log(f"  ⏳ 503 error, retrying in {wait_time}s... ({attempt+1}/{MAX_RETRIES})", "warning")
                        await asyncio.sleep(wait_time)
                        continue
                    return {
                        "success": False,
                        "retryable": True,
                        "status_code": 503,
                        "error": "Service unavailable after retries"
                    }
                
                # 其他 HTTP 错误
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                        # 记录详细错误
                        if "validation" in error_msg.lower():
                            print(f"      Validation error detail: {json.dumps(error_data, indent=2)[:200]}")
                    except:
                        error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                    
                    return {
                        "success": False,
                        "retryable": False,
                        "status_code": response.status_code,
                        "error": error_msg
                    }
                
                # 解析响应
                data = response.json()
                
                if data.get("status") == "success":
                    return {
                        "success": True,
                        "result": data.get("result", {}),
                        "provenance": data.get("provenance", {})
                    }
                else:
                    # API 返回错误
                    error_msg = data.get("error", {}).get("message", "Unknown error")
                    # 某些错误可重试
                    retryable = "max_events" not in error_msg and "not found" not in error_msg.lower()
                    return {
                        "success": False,
                        "retryable": retryable,
                        "status_code": 200,
                        "error": error_msg
                    }
                    
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    self.log(f"  ⏳ Exception: {str(e)[:50]}, retrying... ({attempt+1}/{MAX_RETRIES})", "warning")
                    await asyncio.sleep(wait_time)
                    continue
                return {
                    "success": False,
                    "retryable": True,
                    "error": str(e)
                }
        
        return {"success": False, "retryable": True, "error": "Max retries exceeded"}
    
    async def test_predict(self, client: httpx.AsyncClient, question: dict) -> dict:
        """测试 predict 问题"""
        qid = question.get("id", "unknown")
        cap_request = question.get("cap_request", {})
        
        params = cap_request.get("params", {})
        verb = cap_request.get("verb", "observe.predict")
        
        result = await self.call_cap_api(
            client, verb, params, f"test-{qid}"
        )
        
        if result["success"]:
            res = result["result"]
            prediction = res.get("prediction")
            drivers = res.get("drivers", [])
            self.log(f"  ✅ {qid}: prediction={prediction}, drivers={len(drivers)}", "success")
        else:
            error = result.get("error", "Unknown")[:60]
            self.log(f"  {'⚠️' if result.get('retryable') else '❌'} {qid}: {error}", 
                    "warning" if result.get('retryable') else "error")
        
        return {
            "question_id": qid,
            "verb": verb,
            **result
        }
    
    async def test_intervene(self, client: httpx.AsyncClient, question: dict) -> dict:
        """测试 intervene 问题"""
        qid = question.get("id", "unknown")
        cap_request = question.get("cap_request", {})
        
        params = cap_request.get("params", {})
        verb = cap_request.get("verb", "intervene.do")
        
        # 记录干预参数
        treatment = params.get("treatment_node", "")
        outcome = params.get("outcome_node", "")
        value = params.get("treatment_value", 0)
        
        result = await self.call_cap_api(
            client, verb, params, f"test-{qid}"
        )
        
        if result["success"]:
            res = result["result"]
            effect = res.get("effect")
            self.log(f"  ✅ {qid}: {treatment} -> {outcome}: effect={effect}", "success")
        else:
            error = result.get("error", "Unknown")[:60]
            self.log(f"  {'⚠️' if result.get('retryable') else '❌'} {qid}: {error}",
                    "warning" if result.get('retryable') else "error")
        
        return {
            "question_id": qid,
            "verb": verb,
            "treatment": treatment,
            "outcome": outcome,
            **result
        }
    
    async def test_path(self, client: httpx.AsyncClient, question: dict) -> dict:
        """测试 path 问题"""
        qid = question.get("id", "unknown")
        cap_request = question.get("cap_request", {})
        
        params = cap_request.get("params", {})
        verb = cap_request.get("verb", "graph.paths")
        
        source = params.get("source_node_id", "")
        target = params.get("target_node_id", "")
        
        result = await self.call_cap_api(
            client, verb, params, f"test-{qid}"
        )
        
        if result["success"]:
            res = result["result"]
            paths = res.get("paths", [])
            self.log(f"  ✅ {qid}: {source} -> {target}: {len(paths)} paths", "success")
        else:
            error = result.get("error", "Unknown")[:60]
            self.log(f"  {'⚠️' if result.get('retryable') else '❌'} {qid}: {error}",
                    "warning" if result.get('retryable') else "error")
        
        return {
            "question_id": qid,
            "verb": verb,
            "source": source,
            "target": target,
            **result
        }
    
    async def test_attest(self, client: httpx.AsyncClient, question: dict) -> dict:
        """测试 attest 问题 - 使用 predict + 客户端比较"""
        qid = question.get("id", "unknown")
        
        # 获取比较信息
        attest_info = question.get("_attest_comparison", {})
        primary_node = attest_info.get("primary_node", "")
        comparison_nodes = attest_info.get("comparison_nodes", [])
        
        if not primary_node:
            self.log(f"  ⚠️ {qid}: No attest comparison info", "warning")
            return {
                "question_id": qid,
                "verb": "attest",
                "success": False,
                "error": "No attest comparison info"
            }
        
        # 调用 primary node 的 predict
        result = await self.call_cap_api(
            client, "observe.predict", {"target_node": primary_node}, f"test-{qid}"
        )
        
        if result["success"]:
            res = result["result"]
            drivers = res.get("drivers", [])
            self.log(f"  ✅ {qid}: {primary_node} has {len(drivers)} drivers", "success")
        else:
            error = result.get("error", "Unknown")[:60]
            self.log(f"  {'⚠️' if result.get('retryable') else '❌'} {qid}: {error}",
                    "warning" if result.get('retryable') else "error")
        
        return {
            "question_id": qid,
            "verb": "attest",
            "primary_node": primary_node,
            **result
        }
    
    async def run_tests(self, benchmark_path: str):
        """运行完整的 benchmark 测试"""
        self.log("=" * 80, "info")
        self.log("Abel Causal Benchmark - Full CAP API Test", "info")
        self.log("=" * 80, "info")
        
        # 加载 benchmark
        self.log(f"\n📂 Loading benchmark: {benchmark_path}", "info")
        with open(benchmark_path) as f:
            benchmark = json.load(f)
        
        questions = benchmark.get("questions", [])
        self.log(f"   Total questions: {len(questions)}", "info")
        
        # 按类别分组
        by_category = {}
        for q in questions:
            cat = q.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(q)
        
        # 开始测试
        async with httpx.AsyncClient() as client:
            # 测试 meta.capabilities
            self.log("\n" + "=" * 80, "info")
            self.log("Testing meta.capabilities...", "info")
            self.log("=" * 80, "info")
            
            cap_result = await self.call_cap_api(
                client, "meta.capabilities", {}, "test-capabilities"
            )
            
            if cap_result["success"]:
                caps = cap_result["result"]
                self.log(f"✅ Server: {caps.get('name', 'Unknown')}", "success")
                self.log(f"   Core verbs: {caps.get('supported_verbs', {}).get('core', [])}", "info")
            else:
                self.log(f"❌ Failed to get capabilities: {cap_result.get('error')}", "error")
                return self.stats
            
            # 按类别测试
            for category in sorted(by_category.keys()):
                questions_in_cat = by_category[category]
                cat_name = benchmark.get("categories", {}).get(category, {}).get("name", category)
                
                self.log(f"\n{'=' * 80}", "info")
                self.log(f"Category {category}: {cat_name} ({len(questions_in_cat)} questions)", "info")
                self.log("=" * 80, "info")
                
                for question in questions_in_cat:
                    self.stats["total"] += 1
                    
                    # 记录类别统计
                    if category not in self.stats["by_category"]:
                        self.stats["by_category"][category] = {"total": 0, "success": 0}
                    self.stats["by_category"][category]["total"] += 1
                    
                    cap_primitive = question.get("cap_primitive", "")
                    
                    # 选择合适的测试方法
                    if cap_primitive == "predict":
                        result = await self.test_predict(client, question)
                    elif cap_primitive == "intervene":
                        result = await self.test_intervene(client, question)
                    elif cap_primitive == "path":
                        result = await self.test_path(client, question)
                    elif cap_primitive == "attest":
                        result = await self.test_attest(client, question)
                    else:
                        # 跳过未知类型
                        continue
                    
                    self.results.append(result)
                    
                    # 更新统计
                    verb = result.get("verb", "unknown")
                    if verb not in self.stats["by_verb"]:
                        self.stats["by_verb"][verb] = {"total": 0, "success": 0}
                    self.stats["by_verb"][verb]["total"] += 1
                    
                    if result["success"]:
                        self.stats["success"] += 1
                        self.stats["by_category"][category]["success"] += 1
                        self.stats["by_verb"][verb]["success"] += 1
                    else:
                        self.stats["failed"] += 1
                        if result.get("retryable"):
                            self.stats["retryable"] += 1
                    
                    # 小延迟避免过载
                    await asyncio.sleep(0.1)
        
        return self.stats
    
    def print_summary(self):
        """打印测试总结"""
        self.log("\n" + "=" * 80, "info")
        self.log("Test Summary", "info")
        self.log("=" * 80, "info")
        
        total = self.stats["total"]
        success = self.stats["success"]
        failed = self.stats["failed"]
        retryable = self.stats["retryable"]
        
        if total > 0:
            success_rate = (success / total) * 100
            self.log(f"\n📊 Overall: {success}/{total} passed ({success_rate:.1f}%)", 
                    "success" if success_rate > 50 else "warning" if success_rate > 20 else "error")
            self.log(f"   Failed: {failed} (retryable: {retryable})", "info")
        
        # 类别统计
        self.log("\n📋 By Category:", "info")
        for cat, stats in sorted(self.stats["by_category"].items()):
            cat_success = stats["success"]
            cat_total = stats["total"]
            cat_rate = (cat_success / cat_total * 100) if cat_total > 0 else 0
            color = "success" if cat_rate > 50 else "warning" if cat_rate > 20 else "error"
            self.log(f"   {cat}: {cat_success}/{cat_total} ({cat_rate:.1f}%)", color)
        
        # Verb 统计
        self.log("\n🔧 By Verb:", "info")
        for verb, stats in sorted(self.stats["by_verb"].items()):
            verb_success = stats["success"]
            verb_total = stats["total"]
            verb_rate = (verb_success / verb_total * 100) if verb_total > 0 else 0
            color = "success" if verb_rate > 50 else "warning" if verb_rate > 20 else "error"
            self.log(f"   {verb}: {verb_success}/{verb_total} ({verb_rate:.1f}%)", color)
        
        self.log("\n" + "=" * 80, "info")
    
    def save_results(self, output_path: str):
        """保存详细结果"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "cap_base_url": CAP_BASE_URL,
            "stats": self.stats,
            "detailed_results": self.results
        }
        
        Path(output_path).parent.mkdir(exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        self.log(f"\n📄 Detailed results saved to: {output_path}", "info")


async def main():
    benchmark_path = "src/abel_benchmark/references/benchmark_questions_v2_complete.json"
    output_path = f"test_results/benchmark_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    tester = CAPTester()
    
    try:
        await tester.run_tests(benchmark_path)
    except KeyboardInterrupt:
        tester.log("\n⚠️ Test interrupted by user", "warning")
    except Exception as e:
        tester.log(f"\n❌ Test error: {str(e)}", "error")
    
    tester.print_summary()
    tester.save_results(output_path)
    
    # 返回退出码
    success_rate = tester.stats["success"] / tester.stats["total"] if tester.stats["total"] > 0 else 0
    return 0 if success_rate > 0.3 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
