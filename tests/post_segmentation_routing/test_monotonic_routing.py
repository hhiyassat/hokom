"""
tests/post_segmentation_routing/test_monotonic_routing.py
HOKOM-POST-SEGMENTATION-MORPHOLOGY-ROUTING-OWNERSHIP-01

Invariant: once a boundary is established (OPERATOR_BOUNDARY, MABNI_BOUNDARY,
morphology_blocked), root analysis must NOT be opened (root_candidate must be
None or directive must not be ACCEPT).

All assertions go through hokom() — the canonical LEVEL_B entrypoint.

Architecture note (actual field names found in codebase):
  mabni: MabniBoundary | MabniOpen | MabniBlocked
  attachment.host_route: 'OPERATOR_BOUNDARY' | 'MABNI_BOUNDARY' | 'OPEN_TO_HR2S' | 'EMPTY'
  root_candidate: RootCandidate | None
  root_candidate.directive: 'ACCEPT' | 'DEFER' | 'BLOCK'
"""
import sys
sys.path.insert(0, '.')

import pytest
from hokom_pipeline import hokom
from mabni_layer import MabniBoundary, MabniOpen, MabniBlocked


def _root_candidate(r):
    return r.get('root_candidate')


def _root_dir(r):
    rc = _root_candidate(r)
    return getattr(rc, 'directive', None) if rc else None


def _attach_route(r):
    att = r.get('attachment')
    return getattr(att, 'host_route', None) if att else None


# ═══════════════════════════════════════════════════════════════════════════════
# 1. OPERATOR_BOUNDARY standalone (mabni=MabniBoundary) → root_candidate None
# ═══════════════════════════════════════════════════════════════════════════════
# These tokens are directly MabniBoundary — they never enter MabniOpen.

STANDALONE_OPERATOR_MABNI_BOUNDARY = [
    'إِذَا', 'أَوْ', 'لَا', 'إِلَّا', 'مَا', 'كَمَا',
    'أَيُّهَا',
]


