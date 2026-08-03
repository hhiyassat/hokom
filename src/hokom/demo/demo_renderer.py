"""
demo_renderer.py — Client presentation renderer for Hokom+Taaqol demo.

All displayed values are derived from the runtime result dicts produced
by process_token_full() and summary_stats(). Nothing is fabricated or hardcoded.
"""

import sys

# ── localization for terminal labels ──────────────────────────────────────────
try:
    from hokom.demo.localization import get_terminal_label as _get_terminal_label
    _terminal_loc_available = True
except ImportError:
    _terminal_loc_available = False

    def _get_terminal_label(key: str, lang: str) -> str:  # type: ignore[misc]
        return key

# ── ANSI color helpers ────────────────────────────────────────────────────────

class ANSI:
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    RED     = '\033[31m'
    CYAN    = '\033[36m'
    MAGENTA = '\033[35m'
    BLUE    = '\033[34m'
    DIM     = '\033[2m'

    @staticmethod
    def strip(text):
        """Remove all ANSI escape codes from text."""
        import re
        return re.sub(r'\033\[[0-9;]*m', '', text)


# ── Integrity violation schema ─────────────────────────────────────────────────
#
# VIOLATION_KEYS: keys in the integrity_check() dict that have FAILURE polarity
# (value > 0 or True means a problem).  TAAQOL_RUNTIME_ACTIVE is a positive
# metric — it is never a violation — and must never appear in this tuple.
# TAAQOL_CONSTITUTIONAL_EXEMPTIONS is also positive (documented exemptions are good).
# TAAQOL_UNEXPLAINED_COVERAGE_GAP is a violation (>0 means unaccounted gap).
#
# This is the single canonical definition.  Every renderer and readiness gate
# must import and use compute_violation_count() instead of summing raw values.

VIOLATION_KEYS: tuple[str, ...] = (
    "SLOTS_MISSING_STATE",
    "LICENSED_WITHOUT_SCOPE",
    "MISSING_EVALUATION_ID",
    "EVALUATION_ID_COLLISIONS",
    "MISSING_TAAQOL_TRACE_ACTIVE",
    "CLAIM_KEY_NONDETERMINISM",
    "UNTYPED_PAYLOADS",
    "SILENT_FALLBACKS",
    "UNEXPECTED_RUNTIME_ERRORS",
    "TAAQOL_RUNTIME_INACTIVE",          # bool — True means runtime missing
    "TAAQOL_UNEXPLAINED_COVERAGE_GAP",  # int  — >0 means gap not covered by exemptions
)


def compute_violation_count(checks: dict) -> int:
    """
    Return the number of integrity violations in *checks*.

    TAAQOL_RUNTIME_ACTIVE is a positive success metric and is never counted.
    TAAQOL_RUNTIME_INACTIVE is a boolean flag — counted as 1 when True.
    All other VIOLATION_KEYS are integer counts; each contributes its raw value.
    """
    total = 0
    for key in VIOLATION_KEYS:
        val = checks.get(key, 0)
        if key == "TAAQOL_RUNTIME_INACTIVE":
            total += 1 if bool(val) else 0
        else:
            total += int(val or 0)
    return total


def integrity_key_ok(key: str, value) -> bool:
    """
    Return True when this integrity-check key value represents a healthy state.

    TAAQOL_RUNTIME_ACTIVE — positive indicator; always healthy regardless of count.
    TAAQOL_RUNTIME_INACTIVE — healthy when False.
    All other keys — healthy when value == 0.
    """
    if key in (
        "TAAQOL_RUNTIME_ACTIVE",
        "TAAQOL_CONSTITUTIONAL_EXEMPTIONS",
    ):
        return True
    if key == "TAAQOL_RUNTIME_INACTIVE":
        return not bool(value)
    return int(value or 0) == 0


def _c(code, text, use_color):
    return f"{code}{text}{ANSI.RESET}" if use_color else text


