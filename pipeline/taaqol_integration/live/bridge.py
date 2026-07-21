"""
Canonical bridge: evaluate_hokom_claim_bundle.

HOKOM-TAAQOL-LIVE-INTEGRATION-01

TAAQOL_LIVE_CANONICAL_ENTRYPOINT = 'evaluate_hokom_claim_bundle'

Architecture: SlotGraph → Gamma → TransitionGate → strict decision
Mode: STRICT
Fail-closed: True (never returns LICENSED on Taaqol import failure)
No silent fallback: errors are recorded in trace, not swallowed.
No parallel bridges. No parallel decision engines.

Taaqol vendor: taaqqul_slot_geometry (vendor/Taaqol-GPT/src/)
Requires Python 3.11+ (taaqqul_slot_geometry uses StrEnum).
On Python 3.10: ImportError → DEFERRED (fail-closed, not LICENSED).
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Optional

from .models import (
    HOKOM_TAAQOL_BRIDGE_ID,
    HokomTaaqolDecision,
    HokomTaaqolTraceEvent,
)
from .decision_composition import compose_effective_verdict


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Git helpers (deterministic provenance)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_REPO_ROOT = Path(__file__).resolve().parents[3]
_VENDOR_PATH = _REPO_ROOT / 'vendor' / 'Taaqol-GPT' / 'src'


def _get_taaqol_commit() -> str:
    """Get vendor submodule commit hash deterministically (first 12 chars)."""
    try:
        result = subprocess.run(
            ['git', '-C', 'vendor/Taaqol-GPT', 'rev-parse', 'HEAD'],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
            timeout=5,
        )
        return result.stdout.strip()[:12] if result.returncode == 0 else 'unknown'
    except Exception:
        return 'unknown'


def _get_taaqol_sha_full() -> str:
    """Get full 40-char vendor submodule commit hash for liveness provenance."""
    try:
        result = subprocess.run(
            ['git', '-C', 'vendor/Taaqol-GPT', 'rev-parse', 'HEAD'],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else 'unknown'
    except Exception:
        return 'unknown'


def _get_hokom_commit() -> str:
    """Get Hokom HEAD commit hash."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
            timeout=5,
        )
        return result.stdout.strip()[:12] if result.returncode == 0 else 'unknown'
    except Exception:
        return 'unknown'


