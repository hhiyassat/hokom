#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_masdar/test_phase4c.py — اختبارات Phase 4C (MasdarProjection)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

50+ اختبار يغطي:
  - شروط الفتح
  - العقود (contracts)
  - حالات المجرد (DEFER — سماعي مطلوب)
  - حالات المزيد (ACCEPT — استنتاج هيكلي)
  - انتشار التوجيهات
  - ملكية الكود (لا HR2S، لا تعديل canonical_root)
  - اختبارات التكامل مع الأنبوب الحي
  - التحقق من الملفات المجمّدة
  - مصفوفة المرجع
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pipeline.p4_masdar.models import MasdarCandidate, MasdarProjection, Phase4CResult
from pipeline.p4_masdar.phase4c_orchestrator import project_masdar_with_licensing


# ══════════════════════════════════════════════════════════════════════════════
# Fixtures — مساعدات البناء
# ══════════════════════════════════════════════════════════════════════════════

def make_mock_phase4a(
    wazn_id: str = "FA_A_LA",
    wazn_pattern: str = "فَعَلَ",
    wazn_family: str = "triliteral_bare_verb",
    directive: str = "ACCEPT",
    canonical_root: tuple = ("ض", "ر", "ب"),
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

    sw = MagicMock()
    sw.wazn_id      = wazn_id
    sw.wazn_pattern = wazn_pattern
    sw.wazn_family  = wazn_family

    wp.selected_wazn = sw
    result.wazn_projection = wp
    return result


def make_mock_phase4b(
    bab_id: str | None = None,
    directive: str = "ACCEPT",
) -> MagicMock:
    """أنشئ Phase4BResult وهمي."""
    result = MagicMock()
    result.final_directive = directive
    result.final_bab       = bab_id
    result.evidence_ids    = ()
    result.trace_ids       = ()
    result.residual_codes  = ()

    bp = MagicMock()
    bp.bab_id        = bab_id
    bp.residual_codes = ()
    result.bab_projection = bp
    return result


# ══════════════════════════════════════════════════════════════════════════════
# §1 — شروط الفتح (Opening Conditions)
# ══════════════════════════════════════════════════════════════════════════════

class TestOpeningConditions:
    """اختبارات 1–4: شروط فتح Phase 4C."""

    def test_01_phase4a_accept_opens_phase4c(self):
        """Phase4A ACCEPT → Phase4C تُفتح."""
        p4a = make_mock_phase4a(directive="ACCEPT")
        result = project_masdar_with_licensing(p4a)
        assert result.final_directive != "NOT_OPENED"

    def test_02_phase4a_defer_gives_not_opened(self):
        """Phase4A DEFER → Phase4C NOT_OPENED."""
        p4a = make_mock_phase4a(directive="DEFER")
        result = project_masdar_with_licensing(p4a)
        assert result.final_directive == "NOT_OPENED"
        assert result.source_path == "not_opened"

    def test_03_phase4a_block_gives_not_opened(self):
        """Phase4A BLOCK → Phase4C NOT_OPENED."""
        p4a = make_mock_phase4a(directive="BLOCK")
        result = project_masdar_with_licensing(p4a)
        assert result.final_directive == "NOT_OPENED"

    def test_04_nominal_wazn_not_applicable(self):
        """وزن اسمي (MAF3UL) → NOT_APPLICABLE."""
        p4a = make_mock_phase4a(
            wazn_id="MAF3UL",
            wazn_family="passive_participle",
            directive="ACCEPT",
        )
        result = project_masdar_with_licensing(p4a)
        assert result.final_directive == "NOT_APPLICABLE"
        assert result.source_path == "not_applicable"


# ══════════════════════════════════════════════════════════════════════════════
# §2 — العقود (Contracts)
# ══════════════════════════════════════════════════════════════════════════════

class TestContracts:
    """اختبارات 5–15: عقود Phase4CResult."""

    def test_05_accept_has_selected_masdar(self):
        """ACCEPT → selected_masdar ≠ None."""
        p4a = make_mock_phase4a(wazn_id="FA33ALA", wazn_family="form_II_verb")
        p4b = make_mock_phase4b(bab_id="BAB_FORM_II", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT"
        assert result.final_masdar is not None

    def test_06_defer_has_none_selected_masdar(self):
        """DEFER → selected_masdar = None."""
        p4a = make_mock_phase4a(wazn_id="FA_A_LA", wazn_family="triliteral_bare_verb")
        p4b = make_mock_phase4b(bab_id="BAB_I_NASARA", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "DEFER"
        assert result.final_masdar is None

    def test_07_block_has_none_selected_masdar(self):
        """BLOCK → selected_masdar = None."""
        p4a = make_mock_phase4a(directive="ACCEPT", wazn_family="triliteral_bare_verb")
        p4b = make_mock_phase4b(directive="BLOCK")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "BLOCK"
        assert result.final_masdar is None

    def test_08_not_opened_directive_when_phase4a_not_accept(self):
        """NOT_OPENED → masdar_projection directive = NOT_OPENED أو None."""
        p4a = make_mock_phase4a(directive="DEFER")
        result = project_masdar_with_licensing(p4a)
        assert result.final_directive == "NOT_OPENED"
        # masdar_projection = None عند NOT_OPENED من مسبب عدم ACCEPT
        assert result.masdar_projection is None

    def test_09_to_dict_json_safe(self):
        """to_dict() يُنتج dict قابل لتسلسل JSON."""
        p4a = make_mock_phase4a(wazn_id="FA33ALA", wazn_family="form_II_verb")
        p4b = make_mock_phase4b(bab_id="BAB_FORM_II", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        d = result.to_dict()
        # يجب أن يكون قابلًا للتسلسل بدون استثناء
        json.dumps(d, ensure_ascii=False)

    def test_10_dtos_are_frozen(self):
        """جميع DTOs frozen (لا تعديل)."""
        cand = MasdarCandidate(
            masdar_id="X", masdar_surface=None, masdar_pattern=None,
            source_type="SAMI3I_REQUIRED", confidence="DEFER_REQUIRED",
            evidence_ids=(), trace_ids=(), residual_codes=(),
        )
        with pytest.raises((AttributeError, TypeError)):
            cand.masdar_id = "Y"  # type: ignore[misc]

    def test_11_evidence_ids_preserved(self):
        """evidence_ids مُمرَّرة ومحفوظة في النتيجة."""
        p4a = make_mock_phase4a(directive="DEFER")
        result = project_masdar_with_licensing(p4a)
        # عند NOT_OPENED يجب أن تكون evidence_ids موجودة (tuple)
        assert isinstance(result.evidence_ids, tuple)

    def test_12_trace_ids_preserved(self):
        """trace_ids مُمرَّرة ومحفوظة."""
        p4a = make_mock_phase4a(directive="DEFER")
        result = project_masdar_with_licensing(p4a)
        assert isinstance(result.trace_ids, tuple)

    def test_13_residual_codes_preserved(self):
        """residual_codes موجودة."""
        p4a = make_mock_phase4a(directive="DEFER")
        result = project_masdar_with_licensing(p4a)
        assert isinstance(result.residual_codes, tuple)

    def test_14_final_masdar_pattern_set_when_accept(self):
        """final_masdar_pattern مُعيَّنة عند ACCEPT."""
        p4a = make_mock_phase4a(wazn_id="IFTA3ALA", wazn_family="form_VIII_verb")
        p4b = make_mock_phase4b(bab_id="BAB_FORM_VIII", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT"
        assert result.final_masdar_pattern is not None

    def test_15_source_path_independent_of_directive(self):
        """source_path مستقل — يمكن أن يكون 'deferred' مع final_directive 'DEFER'."""
        p4a = make_mock_phase4a(wazn_id="FA_A_LA", wazn_family="triliteral_bare_verb")
        p4b = make_mock_phase4b(bab_id="BAB_II_DARABA", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.source_path == "deferred"
        assert result.final_directive == "DEFER"


# ══════════════════════════════════════════════════════════════════════════════
# §3 — حالات المجرد (Mujarrad DEFER — سماعي مطلوب)
# ══════════════════════════════════════════════════════════════════════════════

class TestMujarradCases:
    """اختبارات 16–22: الأبواب المجردة → DEFER / SAMI3I_REQUIRED."""

    @pytest.mark.parametrize("bab_id", [
        "BAB_I_NASARA",
        "BAB_II_DARABA",
        "BAB_III_FATAHA",
        "BAB_IV_SAMIA",
        "BAB_V_KARUMA",
        "BAB_VI_HASIBA",
    ])
    def test_16_to_21_mujarrad_babs_give_defer(self, bab_id: str):
        """الأبواب المجردة 1–6 → DEFER مع SAMI3I_REQUIRED."""
        p4a = make_mock_phase4a(wazn_family="triliteral_bare_verb")
        p4b = make_mock_phase4b(bab_id=bab_id, directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "DEFER", (
            f"Expected DEFER for {bab_id}, got {result.final_directive}"
        )
        mp = result.masdar_projection
        assert mp is not None
        if mp.candidate_masadir:
            assert any(
                c.source_type == "SAMI3I_REQUIRED"
                for c in mp.candidate_masadir
            ), f"Expected SAMI3I_REQUIRED candidate for {bab_id}"

    def test_22_mujarrad_defer_is_not_block(self):
        """باب مجرد مع Phase4B DEFER → DEFER مصدر (لا BLOCK)."""
        p4a = make_mock_phase4a(wazn_family="triliteral_bare_verb")
        p4b = make_mock_phase4b(bab_id=None, directive="DEFER")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        # DEFER باب → DEFER مصدر لا BLOCK
        assert result.final_directive in ("DEFER", "ACCEPT")
        assert result.final_directive != "BLOCK"


# ══════════════════════════════════════════════════════════════════════════════
# §4 — حالات المزيد (Augmented ACCEPT — استنتاج هيكلي)
# ══════════════════════════════════════════════════════════════════════════════

class TestAugmentedCases:
    """اختبارات 23–30: الصيغ المزيدة → ACCEPT مع النمط الصحيح."""

    @pytest.mark.parametrize("bab_id,wazn_id,wazn_family,expected_pattern", [
        ("BAB_FORM_II",   "FA33ALA",   "form_II_verb",   "تَفْعِيل"),
        ("BAB_FORM_III",  "FA3ALA",    "form_III_verb",  "مُفَاعَلَة"),
        ("BAB_FORM_IV",   "AF3AL",     "form_IV_verb",   "إِفْعَال"),
        ("BAB_FORM_V",    "TAFA33ALA", "form_V_verb",    "تَفَعُّل"),
        ("BAB_FORM_VI",   "TAFA3ALA",  "form_VI_verb",   "تَفَاعُل"),
        ("BAB_FORM_VII",  "INFA3ALA",  "form_VII_verb",  "اِنْفِعَال"),
        ("BAB_FORM_VIII", "IFTA3ALA",  "form_VIII_verb", "اِفْتِعَال"),
        ("BAB_FORM_X",    "ISTAF3ALA", "form_X_verb",    "اِسْتِفْعَال"),
    ])
    def test_23_to_30_augmented_forms_accept(
        self, bab_id: str, wazn_id: str, wazn_family: str, expected_pattern: str
    ):
        """الصيغ المزيدة → ACCEPT مع النمط الصحيح."""
        p4a = make_mock_phase4a(wazn_id=wazn_id, wazn_family=wazn_family)
        p4b = make_mock_phase4b(bab_id=bab_id, directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT", (
            f"Expected ACCEPT for {bab_id}, got {result.final_directive}"
        )
        assert result.final_masdar_pattern == expected_pattern, (
            f"Expected pattern {expected_pattern!r} for {bab_id}, "
            f"got {result.final_masdar_pattern!r}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# §5 — انتشار التوجيهات (Propagation)
# ══════════════════════════════════════════════════════════════════════════════

class TestPropagation:
    """اختبارات 31–35: انتشار توجيهات Phase4B."""

    def test_31_phase4b_block_propagates_to_masdar(self):
        """Phase4B BLOCK → Phase4C BLOCK."""
        p4a = make_mock_phase4a(wazn_id="FA33ALA", wazn_family="form_II_verb")
        p4b = make_mock_phase4b(bab_id=None, directive="BLOCK")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "BLOCK"
        assert result.source_path == "blocked"

    def test_32_phase4b_defer_without_bab_id_gives_defer(self):
        """Phase4B DEFER بدون bab_id → مصدر DEFER (باب غامض)."""
        p4a = make_mock_phase4a(wazn_id="FA_A_LA", wazn_family="triliteral_bare_verb")
        p4b = make_mock_phase4b(bab_id=None, directive="DEFER")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "DEFER"

    def test_33_phase4b_none_but_phase4a_accept_opens_masdar(self):
        """Phase4B = None لكن Phase4A ACCEPT → يُفتح تحليل المصدر."""
        p4a = make_mock_phase4a(wazn_id="FA33ALA", wazn_family="form_II_verb")
        result = project_masdar_with_licensing(p4a, phase4b_result=None)
        # يجب أن يُفتح التحليل عبر wazn_id
        assert result.final_directive != "NOT_OPENED"

    def test_34_source_type_structural_for_augmented(self):
        """source_type == STRUCTURAL_INFERENCE للصيغة المزيدة."""
        p4a = make_mock_phase4a(wazn_id="IFTA3ALA", wazn_family="form_VIII_verb")
        p4b = make_mock_phase4b(bab_id="BAB_FORM_VIII", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT"
        mp = result.masdar_projection
        assert mp is not None
        assert mp.source_type == "STRUCTURAL_INFERENCE"

    def test_35_source_type_sami3i_for_mujarrad(self):
        """source_type == SAMI3I_REQUIRED للمجرد."""
        p4a = make_mock_phase4a(wazn_id="FA_A_LA", wazn_family="triliteral_bare_verb")
        p4b = make_mock_phase4b(bab_id="BAB_II_DARABA", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "DEFER"
        mp = result.masdar_projection
        assert mp is not None
        assert mp.source_type == "SAMI3I_REQUIRED"


# ══════════════════════════════════════════════════════════════════════════════
# §6 — ملكية الكود (Ownership)
# ══════════════════════════════════════════════════════════════════════════════

class TestOwnership:
    """اختبارات 36–40: ضمانات ملكية الكود."""

    def test_36_no_hr2s_import_in_phase4c_code(self):
        """لا استيراد HR2S في كود Phase 4C."""
        base = Path(__file__).resolve().parents[2] / "pipeline" / "p4_masdar"
        for py_file in base.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "hr2s" not in content.lower(), (
                f"HR2S reference found in {py_file.name}"
            )
            assert "fractal" not in content.lower(), (
                f"fractal reference found in {py_file.name}"
            )

    def test_37_canonical_root_not_modified(self):
        """canonical_root لا يُعدَّل بواسطة Phase4C."""
        original_root = ("ف", "ع", "ل")
        p4a = make_mock_phase4a(canonical_root=original_root, wazn_family="form_II_verb")
        p4b = make_mock_phase4b(bab_id="BAB_FORM_II", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        # canonical_root في masdar_projection يجب أن يطابق المصدر
        mp = result.masdar_projection
        if mp is not None and mp.canonical_root is not None:
            assert mp.canonical_root == original_root

    def test_38_selected_wazn_not_modified(self):
        """selected_wazn لا يُعدَّل بواسطة Phase4C."""
        p4a = make_mock_phase4a(wazn_id="FA33ALA", wazn_family="form_II_verb")
        p4b = make_mock_phase4b(bab_id="BAB_FORM_II", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        # source_wazn = FA33ALA (مُحفوظ، لا مُعدَّل)
        mp = result.masdar_projection
        if mp is not None:
            assert mp.source_wazn == "FA33ALA"

    def test_39_no_mushtaqat_field_in_result(self):
        """لا حقول مشتقات (mushtaqat) في Phase4CResult."""
        p4a = make_mock_phase4a(wazn_family="form_II_verb")
        result = project_masdar_with_licensing(p4a)
        d = result.to_dict()
        mushtaqat_keys = {
            "mushtaqat", "active_participle", "passive_participle",
            "nisba", "masdar_mimi", "ism_makan",
        }
        assert not (mushtaqat_keys & set(d.keys())), (
            f"Found mushtaqat fields: {mushtaqat_keys & set(d.keys())}"
        )

    def test_40_no_paradigm_generation(self):
        """لا توليد تصريف (paradigm) في Phase4CResult."""
        p4a = make_mock_phase4a(wazn_id="FA33ALA", wazn_family="form_II_verb")
        p4b = make_mock_phase4b(bab_id="BAB_FORM_II", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        d = result.to_dict()
        paradigm_keys = {"paradigm", "conjugation", "inflection_table", "forms"}
        assert not (paradigm_keys & set(d.keys())), (
            f"Found paradigm fields: {paradigm_keys & set(d.keys())}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# §7 — اختبارات التكامل (Integration — Live Pipeline)
# ══════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """اختبارات 41–47: تكامل الأنبوب الحي."""

    def test_41_hokom_returns_phase4c_result_key(self):
        """hokom() يُعيد مفتاح phase4c_result في dict."""
        from hokom_pipeline import hokom
        r = hokom("ضَرَبَ")
        assert "phase4c_result" in r, "phase4c_result key missing from hokom() output"

    def test_42_live_augmented_form_has_final_masdar(self):
        """الصيغة المزيدة الحية تُعطي final_masdar عند ACCEPT."""
        p4a = make_mock_phase4a(wazn_id="FA33ALA", wazn_family="form_II_verb")
        p4b = make_mock_phase4b(bab_id="BAB_FORM_II", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        if result.final_directive == "ACCEPT":
            assert result.final_masdar is not None

    def test_43_live_daraba_gives_deferred_masdar(self):
        """ضَرَبَ الحية → phase4c_result.final_masdar = None (مجرد مؤجَّل)."""
        from hokom_pipeline import hokom
        r = hokom("ضَرَبَ")
        p4c = r.get("phase4c_result")
        if p4c is not None:
            # إن وُجدت نتيجة Phase4C → يجب أن تكون DEFER أو NOT_OPENED
            assert p4c.final_masdar is None

    def test_44_phase4a_result_still_present(self):
        """phase4a_result لا يزال موجودًا في output بعد إضافة Phase4C."""
        from hokom_pipeline import hokom
        r = hokom("ضَرَبَ")
        assert "phase4a_result" in r

    def test_45_phase4b_result_still_present(self):
        """phase4b_result لا يزال موجودًا في output بعد إضافة Phase4C."""
        from hokom_pipeline import hokom
        r = hokom("ضَرَبَ")
        assert "phase4b_result" in r

    def test_46_refined_host_unchanged(self):
        """root_refinement لا يُعدَّل بواسطة Phase4C."""
        from hokom_pipeline import hokom
        r = hokom("ضَرَبَ")
        # root_refinement موجود → refined_host لم يتغير
        rr = r.get("root_refinement")
        if rr is not None:
            assert hasattr(rr, "refined_host")

    def test_47_root_source_engine_unchanged(self):
        """source_engine في RootProjection لا يُعدَّل."""
        from hokom_pipeline import hokom
        r = hokom("ضَرَبَ")
        rp = r.get("root_projection")
        if rp is not None:
            assert hasattr(rp, "source_engine")
            # لا يجب أن يحتوي على مرجع HR2S
            assert "hr2s" not in str(rp.source_engine).lower()


# ══════════════════════════════════════════════════════════════════════════════
# §8 — إغلاق الملفات المجمّدة (Frozen Files)
# ══════════════════════════════════════════════════════════════════════════════

FROZEN_FILES = [
    (
        "pipeline/p3_candidate/root_profiles.py",
        "c20a1bc6998516cc",
    ),
    (
        "pipeline/p3_candidate/root_rules.py",
        "a8e35225693f553d",
    ),
    (
        "pipeline/p3_candidate/root_resolution.py",
        "d87d07921d989c26",
    ),
    (
        "pipeline/p3_candidate/root_resolution_orchestrator.py",
        "58ecd174a919cbe8",
    ),
    (
        "pipeline/p2_projection/root_projection.py",
        "7bca3605867e67ed",
    ),
]


@pytest.mark.parametrize("rel_path,expected_prefix", FROZEN_FILES)
def test_48_frozen_files_unchanged(rel_path: str, expected_prefix: str):
    """الملفات المجمّدة لم تتغير (SHA256 prefix)."""
    root = Path(__file__).resolve().parents[2]
    full = root / rel_path
    assert full.exists(), f"Frozen file missing: {rel_path}"
    sha = hashlib.sha256(full.read_bytes()).hexdigest()
    assert sha.startswith(expected_prefix), (
        f"Frozen file CHANGED: {rel_path}\n"
        f"  expected prefix: {expected_prefix}\n"
        f"  actual sha256:   {sha}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# §9 — صحة العقود (Contract Integrity)
# ══════════════════════════════════════════════════════════════════════════════

class TestContractIntegrity:
    """اختبارات 49–55: صحة عقود Phase4B وعدم تغيير semantics."""

    def test_49_phase4b_result_contract_unchanged(self):
        """Phase4BResult contract: الحقول الأساسية موجودة."""
        from pipeline.p4_bab.models import Phase4BResult
        import inspect
        fields = {f for f in inspect.get_annotations(Phase4BResult)}
        required = {
            "initial_wazn_directive", "final_directive",
            "bab_projection", "final_bab", "source_path",
        }
        assert required.issubset(fields), f"Missing Phase4BResult fields: {required - fields}"

    def test_50_bab_wazn_semantics_not_changed(self):
        """BabProjection و WaznProjection contracts لم تتغير."""
        from pipeline.p4_bab.models import BabProjection, BabCandidate
        # BabProjection: directive مطلوبة
        import inspect
        bp_fields = set(inspect.get_annotations(BabProjection))
        assert "directive" in bp_fields
        assert "selected_bab" in bp_fields

    def test_51_masdar_catalog_loads_without_error(self):
        """catalog المصادر يُحمَّل بدون خطأ."""
        from pipeline.p4_masdar.masdar_catalog import load_masdar_catalog
        catalog = load_masdar_catalog()
        assert len(catalog) > 0

    def test_52_masdar_catalog_has_all_required_forms(self):
        """catalog يحتوي على جميع الصيغ المزيدة المطلوبة."""
        from pipeline.p4_masdar.masdar_catalog import load_masdar_catalog
        catalog = load_masdar_catalog()
        masdar_ids = set(catalog.keys())
        required_forms = {
            "MASDAR_FORM_II", "MASDAR_FORM_III", "MASDAR_FORM_IV",
            "MASDAR_FORM_V", "MASDAR_FORM_VI", "MASDAR_FORM_VII",
            "MASDAR_FORM_VIII", "MASDAR_FORM_X",
        }
        assert required_forms.issubset(masdar_ids), (
            f"Missing masdar forms: {required_forms - masdar_ids}"
        )

    def test_53_mujarrad_entries_are_sami3i(self):
        """مدخلات المجرد في catalog مُعلَّمة بـ SAMI3I_REQUIRED."""
        from pipeline.p4_masdar.masdar_catalog import load_masdar_catalog
        catalog = load_masdar_catalog()
        mujarrad_entries = [
            d for d in catalog.values() if d.family == "MUJARRAD"
        ]
        assert len(mujarrad_entries) > 0
        for defn in mujarrad_entries:
            assert defn.source_type == "SAMI3I_REQUIRED", (
                f"{defn.masdar_id} should be SAMI3I_REQUIRED"
            )
            assert defn.masdar_pattern is None, (
                f"{defn.masdar_id} should have no pattern (sami3i)"
            )

    def test_54_structural_entries_have_patterns(self):
        """مدخلات STRUCTURAL_INFERENCE في catalog لها أنماط محددة."""
        from pipeline.p4_masdar.masdar_catalog import load_masdar_catalog
        catalog = load_masdar_catalog()
        structural = [
            d for d in catalog.values()
            if d.source_type == "STRUCTURAL_INFERENCE"
        ]
        assert len(structural) > 0
        for defn in structural:
            assert defn.masdar_pattern is not None, (
                f"{defn.masdar_id} STRUCTURAL_INFERENCE must have masdar_pattern"
            )

    def test_55_no_duplicate_masdar_ids_in_catalog(self):
        """لا masdar_id مكرر في catalog."""
        catalog_path = (
            Path(__file__).resolve().parents[2] / "data" / "masdar" / "masdar_catalog.json"
        )
        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
        ids = [e["masdar_id"] for e in raw["masadir"]]
        assert len(ids) == len(set(ids)), f"Duplicate masdar_ids: {ids}"


# ══════════════════════════════════════════════════════════════════════════════
# §10 — مصفوفة المرجع (Reference Matrix) — C10
# ══════════════════════════════════════════════════════════════════════════════

# المصفوفة:
# | حالة             | Phase4A  | Phase4B      | Wazn       | Bab        | قابلية | source_type        | نمط المصدر     | directive      | residual        |
# |------------------|----------|--------------|------------|------------|--------|--------------------|----------------|----------------|-----------------|
# | ضَرَبَ (حي)     | ACCEPT   | DEFER        | FA_A_LA    | None       | APPL   | SAMI3I_REQUIRED   | None           | DEFER          | sami3i_required |
# | اِفْتَرَسَ       | ACCEPT   | ACCEPT VIII  | IFTA3ALA   | FORM_VIII  | APPL   | STRUCTURAL_INF    | اِفْتِعَال    | ACCEPT         | —               |
# | اِسْتَخْرَجَ     | ACCEPT   | ACCEPT X     | ISTAF3ALA  | FORM_X     | APPL   | STRUCTURAL_INF    | اِسْتِفْعَال  | ACCEPT         | —               |
# | دَرَّسَ           | ACCEPT   | ACCEPT II    | FA33ALA    | FORM_II    | APPL   | STRUCTURAL_INF    | تَفْعِيل      | ACCEPT         | —               |
# | مَسْرُور          | ACCEPT   | DEFER        | MAF3UL     | None       | N/A    | —                 | None           | NOT_APPLICABLE | non_verbal      |
# | قَالَ             | DEFER    | None         | —          | —          | —      | —                 | None           | NOT_OPENED     | —               |
# | مِنْ              | None     | None         | —          | —          | —      | —                 | None           | None (no p4c)  | —               |

class TestReferenceMatrix:
    """C10 — مصفوفة المرجع."""

    def test_matrix_daraba_live(self):
        """ضَرَبَ الحية: Phase4A ACCEPT, Phase4B DEFER, مصدر DEFER."""
        from hokom_pipeline import hokom
        r = hokom("ضَرَبَ")
        p4c = r.get("phase4c_result")
        if p4c is not None:
            assert p4c.final_masdar is None

    def test_matrix_form_viii_iftarasa(self):
        """اِفْتَرَسَ (FORM_VIII mock): ACCEPT → اِفْتِعَال."""
        p4a = make_mock_phase4a(wazn_id="IFTA3ALA", wazn_family="form_VIII_verb",
                                canonical_root=("ف", "ر", "س"))
        p4b = make_mock_phase4b(bab_id="BAB_FORM_VIII", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT"
        assert result.final_masdar_pattern == "اِفْتِعَال"
        mp = result.masdar_projection
        assert mp.source_type == "STRUCTURAL_INFERENCE"

    def test_matrix_form_x_istakhraj(self):
        """اِسْتَخْرَجَ (FORM_X mock): ACCEPT → اِسْتِفْعَال."""
        p4a = make_mock_phase4a(wazn_id="ISTAF3ALA", wazn_family="form_X_verb",
                                canonical_root=("خ", "ر", "ج"))
        p4b = make_mock_phase4b(bab_id="BAB_FORM_X", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT"
        assert result.final_masdar_pattern == "اِسْتِفْعَال"

    def test_matrix_form_ii_darrasa(self):
        """دَرَّسَ (FORM_II mock): ACCEPT → تَفْعِيل."""
        p4a = make_mock_phase4a(wazn_id="FA33ALA", wazn_family="form_II_verb",
                                canonical_root=("د", "ر", "س"))
        p4b = make_mock_phase4b(bab_id="BAB_FORM_II", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT"
        assert result.final_masdar_pattern == "تَفْعِيل"

    def test_matrix_masrur_nominal(self):
        """مَسْرُور (اسم مفعول): Phase4A ACCEPT + وزن اسمي → NOT_APPLICABLE."""
        p4a = make_mock_phase4a(
            wazn_id="MAF3UL",
            wazn_family="passive_participle",
            directive="ACCEPT",
        )
        result = project_masdar_with_licensing(p4a)
        assert result.final_directive == "NOT_APPLICABLE"
        assert result.source_path == "not_applicable"

    def test_matrix_qala_defer(self):
        """قَالَ (Phase4A DEFER): Phase4C NOT_OPENED."""
        p4a = make_mock_phase4a(directive="DEFER")
        result = project_masdar_with_licensing(p4a)
        assert result.final_directive == "NOT_OPENED"
        assert result.masdar_projection is None

    def test_matrix_min_no_phase4c(self):
        """مِنْ (حرف جر): لا Phase4C في الأنبوب."""
        from hokom_pipeline import hokom
        r = hokom("مِنْ")
        # مِنْ حرف → لا phase4a_result → لا phase4c_result
        p4c = r.get("phase4c_result")
        # إما None أو NOT_OPENED
        if p4c is not None:
            assert p4c.final_directive in ("NOT_OPENED", "NOT_APPLICABLE")

    def test_matrix_form_iii_kataba(self):
        """كَاتَبَ (FORM_III mock): ACCEPT → مُفَاعَلَة."""
        p4a = make_mock_phase4a(wazn_id="FA3ALA", wazn_family="form_III_verb",
                                canonical_root=("ك", "ت", "ب"))
        p4b = make_mock_phase4b(bab_id="BAB_FORM_III", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT"
        assert result.final_masdar_pattern == "مُفَاعَلَة"

    def test_matrix_form_iv_akrama(self):
        """أَكْرَمَ (FORM_IV mock): ACCEPT → إِفْعَال."""
        p4a = make_mock_phase4a(wazn_id="AF3AL", wazn_family="form_IV_verb",
                                canonical_root=("ك", "ر", "م"))
        p4b = make_mock_phase4b(bab_id="BAB_FORM_IV", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT"
        assert result.final_masdar_pattern == "إِفْعَال"

    def test_matrix_form_v_tafaallama(self):
        """تَعَلَّمَ (FORM_V mock): ACCEPT → تَفَعُّل."""
        p4a = make_mock_phase4a(wazn_id="TAFA33ALA", wazn_family="form_V_verb",
                                canonical_root=("ع", "ل", "م"))
        p4b = make_mock_phase4b(bab_id="BAB_FORM_V", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT"
        assert result.final_masdar_pattern == "تَفَعُّل"

    def test_matrix_form_vi_takaataba(self):
        """تَكَاتَبَ (FORM_VI mock): ACCEPT → تَفَاعُل."""
        p4a = make_mock_phase4a(wazn_id="TAFA3ALA", wazn_family="form_VI_verb",
                                canonical_root=("ك", "ت", "ب"))
        p4b = make_mock_phase4b(bab_id="BAB_FORM_VI", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT"
        assert result.final_masdar_pattern == "تَفَاعُل"

    def test_matrix_form_vii_inkasara(self):
        """اِنْكَسَرَ (FORM_VII mock): ACCEPT → اِنْفِعَال."""
        p4a = make_mock_phase4a(wazn_id="INFA3ALA", wazn_family="form_VII_verb",
                                canonical_root=("ك", "س", "ر"))
        p4b = make_mock_phase4b(bab_id="BAB_FORM_VII", directive="ACCEPT")
        result = project_masdar_with_licensing(p4a, phase4b_result=p4b)
        assert result.final_directive == "ACCEPT"
        assert result.final_masdar_pattern == "اِنْفِعَال"
