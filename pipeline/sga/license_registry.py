"""
license_registry.py — Authoritative versioning registry for all 8 domain transition licenses.

The 8 SLOT_TRANS_LICENSES are defined in pipeline/p1_atomic_structure/slot_engineering.py
as DomainTransitionLicense instances. This registry adds versioning metadata, status,
and compatibility information to each license.

Single source of truth for license versioning.
HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01 — HARDEN-05
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet

DOMAIN_LICENSE_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class DomainLicenseVersion:
    license_id: str
    schema_version: str            # semver string
    status: str                    # ACTIVE | DEPRECATED | RETIRED
    licensed_transition: str       # human-readable description of the transition
    compatible_profiles: FrozenSet[str]
    compatible_bundle_versions: FrozenSet[str]
    added_in_stage: str


DOMAIN_LICENSE_VERSIONS: dict[str, DomainLicenseVersion] = {
    "DTL-SLOT_TRANS_EPSILON": DomainLicenseVersion(
        license_id="DTL-SLOT_TRANS_EPSILON",
        schema_version="1.0.0",
        status="ACTIVE",
        licensed_transition="PHONOLOGICAL_CELLS(ε) → C — empty slot boundary accepts initial consonant only",
        compatible_profiles=frozenset({
            "ROOT_CLAIM", "WORD_CLASS_CLAIM", "PATTERN_CLAIM",
            "BAB_CLAIM", "MASDAR_CLAIM", "DERIVATIVE_CLAIM", "FUNCTIONAL_OWNER_CLAIM",
        }),
        compatible_bundle_versions=frozenset({"1.0.0"}),
        added_in_stage="HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01",
    ),
    "DTL-SLOT_TRANS_C": DomainLicenseVersion(
        license_id="DTL-SLOT_TRANS_C",
        schema_version="1.0.0",
        status="ACTIVE",
        licensed_transition="PHONOLOGICAL_CELLS(C) → CV — single consonant extends to open syllable on vowel input",
        compatible_profiles=frozenset({
            "ROOT_CLAIM", "WORD_CLASS_CLAIM", "PATTERN_CLAIM",
            "BAB_CLAIM", "MASDAR_CLAIM", "DERIVATIVE_CLAIM", "FUNCTIONAL_OWNER_CLAIM",
        }),
        compatible_bundle_versions=frozenset({"1.0.0"}),
        added_in_stage="HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01",
    ),
    "DTL-SLOT_TRANS_CV": DomainLicenseVersion(
        license_id="DTL-SLOT_TRANS_CV",
        schema_version="1.0.0",
        status="ACTIVE",
        licensed_transition="PHONOLOGICAL_CELLS(CV) → CVV | CVC — open syllable branches to long vowel or closed syllable",
        compatible_profiles=frozenset({
            "ROOT_CLAIM", "WORD_CLASS_CLAIM", "PATTERN_CLAIM",
            "BAB_CLAIM", "MASDAR_CLAIM", "DERIVATIVE_CLAIM", "FUNCTIONAL_OWNER_CLAIM",
        }),
        compatible_bundle_versions=frozenset({"1.0.0"}),
        added_in_stage="HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01",
    ),
    "DTL-SLOT_TRANS_CVV": DomainLicenseVersion(
        license_id="DTL-SLOT_TRANS_CVV",
        schema_version="1.0.0",
        status="ACTIVE",
        licensed_transition="PHONOLOGICAL_CELLS(CVV) → CVVC — long open syllable closes with consonant; second vowel extension forbidden",
        compatible_profiles=frozenset({
            "ROOT_CLAIM", "WORD_CLASS_CLAIM", "PATTERN_CLAIM",
            "BAB_CLAIM", "MASDAR_CLAIM", "DERIVATIVE_CLAIM", "FUNCTIONAL_OWNER_CLAIM",
        }),
        compatible_bundle_versions=frozenset({"1.0.0"}),
        added_in_stage="HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01",
    ),
    "DTL-SLOT_TRANS_CVC": DomainLicenseVersion(
        license_id="DTL-SLOT_TRANS_CVC",
        schema_version="1.0.0",
        status="ACTIVE",
        licensed_transition="PHONOLOGICAL_CELLS(CVC) → CVCC — closed short syllable extends to geminate at word-final position only",
        compatible_profiles=frozenset({
            "ROOT_CLAIM", "WORD_CLASS_CLAIM", "PATTERN_CLAIM",
            "BAB_CLAIM", "MASDAR_CLAIM", "DERIVATIVE_CLAIM", "FUNCTIONAL_OWNER_CLAIM",
        }),
        compatible_bundle_versions=frozenset({"1.0.0"}),
        added_in_stage="HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01",
    ),
    "DTL-SLOT_TRANS_CVVC": DomainLicenseVersion(
        license_id="DTL-SLOT_TRANS_CVVC",
        schema_version="1.0.0",
        status="ACTIVE",
        licensed_transition="PHONOLOGICAL_CELLS(CVVC) → CVVCC — closed long syllable extends to super-heavy at word-final position only",
        compatible_profiles=frozenset({
            "ROOT_CLAIM", "WORD_CLASS_CLAIM", "PATTERN_CLAIM",
            "BAB_CLAIM", "MASDAR_CLAIM", "DERIVATIVE_CLAIM", "FUNCTIONAL_OWNER_CLAIM",
        }),
        compatible_bundle_versions=frozenset({"1.0.0"}),
        added_in_stage="HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01",
    ),
    "DTL-SLOT_TRANS_CVCC": DomainLicenseVersion(
        license_id="DTL-SLOT_TRANS_CVCC",
        schema_version="1.0.0",
        status="ACTIVE",
        licensed_transition="PHONOLOGICAL_CELLS(CVCC) — terminal saturated syllable; no further extension licensed",
        compatible_profiles=frozenset({
            "ROOT_CLAIM", "WORD_CLASS_CLAIM", "PATTERN_CLAIM",
            "BAB_CLAIM", "MASDAR_CLAIM", "DERIVATIVE_CLAIM", "FUNCTIONAL_OWNER_CLAIM",
        }),
        compatible_bundle_versions=frozenset({"1.0.0"}),
        added_in_stage="HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01",
    ),
    "DTL-SLOT_TRANS_CVVCC": DomainLicenseVersion(
        license_id="DTL-SLOT_TRANS_CVVCC",
        schema_version="1.0.0",
        status="ACTIVE",
        licensed_transition="PHONOLOGICAL_CELLS(CVVCC) — super-heavy terminal syllable; no further extension licensed",
        compatible_profiles=frozenset({
            "ROOT_CLAIM", "WORD_CLASS_CLAIM", "PATTERN_CLAIM",
            "BAB_CLAIM", "MASDAR_CLAIM", "DERIVATIVE_CLAIM", "FUNCTIONAL_OWNER_CLAIM",
        }),
        compatible_bundle_versions=frozenset({"1.0.0"}),
        added_in_stage="HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01",
    ),
}

# Canonical ordered set of license IDs (maps to SLOT_TRANS keys in slot_engineering.py)
DOMAIN_LICENSE_IDS: frozenset[str] = frozenset(DOMAIN_LICENSE_VERSIONS.keys())

# Expected count for enforcement tests
DOMAIN_LICENSE_EXPECTED_COUNT = 8


def get_license_version(license_id: str) -> DomainLicenseVersion:
    """
    Return the DomainLicenseVersion for the given license_id.
    Raises KeyError for unknown licenses (fail-closed).
    """
    if license_id not in DOMAIN_LICENSE_VERSIONS:
        raise KeyError(
            f"Unknown domain license: {license_id!r}. "
            "Fail-closed: unregistered licenses are forbidden."
        )
    return DOMAIN_LICENSE_VERSIONS[license_id]


def validate_license_registry() -> list[str]:
    """Return list of registry violations. Empty = clean."""
    violations: list[str] = []
    seen: dict[str, str] = {}

    for lid, lv in DOMAIN_LICENSE_VERSIONS.items():
        if lv.license_id != lid:
            violations.append(f"LICENSE_ID_MISMATCH: key={lid!r}, value={lv.license_id!r}")
        if lid in seen:
            violations.append(f"DUPLICATE_LICENSE_ID: {lid!r}")
        seen[lid] = lid

        valid_statuses = {"ACTIVE", "DEPRECATED", "RETIRED"}
        if lv.status not in valid_statuses:
            violations.append(f"UNKNOWN_STATUS: {lid!r} → {lv.status!r}")

    if len(DOMAIN_LICENSE_VERSIONS) != DOMAIN_LICENSE_EXPECTED_COUNT:
        violations.append(
            f"WRONG_LICENSE_COUNT: expected {DOMAIN_LICENSE_EXPECTED_COUNT}, "
            f"got {len(DOMAIN_LICENSE_VERSIONS)}"
        )

    return violations


__all__ = [
    "DOMAIN_LICENSE_SCHEMA_VERSION",
    "DOMAIN_LICENSE_EXPECTED_COUNT",
    "DOMAIN_LICENSE_IDS",
    "DOMAIN_LICENSE_VERSIONS",
    "DomainLicenseVersion",
    "get_license_version",
    "validate_license_registry",
]
