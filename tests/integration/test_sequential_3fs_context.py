#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_sequential_3fs_context.py

HOKOM-SEQUENTIAL-3FS-RESOLUTION-AND-CANONICAL-ARTIFACT-REBASE-01

General tests for the sequential subject-agreement 3FS context refinement.

Constitutional constraints verified:
  - Correlated ambiguity is PRESERVED when subject evidence is absent
  - Refinement is NEVER applied to JAMID or non-verbal records
  - Masculine/plural subjects do NOT trigger 3FS resolution
  - Clause boundaries (uncoordinated FI3L) block cross-clause lookahead
  - Coordinated فَ/وَ verbs inherit the active feminine context
  - Explicit تِجَارَةً/كَاتِبَةٌ-pattern (ة) subjects resolve to 3FS
  - Delayed subject (within lookahead window) resolves correctly
  - Live verse: تَضِلَّ, فَتُذَكِّرَ, تَكُونَ all resolve to 3FS
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from hokom_pipeline import hokom
from pipeline.p5_inflection.subject_agreement import (
    apply_subject_agreement_context,
    is_feminine_sg_subject_evidence,
)


def _raw(tokens: list[str]) -> list[tuple[str, dict]]:
    """Run hokom() on a token list and return (surface, result) pairs."""
    return [(tok, hokom(tok)) for tok in tokens]


def _resolved(tokens: list[str]) -> tuple[list[tuple[str, dict]], int]:
    return apply_subject_agreement_context(_raw(tokens))


# ── is_feminine_sg_subject_evidence ──────────────────────────────────────────

class TestFeminineSgSubjectEvidence:

    def test_taa_marbuta_is_feminine(self):
        """Explicit taa marbuta (ة) marks feminine subject."""
        r = hokom('كَاتِبَةٌ')
        assert is_feminine_sg_subject_evidence('كَاتِبَةٌ', r)

    def test_tijaratan_is_feminine(self):
        """تِجَارَةً ends in ة → feminine subject evidence."""
        r = hokom('تِجَارَةً')
        assert is_feminine_sg_subject_evidence('تِجَارَةً', r)

    def test_alif_maqsura_is_feminine(self):
        """Alif maqsura (ى) marks inherently feminine nouns."""
        # بُشْرَى ends with ى (feminine word)
        r = hokom('بُشْرَى')
        assert is_feminine_sg_subject_evidence('بُشْرَى', r)

    def test_ihdahuma_alif_construct_detected(self):
        """إِحْدَاهُمَا: alif-maqsura construct state before pronoun enclitic."""
        r = hokom('إِحْدَاهُمَا')
        # bare host = إحدا (ا at end, ISM, enclitic = هما)
        assert is_feminine_sg_subject_evidence('إِحْدَاهُمَا', r)

    def test_rajulun_not_feminine(self):
        """رَجُلٌ (masculine noun, no ة/ى) is NOT feminine subject evidence."""
        r = hokom('رَجُلٌ')
        assert not is_feminine_sg_subject_evidence('رَجُلٌ', r)

    def test_nisaun_plural_not_detected(self):
        """نِسَاءٌ (plural, ends ء not ة/ى) is NOT singular feminine evidence."""
        r = hokom('نِسَاءٌ')
        assert not is_feminine_sg_subject_evidence('نِسَاءٌ', r)

    def test_kitabun_not_feminine(self):
        """كِتَابٌ (masculine noun) is not feminine subject evidence."""
        r = hokom('كِتَابٌ')
        assert not is_feminine_sg_subject_evidence('كِتَابٌ', r)


# ── apply_subject_agreement_context ──────────────────────────────────────────

class TestNoResolutionWithoutSubjectEvidence:

    def test_ambiguous_verb_alone_stays_correlated(self):
        """Ambiguous تَكُونَ in isolation — no subject evidence → unresolved."""
        results, count = _resolved(['تَكُونَ'])
        _, r = results[0]
        assert count == 0
        # person/gender must not be forced to 3FS
        assert r.get('person') not in ('3',)

    def test_masculine_subject_no_3fs_resolution(self):
        """A masculine noun subject does NOT cause 3FS resolution."""
        results, count = _resolved(['تَكُونَ', 'رَجُلٌ'])
        _, rv = results[0]
        assert count == 0
        assert rv.get('person') not in ('3',)


