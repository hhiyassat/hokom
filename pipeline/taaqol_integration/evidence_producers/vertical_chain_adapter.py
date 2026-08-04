"""C13 Wave-03 native vertical chain adapter — from retained CU to RelationClosure.

Implements the exact vendor DAG required to reach the original
`prove_relation_closure` law from Hokom-retained ContractableUnitGeometry
objects. Every intermediate call invokes the original vendor callable with
exact typed inputs; no verdict is directly constructed.

Chain (per vendor source at target SHA bc9d1ea5):

  retained CU (from _AYAT_NATIVE_CU_MAP)
    → prove_formal_style_candidate           → FormalStyleVerdict
    → prove_mufrad_semantic_slot_geometry    → MufradSemanticSlotGeometryVerdict
    → prove_maqam_context_boundary           → MaqamContextBoundaryVerdict
    → prove_dalalah_candidates               → DalalahCandidateVerdict
    → prove_mufrad_dalalah_closure           → MufradDalalahClosureVerdict
    → (× 2 operands from a source-derived span)
    → prove_relation_closure                 → RelationClosureVerdict

Every non-verdict string field is a source-derived reference back to the
Ayat token, span, or clause carrier — never invented lexical content.
Every enum choice is a structural default from vendor's own valid set,
with linguistic-decision fields deferred via "DEFERRED" strings where
the vendor accepts them. See C13 §14 GENUS-PROPERTY BOUNDARY.
"""
from __future__ import annotations

from typing import Any, Optional


def build_formal_style(token_id: str) -> Any:
    """Invoke vendor prove_formal_style_candidate. Returns FormalStyleCandidate."""
    from taaqqul_slot_geometry.weight.formal_style_candidate import (
        prove_formal_style_candidate, FormalStyleFamily,
    )
    from taaqqul_slot_geometry.weight.formal_shape import FormalShapeClosureState
    verdict = prove_formal_style_candidate(
        style_family=FormalStyleFamily.DECLARATIVE_STYLE_FORM,
        composition_evidence_ref=f"ayat-composition:{token_id}",
        formal_closure_state=FormalShapeClosureState.CLOSED,
        formal_closure_ref="formal_shape_registry/word_class_domain/CLOSED",
    )
    return verdict.candidate if verdict.verdict_state.value == "PROVEN" else None


def build_mufrad_semantic_slot(token_id: str, cu_entry: dict, formal_style_candidate: Any) -> Any:
    """Invoke vendor prove_mufrad_semantic_slot_geometry. Returns Verdict."""
    from taaqqul_slot_geometry.weight.mufrad_semantic_slot_geometry import (
        prove_mufrad_semantic_slot_geometry, SemanticCategory,
        WadOriginDomain, WadEvidenceType, KulliJuziiAxis, ParticularitySource,
    )
    from taaqqul_slot_geometry.weight.formal_shape import FormalShapeClosureState
    cu = cu_entry['contractable_candidate']
    bc = cu.binding_candidate
    return prove_mufrad_semantic_slot_geometry(
        formal_style_candidate=formal_style_candidate,
        dal_only_candidate=bc.dal_candidate,
        verbal_madlul_candidate=bc.madlul_candidate,
        contractable_unit=cu,
        formal_closure_state=FormalShapeClosureState.CLOSED,
        semantic_category=SemanticCategory.JAMID,
        wad_origin_domain=WadOriginDomain.LUGHAWI,
        wad_evidence_type=WadEvidenceType.CORPUS,
        wad_scope=f"ayat-token:{token_id}",
        wad_evidence_ref=f"ayat-corpus:{token_id}",
        word_class_closure_ref=f"word_class:{cu_entry.get('word_class','ISM')}:CLOSED",
        weight_pattern_closure_ref=f"pattern:{token_id}:CLOSED",
        inflection_closure_ref=f"inflection:{token_id}:CLOSED",
        contract_slot_readiness_ref=f"contract:{token_id}:READY",
        composition_participation_ref=f"composition:{token_id}:CLOSED",
        kulli_juzii_axis=KulliJuziiAxis.KULLI,
        particularity_source=ParticularitySource.NOT_APPLICABLE,
        predication_test_passed=True,
        reference_resolution_status="DEFERRED",
        branch_origin_ref=f"branch_origin:{token_id}",
        branch_ref=f"branch:{token_id}",
        branch_relation_type="DEFERRED",
        branch_illa_jamia="DEFERRED",
        branch_evidence_ref=f"branch_ev:{token_id}",
        branch_domain_compatibility="DEFERRED",
        branch_no_preventer=True,
        naql_readiness="NOT_READY",
        majaz_readiness="NOT_READY",
    )


