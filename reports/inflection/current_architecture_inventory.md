# p5_inflection Architecture Inventory
# HOKOM-INFLECTION-PARADIGM-OWNERSHIP-01

## Files in pipeline/p5_inflection/

| File | Size | Purpose |
|---|---|---|
| `__init__.py` | 0 bytes | Package marker |
| `models.py` | ~7.6 KB | Domain DTOs + ownership gate |
| `phase5_orchestrator.py` | ~10.4 KB | Canonical entrypoint |
| `api.py` | ~3 KB | Generate-verb API surface |
| `feature_system.py` | ~21 KB | Surface feature extraction |
| `inflection_analysis.py` | ~11 KB | Paradigm analysis + PARADIGM_FOR_ROOT_CLASS |
| `surface_realization.py` | ~49 KB | Surface form generation |
| `verb_classifier.py` | ~2.8 KB | classify_root() → RootClass |

## Public Symbols

### models.py constants
- `INFLECTION_CANONICAL_OWNER = 'HOKOM'`
- `INFLECTION_ENGINE_ID = 'HOKOM_INFLECTION_ENGINE'`
- `INFLECTION_OWNERSHIP_VERSION = '1.0.0'`

### models.py classes (all frozen dataclasses)
- `Tense` — PAST, IMPERFECT, IMPERATIVE
- `Mood` — INDICATIVE, SUBJUNCTIVE, JUSSIVE, IMPERATIVE
- `Voice` — ACTIVE, PASSIVE
- `Person` — 1, 2, 3
- `Number` — SG, DU, PL
- `Gender` — M, F
- `Directive` — ACCEPT, DEFER, BLOCK, NOT_APPLICABLE
- `RootClass` — 14 root class constants
- `InflectionalForm` — surface form DTO with to_dict()
- `ParadigmCandidate` — paradigm classification DTO
- `InflectionalAnalysis` — analysis result with features_dict property
- `Phase5Result` — top-level result with to_dict()
- `InflectionOwnershipGate` — ownership gate with is_closed() and to_dict()

### phase5_orchestrator.py
- `INFLECTION_CANONICAL_ENTRYPOINT = 'project_inflection_with_licensing'`
- `INFLECTION_CANONICAL_ENTRYPOINT_MODULE = 'pipeline.p5_inflection.phase5_orchestrator'`
- `project_inflection_with_licensing(surface, root, bab_id, form_family, wazn_id, morphology_path, phase4a_result, phase4b_result, attachment) -> Phase5Result`

## Current Result Types
- Primary: `Phase5Result` (frozen dataclass)
- Sub-results: `InflectionalForm`, `ParadigmCandidate`, `InflectionalAnalysis`

## Current Entrypoints
- Canonical: `project_inflection_with_licensing` in `pipeline.p5_inflection.phase5_orchestrator`

## Current Callers (hokom_pipeline.py)
- Line 349: `from pipeline.p5_inflection.phase5_orchestrator import project_inflection_with_licensing`
- Line 356–366: called with surface, root, bab_id, form_family, wazn_id, morphology_path, phase4a_result, phase4b_result, attachment

## Existing Tests Count (before this mandate)
- `test_inflection_constitutional.py`: 33
- `test_phase5_reference_matrix.py`: 87
- Total: 120

## What Was Missing for Canonical Ownership
1. Lowercase canonical gate fields on `InflectionOwnershipGate` (engine_id, canonical_owner, etc.)
2. `is_closed()` method on `InflectionOwnershipGate`
3. `to_dict()` method on `InflectionOwnershipGate`
4. `INFLECTION_CANONICAL_ENTRYPOINT_MODULE` constant in orchestrator
5. 4 additional test files (ownership_models, entrypoint, properties, serialization)

## PARALLEL_INFLECTION_IMPLEMENTATIONS: 0
No other inflection package found besides `pipeline/p5_inflection/`.

## DEAD_OR_LEGACY_INFLECTION_CODE
None found. All code in p5_inflection/ is live and referenced.
