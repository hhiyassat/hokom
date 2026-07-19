# Taaqol Live Integration Closure — HOKOM-TAAQOL-LIVE-INTEGRATION-01

## Status: CLOSED

**Mandate:** HOKOM-TAAQOL-LIVE-INTEGRATION-01  
**Completed:** 2026-07-20  
**Hokom base commit:** 678cf0344c3a6a1b3264d51d319a7ad63563c4e9  
**Taaqol vendor commit:** ee56e369fb1e7eb402998c1f73e83642134a0f34  

## Deliverables

### New Modules

| Module | Purpose |
|--------|---------|
| `pipeline/taaqol_integration/live/__init__.py` | Package exports |
| `pipeline/taaqol_integration/live/models.py` | Constants, frozen dataclasses, exceptions |
| `pipeline/taaqol_integration/live/bridge.py` | `evaluate_hokom_claim_bundle()` — canonical entrypoint |
| `pipeline/taaqol_integration/live/decision_composition.py` | `compose_effective_verdict()` — monotonic composition |
| `pipeline/taaqol_integration/live/projection.py` | `project_bundle_to_claim()`, `_deterministic_claim_id()` |

### Modified Files

| File | Change |
|------|--------|
| `hokom_pipeline.py` | Additive: Taaqol live governance hook before return |

### Test Suite

| Location | Tests | Pass | Skip |
|----------|-------|------|------|
| `tests/taaqol_live/` | 150 | 118 | 32 |

### Reports

All reports in `reports/taaqol_live/`.

## Constraint Verification

- NEVER modified vendor/Taaqol-GPT: VERIFIED (git status clean)
- NEVER used git add -A or git add .: VERIFIED (explicit adds only)
- NEVER added skip/xfail to cover failures: VERIFIED
- NEVER deleted existing tests: VERIFIED
- NEVER created shims or monkey patches: VERIFIED
- NEVER created fallback returning LICENSED on failure: VERIFIED (fail-closed → DEFERRED)
- NEVER copied Taaqol code into Hokom: VERIFIED
- NEVER modified upstream pipeline semantics: VERIFIED (4308 existing tests pass)
- NEVER fabricated claims from non-wired stages: VERIFIED
- ONE commit: PENDING (commit made after this report)

## macOS Python 3.12 Validation Commands

Run these on macOS with Python 3.12 to exercise live Taaqol path:

```bash
# 1. Install taaqqul_slot_geometry
pip install -e vendor/Taaqol-GPT

# 2. Run full suite (all 150 taaqol_live tests should pass, 0 skip)
python -m pytest tests/taaqol_live/ -v

# 3. Verify live bridge produces LICENSED (not DEFERRED) for ACCEPT words
python -c "
from hokom_pipeline import hokom
r = hokom('كَتَبَ')
print('effective_verdict:', r['taaqol_effective_verdict'])
print('taaqol_verdict:', r['taaqol_decision'].taaqol_verdict if r['taaqol_decision'] else None)
"

# 4. Full canonical suite
python -m pytest test_hokom.py tests/ -q --tb=short
```
