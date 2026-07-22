# HARDEN-11: Stability and Determinism
Stage: HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01

## Results

| Property                        | Result |
|---------------------------------|--------|
| claim_key determinism (10 runs) | STABLE |
| hollow root claim_key stable    | STABLE |
| functional token claim_key      | STABLE |
| ambiguous bundle claim_key      | STABLE |
| different profiles → diff keys  | CONFIRMED |
| evaluation_id uniqueness (200)  | UNIQUE |
| candidate ordering (5 runs)     | STABLE |
| no cross-evaluation mutation    | CONFIRMED |
| surface provenance not shared   | CONFIRMED |
| SLOT_REGISTRY reload order      | DETERMINISTIC |
| CLAIM_PROFILE_VERSIONS reload   | DETERMINISTIC |
| DOMAIN_LICENSE_VERSIONS reload  | DETERMINISTIC |
| SlotId.value after reload       | STABLE |
| unexplained nondeterminism      | 0 |

## Tests
tests/sga/test_stability.py — 13 tests, 13 passed
