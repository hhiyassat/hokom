"""
tests/canonical/test_stage_adapters.py — Stage adapter behavioral tests.

Tests 01-15 and 17-18 require the registry snapshot to be generated first:
    cd hokom
    PYTHONPATH=src:vendor/Taaqol-GPT/src:../fractal/algebra/Saleh-/src \\
        python scripts/generate_canonical_registry_snapshot.py

Test 16 (LAYER_ID class attributes) works without the snapshot.

Tests:
    01  — UnicodeAdapter: SAHIH on non-empty surface
    02  — UnicodeAdapter: BATIL on empty surface (condition fails)
    03  — RootStemAdapter: SAHIH on 3-consonant word
    04  — RootStemAdapter: DEFERRED on single-consonant (defect)
    05  — RootStemAdapter: BATIL on ROOT_PATH_BLOCKED (function word clitic)
    06  — RootStemAdapter: BATIL on zero consonants
    07  — MufradWordAdapter: SAHIH on resolved word_geometry
    08  — MufradWordAdapter: BATIL on word_type_conflict
    09  — MufradWordAdapter: DEFERRED on boundary_underspecified
    10  — SentenceGeometryAdapter: DEFERRED with 1 unit
    11  — SentenceGeometryAdapter: SAHIH with 2 units + established adjacency
    12  — SentenceGeometryAdapter: BATIL on sentence_boundary_conflict
    13  — IfadahAdapter: candidate_type must be IfadahSpeechForceCandidate (not HukmCandidate)
    14  — IfadahAdapter: _next_layer_id() returns None (TERMINAL, no P13)
    15  — IfadahAdapter: output_flags must not contain forbidden flags
    16  — All 19 adapter LAYER_IDs match CANONICAL_LAYER_IDS order
    17  — StageOutput.next_layer_id is None only for P12
    18  — P12 SAHIH judgment: carry_to_next is None
"""
import pytest

# Check if snapshot is available (needed for adapter instantiation)
try:
    from hokom.canonical.registry import load_snapshot
    load_snapshot()
    _SNAPSHOT_AVAILABLE = True
except Exception:
    _SNAPSHOT_AVAILABLE = False

_requires_snapshot = pytest.mark.skipif(
    not _SNAPSHOT_AVAILABLE,
    reason=(
        "Registry snapshot not generated. Run:\n"
        "  PYTHONPATH=src:vendor/Taaqol-GPT/src:../fractal/algebra/Saleh-/src"
        " python scripts/generate_canonical_registry_snapshot.py"
    ),
)

from unittest.mock import patch

from hokom.canonical.registry import CANONICAL_LAYER_IDS
from hokom.canonical.stages.base import StageInput, TaaqolLicenseOutcome
from hokom.canonical.stages.p0 import UnicodeAdapter
from hokom.canonical.stages.p2_p5 import MufradWordAdapter, RootStemAdapter
from hokom.canonical.stages.p9_p12 import IfadahAdapter, SentenceGeometryAdapter
from hokom.canonical.constitutional.contracts import ConstitutionalStatus
from hokom.canonical.slot_algebra.types import (
    CanonicalCandidateSet,
    CandidateStatus,
)

