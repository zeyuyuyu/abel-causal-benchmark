# CAP (Causal Agent Protocol) Compatibility Report

**Generated**: 2026-03-20T13:57:36.391124
**Base URL**: https://abel-graph-computer-sit.abel.ai
**Total Tests**: 53

## Executive Summary

- **Overall Success Rate**: 18/53 (34.0%)
- **Behavior Match Rate**: 19/53 (35.8%)

## By CAP Primitive

### PREDICT
*Markov blanket inference for next-step prediction*

| Metric | Value |
|--------|-------|
| Tests | 15 |
| Success Rate | 15/15 (100.0%) |
| Behavior Match | 15/15 (100.0%) |
| Required Fields | 100.0% |
| Optional Fields Avg | 1.0 |

### INTERVENE
*Do-calculus intervention impact simulation*

| Metric | Value |
|--------|-------|
| Tests | 10 |
| Success Rate | 0/10 (0.0%) |
| Behavior Match | 0/10 (0.0%) |
| Required Fields | 0.0% |
| Optional Fields Avg | 0.0 |

**Issues:**

- B1: Missing intervention_effect, propagation
- B2: Missing intervention_effect, propagation
- B3: Missing intervention_effect, propagation
- B4: Missing intervention_effect, propagation
- B5: Missing intervention_effect, propagation
- ... and 5 more

### PATH
*Causal path discovery and tracing*

| Metric | Value |
|--------|-------|
| Tests | 7 |
| Success Rate | 0/7 (0.0%) |
| Behavior Match | 0/7 (0.0%) |
| Required Fields | 0.0% |
| Optional Fields Avg | 0.0 |

**Issues:**

- C1: Missing path, hops, tau
- C2: Missing path, hops, tau
- C3: Missing path, hops, tau
- C4: Missing path, hops, tau
- C5: Missing path, hops, tau
- ... and 2 more

### SENSITIVITY
*No description*

| Metric | Value |
|--------|-------|
| Tests | 3 |
| Success Rate | 3/3 (100.0%) |
| Behavior Match | 3/3 (100.0%) |
| Required Fields | 100.0% |
| Optional Fields Avg | 1.0 |

### ATTEST
*Cross-sectional causal claim verification*

| Metric | Value |
|--------|-------|
| Tests | 17 |
| Success Rate | 0/17 (0.0%) |
| Behavior Match | 0/17 (0.0%) |
| Required Fields | 0.0% |
| Optional Fields Avg | 0.0 |

**Issues:**

- D2: Missing comparison, ranking
- E1: Missing comparison, ranking
- E2: Missing comparison, ranking
- E3: Missing comparison, ranking
- E4: Missing comparison, ranking
- ... and 12 more

### EXPLAIN
*Feature attribution and minimal explanation set*

| Metric | Value |
|--------|-------|
| Tests | 1 |
| Success Rate | 0/1 (0.0%) |
| Behavior Match | 1/1 (100.0%) |
| Required Fields | 0.0% |
| Optional Fields Avg | 0.0 |

**Issues:**

- D4: Missing explanation, feature_importance

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
| B3 | intervene | ❌ | intervention_impact | 0/2 | 0 | ❌ |
| B4 | intervene | ❌ | intervention_impact | 0/2 | 0 | ❌ |
| B5 | intervene | ❌ | intervention_impact | 0/2 | 0 | ❌ |
| B6 | intervene | ❌ | intervention_impact | 0/2 | 0 | ❌ |
| B7 | intervene | ❌ | intervention_impact | 0/2 | 0 | ❌ |
| B8 | intervene | ❌ | intervention_impact | 0/2 | 0 | ❌ |
| B9 | intervene | ❌ | intervention_impact | 0/2 | 0 | ❌ |
| B10 | intervene | ❌ | intervention_impact | 0/2 | 0 | ❌ |
| C1 | path | ❌ | nodes_connection | 0/3 | 0 | ❌ |
| C2 | path | ❌ | nodes_connection | 0/3 | 0 | ❌ |
| C3 | path | ❌ | nodes_connection | 0/3 | 0 | ❌ |
| C4 | path | ❌ | nodes_connection | 0/3 | 0 | ❌ |
| C5 | path | ❌ | nodes_connection | 0/3 | 0 | ❌ |
| C6 | path | ❌ | nodes_connection | 0/3 | 0 | ❌ |
| C7 | path | ❌ | nodes_connection | 0/3 | 0 | ❌ |
| D1 | sensitivity | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| D2 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| D3 | sensitivity | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| D4 | explain | ❌ | prediction | 0/2 | 0 | ✅ |
| D5 | sensitivity | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| E1 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| E2 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| E3 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| E4 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| E5 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| F1 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| F2 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| F3 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| F4 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| F5 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| F6 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| F7 | predict | ✅ | multi-step-prediction | 2/2 | 1 | ✅ |
| XF_694a8b8f | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| XF_69493cb1 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| XF_69566909 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| XF_6957ba8a | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| XF_695a5d89 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| XF_695a5d89 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| XF_69566c13 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| XF_6964eca5 | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| XF_6957ba8a | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| XF_69639b3e | attest | ❌ | predictions | 0/2 | 0 | ❌ |
| XF_695a609d | attest | ❌ | predictions | 0/2 | 0 | ❌ |

## Recommendations

1. **Priority Fix**: `intervene` primitive has lowest success rate (0.0%)
2. **Field Coverage**: Ensure all required fields are implemented per CAP spec
3. **Behavior Validation**: Verify API responses match expected CAP semantics
