"""
E2 P2 Registry Projection Tests — T_E2_*

Tests for registry_adapter.py E2 wiring (imports from E1 registry).

Constitutional gates verified: G_E2_01, G_E2_02, G_E2_04

G_E2_03 (P2→P3 cascade) requires Python 3.12+ full Hokom pipeline.
That gate is OWNER_VERIFICATION_REQUIRED on Python 3.12+.

Python 3.10 compat:
  - _E2_REGISTRY_IMPORT_OK = True (E1 module imports cleanly)
  - AYAT_AL_DAYN_REGISTRY = () on Python 3.10 (E1 build fails without vendor)
  - Lookup state = DEFERRED_IMPORT_FAILURE on 3.10 (vendor not available)
  - All registry_matches are non-None (blocker deactivated regardless)

VENDOR_SHA: 35381739410071ac21dd96702ecbb2acb493f90d
Phase: E2 — P2 REGISTRY PROJECTION
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.weight_layer.registry_adapter import (  # noqa: E402
    AYAT_AL_DAYN_REGISTRY,
    _E2_REGISTRY_IMPORT_OK,
    _REGISTRY_CONTRACT_AVAILABLE,
    _VENDOR_SHA,
    build_registry_evidence,
)

REQUIRES_312 = pytest.mark.skipif(
    not _REGISTRY_CONTRACT_AVAILABLE,
    reason="Requires Python 3.12+ (StrEnum vendor layer)",
)

# Sample ISM tokens from the corpus (should be in E1 registry)
_CORPUS_ISM_TOKENS = ["دَيْنٍ", "كَاتِبٌ", "رَجُلَيْنِ", "شَهِيدَيْنِ"]
# Sample HARF tokens (never in registry)
_CORPUS_HARF_TOKENS = ["إِذَا", "إِلَى", "عَلَيْهِ"]


# ── G_E2_01: E1 registry imported ─────────────────────────────────────────────

class TestT_E2_01_RegistryImported:
    """G_E2_01: registry_adapter.py imports AYAT_AL_DAYN_REGISTRY from E1."""

    def test_e2_registry_import_ok(self):
        """_E2_REGISTRY_IMPORT_OK = True — E1 module imported successfully."""
        assert _E2_REGISTRY_IMPORT_OK is True, (
            "E1 registry import failed — G_E2_01 NOT satisfied"
        )

    def test_ayat_al_dayn_registry_is_tuple(self):
        """AYAT_AL_DAYN_REGISTRY is a tuple (may be empty on 3.10)."""
        assert isinstance(AYAT_AL_DAYN_REGISTRY, tuple), (
            f"Expected tuple, got {type(AYAT_AL_DAYN_REGISTRY)}"
        )

    @REQUIRES_312
    def test_ayat_al_dayn_registry_populated_on_312(self):
        """AYAT_AL_DAYN_REGISTRY has 74 entries on Python 3.12+."""
        assert len(AYAT_AL_DAYN_REGISTRY) == 74, (
            f"Expected 74 entries, got {len(AYAT_AL_DAYN_REGISTRY)}"
        )


# ── G_E2_02: registry_matches non-None (P2 blocker deactivated) ──────────────

class TestT_E2_02_BlockerDeactivated:
    """G_E2_02: registry_matches is always non-None."""

    def test_ism_token_registry_matches_non_none(self):
        """ISM token: registry_matches is non-None (blocker deactivated)."""
        ev = build_registry_evidence(
            "تَدَايَنْتُمْ", "FI3L",
            registry=AYAT_AL_DAYN_REGISTRY,
            trace_ref="test:e2:t02:fi3l",
        )
        assert ev["registry_matches"] is not None, (
            "registry_matches is None — P2 blocker still active!"
        )
        assert isinstance(ev["registry_matches"], list), (
            f"registry_matches must be list, got {type(ev['registry_matches'])}"
        )

    def test_harf_token_registry_matches_non_none(self):
        """HARF token: registry_matches is non-None (deactivated)."""
        ev = build_registry_evidence(
            "إِلَى", "HARF",
            registry=AYAT_AL_DAYN_REGISTRY,
            trace_ref="test:e2:t02:harf",
        )
        assert ev["registry_matches"] is not None
        assert ev["registry_matches"] == []  # HARF never FOUND

    def test_empty_surface_registry_matches_non_none(self):
        """Empty surface: registry_matches is non-None."""
        ev = build_registry_evidence(
            "", "ISM",
            registry=AYAT_AL_DAYN_REGISTRY,
            trace_ref="test:e2:t02:empty",
        )
        assert ev["registry_matches"] is not None

    def test_unknown_wc_registry_matches_non_none(self):
        """Unknown word class: registry_matches is non-None."""
        ev = build_registry_evidence(
            "some_surface", "",
            registry=AYAT_AL_DAYN_REGISTRY,
            trace_ref="test:e2:t02:unknown_wc",
        )
        assert ev["registry_matches"] is not None

    def test_all_corpus_harf_tokens_deactivated(self):
        """All HARF corpus tokens have non-None registry_matches."""
        for harf in _CORPUS_HARF_TOKENS:
            ev = build_registry_evidence(
                harf, "HARF",
                registry=AYAT_AL_DAYN_REGISTRY,
                trace_ref=f"test:e2:harf:{harf}",
            )
            assert ev["registry_matches"] is not None, (
                f"HARF token {harf!r}: registry_matches is None"
            )
            assert ev["registry_matches"] == [], (
                f"HARF token {harf!r}: registry_matches non-empty"
            )


# ── G_E2_04: All lookup states tested ─────────────────────────────────────────

class TestT_E2_04_LookupStates:
    """G_E2_04: FOUND/REFUSED/DEFERRED/IMPORT_FAILURE states all exercised."""

    def test_import_failure_state_on_python_310(self):
        """On Python 3.10: ISM/FI3L tokens get DEFERRED_IMPORT_FAILURE."""
        if _REGISTRY_CONTRACT_AVAILABLE:
            pytest.skip("Python 3.12+ — import failure state not applicable")
        ev = build_registry_evidence(
            "تَدَايَنْتُمْ", "FI3L",
            registry=AYAT_AL_DAYN_REGISTRY,
            trace_ref="test:e2:t04:import_failure",
        )
        assert ev["registry_lookup_state"] == "DEFERRED_IMPORT_FAILURE", (
            f"Expected DEFERRED_IMPORT_FAILURE on 3.10, got {ev['registry_lookup_state']!r}"
        )

    def test_harf_not_applicable_state(self):
        """HARF tokens get NOT_APPLICABLE_HARF on Python 3.12+.
        On Python 3.10: vendor check fires first → DEFERRED_IMPORT_FAILURE.
        In both cases: registry_matches=[] (blocker deactivated).
        """
        ev = build_registry_evidence(
            "إِلَى", "HARF",
            registry=AYAT_AL_DAYN_REGISTRY,
            trace_ref="test:e2:t04:harf",
        )
        if _REGISTRY_CONTRACT_AVAILABLE:
            # Python 3.12+: HARF domain returns None → NOT_APPLICABLE_HARF
            assert ev["registry_lookup_state"] == "NOT_APPLICABLE_HARF", (
                f"Expected NOT_APPLICABLE_HARF on 3.12+, got {ev['registry_lookup_state']!r}"
            )
        else:
            # Python 3.10: vendor check fires first → DEFERRED_IMPORT_FAILURE
            assert ev["registry_lookup_state"] == "DEFERRED_IMPORT_FAILURE", (
                f"Expected DEFERRED_IMPORT_FAILURE on 3.10, got {ev['registry_lookup_state']!r}"
            )
        # In both cases: P2 blocker deactivated
        assert ev["registry_matches"] == []

    def test_refused_empty_surface_state(self):
        """Empty surface gets REFUSED_EMPTY_SURFACE on Python 3.12+.
        On Python 3.10: vendor check fires first → DEFERRED_IMPORT_FAILURE.
        In both cases: registry_matches=[] (blocker deactivated).
        """
        ev = build_registry_evidence(
            "", "ISM",
            registry=AYAT_AL_DAYN_REGISTRY,
            trace_ref="test:e2:t04:empty",
        )
        if _REGISTRY_CONTRACT_AVAILABLE:
            # Python 3.12+: domain check passes (ISM), then empty surface guard fires
            assert ev["registry_lookup_state"] == "REFUSED_EMPTY_SURFACE", (
                f"Expected REFUSED_EMPTY_SURFACE on 3.12+, got {ev['registry_lookup_state']!r}"
            )
        else:
            # Python 3.10: vendor check fires first → DEFERRED_IMPORT_FAILURE
            assert ev["registry_lookup_state"] == "DEFERRED_IMPORT_FAILURE", (
                f"Expected DEFERRED_IMPORT_FAILURE on 3.10, got {ev['registry_lookup_state']!r}"
            )
        # In both cases: registry_matches non-None
        assert ev["registry_matches"] == []

    @REQUIRES_312
    def test_found_state_for_corpus_ism(self):
        """ISM token from E1 registry returns FOUND state on Python 3.12+."""
        found_count = 0
        for token in _CORPUS_ISM_TOKENS:
            ev = build_registry_evidence(
                token, "ISM",
                registry=AYAT_AL_DAYN_REGISTRY,
                trace_ref=f"test:e2:t04:found:{token}",
            )
            if ev["registry_lookup_state"] in ("RegistryLookupState.FOUND", "FOUND"):
                found_count += 1
                assert len(ev["registry_matches"]) > 0, (
                    f"FOUND state but empty registry_matches for {token!r}"
                )
        assert found_count > 0, (
            f"No corpus ISM tokens found in registry — E2 wiring may be incomplete. "
            f"Tried: {_CORPUS_ISM_TOKENS}"
        )

    @REQUIRES_312
    def test_found_entry_has_non_meaning_proof(self):
        """A FOUND registry entry carries structural non_meaning_proof."""
        for token in _CORPUS_ISM_TOKENS:
            ev = build_registry_evidence(
                token, "ISM",
                registry=AYAT_AL_DAYN_REGISTRY,
                trace_ref=f"test:e2:t04:nmp:{token}",
            )
            if ev["registry_matches"]:
                match = ev["registry_matches"][0]
                assert "non_meaning_proof" in match, (
                    f"FOUND entry missing non_meaning_proof: {match}"
                )
                assert match["non_meaning_proof"].startswith("structural"), (
                    f"non_meaning_proof not structural: {match['non_meaning_proof']!r}"
                )
                break

    def test_vendor_sha_always_embedded(self):
        """vendor_sha is always embedded in evidence."""
        ev = build_registry_evidence(
            "تَدَايَنْتُمْ", "FI3L",
            registry=AYAT_AL_DAYN_REGISTRY,
            trace_ref="test:e2:t04:sha",
        )
        assert ev["registry_vendor_sha"] == _VENDOR_SHA, (
            f"vendor_sha mismatch: {ev['registry_vendor_sha']!r}"
        )


# ── G_E2_03: P2→P3 cascade (owner verification required) ─────────────────────

class TestT_E2_03_P2ToP3Cascade:
    """G_E2_03: T04_P2_TO_P3_CASCADE — requires Python 3.12+ full pipeline."""

    @pytest.mark.skip(reason="OWNER_VERIFICATION_REQUIRED: Run full Hokom pipeline "
                             "on Python 3.12+ to verify P2→P3 cascade with E1 registry wired.")
    def test_p2_to_p3_cascade_full_pipeline(self):
        """P3 stage opens when registry_matches is non-None.

        Owner must run this on Python 3.12+ with full Hokom pipeline:
            from pipeline.taaqol_integration.weight_layer.registry_adapter import (
                AYAT_AL_DAYN_REGISTRY, build_registry_evidence_for_stage_input
            )
            evidence = build_registry_evidence_for_stage_input(
                token_surface="دَيْنٍ", word_class="ISM",
                registry=AYAT_AL_DAYN_REGISTRY,
                trace_ref=pipeline_trace.trace_id,
            )
            # Pass evidence to Hokom P2 stage; verify P3 opens.
        """
        pass
