# HARDEN-05: Domain License Versioning
Stage: HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01

## Schema Version
DOMAIN_LICENSE_SCHEMA_VERSION = "1.0.0"

## License Registry File
pipeline/sga/license_registry.py

## License Inventory (8 total, all ACTIVE)
| License ID             | Transition                                    |
|------------------------|-----------------------------------------------|
| DTL-SLOT_TRANS_EPSILON | ε → C (initial consonant only)               |
| DTL-SLOT_TRANS_C       | C → CV (open syllable)                       |
| DTL-SLOT_TRANS_CV      | CV → CVV|CVC (branch)                        |
| DTL-SLOT_TRANS_CVV     | CVV → CVVC (close long syllable)             |
| DTL-SLOT_TRANS_CVC     | CVC → CVCC (word-final geminate)             |
| DTL-SLOT_TRANS_CVVC    | CVVC → CVVCC (super-heavy, word-final only)  |
| DTL-SLOT_TRANS_CVCC    | CVCC → terminal saturated                    |
| DTL-SLOT_TRANS_CVVCC   | CVVCC → terminal saturated                   |

## Enforcement
- get_license_version(unknown) → KeyError (fail-closed)
- All 8 compatible with ROOT_CLAIM

## Compatibility Violations: 0

## Tests
tests/sga/test_license_versioning.py — 17 tests, 17 passed
