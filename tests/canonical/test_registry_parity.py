"""
tests/canonical/test_registry_parity.py — Saleh registry snapshot parity tests.

These tests verify the canonical 19-stage registry snapshot against invariants
derived from Saleh/Qiyas master_registry_seed.py.

The snapshot JSON must be generated before running these tests:
    cd hokom
    PYTHONPATH=src:vendor/Taaqol-GPT/src:../fractal/algebra/Saleh-/src \\
        python scripts/generate_canonical_registry_snapshot.py

Tests:
    01 — Snapshot loads without error
    02 — Exactly 19 layers in snapshot
    03 — All 19 layer IDs match CANONICAL_LAYER_IDS
    04 — All layers have status="implemented"
    05 — P12 is terminal (is_terminal=True, target_boundary_opens=[])
    06 — No P13 in canonical_order
    07 — assert_no_p13() passes without error
    08 — P12 forbidden_outputs include HukmCandidate, RealityClaim, FinalMeaning
    09 — Layers in canonical ordinal order match CANONICAL_LAYER_IDS
    10 — Provenance record has non-empty saleh_commit_sha and registry_digest
    11 — P0_UNICODE_CANDIDATE has origin_layer_id="ROOT"
    12 — P1 phase is "SCG-P1" for all 5 P1 layers
    13 — Each layer has at least one condition
    14 — Terminal layer next_layer (if registered) is absent — no target_boundary_opens
    15 — Snapshot is_terminal flag matches target_boundary_opens==[]
"""
import pytest

try:
    from hokom.canonical.registry import (
        load_snapshot,
        get_layer,
        canonical_order,
        terminal_layer_id,
        assert_no_p13,
        CANONICAL_LAYER_IDS,
    )
    from hokom.canonical.registry.saleh_snapshot import RegistrySnapshotMissing
    _SNAPSHOT_AVAILABLE = True
except Exception:
    _SNAPSHOT_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _SNAPSHOT_AVAILABLE,
    reason="hokom.canonical.registry not importable"
)


@pytest.fixture(scope="module")
def snapshot():
    try:
        return load_snapshot()
    except Exception as exc:
        pytest.skip(f"Registry snapshot not available: {exc}")


def test_01_snapshot_loads(snapshot):
    assert snapshot is not None


def test_02_exactly_19_layers(snapshot):
    assert snapshot.layer_count == 19
    assert len(list(snapshot.layers_in_order())) == 19


def test_03_layer_ids_match_canonical(snapshot):
    ids = [l.id for l in snapshot.layers_in_order()]
    assert ids == list(CANONICAL_LAYER_IDS)


def test_04_all_layers_implemented(snapshot):
    non_impl = [l.id for l in snapshot.layers_in_order() if l.status != "implemented"]
    assert non_impl == [], f"Non-implemented layers: {non_impl}"


def test_05_p12_is_terminal(snapshot):
    p12 = snapshot.get_layer("P12_IFADAH_SPEECH_FORCE")
    assert p12.is_terminal is True
    assert p12.target_boundary_opens == ()


def test_06_no_p13_in_canonical_order(snapshot):
    for lid in snapshot.canonical_order:
        assert not lid.startswith("P13"), f"P13 found in canonical_order: {lid}"


def test_07_assert_no_p13_passes(snapshot):
    snapshot.assert_no_p13()  # must not raise


def test_08_p12_forbidden_outputs(snapshot):
    p12 = snapshot.get_layer("P12_IFADAH_SPEECH_FORCE")
    forbidden = set(p12.forbidden_outputs)
    assert "HukmCandidate" in forbidden
    assert "RealityClaim" in forbidden
    assert "FinalMeaning" in forbidden


def test_09_layers_in_canonical_ordinal_order(snapshot):
    layers = list(snapshot.layers_in_order())
    for i, layer in enumerate(layers):
        assert layer.ordinal == i, (
            f"Layer {layer.id} has ordinal {layer.ordinal}, expected {i}"
        )
        assert layer.id == CANONICAL_LAYER_IDS[i], (
            f"At ordinal {i}: expected {CANONICAL_LAYER_IDS[i]}, got {layer.id}"
        )


def test_10_provenance_non_empty(snapshot):
    prov = snapshot.provenance
    assert prov.saleh_commit_sha, "saleh_commit_sha must be non-empty"
    assert prov.registry_digest, "registry_digest must be non-empty"
    assert prov.generation_function == "build_p12_implemented_registry"


def test_11_p0_unicode_origin_is_root(snapshot):
    p0 = snapshot.get_layer("P0_UNICODE_CANDIDATE")
    assert p0.origin_layer_id == "ROOT"


def test_12_p1_layers_phase_scg_p1(snapshot):
    p1_ids = [
        "P1_LETTER_IDENTITY_CARRIER",
        "P1_HARAKA_MARK_IDENTITY_CARRIER",
        "P1_CONDITIONED_TYPED_SEQUENCE",
        "P1_POSITION_CARRIER",
        "P1_SLOT_CANDIDATE",
    ]
    for lid in p1_ids:
        layer = snapshot.get_layer(lid)
        assert layer.phase == "SCG-P1", (
            f"Layer {lid} phase expected 'SCG-P1', got '{layer.phase}'"
        )


def test_13_each_layer_has_at_least_one_condition(snapshot):
    for layer in snapshot.layers_in_order():
        assert len(layer.conditions) >= 1, (
            f"Layer {layer.id} has no conditions"
        )


def test_14_p12_target_boundary_opens_empty(snapshot):
    p12 = snapshot.get_layer("P12_IFADAH_SPEECH_FORCE")
    assert p12.target_boundary_opens == ()


def test_15_is_terminal_matches_target_boundary_opens(snapshot):
    for layer in snapshot.layers_in_order():
        if layer.target_boundary_opens == ():
            assert layer.is_terminal is True, (
                f"Layer {layer.id} has target_boundary_opens==() "
                "but is_terminal is False"
            )
        else:
            assert layer.is_terminal is False, (
                f"Layer {layer.id} has target_boundary_opens={layer.target_boundary_opens} "
                "but is_terminal is True"
            )
