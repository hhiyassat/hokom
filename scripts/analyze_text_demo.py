#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Run from repo root: PYTHONPATH=. python3 scripts/analyze_text_demo.py ...
"""
scripts/analyze_text_demo.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOKOM-TEXT-ROOT-DEMO-RUNNER

Thin wrapper فوق المسار الكنسي — لا يعدّل أي منطق pipeline.
يعرض تحليل كل token حتى مرحلة الجذر فقط (لا وزن، لا باب، لا مصدر، لا مشتقات).

Usage:
  python scripts/analyze_text_demo.py --text "نص عربي" [options]
  python scripts/analyze_text_demo.py --file path.txt  [options]

Options:
  --format  pretty | jsonl     (default: pretty)
  --output  PATH               (اكتب النتيجة إلى ملف بدلًا من stdout)
  --show-trace                 أظهر trace_ids و evidence_ids كاملةً
  --stop-at-root               أوقف التحليل بعد مرحلة الجذر (الوضع الافتراضي)
  --max-tokens N               حلّل أول N token فقط
"""

from __future__ import annotations

import argparse
import json
import sys
import io
import re
from pathlib import Path
from typing import Any

# ── استيراد المسار الكنسي ────────────────────────────────────────────────────
from hokom_pipeline import hokom
from mabni_layer    import MabniBoundary, MabniOpen, MabniBlocked

# ── ثوابت ────────────────────────────────────────────────────────────────────
W = 80
_PUNCT_RE = re.compile(r'^[؀-،؎-ؚ؜-؟'
                       r'ً-ٟ٠-ٯ!؟،.,:;"\'\(\)\[\]…—–]$')

# source_engine display mapping: both root engines → HOKOM_ROOT_ENGINE in output.
# Internal names (hr2s_morphology) are hidden and replaced with neutral labels.
_SE_DISPLAY = {
    'HOKOM_ROOT_ENGINE'     : 'HOKOM_ROOT_ENGINE',
    'HOKOM_AUGMENTED_ENGINE': 'HOKOM_ROOT_ENGINE',    # زيد مُوحَّد مع الأصل في الإخراج
    'HOKOM_BOUNDARY'        : 'HOKOM_BOUNDARY',
    'hr2s_morphology'       : 'EXTERNAL_ROUTE',        # ⚠ تحليل خارجي — لا يُكشف الاسم الداخلي
}
SOURCE_ENGINE_CANONICAL = frozenset({
    'HOKOM_ROOT_ENGINE', 'HOKOM_AUGMENTED_ENGINE', 'HOKOM_BOUNDARY',
})

# root_type → canonical root_class label
_ROOT_TYPE_MAP = {
    'sound'      : 'SOUND',
    'geminate'   : 'GEMINATE',
    'hamza'      : 'HAMZA',
    'assimilated': 'ASSIMILATED',
    'hollow'     : 'HOLLOW',
    'defective'  : 'DEFECTIVE',
    'lafif'      : 'LAFIF',
}

# Characters to strip from the boundaries of a whitespace-separated token
_PUNCT_STRIP = (
    '،'   # Arabic comma       U+060C
    '؛'   # Arabic semicolon   U+061B
    '؟'   # Arabic question    U+061F
    '٪٫٬٭'  # percent / decimal / thousands / five-pointed star
    '۔'   # Arabic full stop   U+06D4
    '.,:;!?\'"()[]{}…—–-'  # Latin/universal
)


# ══════════════════════════════════════════════════════════════════════════════
# 1.  تجزئة النص مع حفظ أرقام الأسطر
# ══════════════════════════════════════════════════════════════════════════════

def tokenize_with_lines(text: str) -> list[dict]:
    """
    جزّئ النص بالمسافات والترقيم فقط — لا فصل للكليتيكس.
    كَتَبَ تبقى token واحدة كاملة (لا تُقسَّم إلى كَ + تَبَ).
    """
    result      = []
    token_number = 0
    for line_no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        for raw in line.split():
            if not raw:
                continue
            # كشف الترقيم الملاصق للكلمة: اقتطعه من البداية والنهاية
            stripped   = raw.strip(_PUNCT_STRIP)
            pre_len    = len(raw) - len(raw.lstrip(_PUNCT_STRIP))
            post_start = len(raw.rstrip(_PUNCT_STRIP))
            pre        = raw[:pre_len]
            word       = raw[pre_len:post_start]
            post       = raw[post_start:]

            if word:
                for part, kind in [(pre, 'punct'), (word, 'word'), (post, 'punct')]:
                    if not part:
                        continue
                    token_number += 1
                    result.append({
                        'line_number' : line_no,
                        'token_number': token_number,
                        'surface'     : part,
                        'kind'        : kind,
                        'original'    : raw,
                    })
            else:
                # الرمز كله ترقيم
                token_number += 1
                result.append({
                    'line_number' : line_no,
                    'token_number': token_number,
                    'surface'     : raw,
                    'kind'        : 'punct',
                    'original'    : raw,
                })
    return result


# ══════════════════════════════════════════════════════════════════════════════
# 2.  استخراج حقول التقرير من نتيجة hokom()
# ══════════════════════════════════════════════════════════════════════════════

