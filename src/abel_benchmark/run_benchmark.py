#!/usr/bin/env python3
"""
FutureX Causal Prediction Benchmark Runner

Execute 20-30 FutureX-style prediction questions against Abel Graph Computer
and calculate Causal Emotional Value Scores (CEVS).

Usage:
    poetry run python run_benchmark.py \
        --base-url "https://abel-graph-computer-sit.abel.ai" \
        --questions-file "../references/benchmark_questions_v1.json" \
        --output-dir "./futurex_results/$(date +%Y%m%d_%H%M%S)"
"""

import argparse
import asyncio
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

import httpx


@dataclass
class BenchmarkQuestion:
    id: str
    category: str
    question: str
    api_endpoint: str
    params: Dict[str, Any]
    expected_causal_value: List[str]
    cevs_weight: float = 1.0
    hypothetical: bool = False
    multi_ticker: Optional[List[str]] = None


@dataclass
class CGExecutionResult:
    question_id: str
    success: bool
    endpoint: str
    response: Optional[Dict] = None
    error: Optional[str] = None
    causal_values_found: List[str] = None
    execution_time_ms: float = 0.0


@dataclass
class CEVSBreakdown:
    explainability: float  # 0-1: Can trace causal path?
    intervenability: float  # 0-1: Can answer what-if?
    confidence_calibration: float  # 0-1: Confidence matches accuracy
    accuracy: float  # 0-1: Directional correctness (if ground truth available)


@dataclass
class BenchmarkResult:
    question: BenchmarkQuestion
    cg_result: CGExecutionResult
    cevs: CEVSBreakdown
    cevs_total: float


class AbelGraphComputerClient:
    """HTTP client for Abel Graph Computer API."""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """Make GET request to CG API."""
        url = f"{self.base_url}{endpoint}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        await self.client.aclose()


