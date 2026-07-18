# Mabniyat Comprehensive Validation — Guards + Governance + Phase A + Phase B Complete

**Status:** GUARDS I–VII + GOVERNANCE G1/G3/G4/G5 + PHASE A (P0_GLYPH_CLASSIFICATION) + PHASE B (P1_POSITION_CARRIER + PR 3.4 + PR 3.5) CLOSED
**Updated:** 2026-07-15

---

## Current Baseline

| Metric | Value |
|---|---|
| Manifest entries | 565 |
| Testable linguistic cases | 404 |
| Harness PASS | 237 (58.7%) |
| Full regression suite | **272 passed, 52 subtests, 0 failed** (hokom unit suite) |
| P0_UNLICENSED_TA_MARBUTA in harness | **0** (was: categorisation error, now correctly HAMZAT_WASL_STRUCTURE) |
| PROBABLE_RUNTIME_FAILURE in harness | **28** (was 29; one reclassified after harness fix) |
| FALSE_SUFFIX_SCAN | **0** |
| P4 monotonicity violations | **0** |
| Guard tests | **64** (31 guard + 33 governance) |
| Glyph classification tests | **122** (new, Phase A) |

---

## Guards Implemented (mabniyat_attachment.py)

| Guard | Description | Status |
|---|---|---|
| I-A | NUN_AL_NISWA blocked after host ending in ي/ى | ✓ DONE |
| I-B | NUN_AL_NISWA blocked after host ending in و (ونَ verbal plural) | ✓ DONE |
| II | TAU blocked after host ending in ا (sound feminine plural اتُ) | ✓ DONE |
| III / G3 | ALIF_AL_ITHNAYN moved to depth-guarded, then replaced with `_is_verbal_dual_host()` gate | ✓ DONE |
| IV | Monotonicity — WAW prefix false scan blocked (وَحْدَ family) | ✓ DONE (already correct) |
| V | Residual host re-checked in operators catalog → OPERATOR_BOUNDARY | ✓ DONE |
| VI | Orthographic unity for بِهِمْ/بِهَا + new TokenAnalysis fields | ✓ DONE |
| VII / G4 | Structural host guard — MABNI_DEFERRED candidates return DEFERRED verdict (not OPEN_TO_HR2S) | ✓ DONE |

### Verbal plural pattern (ونَ)
`_VERBAL_PLURAL_PATTERNS` maps `ونَ` → WAW_AL_JAMAA (attached) + `نَ` (inflectional_tail).
Triggered in `_not_segmented()` fallback when NUN_AL_NISWA guard blocks the regular scan.

### New TokenAnalysis fields
- `inflectional_tail: str` — نون الرفع or other non-pronominal tail (e.g. `'نَ'` for ونَ)
- `original_residual_host: str` — pre-normalization host surface
- `canonical_residual_host: str` — NFC-normalized host surface

### Governance fixes (G1–G5)

**G1** — NUN_AL_NISWA guard replaced with `_is_mudaric_form()` host check.
Old: host ending in ي/ى → block. New: block only when NOT a mudāri' verb form.
يَرْمِينَ, يَسْعَيْنَ now segment correctly; نَاءِمِينَ, ءَلْمَسَاكِينَ still blocked.

**G2 (DEFERRED)** — يَدْعُونَ ambiguity documented as TODO in `_VERBAL_PLURAL_PATTERNS`.
Current treatment (WAW_AL_JAMAA + inflectional نَ) kept unchanged.
No word-specific exception. No test added.

**G3** — ALIF_AL_ITHNAYN removed from `_DEPTH_GUARDED_CATALOG_IDS` and added to
`_MULTI_SPAN_VALID_IDS`. Host validated by `_is_verbal_dual_host()` (fatha on first
consonant, not definite-article-initial). كَتَبَا/ذَهَبَا now segment at depth 0;
حِينَمَا stays blocked (kasra on first letter).

**G4** — When all candidates have MABNI_DEFERRED host, `recognize_token` returns a
`DEFERRED` `TokenAnalysis` with `host_route=MABNI_DEFERRED` — no longer promotes to
`OPEN_TO_HR2S`. P4 monotonicity preserved.

