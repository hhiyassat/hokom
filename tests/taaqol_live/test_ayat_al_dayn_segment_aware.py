"""
Ayat al-Dayn targeted assertions for segment-aware Taaqol integration.
Tests canonical cases from HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME §16.

Expected values are grounded in Hokom's canonical segmenter output.
All assertions are verified against actual segment_token() output.

HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME
"""
from __future__ import annotations
import pytest
from types import SimpleNamespace
from unittest.mock import patch

from pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle
from pipeline.taaqol_integration.live.models import HokomTaaqolDecision
from pipeline.p0_segmentation.models import SegmentationRequest
from pipeline.p0_segmentation.normalization import strip_diacritics


def _seg(surface: str):
    from pipeline.p0_segmentation import segment_token
    req = SegmentationRequest(
        request_id=f'test:{surface}',
        original_surface=surface,
        normalized_surface=surface,
    )
    return segment_token(req)


def _make_bundle(surface: str):
    sb = _seg(surface)
    return SimpleNamespace(
        claim_id=f'hokom:test:{surface}',
        token_id=f'tok_{surface}',
        original_surface=surface,
        normalized_surface=surface,
        segment_bundle=sb,
        segment_host=sb.host,
        segment_proclitics=sb.proclitics,
        segment_definite_article=sb.definite_article,
        segment_enclitics=sb.enclitics,
        segment_clitic_only=sb.clitic_only,
        segment_verdict=str(sb.verdict),
        morphology_surface=sb.host,
        morphology_blocked=(sb.host is None),
        morphology_block_reason=None,
        domain_directive='ACCEPT',
        source_engine='HOKOM_ROOT_ENGINE',
        evidence_ids=(), trace_ids=(), active_residuals=(),
        part_of_speech=None, lexical_class=None, root_claim=None,
        wazn_claim=None, masdar_claim=None, mushtaq_claims=(),
        inflection_claim=None, mabni_status=None,
    )


def bd(surface):
    b = _make_bundle(surface)
    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(b)
    return b, result


# ── §16 canonical cases ────────────────────────────────────────────────────────

def test_case_01_bidayn():
    """بِدَيْنٍ → proclitic بِ + host دَيْنٍ (debt instrument)."""
    b, r = bd('بِدَيْنٍ')
    assert strip_diacritics(b.segment_host or '') == 'دين'
    procs_bare = tuple(strip_diacritics(p) for p in b.segment_proclitics)
    assert 'ب' in procs_bare
    assert isinstance(r, HokomTaaqolDecision)
    # Center must be host, not full token
    assert r.taaqol_center_scope == b.segment_host


def test_case_02_bilAdl():
    """بِالْعَدْلِ → proclitic بِ + host عَدْلِ (with justice)."""
    b, r = bd('بِالْعَدْلِ')
    assert strip_diacritics(b.segment_host or '') == 'عدل', f"host={b.segment_host}"
    procs_bare = tuple(strip_diacritics(p) for p in b.segment_proclitics)
    assert 'ب' in procs_bare
    assert r.taaqol_center_scope == b.segment_host
    assert r.taaqol_center_scope != 'بِالْعَدْلِ'


def test_case_03_walyaktub():
    """وَلْيَكْتُبْ → proclitics وَ + لْ + host يَكْتُبْ."""
    b, r = bd('وَلْيَكْتُبْ')
    procs_bare = tuple(strip_diacritics(p) for p in b.segment_proclitics)
    assert 'و' in procs_bare
    assert 'ل' in procs_bare
    host_bare = strip_diacritics(b.segment_host or '')
    assert host_bare.startswith('يكتب')
    assert r.taaqol_center_scope == b.segment_host


def test_case_04_falyaktub():
    """فَلْيَكْتُبْ → proclitics فَ + لْ + host يَكْتُبْ."""
    b, r = bd('فَلْيَكْتُبْ')
    procs_bare = tuple(strip_diacritics(p) for p in b.segment_proclitics)
    assert 'ف' in procs_bare
    assert 'ل' in procs_bare
    host_bare = strip_diacritics(b.segment_host or '')
    assert host_bare.startswith('يكتب')
    assert r.taaqol_center_scope == b.segment_host


def test_case_07_wa_la():
    """وَلَا → proclitic وَ + host لَا."""
    b, r = bd('وَلَا')
    procs_bare = tuple(strip_diacritics(p) for p in b.segment_proclitics)
    assert 'و' in procs_bare
    host_bare = strip_diacritics(b.segment_host or '')
    assert 'لا' in host_bare or host_bare == 'لا'
    assert r.taaqol_center_scope == b.segment_host


def test_case_08_minhu():
    """مِنْهُ → host مِنْ + enclitic هُ."""
    b, r = bd('مِنْهُ')
    host_bare = strip_diacritics(b.segment_host or '')
    assert host_bare == 'من', f"host={b.segment_host}"
    encs_bare = tuple(strip_diacritics(e) for e in b.segment_enclitics)
    assert any('ه' in e for e in encs_bare), f"enclitic هُ missing from {b.segment_enclitics}"
    assert r.taaqol_center_scope == b.segment_host


