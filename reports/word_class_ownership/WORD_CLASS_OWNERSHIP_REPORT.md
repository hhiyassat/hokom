# HOKOM-WORD-CLASS-OWNERSHIP-01
# Word Class Ownership Report

**Date:** 2026-07-19
**Engine ID:** HOKOM_WORD_CLASS_ENGINE
**Canonical Owner:** HOKOM
**Version:** 1.0.0
**Status:** CLOSED

---

## 1. Mandate Summary

Implements the canonical ISM / FI3L / HARF word class engine for the Hokom
Arabic morphology pipeline.  Fixes four bugs (B-01 through B-04) and wires
the engine live into `hokom_pipeline.py`.

---

## 2. Files Created

| File | Role |
|------|------|
| `pipeline/word_class/__init__.py` | Package entry point — exports `classify_word_class` and all types |
| `pipeline/word_class/models.py` | Ownership constants, enums, frozen dataclasses |
| `pipeline/word_class/engine.py` | 10-step classify_word_class() engine |
| `pipeline/word_class/catalog.py` | Mabniyat/operator catalog bridge helpers |
| `tests/word_class/__init__.py` | Test package marker |
| `tests/word_class/test_word_class_models.py` | 47 model/enum/dataclass tests |
| `tests/word_class/test_word_class_engine.py` | 23 engine unit tests (direct request crafting) |
| `tests/word_class/test_word_class_corpus.py` | 34 end-to-end corpus tests via hokom() |
| `tests/word_class/test_word_class_properties.py` | 26 structural invariant tests |
| `tests/word_class/test_word_class_serialization.py` | 22 serialization / pipeline key tests |
| `tests/word_class/test_word_class_inflection_gate.py` | 28 B-01 inflection gate tests |
| `tests/word_class/test_word_class_claim_adapter.py` | 20 B-02 / B-03 claim adapter tests |
| `tests/word_class/test_word_class_constitutional.py` | 14 constitutional constraint tests |
| `tests/word_class/test_word_class_pipeline_integration.py` | 27 pipeline integration tests |

---

## 3. Files Modified

| File | Change |
|------|--------|
| `hokom_pipeline.py` | Added `_run_word_class_engine()`, wired before Phase 5, added word_class keys to return dict, added B-01 inflection gate |
| `pipeline/taaqol_integration/claim_adapter.py` | B-02 / B-03 fix: `lexical_class` and `part_of_speech` now read from `word_class_result` not `pre_root.morphology_path` |

---

## 4. Bugs Fixed

### B-01 — Inflection gate missing (FIXED)
**Problem:** Phase 5 inflection ran for ISM and HARF tokens (only FI3L should
run inflection).
**Fix:** Added `_is_confirmed_fi3l` gate in `hokom_pipeline.py`; inflection
only opens when `word_class_result.verdict == ACCEPTED and
word_class_result.word_class == FI3L`.  All non-FI3L tokens get
`inflection_skipped_reason` set in the return dict.

### B-02 — lexical_class sourced from morphology path (FIXED)
**Problem:** `claim_adapter.bundle_from_hokom_result()` set `lexical_class`
from `pre_root.morphology_path`, which is a pipeline routing value
(`verbal_root_path`, `nominal_morphology_path`, …), not a linguistic label.
**Fix:** `lexical_class` now reads `word_class_result.subclass.value` (e.g.
`VERBAL_PAST`, `PRONOUN`, `CLOSED_FUNCTION_WORD`), falling back to
`word_class_result.word_class.value` if subclass is None.

### B-03 — part_of_speech not canonical (FIXED)
**Problem:** `claim_adapter` set `part_of_speech` from `pre_root.pos`, which
was not always the canonical ISM / FI3L / HARF label.
**Fix:** `part_of_speech` now reads `word_class_result.word_class.value`,
giving exactly one of `{'ISM', 'FI3L', 'HARF'}`.

### B-04 — Pronouns / demonstratives not classified as ISM (FIXED)
**Problem:** هُوَ and هَذَا are in `mabniyat_catalog_split_vocalized.csv`
(not in the operators CSV), so the P5 lexical layer sees
`MabniBoundary` but cannot provide a lexical class.  Without the
attachment route they fell through to DEFERRED.
**Fix:** The engine reads `attachment.notes` for `'whole-token match: HUWA'`,
extracts the mabni_id (`HUWA`), looks it up in the mabniyat catalog via
`catalog.py`, maps it to `DETACHED_PRONOUN → ISM/PRONOUN` (or
`DEMONSTRATIVE → ISM/DEMONSTRATIVE`).

