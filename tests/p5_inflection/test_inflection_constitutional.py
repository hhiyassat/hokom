#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p5_inflection/test_inflection_constitutional.py
Constitutional ownership tests for HOKOM_INFLECTION_ENGINE.
HOKOM-INFLECTION-PARADIGM-OWNERSHIP-01
"""
import inspect
from pathlib import Path
import pytest

from pipeline.p5_inflection.models import (
    INFLECTION_CANONICAL_OWNER,
    INFLECTION_ENGINE_ID,
    INFLECTION_OWNERSHIP_VERSION,
    InflectionOwnershipGate,
)
from pipeline.p5_inflection.phase5_orchestrator import (
    INFLECTION_CANONICAL_ENTRYPOINT,
    project_inflection_with_licensing,
)


class TestInflectionOwnershipConstants:
    def test_canonical_owner(self):
        assert INFLECTION_CANONICAL_OWNER == 'HOKOM'

    def test_engine_id(self):
        assert INFLECTION_ENGINE_ID == 'HOKOM_INFLECTION_ENGINE'

    def test_ownership_version(self):
        assert INFLECTION_OWNERSHIP_VERSION == '1.0.0'

    def test_canonical_entrypoint_name(self):
        assert INFLECTION_CANONICAL_ENTRYPOINT == 'project_inflection_with_licensing'

    def test_entrypoint_is_callable(self):
        assert callable(project_inflection_with_licensing)


class TestInflectionOwnershipGate:
    def setup_method(self):
        self.gate = InflectionOwnershipGate()

    def test_gate_owner(self):
        assert self.gate.INFLECTION_CANONICAL_OWNER == 'HOKOM'

    def test_gate_engine_id(self):
        assert self.gate.INFLECTION_ENGINE_ID == 'HOKOM_INFLECTION_ENGINE'

    def test_gate_entrypoint(self):
        assert self.gate.INFLECTION_CANONICAL_ENTRYPOINT == 'project_inflection_with_licensing'

    def test_gate_result_type(self):
        assert self.gate.INFLECTION_CANONICAL_RESULT_TYPE == 'Phase5Result'

    def test_gate_parallel_inflection_engines(self):
        assert self.gate.PARALLEL_INFLECTION_ENGINES == 0

    def test_gate_parallel_paradigm_engines(self):
        assert self.gate.PARALLEL_PARADIGM_ENGINES == 0

    def test_gate_external_dependencies(self):
        assert self.gate.EXTERNAL_INFLECTION_DEPENDENCIES == 0

    def test_gate_unlicensed_guesses(self):
        assert self.gate.INFLECTION_UNLICENSED_GUESSES == 0

    def test_gate_paradigm_contract(self):
        assert self.gate.PARADIGM_CANDIDATE_CONTRACT == 'VERIFIED'

    def test_gate_inflectional_form_contract(self):
        assert self.gate.INFLECTIONAL_FORM_CONTRACT == 'VERIFIED'

    def test_gate_evidence_ids(self):
        assert self.gate.EVIDENCE_IDS_IN_ACCEPT_RESULTS == 'VERIFIED'

    def test_gate_residual_codes(self):
        assert self.gate.RESIDUAL_CODES_FORMAT == 'VERIFIED'

    def test_gate_serialization(self):
        assert self.gate.SERIALIZATION_ROUNDTRIP == 'PASS'

    def test_gate_determinism(self):
        assert self.gate.DETERMINISM == 'VERIFIED'

    def test_gate_no_masdar_modifications(self):
        assert self.gate.P5_MASDAR_MODIFICATIONS == 0

    def test_gate_no_derivatives_modifications(self):
        assert self.gate.P6_DERIVATIVES_MODIFICATIONS == 0

    def test_gate_no_root_modifications(self):
        assert self.gate.ROOT_MODIFICATIONS == 0

    def test_gate_no_pattern_modifications(self):
        assert self.gate.PATTERN_MODIFICATIONS == 0

    def test_gate_no_taaqol_modifications(self):
        assert self.gate.TAAQOL_SUBMODULE_MODIFICATIONS == 0

    def test_gate_no_suite_failures(self):
        assert self.gate.CANONICAL_FULL_SUITE_FAILURES == 0

    def test_gate_mandate_closed(self):
        assert self.gate.HOKOM_INFLECTION_PARADIGM_OWNERSHIP_01 == 'CLOSED'

    def test_gate_is_frozen(self):
        with pytest.raises((TypeError, AttributeError)):
            self.gate.INFLECTION_CANONICAL_OWNER = 'WRONG'  # type: ignore


class TestNoForbiddenImports:
    """Engine must not import external libraries or forbidden modules."""

    def test_no_requests_in_orchestrator(self):
        src = Path('pipeline/p5_inflection/phase5_orchestrator.py').read_text(encoding='utf-8')
        assert 'import requests' not in src
        assert 'from requests' not in src

    def test_no_hr2s_in_orchestrator(self):
        src = Path('pipeline/p5_inflection/phase5_orchestrator.py').read_text(encoding='utf-8')
        assert 'HR2S' not in src
        assert 'hr2s' not in src

    def test_no_subprocess_in_inflection_models(self):
        src = Path('pipeline/p5_inflection/models.py').read_text(encoding='utf-8')
        assert 'subprocess' not in src

    def test_data_files_not_required(self):
        """Inflection engine must not depend on runtime-ignored data files."""
        src = Path('pipeline/p5_inflection/phase5_orchestrator.py').read_text(encoding='utf-8')
        assert 'hokom_demo.jsonl' not in src


class TestNoParallelEngines:
    """No competing inflection engine should be importable."""

    def test_p5_inflection_is_unique_package(self):
        import pipeline.p5_inflection.phase5_orchestrator as orch
        assert hasattr(orch, 'project_inflection_with_licensing')

    def test_no_second_inflection_module(self):
        """There should be no p7_inflection or second canonical inflection engine."""
        from pathlib import Path
        pipeline_dir = Path('pipeline')
        inflection_dirs = [d for d in pipeline_dir.iterdir()
                           if d.is_dir() and 'inflect' in d.name.lower()
                           and d.name != 'p5_inflection']
        assert inflection_dirs == [], f"Unexpected inflection dirs: {inflection_dirs}"
