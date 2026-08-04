"""C13 Wave05 downstream closure tests — Hukm / Manat / Tanzil / Mantuq / Mafhum.

Verifies the full native DAG closure from Ifadah into every reachable
downstream stage on the real Ayat corpus.

  Vertical: Ifadah → Hukm → Manat → Tanzil (weight-layer terminal;
      audit-layer bridge added in Wave06 test_c13_wave06_typed_closure.py)
  Parallel: Ifadah → Mantuq → Mafhum

Every stage is a native vendor dataclass (no Hokom-side construction).
Determinism is verified via a two-run compare.
"""
from __future__ import annotations
import pytest

from tests.taaqol_integration.test_c13_wave03_relation_closure import (
    _run_full_ayat_and_produce_spans,
)
from pipeline.taaqol_integration.evidence_producers.wave05_downstream_chain import (
    execute_ayat_full_downstream_chain,
)
from pipeline.taaqol_integration.weight_layer import (
    hukm_candidate_adapter,
    manat_candidate_adapter,
    tanzil_candidate_adapter,
    mantuq_closure_adapter,
    mafhum_closure_adapter,
)


# ── §W5.1 Adapters available ──────────────────────────────────────────

def test_w5_1_all_five_adapters_available():
    """All five downstream adapters must report available under 3.11."""
    assert hukm_candidate_adapter._HUKM_AVAILABLE
    assert manat_candidate_adapter._MANAT_AVAILABLE
    assert tanzil_candidate_adapter._TANZIL_AVAILABLE
    assert mantuq_closure_adapter._MANTUQ_AVAILABLE
    assert mafhum_closure_adapter._MAFHUM_AVAILABLE


# ── §W5.2 End-to-end downstream chain on real Ayat ────────────────────

@pytest.fixture(scope="module")
def _downstream_result():
    cu_map, spans = _run_full_ayat_and_produce_spans()
    return execute_ayat_full_downstream_chain(cu_map, spans)


def test_w5_2_ifadah_proven_upstream_precondition(_downstream_result):
    """Wave04 precondition — at least one Ifadah must have proven."""
    assert _downstream_result["ifadah_proven"] >= 1


def test_w5_3_hukm_all_ifadah_promote(_downstream_result):
    """Every PROVEN Ifadah promotes to a PROVEN Hukm (LINGUISTIC domain)."""
    ifadah = _downstream_result["ifadah_proven"]
    assert _downstream_result["hukm_calls"] == ifadah
    assert _downstream_result["hukm_proven"] == ifadah


def test_w5_4_manat_all_hukm_promote(_downstream_result):
    """Every PROVEN Hukm promotes to PROVEN Manat under TAHQIQ_READINESS_ONLY."""
    hukm = _downstream_result["hukm_proven"]
    assert _downstream_result["manat_calls"] == hukm
    assert _downstream_result["manat_proven"] == hukm


def test_w5_5_tanzil_all_manat_promote(_downstream_result):
    """Every PROVEN Manat promotes to a PROVEN Tanzil (weight-layer terminal)."""
    manat = _downstream_result["manat_proven"]
    assert _downstream_result["tanzil_calls"] == manat
    assert _downstream_result["tanzil_proven"] == manat


def test_w5_6_mantuq_all_ifadah_promote(_downstream_result):
    """Every PROVEN Ifadah also promotes to PROVEN Mantuq (parallel branch)."""
    ifadah = _downstream_result["ifadah_proven"]
    assert _downstream_result["mantuq_calls"] == ifadah
    assert _downstream_result["mantuq_proven"] == ifadah


def test_w5_7_mafhum_all_mantuq_promote(_downstream_result):
    """Every PROVEN Mantuq promotes to a PROVEN Mafhum (MUWAFAQAH branch)."""
    mantuq = _downstream_result["mantuq_proven"]
    assert _downstream_result["mafhum_calls"] == mantuq
    assert _downstream_result["mafhum_proven"] == mantuq


def test_w5_8_all_spans_reach_tanzil(_downstream_result):
    """Every span that reaches the downstream chain must reach TANZIL."""
    reached = _downstream_result["last_reached_stage_per_span"]
    assert reached, "no spans reached the downstream chain"
    assert all(stage == "tanzil_proven" for stage in reached), reached


def test_w5_9_per_span_stage_ordering(_downstream_result):
    """Per-span stage log follows the constitutional DAG order."""
    for span in _downstream_result["per_span_downstream"]:
        stage_names = [name for name, _ in span["stages"]]
        assert stage_names == [
            "relation_closure", "ifadah", "hukm",
            "manat", "tanzil",
            "mantuq", "mafhum",
        ], (span["span_id"], stage_names)


# ── §W5.10 Determinism ────────────────────────────────────────────────

