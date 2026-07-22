"""
Tests for claim profile versioning contract.
HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01 — HARDEN-04
"""
import pytest
from pipeline.sga.contracts import (
    CLAIM_PROFILES, CLAIM_PROFILE_VERSIONS, CLAIM_PROFILE_SCHEMA_VERSION,
    RESERVED_CLAIM_PROFILES, ClaimProfileVersion, get_profile_version,
)


# ── Coverage ───────────────────────────────────────────────────────────────────

def test_all_profiles_have_version_entries():
    """Every entry in CLAIM_PROFILES must have a version record."""
    missing = [p for p in CLAIM_PROFILES if p not in CLAIM_PROFILE_VERSIONS]
    assert missing == [], f"Profiles missing version entries: {missing}"


def test_no_extra_version_entries():
    """CLAIM_PROFILE_VERSIONS must not contain profiles not in CLAIM_PROFILES."""
    extra = [p for p in CLAIM_PROFILE_VERSIONS if p not in CLAIM_PROFILES]
    assert extra == [], f"Extra version entries not in CLAIM_PROFILES: {extra}"


def test_profile_count():
    """Exactly 10 profiles (7 active + 3 reserved in CLAIM_PROFILES)."""
    assert len(CLAIM_PROFILES) == 10
    assert len(CLAIM_PROFILE_VERSIONS) == 10


# ── No collisions ──────────────────────────────────────────────────────────────

def test_no_profile_id_collisions():
    """No two profile version entries share the same profile_id."""
    seen: dict[str, str] = {}
    for profile_id, version in CLAIM_PROFILE_VERSIONS.items():
        assert version.profile_id == profile_id, \
            f"profile_id mismatch: key={profile_id!r}, value={version.profile_id!r}"
        assert profile_id not in seen, f"Duplicate profile_id: {profile_id!r}"
        seen[profile_id] = profile_id


# ── Reserved profiles ──────────────────────────────────────────────────────────

def test_reserved_profiles_have_reserved_status():
    """All reserved claim profiles must have status=RESERVED in version registry."""
    for pid in ("SYNTACTIC_RELATION_CLAIM", "SEMANTIC_RELATION_CLAIM", "EXISTENCE_CLAIM"):
        assert pid in CLAIM_PROFILE_VERSIONS, f"Reserved profile {pid!r} missing version entry"
        assert CLAIM_PROFILE_VERSIONS[pid].status == "RESERVED", \
            f"Reserved profile {pid!r} has non-RESERVED status"


def test_reserved_profiles_raise_on_get_profile_version():
    """get_profile_version() must raise RuntimeError for RESERVED profiles."""
    for pid in ("SYNTACTIC_RELATION_CLAIM", "SEMANTIC_RELATION_CLAIM", "EXISTENCE_CLAIM"):
        with pytest.raises(RuntimeError, match="RESERVED"):
            get_profile_version(pid)


def test_reserved_profiles_have_zero_bundle_versions():
    """Reserved profiles have no compatible bundle versions."""
    for pid in ("SYNTACTIC_RELATION_CLAIM", "SEMANTIC_RELATION_CLAIM", "EXISTENCE_CLAIM"):
        v = CLAIM_PROFILE_VERSIONS[pid]
        assert v.compatible_bundle_versions == frozenset(), \
            f"Reserved profile {pid!r} has non-empty compatible_bundle_versions"


# ── Active profiles ────────────────────────────────────────────────────────────

def test_active_profiles_return_on_get_profile_version():
    """get_profile_version() returns version for all active profiles."""
    for pid in ("ROOT_CLAIM", "PATTERN_CLAIM", "BAB_CLAIM", "MASDAR_CLAIM",
                "DERIVATIVE_CLAIM", "WORD_CLASS_CLAIM", "FUNCTIONAL_OWNER_CLAIM"):
        v = get_profile_version(pid)
        assert v.status == "ACTIVE"
        assert v.profile_id == pid


def test_active_profiles_have_compatible_bundle_versions():
    """All active profiles must declare at least one compatible bundle version."""
    for pid in ("ROOT_CLAIM", "PATTERN_CLAIM", "BAB_CLAIM", "MASDAR_CLAIM",
                "DERIVATIVE_CLAIM", "WORD_CLASS_CLAIM", "FUNCTIONAL_OWNER_CLAIM"):
        v = CLAIM_PROFILE_VERSIONS[pid]
        assert len(v.compatible_bundle_versions) >= 1, \
            f"Active profile {pid!r} has no compatible bundle versions"


def test_active_profiles_have_semver_schema_version():
    """Active profiles must have a valid schema_version (semver-like)."""
    for pid in ("ROOT_CLAIM", "PATTERN_CLAIM", "BAB_CLAIM", "MASDAR_CLAIM",
                "DERIVATIVE_CLAIM", "WORD_CLASS_CLAIM", "FUNCTIONAL_OWNER_CLAIM"):
        v = CLAIM_PROFILE_VERSIONS[pid]
        parts = v.schema_version.split(".")
        assert len(parts) == 3, \
            f"Profile {pid!r} has non-semver schema_version: {v.schema_version!r}"


# ── Unknown profile is fail-closed ────────────────────────────────────────────

def test_unknown_profile_raises_keyerror():
    """get_profile_version() must raise KeyError for unknown profiles."""
    with pytest.raises(KeyError):
        get_profile_version("NONEXISTENT_CLAIM")


def test_empty_profile_id_raises_keyerror():
    with pytest.raises(KeyError):
        get_profile_version("")


# ── Schema version constant ───────────────────────────────────────────────────

def test_claim_profile_schema_version_constant():
    assert CLAIM_PROFILE_SCHEMA_VERSION == "1.0.0"


# ── Status values ──────────────────────────────────────────────────────────────

def test_status_values_are_valid():
    valid_statuses = {"ACTIVE", "RESERVED", "DEPRECATED", "RETIRED"}
    for pid, v in CLAIM_PROFILE_VERSIONS.items():
        assert v.status in valid_statuses, \
            f"Profile {pid!r} has unknown status: {v.status!r}"


# ── No implicit activation ─────────────────────────────────────────────────────

def test_reserved_profiles_not_in_active_claim_profiles():
    """Reserved profiles in CLAIM_PROFILE_VERSIONS must have no required_slots."""
    from pipeline.sga.contracts import CLAIM_PROFILES
    for pid in ("SYNTACTIC_RELATION_CLAIM", "SEMANTIC_RELATION_CLAIM", "EXISTENCE_CLAIM"):
        profile = CLAIM_PROFILES[pid]
        assert len(profile.required_slots) == 0, \
            f"Reserved profile {pid!r} has required_slots — it would be activated implicitly"


def test_reserved_profiles_not_implicitly_activated():
    """Reserved profiles must have minimum_evidence_count=0."""
    from pipeline.sga.contracts import CLAIM_PROFILES
    for pid in ("SYNTACTIC_RELATION_CLAIM", "SEMANTIC_RELATION_CLAIM", "EXISTENCE_CLAIM"):
        profile = CLAIM_PROFILES[pid]
        assert profile.minimum_evidence_count == 0, \
            f"Reserved profile {pid!r} has minimum_evidence_count > 0"


# ── Frozen dataclass ──────────────────────────────────────────────────────────

def test_claim_profile_version_is_frozen():
    v = CLAIM_PROFILE_VERSIONS["ROOT_CLAIM"]
    with pytest.raises((AttributeError, TypeError)):
        v.status = "RETIRED"  # type: ignore[misc]
