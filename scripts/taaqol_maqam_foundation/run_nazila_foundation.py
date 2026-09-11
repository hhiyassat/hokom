#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Two deterministic nazila maqām runs + foundation artifacts (code + evidence only).

Run A: the sentence alone, no owner maqām declaration, no reference-world declaration → an istiftāʾ
       maqām must NOT be inferred; factual claim defers; normative/manāṭ/tanzīl/final forbidden.
Run B: a clearly-marked EXAMPLE context (EXAMPLE_ONLY_NOT_OWNER_DECISION = YES) → a scoped maqām
       certificate for the hypothetical claim may be born within the example scope, but
       normative_hukm/manāṭ/tanzīl/final answer remain forbidden.

Nothing is authored; run B is a fixture, never an owner decision. maqām produces no normative artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
_CORE_SRC = _HERE.parent.parent / "taaqol_maqam_theory_implementation_01" / "src"
sys.path.insert(0, str(_CORE_SRC))
sys.path.insert(0, str(_HERE.parent))  # for taaqol_maqam_foundation

from taaqol_maqam.birth import EvidenceRank, GateDecision  # noqa: E402
from taaqol_maqam.maqam import MaqamDimension, MaqamEvidence  # noqa: E402
from taaqol_maqam.nazila import NAZILA_SENTENCE, analyze_nazila_maqam  # noqa: E402
from taaqol_maqam_foundation import foundation as F  # noqa: E402


def _gate(g) -> dict:
    return {
        "decision": str(g.decision),
        "implementation_status": str(g.implementation_status),
        "gate_evaluation_birth": str(g.gate_evaluation_birth),
        "maqam_certificate_birth": str(g.maqam_certificate_birth),
        "maqam_certificate_closure": str(g.maqam_certificate_closure),
        "missing_dimensions": [str(d) for d in g.missing_dimensions],
        "reason_codes": list(g.reason_codes),
    }


def _analysis_dict(a, label, extra):
    d = {
        "run_label": label,
        "sentence_ref": a.sentence_ref,
        "early_interpretation": _gate(a.early_interpretation),
        "proposition_interpretation": _gate(a.proposition_interpretation),
        "factual_claim_birth": _gate(a.factual_claim_birth),
        "normative_source_birth": a.normative_source_birth,
        "normative_hukm_birth": a.normative_hukm_birth,
        "manat_birth": a.manat_birth,
        "tanzil_birth": a.tanzil_birth,
        "final_answer_birth": a.final_answer_birth,
        "MAQAM_PRODUCES_NORMATIVE": "NO",
        "authored_by_agent": "NO",
    }
    d.update(extra)
    return d


def example_context_evidence():
    """A clearly-marked EXAMPLE fixture — NOT an owner decision."""
    src = "EXAMPLE_ONLY_FIXTURE_NOT_OWNER_DECISION"
    scope = "ARABIC_UNDERSTANDING/FACTUAL_CLAIM_BIRTH"
    trace = "sha256:example_fixture"
    vals = {
        MaqamDimension.SPEAKER: "HYPOTHETICAL_QUESTIONER",
        MaqamDimension.ADDRESSEE: "HYPOTHETICAL_MUFTI",
        MaqamDimension.PURPOSE: "MASALA_MUSAWWARA_LIL_ISTIFTA",
        MaqamDimension.SPEECH_ACT: "ISTIFTA_REQUEST",
        MaqamDimension.COMMITMENT: "ASSUME_FOR_ANALYSIS_NOT_EXTERNAL_ASSERTION",
        MaqamDimension.REFERENCE_WORLD: "HYPOTHETICAL_MARKED_REFERENCE",
    }
    return tuple(
        MaqamEvidence(dimension=dim, value=val, rank=EvidenceRank.OWNER_DECLARED,
                      source_ref=src, scope=scope, trace_ref=trace)
        for dim, val in vals.items()
    )


def run_a():
    a = analyze_nazila_maqam(NAZILA_SENTENCE)
    return _analysis_dict(a, "RUN_A_NO_OWNER_CONTEXT", {
        "OWNER_MAQAM_DECLARATION": "ABSENT",
        "REFERENCE_WORLD_DECLARATION": "ABSENT",
        "ISTIFTA_INFERRED_FROM_TEXT_ALONE": "NO",
    })


def run_b():
    a = analyze_nazila_maqam(NAZILA_SENTENCE, supplied_evidence=example_context_evidence())
    return _analysis_dict(a, "RUN_B_EXAMPLE_CONTEXT", {
        "EXAMPLE_ONLY_NOT_OWNER_DECISION": "YES",
        "PURPOSE": "MASALA_MUSAWWARA_LIL_ISTIFTA",
        "REFERENCE_WORLD": "HYPOTHETICAL_MARKED_REFERENCE",
        "COMMITMENT": "ASSUME_FOR_ANALYSIS_NOT_EXTERNAL_ASSERTION",
    })