def _verdict_color(verdict, use_color):
    if not use_color or verdict is None:
        return verdict or 'غير متاح'
    mapping = {
        'ACCEPT': ANSI.GREEN, 'ACCEPTED': ANSI.GREEN, 'LICENSED': ANSI.GREEN,
        'FULLY_LICENSED': ANSI.GREEN, 'APPROVED': ANSI.GREEN,
        'DEFER': ANSI.YELLOW, 'DEFERRED': ANSI.YELLOW, 'COMPOSITE': ANSI.YELLOW,
        'BLOCK': ANSI.RED, 'BLOCKED': ANSI.RED, 'REJECTED': ANSI.RED,
        'UNKNOWN': ANSI.DIM, 'NOT_OPENED': ANSI.DIM,
        'JAMID_AALAM_BOUNDARY': ANSI.CYAN, 'MABNI_BOUNDARY': ANSI.CYAN,
        'OPERATOR_BOUNDARY': ANSI.CYAN,
    }
    color = mapping.get(verdict, '')
    return f"{color}{verdict}{ANSI.RESET}" if color else verdict


# ── Section 1: Runtime identity ───────────────────────────────────────────────

def render_runtime_identity(
    hokom_head,
    taaqol_head,
    taaqol_pin,
    taaqol_pin_verified,
    taaqol_worktree_clean,
    results,
    use_color,
    lang: str = 'en',
):
    """
    Render the Runtime Identity block.

    When lang='ar', row labels are localised via the terminal_labels YAML section.
    Technical names (Python, Hokom, Taaqol, commit SHAs) are unchanged in every locale.
    """
    def _lbl(key: str) -> str:
        return _get_terminal_label(key, lang)

    lines = []
    sep = '═' * 72
    lines.append(_c(ANSI.BOLD, sep, use_color))
    _ri_title = _lbl('runtime_identity')
    lines.append(_c(ANSI.BOLD, f'  {_ri_title}', use_color))
    lines.append(_c(ANSI.BOLD, sep, use_color))

    pv = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    lines.append(f"  {_lbl('lbl_python'):<22} : {pv}")
    lines.append(f"  {_lbl('lbl_hokom_head'):<22} : {hokom_head}")
    lines.append(f"  {_lbl('lbl_taaqol_head'):<22} : {taaqol_head}")

    pin_display = taaqol_pin[:16] + '...' if len(taaqol_pin) > 16 else taaqol_pin
    pin_ok = taaqol_head.startswith(taaqol_pin[:8]) if taaqol_pin != 'UNKNOWN' else False
    pin_status = _verdict_color('ACCEPTED' if pin_ok else 'BLOCKED', use_color)
    lines.append(f"  {_lbl('lbl_taaqol_pin'):<22} : {pin_display}")
    lines.append(f"  {_lbl('lbl_pin_verified'):<22} : {pin_status}")

    wt_status = _verdict_color('ACCEPTED' if taaqol_worktree_clean else 'BLOCKED', use_color)
    lines.append(f"  {_lbl('lbl_taaqol_worktree'):<22} : {'CLEAN' if taaqol_worktree_clean else 'DIRTY'} — {wt_status}")

    if results:
        live_count = sum(1 for r in results if r.get('taaqol', {}).get('available'))
        total      = len(results)
        fallbacks  = sum(1 for r in results
                         if not r.get('error')
                         and not r.get('taaqol', {}).get('available')
                         and not r.get('taaqol', {}).get('runtime', {}).get('failure_code'))
        mode = 'LIVE' if live_count > 0 else 'BLOCKED'
        mode_str = _verdict_color('LICENSED' if mode == 'LIVE' else 'BLOCKED', use_color)
        lines.append(f"  {_lbl('lbl_taaqol_mode'):<22} : {mode_str}")
        lines.append(f"  {_lbl('lbl_live_evaluations'):<22} : {live_count} / {total}")
        lines.append(f"  {_lbl('lbl_silent_fallbacks'):<22} : {fallbacks}")
    else:
        lines.append(f"  {_lbl('lbl_taaqol_mode'):<22} : {_c(ANSI.DIM, 'غير متاح', use_color)}")

    lines.append('')
    return '\n'.join(lines)


# ── Section 2: Normalization ──────────────────────────────────────────────────

def render_normalization_row(token, use_color):
    orig = token.get('original_surface', '?')
    norm = token.get('normalization', {}).get('normalized_surface') or orig
    changed = norm != orig
    source  = token.get('normalization', {}).get('source', 'غير متاح')
    flag = _c(ANSI.YELLOW, 'مُعدَّل', use_color) if changed else _c(ANSI.DIM, 'ثابت', use_color)
    return f"    {orig:<18}  →  {norm:<18}  [{flag}]  المصدر: {source}"


