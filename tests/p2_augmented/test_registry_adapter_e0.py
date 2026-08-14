"""
tests/p2_augmented/test_registry_adapter_e0.py

E0 acceptance tests for A0_REGISTRY_LOOKUP adapter.

Tests:
    T03_P2_BLOCKER_DEACTIVATED — registry_matches non-None deactivates blocker
    T24_FAIL_CLOSED — import failure → registry_matches=[] (non-None), never None
    T26_NON_MEANING_PROOF — RegistryEntry with empty non_meaning_proof raises error
    T27_RANK_CEILING — RegistryEntry with rank > ceiling raises error
    T00_REGISTRY_SCHEMA — RegistryEntry schema invariants (Python 3.12+ only)

Constitutional references:
    - 05_P2_REGISTRY_CONTRACT.md: blocker root cause + fix
    - 10_FAILURE_AND_RESIDUAL_TAXONOMY.md: FAIL-CLOSED contract
    - 11_PROVENANCE_AND_VERSIONING_POLICY.md: VENDOR_SHA invariant
    - 13_STAGE_ACCEPTANCE_GATES.md: G_E0_01, G_E0_02

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
"""
from __future__ import annotations

import sys
import pytest
from pathlib import Path

# Ensure Hokom src on path
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"))


# ── Import adapter ───────────────────────────────────────────────────────────
from pipeline.taaqol_integration.weight_layer.registry_adapter import (
    build_registry_evidence,
    build_registry_evidence_for_stage_input,
    AYAT_AL_DAYN_REGISTRY,
    _E1_REGISTRY_RAW,
    _E1_REGISTRY_SIZE,
    _HOKOM_E1_REGISTRY_AVAILABLE,
    _REGISTRY_CONTRACT_AVAILABLE,
    _E2_REGISTRY_IMPORT_OK,
    _VENDOR_SHA,
)

PINNED_VENDOR_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

# Vendor import available only on Python 3.12+
_PY312_PLUS = sys.version_info >= (3, 12)
_VENDOR_SKIP = pytest.mark.skipif(
    not _REGISTRY_CONTRACT_AVAILABLE,
    reason="taaqqul_slot_geometry requires Python 3.12+ (StrEnum)"
)


# ─────────────────────────────────────────────────────────────────────────────
# T24 — FAIL-CLOSED: import failure → registry_matches non-None, never None
# ─────────────────────────────────────────────────────────────────────────────

class TestT24FailClosed:
    """T24_FAIL_CLOSED — on any import/runtime failure, registry_matches is non-None."""

    @pytest.mark.parametrize("surface,word_class", [
        ("تَدَايَنْتُمْ", "FI3L"),
        ("بِدَيْنٍ",      "ISM"),
        ("إِلَى",         "HARF"),
        ("كَاتِبٌ",       "ISM"),
        ("",              "ISM"),
        ("يَا",           "HARF"),
        ("آمَنُوا",       "FI3L"),
    ])
    def test_registry_matches_never_none(self, surface, word_class):
        """INV-1: registry_matches is never None regardless of vendor availability."""
        ev = build_registry_evidence(surface, word_class, registry=(), trace_ref="test")
        assert ev["registry_matches"] is not None, (
            f"registry_matches is None for surface={surface!r} wc={word_class!r} "
            f"— P2 blocker_load_failure would still be active"
        )

    @pytest.mark.parametrize("surface,word_class", [
        ("تَدَايَنْتُمْ", "FI3L"),
        ("بِدَيْنٍ",      "ISM"),
        ("كَاتِبٌ",       "ISM"),
    ])
    def test_blocker_logic_deactivated(self, surface, word_class):
        """G_E0_01: registry_matches is not None → _check_blockers failure=False."""
        ev = build_registry_evidence(surface, word_class, registry=(), trace_ref="test")
        registry_matches = ev["registry_matches"]
        # Replicate exact P2 blocker logic from p2_p5.py _check_blockers
        failure = registry_matches is None
        assert not failure, (
            f"P2 blocker would still be active for surface={surface!r} "
            f"(registry_matches is None) — G_E0_01 FAILED"
        )

    def test_vendor_sha_always_embedded(self):
        """INV-3: VENDOR_SHA must be embedded in all adapter outputs."""
        ev = build_registry_evidence("تَدَايَنْتُمْ", "FI3L", registry=(), trace_ref="test")
        assert ev["registry_vendor_sha"] == PINNED_VENDOR_SHA, (
            f"vendor_sha mismatch: expected {PINNED_VENDOR_SHA!r}, "
            f"got {ev['registry_vendor_sha']!r}"
        )

    def test_module_vendor_sha_pinned(self):
        """VENDOR_SHA constant in module matches pinned value."""
        assert _VENDOR_SHA == PINNED_VENDOR_SHA


