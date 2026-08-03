#!/usr/bin/env python3
"""C11 evidence-graph validator.

Verifies that Hokom evidence artifacts are shape-valid, provenance-continuous,
and free of anti-invention violations.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPORTS = REPO / "reports" / "taaqol_full_integration"
TARGET_SHA = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

REQUIRED_ARTIFACTS = [
    "HOKOM_EVIDENCE_PRODUCTION_INVENTORY.json",
    "HOKOM_LEXICAL_EVIDENCE_CLOSURE.json",
    "AYAT_CLAUSE_EVIDENCE.json",
    "AYAT_SOURCE_DERIVED_SPANS.json",
    "AYAT_EVIDENCE_PRODUCTION_MANIFEST.json",
    "LCX_150_EVIDENCE_PRODUCTION.json",
]


def main() -> int:
    errors: list[str] = []
    per_artifact: list[dict] = []
    for name in REQUIRED_ARTIFACTS:
        p = REPORTS / name
        entry = {"artifact": name, "exists": p.exists()}
        if not p.exists():
            entry["error"] = "MISSING"
            errors.append(f"{name}: missing")
            per_artifact.append(entry)
            continue
        doc = json.loads(p.read_text())
        entry["target_taaqol_sha"] = doc.get("target_taaqol_sha")
        if entry["target_taaqol_sha"] != TARGET_SHA:
            errors.append(f"{name}: SHA mismatch {entry['target_taaqol_sha']} != {TARGET_SHA}")
        per_artifact.append(entry)

    # Cross-artifact invariants
    inv = json.loads((REPORTS / "HOKOM_EVIDENCE_PRODUCTION_INVENTORY.json").read_text())
    lex = json.loads((REPORTS / "HOKOM_LEXICAL_EVIDENCE_CLOSURE.json").read_text())
    clauses = json.loads((REPORTS / "AYAT_CLAUSE_EVIDENCE.json").read_text())
    spans = json.loads((REPORTS / "AYAT_SOURCE_DERIVED_SPANS.json").read_text())
    manifest = json.loads((REPORTS / "AYAT_EVIDENCE_PRODUCTION_MANIFEST.json").read_text())
    lcx = json.loads((REPORTS / "LCX_150_EVIDENCE_PRODUCTION.json").read_text())

    checks = {
        "inv.READY_EVIDENCE_PRODUCER_UNWIRED_is_zero":
            inv["totals"]["READY_EVIDENCE_PRODUCER_UNWIRED"] == 0,
        "inv.EVIDENCE_REQUIREMENT_UNREVIEWED_is_zero":
            inv["totals"]["EVIDENCE_REQUIREMENT_UNREVIEWED"] == 0,
        "lex.AYAT_ACCOUNTED_129": lex["totals"]["AYAT_ACCOUNTED"] == 129,
        "lex.AYAT_UNCLASSIFIED_0": lex["totals"]["AYAT_UNCLASSIFIED"] == 0,
        "lex.LEXICAL_RUNTIME_DEFECTS_0": lex["totals"]["LEXICAL_RUNTIME_DEFECTS"] == 0,
        "lex.UNRESOLVED_WITHOUT_REASON_0": lex["totals"]["UNRESOLVED_WITHOUT_REASON"] == 0,
        "clauses.no_missing_boundary_evidence":
            clauses["totals"]["CLAUSE_WITHOUT_BOUNDARY_EVIDENCE"] == 0,
        "clauses.no_missing_provenance": clauses["totals"]["CLAUSE_WITHOUT_PROVENANCE"] == 0,
        "clauses.no_missing_trace": clauses["totals"]["CLAUSE_WITHOUT_TRACE"] == 0,
        "clauses.no_meaning_derived": clauses["totals"]["CLAUSE_DIRECTLY_FROM_TOKEN_MEANING"] == 0,
        "clauses.deterministic": clauses["totals"]["DETERMINISTIC_ACROSS_RUNS"] is True,
        "spans.no_arbitrary_adjacency": spans["totals"]["ARBITRARY_ADJACENCY_SPAN_COUNT"] == 0,
        "spans.no_missing_provenance": spans["totals"]["SPAN_WITHOUT_PROVENANCE"] == 0,
        "manifest.no_duplicate_scope_ids": manifest["totals"]["DUPLICATE_SCOPE_IDS"] == 0,
        "manifest.no_unresolved_scope_refs": manifest["totals"]["UNRESOLVED_SCOPE_REFERENCES"] == 0,
        "manifest.no_evidence_without_source": manifest["totals"]["EVIDENCE_WITHOUT_SOURCE"] == 0,
        "lcx.LCX_TOTAL_150": lcx["totals"]["LCX_TOTAL"] == 150,
        "lcx.LCX_UNCLASSIFIED_0": lcx["totals"]["LCX_UNCLASSIFIED"] == 0,
        "lcx.LCX_RUNTIME_DEFECTS_0": lcx["totals"]["LCX_RUNTIME_DEFECTS"] == 0,
    }
    for k, ok in checks.items():
        if not ok:
            errors.append(f"invariant failed: {k}")

    result = {
        "per_artifact": per_artifact,
        "invariants": {k: bool(v) for k, v in checks.items()},
        "errors": errors,
        "totals": {
            "artifacts_present": sum(1 for a in per_artifact if a.get("exists")),
            "invariants_passed": sum(1 for v in checks.values() if v),
            "invariants_total": len(checks),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 3


if __name__ == "__main__":
    sys.exit(main())
