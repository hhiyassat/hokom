# Finalization Roadmap

**Audit date:** 2026-07-21  
**Hokom HEAD:** b706ced  
**Taaqol PIN:** 35381739410071ac21dd96702ecbb2acb493f90d  

---

## TAAQOL: Area Status

### Closed Areas (as consumed by Hokom)
| Area | PR | Status |
|------|----|--------|
| SlotGraph / Center / Slot / Layer / Boundary | PR-2 | CLOSED |
| TraceLedger / TraceEntryCandidate | PR-2 | CLOSED |
| gamma() / GammaResult | PR-2 | CLOSED |
| RankLattice / Rank | PR-3 | CLOSED |
| ResidualPolicy / ResidualEvaluation / ResidualKind | PR-3 | CLOSED |
| EvidenceContract / EvidenceSource | PR-3 | CLOSED |
| TransitionGate / TransitionVerdict / TransitionState | PR-4/PR-6 | CLOSED |
| FailureCode (97 codes) | PR-2 → PR-10 | CLOSED |
| ForbiddenLineRegistry / CANONICAL_REGISTRY | PR-5 | CLOSED |
| Adapter Boundary (InMemoryModelClient) | PR-8 | CLOSED |
| Pre-weight chain + weight-image carriers | PR-10 | CLOSED |
| G0-C1..G0-C6 bare-stem pipeline | G0 | CLOSED |
| PR-22-AUDIT bridge (AuditedTanzilBridge) | PR-22 | CLOSED |

### Implemented-Not-Closed (not yet consumed by Hokom)
| Area | Status | Note |
|------|--------|------|
| AnswerAudit / ModelClient | TAAQOL_CLOSED, HOKOM_DEFERRED | Hokom is not a ModelClient; deferred per strict_mode |
| G0 full pipeline | TAAQOL_CLOSED, HOKOM_NOT_WIRED | Future milestone |
| weight.* Arabic carriers | TAAQOL_CLOSED, HOKOM_NOT_WIRED | Hokom owns morphology independently |
| lge.* sentence/relation slot runtime | TAAQOL_CLOSED, HOKOM_NOT_WIRED | Future milestone |
| x0r.* KPI/audit | TAAQOL_CLOSED, HOKOM_NOT_WIRED | Future milestone |
| gpt.* knowledge-origin | TAAQOL_CLOSED, HOKOM_NOT_WIRED | Not applicable to Hokom |

### Experimental / Auxiliary
| Area | Classification | Note |
|------|---------------|------|
| enriched_simulation_agent/ | AUXILIARY_EXPERIMENT | Explicitly prohibited from Hokom consumption |

### Open Public-Contract Obligations in Taaqol (none relevant to Hokom)
NONE — All Taaqol public contracts consumed by Hokom are stable. No Taaqol obligation blocks Hokom finalization.

---

## HOKOM: Stage Status

### Closed Stages
| Stage ID | Description | Commit |
|----------|-------------|--------|
| HOKOM-P0-P5-CLOSURE-01 | P0–P5 pipeline, MABNI/OPERATOR | ec41601 |
| HOKOM-CONSTITUTIONAL-AMENDMENT-01 | Python 3.11+ runtime, live Taaqol | f198696 |
| HOKOM-TAAQOL-LIVE-INTEGRATION-01 | Live Taaqol governance bridge | d0071cf / 2897037 |
| HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME | Segment-aware center scope | 4e0886a |
| HOKOM-WORD-CLASS-OWNERSHIP-01 | ISM/FI3L/HARF canonical ownership | 37561f4 |
| HOKOM-SEGMENTATION-OWNERSHIP-01 | Canonical clitic segmentation | b992d7e |
| HOKOM-POST-SEGMENTATION-ROUTING-01 | Post-segmentation morphology routing | 1000bb8 |
| HOKOM-ROOT-OWNERSHIP-01 | Canonical root ownership (10 types) | 291ea1e |
| HOKOM-MORPHOLOGY-PATTERN-OWNERSHIP-01 | FA3IL fix + pattern contracts + corpus tests | 0366776 |
| HOKOM-MASDAR-OWNERSHIP-01 | Canonical masdar ownership | ad376de |
| HOKOM-DERIVATIVES-OWNERSHIP-01 | Canonical derivatives ownership | f3c4724 |
| HOKOM-INFLECTION-OWNERSHIP-01 | Canonical inflection paradigm ownership | 3cd85cf |
| HOKOM-SLOT-ENGINE-PLURAL-VERB-UNLOCK-01 | CVV+V + hamzat-al-wasl false blocks | b7c09fd |
| HOKOM-JAMID-AALAM-BOUNDARY-01 | Jamid aalam boundary before root admission | 041599e |
| HOKOM-TAAQOL-VENDOR-POINTER-UPDATE-01 | Taaqol submodule advance to 35381739 | b706ced |

