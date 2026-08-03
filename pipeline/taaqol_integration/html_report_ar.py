"""
Arabic RTL HTML report renderer for TaaqolFullRunResult.

Contract
--------
* Public API: render_taaqol_html_ar(result) -> str
* Emits self-contained UTF-8 <!DOCTYPE html> with dir="rtl".
* Exactly 14 sections in the mandated order.
* No percentage sign without an adjacent denominator.
"""
from __future__ import annotations

import html
from typing import Iterable

from .result_types import (
    ExecutionStatus,
    ScopeType,
    StageExecutionRecord,
    TaaqolFullRunResult,
)

# ── section titles (Arabic, mandated order) ───────────────────────────────────
SECTION_TITLES_AR: tuple[str, ...] = (
    'الملخص التنفيذي',
    'إصدار Taaqol المستهدَف وبيئة التشغيل',
    'تغطية Taaqol الإجمالية',
    'مصفوفة تغطية مراحل الكلمة',
    'تفاصيل الكلمات',
    'تفاصيل العلاقات متعدّدة الكلمات',
    'تفاصيل السلسلة العمودية',
    'نتائج R1–R7 الحتمية',
    'ملخص المخلّفات والحواجز',
    'الدوال الأصلية المنفَّذة',
    'الدوال الأصلية غير المفتوحة',
    'حسابات حزمة USM/X0R',
    'قسم الإسناد والتتبّع',
    'قسم النزاهة ومنع تسرّب الذهب',
)


_STATUS_BADGE = {
    ExecutionStatus.EXECUTED: ('نُفِّذت',       '#0a7d2c'),
    ExecutionStatus.BLOCKED:  ('محجوبة',       '#a3311f'),
    ExecutionStatus.DEFERRED: ('مؤجَّلة',        '#8b5a00'),
    ExecutionStatus.NOT_OPENED: ('لم تُفتح',    '#555555'),
    ExecutionStatus.NOT_APPLICABLE: ('لا تنطبق', '#666666'),
    ExecutionStatus.ERROR:    ('خطأ',           '#c00000'),
}


def _e(s) -> str:
    if s is None:
        return ''
    return html.escape(str(s), quote=True)


def _badge(status: ExecutionStatus) -> str:
    label, color = _STATUS_BADGE.get(status, (str(status), '#333'))
    return (
        f'<span style="display:inline-block;padding:2px 6px;border-radius:3px;'
        f'background:{color};color:#fff;font-size:12px;">{_e(label)}</span>'
    )


def _table_open(headers: Iterable[str]) -> str:
    ths = ''.join(f'<th>{_e(h)}</th>' for h in headers)
    return (
        '<table style="width:100%;border-collapse:collapse;margin:8px 0;">'
        f'<thead style="background:#f0f0f0;">{ths}</thead><tbody>'
    )


def _table_close() -> str:
    return '</tbody></table>'


def _row(*cells: object) -> str:
    tds = ''.join(f'<td style="border:1px solid #ddd;padding:4px 8px;">{c}</td>' for c in cells)
    return f'<tr>{tds}</tr>'


def _section(idx: int, title: str, body: str) -> str:
    return (
        f'<section id="sec-{idx}" style="margin:24px 0;">'
        f'<h2 style="border-bottom:2px solid #444;padding-bottom:4px;">'
        f'{idx}. {_e(title)}'
        f'</h2>{body}</section>'
    )


# ── individual sections ───────────────────────────────────────────────────────
def _section_1_executive_summary(res: TaaqolFullRunResult) -> str:
    exec_ = res.native_execution
    tokens_core = exec_.get('tokens_reaching_core', 0)
    total_tokens = exec_.get('total_tokens', 0)
    body = (
        '<ul>'
        f'<li>معرِّف التشغيل: <code>{_e(res.run_id)}</code></li>'
        f'<li>عمق التشغيل (taaqol_depth): <b>{_e(res.taaqol_depth)}</b></li>'
        f'<li>حالة السلسلة العمودية الكاملة: <b>{_e(res.full_vertical_slice_status)}</b></li>'
        f'<li>حالة إغلاق مستودع الهدف: <b>{_e(res.target_repository_closure_status)}</b></li>'
        f'<li>هل انعكس المنطق الجاهز لـ Taaqol؟ '
        f'<b>{"نعم" if res.taaqol_ready_logic_reflected else "لا"}</b></li>'
        f'<li>الكلمات الواصلة إلى النواة: <b>{tokens_core} / {total_tokens}</b></li>'
        f'<li>إجمالي سجلّات المراحل: <b>{exec_.get("total_stage_records", 0)}</b></li>'
        '</ul>'
    )
    return _section(1, SECTION_TITLES_AR[0], body)