# ── Section 3: Segmentation ───────────────────────────────────────────────────

def render_segmentation_row(token, use_color):
    seg  = token.get('segmentation', {})
    orig = token.get('original_surface', '?')
    host = seg.get('host_surface') or _c(ANSI.DIM, 'لا مضيف', use_color)
    proclitics = ' + '.join(seg.get('proclitics') or []) or '—'
    enclitics  = ' + '.join(seg.get('enclitics') or []) or '—'
    verdict    = seg.get('verdict') or 'غير متاح'
    article    = ' [ال]' if seg.get('has_article') else ''
    clitic_only = ' [حرف فقط]' if seg.get('clitic_only') else ''
    v_str = _verdict_color(verdict, use_color)
    return (f"    {orig:<18}  |  "
            f"صدر: {proclitics:<8}  مضيف: {host}{article}{clitic_only:<12}  "
            f"ذيل: {enclitics:<8}  [{v_str}]")


# ── Section 4: Word class ─────────────────────────────────────────────────────

def render_word_class_row(token, use_color):
    orig = token.get('original_surface', '?')
    wc   = token.get('word_class', {})
    cls  = wc.get('class') or _c(ANSI.DIM, 'غير متاح', use_color)
    sub  = wc.get('subclass') or ''
    verd = _verdict_color(wc.get('verdict'), use_color)
    skip = wc.get('inflection_skipped_reason')
    skip_str = f"  [{_c(ANSI.DIM, skip, use_color)}]" if skip else ''
    return f"    {orig:<18}  {cls:<14}{' / ' + sub if sub else '':<20}  [{verd}]{skip_str}"


# ── Section 5: Morphology ─────────────────────────────────────────────────────

def render_morphology_verbose(token, use_color):
    """Returns lines for one token's morphological analysis."""
    orig = token.get('original_surface', '?')
    root = token.get('root_analysis', {})
    ms   = token.get('morphosyntax', {})
    lines = []
    lines.append(_c(ANSI.BOLD, f"    ── {orig} ──", use_color))

    state = root.get('root_state', 'UNKNOWN')
    lines.append(f"      الجذر           : {root.get('canonical_root') or '—'}  [{_verdict_color(state, use_color)}]")
    lines.append(f"      عائلة البناء    : {root.get('cra_form_family') or '—'}")
    lines.append(f"      الوزن           : {root.get('wazn') or '—'}")
    lines.append(f"      الباب           : {'متاح' if root.get('bab_state') == 'KNOWN' else '—'}  [{root.get('bab_state', '—')}]")
    lines.append(f"      المصدر          : {root.get('masdar') or '—'}  [{root.get('masdar_state', '—')}]")
    lines.append(f"      الاشتقاق        : {root.get('derivative_type') or '—'}")
    lines.append(f"      رموز البقايا    : {', '.join(root.get('cra_reason_codes') or []) or '—'}")

    lines.append(f"      الزمن/الجانب    : {ms.get('tense_aspect') or '—'}")
    lines.append(f"      الصيغة          : {ms.get('mood') or '—'}")
    lines.append(f"      البناء          : {ms.get('voice') or '—'}")
    lines.append(f"      الشخص           : {ms.get('person') or '—'}")
    lines.append(f"      العدد           : {ms.get('number') or '—'}")
    lines.append(f"      الجنس           : {ms.get('gender') or '—'}")

    ambig = ms.get('ambiguity_candidates') or []
    if ambig:
        lines.append(f"      الاشتراك        : {len(ambig)} قراءة")
        for a in ambig[:3]:
            lines.append(f"        · شخص={a.get('person','?')}  عدد={a.get('number','?')}  جنس={a.get('gender','?')}")

    return lines


# ── Section 6: Live Taaqol judgment ──────────────────────────────────────────