### Committed-Not-Formally-Closed
NONE detected at b706ced. All committed stages have corresponding closure manifests or  
closure documentation.

---

## OPEN HOKOM DEFECT CLUSTERS (from semantic audit at 4e0886a, open at b706ced)

### Severity Priority 1 — FALSE BLOCK (unsafe: complete processing failure)
None remaining. CVV+V and hamzat-al-wasl blocks were closed by HOKOM-SLOT-ENGINE-PLURAL-VERB-UNLOCK-01.

### Severity Priority 2 — Ownership Collisions
NONE.

### Severity Priority 3 — Public-Contract Incompatibilities
NONE.

### Severity Priority 4 — FALSE BLOCK (secondary)
NONE remaining after HOKOM-SLOT-ENGINE-PLURAL-VERB-UNLOCK-01.

### Severity Priority 5 — FALSE DEFER (root/word-class)

#### HOKOM-PRE-ROOT-VERB-PREFIX-STRIPPING-01 (RECOMMENDED NEXT)
| Field | Value |
|-------|-------|
| Stage ID | HOKOM-PRE-ROOT-VERB-PREFIX-STRIPPING-01 |
| Owner | pre_root |
| Scope | Strip مضارع prefixes (ي/ت/ن/أ) before consonant counting |
| Defect Cluster | VERB_PREFIX_NOT_STRIPPED_QUADRILITERAL |
| Affected Tokens | 13 |
| Depends On | HOKOM-SLOT-ENGINE-PLURAL-VERB-UNLOCK-01 (CLOSED) |
| Blocks | HOKOM-PRE-ROOT-GEMINATE-DEDUP-01 |
| Implementation Status | NOT_STARTED |
| Test Status | NOT_STARTED |
| Canonical Status | NOT_CLOSED |
| Estimated Risk | LOW (additive prefix detection, no regression to existing ACCEPT) |
| Recommended Order | 1 |
| Closure Criteria | All 13 tokens extract trilateral root; suite passes twice; node_ids_equal |

#### HOKOM-PRE-ROOT-GEMINATE-DEDUP-01
| Field | Value |
|-------|-------|
| Stage ID | HOKOM-PRE-ROOT-GEMINATE-DEDUP-01 |
| Owner | pre_root / root_candidate |
| Scope | Deduplicate shadda-marked consonants (count shadda as 1 radical, not 2) |
| Defect Cluster | GEMINATE_COUNTED_TWICE |
| Affected Tokens | 4 |
| Depends On | HOKOM-PRE-ROOT-VERB-PREFIX-STRIPPING-01 |
| Blocks | HOKOM-ROOT-PATTERN-EXTENSION-01 |
| Implementation Status | NOT_STARTED |
| Test Status | NOT_STARTED |
| Canonical Status | NOT_CLOSED |
| Estimated Risk | LOW |
| Recommended Order | 2 |
| Closure Criteria | يُمِلَّ[047], فَلْيُمْلِلْ[049], تَضِلَّ[067], بِكُلِّ[126] extract correct root |

