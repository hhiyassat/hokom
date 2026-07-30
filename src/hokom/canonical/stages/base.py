"""
base.py — StageAdapter abstract base class for all 19 canonical stage adapters.

Each concrete adapter implements adapt(input: StageInput) → StageOutput.
The base class enforces:
    - Saleh contract lookup (WadContract from registry snapshot)
    - Taaqol licensing call
    - ConstitutionalJudgment production
    - No P13 enforcement at P12

Ownership boundary: base class uses Hokom evidence; Taaqol for licensing;
Saleh spec via registry snapshot. HR2S/H2RS are FORBIDDEN here.
"""
from __future__ import annotations

import abc
import uuid
from dataclasses import dataclass
from typing import Any

from ..constitutional.contracts import (
    AtharEffect,
    BaqayaResidual,
    ConstitutionalJudgment,
    ConstitutionalStatus,
    IllahRationale,
    ManiBlocker,
    QadihDefect,
    SababEvidence,
    ShartRequirement,
    WadContract,
)
from ..registry import get_layer
from ..slot_algebra.types import (
    CanonicalCandidate,
    CanonicalCandidateSet,
    CandidateStatus,
    EvidenceSet,
    Residual,
    ResidualSeverity,
    SlotState,
)


# ── TaaqolLicenseOutcome ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class TaaqolLicenseOutcome:
    """
    Typed result carrier from _taaqol_license().

    Replaces the bare (int, str) tuple so that trace data flows
    through the call boundary without silent discard.

    Fields:
        granted_rank      — Taaqol lattice rank (0-6)
        gate_id           — e.g. "HOKOM_TAAQOL_LIVE_BRIDGE:P4_JAMID_MUSHTAQ"
        verdict           — "LICENSED" | "DEFERRED" | "BLOCKED" | "RESIDUAL"
        fallback_used     — True when bridge absent (ImportError / RuntimeError)
        trace_ids         — deterministic IDs from bridge trace events
        slot_graph_digest — bridge slot graph digest (empty string if fallback)
        failure_code      — TAAQOL_IMPORT_FAILURE / TAAQOL_RUNTIME_ERROR / None
    """
    granted_rank: int
    gate_id: str
    verdict: str
    fallback_used: bool
    trace_ids: tuple[str, ...]
    slot_graph_digest: str
    failure_code: str | None = None


# ── StageInput / StageOutput ──────────────────────────────────────────────────

@dataclass(frozen=True)
class StageInput:
    """
    Input to a stage adapter.

    Fields:
        layer_id        — target stage ID (Saleh canonical)
        surface         — Arabic surface text (NFC-normalized)
        hokom_evidence  — raw evidence dict from Hokom pipeline module
                          (keys are Hokom slot names; values are typed)
        prior_output    — CanonicalCandidateSet from the previous stage
                          (None for P0)
        pipeline_run_id — unique ID for this pipeline invocation
        word_index      — 0-based position in token sequence (None for sentence-level)
    """
    layer_id: str
    surface: str
    hokom_evidence: dict[str, Any]
    prior_output: CanonicalCandidateSet | None
    pipeline_run_id: str
    word_index: int | None = None


@dataclass(frozen=True)
class StageOutput:
    """
    Output from a stage adapter.

    Fields:
        candidate_set   — CanonicalCandidateSet produced by this stage
        judgment        — ConstitutionalJudgment (full jurisprudential chain)
        next_layer_id   — which stage receives this output (None for P12)
    """
    candidate_set: CanonicalCandidateSet
    judgment: ConstitutionalJudgment
    next_layer_id: str | None   # None for P12 (TERMINAL)


# ── StageAdapter ABC ──────────────────────────────────────────────────────────

