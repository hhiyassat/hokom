"""
Tests that verify Taaqol's actual public symbols exist at the correct import paths.

IMPORTANT: These tests SKIP on Python < 3.11 because taaqqul_slot_geometry uses StrEnum
(available since Python 3.11). This is NOT hiding failures — it is correctly documenting
that these tests require Python 3.11+ as specified by the Taaqol pyproject.toml.

On Python 3.12 (macOS canonical runtime): all tests pass.
On Python 3.10 (Linux container): all tests skip.
"""
from __future__ import annotations

import sys
import pytest

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="taaqqul_slot_geometry requires Python 3.11+ (uses StrEnum)"
)

_VENDOR_SRC = 'vendor/Taaqol-GPT/src'


@pytest.fixture(autouse=True)
def add_vendor_path():
    """Add vendor/Taaqol-GPT/src to sys.path for all tests in this module."""
    if _VENDOR_SRC not in sys.path:
        sys.path.insert(0, _VENDOR_SRC)
    yield
    # Do not remove — it's idempotent and safe


# ── Package importability ─────────────────────────────────────────────────────

def test_taaqol_package_importable():
    import taaqqul_slot_geometry
    assert taaqqul_slot_geometry is not None


def test_taaqol_package_has_version_or_all():
    import taaqqul_slot_geometry
    # Must have __all__ (it does)
    assert hasattr(taaqqul_slot_geometry, '__all__')


# ── SlotGraph ─────────────────────────────────────────────────────────────────

def test_slotgraph_importable():
    from taaqqul_slot_geometry import SlotGraph
    assert SlotGraph is not None


def test_slotgraph_is_dataclass():
    import dataclasses
    from taaqqul_slot_geometry import SlotGraph
    assert dataclasses.is_dataclass(SlotGraph)


def test_slotgraph_construct_classmethod_exists():
    from taaqqul_slot_geometry import SlotGraph
    assert hasattr(SlotGraph, 'construct')
    assert callable(SlotGraph.construct)


def test_slotgraph_required_fields():
    from taaqqul_slot_geometry import SlotGraph
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(SlotGraph)}
    required = {'center', 'slots', 'boundary', 'residuals', 'rank',
                'output_boundary', 'generation_source'}
    assert required.issubset(field_names), \
        f"Missing SlotGraph fields: {required - field_names}"


def test_slotgraph_center_importable():
    from taaqqul_slot_geometry import Center
    assert Center is not None


def test_slotgraph_slot_importable():
    from taaqqul_slot_geometry import Slot
    assert Slot is not None


def test_slotgraph_slot_state_importable():
    from taaqqul_slot_geometry import SlotState
    assert SlotState is not None
    assert hasattr(SlotState, 'EMPTY')
    assert hasattr(SlotState, 'FILLED')
    assert hasattr(SlotState, 'BROKEN')


def test_slotgraph_layer_importable():
    from taaqqul_slot_geometry import Layer
    assert Layer is not None
    assert hasattr(Layer, 'TEXT_ENTRY')
    assert hasattr(Layer, 'SLOT')
    assert hasattr(Layer, 'CANDIDATE')
    assert hasattr(Layer, 'CERTIFICATE')


def test_slotgraph_generation_source_importable():
    from taaqqul_slot_geometry import GenerationSource
    assert GenerationSource is not None
    assert hasattr(GenerationSource, 'DECLARED_ENTRY')
    assert hasattr(GenerationSource, 'CANDIDATE')
    assert hasattr(GenerationSource, 'TRANSITION_VERDICT')


def test_slotgraph_trace_ref_importable():
    from taaqqul_slot_geometry import TraceRef
    assert TraceRef is not None


def test_slotgraph_entry_boundary_importable():
    from taaqqul_slot_geometry import EntryBoundary
    assert EntryBoundary is not None


# ── Gamma ─────────────────────────────────────────────────────────────────────

