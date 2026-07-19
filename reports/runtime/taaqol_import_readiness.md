# Taaqol Import Readiness Report

## Mandate: HOKOM-RUNTIME-PYTHON-3.11+-MIGRATION-01

## Taaqol Vendor Facts
- Package name: `taaqqul_slot_geometry` (double-q)
- Path: `vendor/Taaqol-GPT/src/taaqqul_slot_geometry/`
- requires-python: >=3.11 (from vendor/Taaqol-GPT/pyproject.toml)
- Uses `from enum import StrEnum` in 5+ source files

## Import Readiness by Python Version

| Python | taaqqul_slot_geometry importable? | Reason |
|--------|----------------------------------|--------|
| 3.10 | NO | `ImportError: cannot import name 'StrEnum' from 'enum'` |
| 3.11 | YES | Native StrEnum available |
| 3.12 | YES | Native StrEnum available |

## Current Integration Status
- `TAAQOL_LIVE_CALLS = 0` — Taaqol is NOT activated in the live pipeline
- `hokom_pipeline.py` does NOT import from taaqol vendor directly
- `pipeline/taaqol_integration/admission_gate.py` gates activation on Python 3.11+
  - On Python 3.10: gate blocks with `DEFERRED: StrEnum not available`
  - On Python 3.12: gate will allow when integration is activated (future)

## Key Objects Exposed by Taaqol
From `vendor/Taaqol-GPT/src/taaqqul_slot_geometry/__init__.py`:
- SlotGraph, gamma, GammaResult, TraceEntryCandidate, TraceLedger
- RankLattice, ResidualPolicy, ResidualEvaluation
- EvidenceContract, EvidenceSource
- TransitionGate

## Conclusion
Taaqol import readiness: **READY for Python 3.12** (will succeed when activated).
Live integration status: **NOT_STARTED** (correct per mandate).
