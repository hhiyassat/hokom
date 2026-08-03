# HOKOM-GOLDEN-RULES-LIVE-CLOSURE-FINAL-AUDIT-01 — Audit Report

**Mandate:** HOKOM-GOLDEN-RULES-LIVE-CLOSURE-FINAL-AUDIT-01  
**Audited commit:** c98d35398d440cb3d51597fd8a19a4687ce1c581 (HEAD)  
**Audit date:** 2026-07-24  
**Report status:** PARTIAL — canonical environment (Python 3.12.4 / .venv-py312 / macOS) not executable in session

---

## § 1  HEAD Verification

| Field | Value | Status |
|---|---|---|
| HEAD (full) | c98d35398d440cb3d51597fd8a19a4687ce1c581 | ✓ |
| HEAD (short) | c98d353 | PASS |

---

## § 2  Working-Tree Classification

**Modified (binary, non-semantic):**
- `.DS_Store`, `data/.DS_Store`, `reports/.DS_Store` — macOS filesystem metadata, no source impact

**Untracked (non-semantic):**
- `data/dictionary/`, `data/test-data/`, `doc/` — supplemental data and documentation
- `reports/canonical_gate/`, `reports/segmenter_comparison/`, `reports/semantic_audit/`, `reports/sga_conformance/`, `reports/taaqol_consistency/` — auxiliary report directories
- `hokom_demo.jsonl` — scratch output

**Verdict:** No uncommitted source code, test, manifest, or golden_rules.md changes. Working tree is CLEAN for audit purposes.

---

## § 3  Canonical Environment

| Requirement | Session status |
|---|---|
| Python 3.12.4 | ❌ Session runs Python 3.10.12/Linux (sandbox) |
| .venv-py312 | ❌ Not active in session |
| macOS/Darwin | ❌ Session platform: Linux |

**The two runtime-contract tests (`test_python_version_is_canonical`, `test_virtual_env_is_canonical`) correctly FAIL on sandbox** — this is intended behaviour; they are guards that must not skip.

**Action required:** Run `bash scripts/run_canonical_final_audit.sh` on macOS with `.venv-py312` active. Script written at `scripts/run_canonical_final_audit.sh`.

---

## § 4  Digest Integrity

| Artifact | Expected digest | Status |
|---|---|---|
| `golden_rules.md` | `sha256:7b45e54ed6f2968d5846363749a1861c7d69964305f873ef3d67a993b76ea668` | ✓ GOLDEN_RULES_INTEGRITY_OK |
| `gold_manifest.py` MANIFEST_DIGEST | `sha256:7d09c9f5ce6c536e00ca41d3249b9c3829cbb104c3994c44fb3b9d911bc0d512` | ✓ MANIFEST_INTEGRITY_OK |

---

## § 5  Report File SHA-256

Committed files at HEAD c98d353 (verified before regeneration):

| File | SHA-256 | Status |
|---|---|---|
| `ayat_al_dayn_results.csv` | `9b30e7882c5e654bf9b38e7f587fd714f62592416e6d1d60081262eb13e94b02` | ✓ MATCH |
| `ayat_al_dayn_results_full.json` | `f4cf6f0628a0332d4c5f874b1df84cc71b9c0da5894d06e043026682d156359e` | ✓ MATCH (committed) |
| `ayat_al_dayn_manager_report.html` | `1c213815aaf9007ef9593d503a2bc85aedf92320243cf6f08f456fc81fcce877` | ✓ MATCH (committed) |

**Note:** JSON and HTML embed a `timestamp` field; re-generation produces different SHA-256 for those two files. CSV is fully deterministic and matches on re-generation. This is by design — the frozen committed files are the canonical reference.

---

## § 6  Live Probes (15 tokens, sandbox Python 3.10/Linux)

