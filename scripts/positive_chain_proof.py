#!/usr/bin/env python3
"""
positive_chain_proof.py — B4: Positive approved full-chain proof.

Proves one complete path from raw Arabic input to AnswerAudit APPROVED
without gold fixture seeding, without direct carrier injection, and without
bypassing any gate.

Input: "ذَهَبَ الرَّجُلُ" (The man went) — simple verbal sentence.
NOT seeded from any gold corpus; this sentence is not in Ayat Al-Dayn.

Chain path proven:
    raw input
    → CanonicalPipeline.run_word() × 2   [Hokom live, P0-P8 per token]
    → hokom_trace_to_token_ledger()       [live adapter, 19 rows per token]
    → RelationCandidate construction      [from live stage outputs, no hard-coded]
    → RelationClosureResult               [RELATION_CLOSED]
    → build_ifadah()                      [IFADAH_APPROVED]
    → build_hukm()                        [HUKM_APPROVED]
    → build_answer_audit()                [ANSWER_AUDIT_APPROVED]

Every transition carries:
    stage_id, scope, native_executor (or declared adapter),
    input_ref, output_ref, evidence_ids, residuals, rank_before, rank_after,
    gamma_state, gate_verdict, trace_id.

Must run under Python 3.12.4:
    .venv-py312/bin/python scripts/positive_chain_proof.py

Constitutional notes:
    - Hukm here is LINGUISTIC_STRUCTURAL_CARRIER_NOT_FIQH_RULING
    - No claim is a religious or legal ruling
    - Gold corpus (tests/evaluation/) is NEVER imported here
    - All evidence comes from the live pipeline output
"""
from __future__ import annotations
import os
import sys
import uuid
import traceback

# ── Path setup ────────────────────────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_VENDOR_SRC = os.path.join(_REPO_ROOT, "vendor", "Taaqol-GPT", "src")
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))
sys.path.insert(0, _VENDOR_SRC)

SEP = "=" * 70
PASS = "✅"
FAIL = "❌"


# ── Positive input ────────────────────────────────────────────────────────────
# Simple Arabic verbal sentence: "ذَهَبَ الرَّجُلُ" = "The man went"
# One clear VERB_AGENT relation: ذَهَبَ (verb) → الرَّجُلُ (subject/فاعل)
# This sentence is NOT from Ayat Al-Dayn and NOT from any gold corpus.

POSITIVE_INPUT_SENTENCE = "ذَهَبَ الرَّجُلُ"
POSITIVE_INPUT_TOKENS = [
    {"surface": "ذَهَبَ",    "index": 0, "hokom_evidence_by_stage": {}},
    {"surface": "الرَّجُلُ", "index": 1, "hokom_evidence_by_stage": {}},
]
POSITIVE_INPUT_CLAUSE_ID = "PROOF-C01"
POSITIVE_PIPELINE_RUN_ID = "B4-POSITIVE-PROOF-2026"


def _print_metric(label: str, value, *, ok: bool | None = None) -> None:
    if ok is None:
        print(f"    {label} = {value}")
    else:
        marker = PASS if ok else FAIL
        print(f"    {marker} {label} = {value}")


def _print_transition(label: str, fields: dict) -> None:
    print(f"\n  ── {label} ──")
    for k, v in fields.items():
        print(f"    {k:<40} = {v}")


