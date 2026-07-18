# P3.11 — Root Re-Licensing from WaznHypothesis

**الحالة**: مغلق (PR 3.11)  
**الطبقة**: `pipeline/p3_candidate/root_relicensing.py`  
**الغرض**: قبول الجذر المقترح من WaznHypothesis إذا استوفى شروط الترخيص الكاملة.

---

## شروط القبول (كلها يجب أن تمر بالترتيب)

| # | الشرط | الفشل |
|---|-------|-------|
| 1 | `proposed_root_after is not None` | BLOCK: `block:relicensing:no_proposed_root` |
| 2 | `len(root) in (3, 4)` (ثلاثي أو رباعي) | DEFER: `defer:relicensing:non_trilateral_proposed_root` |
| 3 | لا هويات ممنوعة (`ا/ى/أ/إ/ؤ/ئ/آ`) | BLOCK: `block:relicensing:prohibited_root_identity` |
| 4 | جميع الحروف عربية صحيحة (U+0621–U+064A) | BLOCK: `block:relicensing:non_arabic_consonant_in_root` |
| 5 | `confidence != 'LOW'` | DEFER: `defer:relicensing:low_confidence_hypothesis` |

**ملاحظة**: ء (U+0621) صالحة ومسموح بها صراحةً كهوية جذرية.

---

## نموذج البيانات

```python
@dataclass(frozen=True)
class RootRelicensingResult:
    source: str              # 'WaznHypothesis'
    proposed_root: tuple | None
    directive: str           # 'ACCEPT' | 'DEFER' | 'BLOCK'
    failure_reason: str | None
    evidence_ids: tuple
    trace_ids: tuple
    residual_codes: tuple
```

---

## الرتابة

| مخرج P3.11 | السلوك في الأوركسترا |
|------------|---------------------|
| ACCEPT | RootCandidate مُرقَّى بـ directive='ACCEPT' + canonical_root → project_wazn() → source='hypothesis_relicensed' |
| DEFER | project_wazn() مع RootCandidate الأصلي (DEFER) → source='deferred' |
| BLOCK | project_wazn() مع RootCandidate الأصلي (DEFER) → source='deferred' |

**ضمان الرتابة**: DEFER لا يصبح ACCEPT إلا بعد مرور بوابة P3.11 بالكامل. لا اختصارات.

---

## الاختبارات (R1–R10)

- `tests/p3_candidate/test_root_relicensing.py` — 12 اختبارًا، كلها تمر