#### HOKOM-ROOT-PATTERN-EXTENSION-01
| Field | Value |
|-------|-------|
| Stage ID | HOKOM-ROOT-PATTERN-EXTENSION-01 |
| Owner | root_candidate (consonant counter) |
| Scope | Strip pattern extension elements (ي in فَعِيل, و in فُعُول, ا in فِعَال, tanwin, dual) before root count |
| Defect Cluster | PATTERN_EXTENSION_COUNTED_AS_RADICAL |
| Affected Tokens | 14 |
| Depends On | HOKOM-PRE-ROOT-GEMINATE-DEDUP-01 |
| Blocks | HOKOM-WORD-CLASS-VERB-ISM-DISAMBIGUATION-01 |
| Implementation Status | NOT_STARTED |
| Test Status | NOT_STARTED |
| Canonical Status | NOT_CLOSED |
| Estimated Risk | MEDIUM (pattern-aware logic touches consonant counter) |
| Recommended Order | 3 |
| Closure Criteria | All 14 tokens produce trilateral root; شَهِيد/ضَعِيف/صَغِير/كَبِير/عَلِيم etc. correct |

### Severity Priority 6 — Coverage Improvements (word-class / catalog)

#### HOKOM-MABNI-FUNCTION-WORD-CATALOG-01
| Field | Value |
|-------|-------|
| Stage ID | HOKOM-MABNI-FUNCTION-WORD-CATALOG-01 |
| Owner | mabni_catalog / word_class_engine |
| Scope | Add لَا, إِنَّ, إِنَّ, لَيْسَ, كَمَا, مِمَّنَّ as HARF in post-proclitic host catalog |
| Defect Cluster | FUNCTION_WORD_HOST_NOT_CLASSIFIED |
| Affected Tokens | 13 |
| Depends On | HOKOM-ROOT-PATTERN-EXTENSION-01 (recommended; can be parallel) |
| Blocks | NONE |
| Implementation Status | NOT_STARTED |
| Test Status | NOT_STARTED |
| Canonical Status | NOT_CLOSED |
| Estimated Risk | LOW (catalog addition only) |
| Recommended Order | 4 |
| Closure Criteria | 13 tokens return HARF/HARF_CLOSED word class; suite passes twice |

#### HOKOM-MABNI-RELATIVE-PRONOUN-CATALOG-01
| Field | Value |
|-------|-------|
| Stage ID | HOKOM-MABNI-RELATIVE-PRONOUN-CATALOG-01 |
| Owner | mabni_catalog |
| Scope | Add الَّذِينَ, الَّذِي to mabni operator catalog with blocks_root_path=True, word_class=HARF |
| Defect Cluster | MABNI_NOT_CLASSIFIED_RELATIVE_PRONOUNS |
| Affected Tokens | 3 |
| Depends On | NONE |
| Blocks | NONE |
| Implementation Status | NOT_STARTED |
| Test Status | NOT_STARTED |
| Canonical Status | NOT_CLOSED |
| Estimated Risk | LOW |
| Recommended Order | 5 |
| Closure Criteria | 3 tokens return HARF/CLOSED_FUNCTION_WORD; suite passes twice |

#### HOKOM-WORD-CLASS-VERB-ISM-DISAMBIGUATION-01
| Field | Value |
|-------|-------|
| Stage ID | HOKOM-WORD-CLASS-VERB-ISM-DISAMBIGUATION-01 |
| Owner | word_class_engine |
| Scope | Fix verb patterns (Form II فَعَّلَ, Form X يَسْتَفْعِل, Form II imperfect تُفَعِّل, Form IV تُفْعِل, lam al-amr forms) routing to FI3L not ISM |
| Defect Cluster | VERB_MISCLASSIFIED_AS_ISM |
| Affected Tokens | 6 |
| Depends On | HOKOM-ROOT-PATTERN-EXTENSION-01 |
| Blocks | NONE |
| Implementation Status | NOT_STARTED |
| Test Status | NOT_STARTED |
| Canonical Status | NOT_CLOSED |
| Estimated Risk | MEDIUM (routing decision logic) |
| Recommended Order | 6 |
| Closure Criteria | 6 tokens produce FI3L; no regression to ISM tokens |

#### HOKOM-WORD-CLASS-ISM-VERB-DISAMBIGUATION-01
| Field | Value |
|-------|-------|
| Stage ID | HOKOM-WORD-CLASS-ISM-VERB-DISAMBIGUATION-01 |
| Owner | word_class_engine |
| Scope | Fix nominal/adverbial forms (الحق with ال, بَيْن, عِند, الأُخرى) routing to ISM not FI3L |
| Defect Cluster | NOUN_MISCLASSIFIED_AS_VERB |
| Affected Tokens | 7 |
| Depends On | HOKOM-WORD-CLASS-VERB-ISM-DISAMBIGUATION-01 |
| Blocks | NONE |
| Implementation Status | NOT_STARTED |
| Test Status | NOT_STARTED |
| Canonical Status | NOT_CLOSED |
| Estimated Risk | MEDIUM |
| Recommended Order | 7 |
| Closure Criteria | 7 tokens produce ISM/HARF; no regression to FI3L tokens |

