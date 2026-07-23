#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/word_class/test_word_class_routing.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Word class and subclass routing correctness tests.

HOKOM-AYAT-AL-DAYN-WORD-CLASS-AND-SUBCLASS-ROUTING-CORRECTION-01

Tests cover all five defect classes:
  Class A — ISM:MASDAR priority inversion for augmented verbs
  Class B — VERBAL_PAST hard-coded in engine for imperfect verbs
  Class C — non-verbs misclassified as FI3L
    C1: _is_mudaric_surface false positives (أُخْرَى, أَلَّا)
    C2: ambiguous path + p4a for nouns/adverbs (بَيْنَكُمْ, عِنْدَ, الْحَقُّ)
  Class E — subclass does not match Phase-5 tense_aspect

Positive routing:  FI3L must be assigned with correct subclass
Negative routing:  non-verbs must NOT receive FI3L
Invariant tests:   VERBAL_PAST ⟹ tense ≠ IMPERFECT; VERBAL_IMPERFECT ⟹ tense ≠ PAST
Full-verse metrics: 0 contradictions across all 129 Ayat al-Dayn tokens

WCR-01 through WCR-40
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from hokom_pipeline import hokom as _hokom  # noqa: E402


def _wc(surface: str) -> dict:
    hr = _hokom(surface)
    return {
        'word_class':         hr.get('word_class'),
        'word_class_subclass': hr.get('word_class_subclass'),
        'tense_aspect':       hr.get('tense_aspect'),
    }


# ════════════════════════════════════════════════════════════════════════════
# CLASS A — masdar priority inversion (augmented verbs)
# Fix: licensed_verbal_host + verbal path → FI3L beats ISM:MASDAR
# ════════════════════════════════════════════════════════════════════════════

class TestClassA_MasdarPriorityInversion:
    """
    Augmented verbs (Form II-X) with phase4c masdar acceptance must be
    classified as FI3L (verb), not ISM:MASDAR.

    Before fix: masdar_accepted=True fired in Step 3 BEFORE licensed_verbal_host
                was checked in Step 6.
    After fix:  Step 3 has guard — if licensed_verbal_host=True AND verbal
                morphology path, skip masdar and proceed to Step 6.
    """

    def test_amanuu_is_fi3l_not_masdar(self):
        """آمَنُوا (Form IV past 3MPL) → FI3L, not ISM:MASDAR."""
        r = _wc('آمَنُوا')
        assert r['word_class'] == 'FI3L', (
            f"آمَنُوا: expected FI3L, got {r['word_class']!r}. "
            f"masdar priority inversion — Class A bug not fixed."
        )

    def test_amanuu_subclass_verbal_past(self):
        """آمَنُوا must be VERBAL_PAST (3MPL past suffix وا)."""
        r = _wc('آمَنُوا')
        assert r['word_class_subclass'] == 'VERBAL_PAST'

    def test_allamahu_is_fi3l(self):
        """عَلَّمَهُ (Form II past 3MSG + object هُ) → FI3L:VERBAL_PAST."""
        r = _wc('عَلَّمَهُ')
        assert r['word_class'] == 'FI3L'
        assert r['word_class_subclass'] == 'VERBAL_PAST'

    def test_yastaTiiu_is_fi3l_imperfect(self):
        """يَسْتَطِيعُ (Form X imperfect 3MSG) → FI3L:VERBAL_IMPERFECT."""
        r = _wc('يَسْتَطِيعُ')
        assert r['word_class'] == 'FI3L'
        assert r['word_class_subclass'] == 'VERBAL_IMPERFECT'
        assert r['tense_aspect'] == 'IMPERFECT'

    def test_yumilla_is_fi3l_imperfect(self):
        """يُمِلَّ (Form IV imperfect subjunctive) → FI3L."""
        r = _wc('يُمِلَّ')
        assert r['word_class'] == 'FI3L'

    def test_yudaarra_is_fi3l(self):
        """يُضَارَّ (Form III passive imperfect) → FI3L."""
        r = _wc('يُضَارَّ')
        assert r['word_class'] == 'FI3L'


