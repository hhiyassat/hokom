"""
test_proclitic_aalam.py
HOKOM-JAMID-AALAM-LEXICAL-BOUNDARY-CLOSURE-01

Tests for proclitic-attached forms of اسم الجلالة.

Mandatory cases:
  وَاللَّهُ  → proclitic=(وَ,)  segment_host=اللَّهُ  JAMID_AALAM_BOUNDARY
  فَاللَّهُ  → proclitic=(فَ,)  segment_host=اللَّهُ  JAMID_AALAM_BOUNDARY
  بِاللَّهِ  → proclitic=(بِ,)  segment_host=اللَّهِ  JAMID_AALAM_BOUNDARY
  لِلَّهِ   → proclitic=(لِ,)  segment_host=لَّهِ    JAMID_AALAM_BOUNDARY

Critical negative invariant: proclitic consonants (و ف ب ل) must NOT appear
in any root candidate — the JAMID_AALAM_BOUNDARY must close root before any
root engine runs.
"""
import pytest
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from hokom_pipeline import hokom

# (token, proclitic_bare_consonant, expected_segment_host_bare)
PROCLITIC_CASES = [
    ('وَاللَّهُ', 'و', 'الله'),
    ('فَاللَّهُ', 'ف', 'الله'),
    ('بِاللَّهِ', 'ب', 'لله'),   # bare of اللَّهِ = الله but proclitic ب strips
    ('لِلَّهِ',  'ل', 'له'),     # segment_host='لَّهِ', bare='له'
]

# Roots that must NOT appear — proclitic consonant + ل + ل
FORBIDDEN_ROOTS = [
    ('و', 'ل', 'ل'),
    ('ف', 'ل', 'ل'),
    ('ب', 'ل', 'ل'),
    ('ل', 'ل', 'ه'),
    ('ل', 'ل', 'ل'),
]


class TestProcliticAllahJamidBoundary:
    """All proclitic-attached الله forms must trigger JAMID_AALAM_BOUNDARY."""

    @pytest.mark.parametrize('tok,proclitic_bare,_', PROCLITIC_CASES)
    def test_jamid_verdict(self, tok, proclitic_bare, _):
        r = hokom(tok)
        assert r.get('jamid_verdict') == 'JAMID_AALAM_BOUNDARY', (
            f"{tok}: jamid_verdict must be JAMID_AALAM_BOUNDARY"
        )

    @pytest.mark.parametrize('tok,proclitic_bare,_', PROCLITIC_CASES)
    def test_root_candidate_is_none(self, tok, proclitic_bare, _):
        r = hokom(tok)
        assert r.get('root_candidate') is None, (
            f"{tok}: root_candidate must be None after JAMID_AALAM_BOUNDARY"
        )

    @pytest.mark.parametrize('tok,proclitic_bare,_', PROCLITIC_CASES)
    def test_pre_root_is_none(self, tok, proclitic_bare, _):
        r = hokom(tok)
        assert r.get('pre_root') is None, f"{tok}: pre_root must be None"

    @pytest.mark.parametrize('tok,proclitic_bare,_', PROCLITIC_CASES)
    def test_aalam_category_divine_name(self, tok, proclitic_bare, _):
        r = hokom(tok)
        assert r.get('aalam_category') == 'divine_name', (
            f"{tok}: aalam_category must be divine_name"
        )

    @pytest.mark.parametrize('tok,proclitic_bare,_', PROCLITIC_CASES)
    def test_segment_host_not_original(self, tok, proclitic_bare, _):
        """Lookup must run on segment_host, not original_surface."""
        r = hokom(tok)
        seg_host = r.get('segment_host')
        assert seg_host is not None, f"{tok}: segment_host must exist"
        assert seg_host != tok, (
            f"{tok}: segment_host must differ from original (proclitic stripped)"
        )


