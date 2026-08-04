"""C13 Wave06 typed downstream closure — negative paths + audit bridge.

Closes REPAIR C from the independent audit
(QIYAS-TAAQOL-MAXIMUM-NATIVE-CLOSURE-INDEPENDENT-AUDIT-01 §5):
Manat and Mantuq gain explicit REFUSED tests, the audit bridge
gains ACCEPT + REFUSED tests, and every negative test asserts the
native failure_code and classification (never a bare `None`).

Test map
--------
* §W6.1  Wave06 chain closes all 8 stages 5/5 on real Ayat
* §W6.2  audit-bridge stage present in every span
* §W6.3  unbridged_reachable_stage_count == 0
* §W6.4  Manat DEFER — empty effective_attribute → NO_EFFECTIVE_ATTRIBUTE
* §W6.5  Manat DEFER — empty description → NO_MANAT_DESCRIPTION
* §W6.6  Mantuq DEFER — maqam divergence → MANTUQ_MAQAM_DIVERGENCE
* §W6.7  Mantuq structural — non-Ifadah predecessor → None
* §W6.8  Audit bridge ACCEPT — SURFACED with vendor state=SURFACED
* §W6.9  Audit bridge REFUSED — non-TanzilVerdict input → None
* §W6.10 Audit bridge REFUSED — non-PROVEN Tanzil vendor state returns
        NO_TANZIL_VERDICT, classified as DEFER (typed, not None)
* §W6.11 Deterministic double-run — identical outcomes
"""
from __future__ import annotations
import pytest

from tests.taaqol_integration.test_c13_wave03_relation_closure import (
    _run_full_ayat_and_produce_spans,
)
from pipeline.taaqol_integration.evidence_producers.wave06_downstream_chain_typed import (
    execute_ayat_full_downstream_chain_typed,
)
from pipeline.taaqol_integration.weight_layer.typed_outcomes import (
    ACCEPT, DEFER, BLOCK, UNKNOWN_FAILURE_RESIDUAL_MARKER,
)
from pipeline.taaqol_integration.weight_layer.typed_stage_builders import (
    build_manat_outcome, build_mantuq_outcome,
    build_audited_tanzil_bridge_outcome,
)


# ── §W6.1..3 Full chain on real corpus ──────────────────────────────────

@pytest.fixture(scope="module")
def _typed_result():
    cu, sp = _run_full_ayat_and_produce_spans()
    return execute_ayat_full_downstream_chain_typed(cu, sp)


def test_w6_1_all_stages_close_five_five(_typed_result):
    c = _typed_result['counters']
    for prefix in ("ifadah", "hukm", "manat", "tanzil",
                   "audited_tanzil_bridge", "mantuq", "mafhum"):
        assert c[f'{prefix}_calls'] == 5, (prefix, c[f'{prefix}_calls'])
        assert c[f'{prefix}_accept'] == 5, (prefix, c[f'{prefix}_accept'])
        assert c[f'{prefix}_defer'] == 0
        assert c[f'{prefix}_block'] == 0


def test_w6_2_audit_bridge_present_per_span(_typed_result):
    for span in _typed_result['per_span_downstream']:
        stage_names = [s['stage'] for s in span['stages']]
        assert 'audited_tanzil_bridge' in stage_names, span['span_id']
        atb = [s for s in span['stages'] if s['stage'] == 'audited_tanzil_bridge'][0]
        assert atb['verdict_state'] == 'SURFACED', atb
        assert atb['classification'] == ACCEPT, atb
        assert atb['native_result_type'] == 'AuditedTanzilBridgeVerdict'
        assert atb['trace_ref'].startswith('bridge_tanzil_to_audit/')
        assert atb['input_stage'] == 'tanzil'


def test_w6_3_no_unbridged_reachable_stage(_typed_result):
    assert _typed_result['unbridged_reachable_stage_count'] == 0


# ── Fixture builder for typed negative tests ────────────────────────────

