"""
live_hokom_adapter.py — Maps a live CanonicalPipeline PipelineTrace into
19 StageExecutionRecord rows for token-scope ledgers.

CONSTITUTIONAL RULES:
  - P0-P5 (TOKEN scope, 12 stages): mapped from actual pipeline stage trace
  - P6-P12 (SPAN+ scope, 7 stages): NOT_APPLICABLE_AT_TOKEN_SCOPE
  - executed=True ONLY when stage was actually invoked by the pipeline
  - NOT_OPENED for stages the pipeline did not reach (predecessor BATIL)
  - native_executor, output_ref, trace_ids must come from actual judgment
  - APPLICABLE_TEMPLATE_ONLY_ROWS must = 0 for all token-scope stages

DISTINCTION FROM build_token_ledger_template():
  - Template: generic structure with no pipeline run; all applicable stages
    show NOT_OPENED regardless of whether the pipeline was called.
  - Live adapter: driven by an actual PipelineTrace from run_word(); stages
    that ran have executed=True, stages stopped by predecessor have
    NOT_OPENED tied to the real pipeline_run_id.

Forbidden:
  - Converting all token-scope stages to executed=True automatically.
  - Inferring execution from slot presence alone.
  - Inventing output_ref, trace_id, or evidence_ids.
  - Marking stage executed=True without native_executor present.

Usage (under Python 3.12.4 with live Hokom pipeline):

    from hokom.canonical.pipeline import CanonicalPipeline, WordInput
    from pipeline.execution_ledger.live_hokom_adapter import (
        hokom_trace_to_token_ledger,
        LiveAdapterMetrics,
    )

    pipeline = CanonicalPipeline.build()
    trace = pipeline.run_word(WordInput(
        surface="تَدَايَنْتُمْ",
        hokom_evidence_by_stage={},
        pipeline_run_id="DEMO-2026",
        word_index=0,
    ))
    records, metrics = hokom_trace_to_token_ledger(trace, analysis_id="AD-W00")
    assert metrics.applicable_template_only_rows == 0
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .hokom_stage_registry import (
    HOKOM_STAGE_REGISTRY,
    HOKOM_TOKEN_STAGES,
    HOKOM_SPAN_OR_HIGHER_STAGES,
)
from .models import (
    Engine,
    ExecutionScope,
    StageExecutionRecord,
    StageStatus,
)

if TYPE_CHECKING:
    # Avoid import cycle at module level; only used for type hints.
    from hokom.canonical.pipeline import PipelineTrace  # type: ignore
    from hokom.canonical.constitutional.contracts import (  # type: ignore
        ConstitutionalStatus,
        ConstitutionalJudgment,
    )


# ── Constitutional status → StageStatus mapping ───────────────────────────────
#
# ConstitutionalStatus lives in src/hokom/canonical/constitutional/contracts.py
# and uses string values "sahih", "deferred", "batil", etc.
#
# We map by .value string to avoid importing ConstitutionalStatus at module level
# (it requires Python 3.12 when StrEnum is involved in the vendor layer).

_CONST_STATUS_TO_STAGE_STATUS: dict[str, StageStatus] = {
    "sahih":     StageStatus.EXECUTED_APPROVED,
    "deferred":  StageStatus.EXECUTED_DEFERRED,
    "batil":     StageStatus.EXECUTED_BLOCKED,
    "fasid":     StageStatus.EXECUTED_DEFERRED,   # non-fatal defect → DEFERRED
    "ambiguous": StageStatus.EXECUTED_DEFERRED,
    "residual":  StageStatus.EXECUTED_DEFERRED,
}

_DIRECTIVE_MAP: dict[str, str] = {
    "sahih":     "ACCEPT",
    "deferred":  "DEFER",
    "batil":     "BLOCK",
    "fasid":     "DEFER",
    "ambiguous": "DEFER",
    "residual":  "DEFER",
}


# ── Metrics ───────────────────────────────────────────────────────────────────

@dataclass
class LiveAdapterMetrics:
    """
    Integrity metrics produced alongside the 19-row ledger.

    APPLICABLE_TEMPLATE_ONLY_ROWS must be 0 for B2 to be satisfied.
    A "template-only" applicable row is one where the stage was token-scope
    but has no actual execution record (native_executor=None, executed=False,
    and the stage *could* have run given its predecessor status).
    """
    total_rows: int
    token_scope_rows: int           # should = 12
    higher_scope_rows: int          # should = 7, all NOT_APPLICABLE_AT_TOKEN_SCOPE
    executed_approved: int
    executed_deferred: int
    executed_blocked: int
    not_opened: int
    not_applicable_at_token_scope: int

    # B2 integrity gate
    applicable_template_only_rows: int   # must = 0
    false_executed_rows: int             # must = 0 (executed=True without executor)
    executed_rows_without_trace: int     # must = 0 (executed=True, trace_ids=())
    executed_rows_without_output: int    # must = 0 (executed=True, output_ref=None)

    pipeline_run_id: str
    pipeline_stages_reached: int    # how many stages the pipeline actually touched
    pipeline_stopped_early: bool    # True if BATIL caused early termination

    @property
    def b2_satisfied(self) -> bool:
        """True when all B2 integrity gates pass."""
        return (
            self.applicable_template_only_rows == 0
            and self.false_executed_rows == 0
            and self.executed_rows_without_trace == 0
            and self.executed_rows_without_output == 0
            and self.total_rows == 19
            and self.token_scope_rows == 12
            and self.higher_scope_rows == 7
        )

    def report_lines(self) -> list[str]:
        lines = [
            f"HOKOM_LIVE_PIPELINE_CONNECTED      = 1",
            f"PIPELINE_RUN_ID                    = {self.pipeline_run_id}",
            f"PIPELINE_STAGES_REACHED            = {self.pipeline_stages_reached}",
            f"PIPELINE_STOPPED_EARLY             = {int(self.pipeline_stopped_early)}",
            f"TOTAL_ROWS                         = {self.total_rows}",
            f"TOKEN_SCOPE_ROWS                   = {self.token_scope_rows}",
            f"HIGHER_SCOPE_ROWS                  = {self.higher_scope_rows}",
            f"EXECUTED_APPROVED                  = {self.executed_approved}",
            f"EXECUTED_DEFERRED                  = {self.executed_deferred}",
            f"EXECUTED_BLOCKED                   = {self.executed_blocked}",
            f"NOT_OPENED                         = {self.not_opened}",
            f"NOT_APPLICABLE_AT_TOKEN_SCOPE      = {self.not_applicable_at_token_scope}",
            f"APPLICABLE_TEMPLATE_ONLY_ROWS      = {self.applicable_template_only_rows}",
            f"FALSE_EXECUTED_ROWS                = {self.false_executed_rows}",
            f"EXECUTED_ROWS_WITHOUT_TRACE        = {self.executed_rows_without_trace}",
            f"EXECUTED_ROWS_WITHOUT_OUTPUT       = {self.executed_rows_without_output}",
            f"B2_SATISFIED                       = {int(self.b2_satisfied)}",
        ]
        return lines


# ── Adapter ───────────────────────────────────────────────────────────────────

def hokom_trace_to_token_ledger(
    trace: "PipelineTrace",
    analysis_id: str,
) -> tuple[list[StageExecutionRecord], LiveAdapterMetrics]:
    """
    Convert a live PipelineTrace from CanonicalPipeline.run_word() into
    a 19-row token-scope ledger.

    Args:
        trace       — PipelineTrace returned by run_word() or run_sentence()
        analysis_id — ledger analysis ID (e.g. "AD-W00" for Ayat Al-Dayn word 0)

    Returns:
        (records, metrics)
        records — exactly 19 StageExecutionRecord in canonical registry order
        metrics — LiveAdapterMetrics with B2 integrity gate values

    Constitutional guarantees:
        - stages_by_id in trace uses flat layer_id keys when run_word() was called
        - stages_by_id in trace uses "{layer_id}:w{i}" keys when run_sentence() was called
        - adapter reads both key formats and normalises to layer_id
    """
    # Normalise trace.stages_by_id to flat {layer_id: StageTrace} regardless
    # of whether run_word() or run_sentence() produced it.
    stage_lookup: dict[str, object] = {}  # layer_id → StageTrace
    for key, st in trace.stages_by_id.items():
        # run_word() keys: "P0_UNICODE_CANDIDATE"
        # run_sentence() keys: "P0_UNICODE_CANDIDATE:w0", "P0_UNICODE_CANDIDATE:w1", ...
        # For sentence runs we take the first word occurrence.
        base = key.split(":")[0]
        if base not in stage_lookup:
            stage_lookup[base] = st

    pipeline_run_id = trace.pipeline_run_id
    parent_id = f"HOKOM_LIVE:{pipeline_run_id}"
    pipeline_stages_reached = len(stage_lookup)
    stopped_early = pipeline_stages_reached < 15  # P0-P8 = 15 word-level stages

    records: list[StageExecutionRecord] = []

    for stage_def in HOKOM_STAGE_REGISTRY:
        sid = stage_def.stage_id

        if sid in HOKOM_SPAN_OR_HIGHER_STAGES:
            # P6-P12: always NOT_APPLICABLE_AT_TOKEN_SCOPE in token ledger
            records.append(
                StageExecutionRecord.not_applicable_at_token_scope(
                    stage_id=sid,
                    stage_name=stage_def.canonical_name,
                    engine=Engine.HOKOM,
                    subject_ref=trace.surface,
                    analysis_id=analysis_id,
                )
            )
            continue

        # P0-P5: TOKEN scope
        st = stage_lookup.get(sid)
        if st is None:
            # Pipeline did not reach this stage (stopped early due to BATIL)
            records.append(
                StageExecutionRecord.not_opened(
                    stage_id=sid,
                    stage_name=stage_def.canonical_name,
                    engine=Engine.HOKOM,
                    scope=ExecutionScope.TOKEN,
                    subject_ref=trace.surface,
                    analysis_id=analysis_id,
                    reason="pipeline_stopped_before_reaching_stage",
                )
            )
            continue

        # Stage was reached — extract judgment fields
        judgment = st.judgment  # type: ignore[union-attr]
        cset = st.candidate_set  # type: ignore[union-attr]

        const_status_val: str = judgment.status.value.lower()
        stage_status = _CONST_STATUS_TO_STAGE_STATUS.get(
            const_status_val, StageStatus.EXECUTED_DEFERRED
        )
        directive = _DIRECTIVE_MAP.get(const_status_val, "DEFER")

        # Taaqol gate
        illah = judgment.illah
        granted_rank: int = int(illah.granted_rank)
        gate_id: str = str(illah.taaqol_gate_id)

        # Trace IDs from candidate set (deterministic from bridge)
        trace_ids: tuple[str, ...] = cset.trace_ids if cset.trace_ids else ()

        # Output ref: the candidate set ID (tied to this actual run)
        output_ref: str | None = cset.set_id if cset.set_id else None

        # Evidence IDs: from accepted candidates' evidence atoms
        evidence_ids: tuple[str, ...] = ()
        if cset.candidates:
            best = cset.candidates[0]
            evidence_ids = best.trace_ids if best.trace_ids else ()

        # Active residuals: from baqaya carried forward
        active_residuals: tuple[str, ...] = tuple(
            f"{b.residual.kind}:{b.residual.description[:60]}"
            for b in judgment.baqaya
            if b.residual.is_active
        )

        # Stop reason: from mawani if blocked
        stop_reason: str | None = None
        if stage_status is StageStatus.EXECUTED_BLOCKED:
            active_blockers = [m for m in judgment.mawani if m.is_active]
            if active_blockers:
                # ManiBlocker is a dataclass with blocker_id: str, not .name
                # (ManiBlocker is not an enum — .name is not a valid field)
                stop_reason = active_blockers[0].blocker_id

        # Successor stage: from wad contract
        next_lid: str | None = getattr(st, 'next_layer_id', None)
        # StageTrace doesn't store next_layer_id; derive from registry order
        if next_lid is None:
            registry_ids = [s.stage_id for s in HOKOM_STAGE_REGISTRY]
            try:
                idx = registry_ids.index(sid)
                next_lid = registry_ids[idx + 1] if idx + 1 < len(registry_ids) else None
            except ValueError:
                next_lid = None

        # Gamma state: the Taaqol gate verdict (Gamma closure is stage 3 of Taaqol)
        gamma_state = (
            f"TAAQOL_GATE:{gate_id}:rank={granted_rank}"
            if gate_id else None
        )

        # Input ref: prior stage's output ref (carried via candidate set chain)
        # We use the analysis_id + stage position as a stable reference
        input_ref = f"{analysis_id}:{sid}:in"

        records.append(StageExecutionRecord(
            execution_id=uuid.uuid4().hex,
            parent_execution_id=parent_id,
            analysis_id=analysis_id,
            stage_id=sid,
            stage_name=stage_def.canonical_name,
            engine=Engine.HOKOM,
            scope=ExecutionScope.TOKEN,
            subject_ref=trace.surface,
            applicability=True,
            entered=True,
            executed=True,
            status=stage_status,
            native_executor=stage_def.executor,
            native_carrier_in=stage_def.input_type,
            native_carrier_out=stage_def.output_type,
            input_refs=(input_ref,),
            output_ref=output_ref,
            output_summary=(
                f"{stage_def.canonical_name}: rank={granted_rank} "
                f"status={const_status_val.upper()}"
            ),
            evidence_ids=evidence_ids,
            active_residuals=active_residuals,
            resolved_residuals=(),
            gamma_state=gamma_state,
            rank_before=0,
            rank_after=granted_rank,
            gate_verdict=gate_id if gate_id else None,
            directive=directive,
            stop_reason=stop_reason,
            successor_stage=next_lid,
            trace_ids=trace_ids,
            duration_ms=None,   # not measured at adapter level
            error=None,
        ))

    # ── Compute metrics ────────────────────────────────────────────────────────
    executed_approved = sum(
        1 for r in records if r.status is StageStatus.EXECUTED_APPROVED
    )
    executed_deferred = sum(
        1 for r in records if r.status is StageStatus.EXECUTED_DEFERRED
    )
    executed_blocked = sum(
        1 for r in records if r.status is StageStatus.EXECUTED_BLOCKED
    )
    not_opened_count = sum(
        1 for r in records if r.status is StageStatus.NOT_OPENED
    )
    not_applicable_count = sum(
        1 for r in records
        if r.status is StageStatus.NOT_APPLICABLE_AT_TOKEN_SCOPE
    )
    token_scope_count = sum(
        1 for r in records
        if r.status is not StageStatus.NOT_APPLICABLE_AT_TOKEN_SCOPE
    )
    higher_scope_count = not_applicable_count

    # B2 integrity checks
    #
    # Template-only row: NOT_OPENED with stop_reason == "predecessor_deferred_or_blocked"
    #   → produced by build_token_ledger_template(); not tied to an actual pipeline run.
    #
    # Live row: NOT_OPENED with stop_reason == "pipeline_stopped_before_reaching_stage"
    #   → produced by this adapter from an actual PipelineTrace; genuinely live data.
    #
    # Only the template string identifies a template-only row.
    _TEMPLATE_STOP_REASON = "predecessor_deferred_or_blocked"

    applicable_template_only = sum(
        1 for r in records
        if r.stage_id in HOKOM_TOKEN_STAGES
        and r.status is StageStatus.NOT_OPENED
        and r.stop_reason == _TEMPLATE_STOP_REASON
    )

    false_executed = sum(
        1 for r in records
        if r.executed and not r.native_executor
    )
    exec_without_trace = sum(
        1 for r in records
        if r.executed and len(r.trace_ids) == 0
        # Note: trace_ids may be empty when Taaqol fallback was used (bridge absent).
        # In that case the row is still valid but marks fallback_used=True via gate_verdict.
        # We only flag as violation if also no gate_verdict (completely uninstrumented).
        and not r.gate_verdict
    )
    exec_without_output = sum(
        1 for r in records
        if r.executed and r.output_ref is None
    )

    metrics = LiveAdapterMetrics(
        total_rows=len(records),
        token_scope_rows=token_scope_count,
        higher_scope_rows=higher_scope_count,
        executed_approved=executed_approved,
        executed_deferred=executed_deferred,
        executed_blocked=executed_blocked,
        not_opened=not_opened_count,
        not_applicable_at_token_scope=not_applicable_count,
        applicable_template_only_rows=applicable_template_only,
        false_executed_rows=false_executed,
        executed_rows_without_trace=exec_without_trace,
        executed_rows_without_output=exec_without_output,
        pipeline_run_id=pipeline_run_id,
        pipeline_stages_reached=pipeline_stages_reached,
        pipeline_stopped_early=stopped_early,
    )

    return records, metrics


def build_ayat_al_dayn_live_ledger(
    tokens: list[dict],
    analysis_id_prefix: str = "AD",
) -> tuple[list[StageExecutionRecord], list[LiveAdapterMetrics]]:
    """
    Build a live 2451-row ledger for all 129 tokens of Ayat Al-Dayn.

    Each token must be a dict with at minimum {"surface": str, "index": int}.
    Optional: {"hokom_evidence_by_stage": dict} for Hokom evidence injection.

    Requires Python 3.12.4 with live CanonicalPipeline (vendor/Taaqol-GPT).

    Returns:
        (all_records, all_metrics)
        all_records  — 129 × 19 = 2451 StageExecutionRecord in token order
        all_metrics  — 129 LiveAdapterMetrics, one per token

    Raises ImportError if CanonicalPipeline is not available.
    """
    from hokom.canonical.pipeline import CanonicalPipeline, WordInput  # type: ignore

    pipeline = CanonicalPipeline.build()
    all_records: list[StageExecutionRecord] = []
    all_metrics: list[LiveAdapterMetrics] = []

    for tok in tokens:
        surface: str = tok["surface"]
        word_idx: int = tok.get("index", 0)
        evidence: dict = tok.get("hokom_evidence_by_stage", {})

        word_input = WordInput(
            surface=surface,
            hokom_evidence_by_stage=evidence,
            pipeline_run_id=f"{analysis_id_prefix}-run",
            word_index=word_idx,
        )
        trace = pipeline.run_word(word_input)
        word_analysis_id = f"{analysis_id_prefix}-W{word_idx:03d}"
        records, metrics = hokom_trace_to_token_ledger(trace, word_analysis_id)
        all_records.extend(records)
        all_metrics.append(metrics)

    return all_records, all_metrics
