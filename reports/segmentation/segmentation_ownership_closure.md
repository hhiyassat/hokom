# HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01 — Closure Report

**Status: CLOSED**
**Date: 2026-07-20**
**Engine: HOKOM_CLITIC_SEGMENTER**
**Owner: HOKOM**
**Entrypoint: `segment_token`**

---

## Ownership Gates

| Gate | Status |
|------|--------|
| Engine ID = HOKOM_CLITIC_SEGMENTER | CLOSED |
| Canonical owner = HOKOM | CLOSED |
| HR2S runtime dependencies = 0 | CLOSED |
| Taaqol bridge invocations = 0 | CLOSED |
| Parallel engines = 0 | CLOSED |
| Host contract (no empty string) | CLOSED |
| Clitic-only construction support | CLOSED |
| Ambiguity governance | CLOSED |
| Lexical precedence (protected tokens first) | CLOSED |
| Inflection/clitic separation | CLOSED |
| Serialization (frozen dataclass) | CLOSED |
| Property tests (all corpus) | CLOSED |
| Ayat al-Dayn targeted cases | CLOSED |
| Full suite stability (no regressions) | CLOSED |
| Corrective closure: 4 critical failures fixed | CLOSED |

---

## Package Structure

```
pipeline/p0_segmentation/
    __init__.py        — public API
    models.py          — SegmentBundle, SegmentationOwnershipGate, enums
    inventory.py       — proclitic/enclitic inventories, protected tokens
    normalization.py   — strip_diacritics, count_arabic_consonants
    rules.py           — _extract_proclitics, _try_enclitic, guards
    engine.py          — segment_token (canonical entrypoint)
```

---

## Decision Order

1. Protected whole-token (PROTECTED_WHOLE_TOKENS) → no decomposition
2. Whole-token operator (WHOLE_TOKEN_OPERATORS) → operator host + optional enclitic
3. NON_SEPARABLE_INITIALS guard → reject if bare token in guard set
4. Multi-proclitic sequence + (article?) + host + (enclitic?)
5. Single proclitic with diacritic compatibility check
6. Definite article only + host + (enclitic?)
7. Enclitic only
8. Unsplit whole token

---

## Key Guards

- **Diacritic compatibility**: `فُسُوقٌ` has damma on ف, while فَ (conjunction) expects fatha → rejected
- **Minimum consonant threshold**: CONJUNCTION=3, PREPOSITION=2, FUTURE=3 — prevents `وَعَدَ→وَ+عَدَ`
- **NON_SEPARABLE_INITIALS**: explicit guard for `فَقِيرٌ`, `سَمِعَ` etc.
- **Vocalized operator check**: when text is vocalized, use exact vocalized match before bare fallback — prevents `سَمِعَ→سَ+مِعَ` (مِعَ ≠ مَعَ operator)
- **Clitic-only detection**: if remainder after proclitic is exactly a known enclitic → `host=None, clitic_only=True`
- **Inflectional suffix guard**: وا, ون, ان, ن, ين never treated as enclitics

### Corrective Closure Guards (added in CORRECTIVE_CLOSURE_PASS)

- **`_sa_future_guard`**: FUTURE_PARTICLE سَ only licensed before imperfect verbs;
  remainder must start with a mudaraa' prefix letter (ي ت ن أ). Prevents `سَفِيهًا→سَ+فِيهًا`.
- **Conjunction host guard**: CONJUNCTION proclitics (وَ فَ) verify HOST consonant count
  (after stripping potential enclitic) is ≥3. Prevents `وَلِيُّهُ→وَ+لِيُّهُ` (host=لِيُّ = 2 cons).
- **`_na_is_likely_inflectional`**: نَا blocked as enclitic when bare form ends with 'ونا'
  (dual imperfect verb: ألف التثنية). Prevents `يَكُونَا→يَكُو+نَا`.
- **Tanwin guard**: enclitic split rejected if extracted enclitic surface contains tanwin
  (ً ٌ ٍ — case endings, never pronouns). Prevents `سَفِيهًا→سَفِي+هًا`.
- **Step 2.5 contracted لِل**: bare surface starting with لل (len≥4) handled before
  general proclitic extraction. Extracts لِ + contracted article + host. Resolves
  `لِلشَّهَادَةِ→لِ+ل+شَّهَادَةِ`.

---

## Test Results (Python 3.10 container)

- New tests after initial closure: **509**
- Full suite passed after initial closure: **4817** (4308 baseline + 509 new)
- New tests added in corrective pass: **39** (5 test files)
- Full suite passed after corrective pass: **4919** (4817 + 39 corrective + 63 prior gaps verified)
- Full suite failed: **10** (all pre-existing Python 3.10 vs 3.11+ requirement, unchanged)
- Regressions: **0**

---

## Taaqol Bridge Contract

The Taaqol bridge (`pipeline/taaqol_integration/live/bridge.py`) is **intentionally unchanged**.
The SegmentBundle is stored in `hokom()` output as `segment_bundle`, `segment_host`,
`segment_proclitics`, `segment_enclitics`, `segment_clitic_only`.

The bridge resume phase (HOKOM-TAAQOL-LIVE-INTEGRATION-01 remains OPEN) must:
- Use `SegmentBundle.host` instead of `original_surface` for lexical scope
- Add proclitic/enclitic slots to the SlotGraph
- Never use original_surface as CENTER_SCOPE

---

## Absolute Constraints Honored

- [x] NEVER modified bridge.py, decision_composition.py, projection.py, claim_adapter.py
- [x] NEVER declared HOKOM-TAAQOL-LIVE-INTEGRATION-01 = CLOSED
- [x] NEVER used git add -A or git add .
- [x] NEVER imported HR2S at runtime
- [x] NEVER added HR2S as a dependency
- [x] NEVER added skip/xfail to existing tests
- [x] NEVER deleted existing tests
- [x] NEVER separated واو الجماعة, ألف الاثنين, نون النسوة as enclitics
- [x] NEVER separated a prefix without a legal host remaining
- [x] NEVER guessed prefix by first-letter similarity alone