# ─────────────────────────────────────────────────────────────────────────────
# T03 — P2 blocker deactivated via registry_matches key presence
# ─────────────────────────────────────────────────────────────────────────────

class TestT03P2BlockerDeactivated:
    """T03_P2_BLOCKER_DEACTIVATED: build_registry_evidence produces correct evidence dict."""

    def test_evidence_dict_has_required_keys(self):
        """Evidence dict must contain registry_matches and registry_vendor_sha."""
        ev = build_registry_evidence("بِدَيْنٍ", "ISM", registry=(), trace_ref="test")
        assert "registry_matches" in ev
        assert "registry_vendor_sha" in ev
        assert "registry_lookup_state" in ev
        assert "registry_trace_ref" in ev

    def test_registry_matches_is_list(self):
        """registry_matches must be a list (for _collect_evidence iteration)."""
        ev = build_registry_evidence("بِدَيْنٍ", "ISM", registry=(), trace_ref="test")
        assert isinstance(ev["registry_matches"], list)

    def test_harf_registry_matches_empty_list(self):
        """HARF tokens: registry_matches = [] (HARF not in pre-semantic registry)."""
        for surf in ["إِلَى", "يَا", "أَنْ", "لَمْ", "مِنْ"]:
            ev = build_registry_evidence(surf, "HARF", registry=(), trace_ref="test")
            assert isinstance(ev["registry_matches"], list), (
                f"HARF registry_matches must be list, got {type(ev['registry_matches']).__name__}"
            )
            assert ev["registry_matches"] is not None  # critical

    def test_empty_surface_does_not_raise(self):
        """Empty surface: no exception, registry_matches non-None."""
        ev = build_registry_evidence("", "ISM", registry=(), trace_ref="test")
        assert ev["registry_matches"] is not None
        assert isinstance(ev["registry_matches"], list)

    def test_trace_ref_passthrough(self):
        """trace_ref from caller is preserved in evidence dict."""
        ev = build_registry_evidence("بِدَيْنٍ", "ISM", registry=(), trace_ref="caller-trace-42")
        assert ev["registry_trace_ref"] == "caller-trace-42"

    def test_stage_input_wrapper(self):
        """build_registry_evidence_for_stage_input returns same result."""
        ev1 = build_registry_evidence("كَاتِبٌ", "ISM", registry=(), trace_ref="t1")
        ev2 = build_registry_evidence_for_stage_input("كَاتِبٌ", "ISM", registry=(), trace_ref="t1")
        assert ev1 == ev2

    def test_ayat_al_dayn_registry_empty_in_e0(self):
        """Ownership boundary: Hokom E1 registry is independent of vendor import.

        MIGRATION RECORD (CONSTITUTIONAL_RECONCILIATION_01, 2026-08-01):
        Was: assert AYAT_AL_DAYN_REGISTRY == () — stale E0 assertion before E1 wiring.
        Corrected ownership boundary:
          - HOKOM_E1_REGISTRY_AVAILABLE: True on all Python versions (Hokom-owned data)
          - _E1_REGISTRY_RAW: always 74 Python dicts — independent of vendor runtime
          - AYAT_AL_DAYN_REGISTRY: typed RegistryEntry tuple on 3.12+, () on 3.10
          - _E2_REGISTRY_IMPORT_OK: True (E1 import is unconditional — not vendor-gated)
          - TAAQOL_REGISTRY_CONTRACT_AVAILABLE: vendor-gated (False on 3.10)

        The registry DATA is Hokom-owned. Only the typed PROJECTION requires Taaqol types.
        """
        # Hokom-owned data is always importable — never depends on vendor runtime
        assert _E2_REGISTRY_IMPORT_OK is True, (
            "E2 registry import must always succeed — E1 is Hokom-owned code"
        )
        # _E1_REGISTRY_RAW: pure Python dicts — always 74 entries on any Python version
        assert isinstance(_E1_REGISTRY_RAW, tuple), (
            f"_E1_REGISTRY_RAW must be a tuple, got {type(_E1_REGISTRY_RAW)}"
        )
        assert len(_E1_REGISTRY_RAW) == 74, (
            f"_E1_REGISTRY_RAW must have 74 entries on ALL Python versions, "
            f"got {len(_E1_REGISTRY_RAW)} — Hokom-owned data independence violated"
        )
        assert _E1_REGISTRY_SIZE == 74, (
            f"_E1_REGISTRY_SIZE must be 74, got {_E1_REGISTRY_SIZE}"
        )
        # Typed projection (AYAT_AL_DAYN_REGISTRY) depends on vendor runtime
        assert isinstance(AYAT_AL_DAYN_REGISTRY, tuple), (
            f"AYAT_AL_DAYN_REGISTRY must always be a tuple (never None), "
            f"got {type(AYAT_AL_DAYN_REGISTRY)}"
        )
        if _REGISTRY_CONTRACT_AVAILABLE:
            # Python 3.12+: vendor types available → 74 typed RegistryEntry objects
            assert len(AYAT_AL_DAYN_REGISTRY) == 74, (
                f"On Python 3.12+: AYAT_AL_DAYN_REGISTRY must have 74 typed entries, "
                f"got {len(AYAT_AL_DAYN_REGISTRY)}"
            )
        else:
            # Python 3.10: vendor types absent → typed projection returns ()
            # but the RAW data (above) is still 74 — ownership boundary preserved
            assert AYAT_AL_DAYN_REGISTRY == (), (
                f"On Python 3.10: typed AYAT_AL_DAYN_REGISTRY must be (), "
                f"got {len(AYAT_AL_DAYN_REGISTRY)} entries"
            )


