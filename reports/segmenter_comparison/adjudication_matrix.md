# Adjudication Matrix — HOKOM-HR2S-SEGMENTER-COMPARATIVE-AUDIT-01

**Audit ID:** HOKOM-HR2S-SEGMENTER-COMPARATIVE-AUDIT-01
**Date:** 2026-07-20
**Corpus:** Ayat al-Dayn (Al-Baqarah 282)
**Total tokens:** 129

---

## Architecture Finding

**HR2S is NOT a segmenter.** It is the root analysis engine. No pairwise diff is possible.
This audit evaluates the Hokom segmenter against linguistic ground truth.

---

## Critical Failures (HOKOM)

### Token 41: سَفِيهًا — FALSE_PROCLITIC (CRITICAL)

| Field | Value |
|-------|-------|
| Surface | سَفِيهًا |
| Hokom output | PRC:س \| HOST:في \| ENC:ها |
| Expected | HOST:سَفِيهًا (unsplit nominal) |
| Criterion | A_DESTRUCTIVE |
| Verdict | HOKOM WRONG |

**Analysis (Qiyas):**
- اصل: سَفِيهًا — nominal form of root س-ف-ه (foolish/stupid)
- فرع: سَ + فِيهَا proposed by Hokom
- نسبة: سَ (future particle) only attaches to imperfect verbs; فِيهَا = في+ها (preposition+pronoun) is linguistically incoherent as a standalone host
- شرط: licensed proclitic attachment requires morphological category compatibility
- سبب: diacritic check passed (fatha on سَ); MIN_HOST_CONSONANTS_FUTURE=3, but في=2 consonants — the check SHOULD have rejected this
- مانع: NON_SEPARABLE_INITIALS does not include سفيه; lexical protection missing
- أثر: WHOLE TOKEN is HOST — سَفِيهًا is an unsplit nominal
- بقايا: Gap in engine — FUTURE_PARTICLE سَ is not blocked before nominal forms; MIN_HOST_CONSONANTS_FUTURE=3 but في has only 2 consonants

**Wait — recheck:** فِي = 2 chars bare (ف+ي) = 2 consonants. MIN_HOST_CONSONANTS_FUTURE=3. But هَا is being split as enclitic, leaving host=في with 2 consonants. The `_is_legal_host()` check uses `MIN_HOST_LENGTH_CHARS=2`, not `MIN_HOST_CONSONANTS_FUTURE`. Once the proclitic is extracted and the enclitic is tried, `_is_legal_host(stem)` only requires 2 chars, not 3. This is the bug path.

---

### Token 51: وَلِيُّهُ — FALSE_PROCLITIC (CRITICAL)

| Field | Value |
|-------|-------|
| Surface | وَلِيُّهُ |
| Hokom output | PRC:و \| HOST:لي \| ENC:ه |
| Expected | HOST:وَلِيّ \| ENC:هُ |
| Criterion | A_DESTRUCTIVE |
| Verdict | HOKOM WRONG |

**Analysis (Qiyas):**
- اصل: وَلِيُّهُ — guardian/ward (nominal of root و-ل-ي) + attached pronoun هُ
- فرع: وَ + لِيُّهُ proposed by Hokom (conjunction + remainder)
- نسبة: وَ in وَلِيّ is the FA of triliteral root و-ل-ي, NOT the conjunction وَ
- شرط: conjunction وَ requires a lexically independent remainder; لِيّ is not independent
- سبب: bare remainder ليه has 3 consonants (ل+ي+ه) — passes MIN_HOST_CONSONANTS_CONJUNCTION=3
- مانع: NON_SEPARABLE_INITIALS includes وعد/وجد/ولد but NOT ولي; gap in protection list
- أثر: HOST=وَلِيّ (root-initial وَ preserved) + ENCLITIC=هُ
- بقايا: وَلِيّ must be added to NON_SEPARABLE_INITIALS or WHOLE_TOKEN protection

---

### Token 59: يَكُونَا — FALSE_ENCLITIC (CRITICAL)

| Field | Value |
|-------|-------|
| Surface | يَكُونَا |
| Hokom output | HOST:يَكُو \| ENC:نَا |
| Expected | HOST:يَكُونَا (unsplit — dual inflectional) |
| Criterion | C_FALSE_ENCLITIC |
| Verdict | HOKOM WRONG |