def _p5_status(r: dict) -> tuple[str, str]:
    """أعد (p5_verdict, p5_class) بناءً على نوع mabni."""
    mb = r.get('mabni')
    if isinstance(mb, MabniBoundary):
        return mb.verdict, mb.lexical_class or 'OPERATOR'
    if isinstance(mb, MabniBlocked):
        return 'BLOCK', 'BLOCKED'
    if isinstance(mb, MabniOpen):
        att = r.get('attachment')
        wv  = getattr(att, 'whole_token_verdict', 'MABNI_NOT_FOUND')
        if wv and wv not in ('MABNI_NOT_FOUND', 'OPEN_TO_HR2S'):
            return 'OPEN_MABNI', wv
        return 'OPEN', 'MORPHOLOGICALLY_OPEN'
    return 'UNKNOWN', 'UNKNOWN'


def _root_gate_status(r: dict) -> tuple[str, str]:
    """
    أعد (gate, reason):
      gate  = 'OPENED' | 'CLOSED'
      reason = سبب الإغلاق أو 'ROOT_ENGINE_INVOKED'
    """
    mb = r.get('mabni')
    if isinstance(mb, MabniBoundary):
        # Fix #2: use mb.verdict as the prefix (e.g. OPERATOR_BOUNDARY, not MABNI_BOUNDARY)
        return 'CLOSED', f'{mb.verdict}:{mb.lexical_class or "BOUNDARY"}'
    if isinstance(mb, MabniBlocked):
        return 'CLOSED', 'MABNI_BLOCKED'

    rc = r.get('root_candidate')
    if rc is None:
        pr = r.get('pre_root')
        if pr:
            directive = getattr(pr, 'root_path_directive', 'UNKNOWN')
            if directive != 'OPEN':
                return 'CLOSED', f'PRE_ROOT:{directive}'
        return 'CLOSED', 'ROOT_CANDIDATE_NONE'

    return 'OPENED', 'ROOT_ENGINE_INVOKED'


def _canonicalize_route(route: str | None) -> str | None:
    """Fix #5: map pipeline-internal route names to canonical Hokom labels."""
    if route == 'OPEN_TO_HR2S':
        return 'HOKOM_ROOT_OPEN'
    return route


def _attachment_seg(r: dict) -> dict:
    """ملخص التجزئة الإرفاقية."""
    att = r.get('attachment')
    if not att:
        return {}
    return {
        'host_surface'        : getattr(att, 'host_surface', None),
        'host_route'          : _canonicalize_route(getattr(att, 'host_route', None)),
        'whole_token_verdict' : getattr(att, 'whole_token_verdict', None),
        'segmentation_verdict': getattr(att, 'segmentation_verdict', None),
        'prefix_operators'    : [
            {
                'surface'    : getattr(p, 'surface', None) or getattr(p, 'raw', None),
                'operator_id': getattr(p, 'operator_id', None),
            }
            for p in (getattr(att, 'prefix_operators', None) or [])
        ],
        'inflectional_tail'   : getattr(att, 'inflectional_tail', None),
    }


def _extract_root_fields(r: dict, show_trace: bool) -> dict:
    """استخرج جميع حقول الجذر من نتيجة hokom()."""
    rp = r.get('root_projection')
    rc = r.get('root_candidate')
    rr = r.get('root_refinement')

    root_input_host = None
    if rr:
        root_input_host = getattr(rr, 'input_host', None)
    elif rp:
        root_input_host = getattr(rp, 'analyzed_host', None)

    if rc is None:
        return {
            'root_input_host'       : root_input_host,
            'root_directive'        : None,
            'root_stage_state'      : None,
            'root_candidates'       : [],
            'licensed_root'         : None,
            'root_class'            : None,
            'restoration_operations': [],
            'supporting_evidence'   : [],
            'contradicting_evidence': [],
            'residuals'             : [],
            'trace'                 : [] if show_trace else None,
            'source_engine'         : getattr(rp, 'source_engine', 'HOKOM_ROOT_ENGINE')
                                      if rp else 'HOKOM_ROOT_ENGINE',
        }

    profile = rc.root_profile or {}

    # Fix #3 + #5: determine raw source engine BEFORE display mapping.
    # profile['source_engine'] is more specific than rp.source_engine
    # (e.g. HOKOM_AUGMENTED_ENGINE lives only in profile for augmented forms).
    se_raw = (
        profile.get('source_engine')
        or (getattr(rp, 'source_engine', None) if rp else None)
        or 'HOKOM_ROOT_ENGINE'
    )

    # Fix #3: extract root_class from correct profile key per engine type
    # FA3IL_PARTICIPLE هو مشتق من الثلاثي المجرد (Form I) — root_class = SOUND
    # لا نُعدّه "مزيدًا" وإن مرّ عبر HOKOM_AUGMENTED_ENGINE لدواعٍ هيكلية.
    _FORM_I_DERIVATIVES = frozenset({'FA3IL_PARTICIPLE'})
    if se_raw == 'HOKOM_AUGMENTED_ENGINE':
        ff = profile.get('form_family', '')
        if ff in _FORM_I_DERIVATIVES:
            # اسم فاعل ثلاثي مجرد → root_class = SOUND (الجذر السالم بالافتراض)
            root_class = 'SOUND'
        else:
            root_class = f'AUGMENTED:{ff}' if ff else 'AUGMENTED'
    else:
        rt         = profile.get('root_type', '')
        root_class = _ROOT_TYPE_MAP.get(rt, rt.upper() if rt else None)

    # Fix #5: map to canonical display engine (HOKOM_AUGMENTED_ENGINE → HOKOM_ROOT_ENGINE)
    se           = _SE_DISPLAY.get(se_raw, se_raw)
    se_canonical = se_raw in SOURCE_ENGINE_CANONICAL

    restoration = []
    if 'restoration_operations' in profile:
        restoration = [str(op) for op in profile['restoration_operations']]

    # evidence
    ev_ids = list(getattr(rc, 'evidence_ids', ()) or ())
    if rp:
        ev_ids = list(dict.fromkeys(list(getattr(rp, 'evidence_ids', ()) or []) + ev_ids))

    # residuals
    residuals = list(getattr(rc, 'residual_codes', ()) or ())

    # licensed root
    licensed_root = None
    if rc.directive == 'ACCEPT' and rc.canonical_root:
        licensed_root = list(rc.canonical_root)

    # candidates
    candidates = []
    if rc.canonical_root:
        candidates = [list(rc.canonical_root)]
    elif residuals:
        candidates = []  # DEFER — لا نخمّن

    trace = None
    if show_trace:
        trace = list(getattr(rc, 'trace_ids', ()) or [])
        if rp:
            trace = list(dict.fromkeys(
                list(getattr(rp, 'trace_ids', ()) or []) + trace
            ))

    return {
        'root_input_host'       : root_input_host,
        'root_directive'        : rc.directive,
        'root_stage_state'      : getattr(rp, 'stage_state', None) if rp else None,
        'root_candidates'       : candidates,
        'licensed_root'         : licensed_root,
        'root_class'            : root_class,
        'restoration_operations': restoration,
        'supporting_evidence'   : ev_ids,
        'contradicting_evidence': [],
        'residuals'             : residuals,
        'trace'                 : trace,
        'source_engine'         : se,
        'source_engine_canonical': se_canonical,
    }


