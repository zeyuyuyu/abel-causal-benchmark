# CAP (Causal Agent Protocol) Compatibility Report

**Generated**: 2026-03-20T14:24:54.656723
**Base URL**: https://abel-graph-computer-sit.abel.ai
**Total Tests**: 3

## Executive Summary

- **Overall Success Rate**: 0/3 (0.0%)
- **Behavior Match Rate**: 0/3 (0.0%)

## By CAP Primitive

### ATTEST
*Cross-sectional causal claim verification*

| Metric | Value |
|--------|-------|
| Tests | 3 |
| Success Rate | 0/3 (0.0%) |
| Behavior Match | 0/3 (0.0%) |
| Required Fields | 0.0% |
| Optional Fields Avg | 0.0 |

**Issues:**

- E1: Missing comparison, ranking
- E2: Missing comparison, ranking
- E3: Missing comparison, ranking

## Detailed Test Results

| ID | Primitive | Success | Endpoint | Required | Optional | Behavior |
|---|---|---|---|---|---|---|
| E1 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| E2 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| E3 | attest | ❌ | predictions | 0/2 | 0 | ❌ |

## Recommendations

1. **Priority Fix**: `attest` primitive has lowest success rate (0.0%)
2. **Field Coverage**: Ensure all required fields are implemented per CAP spec
3. **Behavior Validation**: Verify API responses match expected CAP semantics
