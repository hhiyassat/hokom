# HARDEN-04: Claim Profile Versioning
Stage: HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01

## Schema Version
CLAIM_PROFILE_SCHEMA_VERSION = "1.0.0"

## Profile Inventory
### Active (7)
| Profile ID             | Version | Stage Added                                              |
|------------------------|---------|----------------------------------------------------------|
| ROOT_CLAIM             | 1.0.0   | HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01 |
| PATTERN_CLAIM          | 1.0.0   | HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01 |
| BAB_CLAIM              | 1.0.0   | HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01 |
| MASDAR_CLAIM           | 1.0.0   | HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01 |
| DERIVATIVE_CLAIM       | 1.0.0   | HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01 |
| WORD_CLASS_CLAIM       | 1.0.0   | HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01 |
| FUNCTIONAL_OWNER_CLAIM | 1.0.0   | HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01 |

### Reserved (3)
| Profile ID                 | Version         |
|----------------------------|-----------------|
| SYNTACTIC_RELATION_CLAIM   | 0.0.0-reserved  |
| SEMANTIC_RELATION_CLAIM    | 0.0.0-reserved  |
| EXISTENCE_CLAIM            | 0.0.0-reserved  |

## Enforcement
- get_profile_version(unknown) → KeyError (fail-closed)
- get_profile_version(RESERVED) → RuntimeError (cannot execute)

## Violations
- Profile version violations: 0
- Unknown profile activations: 0

## Tests
tests/sga/test_profile_versioning.py — 17 tests, 17 passed
