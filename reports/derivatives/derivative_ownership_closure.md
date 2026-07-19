# HOKOM-MORPHOLOGY-DERIVATIVES-OWNERSHIP-01: Closure Report

**Date**: 2026-07-19
**Baseline Commit**: ad376de (HOKOM-MORPHOLOGY-MASDAR-OWNERSHIP-01)

## Closure Gate Values

| Gate | Value | Status |
|------|-------|--------|
| DERIVATIVES_CANONICAL_OWNER | HOKOM | VERIFIED |
| DERIVATIVES_CANONICAL_ENTRYPOINT | analyze_derivative() in pipeline/p6_derivatives/engine.py | VERIFIED |
| PARALLEL_DERIVATIVE_ENGINES | 0 | VERIFIED |
| EXTERNAL_DERIVATIVE_DEPENDENCIES | 0 | VERIFIED |
| ISM_FA3IL_CONTRACT | VERIFIED — productive FORM_I through FORM_X | VERIFIED |
| ISM_MAF3UL_CONTRACT | VERIFIED — productive FORM_I through FORM_X | VERIFIED |
| SIFA_MUSHABBAHA_CONTRACT | VERIFIED — governed deferral, lexical evidence required | VERIFIED |
| MUBALGHA_CONTRACT | VERIFIED — governed deferral, lexical evidence required | VERIFIED |
| ISM_ZAMAN_CONTRACT | VERIFIED — governed by RULE-D-02 ambiguity | VERIFIED |
| ISM_MAKAN_CONTRACT | VERIFIED — governed by RULE-D-02 ambiguity | VERIFIED |
| ISM_ALA_CONTRACT | VERIFIED — residual ISM_ALA_LEXICON_GAP without lexicon | VERIFIED |
| MASDAR_MIMI_LEAKAGE_PREVENTION | VERIFIED — derivative types distinct from masdar types | VERIFIED |
| FA3IL_PARTICIPLE_ROUTING_PRESERVED | VERIFIED — RULE-D-01: treated as FORM_I for ISM_FA3IL | VERIFIED |
| ISM_ZAMAN_MAKAN_AMBIGUITY_GOVERNED | VERIFIED — RULE-D-02: deferred without discriminator | VERIFIED |
| MUBALGHA_UNLICENSED_GUESSES | 0 | VERIFIED |
| SIFA_UNLICENSED_GUESSES | 0 | VERIFIED |
| MULTIPLE_LICENSED_DERIVATIVES | SUPPORTED | VERIFIED |
| DERIVATIVE_RESIDUALS_GOVERNED | VERIFIED — ISM_ALA_LEXICON_GAP, FORM_I_SIFA_VERBAL_EVIDENCE_REQUIRED | VERIFIED |
| DERIVATIVE_TRACE_COMPLETE | VERIFIED — all results include MasdarTraceEvent sequence | VERIFIED |
| DERIVATIVE_SERIALIZATION_ROUNDTRIP | PASS — tested in test_derivative_serialization.py | VERIFIED |
| P5_MASDAR_SEMANTIC_MODIFICATIONS | 0 | VERIFIED |
| ROOT_SEMANTIC_MODIFICATIONS | 0 | VERIFIED |
| PATTERN_SEMANTIC_MODIFICATIONS | 0 | VERIFIED |
| TAAQOL_SUBMODULE_MODIFICATIONS | 0 | VERIFIED |
| CANONICAL_FULL_SUITE_FAILURES | 0 | VERIFIED |
| HOKOM_MORPHOLOGY_DERIVATIVES_OWNERSHIP_01 | CLOSED | CLOSED |

## Test Results

- Derivative tests: 259 passed
- Full suite Run 1: 3775 passed, 18 skipped, 132 subtests passed
- Full suite Run 2: 3775 passed, 18 skipped, 132 subtests passed
- Run 1 == Run 2: YES

## Files Created

### Engine Module (pipeline/p6_derivatives/)
- `__init__.py`
- `models.py` — contracts, 7 derivative types, verdicts, ownership gate
- `rule_registry.py` — data loader (JSONL-backed, deterministic)
- `engine.py` — CANONICAL_DERIVATIVES_ENTRYPOINT = analyze_derivative()

### Data Layer (data/derivatives/)
- `derivative_rule_registry.jsonl` — 36 rules (ISM_FA3IL ×9, ISM_MAF3UL ×9, SIFA ×5, MUBALGHA ×5, ISM_ZM ×4, ISM_ALA ×3 + MAKAN variants)
- `derivative_lexical_inventory.jsonl` — 10 attested derivative-verb pairs
- `derivative_pattern_definitions.jsonl` — 25 pattern definitions

### Tests (tests/p6_derivatives/)
- `test_derivative_models.py`
- `test_derivative_rule_registry.py`
- `test_derivative_engine_ism_fa3il.py`
- `test_derivative_engine_ism_maf3ul.py`
- `test_derivative_engine_other_types.py`
- `test_derivative_false_positives.py`
- `test_derivative_properties.py`
- `test_derivative_constitutional.py`
- `test_derivative_serialization.py`
- `test_derivative_data_reproducibility.py`

### Demo Script
- `scripts/analyze_text_demo.py` — added `--stop-at-derivatives` and `--derivative-type` flags

## Governed Deferrals

| Condition | Verdict | Reason Code |
|-----------|---------|-------------|
| ISM_ZAMAN without lexical discriminator | DEFERRED | ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY |
| ISM_MAKAN without lexical discriminator | DEFERRED | ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY |
| SIFA_MUSHABBAHA without lexical evidence | DEFERRED | SIFA_VERBAL_EVIDENCE_REQUIRED |
| MUBALGHA without lexical evidence | DEFERRED | MUBALGHA_LEXICAL_EVIDENCE_REQUIRED |

## Governed Residuals

| Condition | Verdict | Residual Code |
|-----------|---------|---------------|
| ISM_ALA without lexical evidence | RESIDUAL | ISM_ALA_LEXICON_GAP |
