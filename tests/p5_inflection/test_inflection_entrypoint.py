#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p5_inflection/test_inflection_entrypoint.py
Canonical entrypoint tests for HOKOM-INFLECTION-PARADIGM-OWNERSHIP-01.
Verifies project_inflection_with_licensing() signature, call site, and result type.
"""
import inspect
import pytest

import pipeline.p5_inflection.phase5_orchestrator as orch
from pipeline.p5_inflection.phase5_orchestrator import (
    INFLECTION_CANONICAL_ENTRYPOINT,
    INFLECTION_CANONICAL_ENTRYPOINT_MODULE,
    project_inflection_with_licensing,
)
from pipeline.p5_inflection.models import Phase5Result


class TestCanonicalEntrypointConstants:
    def test_canonical_entrypoint_name(self):
        assert INFLECTION_CANONICAL_ENTRYPOINT == 'project_inflection_with_licensing'

    def test_canonical_entrypoint_module(self):
        assert INFLECTION_CANONICAL_ENTRYPOINT_MODULE == 'pipeline.p5_inflection.phase5_orchestrator'

    def test_entrypoint_module_is_string(self):
        assert isinstance(INFLECTION_CANONICAL_ENTRYPOINT_MODULE, str)

    def test_entrypoint_constant_is_string(self):
        assert isinstance(INFLECTION_CANONICAL_ENTRYPOINT, str)


class TestCanonicalEntrypointCallable:
    def test_is_callable(self):
        assert callable(project_inflection_with_licensing)

    def test_is_function(self):
        assert inspect.isfunction(project_inflection_with_licensing)

    def test_accessible_from_module(self):
        assert hasattr(orch, 'project_inflection_with_licensing')

    def test_name_matches_constant(self):
        assert project_inflection_with_licensing.__name__ == INFLECTION_CANONICAL_ENTRYPOINT


class TestCanonicalEntrypointSignature:
    """The function must accept the same kwargs that hokom_pipeline.py passes."""

    def test_has_surface_parameter(self):
        sig = inspect.signature(project_inflection_with_licensing)
        assert 'surface' in sig.parameters

    def test_has_root_parameter(self):
        sig = inspect.signature(project_inflection_with_licensing)
        assert 'root' in sig.parameters

    def test_has_bab_id_parameter(self):
        sig = inspect.signature(project_inflection_with_licensing)
        assert 'bab_id' in sig.parameters

    def test_has_form_family_parameter(self):
        sig = inspect.signature(project_inflection_with_licensing)
        assert 'form_family' in sig.parameters

    def test_has_wazn_id_parameter(self):
        sig = inspect.signature(project_inflection_with_licensing)
        assert 'wazn_id' in sig.parameters

    def test_has_morphology_path_parameter(self):
        sig = inspect.signature(project_inflection_with_licensing)
        assert 'morphology_path' in sig.parameters

    def test_has_phase4a_result_parameter(self):
        sig = inspect.signature(project_inflection_with_licensing)
        assert 'phase4a_result' in sig.parameters

    def test_has_phase4b_result_parameter(self):
        sig = inspect.signature(project_inflection_with_licensing)
        assert 'phase4b_result' in sig.parameters

    def test_has_attachment_parameter(self):
        sig = inspect.signature(project_inflection_with_licensing)
        assert 'attachment' in sig.parameters

    def test_all_params_after_surface_have_defaults(self):
        sig = inspect.signature(project_inflection_with_licensing)
        params = list(sig.parameters.values())
        # surface is the first param, all others should have defaults
        for param in params[1:]:
            assert param.default is not inspect.Parameter.empty, (
                f"Parameter {param.name!r} lacks a default"
            )


class TestCanonicalEntrypointCallSite:
    """Call the function with the exact same kwargs that hokom_pipeline.py uses."""

    # Mirrors line 356-366 of hokom_pipeline.py with minimal valid args
    _SOUND_SURFACE = 'نَصَرَ'

    def test_call_with_surface_only_returns_phase5result(self):
        result = project_inflection_with_licensing(surface=self._SOUND_SURFACE)
        assert isinstance(result, Phase5Result)

    def test_call_returns_non_none(self):
        result = project_inflection_with_licensing(surface=self._SOUND_SURFACE)
        assert result is not None

    def test_call_with_empty_surface_returns_defer(self):
        result = project_inflection_with_licensing(surface='')
        assert result.final_directive == 'DEFER'

    def test_call_with_nominal_path_returns_not_applicable(self):
        result = project_inflection_with_licensing(
            surface='كتاب',
            morphology_path='nominal_morphology_path',
        )
        assert result.final_directive == 'NOT_APPLICABLE'
        assert result.source_path == 'not_applicable'

    def test_call_with_known_sound_root(self):
        result = project_inflection_with_licensing(
            surface='نَصَرَ',
            root=('ن', 'ص', 'ر'),
            bab_id='BAB_I_NASARA',
            morphology_path='verbal_root_path',
        )
        assert isinstance(result, Phase5Result)
        assert result.initial_directive == 'ACCEPT'

    def test_call_with_all_kwargs_mirroring_pipeline(self):
        """Mirrors the exact keyword arg names from hokom_pipeline.py lines 356-366."""
        result = project_inflection_with_licensing(
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
        assert isinstance(result, Phase5Result)

    def test_result_has_required_attributes(self):
        result = project_inflection_with_licensing(surface='نَصَرَ')
        assert hasattr(result, 'initial_directive')
        assert hasattr(result, 'final_directive')
        assert hasattr(result, 'paradigm_candidate')
        assert hasattr(result, 'inflectional_form')
        assert hasattr(result, 'source_path')
        assert hasattr(result, 'evidence_ids')
        assert hasattr(result, 'trace_ids')
        assert hasattr(result, 'residual_codes')

    def test_result_has_to_dict(self):
        result = project_inflection_with_licensing(surface='نَصَرَ')
        assert hasattr(result, 'to_dict')
        d = result.to_dict()
        assert isinstance(d, dict)


class TestNoParallelEntrypoints:
    """Only one inflection entrypoint should exist in the canonical module."""

    def test_no_second_inflection_function_exported(self):
        """project_inflection_with_licensing is the single canonical function."""
        inflection_fns = [
            name for name, obj in inspect.getmembers(orch, inspect.isfunction)
            if 'inflect' in name.lower() or 'paradigm' in name.lower()
        ]
        # There may be private helpers; the canonical one must be present
        assert 'project_inflection_with_licensing' in inflection_fns

    def test_private_helpers_are_not_canonical(self):
        """Functions prefixed with _ are helpers, not competing entrypoints."""
        public_inflection_fns = [
            name for name, obj in inspect.getmembers(orch, inspect.isfunction)
            if ('inflect' in name.lower() or 'paradigm' in name.lower())
            and not name.startswith('_')
        ]
        assert public_inflection_fns == ['project_inflection_with_licensing']
