"""Wave09 AnswerAudit integrity — baseline + mutation proofs.

Phase F required-zero invariants proven via:
* baseline: production tree + real 5-span chain yields zero for every counter;
* mutation proof: injecting a synthetic defect flips each counter non-zero.

No defect is committed to production; all mutation fixtures live only
in this test file.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.taaqol_integration.audit_layer.answer_audit_integrity import (
    ANSWER_AUDIT_DECLARED_COUNTERS,
    _ANSWER_AUDIT_RUNTIME_RULES,
    _ANSWER_AUDIT_SOURCE_RULES,
    build_answer_audit_integrity_snapshot,
    derive_answer_audit_runtime,
    structural_counters,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_ROOT = REPO_ROOT / "pipeline"


def _good_record(**overrides) -> dict:
    rec = {
        "span_id": "SPAN-1",
        "predecessor_type": "AuditedTanzilBridgeVerdict",
        "predecessor_trace": "bridge_tanzil_to_audit/surfaced",
        "prompt_fingerprint": "abc123",
        "response_fingerprint": "def456",
        "native_result_type": "AuditedAnswer",
        "gamma_state": "PERFORATED_CLOSED",
        "gate_state": "APPROVED",
        "verdict_state": "APPROVED",
        "failure_code": None,
        "rank": "HYPOTHESIS",
        "successor_present": True,
        "certificate_allowed": False,
        "reasonableness_status": "NOT_RUN",
        "trace_ids": ["trace://Q1"],
        "residual_ids": [],
        "integration_failure_code": None,
        "integration_failure_detail": "",
        "accepted": True,
        "output_fingerprint": "xyz789",
    }
    rec.update(overrides)
    return rec


# ── Baseline: production tree scan ─────────────────────────────────────

def test_baseline_production_source_scan_all_zero():
    """The production audit_layer/ must contain zero anti-pattern hits.

    Note: The audit_layer's exception-handling in the adapter is
    NOT bare-except — it's specific-type catches. The bare-except
    detector should fire only if we introduce a `except:` clause.
    """
    from pipeline.taaqol_integration.integrity_measurement import (
        scan_source_anti_patterns,
    )
    results = scan_source_anti_patterns(
        [PIPELINE_ROOT], list(_ANSWER_AUDIT_SOURCE_RULES),
    )
    for name, entry in results.items():
        assert entry["count"] == 0, (
            f"{name} nonzero on production tree: {entry['sites'][:5]}"
        )


def test_baseline_five_good_records_all_zero_runtime():
    """Five well-formed AnswerAudit records must trigger no violations."""
    per_span = [
        _good_record(span_id=f"SPAN-{i}",
                     prompt_fingerprint=f"p{i}",
                     response_fingerprint=f"r{i}",
                     output_fingerprint=f"o{i}")
        for i in range(5)
    ]
    results = derive_answer_audit_runtime(per_span)
    for name, entry in results.items():
        assert entry["count"] == 0, (
            f"{name} nonzero on baseline: {entry['violating_records']}"
        )
    struct = structural_counters(per_span)
    assert struct["ANSWER_AUDIT_NATIVE_CALL_COUNT"] == 5
    assert struct["MODEL_RESPONSE_REUSE_COUNT"] == 0


def test_declared_counters_all_have_measurement():
    """Every declared counter must be backed by source, runtime, or structural."""
    source_names = {r.counter_name for r in _ANSWER_AUDIT_SOURCE_RULES}
    runtime_names = {r.counter_name for r in _ANSWER_AUDIT_RUNTIME_RULES}
    structural_names = set(structural_counters([]).keys())
    measured = source_names | runtime_names | structural_names
    missing = ANSWER_AUDIT_DECLARED_COUNTERS - measured
    assert not missing, f"Declared but unmeasured: {sorted(missing)}"


# ── Mutation proofs — source scanners ──────────────────────────────────

@pytest.mark.parametrize("counter,pattern_text", [
    ("EXPECTED_AUDIT_RESULT_MAP_COUNT", "verdict = EXPECTED_AUDIT[span]\n"),
    ("EXACT_TEXT_AUDIT_BRANCH_COUNT", 'if answer == "yes":\n    pass\n'),
    ("TOKEN_POSITION_AUDIT_BRANCH_COUNT",
     "if audit_token_position == 3:\n    pass\n"),
    ("SYNTHETIC_AUDIT_EVIDENCE_COUNT", "e = synthetic_audit_evidence(span)\n"),
    ("DIRECT_AUDITED_ANSWER_CONSTRUCTION_COUNT",
     "a = AuditedAnswer(prompt='p', answer='a', gamma_state=None,\n"
     "  gate_state=None, failure_code=None, rank=None,\n"
     "  evidence_refs=(), residuals=(), residual_visibility=False,\n"
     "  successor=None, trace_anchor='t')\n"),
    ("SILENT_PROVIDER_FALLBACK_COUNT", "try:\n    x()\nexcept:\n    pass\n"),
])
def test_source_scanner_detects_injected_defect(
    tmp_path: Path, counter: str, pattern_text: str,
):
    from pipeline.taaqol_integration.integrity_measurement import (
        scan_source_anti_patterns,
    )
    defect = tmp_path / "wave09_defect_fixture.py"
    defect.write_text(f"# temp mutation fixture\n{pattern_text}",
                      encoding="utf-8")
    results = scan_source_anti_patterns(
        [tmp_path], list(_ANSWER_AUDIT_SOURCE_RULES),
    )
    assert results[counter]["count"] >= 1, (
        f"{counter} failed to detect injected defect:\n"
        f"pattern: {pattern_text!r}\n"
        f"sites: {results[counter]['sites']}"
    )


# ── Mutation proofs — runtime record rules ─────────────────────────────

def test_runtime_detects_provider_failure_as_success():
    rec = _good_record(
        integration_failure_code="INTEGRATION_PROVIDER_TIMEOUT",
        accepted=True,
    )
    results = derive_answer_audit_runtime([rec])
    assert results["PROVIDER_FAILURE_AS_SUCCESS_COUNT"]["count"] == 1


def test_runtime_detects_malformed_output_as_success():
    rec = _good_record(
        integration_failure_code="INTEGRATION_PROVIDER_MALFORMED_RESPONSE",
        accepted=True,
    )
    results = derive_answer_audit_runtime([rec])
    assert results["MALFORMED_OUTPUT_AS_SUCCESS_COUNT"]["count"] == 1


def test_runtime_detects_silent_provider_fallback():
    rec = _good_record(
        integration_failure_code="INTEGRATION_PROVIDER_TIMEOUT",
        integration_failure_detail="",
        residual_ids=[],
        accepted=False,
    )
    results = derive_answer_audit_runtime([rec])
    assert results["SILENT_PROVIDER_FALLBACK_COUNT"]["count"] == 1


def test_runtime_detects_audit_decision_without_trace():
    rec = _good_record(trace_ids=[])
    results = derive_answer_audit_runtime([rec])
    assert results["AUDIT_DECISION_WITHOUT_TRACE_COUNT"]["count"] == 1


def test_runtime_detects_audit_failure_without_code():
    rec = _good_record(
        accepted=False,
        failure_code=None,
        integration_failure_code=None,
    )
    results = derive_answer_audit_runtime([rec])
    assert results["AUDIT_FAILURE_WITHOUT_CODE_COUNT"]["count"] == 1


def test_runtime_detects_audit_failure_without_residual_or_reason():
    rec = _good_record(
        accepted=False,
        residual_ids=[],
        integration_failure_detail="",
    )
    results = derive_answer_audit_runtime([rec])
    assert results["AUDIT_FAILURE_WITHOUT_RESIDUAL_OR_REASON_COUNT"]["count"] == 1


def test_runtime_detects_certificate_allowed():
    rec = _good_record(certificate_allowed=True)
    results = derive_answer_audit_runtime([rec])
    assert results["CERTIFICATE_ALLOWED_COUNT"]["count"] == 1


def test_runtime_detects_model_request_without_source_trace():
    rec = _good_record(predecessor_trace="")
    results = derive_answer_audit_runtime([rec])
    assert results["MODEL_REQUEST_WITHOUT_SOURCE_TRACE_COUNT"]["count"] == 1


def test_structural_detects_response_reuse():
    """Two records with identical response_fingerprint but different
    span_id → MODEL_RESPONSE_REUSE_COUNT = 1."""
    per_span = [
        _good_record(span_id="S1", response_fingerprint="shared"),
        _good_record(span_id="S2", response_fingerprint="shared"),
    ]
    struct = structural_counters(per_span)
    assert struct["MODEL_RESPONSE_REUSE_COUNT"] == 1


# ── End-to-end: snapshot on real 5-span chain ──────────────────────────

def test_end_to_end_snapshot_on_real_five_span_chain_all_zero():
    """The full integrity snapshot over the real Ayat 5-span chain
    must report zero for every declared counter and all-zero meta."""
    from tests.taaqol_integration.test_c13_wave03_relation_closure import (
        _run_full_ayat_and_produce_spans,
    )
    from pipeline.taaqol_integration.audit_layer.wave09_answer_audit_chain import (
        execute_wave09_answer_audit_chain,
    )
    cu, sp = _run_full_ayat_and_produce_spans()
    result = execute_wave09_answer_audit_chain(cu, sp)
    per_span = result["answer_audit_per_span"]
    snap = build_answer_audit_integrity_snapshot([PIPELINE_ROOT], per_span)
    for name in ANSWER_AUDIT_DECLARED_COUNTERS:
        obs = snap["counters"].get(name)
        if name == "ANSWER_AUDIT_NATIVE_CALL_COUNT":
            assert obs == 5, f"{name} = {obs} (expected 5)"
        else:
            assert obs == 0, (
                f"{name} nonzero on real 5-span: "
                f"{snap['counter_evidence'][name]}"
            )
    assert snap["meta"]["HARDCODED_ZERO_COUNTER_COUNT"] == 0
    assert snap["meta"]["UNMEASURED_COUNTER_COUNT"] == 0
    assert snap["meta"]["COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT"] == 0
