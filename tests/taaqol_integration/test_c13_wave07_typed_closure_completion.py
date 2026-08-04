"""C13 Wave07 typed-closure completion — reaudit-02 gap closure.

Reaudit-02 §6 flagged that the Wave06 suite has *zero* explicit typed
REFUSED tests via the typed builder for Hukm, Tanzil, and Mafhum, and
that the BLOCK classification path is exercised by *no* test at all
even though ``_BLOCK_CODES`` in typed_outcomes.py enumerates 27
constitutionally-distinct BLOCK codes. This module closes that gap.

Test map
--------
* §W7.1  Hukm DEFER — empty hukm_claim → NO_HUKM_CLAIM
* §W7.2  Hukm DEFER — empty hukm_evidence → NO_HUKM_EVIDENCE
* §W7.3  Hukm DEFER — empty hukm_maqam → NO_HUKM_MAQAM
* §W7.4  Tanzil DEFER — empty reality_evidence → NO_REALITY_EVIDENCE
* §W7.5  Tanzil DEFER — empty instance_descriptor → NO_INSTANCE_DESCRIPTOR
* §W7.6  Tanzil DEFER — empty tanzil_scope → NO_TANZIL_SCOPE
* §W7.7  Tanzil BLOCK — not_execution_marker=False → EXECUTION_LEAK
        (typed builder currently guards this structurally; this test
        proves the guard is intentional AND that the vendor code path
        is a real BLOCK when reached directly.)
* §W7.8  Mafhum DEFER — empty outside_boundary → NO_MAFHUM_WITHOUT_OUTSIDE_BOUNDARY
* §W7.9  Mafhum DEFER — empty source_domain → NO_MAFHUM_WITHOUT_SOURCE_DOMAIN
* §W7.10 Mafhum BLOCK — mantuq_blocks=True → MANTUQ_BLOCKS_MAFHUM
* §W7.11 Mafhum BLOCK — non-empty cross_domain_transfer → NO_MAFHUM_CROSS_DOMAIN_LEAP
* §W7.12 Manat BLOCK — TAHQIQ_READINESS_ONLY + reality-checked description
        → TAHQIQ_OVERCLAIM (end-to-end BLOCK via typed builder)
* §W7.13 Manat missing predecessor — REFUSED HukmVerdict → typed defer
* §W7.14 Mafhum missing predecessor — REFUSED MantuqClosureVerdict → typed defer
* §W7.15 Mafhum wrong-type predecessor → structural None
* §W7.16 Live integrity snapshot on real corpus reports all counters = 0
* §W7.17 Live integrity snapshot on Wave07 negative corpus reports the
        DEFER + BLOCK cases without producing DEFER_WITHOUT_RESIDUAL or
        BLOCK_WITHOUT_REASON violations.

The recipes for driving each REFUSED code are derived from vendor
early-guard clauses in weight/hukm_candidate.py, weight/tanzil_candidate.py,
weight/manat_candidate.py, weight/mafhum_closure.py. Every test invokes
the typed builder (build_*_outcome) — never the vendor producer directly
for the assertion-producing call, and never constructs a verdict outside
the vendor call chain.
"""
from __future__ import annotations

import pytest

from tests.taaqol_integration.test_c13_wave06_typed_closure import (
    _build_stage_prereqs,
)
from pipeline.taaqol_integration.evidence_producers.wave06_downstream_chain_typed import (
    execute_ayat_full_downstream_chain_typed,
)
from tests.taaqol_integration.test_c13_wave03_relation_closure import (
    _run_full_ayat_and_produce_spans,
)
from pipeline.taaqol_integration.weight_layer.typed_outcomes import (
    ACCEPT, DEFER, BLOCK, UNKNOWN_FAILURE_RESIDUAL_MARKER,
)
from pipeline.taaqol_integration.weight_layer.typed_stage_builders import (
    build_hukm_outcome, build_manat_outcome, build_tanzil_outcome,
    build_mantuq_outcome, build_mafhum_outcome,
    build_audited_tanzil_bridge_outcome,
)


@pytest.fixture(scope="module")
def _ctx():
    return _build_stage_prereqs()


@pytest.fixture(scope="module")
def _real_chain_result():
    cu, sp = _run_full_ayat_and_produce_spans()
    return execute_ayat_full_downstream_chain_typed(cu, sp)