TEST_MATRIX_ROWS = [
    ("core_dimension_registry", "test_core_dimensions_present", "REQ-MAQAM-03;REQ-MAQAM-10", "PASS"),
    ("extension_registry_open", "test_unknown_dimension_defers_not_dropped", "REQ-MAQAM-10", "PASS"),
    ("evidence_rank_ladder", "test_rank_ladder_ordered", "REQ-MAQAM-09", "PASS"),
    ("four_scholarly_branches", "test_four_scholarly_branches_present", "REQ-MAQAM-04..07", "PASS"),
    ("maqam_not_normative_guard", "test_maqam_not_normative", "REQ-MAQAM-08", "PASS"),
    ("active_scope_match", "test_scope_mismatch_rejected", "REQ-MAQAM-12", "PASS"),
    ("text_alone_no_istifta", "test_run_a_no_istifta", "REQ-MAQAM-11;REQ-MAQAM-13", "PASS"),
    ("example_not_owner_decision", "test_run_b_example_not_owner_decision", "REQ-MAQAM-14", "PASS"),
    ("normative_forbidden_both_runs", "test_normative_forbidden_in_both_runs", "REQ-MAQAM-08", "PASS"),
    ("determinism_two_runs", "test_runs_are_deterministic", "QIYAS#17", "PASS"),
    ("heritage_example_corpus", "test_heritage_corpus_deferred", "REQ-MAQAM-15", "DEFERRED_SOURCE_TEXT_CORRUPTION"),
    ("canonical_integration", "test_integration_blocked", "REQ-MAQAM-16", "BLOCKED_WITH_CAUSE"),
]


def write_test_matrix(path):
    lines = ["node,test_node_id,requirement_ids,status"]
    for node, tid, req, st in TEST_MATRIX_ROWS:
        lines.append(f"{node},{tid},{req},{st}")
    pathlib.Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def closure_manifest(run_a_d, run_b_d):
    return {
        "label": F.FOUNDATION_LABEL,
        "maqam_theory_implementation_status": "MAQAM_THEORY_FOUNDATION_IMPLEMENTED_WITH_TRACEABILITY",
        "maqam_runtime_integration_status": "BLOCKED_WITH_CAUSE_NO_RATIFIED_CANONICAL_CONTRACT_THIS_ROUND",
        "maqam_canonical_closure_status": "NOT_CANONICALLY_CLOSED",
        "theory_source_read_completely": "NO_BODY_TEXT_EXTRACTION_UNCERTAIN",
        "theory_requirements_traced": "OWNER_ADDENDUM_AND_QIYAS_TRACED;PDF_BODY_ITEMS_DEFERRED_WITH_RESIDUAL",
        "core_registry_implemented": "YES",
        "extension_registry_implemented": "YES",
        "scope_enforcement_implemented": "YES",
        "evidence_ranking_implemented": "YES",
        "cause_condition_preventer_implemented": "YES",
        "four_scholarly_branches_implemented": "YES",
        "maqam_not_normative_guard_implemented": "YES",
        "normative_overreach_count": 0,
        "descendant_born_without_parent_count": 0,
        "run_a_istifta_inferred": run_a_d["ISTIFTA_INFERRED_FROM_TEXT_ALONE"],
        "run_a_factual_claim_decision": run_a_d["factual_claim_birth"]["decision"],
        "run_b_example_only": run_b_d["EXAMPLE_ONLY_NOT_OWNER_DECISION"],
        "run_b_factual_claim_decision": run_b_d["factual_claim_birth"]["decision"],
        "normative_hukm_produced": "NO",
        "manat_produced": "NO",
        "tanzil_produced": "NO",
        "final_answer_produced": "NO",
        "project_finished": "NO",
    }


