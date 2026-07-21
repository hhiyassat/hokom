"""
test_functional_catalog_corpus.py
HOKOM-MABNI-FUNCTIONAL-CATALOG-OWNERSHIP-01 — Commit 1/5

Corpus tests asserting correct OPERATOR/MABNI/AMBIGUITY routing contracts
for all mandatory functional and mabni tokens.

Design:
  - Each case asserts the TARGET correct behavior.
  - Cases marked with a "defect" field fail until production fixes land in
    commits 2–4.  No xfail markers are used — failing tests are expected and
    document the gap.
  - Negative controls assert that normal derivational words PASS THROUGH
    without being closed by the functional lookup.

Root-path closure criterion (matches canonical gate):
  root_candidate is None  AND  pre_root is None

Operator/mabni boundary routing is checked via functional_boundary_owner
(added in commit 4).  Prior to commit 4 the field is absent; the helper
_get_owner() falls back to the mabni verdict so tests still run.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

# Ensure repo root is on sys.path regardless of test invocation CWD
_REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from hokom_pipeline import hokom
from mabni_layer import MabniBoundary, MabniOpen, MabniBlocked

# ── Load fixture ──────────────────────────────────────────────────────────────

_FIXTURE = _REPO / 'tests' / 'fixtures' / 'functional_catalog_cases.json'

with _FIXTURE.open(encoding='utf-8') as _fh:
    _CASES = json.load(_fh)['cases']


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_owner(r: dict) -> str | None:
    """
    Extract effective boundary owner from a hokom() result dict.

    Priority:
      1. functional_boundary_owner (set in commit 4)
      2. mabni.verdict if MabniBoundary
      3. attachment.host_route (OPERATOR_BOUNDARY | MABNI_BOUNDARY) if MabniOpen+SEGMENTED
      4. attachment.host_route if MabniOpen+NOT_SEGMENTED+MABNI_BOUNDARY
      5. None
    """
    # Commit 4 field (primary)
    fbo = r.get('functional_boundary_owner')
    if fbo is not None:
        return fbo

    mabni = r.get('mabni')
    if isinstance(mabni, MabniBoundary):
        return mabni.verdict  # OPERATOR_BOUNDARY | MABNI_BOUNDARY | OPERATOR_DEFERRED

    if isinstance(mabni, MabniOpen):
        att = r.get('attachment')
        if att is not None:
            route = getattr(att, 'host_route', None)
            if route in ('OPERATOR_BOUNDARY', 'MABNI_BOUNDARY'):
                return route

    return None


def _root_closed(r: dict) -> bool:
    """Return True if both root_candidate and pre_root are None."""
    return r.get('root_candidate') is None and r.get('pre_root') is None


def _has_root(r: dict) -> bool:
    """Return True if root_candidate is not None (used for negative controls)."""
    return r.get('root_candidate') is not None


# ── Parametrise cases ─────────────────────────────────────────────────────────

def _case_id(case: dict) -> str:
    return f"{case['surface']}/{case['label']}"


_FUNCTIONAL_CASES = [c for c in _CASES if not c.get('negative_control')]
_NEGATIVE_CONTROLS = [c for c in _CASES if c.get('negative_control')]


# ── Tests: functional / mabni tokens ─────────────────────────────────────────

class TestFunctionalRootClosure:
    """
    Root path must be CLOSED for every functional/mabni token.

    criterion: root_candidate is None AND pre_root is None
    """

    @pytest.mark.parametrize('case', _FUNCTIONAL_CASES, ids=_case_id)
    def test_root_path_closed(self, case):
        r = hokom(case['surface'])
        assert _root_closed(r), (
            f"Token {case['surface']!r} ({case['label']}): root path was OPENED.\n"
            f"  pre_root={r.get('pre_root')!r}\n"
            f"  root_candidate={r.get('root_candidate')!r}\n"
            f"  defect={case.get('defect', 'none')}"
        )


class TestFunctionalOwnerRouting:
    """
    Each functional/mabni token must carry the expected boundary owner.

    Checked via functional_boundary_owner (commit 4) with fallback to
    mabni.verdict / attachment.host_route for earlier commits.
    """

    @pytest.mark.parametrize('case', _FUNCTIONAL_CASES, ids=_case_id)
    def test_expected_owner(self, case):
        expected = case.get('expected_owner')
        if expected is None:
            pytest.skip('no expected_owner defined for this case')
        r = hokom(case['surface'])
        owner = _get_owner(r)
        assert owner == expected, (
            f"Token {case['surface']!r} ({case['label']}): "
            f"expected owner={expected!r}, got owner={owner!r}\n"
            f"  mabni={r.get('mabni')!r}\n"
            f"  functional_boundary_owner={r.get('functional_boundary_owner')!r}"
        )


# ── Tests: collision awareness ────────────────────────────────────────────────

class TestCollisionAwareness:
    """
    Verify that pairs which bare-collide (من/مَنْ, إذا/إذًا, إن/إنَّ, أن/أنَّ)
    are distinguished by the vocalized lookup and that NO silent first-selection
    occurs: each vocalized form must get its own distinct owner assignment.
    """

    COLLISION_PAIRS = [
        ('مِنْ', 'OPERATOR_BOUNDARY', 'مَنْ', 'MABNI_BOUNDARY'),
        ('إِذَا', 'OPERATOR_BOUNDARY', 'إِذًا', 'OPERATOR_BOUNDARY'),
        ('إِنَّ', 'OPERATOR_BOUNDARY', 'إِنْ', 'OPERATOR_BOUNDARY'),
        ('أَنَّ', 'OPERATOR_BOUNDARY', 'أَنْ', 'OPERATOR_BOUNDARY'),
    ]

    @pytest.mark.parametrize('tok_a,exp_a,tok_b,exp_b', COLLISION_PAIRS,
                             ids=[f'{a}/{b}' for a, _, b, _ in COLLISION_PAIRS])
    def test_collision_pair_distinguished(self, tok_a, exp_a, tok_b, exp_b):
        ra = hokom(tok_a)
        rb = hokom(tok_b)
        owner_a = _get_owner(ra)
        owner_b = _get_owner(rb)
        # Both must be closed (no root opened due to ambiguity)
        assert _root_closed(ra), f"{tok_a!r}: root was opened"
        assert _root_closed(rb), f"{tok_b!r}: root was opened"
        # Expected owners
        assert owner_a == exp_a, f"{tok_a!r}: expected {exp_a!r}, got {owner_a!r}"
        assert owner_b == exp_b, f"{tok_b!r}: expected {exp_b!r}, got {owner_b!r}"


# ── Tests: negative controls ──────────────────────────────────────────────────

class TestNegativeControls:
    """
    Normal derivational words must NOT be closed by the functional lookup.
    الحق, الكتاب, كاتب, يكتب → root engine must be reached (root_candidate not None).
    """

    @pytest.mark.parametrize('case', _NEGATIVE_CONTROLS, ids=_case_id)
    def test_not_closed_by_functional_lookup(self, case):
        r = hokom(case['surface'])
        # Negative controls must not get OPERATOR_BOUNDARY or MABNI_BOUNDARY
        owner = _get_owner(r)
        assert owner not in ('OPERATOR_BOUNDARY', 'MABNI_BOUNDARY'), (
            f"Token {case['surface']!r} ({case['label']}): "
            f"should NOT be closed by functional/mabni lookup, got owner={owner!r}"
        )

    def test_yaktubu_has_root(self):
        """يَكْتُبُ must resolve to root ك ت ب."""
        r = hokom('يَكْتُبُ')
        rc = r.get('root_candidate')
        assert rc is not None, "يَكْتُبُ: root_candidate should not be None"
        assert rc.canonical_root == ('ك', 'ت', 'ب'), (
            f"يَكْتُبُ: expected root (ك,ت,ب), got {rc.canonical_root!r}"
        )

    def test_katib_has_root(self):
        """كَاتِبٌ must resolve to root ك ت ب."""
        r = hokom('كَاتِبٌ')
        rc = r.get('root_candidate')
        assert rc is not None, "كَاتِبٌ: root_candidate should not be None"
        assert rc.canonical_root == ('ك', 'ت', 'ب'), (
            f"كَاتِبٌ: expected root (ك,ت,ب), got {rc.canonical_root!r}"
        )


# ── Tests: whole-form protection ──────────────────────────────────────────────

class TestWholeFormProtection:
    """
    A catalog match on segment_host blocks root analysis entirely.
    The full token (with proclitics) must NOT be analysed as a root-eligible form
    when the host is a known functional word.
    """

    def test_bima_host_blocks_root(self):
        """بِمَا: segment_host='مَا' (operator) → root must not be opened."""
        r = hokom('بِمَا')
        assert _root_closed(r), (
            f"بِمَا: root path should be closed when host مَا is operator.\n"
            f"  pre_root={r.get('pre_root')!r}\n"
            f"  root_candidate={r.get('root_candidate')!r}"
        )

    def test_lima_blocks_root(self):
        """لِمَا: compound operator → root must not be opened."""
        r = hokom('لِمَا')
        assert _root_closed(r), (
            f"لِمَا: root path should be closed.\n"
            f"  pre_root={r.get('pre_root')!r}\n"
            f"  root_candidate={r.get('root_candidate')!r}"
        )

    def test_fa_in_blocks_root(self):
        """فَإِنْ: host=إِنْ is operator → root must not be opened."""
        r = hokom('فَإِنْ')
        assert _root_closed(r)

    def test_wa_la_blocks_root(self):
        """وَلَا: host=لَا is operator → root must not be opened."""
        r = hokom('وَلَا')
        assert _root_closed(r)


# ── Tests: Jamid Aalam non-regression ────────────────────────────────────────

class TestJamidAalamNonRegression:
    """الله 7-of-7 must remain JAMID_AALAM_BOUNDARY and root=None after this commit."""

    JALALA_FORMS = [
        'اللَّهُ', 'اللَّهَ', 'اللَّهِ',
        'وَاللَّهُ', 'فَاللَّهُ', 'بِاللَّهِ', 'لِلَّهِ',
    ]

    @pytest.mark.parametrize('tok', JALALA_FORMS)
    def test_jalala_jamid_aalam_boundary(self, tok):
        r = hokom(tok)
        assert r.get('jamid_verdict') == 'JAMID_AALAM_BOUNDARY', (
            f"{tok!r}: expected jamid_verdict='JAMID_AALAM_BOUNDARY', "
            f"got {r.get('jamid_verdict')!r}"
        )
        assert r.get('root_candidate') is None, (
            f"{tok!r}: root_candidate should be None after JAMID_AALAM_BOUNDARY"
        )
