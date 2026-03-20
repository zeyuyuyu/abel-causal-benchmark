#!/usr/bin/env python3
"""
LLM + CAP 混合测试框架
测试 LLM 理解问题 + 调用 CAP API 的综合能力
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

import httpx

# CAP API 配置
CAP_BASE_URL = "https://cap-sit.abel.ai"

# LLM API 配置 - 使用环境变量
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class LLMCAPTester:
    """LLM + CAP 混合测试器"""
    
    def __init__(self):
        self.results = []
        self.cap_client = None
        
    async def __aenter__(self):
        self.cap_client = httpx.AsyncClient()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cap_client.aclose()
    
    async def call_llm(self, prompt: str, model: str = "gpt-4o") -> Dict[str, Any]:
        """调用 LLM API"""
        # 检查可用的 API
        if OPENAI_API_KEY:
            return await self._call_openai(prompt, model)
        elif ANTHROPIC_API_KEY:
            return await self._call_anthropic(prompt, model)
        else:
            # 如果没有 API key，返回模拟响应用于测试
            return self._mock_llm_response(prompt)
    
    async def _call_openai(self, prompt: str, model: str) -> Dict[str, Any]:
        """调用 OpenAI API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a financial prediction agent. You can use causal graph computation to predict market movements."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "content": data["choices"][0]["message"]["content"],
                        "model": model
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text[:100]}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _call_anthropic(self, prompt: str, model: str) -> Dict[str, Any]:
        """调用 Anthropic API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": ANTHROPIC_API_KEY,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-opus-20240229",
                        "max_tokens": 1024,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "content": data["content"][0]["text"],
                        "model": "claude-3-opus"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text[:100]}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _mock_llm_response(self, prompt: str) -> Dict[str, Any]:
        """模拟 LLM 响应（用于测试）"""
        # 简单模拟：根据 prompt 内容返回预设响应
        if "NVDA" in prompt or "Nvidia" in prompt:
            return {
                "success": True,
                "content": json.dumps({
                    "requires_cap": True,
                    "verb": "observe.predict",
                    "target_node": "NVDA_close",
                    "reasoning": "NVDA is in the causal graph, I should query its prediction",
                    "confidence": 0.8
                }),
                "model": "mock-llm"
            }
        elif "Tesla" in prompt or "TSLA" in prompt:
            return {
                "success": True,
                "content": json.dumps({
                    "requires_cap": True,
                    "verb": "observe.predict",
                    "target_node": "TSLA_close",
                    "reasoning": "TSLA is in the causal graph, I should query its prediction",
                    "confidence": 0.8
                }),
                "model": "mock-llm"
            }
        else:
            return {
                "success": True,
                "content": json.dumps({
                    "requires_cap": False,
                    "answer": "Based on general knowledge, this requires reasoning beyond market data",
                    "reasoning": "Question is not financial/market related",
                    "confidence": 0.5
                }),
                "model": "mock-llm"
            }
    
    async def call_cap(self, verb: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用 CAP API"""
        try:
            response = await self.cap_client.post(
                f"{CAP_BASE_URL}/api/v1/cap",
                json={
                    "cap_version": "0.2.2",
                    "request_id": f"test-{datetime.now().timestamp()}",
                    "verb": verb,
                    "params": params,
                    "options": {"timeout_ms": 30000}
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return {
                        "success": True,
                        "result": data.get("result", {}),
                        "provenance": data.get("provenance", {})
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("error", {}).get("message", "Unknown error")
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def build_llm_prompt(self, question: Dict[str, Any]) -> str:
        """构建 LLM 的 prompt"""
        q_text = question.get("question", "")
        context = question.get("context", "")
        
        prompt = f"""You are an AI agent that can use a Causal Graph Computer API to answer financial prediction questions.

Question: {q_text}
Context: {context}

Your task:
1. Determine if this question requires causal graph computation (CAP) or can be answered from general knowledge
2. If CAP is needed, decide which verb to use: observe.predict, graph.neighbors, graph.paths, or intervene.do
3. Identify the target ticker/node from the question

Available nodes in the causal graph: NVDA_close, TSLA_close, AAPL_close, ETHUSD_close, BTCUSD_close, SPY_close, etc.

Respond in JSON format:
{{
    "requires_cap": true/false,
    "verb": "observe.predict" (if applicable),
    "target_node": "TICKER_close" (if applicable),
    "treatment_node": "TICKER_close" (for intervene),
    "outcome_node": "TICKER_close" (for intervene),
    "answer": "Your direct answer if no CAP needed",
    "reasoning": "Why you chose this approach",
    "confidence": 0.0-1.0
}}

Your response:"""
        
        return prompt
    
    async def test_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """测试单个问题"""
        qid = question.get("id", "unknown")
        q_text = question.get("question", "")
        
        print(f"\n{'='*60}")
        print(f"Testing: {qid}")
        print(f"Q: {q_text[:70]}...")
        print(f"{'='*60}")
        
        # Step 1: LLM 决策
        prompt = self.build_llm_prompt(question)
        llm_response = await self.call_llm(prompt)
        
        if not llm_response.get("success"):
            print(f"  ❌ LLM failed: {llm_response.get('error')}")
            return {
                "question_id": qid,
                "approach": "llm_failed",
                "llm_error": llm_response.get("error"),
                "success": False
            }
        
        print(f"  ✅ LLM response received")
        
        # 解析 LLM 的 JSON 响应
        try:
            llm_decision = json.loads(llm_response.get("content", "{}"))
        except:
            # 如果 LLM 没有返回有效 JSON，尝试直接提取
            llm_decision = {"requires_cap": False, "answer": llm_response.get("content", "")}
        
        requires_cap = llm_decision.get("requires_cap", False)
        
        # Step 2: 根据 LLM 决策执行
        if requires_cap:
            verb = llm_decision.get("verb", "observe.predict")
            params = {}
            
            if "target_node" in llm_decision:
                params["target_node"] = llm_decision["target_node"]
            if "treatment_node" in llm_decision:
                params["treatment_node"] = llm_decision["treatment_node"]
            if "outcome_node" in llm_decision:
                params["outcome_node"] = llm_decision["outcome_node"]
            
            print(f"  🔧 Calling CAP: {verb} with {params}")
            
            cap_result = await self.call_cap(verb, params)
            
            if cap_result.get("success"):
                print(f"  ✅ CAP success: {cap_result.get('result', {})}")
                
                # Step 3: LLM 解释 CAP 结果
                explanation_prompt = f"""Based on the causal graph computation result:
{json.dumps(cap_result.get('result', {}), indent=2)}

Answer the original question: {q_text}

Provide your final answer and reasoning."""
                
                final_llm = await self.call_llm(explanation_prompt)
                
                return {
                    "question_id": qid,
                    "approach": "llm+cap",
                    "llm_decision": llm_decision,
                    "cap_result": cap_result,
                    "final_answer": final_llm.get("content", "") if final_llm.get("success") else "Failed to generate final answer",
                    "success": True
                }
            else:
                print(f"  ❌ CAP failed: {cap_result.get('error')}")
                return {
                    "question_id": qid,
                    "approach": "llm+cap",
                    "llm_decision": llm_decision,
                    "cap_error": cap_result.get("error"),
                    "success": False
                }
        else:
            # LLM 直接回答
            answer = llm_decision.get("answer", llm_response.get("content", ""))
            print(f"  📝 LLM direct answer: {answer[:100]}...")
            
            return {
                "question_id": qid,
                "approach": "llm_only",
                "llm_decision": llm_decision,
                "answer": answer,
                "success": True
            }
    
    async def run_benchmark(self, benchmark_path: str, max_questions: int = 10):
        """运行 benchmark 测试"""
        print(f"\n{'='*70}")
        print(f"LLM + CAP Hybrid Testing")
        print(f"{'='*70}")
        print(f"Benchmark: {benchmark_path}")
        print(f"Max questions: {max_questions}")
        print(f"LLM: {'OpenAI' if OPENAI_API_KEY else 'Anthropic' if ANTHROPIC_API_KEY else 'Mock (testing)'}")
        print(f"{'='*70}\n")
        
        # 加载 benchmark
        with open(benchmark_path) as f:
            benchmark = json.load(f)
        
        questions = benchmark.get("questions", [])[:max_questions]
        
        # 测试每个问题
        results = []
        for question in questions:
            result = await self.test_question(question)
            results.append(result)
            
            # 小延迟避免过载
            await asyncio.sleep(0.5)
        
        # 统计
        stats = self._calculate_stats(results)
        self._print_stats(stats)
        
        return results, stats
    
    def _calculate_stats(self, results: list) -> Dict[str, Any]:
        """计算统计"""
        stats = {
            "total": len(results),
            "llm_only": 0,
            "llm_cap": 0,
            "cap_failures": 0,
            "llm_failures": 0
        }
        
        for r in results:
            approach = r.get("approach", "")
            success = r.get("success", False)
            
            if approach == "llm_only" and success:
                stats["llm_only"] += 1
            elif approach == "llm+cap" and success:
                stats["llm_cap"] += 1
            elif approach == "llm+cap" and not success:
                stats["cap_failures"] += 1
            elif approach == "llm_failed":
                stats["llm_failures"] += 1
        
        return stats
    
    def _print_stats(self, stats: Dict[str, Any]):
        """打印统计"""
        print(f"\n{'='*70}")
        print("Test Results Summary")
        print(f"{'='*70}")
        print(f"Total questions: {stats['total']}")
        print(f"LLM only (success): {stats['llm_only']}")
        print(f"LLM + CAP (success): {stats['llm_cap']}")
        print(f"CAP failures: {stats['cap_failures']}")
        print(f"LLM failures: {stats['llm_failures']}")
        print(f"Success rate: {(stats['llm_only'] + stats['llm_cap']) / stats['total'] * 100:.1f}%")
        print(f"{'='*70}\n")


async def main():
    # 检查 API keys
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY:
        print("⚠️  Warning: No LLM API key found.")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        print("   Running in MOCK mode for testing...\n")
    
    benchmark_path = "src/abel_benchmark/references/benchmark_questions_v2_complete.json"
    
    async with LLMCAPTester() as tester:
        results, stats = await tester.run_benchmark(benchmark_path, max_questions=5)
    
    # 保存详细结果
    output = {
        "timestamp": datetime.now().isoformat(),
        "benchmark": benchmark_path,
        "llm_provider": "openai" if OPENAI_API_KEY else "anthropic" if ANTHROPIC_API_KEY else "mock",
        "stats": stats,
        "detailed_results": results
    }
    
    output_path = f"test_results/llm_cap_hybrid_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"📄 Detailed results saved to: {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
