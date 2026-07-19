#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p5_masdar/engine.py — HOKOM_MASDAR_ENGINE canonical entrypoint
MASDAR_CANONICAL_OWNER   = HOKOM
MASDAR_CANONICAL_ENTRYPOINT = analyze_masdar
"""
from __future__ import annotations
import uuid
from typing import Optional

from .models import (
    MASDAR_ENGINE_ID, MASDAR_TYPES, MASDAR_VERDICTS,
    MasdarRequest, MasdarResult, MasdarCandidate, LicensedMasdar,
    DeferredMasdar, BlockedMasdar, MasdarResidual,
    MasdarEvidence, MasdarContradiction, MasdarTraceEvent,
)
from .rule_registry import get_rule_registry

# ── weak root classes that require MASDAR_DEFERRED for realization ────────────
_WEAK_CLASSES_DEFER = frozenset({
    'WEAK_MEDIAL', 'WEAK_FINAL', 'WEAK_INITIAL', 'HOLLOW',
    'DEFECTIVE', 'LAFIF_MAFRUQ', 'LAFIF_MAQRUN',
    'ASSIMILATED',
})

# ── FORM families that use productive rules (non-FORM_I) ─────────────────────
_PRODUCTIVE_FAMILIES = frozenset({
    'FORM_II', 'FORM_III', 'FORM_IV', 'FORM_V', 'FORM_VI',
    'FORM_VII', 'FORM_VIII', 'FORM_IX', 'FORM_X',
    'QUADRILITERAL_FORM_I',
})

# ── block families ─────────────────────────────────────────────────────────────
_BLOCK_FAMILIES = frozenset({'FA3IL_PARTICIPLE'})


def _cid() -> str:
    return uuid.uuid4().hex[:12]


def _ev(eid, etype, suff, src, detail=None) -> MasdarEvidence:
    return MasdarEvidence(
        evidence_id=eid, evidence_type=etype, sufficiency=suff, source=src, detail=detail
    )


def _co(cid, ctype, locus, detail) -> MasdarContradiction:
    return MasdarContradiction(
        contradiction_id=cid, contradiction_type=ctype, locus=locus, detail=detail
    )


def _te(step, stage, action, detail=None) -> MasdarTraceEvent:
    return MasdarTraceEvent(step=step, stage=stage, action=action, detail=detail)


# ── result builders ───────────────────────────────────────────────────────────

def _blocked_result(request, reason, contradictions, trace) -> MasdarResult:
    blk = BlockedMasdar(
        block_id='BLK-' + _cid(),
        reason=reason,
        contradictions=tuple(contradictions),
        trace=tuple(trace),
    )
    return MasdarResult(
        result_id='RES-' + _cid(),
        request=request,
        verdict='MASDAR_BLOCKED',
        multiplicity='NONE',
        licensed_masdars=(),
        deferred=None,
        blocked=blk,
        residuals=(),
        all_candidates=(),
        trace=tuple(trace),
        source_engine=MASDAR_ENGINE_ID,
    )


def _deferred_result(request, reason, candidates, missing, trace) -> MasdarResult:
    dfr = DeferredMasdar(
        deferral_id='DFR-' + _cid(),
        reason=reason,
        candidates=tuple(candidates),
        missing_evidence=tuple(missing),
        trace=tuple(trace),
    )
    return MasdarResult(
        result_id='RES-' + _cid(),
        request=request,
        verdict='MASDAR_DEFERRED',
        multiplicity='NONE',
        licensed_masdars=(),
        deferred=dfr,
        blocked=None,
        residuals=(),
        all_candidates=tuple(candidates),
        trace=tuple(trace),
        source_engine=MASDAR_ENGINE_ID,
    )


def _residual_result(request, code, reason, trace) -> MasdarResult:
    res = MasdarResidual(
        residual_id='RSI-' + _cid(),
        residual_code=code,
        surface=request.original_surface,
        verb=request.verbal_lemma,
        root=request.licensed_root,
        pattern=request.licensed_pattern,
        masdar_type=request.requested_masdar_type,
        current_candidates=(),
        missing_evidence=(reason,),
        blocking_condition=None,
        reason_code=reason,
        owner='HOKOM',
        future_closure_stage='HOKOM-MORPHOLOGY-MASDAR-LEXICON-01',
        status='OPEN',
    )
    return MasdarResult(
        result_id='RES-' + _cid(),
        request=request,
        verdict='MASDAR_RESIDUAL',
        multiplicity='NONE',
        licensed_masdars=(),
        deferred=None,
        blocked=None,
        residuals=(res,),
        all_candidates=(),
        trace=tuple(trace),
        source_engine=MASDAR_ENGINE_ID,
    )


# ── candidate builder from lexical entry ──────────────────────────────────────

def _candidate_from_lexicon(entry, request, root_ev, pattern_ev, ff_ev, cand_idx) -> MasdarCandidate:
    root = tuple(entry.get('root', []))
    slots = ('ROOT_SLOT_FA', 'ROOT_SLOT_AIN', 'ROOT_SLOT_LAM', 'ROOT_SLOT_LAM2')
    root_mapping = tuple(
        (slots[i], root[i]) for i in range(min(len(root), len(slots)))
    )

    lex_ev = _ev(
        f'EV-LEX-{cand_idx:02d}',
        'LEXICAL_MASDAR_ATTESTATION', 'SUFFICIENT',
        f'masdar_lexical_inventory[{entry.get("masdar_id")}]',
        f'pattern={entry.get("canonical_masdar_pattern")}'
    )

    return MasdarCandidate(
        candidate_id=f'CND-{_cid()}',
        masdar_type=entry.get('masdar_type', 'MASDAR_ASLI'),
        surface=entry.get('masdar_surface'),
        normalized_surface=entry.get('masdar_surface'),
        canonical_pattern=entry.get('canonical_masdar_pattern', ''),
        surface_pattern=entry.get('canonical_masdar_pattern', ''),
        underlying_pattern=entry.get('canonical_masdar_pattern', ''),
        source_verb=entry.get('verb_lemma'),
        root=root or None,
        root_class=entry.get('root_class'),
        verb_pattern=entry.get('verb_pattern'),
        verb_form_family=entry.get('form_family'),
        root_mapping=root_mapping,
        slot_mapping=(),
        augmentation_slots=(),
        inflectional_material=(),
        realization_operations=(),
        supporting_evidence=(root_ev, pattern_ev, ff_ev, lex_ev),
        contradicting_evidence=(),
        required_evidence=('LEXICAL_MASDAR_ATTESTATION',),
        evidence_rank='SUFFICIENT',
        sufficiency='SUFFICIENT',
        license_kind='LEXICAL_ATTESTATION',
        lexical_attestation=True,
        verdict='MASDAR_ACCEPTED',
        reason_codes=(),
        named_residual=None,
        trace=(),
    )


# ── candidate builder from productive rule ─────────────────────────────────────

def _candidate_from_rule(rule, request, root_ev, pattern_ev, ff_ev, masdar_pattern_id, cand_idx,
                         weak_defer=False) -> MasdarCandidate:
    root = tuple(request.licensed_root) if request.licensed_root else ()
    slots = ('ROOT_SLOT_FA', 'ROOT_SLOT_AIN', 'ROOT_SLOT_LAM', 'ROOT_SLOT_LAM2')
    root_mapping = tuple(
        (slots[i], root[i]) for i in range(min(len(root), len(slots)))
    )

    rule_ev = _ev(
        f'EV-RULE-{cand_idx:02d}',
        'PRODUCTIVE_MASDAR_RULE', 'SUFFICIENT',
        f'masdar_rule_registry[{rule["rule_id"]}]',
        f'pattern={masdar_pattern_id}'
    )

    verdict       = 'MASDAR_DEFERRED' if weak_defer else 'MASDAR_ACCEPTED'
    reason_codes  = ('WEAK_MASDAR_REALIZATION_GAP',) if weak_defer else ()
    named_residual = 'WEAK_MASDAR_REALIZATION_GAP' if weak_defer else None
    sufficiency   = 'CONTRIBUTORY' if weak_defer else 'SUFFICIENT'
    license_kind  = 'GOVERNED_DEFER' if weak_defer else 'PRODUCTIVE_RULE'

    return MasdarCandidate(
        candidate_id=f'CND-{_cid()}',
        masdar_type='MASDAR_ASLI',
        surface=None,
        normalized_surface=None,
        canonical_pattern=masdar_pattern_id,
        surface_pattern=masdar_pattern_id,
        underlying_pattern=masdar_pattern_id,
        source_verb=request.verbal_lemma or request.verbal_host,
        root=root or None,
        root_class=request.licensed_root_class,
        verb_pattern=request.licensed_pattern,
        verb_form_family=request.verb_form_family,
        root_mapping=root_mapping,
        slot_mapping=(),
        augmentation_slots=(),
        inflectional_material=(),
        realization_operations=(),
        supporting_evidence=(root_ev, pattern_ev, ff_ev, rule_ev),
        contradicting_evidence=(),
        required_evidence=tuple(rule.get('required_evidence', [])),
        evidence_rank='SUFFICIENT' if not weak_defer else 'CONTRIBUTORY',
        sufficiency=sufficiency,
        license_kind=license_kind,
        lexical_attestation=False,
        verdict=verdict,
        reason_codes=reason_codes,
        named_residual=named_residual,
        trace=(),
    )


# ── FORM_I generation ─────────────────────────────────────────────────────────

def _generate_form_i(request, trace, step_ref) -> MasdarResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('FORM_I', 'CHECK_LEXICAL_EVIDENCE', str(request.licensed_root))
    registry = get_rule_registry()
    root_key = tuple(request.licensed_root) if request.licensed_root else ()
    ff = request.verb_form_family or 'FORM_I'
    lex = registry.lexical_entries_for_root_and_ff(root_key, ff)

    if not lex:
        T('FORM_I', 'DEFER', 'FORM_I_LEXICAL_EVIDENCE_REQUIRED')
        return _deferred_result(
            request, 'FORM_I_LEXICAL_EVIDENCE_REQUIRED',
            candidates=(),
            missing=('LEXICAL_MASDAR_ATTESTATION',),
            trace=trace,
        )

    T('FORM_I', 'LEXICAL_EVIDENCE_FOUND', f'{len(lex)} entries')
    root_ev    = _ev('EV-ROOT-01', 'ROOT_LICENSE_EVIDENCE', 'SUFFICIENT', 'upstream', str(root_key))
    pattern_ev = _ev('EV-PAT-01',  'VERB_PATTERN_EVIDENCE', 'SUFFICIENT', 'upstream', request.licensed_pattern)
    ff_ev      = _ev('EV-FF-01',   'FORM_FAMILY_EVIDENCE',  'SUFFICIENT', 'upstream', ff)

    candidates = []
    for idx, entry in enumerate(lex):
        cand = _candidate_from_lexicon(entry, request, root_ev, pattern_ev, ff_ev, idx)
        candidates.append(cand)
        T('FORM_I', 'CANDIDATE_BUILT', cand.canonical_pattern)

    return _finalize(request, candidates, trace)


# ── MIMI, MARRA, HAYAA, ISM_MASDAR ───────────────────────────────────────────

def _generate_mimi(request, trace, step_ref) -> MasdarResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('MIMI', 'DEFER', 'MIMI_DERIVATIONAL_CATEGORY_AMBIGUITY')
    return _deferred_result(
        request, 'MIMI_DERIVATIONAL_CATEGORY_AMBIGUITY', (), ('LEXICAL_MASDAR_ATTESTATION',), trace
    )


def _generate_marra(request, trace, step_ref) -> MasdarResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('MARRA', 'DEFER', 'MASDAR_SUBTYPE_CONTEXT_REQUIRED')
    return _deferred_result(
        request, 'MASDAR_SUBTYPE_CONTEXT_REQUIRED', (), ('PARADIGM_CROSS_FORM_EVIDENCE',), trace
    )


def _generate_hayaa(request, trace, step_ref) -> MasdarResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('HAYAA', 'DEFER', 'MASDAR_SUBTYPE_CONTEXT_REQUIRED')
    return _deferred_result(
        request, 'MASDAR_SUBTYPE_CONTEXT_REQUIRED', (), ('PARADIGM_CROSS_FORM_EVIDENCE',), trace
    )


def _generate_ism_masdar(request, trace, step_ref) -> MasdarResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('ISM_MASDAR', 'RESIDUAL', 'ISM_MASDAR_LEXICON_GAP')
    return _residual_result(request, 'ISM_MASDAR_LEXICON_GAP', 'ISM_MASDAR_LEXICON_GAP', trace)


# ── productive augmented generation ──────────────────────────────────────────

def _generate_augmented(request, form_family, trace, step_ref) -> MasdarResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    registry = get_rule_registry()
    rules = registry.rules_for_form_family(form_family)
    rules = [r for r in rules if r.get('status') == 'ACTIVE']

    if not rules:
        T('AUGMENTED', 'DEFER', f'NO_ACTIVE_RULES_FOR_{form_family}')
        return _deferred_result(request, f'NO_ACTIVE_RULES_FOR_{form_family}', (), (), trace)

    root_key   = tuple(request.licensed_root) if request.licensed_root else ()
    root_class = request.licensed_root_class or 'UNKNOWN'

    # Check if root class is weak — defer surface realization
    is_weak = any(
        wc in root_class.upper()
        for wc in ['WEAK', 'HOLLOW', 'DEFECTIVE', 'LAFIF', 'ASSIMILATED']
    )

    root_ev    = _ev('EV-ROOT-01', 'ROOT_LICENSE_EVIDENCE', 'SUFFICIENT', 'upstream', str(root_key))
    pattern_ev = _ev('EV-PAT-01',  'VERB_PATTERN_EVIDENCE', 'SUFFICIENT', 'upstream', request.licensed_pattern)
    ff_ev      = _ev('EV-FF-01',   'FORM_FAMILY_EVIDENCE',  'SUFFICIENT', 'upstream', form_family)

    candidates = []
    for idx, rule in enumerate(rules):
        for masdar_pattern in rule.get('masdar_patterns', []):
            T('AUGMENTED', 'APPLY_RULE', f'{rule["rule_id"]} → {masdar_pattern}')
            cand = _candidate_from_rule(
                rule, request, root_ev, pattern_ev, ff_ev,
                masdar_pattern, idx, weak_defer=is_weak
            )
            candidates.append(cand)

    return _finalize(request, candidates, trace)


# ── finalize ──────────────────────────────────────────────────────────────────

def _finalize(request, candidates, trace) -> MasdarResult:
    accepted   = [c for c in candidates if c.verdict == 'MASDAR_ACCEPTED']
    deferred_c = [c for c in candidates if c.verdict == 'MASDAR_DEFERRED']

    if accepted:
        licensed = tuple(
            LicensedMasdar(
                masdar_id='LM-' + _cid(),
                candidate=c,
                licensing_evidence=c.supporting_evidence,
                license_kind=c.license_kind,
            )
            for c in accepted
        )
        multiplicity = 'MULTIPLE_LICENSED' if len(licensed) > 1 else 'SINGLE'
        return MasdarResult(
            result_id='RES-' + _cid(),
            request=request,
            verdict='MASDAR_ACCEPTED',
            multiplicity=multiplicity,
            licensed_masdars=licensed,
            deferred=None,
            blocked=None,
            residuals=(),
            all_candidates=tuple(candidates),
            trace=tuple(trace),
            source_engine=MASDAR_ENGINE_ID,
        )
    elif deferred_c:
        dfr = DeferredMasdar(
            deferral_id='DFR-' + _cid(),
            reason=deferred_c[0].reason_codes[0] if deferred_c[0].reason_codes else 'WEAK_MASDAR_REALIZATION_GAP',
            candidates=tuple(deferred_c),
            missing_evidence=deferred_c[0].required_evidence,
            trace=tuple(trace),
        )
        return MasdarResult(
            result_id='RES-' + _cid(),
            request=request,
            verdict='MASDAR_DEFERRED',
            multiplicity='NONE',
            licensed_masdars=(),
            deferred=dfr,
            blocked=None,
            residuals=(),
            all_candidates=tuple(candidates),
            trace=tuple(trace),
            source_engine=MASDAR_ENGINE_ID,
        )
    else:
        return _deferred_result(request, 'NO_CANDIDATES_BUILT', (), (), trace)


# ── VALIDATE_SUPPLIED and ANALYZE_SURFACE modes ───────────────────────────────

def _validate_supplied(request, form_family, trace, step_ref) -> MasdarResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    supplied = request.supplied_masdar_surface
    T('VALIDATE', 'CHECK_SUPPLIED', supplied)

    if not supplied:
        T('VALIDATE', 'BLOCK', 'NO_SUPPLIED_SURFACE')
        return _blocked_result(
            request, 'VERBAL_INPUT_NOT_LICENSED',
            [_co('C-SUP', 'SURFACE_MAPPING_INCOMPLETE', 'supplied_masdar_surface', 'no surface supplied')],
            trace
        )

    registry = get_rule_registry()
    root_key = tuple(request.licensed_root) if request.licensed_root else ()

    if form_family in _BLOCK_FAMILIES:
        T('VALIDATE', 'BLOCK', 'NON_VERBAL_ORIGIN')
        return _blocked_result(request, 'NON_VERBAL_ORIGIN', [
            _co('C-FF', 'NON_VERBAL_ORIGIN', 'form_family', form_family)
        ], trace)
    elif form_family not in _PRODUCTIVE_FAMILIES:
        lex = registry.lexical_entries_for_root_and_ff(root_key, form_family or 'FORM_I')
        surfaces = [e.get('masdar_surface') for e in lex]
        if supplied not in surfaces:
            T('VALIDATE', 'DEFER', 'SURFACE_NOT_IN_LEXICON')
            return _deferred_result(request, 'FORM_I_LEXICAL_EVIDENCE_REQUIRED', (), ('LEXICAL_MASDAR_ATTESTATION',), trace)
    else:
        rules = [r for r in registry.rules_for_form_family(form_family) if r.get('status') == 'ACTIVE']
        allowed_patterns = {p for r in rules for p in r.get('masdar_patterns', [])}
        T('VALIDATE', 'PATTERNS_CHECKED', str(allowed_patterns))

    T('VALIDATE', 'DEFERRED', 'SURFACE_VALIDATION_REQUIRES_FULL_ALIGNMENT')
    return _deferred_result(request, 'SURFACE_VALIDATION_REQUIRES_FULL_ALIGNMENT', (), ('SURFACE_PATTERN_ALIGNMENT',), trace)


def _analyze_surface(request, form_family, trace, step_ref) -> MasdarResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('ANALYZE', 'SURFACE_ANALYSIS', request.original_surface)
    T('ANALYZE', 'DEFER', 'SURFACE_ANALYSIS_REQUIRES_VERBAL_ANCHOR')
    return _deferred_result(
        request, 'SURFACE_ANALYSIS_REQUIRES_VERBAL_ANCHOR', (),
        ('VERBAL_HOST_EVIDENCE', 'ROOT_LICENSE_EVIDENCE'), trace
    )


# ══════════════════════════════════════════════════════════════════════════════
# CANONICAL_MASDAR_ENTRYPOINT
# ══════════════════════════════════════════════════════════════════════════════

def analyze_masdar(request: MasdarRequest) -> MasdarResult:
    """
    CANONICAL_MASDAR_ENTRYPOINT — HOKOM_MASDAR_ENGINE

    Accepts a MasdarRequest and returns a MasdarResult.
    Does NOT re-extract root or wazn. Consumes upstream contracts only.
    """
    trace    = []
    step_ref = [0]

    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('GATE', 'MASDAR_GATE_OPEN', f'mode={request.mode} ff={request.verb_form_family!r}')

    # ── 1. Upstream license gate ──────────────────────────────────────────────
    if request.licensed_root is None:
        T('GATE', 'BLOCK', 'ROOT_NOT_LICENSED')
        return _blocked_result(request, 'MASDAR_NOT_OPENED:ROOT_NOT_LICENSED', [
            _co('C-R', 'UPSTREAM_BLOCKED', 'licensed_root', 'None')
        ], trace)

    if request.licensed_pattern is None:
        T('GATE', 'BLOCK', 'PATTERN_NOT_LICENSED')
        return _blocked_result(request, 'MASDAR_NOT_OPENED:PATTERN_NOT_LICENSED', [
            _co('C-P', 'UPSTREAM_BLOCKED', 'licensed_pattern', 'None')
        ], trace)

    if request.verbal_host is None and request.verbal_lemma is None:
        T('GATE', 'DEFER', 'VERBHOOD_NOT_LICENSED')
        return _deferred_result(
            request, 'MASDAR_NOT_OPENED:VERBHOOD_NOT_LICENSED',
            (), ('VERBAL_HOST_EVIDENCE',), trace
        )

    form_family = request.verb_form_family or ''
    T('GATE', 'PASS', f'root={request.licensed_root} ff={form_family!r}')

    # ── 2. Block non-verbal form families ────────────────────────────────────
    if form_family in _BLOCK_FAMILIES:
        T('GATE', 'BLOCK', f'NON_VERBAL_ORIGIN:{form_family}')
        return _blocked_result(request, 'VERBAL_INPUT_NOT_LICENSED', [
            _co('C-FF', 'NON_VERBAL_ORIGIN', 'form_family',
                f'{form_family} is not a verbal source for masdar generation')
        ], trace)

    # ── 3. Route by requested masdar type ────────────────────────────────────
    mtype = request.requested_masdar_type or 'auto'

    if mtype == 'MASDAR_MIMI':
        return _generate_mimi(request, trace, step_ref)
    if mtype == 'MASDAR_MARRA':
        return _generate_marra(request, trace, step_ref)
    if mtype == 'MASDAR_HAYAA':
        return _generate_hayaa(request, trace, step_ref)
    if mtype == 'ISM_MASDAR':
        return _generate_ism_masdar(request, trace, step_ref)

    # ── 4. Route by mode ──────────────────────────────────────────────────────
    if request.mode == 'VALIDATE_SUPPLIED_MASDAR':
        return _validate_supplied(request, form_family, trace, step_ref)
    if request.mode == 'ANALYZE_MASDAR_SURFACE':
        return _analyze_surface(request, form_family, trace, step_ref)

    # GENERATE_FROM_VERB
    # ── 5. FORM_I: lexical evidence required ─────────────────────────────────
    if form_family in ('FORM_I', '', 'FA3IL_PARTICIPLE'):
        if form_family == 'FA3IL_PARTICIPLE':
            T('GATE', 'BLOCK', 'NON_VERBAL_ORIGIN:FA3IL_PARTICIPLE_REDUNDANT_CHECK')
            return _blocked_result(request, 'VERBAL_INPUT_NOT_LICENSED', [
                _co('C-FF', 'NON_VERBAL_ORIGIN', 'form_family', 'FA3IL_PARTICIPLE')
            ], trace)
        return _generate_form_i(request, trace, step_ref)

    # ── 6. Productive augmented forms ─────────────────────────────────────────
    if form_family in _PRODUCTIVE_FAMILIES:
        return _generate_augmented(request, form_family, trace, step_ref)

    # ── 7. Unknown form_family ─────────────────────────────────────────────────
    T('GATE', 'DEFER', f'UNKNOWN_FORM_FAMILY:{form_family}')
    return _deferred_result(
        request, f'UNKNOWN_FORM_FAMILY:{form_family}',
        (), ('FORM_FAMILY_EVIDENCE',), trace
    )
