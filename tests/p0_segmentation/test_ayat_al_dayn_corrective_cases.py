#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_ayat_al_dayn_corrective_cases.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Regression tests for the 4 critical segmentation failures found in the
Ayat al-Dayn audit (HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01 corrective pass).

Tests are generalised — they verify structural heuristics, not word identities.
The specific corpus tokens are included as named regression anchors.

Critical failures addressed:
  A: سَفِيهًا → سَ incorrectly extracted as future particle
  B: وَلِيُّهُ → وَ incorrectly extracted as conjunction
  C: يَكُونَا → نَا incorrectly extracted as attached pronoun
  D: لِلشَّهَادَةِ → لِل contraction not recognised

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
import pytest
from pipeline.p0_segmentation.models import SegmentationRequest, SegmentationVerdict
from pipeline.p0_segmentation.engine import segment_token
from pipeline.p0_segmentation.normalization import strip_diacritics


def _req(surface: str) -> SegmentationRequest:
    return SegmentationRequest(
        request_id=f'corrective:{surface}',
        original_surface=surface,
        normalized_surface=surface,
    )


# ── Failure A: سَفِيهًا ──────────────────────────────────────────────────────

def test_safiihan_not_split():
    """
    Regression A: سَفِيهًا must not split سَ as future particle.

    The guard: future particle سَ is only licensed before imperfect verbs.
    فِيهًا starts with فِ (fa'), which is NOT a mudaraa' prefix letter.
    Additionally, هًا carries fathatan (tanwin) — a case ending, not a pronoun.
    """
    bundle = segment_token(_req('سَفِيهًا'))
    # No proclitic extraction
    assert bundle.proclitics == (), (
        f'سَفِيهًا: got unexpected proclitics {bundle.proclitics}'
    )
    # No enclitic extraction (هًا is a tanwin case ending, not a pronoun)
    assert bundle.enclitics == (), (
        f'سَفِيهًا: got unexpected enclitics {bundle.enclitics}'
    )
    # Whole token is host
    host_bare = strip_diacritics(bundle.host or '')
    assert host_bare == strip_diacritics('سَفِيهًا'), (
        f'سَفِيهًا: host should be full token, got {bundle.host!r}'
    )
    # Verdict accepted
    assert bundle.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED


# ── Failure B: وَلِيُّهُ ─────────────────────────────────────────────────────

def test_waliyyuhu_enclitic_only():
    """
    Regression B: وَلِيُّهُ — only هُ is enclitic; وَ stays in the host.

    Guard: after stripping هُ from وَلِيُّهُ, the host would be وَلِيُّ (bare
    remainder لِيُّ has only 2 consonants: ل ي). The conjunction minimum is 3.
    Therefore وَ must NOT be extracted.
    """
    bundle = segment_token(_req('وَلِيُّهُ'))
    assert bundle.proclitics == (), (
        f'وَلِيُّهُ: وَ should not be proclitic, got {bundle.proclitics}'
    )
    enc_bare = tuple(strip_diacritics(e) for e in bundle.enclitics)
    assert 'ه' in enc_bare, (
        f'وَلِيُّهُ: هُ should be extracted as enclitic, got {bundle.enclitics}'
    )
    host_bare = strip_diacritics(bundle.host or '')
    assert host_bare.startswith('ولي'), (
        f'وَلِيُّهُ: host should start with ولي (وَلِيُّ), got {bundle.host!r}'
    )
    assert bundle.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED


# ── Failure C: يَكُونَا ──────────────────────────────────────────────────────

def test_yakuuna_inflectional_na():
    """
    Regression C: يَكُونَا — نَا is the dual alef (ألف التثنية), NOT a pronoun.

    Guard: bare form يكونا ends with 'ونا' → inflectional dual-verb pattern.
    The enclitic نَا must not be extracted.
    """
    bundle = segment_token(_req('يَكُونَا'))
    enc_bare = tuple(strip_diacritics(e) for e in bundle.enclitics)
    assert 'نا' not in enc_bare, (
        f'يَكُونَا: نَا should NOT be extracted as pronoun (dual alef), '
        f'got enclitics={bundle.enclitics}'
    )
    host_bare = strip_diacritics(bundle.host or '')
    # The whole token should be the host
    assert strip_diacritics('يَكُونَا') in host_bare or host_bare.startswith('يكون'), (
        f'يَكُونَا: host should be يَكُونَا (unsplit), got {bundle.host!r}'
    )
    assert bundle.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED


# ── Failure D: لِلشَّهَادَةِ ─────────────────────────────────────────────────

def test_lil_shahadati_contracted():
    """
    Regression D: لِلشَّهَادَةِ = لِ + (contracted الْ) + شَهَادَةِ.

    The definite article is contracted: لِ + الْ → لِلْ.
    starts_with_definite_article() misses this because there is no alef.
    Step 2.5 in the engine handles the bare-لل pattern directly.
    """
    bundle = segment_token(_req('لِلشَّهَادَةِ'))
    # Must have لِ as proclitic
    proc_bare = tuple(strip_diacritics(p) for p in bundle.proclitics)
    assert 'ل' in proc_bare, (
        f'لِلشَّهَادَةِ: expected لِ proclitic, got {bundle.proclitics}'
    )
    # Must have a definite article
    assert bundle.definite_article is not None, (
        'لِلشَّهَادَةِ: definite_article should not be None'
    )
    # Host should be شَهَادَةِ
    host_bare = strip_diacritics(bundle.host or '')
    assert 'شهاد' in host_bare, (
        f'لِلشَّهَادَةِ: expected host containing شهاد, got {bundle.host!r}'
    )
    # Article lam must not appear in host
    assert not host_bare.startswith('ل'), (
        f'لِلشَّهَادَةِ: article lam leaked into host: {bundle.host!r}'
    )
    assert bundle.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED


# ── Full Ayat al-Dayn: all 4 critical tokens pass ────────────────────────────

@pytest.mark.parametrize('surface,check', [
    ('سَفِيهًا',       'no_proclitic_no_enclitic'),
    ('وَلِيُّهُ',      'no_proclitic_has_enclitic_h'),
    ('يَكُونَا',       'no_enclitic_na'),
    ('لِلشَّهَادَةِ', 'has_proclitic_lam_and_article'),
])
def test_critical_four_combined(surface, check):
    """All 4 Ayat al-Dayn corrective cases in a single parametrised fixture."""
    bundle = segment_token(_req(surface))
    proc_bare = tuple(strip_diacritics(p) for p in bundle.proclitics)
    enc_bare  = tuple(strip_diacritics(e) for e in bundle.enclitics)

    if check == 'no_proclitic_no_enclitic':
        assert proc_bare == () and enc_bare == (), (
            f'{surface}: expected no proclitics and no enclitics, '
            f'got pro={bundle.proclitics}, enc={bundle.enclitics}'
        )
    elif check == 'no_proclitic_has_enclitic_h':
        assert proc_bare == () and 'ه' in enc_bare, (
            f'{surface}: expected no proclitic + هُ enclitic, '
            f'got pro={bundle.proclitics}, enc={bundle.enclitics}'
        )
    elif check == 'no_enclitic_na':
        assert 'نا' not in enc_bare, (
            f'{surface}: نَا should not be enclitic, got {bundle.enclitics}'
        )
    elif check == 'has_proclitic_lam_and_article':
        assert 'ل' in proc_bare and bundle.definite_article is not None, (
            f'{surface}: expected لِ proclitic + article, '
            f'got pro={bundle.proclitics}, art={bundle.definite_article}'
        )