#### HOKOM-PRE-ROOT-WEAK-VERB-01
| Field | Value |
|-------|-------|
| Stage ID | HOKOM-PRE-ROOT-WEAK-VERB-01 |
| Owner | pre_root |
| Scope | Open root path for medial-waw (أجوف) verbs, جمع تكسير patterns (فُعَلاء), مصدر فَعَالَة |
| Defect Cluster | PRE_ROOT_PATH_NOT_OPENED_FOR_WEAK_VERBS |
| Affected Tokens | 7 |
| Depends On | HOKOM-PRE-ROOT-VERB-PREFIX-STRIPPING-01 |
| Blocks | NONE |
| Implementation Status | NOT_STARTED |
| Test Status | NOT_STARTED |
| Canonical Status | NOT_CLOSED |
| Estimated Risk | MEDIUM |
| Recommended Order | 8 |
| Closure Criteria | يَكُونَا[058], تَكُونَ[098] produce FI3L + root ك-و-ن; suit passes twice |

### Severity Priority 7 — Reporting-Only Defects
NONE detected.

---

## Governance / Tooling Defects

| Defect | Status | Note |
|--------|--------|------|
| upstream_taaqol_tests_pass=False in strict_mode | KNOWN_OPEN | 19 upstream failures in Taaqol repo (missing source files). Not a Hokom defect. |
| Python 3.10 sandbox cannot run StrEnum tests | KNOWN_OPEN | Infrastructure constraint; 32 tests skip in sandbox, pass on Python 3.12 |
| docs/upstream-provenance/Taaqol-GPT.json records old commit | KNOWN_STALE | Records ee56e369 (initial integration commit); b706ced updated pointer to 35381739 |

---

## Recommended Execution Order

```
1. HOKOM-PRE-ROOT-VERB-PREFIX-STRIPPING-01     [pre_root]          HIGH severity, 13 tokens, NEXT
2. HOKOM-PRE-ROOT-GEMINATE-DEDUP-01            [pre_root]          HIGH severity, 4 tokens
3. HOKOM-ROOT-PATTERN-EXTENSION-01             [root_candidate]    MEDIUM severity, 14 tokens
4. HOKOM-MABNI-FUNCTION-WORD-CATALOG-01        [mabni_catalog]     MEDIUM, 13 tokens, can parallel with 3
5. HOKOM-MABNI-RELATIVE-PRONOUN-CATALOG-01     [mabni_catalog]     MEDIUM, 3 tokens, can parallel with 3
6. HOKOM-WORD-CLASS-VERB-ISM-DISAMBIGUATION-01 [word_class_engine] HIGH severity, 6 tokens
7. HOKOM-WORD-CLASS-ISM-VERB-DISAMBIGUATION-01 [word_class_engine] HIGH severity, 7 tokens
8. HOKOM-PRE-ROOT-WEAK-VERB-01                 [pre_root]          MEDIUM, 7 tokens
```

**Total open defect tokens:** 67 across 8 clusters  
**All defects are Hokom-internal** — no Taaqol contract changes required for any of them.

---

## TAAQOL Integration Milestone Roadmap (Future)

These are not defects — they are planned future integration points after Hokom's  
Arabic morphology stages are more complete:

| Milestone | Taaqol Area | Prerequisite |
|-----------|-------------|-------------|
| HOKOM-G0-INTEGRATION-01 | G0-C1..G0-C6 bare-stem pipeline | Root ownership stages complete |
| HOKOM-ANSWER-AUDIT-01 | AnswerAudit / ModelClient | Hokom acts as answer evaluator (future) |
| HOKOM-LGE-INTEGRATION-01 | lge sentence/relation slot runtime | Sentence-level pipeline (not yet in scope) |
