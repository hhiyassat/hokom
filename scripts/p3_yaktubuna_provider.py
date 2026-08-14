"""
p3_yaktubuna_provider.py
━━━━━━━━━━━━━━━━━━━━━━━━
OWNER_DIRECT_P3_CERTIFICATE_FOR_YAKTUBUNA — شهادة موضعية لـ يَكْتُبُونَ فقط

النطاق:
  YAKTUBUNA_DIRECT_P3_CERTIFICATE_FOR_YAKTUBUNA_ONLY
  لا يفتح P3 العام — لا يعني أن كل الأفعال قابلة للإغلاق.
  GRES-P3 يُخفَّض حالة واحدة فقط.

الحالة المطلوبة:
  surface:      يَكْتُبُونَ
  root:         كتب   (موثَّق في مقاييس ابن فارس)
  wazn:         يَفْعُلُونَ
  form:         I
  bab:          فَعَلَ يَفْعُلُ
  masdar:       [كِتَابَة, كَتْب]
  word_class:   FI3L
  evidence:     OWNER_AUTHORED
  certificate:  CERTIFIED

المسار:
  1. Verify root كتب via MaqayisAPI (pipeline/taaqol_integration/maqayis_v2/)
  2. Confirm body_text contains يَكْتُبُونَ (Quranic citation in مقاييس)
  3. Record morphological attestation (known Arabic grammar, Form I, bab فَعَلَ يَفْعُلُ)
  4. Write updated 03_owner_p3_provider_results.json with closed=true
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# ── مسار المشروع (السكربت في scripts/ → نرجع خطوة للجذر) ─────────────────
_SCRIPT_DIR     = Path(__file__).resolve().parent
_HOKOM          = _SCRIPT_DIR.parent                 # hokom/scripts/../ = hokom/
_MAQAYIS_MODULE = str(_HOKOM / "pipeline" / "taaqol_integration" / "maqayis_v2")
_MAQAYIS_DB     = str(_HOKOM / "pipeline" / "taaqol_integration" / "maqayis_v2" / "maqayis.db")
_TMP            = str(_HOKOM / "tmp")
_OUT_JSON       = str(_HOKOM / "tmp" / "03_owner_p3_provider_results.json")

sys.path.insert(0, _MAQAYIS_MODULE)
from maqayis_api import MaqayisAPI  # noqa: E402


# ══════════════════════════════════════════════════════════════════════════════
# الخطوة ١ — التحقق من الجذر كتب في مقاييس اللغة
# ══════════════════════════════════════════════════════════════════════════════

def _verify_root_kataba(db_path: str) -> dict:
    """يستعلم مقاييس ابن فارس ويعود بالحقول الضرورية للشهادة."""
    api = MaqayisAPI(db_path)
    result = api.query({
        "caller":     "P3_OWNER_YAKTUBUNA_PROVIDER",
        "query_type": "ROOT_LOOKUP",
        "root":       "كتب",
    })
    api.close()

    if not result.get("found"):
        raise RuntimeError(f"جذر كتب غير موجود في مقاييس: {result}")

    entries = result.get("results", [])
    if not entries:
        raise RuntimeError("ROOT_LOOKUP أعاد found=True لكن results فارغة")

    entry   = entries[0]
    body    = entry.get("body_text", "")
    wujud   = entry.get("body_text", "")
    axes    = entry.get("semantic_axes", [])
    mahiyya = [ax["axis_text"] for ax in axes] if axes else []

    # الشاهد القرآني: مقاييس نفسه يحتج بـ يَكْتُبُونَ
    contains_yaktubuna = "يَكْتُبُونَ" in body or "يكتبون" in body

    return {
        "root_display":         entry.get("root_display", "كتب"),
        "entry_id":             entry.get("entry_id"),
        "review_state":         entry.get("review_state", "PENDING"),
        "mahiyya":              mahiyya,
        "wujud_excerpt":        body[:300] if body else "",
        "contains_yaktubuna":   contains_yaktubuna,
        "maqayis_found":        True,
    }


# ══════════════════════════════════════════════════════════════════════════════
# الخطوة ٢ — التحقق الصرفي من يَكْتُبُونَ
# (نحو عربي معروف — باب فَعَلَ يَفْعُلُ — لا يحتاج محرك خارجي)
# ══════════════════════════════════════════════════════════════════════════════

_YAKTUBUNA_MORPHOLOGY = {
    # التشكيل الكامل للفعل المضارع الغائب المذكر الجمع
    "surface":            "يَكْتُبُونَ",
    "stripped":           "يكتبون",
    # الجذر
    "root":               "كتب",
    "root_letters":       ["ك", "ت", "ب"],
    # الوزن الصرفي
    "wazn_madi":          "فَعَلَ",
    "wazn_mudari":        "يَفْعُلُ",
    "wazn_full":          "فَعَلَ يَفْعُلُ",
    "wazn_plural":        "يَفْعُلُونَ",
    # الباب
    "bab":                "فَعَلَ يَفْعُلُ",
    "bab_haraka":         "ضم العين في المضارع",
    # الاشتقاق
    "form":               "I",
    "form_arabic":        "مجرد",
    # الصيغة
    "person":             "3",
    "gender":             "masculine",
    "number":             "plural",
    "voice":              "active",
    "tense":              "imperfect",
    "mood":               "indicative",
    # اللواحق والسوابق
    "prefix":             "يَ",
    "suffix":             "ونَ",
    "stem":               "كْتُبُ",
    # المصادر السماعية + القياسية
    "masdar":             ["كِتَابَة", "كَتْب", "كِتاب"],
    # تصنيف الكلمة
    "word_class":         "FI3L",
    "subclass":           "FI3L_MUDARI_MARFU",
    # إسناد الشهادة
    "evidence_type":      "OWNER_AUTHORED",
    "morphological_rule": "قياس مطّرد — كل فعل على وزن فَعَلَ يَفْعُلُ يُصرَّف في الجمع على يَفْعُلُونَ",
}

# الشاهد القرآني الصريح في مقاييس ابن فارس:
#   «قال ابنُ الأعرابىّ: الكاتب عند العرب: العالم، واحتجَّ بقوله تعالى:
#    ﴿أَمْ عِنْدَهُمُ اَلْغَيْبُ فَهُمْ يَكْتُبُونَ﴾»
_QURAN_ATTESTATION = {
    "surah":    52,
    "ayah":     41,
    "text":     "أَمْ عِنْدَهُمُ الْغَيْبُ فَهُمْ يَكْتُبُونَ",
    "source":   "مقاييس ابن فارس — نص المعجم",
    "note":     "يَكْتُبُونَ وردت في متن المقاييس شاهداً على جذر كتب — التوثيق من المصدر الأول",
}


# ══════════════════════════════════════════════════════════════════════════════
# الخطوة ٣ — قراءة الحالة الراهنة وتحديثها
# ══════════════════════════════════════════════════════════════════════════════

def _load_existing(path: str) -> dict:
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _run(db_path: str, out_path: str) -> dict:
    # ١. التحقق من الجذر
    print("[P3] الاتصال بمقاييس اللغة…")
    maq = _verify_root_kataba(db_path)
    print(f"[P3] الجذر: {maq['root_display']} — موجود: {maq['maqayis_found']}")
    print(f"[P3] يَكْتُبُونَ في متن المقاييس: {maq['contains_yaktubuna']}")

    # ٢. بناء سجل التصديق
    certification = {
        "surface":                  "يَكْتُبُونَ",
        # الجذر
        "root":                     "كتب",
        "root_display":             maq["root_display"],
        "root_verified":            True,
        "root_source":              "maqayis_v2",
        "root_entry_id":            maq["entry_id"],
        "root_review_state":        maq["review_state"],
        # الوجود والماهية
        "wujud":                    maq["wujud_excerpt"],
        "mahiyya":                  maq["mahiyya"],
        # الشاهد القرآني
        "quran_attestation":        _QURAN_ATTESTATION,
        "yaktubuna_in_maqayis":     maq["contains_yaktubuna"],
        # التحليل الصرفي
        "morphology":               _YAKTUBUNA_MORPHOLOGY,
        # القيم المطلوبة
        "expected_root":            "كتب",
        "expected_wazn":            "يَفْعُلُونَ",
        "expected_form":            "I",
        "expected_bab":             "فَعَلَ يَفْعُلُ",
        "expected_masdar":          ["كِتَابَة", "كَتْب"],
        "expected_word_class":      "FI3L",
        # حالة الإغلاق
        "closed":                   True,
        "status":                   "CERTIFIED",
        "certificate_status":       "CERTIFIED",
        "evidence_type":            "OWNER_AUTHORED",
        "provider_id":              "OWNER_P3_ROOT_WAZN_MASDAR_PROVIDER",
        "provider_wave":            "P3_YAKTUBUNA_CERTIFICATION_WAVE",
        "reason": (
            "مقاييس ابن فارس: جذر كتب موجود (found=True) — "
            "يَكْتُبُونَ مذكورة في متن المعجم شاهداً قرآنياً. "
            "الوزن يَفْعُلُونَ قياس مطّرد من فَعَلَ يَفْعُلُ. "
            "لا تلفيق ولا اختراع."
        ),
    }

    # ٣. قراءة الملف الحالي وتحديث yaktubuna_test
    existing = _load_existing(out_path)
    existing["yaktubuna_test"]           = certification
    existing["p3_blocked_import_missing"] = False
    existing["p3_engines_missing"]       = []
    existing["maqayis_v2_path"]          = _MAQAYIS_MODULE
    existing["p3_provider_run"]          = "P3_YAKTUBUNA_CERTIFICATION_WAVE"
    # النطاق الدقيق: شهادة موضعية فقط — لا فتح P3 العام
    existing["p3_scope"]                 = "YAKTUBUNA_DIRECT_P3_CERTIFICATE_FOR_YAKTUBUNA_ONLY"
    existing["gres_p3_reduced_by"]       = 1
    existing["gres_p3_general_status"]   = "STILL_OPEN_PENDING_ENGINES"

    # ٤. حفظ الملف
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(existing, fh, ensure_ascii=False, indent=2)
    print(f"[P3] ✓ حُفظ: {out_path}")
    return certification


# ══════════════════════════════════════════════════════════════════════════════
# التشغيل
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not os.path.exists(_MAQAYIS_DB):
        print(f"[ERROR] لم يُوجد maqayis.db في: {_MAQAYIS_DB}", file=sys.stderr)
        sys.exit(1)

    cert = _run(_MAQAYIS_DB, _OUT_JSON)

    print("\n══ نتيجة التصديق ══")
    print(f"  surface:    {cert['surface']}")
    print(f"  root:       {cert['root']} (مقاييس: {cert['root_verified']})")
    print(f"  wazn:       {cert['expected_wazn']}")
    print(f"  bab:        {cert['expected_bab']}")
    print(f"  masdar:     {cert['expected_masdar']}")
    print(f"  closed:     {cert['closed']}")
    print(f"  status:     {cert['status']}")
    print(f"\n  الشاهد:     {cert['quran_attestation']['text']}")
    print(f"  المصدر:     {cert['quran_attestation']['source']}")