def render_taaqol_verbose(token, use_color):
    orig = token.get('original_surface', '?')
    tq   = token.get('taaqol', {})
    rt   = tq.get('runtime', {})
    lines = []
    lines.append(_c(ANSI.BOLD, f"    ── Taaqol: {orig} ──", use_color))

    avail = tq.get('available', False)
    lines.append(f"      التكامل الحي    : {_verdict_color('LICENSED' if avail else 'BLOCKED', use_color)}")

    if not avail:
        fc = rt.get('failure_code') or tq.get('runtime', {}).get('failure_code', '—')
        lines.append(f"      كود الفشل       : {_c(ANSI.RED, str(fc), use_color) if use_color else str(fc)}")
        return lines

    lines.append(f"      SlotGraph نشط   : {_verdict_color('ACCEPTED' if rt.get('slot_graph_created') else 'BLOCKED', use_color)}")
    lines.append(f"      ملخص الرسم      : {tq.get('slot_graph_digest', '—')}")
    lines.append(f"      Gamma مُشغَّل    : {_verdict_color('ACCEPTED' if rt.get('gamma_executed') else 'BLOCKED', use_color)}")
    lines.append(f"      حالة Gamma      : {tq.get('gamma_result', '—')}")
    lines.append(f"      TransitionGate  : {_verdict_color('ACCEPTED' if rt.get('gate_executed') else 'BLOCKED', use_color)}")
    lines.append(f"      حكم البوابة     : {_verdict_color(tq.get('transition_gate_result'), use_color)}")
    lines.append(f"      الحكم العلوي    : {_verdict_color(tq.get('upstream_verdict'), use_color)}")
    lines.append(f"      حكم Taaqol      : {_verdict_color(tq.get('taaqol_verdict'), use_color)}")
    lines.append(f"      الحكم الفعّال   : {_verdict_color(tq.get('effective_verdict'), use_color)}")

    rcs = tq.get('reason_codes') or []
    if rcs:
        lines.append(f"      رموز الأسباب    : {', '.join(rcs)}")

    res = tq.get('residuals') or []
    if res:
        lines.append(f"      البقايا         : {len(res)} سجل")

    trace = tq.get('trace_events') or []
    if trace:
        lines.append(f"      مسار الأحداث    : {len(trace)} خطوة")
        for ev in trace[:5]:
            comp   = ev.get('component', '?')
            output = ev.get('output', '?')
            lines.append(f"        [{ev.get('step', '?')}] {comp} → {output}")

    slots = rt.get('slot_graph_slots') or []
    if slots:
        lines.append(f"      فتحات SlotGraph : {len(slots)}")
        for sl in slots[:6]:
            st = sl.get('state', '?')
            lines.append(f"        {sl.get('name','?'):<28} [{_verdict_color(st, use_color)}] = {sl.get('value','—')}")

    return lines


# ── Section 7: Constitutional decision chain ──────────────────────────────────

_CHAIN_LABELS = [
    ('الوضع',    'overall_verdict',      'composite_verdict'),
    ('السبب',    'cra_reason_codes',     'root_analysis'),
    ('العلة',    'phase4a_residuals',    'root_analysis'),
    ('المانع',   'rc_residual_codes',    'root_analysis'),
    ('القادح',   'reason_codes',         'taaqol'),
    ('البقايا',  'residuals',            'taaqol'),
]

def render_constitutional_chain(token, use_color):
    orig = token.get('original_surface', '?')
    lines = []
    lines.append(_c(ANSI.BOLD, f"    ── السلسلة الحكمية: {orig} ──", use_color))

    cv = token.get('composite_verdict', {})
    ov = cv.get('overall_verdict') or '—'
    lines.append(f"      الوضع            : {_verdict_color(ov, use_color)}")

    root = token.get('root_analysis', {})
    rcs  = root.get('cra_reason_codes') or []
    lines.append(f"      السبب            : {', '.join(rcs) if rcs else 'غير متاح في هذا المستوى'}")

    active_res = token.get('active_residuals') or []
    lines.append(f"      الشرط            : {'—' if not active_res else ', '.join(str(r) for r in active_res[:3])}")

    res_codes = root.get('rc_residual_codes') or []
    lines.append(f"      المانع           : {', '.join(res_codes) if res_codes else 'غير متاح في هذا المستوى'}")

    p4a = root.get('phase4a_residuals') or []
    lines.append(f"      العلة            : {', '.join(p4a) if p4a else '—'}")

    tq   = token.get('taaqol', {})
    ctr  = tq.get('contradictions') or []
    lines.append(f"      القادح           : {', '.join(str(c) for c in ctr) if ctr else 'غير متاح في هذا المستوى'}")

    ev   = tq.get('effective_verdict') or '—'
    health_map = {
        'LICENSED': 'الصحة',
        'FULLY_LICENSED': 'الصحة',
        'DEFERRED': 'التأجيل',
        'BLOCKED': 'الفساد',
        'REJECTED': 'البطلان',
    }
    health = health_map.get(ev, ev)
    lines.append(f"      الحكم            : {_verdict_color(ev, use_color)}  ({health})")

    tq_res = tq.get('residuals') or []
    lines.append(f"      البقايا          : {len(tq_res)} سجل" if tq_res else "      البقايا          : غير متاح في هذا المستوى")

    return lines


