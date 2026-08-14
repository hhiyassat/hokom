"""Wave08 dual-carrier bridge tests.

Verifies that Hokom's typed downstream outcomes convert cleanly into
vendor bc9d1ea's :class:`StageExecutionRecord` mirror, and that the
mirror surfaces any Hokom-side under-reporting at construction time
(vendor's ``__post_init__`` invariants).

Test map
--------
* §W8.1  vendor runtime is importable at the bumped pin
* §W8.2  ACCEPT outcome mirrors as EXECUTED with correct fields
* §W8.3  DEFER outcome mirrors as DEFERRED with remediation hint
* §W8.4  BLOCK outcome with known vendor FailureCode mirrors as BLOCKED
* §W8.5  BLOCK outcome with unmapped code degrades to DEFERRED with
        explicit downgrade hint (fail-open on vocab drift, not silent)
* §W8.6  Rule 4 violation (residuals_before > residuals_after) is
        rejected by vendor __post_init__ — construction raises
* §W8.7  Rule 7 violation (DEFERRED with empty remediation) is
        rejected by vendor __post_init__ — the bridge must always
        supply a hint on DEFER path
* §W8.8  Rule 8 satisfaction — BLOCKED has failure_code enum
* §W8.9  End-to-end mirror over the real Ayat corpus — every per-stage
        record round-trips without vendor rejection
"""
from __future__ import annotations

import pytest

from pipeline.taaqol_integration.vendor_execution_record_bridge import (
    _VENDOR_RUNTIME_AVAILABLE,
    _VENDOR_SHA,
    build_span_record_mirror,
    to_vendor_stage_record,
)

# CAPABILITY GUARD. The Wave08 dual-carrier bridge requires the vendor API
# `taaqqul_slot_geometry.runtime.execution_record`, introduced in the APPROVED
# Taaqol vendor bc9d1ea5 (governed upgrade, owner decision 2026-08-14; the prior
# 05c6668d is SUPERSEDED_APPROVED_BASELINE). With the bc9d1ea5 submodule
# initialized these tests RUN; the guard only skips in an environment where the
# vendor runtime is unavailable (e.g. submodule not initialized).
pytestmark = pytest.mark.skipif(
    not _VENDOR_RUNTIME_AVAILABLE,
    reason="vendor runtime.execution_record unavailable (bc9d1ea5 submodule not "
           "initialized?); run: git submodule update --init --recursive.",
)


def test_w8_1_vendor_runtime_importable_at_bumped_pin():
    assert _VENDOR_RUNTIME_AVAILABLE, (
        "vendor bc9d1ea+ runtime (taaqqul_slot_geometry.runtime) must be "
        "importable after the pin bump"
    )
    assert _VENDOR_SHA.startswith("bc9d1ea"), (
        f"bridge module _VENDOR_SHA should reflect bc9d1ea, "
        f"got {_VENDOR_SHA!r}"
    )


class _Outcome:
    def __init__(self, **kw):
        self.classification = kw.get("classification", "ACCEPT")
        self.stage = kw.get("stage", "hukm")
        self.failure_code = kw.get("failure_code")
        self.failure_detail = kw.get("failure_detail", "")
        self.residual_ids = kw.get("residual_ids", [])
        self.trace_ref = kw.get("trace_ref", "hukm/proven")


_DEFAULT = dict(
    run_id="test:run", corpus_id="test:corpus",
    span_id="SPAN-1", input_carrier_id="c:1:in",
    path_id="HokomSpanPath", predecessor_stage_id="ifadah",
)


def test_w8_2_accept_mirrors_as_executed():
    from taaqqul_slot_geometry.runtime.execution_record import StageTransitionState
    out = _Outcome(classification="ACCEPT", stage="hukm",
                   trace_ref="hukm/proven",
                   residual_ids=["EXPLANATORY:HUKM_NOT_AUTHORITY"])
    rec = to_vendor_stage_record(outcome=out, **_DEFAULT)
    assert rec.transition_state is StageTransitionState.EXECUTED
    assert rec.output_carrier_id is not None
    assert rec.output_carrier_id.endswith(":hukm:out")
    assert rec.stage_id == "HUKM"
    assert rec.span_id == "SPAN-1"
    assert rec.failure_code is None
    assert rec.trace_entry_id == "hukm/proven"


