"""
Stability and determinism tests.
HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01 — HARDEN-11
"""
import uuid
import importlib


def test_claim_key_stable_across_runs():
    """Same inputs must produce the same claim_key across 10 evaluations."""
    from pipeline.sga.adapters import build_claim_bundle

    result = {
        "word": "كَتَبَ",
        "segment_host": "كَتَبَ",
        "root_candidate": "ك-ت-ب",
        "word_class": "VERB",
    }
    keys = [
        build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM").claim_key
        for _ in range(10)
    ]
    assert len(set(keys)) == 1, f"claim_key not stable across runs: {set(keys)}"


def test_claim_key_stable_for_hollow_root():
    from pipeline.sga.adapters import build_claim_bundle

    result = {"word": "قَالَ", "segment_host": "قَالَ", "root_candidate": "ق-و-ل"}
    keys = [
        build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM").claim_key
        for _ in range(10)
    ]
    assert len(set(keys)) == 1, f"Hollow root claim_key not stable: {set(keys)}"


def test_claim_key_stable_for_functional_token():
    from pipeline.sga.adapters import build_claim_bundle

    result = {"word": "مَنْ", "segment_host": "مَنْ", "word_class": "MABNI"}
    keys = [
        build_claim_bundle(result, "FUNCTIONAL_OWNER_CLAIM", "FUNCTIONAL_OWNER_CLAIM").claim_key
        for _ in range(10)
    ]
    assert len(set(keys)) == 1, f"Functional token claim_key not stable: {set(keys)}"


def test_evaluation_ids_unique():
    """UUID4 evaluation IDs must be unique across 200 generations."""
    ids = [str(uuid.uuid4()) for _ in range(200)]
    assert len(set(ids)) == 200, "evaluation_id collision detected"


def test_candidate_ordering_stable():
    """Multiple root candidates must be preserved in consistent order."""
    from pipeline.sga.adapters import build_claim_bundle
    from pipeline.sga.contracts import SlotId

    result = {
        "word": "وَجَدَ",
        "segment_host": "وَجَدَ",
        "root_candidate": ["و-ج-د", "ج-ي-د"],
    }
    orderings = []
    for _ in range(5):
        b = build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM")
        cset = b.candidate_sets.get(SlotId.ROOT_CANDIDATE_SET.value)
        if cset and cset.candidates:
            orderings.append(tuple(c.value for c in cset.candidates))

    if orderings:
        assert len(set(orderings)) == 1, \
            f"Candidate ordering is unstable: {set(orderings)}"


def test_no_cross_evaluation_contamination():
    """Two different tokens must produce different claim_keys, and b1 is not mutated by b2."""
    from pipeline.sga.adapters import build_claim_bundle

    r1 = {"word": "كَتَبَ", "segment_host": "كَتَبَ"}
    r2 = {"word": "قَالَ", "segment_host": "قَالَ"}

    b1 = build_claim_bundle(r1, "ROOT_CLAIM", "ROOT_CLAIM")
    b2 = build_claim_bundle(r2, "ROOT_CLAIM", "ROOT_CLAIM")

    # Different words must give different claim_keys
    assert b1.claim_key != b2.claim_key, \
        "Different words must produce different claim_keys"

    # b1 must not be mutated by b2 creation
    b1_again = build_claim_bundle(r1, "ROOT_CLAIM", "ROOT_CLAIM")
    assert b1.claim_key == b1_again.claim_key, \
        "b1 claim_key was mutated by b2 construction"


def test_surface_provenance_not_shared():
    """Surface provenance objects must not be shared across independent bundles."""
    from pipeline.sga.adapters import build_claim_bundle

    b1 = build_claim_bundle({"word": "كَتَبَ", "segment_host": "كَتَبَ"}, "ROOT_CLAIM", "ROOT_CLAIM")
    b2 = build_claim_bundle({"word": "قَالَ", "segment_host": "قَالَ"}, "ROOT_CLAIM", "ROOT_CLAIM")

    assert b1.surface.original_surface != b2.surface.original_surface, \
        "Surface provenance objects must not be shared"
    assert b1.surface is not b2.surface, \
        "Surface provenance objects must not be the same instance"


def test_registry_loading_deterministic():
    """SLOT_REGISTRY key order is deterministic across reloads."""
    from pipeline.sga.slot_registry import SLOT_REGISTRY
    keys1 = list(SLOT_REGISTRY.keys())

    import pipeline.sga.slot_registry as reg
    importlib.reload(reg)
    keys2 = list(reg.SLOT_REGISTRY.keys())

    assert keys1 == keys2, "SLOT_REGISTRY key order is nondeterministic after reload"


def test_profile_versions_loading_deterministic():
    """CLAIM_PROFILE_VERSIONS key order is deterministic across reloads."""
    from pipeline.sga.contracts import CLAIM_PROFILE_VERSIONS
    keys1 = list(CLAIM_PROFILE_VERSIONS.keys())

    import pipeline.sga.contracts as contracts
    importlib.reload(contracts)
    keys2 = list(contracts.CLAIM_PROFILE_VERSIONS.keys())

    assert keys1 == keys2, "CLAIM_PROFILE_VERSIONS key order is nondeterministic after reload"


def test_license_registry_loading_deterministic():
    """DOMAIN_LICENSE_VERSIONS key order is deterministic across reloads."""
    from pipeline.sga.license_registry import DOMAIN_LICENSE_VERSIONS
    keys1 = list(DOMAIN_LICENSE_VERSIONS.keys())

    import pipeline.sga.license_registry as lr
    importlib.reload(lr)
    keys2 = list(lr.DOMAIN_LICENSE_VERSIONS.keys())

    assert keys1 == keys2, "DOMAIN_LICENSE_VERSIONS key order is nondeterministic after reload"


def test_ambiguous_bundle_claim_key_stable():
    """Bundles with ambiguous roots must also have stable claim_keys."""
    from pipeline.sga.adapters import build_claim_bundle

    result = {
        "word": "وَجَدَ",
        "segment_host": "وَجَدَ",
        "root_candidate": ["و-ج-د", "ج-ي-د"],
    }
    keys = [
        build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM").claim_key
        for _ in range(5)
    ]
    assert len(set(keys)) == 1, \
        f"Ambiguous bundle claim_key is not stable: {set(keys)}"


def test_serialized_id_stable():
    """SlotId.value must not change between module loads."""
    from pipeline.sga.contracts import SlotId
    values1 = {s: s.value for s in SlotId}

    import pipeline.sga.contracts as contracts
    importlib.reload(contracts)
    values2 = {s: s.value for s in contracts.SlotId}

    assert values1 == values2, "SlotId.value changed after module reload"


def test_claim_key_different_profile_different_key():
    """Same word with different profile_id must produce different claim_keys."""
    from pipeline.sga.adapters import build_claim_bundle

    result = {"word": "كَتَبَ", "segment_host": "كَتَبَ", "word_class": "VERB"}
    b_root = build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM")
    b_wc   = build_claim_bundle(result, "WORD_CLASS_CLAIM", "WORD_CLASS_CLAIM")

    assert b_root.claim_key != b_wc.claim_key, \
        "Different profile_ids must produce different claim_keys for the same word"
