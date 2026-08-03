"""
cap_syntax.py — Syntactic capability providers.

CAP_OPERATOR_PROFILE: identifies operators (حروف, particles with structural function)
CAP_CLAUSE_BOUNDARY: detects clause boundary markers
CAP_RELATION_READINESS: signals whether token is ready for relation assignment
CAP_DAL_ONLY_READINESS: signals whether token is ready for dal-only (pre-madlul) step
"""
from __future__ import annotations
from .models import CapabilityResult, CapabilityStatus

SOURCE_MODULE = "pipeline.capability_providers.cap_syntax"

# Operators (structural function particles that mark boundaries or relations)
CONJUNCTION_OPERATORS = {"وَ", "فَ", "ثُمَّ", "أَوْ", "أَمْ", "بَلْ", "لَكِنْ"}
CONDITIONAL_OPERATORS = {"إِذَا", "إِنْ", "لَوْ", "مَتَى", "أَيَّانَ", "كُلَّمَا"}
NEGATION_OPERATORS = {"لَا", "لَمْ", "لَنْ", "لَيْسَ", "مَا", "لَاتَ"}
IMPERATIVE_OPERATORS = {"لِيَ", "لْيَ", "لِ"}
VOCATIVE_OPERATORS = {"يَا", "أَيُّهَا", "أَيَّتُهَا", "هَيَا", "أَيَا"}
PREPOSITIONS = {"فِي", "إِلَى", "مِنْ", "عَلَى", "عَنْ", "بِ", "لِ", "كَ"}
RELATIVE_OPERATORS = {"الَّذِي", "الَّتِي", "الَّذِينَ", "اللَّاتِي", "مَنْ", "مَا"}

ALL_OPERATORS = (
    CONJUNCTION_OPERATORS | CONDITIONAL_OPERATORS | NEGATION_OPERATORS |
    IMPERATIVE_OPERATORS | VOCATIVE_OPERATORS | PREPOSITIONS | RELATIVE_OPERATORS
)

def _surface_root(surface: str) -> str:
    """Strip diacritics for operator lookup."""
    import unicodedata
    return ''.join(c for c in surface if not unicodedata.category(c).startswith('M'))

def CAP_OPERATOR_PROFILE(hokom_result: dict) -> CapabilityResult:
    """Identify if this token is a structural operator and its type."""
    surface = hokom_result.get("original_surface", "")
    wc = hokom_result.get("word_class", {})
    word_class = wc.get("word_class") or ""

    bare = _surface_root(surface)

    operator_type = None
    if bare in CONJUNCTION_OPERATORS or surface in CONJUNCTION_OPERATORS:
        operator_type = "CONJUNCTION"
    elif bare in CONDITIONAL_OPERATORS or surface in CONDITIONAL_OPERATORS:
        operator_type = "CONDITIONAL"
    elif bare in NEGATION_OPERATORS or surface in NEGATION_OPERATORS:
        operator_type = "NEGATION"
    elif bare in IMPERATIVE_OPERATORS or surface in IMPERATIVE_OPERATORS:
        operator_type = "IMPERATIVE_OPERATOR"
    elif bare in VOCATIVE_OPERATORS or surface in VOCATIVE_OPERATORS:
        operator_type = "VOCATIVE"
    elif bare in PREPOSITIONS or surface in PREPOSITIONS:
        operator_type = "PREPOSITION"
    elif bare in RELATIVE_OPERATORS or surface in RELATIVE_OPERATORS:
        operator_type = "RELATIVE"
    elif word_class.startswith("HARF"):
        operator_type = f"PARTICLE:{word_class}"

    if operator_type:
        return CapabilityResult(
            capability_id="CAP_OPERATOR_PROFILE",
            status=CapabilityStatus.PROVIDED,
            value=operator_type,
            value_ar=surface,
            value_en=operator_type,
            evidence_ids=(f"surface:{surface}:operator", f"word_class:{word_class}"),
            residuals=(),
            source_module=SOURCE_MODULE,
        )

    return CapabilityResult(
        capability_id="CAP_OPERATOR_PROFILE",
        status=CapabilityStatus.NOT_APPLICABLE,
        value=None, value_ar=None, value_en=None,
        evidence_ids=(), residuals=(),
        source_module=SOURCE_MODULE,
    )

