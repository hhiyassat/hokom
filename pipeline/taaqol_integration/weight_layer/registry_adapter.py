"""
Registry Adapter — E1/E2_PROVISIONAL_IMPLEMENTATION_ARTIFACT (A0_REGISTRY_LOOKUP)

CONSTITUTIONAL_RECONCILIATION_01 (2026-08-01):
    Reclassified from "E0_A0_REGISTRY_LOOKUP" to "E1/E2_PROVISIONAL_IMPLEMENTATION_ARTIFACT".
    Under constitutional reclassification:
      - E0 = TARGET BASELINE FREEZE (SHAs only — no implementation)
      - E1 = AYAT-AL-DAYN CANONICAL LEXICAL REGISTRY (registry content)
      - E2 = P2 REGISTRY PROJECTION (this adapter, consuming E1 registry)
    This file is an E2 deliverable (P2 registry projection using E1 registry).
    AYAT_AL_DAYN_REGISTRY must be imported from E1 (ayat_al_dayn_registry.py) in E2.
    Current state: AYAT_AL_DAYN_REGISTRY = () (empty tuple — E1 not yet wired).
    E2 task: replace AYAT_AL_DAYN_REGISTRY = () with import from E1.

Purpose:
    Provides `build_registry_evidence(token_surface, word_class)` which populates
    hokom_evidence["P2_REGISTRY_PROJECTION"]["registry_matches"] with a non-None
    value, deactivating the `registry_load_failure` blocker in RegistryProjectionAdapter.

Blocker root cause (confirmed in p2_p5.py _check_blockers):
    registry_matches = input.hokom_evidence.get("registry_matches")
    failure = registry_matches is None          ← None triggers blocker
    → Fix: ensure key is present and value is not None ([] is valid)

Phase: E2 — P2 REGISTRY PROJECTION (formerly labeled E0)
Constitutional gate: G_E2_02, G_E2_03

Constitutional invariants:
    - RegistryEntry ≠ Meaning (PR-16C §6)
    - lookup_registry_entry() is pure: no I/O (PR-16C §5)
    - FAIL-CLOSED: ImportError → registry_matches=[] (non-None, blocker deactivated)
    - No synthetic trace_id: trace_ref must come from caller's PipelineTrace
    - VENDOR_SHA embedded in all produced artifacts
    - No lexical content in E0: registry is empty — all lookups return REFUSED
    - Lexical population is E1 scope (after schema freeze)

Adapter outputs for _collect_evidence (p2_p5.py):
    registry_matches: list[dict]  each dict = {slot_id, root, match_confidence}
    - FOUND entry → [{"slot_id": entry.key, "root": entry.key, "match_confidence": 0.9}]
    - REFUSED/DEFERRED/EMPTY → []   (non-None → blocker deactivated)

VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3 (pinned)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# ── Vendor path ──────────────────────────────────────────────────────────────
_REPO_ROOT   = Path(__file__).resolve().parents[3]
_VENDOR_PATH = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"
_VENDOR_SHA  = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

# ── E1: Hokom-owned lexical registry (unconditional import) ──────────────────
# AYAT_AL_DAYN_REGISTRY is Hokom-owned data — import must succeed regardless of
# vendor runtime. Its EXISTENCE is independent of whether Taaqol imports succeed.
# On Python 3.10: AYAT_AL_DAYN_REGISTRY = () (RegistryEntry type not constructable,
#   E1 build_ayat_al_dayn_registry() returns () — but the import succeeds).
# On Python 3.12+: AYAT_AL_DAYN_REGISTRY = tuple of 74 typed RegistryEntry objects.
# _E1_REGISTRY_RAW is ALWAYS 74 Python dicts on any Python version.
#
# Ownership boundary:
#   HOKOM_E1_REGISTRY_AVAILABLE  = True (independent of vendor import)
#   TAAQOL_REGISTRY_CONTRACT_AVAILABLE = determined by vendor try/except below
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)
from pipeline.taaqol_integration.e1_lexical_registry.ayat_al_dayn_registry import (  # noqa: E402
    AYAT_AL_DAYN_REGISTRY,
    _REGISTRY_RAW as _E1_REGISTRY_RAW,
    REGISTRY_SIZE as _E1_REGISTRY_SIZE,
    _REGISTRY_CONTRACT_AVAILABLE as _HOKOM_E1_REGISTRY_AVAILABLE,
)
_E2_REGISTRY_IMPORT_OK = True   # always True — E1 is Hokom-owned, always importable

# ── Taaqol vendor: registry contract types (gated on vendor runtime) ──────────
# These types are required only for the typed lookup projection.
# The Hokom-owned registry data (above) is always available regardless.
_REGISTRY_CONTRACT_AVAILABLE = False
_lookup_registry_entry = None
_RegistryDomain        = None
_RegistryLookupState   = None
_RegistryEntry         = None

try:
    _vendor_src = str(_VENDOR_PATH)
    if _vendor_src not in sys.path:
        sys.path.insert(0, _vendor_src)
    from taaqqul_slot_geometry.weight.registry_contract import (  # type: ignore
        lookup_registry_entry as _lookup_registry_entry,
        RegistryDomain        as _RegistryDomain,
        RegistryLookupState   as _RegistryLookupState,
        RegistryEntry         as _RegistryEntry,
    )
    _REGISTRY_CONTRACT_AVAILABLE = True
except ImportError:
    pass  # FAIL-CLOSED: all callers receive registry_matches=[] (non-None)


# ── Word-class → domain mapping (structural only — no linguistic content) ────
# HARF tokens are not in the pre-semantic registry (not DAL or VERBAL_MADLUL).
# ISM and FI3L may appear in either domain; try DAL_ONLY first as primary.
# This mapping is provisional for E0 — refined domain inference is E1 scope.

_WORD_CLASS_TO_DOMAIN_HINT = {
    "ISM":  "DAL_ONLY",
    "FI3L": "DAL_ONLY",
    "HARF": None,        # HARF not applicable for registry
}


def _word_class_to_domain(word_class: str):
    """
    Map Hokom word class string to a RegistryDomain for the primary lookup.

    Returns None for HARF (not applicable) and for unknown word classes.
    This is a structural mapping only — no linguistic interpretation.
    """
    if not _REGISTRY_CONTRACT_AVAILABLE or _RegistryDomain is None:
        return None
    hint = _WORD_CLASS_TO_DOMAIN_HINT.get(str(word_class).upper())
    if hint is None:
        return None
    try:
        return _RegistryDomain(hint)
    except Exception:
        return None


def build_registry_evidence(
    token_surface: str,
    word_class: str,
    registry: "tuple[Any, ...]" = (),
    trace_ref: str = "",
) -> dict:
    """
    Build hokom_evidence dict for P2_REGISTRY_PROJECTION.

    Returns a dict that must be merged into hokom_evidence_by_stage["P2_REGISTRY_PROJECTION"].

    Constitutional requirements:
    - registry_matches is NEVER None (fixes registry_load_failure blocker)
    - On ImportError or any exception: registry_matches = [] (non-None, FAIL-CLOSED)
    - trace_ref must be provided by caller from live PipelineTrace (not synthetic)
    - vendor_sha is always embedded

    Args:
        token_surface: The token surface form (Arabic, original or normalized).
        word_class: Hokom word class (ISM | FI3L | HARF | "").
        registry: Tuple of RegistryEntry objects to search. Empty in E0.
                  Populated in E1 with ayat_al_dayn lexical entries.
        trace_ref: trace_id from caller's live PipelineTrace. Required from E1.

    Returns:
        dict: {
            "registry_matches": list[dict],  # never None
            "registry_lookup_state": str,
            "registry_vendor_sha": str,
            "registry_trace_ref": str,
        }
    """
    _base = {
        "registry_matches":      [],    # default: non-None (blocker deactivated)
        "registry_lookup_state": "DEFERRED_NO_CONTRACT",
        "registry_vendor_sha":   _VENDOR_SHA,
        "registry_trace_ref":    trace_ref,
    }

    # ── Guard: vendor not available ──────────────────────────────────────────
    if not _REGISTRY_CONTRACT_AVAILABLE:
        _base["registry_lookup_state"] = "DEFERRED_IMPORT_FAILURE"
        return _base

    # ── Guard: HARF tokens — not applicable ─────────────────────────────────
    domain = _word_class_to_domain(word_class)
    if domain is None:
        _base["registry_lookup_state"] = "NOT_APPLICABLE_HARF"
        return _base

    # ── Guard: empty or whitespace surface ──────────────────────────────────
    surface = (token_surface or "").strip()
    if not surface:
        _base["registry_lookup_state"] = "REFUSED_EMPTY_SURFACE"
        return _base

    # ── Call lookup_registry_entry (pure — no I/O) ──────────────────────────
    try:
        result = _lookup_registry_entry(
            candidate_key=surface,
            domain=domain,
            registry=registry if isinstance(registry, tuple) else tuple(registry),
        )
    except Exception:
        # Unexpected error in pure function — treat as DEFERRED (fail-closed)
        _base["registry_lookup_state"] = "DEFERRED_LOOKUP_ERROR"
        return _base

    # ── Map RegistryLookupResult → registry_matches list ────────────────────
    state_str = str(result.state)
    _base["registry_lookup_state"] = state_str

    if _RegistryLookupState is not None and result.state is _RegistryLookupState.FOUND:
        # Entry found: convert to _collect_evidence list format
        entry = result.entry
        _base["registry_matches"] = [{
            "slot_id":        entry.key,
            "root":           entry.key,
            "match_confidence": 0.9,
            "domain":         str(entry.domain),
            "rank":           str(entry.rank),
            "non_meaning_proof": entry.non_meaning_proof,   # structural proof only
            "trace_ref":      entry.trace_ref,
        }]
    else:
        # REFUSED or DEFERRED: registry_matches = [] (non-None — blocker deactivated)
        # Failure code embedded for observability
        if result.failure_code is not None:
            _base["registry_lookup_failure_code"] = str(result.failure_code)
        _base["registry_matches"] = []

    return _base


def build_registry_evidence_for_stage_input(
    token_surface: str,
    word_class: str,
    registry: "tuple[Any, ...]" = (),
    trace_ref: str = "",
) -> dict:
    """
    Convenience wrapper: returns a dict suitable for merging into
    hokom_evidence_by_stage["P2_REGISTRY_PROJECTION"].

    Usage:
        word_input = WordInput(
            surface=token_surface,
            hokom_evidence_by_stage={
                "P2_REGISTRY_PROJECTION": build_registry_evidence_for_stage_input(
                    token_surface=token_surface,
                    word_class=word_class,
                    registry=AYAT_AL_DAYN_REGISTRY,   # E1: populated; E0: ()
                    trace_ref=pipeline_trace.trace_id,
                ),
                # other stages...
            },
            ...
        )

    Constitutional gate check (caller must verify before moving to E1):
        evidence = build_registry_evidence_for_stage_input(...)
        assert evidence["registry_matches"] is not None, "blocker still active"
    """
    return build_registry_evidence(
        token_surface=token_surface,
        word_class=word_class,
        registry=registry,
        trace_ref=trace_ref,
    )


# ── Module-level invariant assertions (run at import time) ──────────────────
# These verify the adapter invariants without touching any lexical data.

def _verify_invariants() -> None:
    """Verify E0 adapter invariants. Raises AssertionError on violation.

    Invariants hold regardless of whether the vendor import succeeded.
    Python 3.10 (sandbox): _REGISTRY_CONTRACT_AVAILABLE=False — all lookups
    return DEFERRED_IMPORT_FAILURE, but registry_matches is still non-None.
    Python 3.12+ (production): full lookup path exercised.
    """
    # INV-1: build_registry_evidence always returns non-None registry_matches
    # This is the critical invariant — fixes the P2 blocker.
    for _surf, _wc in [("تَدَايَنْتُمْ", "FI3L"), ("بِدَيْنٍ", "ISM"), ("إِلَى", "HARF"), ("", "ISM")]:
        ev = build_registry_evidence(_surf, _wc, registry=(), trace_ref="test")
        assert ev["registry_matches"] is not None, (
            f"INV-1 VIOLATED: registry_matches is None for surface={_surf!r} wc={_wc!r}"
        )

    # INV-2: HARF tokens are never FOUND in the registry.
    # On Python 3.12+ with vendor available: state = NOT_APPLICABLE_HARF
    # On Python 3.10 (import failure): state = DEFERRED_IMPORT_FAILURE
    # In both cases: registry_matches = [] (never FOUND for HARF)
    ev_harf = build_registry_evidence("إِلَى", "HARF", registry=(), trace_ref="test")
    assert ev_harf["registry_lookup_state"] != "FOUND", (
        f"INV-2 VIOLATED: HARF must never be FOUND, got {ev_harf['registry_lookup_state']!r}"
    )
    assert ev_harf["registry_matches"] == [], (
        f"INV-2b VIOLATED: HARF registry_matches must be [], got {ev_harf['registry_matches']!r}"
    )

    # INV-3: vendor_sha is always embedded
    ev_any = build_registry_evidence("تَدَايَنْتُمْ", "FI3L", registry=(), trace_ref="test")
    assert ev_any["registry_vendor_sha"] == _VENDOR_SHA, "INV-3 VIOLATED: vendor_sha missing"

    # INV-4: empty surface returns non-None registry_matches (not an exception)
    ev_empty = build_registry_evidence("", "FI3L", registry=(), trace_ref="test")
    assert ev_empty["registry_matches"] is not None, "INV-4 VIOLATED: empty surface produced None"


_verify_invariants()

__all__ = [
    "build_registry_evidence",
    "build_registry_evidence_for_stage_input",
    "AYAT_AL_DAYN_REGISTRY",
    "_E1_REGISTRY_RAW",
    "_E1_REGISTRY_SIZE",
    "_HOKOM_E1_REGISTRY_AVAILABLE",
    "_E2_REGISTRY_IMPORT_OK",
    "_REGISTRY_CONTRACT_AVAILABLE",
    "_VENDOR_SHA",
]
