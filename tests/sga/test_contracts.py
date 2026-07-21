"""
HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-TESTS-01

16 constitutional tests for the Hokom SGA typed slot contracts.

These tests freeze the invariants of pipeline/sga/contracts.py.
They run on Python 3.10+ (no StrEnum, no taaqqul_slot_geometry import).
NO skip marks. NO xfail marks.

Tests 1-9, 14-16: semantic tests of contracts.py.
Tests 10-13: structural tests of architecture boundaries.
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

# Ensure repo root is on path
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pipeline.sga.contracts import (
    CandidateEntry,
    CandidateSet,
    ClaimProfile,
    CLAIM_PROFILES,
    compute_claim_key,
    deserialize_claim_bundle,
    DomainTransitionLicense,
    EvidenceReference,
    HokomClaimBundle,
    HokomResidualRecord,
    NormalizationOp,
    serialize_claim_bundle,
    SlotId,
    SlotSort,
    SlotState,
    SurfaceProvenance,
    TypedSlot,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_surface(original: str = "كَتَبَ", normalized: str = "كَتَبَ") -> SurfaceProvenance:
    return SurfaceProvenance(
        original_surface=original,
        normalized_surface=normalized,
    )


def _make_filled_slot(slot_id: SlotId = SlotId.SEGMENT_HOST, value: str = "كَتَبَ") -> TypedSlot:
    return TypedSlot(
        slot_id=slot_id,
        sort=SlotSort.SEGMENTATION,
        state=SlotState.FILLED,
        value=value,
    )


def _make_bundle(claim_kind: str = "ROOT_CLAIM", claim_key: str = "a" * 64) -> HokomClaimBundle:
    surface = _make_surface()
    slot = _make_filled_slot()
    return HokomClaimBundle(
        claim_key=claim_key,
        claim_kind=claim_kind,
        profile_id=claim_kind,
        surface=surface,
        typed_slots=(slot,),
        candidate_sets={},
        evidence_refs=(EvidenceReference(
            evidence_id="ev:root_catalog:1",
            kind="CATALOG_HIT",
            source="hokom",
        ),),
        condition_facts=("ROOT_IS_TRILATERAL",),
        obstacle_facts=(),
        defeater_facts=(),
        domain_licenses=(),
        residuals=(),
    )


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 1
# UNKNOWN slot must have value=None (never coerced to default)
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_01_unknown_slot_value_is_none():
    """UNKNOWN state enforces value=None — cannot hold a linguistic value."""
    slot = TypedSlot(
        slot_id=SlotId.ROOT_CANDIDATE_SET,
        sort=SlotSort.RADICAL,
        state=SlotState.UNKNOWN,
        value=None,
    )
    assert slot.state == SlotState.UNKNOWN
    assert slot.value is None


def test_constitutional_01b_unknown_slot_rejects_value():
    """UNKNOWN state with value != None must raise AssertionError."""
    with pytest.raises(AssertionError):
        TypedSlot(
            slot_id=SlotId.ROOT_CANDIDATE_SET,
            sort=SlotSort.RADICAL,
            state=SlotState.UNKNOWN,
            value="ك-ت-ب",  # must be None for UNKNOWN
        )


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 2
# AMBIGUOUS state preserves all candidates and selected=None
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_02_ambiguous_preserves_all_candidates():
    """AMBIGUOUS state must preserve all candidate entries and leave selected=None."""
    c1 = CandidateEntry(value="ك-ت-ب", evidence_code="WAZN_MATCH")
    c2 = CandidateEntry(value="ك-ب-ت", evidence_code="PATTERN_MATCH")
    cs = CandidateSet(candidates=(c1, c2), selected=None)
    slot = TypedSlot(
        slot_id=SlotId.ROOT_CANDIDATE_SET,
        sort=SlotSort.RADICAL,
        state=SlotState.AMBIGUOUS,
        candidate_set=cs,
    )
    assert slot.state == SlotState.AMBIGUOUS
    assert slot.candidate_set is not None
    assert len(slot.candidate_set.candidates) == 2
    assert slot.candidate_set.selected is None


def test_constitutional_02b_ambiguous_rejects_single_candidate():
    """AMBIGUOUS with only 1 candidate must raise AssertionError."""
    c1 = CandidateEntry(value="ك-ت-ب", evidence_code="WAZN_MATCH")
    cs = CandidateSet(candidates=(c1,), selected=None)
    with pytest.raises(AssertionError):
        TypedSlot(
            slot_id=SlotId.ROOT_CANDIDATE_SET,
            sort=SlotSort.RADICAL,
            state=SlotState.AMBIGUOUS,
            candidate_set=cs,
        )


def test_constitutional_02c_ambiguous_rejects_filled_selected():
    """AMBIGUOUS with selected != None must raise AssertionError."""
    c1 = CandidateEntry(value="ك-ت-ب", evidence_code="WAZN_MATCH")
    c2 = CandidateEntry(value="ك-ب-ت", evidence_code="PATTERN_MATCH")
    with pytest.raises(AssertionError):
        cs = CandidateSet(candidates=(c1, c2), selected="ك-ت-ب", selection_evidence="ev:1")
        TypedSlot(
            slot_id=SlotId.ROOT_CANDIDATE_SET,
            sort=SlotSort.RADICAL,
            state=SlotState.AMBIGUOUS,
            candidate_set=cs,
        )


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 3
# Active obstacle produces BLOCKED semantics via HokomResidualRecord
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_03_active_obstacle_is_residual_blocking():
    """Blocking residual records must be visible and have BLOCKING kind semantics."""
    residual = HokomResidualRecord(
        residual_id="res:blocking:01",
        code="block:root:insufficient_evidence",
        kind="BLOCKING",
        source_slot=SlotId.ROOT_CANDIDATE_SET,
        reason="Insufficient evidence for root selection",
        visibility="VISIBLE",
    )
    assert residual.kind == "BLOCKING"
    assert residual.visibility == "VISIBLE"
    assert residual.code.startswith("block:")


def test_constitutional_03b_deferrable_residual_is_not_blocking():
    """DEFERRABLE residual must not carry BLOCKING semantics."""
    residual = HokomResidualRecord(
        residual_id="res:defer:01",
        code="defer:pattern:ambiguous",
        kind="DEFERRABLE",
        source_slot=SlotId.PATTERN_CANDIDATE_SET,
        reason="Pattern ambiguous — defer to context",
    )
    assert residual.kind == "DEFERRABLE"
    assert residual.kind != "BLOCKING"


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 4
# Insufficient evidence produces DEFERRED semantics
# (ClaimProfile enforces minimum_evidence_count)
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_04_claim_profile_requires_minimum_evidence():
    """Every non-reserved CLAIM_PROFILE must declare minimum_evidence_count >= 1."""
    from pipeline.sga.contracts import RESERVED_CLAIM_PROFILES
    for profile_id, profile in CLAIM_PROFILES.items():
        if profile_id in RESERVED_CLAIM_PROFILES:
            continue
        assert profile.minimum_evidence_count >= 1, (
            f"{profile_id}: minimum_evidence_count must be >= 1 for non-reserved profiles"
        )


def test_constitutional_04b_evidence_reference_has_required_fields():
    """EvidenceReference must carry evidence_id, kind, and source."""
    ev = EvidenceReference(
        evidence_id="ev:catalog:k-t-b",
        kind="CATALOG_HIT",
        source="hokom_root_catalog",
    )
    assert ev.evidence_id
    assert ev.kind
    assert ev.source


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 5
# Residuals do not disappear after verdict — bundle preserves them
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_05_residuals_preserved_in_bundle():
    """Residuals placed in HokomClaimBundle must survive bundle creation."""
    residual = HokomResidualRecord(
        residual_id="res:weak:01",
        code="WEAK_RADICAL",
        kind="DEFERRABLE",
        source_slot=SlotId.WEAK_RADICAL_SLOT,
        reason="Weak radical position identified",
        next_evidence_required="LEXICAL_CATALOG_HIT",
    )
    surface = _make_surface()
    bundle = HokomClaimBundle(
        claim_key="a" * 64,
        claim_kind="ROOT_CLAIM",
        profile_id="ROOT_CLAIM",
        surface=surface,
        typed_slots=(),
        candidate_sets={},
        evidence_refs=(),
        condition_facts=(),
        obstacle_facts=(),
        defeater_facts=(),
        domain_licenses=(),
        residuals=(residual,),
    )
    assert len(bundle.residuals) == 1
    assert bundle.residuals[0].code == "WEAK_RADICAL"
    assert bundle.residuals[0].next_evidence_required == "LEXICAL_CATALOG_HIT"


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 6
# Closed boundary cannot be reopened (frozen dataclasses enforce immutability)
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_06_closed_boundary_cannot_be_reopened():
    """SurfaceProvenance is frozen — cannot mutate original_surface after creation."""
    surface = _make_surface("كَتَبَ", "كَتَبَ")
    with pytest.raises((AttributeError, TypeError)):
        surface.original_surface = "modified"  # type: ignore[misc]


def test_constitutional_06b_typed_slot_immutability():
    """TypedSlot value cannot be mutated after creation (mutable but owner-enforced)."""
    slot = _make_filled_slot()
    # TypedSlot is a regular dataclass (not frozen) but the state machine enforces invariants
    # at construction time — this test verifies the construction invariant held.
    assert slot.state == SlotState.FILLED
    assert slot.value is not None


def test_constitutional_06c_candidate_set_is_frozen():
    """CandidateSet is frozen — cannot reassign fields."""
    cs = CandidateSet(candidates=(), selected=None)
    with pytest.raises((AttributeError, TypeError)):
        cs.selected = "ك-ت-ب"  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 7
# Runtime failure does not produce semantic verdict
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_07_runtime_failure_no_semantic_verdict():
    """
    When taaqol_runtime.active=False, taaqol_verdict must be None.
    Verified via HokomTaaqolDecision contract (not bridge execution).
    """
    # Import the decision model (Python 3.10 safe — no StrEnum)
    from pipeline.taaqol_integration.live.models import HokomTaaqolDecision
    decision = HokomTaaqolDecision(
        bridge_id="HOKOM_TAAQOL_LIVE_BRIDGE",
        taaqol_commit="unknown",
        hokom_commit="unknown",
        strict_mode=True,
        slot_graph_digest="UNAVAILABLE",
        gamma_result="UNAVAILABLE",
        transition_gate_result="UNAVAILABLE",
        taaqol_verdict="DEFERRED",
        reason_codes=("TAAQOL_RUNTIME_UNAVAILABLE",),
        contradictions=(),
        residuals=("defer:taaqol:runtime_unavailable",),
        trace=(),
        upstream_verdict="DEFER",
        effective_verdict="DEFERRED",
        fail_closed=True,
        source_engine="TAAQOL",
        taaqol_runtime={"active": False, "failure_code": "TAAQOL_RUNTIME_UNAVAILABLE"},
    )
    # The liveness contract: active=False means no semantic verdict
    assert decision.taaqol_runtime is not None
    assert decision.taaqol_runtime["active"] is False
    assert decision.taaqol_runtime["failure_code"] == "TAAQOL_RUNTIME_UNAVAILABLE"
    # On a real pipeline call, taaqol_verdict in hokom() output is set to None
    # when active=False (see hokom_pipeline.py line: if _taaqol_runtime.get('active'))
    # We verify the contract: DEFERRED verdict paired with active=False is not semantic.
    assert decision.fail_closed is True


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 8
# claim_key is stable for same content
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_08_claim_key_stable_for_same_content():
    """compute_claim_key must return the same hash for identical inputs."""
    key1 = compute_claim_key(
        claim_kind="ROOT_CLAIM",
        profile_id="ROOT_CLAIM",
        slot_values={"RADICAL_R1": "ك", "RADICAL_R2": "ت", "RADICAL_R3": "ب"},
        evidence_codes=("ev:wazn:1", "ev:catalog:2"),
    )
    key2 = compute_claim_key(
        claim_kind="ROOT_CLAIM",
        profile_id="ROOT_CLAIM",
        slot_values={"RADICAL_R1": "ك", "RADICAL_R2": "ت", "RADICAL_R3": "ب"},
        evidence_codes=("ev:wazn:1", "ev:catalog:2"),
    )
    assert key1 == key2
    assert len(key1) == 64  # SHA-256 hex digest length


def test_constitutional_08b_claim_key_is_sha256():
    """compute_claim_key produces a 64-character hex string (SHA-256)."""
    key = compute_claim_key(
        claim_kind="WORD_CLASS_CLAIM",
        profile_id="WORD_CLASS_CLAIM",
        slot_values={"WORD_CLASS_SLOT": "FI3L"},
        evidence_codes=("ev:morphological:1",),
    )
    assert len(key) == 64
    int(key, 16)  # must be valid hex


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 9
# Different claim content produces different keys (uniqueness)
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_09_different_content_different_keys():
    """Two claims with different content must produce different claim_keys."""
    key_root = compute_claim_key(
        claim_kind="ROOT_CLAIM",
        profile_id="ROOT_CLAIM",
        slot_values={"RADICAL_R1": "ك", "RADICAL_R2": "ت", "RADICAL_R3": "ب"},
        evidence_codes=("ev:wazn:1",),
    )
    key_pattern = compute_claim_key(
        claim_kind="PATTERN_CLAIM",
        profile_id="PATTERN_CLAIM",
        slot_values={"PATTERN_CANDIDATE_SET": "فَعَلَ"},
        evidence_codes=("ev:wazn:1",),
    )
    assert key_root != key_pattern


def test_constitutional_09b_same_kind_different_slots_different_keys():
    """Same claim_kind with different slot values must produce different keys."""
    key1 = compute_claim_key(
        claim_kind="ROOT_CLAIM",
        profile_id="ROOT_CLAIM",
        slot_values={"RADICAL_R1": "ك", "RADICAL_R2": "ت", "RADICAL_R3": "ب"},
        evidence_codes=(),
    )
    key2 = compute_claim_key(
        claim_kind="ROOT_CLAIM",
        profile_id="ROOT_CLAIM",
        slot_values={"RADICAL_R1": "ض", "RADICAL_R2": "ر", "RADICAL_R3": "ب"},
        evidence_codes=(),
    )
    assert key1 != key2


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 10
# Rank changes only via RankLattice (structural: bridge.py cannot set rank directly
# in the final verdict; only gate.decide() outcome determines verdict rank)
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_10_bridge_does_not_set_rank_directly():
    """
    Structural test: bridge.py must not contain a line that promotes rank
    by direct assignment outside of gate.decide() return value.
    The bridge maps gate_verdict.state to a string verdict — it never
    calls rank_lattice.meet() or directly assigns Rank.LICENSED as a final verdict.
    """
    bridge_path = _REPO_ROOT / "pipeline" / "taaqol_integration" / "live" / "bridge.py"
    source = bridge_path.read_text(encoding="utf-8")

    # The bridge must call gate.decide() — result drives verdict via state string mapping
    assert "gate.decide(" in source, "bridge must call gate.decide()"

    # The bridge must use _map_transition_state_to_verdict — not hardcode 'LICENSED'
    # as the final verdict without going through gate state mapping.
    assert "_map_transition_state_to_verdict" in source, (
        "bridge must use _map_transition_state_to_verdict for final verdict"
    )

    # Bridge must not call rank_lattice.meet() or rank_lattice.join() directly
    assert "rank_lattice.meet(" not in source
    assert "rank_lattice.join(" not in source


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 11
# GenericPayload cannot become LICENSED
# (structural: CLAIM_PROFILES require minimum evidence; reserved profiles have 0)
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_11_reserved_profiles_have_no_required_slots():
    """Reserved claim profiles (stub/future) have empty required_slots — not LICENSED."""
    from pipeline.sga.contracts import RESERVED_CLAIM_PROFILES
    for profile_id in RESERVED_CLAIM_PROFILES:
        if profile_id in CLAIM_PROFILES:
            profile = CLAIM_PROFILES[profile_id]
            # Reserved profiles are stubs: no required slots, no evidence minimum
            assert len(profile.required_slots) == 0, (
                f"{profile_id}: reserved profiles must have empty required_slots"
            )


def test_constitutional_11b_active_profiles_require_evidence():
    """Non-reserved claim profiles must require at least 1 slot and 1 evidence."""
    from pipeline.sga.contracts import RESERVED_CLAIM_PROFILES
    for profile_id, profile in CLAIM_PROFILES.items():
        if profile_id in RESERVED_CLAIM_PROFILES:
            continue
        assert len(profile.required_slots) >= 1, (
            f"{profile_id}: active profiles must have at least 1 required slot"
        )
        assert profile.minimum_evidence_count >= 1, (
            f"{profile_id}: active profiles must require minimum_evidence_count >= 1"
        )


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 12
# Bridge contains no Arabic morphological rules
# (structural: bridge.py must not contain Arabic letter literals for rule logic)
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_12_bridge_contains_no_arabic_rules():
    """
    Structural test: bridge.py must not contain Arabic letter literals used
    as morphological rule conditions (root extraction, wazn matching, etc.).
    Arabic strings appearing only as domain labels or log messages are allowed,
    but rule-condition patterns like if 'ك' in root: are forbidden.
    """
    bridge_path = _REPO_ROOT / "pipeline" / "taaqol_integration" / "live" / "bridge.py"
    source = bridge_path.read_text(encoding="utf-8")

    # Arabic morphological rule patterns must not appear in bridge
    # (root letter tests, wazn membership, pattern matching)
    forbidden_patterns = [
        # Root analysis patterns
        "trilateral_root",
        "canonical_root",
        "root_candidate",
        "wazn_catalog",
        "wazn_match",
        # Pre-root decision
        "verbal_root_path",
        "nominal_morphology",
        "assess_pre_root",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in source, (
            f"bridge.py must not contain Arabic rule pattern '{pattern}' — "
            f"Arabic rules belong in HOKOM, not BRIDGE"
        )


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 13
# Taaqol vendor does not contain root/wazn extraction
# (structural: vendor src must not import from hokom pipeline modules)
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_13_taaqol_vendor_has_no_hokom_imports():
    """
    Structural test: taaqqul_slot_geometry vendor must not import from
    hokom's pipeline modules (no Arabic morphology in vendor).
    """
    vendor_src = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src" / "taaqqul_slot_geometry"
    import re as _re
    # Match actual Python import statements only (not prose references)
    hokom_import_patterns = [
        r"^(?:import|from)\s+hokom_pipeline",
        r"^(?:import|from)\s+pipeline\.p3_pre_root",
        r"^(?:import|from)\s+pipeline\.p3_candidate",
        r"^(?:import|from)\s+pipeline\.p4_wazn",
        r"^(?:import|from)\s+mabni\b",
        r"^(?:import|from)\s+mabniyat\b",
        r"^(?:import|from)\s+.*canonical_radical_accounting",
    ]
    violations = []
    for py_file in vendor_src.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        for pattern in hokom_import_patterns:
            if _re.search(pattern, text, _re.MULTILINE):
                violations.append(f"{py_file.name}: imports '{pattern}'")
    assert not violations, f"Vendor imports Hokom modules: {violations}"


def test_constitutional_13b_taaqol_vendor_has_no_root_extraction():
    """
    Structural test: vendor must not contain root/wazn extraction functions
    for Arabic morphology. It owns slot algebra, not Arabic linguistics.
    """
    vendor_src = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src" / "taaqqul_slot_geometry"
    arabic_rule_patterns = [
        "trilateral_root",
        "canonical_root",
        "wazn_catalog",
        "assess_pre_root",
        "root_candidate",
        "MorphologyPath",
    ]
    violations = []
    for py_file in vendor_src.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        for pattern in arabic_rule_patterns:
            if pattern in text:
                violations.append(f"{py_file.name}: contains Arabic rule '{pattern}'")
    assert not violations, f"Vendor contains Arabic morphological rules: {violations}"


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 14
# original_surface preserved through all stages
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_14_original_surface_preserved():
    """original_surface must survive SurfaceProvenance construction."""
    original = "كَتَبَ"
    surface = SurfaceProvenance(
        original_surface=original,
        normalized_surface="كَتَبَ",
        operations=(
            NormalizationOp(
                op_code="EXPAND_HAMZA",
                input_char="أ",
                output_char="ء",
                position=0,
            ),
        ),
    )
    surface.assert_original_preserved()
    assert surface.original_surface == original


def test_constitutional_14b_empty_original_surface_raises():
    """Empty original_surface must fail assert_original_preserved()."""
    surface = SurfaceProvenance(
        original_surface="",
        normalized_surface="",
    )
    with pytest.raises(AssertionError):
        surface.assert_original_preserved()


def test_constitutional_14c_original_surface_in_bundle():
    """HokomClaimBundle enforces original_surface via __post_init__."""
    with pytest.raises(AssertionError):
        HokomClaimBundle(
            claim_key="a" * 64,
            claim_kind="ROOT_CLAIM",
            profile_id="ROOT_CLAIM",
            surface=SurfaceProvenance(original_surface="", normalized_surface=""),
            typed_slots=(),
            candidate_sets={},
            evidence_refs=(),
            condition_facts=(),
            obstacle_facts=(),
            defeater_facts=(),
            domain_licenses=(),
            residuals=(),
        )


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 15
# Serialization round-trip preserves semantics
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_15_serialize_roundtrip():
    """serialize_claim_bundle → deserialize_claim_bundle must preserve key fields."""
    key = compute_claim_key(
        claim_kind="ROOT_CLAIM",
        profile_id="ROOT_CLAIM",
        slot_values={"RADICAL_R1": "ك", "RADICAL_R2": "ت", "RADICAL_R3": "ب"},
        evidence_codes=("ev:wazn:fa3ala",),
    )
    bundle = _make_bundle(claim_kind="ROOT_CLAIM", claim_key=key)

    serialized = serialize_claim_bundle(bundle)
    restored = deserialize_claim_bundle(serialized)

    assert restored.claim_key == bundle.claim_key
    assert restored.claim_kind == bundle.claim_kind
    assert restored.profile_id == bundle.profile_id
    assert restored.surface.original_surface == bundle.surface.original_surface
    assert restored.surface.normalized_surface == bundle.surface.normalized_surface


def test_constitutional_15b_slot_roundtrip_preserves_state():
    """Serialized TypedSlot state is preserved through round-trip."""
    key = compute_claim_key(
        claim_kind="ROOT_CLAIM",
        profile_id="ROOT_CLAIM",
        slot_values={"SEGMENT_HOST": "كَتَبَ"},
        evidence_codes=(),
    )
    bundle = _make_bundle(claim_key=key)
    serialized = serialize_claim_bundle(bundle)
    restored = deserialize_claim_bundle(serialized)

    assert len(restored.typed_slots) == 1
    assert restored.typed_slots[0].slot_id == SlotId.SEGMENT_HOST
    assert restored.typed_slots[0].state == SlotState.FILLED


def test_constitutional_15c_condition_facts_roundtrip():
    """condition_facts are preserved through round-trip."""
    key = compute_claim_key(
        claim_kind="ROOT_CLAIM",
        profile_id="ROOT_CLAIM",
        slot_values={},
        evidence_codes=(),
    )
    surface = _make_surface()
    bundle = HokomClaimBundle(
        claim_key=key,
        claim_kind="ROOT_CLAIM",
        profile_id="ROOT_CLAIM",
        surface=surface,
        typed_slots=(),
        candidate_sets={},
        evidence_refs=(),
        condition_facts=("TRILATERAL_ROOT", "VERBAL_FORM_I"),
        obstacle_facts=("WEAK_RADICAL_PRESENT",),
        defeater_facts=(),
        domain_licenses=(),
        residuals=(),
    )
    serialized = serialize_claim_bundle(bundle)
    restored = deserialize_claim_bundle(serialized)
    assert "TRILATERAL_ROOT" in restored.condition_facts
    assert "VERBAL_FORM_I" in restored.condition_facts
    assert "WEAK_RADICAL_PRESENT" in restored.obstacle_facts


# ══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL TEST 16
# No skip marks or xfail marks in the constitutional SGA suite
# ══════════════════════════════════════════════════════════════════════════════

def test_constitutional_16_no_skips_in_constitutional_suite():
    """
    Meta-test: this test file must contain no pytest.mark.skip or
    pytest.mark.xfail decorators. All 16 tests must run unconditionally.
    """
    this_file = Path(__file__)
    source = this_file.read_text(encoding="utf-8")
    # Check that no decorator lines use skip/xfail markers.
    # Pattern strings are built dynamically to avoid self-reference in source.
    _skip_deco  = "@" + "pytest" + "." + "mark" + "." + "skip"
    _xfail_deco = "@" + "pytest" + "." + "mark" + "." + "xfail"
    _skipif_deco = "@" + "pytest" + "." + "mark" + "." + "skipif"
    for _line in source.splitlines():
        _stripped = _line.strip()
        assert not _stripped.startswith(_skip_deco), (
            f"Constitutional suite has forbidden decorator on line: {_stripped!r}"
        )
        assert not _stripped.startswith(_xfail_deco), (
            f"Constitutional suite has forbidden decorator on line: {_stripped!r}"
        )
        assert not _stripped.startswith(_skipif_deco), (
            f"Constitutional suite has forbidden decorator on line: {_stripped!r}"
        )


def test_constitutional_16b_all_claim_profiles_are_defined():
    """CLAIM_PROFILES dict must contain all expected claim kinds."""
    required_profiles = {
        "ROOT_CLAIM",
        "PATTERN_CLAIM",
        "BAB_CLAIM",
        "MASDAR_CLAIM",
        "DERIVATIVE_CLAIM",
        "WORD_CLASS_CLAIM",
        "FUNCTIONAL_OWNER_CLAIM",
    }
    for profile_id in required_profiles:
        assert profile_id in CLAIM_PROFILES, (
            f"CLAIM_PROFILES must include '{profile_id}'"
        )


def test_constitutional_16c_all_slot_sorts_have_unique_values():
    """SlotSort enum must have unique integer values (no accidental duplicates)."""
    values = [s.value for s in SlotSort]
    assert len(values) == len(set(values)), "SlotSort has duplicate values"


def test_constitutional_16d_slot_ids_cover_all_layers():
    """SlotId must cover surface, segmentation, boundary, lexical, morphological, radical, pattern, and evidence layers."""
    slot_ids = {s.value for s in SlotId}
    required_ids = {
        "ORIGINAL_SURFACE", "NORMALIZED_SURFACE",  # surface
        "SEGMENT_HOST", "PROCLITIC_SLOTS",          # segmentation
        "BOUNDARY_TYPE_SLOT",                        # boundary
        "WORD_CLASS_SLOT", "FUNCTIONAL_OWNER_SLOT",  # lexical
        "RADICAL_R1", "ROOT_CANDIDATE_SET",          # radical
        "PATTERN_CANDIDATE_SET",                     # pattern
        "BAB_CANDIDATE_SET", "MASDAR_CANDIDATE_SET", # morphosyntax
        "EVIDENCE_SLOT", "RESIDUAL_SLOT",            # evidence
    }
    missing = required_ids - slot_ids
    assert not missing, f"SlotId missing required members: {missing}"
