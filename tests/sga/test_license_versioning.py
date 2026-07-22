"""
Tests for domain license versioning registry.
HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01 — HARDEN-05
"""
import pytest
from pipeline.sga.license_registry import (
    DOMAIN_LICENSE_VERSIONS, DOMAIN_LICENSE_SCHEMA_VERSION,
    DOMAIN_LICENSE_EXPECTED_COUNT, DOMAIN_LICENSE_IDS,
    DomainLicenseVersion, get_license_version, validate_license_registry,
)


EXPECTED_LICENSE_IDS = {
    "DTL-SLOT_TRANS_EPSILON",
    "DTL-SLOT_TRANS_C",
    "DTL-SLOT_TRANS_CV",
    "DTL-SLOT_TRANS_CVV",
    "DTL-SLOT_TRANS_CVC",
    "DTL-SLOT_TRANS_CVVC",
    "DTL-SLOT_TRANS_CVCC",
    "DTL-SLOT_TRANS_CVVCC",
}


# ── Coverage ───────────────────────────────────────────────────────────────────

def test_license_count():
    """Exactly 8 domain licenses."""
    assert len(DOMAIN_LICENSE_VERSIONS) == 8
    assert len(DOMAIN_LICENSE_VERSIONS) == DOMAIN_LICENSE_EXPECTED_COUNT


def test_all_expected_licenses_present():
    """All 8 expected DTL-SLOT_TRANS licenses must be in the registry."""
    missing = EXPECTED_LICENSE_IDS - set(DOMAIN_LICENSE_VERSIONS.keys())
    assert missing == set(), f"Missing license entries: {missing}"


def test_no_extra_licenses():
    """Registry must not contain unknown license IDs."""
    extra = set(DOMAIN_LICENSE_VERSIONS.keys()) - EXPECTED_LICENSE_IDS
    assert extra == set(), f"Extra license entries: {extra}"


def test_domain_license_ids_frozenset():
    """DOMAIN_LICENSE_IDS frozenset matches DOMAIN_LICENSE_VERSIONS keys."""
    assert DOMAIN_LICENSE_IDS == set(DOMAIN_LICENSE_VERSIONS.keys())


# ── No collisions ──────────────────────────────────────────────────────────────

def test_no_license_id_collisions():
    """No two license version entries share the same license_id."""
    seen: dict[str, str] = {}
    for lid, lv in DOMAIN_LICENSE_VERSIONS.items():
        assert lv.license_id == lid, \
            f"license_id mismatch: key={lid!r}, value={lv.license_id!r}"
        assert lid not in seen, f"Duplicate license_id: {lid!r}"
        seen[lid] = lid


# ── Status values ──────────────────────────────────────────────────────────────

def test_status_values_are_valid():
    valid = {"ACTIVE", "DEPRECATED", "RETIRED"}
    for lid, lv in DOMAIN_LICENSE_VERSIONS.items():
        assert lv.status in valid, \
            f"License {lid!r} has unknown status: {lv.status!r}"


def test_all_licenses_are_active():
    """All 8 SLOT_TRANS licenses are currently active."""
    for lid, lv in DOMAIN_LICENSE_VERSIONS.items():
        assert lv.status == "ACTIVE", \
            f"License {lid!r} is not ACTIVE (status={lv.status!r})"


# ── get_license_version ────────────────────────────────────────────────────────

def test_get_license_version_returns_correct_entry():
    for lid in EXPECTED_LICENSE_IDS:
        lv = get_license_version(lid)
        assert lv.license_id == lid
        assert lv.status == "ACTIVE"


def test_unknown_license_raises_keyerror():
    """get_license_version() must raise KeyError for unknown licenses."""
    with pytest.raises(KeyError):
        get_license_version("DTL-UNKNOWN_LICENSE")


def test_empty_license_id_raises_keyerror():
    with pytest.raises(KeyError):
        get_license_version("")


# ── validate_license_registry ─────────────────────────────────────────────────

def test_validate_license_registry_clean():
    violations = validate_license_registry()
    assert violations == [], f"License registry violations: {violations}"


# ── Compatible profiles ────────────────────────────────────────────────────────

def test_all_licenses_compatible_with_root_claim():
    """All 8 licenses are compatible with ROOT_CLAIM (phonological layer is universal)."""
    for lid, lv in DOMAIN_LICENSE_VERSIONS.items():
        assert "ROOT_CLAIM" in lv.compatible_profiles, \
            f"License {lid!r} not compatible with ROOT_CLAIM"


def test_all_licenses_have_bundle_versions():
    """All licenses must declare at least one compatible bundle version."""
    for lid, lv in DOMAIN_LICENSE_VERSIONS.items():
        assert len(lv.compatible_bundle_versions) >= 1, \
            f"License {lid!r} has no compatible bundle versions"


# ── Slot engineering consistency ──────────────────────────────────────────────

def test_slot_engineering_license_ids_match_registry():
    """The SLOT_TRANS_LICENSES keys in slot_engineering.py must map to registry IDs."""
    try:
        from pipeline.p1_atomic_structure.slot_engineering import SLOT_TRANS_LICENSES
        if not SLOT_TRANS_LICENSES:
            return  # SGA contracts unavailable on this Python version
        for key, dtl in SLOT_TRANS_LICENSES.items():
            # The license_id in each DTL must be in our registry
            assert dtl.license_id in DOMAIN_LICENSE_VERSIONS, \
                f"slot_engineering DTL license_id {dtl.license_id!r} (key={key!r}) not in registry"
    except ImportError:
        pass  # slot_engineering may be unavailable


def test_slot_engineering_license_count_matches_registry():
    """SLOT_TRANS_LICENSES in slot_engineering.py should have exactly 8 entries."""
    try:
        from pipeline.p1_atomic_structure.slot_engineering import SLOT_TRANS_LICENSES
        if not SLOT_TRANS_LICENSES:
            return
        assert len(SLOT_TRANS_LICENSES) == DOMAIN_LICENSE_EXPECTED_COUNT, \
            f"slot_engineering has {len(SLOT_TRANS_LICENSES)} licenses, expected {DOMAIN_LICENSE_EXPECTED_COUNT}"
    except ImportError:
        pass


# ── Schema version constant ────────────────────────────────────────────────────

def test_domain_license_schema_version():
    assert DOMAIN_LICENSE_SCHEMA_VERSION == "1.0.0"


# ── Frozen dataclass ──────────────────────────────────────────────────────────

def test_domain_license_version_is_frozen():
    lv = DOMAIN_LICENSE_VERSIONS["DTL-SLOT_TRANS_EPSILON"]
    with pytest.raises((AttributeError, TypeError)):
        lv.status = "RETIRED"  # type: ignore[misc]
