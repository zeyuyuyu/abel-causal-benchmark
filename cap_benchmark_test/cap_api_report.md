# CAP API Test Report

**Generated**: 2026-03-20T15:41:33.906798
**Base URL**: https://cap-sit.abel.ai
**CAP Endpoint**: /api/v1/cap
**Total Tests**: 10

## Summary

- **Success Rate**: 4/10 (40.0%)

## By Primitive

- **predict**: 4/8 (50.0%)
- **intervene**: 0/2 (0.0%)

## Detailed Results

| ID | Primitive | Success | Fields | Errors |
|---|---|---|---|---|
| A1 | predict | ❌ | 0/2 | HTTP 503: {"cap_version":"0.2. |
| A2 | predict | ✅ | 2/2 | - |
| A3 | predict | ❌ | 0/2 | HTTP 503: {"cap_version":"0.2. |
| A4 | predict | ✅ | 2/2 | - |
| A5 | predict | ✅ | 2/2 | - |
| A6 | predict | ✅ | 2/2 | - |
| A7 | predict | ❌ | 0/2 | HTTP 503: {"cap_version":"0.2. |
| A8 | predict | ❌ | 0/2 | HTTP 503: {"cap_version":"0.2. |
| B1 | intervene | ❌ | 0/2 | HTTP 404: {"cap_version":"0.2. |
| B2 | intervene | ❌ | 0/2 | HTTP 404: {"cap_version":"0.2. |