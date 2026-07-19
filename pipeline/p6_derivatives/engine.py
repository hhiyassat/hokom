#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p6_derivatives/engine.py — HOKOM_DERIVATIVES_ENGINE canonical entrypoint
DERIVATIVES_CANONICAL_OWNER      = HOKOM
CANONICAL_DERIVATIVES_ENTRYPOINT = analyze_derivative
"""
from __future__ import annotations
import uuid
from typing import Optional

from .models import (
    DERIVATIVES_ENGINE_ID, DERIVATIVE_TYPES, DERIVATIVE_VERDICTS,
    DerivativeRequest, DerivativeResult, DerivativeCandidate, LicensedDerivative,
    DeferredDerivative, BlockedDerivative, DerivativeResidual,
    DerivativeEvidence, DerivativeContradiction, DerivativeTraceEvent,
)
from .rule_registry import get_rule_registry

# ── productive form families for ISM_FA3IL / ISM_MAF3UL ──────────────────────
_PRODUCTIVE_FAMILIES_FA3IL = frozenset({
    'FORM_I', 'FORM_II', 'FORM_III', 'FORM_IV', 'FORM_V',
    'FORM_VI', 'FORM_VII', 'FORM_VIII', 'FORM_X',
    'FA3IL_PARTICIPLE',  # treated as FORM_I for derivatives (RULE-D-01)
})

_PRODUCTIVE_FAMILIES_MAF3UL = frozenset({
    'FORM_I', 'FORM_II', 'FORM_III', 'FORM_IV', 'FORM_V',
    'FORM_VI', 'FORM_VII', 'FORM_VIII', 'FORM_X',
})

# ── types requiring lexical evidence (no productive rule) ─────────────────────
_LEXICAL_REQUIRED_TYPES = frozenset({
    'SIFA_MUSHABBAHA', 'MUBALGHA', 'ISM_ZAMAN', 'ISM_MAKAN', 'ISM_ALA',
})

# ── auto mode: generate these two productive types ────────────────────────────
_AUTO_TYPES = ('ISM_FA3IL', 'ISM_MAF3UL')


def _cid() -> str:
    return uuid.uuid4().hex[:12]


def _ev(eid, etype, suff, src, detail=None) -> DerivativeEvidence:
    return DerivativeEvidence(
        evidence_id=eid, evidence_type=etype, sufficiency=suff, source=src, detail=detail
    )


def _co(cid, ctype, locus, detail) -> DerivativeContradiction:
    return DerivativeContradiction(
        contradiction_id=cid, contradiction_type=ctype, locus=locus, detail=detail
    )


def _te(step, stage, action, detail=None) -> DerivativeTraceEvent:
    return DerivativeTraceEvent(step=step, stage=stage, action=action, detail=detail)


# ── result builders ───────────────────────────────────────────────────────────

def _blocked_result(request, reason, contradictions, trace) -> DerivativeResult:
    blk = BlockedDerivative(
        block_id='BLK-' + _cid(),
        reason=reason,
        contradictions=tuple(contradictions),
        trace=tuple(trace),
    )
    return DerivativeResult(
        result_id='RES-' + _cid(),
        request=request,
        verdict='DERIVATIVE_BLOCKED',
        multiplicity='NONE',
        licensed_derivatives=(),
        deferred=None,
        blocked=blk,
        residuals=(),
        all_candidates=(),
        trace=tuple(trace),
        source_engine=DERIVATIVES_ENGINE_ID,
    )


def _deferred_result(request, reason, candidates, missing, trace) -> DerivativeResult:
    dfr = DeferredDerivative(
        deferral_id='DFR-' + _cid(),
        reason=reason,
        candidates=tuple(candidates),
        missing_evidence=tuple(missing),
        trace=tuple(trace),
    )
    return DerivativeResult(
        result_id='RES-' + _cid(),
        request=request,
        verdict='DERIVATIVE_DEFERRED',
        multiplicity='NONE',
        licensed_derivatives=(),
        deferred=dfr,
        blocked=None,
        residuals=(),
        all_candidates=tuple(candidates),
        trace=tuple(trace),
        source_engine=DERIVATIVES_ENGINE_ID,
    )


def _residual_result(request, code, reason, trace) -> DerivativeResult:
    res = DerivativeResidual(
        residual_id='RSI-' + _cid(),
        residual_code=code,
        surface=request.original_surface,
        verb=request.verbal_lemma,
        root=request.licensed_root,
        pattern=request.licensed_pattern,
        derivative_type=request.derivative_type,
        current_candidates=(),
        missing_evidence=(reason,),
        blocking_condition=None,
        reason_code=reason,
        owner='HOKOM',
        future_closure_stage='HOKOM-MORPHOLOGY-DERIVATIVES-LEXICON-01',
        status='OPEN',
    )
    return DerivativeResult(
        result_id='RES-' + _cid(),
        request=request,
        verdict='DERIVATIVE_RESIDUAL',
        multiplicity='NONE',
        licensed_derivatives=(),
        deferred=None,
        blocked=None,
        residuals=(res,),
        all_candidates=(),
        trace=tuple(trace),
        source_engine=DERIVATIVES_ENGINE_ID,
    )


# ── candidate builder from lexical entry ──────────────────────────────────────

def _candidate_from_lexicon(entry, request, root_ev, pattern_ev, ff_ev, cand_idx,
                             dtype_override=None) -> DerivativeCandidate:
    root = tuple(entry.get('root', []))
    slots = ('ROOT_SLOT_FA', 'ROOT_SLOT_AIN', 'ROOT_SLOT_LAM', 'ROOT_SLOT_LAM2')
    root_mapping = tuple(
        (slots[i], root[i]) for i in range(min(len(root), len(slots)))
    )
    dtype = dtype_override or entry.get('derivative_type', 'ISM_FA3IL')

    lex_ev = _ev(
        f'EV-LEX-{cand_idx:02d}',
        'LEXICAL_DERIVATIVE_ATTESTATION', 'SUFFICIENT',
        f'derivative_lexical_inventory[{entry.get("deriv_id")}]',
        f'pattern={entry.get("canonical_derivative_pattern")}'
    )

    return DerivativeCandidate(
        candidate_id=f'CND-{_cid()}',
        derivative_type=dtype,
        surface=entry.get('derivative_surface'),
        normalized_surface=entry.get('derivative_surface'),
        canonical_pattern=entry.get('canonical_derivative_pattern', ''),
        surface_pattern=entry.get('canonical_derivative_pattern', ''),
        underlying_pattern=entry.get('canonical_derivative_pattern', ''),
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
        required_evidence=('LEXICAL_DERIVATIVE_ATTESTATION',),
        evidence_rank='SUFFICIENT',
        sufficiency='SUFFICIENT',
        license_kind='LEXICAL_ATTESTATION',
        lexical_attestation=True,
        verdict='DERIVATIVE_ACCEPTED',
        reason_codes=(),
        named_residual=None,
        trace=(),
    )


# ── candidate builder from productive rule ────────────────────────────────────

def _candidate_from_rule(rule, request, root_ev, pattern_ev, ff_ev,
                          deriv_pattern_id, cand_idx) -> DerivativeCandidate:
    root = tuple(request.licensed_root) if request.licensed_root else ()
    slots = ('ROOT_SLOT_FA', 'ROOT_SLOT_AIN', 'ROOT_SLOT_LAM', 'ROOT_SLOT_LAM2')
    root_mapping = tuple(
        (slots[i], root[i]) for i in range(min(len(root), len(slots)))
    )

    rule_ev = _ev(
        f'EV-RULE-{cand_idx:02d}',
        'PRODUCTIVE_DERIVATIVE_RULE', 'SUFFICIENT',
        f'derivative_rule_registry[{rule["rule_id"]}]',
        f'pattern={deriv_pattern_id}'
    )

    dtype = rule.get('derivative_type', 'ISM_FA3IL')

    return DerivativeCandidate(
        candidate_id=f'CND-{_cid()}',
        derivative_type=dtype,
        surface=None,
        normalized_surface=None,
        canonical_pattern=deriv_pattern_id,
        surface_pattern=deriv_pattern_id,
        underlying_pattern=deriv_pattern_id,
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
        evidence_rank='SUFFICIENT',
        sufficiency='SUFFICIENT',
        license_kind='PRODUCTIVE_RULE',
        lexical_attestation=False,
        verdict='DERIVATIVE_ACCEPTED',
        reason_codes=(),
        named_residual=None,
        trace=(),
    )


# ── finalize ──────────────────────────────────────────────────────────────────

def _finalize(request, candidates, trace) -> DerivativeResult:
    accepted   = [c for c in candidates if c.verdict == 'DERIVATIVE_ACCEPTED']
    deferred_c = [c for c in candidates if c.verdict == 'DERIVATIVE_DEFERRED']

    if accepted:
        licensed = tuple(
            LicensedDerivative(
                derivative_id='LD-' + _cid(),
                candidate=c,
                licensing_evidence=c.supporting_evidence,
                license_kind=c.license_kind,
            )
            for c in accepted
        )
        multiplicity = 'MULTIPLE_LICENSED' if len(licensed) > 1 else 'SINGLE'
        return DerivativeResult(
            result_id='RES-' + _cid(),
            request=request,
            verdict='DERIVATIVE_ACCEPTED',
            multiplicity=multiplicity,
            licensed_derivatives=licensed,
            deferred=None,
            blocked=None,
            residuals=(),
            all_candidates=tuple(candidates),
            trace=tuple(trace),
            source_engine=DERIVATIVES_ENGINE_ID,
        )
    elif deferred_c:
        dfr = DeferredDerivative(
            deferral_id='DFR-' + _cid(),
            reason=deferred_c[0].reason_codes[0] if deferred_c[0].reason_codes else 'DERIVATIVE_DEFERRED',
            candidates=tuple(deferred_c),
            missing_evidence=deferred_c[0].required_evidence,
            trace=tuple(trace),
        )
        return DerivativeResult(
            result_id='RES-' + _cid(),
            request=request,
            verdict='DERIVATIVE_DEFERRED',
            multiplicity='NONE',
            licensed_derivatives=(),
            deferred=dfr,
            blocked=None,
            residuals=(),
            all_candidates=tuple(candidates),
            trace=tuple(trace),
            source_engine=DERIVATIVES_ENGINE_ID,
        )
    else:
        return _deferred_result(request, 'NO_CANDIDATES_BUILT', (), (), trace)


# ── shared evidence builders ──────────────────────────────────────────────────

def _base_evidence(request, ff):
    root_key = tuple(request.licensed_root) if request.licensed_root else ()
    root_ev    = _ev('EV-ROOT-01', 'ROOT_LICENSE_EVIDENCE', 'SUFFICIENT', 'upstream', str(root_key))
    pattern_ev = _ev('EV-PAT-01',  'VERB_PATTERN_EVIDENCE', 'SUFFICIENT', 'upstream', request.licensed_pattern)
    ff_ev      = _ev('EV-FF-01',   'FORM_FAMILY_EVIDENCE',  'SUFFICIENT', 'upstream', ff)
    return root_ev, pattern_ev, ff_ev


# ── ISM_FA3IL generation ──────────────────────────────────────────────────────

def _generate_ism_fa3il(request, form_family, trace, step_ref) -> DerivativeResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    # RULE-D-01: FA3IL_PARTICIPLE treated as FORM_I
    effective_ff = 'FORM_I' if form_family == 'FA3IL_PARTICIPLE' else form_family

    T('ISM_FA3IL', 'LOOKUP_RULE', effective_ff)
    registry = get_rule_registry()
    rules = registry.rules_for_derivative_type_and_form_family('ISM_FA3IL', effective_ff)
    rules = [r for r in rules if r.get('status') == 'ACTIVE']

    if not rules:
        T('ISM_FA3IL', 'DEFER', f'NO_ACTIVE_RULES_FOR_{effective_ff}')
        return _deferred_result(request, f'NO_ACTIVE_RULES_FOR_{effective_ff}', (), (), trace)

    root_ev, pattern_ev, ff_ev = _base_evidence(request, effective_ff)
    candidates = []
    for idx, rule in enumerate(rules):
        for deriv_pattern in rule.get('masdar_patterns', []):
            T('ISM_FA3IL', 'APPLY_RULE', f'{rule["rule_id"]} -> {deriv_pattern}')
            cand = _candidate_from_rule(rule, request, root_ev, pattern_ev, ff_ev,
                                        deriv_pattern, idx)
            candidates.append(cand)

    T('ISM_FA3IL', 'FINALIZE', f'{len(candidates)} candidates')
    return _finalize(request, candidates, trace)


# ── ISM_MAF3UL generation ─────────────────────────────────────────────────────

def _generate_ism_maf3ul(request, form_family, trace, step_ref) -> DerivativeResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('ISM_MAF3UL', 'LOOKUP_RULE', form_family)
    registry = get_rule_registry()
    rules = registry.rules_for_derivative_type_and_form_family('ISM_MAF3UL', form_family)
    rules = [r for r in rules if r.get('status') == 'ACTIVE']

    if not rules:
        T('ISM_MAF3UL', 'DEFER', f'NO_ACTIVE_RULES_FOR_{form_family}')
        return _deferred_result(request, f'NO_ACTIVE_RULES_FOR_{form_family}', (), (), trace)

    root_ev, pattern_ev, ff_ev = _base_evidence(request, form_family)
    candidates = []
    for idx, rule in enumerate(rules):
        for deriv_pattern in rule.get('masdar_patterns', []):
            T('ISM_MAF3UL', 'APPLY_RULE', f'{rule["rule_id"]} -> {deriv_pattern}')
            cand = _candidate_from_rule(rule, request, root_ev, pattern_ev, ff_ev,
                                        deriv_pattern, idx)
            candidates.append(cand)

    T('ISM_MAF3UL', 'FINALIZE', f'{len(candidates)} candidates')
    return _finalize(request, candidates, trace)


# ── SIFA_MUSHABBAHA generation ────────────────────────────────────────────────

def _generate_sifa(request, form_family, trace, step_ref) -> DerivativeResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('SIFA', 'CHECK_LEXICAL_EVIDENCE', str(request.licensed_root))
    registry = get_rule_registry()
    root_key = tuple(request.licensed_root) if request.licensed_root else ()
    lex = registry.lexical_entries_for_root_ff_and_dtype(root_key, form_family or 'FORM_I', 'SIFA_MUSHABBAHA')

    if not lex:
        T('SIFA', 'DEFER', 'SIFA_VERBAL_EVIDENCE_REQUIRED')
        return _deferred_result(
            request, 'SIFA_VERBAL_EVIDENCE_REQUIRED',
            candidates=(), missing=('LEXICAL_DERIVATIVE_ATTESTATION',), trace=trace
        )

    root_ev, pattern_ev, ff_ev = _base_evidence(request, form_family or 'FORM_I')
    candidates = []
    for idx, entry in enumerate(lex):
        cand = _candidate_from_lexicon(entry, request, root_ev, pattern_ev, ff_ev, idx, 'SIFA_MUSHABBAHA')
        candidates.append(cand)

    return _finalize(request, candidates, trace)


# ── MUBALGHA generation ───────────────────────────────────────────────────────

def _generate_mubalgha(request, form_family, trace, step_ref) -> DerivativeResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('MUBALGHA', 'CHECK_LEXICAL_EVIDENCE', str(request.licensed_root))
    registry = get_rule_registry()
    root_key = tuple(request.licensed_root) if request.licensed_root else ()
    lex = registry.lexical_entries_for_root_ff_and_dtype(root_key, form_family or 'FORM_I', 'MUBALGHA')

    if not lex:
        T('MUBALGHA', 'DEFER', 'MUBALGHA_LEXICAL_EVIDENCE_REQUIRED')
        return _deferred_result(
            request, 'MUBALGHA_LEXICAL_EVIDENCE_REQUIRED',
            candidates=(), missing=('LEXICAL_DERIVATIVE_ATTESTATION',), trace=trace
        )

    root_ev, pattern_ev, ff_ev = _base_evidence(request, form_family or 'FORM_I')
    candidates = []
    for idx, entry in enumerate(lex):
        cand = _candidate_from_lexicon(entry, request, root_ev, pattern_ev, ff_ev, idx, 'MUBALGHA')
        candidates.append(cand)

    return _finalize(request, candidates, trace)


# ── ISM_ZAMAN generation ──────────────────────────────────────────────────────

def _generate_ism_zaman(request, form_family, trace, step_ref) -> DerivativeResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('ISM_ZAMAN', 'CHECK_LEXICAL_EVIDENCE', str(request.licensed_root))
    registry = get_rule_registry()
    root_key = tuple(request.licensed_root) if request.licensed_root else ()
    lex = registry.lexical_entries_for_root_ff_and_dtype(root_key, form_family or 'FORM_I', 'ISM_ZAMAN')

    if not lex:
        # RULE-D-02: ambiguity with ISM_MAKAN and masdar mimi — defer
        T('ISM_ZAMAN', 'DEFER', 'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY')
        return _deferred_result(
            request, 'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY',
            candidates=(), missing=('LEXICAL_DERIVATIVE_ATTESTATION', 'DISAMBIGUATION_EVIDENCE'), trace=trace
        )

    # lexical discriminator present — check it
    root_ev, pattern_ev, ff_ev = _base_evidence(request, form_family or 'FORM_I')
    candidates = []
    for idx, entry in enumerate(lex):
        discr = entry.get('lexical_discriminator')
        if discr and discr != 'ISM_ZAMAN':
            T('ISM_ZAMAN', 'SKIP_ENTRY', f'discriminator={discr}')
            continue
        cand = _candidate_from_lexicon(entry, request, root_ev, pattern_ev, ff_ev, idx, 'ISM_ZAMAN')
        candidates.append(cand)

    if not candidates:
        T('ISM_ZAMAN', 'DEFER', 'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY')
        return _deferred_result(
            request, 'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY',
            candidates=(), missing=('DISAMBIGUATION_EVIDENCE',), trace=trace
        )

    return _finalize(request, candidates, trace)


# ── ISM_MAKAN generation ──────────────────────────────────────────────────────

def _generate_ism_makan(request, form_family, trace, step_ref) -> DerivativeResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('ISM_MAKAN', 'CHECK_LEXICAL_EVIDENCE', str(request.licensed_root))
    registry = get_rule_registry()
    root_key = tuple(request.licensed_root) if request.licensed_root else ()
    lex = registry.lexical_entries_for_root_ff_and_dtype(root_key, form_family or 'FORM_I', 'ISM_MAKAN')

    if not lex:
        T('ISM_MAKAN', 'DEFER', 'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY')
        return _deferred_result(
            request, 'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY',
            candidates=(), missing=('LEXICAL_DERIVATIVE_ATTESTATION', 'DISAMBIGUATION_EVIDENCE'), trace=trace
        )

    root_ev, pattern_ev, ff_ev = _base_evidence(request, form_family or 'FORM_I')
    candidates = []
    for idx, entry in enumerate(lex):
        discr = entry.get('lexical_discriminator')
        if discr and discr != 'ISM_MAKAN':
            T('ISM_MAKAN', 'SKIP_ENTRY', f'discriminator={discr}')
            continue
        cand = _candidate_from_lexicon(entry, request, root_ev, pattern_ev, ff_ev, idx, 'ISM_MAKAN')
        candidates.append(cand)

    if not candidates:
        T('ISM_MAKAN', 'DEFER', 'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY')
        return _deferred_result(
            request, 'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY',
            candidates=(), missing=('DISAMBIGUATION_EVIDENCE',), trace=trace
        )

    return _finalize(request, candidates, trace)


# ── ISM_ALA generation ────────────────────────────────────────────────────────

def _generate_ism_ala(request, form_family, trace, step_ref) -> DerivativeResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('ISM_ALA', 'CHECK_LEXICAL_EVIDENCE', str(request.licensed_root))
    registry = get_rule_registry()
    root_key = tuple(request.licensed_root) if request.licensed_root else ()
    lex = registry.lexical_entries_for_root_ff_and_dtype(root_key, form_family or 'FORM_I', 'ISM_ALA')

    if not lex:
        T('ISM_ALA', 'RESIDUAL', 'ISM_ALA_LEXICON_GAP')
        return _residual_result(request, 'ISM_ALA_LEXICON_GAP', 'ISM_ALA_LEXICON_GAP', trace)

    root_ev, pattern_ev, ff_ev = _base_evidence(request, form_family or 'FORM_I')
    candidates = []
    for idx, entry in enumerate(lex):
        cand = _candidate_from_lexicon(entry, request, root_ev, pattern_ev, ff_ev, idx, 'ISM_ALA')
        candidates.append(cand)

    return _finalize(request, candidates, trace)


# ── auto mode: generate ISM_FA3IL + ISM_MAF3UL and merge ─────────────────────

def _generate_auto(request, form_family, trace, step_ref) -> DerivativeResult:
    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('AUTO', 'GENERATE_ISM_FA3IL', form_family)
    fa3il_result  = _generate_ism_fa3il(request, form_family, trace, step_ref)

    T('AUTO', 'GENERATE_ISM_MAF3UL', form_family)
    # FA3IL_PARTICIPLE has no MAF3UL — use FORM_I for MAF3UL lookup
    maf3ul_ff = 'FORM_I' if form_family == 'FA3IL_PARTICIPLE' else form_family
    maf3ul_result = _generate_ism_maf3ul(request, maf3ul_ff, trace, step_ref)

    all_licensed = (
        list(fa3il_result.licensed_derivatives) +
        list(maf3ul_result.licensed_derivatives)
    )
    all_candidates = (
        list(fa3il_result.all_candidates) +
        list(maf3ul_result.all_candidates)
    )

    if not all_licensed:
        # both deferred
        T('AUTO', 'DEFER', 'NO_AUTO_DERIVATIVES_LICENSED')
        return _deferred_result(request, 'NO_AUTO_DERIVATIVES_LICENSED', all_candidates, (), trace)

    multiplicity = 'MULTIPLE_LICENSED' if len(all_licensed) > 1 else 'SINGLE'
    return DerivativeResult(
        result_id='RES-' + _cid(),
        request=request,
        verdict='DERIVATIVE_ACCEPTED',
        multiplicity=multiplicity,
        licensed_derivatives=tuple(all_licensed),
        deferred=None,
        blocked=None,
        residuals=(),
        all_candidates=tuple(all_candidates),
        trace=tuple(trace),
        source_engine=DERIVATIVES_ENGINE_ID,
    )


# ══════════════════════════════════════════════════════════════════════════════
# CANONICAL_DERIVATIVES_ENTRYPOINT
# ══════════════════════════════════════════════════════════════════════════════

def analyze_derivative(request: DerivativeRequest) -> DerivativeResult:
    """
    CANONICAL_DERIVATIVES_ENTRYPOINT — HOKOM_DERIVATIVES_ENGINE

    Accepts a DerivativeRequest and returns a DerivativeResult.
    Does NOT re-extract root or wazn. Consumes upstream contracts only.
    """
    trace    = []
    step_ref = [0]

    def T(stage, action, detail=None):
        step_ref[0] += 1
        trace.append(_te(step_ref[0], stage, action, detail))

    T('GATE', 'DERIVATIVES_GATE_OPEN', f'mode={request.mode} ff={request.verb_form_family!r}')

    # ── 1. Upstream license gate ──────────────────────────────────────────────
    if request.licensed_root is None:
        T('GATE', 'BLOCK', 'ROOT_NOT_LICENSED')
        return _blocked_result(request, 'DERIVATIVE_NOT_OPENED:ROOT_NOT_LICENSED', [
            _co('C-R', 'UPSTREAM_BLOCKED', 'licensed_root', 'None')
        ], trace)

    if request.licensed_pattern is None:
        T('GATE', 'BLOCK', 'PATTERN_NOT_LICENSED')
        return _blocked_result(request, 'DERIVATIVE_NOT_OPENED:PATTERN_NOT_LICENSED', [
            _co('C-P', 'UPSTREAM_BLOCKED', 'licensed_pattern', 'None')
        ], trace)

    if request.verbal_host is None and request.verbal_lemma is None:
        T('GATE', 'DEFER', 'VERBHOOD_NOT_LICENSED')
        return _deferred_result(
            request, 'DERIVATIVE_NOT_OPENED:VERBHOOD_NOT_LICENSED',
            (), ('VERBAL_HOST_EVIDENCE',), trace
        )

    form_family = request.verb_form_family or 'FORM_I'
    T('GATE', 'PASS', f'root={request.licensed_root} ff={form_family!r}')

    # ── 2. Route by derivative_type ───────────────────────────────────────────
    dtype = request.derivative_type or 'auto'

    if dtype == 'ISM_FA3IL':
        return _generate_ism_fa3il(request, form_family, trace, step_ref)

    if dtype == 'ISM_MAF3UL':
        # FA3IL_PARTICIPLE: treat as FORM_I for MAF3UL
        maf3ul_ff = 'FORM_I' if form_family == 'FA3IL_PARTICIPLE' else form_family
        return _generate_ism_maf3ul(request, maf3ul_ff, trace, step_ref)

    if dtype == 'SIFA_MUSHABBAHA':
        return _generate_sifa(request, form_family, trace, step_ref)

    if dtype == 'MUBALGHA':
        return _generate_mubalgha(request, form_family, trace, step_ref)

    if dtype == 'ISM_ZAMAN':
        return _generate_ism_zaman(request, form_family, trace, step_ref)

    if dtype == 'ISM_MAKAN':
        return _generate_ism_makan(request, form_family, trace, step_ref)

    if dtype == 'ISM_ALA':
        return _generate_ism_ala(request, form_family, trace, step_ref)

    if dtype == 'auto':
        return _generate_auto(request, form_family, trace, step_ref)

    # Unknown derivative_type (should not reach here due to model validation)
    T('GATE', 'DEFER', f'UNKNOWN_DERIVATIVE_TYPE:{dtype}')
    return _deferred_result(request, f'UNKNOWN_DERIVATIVE_TYPE:{dtype}', (), (), trace)
