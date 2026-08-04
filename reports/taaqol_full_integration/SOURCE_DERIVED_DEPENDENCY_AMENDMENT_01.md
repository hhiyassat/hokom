# SOURCE-DERIVED DEPENDENCY AMENDMENT — 01

**Document ID:** `SOURCE_DERIVED_DEPENDENCY_AMENDMENT_01`  
**Issued:** 2026-08-01  
**Authority:** HOKOM_TAAQOL_MASTER_EXECUTION_CONSTITUTION_01 (§5)  
**Status:** APPLIED — supersedes conflicting sections of `14_IMPLEMENTATION_DEPENDENCY_GRAPH.md`

---

## Purpose

§5 of the Constitutional Order requires that the source-derived dependency
ordering be extracted directly from vendor type signatures and imports. Where
the previously documented ordering (14_IMPLEMENTATION_DEPENDENCY_GRAPH.md)
diverges from the source-derived ordering, this amendment governs.

All type enforcement is from `vendor/Taaqol-GPT/src/taaqqul_slot_geometry/`.

---

## I. Source-Derived Type Chain (read from vendor source)

### μ Pre-weight chain (E4B scope)

Each stage's output type is the TYPE-REQUIRED input to the next stage.
Enforcement is via `__post_init__` raising `WeightCarrierSchemaError`.

| Stage | μ-stage | Input | Output | Enforced at |
|---|---|---|---|---|
| 1 | μ_seq | Arabic text → (letter, haraka) pairs | `SyllableCandidate(units=tuple[tuple[str,str],...])` | pre_weight.py:92 |
| 2 | μ_boundary | `SyllableCandidate` | `SyllableSequenceCandidate(syllables=tuple[SyllableCandidate,...])` | pre_weight.py:133 |
| 3 | μ_word_carrier | `SyllableSequenceCandidate` | `WordBoundaryCandidate(sequence=SyllableSequenceCandidate)` | pre_weight.py:157 |
| 4 | μ_path_gate | `WordBoundaryCandidate` | `WordCarrierCandidate(bounded_surface=WordBoundaryCandidate)` | pre_weight.py:180 |
| 5 | μ_root_stem | `WordCarrierCandidate` | `PathCandidate(kind=PathKind, carrier=WordCarrierCandidate)` | pre_weight.py:207 |
| 6 | μ_original_extra | `PathCandidate` (kind=ROOT) | `RootStemCandidate(path=PathCandidate)` | pre_weight.py:229 |
| 7 | μ_ops | `RootStemCandidate` + ... | `OriginalExtraMap`, `OperationTraceCandidate` | pre_weight.py:256, 291 |
| 8 | μ_weight_readiness | `PreWeightSurface` | `WeightReadinessCandidate(surface=PreWeightSurface)` | pre_weight.py:369 |

**PreWeightSurface fields** (all type-enforced):
- `carrier: WordCarrierCandidate`
- `path: PathCandidate`
- `original_extra: OriginalExtraMap`
- `operations: OperationTraceCandidate`
- path.carrier MUST == carrier (identity check, pre_weight.py:350)

### Weight Fit chain (E4B→E4C scope)

| Step | Function | Input | Output |
|---|---|---|---|
| weigh() | weight_fit.py | `WeightReadinessCandidate` + `ResidualGovernanceVerdict` | `WeightFitResult(candidate=WeightFitCandidate)` |
| omega_governance() | mu_chain.py | `tuple[Residual,...]`, `Rank` | `ResidualGovernanceVerdict(state=GRANTED|BLOCKED|DEFERRED|REJECTED)` |
| assess_license() | licensing_boundary.py | `WeightFitCandidate`, `BoundaryEvidence`, `ResidualGovernanceVerdict` | `LicensingBoundaryResult` |
| prove_dal() | dal_only.py | `LicensingBoundaryVerdict` (from result) | `DalOnlyCandidate` |

**WeightFitCandidate.source** TYPE-ENFORCED:
```python
# weight_fit.py line 85
if not isinstance(self.source, WeightReadinessCandidate):
    raise WeightCarrierSchemaError(...)
```

**Consequence:** No bypass of the μ chain is possible. weigh() cannot accept
anything that is not a WeightReadinessCandidate.

---

## II. Source-Derived Phase Ordering (Constitutional Order)