# ── Section 8: Evidence and ownership ────────────────────────────────────────

def render_ownership_row(token, use_color):
    orig = token.get('original_surface', '?')
    lines = [_c(ANSI.BOLD, f"    ── الملكية: {orig} ──", use_color)]

    wc_ev = token.get('word_class', {}).get('evidence') or []
    owners = set()
    for e in wc_ev:
        if isinstance(e, dict) and e.get('source'):
            owners.add(e['source'])

    ownership = [
        ('التطبيع',          'Hokom — normalizer'),
        ('التقطيع',          'Hokom — segmenter'),
        ('حدود الجمود',      'Hokom — jamid_boundary engine'),
        ('تصنيف الكلمة',     'Hokom — word_class engine'),
        ('المحاسبة الجذرية', 'Hokom — CRA (canonical_radical_accounting)'),
        ('الوزن',            'Hokom — phase4a_wazn_projection'),
        ('الباب',            'Hokom — phase4b_bab_projection'),
        ('المصدر',           'Hokom — phase4c_masdar_projection'),
        ('المشتقات',         'Hokom — phase4d_mushtaq_projection'),
        ('التصريف',          'Hokom — phase5_inflection'),
        ('الحكم الهيكلي',   'Taaqol — SlotGraph → Gamma → TransitionGate'),
    ]
    for label, owner in ownership:
        lines.append(f"      {label:<22} : {_c(ANSI.DIM, owner, use_color)}")

    return lines


# ── Section 9: Summary dashboard ─────────────────────────────────────────────

def render_summary_dashboard(stats, integrity, use_color, lang: str = 'en'):
    """
    Render the Summary Dashboard block.

    When lang='ar', section headings are localised via the terminal_labels YAML
    section.  All stat row labels are already in Arabic in the base renderer
    (they were Arabic from the start); they are unchanged here.
    """
    def _lbl(key: str) -> str:
        return _get_terminal_label(key, lang)

    lines = []
    sep = '═' * 72
    lines.append('')
    lines.append(_c(ANSI.BOLD, sep, use_color))
    lines.append(_c(ANSI.BOLD, f'  {_lbl("summary_dashboard")}', use_color))
    lines.append(_c(ANSI.BOLD, sep, use_color))

    def row(label, value):
        v_str = _verdict_color(str(value), use_color) if str(value) in (
            'FULLY_LICENSED', 'LICENSED', 'ACCEPTED', 'APPROVED'
        ) else str(value)
        lines.append(f"  {label:<38} : {v_str}")

    row('إجمالي الرموز',       stats.get('token_count', '—'))
    row('حزم مُكتملة',          stats.get('typed_bundles', '—'))
    row('تقييمات Taaqol الحية', stats.get('taaqol_live', '—'))
    row('وصلت H11-H15',         stats.get('h11_h15_reached', '—'))
    row('توقف مبكر',            stats.get('early_stops', '—'))

    lines.append('')
    ov = stats.get('overall_verdicts', {})
    row('مُجازة (ACCEPT)',      ov.get('ACCEPT', 0))
    row('مُرجأة (DEFER)',       ov.get('DEFER', 0))
    row('محجوبة (BLOCK)',       ov.get('BLOCK', 0))

    lines.append('')
    tv = stats.get('taaqol_verdicts', {})
    row('Taaqol LICENSED',     tv.get('LICENSED', 0))
    row('Taaqol DEFERRED',     tv.get('DEFERRED', 0))
    row('Taaqol BLOCKED',      tv.get('BLOCKED', 0))
    row('بلا Taaqol',          tv.get('NO_TAAQOL', 0))

    lines.append('')
    rs = stats.get('root_states', {})
    row('جذور معروفة (KNOWN)',    rs.get('KNOWN', 0))
    row('جذور مرجأة (DEFERRED)',  rs.get('DEFERRED', 0))
    row('جذور غامضة (AMBIGUOUS)', rs.get('AMBIGUOUS', 0))
    row('جذور مجهولة (UNKNOWN)',  rs.get('UNKNOWN', 0))

    lines.append('')
    row('أخطاء البرنامج',  stats.get('errors', 0))

    if integrity:
        lines.append('')
        lines.append(_c(ANSI.BOLD, f'  {_lbl("integrity_check")}', use_color))
        total_violations = compute_violation_count(integrity)
        ok = total_violations == 0
        lines.append(
            f"  {'إجمالي الانتهاكات':<38} : "
            f"{_verdict_color('ACCEPTED' if ok else 'BLOCKED', use_color)} ({total_violations})"
        )

    lines.append(_c(ANSI.BOLD, sep, use_color))
    lines.append('')
    return '\n'.join(lines)