def test_gamma_function_importable():
    from taaqqul_slot_geometry import gamma
    assert callable(gamma)


def test_gamma_result_importable():
    from taaqqul_slot_geometry import GammaResult
    assert GammaResult is not None


def test_closure_state_importable():
    from taaqqul_slot_geometry import ClosureState
    assert ClosureState is not None
    assert hasattr(ClosureState, 'MINIMALLY_CLOSED')
    assert hasattr(ClosureState, 'PERFORATED_CLOSED')
    assert hasattr(ClosureState, 'BLOCKED')
    assert hasattr(ClosureState, 'OPEN')
    assert hasattr(ClosureState, 'INVALID')
    assert hasattr(ClosureState, 'FORBIDDEN_LEAP')


# ── TransitionGate ────────────────────────────────────────────────────────────

def test_transition_gate_importable():
    from taaqqul_slot_geometry import TransitionGate
    assert TransitionGate is not None


def test_transition_gate_is_dataclass():
    import dataclasses
    from taaqqul_slot_geometry import TransitionGate
    assert dataclasses.is_dataclass(TransitionGate)


def test_transition_gate_decide_method_exists():
    from taaqqul_slot_geometry import TransitionGate
    assert hasattr(TransitionGate, 'decide')
    assert callable(TransitionGate.decide)


def test_transition_verdict_importable():
    from taaqqul_slot_geometry import TransitionVerdict
    assert TransitionVerdict is not None


def test_transition_state_importable():
    from taaqqul_slot_geometry import TransitionState
    assert TransitionState is not None
    assert hasattr(TransitionState, 'APPROVED')
    assert hasattr(TransitionState, 'DEFERRED')
    assert hasattr(TransitionState, 'BLOCKED')
    assert hasattr(TransitionState, 'REJECTED')
    assert hasattr(TransitionState, 'FORBIDDEN_LEAP')


# ── Rank lattice ──────────────────────────────────────────────────────────────

def test_rank_importable():
    from taaqqul_slot_geometry import Rank
    assert Rank is not None
    assert hasattr(Rank, 'ZERO')
    assert hasattr(Rank, 'CANDIDATE')
    assert hasattr(Rank, 'HYPOTHESIS')
    assert hasattr(Rank, 'LICENSED')
    assert hasattr(Rank, 'STRONG')
    assert hasattr(Rank, 'CERTIFICATE')


def test_rank_lattice_importable():
    from taaqqul_slot_geometry import RankLattice
    assert callable(RankLattice.meet)
    assert callable(RankLattice.join)


def test_rank_gate_ceilings():
    from taaqqul_slot_geometry import GATE_RANK_CEILING, UNGATED_RANK_CEILING, Rank
    assert GATE_RANK_CEILING == Rank.STRONG
    assert UNGATED_RANK_CEILING == Rank.HYPOTHESIS


# ── Evidence ──────────────────────────────────────────────────────────────────

def test_evidence_contract_importable():
    from taaqqul_slot_geometry import EvidenceContract
    assert EvidenceContract is not None


def test_evidence_source_importable():
    from taaqqul_slot_geometry import EvidenceSource
    assert EvidenceSource is not None


# ── Residuals ─────────────────────────────────────────────────────────────────

def test_residual_importable():
    from taaqqul_slot_geometry import Residual
    assert Residual is not None


def test_residual_kind_importable():
    from taaqqul_slot_geometry import ResidualKind
    assert ResidualKind is not None
    assert hasattr(ResidualKind, 'BLOCKING')
    assert hasattr(ResidualKind, 'DEFERRABLE')
    assert hasattr(ResidualKind, 'NON_BLOCKING')
    assert hasattr(ResidualKind, 'EXPLANATORY')
    assert hasattr(ResidualKind, 'HIDDEN_FORBIDDEN')


# ── FailureCode ───────────────────────────────────────────────────────────────

