"""
Tests for Constitutional Amendment No. 1.
These tests verify the contracts, laws, and invariants.
They do NOT test P6-P12 (out of scope).
"""
import sys
import os
import inspect
import pathlib
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pipeline.taaqol_integration.constitutional_contracts import (
    Assessment, IntrinsicVerdict, OperationalStatus,
    ClaimProvenance, ConceptContract, IfadahCandidate,
    RealityDomain, DomainBridge, TransitionTrace,
    RepairDirective, ApplicationAssessment, AuthorityCheck,
    CorrespondenceAssessment,
)
from pipeline.taaqol_integration.constitutional_validators import (
    assert_assessment_separation,
    assert_no_direct_action_from_ifadah,
    assert_rank_does_not_rise,
    assert_transition_trace_complete,
    assert_no_domain_leap,
    assert_provenance_not_empty,
)


class TestAssessmentSeparation:
    def test_sahih_deferred_is_valid(self):
        """SAHIH + DEFERRED is legal: claim is sound but evidence missing."""
        a = Assessment(
            claim_id='c1',
            intrinsic_verdict=IntrinsicVerdict.SAHIH,
            operational_status=OperationalStatus.DEFERRED,
            evidence_rank='TRACE',
        )
        assert_assessment_separation(a)  # must not raise

    def test_fasid_blocked_is_valid(self):
        """FASID + BLOCKED is legal: claim is defective and a blocker applies."""
        a = Assessment(
            claim_id='c2',
            intrinsic_verdict=IntrinsicVerdict.FASID,
            operational_status=OperationalStatus.BLOCKED,
            evidence_rank='TRACE',
            active_blockers=('MISSING_CONDITION',),
        )
        assert_assessment_separation(a)

    def test_batil_licensed_is_illegal(self):
        """BATIL + LICENSED is a constitutional violation."""
        a = Assessment(
            claim_id='c3',
            intrinsic_verdict=IntrinsicVerdict.BATIL,
            operational_status=OperationalStatus.LICENSED,
            evidence_rank='LICENSED',
        )
        with pytest.raises(ValueError, match="BATIL"):
            assert_assessment_separation(a)

    def test_active_blocker_prevents_licensed(self):
        """Active blocker must not coexist with LICENSED status."""
        a = Assessment(
            claim_id='c4',
            intrinsic_verdict=IntrinsicVerdict.SAHIH,
            operational_status=OperationalStatus.LICENSED,
            evidence_rank='LICENSED',
            active_blockers=('SOME_BLOCKER',),
        )
        with pytest.raises(ValueError, match="blocker"):
            assert_assessment_separation(a)

    def test_three_fields_are_independent(self):
        """The three assessment fields must be stored separately."""
        a = Assessment(
            claim_id='c5',
            intrinsic_verdict=IntrinsicVerdict.SAHIH,
            operational_status=OperationalStatus.RESIDUAL,
            evidence_rank='CANDIDATE',
        )
        assert a.intrinsic_verdict != a.operational_status
        assert a.operational_status != a.evidence_rank

    def test_sahih_residual_is_valid(self):
        """SAHIH + RESIDUAL is valid: sound claim with residuals propagating."""
        a = Assessment(
            claim_id='c6',
            intrinsic_verdict=IntrinsicVerdict.SAHIH,
            operational_status=OperationalStatus.RESIDUAL,
            evidence_rank='HYPOTHESIS',
            active_residuals=('RES_INCOMPLETE_CHAIN',),
        )
        assert_assessment_separation(a)  # must not raise

    def test_undetermined_deferred_is_valid(self):
        """UNDETERMINED + DEFERRED is valid: claim under investigation."""
        a = Assessment(
            claim_id='c7',
            intrinsic_verdict=IntrinsicVerdict.UNDETERMINED,
            operational_status=OperationalStatus.DEFERRED,
            evidence_rank='NO_EVIDENCE',
        )
        assert_assessment_separation(a)