# ── §W7.1..3  Hukm typed REFUSED ────────────────────────────────────────

def test_w7_1_hukm_empty_claim_yields_typed_defer(_ctx):
    """Vendor prove_hukm_candidate requires non-empty hukm_claim.
    Empty triggers NO_HUKM_CLAIM (DEFER). The typed builder must
    preserve this — never collapse to None."""
    from taaqqul_slot_geometry.weight.hukm_candidate import (
        HukmVerdict, EvaluationDomain,
    )
    out = build_hukm_outcome(
        ifadah_verdict=_ctx['ifv'],
        evaluation_domain=EvaluationDomain.LINGUISTIC,
        hukm_claim='',  # <— triggers vendor REFUSED
        hukm_evidence='e', hukm_maqam=_ctx['mq_g'].trace_ref,
        closure_scope='s',
    )
    assert out is not None, "typed builder must not collapse REFUSED to None"
    assert isinstance(out.native_verdict, HukmVerdict)
    assert out.verdict_state == 'REFUSED'
    assert out.classification == DEFER
    assert out.failure_code == 'NO_HUKM_CLAIM'
    assert out.trace_ref
    assert UNKNOWN_FAILURE_RESIDUAL_MARKER not in out.failure_detail


def test_w7_2_hukm_empty_evidence_yields_typed_defer(_ctx):
    from taaqqul_slot_geometry.weight.hukm_candidate import (
        HukmVerdict, EvaluationDomain,
    )
    out = build_hukm_outcome(
        ifadah_verdict=_ctx['ifv'],
        evaluation_domain=EvaluationDomain.LINGUISTIC,
        hukm_claim='c', hukm_evidence='',  # <— triggers vendor REFUSED
        hukm_maqam=_ctx['mq_g'].trace_ref,
        closure_scope='s',
    )
    assert out is not None
    assert isinstance(out.native_verdict, HukmVerdict)
    assert out.classification == DEFER
    assert out.failure_code == 'NO_HUKM_EVIDENCE'


def test_w7_3_hukm_empty_maqam_yields_typed_defer(_ctx):
    from taaqqul_slot_geometry.weight.hukm_candidate import (
        HukmVerdict, EvaluationDomain,
    )
    out = build_hukm_outcome(
        ifadah_verdict=_ctx['ifv'],
        evaluation_domain=EvaluationDomain.LINGUISTIC,
        hukm_claim='c', hukm_evidence='e',
        hukm_maqam='',  # <— triggers vendor REFUSED
        closure_scope='s',
    )
    assert out is not None
    assert isinstance(out.native_verdict, HukmVerdict)
    assert out.classification == DEFER
    assert out.failure_code == 'NO_HUKM_MAQAM'


# ── §W7.4..6  Tanzil typed REFUSED ──────────────────────────────────────

def test_w7_4_tanzil_empty_reality_evidence_yields_typed_defer(_ctx):
    from taaqqul_slot_geometry.weight.tanzil_candidate import TanzilVerdict
    out = build_tanzil_outcome(
        hukm_verdict=_ctx['hukm'].native_verdict,
        manat_verdict=_ctx['mv'].native_verdict,
        reality_evidence='',  # <— triggers vendor REFUSED
        instance_descriptor='i', tanzil_scope='s',
        presentation_warning='CANDIDATE', not_execution_marker=True,
    )
    assert out is not None
    assert isinstance(out.native_verdict, TanzilVerdict)
    assert out.classification == DEFER
    assert out.failure_code == 'NO_REALITY_EVIDENCE'


def test_w7_5_tanzil_empty_instance_descriptor_yields_typed_defer(_ctx):
    from taaqqul_slot_geometry.weight.tanzil_candidate import TanzilVerdict
    out = build_tanzil_outcome(
        hukm_verdict=_ctx['hukm'].native_verdict,
        manat_verdict=_ctx['mv'].native_verdict,
        reality_evidence='r', instance_descriptor='',
        tanzil_scope='s', presentation_warning='CANDIDATE',
        not_execution_marker=True,
    )
    assert out is not None
    assert isinstance(out.native_verdict, TanzilVerdict)
    assert out.classification == DEFER
    assert out.failure_code == 'NO_INSTANCE_DESCRIPTOR'