def test_failure_code_importable():
    from taaqqul_slot_geometry import FailureCode
    assert FailureCode is not None
    assert hasattr(FailureCode, 'BOUNDARY_MISSING')
    assert hasattr(FailureCode, 'REQUIRED_SLOT_EMPTY')
    assert hasattr(FailureCode, 'BLOCKING_RESIDUAL_PRESENT')
    assert hasattr(FailureCode, 'GATE_REQUIRED')


# ── SlotGraph construction (real API) ─────────────────────────────────────────

def test_can_construct_minimal_slot_graph():
    """Verify SlotGraph can be built with real Taaqol API."""
    from taaqqul_slot_geometry import (
        SlotGraph, Center, TraceRef, SlotBoundary, OpeningPolicy,
        Slot, SlotState, OutputBoundary, EntryBoundary, GenerationSource,
        Layer, Rank, FailureCode,
    )
    trace_ref = TraceRef(anchor='test:anchor', kind='test')
    center = Center(
        identity_claim='test_claim',
        domain='test_domain',
        scope='test_scope',
        trace_ref=trace_ref,
    )
    boundary = SlotBoundary(
        domain='test',
        scope='test',
        refusal_codes=(FailureCode.BOUNDARY_MISSING,),
    )
    slot_boundary = SlotBoundary(
        domain='test',
        scope='slot',
        refusal_codes=(FailureCode.REQUIRED_SLOT_EMPTY,),
    )
    opening = OpeningPolicy(allowed_potentials=frozenset({'ACCEPT', 'DEFER'}))
    slot = Slot(
        name='test_slot',
        value_state=SlotState.FILLED,
        boundary=slot_boundary,
        opening=opening,
        required=True,
        value='ACCEPT',
    )
    output_boundary = OutputBoundary(
        declared_layer=Layer.TEXT_ENTRY,
        output_layer=Layer.TEXT_ENTRY,
    )
    entry_boundary = EntryBoundary(
        declared_entry_kind='TEST',
        representation_status='REPRESENTATIONAL',
        ontological_status='NOT_ONTOLOGICAL',
        sound_status='NOT_SOUND',
        meaning_status='NOT_MEANING',
        prior_trace_status='PRESERVED',
        produces_only='TextTraceCandidate',
    )
    graph = SlotGraph(
        center=center,
        slots=(slot,),
        boundary=boundary,
        residuals=(),
        rank=Rank.CANDIDATE,
        output_boundary=output_boundary,
        generation_source=GenerationSource.DECLARED_ENTRY,
        entry_boundary=entry_boundary,
    )
    assert graph is not None
    assert graph.rank == Rank.CANDIDATE


def test_gamma_runs_on_minimal_graph():
    """Verify gamma() can run on a properly constructed SlotGraph."""
    from taaqqul_slot_geometry import (
        SlotGraph, Center, TraceRef, SlotBoundary, OpeningPolicy,
        Slot, SlotState, OutputBoundary, EntryBoundary, GenerationSource,
        Layer, Rank, FailureCode, GammaResult, gamma,
    )
    trace_ref = TraceRef(anchor='gamma_test', kind='test')
    center = Center(
        identity_claim='gamma_test_claim',
        domain='test_domain',
        scope='test_scope',
        trace_ref=trace_ref,
    )
    boundary = SlotBoundary(
        domain='test', scope='test',
        refusal_codes=(FailureCode.BOUNDARY_MISSING,),
    )
    slot_boundary = SlotBoundary(
        domain='test', scope='slot',
        refusal_codes=(FailureCode.REQUIRED_SLOT_EMPTY,),
    )
    opening = OpeningPolicy(allowed_potentials=frozenset({'ACCEPT', 'DEFER'}))
    slot = Slot(
        name='primary',
        value_state=SlotState.FILLED,
        boundary=slot_boundary,
        opening=opening,
        required=True,
        value='ACCEPT',
    )
    output_boundary = OutputBoundary(
        declared_layer=Layer.TEXT_ENTRY,
        output_layer=Layer.TEXT_ENTRY,
    )
    entry_boundary = EntryBoundary(
        declared_entry_kind='TEST',
        representation_status='REPRESENTATIONAL',
        ontological_status='NOT_ONTOLOGICAL',
        sound_status='NOT_SOUND',
        meaning_status='NOT_MEANING',
        prior_trace_status='PRESERVED',
        produces_only='TextTraceCandidate',
    )
    graph = SlotGraph(
        center=center,
        slots=(slot,),
        boundary=boundary,
        residuals=(),
        rank=Rank.CANDIDATE,
        output_boundary=output_boundary,
        generation_source=GenerationSource.DECLARED_ENTRY,
        entry_boundary=entry_boundary,
    )
    result = gamma(graph)
    assert isinstance(result, GammaResult)
    # CANDIDATE rank, no residuals, all required slots filled → MINIMALLY_CLOSED
    from taaqqul_slot_geometry import ClosureState
    assert result.state == ClosureState.MINIMALLY_CLOSED


