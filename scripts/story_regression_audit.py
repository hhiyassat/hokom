#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/story_regression_audit.py
══════════════════════════════════
تشخيص شامل لنص قصة المبنيات — قراءة فقط، لا تعديل للكود.

المخرجات:
  reports/mabniyat/mabniyat_story_regression_report.txt
  reports/mabniyat/mabniyat_story_regression_results.jsonl
"""

import json
import os
import re
import sys
import unicodedata

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOKOM_DIR  = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, HOKOM_DIR)
os.chdir(HOKOM_DIR)

from hokom_pipeline import hokom
from mabni_layer    import MabniBoundary, MabniOpen, MabniBlocked
from mabniyat_attachment import TokenAnalysis

# ─────────────────────────────────────────────────────────────────────────────
# Fixture
# ─────────────────────────────────────────────────────────────────────────────

FIXTURE_PATH = 'tests/fixtures/mabniyat_story_regression.txt'
REPORT_PATH  = 'reports/mabniyat/mabniyat_story_regression_report.txt'
JSONL_PATH   = 'reports/mabniyat/mabniyat_story_regression_results.jsonl'

# ─────────────────────────────────────────────────────────────────────────────
# Classification helpers
# ─────────────────────────────────────────────────────────────────────────────

DIACRITICS = re.compile(r'[ً-ْٰـ]')

def bare(s: str) -> str:
    return DIACRITICS.sub('', s)

def _att_ids(att):
    if att is None:
        return []
    return [sp.mabni_id for sp in att.attached_mabniyat]

def _prefix_ids(att):
    if att is None:
        return []
    return [sp.mabni_id for sp in att.prefix_operators]

TA_MARBUTA = 'ة'

def has_ta_marbuta(surface: str) -> bool:
    return TA_MARBUTA in surface

KNOWN_INFLECTIONAL_ENDINGS = {
    'ينَ': 'جمع المذكر السالم (مجرور/منصوب)',
    'ونَ': 'جمع المذكر السالم (مرفوع)',
    'اتُ': 'جمع المؤنث السالم (مرفوع)',
    'اتِ': 'جمع المؤنث السالم (مجرور)',
    'اتَ': 'جمع المؤنث السالم (منصوب)',
}

# ─────────────────────────────────────────────────────────────────────────────
# Critical cases table
# ─────────────────────────────────────────────────────────────────────────────

CRITICAL_SURFACES = {
    # false prefix scan
    'وَحْدَهُمْ', 'وَحْدَهَا',
    # inflection/mabni confusion
    'نَائِمِينَ', 'الْمَسَاكِينَ', 'يَسْتَطِيعُونَ', 'الْحَيَوَانَاتُ',
    # false suffix scan
    'حِينَمَا',
    # operator + pronoun
    'أَنَّهُمْ',
    # prep + pronoun
    'بِهِمْ', 'بِهَا',
    # unlicensed slot check
    'الدِّفَاعَ',
}

REGRESSION_CORRECT = {
    # surface → expected suffix mabni_ids (subset check — any() match).
    # IDs match the actual catalog entries in mabniyat_catalog_split_vocalized.csv:
    #   هُمْ → ATTACHED_PRONOUN_HUM_SUFFIX  (surface 'هُمْ')
    #   هِمْ → ATTACHED_PRONOUN_HIM         (surface 'هِمْ', after kasra/ya)
    #   هَا  → ATTACHED_PRONOUN_HA_FEM      (surface 'هَا')
    #   هُ   → ATTACHED_PRONOUN_HA          (surface 'هُ', masc sg)
    'يُعَوِّضَهُمْ':   ['ATTACHED_PRONOUN_HUM_SUFFIX'],
    # فَقَدُوهُ: connected-waw + هُ (they-lost-him); deeper analysis is correct.
    # Check for هُ (ATTACHED_PRONOUN_HA) being present — WAW is also accepted.
    'فَقَدُوهُ':       ['ATTACHED_PRONOUN_HA'],
    'أُمِّهِمْ':       ['ATTACHED_PRONOUN_HIM'],
    'حُبِّهَا':        ['ATTACHED_PRONOUN_HA_FEM'],
    'نَوْمِهِمْ':      ['ATTACHED_PRONOUN_HIM'],
    'تَرَكَتْهُمْ':    ['ATTACHED_PRONOUN_HUM_SUFFIX'],
    'تَقْتُلَهُمْ':    ['ATTACHED_PRONOUN_HUM_SUFFIX'],
    'أَنْفُسِهِمْ':    ['ATTACHED_PRONOUN_HIM'],
    'مَعَهُمْ':        ['ATTACHED_PRONOUN_HUM_SUFFIX'],
    'يَحْرُسَهُمْ':    ['ATTACHED_PRONOUN_HUM_SUFFIX'],
    'رُجُوعِهَا':      ['ATTACHED_PRONOUN_HA_FEM'],
    'يَرَهَا':         ['ATTACHED_PRONOUN_HA_FEM'],
}

OPERATORS_EXPECTED = {
    'أَنْ', 'مِنْ', 'وَ', 'حَتَّى', 'لَا', 'عَنْ', 'لَيْسَ', 'مَنْ',
    'لَمْ', 'إِلَى', 'بِ', 'لِ',
}

# ─────────────────────────────────────────────────────────────────────────────
# Token classifier
# ─────────────────────────────────────────────────────────────────────────────

def classify_token(surface: str, r: dict) -> dict:
    """
    Run full classification on a pipeline result dict.
    Returns a classification dict with all required fields.
    """
    mb  = r.get('mabni')
    att = r.get('attachment')
    v4  = r.get('verdict', 'ACCEPT')

    # Basic fields
    p4_verdicts    = [s.get('verdict', '?') for s in r.get('slots', [])]
    structural_v4  = v4
    op_lookup      = isinstance(mb, MabniBoundary)
    mabni_lookup   = (att is not None and isinstance(mb, MabniOpen) and
                      att.segmentation_verdict == 'NOT_SEGMENTED' and
                      att.host_route == 'MABNI_BOUNDARY') if att else False

    prefixes  = _prefix_ids(att)
    suffixes  = _att_ids(att)
    host      = att.host_surface if att else surface
    host_route = att.host_route if att else ('OPERATOR_BOUNDARY' if op_lookup else
                                              ('BLOCKED' if v4 == 'BLOCK' else 'OPEN_TO_HR2S'))
    seg       = att.segmentation_verdict if att else None

    # Token verdict
    if v4 == 'BLOCK':
        token_verdict = 'BLOCKED'
    elif op_lookup:
        token_verdict = 'OPERATOR_BOUNDARY'
    elif att is None:
        token_verdict = 'OPEN_TO_HR2S'
    elif seg == 'NOT_SEGMENTED' and host_route == 'MABNI_BOUNDARY':
        token_verdict = 'MABNI_BOUNDARY'
    elif seg == 'SEGMENTED' and host_route == 'EMPTY':
        token_verdict = 'COMPOSITE_CLOSED'
    elif seg == 'SEGMENTED':
        token_verdict = 'COMPOSITE_BOUNDARY'
    elif seg == 'AMBIGUOUS':
        token_verdict = 'AMBIGUOUS'
    else:
        token_verdict = 'OPEN_TO_HR2S'

    # ── Anomaly detection ──────────────────────────────────────────────────

    anomalies = []

    # 1. FALSE_PREFIX_SCAN — وَحْد split
    if att and prefixes:
        for pfx in (att.prefix_operators or []):
            # check if host starts with sukun (سكون) → synthetic bad host
            h = att.host_surface or ''
            bare_h = bare(h)
            if bare_h and unicodedata.category(h[0]) != 'Lo':
                pass
            # وَ operator prefix extracted from وَحْد-family words
            if pfx.mabni_id in ('WA_PREP', 'WA_ATF') and bare(surface).startswith('وحد'):
                anomalies.append({
                    'code': 'FALSE_PREFIX_SCAN',
                    'detail': f'واو حرف عطف استُخلص خطأً من وَحْد — المضيف المصطنع: {h!r}',
                })

    # Check for synthetic host starting with sukun
    if att and att.host_surface:
        h = att.host_surface
        # NFC + check first diacritic = sukun
        nfc = unicodedata.normalize('NFC', h)
        pairs = []
        cur_base = None
        cur_diacs = []
        for ch in nfc:
            if unicodedata.category(ch).startswith('M'):
                if cur_base: cur_diacs.append(ch)
            else:
                if cur_base: pairs.append((cur_base, ''.join(cur_diacs)))
                cur_base = ch; cur_diacs = []
        if cur_base: pairs.append((cur_base, ''.join(cur_diacs)))
        if pairs and 'ْ' in pairs[0][1]:   # سكون على أول حرف
            anomalies.append({
                'code': 'FALSE_PREFIX_SCAN',
                'detail': f'جذع مصطنع يبدأ بسكون: {h!r} ← مسح بادئة كاذب',
            })

    # 2. INFLECTIONAL_SUFFIX_MISCLASSIFIED_AS_MABNI
    for ending, label in KNOWN_INFLECTIONAL_ENDINGS.items():
        if surface.endswith(ending) or bare(surface).endswith(bare(ending)):
            # Check if نون was attached as NUN_AL_NISWA
            if 'ATTACHED_PRONOUN_NUN_AL_NISWA' in suffixes:
                anomalies.append({
                    'code': 'INFLECTIONAL_SUFFIX_MISCLASSIFIED_AS_MABNI',
                    'detail': f'نون النسوة رُصدت على {surface!r} التي تنتهي بـ {ending!r} ({label})',
                })
            # Check if واو+نون split
            if ('ATTACHED_PRONOUN_WAW_AL_JAMAA' in suffixes and
                    'ATTACHED_PRONOUN_NUN_AL_NISWA' in suffixes):
                anomalies.append({
                    'code': 'INFLECTIONAL_SUFFIX_MISCLASSIFIED_AS_MABNI',
                    'detail': f'واو+نون رُصدا على {surface!r} (يَسْتَطِيعُونَ نموذجًا): نون الرفع ليست نون النسوة',
                })

    # 3. NOMINAL_INFLECTION_MISCLASSIFIED_AS_ATTACHED_PRONOUN — تُ in اتُ
    if (bare(surface).endswith('ات') and
            any(s.mabni_id in ('ATTACHED_PRONOUN_TU', 'ATTACHED_PRONOUN_TAU',
                               'ATTACHED_PRONOUN_TI', 'ATTACHED_PRONOUN_TA')
                for s in (att.attached_mabniyat if att else []))):
        anomalies.append({
            'code': 'NOMINAL_INFLECTION_MISCLASSIFIED_AS_ATTACHED_PRONOUN',
            'detail': f'تاء جمع المؤنث في {surface!r} اشتُبه بها ضمير متصل',
        })

    # 4. FALSE_SUFFIX_SCAN — حِينَمَا: ا مقتطعة من مَا
    if bare(surface) == 'حينما' and 'ATTACHED_PRONOUN_ALIF_AL_ITHNAYN' in suffixes:
        anomalies.append({
            'code': 'FALSE_SUFFIX_SCAN',
            'detail': 'ألف «حِينَمَا» اشتُبه بها ألف الاثنين؛ الألف من مَا',
        })
    if bare(surface) == 'حينما' and seg == 'SEGMENTED':
        anomalies.append({
            'code': 'FALSE_SUFFIX_SCAN',
            'detail': f'حِينَمَا قُطِّعت: host={host!r} suffixes={suffixes} — لا تقطيع مشروع هنا',
        })

    # 5. INTERNAL_OPERATOR_NOT_RECOGNIZED — أَنَّهُمْ
    if bare(surface).startswith('أن') or bare(surface).startswith('ءن'):
        if seg == 'SEGMENTED' and host_route == 'OPEN_TO_HR2S' and host:
            bare_h = bare(host)
            if bare_h in ('أن', 'ءن', 'ءنن', 'أنن'):
                anomalies.append({
                    'code': 'INTERNAL_OPERATOR_NOT_RECOGNIZED',
                    'detail': (f'أَنَّ لم تُرصد كعامل داخلي؛ '
                               f'host={host!r} أُرسل إلى HR2S بدلًا من OPERATOR_BOUNDARY'),
                })

    # 6. ATTACHED_PRONOUN_EXPOSED_AS_STANDALONE_TOKEN
    bare_s = bare(surface)
    if bare_s in ('هم', 'ها', 'هي', 'هو', 'هما', 'هن', 'هن') and token_verdict == 'MABNI_BOUNDARY':
        # OK — standalone pronoun is MABNI_BOUNDARY legitimately
        pass  # هِيَ expected as MABNI_BOUNDARY
    if bare_s in ('هم', 'ها', 'هما', 'هن', 'هم') and token_verdict == 'MABNI_BOUNDARY':
        # These look like attached forms appearing as standalone
        anomalies.append({
            'code': 'ATTACHED_PRONOUN_EXPOSED_AS_STANDALONE_TOKEN',
            'detail': f'{surface!r} ظهر كـ MABNI_BOUNDARY مستقل رغم أنه على الأرجح ضمير متصل',
        })

    # 7. P4_MONOTONICITY_VIOLATION
    if 'DEFER' in p4_verdicts and structural_v4 == 'ACCEPT':
        anomalies.append({
            'code': 'P4_MONOTONICITY_VIOLATION',
            'detail': f'خانة DEFER موجودة لكن الحكم الهيكلي = ACCEPT: {p4_verdicts}',
        })

    # 8. UNLICENSED_SLOT_PROMOTED
    slots_info = r.get('slots', [])
    for i, slot in enumerate(slots_info):
        sv = slot.get('verdict', '')
        sp = slot.get('pattern', '')
        # CVCC not at end → investigate
        if sp == 'CVCC' and i < len(slots_info) - 1 and sv == 'ACCEPT':
            anomalies.append({
                'code': 'UNLICENSED_SLOT_PROMOTED',
                'detail': f'خانة CVCC في الموضع {i} (غير الأخير) مع حكم ACCEPT: الكلمة {surface!r}',
            })

    # 9. Known ta-marbuta blocker
    if has_ta_marbuta(surface) and v4 == 'BLOCK':
        anomalies.append({
            'code': 'KNOWN_P0_TA_MARBUTA_BLOCKER',
            'detail': f'{surface!r} محجوبة بسبب ة (P0) — متوقع، لا إصلاح في هذه المهمة',
        })

    # ── Regression check ──────────────────────────────────────────────────
    regression = None
    if surface in REGRESSION_CORRECT:
        expected_suffixes = REGRESSION_CORRECT[surface]
        if not any(mid in suffixes for mid in expected_suffixes):
            regression = {
                'expected_suffix_ids': expected_suffixes,
                'actual_suffix_ids':   suffixes,
                'verdict': 'REGRESSION_DETECTED',
            }
        else:
            regression = {'verdict': 'OK'}

    # لَهُمْ special
    if bare(surface) == 'لهم':
        if not (seg == 'SEGMENTED' and host_route == 'EMPTY'):
            regression = {
                'expected': 'COMPOSITE_CLOSED (host=EMPTY)',
                'actual': f'seg={seg} host_route={host_route}',
                'verdict': 'REGRESSION_DETECTED',
            }
        else:
            regression = {'verdict': 'OK'}

    # هِيَ
    if bare(surface) == 'هي' and not bare(surface) == 'هيما':
        if token_verdict not in ('MABNI_BOUNDARY', 'COMPOSITE_BOUNDARY'):
            pass  # not testing here for ambiguity
        regression = {'verdict': 'OK'} if token_verdict == 'MABNI_BOUNDARY' else {
            'expected': 'MABNI_BOUNDARY',
            'actual': token_verdict,
            'verdict': 'REGRESSION_DETECTED',
        }

    return {
        'surface':              surface,
        'input_surface':        r.get('input_surface', surface),
        'normalized_surface':   r.get('normalized_surface', ''),
        'canonical_surface':    r.get('canonical_surface', surface),
        'P4_slot_verdicts':     p4_verdicts,
        'structural_verdict':   structural_v4,
        'slots_detail':         r.get('slots', []),
        'whole_operator_lookup':op_lookup,
        'whole_mabni_lookup':   mabni_lookup,
        'prefixes':             prefixes,
        'residual_host':        host,
        'suffixes':             suffixes,
        'host_route':           host_route,
        'segmentation_verdict': seg,
        'token_verdict':        token_verdict,
        'ta_marbuta':           has_ta_marbuta(surface),
        'anomalies':            anomalies,
        'regression':           regression,
        'is_critical':          surface in CRITICAL_SURFACES,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    os.makedirs('reports/mabniyat', exist_ok=True)

    with open(FIXTURE_PATH, encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f.readlines()]

    all_results = []
    line_idx = 0

    for line in lines:
        line_idx += 1
        if not line.strip():
            continue
        # Tokenize: split on whitespace and punctuation, preserve Arabic tokens
        tokens = re.split(r'[\s،,\.؛؟!،]+', line)
        tokens = [t for t in tokens if t.strip()]
        for tok in tokens:
            r   = hokom(tok)
            rec = classify_token(tok, r)
            rec['line'] = line_idx
            rec['raw_token'] = tok
            all_results.append(rec)

    # ── Counters ──────────────────────────────────────────────────────────
    n_tokens      = len(all_results)
    n_correct     = sum(1 for r in all_results if not r['anomalies'] and
                        (r['regression'] is None or r['regression'].get('verdict') == 'OK'))
    n_fp_scan     = sum(1 for r in all_results
                        for a in r['anomalies'] if a['code'] == 'FALSE_PREFIX_SCAN')
    n_fs_scan     = sum(1 for r in all_results
                        for a in r['anomalies'] if a['code'] == 'FALSE_SUFFIX_SCAN')
    n_infl        = sum(1 for r in all_results
                        for a in r['anomalies']
                        if a['code'] in ('INFLECTIONAL_SUFFIX_MISCLASSIFIED_AS_MABNI',
                                         'NOMINAL_INFLECTION_MISCLASSIFIED_AS_ATTACHED_PRONOUN'))
    n_op_miss     = sum(1 for r in all_results
                        for a in r['anomalies'] if a['code'] == 'INTERNAL_OPERATOR_NOT_RECOGNIZED')
    n_p4_viol     = sum(1 for r in all_results
                        for a in r['anomalies'] if a['code'] == 'P4_MONOTONICITY_VIOLATION')
    n_ta          = sum(1 for r in all_results
                        for a in r['anomalies'] if a['code'] == 'KNOWN_P0_TA_MARBUTA_BLOCKER')
    n_other       = sum(1 for r in all_results
                        for a in r['anomalies']
                        if a['code'] not in ('FALSE_PREFIX_SCAN', 'FALSE_SUFFIX_SCAN',
                                             'INFLECTIONAL_SUFFIX_MISCLASSIFIED_AS_MABNI',
                                             'NOMINAL_INFLECTION_MISCLASSIFIED_AS_ATTACHED_PRONOUN',
                                             'INTERNAL_OPERATOR_NOT_RECOGNIZED',
                                             'P4_MONOTONICITY_VIOLATION',
                                             'KNOWN_P0_TA_MARBUTA_BLOCKER'))

    # ── Write JSONL ────────────────────────────────────────────────────────
    with open(JSONL_PATH, 'w', encoding='utf-8') as f:
        for rec in all_results:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')

    # ── Build text report ─────────────────────────────────────────────────
    lines_out = []
    W = 72

    def hr(ch='═'): return ch * W
    def sec(title): lines_out.extend(['', hr(), f'  {title}', hr()])

    lines_out.append(hr())
    lines_out.append('  Mabniyat Story Regression — Diagnostic Report')
    lines_out.append(hr())
    lines_out.append(f'  Fixture : {FIXTURE_PATH}')
    lines_out.append(f'  Results : {JSONL_PATH}')
    lines_out.append(hr())

    # ── Per-token detail ──────────────────────────────────────────────────
    sec('TOKEN-BY-TOKEN ANALYSIS')

    for rec in all_results:
        s    = rec['surface']
        tv   = rec['token_verdict']
        sv   = rec['structural_verdict']
        host = rec['residual_host']
        hr_  = rec['host_route']
        seg  = rec['segmentation_verdict']
        pfx  = rec['prefixes']
        sfx  = rec['suffixes']
        anoms= rec['anomalies']
        regr = rec['regression']

        flag = '⚠ ' if anoms else ('↩ ' if (regr and regr.get('verdict') == 'REGRESSION_DETECTED') else '  ')
        lines_out.append(f'\n{flag}{s}')
        lines_out.append(f'    norm      : {rec["normalized_surface"]}')
        lines_out.append(f'    P4        : {sv}  slots={rec["P4_slot_verdicts"]}')
        lines_out.append(f'    op_lookup : {rec["whole_operator_lookup"]}  '
                         f'mabni_lookup: {rec["whole_mabni_lookup"]}')
        lines_out.append(f'    prefixes  : {pfx or "—"}')
        lines_out.append(f'    host      : {host!r}  route={hr_}  seg={seg}')
        lines_out.append(f'    suffixes  : {sfx or "—"}')
        lines_out.append(f'    verdict   : {tv}')
        if rec['ta_marbuta'] and sv == 'BLOCK':
            lines_out.append(f'    [KNOWN_P0_TA_MARBUTA_BLOCKER]')
        for a in anoms:
            lines_out.append(f'    !! {a["code"]}: {a["detail"]}')
        if regr and regr.get('verdict') == 'REGRESSION_DETECTED':
            lines_out.append(f'    ↩ REGRESSION: {regr}')

    # ── Critical cases table ──────────────────────────────────────────────
    sec('CRITICAL CASES — DETAILED')

    critical_recs = [r for r in all_results if r['is_critical']]
    # also include anything with anomalies that appears in the story
    extra_anom = [r for r in all_results if r['anomalies'] and not r['is_critical']]

    for rec in critical_recs + extra_anom:
        s = rec['surface']
        lines_out.append(f'\n── {s} ──')
        lines_out.append(f'  input_surface       : {rec["input_surface"]}')
        lines_out.append(f'  canonical_surface   : {rec["canonical_surface"]}')
        lines_out.append(f'  normalized_surface  : {rec["normalized_surface"]}')
        lines_out.append(f'  P4_slot_verdicts    : {rec["P4_slot_verdicts"]}')
        lines_out.append(f'  structural_verdict  : {rec["structural_verdict"]}')
        lines_out.append(f'  whole_operator_lookup: {rec["whole_operator_lookup"]}')
        lines_out.append(f'  whole_mabni_lookup  : {rec["whole_mabni_lookup"]}')
        lines_out.append(f'  prefixes            : {rec["prefixes"] or "—"}')
        lines_out.append(f'  residual_host       : {rec["residual_host"]!r}')
        lines_out.append(f'  suffixes            : {rec["suffixes"] or "—"}')
        lines_out.append(f'  host_route          : {rec["host_route"]}')
        lines_out.append(f'  token_verdict       : {rec["token_verdict"]}')
        lines_out.append(f'  segmentation_verdict: {rec["segmentation_verdict"]}')
        for a in rec['anomalies']:
            lines_out.append(f'  ANOMALY [{a["code"]}]: {a["detail"]}')
        if not rec['anomalies']:
            lines_out.append(f'  classification      : CORRECT')
            lines_out.append(f'  reason              : الكلمة تُحلَّل تحليلًا صحيحًا')

    # ── Regression checks ─────────────────────────────────────────────────
    sec('REGRESSION CHECKS — EXPECTED CORRECT CASES')

    for rec in all_results:
        regr = rec.get('regression')
        if regr is None:
            continue
        s    = rec['surface']
        sfx  = rec['suffixes']
        ok   = regr.get('verdict') == 'OK'
        mark = '✓' if ok else '✗'
        lines_out.append(f'  {mark} {s:25} suffixes={sfx}')
        if not ok:
            lines_out.append(f'      {regr}')

    # ── Operator spot-check ───────────────────────────────────────────────
    sec('OPERATOR BOUNDARY SPOT-CHECK')

    for rec in all_results:
        s = rec['surface']
        if s in OPERATORS_EXPECTED:
            tv = rec['token_verdict']
            mark = '✓' if tv == 'OPERATOR_BOUNDARY' else '✗'
            lines_out.append(f'  {mark} {s:12} → {tv}')

    # ── Summary ───────────────────────────────────────────────────────────
    lines_out.append('')
    lines_out.append(hr())
    lines_out.append('  Mabniyat Story Regression — Summary')
    lines_out.append(hr())
    lines_out.append(f'  Input lines                      : {line_idx}')
    lines_out.append(f'  Produced pipeline tokens         : {n_tokens}')
    lines_out.append(f'  Correct analyses (no anomaly)    : {n_correct}')
    lines_out.append(f'  False prefix scans               : {n_fp_scan}')
    lines_out.append(f'  False suffix scans               : {n_fs_scan}')
    lines_out.append(f'  Inflection/mabni confusions      : {n_infl}')
    lines_out.append(f'  Internal operators missed        : {n_op_miss}')
    lines_out.append(f'  P4 monotonicity violations       : {n_p4_viol}')
    lines_out.append(f'  Known ta-marbuta blockers        : {n_ta}')
    lines_out.append(f'  Other anomalies                  : {n_other}')
    lines_out.append(hr())

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines_out) + '\n')

    # ── Print summary to stdout ────────────────────────────────────────────
    for ln in lines_out[-(18):]:
        print(ln)

    print(f'\nReport  : {REPORT_PATH}')
    print(f'JSONL   : {JSONL_PATH}')
    print(f'Fixture : {FIXTURE_PATH}')

if __name__ == '__main__':
    main()
