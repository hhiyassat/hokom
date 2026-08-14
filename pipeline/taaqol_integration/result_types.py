"""
Canonical typed result bundle for the FULL-TARGET Taaqol orchestration.

Purpose
-------
Every stage the Full-Target orchestrator visits is recorded as a
StageExecutionRecord.  Every run produces exactly one TaaqolFullRunResult.

Design invariants (enforced by the orchestrator + tests):
    - Frozen dataclasses; no post-hoc mutation.
    - No stage record with execution_status=EXECUTED may have empty
      provenance_ids or empty trace_ids.
    - Every BLOCKED / DEFERRED record MUST carry a non-empty blocker_codes.
    - Every NOT_OPENED record MUST carry a non-empty blocker_codes reason.
    - The orchestrator never reads or writes any file under the
      pretty-print corpus root; gold_leakage MUST remain 0.

Constitutional context
----------------------
This module reflects only the currently-ready native Taaqol logic.
It never fabricates weight-layer objects (LicensingBoundaryVerdict,
ContractableUnitGeometry, RelationCandidate, etc.).  Stages that
require inputs Hokom does not produce are honestly BLOCKED / DEFERRED.

VENDOR_SHA (Taaqol target): 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


# ── enums ─────────────────────────────────────────────────────────────────────
class ScopeType(StrEnum):
    """Constitutional scope of a stage record."""
    TOKEN = 'TOKEN'
    SPAN = 'SPAN'
    CLAUSE = 'CLAUSE'
    SENTENCE = 'SENTENCE'
    DOCUMENT = 'DOCUMENT'
    REPOSITORY_ACCOUNTING = 'REPOSITORY_ACCOUNTING'


class ExecutionStatus(StrEnum):
    """
    Honest classification of what the stage did.

    EXECUTED         — vendor code ran, produced a typed output
    BLOCKED          — the stage's typed input was not producible
    DEFERRED         — stage input requires a weight-layer object Hokom
                       does not currently produce; distinct from BLOCKED
                       because the register documents it as future work
    NOT_OPENED       — the stage never started; e.g. no origin_binding_result,
                       or accounting layer not wired
    NOT_APPLICABLE   — stage does not apply to this scope
    ERROR            — vendor call raised; recorded fail-closed
    """
    EXECUTED = 'EXECUTED'
    BLOCKED = 'BLOCKED'
    DEFERRED = 'DEFERRED'
    NOT_OPENED = 'NOT_OPENED'
    NOT_APPLICABLE = 'NOT_APPLICABLE'
    ERROR = 'ERROR'


class ClosureLevel(StrEnum):
    """
    How the stage's closure is accounted for in the report.

    RUNTIME_EXECUTED   — real vendor code produced a typed output
    FAIL_CLOSED_ONLY   — stage did not open; a fail-closed verdict was recorded
    CARRIER_VALIDATED  — carrier envelope validated but downstream not opened
    LAW_ACCOUNTED      — accountably-blocked per constitutional law
    STRUCTURAL_ONLY    — structural registration only, no runtime effect
    NOT_PROVEN         — no proof available; recorded as such
    """
    RUNTIME_EXECUTED = 'RUNTIME_EXECUTED'
    FAIL_CLOSED_ONLY = 'FAIL_CLOSED_ONLY'
    CARRIER_VALIDATED = 'CARRIER_VALIDATED'
    LAW_ACCOUNTED = 'LAW_ACCOUNTED'
    STRUCTURAL_ONLY = 'STRUCTURAL_ONLY'
    NOT_PROVEN = 'NOT_PROVEN'


# ── stage record ──────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class StageExecutionRecord:
    """
    One row in the full-target ledger.

    Every stage the orchestrator visits produces exactly one of these.
    """
    stage_id: str
    stage_name: str
    scope_type: ScopeType
    scope_id: str
    owner: str
    native_symbol: str
    native_module: str
    input_type: str
    output_type: str
    execution_status: ExecutionStatus
    verdict: str | None
    rank: str | None
    evidence_ids: tuple = field(default_factory=tuple)
    provenance_ids: tuple = field(default_factory=tuple)
    trace_ids: tuple = field(default_factory=tuple)
    residual_codes: tuple = field(default_factory=tuple)
    blocker_codes: tuple = field(default_factory=tuple)
    error_code: str | None = None
    duration_ms: float = 0.0
    applicability: str = 'APPLICABLE'
    closure_level: ClosureLevel = ClosureLevel.NOT_PROVEN

    def to_dict(self) -> dict:
        return {
            'stage_id': self.stage_id,
            'stage_name': self.stage_name,
            'scope_type': str(self.scope_type),
            'scope_id': self.scope_id,
            'owner': self.owner,
            'native_symbol': self.native_symbol,
            'native_module': self.native_module,
            'input_type': self.input_type,
            'output_type': self.output_type,
            'execution_status': str(self.execution_status),
            'verdict': self.verdict,
            'rank': self.rank,
            'evidence_ids': list(self.evidence_ids),
            'provenance_ids': list(self.provenance_ids),
            'trace_ids': list(self.trace_ids),
            'residual_codes': list(self.residual_codes),
            'blocker_codes': list(self.blocker_codes),
            'error_code': self.error_code,
            'duration_ms': self.duration_ms,
            'applicability': self.applicability,
            'closure_level': str(self.closure_level),
        }


# ── run bundle ────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class TaaqolFullRunResult:
    """
    Top-level result of the Full-Target orchestrator.
    Immutable; the demo and renderers consume this bundle.
    """
    run_id: str
    target_taaqol_sha: str
    hokom_head: str
    python_version: str
    corpus_id: str
    corpus_hash: str
    registry_version: str
    registry_hash: str
    taaqol_depth: str

    stage_records: tuple             # tuple[StageExecutionRecord, ...]

    token_summaries: tuple           # tuple[dict, ...]
    span_summaries: tuple            # tuple[dict, ...]
    sentence_summaries: tuple        # tuple[dict, ...]
    r1_r7_records: tuple             # tuple[StageExecutionRecord, ...]

    # Summary counters (all denominators explicit in the report)
    native_availability: dict = field(default_factory=dict)
    native_execution: dict = field(default_factory=dict)
    native_blocked: dict = field(default_factory=dict)
    native_not_applicable: dict = field(default_factory=dict)
    native_unresolved: dict = field(default_factory=dict)

    integrity_flags: dict = field(default_factory=dict)

    taaqol_ready_logic_reflected: bool = False
    full_vertical_slice_status: str = 'PARTIAL'
    target_repository_closure_status: str = 'PARTIAL'

    def to_dict(self) -> dict:
        return {
            'run_id': self.run_id,
            'target_taaqol_sha': self.target_taaqol_sha,
            'hokom_head': self.hokom_head,
            'python_version': self.python_version,
            'corpus_id': self.corpus_id,
            'corpus_hash': self.corpus_hash,
            'registry_version': self.registry_version,
            'registry_hash': self.registry_hash,
            'taaqol_depth': self.taaqol_depth,
            'stage_records': [r.to_dict() for r in self.stage_records],
            'token_summaries': list(self.token_summaries),
            'span_summaries': list(self.span_summaries),
            'sentence_summaries': list(self.sentence_summaries),
            'r1_r7_records': [r.to_dict() for r in self.r1_r7_records],
            'native_availability': dict(self.native_availability),
            'native_execution': dict(self.native_execution),
            'native_blocked': dict(self.native_blocked),
            'native_not_applicable': dict(self.native_not_applicable),
            'native_unresolved': dict(self.native_unresolved),
            'integrity_flags': dict(self.integrity_flags),
            'taaqol_ready_logic_reflected': self.taaqol_ready_logic_reflected,
            'full_vertical_slice_status': self.full_vertical_slice_status,
            'target_repository_closure_status': self.target_repository_closure_status,
        }


__all__ = [
    'ScopeType',
    'ExecutionStatus',
    'ClosureLevel',
    'StageExecutionRecord',
    'TaaqolFullRunResult',
]
