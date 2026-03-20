# CAP (Causal Agent Protocol) Compatibility Report

**Generated**: 2026-03-20T11:17:16.062363
**Base URL**: https://abel-graph-computer-sit.abel.ai
**Total Tests**: 2

## Executive Summary

- **Overall Success Rate**: 0/2 (0.0%)
- **Behavior Match Rate**: 0/2 (0.0%)

## By CAP Primitive

### PREDICT
*Markov blanket inference for next-step prediction*

| Metric | Value |
|--------|-------|
| Tests | 2 |
| Success Rate | 0/2 (0.0%) |
| Behavior Match | 0/2 (0.0%) |
| Required Fields | 0.0% |
| Optional Fields Avg | 0.0 |

**Issues:**

- A1: Missing prediction, probability_up
- A2: Missing prediction, probability_up

## Detailed Test Results

| ID | Primitive | Success | Endpoint | Required | Optional | Behavior |
|---|---|---|---|---|---|---|
| A1 | predict | ❌ | multi-step-prediction | 0/2 | 0 | ❌ |
| A2 | predict | ❌ | multi-step-prediction | 0/2 | 0 | ❌ |

## Recommendations

1. **Priority Fix**: `predict` primitive has lowest success rate (0.0%)
2. **Field Coverage**: Ensure all required fields are implemented per CAP spec
3. **Behavior Validation**: Verify API responses match expected CAP semantics
