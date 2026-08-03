"""
scope.py — Scope enforcement for execution ledger.

CONSTITUTIONAL RULE: Stages with scope > TOKEN must appear as
NOT_APPLICABLE_AT_TOKEN_SCOPE in token-level ledgers.

ANTI-PATTERNS (forbidden):
    TOKEN_SCOPE_AS_RELATION_SCOPE
    CLAUSE_SCOPE_AS_HUKM
    FEATURE_COUNT_AS_STAGE_COUNT
    SLOT_AS_STAGE
"""
from __future__ import annotations
from .models import ExecutionScope, StageStatus, StageExecutionRecord, Engine
from .hokom_stage_registry import HOKOM_STAGE_REGISTRY, HOKOM_TOKEN_STAGES, HOKOM_SPAN_OR_HIGHER_STAGES

TOKEN_SCOPE_VIOLATIONS: frozenset[str] = frozenset({
    "TOKEN_SCOPE_AS_RELATION_SCOPE",
    "CLAUSE_SCOPE_AS_HUKM",
    "FEATURE_COUNT_AS_STAGE_COUNT",
    "SLOT_AS_STAGE",
    "DISPLAY_VALUE_AS_LICENSED_VALUE",
    "RELATED_SLOT_AS_STAGE_EXECUTION",
    "WRAPPER_CALL_AS_NATIVE_STAGE",
    "DIRECT_WEIGHT_TO_MEANING",
    "DIRECT_RELATION_TO_IFADAH",
    "DIRECT_IFADAH_TO_TANZIL",
    "HIDDEN_RESIDUAL",
    "RANK_INJECTION",
    "SILENT_FALLBACK",
    "MISSING_EVIDENCE_AS_EMPTY_SUCCESS",
    "DEFERRED_AS_ACCEPTED",
    "NOT_OPENED_AS_NOT_APPLICABLE",
    "HUKM_AS_FIQH_RULING",
    "LATE_CARRIER_CONSTRUCTION",
})

def validate_token_ledger(records: list[StageExecutionRecord]) -> list[str]:
    """
    Validate a token-scope ledger.
    Returns list of violation strings.
    """
    violations = []
    stage_ids_present = {r.stage_id for r in records}

    # Check: all 19 Hokom stages must appear
    for stage in HOKOM_STAGE_REGISTRY:
        if stage.stage_id not in stage_ids_present:
            violations.append(
                f"MISSING_STAGE: {stage.stage_id} not in token ledger "
                "(all 19 Hokom stages must appear, no disappearing stages)"
            )

    # Check: higher-scope stages must be NOT_APPLICABLE_AT_TOKEN_SCOPE, not EXECUTED_*
    for record in records:
        if record.stage_id in HOKOM_SPAN_OR_HIGHER_STAGES:
            if record.status in (
                StageStatus.EXECUTED_APPROVED, StageStatus.EXECUTED_DEFERRED,
                StageStatus.EXECUTED_BLOCKED
            ):
                violations.append(
                    f"TOKEN_SCOPE_AS_RELATION_SCOPE: stage {record.stage_id} "
                    f"has scope {record.scope} but is recorded as {record.status} "
                    "in a TOKEN-scope ledger"
                )

    # Check: no REACHED=True without executed=True
    for record in records:
        if record.status in (
            StageStatus.EXECUTED_APPROVED, StageStatus.EXECUTED_DEFERRED,
            StageStatus.EXECUTED_BLOCKED
        ) and not record.executed:
            violations.append(
                f"SLOT_AS_STAGE: {record.stage_id} has executed_status "
                f"but executed=False — REACHED=True without execution is FORBIDDEN"
            )

    return violations

def build_token_ledger_template(
    surface: str,
    analysis_id: str,
    executed_stages: dict[str, dict],  # stage_id → {status, gamma_state, rank, ...}
) -> list[StageExecutionRecord]:
    """
    Build a complete 19-row token ledger.
    All stages appear; higher-scope stages → NOT_APPLICABLE_AT_TOKEN_SCOPE.
    executed_stages provides actual data for stages that ran.
    """
    from .models import StageExecutionRecord, StageStatus, Engine, ExecutionScope
    records = []
    
    for stage in HOKOM_STAGE_REGISTRY:
        sid = stage.stage_id
        
        if sid in HOKOM_SPAN_OR_HIGHER_STAGES:
            records.append(StageExecutionRecord.not_applicable_at_token_scope(
                stage_id=sid,
                stage_name=stage.canonical_name,
                engine=Engine.HOKOM,
                subject_ref=surface,
                analysis_id=analysis_id,
            ))
        elif sid in executed_stages:
            edata = executed_stages[sid]
            status = edata.get("status", StageStatus.EXECUTED_APPROVED)
            records.append(StageExecutionRecord(
                execution_id=edata.get("execution_id", __import__("uuid").uuid4().hex),
                parent_execution_id=edata.get("parent_execution_id"),
                analysis_id=analysis_id,
                stage_id=sid,
                stage_name=stage.canonical_name,
                engine=Engine.HOKOM,
                scope=ExecutionScope.TOKEN,
                subject_ref=surface,
                applicability=True,
                entered=True,
                executed=True,
                status=status,
                native_executor=stage.executor,
                native_carrier_in=stage.input_type,
                native_carrier_out=stage.output_type,
                input_refs=tuple(edata.get("evidence_ids", ())),
                output_ref=edata.get("output_ref"),
                output_summary=edata.get("output_summary"),
                evidence_ids=tuple(edata.get("evidence_ids", ())),
                active_residuals=tuple(edata.get("active_residuals", ())),
                resolved_residuals=tuple(edata.get("resolved_residuals", ())),
                gamma_state=edata.get("gamma_state"),
                rank_before=edata.get("rank_before"),
                rank_after=edata.get("rank_after"),
                gate_verdict=edata.get("gate_verdict"),
                directive=edata.get("directive"),
                stop_reason=edata.get("stop_reason"),
                successor_stage=edata.get("successor_stage"),
                trace_ids=tuple(edata.get("trace_ids", ())),
                duration_ms=edata.get("duration_ms"),
                error=edata.get("error"),
            ))
        else:
            # Stage was not opened — predecessor deferred/blocked before reaching it
            records.append(StageExecutionRecord.not_opened(
                stage_id=sid,
                stage_name=stage.canonical_name,
                engine=Engine.HOKOM,
                scope=ExecutionScope.TOKEN,
                subject_ref=surface,
                analysis_id=analysis_id,
                reason="predecessor_deferred_or_blocked",
            ))
    
    return records
