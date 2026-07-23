"""
tests/p5_inflection/test_past_suffix_paradigm.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Paradigm tests for past-tense suffix analysis in feature_system.py.

Positive cases (must be identified as PAST with correct PNG):
  تَدَايَنْتُمْ  تَبَايَعْتُمْ  كَتَبْتُمْ  كَتَبْتُنَّ  كَتَبْنَا  كَتَبْتُ

Negative cases (must NOT be misidentified as PAST):
  يَتَفَاعَلُ  تَكْتُبُونَ  تَكْتُبِينَ  يَتَفَعَّلُ

Guard tests:
  VERBAL_PAST ⟹ mood = NOT_APPLICABLE   (past tense has no indicative/subjunctive/jussive)
  Extended imperfect check does not fire for Form V/VI past surfaces

P5-PAST-SUFFIX-01 through P5-PAST-SUFFIX-20
"""
from __future__ import annotations
import pytest
from pipeline.p5_inflection.feature_system import (
    identify_tense,
    extract_all_features,
    _has_imperfect_prefix,
)


# ── helpers ───────────────────────────────────────────────────────────────────
def _feats(surface: str) -> dict:
    return extract_all_features(surface)


# ── P5-PAST-SUFFIX-01 to 06: positive cases ──────────────────────────────────

class TestFormVIPastSuffix:
    """Form VI (تَفَاعَلَ) past tense with 2M_PL suffix تُمْ."""

    def test_tadayantum_is_past(self):
        """تَدَايَنْتُمْ must be PAST, not IMPERFECT."""
        assert identify_tense('تَدَايَنْتُمْ') == 'PAST'

    def test_tadayantum_prefix_not_imperfect(self):
        """_has_imperfect_prefix must return None for تَدَايَنْتُمْ."""
        assert _has_imperfect_prefix('تَدَايَنْتُمْ') is None

    def test_tadayantum_person_number_gender(self):
        f = _feats('تَدَايَنْتُمْ')
        assert f['tense_aspect'] == 'PAST'
        assert f['person'] == '2'
        assert f['number'] == 'PL'
        assert f['gender'] == 'M'

    def test_tadayantum_mood_not_applicable(self):
        """Past tense ⟹ mood must be NOT_APPLICABLE."""
        f = _feats('تَدَايَنْتُمْ')
        assert f['mood'] == 'NOT_APPLICABLE', (
            f"Expected NOT_APPLICABLE, got {f['mood']!r}. "
            f"Past tense has no indicative/subjunctive/jussive distinction."
        )

    def test_tadayantum_voice_active(self):
        f = _feats('تَدَايَنْتُمْ')
        assert f['voice'] == 'ACTIVE'


class TestFormVIPastTababaytum:
    """Form VI (تَفَاعَلَ) past: تَبَايَعْتُمْ (verb from Ayat al-Dayn)."""

    def test_tabayatum_is_past(self):
        assert identify_tense('تَبَايَعْتُمْ') == 'PAST'

    def test_tabayatum_prefix_not_imperfect(self):
        assert _has_imperfect_prefix('تَبَايَعْتُمْ') is None

    def test_tabayatum_person_number_gender(self):
        f = _feats('تَبَايَعْتُمْ')
        assert f['tense_aspect'] == 'PAST'
        assert f['person'] == '2'
        assert f['number'] == 'PL'
        assert f['gender'] == 'M'

    def test_tabayatum_mood_not_applicable(self):
        assert _feats('تَبَايَعْتُمْ')['mood'] == 'NOT_APPLICABLE'


# ── P5-PAST-SUFFIX-07 to 10: sound triliteral past ──────────────────────────

