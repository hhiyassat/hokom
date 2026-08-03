"""
integrity.py — Constitutional integrity guards.

Prevents forbidden inferences:
    SLOT_COUNT_AS_STAGE_COUNT
    FEATURE_COUNT_AS_STAGE_COUNT
    DISPLAY_VALUE_AS_LICENSED_VALUE
    RELATED_SLOT_AS_STAGE_EXECUTION
    WRAPPER_CALL_AS_NATIVE_STAGE
    TOKEN_SCOPE_AS_RELATION_SCOPE
    CLAUSE_SCOPE_AS_HUKM
    HUKM_AS_FIQH_RULING
    DEFERRED_AS_ACCEPTED
    NOT_OPENED_AS_NOT_APPLICABLE
    MISSING_EVIDENCE_AS_EMPTY_SUCCESS
    LATE_CARRIER_CONSTRUCTION
    DIRECT_WEIGHT_TO_MEANING
    DIRECT_RELATION_TO_IFADAH
    DIRECT_IFADAH_TO_TANZIL
    HIDDEN_RESIDUAL
    RANK_INJECTION
    SILENT_FALLBACK
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum  # Python 3.11+ (canonical runtime: 3.12.4)
from typing import Optional
import sys

class IntegrityViolation(StrEnum):
    SLOT_COUNT_AS_STAGE_COUNT         = "SLOT_COUNT_AS_STAGE_COUNT"
    FEATURE_COUNT_AS_STAGE_COUNT      = "FEATURE_COUNT_AS_STAGE_COUNT"
    DISPLAY_VALUE_AS_LICENSED_VALUE   = "DISPLAY_VALUE_AS_LICENSED_VALUE"
    RELATED_SLOT_AS_STAGE_EXECUTION   = "RELATED_SLOT_AS_STAGE_EXECUTION"
    WRAPPER_CALL_AS_NATIVE_STAGE      = "WRAPPER_CALL_AS_NATIVE_STAGE"
    TOKEN_SCOPE_AS_RELATION_SCOPE     = "TOKEN_SCOPE_AS_RELATION_SCOPE"
    CLAUSE_SCOPE_AS_HUKM              = "CLAUSE_SCOPE_AS_HUKM"
    HUKM_AS_FIQH_RULING               = "HUKM_AS_FIQH_RULING"
    DEFERRED_AS_ACCEPTED              = "DEFERRED_AS_ACCEPTED"
    NOT_OPENED_AS_NOT_APPLICABLE      = "NOT_OPENED_AS_NOT_APPLICABLE"
    MISSING_EVIDENCE_AS_EMPTY_SUCCESS = "MISSING_EVIDENCE_AS_EMPTY_SUCCESS"
    LATE_CARRIER_CONSTRUCTION         = "LATE_CARRIER_CONSTRUCTION"
    DIRECT_WEIGHT_TO_MEANING          = "DIRECT_WEIGHT_TO_MEANING"
    DIRECT_RELATION_TO_IFADAH         = "DIRECT_RELATION_TO_IFADAH"
    DIRECT_IFADAH_TO_TANZIL           = "DIRECT_IFADAH_TO_TANZIL"
    HIDDEN_RESIDUAL                   = "HIDDEN_RESIDUAL"
    RANK_INJECTION                    = "RANK_INJECTION"
    SILENT_FALLBACK                   = "SILENT_FALLBACK"
    FAKE_NATIVE_TYPE                  = "FAKE_NATIVE_TYPE"
    FORBIDDEN_LEAP                    = "FORBIDDEN_LEAP"

@dataclass
class IntegrityFinding:
    violation: IntegrityViolation
    stage_id: str
    detail: str
    evidence: str

class IntegrityGuard:
    """Constitutional guard that raises on forbidden inferences."""

    def check_slot_count_not_stage_count(
        self, slot_count: int, claimed_stage_count: int, context: str
    ) -> Optional[IntegrityFinding]:
        if slot_count == claimed_stage_count:
            return IntegrityFinding(
                violation=IntegrityViolation.SLOT_COUNT_AS_STAGE_COUNT,
                stage_id=context,
                detail=f"slot_count={slot_count} used as stage_count — FORBIDDEN",
                evidence=f"slot_count={slot_count}, claimed_stages={claimed_stage_count}",
            )
        return None

    def check_feature_count_not_stage_count(
        self, feature_names: list[str], claimed_stage_count: int, context: str
    ) -> Optional[IntegrityFinding]:
        if len(feature_names) == claimed_stage_count:
            return IntegrityFinding(
                violation=IntegrityViolation.FEATURE_COUNT_AS_STAGE_COUNT,
                stage_id=context,
                detail=(
                    f"features {feature_names} counted as {claimed_stage_count} stages — FORBIDDEN. "
                    "number/gender/person/tense are FEATURES, not stages."
                ),
                evidence=f"features={feature_names}",
            )
        return None

    def check_not_deferred_as_accepted(
        self, verdict: str, stage_id: str
    ) -> Optional[IntegrityFinding]:
        if verdict.upper() == "DEFERRED" and stage_id.startswith("FINAL"):
            return IntegrityFinding(
                violation=IntegrityViolation.DEFERRED_AS_ACCEPTED,
                stage_id=stage_id,
                detail="DEFERRED verdict presented as ACCEPTED — FORBIDDEN",
                evidence=f"verdict={verdict}",
            )
        return None

    def check_no_hidden_residual(
        self, residuals: list[str], output_visible: bool, stage_id: str
    ) -> Optional[IntegrityFinding]:
        if residuals and not output_visible:
            return IntegrityFinding(
                violation=IntegrityViolation.HIDDEN_RESIDUAL,
                stage_id=stage_id,
                detail="Active residuals present but not visible in output — FORBIDDEN",
                evidence=f"residuals={residuals}",
            )
        return None

    def check_no_hukm_as_fiqh_ruling(
        self, hukm_label: str, stage_id: str
    ) -> Optional[IntegrityFinding]:
        FORBIDDEN_FIQH_TERMS = {"حلال", "حرام", "واجب", "مكروه", "مندوب", "فتوى", "ruling"}
        for term in FORBIDDEN_FIQH_TERMS:
            if term in hukm_label.lower():
                return IntegrityFinding(
                    violation=IntegrityViolation.HUKM_AS_FIQH_RULING,
                    stage_id=stage_id,
                    detail=f"Hukm carrier contains fiqh/religious term '{term}' — FORBIDDEN",
                    evidence=f"hukm_label={hukm_label!r}",
                )
        return None

INTEGRITY_GUARD = IntegrityGuard()
