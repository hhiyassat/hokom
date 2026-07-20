"""
Canonical public-entrypoint probe tests.
These tests call hokom() directly — LEVEL_B (end-to-end) tests.
A stage cannot be closed if these fail.

WIRING BUG NOTE (HOKOM-CONSTITUTIONAL-AMENDMENT-02):
    hokom_pipeline.py previously passed normalize(word) to SegmentationRequest.
    normalize() expands shadda (شَّ→شْشَ) and madda (آ→ءَا), corrupting segmenter.
    Fix: canonical_normalize(word) is used for the segmenter only.
    These tests verify the fix is wired correctly end-to-end.
"""
import unicodedata
import pytest
from hokom_pipeline import hokom


def bare(s):
    if s is None:
        return None
    return ''.join(c for c in s if unicodedata.category(c) not in ('Mn', 'Cf'))


# ── Basic struct ──────────────────────────────────────────────────────────────

def test_hokom_returns_dict():
    r = hokom('كَاتِبٌ')
    assert isinstance(r, dict)


def test_hokom_has_required_keys():
    r = hokom('بِدَيْنٍ')
    for k in ['segment_host', 'morphology_surface', 'morphology_blocked']:
        assert k in r, f"Missing key: {k!r}"


# ── Probe: بِدَيْنٍ ──────────────────────────────────────────────────────────

def test_probe_bidayn():
    r = hokom('بِدَيْنٍ')
    assert bare(r.get('segment_host')) == 'دين', (
        f"host={r.get('segment_host')!r}, bare={bare(r.get('segment_host'))!r}"
    )
    assert r.get('morphology_blocked') is not True


def test_probe_bidayn_proclitic():
    r = hokom('بِدَيْنٍ')
    proc_bare = tuple(bare(p) for p in (r.get('segment_proclitics') or ()))
    assert 'ب' in proc_bare, f"بِ not proclitic: {proc_bare}"


# ── Probe: بِالْعَدْلِ ───────────────────────────────────────────────────────

def test_probe_bilAdl():
    r = hokom('بِالْعَدْلِ')
    assert bare(r.get('segment_host')) == 'عدل', (
        f"host={r.get('segment_host')!r}"
    )


# ── Probe: آمَنُوا — madda expansion ─────────────────────────────────────────

def test_probe_amaanuu_no_madda_in_host():
    """آمَنُوا: madda must be expanded in segment_host — host must NOT contain آ (U+0622)."""
    r = hokom('آمَنُوا')
    seg_host = r.get('segment_host') or r.get('morphology_surface')
    assert seg_host is not None, "segment_host is None for آمَنُوا"
    assert 'آ' not in seg_host, (
        f"آمَنُوا: segment_host still contains unexpanded madda (آ): {seg_host!r}"
    )


def test_probe_amaanuu_original_surface_immutable():
    r = hokom('آمَنُوا')
    assert r.get('original_surface', 'آمَنُوا') == 'آمَنُوا', (
        "original_surface must be immutable"
    )


def test_probe_amaanuu_no_proclitics():
    r = hokom('آمَنُوا')
    procs = r.get('segment_proclitics') or ()
    assert procs == (), f"آمَنُوا: unexpected proclitics {procs}"


# ── Probe: وَلِيُّهُ — shadda expansion must NOT corrupt segmentation ─────────

def test_probe_waliyyuhu_no_proclitics():
    """وَلِيُّهُ: وَ and لِ are NOT proclitics — the word is وَلِيّ + هُ."""
    r = hokom('وَلِيُّهُ')
    procs = r.get('segment_proclitics') or ()
    assert procs == (), (
        f"وَلِيُّهُ: proclitics should be empty, got {procs!r}. "
        f"Wiring bug: normalize() expands shadda يُّ→يْيُ, causing 'لِ' to be seen as lam-proclitic."
    )


def test_probe_waliyyuhu_ha_enclitic():
    r = hokom('وَلِيُّهُ')
    enc_bare = tuple(bare(e) for e in (r.get('segment_enclitics') or ()))
    assert 'ه' in enc_bare, f"وَلِيُّهُ: هُ should be enclitic, got enclitics={r.get('segment_enclitics')}"


def test_probe_waliyyuhu_host_starts_with_waliy():
    r = hokom('وَلِيُّهُ')
    h = bare(r.get('segment_host'))
    assert h is not None and h.startswith('ولي'), (
        f"وَلِيُّهُ: host_bare should start with ولي, got {h!r}"
    )


# ── Probe: لِلشَّهَادَةِ — shadda expansion must not double consonant ─────────

def test_probe_lil_shahada_host():
    r = hokom('لِلشَّهَادَةِ')
    h = bare(r.get('segment_host'))
    assert h == 'شهادة', (
        f"لِلشَّهَادَةِ: host_bare={h!r}, expected 'شهادة'. "
        f"Wiring bug: normalize() expands شَّ→شْشَ, doubling the consonant in host."
    )


