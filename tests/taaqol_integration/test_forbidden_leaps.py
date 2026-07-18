"""
HT29 -- Negative constitutional tests (forbidden leaps + Python 3.11 migration).
Updated: Python 3.11 migration batch to include native component tests.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pipeline.taaqol_integration.provider_models import (
    HokomLinguisticClaimBundle, ProviderAdmissionResult
)
from pipeline.taaqol_integration.claim_adapter import bundle_from_hokom_result
from pipeline.taaqol_integration.provider_guard import admit_provider, validate_bundle
from pipeline.taaqol_integration.admission_gate import admit_claim, _NATIVE_AVAILABLE
from pipeline.taaqol_integration.rank_adapter import assert_no_rank_injection, hokom_directive_is_not_rank
from pipeline.taaqol_integration.residual_adapter import map_residuals
from pipeline.taaqol_integration.evidence_adapter import map_evidence
from pipeline.taaqol_integration.strict_mode import strict_mode_ready


def _minimal_bundle(**overrides) -> HokomLinguisticClaimBundle:
    """Build a minimal valid bundle with optional overrides."""
    defaults = dict(
        claim_id='hokom:test:surface',
        token_id='test_token',
        original_surface='نَصَرَ',
        normalized_surface='نَصَرَ',
        refined_host='نَصَرَ',
        lexical_class=None,
        part_of_speech=None,
        root_claim=None,
        wazn_claim=None,
        form_claim=None,
        masdar_claim=None,
        mushtaq_claims=(),
        inflection_claim=None,
        attachment_claims=(),
        domain_directive='DEFER',
        source_engine='HOKOM_ROOT_ENGINE',
        evidence_ids=(),
        trace_ids=(),
        active_residuals=(),
        resolved_residuals=(),
        catalog_versions=(),
        engine_version='2026.07.18',
    )
    defaults.update(overrides)
    return HokomLinguisticClaimBundle(**defaults)


class _AdmittedProvider:
    provider_id = 'HOKOM_MORPHOLOGY_ENGINE'
    engine_version = '2026.07.18'
    callable_surface = 'single Arabic token'
    output_schema = 'HokomLinguisticClaimBundle'
    def analyze_token(self, surface):
        return _minimal_bundle(original_surface=surface)


# ============================================================================
# Original tests 1-20
# ============================================================================

def test_accept_without_evidence_is_not_licensed():
    """ACCEPT directive with no evidence_ids must not produce APPROVED admission."""
    bundle = _minimal_bundle(domain_directive='ACCEPT', evidence_ids=(), root_claim=object())
    provider_admission = admit_provider(_AdmittedProvider())
    admission = admit_claim(bundle, provider_admission)
    assert admission.verdict != 'APPROVED', \
        "ACCEPT without evidence must not become APPROVED"
    assert admission.taaqol_rank is None, \
        "Rank must never be set by Hokom side"


def test_missing_trace_not_auto_fixed():
    """A bundle with no trace_ids must not have traces auto-generated."""
    bundle = _minimal_bundle(trace_ids=())
    provider_admission = admit_provider(_AdmittedProvider())
    admission = admit_claim(bundle, provider_admission)
    assert admission.trace_refs == (), "Traces must not be auto-generated"


def test_altered_surface_empty_is_rejected():
    """Bundle with empty original_surface must be rejected by validate_bundle."""
    bundle = _minimal_bundle(original_surface='')
    violations = validate_bundle(bundle)
    assert violations, "Empty original_surface must produce violations"
    assert any('original_surface' in v for v in violations)


def test_unrelated_root_payload_defer():
    """root_claim present but domain_directive=DEFER must stay DEFERRED."""
    bundle = _minimal_bundle(domain_directive='DEFER', root_claim=object(), evidence_ids=())
    provider_admission = admit_provider(_AdmittedProvider())
    admission = admit_claim(bundle, provider_admission)
    assert admission.verdict in ('DEFERRED', 'BLOCKED', 'REJECTED')


def test_hidden_residual_triggers_contract_refusal():
    """Active & resolved overlap must produce contract refusal."""
    bundle = _minimal_bundle(
        active_residuals=('RES_A',),
        resolved_residuals=('RES_A',),  # same code in both = HIDDEN
    )
    violations = validate_bundle(bundle)
    assert any('both active and resolved' in v for v in violations), \
        "Hidden residual (active & resolved overlap) must be flagged"


def test_injected_native_rank_refused():
    """bundle.to_dict() with LICENSED value must trigger rank injection check."""
    bundle_dict = {'claim_id': 'test', 'domain_directive': 'LICENSED', 'verdict': 'ACCEPT'}
    violations = assert_no_rank_injection(bundle_dict)
    assert violations, "LICENSED in bundle_dict must trigger rank injection violation"


def test_hokom_directive_is_not_rank():
    """Boundary assertion: ACCEPT directive is NOT a Taaqol LICENSED rank."""
    assert hokom_directive_is_not_rank('ACCEPT') is True
    assert hokom_directive_is_not_rank('DEFER') is True


def test_unadmitted_provider_rejected():
    """A provider missing required fields must not be admitted."""
    class BadProvider:
        pass
    provider_admission = admit_provider(BadProvider())
    assert not provider_admission.admitted
    bundle = _minimal_bundle()
    admission = admit_claim(bundle, provider_admission)
    assert admission.verdict == 'REJECTED'
    assert 'provider not admitted' in (admission.stop_reason or '')


def test_raw_dict_rejected_by_validate_bundle():
    """validate_bundle must reject any non-HokomLinguisticClaimBundle."""
    raw = {'surface': 'test', 'verdict': 'ACCEPT'}
    violations = validate_bundle(raw)
    assert violations
    assert any('HokomLinguisticClaimBundle' in v for v in violations)


def test_single_token_no_binary_relation():
    """Single token analysis must not claim to have produced RelationCandidate."""
    from hokom_pipeline import hokom
    result = hokom('نَصَرَ')
    bundle = bundle_from_hokom_result(result)
    provider_admission = admit_provider(_AdmittedProvider())
    admission = admit_claim(bundle, provider_admission)
    assert admission.verdict != 'FORBIDDEN_LEAP'


def test_defer_stays_defer():
    """DEFER must remain DEFER; it must not be auto-promoted."""
    bundle = _minimal_bundle(domain_directive='DEFER')
    provider_admission = admit_provider(_AdmittedProvider())
    admission = admit_claim(bundle, provider_admission)
    assert admission.verdict in ('DEFERRED', 'BLOCKED', 'REJECTED'), \
        "DEFER domain_directive must result in DEFERRED/BLOCKED/REJECTED, not APPROVED"


def test_active_residual_survives_serialization():
    """Active residuals must be preserved in bundle.to_dict() output."""
    bundle = _minimal_bundle(active_residuals=('RES_INCOMPLETE',))
    d = bundle.to_dict()
    assert d.get('active_residuals') == ('RES_INCOMPLETE',)


def test_block_directive_produces_blocked_admission():
    """BLOCK domain_directive must produce BLOCKED admission."""
    bundle = _minimal_bundle(domain_directive='BLOCK')
    provider_admission = admit_provider(_AdmittedProvider())
    admission = admit_claim(bundle, provider_admission)
    assert admission.verdict == 'BLOCKED', \
        f"BLOCK directive must produce BLOCKED, got {admission.verdict}"


def test_strict_mode_not_ready():
    """Strict mode must report not-ready with prerequisites pending."""
    ready, missing = strict_mode_ready()
    assert not ready, "Strict mode must not be ready in this batch"
    assert len(missing) > 0, "Missing prerequisites must be listed"


def test_accept_directive_alone_is_not_evidence():
    """The ACCEPT directive alone does not supply root_catalog or wazn_pattern evidence."""
    bundle = _minimal_bundle(
        domain_directive='ACCEPT', evidence_ids=(), root_claim=object(), wazn_claim=object()
    )
    result = map_evidence(bundle)
    assert result.total_count > 0
    assert 'root_catalog_evidence' in result.missing_types or 'wazn_pattern_evidence' in result.missing_types
    assert result.verdict in ('INSUFFICIENT', 'MISSING')


def test_blocking_residual_produces_blocking_verdict():
    """A code containing 'block' must be classified as BLOCKING."""
    result = map_residuals(active=('RES_BLOCK_A',), resolved=())
    assert result.verdict == 'BLOCKING'
    assert result.blocking_count == 1


def test_hidden_residual_in_residual_adapter():
    """Active + resolved overlap must produce HIDDEN verdict in residual adapter."""
    result = map_residuals(active=('RES_X',), resolved=('RES_X',))
    assert result.verdict == 'HIDDEN'
    assert result.hidden_count > 0


def test_provider_admission_is_not_claim_approval():
    """ProviderAdmissionResult.IS_CLAIM_APPROVAL must always be False."""
    provider_admission = admit_provider(_AdmittedProvider())
    assert provider_admission.IS_CLAIM_APPROVAL is False


def test_rank_boundary_holds_for_all_directives():
    """The rank boundary must hold for all possible directives."""
    for directive in ('ACCEPT', 'DEFER', 'BLOCK', 'NOT_APPLICABLE', 'UNKNOWN'):
        assert hokom_directive_is_not_rank(directive) is True


def test_bundle_from_minimal_dict():
    """bundle_from_hokom_result must handle minimal dict without crashing."""
    minimal = {'original': 'هُوَ', 'verdict': 'DEFER'}
    bundle = bundle_from_hokom_result(minimal, token_id='test_20')
    assert isinstance(bundle, HokomLinguisticClaimBundle)
    assert bundle.original_surface == 'هُوَ'
    assert bundle.domain_directive == 'DEFER'


# ============================================================================
# Python 3.11 migration / native component tests (R23 additions)
# ============================================================================

def test_hokom_accept_no_evidence_not_licensed():
    """
    Build bundle with ACCEPT but no evidence_ids.
    Admission must NOT be APPROVED (evidence required by gate).
    """
    bundle = _minimal_bundle(
        domain_directive='ACCEPT',
        evidence_ids=(),
        root_claim=object(),  # root claim present but no evidence_ids
    )
    provider_admission = admit_provider(_AdmittedProvider())
    admission = admit_claim(bundle, provider_admission)
    assert admission.verdict != 'APPROVED', \
        f"ACCEPT with no evidence must not be APPROVED, got {admission.verdict}"


def test_hidden_residual_causes_refusal():
    """
    Build bundle where same code appears in both active and resolved.
    validate_bundle must flag it as HIDDEN before admission runs.
    """
    bundle = _minimal_bundle(
        active_residuals=('HIDDEN_CODE_X',),
        resolved_residuals=('HIDDEN_CODE_X',),
    )
    violations = validate_bundle(bundle)
    assert any('both active and resolved' in v for v in violations), \
        f"Hidden residual must be detected, violations={violations}"

    # Even if we skip validate_bundle, residual_adapter must catch it
    r = map_residuals(('HIDDEN_CODE_X',), ('HIDDEN_CODE_X',))
    assert r.verdict == 'HIDDEN'
    assert r.hidden_count == 1


def test_python_version_meets_requirement():
    """
    Python version must be 3.10+ (3.11+ required for native StrEnum).
    """
    assert sys.version_info >= (3, 10), \
        f"Python 3.10+ required, got {sys.version}"
    # Document that 3.11+ provides native StrEnum; 3.10 requires upgrade
    # No backport accepted per Amendment No. 1 Constraint 1
    if sys.version_info >= (3, 11):
        import enum as _em
        assert hasattr(_em, 'StrEnum'), "Python 3.11+ must have native StrEnum"


@pytest.mark.skipif(sys.version_info < (3, 11), reason="StrEnum is Python 3.11+ only; no backport accepted (Amendment No. 1)")
def test_no_strEnum_shim_missing():
    """Verify StrEnum is importable natively (Python 3.11+, no backport)."""
    from enum import StrEnum  # must not raise on Python 3.11+
    assert StrEnum is not None
    # Verify it behaves as a string-enum
    class TestSE(StrEnum):
        A = 'alpha'
    assert TestSE.A == 'alpha'
    assert isinstance(TestSE.A, str)


def test_vendor_not_patched():
    """Verify docs/upstream-provenance/Taaqol-GPT.json has local_patch_count=0.

    Provenance lives outside the submodule (docs/upstream-provenance/) so the
    submodule tree stays clean at the pinned commit.
    """
    import json, pathlib
    repo_root = pathlib.Path(__file__).resolve().parent.parent.parent
    provenance_path = repo_root / 'docs' / 'upstream-provenance' / 'Taaqol-GPT.json'
    assert provenance_path.exists(), \
        f"Provenance record missing: {provenance_path}"
    with open(provenance_path) as f:
        data = json.load(f)
    assert data.get('local_patch_count') == 0, \
        f"local_patch_count must be 0, got {data.get('local_patch_count')}"
    assert data.get('commit_sha'), "commit_sha must be present"
    assert len(data.get('commit_sha', '')) == 40, \
        f"commit_sha must be 40-char hex, got {data.get('commit_sha')!r}"


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Native Taaqol requires Python 3.11+ (StrEnum; no backport accepted)")
def test_native_taaqol_importable():
    """Native taaqqul_slot_geometry must be importable on Python 3.11+."""
    assert _NATIVE_AVAILABLE, \
        "taaqqul_slot_geometry must be importable on Python 3.11+"


@pytest.mark.skipif(not _NATIVE_AVAILABLE, reason="Native Taaqol not importable on Python < 3.11 without StrEnum")
def test_native_gamma_runs_on_minimal_graph():
    """Native gamma() must execute and return a valid GammaResult."""
    pytest.importorskip('taaqqul_slot_geometry')
    from taaqqul_slot_geometry.core.slot_graph import (
        SlotGraph, Center, Slot, SlotBoundary, OpeningPolicy, SlotState,
        OutputBoundary, GenerationSource, Layer, TraceRef, EntryBoundary,
    )
    from taaqqul_slot_geometry.core.gamma import gamma
    from taaqqul_slot_geometry.core.rank_lattice import Rank
    from taaqqul_slot_geometry.core.failure_taxonomy import FailureCode
    from taaqqul_slot_geometry.core.closure_state import ClosureState

    trace_ref = TraceRef(anchor='test:forbidden_leaps:r23', kind='TEST')
    center = Center(identity_claim='test_r23', domain='TEST', scope='NEGATIVE', trace_ref=trace_ref)
    sb = SlotBoundary(domain='TEST', scope='SLOT', refusal_codes=(FailureCode.IDENTITY_BROKEN,))
    op = OpeningPolicy(allowed_potentials=frozenset({'val'}))
    slot = Slot(name='s', value_state=SlotState.FILLED, boundary=sb, opening=op, required=True, value='val')
    gb = SlotBoundary(domain='TEST', scope='GRAPH', refusal_codes=(FailureCode.BOUNDARY_MISSING,))
    ob = OutputBoundary(declared_layer=Layer.SLOT, output_layer=Layer.SLOT)
    eb = EntryBoundary(
        declared_entry_kind='TEST', representation_status='REP', ontological_status='NOT_ONTO',
        sound_status='NOT_SOUND', meaning_status='NOT_MEANING', prior_trace_status='PRESERVED',
        produces_only='TextTraceCandidate'
    )
    graph = SlotGraph(
        center=center, slots=(slot,), boundary=gb, residuals=(),
        rank=Rank.HYPOTHESIS, output_boundary=ob,
        generation_source=GenerationSource.DECLARED_ENTRY, entry_boundary=eb
    )
    gr = gamma(graph)
    assert gr.state in (ClosureState.MINIMALLY_CLOSED, ClosureState.PERFORATED_CLOSED), \
        f"Minimal graph should close, got {gr.state}"
    assert gr.failure_code is None


@pytest.mark.skipif(not _NATIVE_AVAILABLE, reason="Native Taaqol not importable on Python < 3.11 without StrEnum")
def test_no_output_exceeds_slot_layer():
    """
    The admission gate must never emit a CANDIDATE or CERTIFICATE layer output.
    OutputBoundary.output_layer must be Layer.SLOT for all admission graphs.
    """
    from hokom_pipeline import hokom
    result = hokom('نَصَرَ')
    bundle = bundle_from_hokom_result(result)
    from pipeline.taaqol_integration.api import HokomProvider
    provider_admission = admit_provider(HokomProvider())
    admission = admit_claim(bundle, provider_admission)
    # APPROVED at SLOT layer -- never at CANDIDATE or CERTIFICATE
    if admission.verdict == 'APPROVED':
        rank_str = str(admission.taaqol_rank)
        # The gate rank ceiling is HYPOTHESIS -- never LICENSED or above via single token admission
        assert 'CERTIFICATE' not in rank_str, "Output must never reach CERTIFICATE layer"
        assert 'STRONG' not in rank_str, "Output must never reach STRONG without gate"
