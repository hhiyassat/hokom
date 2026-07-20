"""
test_allah_divine_name.py
HOKOM-JAMID-AALAM-LEXICAL-BOUNDARY-CLOSURE-01

Tests for اسم الجلالة (the divine name الله) via hokom() pipeline entrypoint.

الله is MU'RAB (مرفوع/منصوب/مجرور) — NOT MABNI.
It must never be added to mabni_inventory and must never trigger MabniBoundary.
The correct route is JAMID_AALAM_BOUNDARY which closes root admission.
"""
import pytest
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from hokom_pipeline import hokom
from mabni_layer import MabniBoundary, MabniOpen, MabniBlocked

ALLAH_FORMS = ['اللَّهُ', 'اللَّهَ', 'اللَّهِ']


class TestAllahJamidAalamBoundary:
    """Core contract: all three case-inflected forms of الله must trigger JAMID_AALAM_BOUNDARY."""

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_root_candidate_is_none(self, tok):
        r = hokom(tok)
        assert r.get('root_candidate') is None, (
            f"{tok}: root_candidate must be None — root admission is closed for اسم الجلالة"
        )

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_pre_root_is_none(self, tok):
        r = hokom(tok)
        assert r.get('pre_root') is None, (
            f"{tok}: pre_root must be None — JAMID_AALAM_BOUNDARY closes pre-root stage"
        )

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_jamid_verdict(self, tok):
        r = hokom(tok)
        assert r.get('jamid_verdict') == 'JAMID_AALAM_BOUNDARY', (
            f"{tok}: jamid_verdict must be 'JAMID_AALAM_BOUNDARY'"
        )

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_aalam_category_divine_name(self, tok):
        r = hokom(tok)
        assert r.get('aalam_category') == 'divine_name', (
            f"{tok}: aalam_category must be 'divine_name'"
        )

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_jamid_category_ism_alam(self, tok):
        r = hokom(tok)
        assert r.get('jamid_category') == 'اسم علم', (
            f"{tok}: jamid_category must be 'اسم علم'"
        )

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_jamid_boundary_object_present(self, tok):
        r = hokom(tok)
        jb = r.get('jamid_boundary')
        assert jb is not None, f"{tok}: jamid_boundary object must be present"

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_lexical_identity_is_allah(self, tok):
        r = hokom(tok)
        jb = r.get('jamid_boundary')
        assert getattr(jb, 'lexical_identity', None) == 'الله', (
            f"{tok}: lexical_identity must be 'الله'"
        )

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_blocks_root_path(self, tok):
        r = hokom(tok)
        jb = r.get('jamid_boundary')
        assert getattr(jb, 'blocks_root_path', None) is True, (
            f"{tok}: blocks_root_path must be True"
        )


class TestAllahNotMabni:
    """
    الله is MU'RAB — it must NEVER be classified as mabni.
    mabni.verdict must be 'OPEN' (i.e. MabniOpen), not any MabniBoundary variant.
    """

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_mabni_is_open_not_boundary(self, tok):
        r = hokom(tok)
        mabni = r.get('mabni')
        assert isinstance(mabni, MabniOpen), (
            f"{tok}: mabni must be MabniOpen — الله is MU'RAB, not MABNI. "
            f"Got: {type(mabni).__name__} verdict={getattr(mabni, 'verdict', None)!r}"
        )

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_not_mabni_boundary(self, tok):
        r = hokom(tok)
        mabni = r.get('mabni')
        assert not isinstance(mabni, MabniBoundary), (
            f"{tok}: mabni must NOT be MabniBoundary — الله is MU'RAB"
        )

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_morphology_not_blocked(self, tok):
        r = hokom(tok)
        assert r.get('morphology_blocked') is False, (
            f"{tok}: morphology must not be blocked — الله has valid phonological structure"
        )


class TestAllahDownstreamClosed:
    """Downstream stages must be closed when JAMID_AALAM_BOUNDARY fires."""

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_phase4a_not_opened(self, tok):
        r = hokom(tok)
        assert r.get('phase4a_result') is None, f"{tok}: phase4a must not be opened"

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_phase4b_not_opened(self, tok):
        r = hokom(tok)
        assert r.get('phase4b_result') is None, f"{tok}: phase4b must not be opened"

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_final_root_is_none(self, tok):
        r = hokom(tok)
        assert r.get('final_root') is None, f"{tok}: final_root must be None"

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_final_wazn_is_none(self, tok):
        r = hokom(tok)
        assert r.get('final_wazn') is None, f"{tok}: final_wazn must be None"


class TestAllahSegmentation:
    """Segmentation must be correct — no enclitic/proclitic on bare forms."""

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_no_enclitics(self, tok):
        r = hokom(tok)
        assert r.get('segment_enclitics') == (), f"{tok}: no enclitics expected"

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_no_proclitics(self, tok):
        r = hokom(tok)
        assert r.get('segment_proclitics') == (), f"{tok}: no proclitics on bare form"

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_segment_host_is_not_none(self, tok):
        r = hokom(tok)
        assert r.get('segment_host') is not None, f"{tok}: segment_host must be present"

    @pytest.mark.parametrize('tok', ALLAH_FORMS)
    def test_original_surface_unchanged(self, tok):
        r = hokom(tok)
        assert r.get('original') == tok, f"{tok}: original_surface must be unchanged"