def _build_record(meta: dict, r: dict, show_trace: bool) -> dict:
    """ابنِ سجل JSON كامل لـ token واحد."""
    surface = meta['surface']
    kind    = meta['kind']

    # P4
    p4_verdict = r.get('verdict', 'UNKNOWN')
    slots_raw  = r.get('slots') or []
    p4_slots   = [
        {'surface': s['surface'], 'pattern': s['pattern'], 'gate': s['gate']}
        for s in slots_raw if s['surface'] != ' '
    ]

    # P1/P2/P3
    lic = r.get('licensing') or []
    p0_status  = 'ARABIC' if lic else 'NON_ARABIC_OR_PUNCT'
    p1_license = [lr['cell'] for lr in lic]
    p2_diacs   = 'LICENSED' if all(lr.get('passed', True) for lr in lic) else 'VIOLATION'
    p3_cells   = ' '.join(lr['cell'] for lr in lic) if lic else ''

    # P5
    p5_verdict, p5_class = _p5_status(r)

    # P5 attachment
    att_seg = _attachment_seg(r)

    # Root gate
    gate, gate_reason = _root_gate_status(r)

    # Root fields
    if gate == 'OPENED':
        rf = _extract_root_fields(r, show_trace)
    else:
        rf = {
            'root_input_host'       : None,
            'root_directive'        : 'ROOT_NOT_OPENED',
            'root_stage_state'      : None,
            'root_candidates'       : [],
            'licensed_root'         : None,
            'root_class'            : None,
            'restoration_operations': [],
            'supporting_evidence'   : [],
            'contradicting_evidence': [],
            'residuals'             : [gate_reason],
            'trace'                 : [] if show_trace else None,
            'source_engine'          : 'HOKOM_BOUNDARY',
            'source_engine_canonical': True,
        }

    # ── canonical SegmentBundle fields ─────────────────────────────────────────
    seg_bundle = r.get('segment_bundle')
    seg_def_art = getattr(seg_bundle, 'definite_article', None) if seg_bundle else None

    # ── canonical Taaqol fields ──────────────────────────────────────────────
    taaqol_decision = r.get('taaqol_decision')
    taaqol_reason_codes = list(
        getattr(taaqol_decision, 'reason_codes', ()) or ()
    ) if taaqol_decision else []

    rec: dict[str, Any] = {
        'line_number'            : meta['line_number'],
        'token_number'           : meta['token_number'],
        'input_surface'          : surface,
        # Fix #4: user-visible form (unchanged) vs internal pipeline form
        'normalized_surface'     : surface,
        'analysis_surface'       : r.get('normalized_surface', surface),
        'P0_unicode_status'      : p0_status,
        'P1_character_license'   : p1_license,
        'P2_diacritic_status'    : p2_diacs,
        'P3_cells'               : p3_cells,
        'P4_structural_verdict'  : p4_verdict,
        'P4_slots'               : p4_slots,
        'P5_lexical_verdict'     : p5_verdict,
        'P5_lexical_class'       : p5_class,
        'P5_attachment_segmentation': att_seg,
        'P5_root_gate'           : gate,
        'P5_root_gate_reason'    : gate_reason,
        # ── SegmentBundle / canonical segmentation ──────────────────────────
        'segment_proclitics'      : list(r.get('segment_proclitics') or ()),
        'segment_definite_article': seg_def_art,
        'segment_host'            : r.get('segment_host'),
        'segment_enclitics'       : list(r.get('segment_enclitics') or ()),
        'segment_clitic_only'     : r.get('segment_clitic_only', False),
        'morphology_surface'      : r.get('morphology_surface'),
        'morphology_blocked'      : r.get('morphology_blocked', False),
        'morphology_block_reason' : r.get('morphology_block_reason'),
        # ── Taaqol integration ───────────────────────────────────────────────
        'taaqol_center_scope'     : r.get('taaqol_center_scope'),
        'taaqol_verdict'          : getattr(taaqol_decision, 'taaqol_verdict', None)
                                    if taaqol_decision else None,
        'taaqol_effective_verdict': r.get('taaqol_effective_verdict'),
        'taaqol_reason_codes'     : taaqol_reason_codes,
        **{f'root_{k}' if not k.startswith('root_') else k: v
           for k, v in rf.items()},
    }

    return rec


