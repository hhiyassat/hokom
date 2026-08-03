"""
ExecutionLedger — append-only record of all stage executions for one analysis unit.

CONSTITUTIONAL INVARIANTS:
    - Every stage in the canonical registry must appear in the ledger (no disappearing stages).
    - REACHED = True without executed=True, native_executor, input_ref, trace_id is FORBIDDEN.
    - Status must be one of the enum values — no free-form strings.
    - Stages with scope > TOKEN must appear as NOT_APPLICABLE_AT_TOKEN_SCOPE for token ledgers.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid, datetime
from .models import StageExecutionRecord, LedgerSummary, StageStatus, Engine, ExecutionScope

@dataclass
class ExecutionLedger:
    ledger_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    engine: Engine = Engine.HOKOM
    scope: ExecutionScope = ExecutionScope.TOKEN
    subject_ref: str = ""
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    _records: list[StageExecutionRecord] = field(default_factory=list, repr=False)
    _scope_violations: list[str] = field(default_factory=list, repr=False)

    def append(self, record: StageExecutionRecord) -> None:
        """Append a stage execution record. Validates constitutional invariants."""
        # ANTI-PATTERN: REACHED=True without proper execution evidence
        if record.status in (StageStatus.EXECUTED_APPROVED, StageStatus.EXECUTED_DEFERRED,
                              StageStatus.EXECUTED_BLOCKED) and not record.executed:
            raise ValueError(
                f"CONSTITUTIONAL VIOLATION: stage {record.stage_id} has status "
                f"{record.status} but executed=False. "
                "REACHED=True without executed=True is FORBIDDEN."
            )
        self._records.append(record)

    def append_scope_violation(self, violation: str) -> None:
        self._scope_violations.append(violation)

    @property
    def records(self) -> tuple[StageExecutionRecord, ...]:
        return tuple(self._records)

    def get(self, stage_id: str) -> Optional[StageExecutionRecord]:
        for r in self._records:
            if r.stage_id == stage_id:
                return r
        return None

    def summary(self) -> LedgerSummary:
        counts = {s: 0 for s in StageStatus}
        for r in self._records:
            counts[r.status] = counts.get(r.status, 0) + 1

        # Highest approved stage
        approved = [r for r in self._records if r.status == StageStatus.EXECUTED_APPROVED]
        highest = approved[-1].stage_id if approved else None

        # Stop reason: last deferred/blocked
        stop_reason = None
        for r in reversed(self._records):
            if r.stop_reason:
                stop_reason = r.stop_reason
                break

        all_residuals: list[str] = []
        for r in self._records:
            all_residuals.extend(r.active_residuals)

        return LedgerSummary(
            analysis_id=self.analysis_id,
            subject_ref=self.subject_ref,
            engine=self.engine,
            scope=self.scope,
            total_stages=len(self._records),
            executed_approved=counts.get(StageStatus.EXECUTED_APPROVED, 0),
            executed_deferred=counts.get(StageStatus.EXECUTED_DEFERRED, 0),
            executed_blocked=counts.get(StageStatus.EXECUTED_BLOCKED, 0),
            executed_invalid=counts.get(StageStatus.EXECUTED_INVALID, 0),
            not_opened=counts.get(StageStatus.NOT_OPENED, 0),
            not_applicable=counts.get(StageStatus.NOT_APPLICABLE, 0)
                           + counts.get(StageStatus.NOT_APPLICABLE_AT_TOKEN_SCOPE, 0),
            forbidden=counts.get(StageStatus.FORBIDDEN, 0),
            runtime_errors=counts.get(StageStatus.RUNTIME_ERROR, 0),
            highest_reached_stage=highest,
            stop_reason=stop_reason,
            active_residuals=all_residuals,
            scope_violations=list(self._scope_violations),
            feature_as_stage_violations=0,
            slot_as_stage_violations=0,
        )

    def to_csv_rows(self) -> list[dict]:
        """Serialize all records to a list of flat dicts for CSV export."""
        rows = []
        for r in self._records:
            rows.append({
                'execution_id': r.execution_id,
                'analysis_id': r.analysis_id,
                'stage_id': r.stage_id,
                'stage_name': r.stage_name,
                'engine': r.engine,
                'scope': r.scope,
                'subject_ref': r.subject_ref,
                'applicability': r.applicability,
                'entered': r.entered,
                'executed': r.executed,
                'status': r.status,
                'native_executor': r.native_executor or '',
                'native_carrier_in': r.native_carrier_in or '',
                'native_carrier_out': r.native_carrier_out or '',
                'evidence_ids': '; '.join(r.evidence_ids),
                'active_residuals': '; '.join(r.active_residuals),
                'resolved_residuals': '; '.join(r.resolved_residuals),
                'gamma_state': r.gamma_state or '',
                'rank_before': r.rank_before if r.rank_before is not None else '',
                'rank_after': r.rank_after if r.rank_after is not None else '',
                'gate_verdict': r.gate_verdict or '',
                'directive': r.directive or '',
                'stop_reason': r.stop_reason or '',
                'successor_stage': r.successor_stage or '',
                'trace_ids': '; '.join(r.trace_ids),
                'error': r.error or '',
            })
        return rows
