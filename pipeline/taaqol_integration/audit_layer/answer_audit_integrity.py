"""Wave09 AnswerAudit live integrity measurement.

Phase F — every AnswerAudit-specific counter listed in the directive is
backed by either an AST/regex source scanner or a pure runtime
predicate over per-span :class:`AnswerAuditOutcome` records. No
decorative zeros. Mutation-proof tests live in
`tests/taaqol_integration/test_answer_audit_integrity.py`.

Reuses the machinery from
`pipeline/taaqol_integration/integrity_measurement.py` (Wave07's live
integrity framework) so the source-scan and mutation-proof discipline
is identical.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from pipeline.taaqol_integration.integrity_measurement import (
    RuntimeRecordRule,
    SourceAntiPatternRule,
    _NOSCAN_MARKER,
    scan_source_anti_patterns,
)


# ── Source anti-pattern rules for AnswerAudit-specific concerns ────────

_ANSWER_AUDIT_SOURCE_RULES: tuple[SourceAntiPatternRule, ...] = (
    SourceAntiPatternRule(
        counter_name="EXPECTED_AUDIT_RESULT_MAP_COUNT",
        pattern=r"\b(?:EXPECTED_AUDIT|AUDIT_RESULT_MAP|GPT_ANSWER_MAP|AUDIT_VERDICT_LOOKUP)\b",
        definition="Static dict mapping span identity → expected audit verdict in production code.",
    ),
    SourceAntiPatternRule(
        counter_name="EXACT_TEXT_AUDIT_BRANCH_COUNT",
        pattern=(
            r"(?:answer|prompt|response|provider_output)"
            r"\s*(?:==|!=)\s*[\"']"
        ),
        definition="Executable branch keyed on exact provider answer / prompt / response text.",
    ),
    SourceAntiPatternRule(
        counter_name="TOKEN_POSITION_AUDIT_BRANCH_COUNT",
        pattern=r"\b(?:audit_token_position|audit_token_index)\s*(?:==|!=)\s*['\"0-9]",
        definition="Audit branch keyed on token position of the input.",
    ),
    SourceAntiPatternRule(
        counter_name="SYNTHETIC_AUDIT_EVIDENCE_COUNT",
        pattern=r"\b(?:synthetic_audit_evidence|fabricated_audit_evidence|SYNTHETIC_AUDIT_EV)\b",
        definition="Manufactured audit evidence not derived from vendor output.",
    ),
    SourceAntiPatternRule(
        counter_name="DIRECT_AUDITED_ANSWER_CONSTRUCTION_COUNT",
        pattern="",  # AST-based
        definition="Direct constructor call of AuditedAnswer in Hokom production code.",
        ast_call_name_set=frozenset({"AuditedAnswer"}),
    ),
    SourceAntiPatternRule(
        counter_name="SILENT_PROVIDER_FALLBACK_COUNT",
        # Detect suspicious `except: ... return <success>` patterns.
        # Naive regex — a real defect would look like
        # `except Exception: return AuditedAnswer(...)` or
        # `except: return {"status": "OK"}`. We flag any bare
        # ``except`` clause in audit_layer/ (defensive; strongly
        # discouraged even where intentional).
        pattern=r"^\s*except\s*:",
        definition="Bare `except:` in audit-layer production code — potential silent fallback path.",
    ),
)


# ── Runtime rules over AnswerAudit per-span records ────────────────────

def _has_prompt_and_trace(rec: dict) -> bool:
    return bool(rec.get("prompt_fingerprint")) and bool(
        rec.get("predecessor_trace") or (rec.get("trace_ids") or [])
    )


def _provider_failure_as_success(rec: dict) -> bool:
    return bool(rec.get("integration_failure_code")) and bool(
        rec.get("accepted")
    )


def _malformed_output_as_success(rec: dict) -> bool:
    fc = rec.get("integration_failure_code") or ""
    return fc == "INTEGRATION_PROVIDER_MALFORMED_RESPONSE" and bool(
        rec.get("accepted")
    )


def _silent_provider_fallback(rec: dict) -> bool:
    # A per-record proxy: integration failure with no residual marker
    # AND no failure detail is silent (Hokom absorbed the failure
    # without naming it).
    fc = rec.get("integration_failure_code")
    if fc is None:
        return False
    residuals = rec.get("residual_ids", [])
    detail = rec.get("integration_failure_detail", "")
    return not residuals and not detail


def _audit_decision_without_trace(rec: dict) -> bool:
    # A completed native audit must carry trace_ids (predecessor trace
    # at minimum). An integration failure must also name the
    # predecessor_trace.
    return not (rec.get("trace_ids") or [])


def _audit_failure_without_code(rec: dict) -> bool:
    # If the record represents a non-accepted outcome AND no
    # failure_code AND no integration_failure_code — that's an
    # unnamed refusal.
    if rec.get("accepted"):
        return False
    fc = rec.get("failure_code") or rec.get("integration_failure_code")
    return not fc


def _audit_failure_without_residual_or_reason(rec: dict) -> bool:
    if rec.get("accepted"):
        return False
    residuals = rec.get("residual_ids") or []
    detail = rec.get("integration_failure_detail", "") or ""
    return not residuals and not detail.strip()


def _certificate_allowed(rec: dict) -> bool:
    return bool(rec.get("certificate_allowed"))


def _model_request_without_source_trace(rec: dict) -> bool:
    return bool(rec.get("prompt_fingerprint")) and not (
        rec.get("predecessor_trace")
    )


def _make_response_reuse_detector() -> Callable[[dict], bool]:
    """Stateful detector — flags duplicate response fingerprints across
    different span_ids in the SAME evaluation pass. Reset per snapshot."""
    seen: dict[str, set[str]] = {}

    def predicate(rec: dict) -> bool:
        fp = rec.get("response_fingerprint")
        sid = rec.get("span_id") or ""
        if not fp:
            return False
        span_set = seen.setdefault(fp, set())
        was_new = sid not in span_set
        span_set.add(sid)
        # A response fingerprint used by more than one distinct span_id
        # is reuse — flag every additional occurrence.
        return len(span_set) > 1 and not was_new is False and len(span_set) > 1

    return predicate


_ANSWER_AUDIT_RUNTIME_RULES: tuple[RuntimeRecordRule, ...] = (
    RuntimeRecordRule(
        "PROVIDER_FAILURE_AS_SUCCESS_COUNT",
        _provider_failure_as_success,
        "Records where integration_failure_code is set AND accepted=True.",
    ),
    RuntimeRecordRule(
        "MALFORMED_OUTPUT_AS_SUCCESS_COUNT",
        _malformed_output_as_success,
        "Records where malformed-response failure was somehow accepted.",
    ),
    RuntimeRecordRule(
        "SILENT_PROVIDER_FALLBACK_COUNT",
        _silent_provider_fallback,
        "Integration failure with neither residual marker nor detail.",
    ),
    RuntimeRecordRule(
        "AUDIT_DECISION_WITHOUT_TRACE_COUNT",
        _audit_decision_without_trace,
        "Any record without trace_ids.",
    ),
    RuntimeRecordRule(
        "AUDIT_FAILURE_WITHOUT_CODE_COUNT",
        _audit_failure_without_code,
        "Non-accepted record with neither vendor failure_code nor integration_failure_code.",
    ),
    RuntimeRecordRule(
        "AUDIT_FAILURE_WITHOUT_RESIDUAL_OR_REASON_COUNT",
        _audit_failure_without_residual_or_reason,
        "Non-accepted record with neither residuals nor failure_detail.",
    ),
    RuntimeRecordRule(
        "CERTIFICATE_ALLOWED_COUNT",
        _certificate_allowed,
        "Any record where certificate_allowed is True (constitutional violation).",
    ),
    RuntimeRecordRule(
        "MODEL_REQUEST_WITHOUT_SOURCE_TRACE_COUNT",
        _model_request_without_source_trace,
        "Record with a prompt fingerprint but no predecessor_trace.",
    ),
)


# ── Structural derivations ─────────────────────────────────────────────

def structural_counters(per_span_records: list[dict]) -> dict[str, int]:
    """Runtime-derived counters not fitting per-record predicate shape."""
    native_calls = 0
    seen_response_fps: dict[str, set[str]] = {}
    for rec in per_span_records:
        # Every wave09 per-span record represents one native AnswerAudit
        # adapter call. The native_result_type distinguishes
        # completed-audit (AuditedAnswer) from integration-failure
        # (NoneType).
        native_calls += 1
        fp = rec.get("response_fingerprint")
        sid = rec.get("span_id") or ""
        if fp:
            seen_response_fps.setdefault(fp, set()).add(sid)
    response_reuse = 0
    for fp, spans in seen_response_fps.items():
        if len(spans) > 1:
            response_reuse += len(spans) - 1  # count all reuses beyond first
    return {
        "ANSWER_AUDIT_NATIVE_CALL_COUNT": native_calls,
        "MODEL_RESPONSE_REUSE_COUNT": response_reuse,
    }


# ── Declared counter registry ──────────────────────────────────────────

ANSWER_AUDIT_DECLARED_COUNTERS: frozenset[str] = frozenset({
    # Source anti-pattern (6)
    "EXPECTED_AUDIT_RESULT_MAP_COUNT",
    "EXACT_TEXT_AUDIT_BRANCH_COUNT",
    "TOKEN_POSITION_AUDIT_BRANCH_COUNT",
    "SYNTHETIC_AUDIT_EVIDENCE_COUNT",
    "DIRECT_AUDITED_ANSWER_CONSTRUCTION_COUNT",
    "SILENT_PROVIDER_FALLBACK_COUNT",
    # Runtime typed-outcome (8)
    "PROVIDER_FAILURE_AS_SUCCESS_COUNT",
    "MALFORMED_OUTPUT_AS_SUCCESS_COUNT",
    "AUDIT_DECISION_WITHOUT_TRACE_COUNT",
    "AUDIT_FAILURE_WITHOUT_CODE_COUNT",
    "AUDIT_FAILURE_WITHOUT_RESIDUAL_OR_REASON_COUNT",
    "CERTIFICATE_ALLOWED_COUNT",
    "MODEL_REQUEST_WITHOUT_SOURCE_TRACE_COUNT",
    # Structural (2)
    "ANSWER_AUDIT_NATIVE_CALL_COUNT",
    "MODEL_RESPONSE_REUSE_COUNT",
})


def derive_answer_audit_runtime(
    per_span_records: list[dict],
) -> dict[str, dict[str, Any]]:
    """Apply per-record predicates; return counts + violating records."""
    result: dict[str, dict[str, Any]] = {
        rule.counter_name: {"count": 0, "violating_records": []}
        for rule in _ANSWER_AUDIT_RUNTIME_RULES
    }
    for rec in per_span_records:
        for rule in _ANSWER_AUDIT_RUNTIME_RULES:
            if rule.predicate(rec):
                entry = result[rule.counter_name]
                entry["count"] += 1
                if len(entry["violating_records"]) < 25:
                    entry["violating_records"].append({
                        "span_id": rec.get("span_id"),
                        "predecessor_type": rec.get("predecessor_type"),
                        "gate_state": rec.get("gate_state"),
                        "integration_failure_code": rec.get("integration_failure_code"),
                    })
    return result


def build_answer_audit_integrity_snapshot(
    source_roots: list[Path],
    per_span_records: list[dict],
) -> dict[str, Any]:
    """Emit the canonical AnswerAudit integrity snapshot for the ledger."""
    # NB: exclude the wave09 audit layer's own source files from
    # SILENT_PROVIDER_FALLBACK_COUNT scan by adding to extra_excludes
    # — the audit_layer legitimately catches provider exceptions.
    source_results = scan_source_anti_patterns(
        source_roots,
        list(_ANSWER_AUDIT_SOURCE_RULES),
    )
    runtime_results = derive_answer_audit_runtime(per_span_records)
    struct = structural_counters(per_span_records)

    counters: dict[str, int] = {}
    counter_evidence: dict[str, dict[str, Any]] = {}
    for name, entry in source_results.items():
        counters[name] = entry["count"]
        counter_evidence[name] = {
            "measurement_domain": "SOURCE_ANTI_PATTERN",
            "sites": entry["sites"],
        }
    for name, entry in runtime_results.items():
        counters[name] = entry["count"]
        counter_evidence[name] = {
            "measurement_domain": "RUNTIME_TYPED_OUTCOME",
            "violating_records": entry["violating_records"],
        }
    for name, val in struct.items():
        counters[name] = val
        counter_evidence[name] = {
            "measurement_domain": "STRUCTURAL_DERIVATION",
            "note": "derived from per-span records: native_calls counts records, response_reuse counts response fingerprint duplicates beyond first per fingerprint.",
        }

    measured = set(counters.keys())
    unmeasured = ANSWER_AUDIT_DECLARED_COUNTERS - measured
    return {
        "schema_version": "1.0.0",
        "counters": counters,
        "counter_evidence": counter_evidence,
        "meta": {
            "HARDCODED_ZERO_COUNTER_COUNT": len(unmeasured),
            "UNMEASURED_COUNTER_COUNT": len(unmeasured),
            "COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT": len(unmeasured),
        },
    }


__all__ = [
    "ANSWER_AUDIT_DECLARED_COUNTERS",
    "_ANSWER_AUDIT_SOURCE_RULES",
    "_ANSWER_AUDIT_RUNTIME_RULES",
    "structural_counters",
    "derive_answer_audit_runtime",
    "build_answer_audit_integrity_snapshot",
]
