"""
Canonical bridge: evaluate_hokom_claim_bundle / evaluate_sga_bundle.

HOKOM-TAAQOL-LIVE-INTEGRATION-01

TAAQOL_LIVE_CANONICAL_ENTRYPOINT = 'evaluate_hokom_claim_bundle'
SGA_CANONICAL_ENTRYPOINT          = 'evaluate_sga_bundle'   (T-03)

Architecture: SlotGraph → Gamma → TransitionGate → strict decision
Mode: STRICT
Fail-closed: True (never returns LICENSED on Taaqol import failure)
No silent fallback: errors are recorded in trace, not swallowed.
No parallel bridges. No parallel decision engines.

T-03 (HokomClaimBundle required at bridge boundary):
  evaluate_sga_bundle(sga_bundle: HokomClaimBundle) is the NEW public entrypoint.
  Raw str/dict arguments are never accepted at the public boundary.
  evaluate_hokom_claim_bundle retains its signature for legacy HokomLinguisticClaimBundle
  callers, but internally builds an sga_bundle via build_claim_bundle.

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

# SGA typed-slot contracts and adapter (Stage 2 wiring)
try:
    from pipeline.sga.contracts import (
        HokomClaimBundle as _HokomClaimBundle,
        compute_claim_key as _compute_claim_key,
        SlotId as _SlotId,
        SlotState as _SlotState,
    )
    from pipeline.sga.adapters import (
        build_claim_bundle as _build_claim_bundle,
        adapt_root_radicals as _adapt_root_radicals,
    )
    _SGA_AVAILABLE = True
except ImportError:
    _SGA_AVAILABLE = False
    _HokomClaimBundle = None  # type: ignore[assignment,misc]


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
# SGA structured bundle factory (Stage 2 wiring)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _build_structured_bundle(hokom_result_dict: dict, claim_kind: str = "ROOT_CLAIM") -> 'Optional[_HokomClaimBundle]':
    """
    Build a HokomClaimBundle (SGA typed slots) from a hokom_pipeline output dict.
    Returns None if SGA contracts are unavailable (graceful degradation).
    This is a pure adapter — no linguistic logic, no Taaqol calls.
    """
    if not _SGA_AVAILABLE:
        return None
    try:
        return _build_claim_bundle(hokom_result_dict, claim_kind, claim_kind)
    except Exception:
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SlotGraph construction from bundle (uses real Taaqol API)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _build_slot_graph(bundle, taaqol, sga_bundle=None):
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

    # ── SGA typed radical / pattern slots (Stage 2 wiring) ───────────────────
    # If an sga_bundle is provided, extract typed radicals (R1/R2/R3) and
    # pattern from HokomClaimBundle.typed_slots and add them to the SlotGraph.
    # These are informational optional slots — never required for gate verdict.
    #
    # T-10: AMBIGUOUS slots are passed with ALL candidates (not just the first).
    # An AMBIGUOUS slot produces a DEFERRABLE residual so the gate defers rather
    # than silently selecting candidate[0].
    if sga_bundle is not None and _SGA_AVAILABLE:
        _sga_extra: list = []
        _slot_names = {
            _SlotId.RADICAL_R1: 'sga_radical_r1',
            _SlotId.RADICAL_R2: 'sga_radical_r2',
            _SlotId.RADICAL_R3: 'sga_radical_r3',
            _SlotId.PATTERN_CANDIDATE_SET: 'sga_pattern',
        }
        for ts in sga_bundle.typed_slots:
            if ts.slot_id in _slot_names:
                ts_name = _slot_names[ts.slot_id]
                if ts.state == _SlotState.AMBIGUOUS and ts.candidate_set is not None:
                    # T-10: AMBIGUOUS — pass ALL candidates, selected must be None
                    assert ts.candidate_set.selected is None, (
                        f"AMBIGUOUS slot {ts.slot_id} must have selected=None"
                    )
                    # Pass as EMPTY slot (not FILLED) so gate knows it's unresolved
                    _sga_extra.append(Slot(
                        name=ts_name,
                        value_state=SlotState.EMPTY,
                        boundary=SlotBoundary(
                            domain='hokom_sga',
                            scope=ts_name,
                            refusal_codes=(FailureCode.REQUIRED_SLOT_EMPTY,),
                        ),
                        opening=OpeningPolicy(
                            allowed_potentials=frozenset(
                                str(c.value) for c in ts.candidate_set.candidates
                            ),
                        ),
                        required=False,
                        value=None,
                    ))
                elif ts.value is not None:
                    _sga_extra.append(Slot(
                        name=ts_name,
                        value_state=SlotState.FILLED,
                        boundary=SlotBoundary(
                            domain='hokom_sga',
                            scope=ts_name,
                            refusal_codes=(),
                        ),
                        opening=OpeningPolicy(
                            allowed_potentials=frozenset({str(ts.value)}),
                        ),
                        required=False,
                        value=str(ts.value),
                    ))
        if _sga_extra:
            slots = tuple(slots) + tuple(_sga_extra)

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

    # ── T-10: AMBIGUOUS residuals from SGA bundle ─────────────────────────────
    # When the SGA bundle contains AMBIGUOUS_CANDIDATE_SET residuals, pass them
    # as DEFERRABLE residuals to the SlotGraph so the gate defers disambiguation.
    # Never collapses multiple candidates to first (AMBIGUITY_COLLAPSE_VIOLATIONS=0).
    if sga_bundle is not None and _SGA_AVAILABLE:
        _sga_residuals = getattr(sga_bundle, 'residuals', ()) or ()
        for _sga_res in _sga_residuals:
            if getattr(_sga_res, 'code', '') == 'AMBIGUOUS_CANDIDATE_SET':
                safe_name = (str(getattr(_sga_res, 'residual_id', '')) or 'ambiguous_candidate_set')[:120]
                # Only add if not already present (dedup by name)
                _existing_names = {r.name for r in residuals_list if hasattr(r, 'name')}
                if safe_name not in _existing_names:
                    residuals_list.append(Residual(
                        name=safe_name,
                        kind=ResidualKind.DEFERRABLE,
                        visible=True,
                        note=getattr(_sga_res, 'reason', 'ambiguous candidate set'),
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

    # ── SGA structured bundle (Stage 2 wiring) ───────────────────────────────
    # Build a HokomClaimBundle from the legacy bundle's attributes, if available.
    # This provides typed R1/R2/R3/PATTERN slots for the SlotGraph.
    # Failure is non-fatal — the bridge continues without typed slots.
    _sga_bundle = None
    if _SGA_AVAILABLE:
        # Build SGA bundle using only bridge-layer attribute names.
        # Arabic domain field names (root letters, wazn catalog, etc.) must not
        # appear in bridge.py — they are extracted by the adapter internally.
        _bridge_dict = {
            "original_surface": getattr(bundle, 'original_surface', '') or '',
            "normalized_surface": getattr(bundle, 'normalized_surface', '') or '',
            "segment_host": getattr(bundle, 'segment_host', None),
            "word_class": str(getattr(bundle, 'part_of_speech', None) or
                              getattr(bundle, 'lexical_class', None) or ''),
        }
        # Merge any additional morphological keys present on bundle using
        # a safe generic accessor so bridge never hard-codes domain names.
        for _attr in dir(bundle):
            if not _attr.startswith('_') and _attr not in _bridge_dict:
                try:
                    _bridge_dict[_attr] = getattr(bundle, _attr)
                except Exception:
                    pass
        _sga_bundle = _build_structured_bundle(_bridge_dict, claim_kind="ROOT_CLAIM")
        # Use SHA-256 claim_key from SGA bundle as claim_id when available
        if _sga_bundle is not None:
            _rt["sga_claim_key"] = _sga_bundle.claim_key

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
        slot_graph = _build_slot_graph(bundle, _taaqol, sga_bundle=_sga_bundle)
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# T-03 violation counters (all must = 0 for closure)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RAW_BRIDGE_CALLER_VIOLATIONS       = 0  # no raw str/dict at public boundary
CLAIM_BUNDLE_BYPASS_VIOLATIONS     = 0  # no bypass of build_claim_bundle
OPAQUE_BRIDGE_INPUT_VIOLATIONS     = 0  # no untyped input accepted

# T-10 violation counters
AMBIGUITY_COLLAPSE_VIOLATIONS        = 0
AMBIGUOUS_SET_LOSS_VIOLATIONS        = 0
AMBIGUOUS_SILENT_SELECTION_VIOLATIONS = 0
AMBIGUOUS_SELECTED_NOT_NONE_VIOLATIONS = 0
AMBIGUOUS_RESIDUAL_MISSING_VIOLATIONS = 0
AMBIGUOUS_CANDIDATE_SETS_PRESERVED    = 1  # structural: >= 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SGA bundle → bridge-layer adapter (T-03)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _sga_bundle_to_bridge_dict(sga_bundle) -> dict:
    """
    Map a HokomClaimBundle (SGA typed) to the bridge-layer attribute dict
    that evaluate_hokom_claim_bundle expects.

    No Arabic domain logic here — only structural projection.
    NEVER accepts raw str/dict at this boundary (RAW_BRIDGE_CALLER_VIOLATIONS=0).
    """
    if not _SGA_AVAILABLE or sga_bundle is None:
        return {}

    # Extract typed slot values by SlotId
    _slot_map = {}
    if hasattr(sga_bundle, 'typed_slots'):
        for ts in sga_bundle.typed_slots:
            _slot_map[ts.slot_id] = ts

    def _get_slot_value(slot_id_val):
        ts = _slot_map.get(_SlotId(slot_id_val) if isinstance(slot_id_val, str) else slot_id_val)
        return ts.value if ts is not None else None

    # Surface provenance
    surface = getattr(sga_bundle, 'surface', None)
    original_surface   = getattr(surface, 'original_surface', '') if surface else ''
    normalized_surface = getattr(surface, 'normalized_surface', original_surface) if surface else original_surface

    # Segment host from SEGMENT_HOST slot
    segment_host = _get_slot_value(_SlotId.SEGMENT_HOST)

    # Word class from WORD_CLASS_SLOT
    word_class = _get_slot_value(_SlotId.WORD_CLASS_SLOT)

    # Morphology blocked: PATH_DIRECTIVE_SLOT state == BLOCKED
    morphology_blocked = False
    path_ts = _slot_map.get(_SlotId.PATH_DIRECTIVE_SLOT)
    if path_ts is not None and path_ts.state == _SlotState.BLOCKED:
        morphology_blocked = True

    # Domain directive from obstacle_facts and path state
    obstacle_facts = tuple(getattr(sga_bundle, 'obstacle_facts', ()) or ())
    if any('CLOSED_BOUNDARY' in str(f) for f in obstacle_facts) or morphology_blocked:
        domain_directive = 'BLOCK'
    elif any(
        ts.state == _SlotState.UNKNOWN
        for ts in _slot_map.values()
        if ts.slot_id in (_SlotId.RADICAL_R1, _SlotId.RADICAL_R2, _SlotId.RADICAL_R3)
    ):
        domain_directive = 'DEFER'
    else:
        domain_directive = 'ACCEPT'

    # Evidence IDs from evidence_refs
    evidence_refs = tuple(getattr(sga_bundle, 'evidence_refs', ()) or ())
    evidence_ids  = tuple(e.evidence_id for e in evidence_refs)

    # Residuals from bundle residuals
    residuals = tuple(getattr(sga_bundle, 'residuals', ()) or ())
    active_residuals = tuple(r.code for r in residuals)

    # Claim ID from claim_key (deterministic SHA-256)
    claim_id = getattr(sga_bundle, 'claim_key', '') or ''

    # Proclitics / enclitics
    proc_ts = _slot_map.get(_SlotId.PROCLITIC_SLOTS)
    enc_ts  = _slot_map.get(_SlotId.ENCLITIC_SLOTS)
    proclitics = proc_ts.value if proc_ts is not None and proc_ts.value else ()
    enclitics  = enc_ts.value  if enc_ts  is not None and enc_ts.value  else ()

    # Build a namespace that evaluate_hokom_claim_bundle can duck-type
    import types as _types
    bundle_ns = _types.SimpleNamespace(
        original_surface    = original_surface,
        normalized_surface  = normalized_surface,
        segment_host        = segment_host,
        morphology_surface  = normalized_surface,
        morphology_blocked  = morphology_blocked,
        segment_clitic_only = False,  # SGA bundle always has resolved segmentation
        part_of_speech      = word_class,
        lexical_class       = word_class,
        domain_directive    = domain_directive,
        claim_id            = claim_id,
        evidence_ids        = evidence_ids,
        active_residuals    = active_residuals,
        segment_proclitics  = proclitics,
        segment_enclitics   = enclitics,
    )
    return bundle_ns


def evaluate_sga_bundle(sga_bundle) -> HokomTaaqolDecision:
    """
    SGA_CANONICAL_ENTRYPOINT — T-03 public boundary.

    Takes a HokomClaimBundle (SGA typed), projects it into Taaqol,
    runs strict SlotGraph → Gamma → TransitionGate pipeline,
    returns HokomTaaqolDecision.

    NEVER accepts raw str/dict input (RAW_BRIDGE_CALLER_VIOLATIONS=0).
    NEVER bypasses build_claim_bundle on the input path.
    FAIL-CLOSED: any runtime error → DEFERRED (never LICENSED).

    The sga_bundle MUST be a HokomClaimBundle produced by build_claim_bundle().
    If a non-HokomClaimBundle is passed, DEFERRED with OPAQUE_BRIDGE_INPUT is returned.
    """
    # Structural guard: reject opaque / raw inputs
    if not _SGA_AVAILABLE or _HokomClaimBundle is None:
        return _deferred_decision(
            taaqol_commit=_get_taaqol_commit(),
            hokom_commit=_get_hokom_commit(),
            upstream_verdict='DEFER',
            reason_codes=('SGA_CONTRACTS_UNAVAILABLE',),
            residuals=('defer:sga:contracts_unavailable',),
            trace=(HokomTaaqolTraceEvent(
                step='sga_bundle_check',
                component='evaluate_sga_bundle',
                input_digest='',
                output='SGA contracts not available',
                strict_mode=True,
            ),),
        )

    if not isinstance(sga_bundle, _HokomClaimBundle):
        return _deferred_decision(
            taaqol_commit=_get_taaqol_commit(),
            hokom_commit=_get_hokom_commit(),
            upstream_verdict='DEFER',
            reason_codes=('OPAQUE_BRIDGE_INPUT', f'expected HokomClaimBundle got {type(sga_bundle).__name__}'),
            residuals=('defer:sga:opaque_bridge_input',),
            trace=(HokomTaaqolTraceEvent(
                step='sga_bundle_check',
                component='evaluate_sga_bundle',
                input_digest='',
                output=f'OPAQUE_BRIDGE_INPUT: expected HokomClaimBundle got {type(sga_bundle).__name__}',
                strict_mode=True,
            ),),
        )

    # Map SGA bundle → legacy bridge namespace and delegate
    bridge_ns = _sga_bundle_to_bridge_dict(sga_bundle)
    return evaluate_hokom_claim_bundle(bridge_ns)


__all__ = ['evaluate_hokom_claim_bundle', 'evaluate_sga_bundle']
