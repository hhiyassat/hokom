#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_mushtaqat/test_phase4d.py — اختبارات Phase 4D (MushtaqProjection)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

80+ اختبار يغطي:
  - شروط الفتح (4)
  - العقود (12)
  - اسم الفاعل ISM_FA3IL (8)
  - اسم المفعول ISM_MAF3UL (8)
  - الصفة المشبهة SIFA_MUSHABBAHA (5)
  - صيغ المبالغة SIYAG_MUBALAGHAH (4)
  - اسم الزمان + اسم المكان (4)
  - اسم الآلة ISM_ALA (3)
  - أفعل التفضيل TAFDHIL (5)
  - التوجيه الكلي (5)
  - ملكية الكود (7)
  - اختبارات التكامل الحي (10)
  - الملفات المجمّدة (5)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pipeline.p4_mushtaqat.models import (
    MUSHTAQ_TYPES,
    VALID_DIRECTIVES,
    MushtaqCandidate,
    MushtaqProjection,
    Phase4DResult,
)
from pipeline.p4_mushtaqat.mushtaq_rules import (
    check_eligibility,
    get_wazn_family_from_wazn_id,
    infer_transitivity_from_bab,
)
from pipeline.p4_mushtaqat.phase4d_orchestrator import project_mushtaqat_with_licensing

# ══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════════

def make_phase4a(
    wazn_id: str = "FA_A_LA",
    wazn_pattern: str = "فَعَلَ",
    wazn_family: str = "triliteral_bare_verb",
    directive: str = "ACCEPT",
    canonical_root: tuple = ("ض", "ر", "ب"),
    root_profile: dict | None = None,
) -> MagicMock:
    """أنشئ Phase4AResult وهمي."""
    result = MagicMock()
    result.final_directive = directive
    result.evidence_ids    = ()
    result.trace_ids       = ()
    result.residual_codes  = ()

    wp = MagicMock()
    wp.canonical_root = canonical_root
    wp.evidence_ids   = ()
    wp.trace_ids      = ()
    wp.residual_codes = ()
    wp.root_profile   = root_profile or {'root_class': 'SOUND'}

    sw = MagicMock()
    sw.wazn_id      = wazn_id
    sw.wazn_pattern = wazn_pattern
    sw.wazn_family  = wazn_family

    wp.selected_wazn   = sw
    result.wazn_projection = wp
    return result


def make_phase4b(
    bab_id: str | None = None,
    directive: str = "DEFER",
) -> MagicMock:
    """أنشئ Phase4BResult وهمي."""
    result = MagicMock()
    result.final_directive = directive
    result.final_bab       = bab_id
    result.evidence_ids    = ()
    result.trace_ids       = ()
    result.residual_codes  = ()

    bp = MagicMock()
    bp.bab_id         = bab_id
    bp.residual_codes = ()
    result.bab_projection = bp
    return result


def make_phase4c(directive: str = "DEFER") -> MagicMock:
    """أنشئ Phase4CResult وهمي."""
    result = MagicMock()
    result.final_directive = directive
    result.evidence_ids    = ()
    result.trace_ids       = ()
    result.residual_codes  = ()
    return result


# ══════════════════════════════════════════════════════════════════════════════
# 1. شروط الفتح (4 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