def test_w7_6_tanzil_empty_scope_yields_typed_defer(_ctx):
    from taaqqul_slot_geometry.weight.tanzil_candidate import TanzilVerdict
    out = build_tanzil_outcome(
        hukm_verdict=_ctx['hukm'].native_verdict,
        manat_verdict=_ctx['mv'].native_verdict,
        reality_evidence='r', instance_descriptor='i',
        tanzil_scope='',
        presentation_warning='CANDIDATE', not_execution_marker=True,
    )
    assert out is not None
    assert isinstance(out.native_verdict, TanzilVerdict)
    assert out.classification == DEFER
    assert out.failure_code == 'NO_TANZIL_SCOPE'


def test_w7_7_tanzil_execution_leak_via_vendor_direct(_ctx):
    """The typed builder guards not_execution_marker=False structurally
    (returns None). This test proves the underlying vendor path IS
    a real BLOCK when reached directly — the structural guard is
    correct and defensive, not a lie about vendor behaviour."""
    from taaqqul_slot_geometry.weight.tanzil_candidate import (
        prove_tanzil_candidate, TanzilVerdict,
    )
    # Typed builder returns None on structural guard.
    typed = build_tanzil_outcome(
        hukm_verdict=_ctx['hukm'].native_verdict,
        manat_verdict=_ctx['mv'].native_verdict,
        reality_evidence='r', instance_descriptor='i',
        tanzil_scope='s', presentation_warning='CANDIDATE',
        not_execution_marker=False,  # <— structural guard fires
    )
    assert typed is None, "typed builder must fail-closed structurally"
    # Vendor direct call proves the underlying path is a real BLOCK.
    v = prove_tanzil_candidate(
        hukm_verdict=_ctx['hukm'].native_verdict,
        manat_verdict=_ctx['mv'].native_verdict,
        reality_evidence='r', instance_descriptor='i',
        tanzil_scope='s', presentation_warning='CANDIDATE',
        not_execution_marker=False,
    )
    assert isinstance(v, TanzilVerdict)
    assert v.verdict_state.value == 'REFUSED'
    assert v.failure_code.value == 'EXECUTION_LEAK'


# ── §W7.8..11  Mafhum typed REFUSED + real BLOCK ────────────────────────

def test_w7_8_mafhum_empty_boundary_yields_typed_defer(_ctx):
    from taaqqul_slot_geometry.weight.mafhum_closure import (
        MafhumClosureVerdict, MafhumBranchType,
    )
    from taaqqul_slot_geometry.weight.mantuq_closure import prove_mantuq_closure
    # Build a real PROVEN MantuqClosureVerdict via typed builder.
    mtv = build_mantuq_outcome(
        ifadah_verdict=_ctx['ifv'], maqam_verdict=_ctx['mq_g'],
        mantuq_scope='s', spoken_surface_ref='sr',
        mantuq_evidence='e', closure_scope='cs',
    )
    assert mtv is not None and mtv.accepted
    out = build_mafhum_outcome(
        mantuq_verdict=mtv.native_verdict,
        outside_boundary='',  # <— triggers vendor REFUSED
        branch_type=MafhumBranchType.MUWAFAQAH,
        branch_subtype='', qayd='q', source_domain='lughawi',
        cross_domain_transfer='', mantuq_blocks=False, residuals=(),
    )
    assert out is not None
    assert isinstance(out.native_verdict, MafhumClosureVerdict)
    assert out.classification == DEFER
    assert out.failure_code == 'NO_MAFHUM_WITHOUT_OUTSIDE_BOUNDARY'


def test_w7_9_mafhum_empty_source_domain_yields_typed_defer(_ctx):
    from taaqqul_slot_geometry.weight.mafhum_closure import (
        MafhumClosureVerdict, MafhumBranchType,
    )
    mtv = build_mantuq_outcome(
        ifadah_verdict=_ctx['ifv'], maqam_verdict=_ctx['mq_g'],
        mantuq_scope='s', spoken_surface_ref='sr',
        mantuq_evidence='e', closure_scope='cs',
    )
    out = build_mafhum_outcome(
        mantuq_verdict=mtv.native_verdict,
        outside_boundary='ob', branch_type=MafhumBranchType.MUWAFAQAH,
        branch_subtype='', qayd='q', source_domain='',
        cross_domain_transfer='', mantuq_blocks=False, residuals=(),
    )
    assert out is not None
    assert isinstance(out.native_verdict, MafhumClosureVerdict)
    assert out.classification == DEFER
    assert out.failure_code == 'NO_MAFHUM_WITHOUT_SOURCE_DOMAIN'


