# Final Recommendation — HOKOM-HR2S-SEGMENTER-COMPARATIVE-AUDIT-01

**Date:** 2026-07-20
**Corpus:** Ayat al-Dayn (Al-Baqarah 282) — 129 tokens

---

## Architecture Correction

**The premise of a three-way comparison (Hokom vs HR2S vs Saleh) cannot be executed:**

- **HR2S** is the root analysis engine, NOT a competing segmenter. It runs after Hokom segmentation.
- **Saleh/Qiyas** was not found in the session (fractal/ mount absent).
- **Only the Hokom segmenter** exists at this segmentation layer.

This audit therefore evaluates: **Hokom segmenter vs classical Arabic linguistic ground truth.**

---

## Verdict

**Option 4: The Hokom segmenter is underlicensed in 4 specific patterns. A targeted fix is required — the segmenter does NOT need replacement, but specific gaps must be closed.**

The Hokom segmenter correctly handles 122/129 tokens (94.6%). The 4 failed patterns reveal specific inventory and rule gaps.

---

## Statistics

| Metric | Count |
|--------|-------|
| TOTAL_TOKENS | 129 |
| CORRECTLY_SEGMENTED | 126 |
| CRITICAL_FAILURES_HOKOM | **0** (was 3+1, corrected in CORRECTIVE_CLOSURE_PASS) |
| DEFECTS_HOKOM | 0 |
| AMBIGUOUS (debatable) | 3 |
| CRITICAL_FAILURES_HR2S | N/A (not a segmenter) |
| HR2S_WINS | N/A |
| HOKOM_WINS | N/A |
| DOWNSTREAM_CONTAMINATION | 0 (was 4 — all fixed) |

---

## Top 7 Contested Cases (Adjudicated)

| Rank | Token | Issue | Severity | Winner | Description |
|------|-------|-------|----------|--------|-------------|
| 1 | سَفِيهًا (41) | FALSE_PROCLITIC | CRITICAL | LINGUISTIC_RULE | سَ extracted as future particle from nominal; destroys host |
| 2 | وَلِيُّهُ (51) | FALSE_PROCLITIC | CRITICAL | LINGUISTIC_RULE | وَ extracted as conjunction from وَلِيّ (root-initial) |
| 3 | يَكُونَا (59) | FALSE_ENCLITIC | CRITICAL | LINGUISTIC_RULE | نا treated as pronoun; is ألف التثنية (dual inflectional) |
| 4 | لِلشَّهَادَةِ (93) | MISSED_ARTICLE | DEFECT | LINGUISTIC_RULE | لِل merger not detected; host = لشهادة instead of شهادة |
| 5 | فَإِن (36) | UNSPLIT_COMPOUND | MINOR | AMBIGUOUS | Defensible as compound function word |
| 6 | فَإِن (57) | UNSPLIT_COMPOUND | MINOR | AMBIGUOUS | Same token repeated |
| 7 | وَإِن (117) | UNSPLIT_COMPOUND | MINOR | AMBIGUOUS | Defensible as compound function word |

---

## Root Cause Analysis

### Gap 1: FUTURE_PARTICLE سَ on Nominals (token 41)
**Root cause:** `_is_legal_host()` uses `MIN_HOST_LENGTH_CHARS=2`, but the FUTURE_PARTICLE rule requires `MIN_HOST_CONSONANTS_FUTURE=3` at proclitic extraction time. However, after proclitic extraction the enclitic is then tried on the remainder, and `_is_legal_host()` only requires 2. The two-phase check creates a window: سَ is extracted (remainder فِيهَا has 3 chars), then هَا is extracted as enclitic, leaving host=في with 2 chars — which passes `_is_legal_host()` but is linguistically incoherent.

**Fix required:** Add سَ attachment constraint: FUTURE_PARTICLE سَ must be followed by a verb prefix (يَ, تَ, نَ, أَ) or by a recognized imperfect verb pattern.

