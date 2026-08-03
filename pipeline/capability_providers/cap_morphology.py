"""
cap_morphology.py — Morphological capability providers.

CRITICAL PERSON/NUMBER DISTINCTION:
    person=1 → FIRST_PERSON  (متكلم) — grammatical person
    person=2 → SECOND_PERSON (مخاطَب) — grammatical person, NOT dual
    person=3 → THIRD_PERSON  (غائب)  — grammatical person

    number=SG → مفرد (singular)
    number=DU → مثنى (dual)       ← THIS IS "dual", NOT person=2
    number=PL → جمع  (plural)

    person=2 means SECOND_PERSON (مخاطَب), NEVER dual.
    Dual = مثنى = number=DU.

These two are ORTHOGONAL:
    - person=2, number=PL = "you (pl)" (أنتم)
    - person=3, number=DU = "they (dual)" (هما)
    - person=2, number=DU = "you (dual)" (أنتما)
"""
from __future__ import annotations
from .models import CapabilityResult, CapabilityStatus

SOURCE_MODULE = "pipeline.capability_providers.cap_morphology"

# Person label map (int → formal Arabic/English label)
PERSON_MAP: dict[int, tuple[str, str]] = {
    1: ("متكلم", "FIRST_PERSON"),
    2: ("مخاطَب", "SECOND_PERSON"),
    3: ("غائب", "THIRD_PERSON"),
}

# Number label map (str → formal Arabic/English label)
NUMBER_MAP: dict[str, tuple[str, str]] = {
    "SG": ("مفرد", "SINGULAR"),
    "DU": ("مثنى", "DUAL"),
    "PL": ("جمع", "PLURAL"),
}

# Gender label map
GENDER_MAP: dict[str, tuple[str, str]] = {
    "M": ("مذكر", "MASCULINE"),
    "F": ("مؤنث", "FEMININE"),
    "COMMON": ("مشترك", "COMMON_GENDER"),
}

# Definiteness
DEFINITENESS_MAP: dict[str, tuple[str, str]] = {
    "DEF": ("معرفة", "DEFINITE"),
    "INDEF": ("نكرة", "INDEFINITE"),
    "CONSTRUCT": ("مضاف", "CONSTRUCT_STATE"),
    "PREDICATE": ("خبر", "PREDICATE"),
}

# Mabni/Mu'rab state
MABNI_MURAB_MAP: dict[str, tuple[str, str]] = {
    "MABNI": ("مبني", "MABNI (invariable)"),
    "MURAB": ("معرب", "MURAB (inflected)"),
}

def _get_morphosyntax(hokom_result: dict) -> dict:
    return hokom_result.get("morphosyntax") or hokom_result.get("morphology") or {}

def CAP_NOMINAL_NUMBER(hokom_result: dict) -> CapabilityResult:
    """
    Extract nominal number. SG/DU/PL only.
    NEVER confuse with grammatical person (1/2/3).
    """
    morph = _get_morphosyntax(hokom_result)
    raw_number = morph.get("number")

    if raw_number is None:
        return CapabilityResult(
            capability_id="CAP_NOMINAL_NUMBER",
            status=CapabilityStatus.NOT_APPLICABLE,
            value=None, value_ar=None, value_en=None,
            evidence_ids=(), residuals=("NUMBER_NOT_IN_MORPHOSYNTAX",),
            source_module=SOURCE_MODULE,
        )

    # Normalize
    raw_number = str(raw_number).upper().strip()
    if raw_number in ("SINGULAR", "SG", "1"):
        raw_number = "SG"
    elif raw_number in ("DUAL", "DU", "2") and morph.get("person") is None:
        # number=DU only if there's no person field or it's not a verb context
        raw_number = "DU"
    elif raw_number in ("PLURAL", "PL", "3"):
        raw_number = "PL"

    # CRITICAL GUARD: if raw_number looks like a person number (int 1/2/3)
    # and there IS a person field, treat it as number=PL/SG/DU not as person
    person = morph.get("person")
    if isinstance(raw_number, str) and raw_number.isdigit():
        # This is almost certainly a confused field
        return CapabilityResult(
            capability_id="CAP_NOMINAL_NUMBER",
            status=CapabilityStatus.AMBIGUOUS,
            value=raw_number,
            value_ar=None, value_en=None,
            evidence_ids=(),
            residuals=("NUMBER_AMBIGUOUS_WITH_PERSON_FIELD",),
            source_module=SOURCE_MODULE,
        )

    ar_label, en_label = NUMBER_MAP.get(raw_number, (raw_number, raw_number))
    return CapabilityResult(
        capability_id="CAP_NOMINAL_NUMBER",
        status=CapabilityStatus.PROVIDED,
        value=raw_number,
        value_ar=ar_label,
        value_en=en_label,
        evidence_ids=(f"morphosyntax.number:{raw_number}",),
        residuals=(),
        source_module=SOURCE_MODULE,
    )

