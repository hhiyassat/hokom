# 04A — TARGET VERSION RECOMMENDATION
## HOKOM × TAAQOL-GPT — TARGET_TAAQOL_SHA_SELECTION Gate

**Document ID:** `R0-04A-TARGET`  
**Gate:** `OWNER_DECISION_REQUIRED = TARGET_TAAQOL_SHA_SELECTION`  
**Date:** 2026-08-01  
**Status:** ⛔ AWAITING_OWNER_DECISION — DO NOT PROCEED PAST THIS POINT

---

## DECISION REQUIRED

```
OWNER_DECISION_REQUIRED     = TARGET_TAAQOL_SHA_SELECTION
DIRECT_VENDOR_PULL          = 0  (no pulling until decision made)
SUBMODULE_HEAD_CHANGE       = 0  (no change until decision made)
SUBMODULE_POINTER_CHANGE    = 0  (no change until decision made)
COPY_FROM_MAIN_INTO_HOKOM   = 0  (no copying until decision made)
VENDOR_UPDATE_ALLOWED       = 0  (no update without explicit owner instruction)
AUTONOMOUS_COMMIT_MODE      = 0  (no commit, no tag, no push, no merge)
```

The delta audit (§1–§8A) is complete. All technical facts are established. The owner must now select one of three options before any further execution proceeds.

---

## ESTABLISHED FACTS (BASIS FOR DECISION)

1. **PINNED_SHA = MERGE_BASE** — Pinned is the exact common ancestor of Hokom HEAD and origin/main. Main is 27 commits strictly ahead of pinned. Pinned is 0 commits ahead of main.

2. **ALL HOKOM-CRITICAL CONTRACTS BYTE-IDENTICAL** — weight/, core/, gpt/, lge/ packages are byte-for-byte the same in pinned and main. SHA256 verified on 21 files. Zero diff.

3. **ALL NEW MAIN CONTENT IS ADDITIVE AND OUT-OF-SCOPE** — 82 new symbols in main are entirely in `usm/` (Universal Science Matrix) and `x0r/` (extensions). Neither is imported by any Hokom E0–E15 adapter. Zero overlap.

4. **ZERO REMOVALS** — No symbol present in pinned has been removed in main.

5. **ALL HOKOM ADAPTERS KEEP_AS_IS** — 154 symbols across 12 adapter files all have DECISION = KEEP_AS_IS. No adapter change required for either SHA.

6. **REFERENCE SUITE UNTESTABLE ON PYTHON 3.10** — Requires Python 3.11+. Not a code regression; structural Python version requirement.

7. **E0–E8 IMPLEMENTATION COMPLETE** — FOCUSED_VERIFIED on Python 3.10. G_E1–G_E8 partially pending owner 3.12 verification (PENDING_OWNER_312 gates), not blocking.

---

## THREE OPTIONS

---

### OPTION A: KEEP_PINNED
**Target SHA:** `35381739410071ac21dd96702ecbb2acb493f90d` (current)

**What this means:**
- No action required. Submodule pointer stays where it is.
- All current adapters (E0–E8) continue to work exactly as implemented.
- `_VENDOR_SHA` stamps in all adapter files remain correct.
- E9–E15 (RelationClosure, Ifadah, Hukm, Manat, Tanzil, MantuqMafhum, GPT Reasonableness) proceed against pinned.

**Advantages:**
- Zero risk. Zero migration work.
- Known-stable baseline. Current test suite passes against pinned.
- Constitutional discipline: no change without clear need.

**Disadvantages:**
- Diverges further from upstream over time as main advances.
- USM and x0r capabilities (out-of-scope now, but potentially future scope) accumulate as unreachable.
- When E9–E15 eventually require symbols that later diverge in main, migration cost increases.

**Risk level:** ZERO  
**Migration effort:** ZERO  
**Recommended for:** Staying fully conservative; no timeline pressure on upstream parity.

---

### OPTION B: UPDATE_TO_CURRENT_MAIN
**Target SHA:** `3e48cc14d677b8d4980a58cd3b84d4464cbf60dc`

**What this means:**
- Submodule pointer updated from PINNED_SHA → CURRENT_MAIN_SHA.
- All `_VENDOR_SHA` values in adapter files updated from `35381739...` → `3e48cc14...`.
- Hokom adapters: KEEP_AS_IS (no functional changes, only SHA stamp update).
- Owner runs: `git -C vendor/Taaqol-GPT checkout 3e48cc14d677b8d4980a58cd3b84d4464cbf60dc`
- Then: git add + git commit for the submodule pointer change in Hokom.

**Advantages:**
- Tracks upstream. 27-commit gap eliminated.
- USM and x0r become available (even if not yet in scope).
- Future divergence risk minimized: next main advance will be from current HEAD, not 27-commit-old base.
- Reference test suite can be run against updated vendor.

