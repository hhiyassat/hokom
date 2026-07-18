#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_wazn_pipeline_phase4a.py — تكامل Phase 4A
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يُثبت المسار: RootCandidate P3 → WaznProjection Phase 4A على الحالات المرجعية
الإلزامية (§15/§16)، ومصفوفة الرتابة (§18)، وعدم اقتران المرحلة بـHR2S.

المدخل RootCandidate يُبنى مباشرة (Phase 4A تستهلك RootCandidate فقط — لا HR2S،
لا قراءة للسطح الأصلي).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.p3_candidate.root_candidate import RootCandidate
from pipeline.p4_wazn import project_wazn, WaznDirective, WaznStageState


def rc(surface, host, directive, root):
    return RootCandidate(
        surface=surface, host_surface=host, directive=directive,
        canonical_root=root, root_profile={},
        evidence_ids=(f"ev:root:{surface}",), trace_ids=(f"tr:root:{surface}",),
        residual_codes=(() if directive == "ACCEPT" else (f"{directive.lower()}:root:x",)),
        source_projection="RootProjection")


# (surface, analyzed_host, root_directive, canonical_root,
#  expected_wazn_directive, expected_stage, expected_selected_pattern)
REFERENCE_MATRIX = [
    # ── سالم / مهموز / مضاعف / تصريف: ACCEPT ─────────────────────────────
    ("ضَرَبَ",       "ضَرَبَ",   "ACCEPT", ("ض", "ر", "ب"), "ACCEPT", "COMPLETED", "فَعَلَ"),
    ("قَرَأَ",       "قَرَأَ",   "ACCEPT", ("ق", "ر", "ء"), "ACCEPT", "COMPLETED", "فَعَلَ"),
    ("مَدَّ",        "مَدَّ",    "ACCEPT", ("م", "د", "د"), "ACCEPT", "COMPLETED", "فَعَلَ"),
    ("كَتَبَ",       "كَتَبَ",   "ACCEPT", ("ك", "ت", "ب"), "ACCEPT", "COMPLETED", "فَعَلَ"),
    ("عَطْفِ",       "عَطْفِ",   "ACCEPT", ("ع", "ط", "ف"), "ACCEPT", "COMPLETED", "فَعْل"),
    ("تَرَكَتْهُمْ",  "تَرَكَتْ", "ACCEPT", ("ت", "ر", "ك"), "ACCEPT", "COMPLETED", "فَعَلَ"),
    # ── اسمي يحتاج عقدًا مرخّصًا: DEFER (المرحلة مفتوحة، الوزن مؤجَّل) ──────
    ("شِدَّةِ",       "شِدَّةِ",   "ACCEPT", ("ش", "د", "د"), "DEFER", "DEFERRED", None),
    ("مَحَبَّةِ",     "مَحَبَّةِ", "ACCEPT", ("ح", "ب", "ب"), "DEFER", "DEFERRED", None),
    ("مَسْرُورَةٌ",   "مَسْرُورَةٌ", "ACCEPT", ("س", "ر", "ر"), "DEFER", "DEFERRED", None),
    ("الْأَطْفَالُ",  "أَطْفَالُ", "ACCEPT", ("ط", "ف", "ل"), "DEFER", "DEFERRED", None),
    ("الشَّجَرَةِ",   "شَجَرَةِ",  "ACCEPT", ("ش", "ج", "ر"), "DEFER", "DEFERRED", None),
    # ── جذر غير محلول: الوزن NOT_OPENED ──────────────────────────────────
    ("نَائِمِينَ",    "نَائِم",   "DEFER", None, "DEFER", "NOT_OPENED", None),
    ("قَالَ",         "قَالَ",    "DEFER", None, "DEFER", "NOT_OPENED", None),
    ("دَعَا",         "دَعَا",    "DEFER", None, "DEFER", "NOT_OPENED", None),
    ("وَقَى",         "وَقَى",    "DEFER", None, "DEFER", "NOT_OPENED", None),
    ("قُلْ",          "قُلْ",     "DEFER", None, "DEFER", "NOT_OPENED", None),
    # ── مسار الجذر مغلق: الوزن BLOCK / NOT_OPENED ────────────────────────
    ("مِنْ",          "مِنْ",     "BLOCK", None, "BLOCK", "NOT_OPENED", None),
    ("أَنَّهُمْ",      "أَنَّ",     "BLOCK", None, "BLOCK", "NOT_OPENED", None),
]