**G5** — `HostAnalysis` dataclass and `_analyze_host()` function added. Three new fields
on `TokenAnalysis`: `host_mabni_id`, `host_operator_id`, `host_identity_status`.
`_analyze_host` probes both mabniyat catalog and operators catalog independently.
`identity_status`: DUAL_LICENSED | OPERATOR_ONLY | MABNI_ONLY | NONE.
أَنَّهُمْ: OPERATOR_BOUNDARY, DUAL_LICENSED, mabni_id=ANNA, op_id=ANNA.

### Depth-guarded catalog IDs
`_DEPTH_GUARDED_CATALOG_IDS = set()` — now empty; ALIF_AL_ITHNAYN moved to host-validated gate.
`_MULTI_SPAN_VALID_IDS = {'ATTACHED_PRONOUN_ALIF_AL_ITHNAYN'}` — valid as non-rightmost span
in multi-suffix segmentation (enables كَتَبَاهُ: ا + هُ).

---

## Completed This Session (prior)

- Live integration of attached mabniyat.
- COMPOSITE_BOUNDARY and MABNI_ATTACHED display.
- EMPTY-host handling for forms such as لَهُمْ.
- Standalone mabni routing such as هِيَ → MABNI_BOUNDARY → DAL.
- Explicit-diacritic compatibility guard.
- Original-surface lookup before normalized-surface lookup
  (`original_surface` parameter added to `recognize_token()`).
- Six-tier harness classification.
- Addition of licensed full forms to `mabniyat_catalog_split_vocalized.csv`:
  - `تَانِكَ` (TANIKA) — dual fem remote demonstrative
  - `ذَانِكَ` (DHANIKA) — dual masc remote demonstrative
  - `ثَمَّكَ` (THAMM_KAF) — ثَمَّ + obligatory kaf al-khitab
  - `هَاهُنَاكَ` (HAHUNA_KAF) — هَاهُنَا + obligatory kaf al-khitab
- Harness NFC normalization fix:
  `_KNOWN_SOURCE_DATA_ISSUES` keys and surface lookup key both normalized
  via `unicodedata.normalize('NFC', ...)`.
- Story regression `REGRESSION_CORRECT` dict corrected to match actual catalog IDs
  (ATTACHED_PRONOUN_HUM_SUFFIX not HUM, ATTACHED_PRONOUN_HA_FEM not HA, etc.).

---

## Governance Closure Notes (G1–G5)

**G1 CLOSED — for current licensed scope, not as a general morphological rule.**
`_is_mudaric_form()` detects يَ/تَ prefix + fatha + sukun on the second consonant.
This correctly handles all currently licensed NUN_AL_NISWA cases but will fail on
heavier augmented stems without a prefix sukun in position 3, e.g.:
- يُكْرِمْنَ (Form IV — no sukun at position 3; fatha→kasra shift)
- يَتَعَلَّمْنَ (Form V — first base char is ت at position 2, not 0)
- يَسْتَخْرِجْنَ (Form X — depth-3 prefix before first root consonant)
Treatment: NARROW MORPHOLOGICAL LICENSER, valid within current licensed inventory.
Before expanding the licensed inventory to include augmented verb forms, this
heuristic must be replaced by the Host Morphology Licensing layer (see below).

**G3 CLOSED — for current licensed scope, not as a general morphological rule.**
`_is_verbal_dual_host()` detects: not definite-article-initial, first base char ≠ ي,
first diacritic == fatha. This blocks حِينَمَ (kasra) correctly but may pass:
- nominal roots with fatha on the first consonant that are not verb stems
- hollow or assimilated verb stems where the fatha pattern differs
Treatment: TEMPORARY HOST LICENSING HEURISTIC. Must be replaced before the licensed
inventory includes nominal forms with initial fatha that should not take ألف الاثنين.

**G4 CLOSED.**
P4 monotonicity fully enforced: MABNI_DEFERRED host → DEFERRED verdict, never OPEN_TO_HR2S.