def CAP_FORMAL_GENDER(hokom_result: dict) -> CapabilityResult:
    """Extract formal gender (M/F/COMMON)."""
    morph = _get_morphosyntax(hokom_result)
    raw_gender = morph.get("gender")

    if raw_gender is None:
        return CapabilityResult(
            capability_id="CAP_FORMAL_GENDER",
            status=CapabilityStatus.NOT_APPLICABLE,
            value=None, value_ar=None, value_en=None,
            evidence_ids=(), residuals=("GENDER_NOT_IN_MORPHOSYNTAX",),
            source_module=SOURCE_MODULE,
        )

    raw_gender = str(raw_gender).upper().strip()
    if raw_gender in ("MALE", "MASC", "MASCULINE"):
        raw_gender = "M"
    elif raw_gender in ("FEMALE", "FEM", "FEMININE"):
        raw_gender = "F"

    ar_label, en_label = GENDER_MAP.get(raw_gender, (raw_gender, raw_gender))
    return CapabilityResult(
        capability_id="CAP_FORMAL_GENDER",
        status=CapabilityStatus.PROVIDED,
        value=raw_gender,
        value_ar=ar_label,
        value_en=en_label,
        evidence_ids=(f"morphosyntax.gender:{raw_gender}",),
        residuals=(),
        source_module=SOURCE_MODULE,
    )

def CAP_DEFINITENESS(hokom_result: dict) -> CapabilityResult:
    """Extract definiteness state (DEF/INDEF/CONSTRUCT)."""
    morph = _get_morphosyntax(hokom_result)
    seg = hokom_result.get("segmentation", {})

    # Check for article in segmentation
    has_article = seg.get("article") is True or seg.get("article") == "True"
    definiteness = morph.get("definiteness") or morph.get("state")

    if has_article and not definiteness:
        definiteness = "DEF"

    if not definiteness:
        return CapabilityResult(
            capability_id="CAP_DEFINITENESS",
            status=CapabilityStatus.DEFERRED,
            value=None, value_ar=None, value_en=None,
            evidence_ids=(), residuals=("DEFINITENESS_UNDETERMINED",),
            source_module=SOURCE_MODULE,
        )

    definiteness = str(definiteness).upper().strip()
    if definiteness in ("DEFINITE", "DEF"):
        definiteness = "DEF"
    elif definiteness in ("INDEFINITE", "INDEF", "NAKED"):
        definiteness = "INDEF"
    elif definiteness in ("CONSTRUCT", "MUDAF", "MUDAAF"):
        definiteness = "CONSTRUCT"

    ar_label, en_label = DEFINITENESS_MAP.get(definiteness, (definiteness, definiteness))
    evidence = [f"morphosyntax.definiteness:{definiteness}"]
    if has_article:
        evidence.append("segmentation.article:True")

    return CapabilityResult(
        capability_id="CAP_DEFINITENESS",
        status=CapabilityStatus.PROVIDED,
        value=definiteness,
        value_ar=ar_label,
        value_en=en_label,
        evidence_ids=tuple(evidence),
        residuals=(),
        source_module=SOURCE_MODULE,
    )