def test_w8_3_defer_mirrors_as_deferred_with_hint():
    from taaqqul_slot_geometry.runtime.execution_record import StageTransitionState
    out = _Outcome(classification="DEFER", stage="hukm",
                   failure_code="NO_HUKM_CLAIM",
                   failure_detail="failure_code=NO_HUKM_CLAIM",
                   trace_ref="prove_hukm/refused",
                   residual_ids=[])
    rec = to_vendor_stage_record(outcome=out, **_DEFAULT)
    assert rec.transition_state is StageTransitionState.DEFERRED
    assert rec.remediation_hints, "DEFER must supply remediation hint (rule 7)"
    assert "NO_HUKM_CLAIM" in rec.remediation_hints[0]
    assert rec.output_carrier_id is None  # DEFER emits no output carrier


def test_w8_4_block_with_known_failure_code_mirrors_as_blocked():
    from taaqqul_slot_geometry.runtime.execution_record import StageTransitionState
    from taaqqul_slot_geometry.core.failure_taxonomy import FailureCode
    out = _Outcome(classification="BLOCK", stage="mafhum",
                   failure_code="MANTUQ_BLOCKS_MAFHUM",
                   failure_detail="failure_code=MANTUQ_BLOCKS_MAFHUM",
                   trace_ref="prove_mafhum/refused",
                   residual_ids=[])
    rec = to_vendor_stage_record(outcome=out, **_DEFAULT)
    assert rec.transition_state is StageTransitionState.BLOCKED
    assert rec.failure_code is not None, "BLOCK must carry FailureCode (rule 8)"
    assert isinstance(rec.failure_code, FailureCode)
    assert rec.failure_code.value == "MANTUQ_BLOCKS_MAFHUM"


def test_w8_5_block_with_unmapped_code_downgrades_to_deferred():
    from taaqqul_slot_geometry.runtime.execution_record import StageTransitionState
    out = _Outcome(classification="BLOCK", stage="hukm",
                   failure_code="FAKE_UNKNOWN_BLOCK_CODE",
                   failure_detail="failure_code=FAKE_UNKNOWN_BLOCK_CODE",
                   trace_ref="hukm/refused",
                   residual_ids=[])
    rec = to_vendor_stage_record(outcome=out, **_DEFAULT)
    # Vendor FailureCode has no member "FAKE_UNKNOWN_BLOCK_CODE"; the
    # bridge downgrades to DEFERRED with an explicit hint rather than
    # silently synthesising an enum member.
    assert rec.transition_state is StageTransitionState.DEFERRED
    assert rec.failure_code is None
    assert any("downgraded_from_BLOCK" in h for h in rec.remediation_hints)


def test_w8_6_rule4_residual_monotonicity_enforced():
    """Constructing a record that violates rule 4 (residual deletion)
    must raise ValueError from vendor __post_init__."""
    from taaqqul_slot_geometry.runtime.execution_record import (
        StageExecutionRecord, StageApplicability, StageTransitionState,
    )
    from taaqqul_slot_geometry.core.rank_lattice import Rank
    with pytest.raises(ValueError, match="residuals_after must keep"):
        StageExecutionRecord(
            run_id="r", corpus_id="c", token_id=None, span_id="s",
            stage_id="HUKM", path_id="p", input_carrier_id="i",
            output_carrier_id="o",
            applicability=StageApplicability.APPLICABLE,
            transition_state=StageTransitionState.EXECUTED,
            evidence_refs=("e",),
            rank_before=Rank.ZERO, rank_after=Rank.ZERO,
            residuals_before=("HUKM_NOT_AUTHORITY", "MANAT_DEFERRED"),
            residuals_after=("HUKM_NOT_AUTHORITY",),  # dropped MANAT_DEFERRED
            identity_invariants_checked=("id",),
            trace_parent_ids=(),
            trace_entry_id="t",
            failure_code=None,
            remediation_hints=(),
            next_admissible_stage_ids=(),
            source_commit_sha="sha",
            registry_version="v",
            registry_hash="h",
        )


