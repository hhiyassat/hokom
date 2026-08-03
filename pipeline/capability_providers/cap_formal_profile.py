"""
cap_formal_profile.py — Full formal token profile capability.

Assembles all morphological capabilities into a single typed profile.
Does NOT produce meaning. Provides: word_class, number, person, gender,
tense, definiteness, mabni/murab, inflection.

PERSON/NUMBER DISTINCTION (constitutional rule):
    person: 1=FIRST_PERSON, 2=SECOND_PERSON, 3=THIRD_PERSON
    number: SG=مفرد, DU=مثنى, PL=جمع
    person=2 ≠ dual; dual = number=DU
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .models import CapabilityResult, CapabilityStatus
from .cap_word_class import CAP_WORD_CLASS
from .cap_morphology import (
    CAP_NOMINAL_NUMBER, CAP_FORMAL_GENDER, CAP_DEFINITENESS,
    CAP_MABNI_MURAB_STATE, CAP_INFLECTION_STATE,
)
from .cap_derivation import CAP_DERIVATION_STATE, CAP_REFERENCE_FORM

SOURCE_MODULE = "pipeline.capability_providers.cap_formal_profile"

TENSE_MAP: dict[str, tuple[str, str]] = {
    "PAST": ("ماضٍ", "PAST"),
    "PRESENT": ("مضارع", "PRESENT"),
    "FUTURE": ("مستقبل", "FUTURE"),
    "IMPERATIVE": ("أمر", "IMPERATIVE"),
}

PERSON_LABEL_MAP: dict[int, str] = {
    1: "FIRST_PERSON (متكلم)",
    2: "SECOND_PERSON (مخاطَب)",   # NOT dual — person=2 = مخاطَب
    3: "THIRD_PERSON (غائب)",
}

@dataclass(frozen=True)
class FormalTokenProfile:
    surface: str
    word_class: Optional[str]
    word_class_ar: Optional[str]
    number: Optional[str]           # SG / DU / PL
    number_ar: Optional[str]        # مفرد / مثنى / جمع
    person: Optional[int]           # 1 / 2 / 3
    person_label: Optional[str]     # FIRST_PERSON / SECOND_PERSON / THIRD_PERSON
    gender: Optional[str]           # M / F / COMMON
    gender_ar: Optional[str]
    tense: Optional[str]            # PAST / PRESENT / FUTURE / IMPERATIVE
    tense_ar: Optional[str]
    definiteness: Optional[str]     # DEF / INDEF / CONSTRUCT
    definiteness_ar: Optional[str]
    mabni_murab: Optional[str]      # MABNI / MURAB
    inflection_state: Optional[str] # MARFOO3 / MANSOOB / MAJROOR / MAJZOOM
    derivation_state: Optional[str] # JAMID / MUSHTAQ
    reference_form: Optional[str]
    profile_status: CapabilityStatus
    residuals: tuple[str, ...]
    person_number_confusion_check: str  # always states the distinction

def CAP_FORMAL_TOKEN_PROFILE(hokom_result: dict) -> FormalTokenProfile:
    """
    Build complete formal token profile from Hokom result.
    """
    surface = hokom_result.get("original_surface", "")
    morph = hokom_result.get("morphosyntax") or hokom_result.get("morphology") or {}

    wc_result = CAP_WORD_CLASS(hokom_result)
    num_result = CAP_NOMINAL_NUMBER(hokom_result)
    gender_result = CAP_FORMAL_GENDER(hokom_result)
    def_result = CAP_DEFINITENESS(hokom_result)
    mabni_result = CAP_MABNI_MURAB_STATE(hokom_result)
    infl_result = CAP_INFLECTION_STATE(hokom_result)
    deriv_result = CAP_DERIVATION_STATE(hokom_result)
    ref_result = CAP_REFERENCE_FORM(hokom_result)

    # Person extraction with constitutional guard
    raw_person = morph.get("person")
    person = None
    person_label = None
    if raw_person is not None:
        try:
            p = int(raw_person)
            if p in (1, 2, 3):
                person = p
                person_label = PERSON_LABEL_MAP[p]
        except (ValueError, TypeError):
            pass

    # Tense
    raw_tense = morph.get("tense")
    tense = None
    tense_ar = None
    if raw_tense:
        tense_upper = str(raw_tense).upper()
        if tense_upper in TENSE_MAP:
            tense_ar, tense = TENSE_MAP[tense_upper]
        else:
            tense = tense_upper

    # Collect residuals
    all_residuals: list[str] = []
    for r in (wc_result, num_result, gender_result, def_result,
              mabni_result, infl_result, deriv_result, ref_result):
        all_residuals.extend(r.residuals)

    # Overall status
    if wc_result.status == CapabilityStatus.DEFERRED:
        status = CapabilityStatus.DEFERRED
    elif all_residuals:
        status = CapabilityStatus.AMBIGUOUS
    else:
        status = CapabilityStatus.PROVIDED

    return FormalTokenProfile(
        surface=surface,
        word_class=wc_result.value,
        word_class_ar=wc_result.value_ar,
        number=num_result.value,
        number_ar=num_result.value_ar,
        person=person,
        person_label=person_label,
        gender=gender_result.value,
        gender_ar=gender_result.value_ar,
        tense=tense,
        tense_ar=tense_ar,
        definiteness=def_result.value,
        definiteness_ar=def_result.value_ar,
        mabni_murab=mabni_result.value,
        inflection_state=infl_result.value,
        derivation_state=deriv_result.value,
        reference_form=ref_result.value,
        profile_status=status,
        residuals=tuple(all_residuals),
        person_number_confusion_check=(
            "CONSTITUTIONAL: person=2 means SECOND_PERSON (مخاطَب), "
            "NOT dual. Dual is number=DU (مثنى). "
            "person and number are orthogonal features."
        ),
    )
