"""C13 first-production-wave — native RelationCandidate law verification.

Proves that the original vendor Taaqol RelationCandidate law is
runtime-callable at target SHA 05c6668d, producing a real
vendor RelationVerdict with a nested vendor RelationCandidate whose
governor and dependent fields are real vendor ContractableUnitGeometry
instances.

Non-gold fixture: uses ordinary Arabic surfaces (كَتَبَ + زَيْدٌ),
NOT any Ayat al-Dayn token. This proves LAW_RUNTIME_VERIFIED without
claiming AYAT_RUNTIME_EXECUTED.
"""
from __future__ import annotations

import pytest


def test_native_relation_candidate_law_runtime_verified():
    """The original vendor prove_relation_candidate returns a COMPOSED verdict
    with real vendor ContractableUnitGeometry governor + dependent objects."""
    from pipeline.taaqol_integration.weight_layer.relation_candidate_adapter import (
        build_e8_relation_from_surfaces,
    )

    verdict = build_e8_relation_from_surfaces(
        gov_token_surface="كَتَبَ",
        gov_root_letters="كتب",
        gov_segment_host="كتب",
        gov_word_class="FI3L",
        gov_trace_id="c13_test_governor_ktb",
        dep_token_surface="زَيْدٌ",
        dep_root_letters="زيد",
        dep_segment_host="زيد",
        dep_word_class="ISM",
        dep_trace_id="c13_test_dependent_zayd",
        governor_role_claim="FIL_MUTLI",
        dependent_role_claim="MAFOOL_BIH",
        relation_basis="C13 §9 first-wave non-gold structural fixture",
    )

    # Native law executed and returned a real vendor RelationVerdict
    assert verdict is not None, "vendor prove_relation_candidate returned None"
    assert type(verdict).__name__ == "RelationVerdict", (
        f"expected vendor RelationVerdict, got {type(verdict).__name__}"
    )

    # Verdict is COMPOSED (success state)
    from taaqqul_slot_geometry.weight.relation_candidate import RelationState
    assert verdict.verdict_state == RelationState.COMPOSED, (
        f"expected COMPOSED, got {verdict.verdict_state}"
    )
    assert verdict.failure_code is None

    # The candidate is a real vendor RelationCandidate
    assert type(verdict.candidate).__name__ == "RelationCandidate", (
        f"expected vendor RelationCandidate, got {type(verdict.candidate).__name__}"
    )


def test_native_relation_candidate_carries_real_vendor_contractable_units():
    """The RelationCandidate.governor and .dependent must be real vendor
    ContractableUnitGeometry instances — proof that the vendor CU law
    executed and the objects are retained through the composition."""
    from pipeline.taaqol_integration.weight_layer.relation_candidate_adapter import (
        build_e8_relation_from_surfaces,
    )
    from taaqqul_slot_geometry.weight.contractable_unit_geometry import (
        ContractableUnitGeometry,
    )

    verdict = build_e8_relation_from_surfaces(
        gov_token_surface="كَتَبَ",
        gov_root_letters="كتب",
        gov_segment_host="كتب",
        gov_word_class="FI3L",
        gov_trace_id="c13_cu_retention_test_gov",
        dep_token_surface="زَيْدٌ",
        dep_root_letters="زيد",
        dep_segment_host="زيد",
        dep_word_class="ISM",
        dep_trace_id="c13_cu_retention_test_dep",
        governor_role_claim="FIL_MUTLI",
        dependent_role_claim="MAFOOL_BIH",
        relation_basis="C13 CU retention proof",
    )
    assert verdict is not None
    cand = verdict.candidate
    assert isinstance(cand.governor, ContractableUnitGeometry)
    assert isinstance(cand.dependent, ContractableUnitGeometry)
    # Real vendor objects: they have unit_identity and contractability_profile
    assert cand.governor.unit_identity == "كَتَبَ"
    assert cand.dependent.unit_identity == "زَيْدٌ"
    assert cand.governor.contractability_profile.word_class_affordance == "FI3L"
    assert cand.dependent.contractability_profile.word_class_affordance == "ISM"


def test_native_relation_candidate_refuses_invalid_role():
    """Vendor law must refuse an inadmissible role claim — proof that it
    actually gates instead of always returning success."""
    from pipeline.taaqol_integration.weight_layer.relation_candidate_adapter import (
        build_e8_relation_from_surfaces,
    )
    verdict = build_e8_relation_from_surfaces(
        gov_token_surface="كَتَبَ",
        gov_root_letters="كتب",
        gov_segment_host="كتب",
        gov_word_class="FI3L",
        gov_trace_id="c13_role_reject_gov",
        dep_token_surface="زَيْدٌ",
        dep_root_letters="زيد",
        dep_segment_host="زيد",
        dep_word_class="ISM",
        dep_trace_id="c13_role_reject_dep",
        governor_role_claim="INVALID_ROLE_XYZ",  # not in contractability_profile
        dependent_role_claim="ALSO_INVALID",
        relation_basis="C13 invalid-role rejection test",
    )
    # Adapter fails-closed to None for inadmissible roles
    assert verdict is None, (
        "build_e8_relation_from_surfaces must return None for inadmissible roles; "
        f"got {verdict}"
    )


def test_native_relation_candidate_source_path_under_vendor():
    """Verify the invoked callable is genuinely under vendor/Taaqol-GPT/."""
    import inspect
    from taaqqul_slot_geometry.weight.relation_candidate import prove_relation_candidate
    src = inspect.getfile(prove_relation_candidate)
    assert "vendor/Taaqol-GPT" in src, (
        f"native symbol outside vendor: {src}"
    )
