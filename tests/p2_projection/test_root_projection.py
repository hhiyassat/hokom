#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p2_projection/test_root_projection.py — RootProjection P2 (R-10)

يغطّي قواعد الإسقاط:
  ACCEPT/DEFER/BLOCK، عدم استدعاء HR2S (NOT_OPENED)، أمان UnknownRadical،
  حفظ ء، حفظ ا/ى منعًا كهوية، حفظ evidence/trace/residual، تسلسل JSON،
  عدم استيراد hr2s داخليًا.
"""

from __future__ import annotations

import ast
import json
import pathlib

import pytest

from pipeline.integrations.hr2s_root_adapter import ExternalRadical, ExternalRootAnalysis
from pipeline.p2_projection.root_projection import (
    RootProjection,
    RootProjectionContractError,
)


# ── أدوات بناء ExternalRootAnalysis مباشرة (بلا محرّك) ─────────────────────────

def _rad(identity, position, resolved=True, surface_form=None, candidates=()):
    return ExternalRadical(
        identity=identity if resolved else None,
        surface_form=surface_form or identity,
        position=position,
        resolved=resolved,
        candidates=tuple(candidates),
    )


def _ext(directive, stage_state, radicals=(), *, profile=None,
         evidence=(), trace=(), residual=(), surface='ضَرَبَ', version='9.9'):
    return ExternalRootAnalysis(
        surface=surface,
        directive=directive,
        stage_state=stage_state,
        canonical_radicals=tuple(radicals),
        root_profile=dict(profile or {}),
        evidence_ids=tuple(evidence),
        trace_ids=tuple(trace),
        residual_codes=tuple(residual),
        source_engine='hr2s_morphology',
        source_version=version,
    )


_DARABA = [_rad('ض', 'FA'), _rad('ر', 'AYN'), _rad('ب', 'LAM')]


# ══════════════════════════════════════════════════════════════════════════════
# 1. ACCEPT
# ══════════════════════════════════════════════════════════════════════════════

class TestAcceptProjection:
    def test_accept_populates_canonical_root(self):
        p = RootProjection.from_external_root(_ext('ACCEPT', 'COMPLETED', _DARABA))
        assert p.directive == 'ACCEPT'
        assert p.canonical_root == ('ض', 'ر', 'ب')

    def test_accept_stage_state_opened(self):
        p = RootProjection.from_external_root(_ext('ACCEPT', 'COMPLETED', _DARABA))
        assert p.stage_state == 'OPENED'

    def test_accept_no_unresolved_positions(self):
        p = RootProjection.from_external_root(_ext('ACCEPT', 'COMPLETED', _DARABA))
        assert p.unresolved_positions == ()

    def test_accept_hamza_identity_preserved(self):
        # قَرَأَ → ء محفوظة كهوية جذرية (لا أ)
        rads = [_rad('ق', 'FA'), _rad('ر', 'AYN'), _rad('ء', 'LAM', surface_form='أَ')]
        p = RootProjection.from_external_root(_ext('ACCEPT', 'COMPLETED', rads, surface='قَرَأَ'))
        assert p.canonical_root == ('ق', 'ر', 'ء')
        assert 'أ' not in p.canonical_root

    def test_accept_doubled_root(self):
        # مَدَّ → (م، د، د)
        rads = [_rad('م', 'FA'), _rad('د', 'AYN'), _rad('د', 'LAM')]
        p = RootProjection.from_external_root(_ext('ACCEPT', 'COMPLETED', rads, surface='مَدَّ'))
        assert p.canonical_root == ('م', 'د', 'د')


# ══════════════════════════════════════════════════════════════════════════════
# 2. ACCEPT contract violations
# ══════════════════════════════════════════════════════════════════════════════

class TestAcceptContractErrors:
    def test_accept_with_unknown_radical_raises(self):
        rads = [_rad('ض', 'FA'), _rad(None, 'AYN', resolved=False), _rad('ب', 'LAM')]
        with pytest.raises(RootProjectionContractError):
            RootProjection.from_external_root(_ext('ACCEPT', 'COMPLETED', rads))

    def test_accept_with_alef_identity_raises(self):
        rads = [_rad('ق', 'FA'), _rad('ا', 'AYN'), _rad('ل', 'LAM')]
        with pytest.raises(RootProjectionContractError):
            RootProjection.from_external_root(_ext('ACCEPT', 'COMPLETED', rads))

    def test_accept_with_alef_maqsura_raises(self):
        rads = [_rad('ق', 'FA'), _rad('ر', 'AYN'), _rad('ى', 'LAM')]
        with pytest.raises(RootProjectionContractError):
            RootProjection.from_external_root(_ext('ACCEPT', 'COMPLETED', rads))

    def test_accept_empty_radicals_raises(self):
        with pytest.raises(RootProjectionContractError):
            RootProjection.from_external_root(_ext('ACCEPT', 'COMPLETED', ()))


# ══════════════════════════════════════════════════════════════════════════════
# 3. DEFER / BLOCK
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferProjection:
    def test_defer_canonical_root_none(self):
        rads = [_rad('ق', 'FA'), _rad(None, 'AYN', resolved=False, candidates=('و', 'ي')),
                _rad('ل', 'LAM')]
        p = RootProjection.from_external_root(
            _ext('DEFER', 'DEFERRED', rads, surface='قَالَ',
                 residual=('defer:root:hollow_underlying_radical_unresolved',)))
        assert p.canonical_root is None
        assert p.stage_state == 'DEFERRED'

    def test_defer_preserves_unresolved_positions(self):
        rads = [_rad('ق', 'FA'), _rad(None, 'AYN', resolved=False), _rad('ل', 'LAM')]
        p = RootProjection.from_external_root(_ext('DEFER', 'DEFERRED', rads, surface='قَالَ'))
        assert 'AYN' in p.unresolved_positions

    def test_defer_no_fake_root_from_candidates(self):
        rads = [_rad('ق', 'FA'), _rad(None, 'AYN', resolved=False, candidates=('و', 'ي')),
                _rad('ل', 'LAM')]
        p = RootProjection.from_external_root(_ext('DEFER', 'DEFERRED', rads))
        assert p.canonical_root is None
        # candidates preserved in radicals payload, not fabricated into a root
        assert any(r.get('candidates') for r in p.radicals)

    def test_defer_profile_preserved_lafif(self):
        # وَقَى → root_profile includes LAFIF_MAFRUQ
        rads = [_rad('و', 'FA'), _rad('ق', 'AYN'), _rad(None, 'LAM', resolved=False)]
        p = RootProjection.from_external_root(
            _ext('DEFER', 'DEFERRED', rads, surface='وَقَى',
                 profile={'weakness': 'LAFIF_MAFRUQ'}))
        assert p.root_profile.get('weakness') == 'LAFIF_MAFRUQ'


class TestBlockProjection:
    def test_block_canonical_root_none(self):
        p = RootProjection.from_external_root(_ext('BLOCK', 'BLOCKED', ()))
        assert p.canonical_root is None

    def test_block_profile_cleared(self):
        p = RootProjection.from_external_root(
            _ext('BLOCK', 'BLOCKED', (), profile={'x': 1}))
        assert p.root_profile == {}

    def test_block_evidence_preserved(self):
        p = RootProjection.from_external_root(
            _ext('BLOCK', 'BLOCKED', (), residual=('block:root:obstacle',)))
        assert p.residual_codes == ('block:root:obstacle',)


# ══════════════════════════════════════════════════════════════════════════════
# 4. NOT_OPENED (HR2S not called)
# ══════════════════════════════════════════════════════════════════════════════

class TestNotOpened:
    def test_defer_not_opened_residual_by_pre_root(self):
        p = RootProjection.not_opened(
            input_surface='عَلَى', analyzed_host='عَلَى', directive='DEFER')
        assert p.stage_state == 'NOT_OPENED'
        assert p.canonical_root is None
        assert p.residual_codes == ('defer:root:root_path_not_opened_by_pre_root',)

    def test_block_not_opened(self):
        p = RootProjection.not_opened(
            input_surface='مِنْ', analyzed_host='مِنْ', directive='BLOCK')
        assert p.stage_state == 'NOT_OPENED'
        assert p.residual_codes == ('block:root:root_path_not_opened_by_pre_root',)

    def test_not_opened_rejects_accept(self):
        with pytest.raises(RootProjectionContractError):
            RootProjection.not_opened(
                input_surface='x', analyzed_host='x', directive='ACCEPT')

    def test_external_not_opened_maps_stage(self):
        p = RootProjection.from_external_root(
            _ext('BLOCK', 'NOT_OPENED', (),
                 residual=('block:root:root_path_closed_by_hokom_boundary:closed_function_word',)))
        assert p.stage_state == 'NOT_OPENED'
        assert p.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# 5. عام: directive غير معروف، حفظ الميتاداتا، JSON، نظافة الاستيراد
# ══════════════════════════════════════════════════════════════════════════════

class TestGeneralContracts:
    def test_unknown_directive_raises(self):
        with pytest.raises(RootProjectionContractError):
            RootProjection.from_external_root(_ext('WEIRD', 'COMPLETED', _DARABA))

    def test_evidence_and_trace_preserved(self):
        p = RootProjection.from_external_root(
            _ext('ACCEPT', 'COMPLETED', _DARABA,
                 evidence=('ev:root:FA',), trace=('root:msg',)))
        assert p.evidence_ids == ('ev:root:FA',)
        assert p.trace_ids == ('root:msg',)

    def test_source_version_preserved(self):
        p = RootProjection.from_external_root(_ext('ACCEPT', 'COMPLETED', _DARABA))
        assert p.source_version == '9.9'
        assert p.source_engine == 'hr2s_morphology'

    def test_input_surface_vs_analyzed_host(self):
        p = RootProjection.from_external_root(
            _ext('ACCEPT', 'COMPLETED', _DARABA, surface='أَطْفَالُ'),
            analyzed_host='أَطْفَالُ', input_surface='الْأَطْفَالُ')
        assert p.input_surface == 'الْأَطْفَالُ'
        assert p.analyzed_host == 'أَطْفَالُ'

    def test_json_serializable_accept(self):
        p = RootProjection.from_external_root(_ext('ACCEPT', 'COMPLETED', _DARABA))
        rt = json.loads(json.dumps(p.to_dict()))
        assert rt['canonical_root'] == ['ض', 'ر', 'ب']

    def test_json_serializable_not_opened(self):
        p = RootProjection.not_opened(
            input_surface='مِنْ', analyzed_host='مِنْ', directive='BLOCK')
        json.dumps(p.to_dict())

    def test_no_internal_hr2s_imports(self):
        src = (pathlib.Path(__file__).parents[2] / 'pipeline' / 'p2_projection'
               / 'root_projection.py').read_text(encoding='utf-8')
        tree = ast.parse(src)
        forbidden = ('hr2s.root', 'hr2s.boundary', 'hr2s.surface', 'hr2s')
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or '').split('.')[0] == 'hr2s', node.module
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert not a.name.split('.')[0] == 'hr2s', a.name