**Disadvantages:**
- Requires submodule pointer change and commit (VENDOR_UPDATE_ALLOWED must be set to 1 by owner).
- `_VENDOR_SHA` stamps in all 9 adapter files must be updated (9 one-line edits).
- Owner must run full test suite on Python 3.12+ after update to confirm G_E1–G_E8 PENDING_OWNER_312 gates.

**Risk level:** VERY LOW (contracts byte-identical; functionally equivalent)  
**Migration effort:** LOW (9 SHA stamp updates, 1 submodule pointer commit, 1 test run)  
**Recommended for:** Minimizing long-term upstream debt; preparing for E9+ implementation against a live-tracked vendor.

---

### OPTION C: INTERMEDIATE SHA (CHERRY-PICK BOUNDARY)
**Target SHA:** Owner-specified commit between PINNED_SHA and CURRENT_MAIN_SHA

**What this means:**
- Owner identifies a specific intermediate commit in the 27-commit range (e.g., last commit before USM was introduced, or a tagged release point).
- Submodule pointer set to that intermediate SHA.
- `_VENDOR_SHA` stamps updated to that intermediate SHA.

**Advantages:**
- Can exclude USM/x0r entirely if owner does not want those packages visible.
- Allows tracking a specific named milestone in main.

**Disadvantages:**
- Requires owner to inspect the 27-commit log and identify the boundary.
- More complex than either KEEP_PINNED or UPDATE_TO_MAIN.
- Since USM/x0r are additive and non-interfering, there is no technical reason to stop mid-range.

**Risk level:** VERY LOW (same as Option B for the weight/ layer)  
**Migration effort:** MEDIUM (requires identifying the right commit)  
**Recommended for:** Cases where USM/x0r symbols must be kept out of the installed package for policy reasons.

---

## RECOMMENDATION (TECHNICAL BASIS ONLY)

From a pure technical standpoint, **Option B (UPDATE_TO_CURRENT_MAIN)** is optimal:

- Weight contracts are identical: zero functional risk.
- 27 commits are strictly additive: zero regression risk.
- Staying on pinned has no technical advantage.
- Updating now minimizes future migration cost.

However, the constitutional constraint `VENDOR_UPDATE_ALLOWED = 0` means the owner must explicitly authorize. This document provides the basis for that authorization decision.

---

## ⛔ GATE: OWNER_DECISION_REQUIRED

**No further execution proceeds until the owner selects an option.**

Provide one of:

```
OWNER_DECISION = KEEP_PINNED
```
```
OWNER_DECISION = UPDATE_TO_CURRENT_MAIN
```
```
OWNER_DECISION = INTERMEDIATE_SHA:<sha>
```

Upon receipt, execution resumes with:
- If KEEP_PINNED: proceed to E9 (RelationClosure) against PINNED_SHA.
- If UPDATE_TO_CURRENT_MAIN or INTERMEDIATE_SHA: owner performs submodule update; SHA stamps updated in all 9 adapters; full Python 3.12+ test run; then proceed to E9.

---

## ARTIFACTS PRODUCED (§1–§8A + §9)

| File | Contents |
|---|---|
| `00_SCOPE_AND_BOUNDARIES.md` | Directive scope |
| `01_CANONICAL_CORPUS_MANIFEST.json` | Corpus SHA and token list |
| `03A_PINNED_VENDOR_RUNTIME_INVENTORY.csv` | 719 pinned symbols |
| `03B_CURRENT_MAIN_RUNTIME_INVENTORY.csv` | 801 main symbols |
| `03C_VENDOR_MAIN_SYMBOL_DELTA.csv` | 82 ADDED, 0 REMOVED |
| `04_VENDOR_MAIN_PARITY_REPORT.md` | Full delta audit findings |
| `04A_TARGET_VERSION_RECOMMENDATION.md` | This document |
| `05A_HOKOM_IMPL_FILE_INVENTORY.csv` | 12 files audited |
| `05B_HOKOM_IMPL_SYMBOL_AUDIT.csv` | 154 symbols, all KEEP_AS_IS |
| `05C_HOKOM_IMPL_AUDIT_SUMMARY.csv` | Audit counts |
| `06_API_COMPATIBILITY_MATRIX.csv` | 51 COMPATIBLE, 3 NEW_OBLIGATION |
| `07_REFERENCE_TEST_SUITE_RESULT.json` | BLOCKED_BY_PYTHON_VERSION |
| `PREVIOUS_IMPLEMENTATION_COMPATIBILITY_AUDIT.md` | Narrative §8A audit |

---

**GATE STATUS: ⛔ AWAITING `OWNER_DECISION = TARGET_TAAQOL_SHA_SELECTION`**