class TestProcliticAllahCorrectProclitic:
    """Proclitic consonants must be correctly segmented."""

    def test_waw_allah_proclitic(self):
        r = hokom('وَاللَّهُ')
        proclitics = r.get('segment_proclitics', ())
        # At least one proclitic, and it should contain waw consonant
        assert len(proclitics) >= 1, "وَاللَّهُ must have at least one proclitic"
        bare_proclitic = ''.join(
            c for p in proclitics for c in p
            if '؀' <= c <= 'ۿ' and c not in 'ًٌٍَُِّْٰ'
        )
        assert 'و' in bare_proclitic, f"Expected و in proclitics, got {proclitics!r}"

    def test_fa_allah_proclitic(self):
        r = hokom('فَاللَّهُ')
        proclitics = r.get('segment_proclitics', ())
        assert len(proclitics) >= 1
        bare = ''.join(c for p in proclitics for c in p if '؀' <= c <= 'ۿ' and c not in 'ًٌٍَُِّْٰ')
        assert 'ف' in bare, f"Expected ف in proclitics, got {proclitics!r}"

    def test_ba_allah_proclitic(self):
        r = hokom('بِاللَّهِ')
        proclitics = r.get('segment_proclitics', ())
        assert len(proclitics) >= 1
        bare = ''.join(c for p in proclitics for c in p if '؀' <= c <= 'ۿ' and c not in 'ًٌٍَُِّْٰ')
        assert 'ب' in bare, f"Expected ب in proclitics, got {proclitics!r}"

    def test_lam_allah_proclitic(self):
        r = hokom('لِلَّهِ')
        proclitics = r.get('segment_proclitics', ())
        assert len(proclitics) >= 1
        bare = ''.join(c for p in proclitics for c in p if '؀' <= c <= 'ۿ' and c not in 'ًٌٍَُِّْٰ')
        assert 'ل' in bare, f"Expected ل in proclitics, got {proclitics!r}"


class TestNoProcliticInRoot:
    """
    Proclitic consonants must NEVER appear in root_candidate.
    The JAMID_AALAM_BOUNDARY must prevent root engine from running at all.
    """

    @pytest.mark.parametrize('tok', [
        'وَاللَّهُ', 'فَاللَّهُ', 'بِاللَّهِ', 'لِلَّهِ'
    ])
    def test_no_forbidden_root(self, tok):
        r = hokom(tok)
        rc = r.get('root_candidate')
        # root_candidate should be None entirely
        if rc is None:
            return  # Pass — no root at all
        root = getattr(rc, 'canonical_root', None)
        if root is None:
            return  # Pass — no root
        root_tuple = tuple(root)
        for forbidden in FORBIDDEN_ROOTS:
            assert root_tuple != forbidden, (
                f"{tok}: root {root_tuple!r} is a forbidden proclitic-contaminated root. "
                f"JAMID_AALAM_BOUNDARY must close root before proclitic consonants enter root engine."
            )

    @pytest.mark.parametrize('tok', [
        'وَاللَّهُ', 'فَاللَّهُ', 'بِاللَّهِ', 'لِلَّهِ'
    ])
    def test_root_candidate_is_none(self, tok):
        """Preferred outcome: root_candidate must be None, not just non-forbidden."""
        r = hokom(tok)
        rc = r.get('root_candidate')
        assert rc is None, (
            f"{tok}: root_candidate must be None. "
            f"Got canonical_root={getattr(rc, 'canonical_root', None)!r}"
        )


class TestLillaahSpecialCase:
    """
    لِلَّهِ is the most complex case: لِ proclitic causes لام + ال to merge.
    segment_host becomes لَّهِ (not اللَّهِ).
    The jamid lookup must still identify this as divine_name.
    """

    def test_lillah_segment_host(self):
        r = hokom('لِلَّهِ')
        seg_host = r.get('segment_host')
        # Host should be 'لَّهِ' — with shadda on the lam
        assert seg_host is not None
        assert 'ّ' in seg_host, f"لَّهِ must contain shadda, got {seg_host!r}"

    def test_lillah_jamid_boundary(self):
        r = hokom('لِلَّهِ')
        assert r.get('jamid_verdict') == 'JAMID_AALAM_BOUNDARY'

    def test_lillah_lexical_identity(self):
        r = hokom('لِلَّهِ')
        jb = r.get('jamid_boundary')
        assert getattr(jb, 'lexical_identity', None) == 'الله'

    def test_lillah_aalam_category(self):
        r = hokom('لِلَّهِ')
        assert r.get('aalam_category') == 'divine_name'

    def test_lillah_root_is_none(self):
        r = hokom('لِلَّهِ')
        assert r.get('root_candidate') is None