**G5 CLOSED.**
DUAL_LICENSED identity preserved in TokenAnalysis; operator-first routing does not
erase parallel mabni_id. HostAnalysis dataclass documented and exported.

**G2 DEFERRED — يَدْعُونَ.**
Ambiguity between (A) WAW_AL_JAMAA + نون الرفع and (B) original-و + NUN_AL_NISWA.
Current code resolves as (A). Correct resolution requires root-class lookup (ناقص-و).
Do NOT fix via word-specific exception. Fix belongs in the Host Morphology Licensing layer.

---

## Architectural Roadmap — Three-Phase Foundation Closure

**Ordering rationale:** glyph classification → position tracking → registry projection.
No later layer can be correct if an earlier one leaks. Any gap in P0 (e.g., ة blocked
as a foreign glyph, hamza variant not recognised) propagates uncorrectably into P1
position offsets, then P2 registry matches, then every higher layer. Host Morphology
Licensing (and G2 resolution) are deferred until all three are closed.

Each phase is a separate, independent change with its own:
  plan → implementation → focused tests → full regression → report

Do not combine phases. Do not begin Phase B until Phase A regression is clean.

---

### Phase B — P1_POSITION_CARRIER + PR 3.4 (أجوف) + PR 3.5 (ناقص)  ✓ CLOSED

**Closed:** 2026-07-15 — 272 tests + 52 subtests pass, 0 regressions.

**Deliverables (3 files touched):**

New files (2):
- `root_analysis.py` — root type inference engine (PR 3.4 + 3.5): types, form detectors, extract_radicals(), analyze_lexeme()
- `tests/test_root_analysis.py` — 98 focused tests covering all mandatory spec cases

Modified files (1):
- `normalizer.py` — `normalize_hamza_tracked()` changed from identity-run merging to per-char IDENTITY entries (Phase B compose() bugfix)

**PR 3.4 — Hollow (أجوف) closure conditions (all met):**
1. ✓ قَالَ alone → UnknownRadical{و،ي} at AYN → DEFER
2. ✓ يَقُولُ alone → ق و ل → ACCEPT (root only, no bab/paradigm)
3. ✓ يَبِيعُ alone → ب ي ع → ACCEPT
4. ✓ قَالَ + يَقُولُ → ق و ل → ACCEPT via paired lexeme
5. ✓ بَاعَ + يَبِيعُ → ب ي ع → ACCEPT
6. ✓ HOLLOW weakness + AYN weak_position on profile
7. ✓ يَئِسَ → ي ء س → ASSIMILATED + hamza_position='AYN' → ACCEPT (standalone fix)
8. ✓ يَبِسَ → ي ب س → ASSIMILATED → ACCEPT

**PR 3.5 — Defective (ناقص) closure conditions (all met):**
1. ✓ دَعَا alone → د ع UnknownRadical{و،ي} → DEFER
2. ✓ رَمَى alone → ر م UnknownRadical{و،ي} → DEFER
3. ✓ يَدْعُو alone → د ع و → ACCEPT (root only)
4. ✓ يَرْمِي alone → ر م ي → ACCEPT (root only)
5. ✓ دَعَا + يَدْعُو → د ع و → ACCEPT via lexeme
6. ✓ رَمَى + يَرْمِي → ر م ي → ACCEPT via lexeme
7. ✓ وَقَى, طَوَى → LAFIF DEFER (FA/AYN weak + LAM unknown → ≥2 weak positions)
8. ✓ يَضْرِبُونَ, يَكْتُبُوا, كِتَابِي, يَدْعُونَ → DEFER (phone-count guard)
9. ✓ عَلَى, إِلَى, مَتَى → decision ≠ ACCEPT (after normalize_hamza fails fatha-on-FA check)
10. ✓ دَعَا root NEVER ('د','ع','ا'); رَمَى root NEVER ('ر','م','ى')
11. ✓ ا final → INSUFFICIENT evidence; ى final → CONTRIBUTORY evidence for ي
12. ✓ All outputs JSON-serialisable via to_dict(); UnknownRadical serialises with `type` + `candidates` keys