# ══════════════════════════════════════════════════════════════════════════════
# 3.  عرض pretty
# ══════════════════════════════════════════════════════════════════════════════

_DIR_ICON = {'ACCEPT': '✓', 'DEFER': '◌', 'BLOCK': '✗',
             'ROOT_NOT_OPENED': '—', None: '?'}


def _pretty_record(rec: dict, show_trace: bool, out: io.TextIOBase):
    w = out.write
    def p(line=''):
        w(line + '\n')

    gate   = rec['P5_root_gate']
    p()
    p('─' * W)
    p(f"  [{rec['line_number']:02d}:{rec['token_number']:03d}]  "
      f"surface: {rec['input_surface']!r:30s}  "
      f"P4: {rec['P4_structural_verdict']:<8s}  "
      f"gate: {'⚡ OPENED' if gate=='OPENED' else '✗ CLOSED'}")
    p(f"  normalized      : {rec['normalized_surface']!r}")
    p(f"  P0_unicode      : {rec['P0_unicode_status']}")
    p(f"  P1_license      : {' '.join(rec['P1_character_license'])}")
    p(f"  P2_diacs        : {rec['P2_diacritic_status']}")
    p(f"  P3_cells        : {rec['P3_cells']}")
    slots_str = '  '.join(f"{s['surface']}({s['pattern']})" for s in rec['P4_slots'])
    p(f"  P4_slots        : {slots_str or '—'}")
    p(f"  P5_verdict      : {rec['P5_lexical_verdict']}")
    p(f"  P5_class        : {rec['P5_lexical_class']}")

    # ── [Segmentation] ───────────────────────────────────────────────────────
    p(f"  ── [Segmentation] ─────────────────────────────────────────────────")
    proc_display = '(' + ', '.join(rec['segment_proclitics']) + ')' \
                   if rec['segment_proclitics'] else '—'
    enc_display  = '(' + ', '.join(rec['segment_enclitics']) + ')' \
                   if rec['segment_enclitics'] else '—'
    art_display  = rec['segment_definite_article'] or '—'
    host_display = rec['segment_host'] if rec['segment_host'] is not None else 'None  ← clitic-only'
    p(f"  original_surface   : {rec['input_surface']}")
    p(f"  proclitics         : {proc_display}")
    p(f"  definite_article   : {art_display}")
    p(f"  host               : {host_display}")
    p(f"  enclitics          : {enc_display}")
    p(f"  clitic_only        : {rec['segment_clitic_only']}")
    p(f"  morphology_surface : {rec['morphology_surface']!r}")
    p(f"  morphology_blocked : {rec['morphology_blocked']}")
    if rec['morphology_block_reason']:
        p(f"  block_reason       : {rec['morphology_block_reason']}")

    # ── [Taaqol Integration] ─────────────────────────────────────────────────
    p(f"  ── [Taaqol Integration] ────────────────────────────────────────────")
    p(f"  center_scope       : {rec['taaqol_center_scope']!r}")
    taaqol_v   = rec['taaqol_verdict'] or '—'
    effective_v = rec['taaqol_effective_verdict'] or '—'
    reason_str  = ', '.join(rec['taaqol_reason_codes']) if rec['taaqol_reason_codes'] else ''
    taaqol_v_display = f"{taaqol_v} ({reason_str})" if reason_str else taaqol_v
    p(f"  verdict            : {taaqol_v_display}")
    p(f"  effective_verdict  : {effective_v}")

    # ── P5 attachment (legacy — operates on morphology_surface) ──────────────
    att = rec['P5_attachment_segmentation']
    seg_host    = rec['segment_host']
    input_surf  = rec['input_surface']
    morph_surf  = rec['morphology_surface']
    if att:
        morph_note = morph_surf or '—'
        p(f"  ── [Morphology — operates on: {morph_note}] ─────────────────────")
        att_host = att.get('host_surface')
        # Gate: suppress P5_host when it echoes the full token but segment_host differs
        _host_is_full_token = (att_host == input_surf and seg_host and seg_host != input_surf)
        if not _host_is_full_token and att_host:
            p(f"  P5_host         : {att_host!r}  route={att.get('host_route')}")
        if att.get('prefix_operators'):
            pfxs = [pfx for pfx in att['prefix_operators'] if pfx.get('surface')]
            for pfx in pfxs:
                p(f"  P5_prefix       : {pfx['surface']!r}  id={pfx.get('operator_id')}")
        if att.get('inflectional_tail'):
            p(f"  P5_tail         : {att['inflectional_tail']!r}")

    if gate == 'CLOSED':
        p(f"  ROOT_NOT_OPENED : {rec['P5_root_gate_reason']}")
        return

    # Root opened — all morphological stages operate on morphology_surface
    direc = rec.get('root_directive') or rec.get('root_root_directive')
    stage = rec.get('root_stage_state') or rec.get('root_root_stage_state')
    host  = rec.get('root_input_host') or rec.get('root_root_input_host')
    icon  = _DIR_ICON.get(direc, '?')
    morph_surface = morph_surf or '—'
    p(f"  ── [Root — operates on: {morph_surface}] ────────────────────────────")
    # Gate: suppress root_host when it echoes the full token but segment_host differs
    _root_host_is_full_token = (host == input_surf and seg_host and seg_host != input_surf)
    if not _root_host_is_full_token:
        p(f"  root_host       : {host!r}")
    p(f"  root_stage      : {stage}")
    p(f"  root_directive  : {icon} {direc}")

    lroot = rec.get('licensed_root') or rec.get('root_licensed_root')
    rclass = rec.get('root_class') or rec.get('root_root_class')
    resids = rec.get('residuals') or rec.get('root_residuals') or []
    evids  = rec.get('supporting_evidence') or rec.get('root_supporting_evidence') or []
    restor = rec.get('restoration_operations') or rec.get('root_restoration_operations') or []

    if direc == 'ACCEPT' and lroot:
        p(f"  licensed_root   : ({'، '.join(lroot)})")
        p(f"  root_class      : {rclass}")
        if restor:
            p(f"  restoration     : {', '.join(restor)}")
    else:
        cands = rec.get('root_candidates') or rec.get('root_root_candidates') or []
        if cands:
            p(f"  candidates      : {cands}")
        p(f"  residuals       : {resids or '—'}")

    if evids and show_trace:
        p(f"  evidence        : {evids}")
    trace = rec.get('trace') or rec.get('root_trace') or []
    if trace and show_trace:
        p(f"  trace           : {trace}")

    se           = rec.get('source_engine') or rec.get('root_source_engine')
    se_canonical = rec.get('source_engine_canonical', True)
    se_note      = '' if se_canonical else '  ⚠ non-canonical'
    p(f"  source_engine   : {se}{se_note}")


