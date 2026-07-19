#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/word_class/engine.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Canonical ISM / FI3L / HARF word class engine.

WORD_CLASS_CANONICAL_ENTRYPOINT = 'classify_word_class'
HOKOM-WORD-CLASS-OWNERSHIP-01

Classification priority order:
  1.  HARF — operator catalog: Closed Function Word
  2.  FI3L — verbal operators (كان، كاد، ظن)
  3.  ISM  — accepted masdar (phase4c ACCEPT)
  4.  ISM  — accepted derivative on nominal path
  5.  ISM  — attachment MABNI_BOUNDARY (pronouns/demonstratives: هُوَ, هَذَا — B-04)
  6.  FI3L — licensed verbal host (phase4b bab/form accepted)
  7.  FI3L — verbal_root_path alone (يَكْتُبُ, كَتَبَتْ)
  8.  FI3L — ambiguous path + phase4a wazn accepted (كَتَبَ)
  9.  ISM  — nominal_morphology_path
  10. DEFER — insufficient / ambiguous evidence

ABSOLUTE CONSTRAINTS:
  - operator_status alone → never HARF
  - mabni_status alone    → never HARF
  - pattern alone         → never FI3L
  - No Taaqol runtime
"""
from __future__ import annotations

from .models import (
    WORD_CLASS_ENGINE_ID,
    WordClass,
    WordClassVerdict,
    LexicalSubclass,
    EvidenceType,
    WordClassEvidence,
    WordClassCandidate,
    WordClassRequest,
    WordClassResult,
    WordClassTraceEvent,
)
from .catalog import (
    extract_mabni_id_from_notes,
    get_ism_subclass_from_mabni_id,
    is_ism_mabni_class,
    build_attachment_evidence,
    _HARF_OPERATOR_CLASSES,
    _VERBAL_OPERATOR_CLASSES,
    _DERIVATIVE_TYPE_TO_SUBCLASS,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _ev(ev_type: EvidenceType, source: str, value: str,
        confidence: str = 'HIGH') -> WordClassEvidence:
    return WordClassEvidence(
        evidence_type=ev_type,
        source=source,
        value=value,
        confidence=confidence,
    )


def _trace(step: str, decision: str, *ev_strs: str) -> WordClassTraceEvent:
    return WordClassTraceEvent(step=step, decision=decision,
                               evidence=tuple(ev_strs))


def _accepted(surface, request_id, word_class, subclass, evidence, trace,
              contradictions=(), reason_code='', residuals=()):
    candidate = WordClassCandidate(
        word_class=word_class, subclass=subclass, rank=1,
        evidence=evidence, contradictions=contradictions,
    )
    return WordClassResult(
        request_id=request_id, surface=surface,
        verdict=WordClassVerdict.ACCEPTED,
        word_class=word_class, subclass=subclass,
        candidates=(candidate,), primary_evidence=evidence,
        contradictions=contradictions, reason_code=reason_code,
        residuals=residuals, trace=trace, engine_id=WORD_CLASS_ENGINE_ID,
    )


def _deferred(surface, request_id, reason_code, evidence=(), trace=(),
              contradictions=(), residuals=()):
    return WordClassResult(
        request_id=request_id, surface=surface,
        verdict=WordClassVerdict.DEFERRED,
        word_class=None, subclass=None,
        candidates=(), primary_evidence=evidence,
        contradictions=contradictions, reason_code=reason_code,
        residuals=residuals, trace=trace, engine_id=WORD_CLASS_ENGINE_ID,
    )


def _blocked(surface, request_id, reason_code, evidence=(), trace=()):
    return WordClassResult(
        request_id=request_id, surface=surface,
        verdict=WordClassVerdict.BLOCKED,
        word_class=None, subclass=None,
        candidates=(), primary_evidence=evidence,
        contradictions=(), reason_code=reason_code,
        residuals=(), trace=trace, engine_id=WORD_CLASS_ENGINE_ID,
    )


# ══════════════════════════════════════════════════════════════════════════════
# CANONICAL ENTRYPOINT
# ══════════════════════════════════════════════════════════════════════════════

def classify_word_class(request: WordClassRequest) -> WordClassResult:
    """
    WORD_CLASS_CANONICAL_ENTRYPOINT

    Classify an Arabic surface form as ISM / FI3L / HARF.

    Returns WordClassResult with verdict ∈ {ACCEPTED, DEFERRED, BLOCKED}.
    """
    surface    = request.original_surface
    rid        = request.request_id
    ev: list   = []
    tr: list   = []

    # ── GATE: upstream BLOCK ──────────────────────────────────────────────────
    if request.p5_verdict == 'BLOCK' or request.mabni_status == 'blocked':
        tr.append(_trace('upstream_block', 'BLOCKED:upstream_block',
                         f'p5_verdict={request.p5_verdict}'))
        return _blocked(surface, rid, 'UPSTREAM_BLOCK', trace=tuple(tr))

    # ── p4a accepted? (encoded in available_evidence by request builder) ──────
    _p4a_ok = any(s.startswith('p4a:accept') for s in request.available_evidence)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 1 — HARF: Closed Function Word from operator catalog
    # ══════════════════════════════════════════════════════════════════════════
    # Covers prepositions, conjunctions, negative/interrogative particles, etc.
    # CONSTRAINT: lexical_class must be explicit — operator_status alone is not
    #             sufficient (NEVER equate operator=HARF).
    if (request.p5_verdict in ('OPERATOR_BOUNDARY', 'MABNI_BOUNDARY',
                               'OPERATOR_DEFERRED', 'MABNI_DEFERRED')
            and request.p5_lexical_class in _HARF_OPERATOR_CLASSES):
        harf_ev = _ev(EvidenceType.LEXICAL_HARF_ENTRY,
                      'pipeline.p5_lexical.mabni_projection',
                      request.p5_lexical_class)
        ev.append(harf_ev)
        subclass = (LexicalSubclass.NUMERICAL_OPERATOR
                    if request.p5_lexical_class == 'Numerical Operator'
                    else LexicalSubclass.CLOSED_FUNCTION_WORD)
        tr.append(_trace('operator_catalog_harf', f'HARF:{subclass.value}',
                         f'p5_lexical_class={request.p5_lexical_class}',
                         f'p5_verdict={request.p5_verdict}'))
        return _accepted(surface, rid, WordClass.HARF, subclass,
                         evidence=tuple(ev), trace=tuple(tr),
                         reason_code='LEXICAL_HARF_ENTRY')

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 2 — FI3L: Verbal Operators (كان، كاد، ظن)
    # ══════════════════════════════════════════════════════════════════════════
    # Verbal operators ARE morphologically verbs.
    if (request.p5_verdict in ('OPERATOR_BOUNDARY', 'MABNI_BOUNDARY',
                               'OPERATOR_DEFERRED', 'MABNI_DEFERRED')
            and request.p5_lexical_class in _VERBAL_OPERATOR_CLASSES):
        v_ev = _ev(EvidenceType.LEXICAL_VERBAL_OPERATOR,
                   'pipeline.p5_lexical.mabni_projection',
                   request.p5_lexical_class)
        ev.append(v_ev)
        tr.append(_trace('operator_catalog_verbal', 'FI3L:VERBAL_OPERATOR',
                         f'p5_lexical_class={request.p5_lexical_class}'))
        return _accepted(surface, rid, WordClass.FI3L,
                         LexicalSubclass.VERBAL_OPERATOR,
                         evidence=tuple(ev), trace=tuple(tr),
                         reason_code='LEXICAL_VERBAL_OPERATOR')

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 3 — ISM: accepted masdar (phase4c ACCEPT)
    # ══════════════════════════════════════════════════════════════════════════
    if request.masdar_accepted:
        m_ev = _ev(EvidenceType.ACCEPTED_MASDAR, 'pipeline.p4_masdar',
                   request.masdar_surface or 'MASDAR_ACCEPTED')
        ev.append(m_ev)
        tr.append(_trace('masdar_accepted', 'ISM:MASDAR',
                         f'masdar_surface={request.masdar_surface}'))
        return _accepted(surface, rid, WordClass.ISM, LexicalSubclass.MASDAR,
                         evidence=tuple(ev), trace=tuple(tr),
                         reason_code='ACCEPTED_MASDAR')

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 4 — ISM: accepted derivative (ONLY on nominal morphology path)
    # ══════════════════════════════════════════════════════════════════════════
    # Phase4D accepted_mushtaqat on a verbal surface (كَتَبَ) represents
    # root-level theoretical derivatives, NOT that the current token IS one.
    # We only accept derivative evidence when morphology is explicitly nominal.
    if (request.derivative_accepted and request.derivative_type
            and request.morphology_path in (
                'nominal_morphology_path', 'derived_nominal_path')):
        ds = _DERIVATIVE_TYPE_TO_SUBCLASS.get(
            request.derivative_type, LexicalSubclass.LEXICAL_NOUN)
        d_ev = _ev(EvidenceType.ACCEPTED_DERIVATIVE, 'pipeline.p4_mushtaqat',
                   request.derivative_type)
        ev.append(d_ev)
        tr.append(_trace('derivative_accepted_nominal', f'ISM:{ds.value}',
                         f'derivative_type={request.derivative_type}',
                         f'morphology_path={request.morphology_path}'))
        return _accepted(surface, rid, WordClass.ISM, ds,
                         evidence=tuple(ev), trace=tuple(tr),
                         reason_code='ACCEPTED_DERIVATIVE')

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 5 — ISM: mabniyat attachment MABNI_BOUNDARY
    # B-04 fix: pronouns (هُوَ) and demonstratives (هَذَا)
    # ══════════════════════════════════════════════════════════════════════════
    if request.attachment_route == 'MABNI_BOUNDARY':
        mabni_id = (request.attachment_mabni_id
                    or extract_mabni_id_from_notes(request.attachment_notes))
        if mabni_id and is_ism_mabni_class(mabni_id):
            sub = get_ism_subclass_from_mabni_id(mabni_id) or LexicalSubclass.LEXICAL_NOUN
            att_ev = build_attachment_evidence(mabni_id)
            if att_ev:
                ev.append(att_ev)
            ev.append(_ev(EvidenceType.ATTACHMENT_MABNI, 'mabniyat_attachment',
                          f'{mabni_id}:{request.attachment_route}'))
            tr.append(_trace('attachment_mabni_boundary', f'ISM:{sub.value}',
                             f'mabni_id={mabni_id}',
                             f'attachment_route={request.attachment_route}'))
            return _accepted(surface, rid, WordClass.ISM, sub,
                             evidence=tuple(ev), trace=tuple(tr),
                             reason_code='MABNI_BOUNDARY_ISM')

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 6 — FI3L: licensed verbal host (phase4b bab or augmented form)
    # ══════════════════════════════════════════════════════════════════════════
    _verbal_compat = request.morphology_path in (
        'verbal_root_path', 'ambiguous_morphology_path')
    if request.licensed_verbal_host and _verbal_compat:
        lv_ev = _ev(EvidenceType.LICENSED_VERBAL_HOST, 'pipeline.p4_bab',
                    request.bab_id or request.form_family or 'BAB_ACCEPTED')
        ev.append(lv_ev)
        mp_ev = _ev(EvidenceType.MORPHOLOGY_PATH_VERBAL, 'pipeline.pre_root',
                    request.morphology_path,
                    'HIGH' if request.morphology_path == 'verbal_root_path' else 'MEDIUM')
        ev.append(mp_ev)
        sub = LexicalSubclass.VERBAL_PAST
        if request.bab_id and 'IMPERFECT' in request.bab_id.upper():
            sub = LexicalSubclass.VERBAL_IMPERFECT
        tr.append(_trace('licensed_verbal_host', f'FI3L:{sub.value}',
                         f'bab_id={request.bab_id}',
                         f'form_family={request.form_family}'))
        return _accepted(surface, rid, WordClass.FI3L, sub,
                         evidence=tuple(ev), trace=tuple(tr),
                         reason_code='LICENSED_VERBAL_HOST')

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 7 — FI3L: verbal_root_path alone
    # ══════════════════════════════════════════════════════════════════════════
    # The pre_root classifier sets verbal_root_path when it sees unambiguous
    # verbal morphological features (imperfect prefix يَ/تَ/نَ/أَ + consonant,
    # or past-tense feminine suffix تْ).  No bab confirmation needed.
    # Examples: يَكْتُبُ, كَتَبَتْ
    if request.morphology_path == 'verbal_root_path':
        vr_ev = _ev(EvidenceType.MORPHOLOGY_PATH_VERBAL, 'pipeline.pre_root',
                    'verbal_root_path')
        ev.append(vr_ev)
        tr.append(_trace('verbal_root_path', 'FI3L:VERBAL_PAST',
                         'morphology_path=verbal_root_path'))
        return _accepted(surface, rid, WordClass.FI3L, LexicalSubclass.VERBAL_PAST,
                         evidence=tuple(ev), trace=tuple(tr),
                         reason_code='VERBAL_ROOT_PATH')

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 8 — FI3L: ambiguous_morphology_path + phase4a wazn accepted
    # ══════════════════════════════════════════════════════════════════════════
    # Past-tense forms of bare trilateral verbs (كَتَبَ, ذَهَبَ) have
    # morphology_path=ambiguous (no clear affix). When phase4a accepts a
    # verb-class wazn (FA_A_LA, FA_I_LA, FA_U_LA …), that is FI3L evidence.
    if request.morphology_path == 'ambiguous_morphology_path' and _p4a_ok:
        p4a_ev = _ev(
            EvidenceType.ROOT_PATTERN_VERBAL, 'pipeline.p4_wazn',
            next((s for s in request.available_evidence
                  if s.startswith('p4a:accept')), 'p4a:accept'),
            'MEDIUM')
        ev.append(p4a_ev)
        mp_ev = _ev(EvidenceType.MORPHOLOGY_PATH_VERBAL, 'pipeline.pre_root',
                    'ambiguous:p4a_accepted', 'MEDIUM')
        ev.append(mp_ev)
        tr.append(_trace('ambiguous_p4a_accept', 'FI3L:VERBAL_PAST',
                         'morphology_path=ambiguous_morphology_path',
                         f'p4a_accepted=True'))
        return _accepted(surface, rid, WordClass.FI3L, LexicalSubclass.VERBAL_PAST,
                         evidence=tuple(ev), trace=tuple(tr),
                         reason_code='AMBIGUOUS_PATH_P4A_WAZN')

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 9 — ISM: nominal morphology path
    # ══════════════════════════════════════════════════════════════════════════
    if request.morphology_path in (
            'nominal_morphology_path', 'derived_nominal_path', 'functional_path'):
        n_ev = _ev(EvidenceType.MORPHOLOGY_PATH_NOMINAL, 'pipeline.pre_root',
                   request.morphology_path, 'MEDIUM')
        ev.append(n_ev)
        sub = (LexicalSubclass.CLOSED_FUNCTION_WORD
               if request.morphology_path == 'functional_path'
               else LexicalSubclass.LEXICAL_NOUN)
        tr.append(_trace('nominal_morphology_path', f'ISM:{sub.value}',
                         f'morphology_path={request.morphology_path}'))
        return _accepted(surface, rid, WordClass.ISM, sub,
                         evidence=tuple(ev), trace=tuple(tr),
                         reason_code='NOMINAL_MORPHOLOGY_PATH')

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 10 — DEFER: insufficient / ambiguous evidence
    # ══════════════════════════════════════════════════════════════════════════
    reason = 'INSUFFICIENT_EVIDENCE'
    mp = request.morphology_path
    if mp == 'ambiguous_morphology_path':
        reason = 'AMBIGUOUS_MORPHOLOGY_PATH'
    elif mp in ('no_morphology_path', ''):
        reason = 'NO_MORPHOLOGY_PATH'

    tr.append(_trace('defer', f'DEFERRED:{reason}',
                     f'morphology_path={mp}',
                     f'p5_verdict={request.p5_verdict}'))
    return _deferred(surface, rid, reason_code=reason,
                     evidence=tuple(ev), trace=tuple(tr),
                     residuals=(f'word_class:deferred:{reason}',))
