#!/usr/bin/env python3
"""C10 requirement-document validator.

Validates that every file under requirements/ayat_al_dayn_integration/
matching the mandate §17 numbered names (01_..15_.json) carries the
standard envelope and a technical_validation_status field.

Exit 0 on success, nonzero on validation failure.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REQ_DIR = REPO / "requirements" / "ayat_al_dayn_integration"

REQUIRED_ENVELOPE_KEYS = {
    "schema_version",
    "generated_from_hokom_head",
    "target_taaqol_sha",
    "generated_at_utc",
    "source_files",
    "source_hashes",
    "status",
    "unresolved_items",
    "owner_decision_required",
    "validation_rules",
}

TECHNICAL_STATUSES = {"VALIDATED_CURRENT", "VALIDATED_BLOCKED", "INVALID"}
OWNER_STATUSES = {"NOT_REVIEWED", "APPROVED", "REJECTED"}
LEGACY_STATUSES = {"CURRENT", "STALE_REGENERATED", "NEWLY_CREATED", "BLOCKED", "INCONSISTENT"}

EXPECTED_FILES = [
    "01_VENDOR_CURRENT_MAIN_DELTA_MANIFEST.json",
    "02_CANONICAL_AYAT_AL_DAYN_CORPUS_MANIFEST.json",
    "03_STAGE_OWNERSHIP_MATRIX.json",
    "04_P2_REGISTRY_CONTRACT.json",
    "05_LICENSING_BOUNDARY_VERDICT_MAPPING_CONTRACT.json",
    "06_FULL_TYPED_ADAPTER_CASCADE_MATRIX.json",
    "07_DAL_LAFZI_WADI_PREREQUISITES.json",
    "08_FORMAL_SHAPE_REQUIREMENTS.json",
    "09_RELATION_MULTI_TOKEN_SCOPE_REQUIREMENTS.json",
    "10_MAQAM_CONTEXT_REQUIREMENTS.json",
    "11_PROVENANCE_VERSIONING_POLICY.json",
    "12_FAILURE_RESIDUAL_TAXONOMY.json",
    "13_TEST_FIRST_MATRIX.json",
    "14_STAGE_BY_STAGE_ACCEPTANCE_GATES.json",
    "15_IMPLEMENTATION_DEPENDENCY_GRAPH.json",
]


def validate() -> dict:
    errors: list[str] = []
    per_file: list[dict] = []
    tech_counts = {"VALIDATED_CURRENT": 0, "VALIDATED_BLOCKED": 0, "INVALID": 0}
    owner_counts = {"NOT_REVIEWED": 0, "APPROVED": 0, "REJECTED": 0}

    for name in EXPECTED_FILES:
        p = REQ_DIR / name
        entry = {"file": name, "exists": p.exists()}
        if not p.exists():
            entry["error"] = "MISSING_FILE"
            errors.append(f"{name}: missing")
            per_file.append(entry)
            continue
        try:
            doc = json.loads(p.read_text())
        except Exception as e:
            entry["error"] = f"JSON_PARSE_ERROR::{e}"
            errors.append(f"{name}: parse error {e}")
            per_file.append(entry)
            continue
        missing = REQUIRED_ENVELOPE_KEYS - set(doc.keys())
        if missing:
            entry["error"] = f"MISSING_ENVELOPE_KEYS::{sorted(missing)}"
            errors.append(f"{name}: missing envelope {sorted(missing)}")
        tech = doc.get("technical_validation_status")
        owner = doc.get("owner_review_status")
        if tech not in TECHNICAL_STATUSES:
            entry.setdefault("error", "MISSING_TECHNICAL_VALIDATION_STATUS")
            errors.append(f"{name}: technical_validation_status invalid ({tech!r})")
        else:
            tech_counts[tech] += 1
        if owner not in OWNER_STATUSES:
            entry.setdefault("error", "MISSING_OWNER_REVIEW_STATUS")
            errors.append(f"{name}: owner_review_status invalid ({owner!r})")
        else:
            owner_counts[owner] += 1
        legacy = doc.get("status")
        if legacy not in LEGACY_STATUSES:
            errors.append(f"{name}: legacy status invalid ({legacy!r})")
        entry["technical_validation_status"] = tech
        entry["owner_review_status"] = owner
        entry["legacy_status"] = legacy
        per_file.append(entry)

    return {
        "expected_file_count": len(EXPECTED_FILES),
        "found_file_count": sum(1 for e in per_file if e.get("exists")),
        "errors": errors,
        "per_file": per_file,
        "technical_status_counts": tech_counts,
        "owner_status_counts": owner_counts,
        "requirement_document_count": len(EXPECTED_FILES),
        "requirement_technically_invalid": tech_counts["INVALID"],
        "requirement_technically_unreviewed": len(EXPECTED_FILES) - sum(tech_counts.values()),
    }


def main() -> int:
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["errors"]:
        return 2
    if result["requirement_technically_invalid"] != 0:
        return 3
    if result["requirement_technically_unreviewed"] != 0:
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
