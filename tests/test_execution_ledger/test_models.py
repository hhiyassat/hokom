from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
import pytest, uuid
from enum import StrEnum
from pipeline.execution_ledger.models import (
    ExecutionScope, StageStatus, StageExecutionRecord, LedgerSummary, Engine
)

def test_execution_scope_values():
    assert ExecutionScope.TOKEN == "TOKEN"
    assert ExecutionScope.DISCOURSE == "DISCOURSE"

def test_stage_status_deferred_not_accepted():
    """DEFERRED must not equal EXECUTED_APPROVED."""
    assert StageStatus.EXECUTED_DEFERRED != StageStatus.EXECUTED_APPROVED

def test_not_opened_factory():
    rec = StageExecutionRecord.not_opened(
        stage_id="P0_UNICODE_CANDIDATE",
        stage_name="Unicode Candidate",
        engine=Engine.HOKOM,
        scope=ExecutionScope.TOKEN,
        subject_ref="تَدَايَنْتُمْ",
        analysis_id=str(uuid.uuid4()),
        reason="test_reason",
    )
    assert not rec.entered
    assert not rec.executed
    assert rec.status == StageStatus.NOT_OPENED
    assert rec.stop_reason == "test_reason"

def test_not_applicable_at_token_scope_factory():
    rec = StageExecutionRecord.not_applicable_at_token_scope(
        stage_id="P9_SENTENCE_GEOMETRY",
        stage_name="Sentence Geometry",
        engine=Engine.HOKOM,
        subject_ref="تَدَايَنْتُمْ",
        analysis_id=str(uuid.uuid4()),
    )
    assert rec.status == StageStatus.NOT_APPLICABLE_AT_TOKEN_SCOPE
    assert not rec.applicability


# ── R3: Native StrEnum — no backport ─────────────────────────────────────────

def test_execution_scope_is_strenum():
    """R3: ExecutionScope must subclass the native StrEnum (Python 3.11+)."""
    assert issubclass(ExecutionScope, StrEnum), (
        f"ExecutionScope({ExecutionScope.__mro__}) is not a native StrEnum subclass"
    )


def test_engine_is_strenum():
    """R3: Engine must subclass the native StrEnum (Python 3.11+)."""
    assert issubclass(Engine, StrEnum), (
        f"Engine({Engine.__mro__}) is not a native StrEnum subclass"
    )


def test_stage_status_is_strenum():
    """R3: StageStatus must subclass the native StrEnum (Python 3.11+)."""
    assert issubclass(StageStatus, StrEnum), (
        f"StageStatus({StageStatus.__mro__}) is not a native StrEnum subclass"
    )


def test_strenum_serialization_stability():
    """R3: StrEnum values are plain strings — serialization must be stable."""
    assert ExecutionScope.TOKEN == "TOKEN"
    assert str(ExecutionScope.TOKEN) == "TOKEN"
    assert Engine.HOKOM == "HOKOM"
    assert str(Engine.HOKOM) == "HOKOM"
    assert StageStatus.EXECUTED_APPROVED == "EXECUTED_APPROVED"
    assert str(StageStatus.EXECUTED_APPROVED) == "EXECUTED_APPROVED"


def test_strenum_name_semantics_stability():
    """R3: .name and .value must match (StrEnum invariant)."""
    for member in ExecutionScope:
        assert member.name == member.value
    for member in Engine:
        assert member.name == member.value
    for member in StageStatus:
        assert member.name == member.value


def test_no_local_strenum_injection():
    """R3: No production module may inject a local StrEnum backport class."""
    import pipeline.execution_ledger.models as _m
    import pipeline.execution_ledger.integrity as _i
    # StrEnum used in both modules must be the same object as enum.StrEnum
    from enum import StrEnum as _NativeStrEnum
    # The classes themselves must resolve to native StrEnum in their MRO
    assert _NativeStrEnum in ExecutionScope.__mro__
    assert _NativeStrEnum in Engine.__mro__
    assert _NativeStrEnum in StageStatus.__mro__
    from pipeline.execution_ledger.integrity import IntegrityViolation
    assert _NativeStrEnum in IntegrityViolation.__mro__