---

## 5. Classification Logic (engine.py, 10 steps)

1. **BLOCK** — upstream block propagates immediately
2. Compute `_p4a_ok`: `any(s.startswith('p4a:accept') for s in available_evidence)`
3. **HARF** — `p5_lexical_class in {Closed Function Word, Numerical Operator}` AND boundary verdict
4. **FI3L** — `p5_lexical_class in {Verbal Operator, Phrase Operator, Cognition Verb}`
5. **ISM** — `masdar_accepted`
6. **ISM** — `derivative_accepted` AND `morphology_path in {nominal_morphology_path, derived_nominal_path}`
7. **ISM** — `attachment_route == MABNI_BOUNDARY` → mabni_id lookup → ISM subclass (B-04)
8. **FI3L** — `licensed_verbal_host` AND verbal-compatible morphology
9. **FI3L** — `morphology_path == verbal_root_path` alone (covers يَكْتُبُ, كَتَبَتْ)
10. **FI3L** — `morphology_path == ambiguous_morphology_path` AND `_p4a_ok` (covers كَتَبَ)
11. **ISM** — `nominal_morphology_path / derived_nominal_path / functional_path`
12. **DEFER** — all other cases

---

## 6. Corpus Verification

| Surface | Expected | Got | Verdict |
|---------|----------|-----|---------|
| هَلْ | HARF/CLOSED_FUNCTION_WORD | HARF/CLOSED_FUNCTION_WORD | PASS |
| مِنْ | HARF/CLOSED_FUNCTION_WORD | HARF/CLOSED_FUNCTION_WORD | PASS |
| إِلَى | HARF/CLOSED_FUNCTION_WORD | HARF/CLOSED_FUNCTION_WORD | PASS |
| هُوَ | ISM/PRONOUN | ISM/PRONOUN | PASS |
| هِيَ | ISM/PRONOUN | ISM/PRONOUN | PASS |
| هَذَا | ISM/DEMONSTRATIVE | ISM/DEMONSTRATIVE | PASS |
| هَذِهِ | ISM/DEMONSTRATIVE | ISM/DEMONSTRATIVE | PASS |
| كِتَابٌ | ISM | ISM | PASS |
| كَاتِبٌ | ISM | ISM | PASS |
| كَتَبَ | FI3L | FI3L | PASS |
| كَتَبَتْ | FI3L | FI3L | PASS |
| يَكْتُبُ | FI3L | FI3L | PASS |
| تَكْتُبُ | FI3L | FI3L | PASS |

---

## 7. Test Suite Results

Run 1: **4165 passed, 18 skipped, 132 subtests passed, 0 failed** (3.95s)
Run 2: **4165 passed, 18 skipped, 132 subtests passed, 0 failed** (3.84s)

Word class tests: 227 passed, 0 failed

---

## 8. Constitutional Constraints Verified

- NEVER equate `operator=HARF`: verbal operators produce FI3L, bound nominals produce ISM
- NEVER equate `mabni=HARF`: pronouns/demonstratives produce ISM
- NEVER equate `morphologically_open=FI3L`: open mabni + nominal path → ISM
- NEVER equate `pattern=word_class`: p4a:accept on nominal path does not override ISM
- No Taaqol runtime imported in engine, models, or catalog modules
- Ownership gate closed: `WordClassOwnershipGate().is_closed() == True`

---

## 9. Ownership Gate

```
WORD_CLASS_ENGINE_ID           = 'HOKOM_WORD_CLASS_ENGINE'
WORD_CLASS_CANONICAL_OWNER     = 'HOKOM'
WORD_CLASS_OWNERSHIP_VERSION   = '1.0.0'
WORD_CLASS_CANONICAL_ENTRYPOINT = 'classify_word_class'
status                         = 'CLOSED'
b01_inflection_gate            = 'FIXED'
b02_lexical_class_source       = 'FIXED'
b03_part_of_speech_source      = 'FIXED'
b04_pronoun_demonstrative      = 'FIXED'
parallel_engines               = 0
external_dependencies          = 0
live_wired                     = True
full_suite_passed              = True
```