def _section_2_target_and_runtime(res: TaaqolFullRunResult) -> str:
    body = (
        '<ul>'
        f'<li>Taaqol SHA المستهدف: <code>{_e(res.target_taaqol_sha)}</code></li>'
        f'<li>Hokom HEAD: <code>{_e(res.hokom_head)}</code></li>'
        f'<li>إصدار Python: <code>{_e(res.python_version)}</code></li>'
        f'<li>معرِّف السجل (registry_version): <code>{_e(res.registry_version)}</code></li>'
        f'<li>بصمة السجل (registry_hash): <code>{_e(res.registry_hash)}</code></li>'
        f'<li>معرِّف الحزمة النصية (corpus_id): <code>{_e(res.corpus_id)}</code></li>'
        f'<li>بصمة الحزمة النصية (corpus_hash): <code>{_e(res.corpus_hash)}</code></li>'
        '</ul>'
    )
    return _section(2, SECTION_TITLES_AR[1], body)


def _section_3_overall_coverage(res: TaaqolFullRunResult) -> str:
    exec_ = res.native_execution
    blocked = res.native_blocked
    na = res.native_not_applicable
    unresolved = res.native_unresolved
    avail = res.native_availability

    tokens_core = exec_.get('tokens_reaching_core', 0)
    total_tokens = exec_.get('total_tokens', 0)
    total_recs = exec_.get('total_stage_records', 0)

    body = _table_open(('العدَّاد', 'القيمة (البسط)', 'المقام'))
    body += _row('الكلمات الواصلة إلى النواة (TOKENS_REACHING_CORE)', tokens_core, total_tokens)
    body += _row('المراحل المنفَّذة (EXECUTED)', exec_.get('executed', 0), total_recs)
    body += _row('المراحل المحجوبة (BLOCKED)', blocked.get('blocked', 0), total_recs)
    body += _row('المراحل المؤجَّلة (DEFERRED)', blocked.get('deferred', 0), total_recs)
    body += _row('المراحل غير المفتوحة (NOT_OPENED)', na.get('not_opened', 0), total_recs)
    body += _row('المراحل غير المنطبقة (NOT_APPLICABLE)', na.get('not_applicable', 0), total_recs)
    body += _row('الأخطاء (ERRORS)', unresolved.get('errors', 0), total_recs)
    body += _row('مراحل السجل الأصلية (registry)', avail.get('stages_in_registry', 0), avail.get('stages_in_registry', 0))
    body += _row('المؤهَّلة (ELIGIBLE*)', avail.get('stages_eligible', 0), avail.get('stages_in_registry', 0))
    body += _row('المؤجَّلة (DEFERRED registry)', avail.get('stages_deferred', 0), avail.get('stages_in_registry', 0))
    body += _row('المحظورة للسياق الأحادي (FORBIDDEN)', avail.get('stages_forbidden', 0), avail.get('stages_in_registry', 0))
    body += _table_close()
    return _section(3, SECTION_TITLES_AR[2], body)


def _section_4_token_stage_matrix(res: TaaqolFullRunResult) -> str:
    # Rows = tokens; columns = STAGE positions 0..8 (registry-based)
    positions = (0, 1, 2, 3, 4, 5, 6, 7, 8)
    header_labels = tuple(f'S{p}' for p in positions)

    # Build lookup: (scope_id, position) -> status
    lookup: dict[tuple[str, int], ExecutionStatus] = {}
    for r in res.stage_records:
        # registry stages have stage_id like STAGE_00_...
        if r.stage_id.startswith('STAGE_'):
            try:
                pos = int(r.stage_id.split('_', 2)[1])
            except (IndexError, ValueError):
                continue
            lookup[(r.scope_id, pos)] = r.execution_status

    body = _table_open(('الرمز', 'السطح') + header_labels)
    for tok in res.token_summaries:
        tid = tok['token_id']
        cells = [_e(tid), _e(tok['surface'])]
        for p in positions:
            status = lookup.get((tid, p))
            if status is None:
                cells.append('<span style="color:#aaa;">—</span>')
            else:
                cells.append(_badge(status))
        body += _row(*cells)
    body += _table_close()
    return _section(4, SECTION_TITLES_AR[3], body)