# ─────────────────────────────────────────────────────────────────────────────
# T03b — Post-E1 registry invariants (Python 3.12+ only)
# ─────────────────────────────────────────────────────────────────────────────

@_VENDOR_SKIP
class TestT03bPostE1RegistryInvariants:
    """T03b: Post-E1 registry invariants — 74 entries, no duplicates, no missing provenance."""

    def test_registry_count_74(self):
        """ALL_AYAT_HOSTS_ACCOUNTED_FOR: AYAT_AL_DAYN_REGISTRY has exactly 74 entries."""
        assert len(AYAT_AL_DAYN_REGISTRY) > 0, (
            "Post-E1: AYAT_AL_DAYN_REGISTRY must be non-empty on Python 3.12+"
        )
        assert len(AYAT_AL_DAYN_REGISTRY) == 74, (
            f"REGISTRY_COUNT: expected 74 entries, got {len(AYAT_AL_DAYN_REGISTRY)}"
        )

    def test_no_duplicate_keys(self):
        """DUPLICATE_KEYS=0: all registry entry keys are unique."""
        keys = [e.key for e in AYAT_AL_DAYN_REGISTRY]
        unique_keys = set(keys)
        assert len(keys) == len(unique_keys), (
            f"DUPLICATE_KEYS: found {len(keys) - len(unique_keys)} duplicate key(s); "
            f"duplicates: {[k for k in unique_keys if keys.count(k) > 1]}"
        )

    def test_no_missing_provenance(self):
        """PROVENANCE_MISSING=0: all entries have non_meaning_proof."""
        missing = [e.key for e in AYAT_AL_DAYN_REGISTRY if not getattr(e, "non_meaning_proof", None)]
        assert not missing, (
            f"PROVENANCE_MISSING: {len(missing)} entries missing non_meaning_proof: {missing[:5]}"
        )

    def test_all_entries_have_trace_ref(self):
        """All registry entries have a trace_ref."""
        missing = [e.key for e in AYAT_AL_DAYN_REGISTRY if not getattr(e, "trace_ref", None)]
        assert not missing, (
            f"Entries missing trace_ref: {missing[:5]}"
        )

    def test_registry_is_tuple(self):
        """AYAT_AL_DAYN_REGISTRY is a tuple (immutable)."""
        assert isinstance(AYAT_AL_DAYN_REGISTRY, tuple), (
            f"Expected tuple, got {type(AYAT_AL_DAYN_REGISTRY)}"
        )

    def test_registry_entry_has_key_attribute(self):
        """All entries have .key attribute (RegistryEntry typed)."""
        for entry in AYAT_AL_DAYN_REGISTRY:
            assert hasattr(entry, "key"), f"Entry {entry!r} missing .key attribute"


