from __future__ import annotations
import os, sys, uuid
import pytest
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from pipeline.execution_ledger.ledger import ExecutionLedger
from pipeline.execution_ledger.models import (
    StageExecutionRecord, StageStatus, Engine, ExecutionScope
)

def make_record(stage_id="P0_UNICODE_CANDIDATE", status=StageStatus.EXECUTED_APPROVED,
                executed=True, applicability=True):
    return StageExecutionRecord(
        execution_id=str(uuid.uuid4()),
        parent_execution_id=None,
        analysis_id="test",
        stage_id=stage_id,
        stage_name="Test Stage",
        engine=Engine.HOKOM,
        scope=ExecutionScope.TOKEN,
        subject_ref="تَدَايَنْتُمْ",
        applicability=applicability,
        entered=executed,
        executed=executed,
        status=status,
        native_executor="hokom.test",
        native_carrier_in="str",
        native_carrier_out="Result",
        input_refs=("ev1",),
        output_ref="out1",
        output_summary="test output",
        evidence_ids=("ev1",),
        active_residuals=(),
        resolved_residuals=(),
        gamma_state="GAMMA_OK",
        rank_before=2,
        rank_after=4,
        gate_verdict="APPROVED",
        directive="ACCEPT",
        stop_reason=None,
        successor_stage="P0_TYPED_CODEPOINT",
        trace_ids=("t1",),
        duration_ms=1.5,
        error=None,
    )

def test_append_approved_record():
    ledger = ExecutionLedger(engine=Engine.HOKOM, scope=ExecutionScope.TOKEN)
    rec = make_record()
    ledger.append(rec)
    assert len(ledger.records) == 1

def test_constitutional_violation_raises():
    """CONSTITUTIONAL: REACHED=True without executed=True must raise."""
    ledger = ExecutionLedger()
    bad_rec = make_record(status=StageStatus.EXECUTED_APPROVED, executed=False)
    with pytest.raises(ValueError, match="CONSTITUTIONAL VIOLATION"):
        ledger.append(bad_rec)

def test_summary_counts():
    ledger = ExecutionLedger(engine=Engine.HOKOM, scope=ExecutionScope.TOKEN)
    ledger.append(make_record(stage_id="P0_UNICODE_CANDIDATE"))
    na_rec = StageExecutionRecord.not_applicable_at_token_scope(
        "P9_SENTENCE_GEOMETRY", "SG", Engine.HOKOM, "test", "test"
    )
    ledger.append(na_rec)
    s = ledger.summary()
    assert s.executed_approved == 1
    assert s.not_applicable == 1

def test_to_csv_rows():
    ledger = ExecutionLedger()
    ledger.append(make_record())
    rows = ledger.to_csv_rows()
    assert len(rows) == 1
    assert "stage_id" in rows[0]
