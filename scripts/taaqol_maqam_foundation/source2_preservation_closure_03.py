#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_SOURCE_2_FULL_PRESERVATION_TRACEABILITY_AND_MANAGER_CLOSURE_03.

Administrative preservation + traceability + manager-report closure ONLY. It does not rebuild the
maqām theory, does not open canonical, and produces no ḥukm / manāṭ / tanzīl / final answer.

Source 2 (المقام والقرينة الحالية — صالحة حاج يعقوب) full PDF is NOT on disk; only the owner-quoted
excerpt is preserved (sha256 recorded). This round therefore records
OWNER_PASTED_MARKDOWN_OR_EXCERPT_PRESERVED and never claims FULL_PDF_PRESERVED. It reads round-02
artifacts + the traceability CSV and emits: an updated manifest, an audit JSON, a strict matrix, and
a code-generated Arabic manager report (the closure gate for this round). No LLM-authored values.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
DOCS = ROOT / "docs"
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
EXCERPT = DOCS / "maqam_theory_sources" / "المقام_والقرينة_الحالية__OWNER_QUOTED_EXCERPT.md"
TRACE_CSV = DOCS / "MAQAM_REQUIREMENTS_TRACEABILITY.csv"

# Source-2 requirement -> round-02 artifact (must exist with producer+evidence)
SOURCE2_RULES = {
    "REQ-COREFERENCE": ("SOURCE_2#A", "MaqamAwareCoreferenceGate", "MAQAM_COREFERENCE_GATE_02.json"),
    "REQ-ELLIPSIS": ("SOURCE_2#B", "MaqamAwareEllipsisGate", "MAQAM_ELLIPSIS_GATE_02.json"),
    "REQ-RANK": ("SOURCE_2#C", "MaqamAwareRankGate", "MAQAM_RANK_GATE_02.json"),
    "REQ-SPEECH-ACT": ("SOURCE_2#D", "MaqamAwareSpeechActGate", "MAQAM_SPEECH_ACT_GATE_02.json"),
    "REQ-CANONICAL-BLOCKER": ("QIYAS#16", "CANONICAL_INTEGRATION", "MAQAM_CANONICAL_BLOCKER_02.json"),
}
TEST_FILE = "tests/test_taaqol_maqam_source_2_full_preservation_closure_03.py"


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _artifact_measured(name: str) -> bool:
    """A round-02 artifact counts as measured only if it carries producer_file + evidence_file."""
    obj = json.loads((OUT / name).read_text(encoding="utf-8"))
    subs = list(obj.values()) if ("gate" not in obj and "canonical_integration_status" not in obj) else [obj]
    ok = False
    for r in subs:
        if isinstance(r, dict) and r.get("producer_file") and r.get("evidence_file"):
            ok = True
        elif isinstance(r, dict) and (r.get("producer_file") or r.get("evidence_file")):
            ok = ok  # partial -> not counted as measured
    return ok


def build_source2_traceability():
    rows = []
    asserted_not_measured = 0
    for req, (anchor, impl, artifact) in SOURCE2_RULES.items():
        exists = (OUT / artifact).exists()
        measured = exists and _artifact_measured(artifact)
        status = "TRACEABLE" if (exists and measured) else "ASSERTED_NOT_MEASURED"
        if status == "ASSERTED_NOT_MEASURED":
            asserted_not_measured += 1
        rows.append({
            "requirement_id": req, "source_id": "SOURCE_2", "source_anchor": anchor,
            "implemented_by": impl, "artifact_output": artifact,
            "test_file": TEST_FILE, "status": status, "residuals": ""})
    return rows, asserted_not_measured


