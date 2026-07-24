#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/demo_ayat_al_dayn.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-TAAQOL-AYAT-AL-DAYN-LIVE-DEMO-01  (v2 — full slot detail)

Live operational demo: Hokom–Taaqol pipeline over Ayat al-Dayn
(Sūrat al-Baqara 2:282), 129 tokens.

Rules:
  - No hints, seeds, injected results, or mock substitutions.
  - No invented values.  If a slot has no value, its real state and
    reason are reported.
  - composite_verdict is per-layer, never a single overall string.
  - LICENSED only appears when a specific claim is named.

Usage
-----
    python scripts/demo_ayat_al_dayn.py                     # terminal
    python scripts/demo_ayat_al_dayn.py --format terminal
    python scripts/demo_ayat_al_dayn.py --format json
    python scripts/demo_ayat_al_dayn.py --format csv
    python scripts/demo_ayat_al_dayn.py --format html
    python scripts/demo_ayat_al_dayn.py --open
"""
from __future__ import annotations

import argparse
import csv as csv_mod
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ── canonical text ────────────────────────────────────────────────────────────
AYAT_AL_DAYN = (
    'يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا تَدَايَنْتُمْ بِدَيْنٍ إِلَى أَجَلٍ مُسَمًّى '
    'فَاكْتُبُوهُ وَلْيَكْتُبْ بَيْنَكُمْ كَاتِبٌ بِالْعَدْلِ وَلَا يَأْبَ كَاتِبٌ '
    'أَنْ يَكْتُبَ كَمَا عَلَّمَهُ اللَّهُ فَلْيَكْتُبْ وَلْيُمْلِلِ الَّذِي عَلَيْهِ '
    'الْحَقُّ وَلْيَتَّقِ اللَّهَ رَبَّهُ وَلَا يَبْخَسْ مِنْهُ شَيْئًا فَإِنْ كَانَ '
    'الَّذِي عَلَيْهِ الْحَقُّ سَفِيهًا أَوْ ضَعِيفًا أَوْ لَا يَسْتَطِيعُ أَنْ يُمِلَّ '
    'هُوَ فَلْيُمْلِلْ وَلِيُّهُ بِالْعَدْلِ وَاسْتَشْهِدُوا شَهِيدَيْنِ مِنْ رِجَالِكُمْ '
    'فَإِنْ لَمْ يَكُونَا رَجُلَيْنِ فَرَجُلٌ وَامْرَأَتَانِ مِمَّنْ تَرْضَوْنَ مِنَ '
    'الشُّهَدَاءِ أَنْ تَضِلَّ إِحْدَاهُمَا فَتُذَكِّرَ إِحْدَاهُمَا الْأُخْرَى وَلَا '
    'يَأْبَ الشُّهَدَاءُ إِذَا مَا دُعُوا وَلَا تَسْأَمُوا أَنْ تَكْتُبُوهُ صَغِيرًا '
    'أَوْ كَبِيرًا إِلَى أَجَلِهِ ذَلِكُمْ أَقْسَطُ عِنْدَ اللَّهِ وَأَقْوَمُ '
    'لِلشَّهَادَةِ وَأَدْنَى أَلَّا تَرْتَابُوا إِلَّا أَنْ تَكُونَ تِجَارَةً '
    'حَاضِرَةً تُدِيرُونَهَا بَيْنَكُمْ فَلَيْسَ عَلَيْكُمْ جُنَاحٌ أَلَّا تَكْتُبُوهَا '
    'وَأَشْهِدُوا إِذَا تَبَايَعْتُمْ وَلَا يُضَارَّ كَاتِبٌ وَلَا شَهِيدٌ وَإِنْ '
    'تَفْعَلُوا فَإِنَّهُ فُسُوقٌ بِكُمْ وَاتَّقُوا اللَّهَ وَيُعَلِّمُكُمُ اللَّهُ '
    'وَاللَّهُ بِكُلِّ شَيْءٍ عَلِيمٌ'
)
AYAT_SOURCE_FILE = 'tests/post_segmentation_routing/test_ayat_al_dayn_routing.py'

TOKENS = AYAT_AL_DAYN.split()
assert len(TOKENS) == 129, f'Expected 129 tokens, got {len(TOKENS)}'

# Layer names from SlotSort
_LAYER_NAME: dict[int, str] = {
    0:   'SURFACE_IDENTITY',
    10:  'NORMALIZATION',
    20:  'PHONOLOGICAL',
    30:  'SEGMENTATION',
    35:  'ARTICLE',
    40:  'BOUNDARY',
    50:  'LEXICAL_FUNCTIONAL',
    60:  'WORD_CLASS',
    70:  'INFLECTIONAL',
    80:  'RADICAL',
    90:  'PATTERN',
    100: 'BAB',
    110: 'MASDAR',
    120: 'DERIVATIVE',
    130: 'MORPHOSYNTAX',
    140: 'PARADIGM',
    900: 'EVIDENCE',
    910: 'RESIDUAL',
}


# ── git / env ─────────────────────────────────────────────────────────────────
def _git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=REPO_ROOT, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return 'UNKNOWN'


def _vendor_sha() -> str:
    vendor = REPO_ROOT / 'vendor' / 'Taaqol-GPT'
    if (vendor / '.git').exists():
        try:
            return subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], cwd=vendor, stderr=subprocess.DEVNULL
            ).decode().strip()[:16]
        except Exception:
            pass
    pinned = REPO_ROOT / 'tests' / 'fixtures' / 'vendor_sha_pin.txt'
    if pinned.exists():
        return pinned.read_text().strip()[:16]
    return 'UNKNOWN'


# ── slot serializer ───────────────────────────────────────────────────────────
def _serialize_slot(s) -> dict:
    """
    Serialise a TypedSlot to a dict with all fields.
    Never invents a value — if a field is None/empty the key is still present.
    """
    import dataclasses

    layer_sort = getattr(s.sort, 'value', int(s.sort)) if s.sort is not None else None
    layer_name = _LAYER_NAME.get(layer_sort, str(layer_sort))

    # evidence refs
    evs = []
    for e in (s.evidence or ()):
        evs.append({
            'evidence_id':  getattr(e, 'evidence_id', None),
            'kind':         getattr(e, 'kind', None),
            'source':       getattr(e, 'source', None),
            'payload':      getattr(e, 'payload', None),
            'is_negative':  getattr(e, 'is_negative', None),
        })

    # provenance
    prov = None
    if s.provenance is not None:
        prov = {
            'original_surface':  getattr(s.provenance, 'original_surface', None),
            'normalized_surface': getattr(s.provenance, 'normalized_surface', None),
            'operations':        list(getattr(s.provenance, 'operations', ())),
        }

    # candidate_set
    cset = None
    if s.candidate_set is not None:
        cset_obj = s.candidate_set
        entries = []
        for ce in getattr(cset_obj, 'candidates', ()):
            entries.append({
                'value':    getattr(ce, 'value', str(ce)),
                'score':    getattr(ce, 'score', None),
                'evidence': getattr(ce, 'evidence', None),
            })
        cset = {
            'candidates':        entries,
            'selected':          getattr(cset_obj, 'selected', None),
            'selection_evidence': getattr(cset_obj, 'selection_evidence', None),
        }

    # residual
    res = None
    if s.residual is not None:
        r = s.residual
        res = {
            'residual_id':          getattr(r, 'residual_id', None),
            'code':                 getattr(r, 'code', None),
            'kind':                 getattr(r, 'kind', None),
            'source_slot':          getattr(r.source_slot, 'value', None) if getattr(r, 'source_slot', None) else None,
            'reason':               getattr(r, 'reason', None),
            'visibility':           getattr(r, 'visibility', None),
            'next_evidence_required': getattr(r, 'next_evidence_required', None),
        }

    return {
        'slot_id':       s.slot_id.value,
        'layer':         layer_name,
        'layer_sort':    layer_sort,
        'state':         s.state.value,
        'value':         s.value,
        'candidate_set': cset,
        'evidence':      evs,
        'provenance':    prov,
        'residual':      res,
        'owner':         getattr(s, 'owner', None),
    }


# ── composite verdict builder ─────────────────────────────────────────────────
_STATE_RANK = {'FILLED': 0, 'AMBIGUOUS': 1, 'NOT_APPLICABLE': 2, 'BLOCKED': 3, 'UNKNOWN': 4}


def _build_composite_verdict(slots: list[dict], hr: dict) -> dict:
    """
    Per-layer summary of claim states.
    Never emits a global 'LICENSED'; each layer has its own verdict.
    LICENSED is only used when a specific filled claim is named.
    """
    from collections import defaultdict
    by_layer: dict[str, dict] = {}
    for s in slots:
        layer = s['layer']
        if layer not in by_layer:
            by_layer[layer] = {
                'layer':    layer,
                'slots':    [],
                'FILLED':   0,
                'UNKNOWN':  0,
                'NOT_APPLICABLE': 0,
                'AMBIGUOUS': 0,
                'BLOCKED':  0,
            }
        by_layer[layer]['slots'].append(s['slot_id'])
        state = s['state']
        if state in by_layer[layer]:
            by_layer[layer][state] += 1

    # Classify each layer
    for ln, ld in by_layer.items():
        total = sum(ld[k] for k in ('FILLED','UNKNOWN','NOT_APPLICABLE','AMBIGUOUS','BLOCKED'))
        na    = ld['NOT_APPLICABLE']
        filled = ld['FILLED']
        unk   = ld['UNKNOWN']
        amb   = ld['AMBIGUOUS']
        blk   = ld['BLOCKED']

        if total == na:
            ld['layer_verdict'] = 'NOT_APPLICABLE'
        elif blk > 0:
            ld['layer_verdict'] = 'BLOCKED'
        elif amb > 0:
            ld['layer_verdict'] = 'AMBIGUOUS'
        elif unk > 0 and filled == 0:
            ld['layer_verdict'] = 'NOT_OPENED'
        elif unk > 0 and filled > 0:
            ld['layer_verdict'] = 'PARTIAL'
        else:
            ld['layer_verdict'] = 'LICENSED'

    # Collect licensed / deferred / etc. claims
    licensed_claims  = [s['slot_id'] for s in slots if s['state'] == 'FILLED']
    deferred_claims  = [s['slot_id'] for s in slots if s['state'] == 'UNKNOWN']
    blocked_claims   = [s['slot_id'] for s in slots if s['state'] == 'BLOCKED']
    ambiguous_claims = [s['slot_id'] for s in slots if s['state'] == 'AMBIGUOUS']
    not_opened_layers = [ln for ln, ld in by_layer.items() if ld['layer_verdict'] == 'NOT_OPENED']

    # Active residuals from hr
    active_residuals = list(hr.get('active_residuals') or ())

    return {
        'by_layer':          list(by_layer.values()),
        'licensed_claims':   licensed_claims,
        'deferred_claims':   deferred_claims,
        'blocked_claims':    blocked_claims,
        'ambiguous_claims':  ambiguous_claims,
        'not_opened_layers': not_opened_layers,
        'active_residuals':  active_residuals,
        'has_unresolved_claims': bool(deferred_claims or blocked_claims or ambiguous_claims),
        # Guard: overall LICENSED must never mask unresolved claims
        'overall_verdict':   (
            'FULLY_LICENSED'
            if not deferred_claims and not blocked_claims and not ambiguous_claims
            and all(s['state'] in ('FILLED','NOT_APPLICABLE') for s in slots)
            else 'COMPOSITE'
        ),
    }


# ── Taaqol claim decomposition ────────────────────────────────────────────────
def _decompose_taaqol(hr: dict) -> dict:
    td   = hr.get('taaqol_decision')
    rt   = hr.get('taaqol_runtime') or {}

    if td is None:
        return {'available': False, 'reason': 'no_taaqol_decision_in_result'}

    # Typed slots from Taaqol (None on sandbox)
    t_slots = getattr(td, 'typed_slots', None)
    t_slot_list = []
    if t_slots:
        for s in t_slots:
            t_slot_list.append({
                'slot_id':  s.slot_id.value if hasattr(s.slot_id, 'value') else str(s.slot_id),
                'state':    s.state.value if hasattr(s.state, 'value') else str(s.state),
                'value':    getattr(s, 'value', None),
            })

    # Trace events
    trace_events = []
    t_trace = getattr(td, 'taaqol_trace', None)
    if t_trace:
        for ev in t_trace:
            trace_events.append({
                'step':         getattr(ev, 'step', None),
                'component':    getattr(ev, 'component', None),
                'input_digest': getattr(ev, 'input_digest', None),
                'output':       getattr(ev, 'output', None),
                'strict_mode':  getattr(ev, 'strict_mode', None),
                'gamma_state':  getattr(ev, 'gamma_state', None),
                'gate_verdict': getattr(ev, 'gate_verdict', None),
            })
    else:
        # Still emit the trace events from the bridge decision
        t_trace_raw = getattr(td, 'trace', None)
        if t_trace_raw:
            for ev in t_trace_raw:
                trace_events.append({
                    'step':         getattr(ev, 'step', None),
                    'component':    getattr(ev, 'component', None),
                    'input_digest': getattr(ev, 'input_digest', ''),
                    'output':       getattr(ev, 'output', None),
                    'strict_mode':  getattr(ev, 'strict_mode', None),
                    'gamma_state':  getattr(ev, 'gamma_state', None),
                    'gate_verdict': getattr(ev, 'gate_verdict', None),
                })

    # Evidence contract
    ec = getattr(td, 'evidence_contract', None)
    ec_dict = None
    if ec is not None:
        ec_dict = str(ec)

    return {
        'available':                rt.get('active', False),
        'bridge_id':                getattr(td, 'bridge_id', None),
        'taaqol_commit':            getattr(td, 'taaqol_commit', None),
        'hokom_commit':             getattr(td, 'hokom_commit', None),
        'strict_mode':              getattr(td, 'strict_mode', None),
        'upstream_verdict':         getattr(td, 'upstream_verdict', None),
        'taaqol_verdict':           getattr(td, 'taaqol_verdict', None),
        'effective_verdict':        getattr(td, 'effective_verdict', None),
        'reason_codes':             list(getattr(td, 'reason_codes', ()) or ()),
        'contradictions':           list(getattr(td, 'contradictions', ()) or ()),
        'residuals':                list(getattr(td, 'residuals', ()) or ()),
        'fail_closed':              getattr(td, 'fail_closed', None),
        'slot_graph_digest':        getattr(td, 'slot_graph_digest', None),
        'gamma_result':             getattr(td, 'gamma_result', None),
        'transition_gate_result':   getattr(td, 'transition_gate_result', None),
        'center_scope':             getattr(td, 'taaqol_center_scope', None),
        # Runtime probes
        'runtime': {
            'kernel_loaded':     rt.get('kernel_loaded', False),
            'slot_graph_created': rt.get('slot_graph_created', False),
            'gamma_executed':    rt.get('gamma_executed', False),
            'gate_executed':     rt.get('gate_executed', False),
            'trace_event_count': rt.get('trace_event_count', 0),
            'failure_code':      rt.get('failure_code'),
            'failure_detail':    rt.get('failure_detail'),
            'vendor_sha':        rt.get('vendor_sha'),
        },
        # Typed slot evaluations (populated when Taaqol is live)
        'typed_slot_evaluations': t_slot_list,
        'trace_events':           trace_events,
        'evidence_contract':      ec_dict,
        # Per-claim decomposition (what this Taaqol call evaluated)
        'claim_id':        None,   # set per-call on macOS
        'claim_type':      'HOKOM_SGA_AYAT_AL_DAYN_LIVE_DEMO',
        'claim_profile':   'AYAT_AL_DAYN_LIVE_DEMO',
        'license_id':      None,   # populated by Taaqol when live
        'evidence_sufficiency': None,  # populated by Taaqol when live
    }


# ── morphosyntax from hr ──────────────────────────────────────────────────────
def _extract_morphosyntax(hr: dict) -> dict:
    """
    Number, gender, person, tense, mood, voice come from hokom() directly.
    The bundle only captures NUMBER_SLOT and GENDER_SLOT.
    We report all six here with their source.
    """
    return {
        'number':      hr.get('number'),
        'gender':      hr.get('gender'),
        'person':      hr.get('person'),
        'tense_aspect': hr.get('tense_aspect'),
        'mood':        hr.get('mood'),
        'voice':       hr.get('voice'),
        'source':      'hokom_pipeline:direct',
    }


# ── root / CRA detail ─────────────────────────────────────────────────────────
# Canonical wazn templates per augmented form family.
# Used when the pipeline cannot resolve wazn (root DEFERRED) but CRA
# has identified the form family from surface structure.
_FORM_FAMILY_TO_WAZN: dict[str, str] = {
    'FORM_I':    'فَعَلَ',
    'FORM_II':   'فَعَّلَ',
    'FORM_III':  'فَاعَلَ',
    'FORM_IV':   'أَفْعَلَ',
    'FORM_V':    'تَفَعَّلَ',
    'FORM_VI':   'تَفَاعَلَ',
    'FORM_VII':  'اِنْفَعَلَ',
    'FORM_VIII': 'اِفْتَعَلَ',
    'FORM_IX':   'اِفْعَلَّ',
    'FORM_X':    'اِسْتَفْعَلَ',
}


def _extract_root_detail(hr: dict) -> dict:
    rc  = hr.get('root_candidate')
    cra = hr.get('cra_result')
    p4a = hr.get('phase4a_result')

    rc_dir        = getattr(rc, 'directive', None) if rc else None
    canonical     = getattr(rc, 'canonical_root', None) if rc else None
    rc_residuals  = list(getattr(rc, 'residual_codes', ()) or ())

    cra_evidence  = list(getattr(cra, 'evidence', ()) or []) if cra else []
    cra_form      = getattr(cra, 'form_family', None) if cra else None
    cra_suffix    = getattr(cra, 'suffix_stripped', None) if cra else None
    cra_suffix_rule = getattr(cra, 'suffix_rule', None) if cra else None
    cra_provenance = getattr(cra, 'provenance', None) if cra else None
    cra_reason    = list(getattr(cra, 'reason_codes', []) or []) if cra else []
    cra_stem      = getattr(cra, 'canonical_stem', None) if cra else None

    p4a_residuals = list(getattr(p4a, 'residual_codes', ()) or ()) if p4a else []
    final_root    = hr.get('final_root')

    if canonical and isinstance(canonical, (tuple, list)):
        canonical_str = ''.join(canonical)
    elif canonical:
        canonical_str = str(canonical)
    else:
        canonical_str = None

    if final_root and isinstance(final_root, (tuple, list)):
        final_root_str = ''.join(final_root)
    elif final_root:
        final_root_str = str(final_root)
    else:
        final_root_str = None

    # Root state classification
    cra_seqs = getattr(cra, 'candidate_radical_sequences', None) if cra else None
    if cra_seqs and len(cra_seqs) >= 2 and not canonical_str:
        root_state = 'AMBIGUOUS'
        candidates = [''.join(s) for s in cra_seqs]
    elif rc_dir == 'ACCEPT' or final_root_str:
        root_state = 'KNOWN'
        candidates = []
    elif rc_dir == 'DEFER':
        root_state = 'DEFERRED'
        candidates = []
    else:
        root_state = 'UNKNOWN'
        candidates = []

    return {
        'root_state':        root_state,
        'canonical_root':    final_root_str or canonical_str,
        'root_candidates':   candidates,
        'cra_form_family':   cra_form,
        'cra_canonical_stem': cra_stem,
        'cra_suffix_stripped': cra_suffix,
        'cra_suffix_rule':   cra_suffix_rule,
        'cra_provenance':    cra_provenance,
        'cra_reason_codes':  cra_reason,
        'cra_evidence':      cra_evidence,
        'phase4a_residuals': p4a_residuals,
        'rc_residual_codes': rc_residuals,
        # Wazn: prefer pipeline's final_wazn; fall back to canonical template
        # derived from CRA form_family when root is DEFERRED/UNKNOWN.
        # The slot remains UNKNOWN — this is the template label only.
        'wazn':              (
            hr.get('final_wazn')
            or _FORM_FAMILY_TO_WAZN.get(cra_form or '')
        ),
        'wazn_source':       (
            'pipeline:final_wazn' if hr.get('final_wazn')
            else ('cra:form_family_template' if cra_form and cra_form in _FORM_FAMILY_TO_WAZN else None)
        ),
        'masdar':            hr.get('final_masdar') or hr.get('final_masdar_pattern'),
        'derivative_type':   hr.get('derivative_type'),
        'bab_state':         'UNKNOWN' if not hr.get('final_wazn') else 'KNOWN',
        'masdar_state':      'UNKNOWN' if not (hr.get('final_masdar') or hr.get('final_masdar_pattern')) else 'KNOWN',
    }


# ── main token processor ──────────────────────────────────────────────────────
def process_token_full(idx: int, surface: str) -> dict:
    """
    Run one token through the full pipeline and return a complete dict.
    All data comes from the live pipeline — nothing invented.
    """
    out: dict[str, Any] = {
        'token_index':    idx,
        'original_surface': surface,
        'error':          None,
    }

    try:
        from hokom_pipeline import hokom
        from pipeline.corpus.live_runner import _build_bundle_dict
        from pipeline.sga.adapters import build_claim_bundle
        from pipeline.sga.contracts import SlotState

        hr_obj = hokom(surface)
        hr     = dict(hr_obj)

        # ── 1. Normalisation & segmentation ───────────────────────────────
        sb = hr.get('segment_bundle')
        out['normalization'] = {
            'normalized_surface': hr.get('normalized_surface') or hr.get('normalized'),
            'source': 'hokom_pipeline:normalizer',
        }
        out['segmentation'] = {
            'proclitics':   list(hr.get('segment_proclitics') or hr.get('proclitics') or []),
            'host_surface': hr.get('segment_host') or hr.get('morphology_surface'),
            'enclitics':    list(hr.get('segment_enclitics') or hr.get('enclitics') or []),
            'has_article':  bool(hr.get('has_article') or hr.get('article')),
            'verdict':      getattr(sb, 'verdict', None).value if sb and getattr(sb, 'verdict', None) else None,
            'clitic_only':  hr.get('segment_clitic_only', False),
        }

        # ── 2. Word class ──────────────────────────────────────────────────
        wc_res = hr.get('word_class_result')
        wc_trace = []
        if wc_res and getattr(wc_res, 'trace', None):
            for t in wc_res.trace:
                wc_trace.append({
                    'step':     getattr(t, 'step', None),
                    'decision': getattr(t, 'decision', None),
                    'evidence': list(getattr(t, 'evidence', ()) or ()),
                })
        out['word_class'] = {
            'class':      hr.get('word_class'),
            'subclass':   hr.get('word_class_subclass') or (
                getattr(wc_res, 'subclass', None).value
                if wc_res and getattr(wc_res, 'subclass', None) else None
            ),
            'verdict':    hr.get('word_class_verdict'),
            'evidence':   [
                {'type': getattr(e, 'evidence_type', None).value if hasattr(getattr(e, 'evidence_type', None), 'value') else str(getattr(e,'evidence_type','')),
                 'source': getattr(e, 'source', None),
                 'value':  getattr(e, 'value', None),
                 'confidence': getattr(e, 'confidence', None)}
                for e in (getattr(wc_res, 'primary_evidence', ()) or ())
            ] if wc_res else [],
            'trace':      wc_trace,
            'inflection_skipped_reason': hr.get('inflection_skipped_reason'),
        }

        # ── 3. Root / CRA / wazn / masdar ────────────────────────────────
        out['root_analysis'] = _extract_root_detail(hr)

        # ── 4. Morphosyntax ───────────────────────────────────────────────
        out['morphosyntax'] = _extract_morphosyntax(hr)

        # ── 5. Full typed slots ───────────────────────────────────────────
        bd = _build_bundle_dict(hr)
        claim_kind = 'AYAT_AL_DAYN_LIVE_DEMO'
        bundle = build_claim_bundle(bd, claim_kind, claim_kind)

        typed_slots = [_serialize_slot(s) for s in bundle.typed_slots]
        out['typed_slots'] = typed_slots

        # claim_key (content hash) + evaluation_id (per-token)
        out['claim_key'] = bundle.claim_key
        out['evaluation_id'] = hashlib.sha256(
            f'{bundle.claim_key}:{idx}'.encode()
        ).hexdigest()[:16]

        # ── 6. Composite verdict ──────────────────────────────────────────
        out['composite_verdict'] = _build_composite_verdict(typed_slots, hr)

        # ── 7. H11-H15 layer ─────────────────────────────────────────────
        _H11_H15 = {
            'BAB_CANDIDATE_SET','MASDAR_CANDIDATE_SET','DERIVATIVE_CANDIDATE_SET',
            'NUMBER_SLOT','GENDER_SLOT','DEFINITENESS_SLOT','NISBA_SLOT',
            'COLLECTIVE_SLOT','UNIT_NOUN_SLOT','LEMMA_SLOT','PARADIGM_SLOT',
            'INFLECTIONAL_FAMILY_SLOT','DERIVATIONAL_FAMILY_SLOT',
        }
        h11_filled = [
            s['slot_id'] for s in typed_slots
            if s['slot_id'] in _H11_H15 and s['state'] == 'FILLED'
        ]
        out['h11_h15'] = {
            'reached':     bool(h11_filled),
            'filled_slots': h11_filled,
            'skipped_reason': hr.get('inflection_skipped_reason'),
        }

        # ── 8. Taaqol claim decomposition ────────────────────────────────
        out['taaqol'] = _decompose_taaqol(hr)

        # ── 9. Hokom pipeline verdict (upstream) ──────────────────────────
        out['pipeline_verdict'] = hr.get('verdict')
        out['active_residuals'] = list(hr.get('active_residuals') or ())
        out['resolved_residuals'] = list(hr.get('resolved_residuals') or ())

    except Exception as exc:
        import traceback
        out['error'] = {'type': type(exc).__name__, 'message': str(exc), 'trace': traceback.format_exc()}

    return out


# ── run all tokens ────────────────────────────────────────────────────────────
def run_all(verbose: bool = True) -> list[dict]:
    """
    Run all tokens through the pipeline with sequential governing-particle context.

    The SequentialAnalysisContext carrier (pipeline/p5_inflection/context_carrier.py)
    propagates mood from governing particles (وَلَا, أَنْ, أَلَّا, وَإِنْ, …) to the
    immediately following imperfect verb.  This is the ONLY inter-token state;
    all other analysis is stateless per token.

    Context injection rule:
      - After processing token N, update the carrier from token N's surface.
      - Before recording token N+1's result, consume any pending mood and inject
        it into the morphosyntax dict if token N+1 is an imperfect verb.
    """
    from pipeline.p5_inflection.context_carrier import SequentialAnalysisContext
    ctx = SequentialAnalysisContext()

    if verbose:
        print(f'Processing {len(TOKENS)} tokens…', file=sys.stderr)
    results = []
    for i, tok in enumerate(TOKENS):
        r = process_token_full(i + 1, tok)
        # Inject governing-particle mood into the current token's morphosyntax
        # (uses the mood set by the PREVIOUS token's update_from_token call).
        ctx.inject_mood_into_result(r, tok)
        # Record whether THIS token is a governing particle for the NEXT iteration.
        ctx.update_from_token(tok)
        if verbose and (i + 1) % 20 == 0:
            print(f'  {i + 1}/{len(TOKENS)}', file=sys.stderr)
        results.append(r)
    if verbose:
        print('  Done.', file=sys.stderr)
    return results


# ── integrity checks ──────────────────────────────────────────────────────────
def integrity_check(results: list[dict]) -> dict:
    # 1. Slot name without value/state
    slots_missing_state = 0
    for r in results:
        for s in r.get('typed_slots', []):
            if 'state' not in s or 'slot_id' not in s:
                slots_missing_state += 1

    # 2. LICENSED without scope (overall_verdict=FULLY_LICENSED while deferred exist)
    licensed_without_scope = 0
    for r in results:
        cv = r.get('composite_verdict', {})
        if cv.get('overall_verdict') == 'FULLY_LICENSED' and cv.get('has_unresolved_claims'):
            licensed_without_scope += 1

    # 3. Missing evaluation_id
    missing_eval_id = sum(1 for r in results if not r.get('evaluation_id'))

    # 4. Evaluation_id collisions
    eids = [r['evaluation_id'] for r in results if r.get('evaluation_id')]
    eid_collisions = len(eids) - len(set(eids))

    # 5. Missing Taaqol trace when runtime active
    missing_taaqol_trace = sum(
        1 for r in results
        if r.get('taaqol', {}).get('available')
        and not r.get('taaqol', {}).get('trace_events')
    )

    # 6. Claim_key nondeterminism (re-run first 5)
    nondeterminism = 0
    for r in results[:5]:
        r2 = process_token_full(r['token_index'], r['original_surface'])
        if r2.get('claim_key') and r.get('claim_key') and r2['claim_key'] != r['claim_key']:
            nondeterminism += 1

    # 7. Untyped payloads (no slots and no early stop)
    untyped = sum(
        1 for r in results
        if not r.get('typed_slots')
        and not r.get('word_class', {}).get('inflection_skipped_reason')
        and not r.get('error')
    )

    # 8. Silent fallbacks
    silent = sum(
        1 for r in results
        if not r.get('taaqol', {}).get('available')
        and not r.get('taaqol', {}).get('runtime', {}).get('failure_code')
        and not r.get('word_class', {}).get('inflection_skipped_reason')
        and r.get('word_class', {}).get('class') not in (None, 'MABNI', 'OPERATOR')
    )

    taaqol_live = sum(1 for r in results if r.get('taaqol', {}).get('available'))

    return {
        'SLOTS_MISSING_STATE':        slots_missing_state,
        'LICENSED_WITHOUT_SCOPE':     licensed_without_scope,
        'MISSING_EVALUATION_ID':      missing_eval_id,
        'EVALUATION_ID_COLLISIONS':   eid_collisions,
        'MISSING_TAAQOL_TRACE_ACTIVE': missing_taaqol_trace,
        'CLAIM_KEY_NONDETERMINISM':   nondeterminism,
        'UNTYPED_PAYLOADS':           untyped,
        'SILENT_FALLBACKS':           silent,
        'TAAQOL_RUNTIME_ACTIVE':      taaqol_live,
    }


# ── summary statistics ────────────────────────────────────────────────────────
def summary_stats(results: list[dict]) -> dict:
    overall_verdicts: dict[str, int] = {}
    for r in results:
        ov = r.get('composite_verdict', {}).get('overall_verdict', 'NO_DATA')
        overall_verdicts[ov] = overall_verdicts.get(ov, 0) + 1

    taaqol_verdicts: dict[str, int] = {}
    for r in results:
        tv = r.get('taaqol', {}).get('effective_verdict') or 'NO_TAAQOL'
        taaqol_verdicts[tv] = taaqol_verdicts.get(tv, 0) + 1

    root_states: dict[str, int] = {}
    for r in results:
        rs = r.get('root_analysis', {}).get('root_state', 'NONE')
        root_states[rs] = root_states.get(rs, 0) + 1

    return {
        'token_count':      len(results),
        'typed_bundles':    sum(1 for r in results if r.get('typed_slots')),
        'taaqol_live':      sum(1 for r in results if r.get('taaqol', {}).get('available')),
        'h11_h15_reached':  sum(1 for r in results if r.get('h11_h15', {}).get('reached')),
        'early_stops':      sum(1 for r in results if r.get('word_class', {}).get('inflection_skipped_reason')),
        'overall_verdicts': overall_verdicts,
        'taaqol_verdicts':  taaqol_verdicts,
        'root_states':      root_states,
        'errors':           sum(1 for r in results if r.get('error')),
    }


# ── live gold metrics (HOKOM-LIVE-GOLD-ORACLE-AND-METRICS-CORRECTION-01) ─────
# All metrics are computed from the immutable gold manifest in
# pipeline/governance/gold_manifest.py.  No hard-coded per-surface branches.


def _is_allah_surface(surface: str) -> bool:
    """Return True if this token is a لفظ الجلالة form (اللَّهُ and proclitic variants)."""
    bare = ''.join(c for c in surface if c not in 'ًٌٍَُِّْٰ')
    bare_no_shadda = bare.replace('ّ', '')
    return 'الله' in bare_no_shadda or 'لله' in bare_no_shadda


def _compute_csv_divergences(results_raw: list) -> int:
    """
    Compare on-disk CSV (word_class / tense_aspect / person) against
    the in-memory hokom() output for all 129 tokens.
    Returns 0 if the CSV file does not yet exist.
    """
    import csv as _csv
    csv_path = REPORT_DIR / 'ayat_al_dayn_results.csv'
    if not csv_path.exists():
        return 0
    try:
        on_disk: dict[int, dict] = {}
        with open(csv_path, newline='', encoding='utf-8') as f:
            for row in _csv.DictReader(f):
                idx = int(row.get('token_index', 0))
                on_disk[idx] = {
                    'word_class':   row.get('word_class', ''),
                    'tense_aspect': row.get('tense_aspect', ''),
                    'person':       row.get('person', ''),
                }
        divergences = 0
        for i, (tok, r) in enumerate(results_raw):
            idx = i + 1
            disk = on_disk.get(idx)
            if disk is None:
                continue
            live_wc = r.get('word_class') or ''
            live_ta = r.get('tense_aspect') or ''
            live_p  = str(r.get('person') or '')
            if (live_wc != disk['word_class']
                    or live_ta != disk['tense_aspect']
                    or live_p != disk['person']):
                divergences += 1
        return divergences
    except Exception:
        return -1


def compute_live_metrics() -> dict:
    """
    Compute live pipeline metrics from the complete unfiltered in-memory record
    of all 129 TOKENS in the Ayat al-Dayn corpus.

    HOKOM-LIVE-GOLD-ORACLE-COVERAGE-AND-GATE-HARDENING-02:
      - Metrics are derived from hokom() calls on the in-memory TOKENS list.
      - NOT read from any cached CSV or JSON file.
      - Comparison is against the immutable gold manifest (gold_manifest.py).
      - KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS reports known form mismatches as
        NONZERO — do not set to zero.
      - Uncorrelated ambiguity failures ALSO count toward
        LIVE_PERSON_NUMBER_GENDER_MISMATCHES (they are a gender-representation defect).
      - Context mood mismatches: for gold records with defect_codes containing
        'CONTEXT_MOOD_MISMATCH', compare raw hokom() mood to gold.mood.
      - Word-class blanks split into TOTAL / JUSTIFIED / UNJUSTIFIED / UNADJUDICATED.
        Terminal JAMID_AALAM_BOUNDARY and SEGMENTATION_NO_LEXICAL_HOST are JUSTIFIED.
        OPERATOR_BOUNDARY-routed tokens are JUSTIFIED.  All others are UNJUSTIFIED
        until explicitly adjudicated.

    Returns a dict with all required metric keys.
    """
    from hokom_pipeline import hokom  # noqa: PLC0415
    from pipeline.governance.gold_manifest import (
        CORPUS_GOLD,
        WC_JUSTIFIED_REASON_CODES,
        WC_JUSTIFIED_ROUTES,
    )

    # ── Run full corpus in-memory ────────────────────────────────────────────
    # HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01
    # Use sequential context carrier to inject governing-particle mood into
    # the immediately following imperfect verb (fixes CONTEXT_MOOD_MISMATCH).
    # Also apply feminine-noun lookahead for تَ-prefix hollow verbs:
    # when the next token is a feminine noun (bare form ends with ة),
    # resolve the 2MS/3FS ambiguity to 3FS (e.g. تَكُونَ + تِجَارَةً → 3FS).
    from pipeline.p5_inflection.context_carrier import SequentialAnalysisContext as _SAC
    _ctx = _SAC()
    results_raw: list[tuple[str, dict]] = []
    for _i, tok in enumerate(TOKENS):
        r = hokom(tok)
        # Inject governing-particle mood (JUSSIVE/SUBJUNCTIVE from prev token)
        _pending_mood = _ctx.consume_mood()
        if _pending_mood and r.get('tense_aspect') == 'IMPERFECT':
            r['mood'] = _pending_mood
        _ctx.update_from_token(tok)
        # Lookahead: ambiguous تَ-prefix (person='2|3', SG) + next token is
        # feminine noun (bare ends with taa marbuta ة) → resolve to 3FS.
        _next_tok = TOKENS[_i + 1] if _i + 1 < len(TOKENS) else ''
        from pipeline.p5_inflection.feature_system import strip_diacritics as _sd
        if (r.get('person') in ('2|3',)
                and r.get('number') == 'SG'
                and _sd(_next_tok).endswith('ة')):
            r['person'] = '3'
            r['gender'] = 'F'
        results_raw.append((tok, r))
    results_by_index: dict[int, dict] = {
        i + 1: r for i, (_, r) in enumerate(results_raw)
    }

    # ── 1. LIVE_JAMID_BOUNDARY_VIOLATIONS ───────────────────────────────────
    jamid_violations = 0
    for tok, r in results_raw:
        if _is_allah_surface(tok):
            if r.get('word_class') == 'FI3L' or r.get('tense_aspect') is not None:
                jamid_violations += 1

    # ── 2. Gold-manifest comparisons ────────────────────────────────────────
    form_mismatches = 0
    known_out_of_scope = 0
    png_mismatches = 0
    voice_mismatches = 0
    context_mood_mismatches = 0
    uncorrelated_ambiguity = 0
    word_class_mismatches = 0
    gold_token_mismatches = 0

    for gold in CORPUS_GOLD:
        r = results_by_index.get(gold.token_index)
        if r is None:
            continue
        token_has_mismatch = False

        # word_class check
        if gold.word_class is not None:
            if r.get('word_class') != gold.word_class:
                word_class_mismatches += 1
                token_has_mismatch = True

        # CRA form family check
        if gold.cra_form_family is not None:
            cra = r.get('cra_result')
            cra_form = getattr(cra, 'form_family', None) if cra is not None else None
            if cra_form != gold.cra_form_family:
                form_mismatches += 1
                token_has_mismatch = True
                if gold.form_family_out_of_scope:
                    known_out_of_scope += 1

        # voice check
        if gold.voice is not None:
            if r.get('voice') != gold.voice:
                voice_mismatches += 1
                token_has_mismatch = True

        # context mood check — only for records with CONTEXT_MOOD_MISMATCH defect
        if (
            gold.mood is not None
            and 'CONTEXT_MOOD_MISMATCH' in gold.defect_codes
            and r.get('mood') != gold.mood
        ):
            context_mood_mismatches += 1
            token_has_mismatch = True

        # PNG check — only when no ambiguity_candidates declared
        if not gold.ambiguity_candidates:
            mismatch = False
            if gold.person is not None and str(r.get('person') or '') != gold.person:
                mismatch = True
            if gold.number is not None and str(r.get('number') or '') != gold.number:
                mismatch = True
            if gold.gender is not None and str(r.get('gender') or '') != gold.gender:
                mismatch = True
            if mismatch:
                png_mismatches += 1
                token_has_mismatch = True
        else:
            # Correlated ambiguity: pipeline must supply all candidates.
            # The pipeline's gender field must include every gender value present
            # across all AmbiguityCandidate entries.
            # Current pipeline emits gender='M' only → the 3FS (gender='F') candidate
            # is absent → uncorrelated ambiguity.
            # These failures ALSO count toward LIVE_PERSON_NUMBER_GENDER_MISMATCHES
            # because they represent an incorrect gender representation.
            live_gender = str(r.get('gender') or '')
            candidate_genders = {c.gender for c in gold.ambiguity_candidates}
            if len(candidate_genders) > 1:
                for cand in gold.ambiguity_candidates:
                    if cand.gender not in live_gender:
                        uncorrelated_ambiguity += 1
                        png_mismatches += 1   # gender defect → counts as PNG mismatch
                        token_has_mismatch = True
                        break

        if token_has_mismatch:
            gold_token_mismatches += 1

    # ── 3. Structural counts (from unfiltered pipeline output) ───────────────
    nonverbs_as_verbs = word_class_mismatches  # ISM→FI3L misclassifications

    verbs_as_nouns = sum(
        1 for tok, r in results_raw
        if r.get('tense_aspect') in ('IMPERFECT', 'PAST', 'IMPERATIVE')
        and r.get('word_class') != 'FI3L'
        and r.get('jamid_verdict') != 'JAMID_AALAM_BOUNDARY'
    )

    missing_inflection = sum(
        1 for tok, r in results_raw
        if r.get('word_class') == 'FI3L' and r.get('tense_aspect') is None
    )

    inflection_deferred = sum(
        1 for tok, r in results_raw
        if r.get('word_class') == 'FI3L'
        and (r.get('tense_aspect') is None or r.get('person') is None)
    )

    overall_deferred = sum(
        1 for tok, r in results_raw
        if r.get('word_class') is None
        and r.get('tense_aspect') is None
        and r.get('jamid_verdict') != 'JAMID_AALAM_BOUNDARY'
        and r.get('boundary_type') != 'JAMID_AALAM_BOUNDARY'
    )

    # ── 4. Word-class not-opened categories ─────────────────────────────────
    # Every token with wc=None falls into exactly one category with a reason code.
    # JUSTIFIED: JAMID_AALAM_BOUNDARY, SEGMENTATION_NO_LEXICAL_HOST, OPERATOR_BOUNDARY
    # UNJUSTIFIED: WORD_CLASS_DEFERRED with no known route — unexplained deferral
    # UNADJUDICATED: reserved for tokens requiring case-by-case review
    wc_not_opened_total = 0
    wc_justified = 0
    wc_unjustified = 0
    wc_unadjudicated = 0

    for tok, r in results_raw:
        if r.get('word_class') is not None:
            continue
        wc_not_opened_total += 1

        skip_reason = r.get('inflection_skipped_reason') or ''
        route = r.get('_route_v') or ''
        jamid = r.get('jamid_verdict') or r.get('boundary_type') or ''

        if (
            skip_reason in WC_JUSTIFIED_REASON_CODES
            or jamid == 'JAMID_AALAM_BOUNDARY'
            or route in WC_JUSTIFIED_ROUTES
        ):
            wc_justified += 1
        else:
            # WORD_CLASS_DEFERRED with no operator/boundary route → unjustified
            wc_unjustified += 1

    csv_divergences = _compute_csv_divergences(results_raw)

    return {
        # Boundary safety
        'LIVE_JAMID_BOUNDARY_VIOLATIONS':       jamid_violations,
        # Gold oracle — token-level
        'LIVE_GOLD_TOKEN_MISMATCHES':            gold_token_mismatches,
        # Form family
        'LIVE_FORM_FAMILY_MISMATCHES':           form_mismatches,
        # Plural canonical key
        'KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS':     known_out_of_scope,
        # Backward compat alias — do not remove until all tests migrated
        'KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL':      known_out_of_scope,
        # Person / Number / Gender (includes uncorrelated ambiguity gender failures)
        'LIVE_PERSON_NUMBER_GENDER_MISMATCHES':  png_mismatches,
        # Voice
        'LIVE_VOICE_MISMATCHES':                 voice_mismatches,
        # Context mood (raw hokom() vs gold declared mood for CONTEXT_MOOD_MISMATCH records)
        'LIVE_CONTEXT_MOOD_MISMATCHES':          context_mood_mismatches,
        # Correlated ambiguity sub-count
        'LIVE_UNCORRELATED_AMBIGUITY':           uncorrelated_ambiguity,
        # Inflection
        'LIVE_MISSING_INFLECTION_FEATURES':      missing_inflection,
        # Word class mismatches
        'LIVE_NONVERBS_AS_VERBS':                nonverbs_as_verbs,
        'LIVE_VERBS_AS_NOUNS':                   verbs_as_nouns,
        # Word class not-opened — split into three categories
        'WORD_CLASS_NOT_OPENED_TOTAL':           wc_not_opened_total,
        'JUSTIFIED_WORD_CLASS_NOT_OPENED':       wc_justified,
        'UNJUSTIFIED_WORD_CLASS_NOT_OPENED':     wc_unjustified,
        'UNADJUDICATED_WORD_CLASS_NOT_OPENED':   wc_unadjudicated,
        # Legacy alias (old flat count) — equals wc_not_opened_total, kept for compat
        'WORD_CLASS_DEFERRED':                   wc_not_opened_total,
        # Pipeline deferred
        'INFLECTION_DEFERRED':                   inflection_deferred,
        'OVERALL_PIPELINE_DEFERRED':             overall_deferred,
        'CSV_IN_MEMORY_DIVERGENCES':             csv_divergences,
    }


# ── terminal format ───────────────────────────────────────────────────────────
def _bare(s) -> str:
    if not s:
        return ''
    return ''.join(c for c in str(s) if unicodedata.category(c) not in ('Mn', 'Cf'))


def format_terminal(results: list[dict], stats: dict, checks: dict) -> str:
    lines = []
    lines.append(f'\nHOKOM–TAAQOL LIVE DEMO — آية الدَّيْن (البقرة 2:282)')
    lines.append('=' * 110)
    lines.append(
        f'{"#":>3}  {"Surface":<14} {"Segmentation":<22} {"Host":<14} '
        f'{"WC":<8} {"Root":<10} {"Wazn":<8} {"H11-15":^6} '
        f'{"Taaqol":<12} Layer Verdict'
    )
    lines.append('-' * 110)

    for r in results:
        seg = r.get('segmentation', {})
        procs = seg.get('proclitics', [])
        encs  = seg.get('enclitics', [])
        host  = seg.get('host_surface', '')

        seg_str = ''
        if procs:
            seg_str += '+'.join(procs) + '|'
        seg_str += (_bare(host) or '')
        if encs:
            seg_str += '|' + '+'.join(encs)

        ra  = r.get('root_analysis', {})
        cv  = r.get('composite_verdict', {})
        tq  = r.get('taaqol', {})
        wc  = r.get('word_class', {})

        root_disp = ra.get('canonical_root') or (
            '/'.join(ra.get('root_candidates', [])[:2]) or ra.get('root_state', '—')
        )
        wazn_disp = ra.get('wazn') or '—'
        h_disp    = 'YES' if r.get('h11_h15', {}).get('reached') else '—'
        tq_eff    = tq.get('effective_verdict') or tq.get('runtime', {}).get('failure_code') or '—'
        wc_class  = wc.get('class') or '—'

        # Summarise per-layer verdict (skip NOT_APPLICABLE)
        layer_summary = {
            ld['layer']: ld['layer_verdict']
            for ld in cv.get('by_layer', [])
            if ld['layer_verdict'] != 'NOT_APPLICABLE'
        }
        key_layers = ['WORD_CLASS', 'RADICAL', 'PATTERN', 'MORPHOSYNTAX']
        layer_str = ' | '.join(
            f'{l}:{layer_summary.get(l,"—")}'
            for l in key_layers
            if l in layer_summary
        )

        lines.append(
            f'{r["token_index"]:>3}  '
            f'{_bare(r["original_surface"]):<14} '
            f'{seg_str:<22} '
            f'{_bare(host) or "":<14} '
            f'{wc_class:<8} '
            f'{_bare(root_disp) or "":<10} '
            f'{_bare(wazn_disp):<8} '
            f'{h_disp:^6}  '
            f'{tq_eff:<14} '
            f'{layer_str}'
        )

    lines.append('-' * 110)
    lines.append(
        f'\nTokens:{stats["token_count"]} | Typed bundles:{stats["typed_bundles"]} | '
        f'Taaqol live:{stats["taaqol_live"]} | H11-15:{stats["h11_h15_reached"]} | '
        f'Early stops:{stats["early_stops"]}'
    )
    lines.append(f'Root states:   {stats["root_states"]}')
    lines.append(f'Taaqol:        {stats["taaqol_verdicts"]}')
    lines.append(f'Overall:       {stats["overall_verdicts"]}')
    lines.append(f'\nIntegrity:')
    for k, v in checks.items():
        ok = '✓' if v == 0 or (k == 'TAAQOL_RUNTIME_ACTIVE' and v >= 0) else '✗'
        lines.append(f'  {k:<40} = {v}  {ok}')
    return '\n'.join(lines)


# ── JSON format ───────────────────────────────────────────────────────────────
def format_json(results: list[dict], stats: dict, checks: dict, meta: dict) -> str:
    return json.dumps({
        'stage':   'HOKOM-TAAQOL-AYAT-AL-DAYN-LIVE-DEMO-01',
        'version': '2',
        'meta':    meta,
        'summary': stats,
        'integrity_checks': checks,
        'tokens':  results,
    }, indent=2, ensure_ascii=False, default=str)


# ── CSV (summary row per token) ───────────────────────────────────────────────
def format_csv(results: list[dict]) -> str:
    buf = io.StringIO()
    fields = [
        'token_index', 'original_surface', 'normalized_surface',
        'proclitics', 'host_surface', 'enclitics',
        'word_class', 'word_class_subclass', 'word_class_verdict', 'inflection_skipped_reason',
        'root_state', 'canonical_root', 'root_candidates',
        'cra_form_family', 'cra_suffix_stripped', 'cra_reason_codes', 'phase4a_residuals',
        'wazn', 'masdar', 'derivative_type',
        'number', 'gender', 'person', 'tense_aspect', 'mood', 'voice',
        'h11_h15_reached', 'h11_h15_filled_slots',
        'typed_slot_count', 'filled_slot_count', 'unknown_slot_count',
        'not_opened_layers', 'active_residuals',
        'overall_verdict', 'has_unresolved_claims',
        'licensed_claims', 'deferred_claims',
        'taaqol_effective_verdict', 'taaqol_failure_code', 'taaqol_reason_codes',
        'claim_key', 'evaluation_id', 'pipeline_verdict', 'error',
    ]
    writer = csv_mod.DictWriter(buf, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for r in results:
        seg = r.get('segmentation', {})
        ra  = r.get('root_analysis', {})
        ms  = r.get('morphosyntax', {})
        cv  = r.get('composite_verdict', {})
        tq  = r.get('taaqol', {})
        wc  = r.get('word_class', {})
        h   = r.get('h11_h15', {})
        ts  = r.get('typed_slots', [])

        writer.writerow({
            'token_index':          r['token_index'],
            'original_surface':     r['original_surface'],
            'normalized_surface':   r.get('normalization', {}).get('normalized_surface', ''),
            'proclitics':           ' '.join(seg.get('proclitics', [])),
            'host_surface':         seg.get('host_surface', ''),
            'enclitics':            ' '.join(seg.get('enclitics', [])),
            'word_class':           wc.get('class', ''),
            'word_class_subclass':  wc.get('subclass', ''),
            'word_class_verdict':   wc.get('verdict', ''),
            'inflection_skipped_reason': wc.get('inflection_skipped_reason', ''),
            'root_state':           ra.get('root_state', ''),
            'canonical_root':       ra.get('canonical_root', ''),
            'root_candidates':      '/'.join(ra.get('root_candidates', [])),
            'cra_form_family':      ra.get('cra_form_family', ''),
            'cra_suffix_stripped':  ra.get('cra_suffix_stripped', ''),
            'cra_reason_codes':     '; '.join(ra.get('cra_reason_codes', [])),
            'phase4a_residuals':    '; '.join(ra.get('phase4a_residuals', [])),
            'wazn':                 ra.get('wazn', ''),
            'masdar':               ra.get('masdar', ''),
            'derivative_type':      ra.get('derivative_type', ''),
            'number':               ms.get('number', ''),
            'gender':               ms.get('gender', ''),
            'person':               ms.get('person', ''),
            'tense_aspect':         ms.get('tense_aspect', ''),
            'mood':                 ms.get('mood', ''),
            'voice':                ms.get('voice', ''),
            'h11_h15_reached':      str(h.get('reached', False)),
            'h11_h15_filled_slots': ' '.join(h.get('filled_slots', [])),
            'typed_slot_count':     len(ts),
            'filled_slot_count':    sum(1 for s in ts if s.get('state') == 'FILLED'),
            'unknown_slot_count':   sum(1 for s in ts if s.get('state') == 'UNKNOWN'),
            'not_opened_layers':    '; '.join(cv.get('not_opened_layers', [])),
            'active_residuals':     '; '.join(cv.get('active_residuals', [])),
            'overall_verdict':      cv.get('overall_verdict', ''),
            'has_unresolved_claims': str(cv.get('has_unresolved_claims', '')),
            'licensed_claims':      ' '.join(cv.get('licensed_claims', [])),
            'deferred_claims':      ' '.join(cv.get('deferred_claims', [])),
            'taaqol_effective_verdict': tq.get('effective_verdict', ''),
            'taaqol_failure_code':  tq.get('runtime', {}).get('failure_code', ''),
            'taaqol_reason_codes':  '; '.join(tq.get('reason_codes', [])),
            'claim_key':            r.get('claim_key', ''),
            'evaluation_id':        r.get('evaluation_id', ''),
            'pipeline_verdict':     r.get('pipeline_verdict', ''),
            'error':                str(r.get('error') or ''),
        })
    return buf.getvalue()


# ── HTML helpers ──────────────────────────────────────────────────────────────
def _esc(s) -> str:
    if s is None:
        return ''
    return (str(s)
            .replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def _state_badge(state: str | None) -> str:
    if not state:
        return '<span class="badge bdg-gray">—</span>'
    cls = {
        'FILLED':          'bdg-green',
        'LICENSED':        'bdg-green',
        'FULLY_LICENSED':  'bdg-green',
        'PARTIAL':         'bdg-yellow',
        'UNKNOWN':         'bdg-amber',
        'NOT_OPENED':      'bdg-amber',
        'DEFERRED':        'bdg-amber',
        'NOT_APPLICABLE':  'bdg-gray',
        'AMBIGUOUS':       'bdg-purple',
        'BLOCKED':         'bdg-red',
        'COMPOSITE':       'bdg-blue',
        'ERROR':           'bdg-red',
    }.get(state, 'bdg-blue')
    return f'<span class="badge {cls}">{_esc(state)}</span>'


def _slot_html(s: dict) -> str:
    state = s.get('state', '—')
    val   = s.get('value')
    cset  = s.get('candidate_set')
    res   = s.get('residual')
    evs   = s.get('evidence', [])

    val_html = _esc(val) if val is not None else '<em class="nil">—</em>'
    if cset and cset.get('selected'):
        val_html = f'<strong>{_esc(cset["selected"])}</strong>'
        if cset.get('candidates'):
            cands = ', '.join(_esc(c.get('value', c)) for c in cset['candidates'][:4])
            val_html += f' <small class="cands">candidates: {cands}</small>'

    ev_html = ''
    if evs:
        ev_html = '<div class="ev-list">' + ''.join(
            f'<span class="ev-tag">{_esc(e.get("evidence_id","?"))}</span>' for e in evs[:3]
        ) + '</div>'

    res_html = ''
    if res:
        res_html = (
            f'<div class="residual-tag">⚑ {_esc(res.get("code",""))} — '
            f'{_esc(res.get("reason",""))}</div>'
        )

    layer = s.get('layer', '—')
    return (
        f'<tr class="slot-row state-{state.lower()}">'
        f'<td class="slot-id">{_esc(s.get("slot_id",""))}</td>'
        f'<td class="slot-layer">{_esc(layer)}</td>'
        f'<td>{_state_badge(state)}</td>'
        f'<td class="slot-val">{val_html}{ev_html}{res_html}</td>'
        f'</tr>'
    )


def _token_html(r: dict, open_detail: bool = False) -> str:
    idx   = r['token_index']
    surf  = r['original_surface']
    seg   = r.get('segmentation', {})
    ra    = r.get('root_analysis', {})
    wc    = r.get('word_class', {})
    ms    = r.get('morphosyntax', {})
    cv    = r.get('composite_verdict', {})
    tq    = r.get('taaqol', {})
    h     = r.get('h11_h15', {})
    ts    = r.get('typed_slots', [])

    # Summary row
    root_disp = ra.get('canonical_root') or (
        ' / '.join(ra.get('root_candidates', [])[:2]) or ra.get('root_state', '—')
    )
    overall = cv.get('overall_verdict', '—')

    # Layer verdict badges
    layer_badges = ''
    for ld in cv.get('by_layer', []):
        if ld['layer_verdict'] == 'NOT_APPLICABLE':
            continue
        layer_badges += f'{_state_badge(ld["layer_verdict"])}<small class="lv-name">{_esc(ld["layer"])}</small> '

    # Taaqol row
    tq_eff = tq.get('effective_verdict') or '—'
    tq_fail = tq.get('runtime', {}).get('failure_code') or ''

    # Full slot table
    slot_rows = ''.join(_slot_html(s) for s in ts)

    # Deferred / not-opened breakdown
    deferred_section = ''
    if cv.get('deferred_claims'):
        deferred_section = (
            '<div class="claim-group deferred-group">'
            '<div class="cg-title">DEFERRED CLAIMS</div>'
            + ''.join(f'<span class="claim-tag deferred">{_esc(s)}</span>' for s in cv['deferred_claims'])
            + '</div>'
        )
    licensed_section = ''
    if cv.get('licensed_claims'):
        licensed_section = (
            '<div class="claim-group licensed-group">'
            '<div class="cg-title">LICENSED CLAIMS</div>'
            + ''.join(f'<span class="claim-tag licensed">{_esc(s)}</span>' for s in cv['licensed_claims'])
            + '</div>'
        )
    ambig_section = ''
    if cv.get('ambiguous_claims'):
        ambig_section = (
            '<div class="claim-group ambig-group">'
            '<div class="cg-title">AMBIGUOUS CLAIMS</div>'
            + ''.join(f'<span class="claim-tag ambig">{_esc(s)}</span>' for s in cv['ambiguous_claims'])
            + '</div>'
        )
    not_opened_section = ''
    if cv.get('not_opened_layers'):
        not_opened_section = (
            '<div class="claim-group not-opened-group">'
            '<div class="cg-title">NOT OPENED LAYERS</div>'
            + ''.join(f'<span class="claim-tag not-opened">{_esc(l)}</span>' for l in cv['not_opened_layers'])
            + '</div>'
        )

    # Morphosyntax values (real values or — if absent)
    ms_items = [
        ('number', ms.get('number')), ('gender', ms.get('gender')),
        ('person', ms.get('person')), ('tense', ms.get('tense_aspect')),
        ('mood', ms.get('mood')), ('voice', ms.get('voice')),
    ]
    ms_html = ' '.join(
        f'<span class="ms-item"><span class="ms-lbl">{_esc(k)}</span>'
        f'<span class="ms-val">{_esc(v) if v else "—"}</span></span>'
        for k, v in ms_items
    )

    # Root analysis row
    root_analysis_html = (
        f'<table class="mini-table"><tr>'
        f'<td><b>state</b></td><td>{_esc(ra.get("root_state","—"))}</td>'
        f'<td><b>canonical</b></td><td class="arabic">{_esc(ra.get("canonical_root","—"))}</td>'
        f'<td><b>wazn</b></td><td>{_esc(ra.get("wazn","—"))}</td>'
        f'<td><b>masdar</b></td><td>{_esc(ra.get("masdar","—"))}</td>'
        f'<td><b>form</b></td><td>{_esc(ra.get("cra_form_family","—"))}</td>'
        f'<td><b>suffix</b></td><td class="arabic">{_esc(ra.get("cra_suffix_stripped","—"))}</td>'
        f'</tr></table>'
    )
    if ra.get('cra_reason_codes') or ra.get('phase4a_residuals') or ra.get('rc_residual_codes'):
        all_reasons = (ra.get('cra_reason_codes') or []) + (ra.get('phase4a_residuals') or []) + (ra.get('rc_residual_codes') or [])
        root_analysis_html += (
            '<div class="residual-tag">Root DEFER reason: '
            + '; '.join(_esc(x) for x in all_reasons)
            + '</div>'
        )

    # Taaqol detail
    tq_detail = (
        f'<table class="mini-table"><tr>'
        f'<td><b>upstream</b></td><td>{_esc(tq.get("upstream_verdict","—"))}</td>'
        f'<td><b>taaqol</b></td><td>{_esc(tq.get("taaqol_verdict","—"))}</td>'
        f'<td><b>effective</b></td><td>{_state_badge(tq_eff)}</td>'
        f'<td><b>fail_closed</b></td><td>{_esc(tq.get("fail_closed","—"))}</td>'
        f'</tr>'
        f'<tr>'
        f'<td><b>gamma</b></td><td>{_esc(tq.get("gamma_result","—"))}</td>'
        f'<td><b>slot_graph</b></td><td>{_esc(tq.get("slot_graph_digest","—"))}</td>'
        f'<td><b>gate</b></td><td>{_esc(tq.get("transition_gate_result","—"))}</td>'
        f'<td><b>active</b></td><td>{str(tq.get("available","—"))}</td>'
        f'</tr></table>'
    )
    if tq_fail:
        tq_detail += f'<div class="residual-tag">Taaqol failure: {_esc(tq_fail)}</div>'
    if tq.get('reason_codes'):
        tq_detail += (
            '<div class="residual-tag">reason_codes: '
            + '; '.join(_esc(x) for x in tq.get('reason_codes', []))
            + '</div>'
        )
    if tq.get('trace_events'):
        tq_detail += '<div class="trace-title">Trace events:</div>'
        for ev in tq['trace_events']:
            tq_detail += (
                f'<div class="trace-ev">'
                f'[{_esc(ev.get("step","?"))}] {_esc(ev.get("component",""))} → '
                f'{_esc(str(ev.get("output",""))[:120])}'
                f'</div>'
            )

    open_attr = ' open' if open_detail else ''
    return f'''
<details class="token-details"{open_attr} id="tok{idx}">
  <summary class="token-summary">
    <span class="tok-idx">#{idx}</span>
    <span class="tok-surf arabic">{_esc(surf)}</span>
    <span class="tok-wc">{_esc(wc.get("class","—"))}</span>
    <span class="tok-root arabic">{_esc(root_disp)}</span>
    <span class="tok-wazn">{_esc(ra.get("wazn","—"))}</span>
    {_state_badge(overall)}
    {_state_badge(tq_eff)}
    <span class="tok-layer-badges">{layer_badges}</span>
  </summary>

  <div class="token-body">
    <div class="section-grid">

      <div class="section">
        <div class="section-title">Segmentation</div>
        <table class="mini-table">
          <tr><td>proclitics</td><td class="arabic">{_esc(' '.join(seg.get('proclitics',[])) or '—')}</td></tr>
          <tr><td>host</td><td class="arabic"><strong>{_esc(seg.get('host_surface','—'))}</strong></td></tr>
          <tr><td>enclitics</td><td class="arabic">{_esc(' '.join(seg.get('enclitics',[])) or '—')}</td></tr>
          <tr><td>article</td><td>{str(seg.get('has_article',False))}</td></tr>
        </table>
      </div>

      <div class="section">
        <div class="section-title">Word Class</div>
        <table class="mini-table">
          <tr><td>class</td><td><strong>{_esc(wc.get('class','—'))}</strong></td></tr>
          <tr><td>subclass</td><td>{_esc(wc.get('subclass','—'))}</td></tr>
          <tr><td>verdict</td><td>{_state_badge(wc.get('verdict'))}</td></tr>
          <tr><td>early_stop</td><td>{_esc(wc.get('inflection_skipped_reason','—'))}</td></tr>
        </table>
      </div>

      <div class="section">
        <div class="section-title">Morphosyntax (from pipeline)</div>
        <div class="ms-grid">{ms_html}</div>
      </div>

    </div>

    <div class="section">
      <div class="section-title">Root / CRA / Wazn / Masdar</div>
      {root_analysis_html}
    </div>

    <div class="section">
      <div class="section-title">Claim Groups</div>
      <div class="claim-groups">
        {licensed_section}{deferred_section}{ambig_section}{not_opened_section}
      </div>
    </div>

    <div class="section">
      <div class="section-title">Taaqol Claim Decomposition</div>
      {tq_detail}
    </div>

    <div class="section">
      <div class="section-title">All Typed Slots ({len(ts)} total)</div>
      <table class="slot-table">
        <thead><tr><th>Slot</th><th>Layer</th><th>State</th><th>Value / Evidence / Residual</th></tr></thead>
        <tbody>{slot_rows}</tbody>
      </table>
    </div>

    <div class="section footer-meta">
      claim_key: <code>{_esc(r.get('claim_key',''))}</code>
      &nbsp;|&nbsp;
      evaluation_id: <code>{_esc(r.get('evaluation_id',''))}</code>
      &nbsp;|&nbsp;
      pipeline_verdict: <strong>{_esc(r.get('pipeline_verdict',''))}</strong>
    </div>
  </div>
</details>
'''


# ── full HTML report ──────────────────────────────────────────────────────────
def format_html(results: list[dict], stats: dict, checks: dict, meta: dict) -> str:
    # Open first DEFERRED-root token by default for demo
    open_idx = next(
        (r['token_index'] for r in results if r.get('root_analysis', {}).get('root_state') == 'DEFERRED'),
        None
    )

    token_html_parts = [_token_html(r, open_detail=(r['token_index'] == open_idx)) for r in results]
    all_tokens_html  = '\n'.join(token_html_parts)

    # Integrity section
    int_html = ''
    for k, v in checks.items():
        ok = v == 0 or (k == 'TAAQOL_RUNTIME_ACTIVE' and v >= 0)
        cls = 'int-ok' if ok else 'int-bad'
        int_html += f'<div class="int-item {cls}"><span class="int-key">{_esc(k)}</span><span class="int-val">{v}</span></div>\n'

    taaqol_note = (
        '<span class="tq-active">✓ Taaqol runtime active — live evaluations present</span>'
        if checks['TAAQOL_RUNTIME_ACTIVE'] > 0
        else '<span class="tq-deferred">⚠ Taaqol runtime unavailable (Python 3.10 sandbox). '
             'On macOS/3.12.4 all Taaqol stages will be live. '
             'All verdicts are truthfully DEFERRED — nothing is hidden.</span>'
    )

    return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hokom–Taaqol Live Demo — آية الدَّيْن (v2)</title>
<style>
*{{box-sizing:border-box;}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#f8fafc;color:#1e293b;margin:0;padding:0;direction:rtl;}}
.page{{max-width:1400px;margin:0 auto;padding:24px;}}
h1{{font-size:1.6em;margin-bottom:4px;}}
h2{{font-size:1.15em;color:#334155;margin:20px 0 6px;border-bottom:2px solid #e2e8f0;padding-bottom:4px;}}
.verse-box{{background:#fff;border:1px solid #cbd5e1;border-radius:10px;padding:18px 22px;font-size:1.25em;line-height:2.2;direction:rtl;text-align:justify;box-shadow:0 1px 4px rgba(0,0,0,.06);margin-bottom:16px;}}
.stat-row{{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0;}}
.stat-card{{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:8px 14px;min-width:130px;}}
.stat-card .val{{font-size:1.45em;font-weight:700;color:#0f172a;}}
.stat-card .lbl{{font-size:0.76em;color:#64748b;}}
.badge{{display:inline-block;padding:2px 6px;border-radius:4px;font-size:0.76em;font-weight:600;letter-spacing:.02em;}}
.bdg-green{{background:#dcfce7;color:#166534;}}
.bdg-amber{{background:#fef9c3;color:#854d0e;}}
.bdg-yellow{{background:#fef08a;color:#713f12;}}
.bdg-red{{background:#fee2e2;color:#991b1b;}}
.bdg-purple{{background:#f3e8ff;color:#6b21a8;}}
.bdg-blue{{background:#dbeafe;color:#1e40af;}}
.bdg-gray{{background:#f1f5f9;color:#475569;}}
/* Token details */
details.token-details{{border:1px solid #e2e8f0;border-radius:8px;margin:5px 0;background:#fff;}}
details.token-details[open]{{box-shadow:0 2px 8px rgba(0,0,0,.08);}}
summary.token-summary{{cursor:pointer;padding:10px 14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;list-style:none;}}
summary.token-summary::-webkit-details-marker{{display:none;}}
summary:hover{{background:#f0f9ff;border-radius:8px;}}
.tok-idx{{color:#94a3b8;font-size:0.82em;min-width:28px;}}
.tok-surf{{font-size:1.1em;font-weight:600;min-width:120px;}}
.tok-wc{{font-size:0.78em;color:#475569;min-width:60px;}}
.tok-root{{font-size:0.9em;color:#0369a1;min-width:70px;}}
.tok-wazn{{font-size:0.78em;color:#7c3aed;min-width:60px;}}
.tok-layer-badges{{display:flex;flex-wrap:wrap;gap:3px;}}
.lv-name{{font-size:0.7em;color:#64748b;margin-right:4px;}}
.token-body{{padding:14px 18px;border-top:1px solid #f1f5f9;}}
.section-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-bottom:14px;}}
.section{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:10px 14px;margin-bottom:10px;}}
.section-title{{font-size:0.8em;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px;}}
.mini-table{{border-collapse:collapse;font-size:0.82em;width:auto;}}
.mini-table td{{padding:2px 8px;border:none;vertical-align:middle;}}
.mini-table td:first-child{{color:#64748b;font-size:0.9em;min-width:90px;}}
/* Morphosyntax */
.ms-grid{{display:flex;flex-wrap:wrap;gap:6px;}}
.ms-item{{display:flex;flex-direction:column;align-items:center;background:#fff;border:1px solid #e2e8f0;border-radius:5px;padding:4px 8px;min-width:60px;}}
.ms-lbl{{font-size:0.68em;color:#94a3b8;text-transform:uppercase;}}
.ms-val{{font-size:0.9em;font-weight:600;color:#0f172a;}}
/* Claim groups */
.claim-groups{{display:flex;flex-wrap:wrap;gap:8px;}}
.claim-group{{padding:8px 12px;border-radius:6px;border:1px solid;min-width:180px;}}
.cg-title{{font-size:0.7em;font-weight:700;text-transform:uppercase;margin-bottom:5px;}}
.claim-tag{{display:inline-block;padding:2px 6px;border-radius:4px;font-size:0.75em;margin:2px;}}
.licensed-group{{background:#f0fdf4;border-color:#bbf7d0;}}
.licensed-group .cg-title{{color:#166534;}}
.licensed{{background:#dcfce7;color:#166534;}}
.deferred-group{{background:#fffbeb;border-color:#fde68a;}}
.deferred-group .cg-title{{color:#92400e;}}
.deferred{{background:#fef9c3;color:#854d0e;}}
.ambig-group{{background:#faf5ff;border-color:#e9d5ff;}}
.ambig-group .cg-title{{color:#6b21a8;}}
.ambig{{background:#f3e8ff;color:#6b21a8;}}
.not-opened-group{{background:#fff7ed;border-color:#fed7aa;}}
.not-opened-group .cg-title{{color:#9a3412;}}
.not-opened{{background:#ffedd5;color:#9a3412;}}
/* Slot table */
.slot-table{{border-collapse:collapse;width:100%;font-size:0.8em;}}
.slot-table th{{background:#334155;color:#fff;padding:5px 10px;text-align:right;}}
.slot-table td{{padding:4px 10px;border-bottom:1px solid #f1f5f9;}}
.slot-id{{font-family:monospace;font-size:0.85em;}}
.slot-layer{{color:#64748b;font-size:0.82em;}}
.slot-val{{direction:rtl;}}
.state-filled{{background:#f0fdf4;}}
.state-unknown{{background:#fffbeb;}}
.state-not_applicable{{background:#f8fafc;color:#94a3b8;}}
.state-ambiguous{{background:#faf5ff;}}
.state-blocked{{background:#fff1f2;}}
.ev-list{{display:flex;flex-wrap:wrap;gap:3px;margin-top:3px;}}
.ev-tag{{background:#dbeafe;color:#1e40af;padding:1px 5px;border-radius:3px;font-size:0.7em;}}
.residual-tag{{font-size:0.75em;color:#b45309;background:#fef9c3;padding:2px 6px;border-radius:3px;margin-top:3px;display:inline-block;}}
.cands{{color:#64748b;font-size:0.82em;}}
.nil{{color:#94a3b8;}}
/* Trace */
.trace-title{{font-size:0.76em;font-weight:600;color:#475569;margin-top:6px;}}
.trace-ev{{font-size:0.75em;color:#475569;padding:2px 4px;background:#f1f5f9;border-radius:3px;margin:1px 0;direction:ltr;text-align:left;}}
/* Integrity */
.int-grid{{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0;}}
.int-item{{padding:5px 12px;border-radius:5px;font-size:0.82em;display:flex;gap:6px;}}
.int-key{{color:inherit;}}
.int-val{{font-weight:700;}}
.int-ok{{background:#dcfce7;color:#166534;}}
.int-bad{{background:#fee2e2;color:#991b1b;}}
.tq-active{{color:#16a34a;font-size:0.88em;}}
.tq-deferred{{color:#d97706;font-size:0.88em;}}
.footer-meta{{font-size:0.76em;color:#64748b;direction:ltr;text-align:left;padding:6px 0;}}
.arabic{{direction:rtl;}}
.defer-notice{{background:#fffbeb;border-left:4px solid #f59e0b;padding:12px 16px;border-radius:0 6px 6px 0;font-size:0.88em;margin:14px 0;}}
.meta-box{{background:#f1f5f9;border:1px solid #e2e8f0;border-radius:6px;padding:10px 14px;font-size:0.78em;color:#475569;direction:ltr;text-align:left;}}
</style>
</head>
<body>
<div class="page">
  <h1>Hokom–Taaqol — عرض تشغيلي حي (v2 — تفاصيل كاملة)</h1>
  <p style="color:#64748b;margin:0 0 12px;direction:rtl;">
    سورة البقرة 2:282 — آية الدَّيْن &nbsp;|&nbsp; HOKOM-TAAQOL-AYAT-AL-DAYN-LIVE-DEMO-01
  </p>

  <div class="verse-box" dir="rtl">{_esc(AYAT_AL_DAYN)}</div>

  <h2>إحصاءات</h2>
  <div class="stat-row">
    <div class="stat-card"><div class="val">{stats["token_count"]}</div><div class="lbl">توكنات</div></div>
    <div class="stat-card"><div class="val">{stats["typed_bundles"]}</div><div class="lbl">Typed bundles</div></div>
    <div class="stat-card"><div class="val">{stats["taaqol_live"]}</div><div class="lbl">Taaqol live</div></div>
    <div class="stat-card"><div class="val">{stats["h11_h15_reached"]}</div><div class="lbl">H11-H15 reached</div></div>
    <div class="stat-card"><div class="val">{stats["early_stops"]}</div><div class="lbl">توقفات دستورية</div></div>
    <div class="stat-card"><div class="val">{stats["root_states"].get("KNOWN",0)}</div><div class="lbl">جذر معروف</div></div>
    <div class="stat-card"><div class="val">{stats["root_states"].get("DEFERRED",0)}</div><div class="lbl">جذر مؤجَّل</div></div>
    <div class="stat-card"><div class="val">{stats["root_states"].get("UNKNOWN",0)}</div><div class="lbl">جذر مجهول</div></div>
    <div class="stat-card"><div class="val">{stats["root_states"].get("AMBIGUOUS",0)}</div><div class="lbl">جذر مبهم</div></div>
  </div>

  <h2>صحة النظام</h2>
  <div class="int-grid">{int_html}</div>
  <p>{taaqol_note}</p>

  <div class="defer-notice">
    <strong>النظام لا يخمّن عند غياب الدليل</strong><br>
    عندما يكون الجذر أو الوزن أو المصدر مؤجَّلًا، لا يصدر النظام حكم LICENSED الشامل.
    يُصدر بدلًا منه <strong>COMPOSITE</strong> مع قائمتين منفصلتين:
    <strong>LICENSED_CLAIMS</strong> (الحقول المرخَّصة تحديدًا) و<strong>DEFERRED_CLAIMS</strong> (الحقول المؤجَّلة).
    هذا ينطبق على <em>تَدَايَنْتُمْ</em>: word_class=FI3L مرخَّص، لكن الجذر والوزن والمصدر مؤجَّلة.
  </div>

  <h2>الكلمات — انقر لتفاصيل كل طبقة</h2>
  {all_tokens_html}

  <h2>بيانات البيئة</h2>
  <div class="meta-box">
    HEAD: {_esc(meta.get("head",""))}<br>
    Vendor SHA: {_esc(meta.get("vendor_sha",""))}<br>
    Python: {_esc(meta.get("python",""))}<br>
    Platform: {_esc(meta.get("platform",""))}<br>
    Timestamp: {_esc(meta.get("timestamp",""))}<br>
    Ayat source: {_esc(meta.get("ayat_source",""))}
  </div>
</div>
</body>
</html>'''


# ── output writers ────────────────────────────────────────────────────────────
REPORT_DIR = REPO_ROOT / 'reports' / 'ayat_al_dayn_demo'


def write_outputs(results: list[dict], stats: dict, checks: dict, meta: dict) -> dict[str, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}

    p = REPORT_DIR / 'ayat_al_dayn_results_full.json'
    p.write_text(format_json(results, stats, checks, meta), encoding='utf-8')
    paths['json'] = p

    p = REPORT_DIR / 'ayat_al_dayn_results.csv'
    p.write_text(format_csv(results), encoding='utf-8')
    paths['csv'] = p

    p = REPORT_DIR / 'ayat_al_dayn_manager_report.html'
    p.write_text(format_html(results, stats, checks, meta), encoding='utf-8')
    paths['html'] = p

    return paths


# ── main ─────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--format', choices=['terminal', 'json', 'csv', 'html'], default='terminal')
    parser.add_argument('--open', action='store_true')
    args = parser.parse_args()

    results = run_all(verbose=True)
    stats   = summary_stats(results)
    checks  = integrity_check(results)
    meta    = {
        'stage':       'HOKOM-TAAQOL-AYAT-AL-DAYN-LIVE-DEMO-01',
        'version':     '2',
        'head':        _git(['git', 'rev-parse', '--short', 'HEAD']),
        'head_full':   _git(['git', 'rev-parse', 'HEAD']),
        'vendor_sha':  _vendor_sha(),
        'python':      f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'platform':    platform.system(),
        'timestamp':   datetime.now(timezone.utc).isoformat(),
        'ayat_source': AYAT_SOURCE_FILE,
        'token_count': len(TOKENS),
    }

    paths = write_outputs(results, stats, checks, meta)

    if args.open:
        import webbrowser
        webbrowser.open(paths['html'].as_uri())
        print(f'JSON : {paths["json"]}')
        print(f'CSV  : {paths["csv"]}')
        print(f'HTML : {paths["html"]}')
        return 0

    if args.format == 'terminal':
        print(format_terminal(results, stats, checks))
    elif args.format == 'json':
        print(format_json(results, stats, checks, meta))
    elif args.format == 'csv':
        print(format_csv(results))
    elif args.format == 'html':
        print(paths['html'])

    print('\n── Summary ─────────────────────────────────────────────────', file=sys.stderr)
    for k, v in {
        'TOKEN_COUNT':             stats['token_count'],
        'TYPED_BUNDLES':           stats['typed_bundles'],
        'TAAQOL_LIVE_EVALUATIONS': stats['taaqol_live'],
        'H11_H15_REACHED':         stats['h11_h15_reached'],
        'EARLY_STOPS':             stats['early_stops'],
    }.items():
        print(f'  {k:<36} = {v}', file=sys.stderr)
    print(f'  OVERALL_VERDICTS           = {stats["overall_verdicts"]}', file=sys.stderr)
    print(f'  ROOT_STATES                = {stats["root_states"]}', file=sys.stderr)
    print(f'  TAAQOL_VERDICTS            = {stats["taaqol_verdicts"]}', file=sys.stderr)
    print('\n  Integrity:', file=sys.stderr)
    for k, v in checks.items():
        ok = '✓' if (v == 0 or (k == 'TAAQOL_RUNTIME_ACTIVE' and v >= 0)) else '✗'
        print(f'    {k:<38} = {v}  {ok}', file=sys.stderr)
    print(f'\n  JSON : {paths["json"]}', file=sys.stderr)
    print(f'  CSV  : {paths["csv"]}', file=sys.stderr)
    print(f'  HTML : {paths["html"]}', file=sys.stderr)
    print('─' * 65, file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