**Phase B compose() bugfix (prerequisite — also closed):**
- `normalize_hamza_tracked()` now emits ONE SpanEntry(IDENTITY) per character instead of merged runs
- Eliminates coarse h_map entries that caused `project_to_raw()` to return wrong span when shadda EXPAND overlapped with a large identity block
- 52/52 span alignment tests pass (was 43/52 before fix)

**Governing invariant enforced:**
ا/ى appearing as the final surface character of a defective past form is NEVER promoted to a root identity. It receives an EvidenceAssessment (INSUFFICIENT or CONTRIBUTORY) and the LAM slot remains UnknownRadical{و،ي} until a present form provides SUFFICIENT evidence.

**Deferred to PR 3.6:**
- Lafif with ACCEPT resolution (وَقَى + يَقِي pairing)
- يَسْعَى + يَسْعَيْنَ disambiguation
- Internal Boundary Layer (IBL) — PR 3.6.5, before PR 3.7 compressed imperatives

---

### Phase A — P0_GLYPH_CLASSIFICATION  ✓ CLOSED

**Closed:** 2026-07-15 — 473 tests pass, P0_UNLICENSED_TA_MARBUTA = 0.

**Deliverables (10 files touched):**

New files (2):
- `glyph_classification.py` — new module, single source of truth for Arabic Unicode typing
- `tests/test_glyph_classification.py` — 122 focused tests

Consumer rewires (3 — now delegate to glyph_classification):
- `licensing.py` — `gate_unicode()` delegates to `classify_base_glyph()`; `_P0_CONSONANT_CHARS` includes ة; `CONSONANTS_25` deprecated
- `mabniyat_layer.py` — `_parse_char_diac_pairs()` is now a wrapper over `build_glyph_traces()`; `DIACRITICS` pattern deprecated
- `mabniyat_attachment.py` — `_last_base_char()`, `_is_mudaric_form()`, `_is_verbal_dual_host()` are thin wrappers over GlyphTrace accessors; `_DIACRITICS_RE` / `_FATHA` / `_KASRA` / `_DAMMA` / `_SUKUN` marked deprecated

Deprecation annotations only (5 — constants kept, marked for cleanup):
- `normalizer.py` — `ALL_DIACRITICS` annotated deprecated
- `mabni_inventory.py` — `_ARABIC_DIACRITICS` annotated deprecated
- `operator_id_map.py` — `_DIACRITICS` annotated deprecated
- `tokenizer.py` — `_DIACRITICS` annotated deprecated
- `build_mabniyat.py` — `DIAC_RE` annotated deprecated
- `src/arabic/phonology.py` — entire file marked `DEPRECATED — DO NOT IMPORT`

Harness fix (1):
- `scripts/build_mabniyat_test_harness.py` — `P0_UNLICENSED_TA_MARBUTA` check updated to call `gate_unicode()` directly instead of testing `'ة' in surface` (old heuristic predated Phase A; caused one misclassification)

**Phase A closure conditions (all met):**
1. ✓ Single source of truth for base char, mark, and NFC alignment (`glyph_classification.py`)
2. ✓ No standalone regex making linguistic decisions (wrappers delegate to GlyphTrace)
3. ✓ SUKUN_MARK vs ABSENT_HARAKA distinction preserved (`MarkClass.SUKUN` ≠ `MarkState.ABSENT`)
4. ✓ ة in real words (cases 1–4) passes P0 — `CONSONANT_TA_MARBUTA ∈ _P0_LICENSED`
5. ✓ Cases 5–9 (الهمزة metalinguistic labels) show SOURCE_DATA_ISSUE / HAMZAT_WASL_STRUCTURE
6. ✓ 473 tests pass, JSON harness doesn't regress

