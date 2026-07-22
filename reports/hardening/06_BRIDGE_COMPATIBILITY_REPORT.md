# HARDEN-06: Bridge Compatibility
Stage: HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01

## Positive Tests (valid HokomClaimBundle accepted): 4
- ROOT_CLAIM bundle
- FUNCTIONAL_OWNER_CLAIM bundle
- WORD_CLASS_CLAIM bundle
- DERIVATIVE_CLAIM bundle

## Negative Tests (forbidden input rejected): 8
- dict → TypeError
- tuple → TypeError
- str → TypeError
- bytes → TypeError
- list → TypeError
- int (42) → TypeError
- None → TypeError
- float (3.14) → TypeError

## H11-H15 Slot Preservation
- BAB_CANDIDATE_SET: present when bab provided
- MASDAR_CANDIDATE_SET: present when masdar provided
- DERIVATIVE_CANDIDATE_SET: present when derivative provided
- NUMBER_SLOT: present when number provided
- GENDER_SLOT: present when gender provided

## Ambiguity Preservation (T-10)
- Ambiguous root: R1/R2/R3 = UNKNOWN, ROOT_CANDIDATE_SET preserved, selected=None
- Ambiguous bab: AMBIGUOUS state, selected=None
- Ambiguous masdar: AMBIGUOUS state, selected=None

## Violation Counters (all 0)
- RAW_BRIDGE_CALLER_VIOLATIONS: 0
- CLAIM_BUNDLE_BYPASS_VIOLATIONS: 0
- OPAQUE_BRIDGE_INPUT_VIOLATIONS: 0
- AMBIGUITY_COLLAPSE_VIOLATIONS: 0
- AMBIGUOUS_SET_LOSS_VIOLATIONS: 0
- AMBIGUOUS_SILENT_SELECTION_VIOLATIONS: 0
- AMBIGUOUS_SELECTED_NOT_NONE_VIOLATIONS: 0
- AMBIGUOUS_RESIDUAL_MISSING_VIOLATIONS: 0

## Tests
tests/sga/test_bridge_compatibility.py — 26 tests, 26 passed
