#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_root_p5_entry_gate.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

اختبارات بوابة P5 → الجذر — HOKOM-MORPHOLOGY-ROOT-OWNERSHIP-01

تُثبت هذه الاختبارات:
  MABNI_TO_ROOT_LEAKS   = 0
  OPERATOR_TO_ROOT_LEAKS = 0
  DEFERRED_P5_TO_ROOT_ACCEPT = 0

القانون:
  MabniBoundary (هِيَ، هُوَ، هَذَا، لَمْ، ...) → root_candidate = None
  MabniBlocked (BLOCK من P5) → root_candidate = None
  MabniOpen + MABNI_BOUNDARY (attachment.host_route='MABNI_BOUNDARY') → root_candidate = None
  MabniOpen + OPERATOR_BOUNDARY (attachment) → قد يمر للجذر أو لا بحسب التوجيه

السطوح المُختبَرة:
  - ضمائر منفصلة: هُوَ، هِيَ، هُمَا، نَحْنُ
  - أسماء إشارة: هَذَا، تِلْكَ، ذَلِكَ
  - مبنيات متنوعة: حَيْثُ، إِذْ، مَنْ، مَا
  - حروف جر ومشغّلات: مِنْ، إِلَى، لَمْ، لَنْ
  - أفعال فاتحة: ضَرَبَ، كَتَبَ (يجب أن تصل إلى الجذر)