def _pretty_summary(stats: dict, out: io.TextIOBase):
    p = lambda line='': out.write(line + '\n')
    p()
    p('═' * W)
    p('  SUMMARY')
    p('─' * W)
    for k, v in stats.items():
        p(f"  {k:<30}: {v}")
    p('═' * W)


# ══════════════════════════════════════════════════════════════════════════════
# 4.  الحلقة الرئيسية
# ══════════════════════════════════════════════════════════════════════════════

def run_demo(
    text       : str,
    fmt        : str   = 'pretty',
    show_trace : bool  = False,
    max_tokens : int   = 0,
    out        : io.TextIOBase = sys.stdout,
):
    """شغّل المحلل على النص وأخرج النتيجة."""
    all_tokens  = tokenize_with_lines(text)
    word_tokens = [t for t in all_tokens if t['kind'] in ('word', 'clitic')]

    if max_tokens:
        word_tokens = word_tokens[:max_tokens]

    stats = {
        'TOTAL_TOKENS'         : len(word_tokens),
        'PUNCT_SKIPPED'        : sum(1 for t in all_tokens if t['kind'] == 'punct'),
        # Fix #6: separate P5 gate buckets
        'P5_OPERATOR_BOUNDARY' : 0,   # مبني مشغّل (هَلْ، مِنْ، لَمْ …)
        'P5_MABNI_BOUNDARY'    : 0,   # مبني حدّي آخر
        'P5_BLOCKED'           : 0,   # محجوب (MabniBlocked)
        'P5_OPEN'              : 0,   # مفتوح للجذر
        'ROOT_OPENED'          : 0,
        'ROOT_ACCEPTED'        : 0,
        'ROOT_DEFERRED'        : 0,
        'ROOT_BLOCKED'         : 0,
        'ROOT_RESIDUAL'        : 0,
        'UNHANDLED_ERRORS'     : 0,
    }

    if fmt == 'pretty':
        out.write('\n' + '═' * W + '\n')
        out.write('  Hokom Pipeline  |  خط أنابيب الحكم\n')
        out.write('  token → normalize → license → cell → slot → gate → root\n')
        out.write('═' * W + '\n')

    records = []
    for meta in word_tokens:
        try:
            r   = hokom(meta['surface'])
            rec = _build_record(meta, r, show_trace)
        except Exception as exc:
            stats['UNHANDLED_ERRORS'] += 1
            rec = {
                'line_number'   : meta['line_number'],
                'token_number'  : meta['token_number'],
                'input_surface' : meta['surface'],
                'ERROR'         : str(exc),
            }
            if fmt == 'pretty':
                out.write(f"\n  ⚠ ERROR [{meta['surface']!r}]: {exc}\n")
            else:
                out.write(json.dumps(rec, ensure_ascii=False) + '\n')
            continue

        # --- stats ---
        gate   = rec['P5_root_gate']
        reason = rec['P5_root_gate_reason']
        rd     = rec.get('root_directive') or rec.get('root_root_directive')

        if gate == 'CLOSED':
            # Fix #6: split closed-gate bucket by verdict type
            if reason.startswith('OPERATOR_BOUNDARY'):
                stats['P5_OPERATOR_BOUNDARY'] += 1
            elif reason.startswith('MABNI_BLOCKED'):
                stats['P5_BLOCKED'] += 1
            else:
                stats['P5_MABNI_BOUNDARY'] += 1
        else:
            stats['P5_OPEN']      += 1
            stats['ROOT_OPENED']  += 1
            if rd == 'ACCEPT':
                stats['ROOT_ACCEPTED'] += 1
            elif rd == 'DEFER':
                stats['ROOT_DEFERRED'] += 1
                resids = rec.get('residuals') or rec.get('root_residuals') or []
                if resids:
                    stats['ROOT_RESIDUAL'] += len(resids)
            elif rd == 'BLOCK':
                stats['ROOT_BLOCKED'] += 1

        # --- output ---
        if fmt == 'pretty':
            _pretty_record(rec, show_trace, out)
        else:
            records.append(rec)
            out.write(json.dumps(rec, ensure_ascii=False) + '\n')

    if fmt == 'pretty':
        _pretty_summary(stats, out)
    else:
        summary_rec = {'record_type': 'SUMMARY', **stats}
        out.write(json.dumps(summary_rec, ensure_ascii=False) + '\n')

    return stats