def CAP_MABNI_MURAB_STATE(hokom_result: dict) -> CapabilityResult:
    """Extract mabni/mu'rab (invariable/inflected) state."""
    morph = _get_morphosyntax(hokom_result)
    wc = hokom_result.get("word_class", {})
    word_class = wc.get("word_class") or ""

    # Particles are always mabni
    MABNI_CLASSES = {"HARF", "DAMIR", "DAMIR_MUNFASIL", "DAMIR_MUTTASIL", "ISM_ISHARAH", "ISM_MAWSOOL"}
    if any(word_class.startswith(mc) for mc in MABNI_CLASSES):
        return CapabilityResult(
            capability_id="CAP_MABNI_MURAB_STATE",
            status=CapabilityStatus.PROVIDED,
            value="MABNI",
            value_ar="مبني",
            value_en="MABNI (invariable)",
            evidence_ids=(f"word_class:{word_class}:always_mabni",),
            residuals=(),
            source_module=SOURCE_MODULE,
        )

    # Verbs: past and imperative are generally mabni; mudari' is murab (unless jussive/majzoom)
    if word_class in ("FI3L_MADI", "FI3L_AMR"):
        return CapabilityResult(
            capability_id="CAP_MABNI_MURAB_STATE",
            status=CapabilityStatus.PROVIDED,
            value="MABNI",
            value_ar="مبني",
            value_en="MABNI (invariable)",
            evidence_ids=(f"word_class:{word_class}:mabni_by_rule",),
            residuals=(),
            source_module=SOURCE_MODULE,
        )

    mabni_murab = morph.get("mabni_murab") or morph.get("case_type")
    if not mabni_murab:
        return CapabilityResult(
            capability_id="CAP_MABNI_MURAB_STATE",
            status=CapabilityStatus.DEFERRED,
            value=None, value_ar=None, value_en=None,
            evidence_ids=(), residuals=("MABNI_MURAB_UNDETERMINED",),
            source_module=SOURCE_MODULE,
        )

    mabni_murab = str(mabni_murab).upper()
    ar_label, en_label = MABNI_MURAB_MAP.get(mabni_murab, (mabni_murab, mabni_murab))
    return CapabilityResult(
        capability_id="CAP_MABNI_MURAB_STATE",
        status=CapabilityStatus.PROVIDED,
        value=mabni_murab,
        value_ar=ar_label,
        value_en=en_label,
        evidence_ids=(f"morphosyntax.mabni_murab:{mabni_murab}",),
        residuals=(),
        source_module=SOURCE_MODULE,
    )

def CAP_INFLECTION_STATE(hokom_result: dict) -> CapabilityResult:
    """
    Extract inflection state (case/mood markers).
    Separate from morphosyntax: morphosyntax gives feature values;
    inflection_state gives the formal irab marking.

    Returns: MARFOO3 / MANSOOB / MAJROOR / MAJZOOM / MABNI
    """
    morph = _get_morphosyntax(hokom_result)
    case = morph.get("case") or morph.get("irab")

    IRAB_MAP = {
        "NOM": ("مرفوع", "MARFOO3"),
        "NOMINATIVE": ("مرفوع", "MARFOO3"),
        "MARFOO3": ("مرفوع", "MARFOO3"),
        "ACC": ("منصوب", "MANSOOB"),
        "ACCUSATIVE": ("منصوب", "MANSOOB"),
        "MANSOOB": ("منصوب", "MANSOOB"),
        "GEN": ("مجرور", "MAJROOR"),
        "GENITIVE": ("مجرور", "MAJROOR"),
        "MAJROOR": ("مجرور", "MAJROOR"),
        "JUS": ("مجزوم", "MAJZOOM"),
        "JUSSIVE": ("مجزوم", "MAJZOOM"),
        "MAJZOOM": ("مجزوم", "MAJZOOM"),
    }

    if not case:
        return CapabilityResult(
            capability_id="CAP_INFLECTION_STATE",
            status=CapabilityStatus.DEFERRED,
            value=None, value_ar=None, value_en=None,
            evidence_ids=(), residuals=("IRAB_CASE_UNDETERMINED",),
            source_module=SOURCE_MODULE,
        )

    case_upper = str(case).upper()
    if case_upper in IRAB_MAP:
        ar_label, en_label = IRAB_MAP[case_upper]
        return CapabilityResult(
            capability_id="CAP_INFLECTION_STATE",
            status=CapabilityStatus.PROVIDED,
            value=en_label,
            value_ar=ar_label,
            value_en=en_label,
            evidence_ids=(f"morphosyntax.case:{case}",),
            residuals=(),
            source_module=SOURCE_MODULE,
        )

    return CapabilityResult(
        capability_id="CAP_INFLECTION_STATE",
        status=CapabilityStatus.AMBIGUOUS,
        value=case,
        value_ar=None, value_en=None,
        evidence_ids=(f"morphosyntax.case:{case}",),
        residuals=("IRAB_CASE_UNRECOGNIZED",),
        source_module=SOURCE_MODULE,
    )