class TestForbiddenLeaps:
    def test_ifadah_to_action_is_forbidden(self):
        with pytest.raises(ValueError, match="Forbidden"):
            assert_no_direct_action_from_ifadah('IfadahCandidate', 'Action')

    def test_concept_to_action_is_forbidden(self):
        with pytest.raises(ValueError, match="Forbidden"):
            assert_no_direct_action_from_ifadah('ConceptContract', 'AuthorizedAction')

    def test_candidate_rule_to_final_judgment_is_forbidden(self):
        with pytest.raises(ValueError, match="Forbidden"):
            assert_no_direct_action_from_ifadah('CandidateRule', 'FinalJudgment')

    def test_licensed_judgment_to_action_is_allowed(self):
        """LicensedJudgment -> AuthorizedAction is the legal path."""
        assert_no_direct_action_from_ifadah('LicensedJudgment', 'AuthorizedAction')  # no raise

    def test_ifadah_to_judgment_candidate_is_allowed(self):
        assert_no_direct_action_from_ifadah('IfadahCandidate', 'JudgmentCandidate')  # no raise

    def test_concept_to_final_meaning_is_forbidden(self):
        with pytest.raises(ValueError, match="Forbidden"):
            assert_no_direct_action_from_ifadah('ConceptContract', 'FinalMeaning')

    def test_candidate_rule_to_authorized_action_is_forbidden(self):
        with pytest.raises(ValueError, match="Forbidden"):
            assert_no_direct_action_from_ifadah('CandidateRule', 'AuthorizedAction')


class TestRankLaw:
    def test_rank_cannot_rise_with_same_evidence(self):
        with pytest.raises(ValueError, match="Rank"):
            assert_rank_does_not_rise('TRACE', 'LICENSED', same_evidence_repeated=True)

    def test_rank_may_rise_with_new_evidence(self):
        assert_rank_does_not_rise('TRACE', 'LICENSED', same_evidence_repeated=False)  # no raise

    def test_rank_stays_same_is_always_fine(self):
        assert_rank_does_not_rise('LICENSED', 'LICENSED', same_evidence_repeated=True)  # no raise

    def test_rank_falls_is_always_fine(self):
        assert_rank_does_not_rise('LICENSED', 'TRACE', same_evidence_repeated=True)  # no raise

    def test_hypothesis_to_mass_transmission_with_same_evidence_forbidden(self):
        with pytest.raises(ValueError, match="Rank"):
            assert_rank_does_not_rise('HYPOTHESIS', 'MASS_TRANSMISSION', same_evidence_repeated=True)


class TestDomainBridgeLaw:
    def test_cross_domain_without_bridge_is_forbidden(self):
        with pytest.raises(ValueError, match="DomainBridge"):
            assert_no_domain_leap(
                evidence_domain=RealityDomain.MORPHOLOGICAL,
                conclusion_domain=RealityDomain.LEGAL,
                bridge_declared=False,
            )

    def test_same_domain_no_bridge_needed(self):
        assert_no_domain_leap(
            evidence_domain=RealityDomain.MORPHOLOGICAL,
            conclusion_domain=RealityDomain.MORPHOLOGICAL,
            bridge_declared=False,
        )  # no raise

    def test_cross_domain_with_bridge_is_allowed(self):
        assert_no_domain_leap(
            evidence_domain=RealityDomain.MORPHOLOGICAL,
            conclusion_domain=RealityDomain.LEGAL,
            bridge_declared=True,
        )  # no raise

    def test_morphological_to_shari_without_bridge_forbidden(self):
        with pytest.raises(ValueError, match="DomainBridge"):
            assert_no_domain_leap(
                evidence_domain=RealityDomain.MORPHOLOGICAL,
                conclusion_domain=RealityDomain.SHARI,
                bridge_declared=False,
            )

    def test_semantic_to_legal_without_bridge_forbidden(self):
        with pytest.raises(ValueError, match="DomainBridge"):
            assert_no_domain_leap(
                evidence_domain=RealityDomain.SEMANTIC,
                conclusion_domain=RealityDomain.LEGAL,
                bridge_declared=False,
            )


class TestClaimProvenance:
    def test_incomplete_provenance_raises(self):
        p = ClaimProvenance(
            claim_id='',
            source_identity='HOKOM',
            source_type='HOKOM_ROOT_ENGINE',
            originating_layer='P4A',
            carrier='نَصَرَ',
            preserved_surface='',
        )
        with pytest.raises(ValueError):
            assert_provenance_not_empty(p)

    def test_complete_provenance_passes(self):
        p = ClaimProvenance(
            claim_id='prov-001',
            source_identity='HOKOM_ROOT_ENGINE',
            source_type='HOKOM_ROOT_ENGINE',
            originating_layer='P4A',
            carrier='نَصَرَ',
            preserved_surface='نَصَرَ',
            domain=RealityDomain.MORPHOLOGICAL,
        )
        assert_provenance_not_empty(p)  # no raise

    def test_empty_source_identity_raises(self):
        p = ClaimProvenance(
            claim_id='prov-002',
            source_identity='',
            source_type='HOKOM_ROOT_ENGINE',
            originating_layer='P4A',
            carrier='نَصَرَ',
            preserved_surface='نَصَرَ',
        )
        with pytest.raises(ValueError):
            assert_provenance_not_empty(p)

    def test_transformation_history_preserved(self):
        p = ClaimProvenance(
            claim_id='prov-003',
            source_identity='HOKOM_ROOT_ENGINE',
            source_type='HOKOM_ROOT_ENGINE',
            originating_layer='P5',
            carrier='نَصَرَ',
            preserved_surface='نَصَرَ',
            transformation_history=('P4A->P4B', 'P4B->P5'),
        )
        assert len(p.transformation_history) == 2


