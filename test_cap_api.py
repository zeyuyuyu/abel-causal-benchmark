#!/usr/bin/env python3
"""
CAP API Direct Test - 使用正确的 CAP API 格式

API Endpoint: POST https://cap-sit.abel.ai/api/v1/cap

格式:
{
  "verb": "<cap_verb>",
  "params": {
    // 具体参数
  }
}

注意参数名:
- target_node (不是 target) - 格式: <ticker>_close
- prediction (不是 cumulative_prediction)
- drivers (不是 features)
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

import httpx


@dataclass
class CAPTestResult:
    """Result from testing one CAP primitive."""
    primitive: str
    question_id: str
    success: bool
    endpoint_called: str
    response_received: bool
    required_fields_present: List[str]
    required_fields_missing: List[str]
    optional_fields_present: List[str]
    behavior_match: bool
    errors: List[str]
    raw_response: Optional[Dict]


class CAPAPITester:
    """Test CAP primitives directly against CAP API."""
    
    def __init__(self, base_url: str = "https://cap-sit.abel.ai"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results: List[CAPTestResult] = []
        
        # CAP API endpoint
        self.cap_endpoint = "/api/v1/cap"
        
        # Verb mapping from CAP spec
        self.verb_mapping = {
            "predict": "observe.predict",
            "intervene": "intervene.do",
            "path": "graph.paths",
            "explain": "observe.predict",  # explain uses predict with context
            "attest": "observe.predict",   # attest uses batch predict
            "discover": "graph.markov_blanket",
            "neighbors": "graph.neighbors",
        }
        
        # Expected fields in response
        self.expected_fields = {
            "observe.predict": ["prediction", "drivers"],
            "intervene.do": ["intervention_effect", "affected_nodes"],
            "graph.paths": ["paths", "distance"],
            "graph.neighbors": ["neighbors"],
            "graph.markov_blanket": ["parents", "children", "spouses"],
        }
    
    def _format_node(self, node: str) -> str:
        """Format node name to <ticker>_close format."""
        if not node:
            return "UNKNOWN_close"
        # Remove _close if already present to avoid double suffix
        base = node.replace("_close", "").replace("_price", "").replace("_rate", "")
        return f"{base}_close"
    
    def _build_cap_request(self, primitive: str, question: Dict) -> Dict:
        """Build CAP API request body."""
        cap_input = question.get("cap_request", {}).get("input", {})
        verb = self.verb_mapping.get(primitive, "observe.predict")
        
        params = {}
        
        if verb == "observe.predict":
            # predict: target_node, horizon
            target = cap_input.get("target_node", cap_input.get("ticker", "UNKNOWN"))
            params["target_node"] = self._format_node(target)
            params["horizon"] = cap_input.get("horizon_hours", 24)
            
        elif verb == "intervene.do":
            # intervene: treatment_node, treatment_value, outcome_node
            intervention = cap_input.get("intervention", {})
            target = cap_input.get("target_node", "UNKNOWN")
            
            params["treatment_node"] = self._format_node(intervention.get("node", target))
            params["treatment_value"] = intervention.get("delta", 0.0)
            params["outcome_node"] = self._format_node(target)
            params["horizon"] = cap_input.get("horizon_steps", 72)
            
        elif verb == "graph.paths":
            # path: source_node_id, target_node_id, max_depth
            source = cap_input.get("source_node", cap_input.get("from", "DXY"))
            target = cap_input.get("target_node", cap_input.get("to", "BTCUSD"))
            
            params["source_node_id"] = self._format_node(source)
            params["target_node_id"] = self._format_node(target)
            params["max_depth"] = cap_input.get("max_depth", 3)
            
        elif verb == "graph.neighbors":
            # neighbors: node_id, direction
            target = cap_input.get("target_node", "UNKNOWN")
            params["node_id"] = self._format_node(target)
            params["direction"] = cap_input.get("direction", "both")  # in, out, both
            
        elif verb == "graph.markov_blanket":
            # markov blanket: target_node
            target = cap_input.get("target_node", "UNKNOWN")
            params["target_node"] = self._format_node(target)
        
        return {
            "verb": verb,
            "params": params
        }
    
    async def test_primitive(self, primitive: str, question: Dict) -> CAPTestResult:
        """Test a single CAP primitive."""
        question_id = question.get("id", "UNKNOWN")
        
        # Build request
        request_body = self._build_cap_request(primitive, question)
        verb = request_body["verb"]
        
        url = f"{self.base_url}{self.cap_endpoint}"
        
        try:
            response = await self.client.post(
                url,
                json=request_body,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            # Check status
            if data.get("status") == "error":
                error_msg = data.get("error", {}).get("message", "Unknown error")
                return CAPTestResult(
                    primitive=primitive,
                    question_id=question_id,
                    success=False,
                    endpoint_called=self.cap_endpoint,
                    response_received=True,
                    required_fields_present=[],
                    required_fields_missing=self.expected_fields.get(verb, []),
                    optional_fields_present=[],
                    behavior_match=False,
                    errors=[error_msg],
                    raw_response=data
                )
            
            # Check required fields
            result = data.get("result", {})
            expected = self.expected_fields.get(verb, ["prediction"])
            present = [f for f in expected if f in result]
            missing = [f for f in expected if f not in result]
            
            return CAPTestResult(
                primitive=primitive,
                question_id=question_id,
                success=len(missing) == 0,
                endpoint_called=self.cap_endpoint,
                response_received=True,
                required_fields_present=present,
                required_fields_missing=missing,
                optional_fields_present=[],
                behavior_match=True,
                errors=[],
                raw_response=data
            )
            
        except httpx.HTTPStatusError as e:
            return CAPTestResult(
                primitive=primitive,
                question_id=question_id,
                success=False,
                endpoint_called=self.cap_endpoint,
                response_received=False,
                required_fields_present=[],
                required_fields_missing=self.expected_fields.get(verb, []),
                optional_fields_present=[],
                behavior_match=False,
                errors=[f"HTTP {e.response.status_code}: {e.response.text[:100]}"],
                raw_response=None
            )
        except Exception as e:
            return CAPTestResult(
                primitive=primitive,
                question_id=question_id,
                success=False,
                endpoint_called=self.cap_endpoint,
                response_received=False,
                required_fields_present=[],
                required_fields_missing=self.expected_fields.get(verb, []),
                optional_fields_present=[],
                behavior_match=False,
                errors=[str(e)],
                raw_response=None
            )
    
    async def test_all(self, questions: List[Dict]) -> List[CAPTestResult]:
        """Test all questions against CAP API."""
        print(f"\n{'='*70}")
        print("🧪 Direct CAP API Test - Correct Parameter Format")
        print(f"{'='*70}")
        print(f"Base URL: {self.base_url}")
        print(f"Total Questions: {len(questions)}")
        print(f"{'='*70}\n")
        
        for i, question in enumerate(questions, 1):
            primitive = question.get("cap_primitive", "predict")
            
            # Skip unsupported primitives
            if primitive not in self.verb_mapping:
                print(f"[{i}/{len(questions)}] ⏸️  {primitive:12s} | {question.get('id', 'UNKNOWN'):6s} | Not implemented")
                continue
            
            result = await self.test_primitive(primitive, question)
            self.results.append(result)
            
            status = "✅" if result.success else "❌"
            total_fields = len(result.required_fields_present) + len(result.required_fields_missing)
            fields_str = f"{len(result.required_fields_present)}/{total_fields}" if total_fields > 0 else "N/A"
            
            print(f"[{i}/{len(questions)}] {status} {result.primitive:12s} | "
                  f"{result.question_id:6s} | {fields_str} fields")
            
            if result.errors:
                for error in result.errors[:2]:
                    print(f"      ⚠️  {error[:80]}")
        
        return self.results
    
    def generate_report(self, output_dir: str = "./cap_api_test"):
        """Generate test report."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Calculate stats
        total = len(self.results)
        success = len([r for r in self.results if r.success])
        
        by_primitive = {}
        for r in self.results:
            p = r.primitive
            if p not in by_primitive:
                by_primitive[p] = {"total": 0, "success": 0}
            by_primitive[p]["total"] += 1
            if r.success:
                by_primitive[p]["success"] += 1
        
        # Generate summary
        report = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "cap_endpoint": self.cap_endpoint,
            "total_tests": total,
            "success_count": success,
            "success_rate": f"{success}/{total} ({success/total*100:.1f}%)" if total > 0 else "N/A",
            "by_primitive": by_primitive,
            "results": [asdict(r) for r in self.results]
        }
        
        # Save JSON
        with open(output_path / "cap_api_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save Markdown
        lines = [
            "# CAP API Test Report",
            "",
            f"**Generated**: {report['timestamp']}",
            f"**Base URL**: {report['base_url']}",
            f"**CAP Endpoint**: {report['cap_endpoint']}",
            f"**Total Tests**: {total}",
            "",
            f"## Summary",
            "",
            f"- **Success Rate**: {report['success_rate']}",
            "",
            "## By Primitive",
            "",
        ]
        
        for p, stats in by_primitive.items():
            pct = stats['success'] / stats['total'] * 100
            lines.append(f"- **{p}**: {stats['success']}/{stats['total']} ({pct:.1f}%)")
        
        lines.extend(["", "## Detailed Results", "", "| ID | Primitive | Success | Fields | Errors |", "|---|---|---|---|---|"])
        
        for r in self.results:
            total_fields = len(r.required_fields_present) + len(r.required_fields_missing)
            fields_str = f"{len(r.required_fields_present)}/{total_fields}" if total_fields > 0 else "N/A"
            status = "✅" if r.success else "❌"
            error_str = r.errors[0][:30] if r.errors else "-"
            lines.append(f"| {r.question_id} | {r.primitive} | {status} | {fields_str} | {error_str} |")
        
        with open(output_path / "cap_api_report.md", "w") as f:
            f.write("\n".join(lines))
        
        print(f"\n✅ Report saved to: {output_path}")
        return report
    
    async def close(self):
        await self.client.aclose()


async def main():
    parser = argparse.ArgumentParser(description="Direct CAP API Test")
    parser.add_argument("--base-url", default="https://cap-sit.abel.ai")
    parser.add_argument("--questions-file", default="src/abel_benchmark/references/benchmark_questions_v2_enhanced.json")
    parser.add_argument("--category", default="A", help="Category to test (A, B, C, etc. or 'all')")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of questions")
    parser.add_argument("--output-dir", default="./cap_api_test")
    args = parser.parse_args()
    
    # Load questions
    with open(args.questions_file) as f:
        data = json.load(f)
    questions = data["questions"]
    
    # Filter by category
    if args.category != "all":
        questions = [q for q in questions if q.get("category") == args.category]
    
    # Limit
    if args.limit > 0:
        questions = questions[:args.limit]
    
    # Run tests
    tester = CAPAPITester(args.base_url)
    try:
        await tester.test_all(questions)
        report = tester.generate_report(args.output_dir)
        
        print(f"\n{'='*70}")
        print(f"CAP API Test Summary")
        print(f"{'='*70}")
        print(f"Total: {report['total_tests']}")
        print(f"Success: {report['success_count']}")
        print(f"Rate: {report['success_rate']}")
        print(f"{'='*70}")
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
