# Phase 4A-α — WaznHypothesis

**الحالة**: مغلق (PR 4A-α)  
**الطبقة**: `pipeline/p4_wazn/hypothesis.py`  
**الغرض**: اقتراح وزن لحالات DEFER من P3 عبر كشف الزيادة الداخلية.

---

## الموقع في السلسلة

```
RootCandidate (P3)
  ├─ ACCEPT → project_wazn() مباشرة                  [source='direct']
  ├─ BLOCK  → project_wazn() (NOT_OPENED)             [source='blocked']
  └─ DEFER  → build_wazn_hypothesis()
                ├─ None → project_wazn() (DEFER)      [source='deferred']
                └─ WaznHypothesis
                     └─ relicense_root_from_wazn_hypothesis()  [P3.11]
                           ├─ ACCEPT → RootCandidate مُرقَّى → project_wazn()
                           │                                   [source='hypothesis_relicensed']
                           └─ DEFER/BLOCK → project_wazn() (DEFER) [source='deferred']
```

---

## الزيادات المكتشفة

### Pattern A — MIM_ZIYADAH (مَ/مُ بادئة)

- الكشف: `refined_host` يبدأ بـ `م` متبوعًا بـ `َ` أو `ُ`
- الوزن المقترح: `مَفْعَلَة` أو `مُفْعَلَة`
- استخراج الجذر: حذف الميم + حذف حروف المد (و/ا/ي) → ما تبقى
- الثقة:
  - `HIGH`: 3 حروف أساسية بعد الميم (بعد حذف حروف المد)
  - `MEDIUM`: عدد مختلف مع جذر مستخرج
  - `LOW`: لا جذر مستخرج

### Pattern B — ALIF_WASL + SIN + TA (اسْتَ بادئة)

- الكشف: `refined_host` يبدأ بـ `يَسْتَ` أو `اسْتَ` أو `سْتَ`
- الوزن المقترح: `يَسْتَفْعِل`
- `ziyadah_detected = ('ALIF_WASL', 'SIN', 'TA')`
- الثقة: `HIGH` إذا تبقّى 3 حروف أساسية

---

## القيود (صارمة)

| القيد | التفصيل |
|-------|---------|
| رتابة directive | لا فرضية للـ ACCEPT أو BLOCK — فقط DEFER |
| الهويات الممنوعة | `proposed_root_after` لا يحتوي `ا/ى/أ/إ/ؤ/ئ/آ` |
| لا استيراد hr2s | مُتحقَّق منه باختبار AST (T10) |
| لا مسارات مطلقة | مُتحقَّق منه باختبار AST (O9) |
| إشارة الزيادة | تشترط وجود `defer:root_refinement:internal_ziyadah_not_resolved` أو بادئة معروفة |

---

## نماذج البيانات

```python
@dataclass(frozen=True)
class WaznHypothesis:
    refined_host: str
    proposed_wazn: str
    ziyadah_detected: tuple
    proposed_root_after: tuple | None
    confidence: str          # 'HIGH' | 'MEDIUM' | 'LOW'
    evidence_ids: tuple
    residual_codes: tuple

@dataclass(frozen=True)
class ProposedRootResolution:
    source: str              # 'WaznHypothesis'
    proposed_root: tuple | None
    wazn_pattern: str
    ziyadah_removed: tuple
    confidence: str
    evidence_ids: tuple
    residual_codes: tuple
```

---

## الاختبارات (T1–T10)

- `tests/p4_wazn/test_wazn_hypothesis.py` — 12 اختبارًا، كلها تمر

---

## الوثيقة المكملة

- `docs/morphology/ROOT_RELICENSING_FROM_WAZN.md` — P3.11