class TestTransitionTrace:
    def test_incomplete_trace_raises_on_trace_id(self):
        t = TransitionTrace(
            trace_id='',
            from_layer='P4A',
            to_layer='P4B',
            input_identity='نصر',
            output_identity='BAB_I',
            transformation='wazn_resolution',
            verdict='ACCEPT',
        )
        with pytest.raises(ValueError, match="trace_id"):
            assert_transition_trace_complete(t)

    def test_incomplete_trace_raises_on_output_identity(self):
        t = TransitionTrace(
            trace_id='tr-missing-output',
            from_layer='P4A',
            to_layer='P4B',
            input_identity='نصر',
            output_identity='',
            transformation='wazn_resolution',
            verdict='ACCEPT',
        )
        with pytest.raises(ValueError, match="output_identity"):
            assert_transition_trace_complete(t)

    def test_complete_trace_passes(self):
        t = TransitionTrace(
            trace_id='tr-001',
            from_layer='P4A',
            to_layer='P4B',
            input_identity='نصر',
            output_identity='BAB_I_NASARA',
            transformation='wazn_bab_resolution',
            verdict='ACCEPT',
        )
        assert_transition_trace_complete(t)  # no raise

    def test_trace_is_immutable(self):
        t = TransitionTrace(
            trace_id='tr-002',
            from_layer='P4A',
            to_layer='P4B',
            input_identity='نصر',
            output_identity='BAB_I',
            transformation='wazn_resolution',
            verdict='ACCEPT',
        )
        # frozen=True raises FrozenInstanceError on normal assignment
        with pytest.raises(Exception):
            t.verdict = 'REJECT'  # type: ignore[misc]


class TestIfadahCandidateContract:
    def test_ifadah_candidate_is_not_final_meaning(self):
        """IfadahCandidate has prohibited_inferences to document what it cannot conclude."""
        ic = IfadahCandidate(
            proposition='النصر حدث من زيد',
            source_utterance='نصر زيد عمرًا',
            prohibited_inferences=('FinalMeaning', 'FinalJudgment', 'AuthorizedAction'),
        )
        assert 'FinalMeaning' in ic.prohibited_inferences
        assert 'FinalJudgment' in ic.prohibited_inferences

    def test_ifadah_candidate_blockers_propagate(self):
        ic = IfadahCandidate(
            proposition='النصر حدث',
            source_utterance='نصر',
            blockers=('MISSING_RELATION',),
            residuals=('AGENT_UNSPECIFIED',),
        )
        assert ic.blockers == ('MISSING_RELATION',)
        assert ic.residuals == ('AGENT_UNSPECIFIED',)

    def test_ifadah_candidate_is_candidate_not_rule(self):
        """IfadahCandidate is a proposition candidate, not a rule."""
        ic = IfadahCandidate(
            proposition='test proposition',
            source_utterance='test utterance',
        )
        # It is a candidate -- no 'rule' attribute
        assert not hasattr(ic, 'rule_id')
        assert not hasattr(ic, 'action')


