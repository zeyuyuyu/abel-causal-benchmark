# CAP (Causal Agent Protocol) Compatibility Report

**Generated**: 2026-03-20T13:48:03.283438
**Base URL**: https://abel-graph-computer-sit.abel.ai
**Total Tests**: 10

## Executive Summary

- **Overall Success Rate**: 8/10 (80.0%)
- **Behavior Match Rate**: 8/10 (80.0%)

## By CAP Primitive

### PREDICT
*Markov blanket inference for next-step prediction*

| Metric | Value |
|--------|-------|
| Tests | 8 |
| Success Rate | 8/8 (100.0%) |
| Behavior Match | 8/8 (100.0%) |
| Required Fields | 100.0% |
| Optional Fields Avg | 1.0 |

### INTERVENE
*Do-calculus intervention impact simulation*

| Metric | Value |
|--------|-------|
| Tests | 2 |
| Success Rate | 0/2 (0.0%) |
| Behavior Match | 0/2 (0.0%) |
| Required Fields | 0.0% |
| Optional Fields Avg | 0.0 |

**Issues:**

- B1: Missing intervention_effect, propagation
- B2: Missing intervention_effect, propagation

## Detailed Test Results

| ID | Primitive | Success | Endpoint | Required | Optional | Behavior |
|---|---|---|---|---|---|---|
| A1 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| A2 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| A3 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| A4 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| A5 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| A6 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| A7 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| A8 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| B1 | intervene | ❌ | intervention_impact | 0/2 | 0 | ❌ |
| B2 | intervene | ❌ | intervention_impact | 0/2 | 0 | ❌ |

## Recommendations

1. **Priority Fix**: `intervene` primitive has lowest success rate (0.0%)
2. **Field Coverage**: Ensure all required fields are implemented per CAP spec
3. **Behavior Validation**: Verify API responses match expected CAP semantics