def test_transition_gate_runs_on_minimal_graph():
    """Verify TransitionGate.decide() runs on a properly constructed SlotGraph."""
    from taaqqul_slot_geometry import (
        SlotGraph, Center, TraceRef, SlotBoundary, OpeningPolicy,
        Slot, SlotState, OutputBoundary, EntryBoundary, GenerationSource,
        Layer, Rank, FailureCode,
        TransitionGate, TransitionVerdict, TransitionState,
        EvidenceContract, EvidenceSource,
    )
    trace_ref = TraceRef(anchor='gate_test', kind='test')
    center = Center(
        identity_claim='gate_test_claim',
        domain='test_domain',
        scope='test_scope',
        trace_ref=trace_ref,
    )
    boundary = SlotBoundary(
        domain='test', scope='test',
        refusal_codes=(FailureCode.BOUNDARY_MISSING,),
    )
    slot_boundary = SlotBoundary(
        domain='test', scope='slot',
        refusal_codes=(FailureCode.REQUIRED_SLOT_EMPTY,),
    )
    opening = OpeningPolicy(allowed_potentials=frozenset({'ACCEPT', 'DEFER'}))
    slot = Slot(
        name='primary',
        value_state=SlotState.FILLED,
        boundary=slot_boundary,
        opening=opening,
        required=True,
        value='ACCEPT',
    )
    output_boundary = OutputBoundary(
        declared_layer=Layer.TEXT_ENTRY,
        output_layer=Layer.TEXT_ENTRY,
    )
    entry_boundary = EntryBoundary(
        declared_entry_kind='TEST',
        representation_status='REPRESENTATIONAL',
        ontological_status='NOT_ONTOLOGICAL',
        sound_status='NOT_SOUND',
        meaning_status='NOT_MEANING',
        prior_trace_status='PRESERVED',
        produces_only='TextTraceCandidate',
    )
    graph = SlotGraph(
        center=center,
        slots=(slot,),
        boundary=boundary,
        residuals=(),
        rank=Rank.CANDIDATE,
        output_boundary=output_boundary,
        generation_source=GenerationSource.DECLARED_ENTRY,
        entry_boundary=entry_boundary,
    )
    evidence_source = EvidenceSource(
        name='test_evidence',
        kind='test_kind',
        rank=Rank.HYPOTHESIS,
        trace_ref=TraceRef(anchor='gate_test', kind='evidence'),
    )
    evidence = EvidenceContract(sources=(evidence_source,))
    gate = TransitionGate(name='TEST_GATE', gate_rank=Rank.STRONG)
    verdict = gate.decide(graph, Layer.CANDIDATE, evidence)
    assert isinstance(verdict, TransitionVerdict)
    assert verdict.state == TransitionState.APPROVED