class TestConstitutionalContracts:
    """Verify all 11 contracts are importable and constructable."""

    def test_all_contracts_importable(self):
        from pipeline.taaqol_integration.constitutional_contracts import (
            ClaimProvenance, ConceptContract, IfadahCandidate,
            RealityDomain, DomainBridge, Assessment,
            TransitionTrace, RepairDirective, ApplicationAssessment,
            AuthorityCheck, CorrespondenceAssessment,
        )
        assert True  # importability confirmed

    def test_reality_domain_constants(self):
        assert RealityDomain.MORPHOLOGICAL == 'MORPHOLOGICAL'
        assert RealityDomain.LEGAL == 'LEGAL'
        assert RealityDomain.SHARI == 'SHARI'
        assert RealityDomain.SEMANTIC == 'SEMANTIC'
        assert RealityDomain.EMPIRICAL == 'EMPIRICAL'

    def test_repair_directive_constructable(self):
        rd = RepairDirective(
            directive_id='rd-001',
            failure_layer='P4B',
            return_to_layer='P4A',
            failed_gate='BAB_SELECTION_GATE',
            missing_condition='BAB_VOWEL_REQUIRED',
        )
        assert rd.failure_layer == 'P4B'
        assert rd.return_to_layer == 'P4A'

    def test_domain_bridge_constructable(self):
        db = DomainBridge(
            bridge_id='bridge-morph-legal',
            from_domain=RealityDomain.MORPHOLOGICAL,
            to_domain=RealityDomain.LEGAL,
            bridge_law='QIYAS_MORPHOLOGICAL_EXTENSION',
            conditions=('DECLARED_ANALOGY',),
            evidence_rank='HYPOTHESIS',
        )
        assert db.from_domain == 'MORPHOLOGICAL'
        assert db.to_domain == 'LEGAL'

    def test_application_assessment_constructable(self):
        aa = ApplicationAssessment(
            assessment_id='aa-001',
            judgment_id='j-001',
            case_description='Test case',
            applies='PARTIAL',
            conditions_met=('CONDITION_A',),
            conditions_unmet=('CONDITION_B',),
        )
        assert aa.applies == 'PARTIAL'

    def test_authority_check_constructable(self):
        ac = AuthorityCheck(
            check_id='ac-001',
            actor_id='SCHOLAR_X',
            action_type='ISSUE_FATWA',
            domain=RealityDomain.SHARI,
            authority_source='IJAZAH_CHAIN',
            verdict='AUTHORIZED',
        )
        assert ac.verdict == 'AUTHORIZED'

    def test_correspondence_assessment_non_match_not_batil(self):
        """Non-correspondence does not mean the rule is BATIL."""
        ca = CorrespondenceAssessment(
            assessment_id='ca-001',
            expected_reality='نصر زيد',
            observed_reality='لم ينصر زيد',
            domain=RealityDomain.EMPIRICAL,
            correspondence_status='NONE',
            failure_attribution='DATA',  # failure is in data, not the rule
        )
        assert ca.failure_attribution == 'DATA'
        assert ca.correspondence_status == 'NONE'

    def test_concept_contract_constructable(self):
        cc = ConceptContract(
            concept_id='cc-001',
            identity='الفعل الماضي',
            boundary='past tense verb form',
            domain=RealityDomain.MORPHOLOGICAL,
            intension='completed action in past time',
            extension='Deferred',
            evidence_rank='HYPOTHESIS',
        )
        assert cc.domain == 'MORPHOLOGICAL'

    def test_all_eleven_contracts_count(self):
        """Verify exactly 11 contract types are defined."""
        from pipeline.taaqol_integration import constitutional_contracts as cc
        contract_names = [
            'ClaimProvenance', 'ConceptContract', 'IfadahCandidate',
            'RealityDomain', 'DomainBridge', 'Assessment',
            'TransitionTrace', 'RepairDirective', 'ApplicationAssessment',
            'AuthorityCheck', 'CorrespondenceAssessment',
        ]
        for name in contract_names:
            assert hasattr(cc, name), f"Missing contract: {name}"


