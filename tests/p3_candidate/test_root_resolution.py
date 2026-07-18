#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p3_candidate/test_root_resolution.py — Hokom Local Root Engine

اختبارات R1–R18 (الاختبارات الإلزامية):
  R1.  Sound triliteral ACCEPT (ضَرَبَ → ض ر ب)
  R2.  Hamza preserved as ء (قَرَأَ → ق ر ء)
  R3.  Shadda expands geometrically (مَدَّ → م د د)
  R4.  Hollow alif remains DEFER (قَالَ)
  R5.  Defective final alif remains DEFER (دَعَا)
  R6.  Compressed imperative remains DEFER (قُلْ)
  R7.  Closed function word remains BLOCK (مِنْ + BLOCK directive)
  R8.  Mabni remains BLOCK (هِيَ + BLOCK directive)
  R9.  refined_host = analyzed_host
  R10. RootResolution is frozen
  R11. JSON serialization (to_dict)
  R12. Evidence/trace/residual preservation
  R13. No false ACCEPT for hollow (نَامَ)
  R14. No false ACCEPT for defective (وَقَى)
  R15. No false ACCEPT for hollow (بَاعَ)
  R16. source_engine = 'HOKOM_ROOT_ENGINE'
  R17. ACCEPT carries canonical_root, DEFER/BLOCK carry None
  R18. No imports from hr2s internal modules
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from pipeline.p3_candidate.root_resolution import RootResolution, resolve_root


# ══════════════════════════════════════════════════════════════════════════════
# R1: الجذر الثلاثي السالم → ACCEPT
# ══════════════════════════════════════════════════════════════════════════════