**Analysis (Qiyas):**
- اصل: يَكُونَا — imperfect dual of hollow verb ك-و-ن (they-two become)
- فرع: يَكُو + نَا proposed by Hokom
- نسبة: نا in يَكُونَا is ألف التثنية (dual inflectional marker), NOT the first-person plural pronoun نَا
- شرط: INFLECTIONAL_BARE_SUFFIXES must include نا when context is dual verb
- سبب: نا is in ENCLITICS list; INFLECTIONAL_BARE_SUFFIXES does NOT include نا
- مانع: Gap — INFLECTIONAL_BARE_SUFFIXES = {وا, ون, ين, ان, ن, تم, تن} — نا is absent
- أثر: WHOLE TOKEN is HOST — يَكُونَا is unsplit
- بقايا: Genuine ambiguity — نا can be either dual ألف التثنية or 1st-person-plural enclitic; context resolution needed

---

## Defects (HOKOM)

### Token 93: لِلشَّهَادَةِ — MISSED_ARTICLE (DEFECT)

| Field | Value |
|-------|-------|
| Surface | لِلشَّهَادَةِ |
| Hokom output | PRC:ل \| HOST:لشهادة |
| Expected | PRC:ل \| ART:ال \| HOST:شهادة |
| Criterion | D_WRONG_HOST |
| Verdict | HOKOM DEFECTIVE |

**Analysis (Qiyas):**
- اصل: لِلشَّهَادَةِ = لِ (preposition) + الشَّهَادَة (noun with definite article)
- فرع: Hokom: PRC=ل, HOST=لشهادة (merged form, article not extracted)
- نسبة: لِ+الـ contracts to لِلـ in Arabic orthography/phonology
- شرط: `starts_with_definite_article()` must detect لِل→ال contraction in remainder
- سبب: After لِ is extracted, remainder is لشَّهَادَةِ; `starts_with_definite_article()` checks for ال at start, but sees ل+ش (solar assimilation)
- مانع: The remainder لشهادة starts with ل (from لِل), not ال; the function doesn't recognize the merged form
- أثر: HOST=شَهَادَة; ARTICLE=الـ (after لام merger); PRC=لِ
- بقايا: Engine needs لِل→ال contraction detection in `extract_definite_article_span()`

---

## Debatable / Minor Cases

### Tokens 36, 57: فَإِن — UNSPLIT_COMPOUND (MINOR/AMBIGUOUS)

| Field | Value |
|-------|-------|
| Hokom output | HOST:فإن (unsplit) |
| Alternative | PRC:ف \| HOST:إن |
| Verdict | AMBIGUOUS |

فَإِن can be treated as either a compound conditional conjunction or as فَ+إِن. The unsplit treatment is defensible for Quranic text processing where compound connectors are lexical units. The engine cannot split because إن has only 2 consonants and MIN_HOST_CONSONANTS_CONJUNCTION=3, which is the correct guard preventing false splits.

### Token 117: وَإِن — UNSPLIT_COMPOUND (MINOR/AMBIGUOUS)

Same analysis as فَإِن. وَإِن = conjunction + conditional is a recognized compound in Arabic grammar.

---

## Controlled Replay Notes

Since HR2S is not a segmenter, the controlled replay reduces to:

For each critical case, the impact on the downstream root engine is:

| Token | Hokom Host (sent to HR2S root) | Correct Host | Root Engine Impact |
|-------|-------------------------------|--------------|-------------------|
| سَفِيهًا → في | في (prep fragment) | سفيها | Root engine receives preposition fragment; root analysis will DEFER or BLOCK — contaminated |
| وَلِيُّهُ → لي | لي (2-char stub) | ولي | Root engine receives 2-char stub; likely DEFER — contaminated |
| يَكُونَا → يكو | يكو (3-char hollow stem) | يكونا | Root engine receives truncated hollow form; radicals may be partially recovered but nontrivially wrong |
| لِلشَّهَادَةِ → لشهادة | لشهادة (with extra ل) | شهادة | Root engine receives ل+شهادة; root ش-ه-د recoverable after stripping, but article normalization breaks |

---

## Adjudication Scores

| Metric | Count |
|--------|-------|
| TOTAL_TOKENS | 129 |
| CLEAN (correctly segmented) | 122 |
| CRITICAL_FAILURES_HOKOM | 3 |
| DEFECTS_HOKOM | 1 |
| AMBIGUOUS | 3 |
| HR2S_WINS | N/A (HR2S not a segmenter) |
| HOKOM_WINS | N/A (no competitor) |

