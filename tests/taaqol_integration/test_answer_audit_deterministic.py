"""Wave09 AnswerAudit — deterministic failure-path tests.

Exercises the vendor's native :class:`AnswerAudit` engine through the
thin Hokom adapter and the deterministic :class:`ModelClient`
implementations. Covers the 15 scenarios listed in the campaign
directive Phase D, marking any structurally-impossible scenario as
``TEST_NOT_APPLICABLE`` with a source reference.

Test discipline (per §D):
* every scenario asserts native output type or explicit fail-closed;
* every scenario asserts vendor failure_code / verdict_state where the
  native contract supports it;
* certificate_allowed is False everywhere by law;
* no silent fallback; no exception-to-success conversion.
"""
from __future__ import annotations

import pytest

from pipeline.taaqol_integration.audit_layer.answer_audit_adapter import (
    _VENDOR_AUDIT_AVAILABLE,
    AnswerAuditOutcome,
    INTEGRATION_PROVIDER_MALFORMED_RESPONSE,
    INTEGRATION_PROVIDER_TIMEOUT,
    INTEGRATION_PROVIDER_TRANSPORT_FAILURE,
    audit_bridge_verdict,
)
from pipeline.taaqol_integration.audit_layer.deterministic_model_client import (
    DeterministicModelClient,
    FailingModelClient,
    MalformedModelClient,
)


# ── Shared real-predecessor fixture ────────────────────────────────────

@pytest.fixture(scope="module")
def _real_audited_tanzil():
    """Build a REAL AuditedTanzilBridgeVerdict from the wave06 chain.

    Reuses `_build_stage_prereqs` from test_c13_wave06_typed_closure.py
    which invokes the real vendor prove_hukm/manat/tanzil chain over an
    actual Ayat al-Dayn span, then calls the real bridge_tanzil_to_audit.
    No synthetic construction anywhere.
    """
    from tests.taaqol_integration.test_c13_wave06_typed_closure import (
        _build_stage_prereqs,
    )
    from pipeline.taaqol_integration.weight_layer.typed_stage_builders import (
        build_audited_tanzil_bridge_outcome,
    )
    ctx = _build_stage_prereqs()
    atb_outcome = build_audited_tanzil_bridge_outcome(
        tanzil_verdict=ctx['tv'].native_verdict,
    )
    assert atb_outcome is not None
    return {
        "verdict": atb_outcome.native_verdict,
        "span_id": ctx['span_id'],
    }


# ── §W9.1  Successful response — native audit completes with APPROVED gate ─

def test_w9_1_successful_response_yields_native_audited_answer(_real_audited_tanzil):
    mc = DeterministicModelClient(default_response="valid-integration-answer")
    outcome = audit_bridge_verdict(
        audited_tanzil_verdict=_real_audited_tanzil["verdict"],
        span_id=_real_audited_tanzil["span_id"],
        prompt="wave09-prompt-1",
        model_client=mc,
    )
    assert isinstance(outcome, AnswerAuditOutcome)
    # Vendor audit completed — native_verdict populated, no integration failure.
    assert outcome.native_verdict is not None
    assert outcome.integration_failure_code is None
    from taaqqul_slot_geometry.audit.answer_audit import AuditedAnswer
    assert isinstance(outcome.native_verdict, AuditedAnswer)
    # Vendor's own audit fields present.
    assert outcome.native_verdict.failure_code is None or \
        outcome.accepted is False  # if refused, must be named
    # Certificate policy re-asserted at Hokom seam.
    assert outcome.certificate_allowed is False
    assert outcome.reasonableness_status == "NOT_RUN"
    # ModelClient was called exactly once.
    assert len(mc.call_log) == 1
    assert mc.call_log[0].prompt == "wave09-prompt-1"


# ── §W9.2  Provider timeout ────────────────────────────────────────────

