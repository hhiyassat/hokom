"""Typed downstream stage outcome — preserves REFUSED information.

Prior to Wave06 every downstream adapter collapsed a vendor typed
REFUSED result into an indistinguishable `None`. The independent
audit (QIYAS-TAAQOL-MAXIMUM-NATIVE-CLOSURE-INDEPENDENT-AUDIT-01)
flagged this as a locally-closeable defect because callers could
neither classify the refusal (DEFER vs BLOCK) nor recover the
vendor's `failure_code`, `trace_ref`, or residuals.

This module introduces the immutable Hokom bridge result required
by campaign §4 (REPAIR B). Every downstream stage — Hukm, Manat,
Tanzil, Tanzil-audit-bridge, Mantuq, Mafhum — can now expose the
full native verdict alongside a Hokom-side classification.

The classification (`ACCEPT` / `DEFER` / `BLOCK`) is derived from
the vendor `failure_code` per the discipline documented in campaign
§4. Unclassified refusals default to `DEFER` and carry an explicit
`unknown_failure` marker so the residual is never silent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# ── Classification vocabulary ──────────────────────────────────────────────

ACCEPT = "ACCEPT"
DEFER = "DEFER"
BLOCK = "BLOCK"

_ACCEPT_STATES = frozenset({"PROVEN", "SURFACED"})


# Vendor FailureCodes that indicate missing/insufficient
# predecessor or evidence — these classify as DEFER.
_DEFER_CODES: frozenset[str] = frozenset({
    "NO_HUKM", "NO_MANAT", "NO_IFADAH", "NO_RELATION_CLOSURE",
    "NO_TANZIL_VERDICT", "NO_FORMAL_STYLE", "NO_SPEECH_FORCE",
    "NO_IFADAH_MAQAM", "NO_IFADAH_EVIDENCE", "NO_IFADAH_SCOPE",
    "NO_EVALUATION_DOMAIN", "NO_HUKM_CLAIM", "NO_HUKM_EVIDENCE",
    "NO_HUKM_MAQAM", "NO_MANAT_MODE", "NO_MANAT_DESCRIPTION",
    "NO_EFFECTIVE_ATTRIBUTE", "NO_MANAT_EVIDENCE", "NO_MANAT_DOMAIN",
    "NO_REALITY_EVIDENCE", "NO_INSTANCE_DESCRIPTOR",
    "NO_PRESENTATION_BOUNDARY", "NO_TANZIL_SCOPE",
    "PRESENTATION_WARNING_MISSING", "NO_MANTUQ_SCOPE",
    "NO_SPOKEN_SURFACE", "NO_MANTUQ_EVIDENCE",
    "NO_MANTUQ_CLOSURE_SCOPE",
    "NO_MAFHUM_BEFORE_MANTUQ_CLOSURE",
    "NO_MAFHUM_WITHOUT_OUTSIDE_BOUNDARY",
    "NO_MAFHUM_WITHOUT_SOURCE_DOMAIN",
    "NO_MAFHUM_WITHOUT_BRANCH_RELATION",
    "UPSTREAM_MUFRAD_DALALAH_MISSING",
    "AUDIT_PRESENTATION_ENVELOPE_MISSING",
    "AUDIT_PRESENTATION_WARNING_MISSING",
    "AUDIT_RANK_NOT_VISIBLE", "AUDIT_RESIDUALS_NOT_VISIBLE",
    "AUDIT_TRACE_NOT_VISIBLE",
    "TRACE_MISSING", "CENTER_MISSING", "BOUNDARY_MISSING",
    "DOMAIN_MISSING", "SCOPE_MISSING", "REQUIRED_SLOT_EMPTY",
    "MISSING_QARINAH_FOR_DELETION",
    "REFERENCE_WITHOUT_TRACE", "REFERENCE_BINDING_WITHOUT_SOURCE",
})


# Vendor FailureCodes that indicate invalid or prohibited structure —
# these classify as BLOCK (constitutional guard).
_BLOCK_CODES: frozenset[str] = frozenset({
    "AUTHORITY_LEAK", "EXECUTION_LEAK",
    "AUDIT_EXECUTION_LEAK", "AUDIT_AUTHORITY_LEAK",
    "AUDIT_CERTIFICATE_LEAK",
    "RANK_PROMOTION_WITHOUT_GATE", "RANK_EXCEEDS_CEILING",
    "HIDDEN_RESIDUAL", "BLOCKING_RESIDUAL_PRESENT",
    "MAFHUM_HIDDEN_RESIDUAL",
    "FORBIDDEN_STRAIGHT_LINE", "GATE_REQUIRED",
    "OUTPUT_EXCEEDS_LAYER",
    "UNLICENSED_OPENING", "UNLICENSED_ELLIPSIS",
    "TAHQIQ_OVERCLAIM", "REALITY_APPLICATION_FORBIDDEN",
    "REALITY_APPLICATION_OVERCLAIM",
    "MANTUQ_BLOCKS_MAFHUM", "MAFHUM_HUKM_LEAP",
    "MAFHUM_TANZIL_LEAP", "NO_MAFHUM_CROSS_DOMAIN_LEAP",
    "MAFHUM_BEFORE_MANTUQ",
    "MAQAM_DIVERGENCE", "MANTUQ_MAQAM_DIVERGENCE",
    "FORMAL_STYLE_CONFLICT", "DOMAIN_LEAP",
    "MANAT_MODE_COLLAPSE", "IDENTITY_BROKEN",
    "REFERENCE_RESOLVED_BY_PROBABILITY_ONLY",
    "REFERENCE_AMBIGUOUS_UNCLOSED",
    "REFERENCE_BINDING_COMPETITOR_UNHANDLED",
})


UNKNOWN_FAILURE_RESIDUAL_MARKER = "UNKNOWN_VENDOR_FAILURE_CODE"


def classify_failure(failure_code: Any) -> tuple[str, Optional[str]]:
    """Return (classification, unknown_marker_or_None).

    * ACCEPT is never returned here — callers handle PROVEN separately.
    * A recognised DEFER code → (DEFER, None).
    * A recognised BLOCK code → (BLOCK, None).
    * An unknown code → (DEFER, UNKNOWN_FAILURE_RESIDUAL_MARKER).
    * ``None`` → (DEFER, UNKNOWN_FAILURE_RESIDUAL_MARKER)
      (per §4: an unclassified REFUSED must carry an explicit
      unknown-failure residual — treating it as ACCEPT is forbidden).
    """
    if failure_code is None:
        return DEFER, UNKNOWN_FAILURE_RESIDUAL_MARKER
    code = str(getattr(failure_code, "value", failure_code))
    if code in _DEFER_CODES:
        return DEFER, None
    if code in _BLOCK_CODES:
        return BLOCK, None
    return DEFER, UNKNOWN_FAILURE_RESIDUAL_MARKER


@dataclass(frozen=True, slots=True)
class DownstreamStageOutcome:
    """Typed, immutable Hokom outcome for a single downstream stage.

    Preserves the native vendor verdict AND a Hokom-side
    classification so callers can distinguish ACCEPT / DEFER / BLOCK
    without losing `failure_code`, `trace_ref`, or residuals.

    Fields
    ------
    stage
        The stage name ("hukm" / "manat" / "tanzil" /
        "audited_tanzil_bridge" / "mantuq" / "mafhum").
    verdict_state
        The native vendor verdict state as a string
        ("PROVEN" / "REFUSED" / "SURFACED").
    classification
        The Hokom-side classification: ACCEPT / DEFER / BLOCK.
    native_verdict
        The exact vendor dataclass instance (never re-constructed,
        never a Hokom-side surrogate).
    failure_code
        The vendor FailureCode value as a string (or None on ACCEPT).
    trace_ref
        The vendor `trace_ref` string (never truncated). For
        stages that expose the trace on the verdict itself, this
        is the verdict's `trace_ref`; for stages that expose it
        only on the candidate, it's the candidate's `trace_ref`.
    residuals
        Tuple of native `Residual` objects. Empty tuple only when
        the vendor genuinely emitted no residuals.
    residual_ids
        Serialisable snapshot of residual kinds/names for the
        persisted artifact. Empty tuple when residuals is empty.
    failure_detail
        A short explanatory phrase; empty on ACCEPT. On DEFER/BLOCK
        this includes the vendor failure_code plus any Hokom-side
        unknown-failure marker.
    accepted / deferred / blocked
        Boolean shortcuts. Exactly one is True per outcome.
    """

    stage: str
    verdict_state: str
    classification: str
    native_verdict: Any
    failure_code: Optional[str]
    trace_ref: str
    residuals: tuple = ()
    residual_ids: tuple[str, ...] = ()
    failure_detail: str = ""
    accepted: bool = False
    deferred: bool = False
    blocked: bool = False

    def __post_init__(self) -> None:
        # Exactly one classification flag must be True.
        flags = (self.accepted, self.deferred, self.blocked)
        if sum(bool(f) for f in flags) != 1:
            raise ValueError(
                f"DownstreamStageOutcome: exactly one of accepted/"
                f"deferred/blocked must be True (got {flags})"
            )
        if self.classification not in (ACCEPT, DEFER, BLOCK):
            raise ValueError(
                f"DownstreamStageOutcome.classification must be "
                f"ACCEPT/DEFER/BLOCK, got {self.classification!r}"
            )
        if self.accepted and self.classification != ACCEPT:
            raise ValueError("accepted=True requires classification=ACCEPT")
        if self.deferred and self.classification != DEFER:
            raise ValueError("deferred=True requires classification=DEFER")
        if self.blocked and self.classification != BLOCK:
            raise ValueError("blocked=True requires classification=BLOCK")
        # ACCEPT must not carry a failure_code; refusal must carry one
        # unless the vendor omitted it (then failure_detail must name
        # the unknown-failure marker per §4).
        if self.accepted and self.failure_code is not None:
            raise ValueError(
                "ACCEPT outcome must have failure_code=None"
            )
        if (self.deferred or self.blocked) and self.failure_code is None \
                and UNKNOWN_FAILURE_RESIDUAL_MARKER not in self.failure_detail:
            raise ValueError(
                "REFUSED outcome without failure_code must carry the "
                "unknown-failure marker in failure_detail"
            )


def build_accept_outcome(
    *,
    stage: str,
    verdict_state: str,
    native_verdict: Any,
    trace_ref: str,
    residuals: tuple = (),
) -> DownstreamStageOutcome:
    """Construct an ACCEPT outcome (PROVEN / SURFACED verdict)."""
    if verdict_state not in _ACCEPT_STATES:
        raise ValueError(
            f"build_accept_outcome: verdict_state must be one of "
            f"{_ACCEPT_STATES}, got {verdict_state!r}"
        )
    return DownstreamStageOutcome(
        stage=stage,
        verdict_state=verdict_state,
        classification=ACCEPT,
        native_verdict=native_verdict,
        failure_code=None,
        trace_ref=trace_ref,
        residuals=tuple(residuals),
        residual_ids=tuple(_residual_id(r) for r in residuals),
        failure_detail="",
        accepted=True,
    )


def build_refused_outcome(
    *,
    stage: str,
    native_verdict: Any,
    failure_code: Any,
    trace_ref: str,
    residuals: tuple = (),
    extra_detail: str = "",
) -> DownstreamStageOutcome:
    """Construct a DEFER/BLOCK outcome from a REFUSED vendor verdict.

    Classification is derived via ``classify_failure``. Empty
    ``failure_code`` produces a DEFER carrying the explicit
    unknown-failure marker (per §4).
    """
    classification, unknown_marker = classify_failure(failure_code)
    code_str = None
    if failure_code is not None:
        code_str = str(getattr(failure_code, "value", failure_code))
    parts: list[str] = []
    if code_str is not None:
        parts.append(f"failure_code={code_str}")
    if unknown_marker is not None:
        parts.append(unknown_marker)
    if extra_detail:
        parts.append(extra_detail)
    detail = "; ".join(parts)
    return DownstreamStageOutcome(
        stage=stage,
        verdict_state="REFUSED",
        classification=classification,
        native_verdict=native_verdict,
        failure_code=code_str,
        trace_ref=trace_ref,
        residuals=tuple(residuals),
        residual_ids=tuple(_residual_id(r) for r in residuals),
        failure_detail=detail,
        deferred=(classification == DEFER),
        blocked=(classification == BLOCK),
    )


def _residual_id(r: Any) -> str:
    """Serialise a Residual to a stable id string for the artifact."""
    kind = getattr(getattr(r, "kind", None), "value",
                   getattr(r, "kind", None))
    name = getattr(r, "name", None) or getattr(r, "trace_ref", None) or ""
    if kind is None and not name:
        return repr(r)
    return f"{kind or ''}:{name}"


__all__ = [
    "ACCEPT", "DEFER", "BLOCK",
    "DownstreamStageOutcome",
    "UNKNOWN_FAILURE_RESIDUAL_MARKER",
    "build_accept_outcome",
    "build_refused_outcome",
    "classify_failure",
]
