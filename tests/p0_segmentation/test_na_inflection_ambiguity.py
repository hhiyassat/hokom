#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_na_inflection_ambiguity.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
نَا pronoun vs. inflectional ending (ألف التثنية) disambiguation tests.

When a token's bare form ends with 'ونا', the نَا is the dual subjunctive
inflectional alef (ألف التثنية), NOT the first-person plural attached pronoun.
The heuristic is surface-only: no root computation, no Word Class lookup.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
import pytest
from pipeline.p0_segmentation.models import SegmentationRequest
from pipeline.p0_segmentation.engine import segment_token
from pipeline.p0_segmentation.normalization import strip_diacritics


def _req(surface: str) -> SegmentationRequest:
    return SegmentationRequest(
        request_id=f'test:{surface}',
        original_surface=surface,
        normalized_surface=surface,
    )


@pytest.mark.parametrize('surface', [
    'يَكُونَا',    # dual subjunctive: bare يكونا ends with 'ونا' → inflectional
    'يَفْعَلُونَا', # if this pattern occurred → inflectional (bare ends with ونا)
])
def test_na_not_extracted_as_pronoun_from_ona_pattern(surface):
    """نَا must NOT be extracted as pronoun from tokens whose bare form ends in ...ونا."""
    bundle = segment_token(_req(surface))
    enc_bare = tuple(strip_diacritics(e) for e in bundle.enclitics)
    assert 'نا' not in enc_bare, (
        f'{surface}: نَا should NOT be extracted as pronoun (dual-verb pattern), '
        f'got enclitics={bundle.enclitics}'
    )
    assert bundle.host is not None, f'{surface}: host must not be None'


@pytest.mark.parametrize('surface,expect_na_enc', [
    ('رَبَّنَا',   True),    # رَبَّ + نَا (pronoun) — bare 'ربنا' does NOT end with 'ونا'
    ('عَلَّمَنَا', True),   # عَلَّمَ + نَا (pronoun) — bare 'علمنا' not 'ونا'
])
def test_na_extracted_as_pronoun_when_appropriate(surface, expect_na_enc):
    """نَا MUST be extracted as pronoun when the bare form does not end in ...ونا."""
    bundle = segment_token(_req(surface))
    enc_bare = tuple(strip_diacritics(e) for e in bundle.enclitics)
    has_na = 'نا' in enc_bare
    if expect_na_enc:
        assert has_na, (
            f'{surface}: نَا should be extracted as pronoun, got enclitics={bundle.enclitics}'
        )
    else:
        assert not has_na, (
            f'{surface}: نَا should NOT be extracted, got enclitics={bundle.enclitics}'
        )