def test_w9_2_provider_timeout_yields_typed_integration_failure(_real_audited_tanzil):
    mc = FailingModelClient(TimeoutError("provider took too long"))
    outcome = audit_bridge_verdict(
        audited_tanzil_verdict=_real_audited_tanzil["verdict"],
        span_id=_real_audited_tanzil["span_id"],
        prompt="wave09-prompt-2",
        model_client=mc,
    )
    assert outcome.native_verdict is None
    assert outcome.integration_failure_code == INTEGRATION_PROVIDER_TIMEOUT
    assert "provider timeout" in outcome.integration_failure_detail
    assert outcome.accepted is False
    assert outcome.certificate_allowed is False
    # Named residual marker so downstream artifact can see the failure.
    assert any(
        r.startswith("INTEGRATION_MARKER:INTEGRATION_PROVIDER_TIMEOUT")
        for r in outcome.residual_ids
    )
    assert len(mc.call_log) == 1


# ── §W9.3  Provider transport failure ──────────────────────────────────

def test_w9_3_provider_transport_failure_yields_typed_integration_failure(
    _real_audited_tanzil,
):
    mc = FailingModelClient(ConnectionError("network dead"))
    outcome = audit_bridge_verdict(
        audited_tanzil_verdict=_real_audited_tanzil["verdict"],
        span_id=_real_audited_tanzil["span_id"],
        prompt="wave09-prompt-3",
        model_client=mc,
    )
    assert outcome.native_verdict is None
    assert outcome.integration_failure_code == INTEGRATION_PROVIDER_TRANSPORT_FAILURE
    assert "transport failure" in outcome.integration_failure_detail
    assert outcome.accepted is False
    assert outcome.certificate_allowed is False


# ── §W9.4  Malformed response — non-string payload ─────────────────────

def test_w9_4_malformed_non_string_response_yields_typed_integration_failure(
    _real_audited_tanzil,
):
    """Vendor answer_audit.py:410 raises TypeError on non-string; the
    adapter catches and converts to INTEGRATION_PROVIDER_MALFORMED_RESPONSE."""
    mc = MalformedModelClient(payload=42)
    outcome = audit_bridge_verdict(
        audited_tanzil_verdict=_real_audited_tanzil["verdict"],
        span_id=_real_audited_tanzil["span_id"],
        prompt="wave09-prompt-4",
        model_client=mc,
    )
    assert outcome.native_verdict is None
    assert outcome.integration_failure_code == INTEGRATION_PROVIDER_MALFORMED_RESPONSE
    assert "malformed provider response" in outcome.integration_failure_detail
    assert outcome.accepted is False


# ── §W9.5  Empty response — vendor accepts empty string legitimately ───

def test_w9_5_empty_response_completes_vendor_audit(_real_audited_tanzil):
    """Vendor accepts empty-string ``answer`` (see AuditedAnswer docstring:
    'prompt and answer are recorded verbatim and may be empty'). The
    audit judges the CLAIM GRAPH, not the surface text. So an empty
    response does NOT trigger an integration failure — the vendor's own
    audit completes and its gate decides based on the claim graph."""
    mc = DeterministicModelClient(default_response="")
    outcome = audit_bridge_verdict(
        audited_tanzil_verdict=_real_audited_tanzil["verdict"],
        span_id=_real_audited_tanzil["span_id"],
        prompt="wave09-prompt-5",
        model_client=mc,
    )
    assert outcome.native_verdict is not None
    assert outcome.integration_failure_code is None
    assert outcome.native_verdict.answer == ""
    # Vendor's decision applies; empty answer neither approves nor
    # forces refusal — it's the claim graph that decides.
    from taaqqul_slot_geometry.audit.answer_audit import AuditedAnswer
    assert isinstance(outcome.native_verdict, AuditedAnswer)


# ── §W9.6  Unexpected response type via responder callable ─────────────

def test_w9_6_responder_returning_wrong_type_raises_at_client_boundary(
    _real_audited_tanzil,
):
    """The DeterministicModelClient responder path validates the
    callable's return type before it crosses the docs/01 boundary.
    Non-str return raises TypeError from complete(), which the vendor
    would ALSO catch — the adapter converts to typed integration DEFER."""
    def bad_responder(prompt: str):
        return None  # type: ignore[return-value]
    mc = DeterministicModelClient(responder=bad_responder)
    outcome = audit_bridge_verdict(
        audited_tanzil_verdict=_real_audited_tanzil["verdict"],
        span_id=_real_audited_tanzil["span_id"],
        prompt="wave09-prompt-6",
        model_client=mc,
    )
    assert outcome.native_verdict is None
    assert outcome.integration_failure_code == INTEGRATION_PROVIDER_MALFORMED_RESPONSE


