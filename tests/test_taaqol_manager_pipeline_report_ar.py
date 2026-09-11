#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REBUILD_MANAGER_REPORT_LIKE_EXEC_REPORT_2_PIPELINE_AR_01 — documentary guard test.

Verifies the code-generated Arabic manager PIPELINE report (HTML), EXEC-style:
per-word processing table + a 16-stage x 10-word matrix. Reads artifacts only; no runtime.
"""
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
HTML = GEN / "roadmap" / "TAAQOL_NAZILA_MANAGER_PIPELINE_REPORT_AR_CODE_GENERATED_02.html"

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
OWNER_TEXT = "الأنثى التي تشارك الشخص في الأبوين أو في أحدهما."
WORDS = ["مَاتَ", "مَلِكٌ", "عَنْ", "أُخْتٍ", "سَاكِنَةٍ", "مَعَهُ", "فَأَرَادَ", "وَارِثُهُ", "طَرْدَهَا", "فَتَحَاكَمَا"]


def _html():
    assert HTML.exists(), "pipeline HTML report must exist"
    return HTML.read_text(encoding="utf-8")


def _sentence_element(t):
    m = re.search(r'<div class="sent" id="nazila-sentence">(.*?)</div>', t, flags=re.S)
    assert m, "dedicated sentence element #nazila-sentence must exist"
    return m.group(1)


def test_sentence_element_exact_match():
    # the sentence must equal the trusted literal EXACTLY (fails otherwise)
    assert _sentence_element(_html()) == SENTENCE


def test_sentence_element_has_no_report_phrase_leak():
    s = _sentence_element(_html())
    for leak in ("لم يعمل", "ليس بعد", "ومعه"):
        assert leak not in s, f"report phrase leaked into the sentence: {leak}"


def test_has_both_tables():
    t = _html()
    assert "أولًا · مراحل تعالج الكلمة نفسها" in t
    assert "ثانيًا · ست عشرة مرحلة" in t


def test_has_ten_words():
    t = _html()
    for w in WORDS:
        assert w in t, w


def test_has_16_stages():
    t = _html()
    rows = re.findall(r"<tr><th>(\d+)\.\s", t)
    assert [int(x) for x in rows] == list(range(1, 17)), rows


def test_every_not_yet_cell_has_a_reason():
    t = _html()
    # only inspect table cells (<td ...>...</td>); the intro paragraph is not a cell
    cells = re.findall(r"<td[^>]*>(.*?)</td>", t, flags=re.S)
    offenders = [c for c in cells if "ليس بعد" in c and ("—" not in c and "·" not in c)]
    assert not offenders, f"bare 'ليس بعد' cell(s) without reason: {offenders[:3]}"


def test_t003_owner_text_and_gate_states():
    t = _html()
    assert OWNER_TEXT in t
    assert "PENDING_BINDING_GATE" in t
    assert "SCORE_GATE_NOT_PRESENT" in t


def test_footer_flags_and_no_bound_claim():
    t = _html()
    assert "PROJECT_FINISHED = NO" in t
    assert "REPORT_SOURCE = ARTIFACTS_NOT_LLM_FREE_TEXT" in t
    for kv in ("RUNTIME_CHANGED = NO", "SCORE_CHANGED = NO", "GATES_OPENED = NO", "COMMIT = NO"):
        assert kv in t, kv
    assert "t003 NOT BOUND" in t
    # no positive BOUND claim for t003
    bad = [x for x in re.findall(r"t003[^<]*BOUND", t) if "NOT BOUND" not in x]
    assert not bad, bad


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _html())