def test_w8_7_rule7_defer_requires_remediation():
    from taaqqul_slot_geometry.runtime.execution_record import (
        StageExecutionRecord, StageApplicability, StageTransitionState,
    )
    from taaqqul_slot_geometry.core.rank_lattice import Rank
    with pytest.raises(ValueError, match="deferred stage must include"):
        StageExecutionRecord(
            run_id="r", corpus_id="c", token_id=None, span_id="s",
            stage_id="HUKM", path_id="p", input_carrier_id="i",
            output_carrier_id=None,
            applicability=StageApplicability.APPLICABLE,
            transition_state=StageTransitionState.DEFERRED,
            evidence_refs=("e",),
            rank_before=Rank.ZERO, rank_after=Rank.ZERO,
            residuals_before=(), residuals_after=(),
            identity_invariants_checked=("id",),
            trace_parent_ids=(),
            trace_entry_id="t",
            failure_code=None,
            remediation_hints=(),  # empty on DEFER → violates rule 7
            next_admissible_stage_ids=(),
            source_commit_sha="sha",
            registry_version="v",
            registry_hash="h",
        )


def test_w8_8_rule8_block_requires_failure_code():
    from taaqqul_slot_geometry.runtime.execution_record import (
        StageExecutionRecord, StageApplicability, StageTransitionState,
    )
    from taaqqul_slot_geometry.core.rank_lattice import Rank
    with pytest.raises(ValueError, match="blocked stage must include failure_code"):
        StageExecutionRecord(
            run_id="r", corpus_id="c", token_id=None, span_id="s",
            stage_id="HUKM", path_id="p", input_carrier_id="i",
            output_carrier_id=None,
            applicability=StageApplicability.APPLICABLE,
            transition_state=StageTransitionState.BLOCKED,
            evidence_refs=("e",),
            rank_before=Rank.ZERO, rank_after=Rank.ZERO,
            residuals_before=(), residuals_after=(),
            identity_invariants_checked=("id",),
            trace_parent_ids=(),
            trace_entry_id="t",
            failure_code=None,  # None on BLOCK → violates rule 8
            remediation_hints=(),
            next_admissible_stage_ids=(),
            source_commit_sha="sha",
            registry_version="v",
            registry_hash="h",
        )


def test_w8_9_end_to_end_mirror_over_real_ayat_corpus():
    """Every per-stage record from the real Ayat run must round-trip
    into a vendor StageExecutionRecord without raising."""
    from tests.taaqol_integration.test_c13_wave03_relation_closure import (
        _run_full_ayat_and_produce_spans,
    )
    from pipeline.taaqol_integration.evidence_producers.wave06_downstream_chain_typed import (
        execute_ayat_full_downstream_chain_typed,
    )
    cu, sp = _run_full_ayat_and_produce_spans()
    result = execute_ayat_full_downstream_chain_typed(cu, sp)
    mirror = build_span_record_mirror(result["per_span_downstream"])
    assert len(mirror) == 5, f"expected 5 spans, got {len(mirror)}"
    for span_mirror in mirror:
        assert span_mirror["mirror_ok"], (
            f"span {span_mirror['span_id']} had vendor rejections: "
            f"{span_mirror['rejections']}"
        )
        assert len(span_mirror["vendor_records"]) >= 7, (
            f"span {span_mirror['span_id']} should have at least 7 "
            f"stage records, got {len(span_mirror['vendor_records'])}"
        )
        # Every ACCEPT record must have transition_state=EXECUTED.
        for rec in span_mirror["vendor_records"]:
            if rec["transition_state"] == "EXECUTED":
                assert rec["output_carrier_id"], (
                    f"EXECUTED record must have output_carrier_id: {rec}"
                )
                assert rec["failure_code"] is None
            assert rec["span_id"] == span_mirror["span_id"]
            assert rec["token_id"] is None  # Hokom is span-level
            assert rec["source_commit_sha"] == _VENDOR_SHA
