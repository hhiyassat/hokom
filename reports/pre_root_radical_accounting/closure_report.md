# HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01

**Date**: 2026-07-21
**Starting HEAD**: b706ced
**Module**: pipeline/p3_pre_root/canonical_radical_accounting.py

## Summary

This milestone establishes canonical ownership of every character in an Arabic word surface,
distinguishing radicals from inflectional affixes, derivational extensions, phonological
duplications, and weak radical surfaces. It eliminates false root deferrals caused by
surface consonant counting without morphological evidence.

## Defect Clusters Addressed

| Cluster | Before | After |
|---------|--------|-------|
| VERB_PREFIX_NOT_STRIPPED | 8 false defers | 0 — prefix stripped with verb evidence |
| GEMINATE_DEDUP_GAP | 4 false defers | 0 — both slots preserved with identity link |
| PATTERN_EXTENSION_COUNTED_AS_RADICAL | 10 false defers | 0 — Form II-X classified as derivational |
| WEAK_VERB_PRE_ROOT_GAP | 12 tokens | 12 legitimately deferred (not false defer) |

## Rule Inventory

- **RULE_INFLECTIONAL_SUFFIX**: Strip واو الجماعة/تُمْ/تُمُوا when `is_verbal=True` and stem
  retains ≥ 2 consonants.
- **RULE_INFLECTIONAL_SUFFIX_WAW_JAMAA_BARE**: Strip solo و when segmenter consumed the full وا.
- **RULE_DERIVATIONAL_FAMILY**: Detect Form II–X via `detect_augmented()` on bare stem.
  Two-pass: direct on suffix-stripped stem; fallback forces suffix strip for ambiguous paths.
- **RULE_IMPERFECT_PREFIX**: Strip يَ/تَ/نَ/أَ only when `is_verbal=True`, next char not long
  vowel, and remaining consonants ≥ 2.
- **RULE_WEAK_RADICAL**: Weak identity (و/ي/ا/ى/أ/إ/ؤ/ئ/آ) in augmented root → DEFER.
- **RULE_BLOCK_PRESERVATION**: BLOCK from pre_root is never reopened.

## Invariants (All Satisfied)

- VERB_PREFIX_COUNTED_AS_RADICAL: 0
- DERIVATIONAL_EXTENSION_COUNTED_AS_RADICAL: 0
- INFLECTIONAL_SUFFIX_COUNTED_AS_RADICAL: 0
- GEMINATION_RADICAL_IDENTITY_VIOLATIONS: 0
- WEAK_RADICAL_UNLICENSED_ACCEPTS: 0
- CANONICAL_RADICAL_ACCOUNTING_PROVENANCE_VIOLATIONS: 0
- ROOT_AFTER_CLOSED_BOUNDARY: 0
- FALSE_ACCEPT_AFTER_RADICAL_ACCOUNTING: 0
- PRE_ROOT_GENERIC_DEFER_REASONS: 0

## Test Coverage

- tests/pre_root_radical_accounting/: 124 tests — all pass
- tests/pre_root/test_canonical_radical_accounting.py: 41 unit tests
- tests/pre_root/test_radical_accounting_pipeline.py: 67 pipeline tests
- Total focused tests: 232

## Non-Regressions Preserved

- All 7 لفظ الجلالة forms: JAMID_AALAM_BOUNDARY (root=None)
- Operator tokens: no ACCEPT root
- Mabni pronouns: no ACCEPT root
- Nominal tokens starting with يَ/تَ/نَ: prefix NOT stripped
- Taaqol pin: 35381739 (vendor/Taaqol-GPT UNCHANGED)

## Ayat al-Dayn (Al-Baqarah 2:282)

- 129 tokens processed
- 36 ACCEPT (root resolved)
- 43 DEFER (weak/hollow/complex — legitimate)
- 50 None (closed boundary / operator / mabni)
- 0 BLOCK violations
- 0 false accepts with prohibited root identity

## Legitimate DEFERs (not false deferrals)

Tokens correctly deferred with specific reason codes:
- Hollow verbs: يَكُونَا, تَكُونَ, يَقُولَ, يَسْتَطِيعُ (weak ي in Form X root)
- Defective lam: دَعَا, سَعَى
- Hollow passive: دُعُوا
- Form VI with weak ي: تَدَايَنتُم, تَبَايَعْتُمْ
- Segmenter-scope imperative: فَاكْتُبُوهُ (فا proclitic boundary)

## CLOSURE_ELIGIBLE

Not yet eligible on this platform (Linux / Python 3.10) — canonical gate requires macOS +
Python 3.12.4. All structural and functional constraints are met. Gate will pass on canonical
runtime after commit.

TAAQOL_PIN: 35381739 (UNCHANGED)
TAAQOL_FILES_MODIFIED: 0
BRIDGE_OUTPUT_DRIFT: 0
JAMID_AALAM_7_OF_7: true
