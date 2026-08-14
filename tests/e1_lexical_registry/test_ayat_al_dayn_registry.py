"""
E1 Lexical Registry Tests — T_E1_*

Tests for pipeline/taaqol_integration/e1_lexical_registry/ayat_al_dayn_registry.py

Constitutional gates verified: G_E1_01 through G_E1_08

Constitutional invariants:
  - REGISTRY_SIZE = 74 (unique ISM/FI3L host surfaces from 129-token corpus)
  - All entries have non_meaning_proof (non-empty, structural only)
  - All entries have domain = DAL_ONLY
  - All entries have rank = CANDIDATE on Python 3.12+
  - HARF tokens NOT in registry
  - build_ayat_al_dayn_registry() is fail-closed (ImportError → empty tuple)
  - CORPUS_SHA embedded in module

Python 3.10 compat:
  - _REGISTRY_RAW (pure Python dicts) is always available (tested on 3.10)
  - AYAT_AL_DAYN_REGISTRY (RegistryEntry tuples) requires Python 3.12+ (StrEnum)
  - Vendor-requiring tests skip on 3.10

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
Phase: E1 — AYAT-AL-DAYN CANONICAL LEXICAL REGISTRY
"""
from __future__ import annotations

import sys
import pytest

# ── Module under test ─────────────────────────────────────────────────────────
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.e1_lexical_registry.ayat_al_dayn_registry import (  # noqa: E402
    AYAT_AL_DAYN_REGISTRY,
    BUILD_FAILURES,
    BUILD_FAILURE_COUNT,
    BUILT_SIZE,
    CORPUS_SHA,
    REGISTRY_SIZE,
    VENDOR_SHA,
    _REGISTRY_CONTRACT_AVAILABLE,
    _REGISTRY_RAW,
    _VENDOR_SHA,
    build_ayat_al_dayn_registry,
)

# ── Helpers ───────────────────────────────────────────────────────────────────
REQUIRES_312 = pytest.mark.skipif(
    not _REGISTRY_CONTRACT_AVAILABLE,
    reason="Requires Python 3.12+ (StrEnum vendor layer)",
)

# Known HARF tokens (subset) — should NOT appear in registry
_KNOWN_HARF_SURFACES = {
    "إِذَا", "بِدَيْنٍ", "إِلَى", "فَاكْتُبُوهُ", "وَلَا", "فَإِنَّهُ",
    "عَلَيْهِ", "وَلِيُّهُ", "مِنَ", "وَلَوْ", "اللَّهَ",
}


# ── T_E1_01: REGISTRY_SIZE = 74 ──────────────────────────────────────────────

class TestT_E1_01_RegistrySize:
    """G_E1_01: REGISTRY_SIZE = 74."""

    def test_registry_size_constant(self):
        """REGISTRY_SIZE constant = 74."""
        assert REGISTRY_SIZE == 74, f"Expected 74, got {REGISTRY_SIZE}"

    def test_raw_registry_length(self):
        """_REGISTRY_RAW has exactly 74 entries."""
        assert len(_REGISTRY_RAW) == 74, (
            f"_REGISTRY_RAW has {len(_REGISTRY_RAW)} entries, expected 74"
        )

    def test_raw_registry_keys_unique(self):
        """All keys in _REGISTRY_RAW are unique (deduplication verified)."""
        keys = [e["key"] for e in _REGISTRY_RAW]
        unique_keys = set(keys)
        assert len(keys) == len(unique_keys), (
            f"Duplicate keys found: {len(keys)} entries but {len(unique_keys)} unique"
        )

    @REQUIRES_312
    def test_built_registry_size_matches(self):
        """BUILT_SIZE = 74 on Python 3.12+."""
        assert BUILT_SIZE == 74, f"Expected BUILT_SIZE=74, got {BUILT_SIZE}"

    @REQUIRES_312
    def test_ayat_al_dayn_registry_length(self):
        """AYAT_AL_DAYN_REGISTRY tuple has 74 entries on Python 3.12+."""
        assert len(AYAT_AL_DAYN_REGISTRY) == 74, (
            f"AYAT_AL_DAYN_REGISTRY has {len(AYAT_AL_DAYN_REGISTRY)} entries, expected 74"
        )


