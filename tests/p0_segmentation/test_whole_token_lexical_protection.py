#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_whole_token_lexical_protection.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Whole-token lexical protection tests.

أَيُّهَا and الَّذِي / الَّذِينَ must not have their endings extracted
as enclitics. Protection is enforced in Step 1 of engine.py (before enclitic
scan), via PROTECTED_WHOLE_TOKENS and the bare-form lookup _PROTECTED_BARE.

HOKOM-NORMALIZATION-SEGMENTATION-POST-CLOSURE-DEFECT-01
"""
import pytest
from pipeline.p0_segmentation.models import SegmentationRequest
from pipeline.p0_segmentation.engine import segment_token
from pipeline.p0_segmentation.normalization import strip_diacritics
from pipeline.p0_segmentation.inventory import PROTECTED_WHOLE_TOKENS


def seg(s: str):
    req = SegmentationRequest(request_id=f'x:{s}', original_surface=s, normalized_surface=s)
    return segment_token(req)


# ── Inventory presence ───────────────────────────────────────────────────────

@pytest.mark.parametrize('surface', ['أَيُّهَا', 'الَّذِي', 'الَّذِينَ'])
def test_in_protected_set(surface):
    """Each token must be present in PROTECTED_WHOLE_TOKENS."""
    bare = strip_diacritics(surface)
    in_exact = surface in PROTECTED_WHOLE_TOKENS
    in_bare  = any(strip_diacritics(p) == bare for p in PROTECTED_WHOLE_TOKENS)
    assert in_exact or in_bare, (
        f"{surface!r}: not found in PROTECTED_WHOLE_TOKENS "
        f"(bare={bare!r})"
    )


# ── No enclitic extraction ───────────────────────────────────────────────────

@pytest.mark.parametrize('surface', ['أَيُّهَا', 'الَّذِي', 'الَّذِينَ'])
def test_protected_token_no_enclitic(surface):
    """Protected whole tokens must not have any enclitic extracted."""
    b = seg(surface)
    assert b.enclitics == (), (
        f"{surface!r}: endings must NOT be enclitics (whole-token protection), "
        f"got enclitics={b.enclitics}"
    )


# ── No proclitic extraction ──────────────────────────────────────────────────

@pytest.mark.parametrize('surface', ['أَيُّهَا', 'الَّذِي', 'الَّذِينَ'])
def test_protected_token_no_proclitic(surface):
    """Protected whole tokens must not have any proclitic extracted."""
    b = seg(surface)
    assert b.proclitics == (), (
        f"{surface!r}: must NOT have proclitics, got {b.proclitics}"
    )


# ── Host is the whole token ──────────────────────────────────────────────────

def test_ayyuha_host_is_whole():
    """أَيُّهَا: host must be the whole token, هَا not stripped as enclitic."""
    b = seg('أَيُّهَا')
    assert b.enclitics == (), f"أَيُّهَا: هَا must not be enclitic"
    assert b.clitic_only is False
    host_bare = strip_diacritics(b.host or '')
    assert 'أيه' in host_bare or host_bare.startswith('ايه'), (
        f"أَيُّهَا: unexpected host bare {host_bare!r}"
    )


def test_alladhi_host_is_whole():
    """الَّذِي: host must be the whole token, يَ not stripped as enclitic."""
    b = seg('الَّذِي')
    assert b.enclitics == (), f"الَّذِي: يَ must not be enclitic"
    assert b.clitic_only is False
    host_bare = strip_diacritics(b.host or '')
    assert 'لذي' in host_bare, (
        f"الَّذِي: unexpected host bare {host_bare!r}"
    )


def test_alladhiina_host_is_whole():
    """الَّذِينَ: host is whole, نَ not extracted as part of inflectional ending."""
    b = seg('الَّذِينَ')
    assert b.enclitics == (), f"الَّذِينَ: enclitics must be empty"
    assert b.clitic_only is False
    assert b.host is not None, "الَّذِينَ: host must not be None"
