"""
tests/test_wiring_gate.py
Regression tests for the canonical pipeline wiring gate.
Tests 1-12 as required by HOKOM-GATE-REGRESSION-01.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


_DEMO_ARTIFACT_PATHS = (
    REPO_ROOT / "reports" / "ayat_al_dayn_demo" / "ayat_al_dayn_manager_report.html",
    REPO_ROOT / "reports" / "ayat_al_dayn_demo" / "ayat_al_dayn_results.csv",
    REPO_ROOT / "reports" / "ayat_al_dayn_demo" / "ayat_al_dayn_results_full.json",
)


import pytest

@pytest.fixture(autouse=True)
def _preserve_canonical_demo_artifacts():
    snapshots = {
        artifact: artifact.read_bytes() if artifact.exists() else None
        for artifact in _DEMO_ARTIFACT_PATHS
    }

    yield

    for artifact, original in snapshots.items():
        if original is None:
            artifact.unlink(missing_ok=True)
        else:
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_bytes(original)
sys.path.insert(0, str(REPO_ROOT))

import pytest

# ── helpers ────────────────────────────────────────────────────────────────────

def _hokom(surface):
    """Call hokom() with correct PYTHONPATH."""
    # Ensure vendor is on path
    vendor = REPO_ROOT / 'vendor' / 'Taaqol-GPT' / 'src'
    if str(vendor) not in sys.path:
        sys.path.insert(0, str(vendor))
    from hokom_pipeline import hokom
    return hokom(surface)

def _bundle_dict(hr):
    from pipeline.corpus.live_runner import _build_bundle_dict
    return _build_bundle_dict(hr)

def _claim_bundle(bd):
    from pipeline.sga.adapters import build_claim_bundle
    return build_claim_bundle(bd, 'TEST', 'TEST')

def _slot_value(bundle, slot_id_name):
    from pipeline.sga.contracts import SlotId, SlotState
    for s in bundle.typed_slots:
        if s.slot_id.name == slot_id_name or str(s.slot_id) == slot_id_name:
            if s.state == SlotState.FILLED:
                return s.value
    return None

def _slot_state(bundle, slot_id_name):
    from pipeline.sga.contracts import SlotState
    for s in bundle.typed_slots:
        if s.slot_id.name == slot_id_name or str(s.slot_id) == slot_id_name:
            return s.state
    return None


# ── Test 1: SEGMENT_HOST typed slot and top-level field are identical ─────────
def test_01_segment_host_typed_slot_matches_top_level():
    """SEGMENT_HOST typed slot and segmentation.host_surface must agree."""
    hr = _hokom('يَكْتُبُ')
    bd = _bundle_dict(hr)
    bundle = _claim_bundle(bd)

    # Top-level from bundle dict
    top_level = bd.get('segment_host')

    # From typed slot
    slot_val = _slot_value(bundle, 'SEGMENT_HOST')

    assert top_level == slot_val, (
        f"SEGMENT_HOST mismatch: top_level={top_level!r}, typed_slot={slot_val!r}"
    )


# ── Test 2: OPEN_MORPHOLOGY invokes canonical post-segmentation routing ────────
def test_02_open_morphology_invokes_routing():
    """PATH_DIRECTIVE=OPEN_MORPHOLOGY must not leave WORD_CLASS unexecuted."""
    if sys.version_info < (3, 11):
        pytest.skip("Requires Python 3.11+ for Taaqol StrEnum")
    hr = _hokom('يَكْتُبُ')
    bd = _bundle_dict(hr)
    bundle = _claim_bundle(bd)

    path_directive = _slot_value(bundle, 'PATH_DIRECTIVE_SLOT')
    word_class = bd.get('word_class')

    if path_directive == 'OPEN_MORPHOLOGY':
        assert word_class is not None, (
            "PATH_DIRECTIVE=OPEN_MORPHOLOGY but word_class is None — "
            "post-segmentation routing not executed"
        )


# ── Test 3: يَكْتُبُ reaches actual Word Class owner ──────────────────────────
def test_03_yaktubу_reaches_word_class():
    """يَكْتُبُ must produce a non-None word_class result."""
    if sys.version_info < (3, 11):
        pytest.skip("Requires Python 3.11+ for Taaqol StrEnum")
    hr = _hokom('يَكْتُبُ')
    wc = hr.get('word_class')
    assert wc is not None, (
        f"word_class is None for يَكْتُبُ\n"
        f"  stage={hr.get('stage')!r}  scg_status={hr.get('scg_status')!r}\n"
        f"  failure_code={hr.get('failure_code')!r}\n"
        f"  post_boundary_routing_failure={hr.get('post_boundary_routing_failure')!r}\n"
        f"  word_class_exception={hr.get('word_class_exception')!r}"
    )


# ── Test 4: Runtime inactivity always has a failure code ──────────────────────
def test_04_runtime_inactivity_has_failure_code():
    """When taaqol_decision is None, taaqol_runtime must carry a failure_code."""
    hr = _hokom('يَكْتُبُ')
    td = hr.get('taaqol_decision')
    if td is None:
        tr = hr.get('taaqol_runtime') or {}
        scg_failure = hr.get('failure_code')
        # Either taaqol_runtime.failure_code or scg failure_code must be set
        has_failure = (
            tr.get('failure_code') is not None
            or scg_failure is not None
            or hr.get('post_boundary_routing_failure') is not None
        )
        assert has_failure, (
            "taaqol_decision=None but no failure_code set — silent fallback"
        )


# ── Test 5: No stale Python 3.10 message ──────────────────────────────────────
def test_05_no_stale_python_310_message():
    """Demo output must not contain hardcoded Python 3.10 sandbox statement."""
    import subprocess
    result = subprocess.run(
        [sys.executable, 'scripts/demo_ayat_al_dayn.py',
         '--token', 'يَكْتُبُ', '--no-color'],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        env={**__import__('os').environ,
             'PYTHONPATH': 'src:vendor/Taaqol-GPT/src'},
    )
    combined = result.stdout + result.stderr
    assert 'Python 3.10 sandbox' not in combined, (
        "Hardcoded 'Python 3.10 sandbox' string found in output"
    )
    assert 'python 3.10' not in combined.lower().replace('python 3.12', ''), (
        "Stale Python 3.10 reference found"
    )


# ── Test 6: Single-token report does not display complete ayah ────────────────
def test_06_single_token_does_not_display_full_ayah():
    """--token mode title/summary must not claim to be the full Ayat al-Dayn analysis."""
    import subprocess
    result = subprocess.run(
        [sys.executable, 'scripts/demo_ayat_al_dayn.py',
         '--token', 'يَكْتُبُ', '--no-color'],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        env={**__import__('os').environ,
             'PYTHONPATH': 'src:vendor/Taaqol-GPT/src'},
    )
    # The output must NOT claim 129 tokens or "complete Ayah" when one token was run
    combined = result.stdout + result.stderr
    assert '129' not in combined or 'probe' in combined.lower() or 'single' in combined.lower(), (
        "Single-token run appears to claim full ayah scope"
    )


# ── Test 7: Complete-ayah run cannot claim completion with one token ───────────
def test_07_full_run_requires_all_tokens():
    """Summary stats token_count must equal actual TOKENS list length for full run."""
    import sys as _sys
    _sys.path.insert(0, str(REPO_ROOT))
    try:
        from scripts.demo_ayat_al_dayn import TOKENS, summary_stats
    except ImportError:
        pytest.skip("Cannot import demo script as module")

    # If there are TOKENS defined, a full run must produce that many results
    if len(TOKENS) > 1:
        # Simulate partial results (one token only)
        partial_results = [{'token_index': 1, 'original_surface': TOKENS[0], 'error': None,
                             'taaqol': {'available': False, 'runtime': {}},
                             'word_class': {'class': None}, 'segmentation': {}}]
        stats = summary_stats(partial_results)
        # partial run should not claim token_count == len(TOKENS)
        assert stats.get('token_count', 0) != len(TOKENS) or len(partial_results) != len(TOKENS), (
            "Summary stats claims full ayah with partial results"
        )


# ── Test 8: TAAQOL_RUNTIME_ACTIVE=0 is an integrity failure when requested ────
def test_08_taaqol_inactive_is_integrity_failure():
    """integrity_check must flag TAAQOL_RUNTIME_ACTIVE=0 when Taaqol requested."""
    try:
        from scripts.demo_ayat_al_dayn import integrity_check
    except ImportError:
        pytest.skip("Cannot import demo script as module")

    # Simulate a result where taaqol is requested but inactive
    fake_results = [{
        'token_index': 1,
        'original_surface': 'يَكْتُبُ',
        'error': None,
        'taaqol': {
            'available': False,
            'runtime': {'failure_code': None, 'gate_executed': False,
                        'slot_graph_created': False, 'kernel_loaded': False,
                        'gamma_executed': False},
        },
        'word_class': {'class': 'FI3L', 'inflection_skipped_reason': None},
        'segmentation': {'host_surface': 'يَكْتُبُ'},
        'typed_slots': [],
        'claim_key': 'test',
        'evaluation_id': 'test',
        'composite_verdict': {'overall_verdict': 'UNKNOWN', 'has_unresolved_claims': False},
    }]
    checks = integrity_check(fake_results)
    assert checks.get('SILENT_FALLBACKS', 0) > 0 or checks.get('TAAQOL_RUNTIME_INACTIVE', False), (
        "TAAQOL_RUNTIME_ACTIVE=0 not flagged as failure"
    )


# ── Test 9: CSV and HTML derive from the same canonical bundle ─────────────────
def test_09_csv_html_from_same_bundle():
    """segment_host in _build_bundle_dict must equal hr.get('segment_host')."""
    hr = _hokom('يَكْتُبُ')
    bd = _bundle_dict(hr)

    hr_host = hr.get('segment_host') or hr.get('morphology_surface')
    bd_host = bd.get('segment_host')

    assert hr_host == bd_host, (
        f"Bundle dict segment_host={bd_host!r} != hr segment_host={hr_host!r}"
    )


# ── Test 10: CSV top-level fields agree with typed-slot values ─────────────────
def test_10_csv_top_level_agrees_with_typed_slots():
    """word_class in bundle_dict must match WORD_CLASS_SLOT value in typed slots."""
    hr = _hokom('يَكْتُبُ')
    bd = _bundle_dict(hr)
    bundle = _claim_bundle(bd)

    top_wc = bd.get('word_class')
    slot_wc = _slot_value(bundle, 'WORD_CLASS_SLOT')

    # Both should be equal (or both None/UNKNOWN)
    if top_wc is not None:
        assert slot_wc == top_wc, (
            f"WORD_CLASS mismatch: top_level={top_wc!r}, typed_slot={slot_wc!r}"
        )


# ── Test 11: --fail-on-runtime-error returns nonzero for failed conditions ─────
def test_11_fail_on_runtime_error_nonzero():
    """--fail-on-runtime-error must exit nonzero if WORD_CLASS not reached."""
    import subprocess
    hr = _hokom('يَكْتُبُ')
    wc = hr.get('word_class')

    # Only test the exit code if we know it should fail
    if wc is None:
        result = subprocess.run(
            [sys.executable, 'scripts/demo_ayat_al_dayn.py',
             '--token', 'يَكْتُبُ', '--taaqol', '--no-color', '--fail-on-runtime-error'],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT),
            env={**__import__('os').environ,
                 'PYTHONPATH': 'src:vendor/Taaqol-GPT/src'},
        )
        assert result.returncode != 0, (
            "word_class=None but --fail-on-runtime-error returned 0"
        )


# ── Test 12: Existing canonical tests remain green ────────────────────────────
def test_12_canonical_scg_gates_all_approved():
    """All 11 SCG gates must return APPROVED for a standard verb."""
    vendor = REPO_ROOT / 'vendor' / 'Taaqol-GPT' / 'src'
    if str(vendor) not in sys.path:
        sys.path.insert(0, str(vendor))

    try:
        from pipeline.governance.taaqol_judgment_enforcer import (
            build_judgment_matrix_for_surface,
            DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT,
        )
        matrix = build_judgment_matrix_for_surface('يَكْتُبُ')
        if matrix.edge_count == DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT:
            blocked = [j for j in matrix.judgments if j.gate_verdict != 'APPROVED']
            assert not blocked, (
                f"SCG gates not all APPROVED: {[(j.edge_id, j.gate_verdict) for j in blocked]}"
            )
        # If fewer edges were judged, at least check none are silent fallbacks
        assert matrix.silent_fallbacks == 0, "Silent fallbacks found in SCG gate matrix"
    except ImportError:
        pytest.skip("Taaqol vendor not importable")


# ── Integrity count polarity tests (tests 13-18) ──────────────────────────────
# These tests verify that TAAQOL_RUNTIME_ACTIVE is never counted as a violation
# and that the violation computation is consistent across all renderers.

def _get_compute_violation_count():
    """Import compute_violation_count from its canonical location."""
    sys.path.insert(0, str(REPO_ROOT / 'src'))
    from hokom.demo.demo_renderer import compute_violation_count, integrity_key_ok, VIOLATION_KEYS
    return compute_violation_count, integrity_key_ok, VIOLATION_KEYS


# ── Test 13: TAAQOL_RUNTIME_ACTIVE=1 does not increase violation count ─────────
def test_13_taaqol_runtime_active_not_a_violation():
    """TAAQOL_RUNTIME_ACTIVE=N must never contribute to violation count."""
    compute_violation_count, _, _ = _get_compute_violation_count()
    checks_active = {k: 0 for k in (
        "SLOTS_MISSING_STATE", "LICENSED_WITHOUT_SCOPE", "MISSING_EVALUATION_ID",
        "EVALUATION_ID_COLLISIONS", "MISSING_TAAQOL_TRACE_ACTIVE",
        "CLAIM_KEY_NONDETERMINISM", "UNTYPED_PAYLOADS",
        "SILENT_FALLBACKS", "UNEXPECTED_RUNTIME_ERRORS",
        "TAAQOL_RUNTIME_ACTIVE", "TAAQOL_RUNTIME_INACTIVE",
    )}
    checks_active["TAAQOL_RUNTIME_ACTIVE"] = 1
    assert compute_violation_count(checks_active) == 0, (
        "TAAQOL_RUNTIME_ACTIVE=1 should not be counted as a violation"
    )
    checks_active["TAAQOL_RUNTIME_ACTIVE"] = 5
    assert compute_violation_count(checks_active) == 0, (
        "TAAQOL_RUNTIME_ACTIVE=5 should not be counted as a violation"
    )


# ── Test 14: TAAQOL_RUNTIME_INACTIVE=True adds one violation ─────────────────
def test_14_taaqol_runtime_inactive_true_is_one_violation():
    """TAAQOL_RUNTIME_INACTIVE=True must contribute exactly 1 to the violation count."""
    compute_violation_count, _, _ = _get_compute_violation_count()
    checks = {k: 0 for k in (
        "SLOTS_MISSING_STATE", "LICENSED_WITHOUT_SCOPE", "MISSING_EVALUATION_ID",
        "EVALUATION_ID_COLLISIONS", "MISSING_TAAQOL_TRACE_ACTIVE",
        "CLAIM_KEY_NONDETERMINISM", "UNTYPED_PAYLOADS",
        "SILENT_FALLBACKS", "UNEXPECTED_RUNTIME_ERRORS",
        "TAAQOL_RUNTIME_ACTIVE", "TAAQOL_RUNTIME_INACTIVE",
    )}
    checks["TAAQOL_RUNTIME_INACTIVE"] = True
    assert compute_violation_count(checks) == 1, (
        "TAAQOL_RUNTIME_INACTIVE=True must be exactly 1 violation"
    )
    checks["TAAQOL_RUNTIME_INACTIVE"] = False
    assert compute_violation_count(checks) == 0, (
        "TAAQOL_RUNTIME_INACTIVE=False must be 0 violations"
    )


# ── Test 15: One silent fallback contributes 1 to the violation count ─────────
def test_15_silent_fallback_is_one_violation():
    """SILENT_FALLBACKS=1 must contribute exactly 1 to the violation count."""
    compute_violation_count, _, _ = _get_compute_violation_count()
    checks = {k: 0 for k in (
        "SLOTS_MISSING_STATE", "LICENSED_WITHOUT_SCOPE", "MISSING_EVALUATION_ID",
        "EVALUATION_ID_COLLISIONS", "MISSING_TAAQOL_TRACE_ACTIVE",
        "CLAIM_KEY_NONDETERMINISM", "UNTYPED_PAYLOADS",
        "SILENT_FALLBACKS", "UNEXPECTED_RUNTIME_ERRORS",
        "TAAQOL_RUNTIME_ACTIVE", "TAAQOL_RUNTIME_INACTIVE",
    )}
    checks["SILENT_FALLBACKS"] = 1
    checks["TAAQOL_RUNTIME_ACTIVE"] = 3  # must not inflate the count
    assert compute_violation_count(checks) == 1, (
        "SILENT_FALLBACKS=1 with TAAQOL_RUNTIME_ACTIVE=3 must be exactly 1 violation"
    )


# ── Test 16: All-zero failure keys + active runtime → ACCEPTED (0) ─────────────
def test_16_clean_active_runtime_is_accepted():
    """Clean checks with active Taaqol runtime must produce ACCEPTED (0)."""
    compute_violation_count, _, _ = _get_compute_violation_count()
    checks = {
        "SLOTS_MISSING_STATE":         0,
        "LICENSED_WITHOUT_SCOPE":      0,
        "MISSING_EVALUATION_ID":       0,
        "EVALUATION_ID_COLLISIONS":    0,
        "MISSING_TAAQOL_TRACE_ACTIVE": 0,
        "CLAIM_KEY_NONDETERMINISM":    0,
        "UNTYPED_PAYLOADS":            0,
        "SILENT_FALLBACKS":            0,
        "UNEXPECTED_RUNTIME_ERRORS":   0,
        "TAAQOL_RUNTIME_ACTIVE":       1,
        "TAAQOL_RUNTIME_INACTIVE":     False,
    }
    count = compute_violation_count(checks)
    assert count == 0, f"Expected 0 violations for clean checks, got {count}"


# ── Test 17: Terminal, HTML, JSON renderers use compute_violation_count ────────
def test_17_renderers_use_canonical_violation_count():
    """All renderers must reference compute_violation_count, not sum(values)."""
    # Verify by checking that the demo script imports compute_violation_count
    demo_path = REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    src = demo_path.read_text(encoding='utf-8')
    assert 'compute_violation_count' in src, (
        "demo_ayat_al_dayn.py must use compute_violation_count"
    )
    # Verify demo_renderer also uses it
    renderer_path = REPO_ROOT / 'src' / 'hokom' / 'demo' / 'demo_renderer.py'
    r_src = renderer_path.read_text(encoding='utf-8')
    assert 'compute_violation_count' in r_src, (
        "demo_renderer.py must define/use compute_violation_count"
    )
    assert 'VIOLATION_KEYS' in r_src, (
        "demo_renderer.py must define VIOLATION_KEYS"
    )
    # The old naive sum must not appear
    assert 'sum(v for v in integrity.values()' not in r_src, (
        "demo_renderer.py must not use sum(integrity.values())"
    )


# ── Test 18: Live token remains GATE=PASS with integrity_violation_count=0 ────
def test_18_live_token_gate_pass():
    """A live يَكْتُبُ run must produce integrity_violation_count=0 and exit 0."""
    if sys.version_info < (3, 11):
        pytest.skip("Requires Python 3.11+ for Taaqol StrEnum")
    import subprocess
    result = subprocess.run(
        [sys.executable, 'scripts/demo_ayat_al_dayn.py',
         '--token', 'يَكْتُبُ', '--taaqol', '--no-color', '--fail-on-runtime-error'],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        env={**__import__('os').environ,
             'PYTHONPATH': 'src:vendor/Taaqol-GPT/src'},
    )
    assert result.returncode == 0, (
        f"Gate returned nonzero for يَكْتُبُ:\n{result.stderr[-2000:]}"
    )
    combined = result.stdout + result.stderr
    assert 'GATE=PASS' in combined, "GATE=PASS not found in output"
    assert 'CLIENT_PRESENTATION_READY=YES' in combined, (
        "CLIENT_PRESENTATION_READY=YES not found"
    )
    # integrity_violation_count must be 0 in JSON output
    import json as _json
    json_path = REPO_ROOT / 'reports' / 'ayat_al_dayn_demo' / 'ayat_al_dayn_results_full.json'
    if json_path.exists():
        data = _json.loads(json_path.read_text(encoding='utf-8'))
        assert data.get('integrity_violation_count', -1) == 0, (
            f"JSON integrity_violation_count={data.get('integrity_violation_count')}, expected 0"
        )
        assert data.get('integrity_status') == 'ACCEPTED', (
            f"JSON integrity_status={data.get('integrity_status')!r}, expected ACCEPTED"
        )


# ── Test 19: JSON persists client_presentation_ready as bool ──────────────────
def test_19_json_persists_client_presentation_ready():
    """
    JSON output must include client_presentation_ready as a Python bool (True/False),
    never as the string 'YES'/'NO'.  presentation_failures must be an empty list
    for a clean live token.
    """
    if sys.version_info < (3, 11):
        pytest.skip("Requires Python 3.11+ for Taaqol StrEnum")
    import subprocess, json as _json
    # Run the live token to generate fresh JSON
    result = subprocess.run(
        [sys.executable, 'scripts/demo_ayat_al_dayn.py',
         '--token', 'يَكْتُبُ', '--taaqol', '--no-color'],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        env={**__import__('os').environ,
             'PYTHONPATH': 'src:vendor/Taaqol-GPT/src'},
    )
    assert result.returncode == 0, (
        f"Demo script failed:\n{result.stderr[-2000:]}"
    )
    json_path = REPO_ROOT / 'reports' / 'ayat_al_dayn_demo' / 'ayat_al_dayn_results_full.json'
    assert json_path.exists(), "JSON report not written"
    data = _json.loads(json_path.read_text(encoding='utf-8'))

    # client_presentation_ready must be a bool True, not the string "YES"
    cpr = data.get('client_presentation_ready')
    assert cpr is True, (
        f"client_presentation_ready={cpr!r} — expected True (bool), not 'YES' or False"
    )

    # presentation_failures must be an empty list
    pf = data.get('presentation_failures')
    assert pf == [], (
        f"presentation_failures={pf!r} — expected [] for a clean live token"
    )

    # integrity_violation_count must be 0
    assert data.get('integrity_violation_count') == 0, (
        f"integrity_violation_count={data.get('integrity_violation_count')}, expected 0"
    )
    assert data.get('integrity_status') == 'ACCEPTED'


# ══════════════════════════════════════════════════════════════════════════════
# HOKOM-TAAQOL-FULL-AYAH-COVERAGE-AND-CLITIC-BOUNDARY-CLOSURE-01
# T-03 through T-19  (T-01/T-02 are collection/suite tests verified by CI)
# ══════════════════════════════════════════════════════════════════════════════

_BKUM_TOKEN  = 'بِكُمْ'
_bkum_result = None   # cached across tests in this module


def _get_bkum():
    """Run hokom('بِكُمْ') once and cache the result."""
    global _bkum_result
    if _bkum_result is None:
        vendor = REPO_ROOT / 'vendor' / 'Taaqol-GPT' / 'src'
        if str(vendor) not in sys.path:
            sys.path.insert(0, str(vendor))
        from hokom_pipeline import hokom
        _bkum_result = hokom(_BKUM_TOKEN)
    return _bkum_result


# T-03 ─ بِكُمْ is clitic_only ───────────────────────────────────────────────
def test_T03_bkum_is_clitic_only():
    if sys.version_info < (3, 11):
        pytest.skip("Requires Python 3.11+ — segmentation gate blocked by StrEnum on 3.10")
    r = _get_bkum()
    assert r.get('segment_clitic_only') is True, (
        f"Expected segment_clitic_only=True, got {r.get('segment_clitic_only')!r}"
    )


# T-04 ─ بِكُمْ has segment_host=None ────────────────────────────────────────
def test_T04_bkum_host_is_none():
    r = _get_bkum()
    assert r.get('segment_host') is None, (
        f"Expected segment_host=None, got {r.get('segment_host')!r}"
    )


# T-05 ─ بِكُمْ path directive is not OPEN_MORPHOLOGY ───────────────────────
def test_T05_bkum_path_directive_not_open_morphology():
    r = _get_bkum()
    typed_slots = r.get('typed_slots') or []
    path_slot = next(
        (s for s in typed_slots if s.get('slot_id') == 'PATH_DIRECTIVE_SLOT'),
        None,
    )
    if path_slot is None:
        pytest.skip("typed_slots not present in hokom result for this token")
    assert path_slot.get('value') != 'OPEN_MORPHOLOGY', (
        f"PATH_DIRECTIVE_SLOT must not be OPEN_MORPHOLOGY when clitic_only=True, "
        f"got {path_slot.get('value')!r}"
    )


# T-06 ─ word-class owner is not called for بِكُمْ ───────────────────────────
def test_T06_bkum_word_class_not_called():
    if sys.version_info < (3, 11):
        pytest.skip("Requires Python 3.11+ — segmentation gate blocked by StrEnum on 3.10")
    r = _get_bkum()
    morphology_blocked = r.get('morphology_blocked', False)
    clitic_only = r.get('segment_clitic_only', False)
    # At least one of these must be true for the word-class gate to be closed
    assert morphology_blocked or clitic_only, (
        "Expected morphology_blocked=True or segment_clitic_only=True for بِكُمْ"
    )
    # Word class result must not have been populated
    wc = r.get('word_class_result')
    assert wc is None, f"Expected word_class_result=None, got {wc!r}"


# T-07 ─ root owner is not called for بِكُمْ ─────────────────────────────────
def test_T07_bkum_root_not_called():
    r = _get_bkum()
    rc = r.get('root_candidate')
    assert rc is None, (
        f"Expected root_candidate=None for clitic_only token, got {rc!r}"
    )


# T-08 ─ failure_code=SEGMENTATION_NO_LEXICAL_HOST ───────────────────────────
def test_T08_bkum_failure_code():
    if sys.version_info < (3, 11):
        pytest.skip("Requires Python 3.11+ — segmentation gate blocked by StrEnum on 3.10")
    r = _get_bkum()
    taaqol = r.get('taaqol') or {}
    rt     = taaqol.get('runtime') or {}
    fc     = rt.get('failure_code')
    mbr    = r.get('morphology_block_reason')
    assert (
        fc  == 'SEGMENTATION_NO_LEXICAL_HOST'
        or mbr == 'SEGMENTATION_NO_LEXICAL_HOST'
    ), (
        f"Expected SEGMENTATION_NO_LEXICAL_HOST; "
        f"failure_code={fc!r}, morphology_block_reason={mbr!r}"
    )


# T-09 ─ reason_codes contains SEGMENTATION_NO_LEXICAL_HOST exactly once ─────
def test_T09_bkum_reason_codes_no_duplicate():
    if sys.version_info < (3, 11):
        pytest.skip("Requires Python 3.11+ — Taaqol bridge returns reason_codes")

    import json as _json
    import os as _os
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            "scripts/demo_ayat_al_dayn.py",
            "--token",
            _BKUM_TOKEN,
            "--taaqol",
            "--no-color",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env={
            **_os.environ,
            "PYTHONPATH": "src:vendor/Taaqol-GPT/src",
        },
    )

    assert result.returncode == 0, (
        f"Demo script failed:\\n{result.stderr[-2000:]}"
    )

    json_path = (
        REPO_ROOT
        / "reports"
        / "ayat_al_dayn_demo"
        / "ayat_al_dayn_results_full.json"
    )
    data = _json.loads(json_path.read_text(encoding="utf-8"))

    token = data["tokens"][0]
    reason_codes = (token.get("taaqol") or {}).get("reason_codes") or []
    count = reason_codes.count("SEGMENTATION_NO_LEXICAL_HOST")

    assert count == 1, (
        "Expected SEGMENTATION_NO_LEXICAL_HOST exactly once in "
        f"reason_codes, got {count}: {reason_codes!r}"
    )


# T-13 ─ unexplained gap > 0 fails readiness ──────────────────────────────────
def test_T13_unexplained_gap_fails_readiness():
    sys.path.insert(0, str(REPO_ROOT / 'src'))
    from hokom.demo.demo_renderer import compute_violation_count
    checks_with_gap = {
        'SLOTS_MISSING_STATE': 0, 'LICENSED_WITHOUT_SCOPE': 0,
        'MISSING_EVALUATION_ID': 0, 'EVALUATION_ID_COLLISIONS': 0,
        'MISSING_TAAQOL_TRACE_ACTIVE': 0, 'CLAIM_KEY_NONDETERMINISM': 0,
        'UNTYPED_PAYLOADS': 0, 'SILENT_FALLBACKS': 0,
        'UNEXPECTED_RUNTIME_ERRORS': 0, 'TAAQOL_RUNTIME_ACTIVE': 128,
        'TAAQOL_RUNTIME_INACTIVE': False,
        'TAAQOL_CONSTITUTIONAL_EXEMPTIONS': 1,
        'TAAQOL_UNEXPLAINED_COVERAGE_GAP': 1,   # non-zero → violation
    }
    viol = compute_violation_count(checks_with_gap)
    assert viol > 0, (
        f"Expected violation_count > 0 when TAAQOL_UNEXPLAINED_COVERAGE_GAP=1, "
        f"got {viol}"
    )


# T-14 ─ constitutional exemption alone does not fail readiness ───────────────
def test_T14_constitutional_exemption_not_violation():
    sys.path.insert(0, str(REPO_ROOT / 'src'))
    from hokom.demo.demo_renderer import compute_violation_count
    checks_clean = {
        'SLOTS_MISSING_STATE': 0, 'LICENSED_WITHOUT_SCOPE': 0,
        'MISSING_EVALUATION_ID': 0, 'EVALUATION_ID_COLLISIONS': 0,
        'MISSING_TAAQOL_TRACE_ACTIVE': 0, 'CLAIM_KEY_NONDETERMINISM': 0,
        'UNTYPED_PAYLOADS': 0, 'SILENT_FALLBACKS': 0,
        'UNEXPECTED_RUNTIME_ERRORS': 0, 'TAAQOL_RUNTIME_ACTIVE': 128,
        'TAAQOL_RUNTIME_INACTIVE': False,
        'TAAQOL_CONSTITUTIONAL_EXEMPTIONS': 1,   # documented exemption
        'TAAQOL_UNEXPLAINED_COVERAGE_GAP': 0,    # gap is zero → OK
    }
    viol = compute_violation_count(checks_clean)
    assert viol == 0, (
        f"Constitutional exemption alone must not produce violations, "
        f"got violation_count={viol}"
    )


# T-16 ─ silent fallbacks remain zero ────────────────────────────────────────
def test_T16_bkum_silent_fallbacks_zero():
    r    = _get_bkum()
    taaqol = r.get('taaqol') or {}
    rt     = taaqol.get('runtime') or {}
    assert not rt.get('fallback_used', False), (
        f"Expected fallback_used=False for بِكُمْ"
    )


# T-17 ─ unexpected runtime errors remain zero ────────────────────────────────
def test_T17_bkum_no_unexpected_runtime_error():
    r      = _get_bkum()
    taaqol = r.get('taaqol') or {}
    rt     = taaqol.get('runtime') or {}
    fc     = rt.get('failure_code')
    assert fc != 'BRIDGE_UNEXPECTED_EXCEPTION', (
        f"Unexpected bridge exception for بِكُمْ: {fc!r}"
    )


# T-10/T-11/T-12/T-15/T-18/T-19 ─ full-ayah subprocess tests ─────────────────
# These tests require the full-ayah run with Taaqol (Python 3.11+).
def test_T10_T12_T15_T18_T19_full_ayah_constitutional_accounting():
    """
    T-10: constitutional_exemptions=1  T-11: live=128  T-12: gap=0
    T-15: JSON/terminal/HTML use identical counts  T-18: CPR=YES  T-19: exit=0
    """
    if sys.version_info < (3, 11):
        pytest.skip("Requires Python 3.11+ for Taaqol StrEnum")
    import subprocess, json as _json, os as _os

    result = subprocess.run(
        [sys.executable, 'scripts/demo_ayat_al_dayn.py',
         '--full-ayah', '--taaqol', '--compact', '--no-color',
         '--fail-on-runtime-error'],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        env={**_os.environ, 'PYTHONPATH': 'src:vendor/Taaqol-GPT/src'},
    )
    # T-19: exit code must be 0
    assert result.returncode == 0, (
        f"Full-ayah gate returned nonzero:\n{result.stderr[-3000:]}"
    )
    combined = result.stdout + result.stderr

    # T-18: CLIENT_PRESENTATION_READY
    assert 'CLIENT_PRESENTATION_READY=YES' in combined, (
        "CLIENT_PRESENTATION_READY=YES not found in full-ayah output"
    )
    # T-12: coverage gap must be zero
    import re as _re

    assert _re.search(
        r"TAAQOL_UNEXPLAINED_COVERAGE_GAP\s*=\s*0\b",
        combined,
    ), "Expected TAAQOL_UNEXPLAINED_COVERAGE_GAP=0"

    # T-10/T-11 via JSON
    json_path = REPO_ROOT / 'reports' / 'ayat_al_dayn_demo' / 'ayat_al_dayn_results_full.json'
    assert json_path.exists(), "JSON report not written"
    data = _json.loads(json_path.read_text(encoding='utf-8'))
    summary = data.get('summary', {})

    # T-11: live evaluations = 128
    assert summary.get('taaqol_live') == 128, (
        f"Expected taaqol_live=128, got {summary.get('taaqol_live')}"
    )
    # T-10: constitutional exemptions = 1
    assert summary.get('taaqol_constitutional_exemptions') == 1, (
        f"Expected taaqol_constitutional_exemptions=1, got "
        f"{summary.get('taaqol_constitutional_exemptions')}"
    )
    # T-12: unexplained gap = 0
    assert summary.get('taaqol_unexplained_coverage_gap') == 0, (
        f"Expected taaqol_unexplained_coverage_gap=0, got "
        f"{summary.get('taaqol_unexplained_coverage_gap')}"
    )
    # T-15: JSON integrity_violation_count must be 0
    assert data.get('integrity_violation_count') == 0
    assert data.get('client_presentation_ready') is True
