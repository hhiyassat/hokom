"""Wave09 real AnswerAudit vertical — 5 spans × native AuditedAnswer.

Verifies Phase E requirements: the AnswerAudit call must receive each
span's actual audited-Tanzil predecessor; no fixture replacement; no
predecessor bypass; no direct AuditedAnswer construction.
"""
from __future__ import annotations

import pytest

from tests.taaqol_integration.test_c13_wave03_relation_closure import (
    _run_full_ayat_and_produce_spans,
)
from pipeline.taaqol_integration.audit_layer.wave09_answer_audit_chain import (
    execute_wave09_answer_audit_chain,
)


@pytest.fixture(scope="module")
def _chain_result():
    cu, sp = _run_full_ayat_and_produce_spans()
    return execute_wave09_answer_audit_chain(cu, sp)


def test_w9_e1_real_answer_audit_span_count_is_five(_chain_result):
    """§E: REAL_ANSWER_AUDIT_SPAN_COUNT = 5."""
    assert _chain_result["vendor_available"] is True
    assert len(_chain_result["answer_audit_per_span"]) == 5


def test_w9_e2_native_answer_audit_call_count_is_five(_chain_result):
    """§E: NATIVE_ANSWER_AUDIT_CALL_COUNT = 5."""
    assert _chain_result["counters"]["answer_audit_native_call_count"] == 5


def test_w9_e3_unique_input_trace_count_is_five(_chain_result):
    """§E: UNIQUE_ANSWER_AUDIT_INPUT_TRACE_COUNT = 5.

    Each span's per-record has a unique prompt_fingerprint (deterministic
    per span_id) and unique response_fingerprint.
    """
    per_span = _chain_result["answer_audit_per_span"]
    prompt_fps = {r["prompt_fingerprint"] for r in per_span}
    response_fps = {r["response_fingerprint"] for r in per_span}
    assert len(prompt_fps) == 5, f"expected 5 unique prompts, got {prompt_fps}"
    assert len(response_fps) == 5, f"expected 5 unique responses"


def test_w9_e4_reused_result_object_count_is_zero(_chain_result):
    """§E: REUSED_ANSWER_AUDIT_RESULT_OBJECT_COUNT = 0.

    Every per-span record has a distinct output_fingerprint (derived
    from prompt+response+accepted+certificate).
    """
    per_span = _chain_result["answer_audit_per_span"]
    fingerprints = [r["output_fingerprint"] for r in per_span]
    assert len(set(fingerprints)) == 5, "output_fingerprints must all differ"


def test_w9_e5_predecessor_bypass_count_is_zero(_chain_result):
    """§E: PREDECESSOR_BYPASS_COUNT = 0.

    Every per-span record must name AuditedTanzilBridgeVerdict as
    predecessor_type — no bypass allowed.
    """
    per_span = _chain_result["answer_audit_per_span"]
    for r in per_span:
        assert r["predecessor_type"] == "AuditedTanzilBridgeVerdict", r
        # The predecessor_trace must reflect vendor's own bridge trace_ref.
        assert r["predecessor_trace"].startswith("bridge_tanzil_to_audit/"), r


def test_w9_e6_direct_audited_answer_construction_count_is_zero(_chain_result):
    """§E: DIRECT_AUDITED_ANSWER_CONSTRUCTION_COUNT = 0.

    Every native_result_type must be `AuditedAnswer` — the actual vendor
    dataclass name; anything else would indicate Hokom fabricated a
    surrogate.
    """
    per_span = _chain_result["answer_audit_per_span"]
    for r in per_span:
        assert r["native_result_type"] == "AuditedAnswer", r


def test_w9_e7_certificate_allowed_count_is_zero(_chain_result):
    """Constitutional invariant §F: CERTIFICATE_ALLOWED_COUNT = 0.

    docs/56 §2 B4 — no certificate, no authority, no truth.
    """
    per_span = _chain_result["answer_audit_per_span"]
    assert _chain_result["counters"]["answer_audit_certificate_allowed_count"] == 0
    for r in per_span:
        assert r["certificate_allowed"] is False, r


def test_w9_e8_all_spans_have_full_persistence_fields(_chain_result):
    """Every persisted per-span record must carry the fields §E requires."""
    required_fields = {
        "span_id", "predecessor_type", "predecessor_trace",
        "prompt_fingerprint", "response_fingerprint",
        "gamma_result", "gate_result",
        "native_result_type", "verdict_state", "failure_code",
        "trace_ids", "residual_ids",
        "certificate_allowed", "output_fingerprint",
    }
    for r in _chain_result["answer_audit_per_span"]:
        missing = required_fields - set(r.keys())
        assert not missing, f"span {r.get('span_id')} missing: {missing}"


def test_w9_e9_all_spans_successful_vendor_audit(_chain_result):
    """Real Ayat corpus + valid deterministic responses ⇒ vendor
    AnswerAudit completes for every span with an APPROVED gate."""
    per_span = _chain_result["answer_audit_per_span"]
    for r in per_span:
        assert r["gate_state"] == "APPROVED", r
        assert r["failure_code"] is None, r
        assert r["successor_present"] is True, r
        assert r["accepted"] is True, r


def test_w9_e10_deterministic_double_execution_produces_identical_output():
    """Two independent invocations of the wave09 chain must produce
    byte-identical per-span records (fingerprints, trace_ids, residuals)."""
    cu1, sp1 = _run_full_ayat_and_produce_spans()
    r1 = execute_wave09_answer_audit_chain(cu1, sp1)
    cu2, sp2 = _run_full_ayat_and_produce_spans()
    r2 = execute_wave09_answer_audit_chain(cu2, sp2)

    assert r1["counters"] == r2["counters"]

    def _key(rec):
        return (
            rec["span_id"], rec["prompt_fingerprint"],
            rec["response_fingerprint"], rec["gate_state"],
            rec["gamma_state"], rec["failure_code"],
            tuple(rec["trace_ids"]), tuple(rec["residual_ids"]),
            rec["output_fingerprint"],
        )

    for a, b in zip(r1["answer_audit_per_span"],
                    r2["answer_audit_per_span"]):
        assert _key(a) == _key(b), (
            f"Non-deterministic result for {a['span_id']}"
        )
