#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_AND_SUPPLY_GATE_19 — guard test.

Records a source requirement + owner-fill supply request for the round-18 sukna/possession residual.
Requirement only: no source birth, no hukm candidate, no ḥukm/manāṭ/tanzīl/answer, no composite collapse,
no agent ratification, no live links, EXTERNAL_REFS=0. "لا ضرر" admissible only if owner-supplied+ratified.
Manager report obeys the AR_09_FIXED experience. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
REQ = OUT / "SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_19.json"
SUPPLY = OUT / "OWNER_SOURCE_SUPPLY_REQUEST_FOR_SUKNA_OR_POSSESSION_19.md"
GUARDS = OUT / "SUKNA_OR_POSSESSION_SOURCE_GUARDS_19.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_SOURCE_BIRTH_OR_HUKM_GATE_20.md"
MATRIX = OUT / "SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_19_MATRIX.csv"
REPORT = OUT / "SUKNA_OR_POSSESSION_SOURCE_MANAGER_REPORT_AR_19.html"
FIVE = ["AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"]
NEED_IDS = {"SUKNA_RIGHT", "POSSESSION_OR_YAD", "PREVENT_EXPULSION", "DARAR",
            "USUFRUCT_RIGHT", "SISTER_RESIDENCE_RELATION_POST_DEATH"}
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
    for p in (REQ, SUPPLY, GUARDS, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (REQ, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_requirement_not_source():
    r = json.loads(REQ.read_text(encoding="utf-8"))
    assert r["PROVIDE_SUKNA_SOURCE"] == "YES"
    assert r["ALLOW_NORMATIVE_HUKM_CANDIDATE"] == "NO"
    assert r["PRIMARY_DOMAIN_CANDIDATE"] == "KEEP_COMPOSITE"
    assert r["domain_candidate_id"] == "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"
    assert r["requirement_status"] == "REQUIREMENT_RECORDED_NOT_SOURCE"
    assert r["sukna_source_born"] == "NO"
    assert r["verdict"] == "DEFER_SUKNA_SOURCE_BIRTH_REQUIREMENT_RECORDED"
    assert r["la_darar_admissibility"] == "ONLY_IF_OWNER_SUPPLIED_AND_OWNER_RATIFIED"


def test_six_served_needs():
    r = json.loads(REQ.read_text(encoding="utf-8"))
    needs = r["served_needs"]
    assert len(needs) == 6
    assert {n["need_id"] for n in needs} == NEED_IDS
    for n in needs:
        assert n["need_ar"].strip()


def test_five_fields_plus_ratification_requested():
    r = json.loads(REQ.read_text(encoding="utf-8"))
    assert r["required_fields"] == FIVE + ["OWNER_RATIFICATION"]
    st = r["supply_template"]
    for f in FIVE:
        assert f in st and st[f] == ""
    assert st["OWNER_RATIFICATION"] == "NO"


def test_supply_request_has_fields_and_needs():
    t = SUPPLY.read_text(encoding="utf-8")
    for f in FIVE + ["OWNER_RATIFICATION"]:
        assert f in t, f
    for ar in ("حق السكنى", "الحيازة أو اليد", "منع الطرد", "الضرر", "حق الانتفاع",
               "علاقة الأخت الساكنة بالبيت بعد موت المالك"):
        assert ar in t, ar
    assert "لا ضرر ولا ضرار" in t
    assert "OWNER_SUPPLIED" in t


def test_no_source_born_no_hukm():
    m = _m()
    assert m["SUKNA_SOURCE_REQUIREMENT_PRODUCED"] == "YES"
    assert m["SUKNA_SOURCE_BORN"] == "NO"
    assert m["ALLOW_NORMATIVE_HUKM_CANDIDATE"] == "NO"
    assert m["NORMATIVE_HUKM_CANDIDATE_OPENED"] == "NO"
    assert m["SUKNA_OR_POSSESSION_RESIDUAL_ADDRESSING"] == "REQUIREMENT_ONLY"
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k
    assert m["AGENT_RATIFIED_SOURCE"] == "NO"
    assert m["SELECTED_BY_AGENT"] == "NO"
    assert m["KEEP_COMPOSITE_REMAINS_ACTIVE"] == "YES"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("SUKNA_SOURCE_REQUIREMENT_IS_NOT_SOURCE", "NO_SUKNA_SOURCE_BIRTH",
              "NO_NORMATIVE_HUKM_CANDIDATE_OPENED", "AGENT_DID_NOT_RATIFY_SOURCE",
              "AGENT_DID_NOT_SELECT_SOURCE", "NO_NEW_AGENT_SUPPLIED_SOURCE",
              "LA_DARAR_ONLY_IF_OWNER_SUPPLIED_AND_RATIFIED", "COMPOSITE_KEPT_NOT_COLLAPSED",
              "EVIDENCE_IS_CITATION_STRING_ONLY", "NO_LIVE_EXTERNAL_LINKS",
              "TEXT_VERBATIM_ASSERTED_BY_OWNER_ONLY", "NO_NORMATIVE_HUKM", "NO_MANAT",
              "NO_TANZIL", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k


def test_no_live_links_external_refs_zero():
    blob = REQ.read_text(encoding="utf-8") + REPORT.read_text(encoding="utf-8") + SUPPLY.read_text(encoding="utf-8")
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
    assert "ROUND_19_TESTS = passed" in t
    assert "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE" in t
    for stmt in ("SUKNA_SOURCE_REQUIREMENT_PRODUCED = YES", "SUKNA_SOURCE_BORN = NO",
                 "ALLOW_NORMATIVE_HUKM_CANDIDATE = NO", "NORMATIVE_HUKM_PRODUCED = NO",
                 "MANAT_PRODUCED = NO", "TANZIL_PRODUCED = NO", "FINAL_ANSWER_PRODUCED = NO"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_owner_request_20_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("ALLOW_SUKNA_SOURCE_BIRTH = YES | NO",
              "SUKNA_SOURCE_FIELDS_COMPLETE = YES | NO",
              "ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO",
              "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE"):
        assert q in t, q


def test_no_typos_no_noncanonical_no_commit():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + REQ.read_text(encoding="utf-8")
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