```
E0: TARGET BASELINE FREEZE
    ↓ (SHAs confirmed; no implementation)
E1: AYAT-AL-DAYN CANONICAL LEXICAL REGISTRY
    → ayat_al_dayn_registry.py (74 ISM/FI3L entries)
    ↓
E2: P2 REGISTRY PROJECTION
    → registry_adapter.py imports AYAT_AL_DAYN_REGISTRY from E1
    → P2 blocker deactivated (registry_matches non-None)
    ↓
E3: HOKOM P3/P4/P5 CONTINUITY
    → Trace actual P2→P3 flow; identify real P3 blockers
    ↓
E4A: LICENSING BOUNDARY PRECONDITION GUARDS  ← DONE
    → build_licensing_boundary_verdict() interface
    → HARF / directive / empty-host guards (structural, vendor-independent)
    ↓
E4B: PRE-WEIGHT TYPED CARRIERS
    → Arabic diacritical text → (letter, haraka) pairs
    → SyllableCandidate → ... → WeightReadinessCandidate (all 8 μ-stages)
    ↓
E4C: NATIVE LICENSING BOUNDARY
    → weigh(WeightReadinessCandidate) → WeightFitCandidate
    → omega_governance() → ResidualGovernanceVerdict (GRANTED)
    → BoundaryEvidence(LEXICAL, segment_host, CANDIDATE, DAL_ONLY)
    → assess_license() → LicensingBoundaryResult (ELIGIBLE)
    → LicensingBoundaryVerdict produced for ISM/FI3L corpus tokens
    ↓
E5: DAL-ONLY CHAIN (prove_dal)
    → prove_dal(LicensingBoundaryVerdict) → DalOnlyCandidate
    ↓
E6: VERBAL MADLUL
    ↓
E7: FORMAL SHAPE + MUFRAD DALALAH [MaqamContextBoundary instantiated here]
    → MaqamContextBoundary requires SemanticSlotFrame (E7 prerequisite)
    ↓
E8: RELATION CANDIDATE (2+ ContractableUnit)
    ↓
E9: RELATION CLOSURE
    ↓
E10: IFADAH
    ↓
E11: HUKM
    ↓
E12: MANAT
    ↓
E13: TANZIL (weight-layer terminal)
    ↓
E13.5: AuditedTanzilBridge (audit-layer, closed Wave06)
    ↓
E14: MANTUQ CLOSURE + MAFHUM CLOSURE + AUDIT
    ↓
E15: GPT REASONABLENESS (R1–R8)
```

---

## III. Divergences from 14_IMPLEMENTATION_DEPENDENCY_GRAPH.md

| Old | Correction | Authority |
|---|---|---|
| E0 includes A0/A1 adapters and MaqamContextBoundary | E0 = SHAs only; A0→E2; A1→E4A/E4C; MaqamContextBoundary→E7 | §2, §4 |
| E1 = DalOnly (prove_dal) | E1 = AYAT-AL-DAYN CANONICAL LEXICAL REGISTRY | §2 |
| E2 = VerbalMadlul | E2 = P2 REGISTRY PROJECTION | §2 |
| E3 = Binding | E3 = P3/P4/P5 CONTINUITY | §2 |
| E4 = ContractableUnit | E4 = LICENSING BOUNDARY INTEGRATION (E4A/E4B/E4C) | §2, §5 |
| E5 = FormalShape (old label) | E5 = DAL-ONLY (prove_dal) under new ordering | §2, §9 |
| E7 = RelationCandidate (old label) | E7 = FORMAL_SHAPE_AND_MUFRAD_DALALAH; MaqamContextBoundary here | §4 |
| weigh() described after E5 | weigh() is E4B/E4C — prerequisite of prove_dal (E5) | source:weight_fit.py |

---

## IV. Arabic Text → SyllableCandidate Decomposition (E4B Implementation Note)

Arabic text with full harakat (diacritics) can be mechanically decomposed into
`(letter, haraka)` pairs via Unicode character analysis:

- Arabic consonants: U+0600–U+06FF range (letters)
- Harakat: U+064B–U+0652 range (tanwin, kasra, fatha, damma, sukun, etc.)
- Algorithm: iterate codepoints; accumulate (letter, haraka) pairs

This decomposition does not require an external phonological analyzer.
It is implementable in pure Python using `unicodedata` or direct `ord()` checks.

**E4B implementability:** CONFIRMED — no external dependency beyond Python stdlib.

---

## V. Frozen SHA Registry

| Artifact | SHA | Source |
|---|---|---|
| VENDOR_SHA | `35381739410071ac21dd96702ecbb2acb493f90d` | git HEAD of vendor/Taaqol-GPT |
| HOKOM_HEAD | `8e37b738ece7183818189146912cb14e3dce3a07` | git HEAD of hokom repo |
| CORPUS_SHA | `6bd635a05530965f13f76cf003f7738130badec6981bcb0e73f2465d386e1ed7` | SHA256 of corpus CSV |
| CORPUS_SIZE | 129 unique tokens from البقرة 2:282 | 01_CANONICAL_CORPUS_MANIFEST.json |
| REGISTRY_SIZE | 74 unique ISM/FI3L host surfaces | E1: ayat_al_dayn_registry.py |

---

*Amendment applied by autonomous execution agent per §5 and §15 of the Constitutional Order.*
