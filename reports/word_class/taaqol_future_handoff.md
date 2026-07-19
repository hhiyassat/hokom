# Taaqol Future Handoff — Word Class
## HOKOM-WORD-CLASS-OWNERSHIP-AUDIT-01
**HEAD**: 3cd85cf | **Date**: 2026-07-19

---

## 1. Current Integration Status

**TAAQOL_STATUS**: NOT_STARTED

The Taaqol-GPT vendor (`vendor/Taaqol-GPT`) contains a complete ISM/FI3L/HARF classification system via `WordKindCandidate` with:
- `WordKindCandidate.ISM`, `.FI3L`, `.HARF`
- Constitutional test suite: `test_formal_shape_word_class.py` (full ISM/FI3L/HARF contract tests)
- `word_class_closure_ref="word_class/ISM/closed"` references in multiple test files
- Layered word-kind gates: `b2_word_kind_gate.py`, `b3_source_identity_gate.py`, `b4_form_state_gate.py`

**Python Blocker**: Hokom runs on Python 3.10.12. Taaqol requires Python 3.11+ for structural pattern matching and other modern syntax. Strict-mode import is blocked until Python is upgraded or Taaqol is forked to 3.10-compatible syntax.

**Submodule status**: `vendor/Taaqol-GPT` is clean at `ee56e369fb1e7eb402998c1f73e83642134a0f34 (heads/main)`.

---

## 2. What Taaqol Provides for Word Class

Based on vendor test files (read-only inspection):

### 2.1 WordKindCandidate
```
WordKindCandidate.ISM   — اسم (noun, any nominal)
WordKindCandidate.FI3L  — فعل (verb, any verbal)
WordKindCandidate.HARF  — حرف (particle/function word)
```

### 2.2 Word Kind Gate Chain
- `B2: WordKindGate` — admits proposed word kind, verifies evidence
- `B3: SourceIdentityGate` — verifies source identity (JAMID_ENTITY, etc.)
- `B4: FormStateGate` — verifies form state for ISM subtypes
- `B6: ResidualAuditGate` — governs residuals after word kind assignment
- `B7: Integration` — full word kind integration with closure

### 2.3 Formal Shape for Word Class
```
shape_id = "WORD_CLASS.ISM"    canonical_name = "ism"
shape_id = "WORD_CLASS.FI3L"   (implied)
shape_id = "WORD_CLASS.HARF"   canonical_name = "harf"
```

### 2.4 Closure Reference
`word_class_closure_ref = "word_class/ISM/closed"` is required in multiple contexts (ifadah, hukm, tanzil, mantuq, relation closure, vertical path closure, dalalah closure).

---

## 3. What Hokom Must Provide for Handoff

For Taaqol to accept a word-class claim from Hokom, the `HokomLinguisticClaimBundle` must carry:

| Field | Current state | Required state |
|---|---|---|
| `lexical_class` | morphology_path string (wrong) | ISM \| FI3L \| HARF \| ISM_MABNI \| HARF_MABNI |
| `part_of_speech` | always None (bug) | VERB \| VERBAL_NOUN \| PARTICIPLE (for FI3L only) |
| `domain_directive` | DEFER for most open tokens | ACCEPT when word class is confirmed |
| evidence_ids | partial | must include `word_class:ism:…` or `word_class:fil:…` evidence |

---

## 4. Missing Contracts for Handoff

### Contract MC-01: ISM canonical claim
Hokom must produce: `{"word_class": "ISM", "ism_subclass": "FA3IL_PARTICIPLE" | "MAF3UL" | "MASDAR" | "JAMID" | "MABNI", ...}` with supporting evidence.

### Contract MC-02: FI3L canonical claim
Hokom must produce: `{"word_class": "FI3L", "tense": "PAST" | "IMPERFECT" | "IMPERATIVE", "voice": "ACTIVE" | "PASSIVE", ...}` gated on confirmed verbal morphology.

### Contract MC-03: HARF canonical claim
Hokom must produce: `{"word_class": "HARF", "harf_subclass": "Closed Function Word" | "Numerical Operator" | "Verbal Operator", ...}`. This is the closest to being ready — the P5 lexical `lexical_class` field maps directly.

### Contract MC-04: Mabni independence clause
The `mabni_status` field must be a separate boolean independent of `word_class`. A token can be ISM + mabni (pronouns) or HARF + mabni (function words).

### Contract MC-05: Word class residual codes
Define: `WORD_CLASS_AMBIGUOUS`, `WORD_CLASS_GAP`, `WORD_CLASS_CONFLICT` residual codes for cases where no definitive word class can be assigned.

---

## 5. Blockers Before Handoff Can Begin

1. **Python 3.10 blocker** — Taaqol strict-mode import fails on Python 3.10.
2. **No ISM/FI3L/HARF engine in Hokom** — Taaqol cannot receive what Hokom doesn't produce.
3. **Bug B-01** — Inflection engine must be guarded against mabni-boundary tokens before any HARF handoff.
4. **Bug B-02** — Claim adapter must read from `mabni.lexical_class` not `pre_root.morphology_path`.
5. **Bug B-03** — `part_of_speech` field must be wired to inflectional form, not `pre_root.pos`.
6. **Missing data** — Pronouns (هُوَ) and demonstratives (هَذَا) must be in mabni catalog.

---

## 6. Recommended Sequence

1. Fix Bug B-01 (inflection guard) — 1 file change in hokom_pipeline.py
2. Fix Bug B-02 (claim adapter lexical_class source) — 1 file change in claim_adapter.py
3. Fix Bug B-03 (part_of_speech wiring) — 1 file change in claim_adapter.py
4. Add pronouns/demonstratives to mabni catalog
5. Build WordClassEngine (new module in pipeline/p5_lexical/ or pipeline/word_class/)
6. Upgrade Python to 3.11+ (or fork Taaqol to 3.10)
7. Activate Taaqol word-class gates in shadow mode
8. Verify claim bundle round-trip with Taaqol strict mode

**Next stage**: HOKOM-WORD-CLASS-OWNERSHIP-01