class TestSoundPastSuffixes:
    """كَتَبَ paradigm — 2M_PL, 2F_PL, 1PL, 1SG."""

    def test_katabtum_2mpl(self):
        f = _feats('كَتَبْتُمْ')
        assert f['tense_aspect'] == 'PAST'
        assert f['person'] == '2'
        assert f['number'] == 'PL'
        assert f['gender'] == 'M'
        assert f['mood'] == 'NOT_APPLICABLE'

    def test_katabtunna_2fpl(self):
        f = _feats('كَتَبْتُنَّ')
        assert f['tense_aspect'] == 'PAST'
        assert f['person'] == '2'
        assert f['number'] == 'PL'
        assert f['gender'] == 'F'
        assert f['mood'] == 'NOT_APPLICABLE'

    def test_katabna_1pl(self):
        f = _feats('كَتَبْنَا')
        assert f['tense_aspect'] == 'PAST'
        assert f['person'] == '1'
        assert f['number'] == 'PL'
        assert f['mood'] == 'NOT_APPLICABLE'

    def test_katabtu_1sg(self):
        f = _feats('كَتَبْتُ')
        assert f['tense_aspect'] == 'PAST'
        assert f['person'] == '1'
        assert f['number'] == 'SG'
        assert f['mood'] == 'NOT_APPLICABLE'

    def test_kataba_3msg_default(self):
        f = _feats('كَتَبَ')
        assert f['tense_aspect'] == 'PAST'
        assert f['person'] == '3'
        assert f['number'] == 'SG'
        assert f['gender'] == 'M'
        assert f['mood'] == 'NOT_APPLICABLE'


# ── P5-PAST-SUFFIX-11 to 15: imperfect must not be mislabelled PAST ─────────

class TestImperfectNotMislabelledPast:
    """Augmented imperfect forms must still be IMPERFECT after the fix."""

    def test_yatafaalu_form_vi_imperfect(self):
        assert identify_tense('يَتَفَاعَلُ') == 'IMPERFECT'

    def test_yatafaaalu_mood_indicative(self):
        assert _feats('يَتَفَاعَلُ')['mood'] == 'INDICATIVE'

    def test_yatafaalu_form_v_imperfect(self):
        assert identify_tense('يَتَفَعَّلُ') == 'IMPERFECT'

    def test_taktubuna_2mpl_imperfect(self):
        f = _feats('تَكْتُبُونَ')
        assert f['tense_aspect'] == 'IMPERFECT'
        assert f['number'] == 'PL'
        assert f['gender'] == 'M'

    def test_taktubina_2fsg_imperfect(self):
        f = _feats('تَكْتُبِينَ')
        assert f['tense_aspect'] == 'IMPERFECT'
        assert f['gender'] == 'F'


# ── P5-PAST-SUFFIX-16: generic PAST → NOT_APPLICABLE guard ──────────────────

class TestPastMoodGuard:
    """No past-tense verb should carry indicative/subjunctive/jussive mood."""

    @pytest.mark.parametrize("surface", [
        'نَصَرَ',       # 3M_SG PAST (FORM I)
        'ضَرَبَ',       # 3M_SG PAST
        'كَتَبَ',       # 3M_SG PAST
        'نَصَرُوا',     # 3M_PL PAST
        'نَصَرَتْ',     # 3F_SG PAST
        'كَتَبْتُمْ',   # 2M_PL PAST
        'كَتَبْنَا',    # 1PL PAST
        'تَدَايَنْتُمْ', # 2M_PL PAST Form VI
        'تَبَايَعْتُمْ', # 2M_PL PAST Form VI
    ])
    def test_past_mood_not_applicable(self, surface: str):
        f = _feats(surface)
        assert f['tense_aspect'] == 'PAST', (
            f"{surface}: expected tense=PAST, got {f['tense_aspect']!r}"
        )
        assert f['mood'] == 'NOT_APPLICABLE', (
            f"{surface}: expected mood=NOT_APPLICABLE, got {f['mood']!r}. "
            f"Past tense has no indicative/subjunctive/jussive distinction."
        )

    @pytest.mark.parametrize("surface,exp_mood", [
        ('يَنْصُرُ',   'INDICATIVE'),
        ('يَنْصُرَ',   'SUBJUNCTIVE'),
        ('يَنْصُرْ',   'JUSSIVE'),
        ('يَتَفَاعَلُ', 'INDICATIVE'),
    ])
    def test_imperfect_mood_preserved(self, surface: str, exp_mood: str):
        """Imperfect mood detection must be unaffected by the PAST fix."""
        f = _feats(surface)
        assert f['tense_aspect'] == 'IMPERFECT'
        assert f['mood'] == exp_mood, (
            f"{surface}: expected mood={exp_mood!r}, got {f['mood']!r}"
        )