# ══════════════════════════════════════════════════════════════════════════════
# 5.  CLI
# ══════════════════════════════════════════════════════════════════════════════

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog='analyze_text_demo',
        description='HOKOM-TEXT-ROOT-DEMO-RUNNER — thin wrapper فوق المسار الكنسي',
    )
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument('--text', metavar='TEXT',
                     help='نص عربي مباشر بين علامتَي اقتباس')
    grp.add_argument('--file', metavar='PATH',
                     help='مسار ملف نصي (UTF-8)')
    p.add_argument('--format', choices=['pretty', 'jsonl'], default='pretty',
                   dest='fmt', help='صيغة الإخراج (default: pretty)')
    p.add_argument('--output', metavar='PATH',
                   help='احفظ النتيجة في ملف بدلًا من stdout')
    p.add_argument('--show-trace', action='store_true',
                   help='أظهر trace_ids و evidence_ids')
    p.add_argument('--stop-at-root', action='store_true', default=True,
                   help='أوقف عند الجذر — الوضع الافتراضي دائمًا')
    p.add_argument('--max-tokens', type=int, default=0, metavar='N',
                   help='حلّل أول N token فقط (0 = لا حد)')
    # ── masdar flags ──────────────────────────────────────────────────────────
    p.add_argument('--stop-at-masdar', action='store_true', default=False,
                   help='بعد عرض حقول الجذر/الوزن، أضف تحليل المصدر عبر HOKOM_MASDAR_ENGINE')
    p.add_argument('--masdar-mode', choices=['generate', 'recognize'], default='generate',
                   dest='masdar_mode',
                   help='وضع محرك المصدر: generate=إنتاج | recognize=تحقق (default: generate)')
    p.add_argument('--masdar-type',
                   choices=['asli', 'mimi', 'marra', 'hayaa', 'ism_masdar', 'auto'],
                   default='auto', dest='masdar_type',
                   help='نوع المصدر المطلوب (default: auto)')
    # ── derivatives flags ─────────────────────────────────────────────────────
    p.add_argument('--stop-at-derivatives', action='store_true', default=False,
                   help='بعد عرض حقول الجذر/الوزن/المصدر، أضف تحليل المشتقات عبر HOKOM_DERIVATIVES_ENGINE')
    p.add_argument('--derivative-type',
                   choices=['ism_fa3il', 'ism_maf3ul', 'sifa', 'mubalgha',
                            'ism_zaman', 'ism_makan', 'ism_ala', 'auto'],
                   default='auto', dest='derivative_type',
                   help='نوع المشتق المطلوب (default: auto)')
    return p


