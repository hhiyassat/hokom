"""
taaqol_stage_registry.py — Taaqol canonical operation audit.

AUDIT RESULT (CLOSURE-02):
    TAAQOL_49_STAGE_CLAIM         = RETRACTED
    TAAQOL_DOCUMENT_49            = PV-M0_META_LANGUAGE_BOUNDARY_COVENANT (a LAW, not a stage count)
    TAAQOL_PROVEN_CORE_OPERATIONS = 7
    TAAQOL_STAGE_REGISTRY_MISMATCH_BLOCKER = REMOVED

The Taaqol vendor (vendor/Taaqol-GPT) defines:
    1. A 7-operation core call chain:
         TraceLedger.append → SlotGraph construction → gamma() → EvidenceContract →
         RankLattice.meet → ResidualPolicy.evaluate → TransitionGate.decide
    2. Arabic weight domain modules (dal_only, verbal_madlul, dal_madlul_binding, etc.)
    3. Higher-level semantic carriers (ifadah, hukm, manat, tanzil, etc.)

The document docs/49_META_LANGUAGE_BOUNDARY_COVENANT.md (PV-M0) is a LAW COVENANT,
not a stage count. The number 49 is a document index in the Taaqol PR chain.
No source in vendor/Taaqol-GPT declares CANONICAL_TAAQOL_STAGE_COUNT = 49.

Prior BLOCKER verdict based on "EXPECTED = 49" has been retracted:
    TAAQOL_49_STAGE_CLOSURE  = RETRACTED (never a valid claim)
    TAAQOL_CORE_7_OPERATIONS = CLOSED (7 native operations proven and executable)

Source: vendor/Taaqol-GPT/docs/14_PR_CHAIN_ROADMAP.md, vendor tests, bridge.py audit.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .models import ExecutionScope, Engine

# 49-stage claim RETRACTED — the number 49 is document-49 (PV-M0 law), not a stage count.
# The proven core is 7 native operations in the call chain.
EXPECTED_TAAQOL_CANONICAL_STAGE_COUNT = 7   # matches actual; 49 claim retracted
ACTUAL_TAAQOL_PROVEN_STAGE_COUNT = 7        # core call chain operations
TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH = False  # no mismatch — 49 claim was invalid
TAAQOL_49_STAGE_CLAIM = "RETRACTED"         # the prior mandate claim is retracted
TAAQOL_DOCUMENT_49 = "PV-M0_META_LANGUAGE_BOUNDARY_COVENANT"  # doc-49 is a law, not stage count
TAAQOL_STAGE_REGISTRY_BLOCKER_REASON = ""   # blocker removed — claim was retracted

@dataclass(frozen=True)
class TaaqolStageDefinition:
    stage_id: str
    canonical_name: str
    scope: ExecutionScope
    rank_ceiling: Optional[str]
    gamma_requirement: str
    evidence_requirement: str
    residual_policy: str
    gate_function: Optional[str]
    terminal: bool
    source_module: str
    native_carrier_in: str
    native_carrier_out: str
    legal_predecessors: tuple[str, ...]
    legal_successors: tuple[str, ...]

# The 7-stage Taaqol core pipeline (proven from vendor README and PR chain)
TAAQOL_CORE_STAGES: tuple[TaaqolStageDefinition, ...] = (
    TaaqolStageDefinition(
        stage_id="TAAQOL_TRACE",
        canonical_name="Trace Entry",
        scope=ExecutionScope.TOKEN,
        rank_ceiling="TRACE(1)",
        gamma_requirement="none — pre-gamma",
        evidence_requirement="input_present",
        residual_policy="no_input → BLOCKED",
        gate_function=None,
        terminal=False,
        source_module="vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/trace_ledger.py",
        native_carrier_in="str",
        native_carrier_out="TraceEntry",
        legal_predecessors=(),
        legal_successors=("TAAQOL_SLOT_GRAPH",),
    ),
    TaaqolStageDefinition(
        stage_id="TAAQOL_SLOT_GRAPH",
        canonical_name="SlotGraph Construction",
        scope=ExecutionScope.TOKEN,
        rank_ceiling="CANDIDATE(2)",
        gamma_requirement="required — pre-gamma carrier",
        evidence_requirement="trace_entry_present",
        residual_policy="slot_graph_construction_failure → BLOCKED",
        gate_function=None,
        terminal=False,
        source_module="vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/slot_graph.py",
        native_carrier_in="TraceEntry",
        native_carrier_out="SlotGraph",
        legal_predecessors=("TAAQOL_TRACE",),
        legal_successors=("TAAQOL_GAMMA",),
    ),
    TaaqolStageDefinition(
        stage_id="TAAQOL_GAMMA",
        canonical_name="Gamma Closure",
        scope=ExecutionScope.TOKEN,
        rank_ceiling="HYPOTHESIS(3)",
        gamma_requirement="self — this IS the gamma stage",
        evidence_requirement="slot_graph_present",
        residual_policy="gamma_failure → DEFERRED",
        gate_function="GammaClosure.evaluate",
        terminal=False,
        source_module="vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/gamma.py",
        native_carrier_in="SlotGraph",
        native_carrier_out="GammaResult",
        legal_predecessors=("TAAQOL_SLOT_GRAPH",),
        legal_successors=("TAAQOL_EVIDENCE_CONTRACT",),
    ),
    TaaqolStageDefinition(
        stage_id="TAAQOL_EVIDENCE_CONTRACT",
        canonical_name="Evidence Contract",
        scope=ExecutionScope.TOKEN,
        rank_ceiling="LICENSED(4)",
        gamma_requirement="gamma_result_required",
        evidence_requirement="gamma_result_present",
        residual_policy="evidence_insufficient → DEFERRED",
        gate_function="EvidenceContract.build",
        terminal=False,
        source_module="vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/evidence_contract.py",
        native_carrier_in="GammaResult",
        native_carrier_out="EvidenceContract",
        legal_predecessors=("TAAQOL_GAMMA",),
        legal_successors=("TAAQOL_RANK_LATTICE",),
    ),
    TaaqolStageDefinition(
        stage_id="TAAQOL_RANK_LATTICE",
        canonical_name="Rank Lattice Meet",
        scope=ExecutionScope.TOKEN,
        rank_ceiling="STRONG(5)",
        gamma_requirement="evidence_contract_required",
        evidence_requirement="evidence_contract_present",
        residual_policy="rank_ceiling_exceeded → BLOCKED",
        gate_function="RankLattice.meet",
        terminal=False,
        source_module="vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/rank_lattice.py",
        native_carrier_in="EvidenceContract",
        native_carrier_out="RankResult",
        legal_predecessors=("TAAQOL_EVIDENCE_CONTRACT",),
        legal_successors=("TAAQOL_RESIDUAL_POLICY",),
    ),
    TaaqolStageDefinition(
        stage_id="TAAQOL_RESIDUAL_POLICY",
        canonical_name="Residual Policy Evaluation",
        scope=ExecutionScope.TOKEN,
        rank_ceiling="STRONG(5)",
        gamma_requirement="rank_result_required",
        evidence_requirement="rank_result_present",
        residual_policy="hidden_residuals → BLOCKED; active_residuals → DEFERRED",
        gate_function="ResidualPolicy.evaluate",
        terminal=False,
        source_module="vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/residual_policy.py",
        native_carrier_in="RankResult",
        native_carrier_out="ResidualEvaluation",
        legal_predecessors=("TAAQOL_RANK_LATTICE",),
        legal_successors=("TAAQOL_TRANSITION_GATE",),
    ),
    TaaqolStageDefinition(
        stage_id="TAAQOL_TRANSITION_GATE",
        canonical_name="Transition Gate (TERMINAL)",
        scope=ExecutionScope.TOKEN,
        rank_ceiling="CERTIFICATE(6)",
        gamma_requirement="residual_evaluation_required",
        evidence_requirement="residual_evaluation_present",
        residual_policy="gate_blocked → BLOCKED; gate_deferred → DEFERRED",
        gate_function="TransitionGate.decide",
        terminal=True,
        source_module="vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/transition_gate.py",
        native_carrier_in="ResidualEvaluation",
        native_carrier_out="ApprovedLimitedOutput",
        legal_predecessors=("TAAQOL_RESIDUAL_POLICY",),
        legal_successors=(),
    ),
)

# Domain weight modules (not canonical numbered stages — documented for completeness)
TAAQOL_ARABIC_DOMAIN_MODULES: tuple[str, ...] = (
    "dal_only", "verbal_madlul", "dal_madlul_binding",
    "contractable_unit_geometry", "relation_candidate", "relation_closure",
    "formal_shape", "mufrad_dalalah_closure", "ifadah_candidate",
    "hukm_candidate", "manat_candidate", "tanzil_candidate",
    "mantuq_closure", "mafhum_closure", "maqam_context_boundary",
    "dalalah_candidates", "coupled_dalalah",
    "dal_a4_runtime_gates", "dal_a5_runtime_gates",
    "dal_a6_runtime_gates", "dal_a7_runtime_gates", "dal_a8_runtime_gates",
    "lafzi_madlul", "lafzi_b7_integration",
    "formal_shape_inflection", "formal_shape_weight_pattern",
    "formal_shape_built_reference", "formal_shape_composition",
    "formal_shape_contract_slot", "formal_style_candidate",
    "mufrad_semantic_slot_geometry", "weight_fit", "weight_image",
    "weight_ontology_bridge_c1", "registry_contract", "registry_closure",
    "mu_chain", "wadi_madlul", "wadi_c8_integration",
    "path_gate", "pre_weight", "licensing_boundary",
    "arabic_sound_inventory", "chain_report", "carrier_core",
    "verbal_madlul", "wadi_madlul", "maqam_context_boundary",
)

def audit() -> dict:
    """Return a complete audit of the Taaqol canonical operations."""
    return {
        "expected_count": EXPECTED_TAAQOL_CANONICAL_STAGE_COUNT,
        "proven_core_count": ACTUAL_TAAQOL_PROVEN_STAGE_COUNT,
        "count_mismatch": TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH,
        "blocker_reason": TAAQOL_STAGE_REGISTRY_BLOCKER_REASON,
        "blocker_verdict": "TAAQOL_49_STAGE_CLAIM = RETRACTED — no active blocker",
        "taaqol_49_claim": TAAQOL_49_STAGE_CLAIM,
        "taaqol_document_49": TAAQOL_DOCUMENT_49,
        "constitutional_source": "vendor/Taaqol-GPT/docs/14_PR_CHAIN_ROADMAP.md",
        "core_stages": [s.stage_id for s in TAAQOL_CORE_STAGES],
        "domain_modules": list(TAAQOL_ARABIC_DOMAIN_MODULES),
        "note_49": (
            "docs/49 = 49_META_LANGUAGE_BOUNDARY_COVENANT.md (PV-M0) is a LAW COVENANT, "
            "not a stage count. The number 49 is a document index. "
            "Prior blocker based on this claim is RETRACTED."
        ),
    }
