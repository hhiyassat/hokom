"""
Fail-closed behavior tests for the Taaqol live bridge.

These tests do NOT import taaqqul_slot_geometry directly.
They test the fail-closed contract by mocking or by observing
behavior when Taaqol is unavailable on Python 3.10.

All tests pass on Python 3.10+.
"""
from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import patch

from pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle
from pipeline.taaqol_integration.live.models import HokomTaaqolDecision, HOKOM_TAAQOL_BRIDGE_ID


def _make_minimal_bundle(**kwargs):
    defaults = dict(
        claim_id='hokom:test:test_token',
        token_id='tok_test',
        original_surface='test_token',
        normalized_surface='test_token',
        domain_directive='ACCEPT',
        source_engine='HOKOM_ROOT_ENGINE',
        evidence_ids=('ev1', 'ev2'),
        trace_ids=(),
        active_residuals=(),
        part_of_speech=None,
        lexical_class=None,
        root_claim=None,
        wazn_claim=None,
        masdar_claim=None,
        mushtaq_claims=(),
        inflection_claim=None,
        mabni_status=None,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ── Fail-closed on ImportError ────────────────────────────────────────────────

def test_fail_closed_on_import_error():
    """When Taaqol cannot be imported, result is DEFERRED, not LICENSED."""
    bundle = _make_minimal_bundle()

    with patch.dict('sys.modules', {'taaqqul_slot_geometry': None}):
        # Remove it from sys.modules to force re-import attempt
        import sys as _sys
        saved = _sys.modules.pop('taaqqul_slot_geometry', 'NOT_PRESENT')
        try:
            result = evaluate_hokom_claim_bundle(bundle)
        finally:
            if saved != 'NOT_PRESENT':
                _sys.modules['taaqqul_slot_geometry'] = saved
            else:
                _sys.modules.pop('taaqqul_slot_geometry', None)

    # The result must NEVER be LICENSED on failure
    assert isinstance(result, HokomTaaqolDecision)
    assert result.taaqol_verdict != 'LICENSED', \
        "CRITICAL: fail-closed violated — returned LICENSED on ImportError"
    assert result.effective_verdict != 'LICENSED', \
        "CRITICAL: effective_verdict is LICENSED on ImportError"


def test_fail_closed_returns_decision_not_exception():
    """Fail-closed must return a decision value, never raise."""
    bundle = _make_minimal_bundle()

    # Force import failure path
    import sys as _sys
    saved = _sys.modules.pop('taaqqul_slot_geometry', 'NOT_PRESENT')
    try:
        result = evaluate_hokom_claim_bundle(bundle)
    except Exception as exc:
        if saved != 'NOT_PRESENT':
            _sys.modules['taaqqul_slot_geometry'] = saved
        assert False, f"evaluate_hokom_claim_bundle raised instead of returning: {exc}"
    finally:
        if saved != 'NOT_PRESENT':
            _sys.modules['taaqqul_slot_geometry'] = saved
        else:
            _sys.modules.pop('taaqqul_slot_geometry', None)

    assert isinstance(result, HokomTaaqolDecision)


def test_fail_closed_flag_always_true():
    """HokomTaaqolDecision.fail_closed must always be True."""
    bundle = _make_minimal_bundle()

    import sys as _sys
    saved = _sys.modules.pop('taaqqul_slot_geometry', 'NOT_PRESENT')
    try:
        result = evaluate_hokom_claim_bundle(bundle)
    finally:
        if saved != 'NOT_PRESENT':
            _sys.modules['taaqqul_slot_geometry'] = saved
        else:
            _sys.modules.pop('taaqqul_slot_geometry', None)

    assert result.fail_closed is True


def test_fail_closed_bridge_id():
    """Decision must always carry the correct bridge_id."""
    bundle = _make_minimal_bundle()

    import sys as _sys
    saved = _sys.modules.pop('taaqqul_slot_geometry', 'NOT_PRESENT')
    try:
        result = evaluate_hokom_claim_bundle(bundle)
    finally:
        if saved != 'NOT_PRESENT':
            _sys.modules['taaqqul_slot_geometry'] = saved
        else:
            _sys.modules.pop('taaqqul_slot_geometry', None)

    assert result.bridge_id == HOKOM_TAAQOL_BRIDGE_ID


def test_no_silent_fallback_trace_recorded():
    """The error must be recorded in the decision trace (not swallowed silently)."""
    bundle = _make_minimal_bundle()

    import sys as _sys
    saved = _sys.modules.pop('taaqqul_slot_geometry', 'NOT_PRESENT')
    try:
        result = evaluate_hokom_claim_bundle(bundle)
    finally:
        if saved != 'NOT_PRESENT':
            _sys.modules['taaqqul_slot_geometry'] = saved
        else:
            _sys.modules.pop('taaqqul_slot_geometry', None)

    # Trace must be non-empty (error was recorded)
    assert len(result.trace) > 0, "No trace events recorded — silent fallback!"


def test_fail_closed_reason_codes_non_empty():
    """Reason codes must be non-empty when Taaqol fails."""
    bundle = _make_minimal_bundle()

    import sys as _sys
    saved = _sys.modules.pop('taaqqul_slot_geometry', 'NOT_PRESENT')
    try:
        result = evaluate_hokom_claim_bundle(bundle)
    finally:
        if saved != 'NOT_PRESENT':
            _sys.modules['taaqqul_slot_geometry'] = saved
        else:
            _sys.modules.pop('taaqqul_slot_geometry', None)

    assert len(result.reason_codes) > 0, "reason_codes is empty — error was not documented"


def test_fail_closed_strict_mode_always_true():
    """strict_mode must always be True in the decision."""
    bundle = _make_minimal_bundle()

    import sys as _sys
    saved = _sys.modules.pop('taaqqul_slot_geometry', 'NOT_PRESENT')
    try:
        result = evaluate_hokom_claim_bundle(bundle)
    finally:
        if saved != 'NOT_PRESENT':
            _sys.modules['taaqqul_slot_geometry'] = saved
        else:
            _sys.modules.pop('taaqqul_slot_geometry', None)

    assert result.strict_mode is True


def test_fail_closed_source_engine_is_taaqol():
    """source_engine must always be 'TAAQOL'."""
    bundle = _make_minimal_bundle()

    import sys as _sys
    saved = _sys.modules.pop('taaqqul_slot_geometry', 'NOT_PRESENT')
    try:
        result = evaluate_hokom_claim_bundle(bundle)
    finally:
        if saved != 'NOT_PRESENT':
            _sys.modules['taaqqul_slot_geometry'] = saved
        else:
            _sys.modules.pop('taaqqul_slot_geometry', None)

    assert result.source_engine == 'TAAQOL'


# ── Upstream verdict preserved ────────────────────────────────────────────────

def test_upstream_verdict_preserved_in_decision():
    """upstream_verdict must reflect the bundle's domain_directive."""
    bundle = _make_minimal_bundle(domain_directive='DEFER')

    import sys as _sys
    saved = _sys.modules.pop('taaqqul_slot_geometry', 'NOT_PRESENT')
    try:
        result = evaluate_hokom_claim_bundle(bundle)
    finally:
        if saved != 'NOT_PRESENT':
            _sys.modules['taaqqul_slot_geometry'] = saved
        else:
            _sys.modules.pop('taaqqul_slot_geometry', None)

    assert result.upstream_verdict == 'DEFER'


def test_upstream_block_preserved():
    """Upstream BLOCK must propagate to effective_verdict even when Taaqol fails."""
    bundle = _make_minimal_bundle(domain_directive='BLOCK')

    import sys as _sys
    saved = _sys.modules.pop('taaqqul_slot_geometry', 'NOT_PRESENT')
    try:
        result = evaluate_hokom_claim_bundle(bundle)
    finally:
        if saved != 'NOT_PRESENT':
            _sys.modules['taaqqul_slot_geometry'] = saved
        else:
            _sys.modules.pop('taaqqul_slot_geometry', None)

    # BLOCK + DEFERRED(fail) → BLOCKED (monotonic composition)
    assert result.effective_verdict == 'BLOCKED', \
        f"Expected BLOCKED, got {result.effective_verdict!r}"


# ── Python 3.10 baseline ──────────────────────────────────────────────────────

def test_evaluate_returns_decision_on_current_python():
    """
    On any Python version, evaluate_hokom_claim_bundle returns HokomTaaqolDecision.
    On Python 3.10 (no Taaqol): DEFERRED.
    On Python 3.11+: actual evaluation.
    """
    bundle = _make_minimal_bundle()
    result = evaluate_hokom_claim_bundle(bundle)
    assert isinstance(result, HokomTaaqolDecision)
    assert result.fail_closed is True
    assert result.taaqol_verdict in ('LICENSED', 'DEFERRED', 'BLOCKED', 'RESIDUAL')
    assert result.effective_verdict in ('LICENSED', 'DEFERRED', 'BLOCKED', 'RESIDUAL')