def test_probe_lil_shahada_proclitic():
    r = hokom('لِلشَّهَادَةِ')
    proc_bare = tuple(bare(p) for p in (r.get('segment_proclitics') or ()))
    assert 'ل' in proc_bare, f"لِلشَّهَادَةِ: لِ not proclitic, got {proc_bare}"


# ── Probe: أَيُّهَا — هَا must not be enclitic ────────────────────────────────

def test_probe_ayyuha_no_enclitics():
    r = hokom('أَيُّهَا')
    encs = r.get('segment_enclitics') or ()
    assert encs == (), (
        f"أَيُّهَا: هَا must not be enclitic (it is part of the particle), got {encs!r}"
    )


# ── Probe: الَّذِي — يِ must not be enclitic ─────────────────────────────────

def test_probe_alladhi_no_enclitics():
    r = hokom('الَّذِي')
    encs = r.get('segment_enclitics') or ()
    assert encs == (), (
        f"الَّذِي: يِ must not be enclitic, got {encs!r}. "
        f"Wiring bug: normalize() expands الَّ→ءَلْلَ, breaking the definite article."
    )


# ── Probe: اللَّهُ / اللَّهَ / اللَّهِ — هُ/هَ/هِ must not be enclitic ──────

def test_probe_allah_nom_no_enclitics():
    r = hokom('اللَّهُ')
    encs = r.get('segment_enclitics') or ()
    assert encs == (), (
        f"اللَّهُ: هُ must not be enclitic (it is the final consonant of الله), got {encs!r}. "
        f"Wiring bug: normalize() transforms اللَّهُ→ءَللْلَهُ, exposing 'هُ' as apparent suffix."
    )


def test_probe_allah_acc_no_enclitics():
    r = hokom('اللَّهَ')
    encs = r.get('segment_enclitics') or ()
    assert encs == (), f"اللَّهَ: هَ must not be enclitic, got {encs!r}"


def test_probe_allah_gen_no_enclitics():
    r = hokom('اللَّهِ')
    encs = r.get('segment_enclitics') or ()
    assert encs == (), f"اللَّهِ: هِ must not be enclitic, got {encs!r}"


# ── Probe: بِكُمْ — morphology_blocked ───────────────────────────────────────

def test_probe_bikum_blocked():
    r = hokom('بِكُمْ')
    assert r.get('morphology_blocked') is True, (
        f"بِكُمْ: morphology_blocked={r.get('morphology_blocked')!r}, expected True"
    )


def test_probe_bikum_no_host():
    r = hokom('بِكُمْ')
    assert r.get('segment_host') is None, (
        f"بِكُمْ: segment_host should be None, got {r.get('segment_host')!r}"
    )


# ── Probe: يَكُونَا — نَا must not be enclitic ────────────────────────────────

def test_probe_yakunaa_no_na_enclitic():
    r = hokom('يَكُونَا')
    encs = r.get('segment_enclitics') or ()
    enc_bare = tuple(bare(e) for e in encs)
    assert 'نا' not in enc_bare, (
        f"يَكُونَا: نَا must not be enclitic (dual suffix), got {encs!r}"
    )


# ── Probe: سَفِيهًا — no proclitics ──────────────────────────────────────────

def test_probe_safiihan_no_proclitics():
    r = hokom('سَفِيهًا')
    procs = r.get('segment_proclitics') or ()
    assert procs == (), f"سَفِيهًا: no proclitics expected, got {procs}"


# ── Probe: وَلْيَكْتُبْ — dual proclitics و + ل ───────────────────────────────

def test_probe_walyaktub_waw_proclitic():
    r = hokom('وَلْيَكْتُبْ')
    proc_bare = tuple(bare(p) for p in (r.get('segment_proclitics') or ()))
    assert 'و' in proc_bare, f"وَلْيَكْتُبْ: وَ not proclitic, got {proc_bare}"


def test_probe_walyaktub_lam_proclitic():
    r = hokom('وَلْيَكْتُبْ')
    proc_bare = tuple(bare(p) for p in (r.get('segment_proclitics') or ()))
    assert 'ل' in proc_bare, f"وَلْيَكْتُبْ: لْ not proclitic, got {proc_bare}"


# ── Cross-probe: original_surface immutability ────────────────────────────────

def test_original_surface_immutable():
    """original_surface must equal the input token for all probes."""
    tokens = ['آمَنُوا', 'بِدَيْنٍ', 'وَلِيُّهُ', 'لِلشَّهَادَةِ',
              'بِكُمْ', 'اللَّهُ', 'اللَّهَ', 'اللَّهِ']
    for tok in tokens:
        r = hokom(tok)
        got = r.get('original_surface', tok)
        assert got == tok, f"ORIGINAL_SURFACE_MUTATED: {tok!r} -> {got!r}"
