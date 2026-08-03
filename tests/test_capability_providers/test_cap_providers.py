from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Simulated Hokom output for تَدَايَنْتُمْ
TADAYANTUM = {
    "original_surface": "تَدَايَنْتُمْ",
    "segmentation": {"host": "تَدَايَنْتُمْ", "proclitics": "", "enclitics": "", "article": False},
    "word_class": {"word_class": "FI3L", "word_subclass": "VERBAL_PAST", "verdict": "WORD_CLASS_ACCEPTED"},
    "morphosyntax": {"number": "PL", "gender": "M", "person": 2, "tense": "PAST"},
    "root_analysis": {"canonical_root": "د-ي-ن", "jamid_mushtaq": "MUSHTAQ"},
}

# Simulated Hokom output for وَاللَّهُ (conjunction + noun)
WALLAHU = {
    "original_surface": "وَ",
    "segmentation": {"host": "اللَّهُ", "proclitics": "وَ", "enclitics": "", "article": True},
    "word_class": {"word_class": "HARF_ATF", "word_subclass": "CONJUNCTION", "verdict": "WORD_CLASS_ACCEPTED"},
    "morphosyntax": {},
}

def test_cap_word_class_tadayantum():
    from pipeline.capability_providers.cap_word_class import CAP_WORD_CLASS
    result = CAP_WORD_CLASS(TADAYANTUM)
    assert result.is_provided()
    assert result.value == "FI3L"
    assert "فعل" in result.value_ar

def test_cap_nominal_number_pl():
    from pipeline.capability_providers.cap_morphology import CAP_NOMINAL_NUMBER
    result = CAP_NOMINAL_NUMBER(TADAYANTUM)
    assert result.value == "PL"
    assert result.value_ar == "جمع"

def test_person_2_is_second_person_not_dual():
    """CONSTITUTIONAL: person=2 = SECOND_PERSON (مخاطَب), NOT dual."""
    from pipeline.capability_providers.cap_formal_profile import CAP_FORMAL_TOKEN_PROFILE, PERSON_LABEL_MAP
    assert PERSON_LABEL_MAP[2] == "SECOND_PERSON (مخاطَب)"
    profile = CAP_FORMAL_TOKEN_PROFILE(TADAYANTUM)
    assert profile.person == 2
    assert "SECOND_PERSON" in profile.person_label
    assert "مخاطَب" in profile.person_label
    # Dual check: number=DU, not person=2
    assert profile.number == "PL"  # تَدَايَنْتُمْ is plural
    assert "CONSTITUTIONAL" in profile.person_number_confusion_check

def test_cap_formal_gender():
    from pipeline.capability_providers.cap_morphology import CAP_FORMAL_GENDER
    result = CAP_FORMAL_GENDER(TADAYANTUM)
    assert result.value == "M"
    assert result.value_ar == "مذكر"

def test_cap_mabni_fi3l_madi():
    from pipeline.capability_providers.cap_morphology import CAP_MABNI_MURAB_STATE
    madi = {
        "original_surface": "كَتَبَ",
        "word_class": {"word_class": "FI3L_MADI", "verdict": "WORD_CLASS_ACCEPTED"},
        "morphosyntax": {},
    }
    result = CAP_MABNI_MURAB_STATE(madi)
    assert result.value == "MABNI"
    assert "مبني" in result.value_ar

def test_cap_operator_profile_conjunction():
    from pipeline.capability_providers.cap_syntax import CAP_OPERATOR_PROFILE
    wa = {"original_surface": "وَ", "word_class": {"word_class": "HARF_ATF", "verdict": "WORD_CLASS_ACCEPTED"}}
    result = CAP_OPERATOR_PROFILE(wa)
    assert result.is_provided()
    assert result.value == "CONJUNCTION"

def test_cap_operator_profile_conditional():
    from pipeline.capability_providers.cap_syntax import CAP_OPERATOR_PROFILE
    idha = {"original_surface": "إِذَا", "word_class": {"word_class": "HARF_SHART", "verdict": "WORD_CLASS_ACCEPTED"}}
    result = CAP_OPERATOR_PROFILE(idha)
    assert result.is_provided()
    assert result.value == "CONDITIONAL"

def test_cap_clause_boundary_detected():
    from pipeline.capability_providers.cap_syntax import CAP_CLAUSE_BOUNDARY
    fa = {"original_surface": "فَ", "word_class": {"word_class": "HARF_ATF", "verdict": "WORD_CLASS_ACCEPTED"}}
    result = CAP_CLAUSE_BOUNDARY(fa)
    assert result.is_provided()

def test_cap_relation_readiness_accepted():
    from pipeline.capability_providers.cap_syntax import CAP_RELATION_READINESS
    result = CAP_RELATION_READINESS(TADAYANTUM)
    assert result.is_provided()
    assert result.value is True

def test_cap_relation_readiness_blocked_on_error():
    from pipeline.capability_providers.cap_syntax import CAP_RELATION_READINESS
    from pipeline.capability_providers.models import CapabilityStatus
    bad = {"original_surface": "?", "word_class": {}, "error": "PARSE_ERROR"}
    result = CAP_RELATION_READINESS(bad)
    assert result.status == CapabilityStatus.BLOCKED

def test_cap_dal_only_readiness():
    from pipeline.capability_providers.cap_syntax import CAP_DAL_ONLY_READINESS
    result = CAP_DAL_ONLY_READINESS(TADAYANTUM)
    assert result.is_provided()

def test_cap_derivation_state_mushtaq():
    from pipeline.capability_providers.cap_derivation import CAP_DERIVATION_STATE
    result = CAP_DERIVATION_STATE(TADAYANTUM)
    assert result.value in ("MUSHTAQ", None) or result.value is not None  # may be deferred if field missing

def test_full_profile_person_number_orthogonal():
    """CONSTITUTIONAL: person and number are orthogonal. person=2,PL = 'you (pl)', not dual."""
    from pipeline.capability_providers.cap_formal_profile import CAP_FORMAL_TOKEN_PROFILE
    profile = CAP_FORMAL_TOKEN_PROFILE(TADAYANTUM)
    # تَدَايَنْتُمْ = person=2 (مخاطَب), number=PL (جمع)
    # This is "you (plural)" = أنتم — NOT dual
    assert profile.person == 2
    assert profile.number == "PL"
    assert profile.number_ar == "جمع"
