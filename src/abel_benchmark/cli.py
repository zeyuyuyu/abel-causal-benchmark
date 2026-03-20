#!/usr/bin/env python3
"""
FutureX Benchmark CLI

Usage:
    futurex-benchmark run --base-url <url> --questions <file>
    futurex-benchmark validate --questions <file>
    futurex-benchmark score --results <file>
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from .run_benchmark import AbelCausalBenchmark, BenchmarkReporter
from .enhanced_cevs_scorer import EnhancedCEVSScorer


def cmd_run(args):
    """Run benchmark against CG API."""
    with open(args.questions) as f:
        questions = json.load(f)
    
    async def run():
        benchmark = AbelCausalBenchmark(
            base_url=args.base_url,
            questions=questions['questions']
        )
        results = await benchmark.run()
        
        reporter = BenchmarkReporter(results, Path(args.output_dir))
        reporter.generate()
        
        print(f"\n✅ Benchmark complete. Reports saved to: {args.output_dir}")
        print(f"   Average CEVS: {sum(r.cevs_total for r in results) / len(results):.3f}")
    
    asyncio.run(run())


def cmd_validate(args):
    """Validate questions file format."""
    with open(args.questions) as f:
        data = json.load(f)
    
    errors = []
    
    if 'benchmark_version' not in data:
        errors.append("Missing 'benchmark_version'")
    
    if 'questions' not in data:
        errors.append("Missing 'questions' array")
    else:
        questions = data['questions']
        for i, q in enumerate(questions):
            if 'id' not in q:
                errors.append(f"Question {i}: Missing 'id'")
            if 'category' not in q:
                errors.append(f"Question {i}: Missing 'category'")
            if 'cap_request' not in q:
                errors.append(f"Question {i}: Missing 'cap_request'")
    
    if errors:
        print("❌ Validation failed:")
        for e in errors:
            print(f"   - {e}")
        return 1
    else:
        print(f"✅ Validated {len(data['questions'])} questions")
        return 0


def cmd_score(args):
    """Score existing results."""
    scorer = EnhancedCEVSScorer()
    
    with open(args.results) as f:
        results = json.load(f)
    
    report = scorer.get_scoring_report()
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="FutureX Causal Prediction Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run benchmark
  futurex-benchmark run \\
    --base-url https://abel-graph-computer-sit.abel.ai \\
    --questions references/benchmark_questions_v2_enhanced.json \\
    --output-dir ./results

  # Validate questions file
  futurex-benchmark validate --questions questions.json

  # View scoring report
  futurex-benchmark score --results results/benchmark_results.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run benchmark')
    run_parser.add_argument('--base-url', required=True, help='CG API base URL')
    run_parser.add_argument('--questions', required=True, help='Questions JSON file')
    run_parser.add_argument('--output-dir', default='./futurex_results', help='Output directory')
    run_parser.set_defaults(func=cmd_run)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate questions file')
    validate_parser.add_argument('--questions', required=True, help='Questions JSON file')
    validate_parser.set_defaults(func=cmd_validate)
    
    # Score command
    score_parser = subparsers.add_parser('score', help='Score results')
    score_parser.add_argument('--results', required=True, help='Results JSON file')
    score_parser.set_defaults(func=cmd_score)
    
    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