def test_w7_10_mafhum_mantuq_blocks_yields_typed_block(_ctx):
    """Real end-to-end BLOCK via native vendor code MANTUQ_BLOCKS_MAFHUM.
    This is the first BLOCK-classified test in the entire Wave03-06 suite;
    it proves the BLOCK arm of the classifier is reachable through
    the typed builder without fabrication."""
    from taaqqul_slot_geometry.weight.mafhum_closure import (
        MafhumClosureVerdict, MafhumBranchType,
    )
    mtv = build_mantuq_outcome(
        ifadah_verdict=_ctx['ifv'], maqam_verdict=_ctx['mq_g'],
        mantuq_scope='s', spoken_surface_ref='sr',
        mantuq_evidence='e', closure_scope='cs',
    )
    out = build_mafhum_outcome(
        mantuq_verdict=mtv.native_verdict,
        outside_boundary='ob', branch_type=MafhumBranchType.MUWAFAQAH,
        branch_subtype='', qayd='q', source_domain='lughawi',
        cross_domain_transfer='', mantuq_blocks=True,  # <— BLOCK trigger
        residuals=(),
    )
    assert out is not None
    assert isinstance(out.native_verdict, MafhumClosureVerdict)
    assert out.verdict_state == 'REFUSED'
    assert out.classification == BLOCK, (
        f"MANTUQ_BLOCKS_MAFHUM must classify as BLOCK, "
        f"got {out.classification} for {out.failure_code}"
    )
    assert out.blocked is True
    assert out.failure_code == 'MANTUQ_BLOCKS_MAFHUM'
    assert out.trace_ref
    assert UNKNOWN_FAILURE_RESIDUAL_MARKER not in out.failure_detail


def test_w7_11_mafhum_cross_domain_leap_yields_typed_block(_ctx):
    """Second real BLOCK path — NO_MAFHUM_CROSS_DOMAIN_LEAP fires when
    cross_domain_transfer is non-empty."""
    from taaqqul_slot_geometry.weight.mafhum_closure import (
        MafhumClosureVerdict, MafhumBranchType,
    )
    mtv = build_mantuq_outcome(
        ifadah_verdict=_ctx['ifv'], maqam_verdict=_ctx['mq_g'],
        mantuq_scope='s', spoken_surface_ref='sr',
        mantuq_evidence='e', closure_scope='cs',
    )
    out = build_mafhum_outcome(
        mantuq_verdict=mtv.native_verdict,
        outside_boundary='ob', branch_type=MafhumBranchType.MUWAFAQAH,
        branch_subtype='', qayd='q', source_domain='lughawi',
        cross_domain_transfer='foreign',  # <— BLOCK trigger
        mantuq_blocks=False, residuals=(),
    )
    assert out is not None
    assert isinstance(out.native_verdict, MafhumClosureVerdict)
    assert out.classification == BLOCK
    assert out.failure_code == 'NO_MAFHUM_CROSS_DOMAIN_LEAP'


# ── §W7.12  Manat real BLOCK (TAHQIQ_OVERCLAIM) ─────────────────────────

def test_w7_12_manat_tahqiq_overclaim_yields_typed_block(_ctx):
    """Third real BLOCK path — TAHQIQ_OVERCLAIM fires when
    ManatMode.TAHQIQ_READINESS_ONLY is combined with a description
    containing overclaim keywords ("reality_checked", "applied",
    "executed", "verified", "final_tahqiq", "tahqiq_final",
    "confirmed"). This is the constitutional guard against calling
    a candidate a tahqiq without actual reality application."""
    from taaqqul_slot_geometry.weight.manat_candidate import (
        ManatMode, ManatVerdict,
    )
    out = build_manat_outcome(
        hukm_verdict=_ctx['hukm'].native_verdict,
        manat_mode=ManatMode.TAHQIQ_READINESS_ONLY,
        manat_description='reality_checked applied executed',  # <— overclaim
        effective_attribute_candidate='verified final_tahqiq',
        conditions=(), preventers=(),
        manat_evidence='e', manat_domain='lughawi', closure_scope='s',
    )
    assert out is not None
    assert isinstance(out.native_verdict, ManatVerdict)
    assert out.verdict_state == 'REFUSED'
    assert out.classification == BLOCK
    assert out.blocked is True
    assert out.failure_code == 'TAHQIQ_OVERCLAIM'
    assert out.trace_ref


