#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_SOURCE_TO_MASALA_MAPPING_GATE_18 — guard test.

Structural-only mapping of the round-17 born sources to nazila masʾala segments. No ḥukm/manāṭ/tanzīl/
answer, no new source, no composite collapse, no source-alone ruling, no agent ratification, no live
links, EXTERNAL_REFS=0. Sukna/possession gap recorded. Manager report obeys AR_09_FIXED. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
MAP = OUT / "SOURCE_TO_MASALA_MAPPING_18.json"
GUARDS = OUT / "SOURCE_TO_MASALA_MAPPING_GUARDS_18.json"
RESID = OUT / "SOURCE_TO_MASALA_MAPPING_RESIDUALS_18.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_19.md"
MATRIX = OUT / "SOURCE_TO_MASALA_MAPPING_18_MATRIX.csv"
REPORT = OUT / "SOURCE_TO_MASALA_MAPPING_MANAGER_REPORT_AR_18.html"
SIDS = {"SOURCE_1", "SOURCE_2", "SOURCE_3"}
NODE_FIELDS = ["source_id", "domain_link", "masala_segment_link", "serves_what", "does_not_serve",
               "cause", "conditions", "preventers", "verdict", "evidence", "residuals",
               "hukm_birth_allowed", "manat_birth_allowed", "tanzil_birth_allowed", "final_answer_allowed"]