class StageAdapter(abc.ABC):
    """
    Abstract base for all 19 canonical stage adapters.

    Concrete adapters implement:
        _collect_evidence(input) → EvidenceSet
        _check_conditions(input, evidence) → tuple[ShartRequirement, ...]
        _check_blockers(input, evidence) → tuple[ManiBlocker, ...]
        _check_defects(input, evidence) → tuple[QadihDefect, ...]
        _build_candidate(input, evidence, cid) → CanonicalCandidate
        _next_layer_id() → str | None

    The base class handles:
        - WadContract construction from Saleh snapshot
        - SababEvidence wrapping
        - ConstitutionalStatus determination
        - Taaqol licensing (stub until Taaqol integration layer wired)
        - ConstitutionalJudgment assembly
        - StageOutput packaging
    """

    LAYER_ID: str  # must be overridden

    def __init__(self) -> None:
        if not self.LAYER_ID:
            raise TypeError(
                f"{type(self).__name__} must define LAYER_ID class attribute"
            )
        # Load Saleh LayerSpec from snapshot (fail if snapshot not generated)
        self._layer_entry = get_layer(self.LAYER_ID)
        self._wad = WadContract.from_layer_entry(self._layer_entry)

    # ── public entry point ────────────────────────────────────────────────────

    def adapt(self, input: StageInput) -> StageOutput:
        """Run this stage adapter and return typed StageOutput."""
        assert input.layer_id == self.LAYER_ID, (
            f"StageInput.layer_id mismatch: expected {self.LAYER_ID}, "
            f"got {input.layer_id}"
        )

        # 1. Collect Hokom evidence
        evidence = self._collect_evidence(input)

        # 2. SababEvidence — opening cause
        trigger_rule, is_present = self._check_sabab(input, evidence)
        sabab = SababEvidence(
            layer_id=self.LAYER_ID,
            evidence=evidence,
            trigger_rule=trigger_rule,
            is_present=is_present,
        )

        # 3. Conditions
        shurut = self._check_conditions(input, evidence)

        # 4. Blockers
        mawani = self._check_blockers(input, evidence)

        # 5. Defects
        qawadih = self._check_defects(input, evidence)

        # 6. Request Taaqol licensing — returns typed TaaqolLicenseOutcome
        outcome = self._taaqol_license(input, evidence, sabab)
        granted_rank = outcome.granted_rank
        gate_id = outcome.gate_id
        trace_ids = outcome.trace_ids

        illah = IllahRationale(
            layer_id=self.LAYER_ID,
            rationale=self._wad.shared_cause,
            taaqol_gate_id=gate_id,
            granted_rank=granted_rank,
        )

        # 7. Determine constitutional status
        status = self._determine_status(shurut, mawani, qawadih, granted_rank)

        # 7b. Fail-closed: SAHIH without trace on a live bridge call is a defect
        if status is ConstitutionalStatus.SAHIH and not trace_ids and not outcome.fallback_used:
            # Bridge reached but produced no trace — treat as bridge defect.
            # Downgrade to DEFERRED so the gap surfaces in residuals.
            status = ConstitutionalStatus.DEFERRED

        # 8. Build candidate
        cid = self._make_candidate_id(input)
        candidate = self._build_candidate(input, evidence, cid, status, granted_rank)

        # 9. Assemble residuals
        residuals: list[Residual] = []
        if status in (ConstitutionalStatus.DEFERRED, ConstitutionalStatus.BATIL):
            for i, blocker in enumerate(mawani):
                if blocker.is_active:
                    residuals.append(
                        blocker.to_residual(f"RES-{self.LAYER_ID}-B{i}")
                    )

        candidate_set = CanonicalCandidateSet(
            set_id=f"SET-{self.LAYER_ID}-{input.pipeline_run_id[:8]}",
            layer_id=self.LAYER_ID,
            candidates=(candidate,),
            residuals=tuple(residuals),
            trace_ids=trace_ids,
        )

        # 10. AtharEffect (only for SAHIH)
        athar: AtharEffect | None = None
        if status is ConstitutionalStatus.SAHIH:
            next_lid = self._next_layer_id()
            athar = AtharEffect(
                layer_id=self.LAYER_ID,
                effect_type=self._wad.branch_output_type,
                candidate_id=cid,
                taaqol_rank=granted_rank,
                carry_to_next=next_lid,
            )

        # 11. BaqayaResidual (for DEFERRED / FASID)
        baqaya: list[BaqayaResidual] = []
        if status in (ConstitutionalStatus.DEFERRED, ConstitutionalStatus.FASID):
            for r in residuals:
                baqaya.append(
                    BaqayaResidual(
                        layer_id=self.LAYER_ID,
                        residual=r,
                        constitutional_status=status,
                        retry_at_layer=self._next_layer_id(),
                    )
                )

        judgment = ConstitutionalJudgment(
            layer_id=self.LAYER_ID,
            wad=self._wad,
            sabab=sabab,
            shurut=shurut,
            mawani=mawani,
            illah=illah,
            qawadih=qawadih,
            status=status,
            athar=athar,
            baqaya=tuple(baqaya),
        )

        return StageOutput(
            candidate_set=candidate_set,
            judgment=judgment,
            next_layer_id=self._next_layer_id(),
        )

    # ── hooks for concrete adapters ───────────────────────────────────────────

    @abc.abstractmethod
    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        """Extract EvidenceSet from StageInput.hokom_evidence."""

    def _check_sabab(
        self, input: StageInput, evidence: EvidenceSet
    ) -> tuple[str, bool]:
        """Return (trigger_rule_name, is_present). Default: first condition."""
        first = self._layer_entry.conditions[0] if self._layer_entry.conditions else "input_present"
        return first, True

    @abc.abstractmethod
    def _check_conditions(
        self, input: StageInput, evidence: EvidenceSet
    ) -> tuple[ShartRequirement, ...]:
        """Check all Saleh LayerSpec conditions against the evidence."""

    @abc.abstractmethod
    def _check_blockers(
        self, input: StageInput, evidence: EvidenceSet
    ) -> tuple[ManiBlocker, ...]:
        """Check all Saleh LayerSpec blockers against the evidence."""

    def _check_defects(
        self, input: StageInput, evidence: EvidenceSet
    ) -> tuple[QadihDefect, ...]:
        """Check for qadih defects. Default: none."""
        return ()

    @abc.abstractmethod
    def _build_candidate(
        self,
        input: StageInput,
        evidence: EvidenceSet,
        candidate_id: str,
        status: ConstitutionalStatus,
        taaqol_rank: int,
    ) -> CanonicalCandidate:
        """Build the typed CanonicalCandidate for this stage."""

    @abc.abstractmethod
    def _next_layer_id(self) -> str | None:
        """Return the canonical ID of the next stage (None for P12)."""

    # ── helpers ───────────────────────────────────────────────────────────────

    def _taaqol_license(
        self,
        input: StageInput,
        evidence: EvidenceSet,
        sabab: SababEvidence,
    ) -> TaaqolLicenseOutcome:
        """
        Request Taaqol licensing for the given evidence.

        Returns TaaqolLicenseOutcome carrying granted_rank, gate_id,
        trace_ids, slot_graph_digest, fallback_used, and failure_code.

        Implementation: attempts live Taaqol call via bridge; falls back to
        TRACE(1) if Taaqol runtime is unavailable (Python version mismatch).

        Taaqol rank lattice: ZERO=0, TRACE=1, CANDIDATE=2, HYPOTHESIS=3,
        LICENSED=4, STRONG=5, CERTIFICATE=6.

        Non-promotion law: granted_rank = min(evidence_rank, gate_rank).
        """
        try:
            from hokom.pipeline.taaqol_integration.live.bridge import (  # type: ignore
                evaluate_hokom_claim_bundle as _eval_claim,
            )
            import types as _types
            # evaluate_hokom_claim_bundle accepts any duck-typed object — no
            # isinstance check on the caller side.  Build a SimpleNamespace
            # carrying the attributes the bridge reads via getattr.
            # domain_directive='ACCEPT': this adapter is proposing a claim.
            # evidence_ids: evidence atoms projected to Taaqol source strings.
            _ns = _types.SimpleNamespace(
                original_surface=input.surface,
                normalized_surface=input.surface,
                segment_host=input.surface,
                morphology_surface=input.surface,
                morphology_blocked=False,
                segment_clitic_only=False,
                part_of_speech=None,
                lexical_class=None,
                domain_directive='ACCEPT',
                claim_id=f'hokom:{self.LAYER_ID}:{input.surface}',
                evidence_ids=tuple(evidence.as_taaqol_sources()),
                active_residuals=(),
                segment_proclitics=(),
                segment_enclitics=(),
            )
            result = _eval_claim(_ns)
            # Map taaqol_verdict → Taaqol rank int.  LICENSED=4 is the threshold
            # required by _determine_status to produce SAHIH.
            _verdict = getattr(result, 'taaqol_verdict', 'DEFERRED')
            _RANK_MAP = {
                'LICENSED': 4, 'STRONG': 5, 'CERTIFICATE': 6,
                'DEFERRED': 3, 'RESIDUAL': 2, 'BLOCKED': 1,
            }
            rank = _RANK_MAP.get(str(_verdict).upper(), 3)
            # gate_id built from bridge_id — must not contain error sentinels.
            _bid = getattr(result, 'bridge_id', 'HOKOM_TAAQOL_LIVE_BRIDGE')
            gate_id = f"{_bid}:{self.LAYER_ID}"
            # Extract trace event IDs from result.trace (deterministic from bridge)
            _trace_events = getattr(result, 'trace', ())
            _slot_graph_digest = getattr(result, 'slot_graph_digest', '')
            if _trace_events:
                _trace_ids = tuple(
                    f"{getattr(ev, 'component', '?')}:{getattr(ev, 'input_digest', '?')}"
                    for ev in _trace_events
                )
            elif _slot_graph_digest:
                # No trace events but digest present — derive single trace ID
                _trace_ids = (f"sgd:{_slot_graph_digest[:16]}",)
            else:
                _trace_ids = ()
            return TaaqolLicenseOutcome(
                granted_rank=int(rank),
                gate_id=gate_id,
                verdict=str(_verdict).upper(),
                fallback_used=False,
                trace_ids=_trace_ids,
                slot_graph_digest=_slot_graph_digest,
                failure_code=None,
            )
        except ImportError:
            # Taaqol vendor absent (Python version mismatch or missing package).
            # FAIL CLOSED — §C binding rule 11:
            #   "Absence or failure of the Taaqol runtime must fail closed."
            #   "A fallback may not produce LICENSED."
            # Return TRACE(1): below the LICENSED threshold(≥4).
            # Reason code: TAAQOL_IMPORT_FAILURE (authoritative, from SCG contract)
            return TaaqolLicenseOutcome(
                granted_rank=1,
                gate_id=f"TAAQOL_IMPORT_FAILURE:{self.LAYER_ID}",
                verdict="DEFERRED",
                fallback_used=True,
                trace_ids=(),
                slot_graph_digest="",
                failure_code="TAAQOL_IMPORT_FAILURE",
            )
        except Exception:
            # Taaqol importable but raised at runtime.
            # FAIL CLOSED — same rule. Return TRACE(1).
            # Reason code: TAAQOL_RUNTIME_ERROR (authoritative, from SCG contract)
            return TaaqolLicenseOutcome(
                granted_rank=1,
                gate_id=f"TAAQOL_RUNTIME_ERROR:{self.LAYER_ID}",
                verdict="DEFERRED",
                fallback_used=True,
                trace_ids=(),
                slot_graph_digest="",
                failure_code="TAAQOL_RUNTIME_ERROR",
            )

    def _determine_status(
        self,
        shurut: tuple[ShartRequirement, ...],
        mawani: tuple[ManiBlocker, ...],
        qawadih: tuple[QadihDefect, ...],
        granted_rank: int,
    ) -> ConstitutionalStatus:
        """
        Constitutional status determination:

            Active BLOCKER-severity blocker → BATIL
            Active invalidating defect → BATIL
            Active WARNING-severity blocker → FASID
            Unsatisfied condition → DEFERRED
            granted_rank < 4 (LICENSED) → DEFERRED
            All conditions met, no blockers, rank ≥ 4 → SAHIH
        """
        # Active blockers
        active_blockers = [m for m in mawani if m.is_active]
        for blocker in active_blockers:
            if blocker.severity is ResidualSeverity.BLOCKER:
                return ConstitutionalStatus.BATIL

        # Active invalidating defects
        for defect in qawadih:
            if defect.is_active and defect.invalidating:
                return ConstitutionalStatus.BATIL

        # Non-invalidating defects
        for defect in qawadih:
            if defect.is_active and not defect.invalidating:
                return ConstitutionalStatus.FASID

        # Warning-severity blockers → FASID
        for blocker in active_blockers:
            if blocker.severity is ResidualSeverity.WARNING:
                return ConstitutionalStatus.FASID

        # Unsatisfied conditions
        if any(not s.is_satisfied for s in shurut):
            return ConstitutionalStatus.DEFERRED

        # Taaqol rank gate
        if granted_rank < 4:
            return ConstitutionalStatus.DEFERRED

        return ConstitutionalStatus.SAHIH

    def _make_candidate_id(self, input: StageInput) -> str:
        """Generate a unique candidate ID for this evaluation."""
        return f"{self.LAYER_ID}-{input.pipeline_run_id[:8]}-{input.word_index or 0}"

    def _make_candidate_status(
        self, status: ConstitutionalStatus
    ) -> CandidateStatus:
        if status is ConstitutionalStatus.SAHIH:
            return CandidateStatus.ACCEPTED
        if status is ConstitutionalStatus.BATIL:
            return CandidateStatus.BLOCKED
        return CandidateStatus.DEFERRED

    def _make_slot_state(self, status: ConstitutionalStatus, rank: int) -> SlotState:
        if status is ConstitutionalStatus.SAHIH and rank >= 4:
            return SlotState.LICENSED
        if status is ConstitutionalStatus.BATIL:
            return SlotState.BLOCKED
        if status is ConstitutionalStatus.FASID:
            return SlotState.SUPPORTED
        if status is ConstitutionalStatus.DEFERRED:
            return SlotState.DEFERRED
        return SlotState.CANDIDATE
