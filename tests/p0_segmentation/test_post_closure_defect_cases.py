#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_post_closure_defect_cases.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Regression tests for HOKOM-NORMALIZATION-SEGMENTATION-POST-CLOSURE-DEFECT-01.

20 canonical cases from the Ayat al-Dayn post-closure audit, exercising:
  - Alef madda normalization contract
  - Whole-token lexical protection
  - لفظ الجلالة case forms
  - Contracted لِل with solar assimilation
  - Clitic-only gate (بِكُمْ)
  - Various proclitic cases

HOKOM-NORMALIZATION-SEGMENTATION-POST-CLOSURE-DEFECT-01
"""
import pytest
from pipeline.p0_segmentation.models import SegmentationRequest
from pipeline.p0_segmentation.engine import segment_token
from pipeline.p0_segmentation.normalization import canonical_normalize, strip_diacritics

HAMZA = 'ء'
ALEF_WITH_MADDA = 'آ'
HAMZA_ALEF = HAMZA + 'ا'  # ءا — must NOT appear in madda expansion


def seg(s: str):
    req = SegmentationRequest(request_id=f'x:{s}', original_surface=s, normalized_surface=s)
    return segment_token(req)


# ── Cases 01–02: Alef madda normalization ────────────────────────────────────

def test_case_01_amaanuu_madda():
    """آمَنُوا: madda must be expanded, no ءا sequence inserted."""
    norm = canonical_normalize('آمَنُوا')
    assert ALEF_WITH_MADDA not in norm, f"madda not expanded: {norm!r}"
    assert HAMZA in norm, f"hamza missing: {norm!r}"
    assert HAMZA_ALEF not in norm, f"ءا (hamza+alef) must not appear: {norm!r}"


def test_case_02_aamana_madda():
    """آمَنَ: single-token madda expansion."""
    norm = canonical_normalize('آمَنَ')
    assert ALEF_WITH_MADDA not in norm, f"madda not expanded: {norm!r}"
    assert HAMZA in norm, f"hamza missing: {norm!r}"


# ── Cases 03–04: Preposition + noun / preposition + article ─────────────────

def test_case_03_bidayn():
    """بِدَيْنٍ: بِ proclitic + دَيْنٍ host."""
    b = seg('بِدَيْنٍ')
    assert tuple(strip_diacritics(p) for p in b.proclitics) == ('ب',), \
        f"proclitics={b.proclitics}"
    assert strip_diacritics(b.host or '') == 'دين', f"host={b.host}"


def test_case_04_bil_adl():
    """بِالْعَدْلِ: بِ + article + عَدْلِ host."""
    b = seg('بِالْعَدْلِ')
    proc = tuple(strip_diacritics(p) for p in b.proclitics)
    assert 'ب' in proc, f"proclitics={b.proclitics}"
    assert strip_diacritics(b.host or '') == 'عدل', f"host={b.host}"


# ── Cases 05–06: Multi-proclitic + future guard ──────────────────────────────

def test_case_05_walyaktub():
    """وَلْيَكْتُبْ: وَ + لْ multi-proclitic + verb host."""
    b = seg('وَلْيَكْتُبْ')
    proc = tuple(strip_diacritics(p) for p in b.proclitics)
    assert 'و' in proc and 'ل' in proc, f"proclitics={b.proclitics}"
    assert strip_diacritics(b.host or '').startswith('يكتب'), f"host={b.host}"


def test_case_06_safiihan():
    """سَفِيهًا: سَ must NOT be extracted as future particle."""
    b = seg('سَفِيهًا')
    assert b.proclitics == (), f"proclitics={b.proclitics}"
    assert b.enclitics == (), f"enclitics={b.enclitics}"


# ── Case 07: وَلِيُّهُ guard ───────────────────────────────────────────────

def test_case_07_waliyyuhu():
    """وَلِيُّهُ: وَ must NOT be extracted; only هُ is enclitic."""
    b = seg('وَلِيُّهُ')
    assert b.proclitics == (), (
        f"وَلِيُّهُ: وَ must not be proclitic, got {b.proclitics}. "
        f"Guard: after stripping هُ, remainder لِيُّ has only 2 consonants — "
        f"below the conjunction minimum of 3."
    )
    enc_bare = tuple(strip_diacritics(e) for e in b.enclitics)
    assert 'ه' in enc_bare, f"هُ should be enclitic, got {b.enclitics}"
    host_bare = strip_diacritics(b.host or '')
    assert host_bare.startswith('ولي'), f"host={b.host}"


# ── Case 08: يَكُونَا inflectional نَا ──────────────────────────────────────

def test_case_08_yakuuna():
    """يَكُونَا: نَا is dual alef (inflectional), NOT an attached pronoun."""
    b = seg('يَكُونَا')
    enc_bare = tuple(strip_diacritics(e) for e in b.enclitics)
    assert 'نا' not in enc_bare, (
        f"يَكُونَا: نَا must not be enclitic (it is ألف التثنية), "
        f"got {b.enclitics}"
    )


# ── Case 09: لِلشَّهَادَةِ contracted lil ───────────────────────────────────

def test_case_09_lil_shahada():
    """لِلشَّهَادَةِ: لِ proclitic + contracted article + شهادة host, no duplication."""
    b = seg('لِلشَّهَادَةِ')
    assert 'ل' in tuple(strip_diacritics(p) for p in b.proclitics), \
        f"proclitics={b.proclitics}"
    host_bare = strip_diacritics(b.host or '')
    assert host_bare == 'شهادة', f"host={b.host!r} bare={host_bare!r}"
    assert not host_bare.startswith('شش'), \
        f"solar assimilation leaked into host: {b.host!r}"


# ── Case 10: بِكُمْ clitic-only ──────────────────────────────────────────────

def test_case_10_bikum():
    """بِكُمْ: proclitic بِ + enclitic كُمْ, host=None (clitic-only)."""
    b = seg('بِكُمْ')
    assert b.host is None, (
        f"بِكُمْ: host must be None (clitic-only construction), got {b.host!r}"
    )
    assert b.clitic_only is True, f"بِكُمْ: clitic_only must be True"


# ── Cases 11–12: Whole-token protection ─────────────────────────────────────

def test_case_11_ayyuha():
    """أَيُّهَا: هَا must NOT be extracted as enclitic."""
    b = seg('أَيُّهَا')
    assert b.enclitics == (), (
        f"أَيُّهَا: هَا must not be enclitic (whole-token protection), "
        f"got {b.enclitics}"
    )


def test_case_12_alladhi():
    """الَّذِي: يَ must NOT be extracted as enclitic."""
    b = seg('الَّذِي')
    assert b.enclitics == (), (
        f"الَّذِي: يَ must not be enclitic (whole-token protection), "
        f"got {b.enclitics}"
    )


# ── Cases 13–15: لفظ الجلالة case forms ─────────────────────────────────────

def test_case_13_allah_nominative():
    """اللَّهُ (nominative): هُ must NOT be extracted as enclitic."""
    b = seg('اللَّهُ')
    assert b.enclitics == (), (
        f"اللَّهُ: هُ must not be enclitic, got {b.enclitics}"
    )


def test_case_14_allah_accusative():
    """اللَّهَ (accusative): هَ must NOT be extracted as enclitic."""
    b = seg('اللَّهَ')
    assert b.enclitics == (), (
        f"اللَّهَ: هَ must not be enclitic, got {b.enclitics}"
    )


def test_case_15_allah_genitive():
    """اللَّهِ (genitive): هِ must NOT be extracted as enclitic."""
    b = seg('اللَّهِ')
    assert b.enclitics == (), (
        f"اللَّهِ: هِ must not be enclitic, got {b.enclitics}"
    )


# ── Case 16: وَاللَّهُ ────────────────────────────────────────────────────────

def test_case_16_wa_allah():
    """وَاللَّهُ: وَ is proclitic; اللَّهُ is protected host; no enclitic."""
    b = seg('وَاللَّهُ')
    proc = tuple(strip_diacritics(p) for p in b.proclitics)
    assert 'و' in proc, f"وَاللَّهُ: وَ should be proclitic, got {b.proclitics}"
    assert b.enclitics == (), f"وَاللَّهُ: no enclitic expected, got {b.enclitics}"


# ── Cases 17–20: Conjunction + particle / negation ──────────────────────────

def test_case_17_fa_in():
    """فَإِنْ: فَ proclitic + إِنْ host."""
    b = seg('فَإِنْ')
    assert 'ف' in tuple(strip_diacritics(p) for p in b.proclitics), \
        f"proclitics={b.proclitics}"


def test_case_18_wa_in():
    """وَإِنْ: وَ proclitic + إِنْ host."""
    b = seg('وَإِنْ')
    assert 'و' in tuple(strip_diacritics(p) for p in b.proclitics), \
        f"proclitics={b.proclitics}"


def test_case_19_wa_la():
    """وَلَا: وَ proclitic + لَا host."""
    b = seg('وَلَا')
    assert 'و' in tuple(strip_diacritics(p) for p in b.proclitics), \
        f"proclitics={b.proclitics}"


def test_case_20_falaysa():
    """فَلَيْسَ: فَ proclitic + لَيْسَ host."""
    b = seg('فَلَيْسَ')
    assert 'ف' in tuple(strip_diacritics(p) for p in b.proclitics), \
        f"proclitics={b.proclitics}"