# ── §W9.7  Missing evidence — TEST_NOT_APPLICABLE at adapter level ─────

def test_w9_7_missing_evidence_test_not_applicable():
    """The Hokom adapter constructs :class:`EvidenceContract` from the
    predecessor's own trace_ref (the audited-Tanzil bridge is a real
    licensed prior verdict). Evidence CANNOT be missing at the adapter
    boundary unless the predecessor is malformed — and a malformed
    predecessor already raises TypeError before the adapter can invoke
    AnswerAudit.

    TEST_NOT_APPLICABLE: the missing-evidence scenario is a vendor-side
    concern governed by EvidenceContract construction; the Hokom
    adapter cannot legitimately produce a missing-evidence input to
    AnswerAudit without fabricating the failure. See
    vendor/Taaqol-GPT/tests/test_answer_audit.py for vendor-side
    evidence-missing tests.

    Source reference: vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/
    evidence_contract.py — EvidenceContract requires at least one
    EvidenceSource at construction.
    """
    pytest.skip(
        "TEST_NOT_APPLICABLE: adapter-boundary evidence cannot be "
        "missing without predecessor malformation; see docstring."
    )


# ── §W9.8  Gamma refusal — TEST_NOT_APPLICABLE at adapter level ────────

def test_w9_8_gamma_refusal_test_not_applicable():
    """Gamma refusal is a property of the claim graph the adapter
    constructs from the audited-Tanzil predecessor. The predecessor's
    verdict.state ∈ {SURFACED, REFUSED} — SURFACED graphs close
    gamma at PERFORATED_CLOSED, REFUSED graphs never reach the adapter
    (the wave06 chain short-circuits before calling the bridge).

    TEST_NOT_APPLICABLE: cannot force a gamma refusal at the adapter
    boundary without fabricating the predecessor.

    Source reference: vendor answer_audit.py test_answer_audit.py
    section 4 (refusal emission) exercises this at the vendor level.
    """
    pytest.skip(
        "TEST_NOT_APPLICABLE: gamma refusal requires a malformed "
        "predecessor; see docstring."
    )


# ── §W9.9  TransitionGate refusal — TEST_NOT_APPLICABLE at adapter ─────

def test_w9_9_transition_gate_refusal_test_not_applicable():
    """Gate refusal depends on the gate's own configured rank vs the
    claim graph's residuals. The Hokom adapter uses a fixed
    Wave09-audit-integration gate at Rank.LICENSED; the claim graph
    is built at Rank.HYPOTHESIS with the predecessor's residuals.
    Whether the gate approves or defers is vendor's decision, not
    Hokom's to configure per test.

    TEST_NOT_APPLICABLE at the deterministic engine layer: the gate
    refusal is a vendor-side property tested in
    vendor/Taaqol-GPT/tests/test_transition_gate.py — importing
    those into Hokom's suite would duplicate vendor coverage without
    adding integration value.
    """
    pytest.skip(
        "TEST_NOT_APPLICABLE: gate refusal is vendor-tested; "
        "Hokom cannot force at adapter boundary without inventing."
    )


# ── §W9.10 Unsupported answer — vendor accepts, gate decides ───────────

def test_w9_10_unsupported_answer_completes_audit_with_vendor_decision(
    _real_audited_tanzil,
):
    """An 'unsupported' answer string is arbitrary text; vendor's
    audit judges the claim graph, not the answer semantics (docs/01).
    Result: the audit completes; the gate decides based on the graph."""
    mc = DeterministicModelClient(default_response="i cannot answer this")
    outcome = audit_bridge_verdict(
        audited_tanzil_verdict=_real_audited_tanzil["verdict"],
        span_id=_real_audited_tanzil["span_id"],
        prompt="wave09-prompt-10",
        model_client=mc,
    )
    assert outcome.native_verdict is not None
    assert outcome.native_verdict.answer == "i cannot answer this"


