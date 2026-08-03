from __future__ import annotations
from .ledger import ExecutionLedger
from .hokom_stage_registry import validate_registry, EXPECTED_HOKOM_STAGE_COUNT
from .taaqol_stage_registry import audit as taaqol_audit, TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH

def registry_status_report() -> dict:
    hokom_errors = validate_registry()
    taaqol_info = taaqol_audit()
    return {
        "HOKOM_STAGE_REGISTRY_VALID": 1 if not hokom_errors else 0,
        "HOKOM_STAGE_COUNT_19": 1 if not hokom_errors else 0,
        "HOKOM_ERRORS": hokom_errors,
        "TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH": 1 if TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH else 0,
        "TAAQOL_EXPECTED": taaqol_info["expected_count"],
        "TAAQOL_PROVEN": taaqol_info["proven_core_count"],
        "TAAQOL_BLOCKER": "ACTIVE — TAAQOL_49_STAGE_CLOSURE cannot be CLOSED",
        "TAAQOL_NOTE_49": taaqol_info["note_49"],
        "TAAQOL_CONSTITUTIONAL_SOURCE": taaqol_info["constitutional_source"],
    }
