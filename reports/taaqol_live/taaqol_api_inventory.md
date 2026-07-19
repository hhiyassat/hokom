# Taaqol API Inventory — HOKOM-TAAQOL-LIVE-INTEGRATION-01

**Package:** taaqqul_slot_geometry  
**Vendor path:** vendor/Taaqol-GPT/src/taaqqul_slot_geometry  
**Python requires:** >=3.11  
**Taaqol commit:** ee56e369fb1e7eb402998c1f73e83642134a0f34  
**Hokom commit at integration:** 678cf0344c3a6a1b3264d51d319a7ad63563c4e9  

## Symbols Used

| Symbol | Kind | Module |
|--------|------|--------|
| SlotGraph | dataclass | core.slot_graph |
| Center | dataclass | core.slot_graph |
| TraceRef | dataclass | core.slot_graph |
| SlotBoundary | dataclass | core.slot_graph |
| OpeningPolicy | dataclass | core.slot_graph |
| Slot | dataclass | core.slot_graph |
| SlotState | StrEnum | core.slot_graph |
| OutputBoundary | dataclass | core.slot_graph |
| EntryBoundary | dataclass | core.slot_graph |
| GenerationSource | StrEnum | core.slot_graph |
| Layer | StrEnum | core.slot_graph |
| gamma | function | core.gamma |
| GammaResult | dataclass | core.gamma |
| ClosureState | StrEnum | core.closure_state |
| TransitionGate | dataclass | core.transition_gate |
| TransitionVerdict | dataclass | core.transition_gate |
| TransitionState | StrEnum | core.transition_state |
| GATE_RANK_CEILING | constant | core.transition_gate |
| UNGATED_RANK_CEILING | constant | core.transition_gate |
| Rank | IntEnum | core.rank_lattice |
| RankLattice | class | core.rank_lattice |
| EvidenceContract | dataclass | core.evidence_contract |
| EvidenceSource | dataclass | core.evidence_contract |
| SINGLE_SOURCE_EVIDENCE_CEILING | constant | core.evidence_contract |
| Residual | dataclass | core.residual_policy |
| ResidualKind | StrEnum | core.residual_policy |
| ResidualPolicy | class | core.residual_policy |
| PERFORATING_KINDS | frozenset | core.residual_policy |
| FailureCode | StrEnum | core.failure_taxonomy |

## Pipeline Sequence

SlotGraph → gamma() → GammaResult → TransitionGate.decide() → TransitionVerdict

All symbols imported inside function body (fail-closed on ImportError).
