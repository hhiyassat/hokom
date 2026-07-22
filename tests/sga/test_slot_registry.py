"""
Tests that enforce the 47-slot public contract.
HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01 — HARDEN-02
"""
from pipeline.sga.slot_registry import SLOT_REGISTRY, validate_registry, SlotContract
from pipeline.sga.contracts import SlotId, SlotSort


def test_registry_covers_all_slots():
    """Every SlotId must have a contract entry."""
    missing = [s for s in SlotId if s not in SLOT_REGISTRY]
    assert missing == [], f"Unregistered slots: {missing}"


def test_no_extra_registry_entries():
    """Registry must not contain unknown SlotIds."""
    extra = [k for k in SLOT_REGISTRY if k not in set(SlotId)]
    assert extra == [], f"Extra registry entries: {extra}"


def test_serialized_id_stability():
    """Serialized IDs must match SlotId values."""
    violations = [
        (c.slot_id, c.serialized_id)
        for c in SLOT_REGISTRY.values()
        if c.serialized_id != c.slot_id.value
    ]
    assert violations == [], f"Serialized ID mismatches: {violations}"


def test_no_duplicate_serialized_ids():
    """No two slots may share a serialized ID."""
    seen: dict[str, SlotId] = {}
    for slot_id, contract in SLOT_REGISTRY.items():
        assert contract.serialized_id not in seen, \
            f"Duplicate serialized_id: {contract.serialized_id} (slots: {seen[contract.serialized_id]}, {slot_id})"
        seen[contract.serialized_id] = slot_id


def test_registry_validates_clean():
    """validate_registry() must return empty list."""
    violations = validate_registry()
    assert violations == [], f"Registry violations: {violations}"


def test_slot_count():
    """Exactly 47 slots."""
    assert len(SlotId) == 47
    assert len(SLOT_REGISTRY) == 47


def test_original_surface_not_nullable():
    contract = SLOT_REGISTRY[SlotId.ORIGINAL_SURFACE]
    assert not contract.nullable
    assert not contract.absence_legal
    assert contract.provenance_required
    assert contract.participates_in_claim_key


def test_segment_host_participates_in_eval_identity():
    contract = SLOT_REGISTRY[SlotId.SEGMENT_HOST]
    assert contract.participates_in_eval_identity
    assert contract.participates_in_claim_key


def test_path_directive_always_required():
    contract = SLOT_REGISTRY[SlotId.PATH_DIRECTIVE_SLOT]
    assert not contract.nullable
    assert not contract.absence_legal
    assert contract.participates_in_claim_key
    assert contract.participates_in_eval_identity


def test_ambiguous_capable_slots_have_multi_valued():
    for slot_id, contract in SLOT_REGISTRY.items():
        if contract.ambiguity_legal:
            assert contract.multi_valued_legal, \
                f"Slot {slot_id} is ambiguity_legal but not multi_valued_legal"


def test_required_slots_not_absence_legal():
    """REQUIRED classification must not have absence_legal=True (unless RESERVED)."""
    for slot_id, contract in SLOT_REGISTRY.items():
        if contract.classification == "REQUIRED" and contract.stability != "RESERVED":
            assert not contract.absence_legal, \
                f"REQUIRED slot {slot_id} has absence_legal=True"


def test_stability_values():
    valid = {"STABLE", "PROVISIONAL", "RESERVED", "DEPRECATED"}
    for slot_id, contract in SLOT_REGISTRY.items():
        assert contract.stability in valid, \
            f"Slot {slot_id} has unknown stability: {contract.stability!r}"


def test_classification_values():
    valid = {
        "REQUIRED", "OPTIONAL", "CONDITIONAL",
        "MULTI_VALUED", "AMBIGUOUS_CAPABLE", "PROVENANCE_REQUIRED", "RESERVED",
    }
    for slot_id, contract in SLOT_REGISTRY.items():
        assert contract.classification in valid, \
            f"Slot {slot_id} has unknown classification: {contract.classification!r}"


def test_cardinality_values():
    for slot_id, contract in SLOT_REGISTRY.items():
        assert contract.cardinality in ("SINGLE", "MULTI"), \
            f"Slot {slot_id} has unknown cardinality: {contract.cardinality!r}"


def test_root_candidate_set_ambiguity_capable():
    contract = SLOT_REGISTRY[SlotId.ROOT_CANDIDATE_SET]
    assert contract.ambiguity_legal
    assert contract.multi_valued_legal


def test_bab_masdar_derivative_ambiguity_capable():
    for slot_id in (SlotId.BAB_CANDIDATE_SET, SlotId.MASDAR_CANDIDATE_SET, SlotId.DERIVATIVE_CANDIDATE_SET):
        contract = SLOT_REGISTRY[slot_id]
        assert contract.ambiguity_legal, f"{slot_id} should be ambiguity_legal"
        assert contract.multi_valued_legal, f"{slot_id} should be multi_valued_legal"


def test_closed_boundary_slots_not_in_claim_key():
    """EVIDENCE_SLOT and RESIDUAL_SLOT should not participate in claim_key."""
    for slot_id in (SlotId.EVIDENCE_SLOT, SlotId.RESIDUAL_SLOT):
        contract = SLOT_REGISTRY[slot_id]
        assert not contract.participates_in_claim_key, \
            f"Aggregate slot {slot_id} should not participate in claim_key"


def test_stage_values_nonempty():
    """Every slot must have a non-empty stage."""
    for slot_id, contract in SLOT_REGISTRY.items():
        assert contract.stage, f"Slot {slot_id} has empty stage"


def test_valid_producers_nonempty():
    """Every slot must have at least one valid producer."""
    for slot_id, contract in SLOT_REGISTRY.items():
        assert len(contract.valid_producers) > 0, \
            f"Slot {slot_id} has no valid producers"


def test_h11_to_h15_slots_evidence_required():
    """BAB, MASDAR, DERIVATIVE candidate sets are evidence-required."""
    for slot_id in (SlotId.BAB_CANDIDATE_SET, SlotId.MASDAR_CANDIDATE_SET, SlotId.DERIVATIVE_CANDIDATE_SET):
        contract = SLOT_REGISTRY[slot_id]
        assert contract.evidence_required, f"{slot_id} should require evidence"


def test_provenance_required_slots():
    """ORIGINAL_SURFACE and NORMALIZED_SURFACE require provenance."""
    for slot_id in (SlotId.ORIGINAL_SURFACE, SlotId.NORMALIZED_SURFACE):
        contract = SLOT_REGISTRY[slot_id]
        assert contract.provenance_required, f"{slot_id} should require provenance"


def test_slot_contracts_are_frozen():
    """SlotContracts are frozen dataclasses — immutable."""
    import pytest
    contract = SLOT_REGISTRY[SlotId.ORIGINAL_SURFACE]
    with pytest.raises((AttributeError, TypeError)):
        contract.nullable = True  # type: ignore[misc]


def test_registry_key_order_stable():
    """Registry key order is deterministic across imports."""
    keys1 = list(SLOT_REGISTRY.keys())
    import importlib
    import pipeline.sga.slot_registry as reg
    importlib.reload(reg)
    keys2 = list(reg.SLOT_REGISTRY.keys())
    assert keys1 == keys2, "Registry key order is nondeterministic"