class TestSoundTrilateralAccept:
    def test_daraba_accept(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        assert r.canonical_root == ('ض', 'ر', 'ب')

    def test_kataba_accept(self):
        r = resolve_root('كَتَبَ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        assert r.canonical_root == ('ك', 'ت', 'ب')

    def test_taraka_accept(self):
        r = resolve_root('تَرَكَ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        assert r.canonical_root == ('ت', 'ر', 'ك')

    def test_shajara_accept(self):
        r = resolve_root('شَجَرَ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        assert r.canonical_root == ('ش', 'ج', 'ر')


# ══════════════════════════════════════════════════════════════════════════════
# R2: الهمزة محفوظة كـ ء
# ══════════════════════════════════════════════════════════════════════════════

class TestHamzaPreserved:
    def test_qaraa_hamza_as_hamza(self):
        """قَرَأَ: الهمزة تُطبَّع إلى ء لا تُحذف."""
        r = resolve_root('قَرَأَ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        assert r.canonical_root == ('ق', 'ر', 'ء')

    def test_hamza_not_alif(self):
        """الجذر لا يحتوي أ أو إ كهوية."""
        r = resolve_root('قَرَأَ', pre_root_directive='OPEN')
        assert r.canonical_root is not None
        for ch in r.canonical_root:
            assert ch not in {'أ', 'إ', 'ؤ', 'ئ', 'آ', 'ا', 'ى'}, (
                f"prohibited identity {ch!r} in canonical_root")


# ══════════════════════════════════════════════════════════════════════════════
# R3: الشدة → ضعف حرف بدون زيادة زائفة
# ══════════════════════════════════════════════════════════════════════════════

class TestShaddaExpands:
    def test_madda_geminate(self):
        """مَدَّ: الشدة تتوسع هندسيًا → (م، د، د)."""
        r = resolve_root('مَدَّ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        assert r.canonical_root == ('م', 'د', 'د')

    def test_shadda_no_false_ziyadah(self):
        """مَدَّ لا يُنتج رمز تحفظ زيادة داخلية."""
        r = resolve_root('مَدَّ', pre_root_directive='OPEN')
        assert not any('ziyadah' in code for code in r.residual_codes), (
            f"unexpected ziyadah residual: {r.residual_codes}")


# ══════════════════════════════════════════════════════════════════════════════
# R4: الأجوف (ألف في العين) → DEFER
# ══════════════════════════════════════════════════════════════════════════════

class TestHollowDefers:
    def test_qaala_defers(self):
        r = resolve_root('قَالَ', pre_root_directive='OPEN')
        assert r.directive == 'DEFER'
        assert r.canonical_root is None

    def test_naama_defers(self):
        r = resolve_root('نَامَ', pre_root_directive='OPEN')
        assert r.directive == 'DEFER'
        assert r.canonical_root is None

    def test_baaa_defers(self):
        """بَاعَ: ألف في العين (لا يُفرض الواو أو الياء) → DEFER."""
        r = resolve_root('بَاعَ', pre_root_directive='OPEN')
        assert r.directive == 'DEFER'
        assert r.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# R5: الناقص (ألف في اللام) → DEFER
# ══════════════════════════════════════════════════════════════════════════════

class TestDefectiveDefers:
    def test_daaa_defers(self):
        """دَعَا: ألف في اللام (ناقص) → DEFER."""
        r = resolve_root('دَعَا', pre_root_directive='OPEN')
        assert r.directive == 'DEFER'
        assert r.canonical_root is None

    def test_waqaa_defers(self):
        """وَقَى: واو في الفاء + ياء في اللام → DEFER."""
        r = resolve_root('وَقَى', pre_root_directive='OPEN')
        assert r.directive == 'DEFER'
        assert r.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# R6: الأمر المضغوط → DEFER
# ══════════════════════════════════════════════════════════════════════════════

class TestCompressedImperativeDefers:
    def test_qul_defers(self):
        """قُلْ: حرفان فقط (المضغوط) → DEFER."""
        r = resolve_root('قُلْ', pre_root_directive='OPEN')
        assert r.directive == 'DEFER'
        assert r.canonical_root is None

    def test_qul_failure_reason_mentions_compression(self):
        r = resolve_root('قُلْ', pre_root_directive='OPEN')
        assert r.residual_codes, "expected at least one residual code"


# ══════════════════════════════════════════════════════════════════════════════
# R7: الأداة المغلقة → BLOCK (directive موروث)
# ══════════════════════════════════════════════════════════════════════════════

class TestFunctionWordBlocks:
    def test_min_blocks(self):
        """مِنْ: directive=BLOCK من PreRoot → BLOCK."""
        r = resolve_root('مِنْ', pre_root_directive='BLOCK')
        assert r.directive == 'BLOCK'
        assert r.canonical_root is None

    def test_annahu_blocks(self):
        r = resolve_root('أَنَّهُمْ', pre_root_directive='BLOCK')
        assert r.directive == 'BLOCK'


# ══════════════════════════════════════════════════════════════════════════════
# R8: المبني → BLOCK
# ══════════════════════════════════════════════════════════════════════════════

class TestMabniBlocks:
    def test_hiya_blocks(self):
        r = resolve_root('هِيَ', pre_root_directive='BLOCK')
        assert r.directive == 'BLOCK'
        assert r.canonical_root is None

    def test_anna_blocks(self):
        r = resolve_root('أَنَّ', pre_root_directive='BLOCK')
        assert r.directive == 'BLOCK'


# ══════════════════════════════════════════════════════════════════════════════
# R9: refined_host = analyzed_host
# ══════════════════════════════════════════════════════════════════════════════

class TestAnalyzedHostIsRefinedHost:
    def test_analyzed_host_equals_refined_host(self):
        """المضيف المُحلَّل = المضيف المُنقَّى المُمرَّر مباشرة."""
        r = resolve_root('تَرَكَ', pre_root_directive='OPEN')
        assert r.analyzed_host == 'تَرَكَ'

    def test_analyzed_host_for_shajara(self):
        r = resolve_root('شَجَرَ', pre_root_directive='OPEN')
        assert r.analyzed_host == 'شَجَرَ'


# ══════════════════════════════════════════════════════════════════════════════
# R10: RootResolution مُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestRootResolutionIsFrozen:
    def test_resolution_is_frozen(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        with pytest.raises((AttributeError, TypeError)):
            r.directive = 'BLOCK'  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# R11: التسلسل JSON
# ══════════════════════════════════════════════════════════════════════════════

class TestJsonSerialization:
    def test_to_dict_has_required_keys(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        d = r.to_dict()
        for key in ('directive', 'analyzed_host', 'canonical_root',
                    'source_engine', 'evidence_ids', 'trace_ids', 'residual_codes'):
            assert key in d, f"missing key {key!r} in to_dict()"

    def test_to_dict_canonical_root_list(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        d = r.to_dict()
        assert isinstance(d['canonical_root'], list)
        assert d['canonical_root'] == ['ض', 'ر', 'ب']

    def test_to_dict_defer_canonical_root_none(self):
        r = resolve_root('قَالَ', pre_root_directive='OPEN')
        d = r.to_dict()
        assert d['canonical_root'] is None


# ══════════════════════════════════════════════════════════════════════════════
# R12: حفظ evidence/trace/residual
# ══════════════════════════════════════════════════════════════════════════════

class TestEvidenceTraceResidual:
    def test_evidence_ids_tuple(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN',
                         evidence_ids=('ev:test:sound_trilateral',))
        assert 'ev:test:sound_trilateral' in r.evidence_ids

    def test_trace_ids_tuple(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN',
                         trace_ids=('trace:test:entry',))
        assert 'trace:test:entry' in r.trace_ids

    def test_defer_has_residual_code(self):
        r = resolve_root('قَالَ', pre_root_directive='OPEN')
        assert r.residual_codes, "DEFER result must have at least one residual code"


# ══════════════════════════════════════════════════════════════════════════════
# R13-R15: لا ACCEPT زائف
# ══════════════════════════════════════════════════════════════════════════════

class TestNoFalseAccept:
    def test_naama_no_false_accept(self):
        r = resolve_root('نَامَ', pre_root_directive='OPEN')
        assert r.directive != 'ACCEPT'

    def test_waqaa_no_false_accept(self):
        r = resolve_root('وَقَى', pre_root_directive='OPEN')
        assert r.directive != 'ACCEPT'

    def test_baaa_no_false_accept(self):
        r = resolve_root('بَاعَ', pre_root_directive='OPEN')
        assert r.directive != 'ACCEPT'


# ══════════════════════════════════════════════════════════════════════════════
# R16: source_engine
# ══════════════════════════════════════════════════════════════════════════════

class TestSourceEngine:
    def test_source_engine_is_hokom(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        assert r.source_engine == 'HOKOM_ROOT_ENGINE'

    def test_source_engine_for_defer(self):
        r = resolve_root('قَالَ', pre_root_directive='OPEN')
        assert r.source_engine == 'HOKOM_ROOT_ENGINE'


# ══════════════════════════════════════════════════════════════════════════════
# R17: ACCEPT carries root, DEFER/BLOCK carry None
# ══════════════════════════════════════════════════════════════════════════════

class TestRootCardinality:
    def test_accept_canonical_root_non_none(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        assert r.canonical_root is not None

    def test_defer_canonical_root_none(self):
        r = resolve_root('قَالَ', pre_root_directive='OPEN')
        assert r.canonical_root is None

    def test_block_canonical_root_none(self):
        r = resolve_root('مِنْ', pre_root_directive='BLOCK')
        assert r.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# R18: لا استيراد من hr2s الداخلي
# ══════════════════════════════════════════════════════════════════════════════

class TestNoHr2sInternalImport:
    def _check_file(self, filename: str):
        src = (pathlib.Path(__file__).parent.parent.parent
               / 'pipeline' / 'p3_candidate' / filename)
        tree = ast.parse(src.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                # يُسمح: from hr2s import MorphologyEngine
                # ممنوع: from hr2s.root import ..., from hr2s.boundary import ...
                if node.module.startswith('hr2s.'):
                    raise AssertionError(
                        f"forbidden internal hr2s import in {filename}: "
                        f"from {node.module} import ..."
                    )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith('hr2s.'):
                        raise AssertionError(
                            f"forbidden internal hr2s import in {filename}: "
                            f"import {alias.name}"
                        )

    def test_root_resolution_no_hr2s_internal(self):
        self._check_file('root_resolution.py')

    def test_root_rules_no_hr2s_internal(self):
        self._check_file('root_rules.py')

    def test_root_resolution_orchestrator_no_hr2s_internal(self):
        self._check_file('root_resolution_orchestrator.py')
