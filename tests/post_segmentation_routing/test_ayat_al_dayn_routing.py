"""
tests/post_segmentation_routing/test_ayat_al_dayn_routing.py
HOKOM-POST-SEGMENTATION-MORPHOLOGY-ROUTING-OWNERSHIP-01

Real-corpus regression: run all 129 tokens of Ayat al-Dayn (Q2:282) through
hokom() and assert zero routing violations.

Invariants checked:
  1. POST_SEGMENTATION_ROUTING_VIOLATIONS = 0
  2. ROOT_AFTER_CLOSED_BOUNDARY = 0
  3. SURFACE_PROVENANCE_VIOLATIONS = 0
  4. ARTICLE_REATTACHMENT_VIOLATIONS = 0
  5. UNHANDLED_EXCEPTIONS = 0
"""
import sys
sys.path.insert(0, '.')

import unicodedata
import pytest
from hokom_pipeline import hokom
from mabni_layer import MabniBoundary, MabniOpen, MabniBlocked


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

TOKENS = AYAT_AL_DAYN.split()
assert len(TOKENS) == 129, f'Expected 129 tokens, got {len(TOKENS)}'


def _bare(s):
    if s is None:
        return None
    return ''.join(c for c in s if unicodedata.category(c) not in ('Mn', 'Cf'))


def _collect_violations():
    """Run all tokens and collect violations. Returns (results, violations)."""
    violations = []
    results = []

    for tok in TOKENS:
        try:
            r = hokom(tok)
            mabni = r.get('mabni')
            att = r.get('attachment')
            rc = r.get('root_candidate')
            morph_blocked = r.get('morphology_blocked', False)
            seg_host = r.get('segment_host')
            input_surf = r.get('input_surface', tok)
            ms = r.get('morphology_surface')

            attach_route = getattr(att, 'host_route', None) if att else None
            root_dir = getattr(rc, 'directive', None) if rc else None
            root_canon = getattr(rc, 'canonical_root', None) if rc else None
            root_host_surf = getattr(rc, 'host_surface', None) if rc else None

            # 1. ROOT_AFTER_CLOSED_BOUNDARY: OPERATOR_BOUNDARY standalone
            if isinstance(mabni, MabniBoundary) and rc is not None:
                violations.append({
                    'token': tok,
                    'type': 'ROOT_AFTER_OPERATOR_BOUNDARY_STANDALONE',
                    'root_dir': root_dir,
                })

            # 2. ROOT_AFTER_CLOSED_BOUNDARY: MABNI_BOUNDARY attach route
            if isinstance(mabni, MabniOpen) and attach_route == 'MABNI_BOUNDARY' and rc is not None:
                violations.append({
                    'token': tok,
                    'type': 'ROOT_AFTER_MABNI_BOUNDARY',
                    'root_dir': root_dir,
                    'attach_route': attach_route,
                })

            # 3. ROOT_AFTER_CLOSED_BOUNDARY: OPERATOR_BOUNDARY composite + root ACCEPT
            if isinstance(mabni, MabniOpen) and attach_route == 'OPERATOR_BOUNDARY' and root_dir == 'ACCEPT':
                violations.append({
                    'token': tok,
                    'type': 'ROOT_ACCEPT_AFTER_OP_BOUNDARY_COMPOSITE',
                    'root_dir': root_dir,
                    'root_canon': root_canon,
                })

            # 4. ROOT_AFTER_MORPHOLOGY_BLOCKED
            if morph_blocked and rc is not None:
                violations.append({
                    'token': tok,
                    'type': 'ROOT_AFTER_MORPHOLOGY_BLOCKED',
                    'root_dir': root_dir,
                })

            # 5. SURFACE_PROVENANCE: when root ACCEPT and clitics stripped,
            #    root host must not equal input_surface
            if root_dir == 'ACCEPT' and root_canon is not None:
                if seg_host is not None and seg_host != input_surf:
                    if root_host_surf == input_surf:
                        violations.append({
                            'token': tok,
                            'type': 'SURFACE_PROVENANCE_ROOT_FROM_ORIGINAL',
                            'root_host': root_host_surf,
                            'seg_host': seg_host,
                        })

            # 6. ARTICLE_REATTACHMENT: root host must not start with ال
            if root_host_surf:
                bare_root_host = _bare(root_host_surf)
                if bare_root_host and bare_root_host.startswith('ال'):
                    violations.append({
                        'token': tok,
                        'type': 'ARTICLE_REATTACHMENT',
                        'root_host': root_host_surf,
                        'seg_host': seg_host,
                    })

            results.append({
                'token': tok,
                'mabni_type': type(mabni).__name__,
                'attach_route': attach_route,
                'root_dir': root_dir,
            })

        except Exception as e:
            violations.append({'token': tok, 'type': 'UNHANDLED_EXCEPTION', 'error': str(e)})

    return results, violations


# ── Cache to avoid running hokom 129×6 times ──────────────────────────────────
_cached = None


def _get_violations():
    global _cached
    if _cached is None:
        _cached = _collect_violations()
    return _cached


def test_token_count():
    assert len(TOKENS) == 129


