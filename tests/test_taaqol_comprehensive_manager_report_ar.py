#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUILD_COMPREHENSIVE_MANAGER_REPORT_AR_CODE_GENERATED_01 — documentary guard test.

Verifies the comprehensive Arabic executive manager report (HTML, code-generated). Reads artifacts
only; asserts scope, achievements, t003 status, the 16-stage table, reasons for every "ليس بعد",
the tests section, and the absence of over-claims. No runtime.
"""
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
HTML = GEN / "roadmap" / "TAAQOL_NAZILA_COMPREHENSIVE_MANAGER_REPORT_AR_CODE_GENERATED_01.html"

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
OWNER_TEXT = "الأنثى التي تشارك الشخص في الأبوين أو في أحدهما."
KEY_ACHIEVEMENTS = [
    "TAAQOL_NAZILA_VIEW.html بأمر مالك صريح",
    "أول madlul_text_ar مرخّص",
    "من 0 إلى 1",
    "gloss_ar مادة محجورة",
    "C1–C7",
    "B2 كـ DEFER_PENDING_DATASET",
    "R3-ب كـ DEFER_NO_SOURCE_OR_RULE",
    "PRE_WEIGHT كحارس لا runtime",
    "لن يُسأل عن كل كلمة",
]


def _html():
    assert HTML.exists(), "comprehensive report must exist"
    return HTML.read_text(encoding="utf-8")


def _sentence_element(t):
    m = re.search(r'<div class="sent" id="nazila-sentence">(.*?)</div>', t, flags=re.S)
    assert m, "dedicated sentence element must exist"
    return m.group(1)


def test_report_exists_and_sentence_exact():
    assert _sentence_element(_html()) == SENTENCE


def test_contains_main_achievements():
    t = _html()
    for a in KEY_ACHIEVEMENTS:
        assert a in t, f"missing achievement: {a}"


def test_t003_status_block():
    t = _html()
    assert OWNER_TEXT in t
    assert "PROJECT_TEXT_LICENSED_MADLUL_COUNT" in t
    assert "OWNER_TEXT_LICENSED_PENDING_BINDING_GATE" in t
    assert "PENDING_BINDING_GATE" in t
    assert "SCORE_GATE_NOT_PRESENT" in t
    assert "80.0" in t and "90.0" in t


def test_has_16_stage_table():
    t = _html()
    rows = re.findall(r"<tr><th>(\d+)\.\s", t)
    assert [int(x) for x in rows] == list(range(1, 17)), rows


def test_every_not_yet_cell_has_reason():
    t = _html()
    cells = re.findall(r"<td[^>]*>(.*?)</td>", t, flags=re.S)
    bad = [c for c in cells if "ليس بعد" in c and ("—" not in c and "·" not in c)]
    assert not bad, f"bare 'ليس بعد' cell(s): {bad[:3]}"


def test_tests_section_present():
    assert "PYTEST_TOTAL_PASSED" in _html()


def test_no_overclaim():
    t = _html()
    assert "PROJECT_FINISHED = NO" in t
    assert not re.search(r"PROJECT_FINISHED\s*=\s*YES", t)
    assert "t003 NOT BOUND" in t
    # exclude negations in both English ("NOT BOUND") and Arabic ("غير BOUND")
    bad = [x for x in re.findall(r"t003[^<]*BOUND", t) if "NOT BOUND" not in x and "غير BOUND" not in x]
    assert not bad, bad
    for kv in ("RUNTIME_CHANGED = NO", "SCORE_CHANGED = NO", "GATES_OPENED = NO", "COMMIT = NO"):
        assert kv in t, kv


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _html())
