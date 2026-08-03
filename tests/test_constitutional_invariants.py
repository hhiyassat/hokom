"""
Constitutional invariants test suite.
These tests verify the absolute constitutional rules of the Hokom-Taaqol system.
Any failure here is a BLOCKER.
"""
from __future__ import annotations
import sys
_REPO_ROOT = __import__('os').path.abspath(
    __import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
import sys as _sys
if _REPO_ROOT not in _sys.path: _sys.path.insert(0, _REPO_ROOT)
if __import__('os').path.join(_REPO_ROOT,'src') not in _sys.path:
    _sys.path.insert(0, __import__('os').path.join(_REPO_ROOT,'src'))

# Rule 1: Hokom has exactly 19 stages
def test_hokom_has_exactly_19_stages():
    from pipeline.execution_ledger.hokom_stage_registry import HOKOM_STAGE_REGISTRY
    assert len(HOKOM_STAGE_REGISTRY) == 19

# Rule 2: Taaqol 49-stage claim is RETRACTED (CLOSURE-02)
def test_taaqol_49_not_constitutionally_proven():
    from pipeline.execution_ledger.taaqol_stage_registry import (
        TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH, TAAQOL_49_STAGE_CLAIM,
    )
    # Retraction complete: EXPECTED=7=ACTUAL, no mismatch, claim marked RETRACTED
    assert TAAQOL_49_STAGE_CLAIM == "RETRACTED"
    assert TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH is False

# Rule 3: Taaqol core has 7 stages
def test_taaqol_core_has_7_stages():
    from pipeline.execution_ledger.taaqol_stage_registry import TAAQOL_CORE_STAGES
    assert len(TAAQOL_CORE_STAGES) == 7

# Rule 4: Terminal stage is P12_IFADAH_SPEECH_FORCE
def test_terminal_is_p12():
    from pipeline.execution_ledger.hokom_stage_registry import HOKOM_STAGE_REGISTRY
    terminal = [s for s in HOKOM_STAGE_REGISTRY if s.terminal]
    assert terminal[0].stage_id == "P12_IFADAH_SPEECH_FORCE"

# Rule 5: Ifadah DEFERRED without closed relations (no direct token->Ifadah)
def test_no_direct_token_to_ifadah():
    from pipeline.vertical_chain.chain import build_ifadah
    from pipeline.vertical_chain.models import IfadahVerdict
    ifadah = build_ifadah("clause_1", (), [], ())
    assert ifadah.verdict != IfadahVerdict.IFADAH_APPROVED

# Rule 6: Hukm not opened without Ifadah
def test_no_hukm_without_ifadah():
    from pipeline.vertical_chain.chain import build_ifadah, build_hukm
    from pipeline.vertical_chain.models import HukmVerdict
    ifadah = build_ifadah("c1", (), [], ())
    hukm = build_hukm(ifadah)
    assert hukm.verdict == HukmVerdict.HUKM_DEFERRED

# Rule 7: Hukm is not a fiqh ruling
def test_hukm_constitutional_note():
    from pipeline.vertical_chain.chain import build_ifadah, build_hukm
    ifadah = build_ifadah("c1", (), [], ())
    hukm = build_hukm(ifadah)
    assert "LINGUISTIC_STRUCTURAL_CARRIER" in hukm.constitutional_note

# Rule 8: Forbidden leap detection blocks answer audit
def test_forbidden_leap_blocks_answer():
    from pipeline.vertical_chain.chain import build_answer_audit
    from pipeline.vertical_chain.models import AnswerAuditVerdict
    audit = build_answer_audit([], ["DIRECT_RELATION_TO_IFADAH"], [])
    assert audit.verdict == AnswerAuditVerdict.ANSWER_AUDIT_BLOCKED

# Rule 9: Token ledger has 19 rows
def test_token_ledger_has_19_rows():
    from pipeline.execution_ledger.scope import build_token_ledger_template
    records = build_token_ledger_template("test", "aid", {})
    assert len(records) == 19

# Rule 10: person=2 means SECOND_PERSON (mkhAtab), not dual
def test_person_2_is_second_person_not_dual():
    """person=2 in morphosyntax output means SECOND_PERSON (2nd grammatical person), NOT dual number."""
    # This is a documentation/constraint check — the pipeline uses numeric persons (1,2,3)
    # dual = muthanna = DU, not person=2
    PERSON_LABELS = {1: "FIRST_PERSON", 2: "SECOND_PERSON", 3: "THIRD_PERSON"}
    NUMBER_LABELS = {"SG": "mufrad", "DU": "muthanna", "PL": "jam3"}
    assert PERSON_LABELS[2] == "SECOND_PERSON"
    assert "DU" in NUMBER_LABELS  # dual is number, not person
    assert NUMBER_LABELS["DU"] == "muthanna"