def _print_masdar_section(r: dict, masdar_mode: str, masdar_type: str, out: io.TextIOBase):
    """
    Print masdar analysis for a single token result using HOKOM_MASDAR_ENGINE.
    Called only when --stop-at-masdar is set and the root gate is OPENED with ACCEPT.
    """
    try:
        from pipeline.p5_masdar.engine import analyze_masdar
        from pipeline.p5_masdar.models import MasdarRequest
    except ImportError as e:
        out.write(f'  masdar_gate     : CLOSED (import error: {e})\n')
        return

    rc  = r.get('root_candidate')
    p4a = r.get('phase4a_result')
    aug = r.get('augmented_analysis')

    # Determine licensed root
    prc = getattr(p4a, 'promoted_root_candidate', None) if p4a else None
    if prc is not None:
        licensed_root = tuple(getattr(prc, 'canonical_root', ()) or ())
    elif rc is not None:
        licensed_root = tuple(getattr(rc, 'canonical_root', ()) or ())
    else:
        out.write('  masdar_gate     : CLOSED (no licensed root)\n')
        return

    if not licensed_root:
        out.write('  masdar_gate     : CLOSED (empty root)\n')
        return

    # Determine form_family and pattern
    form_family  = getattr(aug, 'form_family', None) if aug else None
    final_wazn   = getattr(p4a, 'final_wazn', None) if p4a else None
    verbal_host  = r.get('normalized_surface') or r.get('original')

    # Map CLI masdar_type to MASDAR_TYPE
    _TYPE_MAP = {
        'asli'      : 'MASDAR_ASLI',
        'mimi'      : 'MASDAR_MIMI',
        'marra'     : 'MASDAR_MARRA',
        'hayaa'     : 'MASDAR_HAYAA',
        'ism_masdar': 'ISM_MASDAR',
        'auto'      : None,
    }
    req_masdar_type = _TYPE_MAP.get(masdar_type)

    # Map CLI masdar_mode to engine mode
    _MODE_MAP = {
        'generate'  : 'GENERATE_FROM_VERB',
        'recognize' : 'VALIDATE_SUPPLIED_MASDAR',
    }
    engine_mode = _MODE_MAP.get(masdar_mode, 'GENERATE_FROM_VERB')

    masdar_req = MasdarRequest(
        request_id=f'DEMO-{verbal_host}',
        mode=engine_mode,
        original_surface=verbal_host or '',
        normalized_surface=verbal_host or '',
        verbal_host=verbal_host,
        verbal_lemma=None,
        licensed_root=licensed_root,
        licensed_root_class=None,
        licensed_pattern=final_wazn,
        verb_form_family=form_family,
        voice=None,
        available_context=(),
        requested_masdar_type=req_masdar_type,
        supplied_masdar_surface=None,
        evidence=(),
        upstream_trace=(),
    )

    try:
        masdar_result = analyze_masdar(masdar_req)
    except Exception as exc:
        out.write(f'  masdar_gate     : ERROR ({exc})\n')
        return

    verdict   = masdar_result.verdict
    n_cands   = len(masdar_result.licensed_masdars)
    surfaces  = [lm.candidate.surface for lm in masdar_result.licensed_masdars
                 if lm.candidate.surface]
    patterns  = list(dict.fromkeys(
        lm.candidate.canonical_pattern for lm in masdar_result.licensed_masdars
    ))
    reasons   = []
    if masdar_result.deferred:
        reasons.append(masdar_result.deferred.reason)
    if masdar_result.blocked:
        reasons.append(masdar_result.blocked.reason)
    for res in masdar_result.residuals:
        reasons.append(res.residual_code)

    out.write('  ── masdar ─────────────────────────────────────────────────\n')
    out.write(f'  masdar_gate     : OPEN\n')
    out.write(f'  masdar_mode     : {masdar_mode}\n')
    out.write(f'  masdar_verdict  : {verdict}\n')
    out.write(f'  masdar_candidates: {n_cands}\n')
    if surfaces:
        out.write(f'  licensed_masdars: {surfaces}\n')
    if patterns:
        out.write(f'  masdar_patterns : {patterns}\n')
    if reasons:
        out.write(f'  masdar_reason_codes: {reasons}\n')
    out.write(f'  source_engine   : {masdar_result.source_engine}\n')


def _print_derivatives_section(r: dict, derivative_type: str, out: io.TextIOBase):
    """
    Print derivatives analysis for a single token result using HOKOM_DERIVATIVES_ENGINE.
    Called only when --stop-at-derivatives is set and the root gate is OPENED with ACCEPT.
    """
    try:
        from pipeline.p6_derivatives.engine import analyze_derivative
        from pipeline.p6_derivatives.models import DerivativeRequest
    except ImportError as e:
        out.write(f'  derivative_gate : CLOSED (import error: {e})\n')
        return

    rc  = r.get('root_candidate')
    p4a = r.get('phase4a_result')
    aug = r.get('augmented_analysis')

    # Determine licensed root
    prc = getattr(p4a, 'promoted_root_candidate', None) if p4a else None
    if prc is not None:
        licensed_root = tuple(getattr(prc, 'canonical_root', ()) or ())
    elif rc is not None:
        licensed_root = tuple(getattr(rc, 'canonical_root', ()) or ())
    else:
        out.write('  derivative_gate : CLOSED (no licensed root)\n')
        return

    if not licensed_root:
        out.write('  derivative_gate : CLOSED (empty root)\n')
        return

    # Determine form_family and pattern
    form_family  = getattr(aug, 'form_family', None) if aug else None
    final_wazn   = getattr(p4a, 'final_wazn', None) if p4a else None
    verbal_host  = r.get('normalized_surface') or r.get('original')

    # Map CLI derivative_type to DERIVATIVE_TYPE
    _DTYPE_MAP = {
        'ism_fa3il'  : 'ISM_FA3IL',
        'ism_maf3ul' : 'ISM_MAF3UL',
        'sifa'       : 'SIFA_MUSHABBAHA',
        'mubalgha'   : 'MUBALGHA',
        'ism_zaman'  : 'ISM_ZAMAN',
        'ism_makan'  : 'ISM_MAKAN',
        'ism_ala'    : 'ISM_ALA',
        'auto'       : None,
    }
    req_derivative_type = _DTYPE_MAP.get(derivative_type)

    deriv_req = DerivativeRequest(
        request_id=f'DEMO-DERIV-{verbal_host}',
        mode='GENERATE_FROM_VERB',
        original_surface=verbal_host or '',
        normalized_surface=verbal_host or '',
        verbal_host=verbal_host,
        verbal_lemma=None,
        licensed_root=licensed_root,
        licensed_root_class=None,
        licensed_pattern=final_wazn,
        verb_form_family=form_family,
        voice=None,
        available_context=(),
        derivative_type=req_derivative_type,
        supplied_derivative_surface=None,
        evidence=(),
        upstream_trace=(),
    )

    try:
        deriv_result = analyze_derivative(deriv_req)
    except Exception as exc:
        out.write(f'  derivative_gate : ERROR ({exc})\n')
        return

    verdict   = deriv_result.verdict
    n_cands   = len(deriv_result.licensed_derivatives)
    surfaces  = [ld.candidate.surface for ld in deriv_result.licensed_derivatives
                 if ld.candidate.surface]
    patterns  = list(dict.fromkeys(
        ld.candidate.canonical_pattern for ld in deriv_result.licensed_derivatives
    ))
    dtypes    = list(dict.fromkeys(
        ld.candidate.derivative_type for ld in deriv_result.licensed_derivatives
    ))
    reasons   = []
    if deriv_result.deferred:
        reasons.append(deriv_result.deferred.reason)
    if deriv_result.blocked:
        reasons.append(deriv_result.blocked.reason)
    for res in deriv_result.residuals:
        reasons.append(res.residual_code)

    out.write('  ── derivatives ────────────────────────────────────────────\n')
    out.write(f'  derivative_gate      : OPEN\n')
    out.write(f'  derivative_type_req  : {derivative_type}\n')
    out.write(f'  derivative_verdict   : {verdict}\n')
    out.write(f'  derivative_candidates: {n_cands}\n')
    if dtypes:
        out.write(f'  derivative_types     : {dtypes}\n')
    if surfaces:
        out.write(f'  licensed_derivatives : {surfaces}\n')
    if patterns:
        out.write(f'  derivative_patterns  : {patterns}\n')
    if reasons:
        out.write(f'  derivative_reason_codes: {reasons}\n')
    out.write(f'  source_engine        : {deriv_result.source_engine}\n')


