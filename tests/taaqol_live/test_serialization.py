"""
HokomTaaqolDecision serialization tests.
No Taaqol import required — passes on Python 3.10+.
"""
from __future__ import annotations

import dataclasses
import json

from pipeline.taaqol_integration.live.models import (
    HOKOM_TAAQOL_BRIDGE_ID,
    HokomTaaqolDecision,
    HokomTaaqolTraceEvent,
)


def _make_sample_decision(**kwargs):
    trace = (
        HokomTaaqolTraceEvent(
            step='gamma_evaluation',
            component='Gamma',
            input_digest='abc123',
            output='MINIMALLY_CLOSED',
            strict_mode=True,
        ),
    )
    defaults = dict(
        bridge_id=HOKOM_TAAQOL_BRIDGE_ID,
        taaqol_commit='abc123def456',
        hokom_commit='def456abc123',
        strict_mode=True,
        slot_graph_digest='1234567890abcdef',
        gamma_result='MINIMALLY_CLOSED',
        transition_gate_result='APPROVED',
        taaqol_verdict='LICENSED',
        reason_codes=(),
        contradictions=(),
        residuals=(),
        trace=trace,
        upstream_verdict='ACCEPT',
        effective_verdict='LICENSED',
        fail_closed=True,
        source_engine='TAAQOL',
    )
    defaults.update(kwargs)
    return HokomTaaqolDecision(**defaults)


def test_to_dict_returns_dict():
    decision = _make_sample_decision()
    d = decision.to_dict()
    assert isinstance(d, dict)


def test_to_dict_contains_bridge_id():
    decision = _make_sample_decision()
    d = decision.to_dict()
    assert d['bridge_id'] == HOKOM_TAAQOL_BRIDGE_ID


def test_to_dict_contains_all_fields():
    decision = _make_sample_decision()
    d = decision.to_dict()
    expected_fields = {
        'bridge_id', 'taaqol_commit', 'hokom_commit', 'strict_mode',
        'slot_graph_digest', 'gamma_result', 'transition_gate_result',
        'taaqol_verdict', 'reason_codes', 'contradictions', 'residuals',
        'trace', 'upstream_verdict', 'effective_verdict', 'fail_closed',
        'source_engine',
    }
    missing = expected_fields - set(d.keys())
    assert not missing, f"Missing fields in to_dict(): {missing}"


def test_dataclasses_asdict_works():
    decision = _make_sample_decision()
    d = dataclasses.asdict(decision)
    assert isinstance(d, dict)
    assert d['bridge_id'] == HOKOM_TAAQOL_BRIDGE_ID


def test_json_serializable():
    """HokomTaaqolDecision must be JSON-serializable via to_dict()."""
    decision = _make_sample_decision()
    d = decision.to_dict()
    json_str = json.dumps(d)
    assert isinstance(json_str, str)
    assert len(json_str) > 0


def test_json_round_trip():
    """JSON round-trip preserves key fields."""
    decision = _make_sample_decision()
    d = decision.to_dict()
    json_str = json.dumps(d)
    d2 = json.loads(json_str)
    assert d2['bridge_id'] == HOKOM_TAAQOL_BRIDGE_ID
    assert d2['taaqol_verdict'] == 'LICENSED'
    assert d2['effective_verdict'] == 'LICENSED'
    assert d2['fail_closed'] is True
    assert d2['strict_mode'] is True


def test_decision_is_frozen():
    import pytest
    decision = _make_sample_decision()
    with pytest.raises((AttributeError, TypeError)):
        decision.taaqol_verdict = 'BLOCKED'  # type: ignore


def test_trace_events_serializable():
    """HokomTaaqolTraceEvent must be JSON-serializable."""
    event = HokomTaaqolTraceEvent(
        step='gamma_evaluation',
        component='Gamma',
        input_digest='abc',
        output='MINIMALLY_CLOSED',
        strict_mode=True,
    )
    d = dataclasses.asdict(event)
    json_str = json.dumps(d)
    assert '"gamma_evaluation"' in json_str


def test_deferred_decision_serializable():
    """DEFERRED decision (fail-closed) must also be JSON-serializable."""
    decision = _make_sample_decision(
        taaqol_verdict='DEFERRED',
        effective_verdict='DEFERRED',
        reason_codes=('TAAQOL_RUNTIME_UNAVAILABLE',),
        slot_graph_digest='UNAVAILABLE',
        gamma_result='UNAVAILABLE',
        transition_gate_result='UNAVAILABLE',
    )
    d = decision.to_dict()
    json_str = json.dumps(d)
    d2 = json.loads(json_str)
    assert d2['taaqol_verdict'] == 'DEFERRED'
    assert 'TAAQOL_RUNTIME_UNAVAILABLE' in d2['reason_codes']


def test_serialization_preserves_tuples_as_lists():
    """tuples become lists in JSON — that's expected."""
    decision = _make_sample_decision(
        reason_codes=('CODE_1', 'CODE_2'),
        residuals=('residual_1',),
    )
    d = decision.to_dict()
    json_str = json.dumps(d)
    d2 = json.loads(json_str)
    assert isinstance(d2['reason_codes'], list)
    assert 'CODE_1' in d2['reason_codes']
    assert 'CODE_2' in d2['reason_codes']
