#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_hokom_live_pipeline_w6.py — W6 Live Wiring Integration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يُثبت أن hokom() بعد W6:
  1. يُنتج phase4a_result في المخرج.
  2. يستخدم المحرك المحلي (HOKOM_ROOT_ENGINE) — لا HR2S.
  3. يمرر root_candidate المحلي إلى Phase4A الأوركسترا.
  4. يعكس المسارات الصحيحة: ACCEPT / DEFER / None (مبني/مغلق).

قانون الاختبار:
  • هذه الاختبارات تفشل الآن (W6 لم يُطبَّق بعد) وتنجح بعد التعديل.
  • لا تُعدَّل طرق الأوركسترا أو المحرك — تُختبَر عبر hokom() فقط.
  • لا HR2S، لا from_external_root، لا dependency على hr2s_result.
"""

from __future__ import annotations

import inspect

import pytest

from hokom_pipeline import hokom


# ══════════════════════════════════════════════════════════════════════════════
# W6-1 — phase4a_result في المخرج
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase4AResultPresence:
    """W6 يُضيف مفتاح phase4a_result لكل استدعاء لـ hokom()."""

    def test_phase4a_result_key_exists_for_verb(self):
        """OPEN word → phase4a_result present (even if DEFER internally)."""
        r = hokom('ضَرَبَ')
        assert 'phase4a_result' in r, "phase4a_result مفتاح مطلوب في المخرج"

    def test_phase4a_result_key_exists_for_nominal(self):
        r = hokom('مَسْرُورٌ')
        assert 'phase4a_result' in r

    def test_phase4a_result_none_for_mabni_boundary(self):
        """مِنْ: مبني → لا مسار جذر → phase4a_result يجب أن يكون None."""
        r = hokom('مِنْ')
        assert 'phase4a_result' in r
        assert r['phase4a_result'] is None

    def test_phase4a_result_none_when_pre_root_absent(self):
        """أنَّ: مبني (operator) → pre_root=None → phase4a_result=None."""
        r = hokom('هِيَ')
        assert 'phase4a_result' in r
        assert r['phase4a_result'] is None


# ══════════════════════════════════════════════════════════════════════════════
# W6-2 — لا HR2S في الإنتاج
# ══════════════════════════════════════════════════════════════════════════════

class TestNoHr2sInProduction:
    """hr2s_result يُزال من المخرج — الاقتران بـ HR2S محظور في الإنتاج."""

    def test_hr2s_result_removed_from_output(self):
        """W6: hr2s_result لا يظهر في مخرج hokom() بعد الترحيل."""
        r = hokom('ضَرَبَ')
        assert 'hr2s_result' not in r, (
            "hr2s_result يجب إزالته من المخرج بعد W6 — يُستبدل بـ phase4a_result"
        )

    def test_no_hr2s_production_import_in_pipeline(self):
        """لا يوجد import hr2s أو from hr2s في hokom_pipeline.py (إنتاج)."""
        import hokom_pipeline
        src = inspect.getsource(hokom_pipeline)
        has_import = (
            'import hr2s' in src
            or 'from hr2s' in src
            or 'HR2SRootAdapter' in src
        )
        assert not has_import, (
            "hokom_pipeline.py يحتوي على اقتران بـ HR2S — يجب إزالته في W6"
        )


# ══════════════════════════════════════════════════════════════════════════════
# W6-3 — المحرك المحلي هو المصدر الوحيد
# ══════════════════════════════════════════════════════════════════════════════

class TestLocalEngineIsSource:
    """root_candidate يأتي من HOKOM_ROOT_ENGINE — لا HR2S."""

    def test_darab_root_candidate_source_is_hokom(self):
        r = hokom('ضَرَبَ')
        rc = r.get('root_candidate')
        assert rc is not None, "root_candidate يجب أن يُنتَج للكلمات المفتوحة"
        source = rc.root_profile.get('source_engine', '')
        assert source == 'HOKOM_ROOT_ENGINE', (
            f"source_engine={source!r} — المتوقع: HOKOM_ROOT_ENGINE"
        )

    def test_kataba_root_candidate_source_is_hokom(self):
        r = hokom('كَتَبَ')
        rc = r.get('root_candidate')
        assert rc is not None
        assert rc.root_profile.get('source_engine') == 'HOKOM_ROOT_ENGINE'

    def test_root_candidate_none_when_pre_root_absent(self):
        """مِنْ: لا root_candidate لأن مسار الجذر لا يُفتح."""
        r = hokom('مِنْ')
        assert r.get('root_candidate') is None


# ══════════════════════════════════════════════════════════════════════════════
# W6-4 — مسار ACCEPT المباشر
# ══════════════════════════════════════════════════════════════════════════════

class TestDirectAcceptPath:
    """كلمات ذات جذر ثلاثي سالم + وزن مرخَّص → final_directive='ACCEPT'."""

    def test_darab_phase4a_accept(self):
        r = hokom('ضَرَبَ')
        p4 = r.get('phase4a_result')
        assert p4 is not None
        assert p4.final_directive == 'ACCEPT', (
            f"final_directive={p4.final_directive!r} — المتوقع: ACCEPT"
        )
        assert p4.source_path == 'direct_accept'

    def test_darab_selected_wazn_is_faala(self):
        r = hokom('ضَرَبَ')
        p4 = r['phase4a_result']
        assert p4.wazn_projection is not None
        assert p4.wazn_projection.selected_wazn is not None
        assert p4.wazn_projection.selected_wazn.wazn_pattern == 'فَعَلَ'

    def test_kataba_phase4a_accept(self):
        r = hokom('كَتَبَ')
        p4 = r.get('phase4a_result')
        assert p4 is not None
        assert p4.final_directive == 'ACCEPT'

    def test_taraka_suffix_stripped_accept(self):
        """تَرَكَتْهُمْ: P5 يجزّئ → refined_host='تَرَكَ' → ACCEPT فَعَلَ."""
        r = hokom('تَرَكَتْهُمْ')
        p4 = r.get('phase4a_result')
        assert p4 is not None
        assert p4.final_directive == 'ACCEPT'
        assert p4.wazn_projection.selected_wazn.wazn_pattern == 'فَعَلَ'


# ══════════════════════════════════════════════════════════════════════════════
# W6-5 — مسار DEFER (جذر ضعيف / غير محلول)
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferPath:
    """كلمات ذات جذر ضعيف → root_candidate DEFER → phase4a DEFER."""

    def test_qala_root_candidate_deferred(self):
        """قَالَ: جذر مجوف (و) → RootResolution DEFER → Phase4A DEFER."""
        r = hokom('قَالَ')
        rc = r.get('root_candidate')
        assert rc is not None, "قَالَ يجب أن يُنتج root_candidate"
        assert rc.directive == 'DEFER', (
            f"root_candidate.directive={rc.directive!r} — المتوقع: DEFER (مجوف)"
        )

    def test_qala_phase4a_deferred(self):
        r = hokom('قَالَ')
        p4 = r.get('phase4a_result')
        assert p4 is not None
        assert p4.final_directive == 'DEFER'
        assert p4.source_path == 'deferred'

    def test_qala_phase4a_no_selected_wazn(self):
        """DEFER → لا وزن محدد."""
        r = hokom('قَالَ')
        p4 = r['phase4a_result']
        assert p4.final_wazn is None


# ══════════════════════════════════════════════════════════════════════════════
# W6-6 — عقود Phase4AResult
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase4AResultContract:
    """phase4a_result يحترم عقود Phase4AResult الأساسية."""

    def test_accept_has_wazn_projection(self):
        r = hokom('ضَرَبَ')
        p4 = r['phase4a_result']
        assert p4.wazn_projection is not None
        assert p4.wazn_projection.selected_wazn is not None

    def test_defer_has_no_selected_wazn(self):
        r = hokom('قَالَ')
        p4 = r['phase4a_result']
        assert p4.final_wazn is None
        if p4.wazn_projection is not None:
            assert p4.wazn_projection.selected_wazn is None

    def test_final_directive_is_string(self):
        """final_directive قابل للاستخدام المباشر كسلسلة."""
        r = hokom('ضَرَبَ')
        p4 = r['phase4a_result']
        assert isinstance(p4.final_directive, str)
        assert p4.final_directive in ('ACCEPT', 'DEFER', 'BLOCK')

    def test_phase4a_result_serializable(self):
        """to_dict() يعمل بلا استثناء ويُنتج بنية قانونية."""
        import json
        r = hokom('ضَرَبَ')
        p4 = r['phase4a_result']
        d = p4.to_dict()
        json.dumps(d, ensure_ascii=False)
        assert 'final_directive' in d
        assert 'source_path' in d


# ══════════════════════════════════════════════════════════════════════════════
# W6-7 — الرتابة: pre_root.directive ≤ phase4a.final_directive
# ══════════════════════════════════════════════════════════════════════════════

class TestMonotonicity:
    """رتابة المسار: OPEN قد يُنتج أي حكم؛ لا BLOCK بلا سبب مغلق."""

    def test_open_pre_root_may_produce_accept(self):
        r = hokom('ضَرَبَ')
        pr = r.get('pre_root')
        assert pr is not None and pr.root_path_directive == 'OPEN'
        assert r['phase4a_result'].final_directive == 'ACCEPT'

    def test_open_pre_root_may_produce_defer(self):
        r = hokom('قَالَ')
        pr = r.get('pre_root')
        assert pr is not None and pr.root_path_directive == 'OPEN'
        assert r['phase4a_result'].final_directive == 'DEFER'

    def test_no_phase4a_when_no_root_path(self):
        """بلا مسار جذر → phase4a_result=None (لا phase4a BLOCK خاطئ)."""
        r = hokom('مِنْ')
        assert r.get('phase4a_result') is None


# ══════════════════════════════════════════════════════════════════════════════
# W6-8 — الملفات المجمَّدة لم تتغير
# ══════════════════════════════════════════════════════════════════════════════

import hashlib
from pathlib import Path

FROZEN = [
    ('pipeline/p3_candidate/root_profiles.py',             'c20a1bc6998516cc'),
    ('pipeline/p3_candidate/root_rules.py',                '622760abac55e3c1'),
    ('pipeline/p3_candidate/root_resolution.py',           'd87d07921d989c26'),
    ('pipeline/p3_candidate/root_resolution_orchestrator.py', '58ecd174a919cbe8'),
    ('pipeline/p2_projection/root_projection.py',          '7bca3605867e67ed'),
]

_BASE = Path(__file__).parent.parent.parent


@pytest.mark.parametrize("rel_path,sha_prefix", FROZEN, ids=[p for p, _ in FROZEN])
def test_frozen_file_unchanged_w6(rel_path, sha_prefix):
    """الملفات المجمَّدة لا تتغير خلال W6."""
    full = _BASE / rel_path
    content = full.read_bytes()
    actual = hashlib.sha256(content).hexdigest()
    assert actual.startswith(sha_prefix), (
        f"{rel_path}: sha256={actual[:16]} — المتوقع يبدأ بـ {sha_prefix}"
    )