@pytest.mark.parametrize('token', STANDALONE_OPERATOR_MABNI_BOUNDARY)
def test_standalone_mabni_boundary_root_not_opened(token):
    """Standalone MabniBoundary tokens must have root_candidate=None."""
    r = hokom(token)
    mabni = r['mabni']
    mabni_type = type(mabni).__name__
    assert isinstance(mabni, MabniBoundary), (
        f'{token}: expected MabniBoundary, got {mabni_type}'
    )
    assert _root_candidate(r) is None, (
        f'{token}: root_candidate must be None for standalone MabniBoundary; '
        f'got directive={_root_dir(r)}'
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 2. MABNI_BOUNDARY (via MabniOpen attach route OR direct MabniBoundary)
#    → root_candidate None
#
# Updated (commit 3): هُوَ, الَّذِي, الَّذِينَ are now caught directly by
# mabni_inventory via relative_pronouns_catalog.csv, returning MabniBoundary
# rather than going through MabniOpen → attachment path.  The contract
# (root_candidate is None, verdict is MABNI_BOUNDARY) is the same; only the
# mechanism changed.
# ═══════════════════════════════════════════════════════════════════════════════

MABNI_BOUNDARY_ATTACH_TOKENS = [
    'هُوَ', 'الَّذِي', 'الَّذِينَ',
]


@pytest.mark.parametrize('token', MABNI_BOUNDARY_ATTACH_TOKENS)
def test_mabni_boundary_attach_root_not_opened(token):
    """Mabni-boundary tokens must have verdict=MABNI_BOUNDARY and root_candidate=None.

    Accepts both the legacy MabniOpen+attachment path and the newer direct
    MabniBoundary path from mabni_inventory (commit 3).
    """
    from mabni_layer import MabniBoundary as _MB
    r = hokom(token)
    rc = _root_candidate(r)
    mabni = r.get('mabni')

    if isinstance(mabni, _MB):
        # New path: caught directly by mabni_inventory catalog
        assert mabni.verdict == 'MABNI_BOUNDARY', (
            f'{token}: MabniBoundary.verdict expected MABNI_BOUNDARY, got {mabni.verdict!r}'
        )
    else:
        # Legacy path: MabniOpen → segmenter → attachment.host_route
        att = r.get('attachment')
        route = getattr(att, 'host_route', None) if att else None
        assert route == 'MABNI_BOUNDARY', (
            f'{token}: expected MABNI_BOUNDARY attach route, got {route!r}'
        )
    assert rc is None, (
        f'{token}: root_candidate must be None for MABNI_BOUNDARY; '
        f'got directive={_root_dir(r)}'
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. OPERATOR_BOUNDARY composite (MabniOpen with attach_route=OPERATOR_BOUNDARY)
#    → root must NOT be ACCEPT
# ═══════════════════════════════════════════════════════════════════════════════
# These tokens have a proclitic (فَ, وَ, كَ, ...) that segments off, leaving
# an operator as the host. The host_route=OPERATOR_BOUNDARY prevents root opening.

COMPOSITE_OPERATOR_TOKENS = [
    'فَلَيْسَ',   # فَ + لَيْسَ (main regression: was ROOT ACCEPT before fix)
    'فَإِنْ',     # فَ + إِنْ
    'فَإِنَّهُ',  # فَ + إِنَّهُ
    'وَلَا',      # وَ + لَا
    'وَإِنْ',     # وَ + إِنْ
]


@pytest.mark.parametrize('token', COMPOSITE_OPERATOR_TOKENS)
def test_composite_operator_root_not_accepted(token):
    """Composite operator tokens must not open root (root_candidate=None or not ACCEPT)."""
    r = hokom(token)
    route = _attach_route(r)
    rc = _root_candidate(r)
    root_dir = _root_dir(r)

    if route == 'OPERATOR_BOUNDARY':
        assert root_dir != 'ACCEPT', (
            f'{token}: root must NOT be ACCEPT after OPERATOR_BOUNDARY composite; '
            f'got root_dir={root_dir!r}, '
            f'canonical_root={getattr(rc, "canonical_root", None)!r}'
        )


def test_fa_laysa_root_candidate_none():
    """فَلَيْسَ regression: root_candidate must be None (was ACCEPT ل-ي-س before fix)."""
    r = hokom('فَلَيْسَ')
    att = r.get('attachment')
    route = getattr(att, 'host_route', None) if att else None
    rc = _root_candidate(r)

    assert route == 'OPERATOR_BOUNDARY', f'Expected OPERATOR_BOUNDARY, got {route!r}'
    assert rc is None, (
        f'فَلَيْسَ: root_candidate must be None after fix; '
        f'got directive={_root_dir(r)!r}, root={getattr(rc, "canonical_root", None)!r}'
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Morphology blocked → root_candidate must be None
# ═══════════════════════════════════════════════════════════════════════════════

def test_bikum_morphology_blocked_root_none():
    """بِكُمْ regression: clitic-only → morphology_blocked=True → root_candidate=None."""
    r = hokom('بِكُمْ')
    assert r['morphology_blocked'] is True, 'بِكُمْ must have morphology_blocked=True'
    assert r.get('segment_host') is None, 'بِكُمْ must have segment_host=None'
    assert _root_candidate(r) is None, (
        f'بِكُمْ must have root_candidate=None; got {_root_candidate(r)!r}'
    )


def test_morphology_blocked_never_opens_root():
    """For any token with morphology_blocked=True, root_candidate must be None."""
    tokens = ['بِكُمْ', 'بِنَا', 'عَلَيْهِ', 'مِنْهُ', 'لَهُ', 'بِهِ']
    for tok in tokens:
        r = hokom(tok)
        if r.get('morphology_blocked'):
            assert _root_candidate(r) is None, (
                f'{tok}: morphology_blocked=True but root_candidate is not None; '
                f'directive={_root_dir(r)}'
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Root host must NOT equal input_surface when clitics stripped (provenance)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize('token', ['عَلَّمَهُ', 'رَبَّهُ', 'وَلِيُّهُ'])
def test_root_host_not_original_when_clitics_stripped(token):
    r = hokom(token)
    rc = _root_candidate(r)
    seg_host = r.get('segment_host')
    input_surf = r.get('input_surface', token)

    if rc is None:
        # Route is closed — assert closed-route invariants instead of skipping
        route_v = r.get('_route_v')
        mabni_v = r.get('mabni_verdict')
        pre_root = r.get('pre_root')
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

    if seg_host is not None and seg_host != input_surf:
        root_host = getattr(rc, 'host_surface', None)
        root_dir = getattr(rc, 'directive', None)
        if root_dir == 'ACCEPT':
            assert root_host != input_surf, (
                f'{token}: root_candidate.host_surface={root_host!r} equals '
                f'input_surface={input_surf!r}; root must not come from original surface'
            )
