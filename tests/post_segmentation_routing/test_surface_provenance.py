"""
tests/post_segmentation_routing/test_surface_provenance.py
HOKOM-POST-SEGMENTATION-MORPHOLOGY-ROUTING-OWNERSHIP-01
"""
import sys
sys.path.insert(0, '.')

import unicodedata
import pytest
from hokom_pipeline import hokom


ARTICLE_TOKENS = ['الْحَقُّ', 'الشُّهَدَاءِ', 'الْأُخْرَى']


@pytest.mark.parametrize('token,expected_host_prefix', [
    ('عَلَّمَهُ', 'عَلْ'),
    ('رَبَّهُ',   'رَبْ'),
])
def test_root_host_from_morphology_not_original(token, expected_host_prefix):
    r = hokom(token)
    rc = r.get('root_candidate')
    if rc is None:
        pytest.skip(f'{token}: no root_candidate')

    seg_host = r.get('segment_host')
    input_surf = r.get('input_surface', token)
    root_dir = getattr(rc, 'directive', None)

    if root_dir != 'ACCEPT':
        pytest.skip(f'{token}: root not ACCEPT (directive={root_dir})')

    root_host = getattr(rc, 'host_surface', None)

    assert root_host != input_surf, (
        f'{token}: root_candidate.host_surface must not equal input_surface '
        f'when clitics were stripped; got root_host={root_host!r}, input={input_surf!r}'
    )
    assert root_host is not None and root_host.startswith(expected_host_prefix), (
        f'{token}: root_candidate.host_surface={root_host!r} must start with {expected_host_prefix!r}'
    )


def test_morphology_surface_excludes_enclitic():
    """عَلَّمَهُ: morphology_surface must not include هُ (derived from segment_host, not full token)."""
    tok = 'عَلَّمَهُ'
    r = hokom(tok)
    ms = r.get('morphology_surface')
    assert ms is not None, 'morphology_surface must not be None'
    assert 'هُ' not in ms, (
        f'morphology_surface={ms!r} must not contain هُ; '
        f'it should be derived from segment_host, not from full token'
    )


def _bare(s):
    if s is None:
        return None
    return ''.join(c for c in s if unicodedata.category(c) not in ('Mn', 'Cf'))


@pytest.mark.parametrize('token', ARTICLE_TOKENS)
def test_no_article_reattachment_in_root_host(token):
    r = hokom(token)
    rc = r.get('root_candidate')
    if rc is None:
        pytest.skip(f'{token}: no root_candidate')

    root_host = getattr(rc, 'host_surface', None)
    if root_host is None:
        pytest.skip(f'{token}: root_candidate.host_surface is None')

    bare = _bare(root_host) or ''
    assert not bare.startswith('ال'), (
        f'{token}: root_candidate.host_surface={root_host!r} starts with ال (article reattached); '
        f'segment_host={r.get("segment_host")!r}'
    )


def test_segment_host_without_article_for_definite_nouns():
    cases = {
        'الْحَقُّ':      'حق',
        'الشُّهَدَاءِ':  'شه',
        'لِلشَّهَادَةِ': 'شه',
    }
    for tok, expected_bare_prefix in cases.items():
        r = hokom(tok)
        seg_host = r.get('segment_host')
        assert seg_host is not None, f'{tok}: segment_host must not be None'
        bare = _bare(seg_host) or ''
        assert not bare.startswith('ال'), (
            f'{tok}: segment_host={seg_host!r} still starts with ال; P0 should strip article'
        )
        assert bare.startswith(expected_bare_prefix), (
            f'{tok}: expected segment_host bare to start with {expected_bare_prefix!r}, got {bare!r}'
        )