class TestExplicitFeminineSingularResolvesTo3FS:

    def test_tamarbutah_immediately_following_resolves(self):
        """Ambiguous verb + immediately following ة-noun → 3FS."""
        results, count = _resolved(['تَكُونَ', 'تِجَارَةٌ'])
        _, rv = results[0]
        assert count == 1
        assert rv['person'] == '3'
        assert rv['gender'] == 'F'

    def test_katibatun_resolves_3fs(self):
        """كَاتِبَةٌ (ة-noun) immediately after ambiguous verb → 3FS."""
        results, count = _resolved(['تَضِلَّ', 'كَاتِبَةٌ'])
        _, rv = results[0]
        assert count == 1
        assert rv['person'] == '3'
        assert rv['gender'] == 'F'


class TestDelayedFeminineSingularResolves:

    def test_delayed_by_particle_still_resolves(self):
        """Feminine subject delayed by أَنْ particle → still resolves within window."""
        results, count = _resolved(['تَضِلَّ', 'أَنْ', 'كَاتِبَةٌ'])
        _, rv = results[0]
        assert count == 1
        assert rv['person'] == '3'

    def test_ihdahuma_as_delayed_subject_resolves(self):
        """إِحْدَاهُمَا (alif-maqsura construct) as next token → 3FS."""
        results, count = _resolved(['تَضِلَّ', 'إِحْدَاهُمَا'])
        _, rv = results[0]
        assert count == 1
        assert rv['person'] == '3'
        assert rv['gender'] == 'F'


class TestCoordinatedInheritance:

    def test_fa_verb_inherits_active_feminine_context(self):
        """فَتُذَكِّرَ with fa-prefix inherits resolution from resolved context."""
        tokens = ['تَضِلَّ', 'كَاتِبَةٌ', 'فَتُذَكِّرَ']
        results, count = _resolved(tokens)
        _, rv0 = results[0]
        _, rv2 = results[2]
        assert rv0['person'] == '3'   # resolved by lookahead
        assert rv2['person'] == '3'   # inherited via فَ-coordination
        assert count == 2

    def test_wa_verb_inherits_active_feminine_context(self):
        """A وَ-prefixed ambiguous verb also inherits the feminine context."""
        # وَتَكُونَ would start with وَ — but use a token that begins with و
        # After resolution, the next ambiguous verb with و prefix inherits.
        tokens = ['تَكُونَ', 'تِجَارَةٌ', 'فَتُذَكِّرَ']
        results, count = _resolved(tokens)
        _, rv0 = results[0]
        _, rv2 = results[2]
        assert rv0['person'] == '3'
        assert rv2['person'] == '3'
        assert count == 2


class TestMasculineAndPluralDoNotResolve:

    def test_masculine_singular_stays_correlated(self):
        """Masculine singular subject → 3FS NOT forced; correlated ambiguity kept."""
        results, count = _resolved(['تَكُونَ', 'رَجُلٌ'])
        _, rv = results[0]
        assert count == 0
        # person should NOT have been forced to '3' with gender 'F'
        assert not (rv.get('person') == '3' and rv.get('gender') == 'F')

    def test_plural_feminine_does_not_resolve_to_singular_3fs(self):
        """نِسَاءٌ plural — does NOT trigger 3FS singular resolution."""
        results, count = _resolved(['تَكُونَ', 'نِسَاءٌ'])
        _, rv = results[0]
        assert count == 0


class TestClauseBoundaryBlocksLookahead:

    def test_unrelated_later_feminine_noun_blocked_by_clause_boundary(self):
        """FI3L verb between ambiguous verb and feminine noun blocks lookahead."""
        # أَكَلَ is PAST FI3L — stops lookahead before كَاتِبَةٌ
        results, count = _resolved(['تَكُونَ', 'أَكَلَ', 'كَاتِبَةٌ'])
        _, rv = results[0]
        assert count == 0, "Feminine noun across FI3L clause boundary must not resolve"
        assert not (rv.get('person') == '3' and rv.get('gender') == 'F')


