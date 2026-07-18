# تقرير تسليم: HOKOM-ROOT-OWNERSHIP

**التاريخ:** 2026-07-16  
**الدفعة:** نقل ملكية الجذر والصرف إلى Hokom  
**الحالة:** ✅ مكتمل — 0 انحدارات

---

## ملخص تنفيذي

نقل ملكية تحليل الجذر العربي من HR2S كمصدر للحقيقة إلى **محرك Hokom المحلي**.  
HR2S بقي في دور **مرجع المقارنة فقط** — لا يُستدعى في المسار الحي.

---

## الملفات المُنشَأة

| الملف | الوصف |
|---|---|
| `pipeline/p3_candidate/root_profiles.py` | تصنيف نوع الجذر: سالم / مضعَّف / مهموز + `build_root_profile()` |
| `pipeline/p3_candidate/root_rules.py` | قواعد التحليل المحلي: `analyze_host_consonants()` — ACCEPT/DEFER/BLOCK |
| `pipeline/p3_candidate/root_resolution.py` | `RootResolution` (DTO مجمَّد) + `resolve_root()` (نقطة الدخول الوحيدة) |
| `pipeline/p3_candidate/root_resolution_orchestrator.py` | `resolve_root_pipeline()` — التسلسل الكامل RootResolution→Projection→Candidate |

## الملفات المُعدَّلة

| الملف | التعديل |
|---|---|
| `pipeline/p2_projection/root_projection.py` | أُضيف `RootProjection.from_root_resolution()` (classmethod) |
| `tests/p3_candidate/test_root_resolution.py` | 37 اختبار R1–R18 (كانت فاشلة أولاً — TDD) |
| `tests/integration/test_hokom_local_root_engine.py` | 10 اختبارات H1–H6 للتسلسل الكامل |
| `tests/integration/test_hokom_vs_hr2s_root_oracle.py` | 6 اختبارات O1–O2 (O3 مُعلَّقة إذا HR2S غير متاح) |

---

## نتائج الاختبارات

```
tests/p3_candidate/ + tests/integration/test_hokom_*
  92 passed, 3 skipped (O3 — HR2S غير مثبَّت)

الانحدار الكامل:
  1871 passed, 153 failed (نفس الـ 153 السابقة), 13 skipped
  0 انحدارات جديدة
```

---

## هيكل القرار

```
pre_root_directive='BLOCK'  → RootResolution(BLOCK) مباشرة
pre_root_directive='OPEN'   → analyze_host_consonants() → ACCEPT|DEFER
pre_root_directive='DEFER'  → analyze_host_consonants() → DEFER (رتابة صارمة)
```

### ACCEPT (ثلاثية سالمة/مهموز/مضعَّف):
| الكلمة | الجذر |
|---|---|
| ضَرَبَ | (ض، ر، ب) |
| كَتَبَ | (ك، ت، ب) |
| تَرَكَ | (ت، ر، ك) |
| شَجَرَ | (ش، ج، ر) |
| قَرَأَ | (ق، ر، ء) |
| مَدَّ  | (م، د، د) |

### DEFER (ضعيف/مضغوط):
| الكلمة | السبب |
|---|---|
| قَالَ، نَامَ، بَاعَ | أجوف (ألف/واو في العين) |
| دَعَا | ناقص (ألف في اللام) |
| وَقَى  | مثال + ناقص |
| قُلْ   | مضغوط (حرفان) |

### BLOCK (directive موروث من PreRoot):
| الكلمة | السبب |
|---|---|
| مِنْ، هِيَ، أَنَّ، أَنَّهُمْ | pre_root_directive='BLOCK' |

---

## host threading

```
original_host → input_surface في RootProjection
refined_host  → RootResolution.analyzed_host
              → RootProjection.analyzed_host
              → RootCandidate.host_surface
```

✅ التحقق: `تَرَكَتْ` (original) + `تَرَكَ` (refined) → `rc.host_surface == 'تَرَكَ'`

---

## ضمانات المعمارية

- `source_engine='HOKOM_ROOT_ENGINE'` في كل `RootResolution` و`RootProjection`
- لا `from hr2s.root import ...` أو `from hr2s.boundary import ...` في أي ملف جديد (R18 ✅)
- `HR2S = مرجع مقارنة فقط` — المسموح: `from hr2s import MorphologyEngine` في اختبارات O3 فقط
- `RootResolution` مجمَّد (`frozen=True`) — لا تعديل بعد الإنشاء (R10 ✅)
- الرتابة: DEFER لا يُرقَّى إلى ACCEPT داخليًا إلا عبر آلية الترخيص الخارجية

---

## ما لم يتغير (في هذه الدفعة)

- `pipeline/p4_wazn/` — لم يُعدَّل
- `pipeline/p3_candidate/root_relicensing.py` — لم يُعدَّل
- `data/02_mabniyat/` — لم يُعدَّل
- `pipeline/p4_wazn/ilaal.py`, `hypothesis.py`, `wazn_projection.py` — لم تُعدَّل
- لا commits، لا tags، لا دمج
- مشروع HR2S لم يُعدَّل

---

## الخطوة التالية (خارج هذه الدفعة)

Phase 4B: ربط `resolve_root_pipeline()` بالتسلسل الكامل لـ Hokom عبر `hokom_pipeline.py`، وتوسيع DEFER إلى آلية الترخيص للجذور الضعيفة.