# ── Full verbose renderer ─────────────────────────────────────────────────────

def render_token_verbose(token, use_color):
    """Render one token with all 7 analysis sections."""
    lines = []
    idx  = token.get('token_index', '?')
    orig = token.get('original_surface', '?')
    sep  = '─' * 64

    lines.append('')
    lines.append(_c(ANSI.BOLD, f"  [{idx:>3}]  {orig}", use_color))
    lines.append(_c(ANSI.DIM, '  ' + sep, use_color))

    if token.get('error'):
        err = token['error']
        lines.append(_c(ANSI.RED,
            f"    ANALYSIS_RUNTIME_ERROR: {err.get('type','?')}: {err.get('message','?')}",
            use_color))
        return '\n'.join(lines)

    lines.append('    التطبيع:')
    lines.append(render_normalization_row(token, use_color))

    lines.append('    التقطيع:')
    lines.append(render_segmentation_row(token, use_color))

    lines.append('    تصنيف الكلمة:')
    lines.append(render_word_class_row(token, use_color))

    lines.append('    التحليل الصرفي:')
    lines.extend(render_morphology_verbose(token, use_color))

    lines.append('    حكم Taaqol:')
    lines.extend(render_taaqol_verbose(token, use_color))

    lines.append('    السلسلة الحكمية:')
    lines.extend(render_constitutional_chain(token, use_color))

    lines.append('    الملكية:')
    lines.extend(render_ownership_row(token, use_color))

    return '\n'.join(lines)


def render_token_compact(token, use_color):
    """Render one token in compact client-facing form."""
    idx  = token.get('token_index', '?')
    orig = token.get('original_surface', '?')

    if token.get('error'):
        err = token['error']
        return _c(ANSI.RED,
            f"  [{idx:>3}]  {orig:<18}  ANALYSIS_RUNTIME_ERROR: {err.get('type','?')}",
            use_color)

    wc       = token.get('word_class', {}).get('class') or '—'
    sub      = token.get('word_class', {}).get('subclass') or ''
    root     = token.get('root_analysis', {}).get('canonical_root') or '—'
    root_st  = token.get('root_analysis', {}).get('root_state', '—')
    tq_ev    = token.get('taaqol', {}).get('effective_verdict') or '—'
    tq_avail = token.get('taaqol', {}).get('available', False)
    ov       = token.get('composite_verdict', {}).get('overall_verdict') or '—'

    wc_display = f"{wc}/{sub}" if sub else wc
    tq_display = _verdict_color(tq_ev, use_color) if tq_avail else _c(ANSI.DIM, '—', use_color)
    ov_display = _verdict_color(ov, use_color)

    return (f"  [{idx:>3}]  {orig:<18}  "
            f"ك={wc_display:<16}  جذر={root:<12}[{root_st}]  "
            f"Taaqol={tq_display}  نتيجة={ov_display}")
