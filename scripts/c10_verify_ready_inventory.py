#!/usr/bin/env python3
"""C10 ready-inventory verifier.

Verifies that reports/taaqol_full_integration/READY_ADAPTER_WIRING_INVENTORY.json
carries definitive classifications for every adapter — no adapter is
still marked READY_INTEGRATION but unwired.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INV = REPO / "reports" / "taaqol_full_integration" / "READY_ADAPTER_WIRING_INVENTORY.json"

ALLOWED_CLASSIFICATIONS = {
    "READY_RUNTIME",
    "READY_INTEGRATION",
    "CARRIER_ONLY",
    "LAW_ONLY",
    "MISSING_TYPED_PREDECESSOR",
    "MISSING_EVIDENCE",
    "NOT_APPLICABLE_TO_CORPUS",
    "REPORTING_ONLY",
    "NOT_IMPLEMENTED_IN_TARGET",
    "OWNER_SEMANTIC_DECISION_REQUIRED",
    "NATIVE_TAAQOL_LAW",
}


def main() -> int:
    if not INV.exists():
        print(json.dumps({"error": "READY_ADAPTER_WIRING_INVENTORY.json missing"}))
        return 2
    data = json.loads(INV.read_text())
    adapters = data.get("adapters", {})
    errors: list[str] = []
    unwired_ready_integration = 0
    unwired_ready_runtime = 0
    per: list[dict] = []
    for name, meta in adapters.items():
        cls = meta.get("classification")
        wired = meta.get("wired_by_orchestrator", False)
        if cls not in ALLOWED_CLASSIFICATIONS:
            errors.append(f"{name}: unknown classification {cls!r}")
        if cls == "READY_INTEGRATION" and not wired:
            unwired_ready_integration += 1
            errors.append(f"{name}: READY_INTEGRATION but not wired")
        if cls == "READY_RUNTIME" and not wired:
            unwired_ready_runtime += 1
            errors.append(f"{name}: READY_RUNTIME but not wired")
        per.append({"adapter": name, "classification": cls, "wired": wired})
    result = {
        "adapter_count": len(adapters),
        "READY_RUNTIME_UNWIRED_COUNT": unwired_ready_runtime,
        "READY_INTEGRATION_UNWIRED_COUNT": unwired_ready_integration,
        "errors": errors,
        "per": per,
        "summary": data.get("summary", {}),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