def CAP_CLAUSE_BOUNDARY(hokom_result: dict) -> CapabilityResult:
    """Detect if this token marks a clause boundary."""
    op = CAP_OPERATOR_PROFILE(hokom_result)

    BOUNDARY_TYPES = {"CONJUNCTION", "CONDITIONAL", "NEGATION", "IMPERATIVE_OPERATOR", "VOCATIVE", "RELATIVE"}

    if op.is_provided() and op.value in BOUNDARY_TYPES:
        return CapabilityResult(
            capability_id="CAP_CLAUSE_BOUNDARY",
            status=CapabilityStatus.PROVIDED,
            value=op.value,
            value_ar=op.value_ar,
            value_en=f"CLAUSE_BOUNDARY:{op.value}",
            evidence_ids=op.evidence_ids,
            residuals=(),
            source_module=SOURCE_MODULE,
        )

    return CapabilityResult(
        capability_id="CAP_CLAUSE_BOUNDARY",
        status=CapabilityStatus.NOT_APPLICABLE,
        value=None, value_ar=None, value_en=None,
        evidence_ids=(), residuals=(),
        source_module=SOURCE_MODULE,
    )

def CAP_RELATION_READINESS(hokom_result: dict) -> CapabilityResult:
    """
    Signal whether this token is ready for relation assignment.
    Requires: word_class known + mabni/murab or functional classification.
    NOT ready: unknown word class, error in pipeline, deferred root.
    """
    wc = hokom_result.get("word_class", {})
    word_class = wc.get("word_class")
    verdict = wc.get("verdict", "")
    error = hokom_result.get("error")

    if error:
        return CapabilityResult(
            capability_id="CAP_RELATION_READINESS",
            status=CapabilityStatus.BLOCKED,
            value=False, value_ar="غير جاهز", value_en="NOT_READY",
            evidence_ids=(), residuals=(f"PIPELINE_ERROR:{error}",),
            source_module=SOURCE_MODULE,
        )

    if not word_class or word_class == "UNKNOWN" or "ACCEPT" not in verdict.upper():
        return CapabilityResult(
            capability_id="CAP_RELATION_READINESS",
            status=CapabilityStatus.DEFERRED,
            value=False, value_ar="مؤجل", value_en="DEFERRED",
            evidence_ids=(), residuals=("WORD_CLASS_NOT_ACCEPTED",),
            source_module=SOURCE_MODULE,
        )

    return CapabilityResult(
        capability_id="CAP_RELATION_READINESS",
        status=CapabilityStatus.PROVIDED,
        value=True,
        value_ar="جاهز للعلاقة",
        value_en="READY_FOR_RELATION",
        evidence_ids=(f"word_class:{word_class}:accepted",),
        residuals=(),
        source_module=SOURCE_MODULE,
    )

def CAP_DAL_ONLY_READINESS(hokom_result: dict) -> CapabilityResult:
    """
    Signal whether token is ready for the dal-only (pre-madlul) step.
    This is BEFORE any semantic step. Requires only formal identity.
    """
    wc = hokom_result.get("word_class", {})
    word_class = wc.get("word_class")
    error = hokom_result.get("error")

    if error:
        return CapabilityResult(
            capability_id="CAP_DAL_ONLY_READINESS",
            status=CapabilityStatus.BLOCKED,
            value=False, value_ar="مانع", value_en="BLOCKED",
            evidence_ids=(), residuals=(f"PIPELINE_ERROR:{error}",),
            source_module=SOURCE_MODULE,
        )

    if word_class and word_class != "UNKNOWN":
        return CapabilityResult(
            capability_id="CAP_DAL_ONLY_READINESS",
            status=CapabilityStatus.PROVIDED,
            value=True,
            value_ar="جاهز للدال",
            value_en="READY_FOR_DAL_ONLY",
            evidence_ids=(f"word_class:{word_class}",),
            residuals=(),
            source_module=SOURCE_MODULE,
        )

    return CapabilityResult(
        capability_id="CAP_DAL_ONLY_READINESS",
        status=CapabilityStatus.DEFERRED,
        value=False, value_ar="مؤجل", value_en="DEFERRED",
        evidence_ids=(), residuals=("WORD_CLASS_MISSING",),
        source_module=SOURCE_MODULE,
    )
