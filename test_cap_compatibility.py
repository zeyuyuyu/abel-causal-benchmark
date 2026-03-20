#!/usr/bin/env python3
"""
CAP (Causal Agent Protocol) Compatibility Test

Tests how well Abel Graph Computer implements CAP primitives:
- predict: Markov blanket inference
- intervene: do-calculus propagation
- explain: Feature attribution
- path: Causal chain tracing
- attest: Cross-sectional comparison

Uses Abel Causal Benchmark V2 questions as test cases.

Usage:
    # Test all CAP primitives
    python test_cap_compatibility.py --base-url https://abel-graph-computer-sit.abel.ai
    
    # Test specific primitive
    python test_cap_compatibility.py --primitive intervene --category B
    
    # Test with dry-run (no API calls)
    python test_cap_compatibility.py --dry-run
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

import httpx


@dataclass
class CAPPrimitiveTest:
    """Definition of a CAP primitive test."""
    primitive: str  # predict, intervene, explain, path, attest
    question_id: str
    category: str
    description: str
    required_fields: List[str]  # Fields that must be in response
    optional_fields: List[str]   # Fields that should be in response for full score
    api_endpoint: str
    api_params: Dict[str, Any]
    expected_behavior: str


@dataclass
class CAPTestResult:
    """Result of testing one CAP primitive."""
    primitive: str
    question_id: str
    success: bool
    endpoint_called: str
    response_received: bool
    required_fields_present: List[str]
    required_fields_missing: List[str]
    optional_fields_present: List[str]
    behavior_match: bool  # Did API behave as expected for this primitive?
    errors: List[str]
    raw_response: Optional[Dict]


class CAPCompatibilityTester:
    """Test CAP primitive compatibility against CG API."""
    
    def __init__(self, base_url: str, dry_run: bool = False):
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.dry_run = dry_run
        self.client = None if dry_run else httpx.AsyncClient(timeout=30.0)
        self.results: List[CAPTestResult] = []
        
        # CAP Primitive Definitions
        self.primitive_specs = {
            "predict": {
                "description": "Markov blanket inference for next-step prediction",
                "required_fields": ["cumulative_prediction", "probability_up"],
                "optional_fields": ["features", "parents", "tau", "confidence"],
                "primary_endpoint": "/causal_graph/{ticker}/multi-step-prediction",
            },
            "intervene": {
                "description": "Do-calculus intervention impact simulation",
                "required_fields": ["intervention_effect", "propagation"],
                "optional_fields": ["shock_magnitude", "affected_nodes", "second_order_effects"],
                "primary_endpoint": "/graph_stats/intervention_impact",
            },
            "explain": {
                "description": "Feature attribution and minimal explanation set",
                "required_fields": ["explanation", "feature_importance"],
                "optional_fields": ["contributing_nodes", "path", "mechanism"],
                "primary_endpoint": "/causal_graph/{ticker}/prediction",
            },
            "path": {
                "description": "Causal path discovery and tracing",
                "required_fields": ["path", "hops", "tau"],
                "optional_fields": ["intermediate_nodes", "alternative_paths", "path_strength"],
                "primary_endpoint": "/graph_stats/nodes_connection",
            },
            "attest": {
                "description": "Cross-sectional causal claim verification",
                "required_fields": ["comparison", "ranking"],
                "optional_fields": ["confidence_scores", "evidence", "disagreement_flags"],
                "primary_endpoint": "/causal_graph/multi-step-prediction/batch",
            },
        }
    
    async def test_all_primitives(self, questions: List[Dict]) -> List[CAPTestResult]:
        """Test all CAP primitives against provided questions."""
        print(f"\n{'='*70}")
        print("CAP Compatibility Test - FutureX Benchmark V2")
        print(f"{'='*70}")
        print(f"Base URL: {self.base_url or 'DRY RUN'}")
        print(f"Total Questions: {len(questions)}")
        print(f"{'='*70}\n")
        
        for i, question in enumerate(questions, 1):
            result = await self._test_question(question)
            self.results.append(result)
            
            # Print progress
            status = "✅" if result.success else "❌"
            print(f"[{i}/{len(questions)}] {status} {result.primitive:12s} | "
                  f"{result.question_id:6s} | {len(result.required_fields_present)}/{len(result.required_fields_present) + len(result.required_fields_missing)} required fields")
            
            if result.errors:
                for error in result.errors[:2]:  # Show first 2 errors
                    print(f"    ⚠️  {error[:80]}")
        
        return self.results
    
    async def _test_question(self, question: Dict) -> CAPTestResult:
        """Test a single question's CAP primitive."""
        cap_request = question.get("cap_request", {})
        primitive = cap_request.get("capability", "predict")
        
        # Get spec
        spec = self.primitive_specs.get(primitive, self.primitive_specs["predict"])
        
        # Build API call
        endpoint = self._build_endpoint(primitive, question)
        params = self._build_params(primitive, question)
        
        if self.dry_run:
            # Dry run - simulate response
            return CAPTestResult(
                primitive=primitive,
                question_id=question.get("id", "unknown"),
                success=True,
                endpoint_called=endpoint,
                response_received=True,
                required_fields_present=spec["required_fields"],
                required_fields_missing=[],
                optional_fields_present=spec["optional_fields"],
                behavior_match=True,
                errors=[],
                raw_response={"dry_run": True, "primitive": primitive}
            )
        
        # Real API call
        try:
            response = await self._call_api(endpoint, params)
            
            # Check fields
            required_present = [f for f in spec["required_fields"] if self._field_exists(response, f)]
            required_missing = [f for f in spec["required_fields"] if not self._field_exists(response, f)]
            optional_present = [f for f in spec["optional_fields"] if self._field_exists(response, f)]
            
            # Check behavior
            behavior_match = self._check_behavior(primitive, response, question)
            
            return CAPTestResult(
                primitive=primitive,
                question_id=question.get("id", "unknown"),
                success=len(required_missing) == 0,
                endpoint_called=endpoint,
                response_received=True,
                required_fields_present=required_present,
                required_fields_missing=required_missing,
                optional_fields_present=optional_present,
                behavior_match=behavior_match,
                errors=[],
                raw_response=response if len(str(response)) < 10000 else {"truncated": True}
            )
            
        except Exception as e:
            return CAPTestResult(
                primitive=primitive,
                question_id=question.get("id", "unknown"),
                success=False,
                endpoint_called=endpoint,
                response_received=False,
                required_fields_present=[],
                required_fields_missing=spec["required_fields"],
                optional_fields_present=[],
                behavior_match=False,
                errors=[str(e)],
                raw_response=None
            )
    
    def _build_endpoint(self, primitive: str, question: Dict) -> str:
        """Build API endpoint for primitive."""
        spec = self.primitive_specs.get(primitive, self.primitive_specs["predict"])
        endpoint = spec["primary_endpoint"]
        
        # Format with ticker if needed
        cap_input = question.get("cap_request", {}).get("input", {})
        if "{ticker}" in endpoint:
            ticker = cap_input.get("target_node", "UNKNOWN")
            endpoint = endpoint.replace("{ticker}", ticker)
        
        return endpoint
    
    def _build_params(self, primitive: str, question: Dict) -> Dict:
        """Build API parameters for primitive."""
        cap_input = question.get("cap_request", {}).get("input", {})
        params = {}
        
        # Map common fields
        field_mapping = {
            "target_node": "ticker",
            "source_node": "from",
            "target_node_alt": "to",
            "horizon_hours": "lookahead_hours",
            "features_limit": "limit",
        }
        
        for cap_field, api_field in field_mapping.items():
            if cap_field in cap_input:
                params[api_field] = cap_input[cap_field]
        
        # Handle intervention specially
        if primitive == "intervene" and "intervention" in cap_input:
            intervention = cap_input["intervention"]
            if "delta" in intervention:
                params["shock_magnitude"] = intervention["delta"]
        
        return params
    
    async def _call_api(self, endpoint: str, params: Dict) -> Dict:
        """Make actual API call."""
        if not self.client:
            raise RuntimeError("HTTP client not initialized")
        
        url = f"{self.base_url}{endpoint}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def _field_exists(self, response: Dict, field: str) -> bool:
        """Check if field exists in response."""
        # Handle nested fields
        parts = field.split(".")
        current = response
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        
        return True
    
    def _check_behavior(self, primitive: str, response: Dict, question: Dict) -> bool:
        """Check if API behavior matches CAP primitive specification."""
        if primitive == "predict":
            # Should return prediction with probability
            return "prediction" in response or "cumulative_prediction" in response
        
        elif primitive == "intervene":
            # Should acknowledge intervention and show propagation
            has_intervention = "intervention" in str(response).lower() or "shock" in str(response).lower()
            has_propagation = "propagation" in str(response).lower() or "path" in str(response).lower()
            return has_intervention or has_propagation
        
        elif primitive == "explain":
            # Should return explanation structure
            return "explanation" in str(response).lower() or "features" in response
        
        elif primitive == "path":
            # Should return path information
            return "path" in response or "nodes" in str(response)
        
        elif primitive == "attest":
            # Should return comparison
            return "comparison" in str(response).lower() or len(response) > 1
        
        return True
    
    def generate_report(self, output_dir: Path):
        """Generate comprehensive CAP compatibility report."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "dry_run": self.dry_run,
            "total_tests": len(self.results),
            "by_primitive": self._summarize_by_primitive(),
            "results": [asdict(r) for r in self.results]
        }
        
        with open(output_dir / "cap_compatibility_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        # Markdown report
        self._generate_markdown_report(output_dir)
        
        print(f"\n✅ CAP compatibility report saved to: {output_dir}")
    
    def _summarize_by_primitive(self) -> Dict:
        """Summarize results by primitive."""
        from collections import defaultdict
        
        by_primitive = defaultdict(lambda: {
            "total": 0,
            "success": 0,
            "behavior_match": 0,
            "required_fields_avg": 0.0,
            "optional_fields_avg": 0.0
        })
        
        for r in self.results:
            p = r.primitive
            by_primitive[p]["total"] += 1
            if r.success:
                by_primitive[p]["success"] += 1
            if r.behavior_match:
                by_primitive[p]["behavior_match"] += 1
            
            total_required = len(r.required_fields_present) + len(r.required_fields_missing)
            if total_required > 0:
                by_primitive[p]["required_fields_avg"] += len(r.required_fields_present) / total_required
            
            by_primitive[p]["optional_fields_avg"] += len(r.optional_fields_present)
        
        # Normalize averages
        for p in by_primitive:
            count = by_primitive[p]["total"]
            if count > 0:
                by_primitive[p]["required_fields_avg"] /= count
                by_primitive[p]["optional_fields_avg"] /= count
        
        return dict(by_primitive)
    
    def _generate_markdown_report(self, output_dir: Path):
        """Generate Markdown report."""
        summary = self._summarize_by_primitive()
        
        lines = [
            "# CAP (Causal Agent Protocol) Compatibility Report",
            "",
            f"**Generated**: {datetime.now().isoformat()}",
            f"**Base URL**: {self.base_url or 'DRY RUN'}",
            f"**Total Tests**: {len(self.results)}",
            "",
            "## Executive Summary",
            "",
        ]
        
        # Overall stats
        total_success = sum(1 for r in self.results if r.success)
        total_behavior = sum(1 for r in self.results if r.behavior_match)
        
        lines.extend([
            f"- **Overall Success Rate**: {total_success}/{len(self.results)} ({total_success/len(self.results):.1%})",
            f"- **Behavior Match Rate**: {total_behavior}/{len(self.results)} ({total_behavior/len(self.results):.1%})",
            "",
            "## By CAP Primitive",
            "",
        ])
        
        # Per-primitive summary
        for primitive, stats in summary.items():
            spec = self.primitive_specs.get(primitive, {})
            lines.extend([
                f"### {primitive.upper()}",
                f"*{spec.get('description', 'No description')}*",
                "",
                f"| Metric | Value |",
                f"|--------|-------|",
                f"| Tests | {stats['total']} |",
                f"| Success Rate | {stats['success']}/{stats['total']} ({stats['success']/stats['total']:.1%}) |",
                f"| Behavior Match | {stats['behavior_match']}/{stats['total']} ({stats['behavior_match']/stats['total']:.1%}) |",
                f"| Required Fields | {stats['required_fields_avg']:.1%} |",
                f"| Optional Fields Avg | {stats['optional_fields_avg']:.1f} |",
                "",
            ])
            
            # Issues
            failures = [r for r in self.results if r.primitive == primitive and not r.success]
            if failures:
                lines.extend([
                    "**Issues:**",
                    "",
                ])
                for f in failures[:5]:  # Show first 5
                    lines.append(f"- {f.question_id}: Missing {', '.join(f.required_fields_missing)}")
                if len(failures) > 5:
                    lines.append(f"- ... and {len(failures) - 5} more")
                lines.append("")
        
        # Detailed results table
        lines.extend([
            "## Detailed Test Results",
            "",
            "| ID | Primitive | Success | Endpoint | Required | Optional | Behavior |",
            "|---|---|---|---|---|---|---|",
        ])
        
        for r in self.results:
            status = "✅" if r.success else "❌"
            behavior = "✅" if r.behavior_match else "❌"
            total_req = len(r.required_fields_present) + len(r.required_fields_missing)
            req_str = f"{len(r.required_fields_present)}/{total_req}" if total_req > 0 else "N/A"
            opt_str = str(len(r.optional_fields_present))
            endpoint_short = r.endpoint_called.split("/")[-1] if "/" in r.endpoint_called else r.endpoint_called
            
            lines.append(
                f"| {r.question_id} | {r.primitive} | {status} | {endpoint_short} | {req_str} | {opt_str} | {behavior} |"
            )
        
        # Recommendations
        lines.extend([
            "",
            "## Recommendations",
            "",
        ])
        
        # Find weakest primitive
        weakest = min(summary.items(), key=lambda x: x[1]["success"] / x[1]["total"] if x[1]["total"] > 0 else 0)
        lines.extend([
            f"1. **Priority Fix**: `{weakest[0]}` primitive has lowest success rate ({weakest[1]['success']/weakest[1]['total']:.1%})",
            "2. **Field Coverage**: Ensure all required fields are implemented per CAP spec",
            "3. **Behavior Validation**: Verify API responses match expected CAP semantics",
            "",
        ])
        
        with open(output_dir / "cap_compatibility_report.md", "w") as f:
            f.write("\n".join(lines))
    
    async def close(self):
        if self.client:
            await self.client.aclose()


async def main():
    parser = argparse.ArgumentParser(description="Test CAP primitive compatibility")
    parser.add_argument("--base-url", default="", help="CG API base URL")
    parser.add_argument("--questions-file", 
                       default="src/abel_benchmark/references/benchmark_questions_v2_enhanced.json",
                       help="Benchmark questions JSON")
    parser.add_argument("--primitive", choices=["predict", "intervene", "explain", "path", "attest", "all"],
                       default="all", help="Primitive to test")
    parser.add_argument("--category", choices=["A", "B", "C", "D", "E", "all"],
                       default="all", help="Category to test")
    parser.add_argument("--output-dir", default="./cap_compatibility_results", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without API calls")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of tests")
    
    args = parser.parse_args()
    
    # Load questions
    with open(args.questions_file) as f:
        data = json.load(f)
    
    questions = data.get("questions", [])
    
    # Filter
    if args.primitive != "all":
        questions = [q for q in questions if q.get("cap_request", {}).get("capability") == args.primitive]
    
    if args.category != "all":
        questions = [q for q in questions if q.get("category") == args.category]
    
    if args.limit:
        questions = questions[:args.limit]
    
    if not questions:
        print("❌ No questions match filters")
        return 1
    
    # Run tests
    tester = CAPCompatibilityTester(args.base_url, dry_run=args.dry_run)
    
    try:
        await tester.test_all_primitives(questions)
        tester.generate_report(Path(args.output_dir))
        
        # Summary
        success_rate = sum(1 for r in tester.results if r.success) / len(tester.results)
        print(f"\n{'='*70}")
        print("CAP Compatibility Summary")
        print(f"{'='*70}")
        print(f"Tests Run: {len(tester.results)}")
        print(f"Success Rate: {success_rate:.1%}")
        print(f"Behavior Match: {sum(1 for r in tester.results if r.behavior_match)/len(tester.results):.1%}")
        
        if success_rate >= 0.8:
            print("\n✅ CAP compatibility: EXCELLENT")
        elif success_rate >= 0.6:
            print("\n⚠️  CAP compatibility: GOOD (room for improvement)")
        else:
            print("\n❌ CAP compatibility: NEEDS WORK")
        
        return 0 if success_rate >= 0.6 else 1
        
    finally:
        await tester.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
