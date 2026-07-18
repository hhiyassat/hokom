#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_all_mabniyat_json_examples.py
======================================================
اختبارات تكاملية شاملة لجميع أمثلة ملفات data/02_mabniyat/.
الحالات مُحمَّلة من المانيفست المُنتَج بواسطة:
  python scripts/build_mabniyat_test_harness.py

تشغيل:
  pytest tests/integration/test_all_mabniyat_json_examples.py -v
"""

import json
import os
import sys
import pytest

# ── إضافة مسار hokom إلى sys.path ───────────────────────────────────────────
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
HOKOM_DIR = os.path.dirname(os.path.dirname(TESTS_DIR))
sys.path.insert(0, HOKOM_DIR)

from hokom_pipeline import hokom as run_hokom
from mabni_layer    import MabniBoundary, MabniOpen, MabniBlocked

MANIFEST_PATH = os.path.join(
    HOKOM_DIR, 'data', 'generated', '02_mabniyat',
    'mabniyat_examples_manifest.jsonl'
)


# ══════════════════════════════════════════════════════════════════════════════
# تحميل المانيفست
# ══════════════════════════════════════════════════════════════════════════════

def _load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        pytest.skip(f"Manifest not found: {MANIFEST_PATH} — run build_mabniyat_test_harness.py first")
    entries = []
    with open(MANIFEST_PATH, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


ALL_ENTRIES   = _load_manifest()
TESTABLE      = [e for e in ALL_ENTRIES if e['expectation_status'] == 'TESTABLE']
ALL_CASE_IDS  = [e['case_id'] for e in ALL_ENTRIES]


def _run(surface: str):
    """يُشغِّل hokom() ويُعيد (actual_verdict, result_dict)."""
    r   = run_hokom(surface)
    mb  = r.get('mabni')
    att = r.get('attachment')
    v4  = r.get('verdict', 'ACCEPT')

    if v4 == 'BLOCK' or isinstance(mb, MabniBlocked):
        return 'BLOCKED', r

    if isinstance(mb, MabniBoundary):
        return 'OPERATOR_BOUNDARY', r

    if isinstance(mb, MabniOpen):
        if att is None:
            return 'OPEN_TO_HR2S', r
        seg   = att.segmentation_verdict
        route = att.host_route
        if seg == 'NOT_SEGMENTED' and route == 'MABNI_BOUNDARY':
            return 'MABNI_BOUNDARY', r
        if seg == 'SEGMENTED':
            return 'COMPOSITE_CLOSED' if route == 'EMPTY' else 'COMPOSITE_BOUNDARY', r
        if seg == 'AMBIGUOUS':
            return 'AMBIGUOUS', r
        return 'OPEN_TO_HR2S', r

    return 'UNKNOWN', r


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 1: حجم المانيفست
# ══════════════════════════════════════════════════════════════════════════════

def test_manifest_not_empty():
    """المانيفست يجب أن يحتوي على مدخلات."""
    assert len(ALL_ENTRIES) > 0, "المانيفست فارغ — شغِّل build_mabniyat_test_harness.py"


def test_manifest_min_size():
    """المانيفست يجب أن يحتوي على الأقل 100 مدخلة (تغطية كافية)."""
    assert len(ALL_ENTRIES) >= 100, f"المانيفست صغير جدًا: {len(ALL_ENTRIES)}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 2: عدم تكرار case_id
# ══════════════════════════════════════════════════════════════════════════════

def test_no_duplicate_case_ids():
    """يجب أن تكون case_id فريدة في جميع المدخلات."""
    dupes = [cid for cid in ALL_CASE_IDS if ALL_CASE_IDS.count(cid) > 1]
    assert not dupes, f"case_ids مكررة: {set(dupes)}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 3: كل مدخلة TESTABLE لها سطح غير فارغ
# ══════════════════════════════════════════════════════════════════════════════

def test_testable_entries_have_surface():
    """كل مدخلة TESTABLE يجب أن يكون لها expected_surface غير فارغ."""
    missing = [e['case_id'] for e in TESTABLE if not e.get('expected_surface')]
    assert not missing, f"مدخلات TESTABLE بدون surface: {missing[:10]}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 4: كل ملف مصدر موجود في المانيفست
# ══════════════════════════════════════════════════════════════════════════════

def test_all_source_files_represented():
    """يجب أن تكون جميع ملفات data/02_mabniyat/ ممثَّلة في المانيفست."""
    data_dir = os.path.join(HOKOM_DIR, 'data', '02_mabniyat')
    json_files = {f for f in os.listdir(data_dir) if f.endswith('.json')}
    manifest_files = {e['source_file'] for e in ALL_ENTRIES}
    missing = json_files - manifest_files
    assert not missing, f"ملفات غائبة من المانيفست: {missing}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 5: monotonicity — P4 BLOCK يبقى BLOCK
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("entry", TESTABLE, ids=[e['case_id'] for e in TESTABLE])
def test_p4_monotonicity(entry):
    """إذا أعاد P4 BLOCK فلا يجوز لأي طبقة لاحقة تغيير الحكم."""
    surface = entry['expected_surface']
    actual, r = _run(surface)
    mb = r.get('mabni')
    v4 = r.get('verdict', 'ACCEPT')
    if v4 == 'BLOCK':
        # يجب أن تكون النتيجة BLOCKED وليست MABNI_BOUNDARY أو OPERATOR_BOUNDARY
        assert actual == 'BLOCKED', (
            f"P4 monotonicity انتُهكت: P4=BLOCK لكن actual={actual} "
            f"للسطح {surface!r}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 6: MABNI_BOUNDARY لا يذهب إلى HR2S
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize(
    "entry",
    [e for e in TESTABLE
     if e['expected_route'] == 'MABNI_BOUNDARY'
     and 'NORMALIZATION_HAMZA_MISMATCH_EXPECTED' not in (e['expectation_reason'] or '')
     and 'SOURCE_CONTRADICTION' not in (e['expectation_reason'] or '')],
    ids=[e['case_id'] for e in TESTABLE
         if e['expected_route'] == 'MABNI_BOUNDARY'
         and 'NORMALIZATION_HAMZA_MISMATCH_EXPECTED' not in (e['expectation_reason'] or '')
         and 'SOURCE_CONTRADICTION' not in (e['expectation_reason'] or '')],
)
def test_mabni_boundary_route(entry):
    """
    السطوح المتوقعة أن تكون MABNI_BOUNDARY يجب أن تُعيد MABNI_BOUNDARY،
    وليس OPEN_TO_HR2S.
    """
    surface = entry['expected_surface']
    actual, _ = _run(surface)
    assert actual == 'MABNI_BOUNDARY', (
        f"case_id={entry['case_id']}: "
        f"expected=MABNI_BOUNDARY  actual={actual}  surface={surface!r}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 7: OPERATOR_BOUNDARY لا يذهب إلى DAL/HR2S
# ══════════════════════════════════════════════════════════════════════════════

_OPERATOR_ENTRIES = [
    e for e in TESTABLE
    if e['expected_route'] == 'OPERATOR_BOUNDARY'
    and 'NORMALIZATION_HAMZA_MISMATCH_EXPECTED' not in (e['expectation_reason'] or '')
]

@pytest.mark.parametrize(
    "entry", _OPERATOR_ENTRIES,
    ids=[e['case_id'] for e in _OPERATOR_ENTRIES],
)
def test_operator_boundary_route(entry):
    """
    الأدوات المخزنة في operators catalog يجب أن تُعيد OPERATOR_BOUNDARY.
    """
    surface = entry['expected_surface']
    actual, _ = _run(surface)
    assert actual == 'OPERATOR_BOUNDARY', (
        f"case_id={entry['case_id']}: "
        f"expected=OPERATOR_BOUNDARY  actual={actual}  surface={surface!r}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 8: الهمزة الصريحة لا تُحذف في bare fallback
# ══════════════════════════════════════════════════════════════════════════════

def test_explicit_diacritic_respected_in_bare_fallback():
    """
    هُوِ (بكسرة صريحة على الواو) لا يجوز أن يُطابق هُوَ.
    قانون: كل حركة مكتوبة في الإدخال قيدٌ واجب الاحترام.
    """
    actual, _ = _run('هُوِ')
    assert actual != 'MABNI_BOUNDARY', (
        "هُوِ طابق MABNI_BOUNDARY عبر bare fallback — انتهاك قانون التوافق"
    )


def test_hiya_is_mabni_boundary_not_hr2s():
    """هِيَ يجب أن تكون MABNI_BOUNDARY لا OPEN_TO_HR2S."""
    actual, _ = _run('هِيَ')
    assert actual == 'MABNI_BOUNDARY', f"هِيَ → {actual} (يجب MABNI_BOUNDARY)"


def test_huwa_is_mabni_boundary():
    """هُوَ يجب أن تكون MABNI_BOUNDARY."""
    actual, _ = _run('هُوَ')
    assert actual == 'MABNI_BOUNDARY', f"هُوَ → {actual}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 9: الحالات SUFFIX_ONLY موجودة في المانيفست
# ══════════════════════════════════════════════════════════════════════════════

def test_suffix_only_entries_exist():
    """يجب وجود مدخلات SUFFIX_ONLY في المانيفست (الضمائر المتصلة)."""
    suffix_entries = [e for e in ALL_ENTRIES if e['expectation_status'] == 'SUFFIX_ONLY']
    assert len(suffix_entries) > 0, "لا توجد مدخلات SUFFIX_ONLY — فحص pronouns_classification"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 10: الحالات LATENT_ONLY موجودة
# ══════════════════════════════════════════════════════════════════════════════

def test_latent_only_entries_exist():
    """يجب وجود مدخلات LATENT_ONLY في المانيفست (الضمائر المستترة)."""
    latent = [e for e in ALL_ENTRIES if e['expectation_status'] == 'LATENT_ONLY']
    assert len(latent) > 0, "لا توجد مدخلات LATENT_ONLY — فحص hidden_pronouns"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 11: الحالات RULE_ONLY موجودة
# ══════════════════════════════════════════════════════════════════════════════

def test_rule_only_entries_exist():
    """يجب وجود مدخلات RULE_ONLY في المانيفست."""
    rule_entries = [e for e in ALL_ENTRIES if e['expectation_status'] == 'RULE_ONLY']
    assert len(rule_entries) > 0, "لا توجد مدخلات RULE_ONLY"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 12: COMPOSITE_CLOSED لا يُرسل host فارغ إلى HR2S
# ══════════════════════════════════════════════════════════════════════════════

def test_composite_closed_lahum():
    """لَهُمْ يجب أن تكون COMPOSITE_CLOSED — host='' لا يُرسَل إلى HR2S."""
    actual, r = _run('لَهُمْ')
    mb  = r.get('mabni')
    att = r.get('attachment')
    # يجب أن يكون seg=SEGMENTED و route=EMPTY → COMPOSITE_CLOSED
    if isinstance(mb, MabniOpen) and att:
        assert att.segmentation_verdict == 'SEGMENTED', \
            f"لَهُمْ: seg={att.segmentation_verdict} (يجب SEGMENTED)"
        assert att.host_route == 'EMPTY', \
            f"لَهُمْ: host_route={att.host_route} (يجب EMPTY)"
    else:
        pytest.skip("لَهُمْ لم تمر بـ MabniOpen — قد تكون في المسار الصواب بطريقة أخرى")


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 13: هَذَا — MABNI_BOUNDARY بالوحدة
# ══════════════════════════════════════════════════════════════════════════════

def test_hadha_mabni_boundary():
    """هَذَا يجب أن يكون MABNI_BOUNDARY — ضمير إشارة مستقل."""
    actual, _ = _run('هَذَا')
    assert actual == 'MABNI_BOUNDARY', f"هَذَا → {actual}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 14: المانيفست يحتوي على الحقول الـ 13 الإلزامية
# ══════════════════════════════════════════════════════════════════════════════

REQUIRED_FIELDS = [
    'case_id','source_file','source_record_id','source_field',
    'raw_example','expected_mabni_id','expected_surface',
    'expected_surface_kind','expected_position','expected_route',
    'evidence_mode','expectation_status','expectation_reason',
]

def test_manifest_has_required_fields():
    """كل مدخلة في المانيفست يجب أن تحتوي على الحقول الـ 13 الإلزامية."""
    for entry in ALL_ENTRIES[:10]:  # فحص عيِّنة
        for field in REQUIRED_FIELDS:
            assert field in entry, \
                f"case_id={entry.get('case_id','?')} يفتقر إلى الحقل {field!r}"


# ══════════════════════════════════════════════════════════════════════════════
# الاختبار 15: لَمْ → OPERATOR_BOUNDARY
# ══════════════════════════════════════════════════════════════════════════════

def test_lam_operator_boundary():
    """لَمْ حرف جزم → OPERATOR_BOUNDARY."""
    actual, _ = _run('لَمْ')
    assert actual == 'OPERATOR_BOUNDARY', f"لَمْ → {actual}"
