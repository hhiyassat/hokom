"""Live mutation-proof tests for the integrity measurement framework.

Every counter in :mod:`pipeline.taaqol_integration.integrity_measurement`
must satisfy two properties:

1. *baseline*: running the measurement over the actual Hokom production
   tree and over the actual Wave06 per-span records must return zero.
2. *mutation-proof*: injecting a minimal synthetic defect that carries
   the counter's anti-pattern must cause its value to become non-zero.

The defect fixtures live only in this test module — they are constructed
on the fly via ``tmp_path`` (for source scans) or built as ordinary
dicts (for runtime rules). No defect is committed to production code.

Refs: QIYAS-...-CANONICAL-CLOSURE-01 Phase T1 mutation-proof requirement.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.taaqol_integration.integrity_measurement import (
    DECLARED_COUNTERS,
    RuntimeRecordRule,
    SourceAntiPatternRule,
    _ANTI_PATTERN_RULES,
    _RUNTIME_RULES,
    build_integrity_snapshot,
    compute_meta_counters,
    derive_runtime_counters,
    scan_source_anti_patterns,
    structural_counters,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_ROOT = REPO_ROOT / "pipeline"


# ── Helpers ────────────────────────────────────────────────────────────

def _proven_record(stage: str, cls: str = "ACCEPT", **overrides) -> dict:
    rec = {
        "stage": stage,
        "input_stage": "predecessor",
        "native_result_type": f"{stage.title()}Verdict",
        "verdict_state": "PROVEN" if cls == "ACCEPT" else "REFUSED",
        "classification": cls,
        "failure_code": None if cls == "ACCEPT" else "NO_HUKM",
        "trace_ref": f"prove_{stage}/proven",
        "residual_ids": [] if cls == "ACCEPT" else ["EXPLANATORY:PLACEHOLDER"],
        "failure_detail": "" if cls == "ACCEPT" else "failure_code=NO_HUKM",
    }
    rec.update(overrides)
    return rec


# ── Baseline: production tree is clean ─────────────────────────────────

def test_baseline_production_source_scan_all_zero():
    """The current production tree must contain zero anti-pattern hits."""
    results = scan_source_anti_patterns(
        [PIPELINE_ROOT], list(_ANTI_PATTERN_RULES),
    )
    for name, entry in results.items():
        assert entry["count"] == 0, (
            f"{name} nonzero: {entry['sites'][:5]}"
        )


def test_baseline_runtime_derivation_all_zero_on_healthy_records():
    """Well-formed ACCEPT records must trigger no runtime violation."""
    per_span = [
        {
            "span_id": "SPAN-1",
            "input_ids": ["t1", "t2"],
            "stages": [
                _proven_record("relation_closure"),
                _proven_record("ifadah"),
                _proven_record("hukm"),
                _proven_record("manat"),
                _proven_record("tanzil"),
                _proven_record("audited_tanzil_bridge",
                               native_result_type="AuditedTanzilBridgeVerdict",
                               verdict_state="SURFACED"),
                _proven_record("mantuq"),
                _proven_record("mafhum"),
            ],
        },
    ]
    results = derive_runtime_counters(per_span)
    for name, entry in results.items():
        assert entry["count"] == 0, (
            f"{name} nonzero on healthy records: "
            f"{entry['violating_records']}"
        )


def test_declared_counters_all_have_a_measurement_function():
    """DECLARED_COUNTERS must all be backed by source, runtime, or structural."""
    source_names = {r.counter_name for r in _ANTI_PATTERN_RULES}
    runtime_names = {r.counter_name for r in _RUNTIME_RULES}
    structural_names = set(structural_counters([]).keys())
    measured = source_names | runtime_names | structural_names
    missing = DECLARED_COUNTERS - measured
    assert not missing, f"Declared but unmeasured: {sorted(missing)}"


# ── Mutation proofs — source scanners ──────────────────────────────────

@pytest.mark.parametrize("counter,pattern_text", [
    ("TOKEN_POSITION_BRANCH_COUNT", "if token_position == 3:\n    pass\n"),
    ("EXACT_SURFACE_BRANCH_COUNT", 'if surface == "بسم":\n    pass\n'),
    ("GOLD_LOOKUP_COUNT", "result = GOLD_MAP[key]\n"),
    ("EXPECTED_VERDICT_MAP_COUNT", "verdict = EXPECTED_VERDICTS[span_id]\n"),
    ("SYNTHETIC_EVIDENCE_COUNT", "value = synthetic_evidence(span)\n"),
    ("DIRECT_TAAQOL_INJECTION_COUNT",
     "v = AuditedTanzilBridgeVerdict(bridge=None, state=None,\n"
     "                                failure_code=None, rank=None,\n"
     "                                residuals=(), trace_ref='')\n"),
])
def test_source_scanner_detects_injected_defect(
    tmp_path: Path, counter: str, pattern_text: str,
):
    """Each source rule must fire when its anti-pattern is injected in a temp file."""
    defect = tmp_path / "hokom_defect_fixture.py"
    defect.write_text(f"# temp mutation fixture — never committed\n{pattern_text}",
                      encoding="utf-8")
    results = scan_source_anti_patterns(
        [tmp_path], list(_ANTI_PATTERN_RULES),
    )
    assert results[counter]["count"] >= 1, (
        f"{counter} failed to detect injected defect. "
        f"Injected text:\n{pattern_text}\n"
        f"Sites: {results[counter]['sites']}"
    )
    # First site must reference the tmp file
    assert results[counter]["sites"], f"No sites recorded for {counter}"
    site_path, _lineno, _match = results[counter]["sites"][0]
    assert str(defect) == site_path


def test_source_scanner_ignores_noscan_marker(tmp_path: Path):
    """Lines carrying NOSCAN must be skipped (used by the mutation harness itself)."""
    defect = tmp_path / "noscan_fixture.py"
    defect.write_text(
        "if surface == 'test':  # NOSCAN: EXACT_SURFACE_BRANCH_COUNT\n    pass\n",
        encoding="utf-8",
    )
    results = scan_source_anti_patterns(
        [tmp_path], list(_ANTI_PATTERN_RULES),
    )
    assert results["EXACT_SURFACE_BRANCH_COUNT"]["count"] == 0


# ── Mutation proofs — runtime record rules ─────────────────────────────

def test_runtime_detects_refused_collapsed_to_none():
    span = {
        "span_id": "SPAN-X",
        "stages": [{
            "stage": "hukm",
            "input_stage": "ifadah",
            "native_result_type": "NoneType",
            "verdict_state": "REFUSED",
            "classification": "DEFER",
            "failure_code": None,
            "trace_ref": "",
            "residual_ids": [],
            "failure_detail": "hukm adapter returned None",  # no unavailable marker
        }],
    }
    results = derive_runtime_counters([span])
    assert results["REFUSED_COLLAPSED_TO_NONE_COUNT"]["count"] == 1


def test_runtime_detects_refused_as_accept():
    span = {"span_id": "S", "stages": [{
        "stage": "hukm", "input_stage": "ifadah",
        "native_result_type": "HukmVerdict",
        "verdict_state": "REFUSED", "classification": "ACCEPT",
        "failure_code": "NO_HUKM", "trace_ref": "hukm/refused",
        "residual_ids": ["EXPLANATORY:HUKM_NOT_AUTHORITY"],
        "failure_detail": "failure_code=NO_HUKM",
    }]}
    results = derive_runtime_counters([span])
    assert results["REFUSED_AS_ACCEPT_COUNT"]["count"] == 1


def test_runtime_detects_refused_without_failure_code():
    span = {"span_id": "S", "stages": [{
        "stage": "hukm", "input_stage": "ifadah",
        "native_result_type": "HukmVerdict",
        "verdict_state": "REFUSED", "classification": "DEFER",
        "failure_code": None, "trace_ref": "hukm/refused",
        "residual_ids": ["EXPLANATORY:X"],
        "failure_detail": "some detail without marker",
    }]}
    results = derive_runtime_counters([span])
    assert results["REFUSED_WITHOUT_FAILURE_CODE_COUNT"]["count"] == 1


def test_runtime_detects_defer_without_residual():
    span = {"span_id": "S", "stages": [{
        "stage": "hukm", "input_stage": "ifadah",
        "native_result_type": "HukmVerdict",
        "verdict_state": "REFUSED", "classification": "DEFER",
        "failure_code": "NO_HUKM", "trace_ref": "hukm/refused",
        "residual_ids": [],  # empty
        "failure_detail": "failure_code=NO_HUKM",  # no unavailable marker
    }]}
    results = derive_runtime_counters([span])
    assert results["DEFER_WITHOUT_RESIDUAL_COUNT"]["count"] == 1


def test_runtime_accepts_defer_with_extraction_unavailable_marker():
    """Explicit unavailable marker exempts the record — genuinely missing residuals."""
    span = {"span_id": "S", "stages": [{
        "stage": "ifadah", "input_stage": "relation_closure",
        "native_result_type": "NoneType",
        "verdict_state": "REFUSED", "classification": "DEFER",
        "failure_code": None, "trace_ref": "",
        "residual_ids": [],
        "failure_detail": "ifadah adapter returned None; residual extraction unavailable",
    }]}
    results = derive_runtime_counters([span])
    assert results["DEFER_WITHOUT_RESIDUAL_COUNT"]["count"] == 0
    assert results["REFUSED_WITHOUT_TRACE_COUNT"]["count"] == 0
    assert results["REFUSED_COLLAPSED_TO_NONE_COUNT"]["count"] == 0
    assert results["REFUSED_WITHOUT_FAILURE_CODE_COUNT"]["count"] == 0


def test_runtime_detects_block_without_reason():
    span = {"span_id": "S", "stages": [{
        "stage": "mafhum", "input_stage": "mantuq",
        "native_result_type": "MafhumClosureVerdict",
        "verdict_state": "REFUSED", "classification": "BLOCK",
        "failure_code": None,  # missing
        "trace_ref": "mafhum/refused",
        "residual_ids": [],
        "failure_detail": "",  # missing
    }]}
    results = derive_runtime_counters([span])
    assert results["BLOCK_WITHOUT_REASON_COUNT"]["count"] == 1


def test_runtime_detects_missing_predecessor_accept():
    """Structural counter fires when a stage claims ACCEPT after a non-ACCEPT predecessor."""
    span = {"span_id": "S", "stages": [
        {"stage": "ifadah", "classification": "DEFER"},
        # hukm claims ACCEPT even though its predecessor (ifadah) deferred
        {"stage": "hukm", "classification": "ACCEPT"},
    ]}
    results = structural_counters([span])
    assert results["MISSING_PREDECESSOR_ACCEPT_COUNT"] == 1


# ── Meta-counter proof ─────────────────────────────────────────────────

def test_meta_counter_flags_undeclared_addition():
    """Adding a name to DECLARED_COUNTERS without a rule must show up as UNMEASURED."""
    fake_declared = set(DECLARED_COUNTERS) | {"FAKE_UNMEASURED_COUNTER"}
    # Empty source/runtime/structural — the fake name has no measurement
    meta = compute_meta_counters(
        fake_declared,
        source_results={},
        runtime_results={},
        structural_results={},
    )
    assert meta["UNMEASURED_COUNTER_COUNT"] >= 1
    assert meta["HARDCODED_ZERO_COUNTER_COUNT"] >= 1


def test_meta_counter_zero_when_all_declared_are_measured():
    from pipeline.taaqol_integration.integrity_measurement import (
        _ANTI_PATTERN_RULES as ap, _RUNTIME_RULES as rr,
    )
    source_results = {r.counter_name: {"count": 0, "sites": []} for r in ap}
    runtime_results = {r.counter_name: {"count": 0, "violating_records": []}
                       for r in rr}
    structural_results = structural_counters([])
    meta = compute_meta_counters(
        set(DECLARED_COUNTERS),
        source_results, runtime_results, structural_results,
    )
    assert meta["UNMEASURED_COUNTER_COUNT"] == 0
    assert meta["HARDCODED_ZERO_COUNTER_COUNT"] == 0
    assert meta["COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT"] == 0


# ── End-to-end: snapshot on real production tree ───────────────────────

def test_end_to_end_snapshot_on_production_tree_all_zero_baseline():
    """Full snapshot on the actual pipeline with a single healthy synthetic span."""
    per_span = [{
        "span_id": "SPAN-BASELINE",
        "input_ids": ["t1", "t2"],
        "stages": [
            _proven_record("relation_closure"),
            _proven_record("ifadah"),
            _proven_record("hukm"),
            _proven_record("manat"),
            _proven_record("tanzil"),
            _proven_record("audited_tanzil_bridge",
                           native_result_type="AuditedTanzilBridgeVerdict",
                           verdict_state="SURFACED"),
            _proven_record("mantuq"),
            _proven_record("mafhum"),
        ],
    }]
    snap = build_integrity_snapshot([PIPELINE_ROOT], per_span)
    assert snap["schema_version"] == "1.0.0"
    assert snap["meta"]["UNMEASURED_COUNTER_COUNT"] == 0
    assert snap["meta"]["HARDCODED_ZERO_COUNTER_COUNT"] == 0
    for name in DECLARED_COUNTERS:
        assert name in snap["counters"], f"{name} missing from snapshot"
        assert snap["counters"][name] == 0, (
            f"{name} nonzero: {snap['counter_evidence'][name]}"
        )