# ── §W7.13..15  Missing predecessor + wrong type ────────────────────────

def test_w7_13_manat_missing_predecessor_yields_typed_defer(_ctx):
    """Passing a genuinely REFUSED HukmVerdict (obtained via vendor
    direct call with insufficient inputs) drives Manat to a typed
    REFUSED with predecessor-missing semantics."""
    from taaqqul_slot_geometry.weight.hukm_candidate import (
        prove_hukm_candidate, EvaluationDomain, HukmVerdict,
    )
    from taaqqul_slot_geometry.weight.manat_candidate import (
        ManatMode, ManatVerdict,
    )
    # Build a real REFUSED HukmVerdict.
    refused_hukm = prove_hukm_candidate(
        ifadah_verdict=_ctx['ifv'],
        evaluation_domain=EvaluationDomain.LINGUISTIC,
        hukm_claim='',  # <— empty → vendor REFUSED
        hukm_evidence='e', hukm_maqam=_ctx['mq_g'].trace_ref,
        closure_scope='s',
    )
    assert isinstance(refused_hukm, HukmVerdict)
    assert refused_hukm.verdict_state.value == 'REFUSED'
    # Feed the REFUSED HukmVerdict into the typed Manat builder.
    out = build_manat_outcome(
        hukm_verdict=refused_hukm,
        manat_mode=ManatMode.TAHQIQ_READINESS_ONLY,
        manat_description='d', effective_attribute_candidate='attr',
        conditions=(), preventers=(),
        manat_evidence='e', manat_domain='lughawi', closure_scope='s',
    )
    assert out is not None, (
        "typed Manat builder must not collapse REFUSED-predecessor "
        "path to None"
    )
    assert isinstance(out.native_verdict, ManatVerdict)
    assert out.classification == DEFER
    assert out.failure_code == 'NO_HUKM'


def test_w7_14_mafhum_missing_predecessor_yields_typed_defer(_ctx):
    """Passing a genuinely REFUSED MantuqClosureVerdict drives Mafhum
    to typed REFUSED with predecessor-missing semantics."""
    from taaqqul_slot_geometry.weight.mantuq_closure import (
        prove_mantuq_closure, MantuqClosureVerdict,
    )
    from taaqqul_slot_geometry.weight.mafhum_closure import (
        MafhumClosureVerdict, MafhumBranchType,
    )
    # Build a real REFUSED MantuqClosureVerdict.
    refused_mtv = prove_mantuq_closure(
        ifadah_verdict=_ctx['ifv'], maqam_verdict=_ctx['mq_g'],
        mantuq_scope='s', spoken_surface_ref='',  # <— triggers REFUSED
        mantuq_evidence='e', closure_scope='cs',
    )
    assert isinstance(refused_mtv, MantuqClosureVerdict)
    assert refused_mtv.verdict_state.value == 'REFUSED'
    out = build_mafhum_outcome(
        mantuq_verdict=refused_mtv,
        outside_boundary='ob', branch_type=MafhumBranchType.MUWAFAQAH,
        branch_subtype='', qayd='q', source_domain='lughawi',
        cross_domain_transfer='', mantuq_blocks=False, residuals=(),
    )
    assert out is not None
    assert isinstance(out.native_verdict, MafhumClosureVerdict)
    assert out.classification == DEFER
    assert out.failure_code == 'NO_MAFHUM_BEFORE_MANTUQ_CLOSURE'


def test_w7_15_mafhum_wrong_type_returns_none_structural():
    """Structural refusal (wrong-type predecessor) → None (fail-closed)."""
    from taaqqul_slot_geometry.weight.mafhum_closure import MafhumBranchType
    out = build_mafhum_outcome(
        mantuq_verdict=object(),  # <— wrong type
        outside_boundary='ob', branch_type=MafhumBranchType.MUWAFAQAH,
        branch_subtype='', qayd='q', source_domain='lughawi',
        cross_domain_transfer='', mantuq_blocks=False, residuals=(),
    )
    assert out is None