class TestNoParallelRegistry:
    """
    Guards for Repository Cleanliness and Constitutional Correctness.

    Policy (non-negotiable):
      1. strenum_compat.py must not exist anywhere in the repo.
      2. vendor/Taaqol-GPT/tests/conftest.py must not exist (it is untracked
         and was created by the incident — there is no "neutralised" state).
      3. .venv-py310-tmp must not exist.
      4. No StrEnum injection pattern in any .py file in the repo (Hokom tree
         AND vendor tree), except in this test file which holds the literal
         patterns as search strings.
      5. No parallel SCG stage registry (no P13, no SLGE_STAGE).
      6. constitutional_contracts.py must be pure types with no pipeline imports.

    There is no category called "neutralised prohibited file".
    raise ImportError is an active Python statement, not documentation.
    A file that must not exist must be absent, full stop.
    """

    # ── shared helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _repo_root() -> pathlib.Path:
        """Derive repo root from this file: tests/taaqol_integration/<this>.py"""
        return pathlib.Path(__file__).resolve().parent.parent.parent

    @staticmethod
    def _is_excluded_dir(part: str) -> bool:
        """Directories excluded from the content-injection scan."""
        SKIP = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 'dist', 'build'}
        return part in SKIP or part.startswith('.venv') or part in ('venv', 'env')

    # ── prohibited file existence ─────────────────────────────────────────────

    def test_strenum_compat_does_not_exist(self):
        """
        strenum_compat.py must not exist anywhere in the repository tree.
        It is an untracked file created by the incident. Its absence is the
        only acceptable state. There is no 'inert' or 'neutralised' variant.
        """
        repo_root = self._repo_root()
        matches = list(repo_root.rglob('strenum_compat.py'))
        # exclude venv dirs from the existence check too
        matches = [
            p for p in matches
            if not any(self._is_excluded_dir(part) for part in p.parts)
        ]
        assert not matches, (
            "strenum_compat.py must not exist. Found:\n"
            + "\n".join(str(p.relative_to(repo_root)) for p in matches)
        )

    def test_vendor_incident_conftest_does_not_exist(self):
        """
        vendor/Taaqol-GPT/tests/conftest.py must not exist.
        It was created by the incident (untracked) and has no legitimate
        role in the vendor tree. Absence is the only acceptable state.
        """
        repo_root = self._repo_root()
        prohibited = repo_root / 'vendor' / 'Taaqol-GPT' / 'tests' / 'conftest.py'
        assert not prohibited.exists(), (
            "vendor/Taaqol-GPT/tests/conftest.py must not exist. "
            "It was created by the incident. Delete it from the repo."
        )

    def test_venv_py310_tmp_does_not_exist(self):
        """
        .venv-py310-tmp must not exist. It was a mislabelled Python 3.10
        virtual environment created during the incident.
        """
        repo_root = self._repo_root()
        prohibited = repo_root / '.venv-py310-tmp'
        assert not prohibited.exists(), (
            ".venv-py310-tmp must not exist. "
            "It was a mislabelled venv created during the incident. "
            "Remove it: rm -rf .venv-py310-tmp"
        )

    # ── injection scan ────────────────────────────────────────────────────────

    def test_no_strEnum_injection_anywhere(self):
        """
        No StrEnum shim, backport, or monkey-patch in any .py file in the
        repository — including the vendor tree.

        Scan strategy:
          - Root: derived from __file__, never hardcoded.
          - Excludes: venv dirs, .git, __pycache__, .pytest_cache.
          - Does NOT exclude vendor — vendor is scanned for injection patterns.
          - Excludes THIS test file from the content scan only (it holds the
            literal pattern strings as search targets). All other files are
            scanned without exception.
          - No "neutralised" category: every match is a violation.
        """
        this_file = pathlib.Path(__file__).resolve()
        repo_root = self._repo_root()

        PROHIBITED_PATTERNS = [
            'strenum_compat',          # shim module reference
            'setattr(enum',            # monkey-patching enum module
            "sys.modules['enum']",     # direct sys.modules injection (single-quote)
            'sys.modules["enum"]',     # direct sys.modules injection (double-quote)
            'enum.StrEnum =',          # assignment into stdlib enum namespace
            'from strenum import',     # importing from the strenum backport package
        ]

        violations: list[str] = []

        for py_file in repo_root.rglob('*.py'):
            # Exclude virtual environments and tool caches
            if any(self._is_excluded_dir(part) for part in py_file.parts):
                continue
            # Exclude THIS test file from content scan only
            if py_file.resolve() == this_file:
                continue

            try:
                text = py_file.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue

            for pattern in PROHIBITED_PATTERNS:
                if pattern in text:
                    rel = py_file.relative_to(repo_root)
                    violations.append(f"{rel}: {pattern!r}")

        assert not violations, (
            "Prohibited StrEnum injection found:\n"
            + "\n".join(violations)
        )

    # ── parallel registry guard ───────────────────────────────────────────────

    def test_constitutional_contracts_has_no_scg_stages(self):
        """constitutional_contracts.py must not define P0-P12 re-indexing."""
        import pipeline.taaqol_integration.constitutional_contracts as cc
        src = inspect.getsource(cc)
        assert 'P13' not in src, "Amendment must not open P13"
        assert 'SLGE_STAGE' not in src, "SLGE stages are knowledge zones, not SCG replacements"

    def test_constitutional_contracts_has_no_pipeline_imports(self):
        """constitutional_contracts.py must be pure types with no pipeline dependencies."""
        import pipeline.taaqol_integration.constitutional_contracts as cc
        src = inspect.getsource(cc)
        assert 'from hokom_pipeline' not in src
        assert 'import hokom_pipeline' not in src
        assert 'from .admission_gate' not in src
        assert 'from .provider_models' not in src