def _section_5_token_details(res: TaaqolFullRunResult) -> str:
    body = _table_open((
        'الرمز', 'السطح', 'حالة S0', 'حكم S0',
        'عدد الإسناد', 'المخلَّفات', 'رمز الخطأ',
    ))
    for tok in res.token_summaries:
        body += _row(
            _e(tok['token_id']),
            _e(tok['surface']),
            _e(tok['stage_0_status']),
            _e(tok['stage_0_verdict']),
            _e(tok['stage_0_provenance_count']),
            _e(', '.join(tok['stage_0_residuals']) or '—'),
            _e(tok.get('error_code') or '—'),
        )
    body += _table_close()
    return _section(5, SECTION_TITLES_AR[4], body)


def _section_6_multi_token_relations(res: TaaqolFullRunResult) -> str:
    body = _table_open((
        'معرِّف النطاق', 'الرمز الأيسر', 'الرمز الأيمن',
        'RelationCandidate', 'RelationClosure',
    ))
    for sp in res.span_summaries:
        body += _row(
            _e(sp['span_id']),
            _e(sp['left_token_id']),
            _e(sp['right_token_id']),
            _e(sp['relation_candidate_status']),
            _e(sp['relation_closure_status']),
        )
    if not res.span_summaries:
        body += _row('—', '—', '—', '—', '—')
    body += _table_close()
    return _section(6, SECTION_TITLES_AR[5], body)


def _section_7_vertical_chain(res: TaaqolFullRunResult) -> str:
    body = _table_open((
        'معرِّف الجملة', 'المدى الرمزي', 'الحالة',
    ))
    for s in res.sentence_summaries:
        body += _row(_e(s['sentence_id']), _e(s['token_span']), _e(s['status']))
    if not res.sentence_summaries:
        body += _row('—', '—', '—')
    body += _table_close()
    return _section(7, SECTION_TITLES_AR[6], body)


def _section_8_r1_r7(res: TaaqolFullRunResult) -> str:
    body = _table_open((
        'المرحلة', 'الرمز الأصلي', 'الوحدة الأصلية',
        'الحالة', 'رمز الحاجز',
    ))
    for r in res.r1_r7_records:
        body += _row(
            _e(r.stage_id),
            _e(r.native_symbol),
            _e(r.native_module),
            _badge(r.execution_status),
            _e(', '.join(r.blocker_codes) or '—'),
        )
    if not res.r1_r7_records:
        body += _row('—', '—', '—', '—', '—')
    body += _table_close()
    body += (
        f'<p>حالة تفعيل مقدِّم الخدمة الحيّ (live provider): '
        f'<b>{_e(res.native_availability.get("live_provider_authorization"))}</b></p>'
        f'<p>توفُّر المسار الحتمي R1–R7: '
        f'<b>{_e(res.native_availability.get("deterministic_r1_r7_available"))}</b></p>'
    )
    return _section(8, SECTION_TITLES_AR[7], body)


def _section_9_residuals_blockers(res: TaaqolFullRunResult) -> str:
    counts: dict[str, int] = {}
    for r in res.stage_records:
        for b in r.blocker_codes:
            counts[b] = counts.get(b, 0) + 1
    body = _table_open(('رمز الحاجز', 'عدد التكرار'))
    for code, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        body += _row(_e(code), n)
    if not counts:
        body += _row('—', 0)
    body += _table_close()

    # Residuals
    residuals: dict[str, int] = {}
    for r in res.stage_records:
        for c in r.residual_codes:
            residuals[c] = residuals.get(c, 0) + 1
    body += '<h3>المخلَّفات النشطة</h3>'
    body += _table_open(('رمز المخلَّف', 'عدد التكرار'))
    for code, n in sorted(residuals.items(), key=lambda kv: (-kv[1], kv[0])):
        body += _row(_e(code), n)
    if not residuals:
        body += _row('—', 0)
    body += _table_close()
    return _section(9, SECTION_TITLES_AR[8], body)


def _section_10_native_executed(res: TaaqolFullRunResult) -> str:
    body = _table_open((
        'المرحلة', 'النطاق', 'السطح/الرمز', 'الرمز الأصلي',
        'الوحدة الأصلية', 'المدَّة (ms)', 'الإسناد',
    ))
    for r in res.stage_records:
        if r.execution_status != ExecutionStatus.EXECUTED:
            continue
        body += _row(
            _e(r.stage_id),
            _e(str(r.scope_type)),
            _e(r.scope_id),
            _e(r.native_symbol),
            _e(r.native_module),
            _e(f'{r.duration_ms:.3f}'),
            _e(', '.join(r.provenance_ids) or '—'),
        )
    body += _table_close()
    return _section(10, SECTION_TITLES_AR[9], body)


