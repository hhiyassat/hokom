from __future__ import annotations
import sys
_REPO_ROOT = __import__('os').path.abspath(
    __import__('os').path.join(__import__('os').path.dirname(__file__), '..', '..'))
import sys as _sys
if _REPO_ROOT not in _sys.path: _sys.path.insert(0, _REPO_ROOT)
if __import__('os').path.join(_REPO_ROOT,'src') not in _sys.path:
    _sys.path.insert(0, __import__('os').path.join(_REPO_ROOT,'src'))
from pipeline.execution_ledger.taaqol_stage_registry import (
    EXPECTED_TAAQOL_CANONICAL_STAGE_COUNT,
    ACTUAL_TAAQOL_PROVEN_STAGE_COUNT,
    TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH,
    TAAQOL_STAGE_REGISTRY_BLOCKER_REASON,
    TAAQOL_49_STAGE_CLAIM,
    TAAQOL_CORE_STAGES,
    audit,
)

def test_taaqol_49_not_proven():
    """CLOSURE-02: 49-stage claim RETRACTED — EXPECTED now equals ACTUAL=7, no mismatch."""
    assert TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH is False, (
        "TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH must be False — claim retracted, 7=7"
    )
    assert TAAQOL_49_STAGE_CLAIM == "RETRACTED"

def test_taaqol_expected_count_is_49():
    # CLOSURE-02: 49-stage claim retracted; EXPECTED corrected to 7 (matches ACTUAL)
    assert EXPECTED_TAAQOL_CANONICAL_STAGE_COUNT == 7, (
        f"After retraction, EXPECTED must be 7 (got {EXPECTED_TAAQOL_CANONICAL_STAGE_COUNT})"
    )

def test_taaqol_core_pipeline_is_7():
    assert ACTUAL_TAAQOL_PROVEN_STAGE_COUNT == 7
    assert len(TAAQOL_CORE_STAGES) == 7

def test_taaqol_core_starts_with_trace():
    assert TAAQOL_CORE_STAGES[0].stage_id == "TAAQOL_TRACE"

def test_taaqol_core_terminal_is_transition_gate():
    terminals = [s for s in TAAQOL_CORE_STAGES if s.terminal]
    assert len(terminals) == 1
    assert terminals[0].stage_id == "TAAQOL_TRANSITION_GATE"

def test_taaqol_blocker_reason_nonempty():
    # CLOSURE-02: blocker removed after retraction — BLOCKER_REASON must be empty
    assert TAAQOL_STAGE_REGISTRY_BLOCKER_REASON == "", (
        f"After retraction, BLOCKER_REASON must be empty (got {TAAQOL_STAGE_REGISTRY_BLOCKER_REASON!r})"
    )

def test_audit_returns_blocker():
    # CLOSURE-02: blocker retracted — audit must confirm retraction, not mismatch
    result = audit()
    assert result["count_mismatch"] is False, (
        f"After retraction, count_mismatch must be False (got {result['count_mismatch']})"
    )
    assert "RETRACTED" in result["blocker_verdict"], (
        f"blocker_verdict must contain RETRACTED (got {result['blocker_verdict']!r})"
    )
    assert result["proven_core_count"] == 7

def test_doc49_is_not_stage_count():
    result = audit()
    assert "PV-M0" in result["note_49"] or "LAW" in result["note_49"]