def main():
    parser = _build_parser()
    args   = parser.parse_args()

    # --- نص المدخل ---
    if args.text:
        text = args.text
    else:
        path = Path(args.file)
        if not path.exists():
            print(f'⚠ الملف غير موجود: {args.file}', file=sys.stderr)
            sys.exit(1)
        text = path.read_text(encoding='utf-8')

    # --- مخرج ---
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_f = out_path.open('w', encoding='utf-8')
    else:
        out_f = sys.stdout

    stop_at_masdar       = getattr(args, 'stop_at_masdar', False)
    masdar_mode          = getattr(args, 'masdar_mode', 'generate')
    masdar_type          = getattr(args, 'masdar_type', 'auto')
    stop_at_derivatives  = getattr(args, 'stop_at_derivatives', False)
    derivative_type      = getattr(args, 'derivative_type', 'auto')

    try:
        if stop_at_derivatives:
            # Run pipeline and inject derivative output after each accepted token
            all_tokens  = tokenize_with_lines(text)
            word_tokens = [t for t in all_tokens if t['kind'] in ('word', 'clitic')]
            if args.max_tokens:
                word_tokens = word_tokens[:args.max_tokens]
            for meta in word_tokens:
                try:
                    r   = hokom(meta['surface'])
                    rec = _build_record(meta, r, args.show_trace)
                except Exception as exc:
                    out_f.write(f'\n  ERROR [{meta["surface"]!r}]: {exc}\n')
                    continue
                if args.fmt == 'pretty':
                    _pretty_record(rec, args.show_trace, out_f)
                    gate = rec.get('P5_root_gate', 'CLOSED')
                    rd   = rec.get('root_directive') or rec.get('root_root_directive')
                    if gate == 'OPENED' and rd == 'ACCEPT':
                        _print_derivatives_section(r, derivative_type, out_f)
                else:
                    gate = rec.get('P5_root_gate', 'CLOSED')
                    rd   = rec.get('root_directive') or rec.get('root_root_directive')
                    if gate == 'OPENED' and rd == 'ACCEPT':
                        import io as _io
                        _buf = _io.StringIO()
                        _print_derivatives_section(r, derivative_type, _buf)
                        rec['derivatives_section'] = _buf.getvalue()
                    import json as _json
                    out_f.write(_json.dumps(rec, ensure_ascii=False) + '\n')
        elif stop_at_masdar:
            # Run pipeline and inject masdar output after each accepted token
            all_tokens  = tokenize_with_lines(text)
            word_tokens = [t for t in all_tokens if t['kind'] in ('word', 'clitic')]
            if args.max_tokens:
                word_tokens = word_tokens[:args.max_tokens]
            for meta in word_tokens:
                try:
                    r   = hokom(meta['surface'])
                    rec = _build_record(meta, r, args.show_trace)
                except Exception as exc:
                    out_f.write(f'\n  ERROR [{meta["surface"]!r}]: {exc}\n')
                    continue
                if args.fmt == 'pretty':
                    _pretty_record(rec, args.show_trace, out_f)
                    gate = rec.get('P5_root_gate', 'CLOSED')
                    rd   = rec.get('root_directive') or rec.get('root_root_directive')
                    if gate == 'OPENED' and rd == 'ACCEPT':
                        _print_masdar_section(r, masdar_mode, masdar_type, out_f)
                else:
                    gate = rec.get('P5_root_gate', 'CLOSED')
                    rd   = rec.get('root_directive') or rec.get('root_root_directive')
                    if gate == 'OPENED' and rd == 'ACCEPT':
                        from pipeline.p5_masdar.engine import analyze_masdar
                        from pipeline.p5_masdar.models import MasdarRequest
                        # inject masdar fields into JSONL record inline
                        import io as _io
                        _buf = _io.StringIO()
                        _print_masdar_section(r, masdar_mode, masdar_type, _buf)
                        rec['masdar_section'] = _buf.getvalue()
                    import json as _json
                    out_f.write(_json.dumps(rec, ensure_ascii=False) + '\n')
        else:
            run_demo(
                text       = text,
                fmt        = args.fmt,
                show_trace = args.show_trace,
                max_tokens = args.max_tokens,
                out        = out_f,
            )
    finally:
        if args.output:
            out_f.close()
            print(f'✓ محفوظ في: {args.output}')


if __name__ == '__main__':
    main()
