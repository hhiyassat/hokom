"""
tests/post_segmentation_routing/test_allah_variants.py
HOKOM-POST-SEGMENTATION-MORPHOLOGY-ROUTING-OWNERSHIP-01
"""
import sys
sys.path.insert(0, '.')

import pytest
from hokom_pipeline import hokom
from mabni_layer import MabniOpen


ALLAH_VARIANTS = ['اللَّهُ', 'اللَّهَ', 'اللَّهِ']


@pytest.mark.parametrize('token', ALLAH_VARIANTS)
def test_allah_is_mabni_open(token):
    r = hokom(token)
    mabni = r['mabni']
    mabni_type = type(mabni).__name__
    assert isinstance(mabni, MabniOpen), (
        f'{token}: expected MabniOpen, got {mabni_type}'
    )


@pytest.mark.parametrize('token', ALLAH_VARIANTS)
def test_allah_no_enclitics(token):
    r = hokom(token)
    enclitics = r.get('segment_enclitics', ())
    assert enclitics == (), (
        f'{token}: expected segment_enclitics=(), got {enclitics!r}'
    )


@pytest.mark.parametrize('token', ALLAH_VARIANTS)
def test_allah_segment_host_is_full_token(token):
    r = hokom(token)
    seg_host = r.get('segment_host')
    assert seg_host is not None, f'{token}: segment_host must not be None'
    assert seg_host == token, (
        f'{token}: segment_host={seg_host!r} must equal token'
    )


@pytest.mark.parametrize('token', ALLAH_VARIANTS)
def test_allah_morphology_not_blocked(token):
    r = hokom(token)
    assert r.get('morphology_blocked') is False, (
        f'{token}: morphology_blocked must be False'
    )


def test_allah_all_variants_not_operator_boundary():
    for tok in ALLAH_VARIANTS:
        r = hokom(tok)
        att = r.get('attachment')
        route = getattr(att, 'host_route', None) if att else None
        assert route != 'OPERATOR_BOUNDARY', (
            f'{tok}: route must not be OPERATOR_BOUNDARY; got {route!r}'
        )
        assert route != 'MABNI_BOUNDARY', (
            f'{tok}: route must not be MABNI_BOUNDARY; got {route!r}'
        )