def test_case_09_ajalih():
    """أَجَلِهِ → host أَجَلِ + enclitic هِ."""
    b, r = bd('أَجَلِهِ')
    host_bare = strip_diacritics(b.segment_host or '')
    # strip_diacritics preserves hamza: أجل (not اجل)
    assert 'جل' in host_bare, f"host={b.segment_host!r} bare={host_bare!r}"
    encs_bare = tuple(strip_diacritics(e) for e in b.segment_enclitics)
    assert any('ه' in e for e in encs_bare), f"enclitic missing: {b.segment_enclitics}"


def test_case_10_waliyyuhu():
    """وَلِيُّهُ → host وَلِيُّ + enclitic هُ (guardian, no waw-split)."""
    b, r = bd('وَلِيُّهُ')
    # The segmenter preserves وَ in the host (waw is part of the lexical item here)
    host_bare = strip_diacritics(b.segment_host or '')
    assert host_bare.startswith('ولي'), f"host={b.segment_host!r}"
    encs_bare = tuple(strip_diacritics(e) for e in b.segment_enclitics)
    assert any('ه' in e for e in encs_bare), f"enclitic هُ missing: {b.segment_enclitics}"
    # No proclitic — وَ is lexical here
    assert b.segment_proclitics == (), f"No proclitics expected: {b.segment_proclitics}"


def test_case_11_bikum_clitic_only():
    """بِكُمْ → clitic-only, no host → DEFERRED, center=None."""
    b, r = bd('بِكُمْ')
    assert b.segment_host is None, f"بِكُمْ must be clitic-only: host={b.segment_host!r}"
    assert b.segment_clitic_only is True
    assert isinstance(r, HokomTaaqolDecision)
    assert r.effective_verdict != 'LICENSED'
    assert r.taaqol_center_scope is None


def test_case_12_safiihan():
    """سَفِيهًا → no segmentation (unsplit nominal)."""
    b, r = bd('سَفِيهًا')
    assert b.segment_proclitics == (), f"سَفِيهًا should not split: {b.segment_proclitics}"
    host_bare = strip_diacritics(b.segment_host or '')
    assert host_bare.startswith('سفيه'), f"host={b.segment_host}"


def test_case_13_lil_shahada():
    """لِلشَّهَادَةِ → proclitic لِ + host شَّهَادَةِ."""
    b, r = bd('لِلشَّهَادَةِ')
    procs_bare = tuple(strip_diacritics(p) for p in b.segment_proclitics)
    assert 'ل' in procs_bare, f"لِ should be proclitic: {b.segment_proclitics}"
    host_bare = strip_diacritics(b.segment_host or '')
    assert 'شهاد' in host_bare, f"host={b.segment_host}"
    assert r.taaqol_center_scope == b.segment_host
    assert r.taaqol_center_scope != 'لِلشَّهَادَةِ'


def test_case_14_allah():
    """اللَّهُ → no split (divine name is protected host)."""
    b, r = bd('اللَّهُ')
    assert b.segment_proclitics == ()
    host_bare = strip_diacritics(b.segment_host or '')
    assert 'الله' in host_bare or 'لله' in host_bare or 'لل' in host_bare, \
        f"host={b.segment_host!r}"


def test_case_15_wa_allah():
    """وَاللَّهُ → proclitic وَ + host اللَّهُ."""
    b, r = bd('وَاللَّهُ')
    procs_bare = tuple(strip_diacritics(p) for p in b.segment_proclitics)
    assert 'و' in procs_bare
    # Center must not be the full token
    assert r.taaqol_center_scope != 'وَاللَّهُ'
    assert r.taaqol_center_scope == b.segment_host


def test_case_16_katibun():
    """كَاتِبٌ → unsplit nominal (no proclitic)."""
    b, r = bd('كَاتِبٌ')
    assert b.segment_proclitics == ()
    host_bare = strip_diacritics(b.segment_host or '')
    assert host_bare.startswith('كاتب')


def test_case_17_fusooq():
    """فُسُوقٌ → unsplit nominal."""
    b, r = bd('فُسُوقٌ')
    assert b.segment_proclitics == ()
    host_bare = strip_diacritics(b.segment_host or '')
    assert host_bare.startswith('فسوق')


# ── All canonical cases return typed decision ──────────────────────────────────

@pytest.mark.parametrize('surface', [
    'بِدَيْنٍ', 'بِالْعَدْلِ', 'وَلْيَكْتُبْ', 'فَلْيَكْتُبْ',
    'مِنْهُ', 'لِلشَّهَادَةِ', 'بِكُمْ', 'سَفِيهًا',
    'وَلِيُّهُ', 'اللَّهُ', 'وَاللَّهُ', 'كَاتِبٌ', 'فُسُوقٌ',
])
def test_returns_typed_decision(surface):
    """evaluate_hokom_claim_bundle always returns HokomTaaqolDecision."""
    _, r = bd(surface)
    assert isinstance(r, HokomTaaqolDecision)
    assert r.fail_closed is True
    assert r.effective_verdict in ('LICENSED', 'DEFERRED', 'BLOCKED', 'RESIDUAL')