def _digest(text: str) -> str:
    """Deterministic SHA-256 digest (first 16 hex chars)."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Deferred verdict helper (fail-closed template)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _deferred_decision(
    *,
    taaqol_commit: str,
    hokom_commit: str,
    upstream_verdict: str,
    reason_codes: tuple,
    residuals: tuple,
    trace: tuple,
    taaqol_center_scope: 'Optional[str]' = None,
    taaqol_runtime: 'Optional[dict]' = None,
) -> HokomTaaqolDecision:
    """
    Build a DEFERRED decision for fail-closed scenarios.
    NEVER returns LICENSED. Always records the failure in trace.
    taaqol_runtime distinguishes infrastructure failure from semantic DEFER.
    """
    effective = compose_effective_verdict(upstream_verdict, 'DEFERRED')
    return HokomTaaqolDecision(
        bridge_id=HOKOM_TAAQOL_BRIDGE_ID,
        taaqol_commit=taaqol_commit,
        hokom_commit=hokom_commit,
        strict_mode=True,
        slot_graph_digest='UNAVAILABLE',
        gamma_result='UNAVAILABLE',
        transition_gate_result='UNAVAILABLE',
        taaqol_verdict='DEFERRED',
        reason_codes=reason_codes,
        contradictions=(),
        residuals=residuals,
        trace=trace,
        upstream_verdict=upstream_verdict,
        effective_verdict=effective,
        fail_closed=True,
        source_engine='TAAQOL',
        taaqol_center_scope=taaqol_center_scope,
        taaqol_runtime=taaqol_runtime,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SlotGraph construction from bundle (uses real Taaqol API)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _build_slot_graph(bundle, taaqol):
    """
    Build a taaqqul_slot_geometry.SlotGraph from a HokomLinguisticClaimBundle.

    Uses the real Taaqol API: SlotGraph, Center, TraceRef, SlotBoundary,
    OpeningPolicy, Slot, SlotState, OutputBoundary, EntryBoundary,
    GenerationSource, Layer, Rank, Residual, ResidualKind, FailureCode.

    Constitutional shape: G = ⟨Center, Slots, Boundary, Residuals, Rank,
    OutputBoundary, GenerationSource, EntryBoundary⟩
    """
    # Unpack Taaqol types
    SlotGraph        = taaqol.SlotGraph
    Center           = taaqol.Center
    TraceRef         = taaqol.TraceRef
    SlotBoundary     = taaqol.SlotBoundary
    OpeningPolicy    = taaqol.OpeningPolicy
    Slot             = taaqol.Slot
    SlotState        = taaqol.SlotState
    OutputBoundary   = taaqol.OutputBoundary
    EntryBoundary    = taaqol.EntryBoundary
    GenerationSource = taaqol.GenerationSource
    Layer            = taaqol.Layer
    Rank             = taaqol.Rank
    Residual         = taaqol.Residual
    ResidualKind     = taaqol.ResidualKind
    FailureCode      = taaqol.FailureCode

    original_surface  = getattr(bundle, 'original_surface', '') or 'unknown'
    claim_id          = getattr(bundle, 'claim_id', '') or f'hokom:{original_surface}'
    domain_directive  = getattr(bundle, 'domain_directive', 'DEFER') or 'DEFER'
    active_residuals  = tuple(getattr(bundle, 'active_residuals', ()) or ())

    # ── Morphological center (HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME) ───────
    # INVARIANT: Center.scope MUST be the segment_host (lexical host after clitic
    # segmentation), NOT original_surface.
    # original_surface is provenance only — it encodes full token with clitics.
    # segment_host is the canonical morphological identity stripped of clitics.
    morphological_center = (
        getattr(bundle, 'segment_host', None)
        or getattr(bundle, 'morphology_surface', None)
        or original_surface  # last-resort fallback: no segmentation data
    )

    # ── Center ───────────────────────────────────────────────────────────────
    anchor = claim_id or f'hokom:{original_surface}'
    trace_ref = TraceRef(anchor=anchor, kind='hokom_claim')
    center = Center(
        identity_claim=anchor,
        domain='hokom_morphology',
        scope=morphological_center,
        trace_ref=trace_ref,
    )

    # ── Global boundary ───────────────────────────────────────────────────────
    boundary = SlotBoundary(
        domain='hokom_morphology',
        scope='arabic_morphology',
        refusal_codes=(FailureCode.BOUNDARY_MISSING,),
        licensed_operations=('morphological_analysis',),
    )

    # ── Primary slot (domain_claim) ───────────────────────────────────────────
    # ACCEPT → FILLED with directive value
    # BLOCK/DEFER/NOT_APPLICABLE → EMPTY (blocking residuals drive BLOCK outcome)
    _UP = domain_directive.upper()
    if _UP in ('ACCEPT', 'LICENSED'):
        primary_value = 'ACCEPT'
        primary_state = SlotState.FILLED
    else:
        primary_value = None
        primary_state = SlotState.EMPTY

    primary_boundary = SlotBoundary(
        domain='hokom_domain_claim',
        scope='domain_directive',
        refusal_codes=(FailureCode.REQUIRED_SLOT_EMPTY,),
    )
    primary_opening = OpeningPolicy(
        allowed_potentials=frozenset({'ACCEPT', 'DEFER', 'BLOCK', 'NOT_APPLICABLE', 'UNKNOWN'}),
    )
    primary_slot = Slot(
        name='domain_claim',
        value_state=primary_state,
        boundary=primary_boundary,
        opening=primary_opening,
        required=True,
        value=primary_value,
    )

    # ── Word class slot (optional, not required) ──────────────────────────────
    wc_value = str(getattr(bundle, 'part_of_speech', None) or
                   getattr(bundle, 'lexical_class', None) or '')
    if wc_value and _UP in ('ACCEPT', 'LICENSED'):
        wc_boundary = SlotBoundary(
            domain='hokom_word_class',
            scope='part_of_speech',
            refusal_codes=(FailureCode.DOMAIN_MISSING,),
        )
        wc_opening = OpeningPolicy(
            allowed_potentials=frozenset({
                wc_value, 'ISM', 'FI3L', 'HARF', 'UNKNOWN',
            }),
        )
        wc_slot = Slot(
            name='word_class_claim',
            value_state=SlotState.FILLED,
            boundary=wc_boundary,
            opening=wc_opening,
            required=False,
            value=wc_value,
        )
        slots = (primary_slot, wc_slot)
    else:
        slots = (primary_slot,)

    # ── Residuals ─────────────────────────────────────────────────────────────
    residuals_list = []
    if _UP in ('BLOCK', 'BLOCKED'):
        # Upstream BLOCK → explicit BLOCKING residual so gamma returns BLOCKED
        residuals_list.append(Residual(
            name='hokom:upstream_block',
            kind=ResidualKind.BLOCKING,
            visible=True,
            note='Hokom upstream directive is BLOCK',
        ))
    # Map Hokom active_residuals
    for code in active_residuals:
        code_str = str(code)
        if code_str.startswith('block:'):
            kind = ResidualKind.BLOCKING
        elif code_str.startswith('defer:'):
            kind = ResidualKind.DEFERRABLE
        else:
            kind = ResidualKind.NON_BLOCKING
        # Truncate to avoid schema error on long names (must be non-empty string)
        safe_name = code_str[:120] or 'unknown_residual'
        residuals_list.append(Residual(
            name=safe_name,
            kind=kind,
            visible=True,
            note='Hokom residual',
        ))
    residuals = tuple(residuals_list)

    # ── Rank ─────────────────────────────────────────────────────────────────
    # ACCEPT → HYPOTHESIS (below LICENSED, gate can grant up to STRONG)
    # DEFER  → CANDIDATE
    # BLOCK  → CANDIDATE (BLOCKING residual drives result, not rank)
    if _UP in ('ACCEPT', 'LICENSED'):
        rank = Rank.HYPOTHESIS
    else:
        rank = Rank.CANDIDATE

    # ── Output boundary (TEXT_ENTRY level — Hokom is a textual analysis engine)
    output_boundary = OutputBoundary(
        declared_layer=Layer.TEXT_ENTRY,
        output_layer=Layer.TEXT_ENTRY,
    )

    # ── Entry boundary (required for DECLARED_ENTRY generation source)
    entry_boundary = EntryBoundary(
        declared_entry_kind='HOKOM_MORPHOLOGICAL_ANALYSIS',
        representation_status='REPRESENTATIONAL',
        ontological_status='NOT_ONTOLOGICAL',
        sound_status='NOT_SOUND',
        meaning_status='NOT_MEANING',
        prior_trace_status='PRIOR_TRACE_PRESERVED',
        produces_only='TextTraceCandidate',
    )

    return SlotGraph(
        center=center,
        slots=slots,
        boundary=boundary,
        residuals=residuals,
        rank=rank,
        output_boundary=output_boundary,
        generation_source=GenerationSource.DECLARED_ENTRY,
        entry_boundary=entry_boundary,
    )


def _build_evidence_contract(bundle, taaqol):
    """
    Build taaqqul_slot_geometry.EvidenceContract from bundle evidence_ids.
    Uses real Taaqol API: EvidenceContract, EvidenceSource, Rank, TraceRef.
    """
    EvidenceContract = taaqol.EvidenceContract
    EvidenceSource   = taaqol.EvidenceSource
    Rank             = taaqol.Rank
    TraceRef         = taaqol.TraceRef

    claim_id    = getattr(bundle, 'claim_id', 'hokom_claim') or 'hokom_claim'
    evidence_ids = tuple(getattr(bundle, 'evidence_ids', ()) or ())

    sources = []
    for eid in evidence_ids:
        eid_str = str(eid)
        # Determine evidential rank from evidence type
        if any(k in eid_str for k in ('root_catalog', 'corpus', 'lexical')):
            rank = Rank.STRONG
        elif any(k in eid_str for k in ('wazn', 'bab', 'form')):
            rank = Rank.LICENSED
        elif any(k in eid_str for k in ('masdar', 'mushtaq', 'inflection')):
            rank = Rank.HYPOTHESIS
        elif 'accept' in eid_str.lower():
            rank = Rank.HYPOTHESIS
        else:
            rank = Rank.CANDIDATE

        # EvidenceSource requires non-empty name, kind, rank, trace_ref
        safe_name = (eid_str[:120] or 'evidence') if eid_str else 'evidence'
        sources.append(EvidenceSource(
            name=safe_name,
            kind='hokom_evidence',
            rank=rank,
            trace_ref=TraceRef(anchor=claim_id, kind='evidence'),
        ))

    return EvidenceContract(sources=tuple(sources))


def _map_transition_state_to_verdict(state_str: str) -> str:
    """Map TransitionState string to Taaqol verdict string."""
    _MAP = {
        'APPROVED':       'LICENSED',
        'DEFERRED':       'DEFERRED',
        'BLOCKED':        'BLOCKED',
        'REJECTED':       'BLOCKED',
        'FORBIDDEN_LEAP': 'BLOCKED',
    }
    return _MAP.get(str(state_str).upper(), 'DEFERRED')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Canonical entrypoint
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def evaluate_hokom_claim_bundle(bundle) -> HokomTaaqolDecision:
    """
    TAAQOL_LIVE_CANONICAL_ENTRYPOINT

    Takes a HokomLinguisticClaimBundle, projects it into Taaqol,
    runs strict SlotGraph → Gamma → TransitionGate pipeline,
    returns HokomTaaqolDecision.

    FAIL-CLOSED:
    - ImportError → DEFERRED (not LICENSED)
    - Any Taaqol exception → DEFERRED (recorded in trace, not swallowed)

    NO SILENT FALLBACK: all failures are recorded in reason_codes and trace.
    NO PARALLEL BRIDGE: one entrypoint, one pipeline, one decision.
    STRICT MODE: always active.

    Requires Python 3.11+ (taaqqul_slot_geometry uses StrEnum).
    On Python 3.10: returns DEFERRED with TAAQOL_RUNTIME_UNAVAILABLE.

    LIVENESS CONTRACT (HOKOM-TAAQOL-LIVE-BRIDGE-RECOVERY-01):
    taaqol_runtime in the returned decision distinguishes:
      - active=False + failure_code="TAAQOL_RUNTIME_UNAVAILABLE" → import/path failure
      - active=True + gate_executed=True → full chain executed, verdict is semantic
    """
    import sys as _sys

    taaqol_commit = _get_taaqol_commit()
    hokom_commit  = _get_hokom_commit()
    upstream_verdict = str(getattr(bundle, 'domain_directive', 'DEFER') or 'DEFER')
    trace: list = []

    # ── Liveness contract dict ────────────────────────────────────────────────
    # Updated progressively as each step completes. Passed to all returned decisions.
    # Distinguishes infrastructure failure from semantic verdict — never returns
    # active=True with failure_code set, or failure_code=None with active=False.
    _rt: dict = {
        "active": False,
        "repo_root": str(_REPO_ROOT),
        "vendor_path": str(_VENDOR_PATH),
        "vendor_sha": None,
        "public_entrypoint": None,
        "kernel_loaded": False,
        "slot_graph_created": False,
        "gamma_executed": False,
        "gate_executed": False,
        "trace_event_count": 0,
        "failure_code": None,
        "failure_detail": None,
    }

    # ── Compute morphological center (before import so all paths can use it) ──
    # INVARIANT: Center.scope = segment_host, NOT original_surface.
    # original_surface is provenance only.
    # Clitic-only tokens have no lexical host → center is None (never original_surface).
    _original_surface    = getattr(bundle, 'original_surface', '') or 'unknown'
    _morphology_blocked  = bool(getattr(bundle, 'morphology_blocked', False))
    _segment_clitic_only = bool(getattr(bundle, 'segment_clitic_only', False))

    if _morphology_blocked or _segment_clitic_only:
        # No morphological center — clitic-only or segmentation failure.
        # NEVER use original_surface as center for these cases.
        _morphological_center = None
    else:
        _morphological_center = (
            getattr(bundle, 'segment_host', None)
            or getattr(bundle, 'morphology_surface', None)
            or _original_surface  # last-resort: no segmentation data at all
        )

    # ── Import Taaqol (FAIL-CLOSED on ImportError) ────────────────────────────
    # taaqqul_slot_geometry requires Python 3.11+ (StrEnum).
    # On Python 3.10 this ImportError is expected and handled here.
    # LIVENESS: kernel_loaded stays False and failure_code is set — NOT a semantic DEFER.
    try:
        _vendor_src = str(_VENDOR_PATH)
        if _vendor_src not in _sys.path:
            _sys.path.insert(0, _vendor_src)
        import taaqqul_slot_geometry as _taaqol
    except ImportError as e:
        trace.append(HokomTaaqolTraceEvent(
            step='import',
            component='Taaqol',
            input_digest='',
            output=f'ImportError:{e}',
            strict_mode=True,
        ))
        _rt["failure_code"] = "TAAQOL_RUNTIME_UNAVAILABLE"
        _rt["failure_detail"] = f'ImportError:{e}'
        _rt["trace_event_count"] = len(trace)
        return _deferred_decision(
            taaqol_commit=taaqol_commit,
            hokom_commit=hokom_commit,
            upstream_verdict=upstream_verdict,
            reason_codes=('TAAQOL_RUNTIME_UNAVAILABLE', f'ImportError:{e}'),
            residuals=('defer:taaqol:runtime_unavailable',),
            trace=tuple(trace),
            taaqol_center_scope=_morphological_center,
            taaqol_runtime=dict(_rt),
        )

    # ── Taaqol kernel loaded successfully ─────────────────────────────────────
    _rt["kernel_loaded"] = True
    _rt["vendor_sha"] = _get_taaqol_sha_full()
    _rt["public_entrypoint"] = "taaqqul_slot_geometry"

    # ── Clitic-only gate ─────────────────────────────────────────────────────
    # If the segmenter found no lexical host (pure clitic construction, e.g. بِكُمْ),
    # there is no morphological center — SlotGraph cannot be built.
    # Return DEFERRED immediately rather than silently using the full token as center.
    # (_morphology_blocked and _segment_clitic_only computed above, before import)
    if _morphology_blocked or _segment_clitic_only:
        _block_reason = (
            getattr(bundle, 'morphology_block_reason', None)
            or 'SEGMENTATION_NO_LEXICAL_HOST'
        )
        trace.append(HokomTaaqolTraceEvent(
            step='clitic_only_gate',
            component='SlotGraph',
            input_digest='',
            output=f'DEFERRED:no_lexical_host:{_block_reason}:surface={_original_surface!r}',
            strict_mode=True,
        ))
        _rt["failure_code"] = "SEGMENTATION_NO_LEXICAL_HOST"
        _rt["failure_detail"] = _block_reason
        _rt["trace_event_count"] = len(trace)
        return _deferred_decision(
            taaqol_commit=taaqol_commit,
            hokom_commit=hokom_commit,
            upstream_verdict=upstream_verdict,
            reason_codes=('SEGMENTATION_NO_LEXICAL_HOST', _block_reason),
            residuals=('defer:taaqol:clitic_only_no_center',),
            trace=tuple(trace),
            taaqol_center_scope=None,
            taaqol_runtime=dict(_rt),
        )

    # ── Step 1: Build SlotGraph ───────────────────────────────────────────────
    try:
        slot_graph = _build_slot_graph(bundle, _taaqol)
        graph_digest = _digest(
            f'{getattr(bundle, "claim_id", "")}:'
            f'{getattr(bundle, "domain_directive", "")}:'
            f'{sorted(str(e) for e in getattr(bundle, "evidence_ids", ()) or ())}'
        )
        trace.append(HokomTaaqolTraceEvent(
            step='slot_graph_construction',
            component='SlotGraph',
            input_digest=_digest(str(getattr(bundle, 'claim_id', ''))),
            output=(
                f'SlotGraph(center={_morphological_center!r},'
                f'rank={slot_graph.rank},'
                f'original={_original_surface!r})'
            ),
            strict_mode=True,
        ))
        _rt["slot_graph_created"] = True
    except Exception as e:
        trace.append(HokomTaaqolTraceEvent(
            step='slot_graph_construction',
            component='SlotGraph',
            input_digest='',
            output=f'Error:{type(e).__name__}:{e}',
            strict_mode=True,
        ))
        _rt["failure_code"] = "SLOT_GRAPH_CONSTRUCTION_FAILED"
        _rt["failure_detail"] = f'{type(e).__name__}:{e}'
        _rt["trace_event_count"] = len(trace)
        return _deferred_decision(
            taaqol_commit=taaqol_commit,
            hokom_commit=hokom_commit,
            upstream_verdict=upstream_verdict,
            reason_codes=('SLOT_GRAPH_CONSTRUCTION_FAILED', f'{type(e).__name__}:{e}'),
            residuals=('defer:taaqol:slot_graph_construction_failed',),
            trace=tuple(trace),
            taaqol_center_scope=_morphological_center,
            taaqol_runtime=dict(_rt),
        )

    # ── Step 2: Run Gamma ─────────────────────────────────────────────────────
    try:
        from taaqqul_slot_geometry.core.gamma import gamma
        gamma_result = gamma(slot_graph)
        gamma_state_str = str(gamma_result.state)
        trace.append(HokomTaaqolTraceEvent(
            step='gamma_evaluation',
            component='Gamma',
            input_digest=graph_digest,
            output=f'GammaResult(state={gamma_state_str},rank={gamma_result.rank})',
            strict_mode=True,
        ))
        _rt["gamma_executed"] = True
    except Exception as e:
        trace.append(HokomTaaqolTraceEvent(
            step='gamma_evaluation',
            component='Gamma',
            input_digest=graph_digest,
            output=f'Error:{type(e).__name__}:{e}',
            strict_mode=True,
        ))
        _rt["failure_code"] = "GAMMA_EVALUATION_FAILED"
        _rt["failure_detail"] = f'{type(e).__name__}:{e}'
        _rt["trace_event_count"] = len(trace)
        return _deferred_decision(
            taaqol_commit=taaqol_commit,
            hokom_commit=hokom_commit,
            upstream_verdict=upstream_verdict,
            reason_codes=('GAMMA_EVALUATION_FAILED', f'{type(e).__name__}:{e}'),
            residuals=('defer:taaqol:gamma_failed',),
            trace=tuple(trace),
            taaqol_center_scope=_morphological_center,
            taaqol_runtime=dict(_rt),
        )

    # ── Step 3: Build EvidenceContract ────────────────────────────────────────
    try:
        evidence = _build_evidence_contract(bundle, _taaqol)
        trace.append(HokomTaaqolTraceEvent(
            step='evidence_contract_build',
            component='EvidenceContract',
            input_digest=graph_digest,
            output=f'EvidenceContract(sources={len(evidence.sources)},rank={evidence.evidence_rank})',
            strict_mode=True,
        ))
    except Exception as e:
        trace.append(HokomTaaqolTraceEvent(
            step='evidence_contract_build',
            component='EvidenceContract',
            input_digest=graph_digest,
            output=f'Error:{type(e).__name__}:{e}',
            strict_mode=True,
        ))
        _rt["failure_code"] = "EVIDENCE_CONTRACT_FAILED"
        _rt["failure_detail"] = f'{type(e).__name__}:{e}'
        _rt["trace_event_count"] = len(trace)
        return _deferred_decision(
            taaqol_commit=taaqol_commit,
            hokom_commit=hokom_commit,
            upstream_verdict=upstream_verdict,
            reason_codes=('EVIDENCE_CONTRACT_FAILED', f'{type(e).__name__}:{e}'),
            residuals=('defer:taaqol:evidence_failed',),
            trace=tuple(trace),
            taaqol_center_scope=_morphological_center,
            taaqol_runtime=dict(_rt),
        )

    # ── Step 4: Run TransitionGate ────────────────────────────────────────────
    try:
        gate = _taaqol.TransitionGate(
            name='HOKOM_TAAQOL_GATE',
            gate_rank=_taaqol.Rank.STRONG,
        )
        gate_verdict = gate.decide(
            input_graph=slot_graph,
            target_layer=_taaqol.Layer.CANDIDATE,
            evidence=evidence,
        )
        gate_state_str = str(gate_verdict.state)
        trace.append(HokomTaaqolTraceEvent(
            step='transition_gate_decision',
            component='TransitionGate',
            input_digest=graph_digest,
            output=(
                f'TransitionVerdict(state={gate_state_str},'
                f'rank={gate_verdict.granted_rank},'
                f'gamma={gate_verdict.gamma_state})'
            ),
            strict_mode=True,
        ))
        _rt["gate_executed"] = True
    except Exception as e:
        trace.append(HokomTaaqolTraceEvent(
            step='transition_gate_decision',
            component='TransitionGate',
            input_digest=graph_digest,
            output=f'Error:{type(e).__name__}:{e}',
            strict_mode=True,
        ))
        _rt["failure_code"] = "TRANSITION_GATE_FAILED"
        _rt["failure_detail"] = f'{type(e).__name__}:{e}'
        _rt["trace_event_count"] = len(trace)
        return _deferred_decision(
            taaqol_commit=taaqol_commit,
            hokom_commit=hokom_commit,
            upstream_verdict=upstream_verdict,
            reason_codes=('TRANSITION_GATE_FAILED', f'{type(e).__name__}:{e}'),
            residuals=('defer:taaqol:gate_failed',),
            trace=tuple(trace),
            taaqol_center_scope=_morphological_center,
            taaqol_runtime=dict(_rt),
        )

    # ── Step 5: Compose decision ──────────────────────────────────────────────
    taaqol_verdict = _map_transition_state_to_verdict(gate_state_str)
    effective_verdict = compose_effective_verdict(upstream_verdict, taaqol_verdict)

    # Collect reason codes
    reason_codes_list = []
    if gate_verdict.failure_code is not None:
        reason_codes_list.append(str(gate_verdict.failure_code))
    if gamma_result.failure_code is not None:
        reason_codes_list.append(f'gamma:{gamma_result.failure_code}')

    # Collect residuals from graph
    residuals_list = []
    for r in slot_graph.residuals:
        residuals_list.append(str(r.name))

    # ── Finalize liveness contract ────────────────────────────────────────────
    # All steps succeeded: active=True, all flags set, no failure_code.
    _rt["active"] = True
    _rt["trace_event_count"] = len(trace)

    return HokomTaaqolDecision(
        bridge_id=HOKOM_TAAQOL_BRIDGE_ID,
        taaqol_commit=taaqol_commit,
        hokom_commit=hokom_commit,
        strict_mode=True,
        slot_graph_digest=graph_digest,
        gamma_result=gamma_state_str,
        transition_gate_result=gate_state_str,
        taaqol_verdict=taaqol_verdict,
        reason_codes=tuple(reason_codes_list),
        contradictions=(),
        residuals=tuple(residuals_list),
        trace=tuple(trace),
        upstream_verdict=upstream_verdict,
        effective_verdict=effective_verdict,
        fail_closed=True,
        source_engine='TAAQOL',
        taaqol_center_scope=_morphological_center,
        taaqol_runtime=dict(_rt),
    )


__all__ = ['evaluate_hokom_claim_bundle']