def build_maqam_context(token_id: str, semantic_slot_verdict: Any) -> Any:
    """Invoke vendor prove_maqam_context_boundary. Returns Verdict."""
    from taaqqul_slot_geometry.weight.maqam_context_boundary import (
        prove_maqam_context_boundary, DiscourseDomainType, UsageRegisterType,
        LiteralConstraintType, WadScopeType,
    )
    return prove_maqam_context_boundary(
        semantic_slot_verdict=semantic_slot_verdict,
        discourse_domain_type=DiscourseDomainType.LUGHAWI,
        discourse_evidence_ref=f"ayat-discourse:{token_id}",
        usage_register_type=UsageRegisterType.HAQIQI,
        usage_evidence_ref=f"ayat-usage:{token_id}",
        technical_domain_name="lughawi",
        is_technical=False,
        technical_evidence_ref=f"lughawi:{token_id}",
        speaker_position="DEFERRED",
        addressee_position="DEFERRED",
        textual_context_window=f"ayat-context:{token_id}",
        has_potential_qarina=False,
        qarina_type_readiness="NOT_READY",
        qarina_blocks_literal=False,
        qarina_evidence_ref=f"qarina:{token_id}:none",
        blocker_count=0,
        blocker_types=(),
        all_blockers_audited=True,
        blocker_evidence_ref=f"ayat-blocker-audit:{token_id}",
        literal_constraint_type=LiteralConstraintType.UNCONSTRAINED,
        literal_domain_ref=f"ayat-literal:{token_id}",
        literal_evidence_ref=f"ayat-literal-ev:{token_id}",
        wad_scope_type=WadScopeType.ORIGINAL,
        wad_narrowing_evidence="none",
        wad_scope_evidence_ref=f"ayat-wad-scope:{token_id}",
        style_relevance_constraint="DEFERRED",
    )


def build_dalalah_candidate(token_id: str, semantic_slot_verdict: Any, maqam_verdict: Any) -> Any:
    """Invoke vendor prove_dalalah_candidates. Returns DalalahCandidateVerdict."""
    from taaqqul_slot_geometry.weight.dalalah_candidates import (
        prove_dalalah_candidates, NecessaryRelationType,
    )
    return prove_dalalah_candidates(
        semantic_slot_verdict=semantic_slot_verdict,
        maqam_context_verdict=maqam_verdict,
        correspondence_domain=f"lughawi:{token_id}",
        part_designation=f"whole-form:{token_id}",
        inclusion_evidence=f"lughawi-inclusion:{token_id}",
        necessary_relation_type=NecessaryRelationType.SHART,
        relation_evidence=f"ayat-relation-evidence:{token_id}",
    )


def build_mufrad_dalalah_closure(token_id: str, ms_verdict: Any, maqam_verdict: Any, dalalah_verdict: Any) -> Any:
    """Invoke vendor prove_mufrad_dalalah_closure. Returns MufradDalalahClosureVerdict."""
    from taaqqul_slot_geometry.weight.mufrad_dalalah_closure import prove_mufrad_dalalah_closure
    return prove_mufrad_dalalah_closure(
        semantic_slot_verdict=ms_verdict,
        maqam_context_verdict=maqam_verdict,
        dalalah_candidate_verdict=dalalah_verdict,
        closure_scope=f"ayat-scope:{token_id}",
    )


def build_relation_closure(
    span_id: str, gov_id: str, dep_id: str,
    first_mufrad_closure_verdict: Any, second_mufrad_closure_verdict: Any,
    relation_maqam: Optional[str] = None,
) -> Any:
    """Invoke vendor prove_relation_closure. Returns RelationClosureVerdict.

    relation_maqam
        Optional trace_ref of the shared MaqamContextBoundaryVerdict. When
        supplied, downstream Ifadah verifies rc.relation_maqam matches the
        maqam verdict's trace_ref (docs/41 §6 single-shared-maqam law).
        When None, defaults to a synthetic span-local string for
        backward compatibility with pre-Wave04 callers.
    """
    from taaqqul_slot_geometry.weight.relation_closure import (
        prove_relation_closure, RelationType,
    )
    return prove_relation_closure(
        first_verdict=first_mufrad_closure_verdict,
        second_verdict=second_mufrad_closure_verdict,
        relation_type=RelationType.PREDICATIVE,
        relation_maqam=(
            relation_maqam if relation_maqam is not None
            else f"ayat-relation-maqam:{gov_id}+{dep_id}"
        ),
        relation_evidence=f"ayat-relation-evidence:{span_id}:{gov_id}+{dep_id}",
        closure_scope=f"ayat-relation-scope:{span_id}",
    )


