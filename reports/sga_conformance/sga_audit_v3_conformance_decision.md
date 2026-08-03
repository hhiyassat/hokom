# SGA Conformance Audit — Conformance Decision
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

### Decision: SGA_ENFORCEMENT_REQUIRED

| Field | Value |
|-------|-------|
| ACTUAL_HEAD | 02918a6f9bd33f89352ca64ea70c432c2d16a05e |
| T-01 STATUS | RESOLVED in 53e7932 |
| OPEN VIOLATIONS | 13 (T-02 through T-14) |
| BRIDGE_EXPRESSIVITY_STATUS | PARTIAL |
| SERIALIZATION_CONTRACT_STATUS | PARTIAL |
| DECISION | SGA_ENFORCEMENT_REQUIRED |

### Remediation Order (Dependency-Ordered)

The following order respects inter-violation dependencies — complete foundational violations before dependent ones.

**Layer 1 — Typing Infrastructure (no dependencies)**

1. **T-14**: Type `HokomTaaqolDecision.residuals` as `tuple[HokomTaaqolResidual, ...]` (models.py). Prerequisite for T-03–T-07 which will produce typed residuals.
2. **T-12**: Split `HokomTaaqolTraceEvent.output` into `gamma_state: Optional[str]` and `gate_verdict: Optional[str]` (models.py). No dependencies.
3. **T-11**: Replace `uuid4()` in claim_adapter.py with deterministic SHA-256 hash of normalized input fields. No dependencies.

**Layer 2 — Serialization (depends on Layer 1)**

4. **T-13**: Add `from_dict()` classmethod to `HokomTaaqolDecision` and a round-trip test (depends on T-14 having stabilized the residuals type).

**Layer 3 — Phonological Slot Typing (depends on Layer 1)**

5. **T-02**: Define `PhonologicalSlot` frozen dataclass; replace `syllabify() -> list[dict]` with `syllabify() -> list[PhonologicalSlot]` (cell_builder.py). No bridge dependency.

**Layer 4 — Slot Transition Licensing (depends on T-02)**

6. **T-08**: Route all 8 `SLOT_TRANS` entries through `TransitionGate.decide()` with phonological `EvidenceContract`. Replace `_gate(state) -> str` with typed `TransitionVerdict` (slot_engineering.py). Depends on T-02 (PhonologicalSlot as SlotGraph input).

**Layer 5 — Bridge Claim Projection (depends on Layer 1 + Layer 2)**

7. **T-03**: Add `ROOT_CLAIM` slot to `_build_slot_graph()` in bridge.py.
8. **T-04**: Add `PATTERN_CLAIM` slot (wazn/form) to `_build_slot_graph()`.
9. **T-05**: Add `BAB_CLAIM` slot to `_build_slot_graph()`.
10. **T-06**: Add `MASDAR_CLAIM` slot to `_build_slot_graph()`.
11. **T-07**: Add `DERIVATIVE_CLAIM` slots (one per mushtaq) to `_build_slot_graph()`.

**Layer 6 — Bridge Expressivity (depends on Layer 5)**

12. **T-10**: Implement ambiguity preservation — populate candidate_set or use parallel slots for competing parse hypotheses (depends on T-03–T-07 for full multi-slot graph).
13. **T-09**: Populate SlotGraph conditions, obstacles, defeaters, candidate_set fields. Full expressivity requires all claim slots (T-03–T-07) to be present first.

### Passing Tests (Runtime Evidence)

| Test | Status |
|------|--------|
| test_repo_root_resolves_correctly | PASSED |
| test_vendor_path_exists | PASSED |
| test_vendor_sha_matches_pin | PASSED |
| test_runtime_failure_is_not_semantic_defer | PASSED |
| test_no_silent_fallback | PASSED |
| test_taaqol_not_modified | PASSED |
| test_taaqol_public_entrypoint_loads | SKIPPED (Python 3.10 < 3.11) |
| test_slot_graph_created | SKIPPED |
| test_gamma_executes | SKIPPED |
| test_gate_executes | SKIPPED |
| test_trace_ledger_has_event | SKIPPED |
| test_live_pipeline_integration | SKIPPED |

6 skipped tests require Python 3.11+ to load `taaqqul_slot_geometry` (StrEnum dependency). These will pass on the canonical Darwin/Python 3.12.4 environment.
