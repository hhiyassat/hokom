# HOKOM-MORPHOLOGY-MASDAR-OWNERSHIP-01 — Canonical Masdar Ownership Closure

## Gate Values

| Gate | Value |
|------|-------|
| MASDAR_CANONICAL_OWNER | HOKOM |
| MASDAR_CANONICAL_ENTRYPOINT | VERIFIED (analyze_masdar) |
| MASDAR_OWNERSHIP_VERSION | 1.0.0 |
| MASDAR_CANONICAL_RESULT_TYPE | MasdarResult |
| MASDAR_CANONICAL_RULE_REGISTRY | data/masdar/masdar_rule_registry.jsonl |
| MASDAR_CANONICAL_DATA_SOURCE | data/masdar/masdar_lexical_inventory.jsonl |
| MASDAR_CANONICAL_TRACE_FORMAT | MasdarTraceEvent |
| MASDAR_CANONICAL_RESIDUAL_REGISTRY | data/masdar/masdar_residual_registry.jsonl |
| PARALLEL_MASDAR_ENGINES | 0 |
| EXTERNAL_MASDAR_DEPENDENCIES | 0 |
| FORM_I_UNLICENSED_GUESSES | 0 |
| UNLICENSED_MASDAR_GUESSES | 0 |
| FORCED_SINGLE_MASDAR_RESULTS | 0 |
| MULTIPLE_LICENSED_MASDARS | SUPPORTED |
| MASDAR_MIMI_CONTRACT | VERIFIED |
| MASDAR_MARRA_CONTRACT | VERIFIED |
| MASDAR_HAYAA_CONTRACT | VERIFIED |
| ISM_MASDAR_CONTRACT | VERIFIED |
| P5_SEMANTIC_MODIFICATIONS | 0 |
| ROOT_SEMANTIC_MODIFICATIONS | 0 |
| PATTERN_SEMANTIC_MODIFICATIONS | 0 |
| TAAQOL_SUBMODULE_MODIFICATIONS | 0 |

## Architecture Summary

- **Engine**: `pipeline/p5_masdar/engine.py` — `analyze_masdar(MasdarRequest) -> MasdarResult`
- **Models**: `pipeline/p5_masdar/models.py` — all frozen dataclasses
- **Registry**: `pipeline/p5_masdar/rule_registry.py` — loads from JSONL data files
- **Data**: `data/masdar/*.jsonl` — 4 tracked data files
- **Tests**: `tests/p5_masdar/` — 130 tests across 9 test files

## Design Principles

1. FORM_I masdar is governed-defer: lexical evidence required (SAMI3I)
2. Augmented forms (FORM_II–X + QUADRILITERAL_FORM_I) use productive rules
3. FA3IL_PARTICIPLE is always BLOCKED (non-verbal source)
4. Multiple licensed masdars supported (FORM_III: MUFA3ALA + FI3AL)
5. Weak roots (HOLLOW, DEFECTIVE, LAFIF, etc.) defer surface realization
6. No root/wazn re-extraction inside the masdar engine
7. No external engines, network, subprocess
8. Deterministic ordering enforced at registry level

## Test Results

- Run 1: 3516 passed, 18 skipped, 0 failed
- Run 2: 3516 passed, 18 skipped, 0 failed
- Masdar-specific: 130 passed, 0 failed