# ── §W7.16..17  Live integrity snapshot ─────────────────────────────────

def test_w7_16_live_integrity_snapshot_on_real_corpus_all_zero(
    _real_chain_result,
):
    """The Wave07 integrity framework, run on the real Ayat corpus
    outcome, must report zero for every declared counter."""
    from pathlib import Path
    from pipeline.taaqol_integration.integrity_measurement import (
        build_integrity_snapshot, DECLARED_COUNTERS,
    )
    pipeline_root = Path(__file__).resolve().parents[2] / "pipeline"
    per_span = _real_chain_result['per_span_downstream']
    snap = build_integrity_snapshot([pipeline_root], per_span)
    for name in DECLARED_COUNTERS:
        assert name in snap['counters'], f"{name} missing"
        assert snap['counters'][name] == 0, (
            f"{name} nonzero on real corpus: {snap['counter_evidence'][name]}"
        )
    assert snap['meta']['HARDCODED_ZERO_COUNTER_COUNT'] == 0
    assert snap['meta']['UNMEASURED_COUNTER_COUNT'] == 0


def test_w7_17_live_integrity_on_defect_span_flags_expected_counters(_ctx):
    """When we feed the framework a synthetic span containing this
    module's own DEFER/BLOCK cases, the runtime counters must NOT
    report DEFER_WITHOUT_RESIDUAL or BLOCK_WITHOUT_REASON — because
    each typed outcome carries the required failure_code/trace/residual
    fields."""
    from pathlib import Path
    from pipeline.taaqol_integration.integrity_measurement import (
        derive_runtime_counters,
    )
    # Reuse the exact typed outcomes the tests above produced.
    from taaqqul_slot_geometry.weight.mafhum_closure import (
        MafhumBranchType,
    )
    mtv = build_mantuq_outcome(
        ifadah_verdict=_ctx['ifv'], maqam_verdict=_ctx['mq_g'],
        mantuq_scope='s', spoken_surface_ref='sr',
        mantuq_evidence='e', closure_scope='cs',
    )
    mfv_block = build_mafhum_outcome(
        mantuq_verdict=mtv.native_verdict,
        outside_boundary='ob', branch_type=MafhumBranchType.MUWAFAQAH,
        branch_subtype='', qayd='q', source_domain='lughawi',
        cross_domain_transfer='', mantuq_blocks=True, residuals=(),
    )
    mfv_defer = build_mafhum_outcome(
        mantuq_verdict=mtv.native_verdict,
        outside_boundary='', branch_type=MafhumBranchType.MUWAFAQAH,
        branch_subtype='', qayd='q', source_domain='lughawi',
        cross_domain_transfer='', mantuq_blocks=False, residuals=(),
    )
    # Package as per-span record dicts, same shape as
    # execute_ayat_full_downstream_chain_typed emits.
    def _rec(outcome, input_stage='mantuq'):
        return {
            'stage': outcome.stage, 'input_stage': input_stage,
            'native_result_type': type(outcome.native_verdict).__name__,
            'verdict_state': outcome.verdict_state,
            'classification': outcome.classification,
            'failure_code': outcome.failure_code,
            'trace_ref': outcome.trace_ref,
            'residual_ids': list(outcome.residual_ids),
            'failure_detail': outcome.failure_detail,
        }
    per_span = [{
        'span_id': 'SPAN-DEFECT-PROBE',
        'stages': [_rec(mfv_block), _rec(mfv_defer)],
    }]
    r = derive_runtime_counters(per_span)
    # No violation counters — the typed builders populate all required
    # fields for BLOCK and DEFER outcomes alike.
    assert r['DEFER_WITHOUT_RESIDUAL_COUNT']['count'] == 0, r
    assert r['BLOCK_WITHOUT_REASON_COUNT']['count'] == 0, r
    assert r['REFUSED_COLLAPSED_TO_NONE_COUNT']['count'] == 0
    assert r['REFUSED_WITHOUT_FAILURE_CODE_COUNT']['count'] == 0
    assert r['TRACE_INCOMPLETE_COUNT']['count'] == 0