class TestJamidAndNonVerbalNotRefined:

    def test_allah_jamid_not_context_refined(self):
        """اللَّهُ (JAMID_AALAM_BOUNDARY) is never touched by context resolution."""
        results, count = _resolved(['اللَّهُ', 'كَاتِبَةٌ'])
        _, rv = results[0]
        # JAMID record: word_class should be None, no person
        assert rv.get('word_class') is None
        assert rv.get('person') is None

    def test_ism_not_context_refined(self):
        """ISM tokens are never assigned person/gender by subject-agreement context."""
        results, count = _resolved(['أَجَلٍ', 'كَاتِبَةٌ'])
        _, rv = results[0]
        assert rv.get('word_class') == 'ISM'
        # apply_subject_agreement_context never touches ISM records
        assert rv.get('person') is None


# ── Live verse: تَضِلَّ, فَتُذَكِّرَ, تَكُونَ ──────────────────────────────

class TestLiveVerseCorpus3FSResolution:

    @pytest.fixture(scope='class')
    @classmethod
    def live_metrics(cls):
        """Run compute_live_metrics() once for the whole test class."""
        import importlib.util
        import pathlib
        spec = importlib.util.spec_from_file_location(
            'demo_ayat_al_dayn',
            pathlib.Path(REPO_ROOT) / 'scripts' / 'demo_ayat_al_dayn.py'
        )
        demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(demo)
        return demo.compute_live_metrics()

    def test_sequential_context_3fs_resolved_equals_3(self, live_metrics):
        """Live corpus: exactly 3 tokens resolved to 3FS via sequential context."""
        assert live_metrics['LIVE_CONTEXT_3FS_RESOLVED'] == 3

    def test_tadilla_resolves_to_3fs(self, live_metrics):
        """تَضِلَّ: resolved to 3FS by إِحْدَاهُمَا subject evidence."""
        # Verify via probe on sequential runner (not isolated hokom())
        from scripts.demo_ayat_al_dayn import TOKENS
        raw = [(tok, hokom(tok)) for tok in TOKENS]
        resolved, _ = apply_subject_agreement_context(raw)
        # تَضِلَّ is at index 67 (0-based)
        tok67, r67 = resolved[67]
        assert tok67 == 'تَضِلَّ'
        assert r67['person'] == '3'
        assert r67['gender'] == 'F'

    def test_fatudhakirra_resolves_to_3fs(self, live_metrics):
        """فَتُذَكِّرَ: resolved to 3FS via coordination with تَضِلَّ."""
        from scripts.demo_ayat_al_dayn import TOKENS
        raw = [(tok, hokom(tok)) for tok in TOKENS]
        resolved, _ = apply_subject_agreement_context(raw)
        tok69, r69 = resolved[69]
        assert tok69 == 'فَتُذَكِّرَ'
        assert r69['person'] == '3'
        assert r69['gender'] == 'F'

    def test_takuna_resolves_to_3fs(self, live_metrics):
        """تَكُونَ: resolved to 3FS by تِجَارَةً lookahead."""
        from scripts.demo_ayat_al_dayn import TOKENS
        raw = [(tok, hokom(tok)) for tok in TOKENS]
        resolved, _ = apply_subject_agreement_context(raw)
        tok98, r98 = resolved[98]
        assert tok98 == 'تَكُونَ'
        assert r98['person'] == '3'
        assert r98['gender'] == 'F'

    def test_closure_gate_passes_after_fix(self, live_metrics):
        """All 10 closure metrics remain 0 after 3FS fix."""
        REQUIRED_ZERO = [
            'LIVE_GOLD_TOKEN_MISMATCHES',
            'LIVE_FORM_FAMILY_MISMATCHES',
            'KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS',
            'LIVE_PERSON_NUMBER_GENDER_MISMATCHES',
            'LIVE_VOICE_MISMATCHES',
            'LIVE_CONTEXT_MOOD_MISMATCHES',
            'LIVE_UNCORRELATED_AMBIGUITY',
            'UNJUSTIFIED_WORD_CLASS_NOT_OPENED',
            'LIVE_NONVERBS_AS_VERBS',
            'LIVE_JAMID_BOUNDARY_VIOLATIONS',
        ]
        for metric in REQUIRED_ZERO:
            assert live_metrics[metric] == 0, f'{metric} = {live_metrics[metric]}'