def test_w5_10_determinism_double_run():
    """Two independent runs produce identical per-stage counts."""
    cu_map1, spans1 = _run_full_ayat_and_produce_spans()
    r1 = execute_ayat_full_downstream_chain(cu_map1, spans1)
    cu_map2, spans2 = _run_full_ayat_and_produce_spans()
    r2 = execute_ayat_full_downstream_chain(cu_map2, spans2)
    for key in [
        "ifadah_proven",
        "hukm_calls", "hukm_proven",
        "manat_calls", "manat_proven",
        "tanzil_calls", "tanzil_proven",
        "mantuq_calls", "mantuq_proven",
        "mafhum_calls", "mafhum_proven",
    ]:
        assert r1[key] == r2[key], (key, r1[key], r2[key])
    assert r1["last_reached_stage_per_span"] == r2["last_reached_stage_per_span"]


# ── §W5.11 Vendor-native verdict types ────────────────────────────────

def test_w5_11_native_verdict_types_at_each_stage():
    """Directly invoke each adapter on a single span and assert the
    return values are vendor dataclass instances (not Hokom dicts)."""
    from pipeline.taaqol_integration.evidence_producers.wave04_ifadah_chain import (
        build_formal_style_verdict,
    )
    from pipeline.taaqol_integration.evidence_producers.vertical_chain_adapter import (
        build_mufrad_semantic_slot, build_maqam_context,
        build_dalalah_candidate, build_mufrad_dalalah_closure,
        build_relation_closure,
    )
    from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (
        build_ifadah_candidate,
    )
    from pipeline.taaqol_integration.weight_layer.hukm_candidate_adapter import (
        build_hukm_candidate,
    )
    from pipeline.taaqol_integration.weight_layer.manat_candidate_adapter import (
        build_manat_candidate,
    )
    from pipeline.taaqol_integration.weight_layer.tanzil_candidate_adapter import (
        build_tanzil_candidate,
    )
    from pipeline.taaqol_integration.weight_layer.mantuq_closure_adapter import (
        build_mantuq_closure,
    )
    from pipeline.taaqol_integration.weight_layer.mafhum_closure_adapter import (
        build_mafhum_closure,
    )
    from taaqqul_slot_geometry.weight.ifadah_candidate import (
        SpeechForceKind, IfadahVerdict,
    )
    from taaqqul_slot_geometry.weight.hukm_candidate import (
        EvaluationDomain, HukmVerdict,
    )
    from taaqqul_slot_geometry.weight.manat_candidate import (
        ManatMode, ManatVerdict,
    )
    from taaqqul_slot_geometry.weight.tanzil_candidate import TanzilVerdict
    from taaqqul_slot_geometry.weight.mantuq_closure import MantuqClosureVerdict
    from taaqqul_slot_geometry.weight.mafhum_closure import (
        MafhumBranchType, MafhumClosureVerdict,
    )

    cu_map, spans = _run_full_ayat_and_produce_spans()
    span = next(s for s in spans if len(
        [t for t in s.get('member_token_ids') or [] if t in cu_map]) >= 2)
    m = [t for t in span['member_token_ids'] if t in cu_map]
    gov, dep = m[0], m[-1]

    def build_upto_mc(tid):
        entry = cu_map[tid]
        fs = build_formal_style_verdict(tid)
        ms = build_mufrad_semantic_slot(tid, entry, fs.candidate)
        mq = build_maqam_context(tid, ms)
        dal = build_dalalah_candidate(tid, ms, mq)
        return fs, mq, build_mufrad_dalalah_closure(tid, ms, mq, dal)

    fs_g, mq_g, mc_g = build_upto_mc(gov)
    _fs_d, _mq_d, mc_d = build_upto_mc(dep)
    rc = build_relation_closure(span['span_id'], gov, dep, mc_g, mc_d,
                                relation_maqam=mq_g.trace_ref)
    ifv = build_ifadah_candidate(
        relation_closure_verdict=rc, formal_style_verdict=fs_g,
        ifadah_maqam_verdict=mq_g, speech_force=SpeechForceKind.KHABAR,
        ifadah_evidence='e', closure_scope='s',
    )
    assert isinstance(ifv, IfadahVerdict)
    hv = build_hukm_candidate(
        ifadah_verdict=ifv, evaluation_domain=EvaluationDomain.LINGUISTIC,
        hukm_claim='c', hukm_evidence='e',
        hukm_maqam=mq_g.trace_ref, closure_scope='s',
    )
    assert isinstance(hv, HukmVerdict)
    mv = build_manat_candidate(
        hukm_verdict=hv, manat_mode=ManatMode.TAHQIQ_READINESS_ONLY,
        manat_description='d', effective_attribute_candidate='attr',
        conditions=(), preventers=(),
        manat_evidence='e', manat_domain='lughawi', closure_scope='s',
    )
    assert isinstance(mv, ManatVerdict)
    tv = build_tanzil_candidate(
        hukm_verdict=hv, manat_verdict=mv,
        reality_evidence='r', instance_descriptor='i',
        tanzil_scope='s', presentation_warning='CANDIDATE',
    )
    assert isinstance(tv, TanzilVerdict)
    mtv = build_mantuq_closure(
        ifadah_verdict=ifv, maqam_verdict=mq_g,
        mantuq_scope='s', spoken_surface_ref='sr',
        mantuq_evidence='e', closure_scope='cs',
    )
    assert isinstance(mtv, MantuqClosureVerdict)
    mfv = build_mafhum_closure(
        mantuq_verdict=mtv, outside_boundary='b',
        branch_type=MafhumBranchType.MUWAFAQAH, branch_subtype='',
        qayd='q', source_domain='lughawi', cross_domain_transfer='',
        mantuq_blocks=False, residuals=(),
    )
    assert isinstance(mfv, MafhumClosureVerdict)


