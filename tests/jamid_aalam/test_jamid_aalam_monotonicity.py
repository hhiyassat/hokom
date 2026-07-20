"""
test_jamid_aalam_monotonicity.py
HOKOM-JAMID-AALAM-LEXICAL-BOUNDARY-CLOSURE-01

Monotonicity invariant:
  JAMID_AALAM_BOUNDARY ⟹ pre_root is None ⟹ root_candidate is None

If the jamid boundary fires, no downstream stage (pre_root, root engine,
wazn, bab, masdar, mushtaqat, inflection) must be opened.
This is a structural invariant that must hold for ALL inputs.
"""
import pytest
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from hokom_pipeline import hokom

ALL_ALLAH_FORMS = [
    'اللَّهُ', 'اللَّهَ', 'اللَّهِ',
    'وَاللَّهُ', 'فَاللَّهُ', 'بِاللَّهِ', 'لِلَّهِ',
]


class TestJamidAalamMonotonicity:
    """
    Monotonicity: JAMID_AALAM_BOUNDARY closes all downstream stages.
    """

    @pytest.mark.parametrize('tok', ALL_ALLAH_FORMS)
    def test_jamid_boundary_implies_pre_root_none(self, tok):
        r = hokom(tok)
        if r.get('jamid_verdict') == 'JAMID_AALAM_BOUNDARY':
            assert r.get('pre_root') is None, (
                f"{tok}: JAMID_AALAM_BOUNDARY must imply pre_root=None"
            )

    @pytest.mark.parametrize('tok', ALL_ALLAH_FORMS)
    def test_pre_root_none_implies_root_candidate_none(self, tok):
        r = hokom(tok)
        if r.get('pre_root') is None and r.get('jamid_verdict') == 'JAMID_AALAM_BOUNDARY':
            assert r.get('root_candidate') is None, (
                f"{tok}: pre_root=None (from JAMID_AALAM_BOUNDARY) must imply root_candidate=None"
            )

    @pytest.mark.parametrize('tok', ALL_ALLAH_FORMS)
    def test_jamid_boundary_implies_root_candidate_none(self, tok):
        """Direct transitivity check."""
        r = hokom(tok)
        if r.get('jamid_verdict') == 'JAMID_AALAM_BOUNDARY':
            assert r.get('root_candidate') is None, (
                f"{tok}: JAMID_AALAM_BOUNDARY must close root_candidate"
            )

    @pytest.mark.parametrize('tok', ALL_ALLAH_FORMS)
    def test_jamid_boundary_implies_phase4a_none(self, tok):
        r = hokom(tok)
        if r.get('jamid_verdict') == 'JAMID_AALAM_BOUNDARY':
            assert r.get('phase4a_result') is None, (
                f"{tok}: JAMID_AALAM_BOUNDARY must close phase4a (no wazn)"
            )

    @pytest.mark.parametrize('tok', ALL_ALLAH_FORMS)
    def test_jamid_boundary_implies_phase4b_none(self, tok):
        r = hokom(tok)
        if r.get('jamid_verdict') == 'JAMID_AALAM_BOUNDARY':
            assert r.get('phase4b_result') is None, (
                f"{tok}: JAMID_AALAM_BOUNDARY must close phase4b (no bab)"
            )

    @pytest.mark.parametrize('tok', ALL_ALLAH_FORMS)
    def test_jamid_boundary_implies_final_root_none(self, tok):
        r = hokom(tok)
        if r.get('jamid_verdict') == 'JAMID_AALAM_BOUNDARY':
            assert r.get('final_root') is None, (
                f"{tok}: JAMID_AALAM_BOUNDARY must close final_root"
            )

    @pytest.mark.parametrize('tok', ALL_ALLAH_FORMS)
    def test_morphology_not_blocked_even_with_jamid(self, tok):
        """
        JAMID_AALAM_BOUNDARY ≠ morphology_blocked.
        The phonological structure of الله is valid — jamid classification
        is a LEXICAL decision, not a PHONOLOGICAL block.
        """
        r = hokom(tok)
        assert r.get('morphology_blocked') is False, (
            f"{tok}: morphology_blocked must be False for الله — "
            f"JAMID_AALAM is a lexical boundary, not a phonological failure"
        )

    @pytest.mark.parametrize('tok', ALL_ALLAH_FORMS)
    def test_mabni_not_mutated_by_jamid(self, tok):
        """
        mabni.verdict must remain 'OPEN' after JAMID_AALAM_BOUNDARY fires.
        The jamid layer does not change or wrap the mabni result.
        """
        r = hokom(tok)
        mabni = r.get('mabni')
        mabni_verdict = getattr(mabni, 'verdict', None)
        assert mabni_verdict == 'OPEN', (
            f"{tok}: mabni.verdict must remain 'OPEN' — "
            f"JAMID_AALAM is a separate lexical layer, not a mabni classification. "
            f"Got: {mabni_verdict!r}"
        )

    def test_jamid_is_checked_on_segment_host_not_original(self):
        """
        The lookup must use segment_host, not original_surface.
        For وَاللَّهُ: original=وَاللَّهُ, segment_host=اللَّهُ.
        The jamid_boundary.input_surface must equal segment_host.
        """
        r = hokom('وَاللَّهُ')
        jb = r.get('jamid_boundary')
        seg_host = r.get('segment_host')
        assert jb is not None
        assert jb.input_surface == seg_host, (
            f"jamid_boundary.input_surface must equal segment_host, "
            f"not original_surface. "
            f"input_surface={jb.input_surface!r}, segment_host={seg_host!r}"
        )
        assert jb.input_surface != 'وَاللَّهُ', (
            "jamid_boundary.input_surface must NOT be the original full token"
        )
