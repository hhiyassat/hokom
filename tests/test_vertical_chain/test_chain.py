from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from pipeline.vertical_chain.chain import build_ifadah, build_hukm, build_answer_audit
from pipeline.vertical_chain.models import (
    IfadahVerdict, HukmVerdict, AnswerAuditVerdict
)

def test_ifadah_deferred_without_closed_relations():
    ifadah = build_ifadah(
        clause_id="AD-C01",
        relation_refs=(),
        closed_relations=[],
        evidence_ids=(),
    )
    assert ifadah.verdict == IfadahVerdict.IFADAH_DEFERRED
    assert "NO_CLOSED_RELATIONS" in ifadah.active_residuals

def test_hukm_deferred_without_licensed_ifadah():
    ifadah = build_ifadah("AD-C01", (), [], ())
    hukm = build_hukm(ifadah)
    assert hukm.verdict == HukmVerdict.HUKM_DEFERRED
    assert "IFADAH_NOT_APPROVED" in hukm.residuals

def test_hukm_constitutional_note():
    ifadah = build_ifadah("AD-C01", (), [], ())
    hukm = build_hukm(ifadah)
    assert "LINGUISTIC" in hukm.constitutional_note or "FIQH" in hukm.constitutional_note

def test_answer_audit_blocked_on_forbidden_leap():
    audit = build_answer_audit(
        chain_items=[],
        forbidden_leaps_found=["DIRECT_TOKEN_TO_IFADAH"],
        unresolved_residuals=[],
    )
    assert audit.verdict == AnswerAuditVerdict.ANSWER_AUDIT_BLOCKED
    assert "FORBIDDEN_LEAP_DETECTED" in audit.stop_reason

def test_answer_audit_deferred_on_residuals():
    audit = build_answer_audit([], [], ["UNRESOLVED_ROOT"])
    assert audit.verdict == AnswerAuditVerdict.ANSWER_AUDIT_DEFERRED

def test_answer_audit_approved_when_clean():
    audit = build_answer_audit([], [], [])
    assert audit.verdict == AnswerAuditVerdict.ANSWER_AUDIT_APPROVED
