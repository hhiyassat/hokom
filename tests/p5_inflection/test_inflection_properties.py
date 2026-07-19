#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p5_inflection/test_inflection_properties.py
Property-based ownership tests for HOKOM-INFLECTION-PARADIGM-OWNERSHIP-01.
Verifies determinism, immutability, and gate consistency.
"""
import copy
import pytest

from pipeline.p5_inflection.phase5_orchestrator import project_inflection_with_licensing
from pipeline.p5_inflection.models import (
    INFLECTION_ENGINE_ID,
    INFLECTION_CANONICAL_OWNER,
    InflectionOwnershipGate,
    Phase5Result,
)


# Representative call args used across property tests
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

_ARGS_IMPERFECT = dict(
    surface='يَنْصُرُ',
    root=('ن', 'ص', 'ر'),
    bab_id='BAB_I_NASARA',
    form_family=None,
    wazn_id=None,
    morphology_path='verbal_root_path',
    phase4a_result=None,
    phase4b_result=None,
    attachment=None,
)

_ARGS_NOMINAL = dict(
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


class TestDeterminism:
    """Same input → same output on every call."""

    def test_sound_past_deterministic(self):
        r1 = project_inflection_with_licensing(**_ARGS_SOUND)
        r2 = project_inflection_with_licensing(**_ARGS_SOUND)
        assert r1 == r2

    def test_imperfect_deterministic(self):
        r1 = project_inflection_with_licensing(**_ARGS_IMPERFECT)
        r2 = project_inflection_with_licensing(**_ARGS_IMPERFECT)
        assert r1 == r2

    def test_nominal_not_applicable_deterministic(self):
        r1 = project_inflection_with_licensing(**_ARGS_NOMINAL)
        r2 = project_inflection_with_licensing(**_ARGS_NOMINAL)
        assert r1 == r2

    def test_source_path_deterministic(self):
        r1 = project_inflection_with_licensing(**_ARGS_SOUND)
        r2 = project_inflection_with_licensing(**_ARGS_SOUND)
        assert r1.source_path == r2.source_path

    def test_evidence_ids_deterministic(self):
        r1 = project_inflection_with_licensing(**_ARGS_SOUND)
        r2 = project_inflection_with_licensing(**_ARGS_SOUND)
        assert r1.evidence_ids == r2.evidence_ids

    def test_residual_codes_deterministic(self):
        r1 = project_inflection_with_licensing(**_ARGS_SOUND)
        r2 = project_inflection_with_licensing(**_ARGS_SOUND)
        assert r1.residual_codes == r2.residual_codes

    def test_multiple_calls_identical(self):
        results = [project_inflection_with_licensing(**_ARGS_SOUND) for _ in range(5)]
        for r in results[1:]:
            assert r == results[0]


class TestInputPreservation:
    """Input arguments must not be mutated by the function."""

    def test_root_tuple_not_mutated(self):
        args = dict(_ARGS_SOUND)
        original_root = args['root']
        project_inflection_with_licensing(**args)
        assert args['root'] == original_root

    def test_surface_string_not_mutated(self):
        args = dict(_ARGS_SOUND)
        original_surface = args['surface']
        project_inflection_with_licensing(**args)
        assert args['surface'] == original_surface

    def test_none_args_remain_none(self):
        args = dict(_ARGS_SOUND)
        project_inflection_with_licensing(**args)
        assert args['form_family'] is None
        assert args['phase4a_result'] is None
        assert args['phase4b_result'] is None
        assert args['attachment'] is None


class TestOutputImmutability:
    """Phase5Result must be a frozen dataclass — no mutation after creation."""

    def test_result_is_frozen(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        with pytest.raises((TypeError, AttributeError)):
            result.initial_directive = 'WRONG'  # type: ignore

    def test_inflectional_form_is_frozen(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        if result.inflectional_form is not None:
            with pytest.raises((TypeError, AttributeError)):
                result.inflectional_form.surface = 'WRONG'  # type: ignore

    def test_paradigm_candidate_is_frozen(self):
        result = project_inflection_with_licensing(**_ARGS_SOUND)
        if result.paradigm_candidate is not None:
            with pytest.raises((TypeError, AttributeError)):
                result.paradigm_candidate.paradigm_id = 'WRONG'  # type: ignore


class TestGateConsistency:
    """InflectionOwnershipGate.is_closed() must always return True."""

    def test_gate_closed_first_call(self):
        assert InflectionOwnershipGate().is_closed() is True

    def test_gate_closed_second_call(self):
        assert InflectionOwnershipGate().is_closed() is True

    def test_gate_closed_independent_instances(self):
        g1 = InflectionOwnershipGate()
        g2 = InflectionOwnershipGate()
        assert g1.is_closed() == g2.is_closed()

    def test_gate_instances_are_equal(self):
        g1 = InflectionOwnershipGate()
        g2 = InflectionOwnershipGate()
        assert g1 == g2

    def test_gate_status_never_changes(self):
        gates = [InflectionOwnershipGate() for _ in range(10)]
        statuses = {g.status for g in gates}
        assert statuses == {'CLOSED'}

    def test_gate_parallel_engines_always_zero(self):
        gates = [InflectionOwnershipGate() for _ in range(5)]
        for g in gates:
            assert g.parallel_engines == 0


class TestNoParallelEngine:
    """Only one canonical inflection engine should exist."""

    def test_engine_id_is_unique_constant(self):
        assert INFLECTION_ENGINE_ID == 'HOKOM_INFLECTION_ENGINE'

    def test_canonical_owner_is_hokom(self):
        assert INFLECTION_CANONICAL_OWNER == 'HOKOM'

    def test_gate_reports_zero_parallel_engines(self):
        assert InflectionOwnershipGate().parallel_engines == 0

    def test_gate_reports_zero_external_dependencies(self):
        assert InflectionOwnershipGate().external_dependencies == 0


class TestParadigmOrderingStability:
    """Paradigm fields in repeated calls must appear in the same order."""

    def test_inflectional_form_affixes_order_stable(self):
        r1 = project_inflection_with_licensing(**_ARGS_SOUND)
        r2 = project_inflection_with_licensing(**_ARGS_SOUND)
        if r1.inflectional_form and r2.inflectional_form:
            assert r1.inflectional_form.suffixes == r2.inflectional_form.suffixes
            assert r1.inflectional_form.prefixes == r2.inflectional_form.prefixes

    def test_evidence_ids_order_stable(self):
        r1 = project_inflection_with_licensing(**_ARGS_SOUND)
        r2 = project_inflection_with_licensing(**_ARGS_SOUND)
        assert list(r1.evidence_ids) == list(r2.evidence_ids)

    def test_residual_codes_order_stable(self):
        r1 = project_inflection_with_licensing(**_ARGS_SOUND)
        r2 = project_inflection_with_licensing(**_ARGS_SOUND)
        assert list(r1.residual_codes) == list(r2.residual_codes)
