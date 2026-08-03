# 09 — CONTEXT AND MAQAM REQUIREMENTS

**Document ID:** `R0-09-MAQAM`  
**Phase:** R0 — Requirements Package  
**Date:** 2026-08-01  
**Status:** REQUIREMENTS_READY

---

## 1. Overview

Maqam (مقام) context boundary is a cross-cutting concern in the Taaqol weight chain. The `maqam_context_boundary.py` module defines the boundary within which DAL and LAFZI analyses are constrained. It is an **integration carrier** (CARRIER/INTEGRATION) that must be provided before the weight chain begins.

---

## 2. Scope for آية الدين

| Maqam Property | Value | Source |
|---|---|---|
| Source text | البقرة 2:282 | Quran corpus |
| Domain | Contractual (عقود — debt/witness recording) | Semantic domain of the verse |
| Linguistic register | Classical Arabic (فصحى) | Standard for all Hokom analysis |
| Discourse type | Direct address (يَا أَيُّهَا الَّذِينَ آمَنُوا) | Vocative opening |
| Clause structure | Compound conditional clause with multiple obligations | Multi-token scope required for RelationCandidate |

---

## 3. MaqamContextBoundary Requirements

The adapter (A17_MAQAM_CONTEXT) must produce a `MaqamContextBoundary` instance containing:

| Field | Required Value | Notes |
|---|---|---|
| `source_id` | `BQR_2_282` | Surah:Ayah identifier |
| `domain` | `CONTRACTUAL` | Debt/witness domain classification |
| `register` | `CLASSICAL_ARABIC` | All tokens are fasih |
| `clause_scope_tokens` | list of token indices forming each clause | Required before RelationCandidate |
| `maqam_trace_ref` | live PipelineTrace trace_id | No synthetic IDs |
| `vendor_sha` | `35381739410071ac21dd96702ecbb2acb493f90d` | Pinned |

---

## 4. Clause Boundary Definition (آية الدين)

The ayat is a single long verse with multiple clause boundaries. The RelationCandidate (Stage 5) requires that at least 2 ContractableUnit instances are defined within a single MaqamContextBoundary. The following high-level clause groupings apply:

| Clause ID | Description | Approximate Token Range |
|---|---|---|
| CLAUSE_01 | يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا تَدَايَنْتُمْ بِدَيْنٍ | Tokens 1–7 |
| CLAUSE_02 | فَاكْتُبُوهُ... بِالْعَدْلِ | Tokens 11–15 (writing obligation) |
| CLAUSE_03 | وَلَا يَأْبَ كَاتِبٌ أَنْ يَكْتُبَ | Tokens 16–20 (scribe obligation) |
| CLAUSE_04 | وَلْيُمْلِلِ الَّذِي عَلَيْهِ الْحَقُّ | Dictation obligation |
| CLAUSE_05 | وَاسْتَشْهِدُوا شَهِيدَيْنِ | Witness obligation |
| CLAUSE_06 | فَإِنْ لَمْ يَكُونَا رَجُلَيْنِ | Substitute witness condition |
| CLAUSE_07 | وَاتَّقُوا اللَّهَ | Closing command |

**Implementation note:** Exact token-to-clause mapping must be verified against the 129-token corpus. The above is a structural sketch, not a binding classification. Clause mapping is an E7 deliverable (RelationCandidate scope).

---

## 5. Integration Requirements

**CONSTITUTIONAL_RECONCILIATION_01 AMENDMENT (2026-08-01):**
A17_MAQAM_CONTEXT scope corrected from E0 to E7. MaqamContextBoundary requires
SemanticSlotFrame which is produced in E7_FORMAL_SHAPE_AND_MUFRAD_DALALAH.
It cannot be instantiated in E0 (baseline freeze — no implementation).

1. `MaqamContextBoundary` must be instantiated in E7 (requires SemanticSlotFrame — E7 prerequisite)
2. All weight-chain stages from E7 onward inherit the same `MaqamContextBoundary` instance — no divergence
3. `maqam_trace_ref` must match the live `PipelineTrace.trace_id` for this run
4. Clause boundary tokens must be a subset of the 129-token canonical corpus
5. No clause boundary may cross a `PIPELINE_DEFER` token boundary without explicit documentation

---

## 6. Relationship to LAFZI and WADI

- **LAFZI (lafzi_b7_integration.py):** Uses maqam context to determine phonological boundary scope. Currently BLOCKED (no phonological analysis in Hokom). Maqam context is a prerequisite but LAFZI integration remains BLOCKED.
- **WADI (wadi_c8_integration.py):** Uses maqam context for WADI domain classification. Currently BLOCKED pending WADI classification.
- Both BLOCKED items must be documented with proof in their respective phase certificates.

---

## 7. Owner Decision Boundary

If the maqam domain classification is disputed (e.g., whether a token is in scope for a given clause), this is an OWNER_DECISION_REQUIRED item. No maqam reclassification may proceed without explicit owner authorization.
