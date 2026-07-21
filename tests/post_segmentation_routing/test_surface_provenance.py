"""
tests/post_segmentation_routing/test_surface_provenance.py
HOKOM-POST-SEGMENTATION-MORPHOLOGY-ROUTING-OWNERSHIP-01
"""
import sys
sys.path.insert(0, '.')

import unicodedata
import pytest
from hokom_pipeline import hokom


ARTICLE_TOKENS = ['الْحَقُّ', 'الشُّهَدَاءِ']


@pytest.mark.parametrize('token,expected_host_prefix', [
    ('عَلَّمَهُ', 'عَلْ'),
    ('رَبَّهُ',   'رَبْ'),
])
def test_root_host_from_morphology_not_original(token, expected_host_prefix):
    r = hokom(token)
    rc = r.get('root_candidate')
    if rc is None:
        # Route is closed — assert closed-route invariants instead of skipping
        route_v = r.get('_route_v')
        mabni_v = r.get('mabni_verdict')
        pre_root = r.get('pre_root')
        seg_host = r.get('segment_host')
        input_surf = r.get('input_surface', token)
        seg_enclitics = r.get('segment_enclitics', ())
        assert route_v is not None or mabni_v is not None, (
            f'{token}: closed route must have _route_v or mabni_verdict set; '
            f'got _route_v={route_v!r}, mabni_verdict={mabni_v!r}'
        )
        assert pre_root is None, (
            f'{token}: pre_root must be None when route is closed; got {pre_root!r}'
        )
        assert seg_host is not None and seg_host != input_surf, (
            f'{token}: segment_host must differ from input_surface when clitics stripped; '
            f'seg_host={seg_host!r}, input_surf={input_surf!r}'
        )
        assert 'هُ' in seg_enclitics, (
            f'{token}: attached pronoun هُ must appear in segment_enclitics, not as radical; '
            f'got {seg_enclitics!r}'
        )
        return

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


def test_ukhraa_no_root_candidate():
    """الْأُخْرَى: article stripped, root_candidate is None — correct for this token."""
    r = hokom('الْأُخْرَى')
    # Segmentation: article stripped, host preserved
    seg_host = r.get('segment_host')
    assert seg_host is not None, "segment_host must not be None"
    # The host must not contain the article prefix
    bare_host = _bare(seg_host) or ''
    assert not bare_host.startswith('ال'), (
        f'segment_host={seg_host!r} still starts with ال; article must be stripped'
    )
    # Morphology not blocked
    assert r.get('morphology_blocked', False) is False, (
        f'morphology_blocked must be False, got {r.get("morphology_blocked")!r}'
    )
    # Root candidate is None — this is the correct, expected result for this token
    rc = r.get('root_candidate')
    assert rc is None, f'expected no root_candidate for الْأُخْرَى, got {rc!r}'
    # Input surface preserved
    orig = r.get('input_surface') or r.get('original_surface')
    assert orig == 'الْأُخْرَى', f'surface mutated: {orig!r}'


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