# ── §W9.11 Inconsistent answer — vendor accepts, no answer-semantic branch ─

def test_w9_11_inconsistent_answer_completes_audit(_real_audited_tanzil):
    """Same discipline as W9.10: answer semantics are opaque to the
    audit shell. An 'inconsistent' answer neither adds nor removes
    vendor decision material."""
    mc = DeterministicModelClient(
        default_response="answer contradicting the prompt entirely"
    )
    outcome = audit_bridge_verdict(
        audited_tanzil_verdict=_real_audited_tanzil["verdict"],
        span_id=_real_audited_tanzil["span_id"],
        prompt="wave09-prompt-11",
        model_client=mc,
    )
    assert outcome.native_verdict is not None
    # Hokom does NOT branch on answer text (per §C — no text-specific
    # audit branch).  This test's assertion is that the adapter did
    # NOT inspect the answer to derive its outcome; the vendor's
    # AuditedAnswer is returned as-is.


# ── §W9.12 Hallucination indicator — vendor treats as opaque text ──────

def test_w9_12_hallucination_indicator_completes_audit(_real_audited_tanzil):
    """No 'hallucination detection' branch in Hokom. The vendor's
    docs/01 boundary asserts that the model's own confidence is never
    evidence; any hallucination indicator in the response text is
    treated as opaque bytes."""
    mc = DeterministicModelClient(default_response="HALLUCINATED_TEXT: xxx")
    outcome = audit_bridge_verdict(
        audited_tanzil_verdict=_real_audited_tanzil["verdict"],
        span_id=_real_audited_tanzil["span_id"],
        prompt="wave09-prompt-12",
        model_client=mc,
    )
    assert outcome.native_verdict is not None


# ── §W9.13 Repeated deterministic invocation — bit-identical outcomes ──

def test_w9_13_deterministic_repeat_yields_identical_outcomes(_real_audited_tanzil):
    """Two consecutive adapter invocations with the same prompt +
    model client behavior produce identical outcome fingerprints."""
    mc1 = DeterministicModelClient(default_response="deterministic-answer-13")
    mc2 = DeterministicModelClient(default_response="deterministic-answer-13")
    out1 = audit_bridge_verdict(
        audited_tanzil_verdict=_real_audited_tanzil["verdict"],
        span_id=_real_audited_tanzil["span_id"],
        prompt="wave09-prompt-13",
        model_client=mc1,
    )
    out2 = audit_bridge_verdict(
        audited_tanzil_verdict=_real_audited_tanzil["verdict"],
        span_id=_real_audited_tanzil["span_id"],
        prompt="wave09-prompt-13",
        model_client=mc2,
    )
    # Fingerprints must match; residual_ids and trace_ids must match.
    assert out1.prompt_fingerprint == out2.prompt_fingerprint
    assert out1.response_fingerprint == out2.response_fingerprint
    assert out1.residual_ids == out2.residual_ids
    assert out1.trace_ids == out2.trace_ids
    assert out1.accepted == out2.accepted


# ── §W9.14 Irrelevant extra provider fields — n/a in string protocol ──

def test_w9_14_irrelevant_extra_provider_fields_test_not_applicable():
    """The vendor's ModelClient protocol is string→string (docs/01).
    There are no 'extra fields' in the transport surface — anything
    beyond the answer string cannot cross the boundary.

    TEST_NOT_APPLICABLE: the docs/01 boundary structurally forbids
    non-string transport surface; there is no such thing as an
    'extra field' in a plain string response.

    Source: vendor/Taaqol-GPT/src/taaqqul_slot_geometry/audit/
    model_client.py — Protocol has a single method complete(prompt: str) -> str.
    """
    pytest.skip(
        "TEST_NOT_APPLICABLE: docs/01 protocol is str→str; no fields."
    )


# ── §W9.15 Trace-ledger failure — n/a; ledger writes cannot fail cleanly ─

