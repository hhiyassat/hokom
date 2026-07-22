# HARDEN-03: HokomClaimBundle Contract
Stage: HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01

## Contract File
pipeline/sga/bundle_contract.py

## Contract Version
BUNDLE_CONTRACT_VERSION = "1.0.0"

## Accepted Input Types
- HokomClaimBundle (produced by build_claim_bundle())

## Rejected Input Types
- dict → TypeError
- tuple → TypeError
- list → TypeError
- str → TypeError
- bytes → TypeError
- int → TypeError
- None → TypeError
- float → TypeError

## Contract Requirements
- claim_key: 64-character SHA-256 hex string
- surface.original_surface: non-empty, preserved through all stages
- AMBIGUOUS slots: candidate_set.selected must be None
- AMBIGUOUS slots: candidate_set must have ≥2 candidates
- profile_id: must be in CLAIM_PROFILES

## Key Functions
- validate_bundle(bundle) → (bool, list[str])  # diagnostic validation
- assert_valid_bundle_input(obj) → None | raises TypeError  # enforcement guard

## Provenance Status
PRESERVED — original_surface is never replaced by normalized_surface

## Ambiguity-Preservation Status
ENFORCED — selected=None guaranteed for all AMBIGUOUS slots (T-10)

## Tests
tests/sga/test_bundle_contract.py — 21 tests, 21 passed