# ── §W5.12 Fail-closed on wrong types ─────────────────────────────────

def test_w5_12_hukm_wrong_type_returns_none():
    from pipeline.taaqol_integration.weight_layer.hukm_candidate_adapter import (
        build_hukm_candidate,
    )
    from taaqqul_slot_geometry.weight.hukm_candidate import EvaluationDomain
    r = build_hukm_candidate(
        ifadah_verdict=object(),
        evaluation_domain=EvaluationDomain.LINGUISTIC,
        hukm_claim='c', hukm_evidence='e',
        hukm_maqam='m', closure_scope='s',
    )
    assert r is None


def test_w5_13_tanzil_not_execution_marker_false_returns_none():
    from pipeline.taaqol_integration.weight_layer.tanzil_candidate_adapter import (
        build_tanzil_candidate,
    )
    r = build_tanzil_candidate(
        hukm_verdict=object(), manat_verdict=object(),
        reality_evidence='r', instance_descriptor='i',
        tanzil_scope='s', not_execution_marker=False,
    )
    assert r is None


def test_w5_14_mafhum_empty_qayd_refused_via_adapter():
    """Empty qayd triggers NO_MAFHUM_WITHOUT_BRANCH_RELATION; adapter
    returns None per fail-closed."""
    from pipeline.taaqol_integration.weight_layer.mafhum_closure_adapter import (
        build_mafhum_closure,
    )
    from taaqqul_slot_geometry.weight.mafhum_closure import MafhumBranchType
    from taaqqul_slot_geometry.weight.mantuq_closure import (
        MantuqClosureVerdict,
    )
    # Build a legitimate Mantuq to isolate the qayd failure
    from pipeline.taaqol_integration.evidence_producers.wave04_ifadah_chain import (
        build_formal_style_verdict,
    )
    from pipeline.taaqol_integration.evidence_producers.vertical_chain_adapter import (
        build_mufrad_semantic_slot, build_maqam_context,
        build_dalalah_candidate, build_mufrad_dalalah_closure,
        build_relation_closure,
    )
    from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (
        build_ifadah_candidate,
    )
    from pipeline.taaqol_integration.weight_layer.mantuq_closure_adapter import (
        build_mantuq_closure,
    )
    from taaqqul_slot_geometry.weight.ifadah_candidate import SpeechForceKind

    cu_map, spans = _run_full_ayat_and_produce_spans()
    span = next(s for s in spans if len(
        [t for t in s.get('member_token_ids') or [] if t in cu_map]) >= 2)
    m = [t for t in span['member_token_ids'] if t in cu_map]
    gov, dep = m[0], m[-1]

    def _mc(tid):
        entry = cu_map[tid]
        fs = build_formal_style_verdict(tid)
        ms = build_mufrad_semantic_slot(tid, entry, fs.candidate)
        mq = build_maqam_context(tid, ms)
        dal = build_dalalah_candidate(tid, ms, mq)
        return fs, mq, build_mufrad_dalalah_closure(tid, ms, mq, dal)

    fs_g, mq_g, mc_g = _mc(gov)
    _, _, mc_d = _mc(dep)
    rc = build_relation_closure(span['span_id'], gov, dep, mc_g, mc_d,
                                relation_maqam=mq_g.trace_ref)
    ifv = build_ifadah_candidate(
        relation_closure_verdict=rc, formal_style_verdict=fs_g,
        ifadah_maqam_verdict=mq_g, speech_force=SpeechForceKind.KHABAR,
        ifadah_evidence='e', closure_scope='s',
    )
    mtv = build_mantuq_closure(
        ifadah_verdict=ifv, maqam_verdict=mq_g,
        mantuq_scope='s', spoken_surface_ref='sr',
        mantuq_evidence='e', closure_scope='cs',
    )
    assert isinstance(mtv, MantuqClosureVerdict)
    r = build_mafhum_closure(
        mantuq_verdict=mtv, outside_boundary='b',
        branch_type=MafhumBranchType.MUWAFAQAH, branch_subtype='',
        qayd='', source_domain='lughawi', cross_domain_transfer='',
        mantuq_blocks=False, residuals=(),
    )
    assert r is None
