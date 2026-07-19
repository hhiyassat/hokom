# Word Class Ownership Audit
## HOKOM-WORD-CLASS-OWNERSHIP-AUDIT-01
**HEAD**: 3cd85cfba6b85f45bbf6431c1a37cf3cb606bdf3  
**Date**: 2026-07-19  
**Auditor**: Claude (Sonnet 4.6) — READ-ONLY, no production code modified  
**Baseline**: 3938 passed / 0 failed / 18 skipped

---

## Selected Case

**CASE C: WORD_CLASS_SHADOW_ONLY**

Word-class classifications are scattered as labels across four independent subsystems (P5 lexical, MorphologyPath, InflectionalForm.part_of_speech, Taaqol claim adapter) without a unified judgment engine that produces canonical ISM/FI3L/HARF for every token. The Taaqol vendor provides a complete ISM/FI3L/HARF architecture but it is not activated.

**Evidence**:
- No module in `pipeline/` produces ISM, FI3L, or HARF as a canonical verdict
- `hokom()` return dict has no `word_class` key
- 16 tokens traced — 0 receive a canonical word-class label
- 4 partial shadow classifiers produce incompatible label vocabularies
- `vendor/Taaqol-GPT` has `WordKindCandidate.ISM/FI3L/HARF` but import is blocked (Python 3.10)

---

## 15 Truth Principles Assessment

| # | Principle | Status | Evidence |
|---|---|---|---|
| T-01 | Every token receives exactly one of ISM, FI3L, or HARF | NOT_IMPLEMENTED | Zero tokens in live trace receive this label |
| T-02 | Word class is determined by morphological structure, not meaning | PARTIALLY_SUPPORTED | MorphologyPath uses structural evidence only; but no final ISM/FI3L/HARF synthesis |
| T-03 | Classification is deterministic and reproducible | NOT_IMPLEMENTED | No word-class engine to be deterministic; shadow classifiers disagree |
| T-04 | Mabni status is independent of word class | PARTIALLY_SUPPORTED | P5 lexical separates mabni subclasses correctly; but mabni tokens are not labelled HARF or ISM |
| T-05 | Operator status is a functional attribute, not the word class | SUPPORTED | `is_operator` field in MabniEntry is distinct from `lexical_class`; operator boundary ≠ HARF label |
| T-06 | Masdar is always ISM regardless of verbal origin | NOT_IMPLEMENTED | Masdar engine identifies masdar type; no ISM label projected |
| T-07 | Derivatives (ISM_FA3IL, ISM_MAF3UL…) are always ISM | NOT_IMPLEMENTED | Derivative engine identifies derivative type; no ISM label projected |
| T-08 | Verbal subclasses (tense/aspect) apply only within FI3L | VIOLATED | InflectionalForm.part_of_speech=VERB and tense/mood assigned to هَلْ، مِنْ، كَمْ (operators) — Bug B-01 |
| T-09 | Ambiguous surfaces are governed by residual codes, not guessed | PARTIALLY_SUPPORTED | AMBIGUOUS_MORPHOLOGY_PATH produces DEFER; but no word-class-specific residuals defined |
| T-10 | Word class is serializable and round-trippable | NOT_IMPLEMENTED | No word_class field in hokom() dict; no round-trip contract |
| T-11 | No parallel word-class engines (single canonical owner) | VIOLATED | Four shadow classifiers produce incompatible partial classifications simultaneously |
| T-12 | Word class gates downstream analysis | PARTIALLY_SUPPORTED | MorphologyPath gates inflection (verbal/non-verbal paths); but bug allows inflection on HARF tokens |
| T-13 | Canonical entrypoint is documented and enforced | NOT_IMPLEMENTED | No canonical entrypoint exists; no WORD_CLASS_CANONICAL_ENTRYPOINT constant |
| T-14 | All word-class decisions carry evidence_ids | NOT_IMPLEMENTED | No word-class decisions with evidence_ids exist |
| T-15 | Taaqol integration receives word class via defined contract | NOT_IMPLEMENTED | Taaqol bundle carries morphology_path as lexical_class (semantic mismatch); part_of_speech always None |

**Summary**: 1 SUPPORTED / 4 PARTIALLY_SUPPORTED / 3 VIOLATED / 7 NOT_IMPLEMENTED

---

## Gap Matrix Summary