# ════════════════════════════════════════════════════════════════════════════
# CLASS B / E — subclass must reflect tense (VERBAL_PAST / VERBAL_IMPERFECT)
# Fix: _subclass_from_surface() called in Steps 6, 7, 8 + post-Phase-5 reconciliation
# ════════════════════════════════════════════════════════════════════════════

class TestClassB_SubclassFromTense:
    """
    Imperfect verbs must carry VERBAL_IMPERFECT, not VERBAL_PAST.
    Past verbs must carry VERBAL_PAST.

    Before fix: all verbal_root_path tokens → VERBAL_PAST (hardcoded).
    After fix:  _subclass_from_surface(normalized_surface) derives the subclass
                from the surface's imperfect-prefix / personal-suffix pattern.
                The post-Phase-5 reconciliation in hokom_pipeline.py enforces
                the invariant FI3L + tense_aspect → correct subclass.
    """

    @pytest.mark.parametrize("surface,exp_sub,exp_ta", [
        ('يَكْتُبَ',   'VERBAL_IMPERFECT', 'IMPERFECT'),
        ('يَأْبَ',     'VERBAL_IMPERFECT', 'IMPERFECT'),
        ('يَبْخَسْ',   'VERBAL_IMPERFECT', 'IMPERFECT'),
        ('تَرْضَوْنَ', 'VERBAL_IMPERFECT', 'IMPERFECT'),
        ('يَكْتُبُ',   'VERBAL_IMPERFECT', 'IMPERFECT'),
        ('يَسْتَطِيعُ','VERBAL_IMPERFECT', 'IMPERFECT'),
        ('تَرْتَابُوا','VERBAL_IMPERFECT', 'IMPERFECT'),
        ('تَسْأَمُوا', 'VERBAL_IMPERFECT', 'IMPERFECT'),
        ('تَفْعَلُوا', 'VERBAL_IMPERFECT', 'IMPERFECT'),
    ])
    def test_imperfect_subclass(self, surface, exp_sub, exp_ta):
        """Imperfect verbs must be FI3L:VERBAL_IMPERFECT, not VERBAL_PAST."""
        r = _wc(surface)
        assert r['word_class'] == 'FI3L', (
            f"{surface}: expected FI3L, got {r['word_class']!r}"
        )
        assert r['word_class_subclass'] == exp_sub, (
            f"{surface}: expected subclass {exp_sub!r}, got {r['word_class_subclass']!r}. "
            f"Class B: VERBAL_PAST was hardcoded for all verbal_root_path tokens."
        )
        assert r['tense_aspect'] == exp_ta, (
            f"{surface}: expected tense {exp_ta!r}, got {r['tense_aspect']!r}"
        )

    @pytest.mark.parametrize("surface,exp_sub,exp_ta", [
        ('كَتَبَ',       'VERBAL_PAST', 'PAST'),
        ('ذَهَبَ',       'VERBAL_PAST', 'PAST'),
        ('نَصَرَ',       'VERBAL_PAST', 'PAST'),
        ('آمَنُوا',     'VERBAL_PAST', 'PAST'),
        ('عَلَّمَهُ',   'VERBAL_PAST', 'PAST'),
        ('تَدَايَنْتُمْ','VERBAL_PAST', 'PAST'),
        ('تَبَايَعْتُمْ','VERBAL_PAST', 'PAST'),
        ('كَتَبَتْ',    'VERBAL_PAST', 'PAST'),
    ])
    def test_past_subclass(self, surface, exp_sub, exp_ta):
        """Past verbs must be FI3L:VERBAL_PAST."""
        r = _wc(surface)
        assert r['word_class'] == 'FI3L', (
            f"{surface}: expected FI3L, got {r['word_class']!r}"
        )
        assert r['word_class_subclass'] == exp_sub, (
            f"{surface}: expected subclass {exp_sub!r}, got {r['word_class_subclass']!r}"
        )
        assert r['tense_aspect'] == exp_ta, (
            f"{surface}: expected tense {exp_ta!r}, got {r['tense_aspect']!r}"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLASS C1 — _is_mudaric_surface false positives
# Fix: ى-ending guard + أَلَّ/إِلَّ shadda guard in morphology_path.py
# ════════════════════════════════════════════════════════════════════════════

class TestClassC1_MudaricFalsePositives:
    """
    Adjectives ending in ى and particles with أَلَّ/إِلَّ pattern were
    incorrectly classified as VERBAL_ROOT_PATH by _is_mudaric_surface().

    Before fix: أُخْرَى → verbal_root_path → FI3L:VERBAL_PAST (wrong)
                أَلَّا   → verbal_root_path → FI3L:VERBAL_PAST (wrong)
    After fix:  ى-ending guard and lam+shadda guard make _is_mudaric_surface
                return False → AMBIGUOUS path → DEFERRED (not FI3L).
    """

    def test_al_ukhra_not_fi3l(self):
        """الْأُخْرَى (comparative adjective) must NOT be FI3L."""
        r = _wc('الْأُخْرَى')
        assert r['word_class'] != 'FI3L', (
            f"الْأُخْرَى: got FI3L — C1 bug: أُخْرَى matched imperfect prefix أُ+خ"
        )

    def test_alla_not_fi3l(self):
        """أَلَّا (particle أَنْ + لَا) must NOT be FI3L."""
        r = _wc('أَلَّا')
        assert r['word_class'] != 'FI3L', (
            f"أَلَّا: got FI3L — C1 bug: أَلَّ matched imperfect prefix"
        )

    def test_illa_not_fi3l(self):
        """إِلَّا (exception particle) must NOT be FI3L."""
        r = _wc('إِلَّا')
        assert r['word_class'] != 'FI3L', (
            f"إِلَّا: got FI3L — C1 bug: إِلَّ matched imperfect prefix"
        )

    def test_kubra_not_fi3l(self):
        """كُبْرَى (elative adjective ending in ى) must NOT be FI3L."""
        r = _wc('كُبْرَى')
        assert r['word_class'] != 'FI3L', (
            f"كُبْرَى: got FI3L — C1 bug: ى ending should block VERBAL_ROOT_PATH"
        )

    def test_bushra_not_fi3l(self):
        """بُشْرَى (noun ending in ى) must NOT be FI3L."""
        r = _wc('بُشْرَى')
        assert r['word_class'] != 'FI3L', (
            f"بُشْرَى: got FI3L — C1 bug: ى ending should block VERBAL_ROOT_PATH"
        )

    # Regression: valid verbs with أَ prefix must NOT be affected
    def test_aktub_1sg_imperfect_still_verbal(self):
        """أَكْتُبُ (1SG imperfect) must still be classified as FI3L."""
        r = _wc('أَكْتُبُ')
        assert r['word_class'] == 'FI3L', (
            f"أَكْتُبُ: expected FI3L, got {r['word_class']!r}. "
            f"C1 fix must not block valid 1SG imperfect verbs."
        )

    def test_atafaalu_form_v_1sg_still_verbal(self):
        """أَتَفَعَّلُ (Form V 1SG imperfect) must still be FI3L.

        Note: أَتَفَاعَلُ (Form VI, with long-vowel ا in stem) triggers the
        existing broken-plural heuristic and is excluded here — that is a
        pre-existing limitation unrelated to the C1 fix.
        """
        r = _wc('أَتَفَعَّلُ')
        assert r['word_class'] == 'FI3L', (
            f"أَتَفَعَّلُ: expected FI3L, got {r['word_class']!r}. "
            f"C1 fix must not block valid Form V 1SG imperfect verbs."
        )


# ════════════════════════════════════════════════════════════════════════════
# CLASS C2 — ambiguous path + p4a for non-verbs
# Fix: article guard (G1) + p4b:attempted guard (G2) in engine Step 8
# ════════════════════════════════════════════════════════════════════════════

class TestClassC2_AmbiguousPathNonVerbs:
    """
    Nouns and adverbs whose trilateral root skeleton passes phase4a but
    whose surface is NOT a conjugated verb must not receive FI3L.

    Before fix: Step 8 (ambiguous + p4a) fired unconditionally → FI3L:VERBAL_PAST.
    After fix:
      G1 — definite article (ال) → cannot be finite verb → DEFER
      G2 — p4b never attempted (NOT_APPLICABLE) AND no verbal host license → DEFER
    """

    def test_baynakum_not_fi3l(self):
        """بَيْنَكُمْ (preposition + pronoun) must NOT be FI3L."""
        r = _wc('بَيْنَكُمْ')
        assert r['word_class'] != 'FI3L', (
            f"بَيْنَكُمْ: got FI3L — C2 bug: ambiguous+p4a fired without p4b evidence"
        )

    def test_inda_not_fi3l(self):
        """عِنْدَ (adverb/quasi-preposition) must NOT be FI3L."""
        r = _wc('عِنْدَ')
        assert r['word_class'] != 'FI3L', (
            f"عِنْدَ: got FI3L — C2 bug: ambiguous+p4a fired without p4b evidence"
        )

    def test_alhaqq_not_fi3l(self):
        """الْحَقُّ (definite noun with article) must NOT be FI3L."""
        r = _wc('الْحَقُّ')
        assert r['word_class'] != 'FI3L', (
            f"الْحَقُّ: got FI3L — C2 bug: article guard (G1) did not fire"
        )

    def test_alladhiina_not_fi3l(self):
        """الَّذِينَ (relative pronoun with article) must NOT be FI3L."""
        r = _wc('الَّذِينَ')
        assert r['word_class'] != 'FI3L'

    # Regression: 3MSG past verbs on ambiguous path must still be FI3L
    def test_kataba_still_verbal(self):
        """كَتَبَ (3MSG past, no suffix) must remain FI3L:VERBAL_PAST."""
        r = _wc('كَتَبَ')
        assert r['word_class'] == 'FI3L', (
            f"كَتَبَ: expected FI3L, got {r['word_class']!r}. "
            f"C2 guard must not block valid 3MSG past verbs."
        )
        assert r['word_class_subclass'] == 'VERBAL_PAST'

    def test_dhahaba_still_verbal(self):
        """ذَهَبَ (3MSG past) must remain FI3L:VERBAL_PAST."""
        r = _wc('ذَهَبَ')
        assert r['word_class'] == 'FI3L'
        assert r['word_class_subclass'] == 'VERBAL_PAST'

    def test_nasara_still_verbal(self):
        """نَصَرَ (3MSG past, verbal_root_path) must remain FI3L:VERBAL_PAST."""
        r = _wc('نَصَرَ')
        assert r['word_class'] == 'FI3L'
        assert r['word_class_subclass'] == 'VERBAL_PAST'


# ════════════════════════════════════════════════════════════════════════════
# INVARIANT TESTS — cross-layer consistency
# ════════════════════════════════════════════════════════════════════════════

class TestInvariants:
    """
    Hard consistency rules that must hold for every token:
      INV-1: FI3L:VERBAL_PAST must not have tense_aspect=IMPERFECT
      INV-2: FI3L:VERBAL_IMPERFECT must not have tense_aspect=PAST
      INV-3: No FI3L token with tense_aspect=IMPERFECT may carry VERBAL_PAST subclass
      INV-4: ISM:MASDAR tokens must not have tense_aspect=PAST or IMPERFECT
    """

    AYAT_AL_DAYN = (
        'يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا تَدَايَنْتُمْ بِدَيْنٍ إِلَى أَجَلٍ مُسَمًّى '
        'فَاكْتُبُوهُ وَلْيَكْتُبْ بَيْنَكُمْ كَاتِبٌ بِالْعَدْلِ وَلَا يَأْبَ كَاتِبٌ '
        'أَنْ يَكْتُبَ كَمَا عَلَّمَهُ اللَّهُ فَلْيَكْتُبْ وَلْيُمْلِلِ الَّذِي عَلَيْهِ '
        'الْحَقُّ وَلْيَتَّقِ اللَّهَ رَبَّهُ وَلَا يَبْخَسْ مِنْهُ شَيْئًا فَإِنْ كَانَ '
        'الَّذِي عَلَيْهِ الْحَقُّ سَفِيهًا أَوْ ضَعِيفًا أَوْ لَا يَسْتَطِيعُ أَنْ يُمِلَّ '
        'هُوَ فَلْيُمْلِلْ وَلِيُّهُ بِالْعَدْلِ وَاسْتَشْهِدُوا شَهِيدَيْنِ مِنْ رِجَالِكُمْ '
        'فَإِنْ لَمْ يَكُونَا رَجُلَيْنِ فَرَجُلٌ وَامْرَأَتَانِ مِمَّنْ تَرْضَوْنَ مِنَ '
        'الشُّهَدَاءِ أَنْ تَضِلَّ إِحْدَاهُمَا فَتُذَكِّرَ إِحْدَاهُمَا الْأُخْرَى وَلَا '
        'يَأْبَ الشُّهَدَاءُ إِذَا مَا دُعُوا وَلَا تَسْأَمُوا أَنْ تَكْتُبُوهُ صَغِيرًا '
        'أَوْ كَبِيرًا إِلَى أَجَلِهِ ذَلِكُمْ أَقْسَطُ عِنْدَ اللَّهِ وَأَقْوَمُ '
        'لِلشَّهَادَةِ وَأَدْنَى أَلَّا تَرْتَابُوا إِلَّا أَنْ تَكُونَ تِجَارَةً '
        'حَاضِرَةً تُدِيرُونَهَا بَيْنَكُمْ فَلَيْسَ عَلَيْكُمْ جُنَاحٌ أَلَّا تَكْتُبُوهَا '
        'وَأَشْهِدُوا إِذَا تَبَايَعْتُمْ وَلَا يُضَارَّ كَاتِبٌ وَلَا شَهِيدٌ وَإِنْ '
        'تَفْعَلُوا فَإِنَّهُ فُسُوقٌ بِكُمْ وَاتَّقُوا اللَّهَ وَيُعَلِّمُكُمُ اللَّهُ '
        'وَاللَّهُ بِكُلِّ شَيْءٍ عَلِيمٌ'
    )

    @pytest.fixture(scope='class')
    def all_results(self):
        tokens = self.AYAT_AL_DAYN.split()
        return [(t, _hokom(t)) for t in tokens]

    def test_inv1_verbal_past_not_imperfect(self, all_results):
        """INV-1: FI3L:VERBAL_PAST must never have tense_aspect=IMPERFECT."""
        violations = [
            f"[{i+1}] {t}: sub=VERBAL_PAST, ta=IMPERFECT"
            for i, (t, hr) in enumerate(all_results)
            if hr.get('word_class') == 'FI3L'
            and hr.get('word_class_subclass') == 'VERBAL_PAST'
            and hr.get('tense_aspect') == 'IMPERFECT'
        ]
        assert not violations, (
            f"VERBAL_PAST_WITH_IMPERFECT_COUNT = {len(violations)}\n"
            + '\n'.join(violations)
        )

    def test_inv2_verbal_imperfect_not_past(self, all_results):
        """INV-2: FI3L:VERBAL_IMPERFECT must never have tense_aspect=PAST."""
        violations = [
            f"[{i+1}] {t}: sub=VERBAL_IMPERFECT, ta=PAST"
            for i, (t, hr) in enumerate(all_results)
            if hr.get('word_class') == 'FI3L'
            and hr.get('word_class_subclass') == 'VERBAL_IMPERFECT'
            and hr.get('tense_aspect') == 'PAST'
        ]
        assert not violations, (
            f"VERBAL_IMPERFECT_WITH_PAST_COUNT = {len(violations)}\n"
            + '\n'.join(violations)
        )

    def test_inv3_known_non_verbs_not_fi3l(self, all_results):
        """INV-3: Confirmed non-verbal tokens must not receive FI3L."""
        CONFIRMED_NON_VERBS = {
            'بَيْنَكُمْ', 'الْحَقُّ', 'الْأُخْرَى', 'أَلَّا', 'عِنْدَ',
        }
        violations = [
            f"{t}: got word_class=FI3L"
            for t, hr in all_results
            if t in CONFIRMED_NON_VERBS
            and hr.get('word_class') == 'FI3L'
        ]
        assert not violations, (
            f"NON_VERBS_CLASSIFIED_AS_VERBS = {len(violations)}\n"
            + '\n'.join(violations)
        )

    def test_inv4_known_verbs_not_masdar(self, all_results):
        """INV-4: Confirmed finite verbs must not be ISM:MASDAR."""
        CONFIRMED_VERBS = {
            'آمَنُوا', 'تَدَايَنْتُمْ', 'يَأْبَ', 'يَكْتُبَ', 'عَلَّمَهُ',
            'يَبْخَسْ', 'يَسْتَطِيعُ', 'تَرْضَوْنَ', 'تَبَايَعْتُمْ',
        }
        violations = [
            f"{t}: got word_class=ISM, subclass=MASDAR"
            for t, hr in all_results
            if t in CONFIRMED_VERBS
            and hr.get('word_class') == 'ISM'
            and hr.get('word_class_subclass') == 'MASDAR'
        ]
        assert not violations, (
            f"VERBS_CLASSIFIED_AS_NOUNS = {len(violations)}\n"
            + '\n'.join(violations)
        )

    def test_total_subclass_contradictions_zero(self, all_results):
        """Total subclass contradictions across 129 tokens must be 0."""
        sc = sum(
            1 for _, hr in all_results
            if hr.get('word_class') == 'FI3L' and (
                (hr.get('word_class_subclass') == 'VERBAL_PAST'
                 and hr.get('tense_aspect') == 'IMPERFECT')
                or
                (hr.get('word_class_subclass') == 'VERBAL_IMPERFECT'
                 and hr.get('tense_aspect') == 'PAST')
            )
        )
        assert sc == 0, (
            f"WORD_CLASS_SUBCLASS_CONTRADICTIONS = {sc} (expected 0)"
        )


# ════════════════════════════════════════════════════════════════════════════
# SPOT TESTS — key tokens from Ayat al-Dayn
# ════════════════════════════════════════════════════════════════════════════

class TestSpotChecks:
    """Spot-checks for specific tokens from Ayat al-Dayn."""

    def test_tadayantum_past_plural(self):
        """تَدَايَنْتُمْ (Form VI 2M_PL past) → FI3L:VERBAL_PAST."""
        r = _wc('تَدَايَنْتُمْ')
        assert r['word_class'] == 'FI3L'
        assert r['word_class_subclass'] == 'VERBAL_PAST'
        assert r['tense_aspect'] == 'PAST'

    def test_tabayatum_past_plural(self):
        """تَبَايَعْتُمْ (Form VI 2M_PL past) → FI3L:VERBAL_PAST."""
        r = _wc('تَبَايَعْتُمْ')
        assert r['word_class'] == 'FI3L'
        assert r['word_class_subclass'] == 'VERBAL_PAST'
        assert r['tense_aspect'] == 'PAST'

    def test_tardawna_imperfect_plural(self):
        """تَرْضَوْنَ (imperfect 2M_PL) → FI3L:VERBAL_IMPERFECT."""
        r = _wc('تَرْضَوْنَ')
        assert r['word_class'] == 'FI3L'
        assert r['word_class_subclass'] == 'VERBAL_IMPERFECT'
        assert r['tense_aspect'] == 'IMPERFECT'

    def test_yaktuba_subjunctive(self):
        """يَكْتُبَ (imperfect subjunctive 3MSG) → FI3L:VERBAL_IMPERFECT."""
        r = _wc('يَكْتُبَ')
        assert r['word_class'] == 'FI3L'
        assert r['word_class_subclass'] == 'VERBAL_IMPERFECT'
        assert r['tense_aspect'] == 'IMPERFECT'

    def test_yabkhas_jussive(self):
        """يَبْخَسْ (imperfect jussive 3MSG) → FI3L:VERBAL_IMPERFECT."""
        r = _wc('يَبْخَسْ')
        assert r['word_class'] == 'FI3L'
        assert r['word_class_subclass'] == 'VERBAL_IMPERFECT'
        assert r['tense_aspect'] == 'IMPERFECT'

    def test_kana_past(self):
        """كَانَ (hollow verb, 3MSG past) → FI3L:VERBAL_PAST."""
        r = _wc('كَانَ')
        assert r['word_class'] == 'FI3L'
        assert r['word_class_subclass'] == 'VERBAL_PAST'

    def test_tujara_masdar_noun(self):
        """تِجَارَةً (nominal masdar, accusative) → ISM:MASDAR (correct)."""
        r = _wc('تِجَارَةً')
        assert r['word_class'] == 'ISM'
        assert r['word_class_subclass'] == 'MASDAR'
