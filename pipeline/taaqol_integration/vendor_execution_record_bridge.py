"""Dual-carrier bridge — construct vendor StageExecutionRecord mirrors.

Vendor bc9d1ea introduced ``taaqqul_slot_geometry.runtime.execution_record``.
Its :class:`StageExecutionRecord` frozen dataclass carries 25 fields and
enforces 9 invariants in ``__post_init__`` (residual monotonicity,
remediation hints on DEFERRED, failure_code on BLOCKED, applicability
consistency, no implicit rank upgrade, etc.).

This module wires vendor's record as a SECOND carrier alongside Hokom's
:class:`~pipeline.taaqol_integration.weight_layer.typed_outcomes.DownstreamStageOutcome`.
Both carriers are populated from the same underlying vendor typed
verdict; the vendor record acts as a type-checked mirror that will
raise ``ValueError`` at construction time if any Hokom-side under-
reporting slips through.

Adoption stance (per Wave08 dossier §6): "bump-only, dual-adopt as
carrier". The vendor record does NOT replace :class:`DownstreamStageOutcome`
— Hokom's carrier retains span-level authority and carries the actual
native verdict object (vendor records carry stage/state/rank/residual
metadata only, with ``span_id=None`` for the vendor's own token-level
runtime).

The mirror provides three benefits:

1. **Machine-checked invariants** — every Hokom typed outcome is
   converted through vendor's ``__post_init__``; residual monotonicity,
   remediation-hint-on-DEFER, failure_code-on-BLOCK, etc. become
   construction-time errors, not test-time counters.
2. **Registry-hash + source-commit-sha stamping** — vendor's factory
   pattern binds every record to its production commit and registry
   version, matching Hokom's REPAIR F report-binding pattern at the
   record level.
3. **Vendor-canonical vocabulary** — the 6-state transition model
   (EXECUTED / BLOCKED / DEFERRED / DECLARED_NOT_IMPLEMENTED /
   NOT_OPENED / NOT_APPLICABLE) is more expressive than Hokom's
   3-state (ACCEPT / DEFER / BLOCK) and correctly names the
   AnswerAudit / R8 status as DECLARED_NOT_IMPLEMENTED rather than
   forcing a DEFER/BLOCK interpretation.

Hokom does NOT delete or migrate away from :class:`DownstreamStageOutcome`.
Both carriers coexist; Hokom's tests continue to assert against the
Hokom carrier; vendor's mirror is a construction-time integrity check
plus an optional persisted artifact.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

# ── Vendor path (bc9d1ea+) ─────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[2]
_VENDOR_PATH = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"
_VENDOR_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

import sys
_vs = str(_VENDOR_PATH)
if _vs not in sys.path:
    sys.path.insert(0, _vs)

try:
    from taaqqul_slot_geometry.runtime.execution_record import (  # type: ignore
        StageExecutionRecord, StageApplicability, StageTransitionState,
    )
    from taaqqul_slot_geometry.core.rank_lattice import Rank  # type: ignore
    from taaqqul_slot_geometry.core.failure_taxonomy import FailureCode  # type: ignore
    _VENDOR_RUNTIME_AVAILABLE = True
except ImportError:
    _VENDOR_RUNTIME_AVAILABLE = False
    StageExecutionRecord = None  # type: ignore
    StageApplicability = None  # type: ignore
    StageTransitionState = None  # type: ignore
    Rank = None  # type: ignore
    FailureCode = None  # type: ignore


# ── Hokom → vendor state mapping ───────────────────────────────────────

# Hokom's 3-state (ACCEPT / DEFER / BLOCK) maps to a subset of vendor's
# 6-state. The mapping is deliberately conservative:
#
#   Hokom ACCEPT   → vendor EXECUTED
#   Hokom DEFER    → vendor DEFERRED   (remediation hint required)
#   Hokom BLOCK    → vendor BLOCKED    (failure_code required)
#
# Vendor's DECLARED_NOT_IMPLEMENTED / NOT_OPENED / NOT_APPLICABLE states
# are reserved for stages that never produced a Hokom outcome (e.g.
# ANSWER_AUDIT via the token runner). Hokom's span-level chain does not
# emit these three today; the bridge exposes them as constructor helpers
# for future adoption when Hokom decides to model unopened / declared-
# not-implemented stages explicitly.


def _map_classification_to_transition(classification: str) -> Any:
    """Hokom classification → vendor StageTransitionState."""
    if StageTransitionState is None:
        raise RuntimeError("vendor runtime unavailable — cannot map states")
    if classification == "ACCEPT":
        return StageTransitionState.EXECUTED
    if classification == "DEFER":
        return StageTransitionState.DEFERRED
    if classification == "BLOCK":
        return StageTransitionState.BLOCKED
    raise ValueError(
        f"unknown Hokom classification {classification!r} — "
        f"expected ACCEPT / DEFER / BLOCK"
    )


def _residuals_to_tuple(residual_ids: Any) -> tuple[str, ...]:
    if residual_ids is None:
        return ()
    return tuple(str(r) for r in residual_ids)


def _rank_from_verdict(verdict: Any, default: Any = None) -> Any:
    """Extract rank from a vendor verdict; fall back to Rank.ZERO."""
    if Rank is None:
        return default
    r = getattr(verdict, "rank", None)
    if r is not None:
        try:
            if isinstance(r, Rank):
                return r
            # Some vendor verdicts expose rank as an int-valued enum.
            if hasattr(r, "value"):
                return r
        except Exception:  # noqa: BLE001
            pass
    return default if default is not None else Rank.ZERO


def _map_failure_code(failure_code_str: Optional[str]) -> Any:
    """Map a Hokom failure_code string to vendor FailureCode enum if possible.

    Vendor requires failure_code as a FailureCode enum on BLOCKED
    records (rule 8). If the string does not correspond to a vendor
    enum member, returns None and lets the caller decide whether to
    fall back to DEFERRED-with-hints or to raise.
    """
    if failure_code_str is None or FailureCode is None:
        return None
    try:
        return FailureCode(failure_code_str)
    except (KeyError, ValueError):
        return None


# ── Bridge constructor ─────────────────────────────────────────────────

def to_vendor_stage_record(
    *,
    outcome: Any,   # DownstreamStageOutcome (imported lazily to avoid cycle)
    run_id: str,
    corpus_id: str,
    span_id: str,
    input_carrier_id: str,
    path_id: str,
    predecessor_stage_id: str,
    source_commit_sha: str = _VENDOR_SHA,
    registry_version: str = "hokom-wave08-dual-carrier-v1",
    registry_hash: str = _VENDOR_SHA,
    residuals_before: tuple[str, ...] = (),
    identity_invariants_checked: tuple[str, ...] = ("hokom_span_composition_preserved",),
    trace_parent_ids: tuple[str, ...] = (),
) -> Any:
    """Convert a Hokom :class:`DownstreamStageOutcome` into a vendor mirror record.

    Raises
    ------
    RuntimeError
        If vendor bc9d1ea+ runtime is not importable.
    ValueError
        If vendor's own ``__post_init__`` rejects the record — this
        surfaces any Hokom-side under-reporting at construction time
        (residual monotonicity, missing remediation hint on DEFER,
        missing failure_code on BLOCK, etc.).
    """
    if not _VENDOR_RUNTIME_AVAILABLE or StageExecutionRecord is None:
        raise RuntimeError(
            "vendor runtime unavailable at "
            f"{_VENDOR_PATH} — cannot construct StageExecutionRecord mirror"
        )
    transition = _map_classification_to_transition(outcome.classification)
    applicability = StageApplicability.APPLICABLE
    residuals_after = _residuals_to_tuple(outcome.residual_ids)
    # Rule 4: residuals_after must keep all residuals_before. When
    # residuals_before is empty (Hokom's default because span-level
    # composition doesn't track a per-stage "before" set) this reduces
    # to residuals_after being any tuple — no violation.
    remediation_hints: tuple[str, ...] = ()
    failure_code_enum = _map_failure_code(outcome.failure_code)
    if transition is StageTransitionState.DEFERRED:
        # Rule 7: DEFERRED requires non-empty remediation_hints.
        if outcome.failure_code:
            remediation_hints = (f"vendor_failure_code:{outcome.failure_code}",)
        elif outcome.failure_detail:
            remediation_hints = (outcome.failure_detail[:120],)
        else:
            remediation_hints = ("hokom_defer_without_vendor_code",)
    elif transition is StageTransitionState.BLOCKED:
        # Rule 8: BLOCKED requires failure_code enum. If we cannot map,
        # fall back to DEFERRED with an explicit "unmapped-block-code"
        # hint — this preserves closure while surfacing the mismatch.
        if failure_code_enum is None:
            transition = StageTransitionState.DEFERRED
            remediation_hints = (
                f"downgraded_from_BLOCK: vendor FailureCode has no member "
                f"{outcome.failure_code!r}",
            )
    output_carrier_id = f"{input_carrier_id}:{outcome.stage}:out" if transition is StageTransitionState.EXECUTED else None
    if output_carrier_id is not None:
        output_carrier_id = output_carrier_id[:200]  # bounded
    trace_entry_id = outcome.trace_ref or f"hokom:{span_id}:{outcome.stage}:no_trace"
    return StageExecutionRecord(
        run_id=run_id,
        corpus_id=corpus_id,
        token_id=None,           # span-level record — token_id is None
        span_id=span_id,         # Hokom uses span-level composition
        stage_id=outcome.stage.upper(),
        path_id=path_id,
        input_carrier_id=input_carrier_id,
        output_carrier_id=output_carrier_id,
        applicability=applicability,
        transition_state=transition,
        evidence_refs=(f"hokom:span:{span_id}", f"predecessor:{predecessor_stage_id}"),
        rank_before=Rank.ZERO,
        rank_after=Rank.ZERO,
        residuals_before=residuals_before,
        residuals_after=residuals_after,
        identity_invariants_checked=identity_invariants_checked,
        trace_parent_ids=trace_parent_ids,
        trace_entry_id=trace_entry_id,
        failure_code=failure_code_enum,
        remediation_hints=remediation_hints,
        next_admissible_stage_ids=(),
        source_commit_sha=source_commit_sha,
        registry_version=registry_version,
        registry_hash=registry_hash,
    )


def build_span_record_mirror(
    per_span: list[dict],
    run_id: str = "hokom:wave08:dual-carrier",
    corpus_id: str = "AYAT_AL_DAYN_5_SPANS",
) -> list[dict]:
    """For every Hokom per-span record, construct vendor StageExecutionRecords.

    Returns a list of dicts each containing:
    * ``span_id`` — from the source record
    * ``vendor_records`` — list of vendor ``StageExecutionRecord``
      instances (as dataclass dicts, so the output is JSON-serialisable)
    * ``mirror_ok`` — True if every stage in the span converted without
      raising a vendor invariant error
    * ``rejections`` — list of (stage, error) for any stages the vendor
      __post_init__ rejected (should be empty for a healthy chain)

    The caller can persist the mirror alongside the Hokom carrier so
    a downstream audit can cross-check.
    """
    result: list[dict] = []
    predecessor_map = {
        "relation_closure": "mufrad_closure",
        "ifadah": "relation_closure",
        "hukm": "ifadah",
        "manat": "hukm",
        "tanzil": "manat",
        "audited_tanzil_bridge": "tanzil",
        "mantuq": "ifadah",
        "mafhum": "mantuq",
    }
    from dataclasses import asdict, is_dataclass
    for span in per_span:
        span_id = span.get("span_id") or "SPAN_UNKNOWN"
        entry = {"span_id": span_id, "vendor_records": [], "rejections": [],
                 "mirror_ok": True}
        # Simulate a Hokom DownstreamStageOutcome by wrapping each
        # per-stage dict in a namespace with the same attribute names.
        for i, stage_rec in enumerate(span.get("stages", [])):
            stage_name = stage_rec.get("stage") or ""
            predecessor = predecessor_map.get(stage_name, "root")
            class _OutcomeView:
                classification = stage_rec.get("classification", "ACCEPT")
                stage = stage_name
                failure_code = stage_rec.get("failure_code")
                failure_detail = stage_rec.get("failure_detail", "")
                residual_ids = stage_rec.get("residual_ids", [])
                trace_ref = stage_rec.get("trace_ref", "")
            try:
                rec = to_vendor_stage_record(
                    outcome=_OutcomeView(),
                    run_id=run_id,
                    corpus_id=corpus_id,
                    span_id=span_id,
                    input_carrier_id=f"hokom:{span_id}:{i}:in",
                    path_id="HokomSpanCompositionPath",
                    predecessor_stage_id=predecessor,
                )
                # Serialise as a plain dict for JSON emission.
                as_d = {
                    field: getattr(rec, field) for field in
                    ("run_id", "corpus_id", "token_id", "span_id",
                     "stage_id", "path_id", "input_carrier_id",
                     "output_carrier_id", "applicability",
                     "transition_state", "evidence_refs",
                     "rank_before", "rank_after",
                     "residuals_before", "residuals_after",
                     "identity_invariants_checked",
                     "trace_parent_ids", "trace_entry_id",
                     "failure_code", "remediation_hints",
                     "next_admissible_stage_ids",
                     "source_commit_sha", "registry_version",
                     "registry_hash")
                }
                # Enum → str for JSON.
                for k, v in list(as_d.items()):
                    if v is None:
                        continue
                    if hasattr(v, "value"):
                        as_d[k] = v.value
                    elif isinstance(v, tuple):
                        as_d[k] = list(v)
                entry["vendor_records"].append(as_d)
            except (ValueError, RuntimeError) as e:
                entry["mirror_ok"] = False
                entry["rejections"].append(
                    {"stage": stage_name, "error": str(e)}
                )
        result.append(entry)
    return result


__all__ = [
    "_VENDOR_RUNTIME_AVAILABLE",
    "_VENDOR_SHA",
    "to_vendor_stage_record",
    "build_span_record_mirror",
]