def main() -> int:
    print(f"\n{SEP}")
    print("B4: POSITIVE APPROVED FULL-CHAIN PROOF")
    print(f"Input: '{POSITIVE_INPUT_SENTENCE}'")
    print(f"Python: {sys.version}")
    print(SEP)

    b4_metrics: dict[str, int] = {
        "POSITIVE_INPUT_NOT_ENGINE_SEED":       1,
        "POSITIVE_HOKOM_LIVE_EXECUTION":        0,
        "POSITIVE_TAAQOL_NATIVE_EXECUTION":     0,
        "POSITIVE_CLAUSE_PROOF":                0,
        "POSITIVE_RELATION_CANDIDATE_PROOF":    0,
        "POSITIVE_RELATION_CLOSURE_PROOF":      0,
        "POSITIVE_IFADAH_PROOF":                0,
        "POSITIVE_HUKM_PROOF":                  0,
        "POSITIVE_ANSWER_AUDIT_PROOF":          0,
        "POSITIVE_CHAIN_ALL_TRANSITIONS_GATED": 0,
        "POSITIVE_CHAIN_HIDDEN_RESIDUALS":      0,
        "POSITIVE_CHAIN_FORBIDDEN_LEAPS":       0,
        "POSITIVE_CHAIN_GOLD_LEAKAGE":          0,
    }

    # ── Step 1: Verify no gold import ─────────────────────────────────────────
    print("\n── Step 1: Gold Leakage Guard ──")
    gold_module = "tests.evaluation.ayat_al_dayn_gold_corpus"
    if gold_module in sys.modules:
        print(f"  {FAIL} Gold corpus already imported — VIOLATION")
        b4_metrics["POSITIVE_CHAIN_GOLD_LEAKAGE"] = 1
        return 1
    print(f"  {PASS} Gold corpus not imported")

    # ── Step 2: Live Hokom execution (run_word per token) ─────────────────────
    print("\n── Step 2: Live Hokom Execution (P0-P8 per token via run_word) ──")
    relation_evidence: tuple = ()
    try:
        from hokom.canonical.pipeline import CanonicalPipeline, WordInput  # type: ignore
        from pipeline.execution_ledger.live_hokom_adapter import hokom_trace_to_token_ledger

        pipeline = CanonicalPipeline.build()

        # Run each token independently via run_word (P0-P8 word-level stages)
        word_traces = []
        for tok in POSITIVE_INPUT_TOKENS:
            word_input = WordInput(
                surface=tok["surface"],
                hokom_evidence_by_stage=tok["hokom_evidence_by_stage"],
                pipeline_run_id=POSITIVE_PIPELINE_RUN_ID,
                word_index=tok["index"],
            )
            trace = pipeline.run_word(word_input)
            word_traces.append(trace)

        b4_metrics["POSITIVE_HOKOM_LIVE_EXECUTION"] = 1

        # Check Taaqol native execution: bridge returned rank > 1 (not TRACE fallback)
        taaqol_native_used = False
        for trace in word_traces:
            for st in trace.all_stages:
                illah = getattr(st.judgment, 'illah', None)
                if illah is not None:
                    rank = getattr(illah, 'granted_rank', 0)
                    gate_id = str(getattr(illah, 'taaqol_gate_id', ''))
                    if rank > 1 and 'TAAQOL_IMPORT_FAILURE' not in gate_id:
                        taaqol_native_used = True
                        break
            if taaqol_native_used:
                break

        b4_metrics["POSITIVE_TAAQOL_NATIVE_EXECUTION"] = int(taaqol_native_used)

        # Build per-token ledger records (19 rows each via live adapter)
        all_records = []
        all_ledger_metrics = []
        for i, (tok, trace) in enumerate(zip(POSITIVE_INPUT_TOKENS, word_traces)):
            recs, metrics = hokom_trace_to_token_ledger(
                trace, analysis_id=f"B4-W{i:02d}"
            )
            all_records.extend(recs)
            all_ledger_metrics.append(metrics)

        total_ledger_rows = len(all_records)
        template_only_rows = sum(m.applicable_template_only_rows for m in all_ledger_metrics)

        # PROVENANCE CONTRACT: only real trace_ids from executed PipelineTrace stages accepted.
        # Synthetic fallback IDs are FORBIDDEN (EVIDENCE_PROVENANCE_CONTINUITY=0 if generated).
        # Strategy mirrors _extract_live_evidence(): P5 primary → all_stages scan fallback.
        verb_evidence: list[str] = []
        subj_evidence: list[str] = []
        for i, (trace, container) in enumerate(zip(word_traces, [verb_evidence, subj_evidence])):
            # Primary: P5_MUFRAD_WORD_CONTRACTS candidate_set.trace_ids
            p5_stage = trace.stages_by_id.get("P5_MUFRAD_WORD_CONTRACTS")
            if p5_stage is not None:
                cs = getattr(p5_stage, 'candidate_set', None)
                tids = list(getattr(cs, 'trace_ids', None) or [])
                if not tids:
                    tids = list(getattr(getattr(p5_stage, 'judgment', None), 'trace_ids', None) or [])
                container.extend(tids)
            # Fallback: scan all_stages for trace_ids — same path as _extract_live_evidence()
            if not container:
                for st in getattr(trace, 'all_stages', None) or []:
                    cs = getattr(st, 'candidate_set', None)
                    for tid in getattr(cs, 'trace_ids', None) or []:
                        if tid not in container:
                            container.append(tid)
            # No synthetic IDs generated here. Empty means genuinely absent.

        # evidence_residuals gates B4 — no synthetic fallback permitted.
        evidence_residuals: list[str] = []
        relation_evidence = tuple(verb_evidence + subj_evidence)
        if not relation_evidence:
            evidence_residuals.append("MISSING_HOKOM_TRACE_PROVENANCE")

        last_stages = [getattr(trace, 'last_stage', 'N/A') for trace in word_traces]

        _print_transition("Hokom Live Execution", {
            "SURFACE":                      POSITIVE_INPUT_SENTENCE,
            "TOKENS":                       len(POSITIVE_INPUT_TOKENS),
            "TRACES_BUILT":                 len(word_traces),
            "VERB_TRACE_LAST_STAGE":        last_stages[0] if last_stages else "N/A",
            "SUBJ_TRACE_LAST_STAGE":        last_stages[1] if len(last_stages) > 1 else "N/A",
            "TOTAL_LEDGER_ROWS":            total_ledger_rows,
            "APPLICABLE_TEMPLATE_ONLY":     template_only_rows,
            "TAAQOL_NATIVE_USED":           int(taaqol_native_used),
            "PIPELINE_RUN_ID":              POSITIVE_PIPELINE_RUN_ID,
            "EVIDENCE_IDS_VERB":            str(verb_evidence[:1]),
            "EVIDENCE_IDS_SUBJ":            str(subj_evidence[:1]),
            "NATIVE_EXECUTOR":              "hokom.canonical.pipeline.CanonicalPipeline.run_word",
            "OUTPUT_TYPE":                  "PipelineTrace × 2",
            "EVIDENCE_RESIDUALS":           str(evidence_residuals) if evidence_residuals else "none",
            "GATE_VERDICT":                 "PIPELINE_RUN_COMPLETE" if not evidence_residuals else "EVIDENCE_ABSENT",
        })

        if evidence_residuals:
            print(f"  {FAIL} No real trace_ids from PipelineTrace: {evidence_residuals}")
            print(f"       IFADAH gate cannot open — EVIDENCE_PROVENANCE_CONTINUITY=0")
            _print_b4_summary(b4_metrics)
            return 1

    except ImportError as e:
        print(f"  {FAIL} CanonicalPipeline not available: {e}")
        print(f"  NOTE: Requires Python 3.12.4 and hokom package")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"  {FAIL} Pipeline error: {e}")
        traceback.print_exc()
        return 1

    # ── Step 3: Clause detection ───────────────────────────────────────────────
    print("\n── Step 3: Clause Detection ──")
    try:
        from pipeline.clause_graph.segmenter import segment_into_clauses

        token_list = [
            {"surface": tok["surface"], "index": tok["index"]}
            for tok in POSITIVE_INPUT_TOKENS
        ]
        clauses = segment_into_clauses(token_list)
        b4_metrics["POSITIVE_CLAUSE_PROOF"] = 1

        _print_transition("Clause Detection", {
            "INPUT":            POSITIVE_INPUT_SENTENCE,
            "CLAUSE_COUNT":     len(clauses),
            "CLAUSE_IDS":       ", ".join(c.clause_id for c in clauses) if clauses else "none",
            "NATIVE_EXECUTOR":  "pipeline.clause_graph.segmenter.segment_into_clauses",
            "INPUT_TYPE":       "list[dict]",
            "OUTPUT_TYPE":      "list[ClauseCandidate]",
            "GATE_VERDICT":     "CLAUSE_DETECTED",
        })
    except Exception as e:
        print(f"  {FAIL} Clause detection error: {e}")
        traceback.print_exc()
        return 1

    # ── Step 4: Production relation inference (NOT direct carrier injection) ──────
    # DIRECT_CARRIER_INJECTION = 0: RelationCandidate must come from production module.
    # Constructing RelationCandidate manually here is FORBIDDEN per mandate §9.
    print("\n── Step 4: Production Relation Inference ──")
    relation_candidates: list = []
    try:
        from pipeline.relation_graph.inference import infer_relations_from_traces
        from pipeline.relation_graph.models import RelationClosureState

        token_surfaces = [tok["surface"] for tok in POSITIVE_INPUT_TOKENS]
        relation_candidates = infer_relations_from_traces(
            traces=word_traces,
            token_surfaces=token_surfaces,
            clause_candidate=clauses[0] if clauses else None,
            clause_id=POSITIVE_INPUT_CLAUSE_ID,
            pipeline_run_id=POSITIVE_PIPELINE_RUN_ID,
        )

        if not relation_candidates:
            print(f"  {FAIL} Production inference returned 0 candidates — B4 DEFERRED")
            b4_metrics["POSITIVE_RELATION_CANDIDATE_PROOF"] = 0
            _print_b4_summary(b4_metrics)
            return 1

        b4_metrics["POSITIVE_RELATION_CANDIDATE_PROOF"] = 1
        for rc in relation_candidates:
            _print_transition("Relation Candidate (production inference)", {
                "RELATION_ID":          rc.relation_id,
                "TYPE":                 str(rc.relation_type),
                "SOURCE":               rc.source_surface,
                "TARGET":               rc.target_surface,
                "CONFIDENCE_RANK":      rc.confidence_rank,
                "EVIDENCE_IDS":         str(rc.evidence_ids[:2]),
                "PRODUCTION_MODULE":    "pipeline.relation_graph.inference.infer_relations_from_traces",
                "DIRECT_INJECTION":     "0",
                "INPUT_TYPE":           "list[PipelineTrace] \u00d7 2 + ClauseCandidate",
                "OUTPUT_TYPE":          "list[RelationCandidate]",
                "GATE_VERDICT":         "RELATION_CANDIDATE",
            })
    except Exception as e:
        print(f"  {FAIL} Production inference error: {e}")
        traceback.print_exc()
        return 1

    # ── Step 5: Production relation closure ────────────────────────────────────
    # DIRECT_CARRIER_INJECTION = 0: closure_state must be set by close_relations(),
    # not by directly constructing RelationClosureResult with RELATION_CLOSED hardcoded.
    print("\n── Step 5: Production Relation Closure ──")
    closed_relation = None
    try:
        from pipeline.relation_graph.inference import close_relations
        from pipeline.relation_graph.models import RelationClosureState

        closed_relations_list = close_relations(
            candidates=relation_candidates,
            traces=word_traces,
            token_surfaces=[tok["surface"] for tok in POSITIVE_INPUT_TOKENS],
        )

        actually_closed = [
            r for r in closed_relations_list
            if r.closure_state == RelationClosureState.RELATION_CLOSED
            and r.required_argument_complete
        ]

        if not actually_closed:
            print(f"  {FAIL} No relations reached RELATION_CLOSED — live evidence insufficient")
            print(f"        candidates={len(relation_candidates)}, closed={len(actually_closed)}")
            for r in closed_relations_list:
                print(f"        {r.relation_id}: {r.closure_state}  req_arg={r.required_argument_complete}")
            _print_b4_summary(b4_metrics)
            return 1

        closed_relation = actually_closed[0]
        b4_metrics["POSITIVE_RELATION_CLOSURE_PROOF"] = 1

        _print_transition("Relation Closure (production close_relations)", {
            "RELATION_ID":                  closed_relation.relation_id,
            "CLOSURE_STATE":                str(closed_relation.closure_state),
            "REQUIRED_ARGUMENT_COMPLETE":   closed_relation.required_argument_complete,
            "SCOPE_CLOSED":                 closed_relation.scope_closed,
            "LICENSED_PARTIES":             str(closed_relation.licensed_parties),
            "EVIDENCE":                     str(closed_relation.evidence[:2]),
            "PRODUCTION_MODULE":            "pipeline.relation_graph.inference.close_relations",
            "DIRECT_INJECTION":             "0",
            "INPUT_TYPE":                   "list[RelationCandidate] + list[PipelineTrace]",
            "OUTPUT_TYPE":                  "RelationClosureResult",
            "GATE_VERDICT":                 "RELATION_CLOSED",
        })
    except Exception as e:
        print(f"  {FAIL} Relation closure error: {e}")
        traceback.print_exc()
        return 1

    # ── Step 6: Ifadah ────────────────────────────────────────────────────────
    print("\n── Step 6: Ifadah ──")
    try:
        from pipeline.vertical_chain.chain import build_ifadah
        from pipeline.vertical_chain.models import IfadahVerdict as _IV

        ifadah = build_ifadah(
            clause_id=POSITIVE_INPUT_CLAUSE_ID,
            relation_refs=(closed_relation.relation_id,),
            closed_relations=[closed_relation],   # genuinely RELATION_CLOSED
            evidence_ids=closed_relation.evidence,
        )

        ifadah_approved = (ifadah.verdict == _IV.IFADAH_APPROVED)
        b4_metrics["POSITIVE_IFADAH_PROOF"] = int(ifadah_approved)

        _print_transition("Ifadah", {
            "IFADAH_ID":            ifadah.ifadah_id,
            "CLAUSE_ID":            ifadah.clause_id,
            "PROPOSITION_SHAPE":    str(ifadah.proposition_shape),
            "CLOSURE_STATE":        str(ifadah.closure_state),
            "RANK":                 ifadah.rank,
            "EVIDENCE_IDS":         str(ifadah.evidence_ids[:2]),
            "ACTIVE_RESIDUALS":     str(ifadah.active_residuals),
            "VERDICT":              ifadah.verdict.value,
            "INPUT_TYPE":           "list[RelationClosureResult]",
            "OUTPUT_TYPE":          "IfadahCandidate",
            "NATIVE_EXECUTOR":      "pipeline.vertical_chain.chain.build_ifadah",
            "GATE_VERDICT":         ifadah.verdict.value,
        })
        if not ifadah_approved:
            print(f"  {FAIL} Ifadah not approved: {ifadah.stop_reason}")
            _print_b4_summary(b4_metrics)
            return 1
        print(f"  {PASS} IFADAH_APPROVED")
    except Exception as e:
        print(f"  {FAIL} Ifadah error: {e}")
        traceback.print_exc()
        return 1

    # ── Step 7: Hukm ──────────────────────────────────────────────────────────
    print("\n── Step 7: Hukm (LINGUISTIC_STRUCTURAL_CARRIER_NOT_FIQH_RULING) ──")
    try:
        from pipeline.vertical_chain.chain import build_hukm
        from pipeline.vertical_chain.models import HukmVerdict as _HV

        hukm = build_hukm(ifadah, modality="DECLARATIVE")
        hukm_approved = (hukm.verdict == _HV.HUKM_APPROVED)
        b4_metrics["POSITIVE_HUKM_PROOF"] = int(hukm_approved)

        _print_transition("Hukm", {
            "HUKM_ID":              hukm.hukm_id,
            "IFADAH_ID":            hukm.ifadah_id,
            "SUBJECT_REF":          str(hukm.subject_ref),
            "PREDICATE_REF":        str(hukm.predicate_ref),
            "POLARITY":             str(hukm.polarity),
            "MODALITY":             str(hukm.modality),
            "RANK":                 hukm.rank,
            "EVIDENCE_IDS":         str(hukm.evidence_ids[:2]),
            "RESIDUALS":            str(hukm.residuals),
            "VERDICT":              hukm.verdict.value,
            "CONSTITUTIONAL_NOTE":  str(hukm.constitutional_note),
            "INPUT_TYPE":           "IfadahCandidate(APPROVED)",
            "OUTPUT_TYPE":          "HukmCandidate",
            "NATIVE_EXECUTOR":      "pipeline.vertical_chain.chain.build_hukm",
            "GATE_VERDICT":         hukm.verdict.value,
        })
        if not hukm_approved:
            print(f"  {FAIL} Hukm not approved: {hukm.stop_reason}")
            _print_b4_summary(b4_metrics)
            return 1
        print(f"  {PASS} HUKM_APPROVED  [LINGUISTIC CARRIER — NOT FIQH RULING]")
    except Exception as e:
        print(f"  {FAIL} Hukm error: {e}")
        traceback.print_exc()
        return 1

    # ── Step 8: AnswerAudit ───────────────────────────────────────────────────
    print("\n── Step 8: AnswerAudit ──")
    try:
        from pipeline.vertical_chain.chain import build_answer_audit
        from pipeline.vertical_chain.models import AnswerAuditVerdict as _AAV

        chain_items = [
            {"type": "RelationClosureResult", "id": closed_relation.relation_id,
             "verdict": "RELATION_CLOSED"},
            {"type": "IfadahCandidate", "id": ifadah.ifadah_id,
             "verdict": ifadah.verdict.value},
            {"type": "HukmCandidate", "id": hukm.hukm_id,
             "verdict": hukm.verdict.value},
        ]

        # Forbidden leaps check
        forbidden_leaps: list[str] = []
        if not closed_relation.required_argument_complete:
            forbidden_leaps.append("DIRECT_TOKEN_TO_IFADAH_WITHOUT_ARGUMENT_COMPLETE")
        if hukm.ifadah_id != ifadah.ifadah_id:
            forbidden_leaps.append("HUKM_NOT_CHAINED_TO_IFADAH")
        b4_metrics["POSITIVE_CHAIN_FORBIDDEN_LEAPS"] = len(forbidden_leaps)

        # Unresolved residuals: surface all (hidden = 0)
        unresolved = list(hukm.residuals) + list(ifadah.active_residuals)
        b4_metrics["POSITIVE_CHAIN_HIDDEN_RESIDUALS"] = 0

        answer_audit = build_answer_audit(
            chain_items=chain_items,
            forbidden_leaps_found=forbidden_leaps,
            unresolved_residuals=unresolved,
        )
        audit_approved = (answer_audit.verdict == _AAV.ANSWER_AUDIT_APPROVED)
        b4_metrics["POSITIVE_ANSWER_AUDIT_PROOF"] = int(audit_approved)

        _print_transition("AnswerAudit", {
            "AUDIT_ID":                         answer_audit.audit_id,
            "CLAIM_PROVENANCE_VERIFIED":        answer_audit.claim_provenance_verified,
            "EVIDENCE_CONTINUITY_VERIFIED":     answer_audit.evidence_continuity_verified,
            "STAGE_CONTINUITY_VERIFIED":        answer_audit.stage_continuity_verified,
            "FORBIDDEN_LEAPS":                  str(answer_audit.forbidden_leaps),
            "UNRESOLVED_RESIDUALS":             str(answer_audit.unresolved_residuals),
            "LINGUISTIC_VS_RELIGIOUS_CLEAR":    answer_audit.linguistic_vs_religious_distinction_clear,
            "RANK_CEILING":                     answer_audit.rank_ceiling,
            "VERDICT":                          answer_audit.verdict.value,
            "INPUT_TYPE":                       "chain_items + forbidden_leaps + unresolved",
            "OUTPUT_TYPE":                      "AnswerAuditResult",
            "NATIVE_EXECUTOR":                  "pipeline.vertical_chain.chain.build_answer_audit",
            "GATE_VERDICT":                     answer_audit.verdict.value,
        })

        if not audit_approved:
            print(f"  {FAIL} AnswerAudit not approved: {answer_audit.stop_reason}")
            _print_b4_summary(b4_metrics)
            return 1
        print(f"  {PASS} ANSWER_AUDIT_APPROVED")

        b4_metrics["POSITIVE_CHAIN_ALL_TRANSITIONS_GATED"] = 1

    except Exception as e:
        print(f"  {FAIL} AnswerAudit error: {e}")
        traceback.print_exc()
        return 1

    # ── Final gold check ──────────────────────────────────────────────────────
    gold_module = "tests.evaluation.ayat_al_dayn_gold_corpus"
    if gold_module in sys.modules:
        b4_metrics["POSITIVE_CHAIN_GOLD_LEAKAGE"] = 1
        print(f"  {FAIL} Gold corpus imported during proof run — VIOLATION")
        _print_b4_summary(b4_metrics)
        return 1

    _print_b4_summary(b4_metrics)
    return 0


def _print_b4_summary(b4_metrics: dict) -> None:
    print(f"\n{SEP}")
    print("B4 SUMMARY")
    print(SEP)
    all_ok = True
    for key, val in b4_metrics.items():
        marker = PASS
        if key in ("POSITIVE_CHAIN_HIDDEN_RESIDUALS", "POSITIVE_CHAIN_FORBIDDEN_LEAPS",
                   "POSITIVE_CHAIN_GOLD_LEAKAGE"):
            ok = val == 0
        else:
            ok = val == 1
        if not ok:
            marker = FAIL
            all_ok = False
        print(f"  {marker} {key} = {val}")

    print()
    if all_ok:
        print(f"  {PASS} B4_CLOSED = 1")
    else:
        print(f"  {FAIL} B4_CLOSED = 0")


if __name__ == "__main__":
    sys.exit(main())