**Deprecated (not yet deleted — Phase A cleanup deferred):**
- `CONSONANTS_25` in `licensing.py`
- `_DIACRITICS_RE`, `_FATHA`, `_KASRA`, `_DAMMA`, `_SUKUN` in `mabniyat_attachment.py`
- `ALL_DIACRITICS` in `normalizer.py`
- `_ARABIC_DIACRITICS` in `mabni_inventory.py`
- `_DIACRITICS` in `operator_id_map.py` and `tokenizer.py`
- `DIAC_RE` in `build_mabniyat.py`
- `DIACRITICS` in `mabniyat_layer.py`
- `src/arabic/phonology.py` (entire file)

---

**Original Phase A spec (preserved for reference):**

**Goal:** every Unicode codepoint or combining sequence in Arabic text is assigned
a precise, typed classification before any downstream processing.

**Output types:**
```
GlyphClass (enum):
  BASE_LETTER          — base Arabic letter (excludes hamza carriers)
  HAMZA_CARRIER        — ا ء و ي as hamza seats (codepoint recorded)
  INDEPENDENT_HAMZA    — ء standing alone (not a carrier)
  TA_MARBUTA           — ة (currently blocked as foreign glyph — this closes that bug)
  ALIF_MAQSURA         — ى (including final-ya without dots)
  MADD_LETTER          — آ / ٱ / long-vowel letters in continuation
  SHADDA_MARK          — ّ
  HARAKA_MARK          — fatha / kasra / damma
  TANWIN_MARK          — tanwin fath / kasr / damm
  SUKUN_MARK           — explicit sukun (ْ) only — not implied absence of haraka
  ABSENT_HARAKA        — position where no haraka mark is present (distinct from sukun)
  COMBINING_SEQUENCE   — shadda+haraka, tanwin pair, or other multi-codepoint cluster
  UNKNOWN_MARK         — anything unclassified (error signal, not silently absorbed)

GlyphTrace (per codepoint / grapheme):
  glyph_class          — GlyphClass value
  original_codepoint   — exact Unicode codepoint as input
  canonical_codepoint  — after NFC
  normalized_form      — after Arabic-specific normalization (hamza unification etc.)
  mark_order           — position within a combining sequence (0 = base)
  provenance           — ORIGINAL | NFC | NORMALIZED | INFERRED
```

**Key distinctions this closes:**
- `ة` vs `ت` — currently ة may be rejected as unlicensed; GlyphClass makes it BASE_LETTER+TA_MARBUTA
- Explicit sukun (`ْ`) vs absent haraka — currently conflated in `_explicit_marks_compatible`
- Hamza-on-alif (`أ` / `إ` / `آ`) vs hamza-on-waw (`ؤ`) vs hamza-on-ya (`ئ`) vs standalone (`ء`)
- Shadda+haraka (`شَّ`) as a single COMBINING_SEQUENCE vs two independent marks
- Tanwin forms (`ً` `ٍ` `ٌ`) as TANWIN_MARK, not HARAKA_MARK
- Alif maqsura (`ى`) vs ya with dots (`ي`)
- Alif khanjariyya (`ٰ`) — in scope if it appears in any licensed form

**Tests (focused):**
```
ة / ت → different GlyphClass
أ / إ / آ / ء / ؤ / ئ → correct HAMZA_CARRIER vs INDEPENDENT_HAMZA vs MADD_LETTER
ى / ي → ALIF_MAQSURA vs BASE_LETTER
شَّ → COMBINING_SEQUENCE with mark_order [0=shadda, 1=fatha]
ً ٍ ٌ → TANWIN_MARK (not HARAKA_MARK)
ْ → SUKUN_MARK; absent haraka → ABSENT_HARAKA
NFC vs NFD round-trip: canonical_codepoint stable, original_codepoint preserved
combining-mark reorder → same GlyphTrace regardless of input order
```

**Regression gate:** 351 tests pass, story audit and JSON harness unchanged.

---

### Phase B — P1_POSITION_CARRIER

**Goal:** every glyph has a stable position across all normalization layers, and
any segmentation or normalization step can be reversed to recover the original span.

**Governing rule:**
> No segmentation or normalization step may make it impossible to recover every
> element's position in the original surface.