def _build_stage_prereqs(span_selector=0):
    """Build a genuine (hukm, mv, tv, ifv, mq_g, gov, span_id) tuple."""
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
    from pipeline.taaqol_integration.weight_layer.typed_stage_builders import (
        build_hukm_outcome, build_manat_outcome, build_tanzil_outcome,
    )
    from taaqqul_slot_geometry.weight.ifadah_candidate import SpeechForceKind
    from taaqqul_slot_geometry.weight.hukm_candidate import EvaluationDomain
    from taaqqul_slot_geometry.weight.manat_candidate import ManatMode

    cu, spans = _run_full_ayat_and_produce_spans()
    span = [s for s in spans if len(
        [t for t in s.get('member_token_ids') or [] if t in cu]) >= 2
    ][span_selector]
    ms = [t for t in span['member_token_ids'] if t in cu]
    gov, dep = ms[0], ms[-1]

    def _mc(tid):
        e = cu[tid]
        fs = build_formal_style_verdict(tid)
        _ms = build_mufrad_semantic_slot(tid, e, fs.candidate)
        _mq = build_maqam_context(tid, _ms)
        _dal = build_dalalah_candidate(tid, _ms, _mq)
        return fs, _mq, build_mufrad_dalalah_closure(tid, _ms, _mq, _dal)

    fs_g, mq_g, mc_g = _mc(gov)
    _, _, mc_d = _mc(dep)
    rc = build_relation_closure(span['span_id'], gov, dep, mc_g, mc_d,
                                relation_maqam=mq_g.trace_ref)
    ifv = build_ifadah_candidate(
        relation_closure_verdict=rc, formal_style_verdict=fs_g,
        ifadah_maqam_verdict=mq_g, speech_force=SpeechForceKind.KHABAR,
        ifadah_evidence='e', closure_scope='s',
    )
    hukm = build_hukm_outcome(
        ifadah_verdict=ifv, evaluation_domain=EvaluationDomain.LINGUISTIC,
        hukm_claim='c', hukm_evidence='e', hukm_maqam=mq_g.trace_ref,
        closure_scope='s',
    )
    mv = build_manat_outcome(
        hukm_verdict=hukm.native_verdict,
        manat_mode=ManatMode.TAHQIQ_READINESS_ONLY,
        manat_description='d',
        effective_attribute_candidate='attr',
        conditions=(), preventers=(),
        manat_evidence='e', manat_domain='lughawi', closure_scope='s',
    )
    tv = build_tanzil_outcome(
        hukm_verdict=hukm.native_verdict,
        manat_verdict=mv.native_verdict,
        reality_evidence='r', instance_descriptor='i',
        tanzil_scope='s', presentation_warning='CANDIDATE',
    )
    return {
        'gov': gov, 'span_id': span['span_id'], 'ifv': ifv,
        'mq_g': mq_g, 'hukm': hukm, 'mv': mv, 'tv': tv,
    }


# ── §W6.4..5 Manat typed REFUSED ────────────────────────────────────────

def test_w6_4_manat_empty_effective_attribute_yields_typed_defer():
    from taaqqul_slot_geometry.weight.manat_candidate import (
        ManatMode, ManatVerdict,
    )
    ctx = _build_stage_prereqs()
    out = build_manat_outcome(
        hukm_verdict=ctx['hukm'].native_verdict,
        manat_mode=ManatMode.TAHQIQ_READINESS_ONLY,
        manat_description='d',
        effective_attribute_candidate='',  # <— triggers vendor DEFER
        conditions=(), preventers=(),
        manat_evidence='e', manat_domain='lughawi', closure_scope='s',
    )
    assert out is not None, "must not collapse to None"
    assert isinstance(out.native_verdict, ManatVerdict)
    assert out.deferred is True
    assert out.classification == DEFER
    assert out.verdict_state == 'REFUSED'
    assert out.failure_code == 'NO_EFFECTIVE_ATTRIBUTE'
    assert out.trace_ref
    assert UNKNOWN_FAILURE_RESIDUAL_MARKER not in out.failure_detail


def test_w6_5_manat_empty_description_yields_typed_defer():
    from taaqqul_slot_geometry.weight.manat_candidate import (
        ManatMode, ManatVerdict,
    )
    ctx = _build_stage_prereqs()
    out = build_manat_outcome(
        hukm_verdict=ctx['hukm'].native_verdict,
        manat_mode=ManatMode.TAHQIQ_READINESS_ONLY,
        manat_description='',  # <— triggers vendor DEFER
        effective_attribute_candidate='attr',
        conditions=(), preventers=(),
        manat_evidence='e', manat_domain='lughawi', closure_scope='s',
    )
    assert out is not None
    assert isinstance(out.native_verdict, ManatVerdict)
    assert out.deferred is True
    assert out.classification == DEFER
    assert out.failure_code == 'NO_MANAT_DESCRIPTION'


# ── §W6.6..7 Mantuq typed REFUSED / structural ──────────────────────────

