# HARDEN-01: Baseline Report
Stage: HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01
Date: 2026-07-22

## Environment
- Platform: Linux 6.8.0-124-generic aarch64
- Python: 3.10.12 (/usr/bin/python3)
- Virtual env: .venv (system Python)
- Repo HEAD at start: ef87e6ab1f9d75529b55e02b4093bea7d8938509 (ef87e6a)
- Branch: main
- Worktree: untracked files only (no staged/unstaged tracked changes)
- Vendor SHA: 35381739410071ac21dd96702ecbb2acb493f90d

## Starting Test Counts
- tests/sga/ : 98 passed, 0 failed
- tests/taaqol_bridge/ : 6 passed, 6 skipped
- Full suite: 12 failed (pre-existing Python 3.10 compat), 5512 passed, 55 skipped

## Pre-existing Failures (all Python 3.10 runtime)
All 12 are Python 3.11+ requirement failures:
- test_native_strenum.py (3)
- test_no_compatibility_injection.py (1)
- test_packaging_python_requires.py (2)
- test_python_runtime_imports.py (1)
- test_python_version_contract.py (2)
- test_taaqol_import_readiness.py (1)
- test_canonical_runtime_contract.py (2)

## Slot/Profile Inventory at Baseline
- SlotId count: 47
- SlotSort count: 18
- CLAIM_PROFILES: 10 (7 active + 3 reserved in dict)
- RESERVED_CLAIM_PROFILES set: 6
- DOMAIN_LICENSE count (SLOT_TRANS_LICENSES): 8