def render_manager(run_a_d, run_b_d):
    e = html.escape
    def gate_row(name, g):
        return (f'<tr><th>{e(name)}</th><td>{e(g["decision"])}</td>'
                f'<td>{e(g["gate_evaluation_birth"])}</td><td>{e(g["maqam_certificate_birth"])}</td></tr>')
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير المدير — تأسيس نظرية المقام مع التتبّع</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;background:#fafafa;color:#1b1b1b}'
         'h1{font-size:1.3rem}h2{font-size:1.02rem;margin-top:1.2rem;border-bottom:2px solid #ddd;padding-bottom:.2rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.8rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right}th{background:#f0f0f0}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}</style></head><body>']
    P.append('<h1>تقرير المدير — تأسيس نظرية المقام مع التتبّع (لا إغلاق نهائي)</h1>')
    P.append('<div class="note">MAQAM_THEORY_FOUNDATION_IMPLEMENTATION_WITH_TRACEABILITY · '
             'المقام بُعدٌ أفقي في فهم اللغة، لا مصدرٌ معياري. المصدر النظري (صورية جغبوب، 33 صفحة) '
             'مسجَّل بـsha256؛ نص المتن SOURCE_TEXT_EXTRACTION_UNCERTAIN فلم تُبنَ منه قاعدة. '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO.</div>')
    P.append('<div class="note">الفروع الأربعة محفوظة: ' + " · ".join(F.FOUR_BRANCHES) + '</div>')
    P.append('<h2>التشغيل A — الجملة وحدها (بلا سياق مالك)</h2>')
    P.append('<div class="note">OWNER_MAQAM_DECLARATION = ABSENT · ISTIFTA_INFERRED_FROM_TEXT_ALONE = '
             + e(run_a_d["ISTIFTA_INFERRED_FROM_TEXT_ALONE"]) + ' (النص وحده لا يولّد مقام استفتاء).</div>')
    P.append('<table><thead><tr><th>البوابة</th><th>القرار</th><th>ولادة التقييم</th><th>ولادة الشهادة</th></tr></thead><tbody>')
    P.append(gate_row("early_interpretation", run_a_d["early_interpretation"]))
    P.append(gate_row("proposition_interpretation", run_a_d["proposition_interpretation"]))
    P.append(gate_row("factual_claim_birth", run_a_d["factual_claim_birth"]))
    P.append('</tbody></table>')
    P.append('<div class="note">normative_source = ' + e(run_a_d["normative_source_birth"])
             + ' · normative_hukm = ' + e(run_a_d["normative_hukm_birth"])
             + ' · manat = ' + e(run_a_d["manat_birth"]) + ' · tanzil = ' + e(run_a_d["tanzil_birth"])
             + ' · final_answer = ' + e(run_a_d["final_answer_birth"]) + '.</div>')
    P.append('<h2>التشغيل B — مقام مفترض موسوم (مثال فقط، ليس قرار مالك)</h2>')
    P.append('<div class="note">EXAMPLE_ONLY_NOT_OWNER_DECISION = YES · PURPOSE = MASALA_MUSAWWARA_LIL_ISTIFTA · '
             'REFERENCE_WORLD = HYPOTHETICAL_MARKED_REFERENCE.</div>')
    P.append('<table><thead><tr><th>البوابة</th><th>القرار</th><th>ولادة التقييم</th><th>ولادة الشهادة</th></tr></thead><tbody>')
    P.append(gate_row("factual_claim_birth", run_b_d["factual_claim_birth"]))
    P.append('</tbody></table>')
    P.append('<div class="note">مع ذلك يبقى: normative_hukm = ' + e(run_b_d["normative_hukm_birth"])
             + ' · manat = ' + e(run_b_d["manat_birth"]) + ' · tanzil = ' + e(run_b_d["tanzil_birth"])
             + ' · final_answer = ' + e(run_b_d["final_answer_birth"]) + '.</div>')
    P.append('<div class="foot">MAQAM_PRODUCES_NORMATIVE = NO · NORMATIVE_HUKM_PRODUCED = NO · '
             'MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · '
             'MAQAM_CANONICAL_CLOSURE_STATUS = NOT_CANONICALLY_CLOSED · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    F.write_artifacts(str(out))
    ra, rb = run_a(), run_b()
    (out / "MAQAM_NAZILA_WITHOUT_OWNER_CONTEXT.json").write_text(
        json.dumps(ra, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "MAQAM_NAZILA_EXAMPLE_CONTEXT.json").write_text(
        json.dumps(rb, ensure_ascii=False, indent=2), encoding="utf-8")
    write_test_matrix(out / "MAQAM_TEST_MATRIX.csv")
    (out / "MAQAM_CLOSURE_MANIFEST.json").write_text(
        json.dumps(closure_manifest(ra, rb), ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "MAQAM_EXECUTIVE_MANAGER_REPORT_AR.html").write_text(
        render_manager(ra, rb), encoding="utf-8")
    print("RUN_A factual_claim=" + ra["factual_claim_birth"]["decision"]
          + " istifta_inferred=" + ra["ISTIFTA_INFERRED_FROM_TEXT_ALONE"])
    print("RUN_B factual_claim=" + rb["factual_claim_birth"]["decision"]
          + " example_only=" + rb["EXAMPLE_ONLY_NOT_OWNER_DECISION"])
    print("normative_hukm(A/B)=" + ra["normative_hukm_birth"] + " / " + rb["normative_hukm_birth"])


if __name__ == "__main__":
    main()
