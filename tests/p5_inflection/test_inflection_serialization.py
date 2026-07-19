#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p5_inflection/test_inflection_serialization.py
Serialization round-trip tests for HOKOM-INFLECTION-PARADIGM-OWNERSHIP-01.
Verifies Phase5Result and InflectionOwnershipGate can be serialized to JSON.
"""
import json
import dataclasses
import pytest

from pipeline.p5_inflection.phase5_orchestrator import project_inflection_with_licensing
from pipeline.p5_inflection.models import (
    InflectionOwnershipGate,
    Phase5Result,
    InflectionalForm,
)


_ARGS_SOUND = dict(
    surface='نَصَرَ',
    root=('ن', 'ص', 'ر'),
    bab_id='BAB_I_NASARA',
    form_family=None,
    wazn_id='FA_A_LA',
    morphology_path='verbal_root_path',
    phase4a_result=None,
    phase4b_result=None,
    attachment=None,
)

_ARGS_NOT_APPLICABLE = dict(
    surface='كتاب',
    root=None,
    bab_id=None,
    form_family=None,
    wazn_id=None,
    morphology_path='nominal_morphology_path',
    phase4a_result=None,
    phase4b_result=None,
    attachment=None,
)


class TestPhase5ResultSerialization:
    """Phase5Result.to_dict() must produce a JSON-serializable structure."""

    def test_to_dict_returns_dict(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        d = result.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_not_applicable_result(self):
        result = project_inflection_with_licensing(**_ARGS_NOT_APPLICABLE)
        d = result.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_has_initial_directive(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        d = result.to_dict()
        assert 'initial_directive' in d

    def test_to_dict_has_final_directive(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        d = result.to_dict()
        assert 'final_directive' in d

    def test_to_dict_has_source_path(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        d = result.to_dict()
        assert 'source_path' in d

    def test_to_dict_values_correct(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        d = result.to_dict()
        assert d['initial_directive'] == result.initial_directive
        assert d['final_directive'] == result.final_directive
        assert d['source_path'] == result.source_path

    def test_to_dict_is_json_serializable(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        d = result.to_dict()
        serialized = json.dumps(d)
        assert isinstance(serialized, str)

    def test_to_dict_json_round_trip_source_path(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        d = result.to_dict()
        recovered = json.loads(json.dumps(d))
        assert recovered['source_path'] == d['source_path']

    def test_to_dict_json_round_trip_directives(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        d = result.to_dict()
        recovered = json.loads(json.dumps(d))
        assert recovered['initial_directive'] == d['initial_directive']
        assert recovered['final_directive'] == d['final_directive']

    def test_to_dict_not_applicable_json_serializable(self):
        result = project_inflection_with_licensing(**_ARGS_NOT_APPLICABLE)
        d = result.to_dict()
        serialized = json.dumps(d)
        recovered = json.loads(serialized)
        assert recovered['initial_directive'] == 'NOT_APPLICABLE'

    def test_inflectional_form_in_to_dict_when_present(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        d = result.to_dict()
        assert 'inflectional_form' in d
        if result.inflectional_form is not None:
            assert d['inflectional_form'] is not None
            assert isinstance(d['inflectional_form'], dict)

    def test_inflectional_form_dict_has_surface(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        d = result.to_dict()
        if d.get('inflectional_form') is not None:
            assert 'surface' in d['inflectional_form']


class TestInflectionalFormSerialization:
    """InflectionalForm.to_dict() must also be JSON-serializable."""

    def test_inflectional_form_has_to_dict(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        if result.inflectional_form is not None:
            assert hasattr(result.inflectional_form, 'to_dict')
            assert callable(result.inflectional_form.to_dict)

    def test_inflectional_form_to_dict_returns_dict(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        if result.inflectional_form is not None:
            d = result.inflectional_form.to_dict()
            assert isinstance(d, dict)

    def test_inflectional_form_to_dict_json_serializable(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        if result.inflectional_form is not None:
            d = result.inflectional_form.to_dict()
            serialized = json.dumps(d)
            assert isinstance(serialized, str)


class TestGateSerialization:
    """InflectionOwnershipGate.to_dict() must round-trip through JSON."""

    def setup_method(self):
        self.gate = InflectionOwnershipGate()

    def test_to_dict_returns_dict(self):
        d = self.gate.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_has_status(self):
        d = self.gate.to_dict()
        assert 'status' in d
        assert d['status'] == 'CLOSED'

    def test_to_dict_has_parallel_engines(self):
        d = self.gate.to_dict()
        assert 'parallel_engines' in d
        assert d['parallel_engines'] == 0

    def test_to_dict_has_external_dependencies(self):
        d = self.gate.to_dict()
        assert 'external_dependencies' in d
        assert d['external_dependencies'] == 0

    def test_to_dict_has_canonical_owner(self):
        d = self.gate.to_dict()
        assert 'canonical_owner' in d
        assert d['canonical_owner'] == 'HOKOM'

    def test_to_dict_has_engine_id(self):
        d = self.gate.to_dict()
        assert 'engine_id' in d
        assert d['engine_id'] == 'HOKOM_INFLECTION_ENGINE'

    def test_to_dict_is_json_serializable(self):
        d = self.gate.to_dict()
        serialized = json.dumps(d)
        assert isinstance(serialized, str)

    def test_to_dict_round_trips_status(self):
        d = self.gate.to_dict()
        recovered = json.loads(json.dumps(d))
        assert recovered['status'] == 'CLOSED'

    def test_to_dict_round_trips_engine_id(self):
        d = self.gate.to_dict()
        recovered = json.loads(json.dumps(d))
        assert recovered['engine_id'] == 'HOKOM_INFLECTION_ENGINE'

    def test_to_dict_round_trips_canonical_owner(self):
        d = self.gate.to_dict()
        recovered = json.loads(json.dumps(d))
        assert recovered['canonical_owner'] == 'HOKOM'

    def test_to_dict_round_trips_parallel_engines(self):
        d = self.gate.to_dict()
        recovered = json.loads(json.dumps(d))
        assert recovered['parallel_engines'] == 0

    def test_to_dict_round_trips_modification_counters(self):
        d = self.gate.to_dict()
        recovered = json.loads(json.dumps(d))
        assert recovered['p5_masdar_modifications'] == 0
        assert recovered['p6_derivatives_modifications'] == 0
        assert recovered['p4_wazn_modifications'] == 0
        assert recovered['hokom_pipeline_modifications'] == 0
        assert recovered['taaqol_submodule_modifications'] == 0

    def test_to_dict_keys_are_consistent_across_calls(self):
        d1 = self.gate.to_dict()
        d2 = InflectionOwnershipGate().to_dict()
        assert set(d1.keys()) == set(d2.keys())

    def test_to_dict_values_match_across_calls(self):
        d1 = self.gate.to_dict()
        d2 = InflectionOwnershipGate().to_dict()
        assert d1 == d2
