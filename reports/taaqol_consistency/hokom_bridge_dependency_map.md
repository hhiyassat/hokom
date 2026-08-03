# Hokom Bridge Dependency Map

**Audit date:** 2026-07-21  
**Hokom HEAD:** b706ced  
**Taaqol PIN:** 35381739410071ac21dd96702ecbb2acb493f90d  

## PROHIBITED_INTERNAL_IMPORTS

**Count: 0**

No underscore-prefixed submodules, no test helpers, no simulation internals,  
no `enriched_simulation_agent`, no `lge`, no `x0r`, no `gpt` internals consumed.  
All imports resolved against public `__all__` of `taaqqul_slot_geometry`.

## Bridge Files Consuming Taaqol

| Hokom File | Import Style |
|------------|-------------|
| `pipeline/taaqol_integration/admission_gate.py` | `from taaqqul_slot_geometry.core.X import Y` inside try/except |
| `pipeline/taaqol_integration/live/bridge.py` | `import taaqqul_slot_geometry as _taaqol` + `from taaqqul_slot_geometry.core.gamma import gamma` |
| `pipeline/taaqol_integration/shadow_mode.py` | `from taaqqul_slot_geometry.core.{closure_state,gamma,rank_lattice} import ...` |
| `pipeline/taaqol_integration/native_continuation.py` | `from taaqqul_slot_geometry.core.rank_lattice import Rank` |

All imports are inside function bodies or guarded try/except blocks with fail-closed  
behavior (returns DEFERRED on ImportError). No top-level import of taaqqul_slot_geometry.

## Symbol Dependency Table

| Imported Symbol | Taaqol Module | In __all__ | Kind | Used For | Compatible at PIN | Adaptation Required | Semantic Risk |
|----------------|--------------|-----------|------|----------|------------------|--------------------|----|
| SlotGraph | core.slot_graph | YES | dataclass | Build claim graph | YES | NO | LOW |
| Center | core.slot_graph | YES | dataclass | Morphological center scope | YES | NO | LOW |
| TraceRef | core.slot_graph | YES | dataclass | Trace reference | YES | NO | LOW |
| SlotBoundary | core.slot_graph | YES | dataclass | Input/output boundary | YES | NO | LOW |
| OpeningPolicy | core.slot_graph | YES | dataclass | Slot opening rules | YES | NO | LOW |
| Slot | core.slot_graph | YES | dataclass | Individual slot | YES | NO | LOW |
| SlotState | core.slot_graph | YES | StrEnum | Slot closure state | YES | NO | LOW |
| OutputBoundary | core.slot_graph | YES | dataclass | Output boundary | YES | NO | LOW |
| EntryBoundary | core.slot_graph | YES | dataclass | Entry boundary | YES | NO | LOW |
| GenerationSource | core.slot_graph | YES | StrEnum | Source engine tag | YES | NO | LOW |
| Layer | core.slot_graph | YES | StrEnum | Rank layer | YES | NO | LOW |
| gamma | core.gamma | YES | function | Ordered verdict function | YES | NO | LOW |
| GammaResult | core.gamma | YES | dataclass | Verdict + trace pair | YES | NO | LOW |
| ClosureState | core.closure_state | YES | StrEnum | Slot closure state | YES | NO | LOW |
| TransitionGate | core.transition_gate | YES | dataclass | Cross-layer gate | YES | NO | LOW |
| TransitionVerdict | core.transition_gate | YES | dataclass | Gate verdict | YES | NO | LOW |
| GATE_RANK_CEILING | core.transition_gate | YES | constant | Rank ceiling constant | YES | NO | LOW |
| UNGATED_RANK_CEILING | core.transition_gate | YES | constant | Ungated rank ceiling | YES | NO | LOW |
| TransitionState | core.transition_state | YES | StrEnum | Five-state verdict vocab | YES | NO | LOW |
| Rank | core.rank_lattice | YES | IntEnum | Rank values | YES | NO | LOW |
| RankLattice | core.rank_lattice | YES | class | meet/join operations | YES | NO | LOW |
| EvidenceContract | core.evidence_contract | YES | dataclass | Evidence carrier | YES | NO | LOW |
| EvidenceSource | core.evidence_contract | YES | dataclass | Evidence source | YES | NO | LOW |
| SINGLE_SOURCE_EVIDENCE_CEILING | core.evidence_contract | YES | constant | Evidence rank ceiling | YES | NO | LOW |
| Residual | core.residual_policy | YES | dataclass | Residual carrier | YES | NO | LOW |
| ResidualKind | core.residual_policy | YES | StrEnum | Residual classification | YES | NO | LOW |
| ResidualPolicy | core.residual_policy | YES | class | Visibility engine | YES | NO | LOW |
| PERFORATING_KINDS | core.residual_policy | YES | frozenset | Perforating residual set | YES | NO | LOW |
| FailureCode | core.failure_taxonomy | YES | StrEnum | Named failure codes | YES | NO | LOW |

## Taaqol Submodules NOT Consumed by Hokom

| Subpackage | Reason Not Consumed |
|-----------|---------------------|
| `adapters` | Hokom is not a ModelClient adapter |
| `audit` | AnswerAudit requires ModelClient — DEFERRED per strict_mode |
| `weight` | Arabic weight carriers — Hokom owns weight/morphology |
| `gpt` | GPT hallucination / knowledge-origin layer — not Hokom concern |
| `lge` | Sentence/relation slot runtime — not yet wired |
| `x0r` | Archimedean/KPI audit — not yet wired |
| `L1` | AQD audit contracts — not yet wired |
| `g0_c1..g0_c6` | G0 bare-stem pipeline — not yet wired |
| `enriched_simulation_agent` | AUXILIARY_EXPERIMENT — explicitly forbidden |

## Test Coverage of Bridge Dependencies

| Symbol | Test File | Tests |
|--------|-----------|-------|
| SlotGraph + gamma + TransitionGate | tests/taaqol_live/test_segment_aware_slot_graph.py | 8 |
| TransitionState (DEFERRED path) | tests/taaqol_live/test_clitic_only_fail_closed.py | 7 |
| Center.scope contract | tests/taaqol_live/test_no_full_token_center.py | 16 |
| Full bridge pipeline | tests/taaqol_live/test_ayat_al_dayn_segment_aware.py | 30 |
| Determinism | tests/taaqol_live/test_determinism.py | (included in 118 pass) |
| Serialization | tests/taaqol_live/test_serialization.py | (included in 118 pass) |
| Constitutional | tests/taaqol_live/test_constitutional.py | (included in 118 pass) |

## Ownership Collisions

**Count: 0**

No symbol imported from Taaqol is re-implemented, shadowed, or owned  
by a Hokom module. Hokom bridge is consumer-only.