def test_no_unhandled_exceptions():
    _, violations = _get_violations()
    exc_viols = [v for v in violations if v['type'] == 'UNHANDLED_EXCEPTION']
    assert exc_viols == [], f'Unhandled exceptions: {exc_viols}'


def test_zero_root_after_closed_boundary():
    """Tokens with closed boundary (OPERATOR, MABNI, blocked) must not open root."""
    _, violations = _get_violations()
    boundary_viols = [
        v for v in violations
        if v['type'] in ('ROOT_AFTER_OPERATOR_BOUNDARY_STANDALONE',
                         'ROOT_AFTER_MABNI_BOUNDARY',
                         'ROOT_ACCEPT_AFTER_OP_BOUNDARY_COMPOSITE',
                         'ROOT_AFTER_MORPHOLOGY_BLOCKED')
    ]
    assert boundary_viols == [], (
        f'Root opened after closed boundary in {len(boundary_viols)} token(s):\n'
        + '\n'.join(f'  {v}' for v in boundary_viols)
    )


def test_zero_surface_provenance_violations():
    """Root host must not equal input_surface when clitics were stripped."""
    _, violations = _get_violations()
    prov_viols = [v for v in violations if v['type'] == 'SURFACE_PROVENANCE_ROOT_FROM_ORIGINAL']
    assert prov_viols == [], (
        f'Surface provenance violations: {prov_viols}'
    )


def test_zero_article_reattachment_violations():
    """Root candidate host must never start with definite article ال."""
    _, violations = _get_violations()
    art_viols = [v for v in violations if v['type'] == 'ARTICLE_REATTACHMENT']
    assert art_viols == [], (
        f'Article reattachment in {len(art_viols)} token(s): {art_viols}'
    )


def test_total_violations_zero():
    """Master assertion: zero routing violations across all 129 tokens."""
    _, violations = _get_violations()
    assert violations == [], (
        f'{len(violations)} routing violation(s) found:\n'
        + '\n'.join(f'  {v}' for v in violations)
    )


# ── Spot-check specific tokens ─────────────────────────────────────────────────

def test_fa_laysa_root_not_accepted():
    """فَلَيْسَ regression: لَيْسَ is OPERATOR after stripping فَ, root must not be ACCEPT."""
    r = hokom('فَلَيْسَ')
    rc = r.get('root_candidate')
    att = r.get('attachment')
    route = getattr(att, 'host_route', None) if att else None
    assert route == 'OPERATOR_BOUNDARY', f'Expected OPERATOR_BOUNDARY, got {route!r}'
    assert rc is None or getattr(rc, 'directive', None) != 'ACCEPT', (
        f'فَلَيْسَ: root must not be ACCEPT; got {getattr(rc, "directive", None)!r}'
    )


def test_bikum_root_candidate_none():
    """بِكُمْ regression: clitic-only token must have root_candidate=None."""
    r = hokom('بِكُمْ')
    assert r['morphology_blocked'] is True
    assert r.get('root_candidate') is None, (
        f'بِكُمْ must have root_candidate=None; got {r.get("root_candidate")!r}'
    )


def test_allah_three_variants_no_enclitics():
    for tok in ['اللَّهُ', 'اللَّهَ', 'اللَّهِ']:
        r = hokom(tok)
        assert r.get('segment_enclitics') == (), f'{tok}: expected no enclitics'


def test_hoo_root_not_opened():
    """هُوَ (mabni pronoun) must not open root analysis."""
    r = hokom('هُوَ')
    att = r.get('attachment')
    rc = r.get('root_candidate')
    route = getattr(att, 'host_route', None) if att else None
    assert route == 'MABNI_BOUNDARY', f'هُوَ: expected MABNI_BOUNDARY, got {route!r}'
    assert rc is None, f'هُوَ: root_candidate must be None; got {rc!r}'


def test_alladhi_root_not_opened():
    """الَّذِي (relative pronoun) must not open root analysis."""
    r = hokom('الَّذِي')
    att = r.get('attachment')
    rc = r.get('root_candidate')
    route = getattr(att, 'host_route', None) if att else None
    assert route == 'MABNI_BOUNDARY', f'الَّذِي: expected MABNI_BOUNDARY, got {route!r}'
    assert rc is None, f'الَّذِي: root_candidate must be None; got {rc!r}'


def test_allama_root_from_segment_host():
    """عَلَّمَهُ: root must be derived from segment_host (عَلَّمَ), not full token."""
    r = hokom('عَلَّمَهُ')
    rc = r.get('root_candidate')
    seg_host = r.get('segment_host')

    assert seg_host is not None, 'عَلَّمَهُ: segment_host must not be None'
    assert 'هُ' not in (seg_host or ''), f'عَلَّمَهُ: segment_host must not contain هُ; got {seg_host!r}'

    if rc is not None and getattr(rc, 'directive', None) == 'ACCEPT':
        root_host = getattr(rc, 'host_surface', None)
        assert root_host != 'عَلَّمَهُ', (
            f'عَلَّمَهُ: root host must not be full token; got {root_host!r}'
        )