@pytest.mark.parametrize(
    "surface,host,root_dir,root,exp_dir,exp_stage,exp_pattern",
    REFERENCE_MATRIX,
    ids=[m[0] for m in REFERENCE_MATRIX],
)
def test_reference_matrix(surface, host, root_dir, root, exp_dir, exp_stage, exp_pattern):
    p = project_wazn(rc(surface, host, root_dir, root))
    assert p.directive.value == exp_dir
    assert p.stage_state.value == exp_stage
    if exp_pattern is None:
        assert p.selected_wazn is None
    else:
        assert p.selected_wazn is not None
        assert p.selected_wazn.wazn_pattern == exp_pattern
    # المضيف المُحلَّل هو المستعمَل، لا السطح الكامل.
    assert p.analyzed_host == host
    # قابلية التسلسل لكل حالة.
    import json
    json.dumps(p.to_dict(), ensure_ascii=False)


class TestMonotonicityMatrix:
    """§18 — الرتابة بين RootCandidate و WaznProjection."""

    def test_root_block_never_accepts_or_defers_open(self):
        p = project_wazn(rc("مِنْ", "مِنْ", "BLOCK", None))
        assert p.directive == WaznDirective.BLOCK
        assert p.stage_state == WaznStageState.NOT_OPENED

    def test_root_defer_never_accepts(self):
        p = project_wazn(rc("قَالَ", "قَالَ", "DEFER", None))
        assert p.directive != WaznDirective.ACCEPT
        assert p.stage_state == WaznStageState.NOT_OPENED

    def test_root_accept_may_yield_any(self):
        outcomes = set()
        for surface, host, root_dir, root, *_ in REFERENCE_MATRIX:
            if root_dir != "ACCEPT":
                continue
            outcomes.add(project_wazn(rc(surface, host, root_dir, root)).directive)
        # نثبت وجود ACCEPT و DEFER على الأقل ضمن فرع ACCEPT.
        assert WaznDirective.ACCEPT in outcomes
        assert WaznDirective.DEFER in outcomes

    def test_full_matrix_respects_monotonicity(self):
        for surface, host, root_dir, root, *_ in REFERENCE_MATRIX:
            p = project_wazn(rc(surface, host, root_dir, root))
            if root_dir == "BLOCK":
                assert p.directive == WaznDirective.BLOCK
                assert p.stage_state == WaznStageState.NOT_OPENED
            elif root_dir == "DEFER":
                assert p.directive == WaznDirective.DEFER
                assert p.stage_state == WaznStageState.NOT_OPENED
            else:  # ACCEPT
                assert p.directive in (WaznDirective.ACCEPT, WaznDirective.DEFER,
                                       WaznDirective.BLOCK)


class TestNoHR2SCoupling:
    """§23 — لا استدعاء ولا استيراد لـHR2S في طبقة الوزن."""

    def test_p4_wazn_source_has_no_hr2s_import(self):
        # يُسمح بذكر HR2S في التوثيق (لتوضيح أنها لا تُستدعى)، ويُمنع أي استيراد فعلي.
        import re
        pkg_dir = Path(__file__).resolve().parents[2] / "pipeline" / "p4_wazn"
        import_pat = re.compile(r"^\s*(?:from|import)\s+.*hr2s", re.IGNORECASE | re.MULTILINE)
        offenders = []
        for py in pkg_dir.glob("*.py"):
            text = py.read_text(encoding="utf-8")
            if import_pat.search(text) or "hr2s_root_adapter" in text:
                offenders.append(py.name)
        assert offenders == [], f"hr2s imported in {offenders}"

    def test_candidate_not_reread_from_surface(self):
        # لا تُقرأ raw surface: تغيير surface مع ثبات host لا يغيّر الوزن.
        a = project_wazn(rc("XYZ_GARBAGE", "ضَرَبَ", "ACCEPT", ("ض", "ر", "ب")))
        b = project_wazn(rc("ضَرَبَ",      "ضَرَبَ", "ACCEPT", ("ض", "ر", "ب")))
        assert a.selected_wazn.wazn_id == b.selected_wazn.wazn_id
        assert a.directive == b.directive == WaznDirective.ACCEPT


class TestEvidenceTraceResidualPreservation:
    def test_evidence_and_trace_flow_through(self):
        p = project_wazn(rc("ضَرَبَ", "ضَرَبَ", "ACCEPT", ("ض", "ر", "ب")))
        assert any(e.startswith("ev:root") for e in p.evidence_ids)
        assert any(t.startswith("tr:root") for t in p.trace_ids)

    def test_root_residuals_preserved_on_not_opened(self):
        p = project_wazn(rc("قَالَ", "قَالَ", "DEFER", None))
        assert any(r.startswith("defer:root") for r in p.residual_codes)
        assert "defer:wazn:root_candidate_not_resolved" in p.residual_codes