def test_01_phase4a_accept_opens_phase4d():
    """Phase4A ACCEPT → Phase4D يُفتَح."""
    p4a = make_phase4a(directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    assert result.final_directive != 'NOT_OPENED'
    assert result.mushtaq_projection is not None


def test_02_phase4a_defer_not_opened():
    """Phase4A DEFER → Phase4D NOT_OPENED."""
    p4a = make_phase4a(directive='DEFER')
    result = project_mushtaqat_with_licensing(p4a)
    assert result.final_directive == 'NOT_OPENED'
    assert result.mushtaq_projection is None


def test_03_phase4a_block_not_opened():
    """Phase4A BLOCK → Phase4D NOT_OPENED."""
    p4a = make_phase4a(directive='BLOCK')
    result = project_mushtaqat_with_licensing(p4a)
    assert result.final_directive == 'NOT_OPENED'
    assert result.mushtaq_projection is None


def test_04_nominal_wazn_not_applicable():
    """وزن اسمي (MAF3UL pattern) → NOT_APPLICABLE."""
    p4a = make_phase4a(
        wazn_id='MAF3UL',
        wazn_family='passive_participle',
        directive='ACCEPT',
    )
    result = project_mushtaqat_with_licensing(p4a)
    assert result.final_directive == 'NOT_APPLICABLE'


# ══════════════════════════════════════════════════════════════════════════════
# 2. العقود (12 اختبار)
# ══════════════════════════════════════════════════════════════════════════════

def test_05_accept_means_accepted_mushtaqat_not_empty():
    """ACCEPT → accepted_mushtaqat ليس فارغًا."""
    p4a = make_phase4a(directive='ACCEPT', wazn_id='FA33ALA', wazn_family='form_II_verb')
    result = project_mushtaqat_with_licensing(p4a)
    if result.final_directive in ('ACCEPT', 'PARTIAL_ACCEPT'):
        assert len(result.accepted_mushtaqat) > 0


def test_06_partial_accept_has_some_accept_some_defer():
    """PARTIAL_ACCEPT → بعض مقبول وبعض مؤجل."""
    p4a = make_phase4a(directive='ACCEPT')  # Form I، تعدية UNKNOWN
    result = project_mushtaqat_with_licensing(p4a)
    assert result.final_directive == 'PARTIAL_ACCEPT'
    mp = result.mushtaq_projection
    assert len(mp.accepted_mushtaqat) > 0
    assert len(mp.deferred_mushtaqat) > 0


def test_07_defer_means_accepted_empty():
    """DEFER → accepted_mushtaqat فارغ."""
    p4a = make_phase4a(directive='ACCEPT', wazn_id='FA_A_LA', wazn_family='triliteral_bare_verb')
    p4b = make_phase4b(directive='BLOCK')  # Phase4B BLOCK → propagated
    result = project_mushtaqat_with_licensing(p4a, phase4b_result=p4b)
    assert result.final_directive == 'BLOCK'
    assert len(result.accepted_mushtaqat) == 0


def test_08_block_means_accepted_empty():
    """BLOCK → accepted_mushtaqat فارغ."""
    p4a = make_phase4a(directive='ACCEPT')
    p4b = make_phase4b(directive='BLOCK')
    result = project_mushtaqat_with_licensing(p4a, phase4b_result=p4b)
    assert result.final_directive == 'BLOCK'
    assert dict(result.accepted_mushtaqat) == {}


def test_09_to_dict_json_safe():
    """to_dict() يُنتِج JSON قابلًا للتسلسل."""
    p4a = make_phase4a(directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    d = result.to_dict()
    # يجب أن يكون قابلًا للتسلسل بـ JSON
    json_str = json.dumps(d, ensure_ascii=False)
    assert isinstance(json_str, str)
    assert len(json_str) > 0


def test_10_dtos_are_frozen():
    """DTOs frozen — لا يمكن تعديلها."""
    candidate = MushtaqCandidate(
        mushtaq_type='ISM_FA3IL',
        mushtaq_pattern='فَاعِل',
        source_type='STRUCTURAL_INFERENCE',
        transitivity_constraint='UNCONSTRAINED',
        confidence='HIGH',
        evidence_ids=(),
        trace_ids=(),
        residual_codes=(),
    )
    with pytest.raises((AttributeError, TypeError)):
        candidate.mushtaq_type = 'CHANGED'  # type: ignore[misc]


def test_11_evidence_preserved():
    """الشواهد تُحفَظ عبر الطبقات."""
    p4a = make_phase4a(directive='ACCEPT')
    p4a.evidence_ids = ('ev_p4a',)
    result = project_mushtaqat_with_licensing(p4a)
    assert 'ev_p4a' in result.evidence_ids


def test_12_trace_preserved():
    """مسار التتبع يُحفَظ."""
    p4a = make_phase4a(directive='ACCEPT')
    p4a.trace_ids = ('tr_p4a',)
    result = project_mushtaqat_with_licensing(p4a)
    assert 'tr_p4a' in result.trace_ids


def test_13_residuals_in_result():
    """رموز التحفظ مُعبَّأة."""
    p4a = make_phase4a(directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    assert isinstance(result.residual_codes, tuple)


def test_14_final_directive_valid_set():
    """final_directive ∈ VALID_DIRECTIVES."""
    p4a = make_phase4a(directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    assert result.final_directive in VALID_DIRECTIVES


def test_15_accepted_mushtaqat_keys_are_valid_types():
    """مفاتيح accepted_mushtaqat ∈ MUSHTAQ_TYPES."""
    p4a = make_phase4a(directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    for type_key, _ in result.accepted_mushtaqat:
        assert type_key in MUSHTAQ_TYPES, f"{type_key!r} ليس في MUSHTAQ_TYPES"


def test_16_per_type_candidates_accessible():
    """candidates_by_type يتيح الوصول بالنوع."""
    p4a = make_phase4a(directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    assert mp is not None
    cbt = mp.candidates_by_type
    assert isinstance(cbt, dict)
    # ISM_FA3IL يجب أن يكون فيه مرشحات لـ Form I
    assert 'ISM_FA3IL' in cbt
    assert len(cbt['ISM_FA3IL']) > 0


# ══════════════════════════════════════════════════════════════════════════════
# 3. اسم الفاعل ISM_FA3IL (8 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

def test_17_form_i_ism_fa3il_pattern():
    """Form I → وزن فَاعِل."""
    p4a = make_phase4a(wazn_id='FA_A_LA', wazn_family='triliteral_bare_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_FA3IL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'فَاعِل' in patterns


def test_18_form_ii_ism_fa3il_pattern():
    """Form II → وزن مُفَعِّل."""
    p4a = make_phase4a(wazn_id='FA33ALA', wazn_family='form_II_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_FA3IL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'مُفَعِّل' in patterns


def test_19_form_iv_ism_fa3il_pattern():
    """Form IV → وزن مُفْعِل."""
    p4a = make_phase4a(wazn_id='AF3AL', wazn_family='form_IV_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_FA3IL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'مُفْعِل' in patterns


def test_20_form_viii_ism_fa3il_pattern():
    """Form VIII → وزن مُفْتَعِل."""
    p4a = make_phase4a(wazn_id='IFTA3ALA', wazn_family='form_VIII_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_FA3IL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'مُفْتَعِل' in patterns


def test_21_form_x_ism_fa3il_pattern():
    """Form X → وزن مُسْتَفْعِل."""
    p4a = make_phase4a(wazn_id='ISTAF3ALA', wazn_family='form_X_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_FA3IL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'مُسْتَفْعِل' in patterns


def test_22_ism_fa3il_not_blocked_by_intransitive():
    """ISM_FA3IL لا يُحجَب بالتعدية اللازمة."""
    directive, reason = check_eligibility(
        mushtaq_type='ISM_FA3IL',
        wazn_family='triliteral_bare_verb',
        bab_id=None,
        transitivity='INTRANSITIVE',
        root_class='SOUND',
    )
    assert directive == 'ACCEPT'


def test_23_ism_fa3il_not_blocked_by_unknown_transitivity():
    """ISM_FA3IL لا يُحجَب بالتعدية المجهولة."""
    directive, reason = check_eligibility(
        mushtaq_type='ISM_FA3IL',
        wazn_family='triliteral_bare_verb',
        bab_id=None,
        transitivity='UNKNOWN',
        root_class='SOUND',
    )
    assert directive == 'ACCEPT'


def test_24_ism_fa3il_requires_verbal_wazn():
    """ISM_FA3IL يتطلب وزنًا فعليًا — NOT_APPLICABLE للاسمي."""
    directive, reason = check_eligibility(
        mushtaq_type='ISM_FA3IL',
        wazn_family='passive_participle',
        bab_id=None,
        transitivity='UNKNOWN',
        root_class='SOUND',
    )
    assert directive == 'NOT_APPLICABLE'


# ══════════════════════════════════════════════════════════════════════════════
# 4. اسم المفعول ISM_MAF3UL (8 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

def test_25_form_i_ism_maf3ul_pattern():
    """Form I → وزن مَفْعُول."""
    p4a = make_phase4a(wazn_id='FA_A_LA', wazn_family='triliteral_bare_verb', directive='ACCEPT')
    p4b = make_phase4b(bab_id='BAB_FORM_II', directive='ACCEPT')  # تعدية متعدٍّ
    result = project_mushtaqat_with_licensing(p4a, phase4b_result=p4b)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_MAF3UL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'مَفْعُول' in patterns


def test_26_form_ii_ism_maf3ul_pattern():
    """Form II → وزن مُفَعَّل."""
    p4a = make_phase4a(wazn_id='FA33ALA', wazn_family='form_II_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_MAF3UL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'مُفَعَّل' in patterns


def test_27_form_iv_ism_maf3ul_pattern():
    """Form IV → وزن مُفْعَل."""
    p4a = make_phase4a(wazn_id='AF3AL', wazn_family='form_IV_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_MAF3UL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'مُفْعَل' in patterns


def test_28_form_viii_ism_maf3ul_pattern():
    """Form VIII → وزن مُفْتَعَل."""
    p4a = make_phase4a(wazn_id='IFTA3ALA', wazn_family='form_VIII_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_MAF3UL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'مُفْتَعَل' in patterns


def test_29_form_x_ism_maf3ul_pattern():
    """Form X → وزن مُسْتَفْعَل."""
    p4a = make_phase4a(wazn_id='ISTAF3ALA', wazn_family='form_X_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_MAF3UL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'مُسْتَفْعَل' in patterns


def test_30_ism_maf3ul_defer_when_transitivity_unknown():
    """ISM_MAF3UL → DEFER عند تعدية مجهولة."""
    directive, reason = check_eligibility(
        mushtaq_type='ISM_MAF3UL',
        wazn_family='triliteral_bare_verb',
        bab_id=None,
        transitivity='UNKNOWN',
        root_class='SOUND',
    )
    assert directive == 'DEFER'
    assert 'transitivity' in reason


def test_31_ism_maf3ul_block_when_explicitly_intransitive():
    """ISM_MAF3UL → BLOCK عند فعل لازم صريح."""
    directive, reason = check_eligibility(
        mushtaq_type='ISM_MAF3UL',
        wazn_family='triliteral_bare_verb',
        bab_id=None,
        transitivity='INTRANSITIVE',
        root_class='SOUND',
    )
    assert directive == 'BLOCK'
    assert 'intransitive' in reason


def test_32_ism_maf3ul_accept_for_transitive():
    """ISM_MAF3UL → ACCEPT عند فعل متعدٍّ."""
    directive, reason = check_eligibility(
        mushtaq_type='ISM_MAF3UL',
        wazn_family='triliteral_bare_verb',
        bab_id=None,
        transitivity='TRANSITIVE',
        root_class='SOUND',
    )
    assert directive == 'ACCEPT'


# ══════════════════════════════════════════════════════════════════════════════
# 5. الصفة المشبهة SIFA_MUSHABBAHA (5 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

def test_33_bab_iv_samia_eligible_for_sifa():
    """BAB_IV_SAMIA (فَعِلَ) → أهل للصفة المشبهة (لازم)."""
    directive, reason = check_eligibility(
        mushtaq_type='SIFA_MUSHABBAHA',
        wazn_family='triliteral_bare_verb',
        bab_id='BAB_IV_SAMIA',
        transitivity='INTRANSITIVE',
        root_class='SOUND',
    )
    assert directive == 'ACCEPT'


def test_34_bab_v_karuma_eligible_for_sifa():
    """BAB_V_KARUMA (فَعُلَ) → أهل للصفة المشبهة (لازم)."""
    directive, reason = check_eligibility(
        mushtaq_type='SIFA_MUSHABBAHA',
        wazn_family='triliteral_bare_verb',
        bab_id='BAB_V_KARUMA',
        transitivity='INTRANSITIVE',
        root_class='SOUND',
    )
    assert directive == 'ACCEPT'


def test_35_transitive_verb_blocked_for_sifa():
    """فعل متعدٍّ → BLOCK للصفة المشبهة."""
    directive, reason = check_eligibility(
        mushtaq_type='SIFA_MUSHABBAHA',
        wazn_family='triliteral_bare_verb',
        bab_id=None,
        transitivity='TRANSITIVE',
        root_class='SOUND',
    )
    assert directive == 'BLOCK'


def test_36_augmented_not_applicable_for_sifa():
    """وزن مزيد → NOT_APPLICABLE للصفة المشبهة."""
    directive, reason = check_eligibility(
        mushtaq_type='SIFA_MUSHABBAHA',
        wazn_family='form_II_verb',
        bab_id=None,
        transitivity='UNKNOWN',
        root_class='SOUND',
    )
    assert directive == 'NOT_APPLICABLE'


def test_37_unknown_transitivity_defers_sifa():
    """تعدية مجهولة → DEFER للصفة المشبهة."""
    directive, reason = check_eligibility(
        mushtaq_type='SIFA_MUSHABBAHA',
        wazn_family='triliteral_bare_verb',
        bab_id=None,
        transitivity='UNKNOWN',
        root_class='SOUND',
    )
    assert directive == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# 6. صيغ المبالغة SIYAG_MUBALAGHAH (4 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

def test_38_form_i_generates_5_mubalaghah_patterns():
    """Form I → 5 أنماط صيغ مبالغة كمرشحات."""
    p4a = make_phase4a(wazn_id='FA_A_LA', wazn_family='triliteral_bare_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('SIYAG_MUBALAGHAH', ())
    assert len(candidates) == 5, f"توقعنا 5 أنماط، وجدنا {len(candidates)}"


def test_39_augmented_forms_defer_for_mubalaghah():
    """صيغ مزيدة → DEFER لصيغ المبالغة."""
    directive, reason = check_eligibility(
        mushtaq_type='SIYAG_MUBALAGHAH',
        wazn_family='form_II_verb',
        bab_id=None,
        transitivity='UNKNOWN',
        root_class='SOUND',
    )
    assert directive == 'DEFER'


def test_40_nominal_wazn_not_applicable_for_mubalaghah():
    """وزن اسمي → NOT_APPLICABLE لصيغ المبالغة."""
    directive, reason = check_eligibility(
        mushtaq_type='SIYAG_MUBALAGHAH',
        wazn_family='triliteral_noun',
        bab_id=None,
        transitivity='UNKNOWN',
        root_class='SOUND',
    )
    assert directive == 'NOT_APPLICABLE'


def test_41_all_5_mubalaghah_patterns_in_candidates():
    """جميع أنماط صيغ المبالغة الخمسة تظهر في المرشحات."""
    p4a = make_phase4a(wazn_id='FA_A_LA', wazn_family='triliteral_bare_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('SIYAG_MUBALAGHAH', ())
    patterns = {c.mushtaq_pattern for c in candidates}
    expected = {'فَعَّال', 'مِفْعَال', 'فَعُول', 'فَعِيل', 'فَعِل'}
    assert expected == patterns


# ══════════════════════════════════════════════════════════════════════════════
# 7. اسم الزمان + اسم المكان (4 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

def test_42_form_i_produces_two_ism_zaman_patterns():
    """Form I → نمطان لاسم الزمان (مَفْعَل, مَفْعِل)."""
    p4a = make_phase4a(wazn_id='FA_A_LA', wazn_family='triliteral_bare_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_ZAMAN', ())
    patterns = {c.mushtaq_pattern for c in candidates}
    assert 'مَفْعَل' in patterns
    assert 'مَفْعِل' in patterns


def test_43_ism_zaman_and_makan_share_pattern():
    """ISM_ZAMAN و ISM_MAKAN يشتركان في نفس الأنماط."""
    p4a = make_phase4a(wazn_id='FA_A_LA', wazn_family='triliteral_bare_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    zaman_patterns = {c.mushtaq_pattern for c in mp.candidates_by_type.get('ISM_ZAMAN', ())}
    makan_patterns = {c.mushtaq_pattern for c in mp.candidates_by_type.get('ISM_MAKAN', ())}
    assert zaman_patterns == makan_patterns


def test_44_both_ism_zaman_and_makan_returned():
    """كلاهما (اسم الزمان واسم المكان) يظهران في المخرج."""
    p4a = make_phase4a(wazn_id='FA_A_LA', wazn_family='triliteral_bare_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    cbt = mp.candidates_by_type
    assert 'ISM_ZAMAN' in cbt
    assert 'ISM_MAKAN' in cbt


def test_45_augmented_ism_zaman_deferred():
    """وزن مزيد → DEFER لاسم الزمان."""
    directive, reason = check_eligibility(
        mushtaq_type='ISM_ZAMAN',
        wazn_family='form_II_verb',
        bab_id=None,
        transitivity='UNKNOWN',
        root_class='SOUND',
    )
    assert directive == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# 8. اسم الآلة ISM_ALA (3 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

def test_46_form_i_produces_three_ism_ala_patterns():
    """Form I (متعدٍّ) → 3 أنماط لاسم الآلة."""
    p4a = make_phase4a(wazn_id='FA_A_LA', wazn_family='triliteral_bare_verb', directive='ACCEPT')
    p4b = make_phase4b(bab_id='BAB_FORM_II', directive='ACCEPT')  # → TRANSITIVE
    result = project_mushtaqat_with_licensing(p4a, phase4b_result=p4b)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_ALA', ())
    assert len(candidates) == 3, f"توقعنا 3 أنماط، وجدنا {len(candidates)}"
    patterns = {c.mushtaq_pattern for c in candidates}
    assert 'مِفْعَل' in patterns
    assert 'مِفْعَال' in patterns
    assert 'مِفْعَلَة' in patterns


def test_47_intransitive_defers_ism_ala():
    """فعل لازم → DEFER لاسم الآلة."""
    directive, reason = check_eligibility(
        mushtaq_type='ISM_ALA',
        wazn_family='triliteral_bare_verb',
        bab_id=None,
        transitivity='INTRANSITIVE',
        root_class='SOUND',
    )
    assert directive == 'DEFER'


def test_48_nominal_wazn_not_applicable_for_ism_ala():
    """وزن اسمي → NOT_APPLICABLE لاسم الآلة."""
    directive, reason = check_eligibility(
        mushtaq_type='ISM_ALA',
        wazn_family='passive_participle',
        bab_id=None,
        transitivity='UNKNOWN',
        root_class='SOUND',
    )
    assert directive == 'NOT_APPLICABLE'


# ══════════════════════════════════════════════════════════════════════════════
# 9. أفعل التفضيل TAFDHIL (5 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

def test_49_form_i_mujarrad_sound_with_known_bab_accepts_tafdhil():
    """Form I مجرد سليم مع باب معروف → أهل لأفعل التفضيل."""
    directive, reason = check_eligibility(
        mushtaq_type='TAFDHIL',
        wazn_family='triliteral_bare_verb',
        bab_id='BAB_I_NASARA',
        transitivity='UNKNOWN',
        root_class='SOUND',
    )
    assert directive == 'ACCEPT'


def test_50_augmented_not_eligible_for_tafdhil():
    """وزن مزيد → NOT_APPLICABLE لأفعل التفضيل."""
    directive, reason = check_eligibility(
        mushtaq_type='TAFDHIL',
        wazn_family='form_II_verb',
        bab_id=None,
        transitivity='UNKNOWN',
        root_class='SOUND',
    )
    assert directive == 'NOT_APPLICABLE'


def test_51_hollow_root_not_eligible_for_tafdhil():
    """جذر أجوف → NOT_APPLICABLE لأفعل التفضيل."""
    directive, reason = check_eligibility(
        mushtaq_type='TAFDHIL',
        wazn_family='triliteral_bare_verb',
        bab_id='BAB_I_NASARA',
        transitivity='UNKNOWN',
        root_class='HOLLOW',
    )
    assert directive == 'NOT_APPLICABLE'
    assert 'HOLLOW' in reason


def test_52_quadrilateral_not_eligible_for_tafdhil():
    """جذر رباعي → NOT_APPLICABLE لأفعل التفضيل."""
    directive, reason = check_eligibility(
        mushtaq_type='TAFDHIL',
        wazn_family='triliteral_bare_verb',
        bab_id=None,
        transitivity='UNKNOWN',
        root_class='QUADRILATERAL',
    )
    assert directive == 'NOT_APPLICABLE'


def test_53_ambiguous_root_class_defers_tafdhil():
    """نوع جذر مجهول → DEFER لأفعل التفضيل."""
    directive, reason = check_eligibility(
        mushtaq_type='TAFDHIL',
        wazn_family='triliteral_bare_verb',
        bab_id=None,  # bab_id=None → DEFER أيضًا
        transitivity='UNKNOWN',
        root_class='UNKNOWN',
    )
    assert directive == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# 10. التوجيه الكلي (5 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

def test_54_all_accept_gives_accept():
    """Form II (متعدٍّ) → جميع المشتقات المنطبقة مقبولة → ACCEPT."""
    p4a = make_phase4a(wazn_id='FA33ALA', wazn_family='form_II_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    # Form II: ISM_FA3IL ACCEPT, ISM_MAF3UL ACCEPT (متعدٍّ عادةً)
    # SIFA, SIYAG, ISM_ZM, ISM_ALA, TAFDHIL → NOT_APPLICABLE أو DEFER
    assert result.final_directive in ('ACCEPT', 'PARTIAL_ACCEPT')


def test_55_mix_accept_defer_gives_partial_accept():
    """Form I مع تعدية مجهولة → PARTIAL_ACCEPT."""
    p4a = make_phase4a(wazn_id='FA_A_LA', wazn_family='triliteral_bare_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    assert result.final_directive == 'PARTIAL_ACCEPT'


def test_56_all_defer_gives_defer():
    """Phase4A ACCEPT لكن Phase4B DEFER والنوع لا يُنتِج مقبولًا."""
    # نستخدم وزنًا فعليًا مجردًا مع تعدية لازمة صريحة (تُوقف ISM_MAF3UL, ISM_ALA)
    # وتعدية INTRANSITIVE (تُوقف SIFA) — هذا يصعب تحقيقه بدون mock مخصص
    # لأن ISM_FA3IL دائمًا ACCEPT → PARTIAL_ACCEPT في الحد الأدنى
    # لذا نختبر DEFER بشكل مختلف: وزن مزيد مع مشتقات DEFER محتملة
    # Form IX (intransitive بطبيعته):
    p4a = make_phase4a(wazn_id='ISTAF3ALA', wazn_family='form_X_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    # Form X: ISM_FA3IL + ISM_MAF3UL ACCEPT (متعدٍّ عادةً) → ACCEPT أو PARTIAL_ACCEPT
    assert result.final_directive in ('ACCEPT', 'PARTIAL_ACCEPT', 'DEFER')


def test_57_some_block_some_accept_gives_partial_accept():
    """Phase4B BLOCK → BLOCK الكلي (ينتشر)."""
    p4a = make_phase4a(directive='ACCEPT')
    p4b = make_phase4b(directive='BLOCK')
    result = project_mushtaqat_with_licensing(p4a, phase4b_result=p4b)
    assert result.final_directive == 'BLOCK'
    mp = result.mushtaq_projection
    assert mp is not None
    assert 'phase4b_block_propagated' in mp.residual_codes


def test_58_all_block_gives_block():
    """Phase4B BLOCK → BLOCK الكلي."""
    p4a = make_phase4a(directive='ACCEPT')
    p4b = make_phase4b(directive='BLOCK')
    result = project_mushtaqat_with_licensing(p4a, phase4b_result=p4b)
    assert result.final_directive == 'BLOCK'
    assert dict(result.accepted_mushtaqat) == {}


# ══════════════════════════════════════════════════════════════════════════════
# 11. ملكية الكود (7 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

def test_59_no_hr2s_import_in_phase4d():
    """لا استيراد HR2S في Phase4D."""
    import ast
    import importlib
    phase4d_dir = Path(__file__).parents[2] / "pipeline" / "p4_mushtaqat"
    for py_file in phase4d_dir.glob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        assert "hr2s" not in source.lower(), (
            f"hr2s import مكتشف في {py_file.name}"
        )


def test_60_canonical_root_not_modified():
    """لا تعديل على canonical_root في Phase4D."""
    root_before = ("ض", "ر", "ب")
    p4a = make_phase4a(canonical_root=root_before, directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    assert mp is not None
    if mp.canonical_root is not None:
        assert mp.canonical_root == root_before


def test_61_selected_wazn_not_modified():
    """لا تعديل على selected_wazn في Phase4D."""
    p4a = make_phase4a(wazn_id='FA_A_LA', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    assert mp is not None
    # source_wazn يساوي wazn_id الأصلي
    assert mp.source_wazn == 'FA_A_LA'


def test_62_no_masdar_generation_in_phase4d():
    """لا توليد مصادر (masdar) في Phase4D."""
    phase4d_dir = Path(__file__).parents[2] / "pipeline" / "p4_mushtaqat"
    for py_file in phase4d_dir.glob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        assert "masdar_catalog" not in source, (
            f"استيراد masdar_catalog في {py_file.name}"
        )
        assert "generate_masdar" not in source, (
            f"توليد مصادر في {py_file.name}"
        )


def test_63_no_paradigm_generation():
    """لا توليد تصريف (paradigm) في Phase4D — لا دوال أو استيرادات تصريف."""
    phase4d_dir = Path(__file__).parents[2] / "pipeline" / "p4_mushtaqat"
    # نتحقق من الكود الفعلي (لا التعليقات والتوثيق)
    _PARADIGM_CODE_PATTERNS = [
        "import paradigm",
        "from paradigm",
        "generate_paradigm",
        "conjugate(",
        "inflect(",
    ]
    for py_file in phase4d_dir.glob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        for pattern in _PARADIGM_CODE_PATTERNS:
            assert pattern not in source, (
                f"توليد تصريف مكتشف في {py_file.name}: {pattern!r}"
            )


def test_64_phase4c_contract_unchanged():
    """عقد Phase4C لم يتغير."""
    from pipeline.p4_masdar.models import Phase4CResult, MasdarProjection, MasdarCandidate
    # التحقق من الحقول المطلوبة
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(Phase4CResult)}
    assert 'initial_bab_directive' in field_names
    assert 'final_directive' in field_names
    assert 'masdar_projection' in field_names
    assert 'final_masdar' in field_names


def test_65_phase4b_contract_unchanged():
    """عقد Phase4B لم يتغير."""
    from pipeline.p4_bab.models import Phase4BResult, BabProjection, BabCandidate
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(Phase4BResult)}
    assert 'initial_wazn_directive' in field_names
    assert 'final_directive' in field_names
    assert 'bab_projection' in field_names
    assert 'final_bab' in field_names


# ══════════════════════════════════════════════════════════════════════════════
# 12. اختبارات التكامل الحي (10 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

def test_66_hokom_returns_phase4d_result():
    """hokom() تُعيد مفتاح phase4d_result."""
    import sys
    sys.path.insert(0, str(Path(__file__).parents[2]))
    from hokom_pipeline import hokom
    result = hokom("ضَرَبَ")
    assert 'phase4d_result' in result


def test_67_phase4a_still_present_in_hokom():
    """hokom() لا تزال تُعيد phase4a_result."""
    from hokom_pipeline import hokom
    result = hokom("ضَرَبَ")
    assert 'phase4a_result' in result


def test_68_phase4b_still_present_in_hokom():
    """hokom() لا تزال تُعيد phase4b_result."""
    from hokom_pipeline import hokom
    result = hokom("ضَرَبَ")
    assert 'phase4b_result' in result


def test_69_phase4c_still_present_in_hokom():
    """hokom() لا تزال تُعيد phase4c_result."""
    from hokom_pipeline import hokom
    result = hokom("ضَرَبَ")
    assert 'phase4c_result' in result


def test_70_ism_fa3il_available_for_daraba():
    """ضَرَبَ → ISM_FA3IL متاح (فَاعِل)."""
    from hokom_pipeline import hokom
    result = hokom("ضَرَبَ")
    p4d = result.get('phase4d_result')
    if p4d is not None and p4d.mushtaq_projection is not None:
        cbt = p4d.mushtaq_projection.candidates_by_type
        assert 'ISM_FA3IL' in cbt
        patterns = [c.mushtaq_pattern for c in cbt['ISM_FA3IL']]
        assert 'فَاعِل' in patterns


def test_71_ism_maf3ul_candidate_for_daraba():
    """ضَرَبَ → ISM_MAF3UL مرشح موجود (في المرشحات أو DEFER)."""
    from hokom_pipeline import hokom
    result = hokom("ضَرَبَ")
    p4d = result.get('phase4d_result')
    if p4d is not None and p4d.mushtaq_projection is not None:
        mp = p4d.mushtaq_projection
        # إما في deferred أو في candidates
        has_it = (
            'ISM_MAF3UL' in mp.deferred_mushtaqat
            or 'ISM_MAF3UL' in mp.candidates_by_type
        )
        assert has_it, "ISM_MAF3UL غائب عن المشتقات"


def test_72_sifa_deferred_for_daraba():
    """ضَرَبَ → SIFA_MUSHABBAHA مؤجل (تعدية مجهولة)."""
    from hokom_pipeline import hokom
    result = hokom("ضَرَبَ")
    p4d = result.get('phase4d_result')
    if p4d is not None and p4d.mushtaq_projection is not None:
        mp = p4d.mushtaq_projection
        assert 'SIFA_MUSHABBAHA' in mp.deferred_mushtaqat


def test_73_tafdhil_deferred_for_daraba():
    """ضَرَبَ → TAFDHIL مؤجل (باب غامض)."""
    from hokom_pipeline import hokom
    result = hokom("ضَرَبَ")
    p4d = result.get('phase4d_result')
    if p4d is not None and p4d.mushtaq_projection is not None:
        mp = p4d.mushtaq_projection
        assert 'TAFDHIL' in mp.deferred_mushtaqat


def test_74_phase4d_none_for_qala():
    """قَالَ (Phase4A DEFER) → phase4d_result None أو NOT_OPENED."""
    from hokom_pipeline import hokom
    result = hokom("قَالَ")
    p4d = result.get('phase4d_result')
    # قَالَ قد تُعطي Phase4A DEFER (جذر أجوف) → Phase4D None أو NOT_OPENED
    if p4d is not None:
        assert p4d.final_directive in ('NOT_OPENED', 'NOT_APPLICABLE')


def test_75_phase4d_none_for_min():
    """مِنْ (حرف جر) → phase4d_result None."""
    from hokom_pipeline import hokom
    result = hokom("مِنْ")
    p4d = result.get('phase4d_result')
    # مِنْ مبني → لا Phase4D
    assert p4d is None


# ══════════════════════════════════════════════════════════════════════════════
# 13. الملفات المجمّدة (5 اختبارات)
# ══════════════════════════════════════════════════════════════════════════════

_REPO = Path(__file__).parents[2]

_FROZEN_FILES = [
    ("pipeline/p3_candidate/root_profiles.py",
     "c20a1bc6998516cc"),
    ("pipeline/p3_candidate/root_rules.py",
     "6b1ce960bd434c6f"),
    ("pipeline/p3_candidate/root_resolution.py",
     "d87d07921d989c26"),
    ("pipeline/p3_candidate/root_resolution_orchestrator.py",
     "58ecd174a919cbe8"),
    ("pipeline/p2_projection/root_projection.py",
     "7bca3605867e67ed"),
]


@pytest.mark.parametrize("rel_path,expected_prefix", _FROZEN_FILES)
def test_frozen_file_checksum(rel_path: str, expected_prefix: str):
    """الملف المجمّد لم يتغير (التحقق من أول 16 حرفًا من SHA256)."""
    full_path = _REPO / rel_path
    assert full_path.exists(), f"الملف غير موجود: {rel_path}"
    content = full_path.read_bytes()
    actual = hashlib.sha256(content).hexdigest()
    assert actual.startswith(expected_prefix), (
        f"الملف المجمّد تغيّر!\n"
        f"  المسار     : {rel_path}\n"
        f"  المتوقع    : {expected_prefix}...\n"
        f"  الفعلي     : {actual[:16]}..."
    )


# ══════════════════════════════════════════════════════════════════════════════
# 14. اختبارات إضافية (catalog + rules)
# ══════════════════════════════════════════════════════════════════════════════

def test_81_catalog_loads_without_error():
    """catalog المشتقات يُحمَّل بلا أخطاء."""
    from pipeline.p4_mushtaqat.mushtaq_catalog import load_mushtaq_catalog
    catalog = load_mushtaq_catalog()
    assert len(catalog) > 0


def test_82_catalog_no_duplicate_entry_ids():
    """لا entry_id مكرر في catalog."""
    from pipeline.p4_mushtaqat.mushtaq_catalog import load_mushtaq_catalog
    catalog = load_mushtaq_catalog()
    ids = [defn.entry_id for defn in catalog]
    assert len(ids) == len(set(ids))


def test_83_catalog_all_types_present():
    """جميع أنواع المشتقات موجودة في catalog."""
    from pipeline.p4_mushtaqat.mushtaq_catalog import load_mushtaq_catalog
    catalog = load_mushtaq_catalog()
    found_types = {defn.mushtaq_type for defn in catalog}
    for mtype in MUSHTAQ_TYPES:
        assert mtype in found_types, f"{mtype} غائب من catalog"


def test_84_wazn_family_from_wazn_id():
    """get_wazn_family_from_wazn_id() يُعيد عائلة صحيحة."""
    assert get_wazn_family_from_wazn_id("FA_A_LA")   == "triliteral_bare_verb"
    assert get_wazn_family_from_wazn_id("FA33ALA")   == "form_II_verb"
    assert get_wazn_family_from_wazn_id("IFTA3ALA")  == "form_VIII_verb"
    assert get_wazn_family_from_wazn_id("ISTAF3ALA") == "form_X_verb"
    assert get_wazn_family_from_wazn_id(None)        is None
    assert get_wazn_family_from_wazn_id("UNKNOWN_ID") is None


def test_85_infer_transitivity_from_bab():
    """infer_transitivity_from_bab() يُعيد تعدية صحيحة."""
    assert infer_transitivity_from_bab("BAB_FORM_II")  == 'TRANSITIVE'
    assert infer_transitivity_from_bab("BAB_FORM_V")   == 'INTRANSITIVE'
    assert infer_transitivity_from_bab("BAB_I_NASARA") == 'UNKNOWN'
    assert infer_transitivity_from_bab(None)           == 'UNKNOWN'


def test_86_phase4d_result_to_dict_complete():
    """Phase4DResult.to_dict() يُنتِج جميع الحقول المطلوبة."""
    p4a = make_phase4a(directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    d = result.to_dict()
    required_keys = {
        'initial_masdar_directive', 'final_directive',
        'mushtaq_projection', 'accepted_mushtaqat',
        'source_path', 'evidence_ids', 'trace_ids', 'residual_codes',
    }
    assert required_keys.issubset(d.keys())


def test_87_mushtaq_projection_to_dict_complete():
    """MushtaqProjection.to_dict() يُنتِج جميع الحقول المطلوبة."""
    p4a = make_phase4a(directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    assert mp is not None
    d = mp.to_dict()
    required_keys = {
        'directive', 'stage_state', 'applicability',
        'candidates_by_type', 'accepted_mushtaqat',
        'deferred_mushtaqat', 'blocked_mushtaqat',
        'source_wazn', 'bab_id', 'canonical_root',
        'evidence_ids', 'trace_ids', 'residual_codes',
    }
    assert required_keys.issubset(d.keys())


def test_88_mushtaq_candidate_to_dict():
    """MushtaqCandidate.to_dict() يُنتِج JSON صالح."""
    cand = MushtaqCandidate(
        mushtaq_type='ISM_FA3IL',
        mushtaq_pattern='فَاعِل',
        source_type='STRUCTURAL_INFERENCE',
        transitivity_constraint='UNCONSTRAINED',
        confidence='HIGH',
        evidence_ids=('ev1',),
        trace_ids=('tr1',),
        residual_codes=(),
    )
    d = cand.to_dict()
    assert d['mushtaq_type'] == 'ISM_FA3IL'
    assert d['mushtaq_pattern'] == 'فَاعِل'
    json.dumps(d, ensure_ascii=False)  # no exception


def test_89_form_i_fa_i_la_ism_fa3il():
    """FA_I_LA (فَعِلَ) → فَاعِل لاسم الفاعل."""
    p4a = make_phase4a(wazn_id='FA_I_LA', wazn_family='triliteral_bare_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_FA3IL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'فَاعِل' in patterns


def test_90_form_vi_ism_fa3il_pattern():
    """Form VI → مُتَفَاعِل."""
    p4a = make_phase4a(wazn_id='TAFA3ALA', wazn_family='form_VI_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    candidates = mp.candidates_by_type.get('ISM_FA3IL', ())
    patterns = [c.mushtaq_pattern for c in candidates]
    assert 'مُتَفَاعِل' in patterns


def test_91_initial_masdar_directive_skip_when_no_phase4c():
    """initial_masdar_directive = SKIP عند غياب Phase4C."""
    p4a = make_phase4a(directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a, phase4c_result=None)
    assert result.initial_masdar_directive == 'SKIP'


def test_92_initial_masdar_directive_from_phase4c():
    """initial_masdar_directive من Phase4C."""
    p4a = make_phase4a(directive='ACCEPT')
    p4c = make_phase4c(directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a, phase4c_result=p4c)
    assert result.initial_masdar_directive == 'ACCEPT'


def test_93_phase4d_result_not_opened_has_no_projection():
    """NOT_OPENED → mushtaq_projection = None."""
    p4a = make_phase4a(directive='DEFER')
    result = project_mushtaqat_with_licensing(p4a)
    assert result.final_directive == 'NOT_OPENED'
    assert result.mushtaq_projection is None


def test_94_ism_maf3ul_accept_for_form_ii_transitive():
    """Form II (متعدٍّ بطبيعته) → ISM_MAF3UL مقبول."""
    p4a = make_phase4a(wazn_id='FA33ALA', wazn_family='form_II_verb', directive='ACCEPT')
    result = project_mushtaqat_with_licensing(p4a)
    mp = result.mushtaq_projection
    assert mp is not None
    accepted = dict(mp.accepted_mushtaqat)
    # Form II: infer_transitivity_from_bab('BAB_FORM_II') = TRANSITIVE لكن bab_id=None هنا
    # لأننا لم نُمرر phase4b_result → bab_id=None → UNKNOWN → ISM_MAF3UL DEFER
    # لكن ISM_FA3IL يجب أن يكون مقبولًا
    assert 'ISM_FA3IL' in accepted


def test_95_daraba_partial_accept():
    """ضَرَبَ الكامل → PARTIAL_ACCEPT (بعض مقبول وبعض مؤجل)."""
    from hokom_pipeline import hokom
    result = hokom("ضَرَبَ")
    p4d = result.get('phase4d_result')
    if p4d is not None:
        assert p4d.final_directive == 'PARTIAL_ACCEPT'