| Status | Count | Capabilities |
|---|---|---|
| PRESENT | 1 | Operator/non-operator separation |
| PARTIAL | 9 | Lexical subclass, Mabni independence, Verbhood evidence, Tense subclass, Ambiguous handling, Serialization, Determinism, Residual governance, Pipeline integration, Demo display |
| ABSENT | 7 | Top-level ISM/FI3L/HARF, Masdar→ISM, Derivative→ISM, Canonical entrypoint, Ownership gate, Taaqol handoff |

---

## Word Class Producers (Live, Canonical)

**LIVE_WORD_CLASS_PRODUCERS**: 0 canonical producers.

**Shadow classifiers** (partial, non-canonical):
1. `pipeline/p5_lexical/mabni_projection.py` → `MabniBoundary.lexical_class` (6 mabni subclasses)
2. `pipeline/pre_root/morphology_path.py` → `MorphologyPath` (6 structural heuristic paths)
3. `pipeline/p5_inflection/models.py` → `InflectionalForm.part_of_speech` (VERB/VERBAL_NOUN/PARTICIPLE, runs on wrong tokens)
4. `pipeline/taaqol_integration/claim_adapter.py` → `HokomLinguisticClaimBundle.lexical_class` (morphology_path value as lexical_class — semantic mismatch)

**PARALLEL_WORD_CLASS_ENGINES**: 0 canonical. 4 shadow classifiers with conflicting scopes and vocabularies.

---

## Routing Effect

For mabni-boundary tokens (OPERATOR_BOUNDARY/MABNI_BOUNDARY):
- Root path is CLOSED — no root analysis
- Inflection engine runs WITHOUT morphology_path guard → false VERB features (Bug B-01)

For morphologically-open tokens:
- MorphologyPath classifies structural path
- verbal_root_path → inflection engine runs correctly
- nominal_morphology_path → inflection returns NOT_APPLICABLE
- ambiguous_morphology_path → inflection attempts analysis (may run)
- No ISM/FI3L/HARF synthesis occurs at any stage

**LIVE_ROUTING_EFFECT**: "MorphologyPath gates root and inflection analysis but no word-class verdict is ever synthesized. Bug B-01 causes false VERB assignment for all closed function words."

---

## Missing Contracts

1. No `WordClassOwnershipGate` dataclass
2. No `WORD_CLASS_CANONICAL_OWNER` constant
3. No `WORD_CLASS_CANONICAL_ENTRYPOINT` constant
4. No `word_class` key in `hokom()` return dict
5. No `word_class` field in `HokomLinguisticClaimBundle` (correct name — not morphology_path)
6. No residual codes: WORD_CLASS_AMBIGUOUS / WORD_CLASS_GAP / WORD_CLASS_CONFLICT
7. No mabni-boundary guard in `project_inflection_with_licensing()`

---

## Files Allowed to Change Next Stage

(HOKOM-WORD-CLASS-OWNERSHIP-01 — implementation, not audit)

```
pipeline/p5_lexical/         (new word_class_engine.py + word_class_models.py)
pipeline/word_class/          (new package if separate from p5_lexical)
hokom_pipeline.py             (add word_class to return dict + fix Bug B-01 guard)
pipeline/taaqol_integration/claim_adapter.py   (fix B-02, B-03)
tests/word_class/             (new test package)
reports/word_class/           (report files only — already open)
```

## Files Forbidden to Change Next Stage

```
pipeline/p5_inflection/       (ownership already closed — HOKOM-INFLECTION-PARADIGM-OWNERSHIP-01)
pipeline/p5_masdar/           (ownership already closed)
pipeline/p6_derivatives/      (ownership already closed)
pipeline/p3_candidate/        (root ownership closed)
pipeline/p4_wazn/             (pattern ownership closed)
pipeline/p4_masdar/           (masdar pattern closed)
pipeline/p4_mushtaqat/        (mushtaqat closed)
vendor/Taaqol-GPT/            (never modify vendor)
test_hokom.py                 (root-level test file — do not modify)
```

---

## Stability Gate Result

| Check | Result |
|---|---|
| HEAD | 3cd85cfba6b85f45bbf6431c1a37cf3cb606bdf3 |
| Baseline failures | 0 |
| Tracked files dirty | 0 (only ?? untracked: doc/ and hokom_demo.jsonl) |
| Taaqol submodule dirty | 0 |
| Python version | 3.10.12 |
| pytest version | 9.1.1 |

**AUDIT_BASELINE**: VALID

---

## HOKOM_WORD_CLASS_OWNERSHIP_AUDIT_01 = CLOSED