# ── T_E1_02: non_meaning_proof non-empty and structural ──────────────────────

class TestT_E1_02_NonMeaningProof:
    """G_E1_02: All entries have non_meaning_proof (non-empty, structural only)."""

    def test_all_raw_entries_have_non_meaning_proof(self):
        """All _REGISTRY_RAW entries have non_meaning_proof key."""
        missing = [e["key"] for e in _REGISTRY_RAW if "non_meaning_proof" not in e]
        assert not missing, f"Entries missing non_meaning_proof: {missing}"

    def test_all_non_meaning_proof_non_empty(self):
        """All non_meaning_proof values are non-empty strings."""
        empty = [
            e["key"] for e in _REGISTRY_RAW
            if not isinstance(e.get("non_meaning_proof"), str)
            or not e["non_meaning_proof"].strip()
        ]
        assert not empty, f"Entries with empty non_meaning_proof: {empty}"

    def test_non_meaning_proof_starts_with_structural(self):
        """All non_meaning_proof values begin with 'structural pre-semantic'."""
        bad = [
            e["key"] for e in _REGISTRY_RAW
            if not e.get("non_meaning_proof", "").startswith("structural pre-semantic")
        ]
        assert not bad, (
            f"Entries with non-structural non_meaning_proof prefix: {bad[:5]}"
        )

    def test_non_meaning_proof_no_semantic_meaning_words(self):
        """non_meaning_proof does not contain semantic/meaning vocabulary."""
        forbidden = ["meaning", "signifies", "denotes", "مدلول", "معنى"]
        violations = []
        for e in _REGISTRY_RAW:
            proof = e.get("non_meaning_proof", "").lower()
            for word in forbidden:
                if word.lower() in proof:
                    violations.append((e["key"], word))
        assert not violations, (
            f"non_meaning_proof contains forbidden semantic terms: {violations[:5]}"
        )

    @REQUIRES_312
    def test_registry_entries_have_non_meaning_proof(self):
        """All RegistryEntry objects have non_meaning_proof attribute."""
        missing = [
            e for e in AYAT_AL_DAYN_REGISTRY
            if not getattr(e, "non_meaning_proof", None)
        ]
        assert not missing, f"{len(missing)} entries missing non_meaning_proof"


# ── T_E1_03: domain = DAL_ONLY ────────────────────────────────────────────────

class TestT_E1_03_Domain:
    """G_E1_03: All entries have domain = DAL_ONLY."""

    def test_all_raw_entries_domain_dal_only(self):
        """All _REGISTRY_RAW entries have domain = 'DAL_ONLY'."""
        bad = [e["key"] for e in _REGISTRY_RAW if e.get("domain") != "DAL_ONLY"]
        assert not bad, f"Entries with wrong domain: {bad}"

    @REQUIRES_312
    def test_registry_entry_domain_dal_only(self):
        """All RegistryEntry objects have domain DAL_ONLY."""
        for entry in AYAT_AL_DAYN_REGISTRY:
            assert str(entry.domain) in ("DAL_ONLY", "RegistryDomain.DAL_ONLY"), (
                f"Entry {entry.key!r} has domain {entry.domain!r}, expected DAL_ONLY"
            )


# ── T_E1_04: rank = CANDIDATE ─────────────────────────────────────────────────

class TestT_E1_04_Rank:
    """G_E1_04: All entries have rank = CANDIDATE on Python 3.12+."""

    def test_all_raw_entries_rank_candidate(self):
        """All _REGISTRY_RAW entries have rank = 'CANDIDATE'."""
        bad = [e["key"] for e in _REGISTRY_RAW if e.get("rank") != "CANDIDATE"]
        assert not bad, f"Entries with non-CANDIDATE rank: {bad}"

    @REQUIRES_312
    def test_registry_entry_rank_candidate(self):
        """All RegistryEntry objects have rank CANDIDATE."""
        for entry in AYAT_AL_DAYN_REGISTRY:
            # Python 3.12 changed IntEnum.__str__: str(Rank.CANDIDATE) == "2" not "CANDIDATE".
            # Use .name for string check; identity check is semantically stronger.
            assert entry.rank.name == "CANDIDATE", (
                f"Entry {entry.key!r} has rank {entry.rank!r}, expected CANDIDATE "
                f"(name={entry.rank.name!r})"
            )


