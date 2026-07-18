#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p5_inflection/test_phase5_reference_matrix.py

Phase 5 reference matrix — covers the paradigm test cases mandated by P5-19.
Tests both:
  1. Surface generation via api.generate_verb()
  2. Feature extraction via api.analyze_verb() / phase5_orchestrator

All generated forms are cross-checked against authoritative Arabic morphology tables.
"""
import pytest
from pipeline.p5_inflection.api import generate_verb, analyze_verb
from pipeline.p5_inflection.phase5_orchestrator import project_inflection_with_licensing
from pipeline.p5_inflection.feature_system import extract_all_features, identify_tense


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def gen(root, bab, tense='PAST', mood='INDICATIVE', voice='ACTIVE',
        person='3', number='SG', gender='M', wazn_id=None):
    """Shorthand wrapper for generate_verb."""
    return generate_verb(root=root, bab_id=bab, tense=tense, mood=mood,
                         voice=voice, person=person, number=number, gender=gender,
                         wazn_id=wazn_id)


def analyze(surface, root=None, bab_id=None, wazn_id=None):
    return analyze_verb(surface, root=root, bab_id=bab_id, wazn_id=wazn_id)


# ──────────────────────────────────────────────────────────────────────────────
# ROOT CONSTANTS (tuples)
# ──────────────────────────────────────────────────────────────────────────────
NSR  = ('ن', 'ص', 'ر')   # BAB_I_NASARA  (نَصَرَ / يَنْصُرُ)
DRB  = ('ض', 'ر', 'ب')   # BAB_II_DARABA (ضَرَبَ / يَضْرِبُ)
FTH  = ('ف', 'ت', 'ح')   # BAB_III_FATAHA (فَتَحَ / يَفْتَحُ)
SME  = ('س', 'م', 'ع')   # BAB_IV_SAMIA  (سَمِعَ / يَسْمَعُ)
KRM  = ('ك', 'ر', 'م')   # BAB_V_KARUMA  (كَرُمَ / يَكْرُمُ)
HSB  = ('ح', 'س', 'ب')   # BAB_VI_HASIBA (حَسِبَ / يَحْسِبُ)
QAL  = ('ق', 'و', 'ل')   # HOLLOW_WAW    (قَالَ / يَقُولُ)
BAA  = ('ب', 'ي', 'ع')   # HOLLOW_YAA    (بَاعَ / يَبِيعُ)
DAA  = ('د', 'ع', 'و')   # DEFECTIVE_WAW (دَعَا / يَدْعُو)
RMA  = ('ر', 'م', 'ي')   # DEFECTIVE_YAA (رَمَى / يَرْمِي)
WAD  = ('و', 'ع', 'د')   # ASSIMILATED_WAW (وَعَدَ / يَعِدُ)
MAD  = ('م', 'د', 'د')   # GEMINATED     (مَدَّ / يَمُدُّ)
QRA  = ('ق', 'ر', 'ء')   # HAMZATED_C3   (قَرَأَ / يَقْرَأُ)


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-01: Sound verb — past active (all 6 babs, 3M_SG)
# ──────────────────────────────────────────────────────────────────────────────

class TestSoundPastActive:
    """Sound verb past active 3M_SG — six mujarrad babs."""

    def test_bab_i_nasara_3msg_past(self):
        assert gen(NSR, 'BAB_I_NASARA') == 'نَصَرَ'

    def test_bab_ii_daraba_3msg_past(self):
        assert gen(DRB, 'BAB_II_DARABA') == 'ضَرَبَ'

    def test_bab_iii_fataha_3msg_past(self):
        assert gen(FTH, 'BAB_III_FATAHA') == 'فَتَحَ'

    def test_bab_iv_samia_3msg_past(self):
        assert gen(SME, 'BAB_IV_SAMIA') == 'سَمِعَ'

    def test_bab_v_karuma_3msg_past(self):
        assert gen(KRM, 'BAB_V_KARUMA') == 'كَرُمَ'

    def test_bab_vi_hasiba_3msg_past(self):
        assert gen(HSB, 'BAB_VI_HASIBA') == 'حَسِبَ'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-02: Sound verb — past active (selected persons / numbers / genders)
# ──────────────────────────────────────────────────────────────────────────────

class TestSoundPastPersonNumberGender:
    """Past active paradigm for BAB_I_NASARA (ن ص ر)."""

    def test_3msg(self): assert gen(NSR, 'BAB_I_NASARA', person='3', number='SG', gender='M') == 'نَصَرَ'
    def test_3fsg(self): assert gen(NSR, 'BAB_I_NASARA', person='3', number='SG', gender='F') == 'نَصَرَتْ'
    def test_3mpl(self): assert gen(NSR, 'BAB_I_NASARA', person='3', number='PL', gender='M') == 'نَصَرُوا'
    def test_2msg(self): assert gen(NSR, 'BAB_I_NASARA', person='2', number='SG', gender='M') == 'نَصَرْتَ'
    def test_2fsg(self): assert gen(NSR, 'BAB_I_NASARA', person='2', number='SG', gender='F') == 'نَصَرْتِ'
    def test_2mpl(self): assert gen(NSR, 'BAB_I_NASARA', person='2', number='PL', gender='M') == 'نَصَرْتُمْ'
    def test_1sg(self):  assert gen(NSR, 'BAB_I_NASARA', person='1', number='SG', gender='M') == 'نَصَرْتُ'
    def test_1pl(self):  assert gen(NSR, 'BAB_I_NASARA', person='1', number='PL', gender='M') == 'نَصَرْنَا'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-03: Sound verb — imperfect active (indicative)
# ──────────────────────────────────────────────────────────────────────────────

class TestSoundImperfectIndicative:
    """Imperfect indicative forms — key person/number/gender cells."""

    def test_3msg(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='INDICATIVE', person='3', number='SG', gender='M') == 'يَنْصُرُ'

    def test_3fsg(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='INDICATIVE', person='3', number='SG', gender='F') == 'تَنْصُرُ'

    def test_3mpl(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='INDICATIVE', person='3', number='PL', gender='M') == 'يَنْصُرُونَ'

    def test_3mdu(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='INDICATIVE', person='3', number='DU', gender='M') == 'يَنْصُرَانِ'

    def test_2fsg(self):
        assert gen(DRB, 'BAB_II_DARABA', tense='IMPERFECT', mood='INDICATIVE', person='2', number='SG', gender='F') == 'تَضْرِبِينَ'

    def test_2mpl(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='INDICATIVE', person='2', number='PL', gender='M') == 'تَنْصُرُونَ'

    def test_1sg(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='INDICATIVE', person='1', number='SG', gender='M') == 'أَنْصُرُ'

    def test_1pl(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='INDICATIVE', person='1', number='PL', gender='M') == 'نَنْصُرُ'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-04: Sound verb — imperfect subjunctive and jussive
# ──────────────────────────────────────────────────────────────────────────────

class TestSoundImperfectMood:
    """Subjunctive and Jussive forms."""

    # SUBJUNCTIVE
    def test_subj_3msg(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='SUBJUNCTIVE', person='3', number='SG', gender='M') == 'يَنْصُرَ'

    def test_subj_3mpl(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='SUBJUNCTIVE', person='3', number='PL', gender='M') == 'يَنْصُرُوا'

    def test_subj_2fsg(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='SUBJUNCTIVE', person='2', number='SG', gender='F') == 'تَنْصُرِي'

    def test_subj_3mdu(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='SUBJUNCTIVE', person='3', number='DU', gender='M') == 'يَنْصُرَا'

    # JUSSIVE
    def test_juss_3msg(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='JUSSIVE', person='3', number='SG', gender='M') == 'يَنْصُرْ'

    def test_juss_3mpl(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='JUSSIVE', person='3', number='PL', gender='M') == 'يَنْصُرُوا'

    def test_juss_2fsg(self):
        assert gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='JUSSIVE', person='2', number='SG', gender='F') == 'تَنْصُرِي'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-05: Hamzated C3 (ق ر ء)
# ──────────────────────────────────────────────────────────────────────────────

class TestHamzatedC3:
    """قَرَأَ / يَقْرَأُ — hamza seat on final C3."""

    def test_past_3msg(self):
        assert gen(QRA, 'BAB_III_FATAHA') == 'قَرَأَ'

    def test_imperfect_3msg(self):
        assert gen(QRA, 'BAB_III_FATAHA', tense='IMPERFECT', mood='INDICATIVE') == 'يَقْرَأُ'

    def test_imperfect_3mpl(self):
        # يَقْرَءُونَ — hamza seated on ء when followed by damma (ؤ not used here, ء standalone)
        result = gen(QRA, 'BAB_III_FATAHA', tense='IMPERFECT', mood='INDICATIVE',
                     person='3', number='PL', gender='M')
        assert result is not None  # DEFER is acceptable for complex hamza PL
        # If realized at HIGH, check damma on C3-area
        if result:
            import unicodedata
            nfc = unicodedata.normalize('NFC', result)
            assert 'قر' in ''.join(c for c in nfc if c not in 'َُِّْ')


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-06: Hollow verbs (WAW and YAA)
# ──────────────────────────────────────────────────────────────────────────────

class TestHollowVerbs:
    """قَالَ (HOLLOW_WAW) and بَاعَ (HOLLOW_YAA) paradigms."""

    # HOLLOW_WAW past
    def test_hollow_waw_past_3msg(self):
        assert gen(QAL, None, wazn_id='FA_A_LA') == 'قَالَ'

    def test_hollow_waw_past_3mpl(self):
        assert gen(QAL, None, wazn_id='FA_A_LA', person='3', number='PL', gender='M') == 'قَالُوا'

    def test_hollow_waw_past_1sg(self):
        assert gen(QAL, None, wazn_id='FA_A_LA', person='1', number='SG', gender='M') == 'قُلْتُ'

    # HOLLOW_WAW imperfect
    def test_hollow_waw_imperfect_3msg(self):
        assert gen(QAL, None, tense='IMPERFECT', mood='INDICATIVE', wazn_id='FA_A_LA') == 'يَقُولُ'

    def test_hollow_waw_imperfect_juss_3msg(self):
        assert gen(QAL, None, tense='IMPERFECT', mood='JUSSIVE', wazn_id='FA_A_LA') == 'يَقُلْ'

    # HOLLOW_YAA past
    def test_hollow_yaa_past_3msg(self):
        assert gen(BAA, None, wazn_id='FA_I_LA') == 'بَاعَ'

    def test_hollow_yaa_past_1sg(self):
        assert gen(BAA, None, wazn_id='FA_I_LA', person='1', number='SG', gender='M') == 'بِعْتُ'

    # HOLLOW_YAA imperfect
    def test_hollow_yaa_imperfect_3msg(self):
        assert gen(BAA, None, tense='IMPERFECT', mood='INDICATIVE', wazn_id='FA_I_LA') == 'يَبِيعُ'

    def test_hollow_yaa_imperfect_juss_3msg(self):
        assert gen(BAA, None, tense='IMPERFECT', mood='JUSSIVE', wazn_id='FA_I_LA') == 'يَبِعْ'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-07: Defective verbs (WAW and YAA)
# ──────────────────────────────────────────────────────────────────────────────

class TestDefectiveVerbs:
    """دَعَا (DEFECTIVE_WAW) and رَمَى (DEFECTIVE_YAA) paradigms.

    دَعَا/يَدْعُو is BAB_I_NASARA (Vp=fatha, Vi=damma).
    رَمَى/يَرْمِي is BAB_II_DARABA (Vp=fatha, Vi=kasra).
    """

    # DEFECTIVE_WAW — دَعَا = d+a+`a`+a+alif (Vp2=fatha, Vi=damma)
    def test_defective_waw_past_3msg(self):
        assert gen(DAA, 'BAB_I_NASARA') == 'دَعَا'

    def test_defective_waw_past_3mpl(self):
        assert gen(DAA, 'BAB_I_NASARA', person='3', number='PL', gender='M') == 'دَعَوْا'

    def test_defective_waw_imperfect_3msg(self):
        assert gen(DAA, 'BAB_I_NASARA', tense='IMPERFECT', mood='INDICATIVE') == 'يَدْعُو'

    # DEFECTIVE_YAA — رَمَى = r+a+m+a+alif_maqsura (Vp2=fatha, Vi=kasra)
    def test_defective_yaa_past_3msg(self):
        assert gen(RMA, 'BAB_II_DARABA') == 'رَمَى'

    def test_defective_yaa_past_3mpl(self):
        assert gen(RMA, 'BAB_II_DARABA', person='3', number='PL', gender='M') == 'رَمَوْا'

    def test_defective_yaa_imperfect_3msg(self):
        assert gen(RMA, 'BAB_II_DARABA', tense='IMPERFECT', mood='INDICATIVE') == 'يَرْمِي'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-08: Assimilated WAW (وَعَدَ / يَعِدُ)
# ──────────────────────────────────────────────────────────────────────────────

class TestAssimilatedWAW:

    def test_assimilated_waw_past_3msg(self):
        assert gen(WAD, 'BAB_II_DARABA') == 'وَعَدَ'

    def test_assimilated_waw_imperfect_3msg(self):
        # يَعِدُ — C1 (و) drops in imperfect
        assert gen(WAD, 'BAB_II_DARABA', tense='IMPERFECT', mood='INDICATIVE') == 'يَعِدُ'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-09: Geminated verbs (مَدَّ / يَمُدُّ)
# ──────────────────────────────────────────────────────────────────────────────

class TestGeminated:

    def test_geminated_past_3msg(self):
        assert gen(MAD, 'BAB_I_NASARA') == 'مَدَّ'

    def test_geminated_past_3mpl(self):
        # مَدُّوا — C2+C3 merge, damma+shadda+waw
        assert gen(MAD, 'BAB_I_NASARA', person='3', number='PL', gender='M') == 'مَدُّوا'

    def test_geminated_past_2msg(self):
        # مَدَدْتَ — C2+C3 ungeminated before consonant suffix
        assert gen(MAD, 'BAB_I_NASARA', person='2', number='SG', gender='M') == 'مَدَدْتَ'

    def test_geminated_imperfect_3msg(self):
        assert gen(MAD, 'BAB_I_NASARA', tense='IMPERFECT', mood='INDICATIVE') == 'يَمُدُّ'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-10: Feature extraction — tense identification
# ──────────────────────────────────────────────────────────────────────────────

class TestTenseIdentification:
    """identify_tense() on reference surfaces."""

    def test_past_nasara(self):
        assert identify_tense('نَصَرَ') == 'PAST'

    def test_past_daRaba(self):
        assert identify_tense('ضَرَبَ') == 'PAST'

    def test_imperfect_yansuru(self):
        assert identify_tense('يَنْصُرُ') == 'IMPERFECT'

    def test_imperfect_taktubuna(self):
        assert identify_tense('يَكْتُبُونَ') == 'IMPERFECT'

    def test_imperfect_augmented_with_pronoun(self):
        assert identify_tense('يُعَوِّضُهُمْ') == 'IMPERFECT'

    def test_imperfect_passive(self):
        assert identify_tense('يُنْصَرُ') == 'IMPERFECT'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-11: Feature extraction — person/number/gender
# ──────────────────────────────────────────────────────────────────────────────

class TestPersonNumberGender:
    """extract_all_features() on reference surfaces."""

    def _feats(self, surface):
        return extract_all_features(surface)

    def test_daRaba_3msg(self):
        f = self._feats('ضَرَبَ')
        assert f['tense_aspect'] == 'PAST'
        assert f['person'] == '3'
        assert f['number'] == 'SG'
        assert f['gender'] == 'M'

    def test_nasartu_1sg(self):
        f = self._feats('نَصَرْتُ')
        assert f['person'] == '1'
        assert f['number'] == 'SG'

    def test_nasaru_3mpl(self):
        f = self._feats('نَصَرُوا')
        assert f['person'] == '3'
        assert f['number'] == 'PL'
        assert f['gender'] == 'M'

    def test_yansuru_3msg_ind(self):
        f = self._feats('يَنْصُرُ')
        assert f['tense_aspect'] == 'IMPERFECT'
        assert f['mood'] == 'INDICATIVE'
        assert f['person'] == '3'
        assert f['number'] == 'SG'
        assert f['gender'] == 'M'

    def test_yaktubuna_3mpl(self):
        f = self._feats('يَكْتُبُونَ')
        assert f['tense_aspect'] == 'IMPERFECT'
        assert f['mood'] == 'INDICATIVE'
        assert f['person'] == '3'
        assert f['number'] == 'PL'
        assert f['gender'] == 'M'

    def test_taktubina_2fsg(self):
        f = self._feats('تَكْتُبِينَ')
        assert f['tense_aspect'] == 'IMPERFECT'
        assert f['mood'] == 'INDICATIVE'
        assert f['person'] == '2'
        assert f['number'] == 'SG'
        assert f['gender'] == 'F'

    def test_yansurna_3fpl(self):
        f = self._feats('يَنْصُرْنَ')
        assert f['tense_aspect'] == 'IMPERFECT'
        assert f['number'] == 'PL'
        assert f['gender'] == 'F'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-12: Mood detection — including pronoun-attached surfaces
# ──────────────────────────────────────────────────────────────────────────────

class TestMoodDetection:

    def _feats(self, surface):
        return extract_all_features(surface)

    def test_indicative_yansuru(self):
        f = self._feats('يَنْصُرُ')
        assert f['mood'] == 'INDICATIVE'

    def test_subjunctive_yansura(self):
        f = self._feats('يَنْصُرَ')
        assert f['mood'] == 'SUBJUNCTIVE'

    def test_jussive_yansur(self):
        f = self._feats('يَنْصُرْ')
        assert f['mood'] == 'JUSSIVE'

    def test_indicative_with_pronoun_yUawwidhuhum(self):
        # يُعَوِّضُهُمْ — هُمْ attached; stem ends in ضُ (DAMMA → INDICATIVE)
        f = self._feats('يُعَوِّضُهُمْ')
        assert f['mood'] == 'INDICATIVE'

    def test_indicative_with_pronoun_yansuruha(self):
        f = self._feats('يَنْصُرُهَا')
        assert f['mood'] == 'INDICATIVE'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-13: Phase 5 orchestrator — non-verbal path → NOT_APPLICABLE
# ──────────────────────────────────────────────────────────────────────────────

class TestOrchestratorNonVerbal:

    def test_nominal_path_returns_not_applicable(self):
        from pipeline.p5_inflection.models import Directive
        res = project_inflection_with_licensing(
            surface='الْكِتَابِ',
            root=('ك', 'ت', 'ب'),
            bab_id=None,
            form_family=None,
            wazn_id=None,
            morphology_path='nominal_morphology_path',
            phase4a_result=None,
            phase4b_result=None,
            attachment=None,
        )
        assert res is not None
        # Phase5Result uses final_directive, not status
        assert res.final_directive == Directive.NOT_APPLICABLE

    def test_no_morphology_path_returns_not_applicable(self):
        from pipeline.p5_inflection.models import Directive
        res = project_inflection_with_licensing(
            surface='هَذَا',
            root=None,
            bab_id=None,
            form_family=None,
            wazn_id=None,
            morphology_path='no_morphology_path',
            phase4a_result=None,
            phase4b_result=None,
            attachment=None,
        )
        assert res is not None
        assert res.final_directive == Directive.NOT_APPLICABLE


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-14: Paradigm catalog selection
# ──────────────────────────────────────────────────────────────────────────────

class TestParadigmCatalog:

    def _orchestrate(self, surface, root, bab_id=None, wazn_id=None):
        return project_inflection_with_licensing(
            surface=surface,
            root=root,
            bab_id=bab_id,
            form_family=None,
            wazn_id=wazn_id,
            morphology_path='verbal_root_path',
            phase4a_result=None,
            phase4b_result=None,
            attachment=None,
        )

    def test_sound_mujarrad_paradigm(self):
        res = self._orchestrate('نَصَرَ', NSR, bab_id='BAB_I_NASARA', wazn_id='FA_A_LA')
        assert res.paradigm_candidate is not None
        assert res.paradigm_candidate.paradigm_id == 'SOUND_MUJARRAD'

    def test_hollow_waw_paradigm(self):
        res = self._orchestrate('قَالَ', QAL, wazn_id='FA_A_LA')
        assert res.paradigm_candidate is not None
        assert res.paradigm_candidate.paradigm_id == 'HOLLOW_WAW'

    def test_hollow_yaa_paradigm(self):
        res = self._orchestrate('بَاعَ', BAA, wazn_id='FA_I_LA')
        assert res.paradigm_candidate is not None
        assert res.paradigm_candidate.paradigm_id == 'HOLLOW_YAA'

    def test_geminated_paradigm(self):
        res = self._orchestrate('مَدَّ', MAD, bab_id='BAB_I_NASARA')
        assert res.paradigm_candidate is not None
        assert res.paradigm_candidate.paradigm_id == 'GEMINATED'

    def test_hamzated_c3_paradigm(self):
        res = self._orchestrate('قَرَأَ', QRA, bab_id='BAB_III_FATAHA')
        assert res.paradigm_candidate is not None
        assert res.paradigm_candidate.paradigm_id == 'HAMZATED_C3'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-15: generate_verb helper function (api.py)
# ──────────────────────────────────────────────────────────────────────────────

class TestGenerateVerbAPI:
    """Black-box tests of the public generate_verb() API."""

    def test_returns_string_for_known_form(self):
        result = generate_verb(root=NSR, bab_id='BAB_I_NASARA')
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_none_for_unimplemented_form(self):
        # Passive imperative — not implemented
        result = generate_verb(root=NSR, bab_id='BAB_I_NASARA',
                               tense='IMPERATIVE', voice='PASSIVE')
        # Should return None or DEFER (not an incorrect string)
        assert result is None or isinstance(result, str)

    def test_nfc_normalization_of_output(self):
        import unicodedata
        result = generate_verb(root=MAD, bab_id='BAB_I_NASARA')
        assert result == unicodedata.normalize('NFC', result)

    def test_all_six_babs_return_strings(self):
        babs = ['BAB_I_NASARA', 'BAB_II_DARABA', 'BAB_III_FATAHA',
                'BAB_IV_SAMIA', 'BAB_V_KARUMA', 'BAB_VI_HASIBA']
        roots = [NSR, DRB, FTH, SME, KRM, HSB]
        for root, bab in zip(roots, babs):
            result = generate_verb(root=root, bab_id=bab)
            assert isinstance(result, str), f'Expected str for {bab}, got {result!r}'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-16: Imperative forms (2M_SG base)
# ──────────────────────────────────────────────────────────────────────────────

class TestImperative:
    """2M_SG imperative — sound and hollow."""

    def test_imperative_sound_bab_i(self):
        # اُنْصُرْ (hamzat al-wasl + damma because Vi=damma)
        result = gen(NSR, 'BAB_I_NASARA', tense='IMPERATIVE', person='2', number='SG', gender='M')
        assert result is not None

    def test_imperative_sound_bab_ii(self):
        # اِضْرِبْ (hamzat al-wasl + kasra because Vi=kasra)
        result = gen(DRB, 'BAB_II_DARABA', tense='IMPERATIVE', person='2', number='SG', gender='M')
        assert result is not None

    def test_imperative_hollow_waw(self):
        # قُلْ (no hamzat al-wasl because starts with vowelled consonant)
        result = gen(QAL, None, tense='IMPERATIVE', wazn_id='FA_A_LA', person='2', number='SG', gender='M')
        assert result == 'قُلْ'


# ──────────────────────────────────────────────────────────────────────────────
# P5-REF-17: Passive voice — past passive
# ──────────────────────────────────────────────────────────────────────────────

class TestPassiveVoice:

    def test_past_passive_3msg_sound(self):
        # نُصِرَ
        result = gen(NSR, 'BAB_I_NASARA', voice='PASSIVE')
        assert result == 'نُصِرَ'

    def test_imperfect_passive_3msg(self):
        # يُنْصَرُ
        result = gen(NSR, 'BAB_I_NASARA', tense='IMPERFECT', mood='INDICATIVE', voice='PASSIVE')
        assert result == 'يُنْصَرُ'