class TestProvenanceIntegration:
    """Test that claim_adapter populates provenance when data is available."""

    def test_bundle_with_claim_id_gets_provenance(self):
        from pipeline.taaqol_integration.claim_adapter import bundle_from_hokom_result
        result = {
            'original': 'نَصَرَ',
            'verdict': 'ACCEPT',
            'claim_id': 'root:nasr:001',
            'trace_ids': ['trace-001'],
        }
        bundle = bundle_from_hokom_result(result)
        assert bundle.provenance is not None
        assert bundle.provenance.preserved_surface == 'نَصَرَ'
        assert bundle.provenance.claim_id == 'root:nasr:001'
        assert bundle.provenance.source_type == 'HOKOM_ROOT_ENGINE'

    def test_bundle_without_claim_id_has_no_provenance(self):
        from pipeline.taaqol_integration.claim_adapter import bundle_from_hokom_result
        result = {'original': 'هُوَ', 'verdict': 'DEFER'}
        bundle = bundle_from_hokom_result(result)
        assert bundle.provenance is None  # no claim_id to anchor provenance

    def test_provenance_domain_is_morphological(self):
        from pipeline.taaqol_integration.claim_adapter import bundle_from_hokom_result
        result = {
            'original': 'نَصَرَ',
            'verdict': 'ACCEPT',
            'claim_id': 'root:nasr:002',
        }
        bundle = bundle_from_hokom_result(result)
        assert bundle.provenance is not None
        assert bundle.provenance.domain == RealityDomain.MORPHOLOGICAL

    def test_bundle_backward_compatibility(self):
        """Existing bundles constructed without provenance still work."""
        from pipeline.taaqol_integration.provider_models import HokomLinguisticClaimBundle
        b = HokomLinguisticClaimBundle(
            claim_id='c1', token_id='t1', original_surface='test',
            normalized_surface='test', refined_host=None, lexical_class=None,
            part_of_speech=None, root_claim=None, wazn_claim=None, form_claim=None,
            masdar_claim=None, mushtaq_claims=(), inflection_claim=None,
            attachment_claims=(), domain_directive='DEFER', source_engine='HOKOM_ROOT_ENGINE',
            evidence_ids=(), trace_ids=(), active_residuals=(), resolved_residuals=(),
            catalog_versions=(), engine_version='2026.07.18',
        )
        assert b.provenance is None

    def test_admission_result_backward_compatibility(self):
        """Existing HokomTaaqolAdmissionResult constructed without assessment still works."""
        from pipeline.taaqol_integration.provider_models import (
            HokomTaaqolAdmissionResult, ProviderAdmissionResult,
        )
        pa = ProviderAdmissionResult(provider_id='X', admitted=True, violations=(), note='')
        a = HokomTaaqolAdmissionResult(
            claim_id='c1', verdict='DEFERRED', provider_admission=pa,
            identity_continuity='DEFER', evidence_verdict='MISSING',
            residual_verdict='CLEAR', gate_verdict='PENDING',
            native_entry_stage=None, stop_reason=None,
            trace_refs=(), active_residuals=(), resolved_residuals=(),
            taaqol_rank=None, gamma_result=None,
        )
        assert a.assessment is None


class TestStep6Status:
    """Step 6 is IMPLEMENTED_DEFERRED_ACTIVATION until Python 3.11 confirmed."""

    def test_step6_defers_on_python_310(self):
        """On Python 3.10, admission gate must report DEFERRED for native path."""
        if sys.version_info >= (3, 11):
            pytest.skip("Python 3.11+ -- native path may be APPROVED, not testing deferral")
        from pipeline.taaqol_integration.admission_gate import _NATIVE_AVAILABLE
        assert not _NATIVE_AVAILABLE, \
            "On Python 3.10, native taaqqul_slot_geometry must not be available without backport"

    def test_step6_implementation_code_present(self):
        """Step 6 implementation code must exist in admission_gate.py."""
        from pipeline.taaqol_integration import admission_gate
        src = inspect.getsource(admission_gate)
        assert '_try_native_admission' in src
        assert '_build_and_run_native_graph' in src
        assert 'DEFERRED' in src
        assert 'SlotGraph' in src