| Token | Expected | Observed | Status |
|---|---|---|---|
| اللَّهُ | wc=None, JAMID_AALAM_BOUNDARY | wc=None, boundary=JAMID_AALAM_BOUNDARY | ✓ PASS |
| اللَّهَ | wc=None, JAMID_AALAM_BOUNDARY | wc=None, boundary=JAMID_AALAM_BOUNDARY | ✓ PASS |
| اللَّهِ | wc=None, JAMID_AALAM_BOUNDARY | wc=None, boundary=JAMID_AALAM_BOUNDARY | ✓ PASS |
| سَيَسْتَغْفِرُونَ | FI3L / FORM_X / root=غفر | FI3L / FORM_X / root=غفر | ✓ PASS |
| يَسْتَغْفِرُونَ | FI3L / FORM_X / root=غفر | FI3L / FORM_X / root=غفر | ✓ PASS |
| وَاسْتَشْهِدُوا | FI3L / FORM_X / IMPERATIVE | FI3L / FORM_X / IMPERATIVE | ✓ PASS |
| فَاكْتُبُوهُ | FI3L / FORM_I / IMPERATIVE | FI3L / FORM_I / IMPERATIVE | ✓ PASS |
| وَاتَّقُوا | FI3L / FORM_VIII / IMPERATIVE | FI3L / FORM_VIII / IMPERATIVE | ✓ PASS |
| وَلْيَتَّقِ | FI3L / FORM_VIII / JUSSIVE | FI3L / FORM_VIII / JUSSIVE | ✓ PASS |
| أَجَلٍ | ISM / LEXICAL_NOUN | ISM / LEXICAL_NOUN | ✓ PASS |
| يَسْتَطِيعُ | FI3L / FORM_X / INDICATIVE | FI3L / FORM_X / INDICATIVE | ✓ PASS |
| يَكُونَا | FI3L / DU | FI3L / DU | ✓ PASS |
| تُدِيرُونَهَا | FI3L / FORM_IV / ACTIVE / root=دور | FI3L / FORM_IV / ACTIVE / root=دور | ✓ PASS |
| تَضِلَّ | correlated ambiguity (2MS\|3FS bundle) | candidates={2MS,3FS} | ✓ PASS |
| فَتُذَكِّرَ | correlated ambiguity (2MS\|3FS bundle) | candidates={2MS,3FS} | ✓ PASS |
| تَكُونَ | correlated ambiguity (2MS\|3FS bundle) | candidates={2MS,3FS} | ✓ PASS |

**PROBE_VERDICT: ALL_PASS (16/16 probes)** *(sandbox env — canonical re-verification required)*

---

## § 7  Test Suite (sandbox Python 3.10/Linux)

### Critical test files (governance + integration gold oracle + correction_01):

| Run | Tests | Passed | Failed | Notes |
|---|---|---|---|---|
| Sandbox RUN_1 | 135 | 135 | 0 | Excludes `test_canonical_runtime_contract.py` (intentional FAIL on wrong env) |
| Sandbox RUN_2 | 135 | 135 | 0 | Identical result — suite is deterministic |

Full 941-test integration suite exceeds 45s sandbox timeout; critical governance and oracle tests pass. **Canonical RUN required on macOS with `.venv-py312`.**

---

## § 8  Closure Gate (sandbox)

```
$ python scripts/run_live_gold_closure_gate.py
CLOSURE GATE PASSED — all metrics at threshold.
GATE_EXIT=0
```

All 10 CLOSURE_METRICS = 0 in sandbox execution.

---

## § 9  Constitutional Constraints — Verified Unmodified

| Constraint | Status |
|---|---|
| vendor/Taaqol-GPT unmodified | ✓ No changes in working tree |
| ROOT/PATTERN/MASDAR/DERIVATIVES/INFLECTION/WORD_CLASS/PYTHON_RUNTIME/TAAQOL/SEGMENTATION/FORM reopening | ✓ No such changes in working tree or commits |
| MANIFEST_DIGEST unchanged without amendment | ✓ Digest matches stored value |
| GOLDEN_RULES_DIGEST unchanged without amendment | ✓ Digest verified OK |
| No hard-coded runtime token list | ✓ Confirmed |
| No mock Taaqol | ✓ Confirmed |
| No monkey patches | ✓ Confirmed |
| gold assertions not weakened | ✓ All assertions == 0 |

---

## § 10  Final Verdict

```
SANDBOX_PROBE_VERDICT        = ALL_PASS (16/16)
SANDBOX_GATE_EXIT            = 0
SANDBOX_CRITICAL_SUITE       = 135/135 passed (RUN_1 = RUN_2)
GOLDEN_RULES_INTEGRITY       = OK
MANIFEST_INTEGRITY           = OK
HEAD_VERIFIED                = c98d353
WORKING_TREE                 = CLEAN (semantic)
CSV_DIGEST_MATCH             = OK (deterministic)
JSON_DIGEST_COMMITTED        = OK (timestamp field — non-deterministic on regen)
HTML_DIGEST_COMMITTED        = OK (timestamp field — non-deterministic on regen)

CANONICAL_ENV_EXECUTABLE     = NO (Terminal is click-tier; bash=Python 3.10/Linux)

CLOSURE_VERDICT = OPEN (CANONICAL_ENV_NOT_EXECUTABLE_IN_SESSION)
```

**To achieve VERIFIED_CLOSED:** Run `bash scripts/run_canonical_final_audit.sh` inside the repository on macOS with `.venv-py312` active. If all 10 closure metrics remain 0 and the full suite shows 0 failures, amend this verdict to `VERIFIED_CLOSED`.

All evidence gathered in this session is consistent with closure. The single blocker is the canonical environment constraint, which cannot be satisfied from within this session.