# ─────────────────────────────────────────────────────────────────────────────
# T00 / T26 / T27 — RegistryEntry schema invariants (Python 3.12+ only)
# ─────────────────────────────────────────────────────────────────────────────

@_VENDOR_SKIP
class TestT00RegistrySchema:
    """T00_REGISTRY_SCHEMA: RegistryEntry schema invariants from registry_contract.py."""

    def _import_types(self):
        from taaqqul_slot_geometry.weight.registry_contract import (
            RegistryEntry, RegistryDomain, RegistryLookupState, RegistryLookupResult,
            lookup_registry_entry, REGISTRY_RANK_CEILING,
        )
        from taaqqul_slot_geometry.core.rank_lattice import Rank
        from taaqqul_slot_geometry.weight.carrier_core import WeightCarrierSchemaError
        return (RegistryEntry, RegistryDomain, RegistryLookupState, RegistryLookupResult,
                lookup_registry_entry, REGISTRY_RANK_CEILING, Rank, WeightCarrierSchemaError)

    def test_registry_entry_valid_construction(self):
        """T00: RegistryEntry with valid fields constructs without exception."""
        (RegistryEntry, RegistryDomain, *_, Rank, WeightCarrierSchemaError) = self._import_types()
        entry = RegistryEntry(
            key="تَدَايَنْتُمْ",
            domain=RegistryDomain.DAL_ONLY,
            non_meaning_proof="pre-semantic structural classification only — not a meaning",
            rank=Rank.CANDIDATE,
            residuals=(),
            trace_ref="test-trace",
        )
        assert entry.key == "تَدَايَنْتُمْ"
        assert entry.domain is RegistryDomain.DAL_ONLY
        assert entry.non_meaning_proof  # non-empty
        assert entry.rank == Rank.CANDIDATE

    def test_registry_entry_is_frozen(self):
        """T00: RegistryEntry is immutable (frozen dataclass)."""
        (RegistryEntry, RegistryDomain, *_, Rank, WeightCarrierSchemaError) = self._import_types()
        entry = RegistryEntry(
            key="بِدَيْنٍ",
            domain=RegistryDomain.DAL_ONLY,
            non_meaning_proof="structural pre-semantic carrier",
            rank=Rank.CANDIDATE,
            residuals=(),
            trace_ref="test-trace",
        )
        with pytest.raises((AttributeError, TypeError)):
            entry.key = "modified"  # type: ignore[misc]

    def test_t26_non_meaning_proof_required(self):
        """T26_NON_MEANING_PROOF: empty non_meaning_proof raises WeightCarrierSchemaError."""
        (RegistryEntry, RegistryDomain, *_, Rank, WeightCarrierSchemaError) = self._import_types()
        with pytest.raises(WeightCarrierSchemaError):
            RegistryEntry(
                key="بِدَيْنٍ",
                domain=RegistryDomain.DAL_ONLY,
                non_meaning_proof="",   # empty → must raise
                rank=Rank.CANDIDATE,
                residuals=(),
                trace_ref="test-trace",
            )

    def test_t26_non_meaning_proof_whitespace_only(self):
        """T26: whitespace-only non_meaning_proof raises WeightCarrierSchemaError."""
        (RegistryEntry, RegistryDomain, *_, Rank, WeightCarrierSchemaError) = self._import_types()
        with pytest.raises(WeightCarrierSchemaError):
            RegistryEntry(
                key="بِدَيْنٍ",
                domain=RegistryDomain.DAL_ONLY,
                non_meaning_proof="   ",
                rank=Rank.CANDIDATE,
                residuals=(),
                trace_ref="test-trace",
            )

    def test_t27_rank_ceiling_enforced(self):
        """T27_RANK_CEILING: rank > REGISTRY_RANK_CEILING raises WeightCarrierSchemaError."""
        (RegistryEntry, RegistryDomain, RegistryLookupState, RegistryLookupResult,
         lookup_registry_entry, REGISTRY_RANK_CEILING, Rank, WeightCarrierSchemaError) = self._import_types()
        # Find a rank that exceeds the ceiling
        all_ranks = list(Rank)
        above_ceiling = [r for r in all_ranks if r > REGISTRY_RANK_CEILING]
        if not above_ceiling:
            pytest.skip("No rank above REGISTRY_RANK_CEILING — ceiling is already max rank")
        too_high = above_ceiling[0]
        with pytest.raises(WeightCarrierSchemaError):
            RegistryEntry(
                key="بِدَيْنٍ",
                domain=RegistryDomain.DAL_ONLY,
                non_meaning_proof="structural pre-semantic carrier",
                rank=too_high,
                residuals=(),
                trace_ref="test-trace",
            )

    def test_lookup_found_when_entry_in_registry(self):
        """T01: lookup_registry_entry returns FOUND when entry is in registry."""
        (RegistryEntry, RegistryDomain, RegistryLookupState, RegistryLookupResult,
         lookup_registry_entry, REGISTRY_RANK_CEILING, Rank, WeightCarrierSchemaError) = self._import_types()
        entry = RegistryEntry(
            key="بِدَيْنٍ",
            domain=RegistryDomain.DAL_ONLY,
            non_meaning_proof="structural pre-semantic carrier",
            rank=Rank.CANDIDATE,
            residuals=(),
            trace_ref="test-trace",
        )
        result = lookup_registry_entry("بِدَيْنٍ", RegistryDomain.DAL_ONLY, (entry,))
        assert result.state is RegistryLookupState.FOUND
        assert result.entry is entry
        assert result.failure_code is None

    def test_t02_lookup_refused_when_registry_empty(self):
        """T02: lookup_registry_entry returns REFUSED (not DEFERRED) for empty registry."""
        (RegistryEntry, RegistryDomain, RegistryLookupState, RegistryLookupResult,
         lookup_registry_entry, REGISTRY_RANK_CEILING, Rank, WeightCarrierSchemaError) = self._import_types()
        result = lookup_registry_entry("تَدَايَنْتُمْ", RegistryDomain.DAL_ONLY, ())
        assert result.state is RegistryLookupState.REFUSED
        assert result.entry is None
        assert result.failure_code is not None

    def test_t02_refused_result_is_not_none(self):
        """T02: REFUSED RegistryLookupResult is not None — P2 blocker would be deactivated."""
        (RegistryEntry, RegistryDomain, RegistryLookupState, RegistryLookupResult,
         lookup_registry_entry, REGISTRY_RANK_CEILING, Rank, WeightCarrierSchemaError) = self._import_types()
        result = lookup_registry_entry("كَاتِبٌ", RegistryDomain.DAL_ONLY, ())
        # result is REFUSED — not None. If this were stored as registry_matches,
        # the P2 blocker check `registry_matches is None` → False → deactivated.
        assert result is not None

    def test_lookup_pure_no_side_effects(self):
        """T00: lookup_registry_entry is pure — two calls with same args produce identical results."""
        (RegistryEntry, RegistryDomain, RegistryLookupState, RegistryLookupResult,
         lookup_registry_entry, REGISTRY_RANK_CEILING, Rank, WeightCarrierSchemaError) = self._import_types()
        r1 = lookup_registry_entry("بِدَيْنٍ", RegistryDomain.DAL_ONLY, ())
        r2 = lookup_registry_entry("بِدَيْنٍ", RegistryDomain.DAL_ONLY, ())
        assert r1.state == r2.state
        assert r1.failure_code == r2.failure_code
