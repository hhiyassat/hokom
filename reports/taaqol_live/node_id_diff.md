# Node ID Diff — HOKOM-TAAQOL-LIVE-INTEGRATION-01

## Before Integration (without tests/taaqol_live/)

4218 tests collected in 0.73s

## After Integration

4368 tests collected in 0.74s

## New Test Module Added

`tests/taaqol_live/` — 150 tests (118 pass on Python 3.10, 32 skip pending Python 3.11+)

| Test File | Count | Status |
|-----------|-------|--------|
| test_constitutional.py | ~20 | PASS |
| test_decision_composition.py | ~30 | PASS |
| test_claim_projection.py | 18 | PASS |
| test_fail_closed.py | 11 | PASS |
| test_no_parallel_engine.py | 12 | PASS |
| test_serialization.py | 10 | PASS |
| test_determinism.py | 11 | PASS |
| test_vendor_integrity.py | 7 | PASS |
| test_taaqol_public_api.py | ~35 | SKIP (Python 3.11+ required) |
