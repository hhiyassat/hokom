# 15 — MANAGER DEMO ACCEPTANCE SCENARIO

**Document ID:** `R0-15-DEMO`  
**Phase:** R0 — Requirements Package  
**Date:** 2026-08-01  
**Status:** REQUIREMENTS_READY

---

## Purpose

This document defines the observable, verifiable output that constitutes proof of integration success for each major milestone. A "demo" here means: run the pipeline, observe the output, check the claimed state. No screenshots, no verbal claims — only emitted artifacts and verifiable verdicts.

---

## Demo D0 — P2 Blocker Fixed (E0 target)

**Claim:** "P2 registry_load_failure blocker is inactive. P3 opens."

**Run:**
```python
from hokom.canonical.stages.p2_p5 import run_p2
result = run_p2(token_surface="تَدَايَنْتُمْ", hokom_evidence=adapter.build_evidence())
```

**Expected output:**
```
blocker.registry_load_failure.is_active = False
p2_state = EXECUTED
p3_state = OPEN (was NOT_OPENED)
registry_matches ≠ None
```

**Falsifying condition:** `blocker.is_active = True` OR `registry_matches is None` → Demo FAILS, state = NOT CLOSED.

---

## Demo D1 — DalOnly on Ayat al-Dayn Tokens (E1 target)

**Claim:** "prove_dal() called with real LicensingBoundaryVerdict for آية الدين tokens."

**Run:**
```python
results = run_dal_only_corpus(corpus=AYAT_AL_DAYN_TOKENS)
```

**Expected output:**
```
total_tokens_attempted = 129
dal_only_candidate_produced = <N> (ISM + FI3L that are DAL_ONLY domain)
deferred_with_reason = <M>  # HARF, PIPELINE_DEFER, or domain mismatch
pipeline_defer_count = 8    # exactly 8 tokens remain DEFER (pipeline upstream)
vendor_sha_in_all = True
trace_id_synthetic = False  # zero synthetic IDs
```

**Falsifying condition:** Any `DalOnlyCandidate` with `trace_id` containing `"HOKOM_P5:"` or `"HOKOM_TRACE:"` → INVALID. Any LICENSED verdict on import failure → INVALID.

---

## Demo D2 — Single Token STOP Enforced (E4 target)

**Claim:** "Single token cannot produce RelationCandidate."

**Run:**
```python
single_cu = ContractableUnitGeometry(token_index=4, surface="آمَنُوا", ...)
result = attempt_relation_candidate(units=[single_cu])
```

**Expected output:**
```
result.state = CONSTITUTIONAL_STOP
result.reason = "RelationCandidate requires 2+ ContractableUnit"
no RelationCandidate artifact produced
```

**Falsifying condition:** RelationCandidate produced from single unit → Constitution violated, INVALID.

---

## Demo D3 — RelationCandidate from Clause Scope (E7 target)

**Claim:** "RelationCandidate proved on 2+ ContractableUnit from clause 01 of آية الدين."

**Run:**
```python
clause_units = get_clause_01_contractable_units()  # tokens 1–7
assert len(clause_units) >= 2
rc = prove_relation_candidate(units=clause_units, maqam=AYAT_AL_DAYN_MAQAM)
```

**Expected output:**
```
relation_candidate.state = PROVED
relation_candidate.unit_count >= 2
relation_candidate.trace_id = <from PipelineTrace>
relation_candidate.vendor_sha = 35381739410071ac21dd96702ecbb2acb493f90d
```

**Falsifying condition:** `unit_count < 2` → Constitution violated. `trace_id` synthetic → INVALID.

---

## Demo D4 — Full Vertical Chain to Tanzil (E12 target)

**Claim:** "Ifadah → Hukm → Manat → Tanzil complete for clause scope of آية الدين."

**Expected output:**
```json
{
  "stage": "P12_IFADAH_SPEECH_FORCE",
  "marker": "TERMINAL",
  "ifadah": { "state": "PROVED" },
  "hukm": { "type": "LINGUISTIC_STRUCTURAL", "state": "PROVED" },
  "manat": { "state": "PROVED" },
  "tanzil": { "state": "PROVED", "terminal": true },
  "vendor_sha": "35381739410071ac21dd96702ecbb2acb493f90d",
  "trace_id": "<from PipelineTrace>"
}
```

**Falsifying condition:** Any `state = STUB` or `state = MOCKED` in any field → NOT CLOSED.  
`hukm.type = FIQH_RULING` → Constitution violated (Hukm here = linguistic structural only).

---

## Demo D5 — MantuqClosure + MafhumClosure + AnswerAudit (E14 target)

**Claim:** "Full post-vertical closure complete. chain_report produced."

**Expected output:**
```json
{
  "mantuq_closure": { "state": "PROVED" },
  "mafhum_closure": { "state": "PROVED" },
  "answer_audit": { "state": "AUDITED" },
  "chain_report": {
    "stages_complete": ["DAL_ONLY","VERBAL_MADLUL","BINDING","CONTRACTABLE_UNIT",
                        "FORMAL_SHAPE","MUFRAD_DALALAH","RELATION_CANDIDATE",
                        "RELATION_CLOSURE","IFADAH","HUKM","MANAT","TANZIL",
                        "MANTUQ_CLOSURE","MAFHUM_CLOSURE"],
    "blocked": ["LAFZI","WADI"],
    "deferred": ["GPT_LIVE_PROVIDER"],
    "vendor_sha": "35381739410071ac21dd96702ecbb2acb493f90d"
  }
}
```

---

## Demo D6 — GPT Reasonableness Deterministic Track (E15 target)

**Claim:** "R1–R8 complete on deterministic track without live LLM call."

**Expected output:**
```
gpt_r1_state = COMPLETE (deterministic)
gpt_r2_state = COMPLETE (deterministic)
...
gpt_r8_state = COMPLETE (deterministic)
live_provider_called = False
live_provider_auth = OWNER_DECISION_REQUIRED (documented)
```

---

## What "Done" Looks Like — Final Acceptance

```
HOKOM_FULL_TAAQOL_TARGET_INTEGRATION = VERIFIED_CLOSED

Evidence:
- E0_REQUIREMENTS_READINESS.json  ✓
- E0_SCHEMA_FREEZE.json            ✓
- E1_DAL_ONLY.json                 ✓
- E2_VERBAL_MADLUL.json            ✓
- E3_BINDING.json                  ✓
- E4_CONTRACTABLE_UNIT.json        ✓
- E5_FORMAL_SHAPE.json             ✓
- E6_MUFRAD_DALALAH.json           ✓
- E7_RELATION_CANDIDATE.json       ✓
- E8_RELATION_CLOSURE.json         ✓
- E9_IFADAH.json                   ✓
- E10_HUKM.json                    ✓
- E11_MANAT.json                   ✓
- E12_TANZIL.json                  ✓
- E13_MANTUQ_CLOSURE.json          ✓
- E14_MAFHUM_CLOSURE_AUDIT.json    ✓
- E15_GPT_REASONABLENESS.json      ✓

All blocking_residuals = []
All synthetic_id_count = 0
All vendor_sha = 35381739410071ac21dd96702ecbb2acb493f90d
```

**Before all 17 certificates exist and all gates pass: no claim of completion is valid.**
