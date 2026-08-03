"""
test_taaqol_correction.py — Verify TAAQOL_49_STAGE_CLAIM retracted.

CONSTITUTIONAL CORRECTION:
    TAAQOL_49_STAGE_CLAIM = RETRACTED
    TAAQOL_DOCUMENT_49 = META_LANGUAGE_BOUNDARY_COVENANT (PV-M0 law)
    TAAQOL_CANONICAL_CORE_STAGE_COUNT = 7
"""
from __future__ import annotations
import sys
_REPO_ROOT = __import__('os').path.abspath(
    __import__('os').path.join(__import__('os').path.dirname(__file__), '..', '..'))
import sys as _sys
if _REPO_ROOT not in _sys.path: _sys.path.insert(0, _REPO_ROOT)
if __import__('os').path.join(_REPO_ROOT,'src') not in _sys.path:
    _sys.path.insert(0, __import__('os').path.join(_REPO_ROOT,'src'))

from pipeline.execution_ledger.taaqol_stage_registry import (
    TAAQOL_CORE_STAGES, ACTUAL_TAAQOL_PROVEN_STAGE_COUNT,
    TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH, TAAQOL_STAGE_REGISTRY_BLOCKER_REASON,
    TAAQOL_49_STAGE_CLAIM, TAAQOL_DOCUMENT_49,
    audit,
)

TAAQOL_7_CANONICAL_STAGE_IDS = [
    "TAAQOL_TRACE",
    "TAAQOL_SLOT_GRAPH",
    "TAAQOL_GAMMA",
    "TAAQOL_EVIDENCE_CONTRACT",
    "TAAQOL_RANK_LATTICE",
    "TAAQOL_RESIDUAL_POLICY",
    "TAAQOL_TRANSITION_GATE",
]


def test_taaqol_49_claim_retracted():
    """CLOSURE-02: Retraction complete — COUNT_MISMATCH=False, claim=RETRACTED."""
    assert TAAQOL_49_STAGE_CLAIM == "RETRACTED", (
        f"TAAQOL_49_STAGE_CLAIM must be RETRACTED (got {TAAQOL_49_STAGE_CLAIM!r})"
    )
    assert TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH is False, (
        "After retraction, expected=7=actual=7, so COUNT_MISMATCH must be False"
    )


def test_taaqol_core_count_is_7():
    assert ACTUAL_TAAQOL_PROVEN_STAGE_COUNT == 7
    assert len(TAAQOL_CORE_STAGES) == 7


def test_taaqol_canonical_7_stage_ids():
    """All 7 canonical stage IDs must be present and correct."""
    actual_ids = [s.stage_id for s in TAAQOL_CORE_STAGES]
    assert actual_ids == TAAQOL_7_CANONICAL_STAGE_IDS


def test_taaqol_document_49_is_not_stage():
    """CLOSURE-02: doc-49 is PV-M0 law — stored in TAAQOL_DOCUMENT_49, not as a stage."""
    assert "PV-M0" in TAAQOL_DOCUMENT_49, (
        f"TAAQOL_DOCUMENT_49 must reference PV-M0 (got {TAAQOL_DOCUMENT_49!r})"
    )
    assert "49" not in [s.stage_id for s in TAAQOL_CORE_STAGES]


def test_taaqol_core_each_stage_has_vendor_module():
    """Each of the 7 core stages must reference the vendor/Taaqol-GPT source."""
    for stage in TAAQOL_CORE_STAGES:
        assert stage.source_module, f"{stage.stage_id} missing source_module"
        assert "taaqqul_slot_geometry" in stage.source_module, (
            f"{stage.stage_id}.source_module does not reference taaqqul_slot_geometry: {stage.source_module}"
        )


def test_taaqol_core_pipeline_chain():
    """Stages form a proper predecessor/successor chain."""
    ids = [s.stage_id for s in TAAQOL_CORE_STAGES]
    for i, stage in enumerate(TAAQOL_CORE_STAGES):
        if i == 0:
            assert stage.legal_predecessors == (), f"First stage must have no predecessors"
        else:
            assert ids[i-1] in stage.legal_predecessors, (
                f"{stage.stage_id} missing predecessor {ids[i-1]}"
            )


def test_taaqol_terminal_is_transition_gate():
    terminals = [s for s in TAAQOL_CORE_STAGES if s.terminal]
    assert len(terminals) == 1
    assert terminals[0].stage_id == "TAAQOL_TRANSITION_GATE"


def test_taaqol_no_fake_stage_padding():
    """No alias or fake stages inflating count beyond 7."""
    assert len(set(s.stage_id for s in TAAQOL_CORE_STAGES)) == 7


def test_audit_returns_correct_core_count():
    result = audit()
    assert result["proven_core_count"] == 7
    assert len(result["core_stages"]) == 7
