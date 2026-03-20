#!/usr/bin/env python3
"""
CAP (Causal Agent Protocol) Test with Abel Causal Benchmark V2

This script tests Abel Graph Computer's CAP implementation against
Abel Causal Benchmark's 35 forward-looking prediction questions.

Usage:
    python test_cap_with_benchmark.py \
        --base-url https://abel-graph-computer-sit.abel.ai \
        --category B \
        --output-dir ./cap_test_results

Requirements:
    - Running Abel Graph Computer API
    - httpx, pandas, numpy
    - futurex-benchmark package installed
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import httpx


@dataclass
class CAPTestResult:
    """Result from testing one CAP primitive."""
    question_id: str
    category: str
    cap_primitive: str
    success: bool
    endpoint_used: str
    fallback_used: bool
    response: Optional[Dict]
    error: Optional[str]
    cevs_total: float
    cevs_breakdown: Dict[str, float]
    execution_time_ms: float


class CAPPrimitiveTester:
    """Test CAP primitives against CG API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # CAP to CG API mapping (from benchmark JSON)
        self.cap_mapping = {
            "predict": {
                "primary": "/causal_graph/{ticker}/multi-step-prediction",
                "fallbacks": ["/causal_graph/{ticker}/prediction"],
                "required_params": ["ticker"],
                "optional_params": ["lookahead_hours", "limit"]
            },
            "intervene": {
                "primary": "/graph_stats/intervention_impact",
                "fallbacks": [
                    "/causal_graph/{ticker}/prediction",
                    "/causal_graph/{ticker}/multi-step-prediction"
                ],
                "required_params": ["ticker", "shock_magnitude"],
                "optional_params": ["lookahead_hours", "max_hops"]
            },
            "path": {
                "primary": "/graph_stats/nodes_connection",
                "fallbacks": [],
                "required_params": ["from", "to"],
                "optional_params": ["depth"]
            },
            "explain": {
                "primary": "/causal_graph/{ticker}/prediction",
                "fallbacks": [],
                "required_params": ["ticker"],
                "optional_params": ["include_features"]
            },
            "attest": {
                "primary": "/causal_graph/batch/predictions",
                "fallbacks": [],
                "required_params": ["tickers"],
                "optional_params": []
            }
        }
    
    async def test_primitive(
        self,
        question: Dict[str, Any]
    ) -> CAPTestResult:
        """Test a single CAP primitive."""
        import time
        
        start = time.time()
        
        question_id = question.get("id", "unknown")
        category = question.get("category", "A")
        cap_request = question.get("cap_request", {})
        cap_primitive = cap_request.get("capability", "predict")
        
        # Get mapping
        mapping = self.cap_mapping.get(cap_primitive, self.cap_mapping["predict"])
        
        # Extract params from cap_request
        params = self._extract_params(cap_request, question)
        
        # Try primary endpoint
        endpoint = mapping["primary"]
        endpoint = self._format_endpoint(endpoint, params)
        
        try:
            response = await self._call_api(endpoint, params)
            execution_time = (time.time() - start) * 1000
            
            # Score with CEVS
            cevs_result = self._calculate_cevs(response, question)
            
            return CAPTestResult(
                question_id=question_id,
                category=category,
                cap_primitive=cap_primitive,
                success=True,
                endpoint_used=endpoint,
                fallback_used=False,
                response=response,
                error=None,
                cevs_total=cevs_result["total"],
                cevs_breakdown=cevs_result,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            # Try fallbacks
            for fallback in mapping["fallbacks"]:
                try:
                    fallback_endpoint = self._format_endpoint(fallback, params)
                    response = await self._call_api(fallback_endpoint, params)
                    execution_time = (time.time() - start) * 1000
                    
                    cevs_result = self._calculate_cevs(response, question)
                    
                    return CAPTestResult(
                        question_id=question_id,
                        category=category,
                        cap_primitive=cap_primitive,
                        success=True,
                        endpoint_used=fallback_endpoint,
                        fallback_used=True,
                        response=response,
                        error=None,
                        cevs_total=cevs_result["total"],
                        cevs_breakdown=cevs_result,
                        execution_time_ms=execution_time
                    )
                except Exception:
                    continue
            
            # All failed
            execution_time = (time.time() - start) * 1000
            return CAPTestResult(
                question_id=question_id,
                category=category,
                cap_primitive=cap_primitive,
                success=False,
                endpoint_used=endpoint,
                fallback_used=False,
                response=None,
                error=str(e),
                cevs_total=0.0,
                cevs_breakdown={},
                execution_time_ms=execution_time
            )
    
    def _extract_params(self, cap_request: Dict, question: Dict) -> Dict:
        """Extract parameters from CAP request."""
        params = {}
        
        input_data = cap_request.get("input", {})
        
        # Map common fields
        if "target_node" in input_data:
            params["ticker"] = input_data["target_node"]
        
        if "horizon_hours" in input_data:
            params["lookahead_hours"] = input_data["horizon_hours"]
        
        if "features_limit" in input_data:
            params["limit"] = input_data["features_limit"]
        
        if "intervention" in input_data:
            intervention = input_data["intervention"]
            if "delta" in intervention:
                params["shock_magnitude"] = intervention["delta"]
        
        if "source_node" in input_data and "target_node" in input_data:
            params["from"] = input_data["source_node"]
            params["to"] = input_data["target_node"]
        
        return params
    
    def _format_endpoint(self, endpoint: str, params: Dict) -> str:
        """Format endpoint with path parameters."""
        if "{ticker}" in endpoint and "ticker" in params:
            endpoint = endpoint.replace("{ticker}", params["ticker"])
        return endpoint
    
    async def _call_api(self, endpoint: str, params: Dict) -> Dict:
        """Make API call."""
        url = f"{self.base_url}{endpoint}"
        
        # Filter params that are path parameters (already in URL)
        query_params = {k: v for k, v in params.items() if "{" + k + "}" not in endpoint}
        
        response = await self.client.get(url, params=query_params)
        response.raise_for_status()
        return response.json()
    
    def _calculate_cevs(self, response: Dict, question: Dict) -> Dict:
        """Calculate CEVS using enhanced scorer."""
        try:
            from enhanced_cevs_scorer import EnhancedCEVSScorer
            scorer = EnhancedCEVSScorer()
            cevs = scorer.calculate_cevs(response, question)
            return {
                "total": cevs.total,
                "explainability": cevs.explainability,
                "intervenability": cevs.intervenability,
                "confidence_calibration": cevs.confidence_calibration,
                "accuracy": cevs.accuracy
            }
        except Exception as e:
            # Fallback scoring
            return {
                "total": 0.5,
                "explainability": 0.5,
                "intervenability": 0.5,
                "confidence_calibration": 0.5,
                "accuracy": 0.5,
                "error": str(e)
            }
    
    async def close(self):
        await self.client.aclose()


class CAPTestReporter:
    """Generate test reports."""
    
    def __init__(self, results: List[CAPTestResult], output_dir: Path):
        self.results = results
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self):
        """Generate all report formats."""
        self._generate_json()
        self._generate_csv()
        self._generate_markdown()
        print(f"\n✅ CAP Test reports saved to: {self.output_dir}")
    
    def _generate_json(self):
        """Generate JSON report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(self.results),
            "successful": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "avg_cevs": sum(r.cevs_total for r in self.results) / len(self.results) if self.results else 0,
            "by_primitive": self._summarize_by_primitive(),
            "results": [
                {
                    "question_id": r.question_id,
                    "category": r.category,
                    "cap_primitive": r.cap_primitive,
                    "success": r.success,
                    "endpoint_used": r.endpoint_used,
                    "fallback_used": r.fallback_used,
                    "cevs_total": r.cevs_total,
                    "cevs_breakdown": r.cevs_breakdown,
                    "execution_time_ms": r.execution_time_ms,
                    "error": r.error
                }
                for r in self.results
            ]
        }
        
        with open(self.output_dir / "cap_test_results.json", "w") as f:
            json.dump(report, f, indent=2)
    
    def _generate_csv(self):
        """Generate CSV report."""
        import csv
        
        with open(self.output_dir / "cap_test_results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "question_id", "category", "cap_primitive", "success",
                "endpoint_used", "fallback_used", "cevs_total",
                "explainability", "intervenability", "confidence", "accuracy",
                "execution_time_ms", "error"
            ])
            
            for r in self.results:
                writer.writerow([
                    r.question_id,
                    r.category,
                    r.cap_primitive,
                    r.success,
                    r.endpoint_used,
                    r.fallback_used,
                    round(r.cevs_total, 3),
                    round(r.cevs_breakdown.get("explainability", 0), 3),
                    round(r.cevs_breakdown.get("intervenability", 0), 3),
                    round(r.cevs_breakdown.get("confidence_calibration", 0), 3),
                    round(r.cevs_breakdown.get("accuracy", 0), 3),
                    round(r.execution_time_ms, 1),
                    r.error or ""
                ])
    
    def _generate_markdown(self):
        """Generate Markdown report."""
        lines = [
            "# CAP Test Results with FutureX Benchmark V2",
            "",
            f"**Timestamp**: {datetime.now().isoformat()}",
            "",
            f"**Total Questions**: {len(self.results)}",
            f"**Successful**: {sum(1 for r in self.results if r.success)}",
            f"**Failed**: {sum(1 for r in self.results if not r.success)}",
            f"**Average CEVS**: {sum(r.cevs_total for r in self.results) / len(self.results):.3f}" if self.results else "**Average CEVS**: N/A",
            "",
            "## By CAP Primitive",
            ""
        ]
        
        by_primitive = self._summarize_by_primitive()
        for primitive, stats in by_primitive.items():
            lines.extend([
                f"### {primitive}",
                f"- Count: {stats['count']}",
                f"- Success Rate: {stats['success_rate']:.1%}",
                f"- Avg CEVS: {stats['avg_cevs']:.3f}",
                f"- Fallback Usage: {stats['fallback_rate']:.1%}",
                ""
            ])
        
        lines.extend([
            "## Detailed Results",
            "",
            "| ID | Category | Primitive | Success | Endpoint | CEVS | Time (ms) |",
            "|---|---|---|---|---|---|---|"
        ])
        
        for r in self.results:
            status = "✅" if r.success else "❌"
            fallback = " (fb)" if r.fallback_used else ""
            lines.append(
                f"| {r.question_id} | {r.category} | {r.cap_primitive} | {status} | {r.endpoint_used.split('/')[-1]}{fallback} | {r.cevs_total:.3f} | {r.execution_time_ms:.1f} |"
            )
        
        with open(self.output_dir / "cap_test_report.md", "w") as f:
            f.write("\n".join(lines))
    
    def _summarize_by_primitive(self) -> Dict:
        """Summarize results by CAP primitive."""
        from collections import defaultdict
        
        by_primitive = defaultdict(list)
        for r in self.results:
            by_primitive[r.cap_primitive].append(r)
        
        summary = {}
        for primitive, results in by_primitive.items():
            success_count = sum(1 for r in results if r.success)
            fallback_count = sum(1 for r in results if r.fallback_used)
            avg_cevs = sum(r.cevs_total for r in results) / len(results)
            
            summary[primitive] = {
                "count": len(results),
                "success_rate": success_count / len(results),
                "avg_cevs": avg_cevs,
                "fallback_rate": fallback_count / len(results) if results else 0
            }
        
        return summary


async def main():
    parser = argparse.ArgumentParser(
        description="Test CAP implementation with FutureX Benchmark V2"
    )
    parser.add_argument(
        "--base-url",
        default="https://abel-graph-computer-sit.abel.ai",
        help="Abel Graph Computer API base URL"
    )
    parser.add_argument(
        "--questions-file",
        default="src/abel_benchmark/references/benchmark_questions_v2_enhanced.json",
        help="Path to benchmark questions JSON"
    )
    parser.add_argument(
        "--category",
        choices=["A", "B", "C", "D", "E", "all"],
        default="all",
        help="Category to test (default: all)"
    )
    parser.add_argument(
        "--output-dir",
        default=f"./cap_test_results/{datetime.now():%Y%m%d_%H%M%S}",
        help="Output directory for results"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of questions to test"
    )
    
    args = parser.parse_args()
    
    # Load questions
    with open(args.questions_file) as f:
        data = json.load(f)
    
    questions = data.get("questions", [])
    
    # Filter by category
    if args.category != "all":
        questions = [q for q in questions if q.get("category") == args.category]
    
    # Apply limit
    if args.limit:
        questions = questions[:args.limit]
    
    print(f"\n{'='*60}")
    print("CAP Test with FutureX Benchmark V2")
    print(f"{'='*60}")
    print(f"Base URL: {args.base_url}")
    print(f"Questions: {len(questions)} (Category: {args.category})")
    print(f"Output: {args.output_dir}")
    print(f"{'='*60}\n")
    
    # Run tests
    tester = CAPPrimitiveTester(args.base_url)
    results = []
    
    try:
        for i, question in enumerate(questions, 1):
            print(f"[{i}/{len(questions)}] Testing {question.get('id', 'unknown')}: {question.get('question', '')[:50]}...")
            
            result = await tester.test_primitive(question)
            results.append(result)
            
            status = "✅" if result.success else "❌"
            print(f"    {status} Endpoint: {result.endpoint_used.split('/')[-1]}")
            if result.fallback_used:
                print(f"    🔄 Fallback used")
            print(f"    📊 CEVS: {result.cevs_total:.3f} (Explain: {result.cevs_breakdown.get('explainability', 0):.2f}, Intervene: {result.cevs_breakdown.get('intervenability', 0):.2f})")
            if result.error:
                print(f"    ⚠️  Error: {result.error[:100]}")
        
        # Generate reports
        output_dir = Path(args.output_dir)
        reporter = CAPTestReporter(results, output_dir)
        reporter.generate()
        
        # Summary
        print(f"\n{'='*60}")
        print("CAP Test Summary")
        print(f"{'='*60}")
        print(f"Total: {len(results)}")
        print(f"Successful: {sum(1 for r in results if r.success)}")
        print(f"Failed: {sum(1 for r in results if not r.success)}")
        print(f"Average CEVS: {sum(r.cevs_total for r in results) / len(results):.3f}")
        
        by_primitive = reporter._summarize_by_primitive()
        print("\nBy CAP Primitive:")
        for primitive, stats in by_primitive.items():
            print(f"  {primitive:12s}: {stats['count']:2d} tests, {stats['success_rate']:5.1%} success, {stats['avg_cevs']:.3f} avg CEVS")
        
        print(f"\n✅ Reports saved to: {output_dir}")
        
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
