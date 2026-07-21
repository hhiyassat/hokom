#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/slot_engine/test_slot_negative_controls.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-SLOT-ENGINE-PLURAL-VERB-UNLOCK-01 — negative controls.

These tests confirm that the two new slot-engine rules DO NOT fire on
forms they should not license:

  ALEF_FARQA must NOT fire when:
    - The word ends in waw without a trailing alef (no وا)
    - The alef follows CVV but is NOT the last phone (dual suffix -ان)

  HAMZAT_AL_WASL must NOT fire when:
    - The initial alef is NOT followed by a sakin consonant (e.g. آمَنَ)
    - The token is an operator/particle whose initial alef is already
      handled by a different boundary (إِذَا, إِلَى)

  JAMID_AALAM_BOUNDARY must remain intact:
    - الله and all declined forms must still return
      jamid_verdict='JAMID_AALAM_BOUNDARY' with root_candidate=None.
"""

from __future__ import annotations
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from hokom_pipeline import hokom
from pipeline.p1_atomic_structure.slot_engineering import (
    HAMZAT_AL_WASL_PATTERN,
    ALEF_FARQA_PATTERN,
)


def _patterns(r: dict) -> list[str]:
    return [s['pattern'] for s in r.get('slots', []) if s.get('surface') != ' ']


def _mabni_verdict(r: dict) -> str:
    mabni = r.get('mabni')
    return getattr(mabni, 'verdict', None) if mabni else r.get('verdict', 'UNKNOWN')


# ─────────────────────────────────────────────────────────────────────────────
# ALEF_FARQA must NOT fire: word ends in waw (no trailing alef)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('token', ['يَدْعُو', 'يَسْمُو', 'يَغْلُو'])
def test_no_alef_farqa_without_trailing_alef(token):
    """Words ending in waw (و) without trailing alef must NOT get ALEF_FARQA."""
    r = hokom(token)
    pats = _patterns(r)
    assert ALEF_FARQA_PATTERN not in pats, (
        f"{token!r}: ALEF_FARQA incorrectly fired. patterns={pats}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# ALEF_FARQA must NOT fire: CVV + alef NOT in final position (dual -ان)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('token', ['كِتَابَانِ', 'طَالِبَانِ', 'مُسْلِمَانِ'])
def test_no_alef_farqa_mid_word(token):
    """Dual forms with CVV+alef in non-final position must NOT get ALEF_FARQA."""
    r = hokom(token)
    pats = _patterns(r)
    assert ALEF_FARQA_PATTERN not in pats, (
        f"{token!r}: ALEF_FARQA fired on non-final alef. patterns={pats}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# HAMZAT_AL_WASL must NOT fire: initial alef NOT followed by sakin
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('token', ['آمَنَ', 'آمَنَتْ', 'آخُذُ'])
def test_no_hamzat_al_wasl_without_following_sakin(token):
    """Initial alef (madda/alef+mutaharrik) not followed by sakin must NOT get HAMZAT_AL_WASL."""
    r = hokom(token)
    pats = _patterns(r)
    assert HAMZAT_AL_WASL_PATTERN not in pats, (
        f"{token!r}: HAMZAT_AL_WASL incorrectly fired. patterns={pats}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# HAMZAT_AL_WASL must NOT fire: operators (handled by other boundary)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('token,expected_verdict', [
    ('إِذَا', 'OPERATOR_BOUNDARY'),
    ('إِلَى', 'OPERATOR_BOUNDARY'),
    ('أَنْ',  'OPERATOR_BOUNDARY'),
])
def test_operator_boundary_unaffected(token, expected_verdict):
    """Operators must not be rerouted by the new hamzat-al-wasl rule."""
    r = hokom(token)
    v = _mabni_verdict(r)
    assert v == expected_verdict, (
        f"{token!r}: expected {expected_verdict!r}, got {v!r}"
    )
    pats = _patterns(r)
    assert HAMZAT_AL_WASL_PATTERN not in pats, (
        f"{token!r}: HAMZAT_AL_WASL fired on operator. patterns={pats}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# JAMID_AALAM_BOUNDARY must remain intact for الله forms
# ─────────────────────────────────────────────────────────────────────────────

JALALA_CASES = [
    'اللَّهُ', 'اللَّهَ', 'اللَّهِ',
    'وَاللَّهُ', 'فَاللَّهُ', 'بِاللَّهِ', 'لِلَّهِ',
]


@pytest.mark.parametrize('token', JALALA_CASES)
def test_jalala_jamid_verdict_unchanged(token):
    """Lafz al-jalala must return jamid_verdict='JAMID_AALAM_BOUNDARY'."""
    r = hokom(token)
    jv = r.get('jamid_verdict')
    assert jv == 'JAMID_AALAM_BOUNDARY', (
        f"{token!r}: jamid_verdict={jv!r}, expected 'JAMID_AALAM_BOUNDARY'"
    )


@pytest.mark.parametrize('token', JALALA_CASES)
def test_jalala_no_root_candidate(token):
    """Lafz al-jalala must have root_candidate=None (no root extraction attempted)."""
    r = hokom(token)
    rc = r.get('root_candidate')
    assert rc is None, (
        f"{token!r}: root_candidate={rc!r}, expected None"
    )