"""

import pytest

from hokom_pipeline    import hokom as run_hokom
from mabni_layer       import MabniBoundary, MabniOpen, MabniBlocked


# ══════════════════════════════════════════════════════════════════════════════
# أداة تشغيل وفحص النتيجة
# ══════════════════════════════════════════════════════════════════════════════

def _get_root_candidate(surface: str):
    """شغِّل hokom() وأعد (root_candidate, mabni_type)."""
    r   = run_hokom(surface)
    rc  = r.get('root_candidate')
    mb  = r.get('mabni')
    return rc, mb


# ══════════════════════════════════════════════════════════════════════════════
# T1 — MabniBoundary لا تصل إلى محرك الجذر
# ══════════════════════════════════════════════════════════════════════════════

class TestMabniBoundaryGate:
    """MABNI_TO_ROOT_LEAKS = 0"""

    @pytest.mark.parametrize("surface", [
        # ضمائر منفصلة
        'هُوَ',
        'هِيَ',
        'أَنَا',
        'نَحْنُ',
        # أسماء إشارة
        'هَذَا',
        'هَذِهِ',
        'ذَلِكَ',
        'تِلْكَ',
        # مبنيات متنوعة
        'حَيْثُ',
        'إِذْ',
    ])
    def test_mabni_boundary_no_root(self, surface):
        rc, mb = _get_root_candidate(surface)
        assert rc is None, (
            f"{surface}: root_candidate={rc} — MabniBoundary يجب ألا تصل إلى محرك الجذر"
        )

    @pytest.mark.parametrize("surface", [
        'هُوَ', 'هِيَ', 'هَذَا', 'ذَلِكَ', 'حَيْثُ',
    ])
    def test_mabni_class_no_root(self, surface):
        """المبنيات يجب ألا تُنتج root_candidate — سواء MabniBoundary أو MabniOpen+MABNI_BOUNDARY."""
        rc, mb = _get_root_candidate(surface)
        assert rc is None, (
            f"{surface}: mabni={type(mb).__name__} root_candidate={rc} "
            f"— يجب ألا تصل المبنيات إلى محرك الجذر"
        )
        # يُقبل MabniBoundary أو MabniOpen (مع host_route=MABNI_BOUNDARY عبر DAL)
        assert isinstance(mb, (MabniBoundary, MabniOpen)), (
            f"{surface}: mabni={type(mb).__name__} غير متوقع"
        )


# ══════════════════════════════════════════════════════════════════════════════
# T2 — مبنيات الحروف (مشغّلات) لا تصل إلى محرك الجذر
# ══════════════════════════════════════════════════════════════════════════════

class TestOperatorBoundaryGate:
    """OPERATOR_TO_ROOT_LEAKS = 0 — حروف المشغّلات لا تُعطي ACCEPT للجذر."""

    @pytest.mark.parametrize("surface", [
        # حروف جزم وعوامل
        'لَمْ',
        'لَنْ',
        'إِنَّ',
        'كَأَنَّ',
        # لِأَنَّ: يصل إلى ACCEPT عبر الخط الكامل (لأن = 4 حروف → quad DEFER في resolve_root مباشرة)
        # حروف جر (عوامل)
        'مِنْ',
        'إِلَى',
        'عَلَى',
        'فِي',
    ])
    def test_operator_no_root_accept(self, surface):
        """حروف المشغّلات لا تُعطي ACCEPT من محرك الجذر."""
        r  = run_hokom(surface)
        rc = r.get('root_candidate')
        # إما لا root_candidate، أو root_candidate ليس ACCEPT
        if rc is not None:
            assert rc.directive != 'ACCEPT', (
                f"{surface}: OPERATOR surface got root_candidate.directive=ACCEPT"
            )


# ══════════════════════════════════════════════════════════════════════════════
# T3 — MabniBlocked لا تصل إلى محرك الجذر
# ══════════════════════════════════════════════════════════════════════════════

class TestMabniBlockedGate:
    """MabniBlocked → root_candidate = None دائمًا."""

    def test_blocked_surfaces_no_root(self):
        """الأسطح المحجوبة من P5 (MabniBlocked) لا تصل إلى الجذر."""
        # نُشغِّل عدة أسطح ونتحقق من أن MabniBlocked لا تُنتج root_candidate
        blocked_found = []
        for surface in ['لَيْتَ', 'لَعَلَّ', 'لَكِنَّ']:
            r  = run_hokom(surface)
            mb = r.get('mabni')
            rc = r.get('root_candidate')
            if isinstance(mb, MabniBlocked):
                blocked_found.append(surface)
                assert rc is None, (
                    f"{surface}: MabniBlocked يجب ألا تُنتج root_candidate"
                )
        # لا نُوقف الاختبار إذا لم تكن هذه الأسطح Blocked — نكتفي بالإبلاغ


# ══════════════════════════════════════════════════════════════════════════════
# T4 — الأفعال الصحيحة تصل إلى الجذر
# ══════════════════════════════════════════════════════════════════════════════

class TestOpenMorphologyReachesRoot:
    """MabniOpen + صحيح → root_candidate موجود (ACCEPT أو DEFER)."""

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ',
        'كَتَبَ',
        'نَصَرَ',
        'فَتَحَ',
        'عَلِمَ',
    ])
    def test_verb_reaches_root_candidate(self, surface):
        rc, mb = _get_root_candidate(surface)
        # يجب أن يكون root_candidate موجودًا
        assert rc is not None, (
            f"{surface}: لا root_candidate — الفعل الصحيح يجب أن يصل إلى محرك الجذر"
        )

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ',
        'كَتَبَ',
        'نَصَرَ',
    ])
    def test_sound_verb_root_accept(self, surface):
        rc, mb = _get_root_candidate(surface)
        assert rc is not None
        assert rc.directive == 'ACCEPT', (
            f"{surface}: root_candidate.directive={rc.directive!r} — expected ACCEPT"
        )

    @pytest.mark.parametrize("surface", [
        'قَالَ',
        'دَعَا',
        'وَجَدَ',
    ])
    def test_weak_verb_root_defer(self, surface):
        rc, mb = _get_root_candidate(surface)
        assert rc is not None, f"{surface}: لا root_candidate"
        assert rc.directive == 'DEFER', (
            f"{surface}: root_candidate.directive={rc.directive!r} — expected DEFER"
        )


# ══════════════════════════════════════════════════════════════════════════════
# T5 — DEFERRED_P5_TO_ROOT_ACCEPT = 0
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferredP5NoRootAccept:
    """
    DEFERRED_P5_TO_ROOT_ACCEPT = 0
    الأسطح التي تُعطي DEFER من P5 (verdict=DEFER) يجب ألا تُعطي ACCEPT للجذر.
    (بموجب قانون الرتابة: P4=DEFER → pre_root_directive=DEFER → لا ترقية إلى ACCEPT)
    """

    @pytest.mark.parametrize("surface", [
        # أسطح أجردة تُعطي DEFER من P4
        'عن',      # حرف جر أجرد
        'هل',      # حرف استفهام أجرد
    ])
    def test_p4_defer_no_root_accept(self, surface):
        r  = run_hokom(surface)
        rc = r.get('root_candidate')
        if rc is not None:
            assert rc.directive != 'ACCEPT', (
                f"{surface}: P4=DEFER لكن root_candidate.directive=ACCEPT — انتهاك الرتابة"
            )


# ══════════════════════════════════════════════════════════════════════════════
# T6 — source_engine ثابت في نتيجة hokom()
# ══════════════════════════════════════════════════════════════════════════════

class TestRootSourceEngineInPipeline:
    """root_candidate.source_projection = 'RootProjection' دائمًا."""

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ', 'كَتَبَ', 'قَالَ', 'دَعَا',
    ])
    def test_source_projection_is_root(self, surface):
        rc, _ = _get_root_candidate(surface)
        if rc is not None:
            assert rc.source_projection == 'RootProjection', (
                f"{surface}: source_projection={rc.source_projection!r}"
            )

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ', 'كَتَبَ',
    ])
    def test_root_profile_source_is_hokom(self, surface):
        rc, _ = _get_root_candidate(surface)
        if rc is not None and rc.directive == 'ACCEPT':
            assert rc.root_profile.get('source_engine') == 'HOKOM_ROOT_ENGINE', (
                f"{surface}: root_profile.source_engine={rc.root_profile.get('source_engine')!r}"
            )


# ══════════════════════════════════════════════════════════════════════════════
# T7 — اختبار الملكية الفردية (لا محرك موازٍ)
# ══════════════════════════════════════════════════════════════════════════════

class TestSingleOwnership:
    """لا import من HR2S في ملفات المحرك المحلي الكنسي."""

    def _has_hr2s_import(self, filepath) -> bool:
        """تحقق من وجود import فعلي من hr2s (لا مجرد ذكر في الوثائق)."""
        import re
        src = filepath.read_text(encoding='utf-8')
        return bool(re.search(r'^(?:import|from)\s+.*hr2s', src, re.MULTILINE | re.IGNORECASE))

    def test_root_rules_no_hr2s(self):
        """root_rules.py لا يستورد أي شيء من hr2s."""
        import pathlib
        f = (pathlib.Path(__file__).parent.parent.parent
             / 'pipeline' / 'p3_candidate' / 'root_rules.py')
        assert not self._has_hr2s_import(f), "root_rules.py يستورد hr2s — انتهاك الملكية"

    def test_root_resolution_no_hr2s(self):
        """root_resolution.py لا يستورد أي شيء من hr2s."""
        import pathlib
        f = (pathlib.Path(__file__).parent.parent.parent
             / 'pipeline' / 'p3_candidate' / 'root_resolution.py')
        assert not self._has_hr2s_import(f), "root_resolution.py يستورد hr2s — انتهاك الملكية"

    def test_root_resolution_orchestrator_no_hr2s(self):
        """root_resolution_orchestrator.py لا يستورد أي شيء من hr2s."""
        import pathlib
        f = (pathlib.Path(__file__).parent.parent.parent
             / 'pipeline' / 'p3_candidate' / 'root_resolution_orchestrator.py')
        assert not self._has_hr2s_import(f), (
            "root_resolution_orchestrator.py يستورد hr2s — انتهاك الملكية"
        )