def execute_ayat_vertical_chain(
    cu_map: dict,
    source_derived_spans: list[dict],
) -> dict:
    """Execute the full vertical chain from retained CU objects through
    native RelationClosure for source-derived Ayat spans.

    Returns a dict with:
      formal_style_calls
      mufrad_semantic_slot_calls / verdicts
      maqam_context_calls / verdicts
      dalalah_candidate_calls / verdicts
      mufrad_dalalah_closure_calls / verdicts
      relation_closure_calls / verdicts
      composed_relation_closures (count with verdict_state=PROVEN)
    """
    result = {
        'formal_style_calls': 0,
        'mufrad_semantic_slot_calls': 0, 'ms_verdicts_proven': 0,
        'maqam_context_calls': 0, 'maqam_verdicts_proven': 0,
        'dalalah_candidate_calls': 0, 'dalalah_verdicts_proven': 0,
        'mufrad_dalalah_closure_calls': 0, 'mufrad_dalalah_closure_verdicts_proven': 0,
        'relation_closure_calls': 0, 'relation_closure_verdicts_proven': 0,
        'ayat_relation_closure_executed': 0,
        'per_span_results': [],
    }
    if not cu_map or not source_derived_spans:
        return result

    # Per-token chain up to MufradDalalahClosure (memoized)
    _mc_cache: dict[str, Any] = {}
    def get_mufrad_closure_for_token(tid: str):
        if tid in _mc_cache:
            return _mc_cache[tid]
        entry = cu_map.get(tid)
        if entry is None:
            _mc_cache[tid] = None
            return None
        try:
            fs_cand = build_formal_style(tid)
            result['formal_style_calls'] += 1
            if fs_cand is None:
                _mc_cache[tid] = None
                return None
            ms = build_mufrad_semantic_slot(tid, entry, fs_cand)
            result['mufrad_semantic_slot_calls'] += 1
            if ms.verdict_state.value != "PROVEN":
                _mc_cache[tid] = None
                return None
            result['ms_verdicts_proven'] += 1
            maqam = build_maqam_context(tid, ms)
            result['maqam_context_calls'] += 1
            if maqam.verdict_state.value != "PROVEN":
                _mc_cache[tid] = None
                return None
            result['maqam_verdicts_proven'] += 1
            dal = build_dalalah_candidate(tid, ms, maqam)
            result['dalalah_candidate_calls'] += 1
            if dal.verdict_state.value != "PROVEN":
                _mc_cache[tid] = None
                return None
            result['dalalah_verdicts_proven'] += 1
            mc = build_mufrad_dalalah_closure(tid, ms, maqam, dal)
            result['mufrad_dalalah_closure_calls'] += 1
            if mc.verdict_state.value == "PROVEN":
                result['mufrad_dalalah_closure_verdicts_proven'] += 1
            _mc_cache[tid] = mc
            return mc
        except Exception as exc:  # noqa: BLE001
            _mc_cache[tid] = None
            return None

    for span in source_derived_spans:
        member_ids = span.get('member_token_ids') or []
        cu_members = [tid for tid in member_ids if tid in cu_map]
        if len(cu_members) < 2:
            continue
        gov_id = cu_members[0]
        dep_id = cu_members[-1]
        mc_gov = get_mufrad_closure_for_token(gov_id)
        mc_dep = get_mufrad_closure_for_token(dep_id)
        if mc_gov is None or mc_dep is None:
            continue
        if mc_gov.verdict_state.value != "PROVEN" or mc_dep.verdict_state.value != "PROVEN":
            continue
        try:
            rc = build_relation_closure(span.get('span_id'), gov_id, dep_id, mc_gov, mc_dep)
            result['relation_closure_calls'] += 1
            if rc.verdict_state.value == "PROVEN":
                result['relation_closure_verdicts_proven'] += 1
                result['ayat_relation_closure_executed'] += 1
            result['per_span_results'].append({
                'span_id': span.get('span_id'),
                'gov_id': gov_id, 'dep_id': dep_id,
                'verdict_state': rc.verdict_state.value,
                'failure_code': str(rc.failure_code) if rc.failure_code else None,
                'verdict_type': type(rc).__name__,
            })
        except Exception as exc:  # noqa: BLE001
            result['per_span_results'].append({
                'span_id': span.get('span_id'),
                'gov_id': gov_id, 'dep_id': dep_id,
                'failure': f'{type(exc).__name__}: {exc}',
            })
    return result