---

#### Phase B Diagnostic Findings (2026-07-15 — exploration only, no code changes)

**Three independent span gaps identified:**

**Gap 1 — normalize() produces no offset map.**
All three normalization functions change string length with no position tracking:

| Function | Changes length? | Example |
|---|---|---|
| normalize_hamza | YES | آ (1 cp) → ءَا (3 cp) |
| normalize_al | YES | الكتاب → ءَلكتاب (+1 cp) |
| normalize_shadda | YES | مِّ (3 cp) → مْمِ (4 cp); net +1 per shadda |

Five-case span delta table:
```
أُمِّهِمْ  raw=9  norm=10  delta=+1  ⚠ offsets shift after shadda site
أَنَّهُمْ  raw=9  norm=10  delta=+1  ⚠ offsets shift after shadda site
كَتَبَاهُ  raw=9  norm=9   delta=0    spans happen to be correct
بِهِمْ     raw=6  norm=6   delta=0    spans happen to be correct
وَحْدَهُمْ raw=10 norm=10  delta=0    spans happen to be correct
```

**Gap 2 — GlyphTrace.original_span is precise only within normalize()-output coordinates.**
`build_glyph_traces()` is called on the normalize()-output string. Even when
`same_length=True` makes original_span precise relative to the string it received,
that string is already offset-shifted from the raw surface in shadda cases.
Result: `original_span` is reliable only for tokens where normalize() is identity.

**Gap 3 — AttachedMabniSpan.span_start/end live in normalized coordinate space.**
`_strip_suffixes()` computes offsets as `len(host)` and `len(surface)` on whatever
normalized string was passed to `recognize_token()`. No back-projection to the raw
surface exists. `original_surface` parameter in `recognize_token()` is used for
catalog lookup only — it is never used for span remapping.

**Existing span infrastructure (what Phase B can build on):**
- `GlyphTrace.nfc_span` — always precise (computed by `_walk_string()`)
- `GlyphTrace.original_span` — best-effort (precise when normalize() is identity)
- `AttachedMabniSpan.span_start / span_end` — present, normalized-coord space only
- `TokenAnalysis.original_residual_host / canonical_residual_host` — string fields, no offsets
- `_walk_string()` in `glyph_classification.py` — the only character-level index tracker

**P1 insertion point:**
Between the raw surface and the first `normalize()` call. Each of the three
normalize_* functions must be wrapped in a character-alignment recorder that emits
`list[tuple[int, int, int, int]]` (raw_start, raw_end, norm_start, norm_end)
alongside the transformed string. That alignment map must then thread through
`recognize_token()` so every downstream span can be expressed in raw-surface
coordinates.

---

#### Phase B Implementation Plan

**B-1 — SpanAlignmentMap (new module: `span_alignment.py`)**
```python
@dataclass(frozen=True)
class SpanEntry:
    raw_start:  int    # inclusive, in original surface
    raw_end:    int    # exclusive, in original surface
    norm_start: int    # inclusive, in normalized surface
    norm_end:   int    # exclusive, in normalized surface
    op:         str    # 'IDENTITY' | 'EXPAND' | 'CONTRACT' | 'REPLACE'
    note:       str    # e.g. 'shadda expansion م' | 'hamza ءَا' | 'al prefix'

class SpanAlignmentMap:
    def project_to_raw(self, norm_start: int, norm_end: int) -> tuple[int, int]
    def project_to_norm(self, raw_start: int, raw_end: int) -> tuple[int, int]
```

**B-2 — normalize_tracked() wrappers**
```python
def normalize_hamza_tracked(s: str) -> tuple[str, SpanAlignmentMap]
def normalize_al_tracked(s: str)    -> tuple[str, SpanAlignmentMap]
def normalize_shadda_tracked(s: str) -> tuple[str, SpanAlignmentMap]
def normalize_tracked(s: str)       -> tuple[str, SpanAlignmentMap]
```
Non-tracked versions (`normalize()` etc.) remain unchanged for callers that don't need spans.

