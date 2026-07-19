# Root Ownership Closure — HOKOM-MORPHOLOGY-ROOT-OWNERSHIP-01

**Mandate:** HOKOM-MORPHOLOGY-ROOT-OWNERSHIP-01  
**Baseline commit:** `ed343a2` (P5 closure, 0 failures)  
**Closure commit:** `feat(morphology): establish canonical root ownership in Hokom`  
**Suite:** 3299 passed, 18 skipped, 132 subtests — **0 failures × 2 runs**

---

## §17 Boolean Gates — ALL PASS ✅

| Gate | Description | Result |
|------|-------------|--------|
| G1 | P5 baseline 0 failures before root work (ed343a2) | ✅ |
| G2 | `reports/root-ownership/root_inventory.jsonl` exists | ✅ |
| G3 | All 10 canonical contract types present in `root_contracts.py` | ✅ |
| G4 | `defer:root:lafif_mafruq_unresolved` residual in `root_rules.py` | ✅ |
| G5 | `defer:root:lafif_maqrun_unresolved` residual in `root_rules.py` | ✅ |
| G6 | Lafif detection pass precedes individual weak-position checks | ✅ |
| G7 | `tests/p3_candidate/test_root_classes_corpus.py` exists | ✅ |
| G8 | `tests/p3_candidate/test_root_properties.py` exists | ✅ |
| G9 | `tests/integration/test_root_p5_entry_gate.py` exists | ✅ |
| G10 | No `import`/`from` hr2s in any canonical engine file | ✅ |
| G11 | `resolve_root_pipeline()` is single entrypoint in orchestrator | ✅ |
| G12 | `HOKOM_ROOT_ENGINE` source constant in `root_resolution.py` | ✅ |
| G13 | `ROOT_CLASS_CONTRACTS` covers classes A–L (11 classes) | ✅ |
| G14 | `RootResolution` is a frozen dataclass | ✅ |
| G15 | `vendor/Taaqol-GPT` unmodified | ✅ |
| G16 | P5_FILES_MODIFIED = 0 (no p5_* file touched) | ✅ |
| G17 | Full suite 0 failures (confirmed × 2) | ✅ |

---

## Deliverables

### New files

| File | Role |
|------|------|
| `pipeline/p3_candidate/root_contracts.py` | 10 canonical contract dataclasses + ROOT_CLASS_CONTRACTS A–L |
| `reports/root-ownership/root_inventory.jsonl` | Full inventory of 13 root-adjacent files; canonical engine documented |
| `tests/p3_candidate/test_root_classes_corpus.py` | Corpus tests: classes A–L, negative cases, monotonicity, serialization |
| `tests/p3_candidate/test_root_properties.py` | P1–P10 property tests (determinism, monotonicity, frozen, idempotence…) |
| `tests/integration/test_root_p5_entry_gate.py` | P5 entry gate: MABNI_TO_ROOT_LEAKS=0, OPERATOR leaks=0, DEFERRED≠ACCEPT |

### Modified files

| File | Change |
|------|--------|
| `pipeline/p3_candidate/root_rules.py` | Added lafif detection pass (لفيف مفروق + لفيف مقرون) before individual weak checks |
| `tests/*/test_*_frozen*.py` (×6) | Updated `root_rules.py` checksum prefix to `a8e35225693f553d` |

---

## Root Engine — Classes A–L

| Class | Type | Verdict | Residual |
|-------|------|---------|----------|
| A | Sound (سالم) | ACCEPT | — |
| B | Hamza (مهموز) | ACCEPT | — |
| C | Geminate (مضعَّف) | ACCEPT | — |
| D | Assimilated (مثال) | DEFER | `assimilated_fa_unresolved` |
| E | Hollow (أجوف) | DEFER | `hollow_underlying_radical_unresolved` |
| F | Defective (ناقص) | DEFER | `defective_lam_unresolved` |
| G | Lafif Mafruq (لفيف مفروق) | DEFER | `lafif_mafruq_unresolved` |
| H | Lafif Maqrun (لفيف مقرون) | DEFER | `lafif_maqrun_unresolved` |
| I | Quadrilateral (رباعي) | DEFER | `quadriliteral_beyond_scope` |
| K | Compressed (أمر مضغوط) | DEFER | `two_consonant_form_unresolved` |
| L | Insufficient (بنية قاصرة) | BLOCK | `insufficient_consonants` |

---

## Critical Fix: Lafif Detection Gap

**Before:** `_analyze_trilateral()` checked weak positions sequentially — a word with both FA+LAM weak (لفيف مفروق) was misidentified as ASSIMILATED (only FA detected); a word with both AYN+LAM weak (لفيف مقرون) was misidentified as HOLLOW (only AYN detected).

**After:** A dedicated lafif detection pass runs first, before any individual position check. FA+LAM weak → `RESIDUAL_LAFIF_MAFRUQ`; AYN+LAM weak → `RESIDUAL_LAFIF_MAQRUN`.

Confirmed:
- وَقَى, وَفَى, وَعَى, وَلِيَ → `defer:root:lafif_mafruq_unresolved` ✅
- طَوَى, نَوَى, حَوَى, رَوَى, سَوَى, لَوَى → `defer:root:lafif_maqrun_unresolved` ✅

---

## Constraints Honoured

- لا تعديل داخل vendor/Taaqol-GPT ✅
- لا استيراد من hr2s في ملفات المحرك ✅
- P5_FILES_MODIFIED = 0 ✅
- الحالات الـ29 المصنفة BLOCKED_BY_P4 تبقى بقايا محكومة ✅
- لا تغيير expected outputs لتغطية سلوك خاطئ ✅
- لا بداية الوزن أو المصدر أو المشتقات ✅

---

*هذا هو الانتقال الفعلي إلى الجذر. لا مراجعة جديدة لـP5 بعد `ed343a2`.*
