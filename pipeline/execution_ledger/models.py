from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum  # Python 3.11+ (canonical runtime: 3.12.4)
from typing import Optional
import sys, uuid, datetime

class ExecutionScope(StrEnum):
    TOKEN = "TOKEN"
    SPAN = "SPAN"
    CLAUSE = "CLAUSE"
    SENTENCE = "SENTENCE"
    RELATION = "RELATION"
    DISCOURSE = "DISCOURSE"
    ANSWER = "ANSWER"

class Engine(StrEnum):
    HOKOM = "HOKOM"
    TAAQOL = "TAAQOL"

class StageStatus(StrEnum):
    EXECUTED_APPROVED = "EXECUTED_APPROVED"
    EXECUTED_DEFERRED = "EXECUTED_DEFERRED"
    EXECUTED_BLOCKED = "EXECUTED_BLOCKED"
    EXECUTED_INVALID = "EXECUTED_INVALID"
    NOT_OPENED = "NOT_OPENED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_APPLICABLE_AT_TOKEN_SCOPE = "NOT_APPLICABLE_AT_TOKEN_SCOPE"
    FORBIDDEN = "FORBIDDEN"
    RUNTIME_ERROR = "RUNTIME_ERROR"

@dataclass
class StageExecutionRecord:
    execution_id: str
    parent_execution_id: Optional[str]
    analysis_id: str
    stage_id: str
    stage_name: str
    engine: Engine
    scope: ExecutionScope
    subject_ref: str            # token surface, clause_id, etc.
    applicability: bool
    entered: bool
    executed: bool
    status: StageStatus
    native_executor: Optional[str]       # module path of executor
    native_carrier_in: Optional[str]     # type name of input carrier
    native_carrier_out: Optional[str]    # type name of output carrier
    input_refs: tuple[str, ...]          # evidence IDs
    output_ref: Optional[str]            # output carrier ID
    output_summary: Optional[str]        # brief human-readable
    evidence_ids: tuple[str, ...]
    active_residuals: tuple[str, ...]
    resolved_residuals: tuple[str, ...]
    gamma_state: Optional[str]
    rank_before: Optional[int]
    rank_after: Optional[int]
    gate_verdict: Optional[str]
    directive: Optional[str]             # ACCEPT / DEFER / BLOCK
    stop_reason: Optional[str]
    successor_stage: Optional[str]
    trace_ids: tuple[str, ...]
    duration_ms: Optional[float]
    error: Optional[str]

    @classmethod
    def not_opened(cls, stage_id: str, stage_name: str, engine: Engine,
                   scope: ExecutionScope, subject_ref: str,
                   analysis_id: str, reason: str) -> StageExecutionRecord:
        return cls(
            execution_id=str(uuid.uuid4()),
            parent_execution_id=None,
            analysis_id=analysis_id,
            stage_id=stage_id,
            stage_name=stage_name,
            engine=engine,
            scope=scope,
            subject_ref=subject_ref,
            applicability=True,
            entered=False,
            executed=False,
            status=StageStatus.NOT_OPENED,
            native_executor=None,
            native_carrier_in=None,
            native_carrier_out=None,
            input_refs=(),
            output_ref=None,
            output_summary=None,
            evidence_ids=(),
            active_residuals=(reason,),
            resolved_residuals=(),
            gamma_state=None,
            rank_before=None,
            rank_after=None,
            gate_verdict=None,
            directive=None,
            stop_reason=reason,
            successor_stage=None,
            trace_ids=(),
            duration_ms=None,
            error=None,
        )

    @classmethod
    def not_applicable(cls, stage_id: str, stage_name: str, engine: Engine,
                       scope: ExecutionScope, subject_ref: str,
                       analysis_id: str, reason: str = "scope_mismatch") -> StageExecutionRecord:
        rec = cls.not_opened(stage_id, stage_name, engine, scope, subject_ref, analysis_id, reason)
        object.__setattr__(rec, 'status', StageStatus.NOT_APPLICABLE)
        object.__setattr__(rec, 'applicability', False)
        return rec

    @classmethod
    def not_applicable_at_token_scope(cls, stage_id: str, stage_name: str, engine: Engine,
                                       subject_ref: str, analysis_id: str) -> StageExecutionRecord:
        rec = cls.not_opened(stage_id, stage_name, engine, ExecutionScope.TOKEN, subject_ref,
                             analysis_id, "stage_requires_span_or_higher_scope")
        object.__setattr__(rec, 'status', StageStatus.NOT_APPLICABLE_AT_TOKEN_SCOPE)
        object.__setattr__(rec, 'applicability', False)
        return rec

@dataclass
class LedgerSummary:
    analysis_id: str
    subject_ref: str
    engine: Engine
    scope: ExecutionScope
    total_stages: int
    executed_approved: int
    executed_deferred: int
    executed_blocked: int
    executed_invalid: int
    not_opened: int
    not_applicable: int
    forbidden: int
    runtime_errors: int
    highest_reached_stage: Optional[str]
    stop_reason: Optional[str]
    active_residuals: list[str]
    scope_violations: list[str]
    feature_as_stage_violations: int
    slot_as_stage_violations: int
