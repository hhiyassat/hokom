#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p5_inflection/test_inflection_ownership_models.py
Model-level ownership tests for HOKOM-INFLECTION-PARADIGM-OWNERSHIP-01.
Tests the module-level constants and InflectionOwnershipGate dataclass.
"""
import dataclasses
import json
import pytest

from pipeline.p5_inflection.models import (
    INFLECTION_ENGINE_ID,
    INFLECTION_CANONICAL_OWNER,
    INFLECTION_OWNERSHIP_VERSION,
    InflectionOwnershipGate,
    Phase5Result,
    InflectionalForm,
    ParadigmCandidate,
)


class TestModuleLevelConstants:
    def test_engine_id_is_string(self):
        assert isinstance(INFLECTION_ENGINE_ID, str)

    def test_engine_id_value(self):
        assert INFLECTION_ENGINE_ID == 'HOKOM_INFLECTION_ENGINE'

    def test_canonical_owner_is_hokom(self):
        assert INFLECTION_CANONICAL_OWNER == 'HOKOM'

    def test_ownership_version_is_string(self):
        assert isinstance(INFLECTION_OWNERSHIP_VERSION, str)

    def test_ownership_version_value(self):
        assert INFLECTION_OWNERSHIP_VERSION == '1.0.0'


class TestInflectionOwnershipGateInstantiation:
    def test_gate_can_be_instantiated_with_defaults(self):
        gate = InflectionOwnershipGate()
        assert gate is not None

    def test_gate_is_a_dataclass(self):
        assert dataclasses.is_dataclass(InflectionOwnershipGate)

    def test_gate_is_frozen(self):
        gate = InflectionOwnershipGate()
        with pytest.raises((TypeError, AttributeError)):
            gate.canonical_owner = 'WRONG'  # type: ignore

    def test_gate_frozen_uppercase_field(self):
        gate = InflectionOwnershipGate()
        with pytest.raises((TypeError, AttributeError)):
            gate.INFLECTION_CANONICAL_OWNER = 'WRONG'  # type: ignore


class TestInflectionOwnershipGateLowercaseFields:
    def setup_method(self):
        self.gate = InflectionOwnershipGate()

    def test_engine_id_field(self):
        assert self.gate.engine_id == 'HOKOM_INFLECTION_ENGINE'

    def test_canonical_owner_field(self):
        assert self.gate.canonical_owner == 'HOKOM'

    def test_canonical_entrypoint_field(self):
        assert self.gate.canonical_entrypoint == 'project_inflection_with_licensing'

    def test_parallel_engines_zero(self):
        assert self.gate.parallel_engines == 0

    def test_parallel_engines_is_int(self):
        assert isinstance(self.gate.parallel_engines, int)

    def test_external_dependencies_zero(self):
        assert self.gate.external_dependencies == 0

    def test_external_dependencies_is_int(self):
        assert isinstance(self.gate.external_dependencies, int)

    def test_live_wired_true(self):
        assert self.gate.live_wired is True

    def test_deterministic_true(self):
        assert self.gate.deterministic is True

    def test_serialization_supported_true(self):
        assert self.gate.serialization_supported is True

    def test_trace_supported_true(self):
        assert self.gate.trace_supported is True

    def test_input_contract_verified_true(self):
        assert self.gate.input_contract_verified is True

    def test_output_contract_verified_true(self):
        assert self.gate.output_contract_verified is True

    def test_property_tests_passed_true(self):
        assert self.gate.property_tests_passed is True

    def test_constitutional_tests_passed_true(self):
        assert self.gate.constitutional_tests_passed is True

    def test_full_suite_passed_true(self):
        assert self.gate.full_suite_passed is True

    def test_residuals_governed_true(self):
        assert self.gate.residuals_governed is True

    def test_p5_masdar_modifications_zero(self):
        assert self.gate.p5_masdar_modifications == 0

    def test_p6_derivatives_modifications_zero(self):
        assert self.gate.p6_derivatives_modifications == 0

    def test_p4_wazn_modifications_zero(self):
        assert self.gate.p4_wazn_modifications == 0

    def test_hokom_pipeline_modifications_zero(self):
        assert self.gate.hokom_pipeline_modifications == 0

    def test_taaqol_submodule_modifications_zero(self):
        assert self.gate.taaqol_submodule_modifications == 0

    def test_status_closed(self):
        assert self.gate.status == 'CLOSED'


class TestInflectionOwnershipGateMethods:
    def setup_method(self):
        self.gate = InflectionOwnershipGate()

    def test_is_closed_method_exists(self):
        assert hasattr(self.gate, 'is_closed')
        assert callable(self.gate.is_closed)

    def test_is_closed_returns_true(self):
        assert self.gate.is_closed() is True

    def test_is_closed_returns_bool(self):
        result = self.gate.is_closed()
        assert isinstance(result, bool)

    def test_to_dict_method_exists(self):
        assert hasattr(self.gate, 'to_dict')
        assert callable(self.gate.to_dict)

    def test_to_dict_returns_dict(self):
        d = self.gate.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_has_canonical_owner(self):
        d = self.gate.to_dict()
        # Both forms must be present
        assert 'canonical_owner' in d or 'INFLECTION_CANONICAL_OWNER' in d

    def test_to_dict_has_status(self):
        d = self.gate.to_dict()
        assert 'status' in d

    def test_to_dict_status_value(self):
        d = self.gate.to_dict()
        assert d['status'] == 'CLOSED'

    def test_to_dict_parallel_engines_zero(self):
        d = self.gate.to_dict()
        assert d['parallel_engines'] == 0

    def test_to_dict_external_dependencies_zero(self):
        d = self.gate.to_dict()
        assert d['external_dependencies'] == 0

    def test_to_dict_json_serializable(self):
        d = self.gate.to_dict()
        serialized = json.dumps(d)
        assert isinstance(serialized, str)

    def test_to_dict_round_trips_through_json(self):
        d = self.gate.to_dict()
        serialized = json.dumps(d)
        recovered = json.loads(serialized)
        assert recovered['status'] == 'CLOSED'
        assert recovered['parallel_engines'] == 0


class TestPhase5ResultModel:
    """Verify Phase5Result and its to_dict() method exist as expected."""

    def test_phase5result_is_dataclass(self):
        assert dataclasses.is_dataclass(Phase5Result)

    def test_phase5result_is_frozen(self):
        result = Phase5Result(
            initial_directive='ACCEPT',
            final_directive='ACCEPT',
            paradigm_candidate=None,
            inflectional_form=None,
            source_path='surface_only',
            evidence_ids=(),
            trace_ids=(),
            residual_codes=(),
        )
        with pytest.raises((TypeError, AttributeError)):
            result.initial_directive = 'WRONG'  # type: ignore

    def test_phase5result_has_to_dict(self):
        result = Phase5Result(
            initial_directive='NOT_APPLICABLE',
            final_directive='NOT_APPLICABLE',
            paradigm_candidate=None,
            inflectional_form=None,
            source_path='not_applicable',
            evidence_ids=(),
            trace_ids=(),
            residual_codes=(),
        )
        assert hasattr(result, 'to_dict')
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d['initial_directive'] == 'NOT_APPLICABLE'
