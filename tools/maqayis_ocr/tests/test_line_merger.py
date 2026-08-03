"""
tests/test_line_merger.py — Maqayis OCR v2

Unit tests for line_merger.py.
These tests do NOT require a PDF or Apple Vision — they work on synthetic
observation dicts that mimic vision_ocr.swift output.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from line_merger import merge_observations, SAME_LINE_Y_TOLERANCE


# ── helpers ───────────────────────────────────────────────────────────────────

def _obs(idx, x, y, w, h, raw="text", corr="text", raw_conf=0.9, corr_conf=0.9):
    return {
        "observation_index": idx,
        "bounding_box": {"x": x, "y": y, "w": w, "h": h},
        "raw_ocr":  raw,
        "corrected_ocr": corr,
        "raw_candidates":  [{"text": raw,  "confidence": raw_conf}],
        "corrected_candidates": [{"text": corr, "confidence": corr_conf}],
    }


# ── tests ──────────────────────────────────────────────────────────────────────

def test_single_observation_becomes_single_line():
    obs = [_obs(0, 0.1, 0.8, 0.8, 0.03, raw="كتاب الحاء")]
    lines = merge_observations(obs, "02.pdf", 3)
    assert len(lines) == 1
    assert lines[0]["raw_ocr"] == "كتاب الحاء"
    assert lines[0]["line_id"] == "02.pdf:p3:l0001"


def test_two_obs_on_same_y_merge():
    """Two fragments close in Y should merge into one line."""
    obs = [
        _obs(0, 0.5, 0.80, 0.3, 0.03, raw="والدال", corr="والدال"),
        _obs(1, 0.1, 0.80, 0.3, 0.03, raw="الحاء",  corr="الحاء"),
    ]
    lines = merge_observations(obs, "02.pdf", 3)
    assert len(lines) == 1
    # RTL merge: rightmost fragment first (higher X)
    assert "الحاء" in lines[0]["raw_ocr"]


def test_two_obs_on_different_y_stay_separate():
    """Observations more than tolerance apart in Y → two lines."""
    gap = SAME_LINE_Y_TOLERANCE * 3
    obs = [
        _obs(0, 0.1, 0.80, 0.8, 0.025, raw="line one"),
        _obs(1, 0.1, 0.80 - gap, 0.8, 0.025, raw="line two"),
    ]
    lines = merge_observations(obs, "01.pdf", 5)
    assert len(lines) == 2


def test_line_ids_are_unique():
    obs = [_obs(i, 0.1, 0.9 - i * 0.05, 0.8, 0.025, raw=f"line{i}") for i in range(5)]
    lines = merge_observations(obs, "03.pdf", 10)
    ids = [l["line_id"] for l in lines]
    assert len(ids) == len(set(ids)), "Line IDs must be unique"


def test_bounding_box_union():
    """Merged line bbox should span both observations."""
    obs = [
        _obs(0, x=0.5, y=0.8, w=0.2, h=0.03),
        _obs(1, x=0.1, y=0.8, w=0.2, h=0.03),
    ]
    lines = merge_observations(obs, "02.pdf", 3)
    bb = lines[0]["bounding_box"]
    assert abs(bb["x"] - 0.1) < 1e-9
    assert abs(bb["w"] - 0.6) < 1e-9   # spans from 0.1 to 0.7


def test_candidates_merged_and_deduplicated():
    """Best candidates from multiple observations should be de-duplicated."""
    obs = [
        _obs(0, 0.5, 0.8, 0.3, 0.03, raw="أصل", raw_conf=0.95),
        _obs(1, 0.1, 0.8, 0.3, 0.03, raw="واحد", raw_conf=0.85),
    ]
    # Give obs[1] a duplicate text with lower confidence to test dedup
    obs[1]["raw_candidates"].append({"text": "أصل", "confidence": 0.60})

    lines = merge_observations(obs, "02.pdf", 3)
    raw_texts = [c["text"] for c in lines[0]["raw_candidates"]]
    # "أصل" should appear only once (highest confidence wins)
    assert raw_texts.count("أصل") == 1


def test_source_pdf_and_page_preserved():
    obs = [_obs(0, 0.1, 0.8, 0.8, 0.03)]
    lines = merge_observations(obs, "05.pdf", 42)
    assert lines[0]["source_pdf"] == "05.pdf"
    assert lines[0]["pdf_page"] == 42


def test_empty_observations():
    lines = merge_observations([], "01.pdf", 1)
    assert lines == []


def test_review_status_defaults_to_auto_agreed():
    obs = [_obs(0, 0.1, 0.8, 0.8, 0.03)]
    lines = merge_observations(obs, "02.pdf", 3)
    assert lines[0]["review_status"] == "AUTO_AGREED"


def test_region_type_defaults_to_unknown():
    obs = [_obs(0, 0.1, 0.8, 0.8, 0.03)]
    lines = merge_observations(obs, "02.pdf", 3)
    assert lines[0]["region_type"] == "UNKNOWN"