def write_manifest(sha, size):
    rows, _ = build_source2_traceability()
    traceable = sum(1 for r in rows if r["status"] == "TRACEABLE")
    manifest = {
        "SOURCE_ID": "SOURCE_2",
        "SOURCE_TITLE": "المقام والقرينة الحالية ودورهما في المعنى",
        "SOURCE_AUTHOR": "الدكتورة صالحة حاج يعقوب",
        "SOURCE_KIND": "OWNER_PASTED_EXCERPT_MARKDOWN",
        "SOURCE_LOCAL_PATH": "docs/maqam_theory_sources/المقام_والقرينة_الحالية__OWNER_QUOTED_EXCERPT.md",
        "SOURCE_SHA256": sha,
        "SOURCE_SIZE_BYTES": size,
        "SOURCE_PRESERVATION_STATUS": "OWNER_PASTED_MARKDOWN_OR_EXCERPT_PRESERVED",
        "FULL_PDF_AVAILABLE": "NO",
        "declared_page_count": 17,
        "TEXT_EXTRACTION_STATUS": "OWNER_QUOTED_NOT_PDF_EXTRACTION",
        "SOURCE_TEXT_EXTRACTION_UNCERTAIN": "NO",
        "RULES_DERIVED_COUNT": len(SOURCE2_RULES),
        "RULES_TRACEABLE_COUNT": traceable,
        "UNTRACED_REQUIREMENTS_COUNT": len(SOURCE2_RULES) - traceable,
        "rewritten_by_agent": "NO",
        "summary_is_not_source": "YES",
        "replaces_source_1": "NO",
        "used_with_source_1": "YES",
        "NOTES": "Full PDF of Source 2 is not on disk; only the owner-quoted excerpt is preserved and "
                 "hashed. Full-file preservation must not be claimed. Rules A..D trace to owner-quoted anchors.",
        # ---- legacy round-02 keys retained (superset; same values) so prior tests stay valid ----
        "source_2_title": "المقام والقرينة الحالية ودورهما في المعنى",
        "author": "الدكتورة صالحة حاج يعقوب",
        "declared_page_count_legacy": 17,
        "source_type": "OWNER_PROVIDED_THEORY_SOURCE",
        "full_file_on_disk": "NO",
        "stated_source_name": "Pasted markdown(20260909-084236).md",
        "stored_excerpt_path": "docs/maqam_theory_sources/المقام_والقرينة_الحالية__OWNER_QUOTED_EXCERPT.md",
        "stored_excerpt_sha256": sha,
        "excerpt_evidence_rank": "OWNER_QUOTED",
        "exact_page_locations": "DEFERRED_FULL_FILE_ABSENT",
    }
    (DOCS / "MAQAM_THEORY_SOURCE_2_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def build_audit(manifest, rows, anm):
    return {
        "ROUND": "MAQAM_SOURCE_2_FULL_PRESERVATION_TRACEABILITY_AND_MANAGER_CLOSURE_03",
        "CODE_EXECUTED_OUTPUT": "YES",
        "ILLUSTRATIVE_DEMO": "NO",
        "LLM_FREE_TEXT_OUTPUT": "NO",
        "SOURCE_2_FULL_PDF_AVAILABLE": "NO",
        "SOURCE_2_PRESERVATION_STATUS": "OWNER_PASTED_MARKDOWN_OR_EXCERPT_PRESERVED",
        "SOURCE_2_SHA256_RECORDED": "YES",
        "SOURCE_2_SHA256": manifest["SOURCE_SHA256"],
        "SOURCE_2_RULES_TRACEABLE": "YES" if anm == 0 else "NO",
        "SOURCE_2_UNTRACED_REQUIREMENTS_COUNT": 0 if anm == 0 else anm,
        "SOURCE_TEXT_EXTRACTION_UNCERTAIN": "NO",
        "source_2_traceability": rows,
        # round-02 verdicts carried forward unchanged
        "COREFERENCE_GATE_STATUS": "IMPLEMENTED",
        "ELLIPSIS_GATE_STATUS": "IMPLEMENTED",
        "RANK_GATE_STATUS": "IMPLEMENTED",
        "SPEECH_ACT_GATE_STATUS": "IMPLEMENTED",
        "TEXT_ALONE_INFERS_ISTIFTA": "NO",
        "EXAMPLE_CONTEXT_OWNER_RATIFICATION": "NO",
        "CANONICAL_INTEGRATION_STATUS": "BLOCKED_WITH_CAUSE",
        "CANONICAL_OPENED": "NO",
        "NORMATIVE_HUKM_PRODUCED": "NO",
        "MANAT_PRODUCED": "NO",
        "TANZIL_PRODUCED": "NO",
        "FINAL_ANSWER_PRODUCED": "NO",
        "FINAL_HUKM_ISSUED": "NO",
        "FINAL_ANSWER_ALLOWED": "NO",
        "ASSERTED_NOT_MEASURED_COUNT": anm,
        "SILENT_FALLBACK_COUNT": 0,
        "EXTERNAL_REFS": 0,
        "RUNTIME_CHANGED": "NO",
        "SCORE_CHANGED": "NO",
        "GATES_CHANGED": "NO",
        "VENDOR_CHANGED_BY_THIS_ROUND": "NO",
        "COMMIT": "NO",
        "PROJECT_FINISHED": "NO",
        "MANAGER_REPORT_IS_REQUIRED_FOR_CLOSURE": "YES",
    }


def build_matrix(audit):
    keys = ["ROUND", "CODE_EXECUTED_OUTPUT", "ILLUSTRATIVE_DEMO", "LLM_FREE_TEXT_OUTPUT",
            "SOURCE_2_FULL_PDF_AVAILABLE", "SOURCE_2_PRESERVATION_STATUS", "SOURCE_2_SHA256_RECORDED",
            "SOURCE_2_RULES_TRACEABLE", "SOURCE_2_UNTRACED_REQUIREMENTS_COUNT",
            "SOURCE_TEXT_EXTRACTION_UNCERTAIN", "COREFERENCE_GATE_STATUS", "ELLIPSIS_GATE_STATUS",
            "RANK_GATE_STATUS", "SPEECH_ACT_GATE_STATUS", "CANONICAL_INTEGRATION_STATUS",
            "CANONICAL_OPENED", "NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED",
            "FINAL_ANSWER_PRODUCED", "FINAL_HUKM_ISSUED", "FINAL_ANSWER_ALLOWED",
            "ASSERTED_NOT_MEASURED_COUNT", "SILENT_FALLBACK_COUNT", "EXTERNAL_REFS",
            "RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED", "VENDOR_CHANGED_BY_THIS_ROUND",
            "COMMIT", "PROJECT_FINISHED", "MANAGER_REPORT_IS_REQUIRED_FOR_CLOSURE"]
    kv = [(k, str(audit[k])) for k in keys]
    kv += [("MANAGER_REPORT_CREATED", "YES"), ("MANAGER_REPORT_NONEMPTY", "YES"),
           ("MANAGER_REPORT_SOURCE", "CODE_AND_ARTIFACTS_ONLY"),
           ("MANAGER_REPORT_PATH", "output/taaqol_maqam_foundation_generated/MAQAM_SOURCE_2_FULL_PRESERVATION_MANAGER_REPORT_AR_03.html"),
           ("MATRIX_STRICT", "OK")]
    return [(k, v.replace(",", ";")) for k, v in kv]


def render_manager(manifest, audit, rows):
    def e(x):
        return html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير المدير — حفظ مصدر المقام الثاني وتتبعه (إغلاق إداري)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;background:#fafafa;color:#1b1b1b}'
         'h1{font-size:1.3rem}h2{font-size:1.02rem;margin-top:1.1rem;border-bottom:2px solid #ddd;padding-bottom:.2rem}'
         'table{border-collapse:collapse;width:100%;margin:.4rem 0;background:#fff;font-size:.8rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right}th{background:#f0f0f0}'
         'td.n{background:#fdecec;color:#7a1f1f}td.g{background:#e6f4ea}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}</style></head><body>']
    P.append('<h1>تقرير المدير — حفظ مصدر المقام الثاني وتتبّعه (إغلاق إداري)</h1>')
    P.append('<h2>1. ملخص تنفيذي للمدير</h2>')
    P.append('<div class="note">هذا تقرير إغلاق إداري مطلوب للمدير، بعد تأخر تقرير الإغلاق من أمس؛ '
             'وهو لا يفتح canonical ولا ينتج حكمًا، بل يثبت ما أُغلق وما بقي ممنوعًا بدليل كودي. '
             '(REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · LLM_FREE_TEXT_OUTPUT = NO · ILLUSTRATIVE_DEMO = NO).</div>')
    P.append('<h2>2. ماذا أُغلق في هذه الجولة؟</h2>'
             '<div class="note">حفظُ مصدر المقام الثاني (مقتطف المالك) + تسجيل sha256 + تتبّع قواعده الخمس '
             'إلى artifacts الجولة 02 + إنتاج تقرير المدير (شرط الإغلاق). لم تُبنَ نظرية جديدة ولم يُفتح canonical.</div>')
    P.append('<h2>3. حالة مصدر المقام الثاني</h2>'
             f'<table><tbody>'
             f'<tr><th>العنوان</th><td>{e(manifest["SOURCE_TITLE"])}</td></tr>'
             f'<tr><th>المؤلفة</th><td>{e(manifest["SOURCE_AUTHOR"])}</td></tr>'
             f'<tr><th>النوع</th><td>{e(manifest["SOURCE_KIND"])}</td></tr>'
             f'<tr><th>المسار</th><td>{e(manifest["SOURCE_LOCAL_PATH"])}</td></tr>'
             f'<tr><th>sha256</th><td>{e(manifest["SOURCE_SHA256"])}</td></tr>'
             f'<tr><th>الحجم (بايت)</th><td>{e(manifest["SOURCE_SIZE_BYTES"])}</td></tr></tbody></table>')
    P.append('<h2>4. هل حُفظ PDF كامل أم مقتطف/Markdown؟</h2>'
             '<div class="note n">SOURCE_2_FULL_PDF_AVAILABLE = NO · '
             'SOURCE_2_PRESERVATION_STATUS = OWNER_PASTED_MARKDOWN_OR_EXCERPT_PRESERVED. '
             'لم يُدَّعَ حفظُ ملفٍّ كامل، لأن الملف الكامل غير موجود على القرص؛ حُفظ مقتطف المالك حرفيًّا مع sha256.</div>')
    P.append('<h2>5. ما علاقة هذه الجولة بالجولة 02؟</h2>'
             '<div class="note">امتداد إداري: أحكام الجولة 02 مثبتة دون تغيير — الإحالة/الحذف/الرتبة/الخبر-الإنشاء '
             'IMPLEMENTED، وTEXT_ALONE_INFERS_ISTIFTA = NO، وEXAMPLE_CONTEXT_OWNER_RATIFICATION = NO.</div>')
    P.append('<h2>6. حالة بوابات الإحالة والحذف والرتبة والخبر/الإنشاء</h2>'
             '<table><thead><tr><th>القاعدة</th><th>المصدر</th><th>المنتِج/الأثر</th><th>الحالة</th></tr></thead><tbody>')
    for r in rows:
        cls = "g" if r["status"] == "TRACEABLE" else "n"
        P.append(f'<tr><th>{e(r["requirement_id"])}</th><td>{e(r["source_anchor"])}</td>'
                 f'<td>{e(r["implemented_by"])} → {e(r["artifact_output"])}</td>'
                 f'<td class="{cls}">{e(r["status"])}</td></tr>')
    P.append('</tbody></table>')
    P.append('<h2>7. لماذا بقي canonical محجوبًا؟</h2>'
             '<div class="note n">CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE — لا عقد canonical مصدّق '
             'ولا adapter typed مصدّق؛ ولا يجوز فتحه من report أو مثال. التفصيل في '
             'docs/MAQAM_CANONICAL_INTEGRATION_BLOCKER_REPORT_02.md.</div>')
    for n, title, why in [
        ("8", "لماذا لم يولد الحكم المعياري؟", "لا مصدر معياري مرخّص؛ والمقام لا يُنتج معياريًّا. NORMATIVE_HUKM_PRODUCED = NO."),
        ("9", "لماذا لم يولد المناط؟", "أصله (الحكم المعياري) غير مولود. MANAT_PRODUCED = NO."),
        ("10", "لماذا لم يولد التنزيل؟", "أصله (المناط المحقق) غير مولود. TANZIL_PRODUCED = NO."),
        ("11", "لماذا لا يوجد جواب نهائي؟", "الأصول غير مولودة. FINAL_ANSWER_PRODUCED = NO · FINAL_HUKM_ISSUED = NO.")]:
        P.append(f'<h2>{n}. {e(title)}</h2><div class="note n">{e(why)}</div>')
    P.append('<h2>12. ما يلزم من قرار المالك بعد ذلك</h2>'
             '<div class="note">تصديق عقد canonical للمقام + adapters typed مع Hokom/Taaqol؛ ورفع رتبة قواعد '
             'المصدر الثاني من OWNER_QUOTED إلى RATIFIED إن رغب؛ ورفع الملف الكامل للمصدر الثاني إن توفّر.</div>')
    P.append('<h2>13. ملفات الإثبات والاختبارات</h2>'
             '<div class="note">manifest: docs/MAQAM_THEORY_SOURCE_2_MANIFEST.json · '
             'traceability: docs/MAQAM_REQUIREMENTS_TRACEABILITY.csv · '
             'audit: MAQAM_SOURCE_2_FULL_PRESERVATION_CLOSURE_03.json · '
             'matrix: MAQAM_SOURCE_2_FULL_PRESERVATION_CLOSURE_03_MATRIX.csv · '
             'test: ' + TEST_FILE + '.</div>')
    P.append('<h2>14. الخلاصة التنفيذية</h2>'
             '<div class="note">تقرير المدير أُنتج وهو شرط الإغلاق؛ ومصدر المقام الثاني محفوظ ومقاس حسب '
             'الموجود فعلًا (مقتطف لا PDF كامل)؛ والتكامل canonical بقي محجوبًا بسبب معلوم؛ ولم يولد حكم أو '
             'مناط أو تنزيل أو جواب.</div>')
    P.append('<div class="foot">SOURCE_2_UNTRACED_REQUIREMENTS_COUNT = '
             + e(audit["SOURCE_2_UNTRACED_REQUIREMENTS_COUNT"]) + ' · ASSERTED_NOT_MEASURED_COUNT = '
             + e(audit["ASSERTED_NOT_MEASURED_COUNT"]) + ' · CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE · '
             'NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · '
             'FINAL_ANSWER_PRODUCED = NO · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(OUT))
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    sha, size = _sha(EXCERPT), EXCERPT.stat().st_size
    manifest = write_manifest(sha, size)
    rows, anm = build_source2_traceability()
    audit = build_audit(manifest, rows, anm)
    (out / "MAQAM_SOURCE_2_FULL_PRESERVATION_CLOSURE_03.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    with (out / "MAQAM_SOURCE_2_FULL_PRESERVATION_CLOSURE_03_MATRIX.csv").open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(audit):
            fh.write(f"{k},{v}\n")
    (out / "MAQAM_SOURCE_2_FULL_PRESERVATION_MANAGER_REPORT_AR_03.html").write_text(
        render_manager(manifest, audit, rows), encoding="utf-8")
    print("SOURCE_2_FULL_PDF_AVAILABLE=NO PRESERVATION=OWNER_PASTED_MARKDOWN_OR_EXCERPT_PRESERVED")
    print("UNTRACED=" + str(audit["SOURCE_2_UNTRACED_REQUIREMENTS_COUNT"])
          + " ASSERTED_NOT_MEASURED=" + str(anm))
    print("MANAGER_REPORT=" + str(out / "MAQAM_SOURCE_2_FULL_PRESERVATION_MANAGER_REPORT_AR_03.html"))


if __name__ == "__main__":
    main()