SECTIONS = [
    "1. ملخص للمدير", "2. الجملة محل التشغيل", "3. جدول الكلمات العشر", "4. الإفادة", "5. المقام",
    "6. سياسة المرجع", "7. الدعوى الواقعية ورخصة العبور", "8. المصدر المعياري", "9. موضع التوقف",
    "10. المعلومات الناقصة / الطلب الأدق", "11. ما يلزم بعد الوصول", "12. الاختبارات",
    "13. إثبات سلسلة التوليد", "14. الخلاصة التنفيذية",
]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (MAP, GUARDS, RESID, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (MAP, GUARDS, RESID):
        json.loads(p.read_text(encoding="utf-8"))


def test_three_sources_mapped_full_shape():
    m = json.loads(MAP.read_text(encoding="utf-8"))
    assert m["SOURCE_TO_MASALA_MAPPING_ALLOWED"] == "YES"
    assert m["mapping_mode"] == "STRUCTURAL_ONLY"
    assert m["PRIMARY_DOMAIN_CANDIDATE"] == "KEEP_COMPOSITE"
    assert m["source_count_mapped"] == 3
    nodes = m["mapping_nodes"]
    assert len(nodes) == 3
    assert {n["source_id"] for n in nodes} == SIDS
    for n in nodes:
        for k in NODE_FIELDS:
            assert k in n and n[k] not in (None, "", []), (n["source_id"], k)
        assert n["verdict"] == "MAPPED_TO_MASALA_SEGMENT_STRUCTURAL_ONLY"
        for g in ("hukm_birth_allowed", "manat_birth_allowed", "tanzil_birth_allowed", "final_answer_allowed"):
            assert n[g] == "NO", (n["source_id"], g)


def test_specific_segment_links():
    nodes = {n["source_id"]: n for n in json.loads(MAP.read_text(encoding="utf-8"))["mapping_nodes"]}
    assert "أخت" in nodes["SOURCE_1"]["masala_segment_link"]
    assert "الكلالة" in nodes["SOURCE_1"]["does_not_serve"] or "الورث" in nodes["SOURCE_1"]["does_not_serve"]
    assert "التركة" in nodes["SOURCE_2"]["masala_segment_link"] or "الفروض" in nodes["SOURCE_2"]["masala_segment_link"]
    assert "السكن" in nodes["SOURCE_2"]["does_not_serve"] or "الطرد" in nodes["SOURCE_2"]["does_not_serve"]
    assert "دعو" in nodes["SOURCE_3"]["masala_segment_link"] or "تحاكم" in nodes["SOURCE_3"]["masala_segment_link"]
    assert "السكن" in nodes["SOURCE_3"]["does_not_serve"] or "ملكي" in nodes["SOURCE_3"]["does_not_serve"]


def test_no_hukm_manat_tanzil_final():
    m = _m()
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k
    assert m["AGENT_RATIFIED_SOURCE"] == "NO"
    assert m["SELECTED_BY_AGENT"] == "NO"
    assert m["NORMATIVE_SOURCE_BORN"] == "YES"


def test_composite_kept():
    assert _m()["KEEP_COMPOSITE_REMAINS_ACTIVE"] == "YES"
    assert _m()["PRIMARY_DOMAIN_CANDIDATE"] == "KEEP_COMPOSITE"


def test_sukna_residual_recorded():
    r = json.loads(RESID.read_text(encoding="utf-8"))
    assert r["unresolved_residuals_recorded"] == "YES"
    assert r["sukna_or_possession_uncovered"] == "YES"
    assert "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE" in r["uncovered_domain_candidates"]
    assert any("SUKNA" in u["domain_candidate_id"] for u in r["per_uncovered"])
    assert len(r["open_residuals_before_hukm_gate"]) >= 1
    assert _m()["SUKNA_OR_POSSESSION_UNCOVERED"] == "YES"
    assert _m()["UNRESOLVED_RESIDUALS_RECORDED"] == "YES"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("SOURCE_TO_MASALA_MAPPING_IS_NOT_HUKM", "SOURCE_IS_NOT_HUKM", "SOURCE_IS_NOT_MANAT",
              "SOURCE_IS_NOT_TANZIL", "SOURCE_ALONE_DOES_NOT_PRODUCE_HUKM",
              "DOMAIN_CANDIDATE_IS_NOT_FINAL_DOMAIN", "KEEP_COMPOSITE_REMAINS_ACTIVE",
              "NO_NEW_SOURCE_ADDED", "AGENT_DID_NOT_RATIFY_SOURCE", "AGENT_DID_NOT_SELECT_SOURCE",
              "TEXT_VERBATIM_ASSERTED_BY_OWNER_ONLY", "EVIDENCE_IS_CITATION_STRING_ONLY",
              "NO_LIVE_EXTERNAL_LINKS", "NO_NORMATIVE_HUKM", "NO_MANAT", "NO_TANZIL", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k


def test_no_live_links_external_refs_zero():
    blob = MAP.read_text(encoding="utf-8") + REPORT.read_text(encoding="utf-8") + RESID.read_text(encoding="utf-8")
    assert not re.search(r"https?://|www\.|//cdn|quran\.com|sunnah\.com", blob)
    assert _m()["EXTERNAL_REFS"] == "0"
    assert _m()["LIVE_EXTERNAL_LINKS_IN_ARTIFACTS"] == "NO"


def test_report_sections_ordered_1_to_14():
    t = REPORT.read_text(encoding="utf-8")
    positions = []
    for s in SECTIONS:
        idx = t.find(s)
        assert idx != -1, s
        positions.append(idx)
    assert positions == sorted(positions), "sections not in order"


def test_report_ar09_experience():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f"<th>t00{i}</th>" in t, i
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    assert "ROUND_18_TESTS = passed" in t
    for sid in SIDS:
        assert sid in t, sid
    for stmt in ("NORMATIVE_HUKM_PRODUCED = NO", "MANAT_PRODUCED = NO",
                 "TANZIL_PRODUCED = NO", "FINAL_ANSWER_PRODUCED = NO",
                 "PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_owner_request_19_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("PROVIDE_SUKNA_SOURCE = YES | NO",
              "ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO",
              "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE"):
        assert q in t, q


def test_no_typos_no_noncanonical_no_commit():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + MAP.read_text(encoding="utf-8")
    for bad in TYPOS:
        assert bad not in blob, bad
    assert "DOMAIN_ROUTING_LAYER" not in t
    m = _m()
    assert m["PRIOR_ROUND_VERDICTS_CHANGED"] == "NO"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED",
              "VENDOR_CHANGED_BY_THIS_ROUND", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"
    assert m["SILENT_FALLBACK_COUNT"] == "0"


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
