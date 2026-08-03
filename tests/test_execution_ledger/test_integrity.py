from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from pipeline.execution_ledger.integrity import INTEGRITY_GUARD, IntegrityViolation

def test_slot_count_not_stage_count_violation():
    finding = INTEGRITY_GUARD.check_slot_count_not_stage_count(19, 19, "P1_SLOT_CANDIDATE")
    assert finding is not None
    assert finding.violation == IntegrityViolation.SLOT_COUNT_AS_STAGE_COUNT

def test_slot_count_not_stage_count_no_violation():
    finding = INTEGRITY_GUARD.check_slot_count_not_stage_count(5, 19, "P1_SLOT_CANDIDATE")
    assert finding is None

def test_feature_count_not_stage_count_violation():
    features = ["number", "gender", "person", "tense"]
    finding = INTEGRITY_GUARD.check_feature_count_not_stage_count(features, 4, "morpho")
    assert finding is not None
    assert finding.violation == IntegrityViolation.FEATURE_COUNT_AS_STAGE_COUNT

def test_no_hidden_residual_violation():
    finding = INTEGRITY_GUARD.check_no_hidden_residual(["residual_1"], False, "P5_MUFRAD")
    assert finding is not None
    assert finding.violation == IntegrityViolation.HIDDEN_RESIDUAL

def test_no_hidden_residual_no_violation():
    finding = INTEGRITY_GUARD.check_no_hidden_residual(["residual_1"], True, "P5_MUFRAD")
    assert finding is None

def test_hukm_as_fiqh_ruling_detection():
    finding = INTEGRITY_GUARD.check_no_hukm_as_fiqh_ruling("هذا حلال", "P12")
    assert finding is not None
    assert finding.violation == IntegrityViolation.HUKM_AS_FIQH_RULING

def test_hukm_not_fiqh_ruling():
    finding = INTEGRITY_GUARD.check_no_hukm_as_fiqh_ruling("إسناد فعلي", "P12")
    assert finding is None