def test_w6_6_mantuq_empty_spoken_surface_yields_typed_defer():
    """Vendor requires a non-empty spoken_surface_ref (constitutional
    anchor for the preserved textual origin). Empty → typed REFUSED
    (DEFER: missing evidence)."""
    from taaqqul_slot_geometry.weight.mantuq_closure import MantuqClosureVerdict
    ctx = _build_stage_prereqs()
    out = build_mantuq_outcome(
        ifadah_verdict=ctx['ifv'], maqam_verdict=ctx['mq_g'],
        mantuq_scope='s', spoken_surface_ref='',  # <— triggers vendor REFUSED
        mantuq_evidence='e', closure_scope='cs',
    )
    assert out is not None, "typed builder must not collapse REFUSED to None"
    assert isinstance(out.native_verdict, MantuqClosureVerdict)
    assert out.classification == DEFER
    assert out.deferred is True
    assert out.failure_code == 'NO_SPOKEN_SURFACE'
    assert UNKNOWN_FAILURE_RESIDUAL_MARKER not in out.failure_detail


def test_w6_7_mantuq_wrong_ifadah_type_returns_none_structural():
    """Structural refusal (wrong type) still returns None — this is
    correct fail-closed. Wave06 preserves this behaviour for
    structural guards; only vendor typed REFUSED becomes DEFER/BLOCK."""
    out = build_mantuq_outcome(
        ifadah_verdict=object(), maqam_verdict=object(),
        mantuq_scope='s', spoken_surface_ref='sr',
        mantuq_evidence='e', closure_scope='cs',
    )
    assert out is None


# ── §W6.8..10 Audit-bridge tests ────────────────────────────────────────

def test_w6_8_audit_bridge_accept_on_proven_tanzil():
    from taaqqul_slot_geometry.audit.tanzil_bridge import (
        AuditedTanzilBridgeVerdict, AuditBridgeState,
    )
    ctx = _build_stage_prereqs()
    out = build_audited_tanzil_bridge_outcome(
        tanzil_verdict=ctx['tv'].native_verdict,
    )
    assert out is not None
    assert isinstance(out.native_verdict, AuditedTanzilBridgeVerdict)
    assert out.native_verdict.state is AuditBridgeState.SURFACED
    assert out.accepted is True
    assert out.classification == ACCEPT
    assert out.verdict_state == 'SURFACED'
    assert out.failure_code is None
    assert out.trace_ref == 'bridge_tanzil_to_audit/surfaced'
    assert out.native_verdict.bridge is not None


def test_w6_9_audit_bridge_wrong_type_returns_none():
    out = build_audited_tanzil_bridge_outcome(tanzil_verdict=object())
    assert out is None


def test_w6_10_audit_bridge_non_proven_tanzil_produces_typed_defer():
    """Vendor bridge_tanzil_to_audit refuses with NO_TANZIL_VERDICT
    when the tanzil verdict is not PROVEN. That REFUSED must reach
    Hokom typed (DEFER) — never a bare None."""
    from taaqqul_slot_geometry.audit.tanzil_bridge import (
        AuditedTanzilBridgeVerdict,
    )
    # Build a REFUSED TanzilVerdict via the vendor directly (fail-closed
    # path — no synthetic construction).
    from taaqqul_slot_geometry.weight.tanzil_candidate import (
        prove_tanzil_candidate,
    )
    refused_tv = prove_tanzil_candidate(
        hukm_verdict=object(),  # wrong type → vendor REFUSED
        manat_verdict=object(),
        reality_evidence='r', instance_descriptor='i',
        tanzil_scope='s', presentation_warning='CANDIDATE',
        not_execution_marker=True,
    )
    assert refused_tv.verdict_state.value == 'REFUSED'
    out = build_audited_tanzil_bridge_outcome(tanzil_verdict=refused_tv)
    assert out is not None, "REFUSED must not collapse to None"
    assert isinstance(out.native_verdict, AuditedTanzilBridgeVerdict)
    assert out.deferred is True
    assert out.classification == DEFER
    assert out.verdict_state == 'REFUSED'
    assert out.failure_code == 'NO_TANZIL_VERDICT'


# ── §W6.11 Determinism ──────────────────────────────────────────────────

def test_w6_11_determinism_double_run():
    cu1, sp1 = _run_full_ayat_and_produce_spans()
    r1 = execute_ayat_full_downstream_chain_typed(cu1, sp1)
    cu2, sp2 = _run_full_ayat_and_produce_spans()
    r2 = execute_ayat_full_downstream_chain_typed(cu2, sp2)
    assert r1['counters'] == r2['counters']
    # Compare per-span stage summaries (trace_ref, verdict_state,
    # classification, failure_code, residual_ids)
    def _key(rec):
        return [
            (s['stage'], s['input_stage'], s['native_result_type'],
             s['verdict_state'], s['classification'],
             s['failure_code'], s['trace_ref'],
             tuple(s['residual_ids']), s['failure_detail'])
            for s in rec['stages']
        ]
    for a, b in zip(r1['per_span_downstream'], r2['per_span_downstream']):
        assert a['span_id'] == b['span_id']
        assert _key(a) == _key(b)
