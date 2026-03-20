# CAP (Causal Agent Protocol) Compatibility Report

**Generated**: 2026-03-20T13:48:12.227591
**Base URL**: https://abel-graph-computer-sit.abel.ai
**Total Tests**: 3

## Executive Summary

- **Overall Success Rate**: 0/3 (0.0%)
- **Behavior Match Rate**: 0/3 (0.0%)

## By CAP Primitive

### PATH
*Causal path discovery and tracing*

| Metric | Value |
|--------|-------|
| Tests | 3 |
| Success Rate | 0/3 (0.0%) |
| Behavior Match | 0/3 (0.0%) |
| Required Fields | 0.0% |
| Optional Fields Avg | 0.0 |

**Issues:**

- C1: Missing path, hops, tau
- C2: Missing path, hops, tau
- C3: Missing path, hops, tau

## Detailed Test Results

| ID | Primitive | Success | Endpoint | Required | Optional | Behavior |
|---|---|---|---|---|---|---|
| C1 | path | ❌ | nodes_connection | 0/3 | 0 | ❌ |
| C2 | path | ❌ | nodes_connection | 0/3 | 0 | ❌ |
| C3 | path | ❌ | nodes_connection | 0/3 | 0 | ❌ |

## Recommendations

1. **Priority Fix**: `path` primitive has lowest success rate (0.0%)
2. **Field Coverage**: Ensure all required fields are implemented per CAP spec
3. **Behavior Validation**: Verify API responses match expected CAP semantics
