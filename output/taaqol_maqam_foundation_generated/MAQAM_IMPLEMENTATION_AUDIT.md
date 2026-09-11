# MAQAM_IMPLEMENTATION_AUDIT — foundation round

**Label:** `MAQAM_THEORY_FOUNDATION_IMPLEMENTATION_WITH_TRACEABILITY` · **PROJECT_FINISHED = NO**

## Found before implementation
The existing package `taaqol_maqam_theory_implementation_01` already implements a strong core:
four-axis status separation (`birth.py`), rank-based conflict resolution and cause/condition/preventer
gating (`maqam.py::evaluate_maqam_birth`), and candidate-only text extraction (`nazila.py`). Its 7
tests pass. Gaps vs the QIYAS brief: closed `MaqamDimension` enum, missing `EXTERNALLY_SUPPLIED` rank,
no scholarly branches, scope stored but not actively matched, no explicit MAQAM≠NORMATIVE guard.

## Fixed / added this round (foundation layer, core preserved)
```
+ CoreMaqamDimensionRegistry  (versioned ratified set, 31 axes)      REQ-MAQAM-03/10
+ MaqamExtensionRegistry      (open; unknown => DEFER_OR_REGISTER;   REQ-MAQAM-10
                               silent drop forbidden by construction)
+ full evidence rank ladder   (+EXTERNALLY_SUPPLIED)                 REQ-MAQAM-09
+ four scholarly branches     (linguists/rhetoricians/usuliyyin/tafsir)  REQ-MAQAM-04..07
+ assert_maqam_not_normative  (guard, raises MaqamOverreachError)    REQ-MAQAM-08
+ scope_within                (active scope match)                   REQ-MAQAM-12
+ two deterministic nazila runs (A no-context / B example-only)      REQ-MAQAM-13/14
```

## Per-node summary (this round)
```
node                     producer_file                                          gate_decision   birth
EARLY_INTERPRETATION     taaqol_maqam/maqam.py                                  ACCEPT (run A)  certificate BORN(scope)
PROPOSITION_INTERP.      taaqol_maqam/maqam.py                                  DEFER  (run A)  UNBORN_PENDING
FACTUAL_CLAIM_BIRTH      taaqol_maqam/maqam.py                                  DEFER  (A)/ACCEPT(B example)  UNBORN_PENDING / BORN(example scope)
NORMATIVE_SOURCE         (not produced by maqām — separate branch)              n/a             UNBORN
NORMATIVE_HUKM           (forbidden — missing normative source)                 n/a             FORBIDDEN
MANAT / TANZIL / FINAL   (forbidden — ancestor unborn)                          n/a             FORBIDDEN
```

## Acceptance-criteria posture (honest)
```
THEORY_SOURCE_READ_COMPLETELY = NO (body text extraction uncertain; metadata verified)
THEORY_REQUIREMENTS_TRACED = OWNER_ADDENDUM_AND_QIYAS_TRACED; PDF_BODY_ITEMS_DEFERRED_WITH_RESIDUAL
MAQAM_CORE_REGISTRY_IMPLEMENTED = YES
MAQAM_EXTENSION_REGISTRY_IMPLEMENTED = YES
SCOPE_ENFORCEMENT_IMPLEMENTED = YES
EVIDENCE_RANKING_IMPLEMENTED = YES
CAUSE_CONDITION_PREVENTER_IMPLEMENTED = YES (existing core)
SPEECH_ACT_GATE / COREFERENCE / ELLIPSIS / WORD_ORDER = DEFERRED_WITH_RESIDUAL (foundation-round scope)
NORMATIVE_OVERREACH_COUNT = 0
DESCENDANT_BORN_WITHOUT_PARENT_COUNT = 0
CANONICAL_INTEGRATION = BLOCKED_WITH_CAUSE
TESTS_PASS = YES
```

## Tests run
```
tests/test_taaqol_maqam_foundation.py                         → 14 passed
taaqol_maqam_theory_implementation_01/tests (existing core)   → 7 passed
```