**B-3 — GlyphTrace.original_span upgrade**
After B-2 exists, `build_glyph_traces()` gains an optional `alignment: SpanAlignmentMap`
parameter. When provided, `original_span` is projected through the alignment map to
raw-surface coordinates (precise). When absent, falls back to current best-effort behavior.

**B-4 — AttachedMabniSpan raw_span field**
`recognize_token()` gains an optional `alignment: SpanAlignmentMap` parameter.
When provided, each `AttachedMabniSpan` gets a `raw_span: tuple[int,int]` field
in addition to `span_start/span_end` (normalized). Backward-compatible addition.

**B-5 — ComponentBoundary (new)**
```python
@dataclass(frozen=True)
class ComponentBoundary:
    kind:      str               # 'HOST' | 'PREFIX' | 'SUFFIX' | 'OPERATOR' | 'MABNI' | 'INFLECTIONAL_TAIL'
    surface:   str               # the surface string of this component
    norm_span: tuple[int, int]   # in normalized surface
    raw_span:  tuple[int, int]   # in original raw surface
```
Constructed by `recognize_token()` when alignment is provided.

**Tests (focused, new file: `tests/test_span_alignment.py`):**
```
normalize_hamza_tracked('آ')          → norm='ءَا', map: raw[0:1] → norm[0:3] (EXPAND)
normalize_al_tracked('الكتاب')       → norm='ءَلكتاب', map: raw[0:2] → norm[0:3] (EXPAND)
normalize_shadda_tracked('مِّ')       → norm='مْمِ', map: raw[0:3] → norm[0:4] (EXPAND)
normalize_tracked('أُمِّهِمْ')         → composite; project_to_raw(0,10) covers all
normalize_tracked('كَتَبَاهُ')         → identity; every raw span == norm span
GlyphTrace with alignment: أُمِّهِمْ → original_span of all 5 glyphs project to raw correctly
AttachedMabniSpan: كَتَبَاهُ → هُ raw_span == norm_span (identity case)
AttachedMabniSpan: أَنَّهُمْ → هُمْ raw_span ≠ norm_span (shifted by +1 from shadda)
```

**Regression gate:** 473 tests pass (351 hokom + 122 glyph_classification), harness unchanged.
normalize() remains unchanged for existing callers — tracked variants are additive only.

---

### Phase C — P2_REGISTRY_PROJECTION

**Goal:** a single unified `RegistryProjectionCandidate` structure replaces the
three separate catalog lookups (operators, mabniyat, attachment) and can be extended
to future registries (root-class, wazn, derivational) without architectural change.

**Output types:**
```
RegistryProjectionCandidate:
  registry_name        — OPERATOR | MABNI | ATTACHED_MABNI | INFLECTIONAL_ENDING |
                         DERIVATIONAL_AFFIX | ROOT_CLASS | WAZN |
                         CLOSED_FUNCTION_WORD | AMBIGUOUS_LEXEME
  entry_id             — catalog row identifier
  matched_surface      — surface string that triggered the match
  match_mode           — VOCALIZED_EXACT | CANONICAL_NFC | NORMALIZED | BARE_CONSONANTS
  evidence_rank        — 1 (highest) … N: ordering when multiple candidates collide
  identity_type        — MABNI_ONLY | OPERATOR_ONLY | DUAL_LICENSED | NONE
  functional_type      — what role this entry plays (PRONOUN | PARTICLE | VERB | ...)
  source_file          — originating CSV/JSON file
  source_row           — row ID within that file
  projection_status    — ACCEPTED | DEFERRED | REJECTED | COLLISION
  collision_set        — list of competing RegistryProjectionCandidates (if any)

ProjectionDecision:
  Resolves a collision_set into a single winner using priority rules:
    1. VOCALIZED_EXACT beats CANONICAL_NFC beats NORMALIZED beats BARE_CONSONANTS
    2. OPERATOR beats MABNI for routing (G5 operator-first rule encoded here, not in
       _analyze_host)
    3. evidence_rank as tiebreaker
  Records the losing candidates in collision_set for auditability.
```