class AbelCausalBenchmark:
    """Main benchmark orchestrator."""
    
    def __init__(self, base_url: str, questions: List[BenchmarkQuestion]):
        self.cg_client = AbelGraphComputerClient(base_url)
        self.questions = questions
        self.results: List[BenchmarkResult] = []
    
    async def run(self) -> List[BenchmarkResult]:
        """Execute all benchmark questions."""
        print(f"Running FutureX Benchmark with {len(self.questions)} questions...")
        print("=" * 60)
        
        for i, q in enumerate(self.questions, 1):
            print(f"\n[{i}/{len(self.questions)}] {q.id}: {q.question[:60]}...")
            
            # Execute against CG
            cg_result = await self.execute_cg(q)
            
            # Calculate CEVS
            cevs = self.calculate_cevs(cg_result, q)
            
            # Weighted total
            cevs_total = (
                cevs.explainability * 0.3 +
                cevs.intervenability * 0.25 +
                cevs.confidence_calibration * 0.25 +
                cevs.accuracy * 0.2
            ) * q.cevs_weight
            
            result = BenchmarkResult(
                question=q,
                cg_result=cg_result,
                cevs=cevs,
                cevs_total=cevs_total
            )
            self.results.append(result)
            
            print(f"    ✓ CG Success: {cg_result.success}")
            print(f"    ✓ CEVS: {cevs_total:.2f} (Explain: {cevs.explainability:.2f}, "
                  f"Intervene: {cevs.intervenability:.2f}, "
                  f"Confidence: {cevs.confidence_calibration:.2f}, "
                  f"Accuracy: {cevs.accuracy:.2f})")
        
        return self.results
    
    async def execute_cg(self, q: BenchmarkQuestion) -> CGExecutionResult:
        """Execute question against CG API."""
        import time
        start = time.time()
        
        try:
            # Handle comparison questions
            if "params_comparison" in q.__dict__ and q.params_comparison:
                responses = []
                for params in q.params_comparison:
                    endpoint = self._format_endpoint(q.api_endpoint, params)
                    resp = await self.cg_client.get(endpoint, params)
                    responses.append(resp)
                response = {"comparison_results": responses}
            else:
                # Standard single request
                endpoint = self._format_endpoint(q.api_endpoint, q.params)
                response = await self.cg_client.get(endpoint, q.params)
            
            execution_time = (time.time() - start) * 1000
            
            # Check for expected causal values
            causal_values_found = self._extract_causal_values(response, q.expected_causal_value)
            
            return CGExecutionResult(
                question_id=q.id,
                success=True,
                endpoint=q.api_endpoint,
                response=response,
                causal_values_found=causal_values_found,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start) * 1000
            return CGExecutionResult(
                question_id=q.id,
                success=False,
                endpoint=q.api_endpoint,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    def _format_endpoint(self, endpoint_template: str, params: Dict) -> str:
        """Format endpoint with path parameters."""
        endpoint = endpoint_template
        # Replace {ticker} with actual ticker
        if "{ticker}" in endpoint and "ticker" in params:
            endpoint = endpoint.replace("{ticker}", params["ticker"])
        return endpoint
    
    def _extract_causal_values(self, response: Dict, expected_paths: List[str]) -> List[str]:
        """Check which expected causal values are present in response."""
        found = []
        response_str = json.dumps(response)
        
        for path in expected_paths:
            # Simple check - could be enhanced with proper JSONPath
            key_parts = path.replace("[]", "").split(".")
            if self._check_path_exists(response, key_parts):
                found.append(path)
        
        return found
    
    def _check_path_exists(self, obj: Any, path_parts: List[str]) -> bool:
        """Check if path exists in nested dict/list."""
        current = obj
        for part in path_parts:
            if isinstance(current, dict):
                if part not in current:
                    return False
                current = current[part]
            elif isinstance(current, list) and current:
                # Check if path exists in first item of list
                if isinstance(current[0], dict) and part in current[0]:
                    current = current[0][part]
                else:
                    return False
            else:
                return False
        return True
    
    def calculate_cevs(self, cg_result: CGExecutionResult, q: BenchmarkQuestion) -> CEVSBreakdown:
        """Calculate Causal Emotional Value Score components."""
        
        if not cg_result.success:
            return CEVSBreakdown(0, 0, 0, 0)
        
        response = cg_result.response or {}
        
        # Explainability: Can we trace causal path?
        explainability = self._score_explainability(response, q)
        
        # Intervenability: Can we answer what-if?
        intervenability = self._score_intervenability(response, q)
        
        # Confidence calibration: Is there probability calibration?
        confidence_calibration = self._score_confidence(response, q)
        
        # Accuracy: Would need ground truth, placeholder for now
        accuracy = 0.5  # Neutral if no ground truth yet
        
        return CEVSBreakdown(
            explainability=explainability,
            intervenability=intervenability,
            confidence_calibration=confidence_calibration,
            accuracy=accuracy
        )
    
    def _score_explainability(self, response: Dict, q: BenchmarkQuestion) -> float:
        """Score based on presence of causal path information."""
        score = 0.0
        
        # Has features with impact attribution
        if "features" in response and isinstance(response["features"], list):
            for f in response["features"]:
                if "cumulative_impact" in f or "impact_percent" in f:
                    score += 0.3
                    break
        
        # Has parent/child path information
        if any(k in response for k in ["parents", "children", "path", "paths"]):
            score += 0.4
        
        # Has tau/temporal information
        if any(k in response for k in ["tau", "tau_value", "max_lookahead_hours"]):
            score += 0.3
        
        return min(score, 1.0)
    
    def _score_intervenability(self, response: Dict, q: BenchmarkQuestion) -> float:
        """Score based on intervention capabilities."""
        if q.category == "B":  # Intervention questions
            if "intervention_impact" in response or "propagation_path" in response:
                return 1.0
            return 0.0
        
        # For non-intervention questions, check if intervention API could theoretically apply
        return 0.5  # Moderate - could be extended
    
    def _score_confidence(self, response: Dict, q: BenchmarkQuestion) -> float:
        """Score based on confidence calibration."""
        score = 0.0
        
        # Has probability_up
        if "probability_up" in response:
            score += 0.4
        
        # Has prediction with magnitude
        if "prediction" in response or "cumulative_prediction" in response:
            score += 0.3
        
        # Has feature-level confidence
        if "features" in response:
            features = response["features"]
            if features and any("impact_percent" in f or "weight" in f for f in features):
                score += 0.3
        
        return min(score, 1.0)
    
    async def close(self):
        await self.cg_client.close()


class BenchmarkReporter:
    """Generate reports from benchmark results."""
    
    def __init__(self, results: List[BenchmarkResult], output_dir: Path):
        self.results = results
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self):
        """Generate all report formats."""
        self._generate_csv()
        self._generate_json()
        self._generate_markdown()
        print(f"\nReports saved to: {self.output_dir}")
    
    def _generate_csv(self):
        """Generate CSV report."""
        csv_path = self.output_dir / "benchmark_results.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'question_id', 'category', 'question', 'success',
                'cevs_total', 'explainability', 'intervenability',
                'confidence', 'accuracy', 'execution_time_ms'
            ])
            for r in self.results:
                writer.writerow([
                    r.question.id,
                    r.question.category,
                    r.question.question[:100],
                    r.cg_result.success,
                    round(r.cevs_total, 3),
                    round(r.cevs.explainability, 3),
                    round(r.cevs.intervenability, 3),
                    round(r.cevs.confidence_calibration, 3),
                    round(r.cevs.accuracy, 3),
                    round(r.cg_result.execution_time_ms, 1)
                ])
    
    def _generate_json(self):
        """Generate JSON report."""
        json_path = self.output_dir / "benchmark_results.json"
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(self.results),
            "successful_executions": sum(1 for r in self.results if r.cg_result.success),
            "average_cevs": sum(r.cevs_total for r in self.results) / len(self.results),
            "by_category": self._summarize_by_category(),
            "results": [
                {
                    "question": asdict(r.question),
                    "cg_result": {
                        **asdict(r.cg_result),
                        "response": None if not r.cg_result.success else "..."
                    },
                    "cevs": asdict(r.cevs),
                    "cevs_total": r.cevs_total
                }
                for r in self.results
            ]
        }
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    def _generate_markdown(self):
        """Generate Markdown report."""
        md_path = self.output_dir / "benchmark_report.md"
        with open(md_path, 'w') as f:
            f.write("# FutureX Causal Prediction Benchmark Report\n\n")
            f.write(f"**Timestamp**: {datetime.now().isoformat()}\n\n")
            f.write(f"**Total Questions**: {len(self.results)}\n\n")
            f.write(f"**Average CEVS**: {sum(r.cevs_total for r in self.results) / len(self.results):.3f}\n\n")
            
            f.write("## By Category\n\n")
            for cat, stats in self._summarize_by_category().items():
                f.write(f"### Category {cat}\n")
                f.write(f"- Count: {stats['count']}\n")
                f.write(f"- Avg CEVS: {stats['avg_cevs']:.3f}\n")
                f.write(f"- Success Rate: {stats['success_rate']:.1%}\n\n")
            
            f.write("## Detailed Results\n\n")
            f.write("| ID | Category | CEVS | Explain | Intervene | Confidence | Status |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for r in self.results:
                status = "✅" if r.cg_result.success else "❌"
                f.write(f"| {r.question.id} | {r.question.category} | "
                       f"{r.cevs_total:.2f} | {r.cevs.explainability:.2f} | "
                       f"{r.cevs.intervenability:.2f} | {r.cevs.confidence_calibration:.2f} | {status} |\n")
    
    def _summarize_by_category(self) -> Dict[str, Dict]:
        """Summarize results by category."""
        by_cat = {}
        for r in self.results:
            cat = r.question.category
            if cat not in by_cat:
                by_cat[cat] = {"count": 0, "cevs_sum": 0, "success_count": 0}
            by_cat[cat]["count"] += 1
            by_cat[cat]["cevs_sum"] += r.cevs_total
            if r.cg_result.success:
                by_cat[cat]["success_count"] += 1
        
        return {
            cat: {
                "count": stats["count"],
                "avg_cevs": stats["cevs_sum"] / stats["count"],
                "success_rate": stats["success_count"] / stats["count"]
            }
            for cat, stats in by_cat.items()
        }


def load_questions(file_path: Path) -> List[BenchmarkQuestion]:
    """Load questions from JSON file."""
    with open(file_path) as f:
        data = json.load(f)
    
    return [
        BenchmarkQuestion(
            id=q["id"],
            category=q["category"],
            question=q["question"],
            api_endpoint=q["api_endpoint"],
            params=q.get("params", {}),
            expected_causal_value=q.get("expected_causal_value", []),
            cevs_weight=q.get("cevs_weight", 1.0),
            hypothetical=q.get("hypothetical", False),
            multi_ticker=q.get("multi_ticker")
        )
        for q in data["questions"]
    ]


async def main():
    parser = argparse.ArgumentParser(description="FutureX Causal Prediction Benchmark")
    parser.add_argument("--base-url", default="https://abel-graph-computer-sit.abel.ai",
                       help="Abel Graph Computer base URL")
    parser.add_argument("--questions-file", required=True,
                       help="Path to benchmark questions JSON")
    parser.add_argument("--output-dir", default="./futurex_results",
                       help="Output directory for reports")
    parser.add_argument("--category", choices=["A", "B", "C", "D", "E"],
                       help="Run only specific category")
    
    args = parser.parse_args()
    
    # Load questions
    questions = load_questions(Path(args.questions_file))
    
    # Filter by category if specified
    if args.category:
        questions = [q for q in questions if q.category == args.category]
        print(f"Running only category {args.category}: {len(questions)} questions")
    
    # Run benchmark
    benchmark = AbelCausalBenchmark(args.base_url, questions)
    try:
        results = await benchmark.run()
        
        # Generate reports
        output_dir = Path(args.output_dir) / datetime.now().strftime("%Y%m%d_%H%M%S")
        reporter = BenchmarkReporter(results, output_dir)
        reporter.generate()
        
        # Final summary
        avg_cevs = sum(r.cevs_total for r in results) / len(results)
        success_rate = sum(1 for r in results if r.cg_result.success) / len(results)
        
        print("\n" + "=" * 60)
        print(f"BENCHMARK COMPLETE")
        print(f"Average CEVS: {avg_cevs:.3f}")
        print(f"Success Rate: {success_rate:.1%}")
        print(f"Reports: {output_dir}")
        
    finally:
        await benchmark.close()


if __name__ == "__main__":
    asyncio.run(main())