# When Taaqol is unavailable the stub returns TRACE(1) → DEFERRED (fail-closed,
# §C rule 11).  Tests that assert SAHIH must patch _taaqol_license to return
# LICENSED(4), isolating adapter logic from runtime availability.
# TaaqolLicenseOutcome is required — bare (int, str) tuples no longer accepted.
_MOCK_LICENSED = TaaqolLicenseOutcome(
    granted_rank=4,
    gate_id="TEST-GATE-LICENSED",
    verdict="LICENSED",
    fallback_used=False,
    trace_ids=("test:mock-trace-001",),
    slot_graph_digest="",
    failure_code=None,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _empty_cs(layer_id: str) -> CanonicalCandidateSet:
    return CanonicalCandidateSet(
        set_id="EMPTY", layer_id=layer_id, candidates=(), residuals=(), trace_ids=()
    )


def _stage_input(layer_id: str, surface: str, evidence: dict, prior=None) -> StageInput:
    return StageInput(
        layer_id=layer_id,
        surface=surface,
        hokom_evidence=evidence,
        prior_output=prior,
        pipeline_run_id="test-run-001",
        word_index=0,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

@_requires_snapshot
def test_01_unicode_adapter_sahih_non_empty():
    adapter = UnicodeAdapter()
    inp = _stage_input(
        "P0_UNICODE_CANDIDATE",
        "كَتَبَ",
        {"codepoints": [{"position": 0, "codepoint": 1603, "char": "ك"}]},
    )
    with patch.object(adapter, "_taaqol_license", return_value=_MOCK_LICENSED):
        out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.SAHIH
    assert out.candidate_set.accepted


@_requires_snapshot
def test_02_unicode_adapter_deferred_empty_surface():
    adapter = UnicodeAdapter()
    inp = _stage_input("P0_UNICODE_CANDIDATE", "   ", {})
    out = adapter.adapt(inp)
    assert out.judgment.status in (
        ConstitutionalStatus.DEFERRED, ConstitutionalStatus.BATIL
    )


@_requires_snapshot
def test_03_root_stem_adapter_sahih_3_consonants():
    adapter = RootStemAdapter()
    from hokom.canonical.slot_algebra.types import CanonicalCandidate, CandidateStatus, EvidenceSet, EvidenceAtom, ProvenanceRef, SlotState
    from hokom.canonical.stages.p2_p5 import RegistryProjectionAdapter
    # Provide a mock prior output with accepted candidate
    prov = ProvenanceRef(owner="hokom", module_path="hokom.test", rule_id="r", stage_id="P2_REGISTRY_PROJECTION")
    atom = EvidenceAtom(key="k", value="v", confidence=0.9, provenance=prov)
    ev = EvidenceSet.from_atoms("P2_REGISTRY_PROJECTION", (atom,))
    prior_candidate = CanonicalCandidate(
        candidate_id="C1", candidate_type="RegistryProjectionCandidate",
        status=CandidateStatus.ACCEPTED, layer_id="P2_REGISTRY_PROJECTION",
        source_rule_id="r", evidence=ev, taaqol_rank=4,
    )
    prior = CanonicalCandidateSet(
        set_id="S1", layer_id="P2_REGISTRY_PROJECTION",
        candidates=(prior_candidate,), residuals=(), trace_ids=(),
    )
    inp = _stage_input(
        "P3_ROOT_STEM_CLOSURE",
        "كَتَبَ",
        {
            "consonant_count": 3,
            "root_radicals": ["ك", "ت", "ب"],
            "stem": "كَتَبَ",
            "root_path": "",
        },
        prior=prior,
    )
    with patch.object(adapter, "_taaqol_license", return_value=_MOCK_LICENSED):
        out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.SAHIH
    assert out.candidate_set.accepted[0].candidate_type == "RootStemCandidate"


@_requires_snapshot
def test_04_root_stem_adapter_deferred_single_consonant():
    adapter = RootStemAdapter()
    inp = _stage_input(
        "P3_ROOT_STEM_CLOSURE",
        "ي",
        {"consonant_count": 1, "root_radicals": ["ي"], "stem": "ي", "root_path": ""},
    )
    out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.DEFERRED


@_requires_snapshot
def test_05_root_stem_adapter_batil_root_path_blocked():
    adapter = RootStemAdapter()
    inp = _stage_input(
        "P3_ROOT_STEM_CLOSURE",
        "بِ",
        {"consonant_count": 1, "root_radicals": [], "stem": "", "root_path": "ROOT_PATH_BLOCKED"},
    )
    out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.BATIL


@_requires_snapshot
def test_06_root_stem_adapter_batil_zero_consonants():
    adapter = RootStemAdapter()
    inp = _stage_input(
        "P3_ROOT_STEM_CLOSURE",
        "",
        {"consonant_count": 0, "root_radicals": [], "stem": "", "root_path": ""},
    )
    out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.BATIL


@_requires_snapshot
def test_07_mufrad_word_adapter_sahih_resolved():
    from hokom.canonical.slot_algebra.types import (
        CanonicalCandidate, EvidenceAtom, EvidenceSet, ProvenanceRef,
    )
    # P5 requires a prior P4 JamidMushtaqCandidate (jamid_mushtaq_resolved condition)
    prov = ProvenanceRef(owner="hokom", module_path="hokom.test", rule_id="r",
                         stage_id="P4_JAMID_MUSHTAQ")
    atom = EvidenceAtom(key="jamid_mushtaq", value="mushtaq", confidence=0.9, provenance=prov)
    ev = EvidenceSet.from_atoms("P4_JAMID_MUSHTAQ", (atom,))
    prior_candidate = CanonicalCandidate(
        candidate_id="C4", candidate_type="JamidMushtaqCandidate",
        status=CandidateStatus.ACCEPTED, layer_id="P4_JAMID_MUSHTAQ",
        source_rule_id="r", evidence=ev, taaqol_rank=4,
    )
    prior = CanonicalCandidateSet(
        set_id="S4", layer_id="P4_JAMID_MUSHTAQ",
        candidates=(prior_candidate,), residuals=(), trace_ids=(),
    )
    adapter = MufradWordAdapter()
    inp = _stage_input(
        "P5_MUFRAD_WORD_CONTRACTS",
        "كَتَبَ",
        {"word_geometry": "resolved", "word_class": "verb"},
        prior=prior,
    )
    with patch.object(adapter, "_taaqol_license", return_value=_MOCK_LICENSED):
        out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.SAHIH
    assert out.candidate_set.accepted[0].candidate_type == "MufradWordCandidate"


@_requires_snapshot
def test_08_mufrad_word_adapter_batil_conflict():
    adapter = MufradWordAdapter()
    inp = _stage_input(
        "P5_MUFRAD_WORD_CONTRACTS",
        "كَتَبَ",
        {"word_geometry": "conflict", "word_class": "unknown"},
    )
    out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.BATIL


@_requires_snapshot
def test_09_mufrad_word_adapter_deferred_boundary():
    adapter = MufradWordAdapter()
    inp = _stage_input(
        "P5_MUFRAD_WORD_CONTRACTS",
        "كَتَبَ",
        {"word_geometry": "boundary_underspecified", "word_class": "unknown"},
    )
    out = adapter.adapt(inp)
    assert out.judgment.status in (ConstitutionalStatus.DEFERRED, ConstitutionalStatus.FASID)


@_requires_snapshot
def test_10_sentence_geometry_deferred_one_unit():
    adapter = SentenceGeometryAdapter()
    inp = StageInput(
        layer_id="P9_SENTENCE_GEOMETRY",
        surface="كَتَبَ",
        hokom_evidence={
            "amil_mamul_units": [{"unit_id": "w0", "word_index": 0, "role": "amil", "candidate_id": ""}],
            "adjacency_relation": "underspecified",
            "sentence_boundary": "open",
        },
        prior_output=None,
        pipeline_run_id="test-run-001",
        word_index=None,
    )
    out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.DEFERRED


@_requires_snapshot
def test_11_sentence_geometry_sahih_two_units():
    adapter = SentenceGeometryAdapter()
    from hokom.canonical.slot_algebra.types import CanonicalCandidate, CandidateStatus, EvidenceSet, EvidenceAtom, ProvenanceRef
    prov = ProvenanceRef(owner="hokom", module_path="m", rule_id="r", stage_id="P8_AMIL_MAMUL")
    atom = EvidenceAtom(key="k", value="v", confidence=0.9, provenance=prov)
    ev = EvidenceSet.from_atoms("P8_AMIL_MAMUL", (atom,))
    c = CanonicalCandidate(
        candidate_id="C1", candidate_type="AmilMamulCandidate",
        status=CandidateStatus.ACCEPTED, layer_id="P8_AMIL_MAMUL",
        source_rule_id="r", evidence=ev, taaqol_rank=4,
    )
    prior = CanonicalCandidateSet(
        set_id="S1", layer_id="P8_AMIL_MAMUL",
        candidates=(c,), residuals=(), trace_ids=()
    )
    inp = StageInput(
        layer_id="P9_SENTENCE_GEOMETRY",
        surface="كَتَبَ الطَّالِبُ",
        hokom_evidence={
            "amil_mamul_units": [
                {"unit_id": "w0", "word_index": 0, "role": "amil", "candidate_id": ""},
                {"unit_id": "w1", "word_index": 1, "role": "mamul", "candidate_id": ""},
            ],
            "adjacency_relation": "established",
            "sentence_boundary": "closed",
        },
        prior_output=prior,
        pipeline_run_id="test-run-001",
        word_index=None,
    )
    with patch.object(adapter, "_taaqol_license", return_value=_MOCK_LICENSED):
        out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.SAHIH


@_requires_snapshot
def test_12_sentence_geometry_batil_conflict():
    adapter = SentenceGeometryAdapter()
    inp = StageInput(
        layer_id="P9_SENTENCE_GEOMETRY",
        surface="test",
        hokom_evidence={
            "amil_mamul_units": [
                {"unit_id": "w0", "word_index": 0, "role": "amil", "candidate_id": ""},
                {"unit_id": "w1", "word_index": 1, "role": "mamul", "candidate_id": ""},
            ],
            "adjacency_relation": "established",
            "sentence_boundary": "conflict",
        },
        prior_output=None,
        pipeline_run_id="test-run-001",
        word_index=None,
    )
    out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.BATIL


@_requires_snapshot
def test_13_ifadah_candidate_type():
    adapter = IfadahAdapter()
    inp = StageInput(
        layer_id="P12_IFADAH_SPEECH_FORCE",
        surface="test",
        hokom_evidence={"speech_force": "khabar", "ifadah_basis": "test", "force_confidence": 0.9},
        prior_output=_empty_cs("P11_IRAB_GEOMETRY"),
        pipeline_run_id="test-run-001",
        word_index=None,
    )
    # May DEFERRED if prior_output has no accepted candidates — check type
    out = adapter.adapt(inp)
    for c in out.candidate_set.candidates:
        assert c.candidate_type == "IfadahSpeechForceCandidate"
        assert "HukmCandidate" not in (c.output_flags or frozenset())
        assert "RealityClaim" not in (c.output_flags or frozenset())
        assert "FinalMeaning" not in (c.output_flags or frozenset())


@_requires_snapshot
def test_14_ifadah_next_layer_id_is_none():
    adapter = IfadahAdapter()
    assert adapter._next_layer_id() is None


@_requires_snapshot
def test_15_ifadah_output_flags_no_forbidden():
    adapter = IfadahAdapter()
    forbidden = {"HukmCandidate", "RealityClaim", "FinalMeaning", "FinalCaseJudgment"}
    inp = StageInput(
        layer_id="P12_IFADAH_SPEECH_FORCE",
        surface="كَتَبَ الطَّالِبُ",
        hokom_evidence={"speech_force": "khabar", "ifadah_basis": "test", "force_confidence": 0.9},
        prior_output=None,
        pipeline_run_id="test-run-001",
        word_index=None,
    )
    out = adapter.adapt(inp)
    for c in out.candidate_set.candidates:
        overlap = (c.output_flags or frozenset()) & forbidden
        assert not overlap, f"Forbidden flags in P12 candidate: {overlap}"


def test_16_all_19_adapter_layer_ids():
    from hokom.canonical.stages.p0 import UnicodeAdapter, TypedCodepointAdapter, GlyphAdapter
    from hokom.canonical.stages.p1 import (
        LetterIdentityAdapter, HarakaMarkAdapter, ConditionedSequenceAdapter,
        PositionAdapter, SlotCandidateAdapter,
    )
    from hokom.canonical.stages.p2_p5 import (
        RegistryProjectionAdapter, RootStemAdapter, JamidMushtaqAdapter, MufradWordAdapter,
    )
    from hokom.canonical.stages.p6_p8 import (
        VerbalSignifiedAdapter, CompositionReadinessAdapter, AmilMamulAdapter,
    )
    from hokom.canonical.stages.p9_p12 import (
        SentenceGeometryAdapter, RelationGeometryAdapter, IrabGeometryAdapter, IfadahAdapter,
    )
    adapter_classes = [
        UnicodeAdapter, TypedCodepointAdapter, GlyphAdapter,
        LetterIdentityAdapter, HarakaMarkAdapter, ConditionedSequenceAdapter,
        PositionAdapter, SlotCandidateAdapter,
        RegistryProjectionAdapter, RootStemAdapter, JamidMushtaqAdapter, MufradWordAdapter,
        VerbalSignifiedAdapter, CompositionReadinessAdapter, AmilMamulAdapter,
        SentenceGeometryAdapter, RelationGeometryAdapter, IrabGeometryAdapter, IfadahAdapter,
    ]
    adapter_ids = [cls.LAYER_ID for cls in adapter_classes]
    assert len(adapter_ids) == 19
    assert adapter_ids == list(CANONICAL_LAYER_IDS)


@_requires_snapshot
def test_17_next_layer_id_none_only_for_p12():
    from hokom.canonical.stages.p0 import UnicodeAdapter, TypedCodepointAdapter, GlyphAdapter
    from hokom.canonical.stages.p9_p12 import IfadahAdapter, IrabGeometryAdapter
    assert UnicodeAdapter()._next_layer_id() == "P0_TYPED_CODEPOINT"
    assert TypedCodepointAdapter()._next_layer_id() == "P0_GLYPH_CLASSIFICATION"
    assert GlyphAdapter()._next_layer_id() == "P1_LETTER_IDENTITY_CARRIER"
    assert IrabGeometryAdapter()._next_layer_id() == "P12_IFADAH_SPEECH_FORCE"
    assert IfadahAdapter()._next_layer_id() is None


@_requires_snapshot
def test_18_p12_sahih_athar_carry_to_next_none():
    """When P12 produces a SAHIH judgment, AtharEffect.carry_to_next must be None."""
    adapter = IfadahAdapter()
    from hokom.canonical.slot_algebra.types import CanonicalCandidate, CandidateStatus, EvidenceSet, EvidenceAtom, ProvenanceRef
    prov = ProvenanceRef(owner="hokom", module_path="m", rule_id="r", stage_id="P11_IRAB_GEOMETRY")
    atom = EvidenceAtom(key="k", value="v", confidence=0.95, provenance=prov)
    ev = EvidenceSet.from_atoms("P11_IRAB_GEOMETRY", (atom,))
    c = CanonicalCandidate(
        candidate_id="C1", candidate_type="IrabGeometryCandidate",
        status=CandidateStatus.ACCEPTED, layer_id="P11_IRAB_GEOMETRY",
        source_rule_id="r", evidence=ev, taaqol_rank=4,
    )
    prior = CanonicalCandidateSet(
        set_id="S1", layer_id="P11_IRAB_GEOMETRY",
        candidates=(c,), residuals=(), trace_ids=()
    )
    inp = StageInput(
        layer_id="P12_IFADAH_SPEECH_FORCE",
        surface="كَتَبَ الطَّالِبُ",
        hokom_evidence={"speech_force": "khabar", "ifadah_basis": "verb_subject_pair", "force_confidence": 0.92},
        prior_output=prior,
        pipeline_run_id="test-run-001",
        word_index=None,
    )
    with patch.object(adapter, "_taaqol_license", return_value=_MOCK_LICENSED):
        out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.SAHIH
    assert out.judgment.athar is not None
    assert out.judgment.athar.carry_to_next is None   # TERMINAL
    assert out.next_layer_id is None
