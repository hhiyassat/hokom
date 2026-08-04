#!/usr/bin/env python3
"""C12 native-vertical verifier.

Validates the shape and integrity of C12_VERTICAL_STAGE_RECORDS.json
plus adapter probe artifacts. Ensures no fabricated Ayat execution.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPORTS = REPO / "reports" / "taaqol_full_integration"
TARGET_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for name in [
        "C12_NATIVE_VERTICAL_CONTRACTS.json",
        "C12_HOKOM_EVIDENCE_PRODUCERS.json",
        "C12_AYAT_SOURCE_DERIVED_SPANS.json",
        "C12_RELATION_COMPATIBILITY.json",
        "C12_SENTENCE_MAQAM_EVIDENCE.json",
        "C12_VERTICAL_STAGE_RECORDS.json",
    ]:
        p = REPORTS / name
        if not p.exists():
            errors.append(f"missing {name}")
            continue
        doc = json.loads(p.read_text())
        if doc.get("target_taaqol_sha") != TARGET_SHA:
            errors.append(f"{name}: SHA mismatch")

    vsr = json.loads((REPORTS / "C12_VERTICAL_STAGE_RECORDS.json").read_text())
    live = vsr["totals"].get("LIVE_PROVIDER_CALL_COUNT", 0)
    net = vsr["totals"].get("NETWORK_PROVIDER_CALL_COUNT", 0)
    if live != 0:
        errors.append(f"LIVE_PROVIDER_CALL_COUNT = {live}")
    if net != 0:
        errors.append(f"NETWORK_PROVIDER_CALL_COUNT = {net}")

    # No vendor stage may report ayat_executed > 0 without RelationClosure also > 0
    rc = next((s for s in vsr["stages"] if s["stage"] == "RelationClosure (native)"), None)
    rc_ayat = rc["ayat_executed"] if rc else 0
    for s in vsr["stages"]:
        if s["layer"] == "TAAQOL_NATIVE" and s["ayat_executed"] > 0 and rc_ayat == 0:
            errors.append(f"{s['stage']}: reports ayat_executed>0 while RelationClosure did not")

    # Relation compatibility must not carry vendor verdict fields
    rel = json.loads((REPORTS / "C12_RELATION_COMPATIBILITY.json").read_text())
    if rel["totals"].get("RELATION_EXPECTED_VERDICT_FIELDS", 0) != 0:
        errors.append("RELATION_EXPECTED_VERDICT_FIELDS != 0")
    for rcc in rel.get("compatibility_carriers", []):
        hint = rcc.get("structural_relation_hint", "")
        for forbidden in ("PROVEN", "COMPOSED", "IFADAH_VERDICT", "CLOSED_VERDICT"):
            if forbidden in hint:
                errors.append(f"structural_relation_hint contains vendor verdict term: {hint}")

    result = {
        "errors": errors,
        "warnings": warnings,
        "totals": vsr["totals"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 3


if __name__ == "__main__":
    sys.exit(main())