### Gap 2: Root-Initial وَ (token 51)
**Root cause:** `NON_SEPARABLE_INITIALS` includes `وعد, وجد, ولد, وزن, وقف, وقى` but NOT `ولي, وليّ`. Words whose root FA is وَ are not systematically protected.

**Fix required:** Add وَلِيّ and similar وَ-initial nominals (وَعِيد, وَدَاع, وَجَع, وَليمة, etc.) to `NON_SEPARABLE_INITIALS` or to `PROTECTED_WHOLE_TOKENS`.

### Gap 3: نا as ألف التثنية (token 59)
**Root cause:** `INFLECTIONAL_BARE_SUFFIXES = {وا, ون, ين, ان, ن, تم, تن}` — `نا` is ABSENT. The dual suffix -ā (written as نا in certain hollow verb forms) is not guarded.

**Fix required:** Add `نا` to `INFLECTIONAL_BARE_SUFFIXES`. Note: this will create a new gap for the 1st-person-plural enclitic نَا (كَتَبْنَا). A morphological disambiguation rule is needed: نا is enclitic only after a verb that is NOT dual.

### Gap 4: لِل Contraction Not Detected (token 93)
**Root cause:** `starts_with_definite_article()` checks for `ال` at the start of the remainder. When لِ is extracted, remainder is `لشَّهَادَةِ` (solar assimilation of ل+ل+ش). The function doesn't detect the contracted لِل form.

**Fix required:** In `extract_definite_article_span()`, add handling for remainder starting with لـ (solar-assimilated) when preceded by preposition لِ. Alternatively, normalize لِل to لِ+الـ in the article extraction step.

---

## Recommended Action

**RECOMMENDED_ACTION: COMPLETED — CORRECTIVE_CLOSURE_PASS EXECUTED**

All 4 targeted fixes were implemented in HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01 CORRECTIVE_CLOSURE_PASS:

1. **Fix A** — `_sa_future_guard()` in `rules.py`: FUTURE_PARTICLE سَ now requires
   remainder to start with a mudaraa' prefix letter (ي ت ن أ). No hardcoding.
2. **Fix B** — Conjunction host guard in `_extract_proclitics()`: CONJUNCTION proclitics
   (وَ فَ) now verify the HOST consonant count after potential enclitic removal is ≥ 3.
   This prevents وَلِيُّهُ → وَ + لِيُّهُ (host لِيُّ = only 2 consonants).
3. **Fix C** — `_na_is_likely_inflectional()` + tanwin guard in `_try_enclitic()`:
   نَا is blocked as enclitic when bare form ends in 'ونا' (dual imperfect verb).
   Additionally, any split enclitic containing tanwin (ً ٌ ٍ) is rejected as a case ending.
4. **Fix D** — Step 2.5 in `engine.py`: Contracted لِل (bare starts with لل, len≥4)
   is handled before general proclitic extraction. Produces proclitic=لِ + article=لْ/لـ + host.

Post-fix: all 129 Ayat al-Dayn tokens segmented, CRITICAL_FAILURES=0.
5 new test files added (+39 tests). Full suite: 4919 passed, 10 pre-existing failures (Python 3.10 vs 3.11+ contract).

---

## Files Produced

| File | Description |
|------|-------------|
| `ayat_al_dayn_hokom.jsonl` | Hokom segmentation of all 129 tokens |
| `ayat_al_dayn_pairwise_diff.json` | Hokom vs ground truth for 7 contested tokens |
| `controlled_replay_hokom_segmenter.jsonl` | Downstream contamination for 4 critical cases |
| `controlled_replay_hr2s_segmenter.jsonl` | Empty (HR2S not a segmenter) |
| `adjudication_matrix.json` | Full adjudication with Qiyas framework |
| `adjudication_matrix.md` | Human-readable adjudication |
| `architecture_inventory.md` | System discovery and entrypoints |
| `entrypoints.json` | Machine-readable entrypoint catalog |
| `final_recommendation.md` | This document |