**What this replaces / unifies:**
- Current: three separate lookup paths (`by_vocalized`, `_get_ops_inventory()`, `_analyze_host`)
- After: single `project(surface, original_surface)` call → list of `RegistryProjectionCandidate`
- The 27 DUAL_LICENSED_REVIEW harness cases become first-class `DUAL_LICENSED` candidates
- `_analyze_host` becomes a thin adapter over `project()` — no logic lives in it

**Future-proofing:** `registry_name` includes ROOT_CLASS, WAZN, DERIVATIONAL_AFFIX.
These are not populated now. Phase C just ensures the slot exists and is typed
so that P3_ROOT_STEM_CLOSURE can project onto the same structure without refactoring.

**Tests (focused):**
```
أَنَّ → collision_set=[OPERATOR(ANNA), MABNI(ANNA)] → DUAL_LICENSED, OPERATOR wins routing
ذَلِكَ → MABNI_ONLY, no operator entry
إِلَى → OPERATOR_ONLY
لَهُمْ → لَ projected as OPERATOR, هُمْ as ATTACHED_MABNI; collision_set empty for each
bare key collision (e.g., ان matches multiple entries) → collision_set non-empty, deferred
VOCALIZED_EXACT beats NORMALIZED when both present
```

**Regression gate:** 351 tests pass, story audit and JSON harness unchanged.

---

### After Phase C — Host Morphology Licensing (deferred)

Only after P0/P1/P2 are closed does it make sense to build `host_morphology.py`.
At that point `_is_mudaric_form` and `_is_verbal_dual_host` migrate into it and
G2 (يَدْعُونَ) is resolved via root-class projection from P2, not a hardcoded heuristic.

The `HostMorphClass` design from the earlier roadmap entry remains valid — it simply
waits for P2_REGISTRY_PROJECTION to be its data source.

---

## To Be Done

1. **Review the six remaining NORMALIZATION_HAMZA_MISMATCH cases.**
   All six currently get P4=BLOCK on their normalized forms (bare, no tashkeel,
   or impossible combining sequences). Determine whether the block is correct
   (unlicensed slot) or whether the original-surface fallback should have
   resolved them before slot engineering reaches them.

2. **Verify the general governing rule:**
   Written sukun and absence of haraka both represent a sakin letter;
   distinguish implicit sukun from genuinely unspecified diacritics.
   The fix to `_explicit_marks_compatible` (sukun on ياء/واو vs empty = compatible)
   must not extend to cases where the catalog absence of a diacritic means
   "any vowel is possible" rather than "this position is sakin."

3. **Review the classification of هَاْدُوْكَ:**
   Do not reject it merely for being dialectal.
   Determine whether it is `SOURCE_DATA_ISSUE` or a new tier
   `UNDERLICENSED_DIALECTAL` based on `relative_pronouns.json`'s declared scope.
   The neighbouring records (42: 'بب', 43: 'سالم قنديل') are junk;
   note whether the file header declares MSA-only scope.

4. **Verify provenance fields for the four newly added catalog rows:**
   Confirm `evidence_mode`, `derived_from`, `source_file`, and
   `source_record_id` are consistent with the fields of neighbouring rows
   (especially HAHUNA and THAMM) and with the harness manifest entries.

5. **Preserve the distinction between `residual_surface` and `reconstructed_host`**,
   especially in forms such as فَقَدُوهُ (connected-waw allomorph at depth ≥ 1).
   This distinction must survive any future refactor of `TokenAnalysis` fields.

6. **Do not** modify ة licensing, Hamzat al-Wasl handling, HR2S, or any
   unrelated layers as part of this paused task.

---

## Scope Constraints (always in force)

- Work only in `/Users/husseinhiyassat/hokom`.
- Do not create commits, tags, or merges.
- Do not modify any JSON file under `data/02_mabniyat/`.
- Do not change HR2S, DAL, LAFZI, P4 law, or licensed slot patterns.
- Source JSON files are evidence inputs; errors in them are reported, not corrected.