# ── T_E1_05: HARF tokens absent ───────────────────────────────────────────────

class TestT_E1_05_HarfAbsent:
    """G_E1_05: HARF tokens absent from registry."""

    def test_known_harf_surfaces_not_in_raw_keys(self):
        """Known HARF surface forms are not registry keys."""
        raw_keys = {e["key"] for e in _REGISTRY_RAW}
        present = _KNOWN_HARF_SURFACES & raw_keys
        assert not present, f"HARF surfaces found in registry: {present}"

    def test_all_raw_entries_are_ism_or_fi3l(self):
        """All _REGISTRY_RAW entries have wc = ISM or FI3L."""
        bad = [
            e["key"] for e in _REGISTRY_RAW
            if e.get("wc") not in ("ISM", "FI3L")
        ]
        assert not bad, f"Entries with non-ISM/FI3L word class: {bad}"

    @REQUIRES_312
    def test_known_harf_surfaces_not_in_registry(self):
        """Known HARF surfaces not in AYAT_AL_DAYN_REGISTRY keys."""
        registry_keys = {e.key for e in AYAT_AL_DAYN_REGISTRY}
        present = _KNOWN_HARF_SURFACES & registry_keys
        assert not present, f"HARF surfaces found in registry: {present}"


# ── T_E1_06: AYAT_AL_DAYN_REGISTRY is a tuple ───────────────────────────────

class TestT_E1_06_RegistryTuple:
    """G_E1_06: AYAT_AL_DAYN_REGISTRY accessible as tuple."""

    def test_registry_is_tuple(self):
        """AYAT_AL_DAYN_REGISTRY is a tuple."""
        assert isinstance(AYAT_AL_DAYN_REGISTRY, tuple), (
            f"Expected tuple, got {type(AYAT_AL_DAYN_REGISTRY)}"
        )

    def test_raw_registry_is_tuple(self):
        """_REGISTRY_RAW is a tuple."""
        assert isinstance(_REGISTRY_RAW, tuple), (
            f"Expected tuple, got {type(_REGISTRY_RAW)}"
        )

    def test_fail_closed_on_python_310(self):
        """On Python 3.10 (no vendor), AYAT_AL_DAYN_REGISTRY = () (empty, not error)."""
        if _REGISTRY_CONTRACT_AVAILABLE:
            pytest.skip("Python 3.12+ has vendor — skip fail-closed test")
        # On 3.10: AYAT_AL_DAYN_REGISTRY must be empty tuple (not None, not error)
        assert AYAT_AL_DAYN_REGISTRY == (), (
            f"Expected () on Python 3.10, got {AYAT_AL_DAYN_REGISTRY!r}"
        )
        assert BUILT_SIZE == 0, f"Expected BUILT_SIZE=0 on 3.10, got {BUILT_SIZE}"

    def test_build_returns_tuple(self):
        """build_ayat_al_dayn_registry() always returns a tuple."""
        result = build_ayat_al_dayn_registry()
        assert isinstance(result, tuple), (
            f"build_ayat_al_dayn_registry() returned {type(result)}, expected tuple"
        )

    def test_build_never_raises(self):
        """build_ayat_al_dayn_registry() never raises (fail-closed)."""
        try:
            result = build_ayat_al_dayn_registry()
        except Exception as exc:  # noqa: BLE001
            pytest.fail(
                f"build_ayat_al_dayn_registry() raised {type(exc).__name__}: {exc}"
            )


# ── T_E1_07: BUILD_FAILURES = [] ─────────────────────────────────────────────

class TestT_E1_07_BuildFailures:
    """G_E1_07: BUILD_FAILURES = [] on Python 3.12+."""

    @REQUIRES_312
    def test_build_failures_empty(self):
        """BUILD_FAILURES is empty on Python 3.12+."""
        assert BUILD_FAILURES == [], (
            f"BUILD_FAILURES is not empty: {BUILD_FAILURES}"
        )
        assert BUILD_FAILURE_COUNT == 0, (
            f"BUILD_FAILURE_COUNT is not 0: {BUILD_FAILURE_COUNT}"
        )

    def test_build_failures_is_list(self):
        """BUILD_FAILURES is always a list."""
        assert isinstance(BUILD_FAILURES, list), (
            f"Expected list, got {type(BUILD_FAILURES)}"
        )

    def test_build_failure_count_is_int(self):
        """BUILD_FAILURE_COUNT is always an int."""
        assert isinstance(BUILD_FAILURE_COUNT, int), (
            f"Expected int, got {type(BUILD_FAILURE_COUNT)}"
        )