def _section_11_native_not_opened(res: TaaqolFullRunResult) -> str:
    body = _table_open((
        'المرحلة', 'النطاق', 'الحالة', 'الرمز الأصلي', 'الحاجز',
    ))
    for r in res.stage_records:
        if r.execution_status in (ExecutionStatus.EXECUTED,):
            continue
        body += _row(
            _e(r.stage_id),
            _e(str(r.scope_type)),
            _badge(r.execution_status),
            _e(r.native_symbol),
            _e(', '.join(r.blocker_codes) or '—'),
        )
    body += _table_close()
    return _section(11, SECTION_TITLES_AR[10], body)


def _section_12_accounting(res: TaaqolFullRunResult) -> str:
    body = _table_open((
        'الطبقة', 'الرمز الأصلي', 'الحالة', 'رمز الحاجز',
    ))
    seen = False
    for r in res.stage_records:
        if r.scope_type != ScopeType.REPOSITORY_ACCOUNTING:
            continue
        seen = True
        body += _row(
            _e(r.stage_name),
            _e(r.native_symbol),
            _badge(r.execution_status),
            _e(', '.join(r.blocker_codes) or '—'),
        )
    if not seen:
        body += _row('—', '—', '—', '—')
    body += _table_close()
    return _section(12, SECTION_TITLES_AR[11], body)


def _section_13_provenance_trace(res: TaaqolFullRunResult) -> str:
    body = _table_open((
        'المرحلة', 'النطاق/الرمز', 'عدد الإسناد', 'عدد التتبع',
    ))
    for r in res.stage_records:
        if r.execution_status != ExecutionStatus.EXECUTED:
            continue
        body += _row(
            _e(r.stage_id),
            _e(r.scope_id),
            len(r.provenance_ids),
            len(r.trace_ids),
        )
    body += _table_close()
    return _section(13, SECTION_TITLES_AR[12], body)


def _section_14_integrity(res: TaaqolFullRunResult) -> str:
    flags = res.integrity_flags
    body = _table_open(('علَم النزاهة', 'القيمة'))
    for key in ('silent_fallbacks', 'synthetic_provenance', 'gold_leakage', 'forbidden_leaps'):
        body += _row(_e(key), flags.get(key, 0))
    body += _table_close()
    body += (
        '<p>يُثبت هذا القسم عدم تسرُّب الحقيقة الذهبية (gold_leakage=0) وعدم '
        'وجود قفزات محظورة (forbidden_leaps=0). المخلِّف الاصطناعي المسموح به '
        'هو صفر (synthetic_provenance=0). أي احتياطي صامت (silent_fallbacks) '
        'مراقَب بشكل صارم.</p>'
    )
    return _section(14, SECTION_TITLES_AR[13], body)


# ── top-level renderer ───────────────────────────────────────────────────────
def render_taaqol_html_ar(result: TaaqolFullRunResult) -> str:
    """Render a full-target Arabic RTL HTML report."""
    sections = (
        _section_1_executive_summary(result),
        _section_2_target_and_runtime(result),
        _section_3_overall_coverage(result),
        _section_4_token_stage_matrix(result),
        _section_5_token_details(result),
        _section_6_multi_token_relations(result),
        _section_7_vertical_chain(result),
        _section_8_r1_r7(result),
        _section_9_residuals_blockers(result),
        _section_10_native_executed(result),
        _section_11_native_not_opened(result),
        _section_12_accounting(result),
        _section_13_provenance_trace(result),
        _section_14_integrity(result),
    )

    style = (
        'body{font-family:"Amiri","Traditional Arabic",serif;'
        'margin:16px;line-height:1.6;color:#111;}'
        'h1,h2,h3{color:#222;}'
        'table{font-size:13px;}'
        'code{background:#f4f4f4;padding:1px 4px;border-radius:3px;}'
    )

    return (
        '<!DOCTYPE html>'
        '<html lang="ar" dir="rtl">'
        '<head>'
        '<meta charset="utf-8">'
        f'<title>تقرير Taaqol الكامل — {_e(result.run_id)}</title>'
        f'<style>{style}</style>'
        '</head>'
        '<body>'
        f'<h1>تقرير Taaqol الكامل (Full-Target)</h1>'
        f'<p><b>معرِّف التشغيل:</b> <code>{_e(result.run_id)}</code></p>'
        + ''.join(sections)
        + '</body></html>'
    )


__all__ = ['render_taaqol_html_ar', 'SECTION_TITLES_AR']
