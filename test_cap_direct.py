#!/usr/bin/env python3
"""
Direct CAP API Test - 直接测试 CAP 端点

Based on CAP API Schema:
- POST /cap/v1/predict
- POST /cap/v1/explain
- POST /cap/v1/intervene
- POST /cap/v1/counterfactual
- POST /cap/v1/validate
- GET  /cap/v1/schema/primitives
- GET  /cap/v1/schema/variables
- GET  /cap/v1/schema/neighborhood
- GET  /cap/v1/schema/paths
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


class CAPDirectTester:
    """Test CAP primitives directly against CAP API endpoints."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results: List[CAPTestResult] = []
        
        # CAP API Endpoints (from schema)
        self.cap_endpoints = {
            "predict": "/cap/v1/predict",
            "explain": "/cap/v1/explain",
            "intervene": "/cap/v1/intervene",
            "counterfactual": "/cap/v1/counterfactual",
            "validate": "/cap/v1/validate",
            "schema_primitives": "/cap/v1/schema/primitives",
            "schema_variables": "/cap/v1/schema/variables",
            "schema_neighborhood": "/cap/v1/schema/neighborhood",
            "schema_paths": "/cap/v1/schema/paths",
        }
        
        # Expected fields for each primitive
        self.expected_fields = {
            "predict": ["prediction", "confidence", "factors"],
            "explain": ["explanation", "contributing_factors", "confidence"],
            "intervene": ["intervention_effect", "propagation", "affected_nodes"],
            "counterfactual": ["counterfactual_outcome", "probability", "path"],
            "validate": ["valid", "confidence", "reasoning"],
        }
    
    async def test_schema_primitives(self) -> Dict:
        """Test GET /cap/v1/schema/primitives"""
        url = f"{self.base_url}{self.cap_endpoints['schema_primitives']}"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def test_predict(self, question: Dict) -> CAPTestResult:
        """Test POST /cap/v1/predict"""
        question_id = question.get("id", "UNKNOWN")
        cap_input = question.get("cap_request", {}).get("input", {})
        
        endpoint = self.cap_endpoints["predict"]
        url = f"{self.base_url}{endpoint}"
        
        # Build request body
        payload = {
            "target": cap_input.get("target_node"),
            "horizon": cap_input.get("horizon_hours", 24),
            "features_limit": cap_input.get("features_limit", 5),
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Check required fields
            expected = self.expected_fields["predict"]
            present = [f for f in expected if f in data]
            missing = [f for f in expected if f not in data]
            
            return CAPTestResult(
                primitive="predict",
                question_id=question_id,
                success=len(missing) == 0,
                endpoint_called=endpoint,
                response_received=True,
                required_fields_present=present,
                required_fields_missing=missing,
                optional_fields_present=[],
                behavior_match=True,
                errors=[],
                raw_response=data
            )
        except Exception as e:
            return CAPTestResult(
                primitive="predict",
                question_id=question_id,
                success=False,
                endpoint_called=endpoint,
                response_received=False,
                required_fields_present=[],
                required_fields_missing=self.expected_fields["predict"],
                optional_fields_present=[],
                behavior_match=False,
                errors=[str(e)],
                raw_response=None
            )
    
    async def test_intervene(self, question: Dict) -> CAPTestResult:
        """Test POST /cap/v1/intervene"""
        question_id = question.get("id", "UNKNOWN")
        cap_input = question.get("cap_request", {}).get("input", {})
        
        endpoint = self.cap_endpoints["intervene"]
        url = f"{self.base_url}{endpoint}"
        
        # Build request body
        intervention = cap_input.get("intervention", {})
        payload = {
            "target": cap_input.get("target_node"),
            "intervention_node": intervention.get("node"),
            "delta": intervention.get("delta"),
            "horizon": cap_input.get("horizon_steps", 72),
            "max_hops": cap_input.get("max_hops", 3),
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            expected = self.expected_fields["intervene"]
            present = [f for f in expected if f in data]
            missing = [f for f in expected if f not in data]
            
            return CAPTestResult(
                primitive="intervene",
                question_id=question_id,
                success=len(missing) == 0,
                endpoint_called=endpoint,
                response_received=True,
                required_fields_present=present,
                required_fields_missing=missing,
                optional_fields_present=[],
                behavior_match=True,
                errors=[],
                raw_response=data
            )
        except Exception as e:
            return CAPTestResult(
                primitive="intervene",
                question_id=question_id,
                success=False,
                endpoint_called=endpoint,
                response_received=False,
                required_fields_present=[],
                required_fields_missing=self.expected_fields["intervene"],
                optional_fields_present=[],
                behavior_match=False,
                errors=[str(e)],
                raw_response=None
            )
    
    async def test_explain(self, question: Dict) -> CAPTestResult:
        """Test POST /cap/v1/explain"""
        question_id = question.get("id", "UNKNOWN")
        cap_input = question.get("cap_request", {}).get("input", {})
        
        endpoint = self.cap_endpoints["explain"]
        url = f"{self.base_url}{endpoint}"
        
        payload = {
            "target": cap_input.get("target_node"),
            "context": cap_input.get("context", {}),
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            expected = self.expected_fields["explain"]
            present = [f for f in expected if f in data]
            missing = [f for f in expected if f not in data]
            
            return CAPTestResult(
                primitive="explain",
                question_id=question_id,
                success=len(missing) == 0,
                endpoint_called=endpoint,
                response_received=True,
                required_fields_present=present,
                required_fields_missing=missing,
                optional_fields_present=[],
                behavior_match=True,
                errors=[],
                raw_response=data
            )
        except Exception as e:
            return CAPTestResult(
                primitive="explain",
                question_id=question_id,
                success=False,
                endpoint_called=endpoint,
                response_received=False,
                required_fields_present=[],
                required_fields_missing=self.expected_fields["explain"],
                optional_fields_present=[],
                behavior_match=False,
                errors=[str(e)],
                raw_response=None
            )
    
    async def test_all(self, questions: List[Dict]) -> List[CAPTestResult]:
        """Test all questions against CAP API."""
        print(f"\n{'='*70}")
        print("🧪 Direct CAP API Test")
        print(f"{'='*70}")
        print(f"Base URL: {self.base_url}")
        print(f"Total Questions: {len(questions)}")
        print(f"{'='*70}\n")
        
        # First test schema endpoint
        schema = await self.test_schema_primitives()
        print(f"📋 Schema primitives: {list(schema.keys()) if 'error' not in schema else 'ERROR'}")
        print()
        
        # Test by category
        for i, question in enumerate(questions, 1):
            primitive = question.get("cap_primitive", "predict")
            
            if primitive == "predict":
                result = await self.test_predict(question)
            elif primitive == "intervene":
                result = await self.test_intervene(question)
            elif primitive == "explain":
                result = await self.test_explain(question)
            else:
                # Skip unsupported primitives for now
                print(f"[{i}/{len(questions)}] ⏸️  {primitive:12s} | {question.get('id', 'UNKNOWN'):6s} | Not implemented yet")
                continue
            
            self.results.append(result)
            
            status = "✅" if result.success else "❌"
            print(f"[{i}/{len(questions)}] {status} {result.primitive:12s} | "
                  f"{result.question_id:6s} | {len(result.required_fields_present)}/{len(result.required_fields_present) + len(result.required_fields_missing)} fields")
            
            if result.errors:
                for error in result.errors[:2]:
                    print(f"      ⚠️  {error[:60]}")
        
        return self.results
    
    def generate_report(self, output_dir: str = "./cap_direct_test"):
        """Generate test report."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Calculate stats
        total = len(self.results)
        success = len([r for r in self.results if r.success])
        
        # Generate summary
        report = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "total_tests": total,
            "success_count": success,
            "success_rate": f"{success}/{total} ({success/total*100:.1f}%)",
            "results": [asdict(r) for r in self.results]
        }
        
        # Save JSON
        with open(output_path / "cap_direct_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save Markdown
        lines = [
            "# Direct CAP API Test Report",
            "",
            f"**Generated**: {report['timestamp']}",
            f"**Base URL**: {self.base_url}",
            f"**Total Tests**: {total}",
            "",
            f"## Summary",
            "",
            f"- **Success Rate**: {report['success_rate']}",
            "",
            "## Results",
            "",
            "| ID | Primitive | Success | Endpoint | Fields |",
            "|---|---|---|---|---|",
        ]
        
        for r in self.results:
            total_fields = len(r.required_fields_present) + len(r.required_fields_missing)
            fields_str = f"{len(r.required_fields_present)}/{total_fields}"
            status = "✅" if r.success else "❌"
            lines.append(f"| {r.question_id} | {r.primitive} | {status} | {r.endpoint_called} | {fields_str} |")
        
        with open(output_path / "cap_direct_report.md", "w") as f:
            f.write("\n".join(lines))
        
        print(f"\n✅ Report saved to: {output_path}")
        
        return report


async def main():
    parser = argparse.ArgumentParser(description="Direct CAP API Test")
    parser.add_argument("--base-url", default="https://abel-graph-computer-sit.abel.ai")
    parser.add_argument("--questions-file", default="src/abel_benchmark/references/benchmark_questions_v2_enhanced.json")
    parser.add_argument("--category", default="A", help="Category to test (A, B, C, etc. or 'all')")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of questions")
    parser.add_argument("--output-dir", default="./cap_direct_test")
    args = parser.parse_args()
    
    # Load questions
    with open(args.questions_file) as f:
        data = json.load(f)
    questions = data["questions"]
    
    # Filter by category
    if args.category != "all":
        questions = [q for q in questions if q.get("category") == args.category]
    
    # Filter by primitive (only test supported ones for now)
    supported_primitives = ["predict", "intervene", "explain"]
    questions = [q for q in questions if q.get("cap_primitive") in supported_primitives]
    
    # Limit
    if args.limit > 0:
        questions = questions[:args.limit]
    
    # Run tests
    tester = CAPDirectTester(args.base_url)
    try:
        await tester.test_all(questions)
        report = tester.generate_report(args.output_dir)
        
        print(f"\n{'='*70}")
        print(f"Direct CAP API Test Summary")
        print(f"{'='*70}")
        print(f"Total: {report['total_tests']}")
        print(f"Success: {report['success_count']}")
        print(f"Rate: {report['success_rate']}")
        print(f"{'='*70}")
    finally:
        await tester.client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