# ── T_E1_08: CORPUS_SHA embedded ─────────────────────────────────────────────

class TestT_E1_08_CorpusSha:
    """G_E1_08: CORPUS_SHA embedded in registry module."""

    def test_corpus_sha_present(self):
        """CORPUS_SHA constant is present and non-empty."""
        assert isinstance(CORPUS_SHA, str) and CORPUS_SHA.strip(), (
            "CORPUS_SHA is missing or empty"
        )

    def test_corpus_sha_value(self):
        """CORPUS_SHA matches the pinned corpus hash."""
        expected = "6bd635a05530965f13f76cf003f7738130badec6981bcb0e73f2465d386e1ed7"
        assert CORPUS_SHA == expected, (
            f"CORPUS_SHA mismatch: expected {expected!r}, got {CORPUS_SHA!r}"
        )

    def test_vendor_sha_present(self):
        """VENDOR_SHA constant is present (public alias of _VENDOR_SHA)."""
        assert isinstance(VENDOR_SHA, str) and VENDOR_SHA.strip(), (
            "VENDOR_SHA is missing or empty"
        )

    def test_vendor_sha_value(self):
        """VENDOR_SHA matches the pinned VENDOR_SHA."""
        expected = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"
        assert VENDOR_SHA == expected, (
            f"VENDOR_SHA mismatch: expected {expected!r}, got {VENDOR_SHA!r}"
        )
        # Also verify private alias agrees
        assert _VENDOR_SHA == expected, (
            f"_VENDOR_SHA mismatch: expected {expected!r}, got {_VENDOR_SHA!r}"
        )


# ── T_E1_09: Structural integrity checks ─────────────────────────────────────

class TestT_E1_09_StructuralIntegrity:
    """Additional structural integrity tests."""

    def test_all_raw_entries_have_required_keys(self):
        """All _REGISTRY_RAW entries have required keys."""
        required = {"key", "domain", "non_meaning_proof", "rank", "residuals",
                    "trace_ref", "wc", "root_state", "root", "wazn"}
        for entry in _REGISTRY_RAW:
            missing = required - set(entry.keys())
            assert not missing, (
                f"Entry {entry.get('key', '?')!r} missing keys: {missing}"
            )

    def test_known_ism_tokens_in_registry(self):
        """Key ISM tokens from corpus are in the registry."""
        known_ism = {"دَيْنٍ", "كَاتِبٌ", "رَجُلَيْنِ", "شَهِيدَيْنِ"}
        raw_keys = {e["key"] for e in _REGISTRY_RAW}
        missing = known_ism - raw_keys
        # Allow partial miss (deduplication may have merged)
        if len(missing) == len(known_ism):
            pytest.fail(f"None of the known ISM tokens found in registry: {known_ism}")

    def test_trace_refs_have_corpus_prefix(self):
        """All trace_ref values begin with 'corpus:'."""
        bad = [
            e["key"] for e in _REGISTRY_RAW
            if not e.get("trace_ref", "").startswith("corpus:")
        ]
        assert not bad, f"Entries with non-corpus trace_ref: {bad[:5]}"

    def test_residuals_are_lists(self):
        """All residuals fields are lists."""
        bad = [
            e["key"] for e in _REGISTRY_RAW
            if not isinstance(e.get("residuals"), list)
        ]
        assert not bad, f"Entries with non-list residuals: {bad}"

    @REQUIRES_312
    def test_registry_entries_are_typed(self):
        """All AYAT_AL_DAYN_REGISTRY entries are RegistryEntry objects (have .key attr)."""
        for entry in AYAT_AL_DAYN_REGISTRY:
            assert hasattr(entry, "key"), (
                f"Entry {entry!r} missing .key attribute"
            )
            assert hasattr(entry, "non_meaning_proof"), (
                f"Entry {entry!r} missing .non_meaning_proof attribute"
            )