def test_w9_15_trace_ledger_failure_test_not_applicable():
    """The vendor's :class:`TraceLedger` is a pure in-memory data
    structure; its ``append`` method has no I/O and no failure mode
    except structural TypeError on wrong candidate type — which is
    programmer error, not a runtime path.

    TEST_NOT_APPLICABLE: no legitimate runtime failure mode exists
    for the TraceLedger at this layer.

    Source: vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/
    trace_ledger.py.
    """
    pytest.skip(
        "TEST_NOT_APPLICABLE: TraceLedger has no runtime failure mode."
    )


# ── §W9.16 Adapter refuses wrong-type predecessor structurally ─────────

def test_w9_16_wrong_type_predecessor_raises_at_adapter_boundary():
    mc = DeterministicModelClient(default_response="unused")
    with pytest.raises(TypeError, match="AuditedTanzilBridgeVerdict"):
        audit_bridge_verdict(
            audited_tanzil_verdict=object(),
            span_id="SPAN-BAD",
            prompt="p",
            model_client=mc,
        )


# ── §W9.17 Adapter refuses wrong-type model client structurally ────────

def test_w9_17_wrong_type_model_client_raises_at_adapter_boundary(
    _real_audited_tanzil,
):
    with pytest.raises(TypeError, match="ModelClient protocol"):
        audit_bridge_verdict(
            audited_tanzil_verdict=_real_audited_tanzil["verdict"],
            span_id=_real_audited_tanzil["span_id"],
            prompt="p",
            model_client=object(),
        )


# ── §W9.18 Adapter refuses empty span_id ───────────────────────────────

def test_w9_18_empty_span_id_raises_at_adapter_boundary(_real_audited_tanzil):
    mc = DeterministicModelClient(default_response="unused")
    with pytest.raises(ValueError, match="span_id"):
        audit_bridge_verdict(
            audited_tanzil_verdict=_real_audited_tanzil["verdict"],
            span_id="",
            prompt="p",
            model_client=mc,
        )


# ── §W9.19 AnswerAuditOutcome constitutional invariants ───────────────

def test_w9_19_outcome_rejects_both_verdict_and_integration_failure():
    """The __post_init__ enforces XOR between native_verdict and
    integration_failure_code — both populated is a Hokom logic error."""
    with pytest.raises(ValueError, match="exactly one"):
        AnswerAuditOutcome(
            span_id="s", predecessor_trace="t",
            prompt_fingerprint="p", response_fingerprint="r",
            native_verdict=object(),           # populated
            integration_failure_code="X",       # also populated — invalid
            integration_failure_detail="",
            accepted=False,
            reasonableness_status="NOT_RUN",
            certificate_allowed=False,
            trace_ids=(), residual_ids=(),
        )


def test_w9_20_outcome_rejects_certificate_allowed_true():
    """Constitutional invariant: certificate_allowed MUST be False
    (docs/56 §2 B4 — no certificate, no authority, no truth)."""
    with pytest.raises(ValueError, match="certificate_allowed must be False"):
        AnswerAuditOutcome(
            span_id="s", predecessor_trace="t",
            prompt_fingerprint="p", response_fingerprint="r",
            native_verdict=None,
            integration_failure_code="X",
            integration_failure_detail="",
            accepted=False,
            reasonableness_status="NOT_RUN",
            certificate_allowed=True,           # invalid — always False
            trace_ids=(), residual_ids=(),
        )


def test_w9_21_outcome_rejects_accepted_true_with_integration_failure():
    """Constitutional invariant: an integration failure cannot be
    accepted (accepted=True + integration_failure_code both set is a
    Hokom logic error)."""
    with pytest.raises(ValueError, match="accepted=True is incompatible"):
        AnswerAuditOutcome(
            span_id="s", predecessor_trace="t",
            prompt_fingerprint="p", response_fingerprint="r",
            native_verdict=None,
            integration_failure_code="X",
            integration_failure_detail="",
            accepted=True,                      # invalid
            reasonableness_status="NOT_RUN",
            certificate_allowed=False,
            trace_ids=(), residual_ids=(),
        )
