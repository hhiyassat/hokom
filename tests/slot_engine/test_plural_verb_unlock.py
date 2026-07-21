#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/slot_engine/test_plural_verb_unlock.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-SLOT-ENGINE-PLURAL-VERB-UNLOCK-01

Canonical acceptance tests for the two FALSE_BLOCK defect clusters
identified in the Ayat al-Dayn semantic audit (commit 4e0886a):

  Cluster A — CVV+V  (ALEF_FARQA_BOUNDARY):
    Masculine plural verb forms ending in وا (waw al-jamaa + alef al-farqa).
    The final ا is orthographic only; extending CVV→CVV+V was a false BLOCK.

  Cluster B — +V  (HAMZAT_AL_WASL_SKIP):
    Verb/noun forms starting with hamzat al-wasl (ا + sakin consonant).
    After proclitic stripping the segment_host begins with bare ا;
    treating it as a phonological V was a false BLOCK.

Contract:
  - All 10 tokens must return mabni_verdict != 'BLOCK'.
  - The slot patterns must include the evidence label
    (ALEF_FARQA or HAMZAT_AL_WASL) exactly where expected.
  - Evidence slots must have gate='' (invisible to word_gate BLOCK/DEFER tests).
"""

from __future__ import annotations
import sys
import os
import pytest

# Ensure repo root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from hokom_pipeline import hokom
from pipeline.p1_atomic_structure.slot_engineering import (
    HAMZAT_AL_WASL_PATTERN,
    ALEF_FARQA_PATTERN,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _run(token: str) -> dict:
    return hokom(token)


def _patterns(r: dict) -> list[str]:
    return [s['pattern'] for s in r.get('slots', []) if s.get('surface') != ' ']


def _mabni_verdict(r: dict) -> str:
    mabni = r.get('mabni')
    return getattr(mabni, 'verdict', None) if mabni else r.get('verdict', 'UNKNOWN')


# ─────────────────────────────────────────────────────────────────────────────
# Cluster A — ALEF_FARQA_BOUNDARY  (CVV+V false BLOCK)
# ─────────────────────────────────────────────────────────────────────────────

CLUSTER_A_CASES = [
    # (token, index_in_ayat, description)
    ('آمَنُوا',    3,  'Form IV past plural (آمن + واو الجماعة)'),
    ('دُعُوا',     77, 'Passive past plural (دعا passive + واو الجماعة)'),
    ('تَسْأَمُوا', 79, 'Form I imperfect subjunctive plural (سئم + واو)'),
    ('تَرْتَابُوا',95, 'Form VIII imperfect subjunctive plural (ريب + واو)'),
    ('وَأَشْهِدُوا',108,'Form IV imperative plural after waw (شهد + واو)'),
    ('تَفْعَلُوا', 117,'Form I imperfect subjunctive plural (فعل + واو)'),
]


@pytest.mark.parametrize('token,idx,desc', CLUSTER_A_CASES)
def test_cluster_a_not_blocked(token, idx, desc):
    """CVV+V tokens (واو الجماعة suffix) must NOT be BLOCK after fix."""
    r = _run(token)
    v = _mabni_verdict(r)
    assert v != 'BLOCK', (
        f"[{idx:03d}] {token!r} ({desc}): expected not-BLOCK, got {v!r}\n"
        f"  patterns: {_patterns(r)}"
    )


@pytest.mark.parametrize('token,idx,desc', CLUSTER_A_CASES)
def test_cluster_a_alef_farqa_evidence(token, idx, desc):
    """ALEF_FARQA evidence slot must appear in the slot list."""
    r = _run(token)
    pats = _patterns(r)
    assert ALEF_FARQA_PATTERN in pats, (
        f"[{idx:03d}] {token!r}: ALEF_FARQA evidence missing\n"
        f"  patterns: {pats}"
    )


@pytest.mark.parametrize('token,idx,desc', CLUSTER_A_CASES)
def test_cluster_a_alef_farqa_gate_transparent(token, idx, desc):
    """ALEF_FARQA evidence slot must have gate='' (transparent to word_gate)."""
    r = _run(token)
    slots = [s for s in r.get('slots', []) if s.get('surface') != ' ']
    farqa_slots = [s for s in slots if s['pattern'] == ALEF_FARQA_PATTERN]
    assert farqa_slots, f"[{idx:03d}] {token!r}: no ALEF_FARQA slot"
    for s in farqa_slots:
        assert s['gate'] == '', (
            f"[{idx:03d}] {token!r}: ALEF_FARQA slot has gate={s['gate']!r}, expected ''"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster B — HAMZAT_AL_WASL_SKIP  (+V false BLOCK)
# ─────────────────────────────────────────────────────────────────────────────

CLUSTER_B_CASES = [
    # (token, index_in_ayat, description)
    ('فَاكْتُبُوهُ',   10,  'Form I imperative pl. after فَ (كتب)'),
    ('وَاسْتَشْهِدُوا',52, 'Form X imperative pl. after وَ (شهد)'),
    ('وَامْرَأَتَانِ', 61, 'Noun with hamzat al-wasl after وَ'),
    ('وَاتَّقُوا',     121,'Form VIII imperative pl. after وَ (وقي)'),
]


@pytest.mark.parametrize('token,idx,desc', CLUSTER_B_CASES)
def test_cluster_b_not_blocked(token, idx, desc):
    """Hamzat-al-wasl tokens must NOT be BLOCK after fix."""
    r = _run(token)
    v = _mabni_verdict(r)
    assert v != 'BLOCK', (
        f"[{idx:03d}] {token!r} ({desc}): expected not-BLOCK, got {v!r}\n"
        f"  patterns: {_patterns(r)}"
    )


@pytest.mark.parametrize('token,idx,desc', CLUSTER_B_CASES)
def test_cluster_b_hamzat_al_wasl_evidence(token, idx, desc):
    """HAMZAT_AL_WASL evidence slot must appear in the slot list."""
    r = _run(token)
    pats = _patterns(r)
    assert HAMZAT_AL_WASL_PATTERN in pats, (
        f"[{idx:03d}] {token!r}: HAMZAT_AL_WASL evidence missing\n"
        f"  patterns: {pats}"
    )


@pytest.mark.parametrize('token,idx,desc', CLUSTER_B_CASES)
def test_cluster_b_hamzat_gate_transparent(token, idx, desc):
    """HAMZAT_AL_WASL evidence slot must have gate='' (transparent to word_gate)."""
    r = _run(token)
    slots = [s for s in r.get('slots', []) if s.get('surface') != ' ']
    hw_slots = [s for s in slots if s['pattern'] == HAMZAT_AL_WASL_PATTERN]
    assert hw_slots, f"[{idx:03d}] {token!r}: no HAMZAT_AL_WASL slot"
    for s in hw_slots:
        assert s['gate'] == '', (
            f"[{idx:03d}] {token!r}: HAMZAT_AL_WASL slot has gate={s['gate']!r}, expected ''"
        )
