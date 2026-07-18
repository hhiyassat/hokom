#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_root_pipeline_r10.py — ربط HR2S ↔ RootProjection ↔ RootCandidate (R-10)

يُشغّل project_root عبر HR2SRootAdapter بمحرّك مُزيَّف (public schema) ويُثبت:
  - OPEN → استدعاء HR2S مرة واحدة → ACCEPT canonical_root.
  - PreRoot BLOCK/DEFER → HR2S calls=0 → NOT_OPENED.
  - المضيف المُحلَّل هو ما يُرسَل للمحرّك (الأداة/اللاحقة تُفصل).
  - RootCandidate يعكس RootProjection دون ترقية.
"""

from __future__ import annotations

import types
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import MagicMock

import pytest

from boundary.models import (
    BoundaryKind, RootEligibilityDecision, RootPathDirective,
    BoundaryEvidence, directive_for, stage_state_for,
)
from pipeline.integrations.hr2s_root_adapter import HR2SRootAdapter
from pipeline.p2_projection.root_projection import (
    RootProjection, project_root, project_root_from_pre_root,
)
from pipeline.p3_candidate.root_candidate import RootCandidate


# ── حدود Hokom ─────────────────────────────────────────────────────────────────

def _boundary(surface='ضَرَبَ', kind=BoundaryKind.ROOT_ELIGIBLE):
    d = directive_for(kind)
    return RootEligibilityDecision(
        surface=surface, normalized=surface, kind=kind, directive=d,
        stage_state=stage_state_for(d),
        evidence=[BoundaryEvidence(source='test', note='fixture')], note=None)


# ── محرّك HR2S مُزيَّف (يطابق public schema) ────────────────────────────────────

class _Dir(str, Enum):
    ACCEPT = 'ACCEPT'; DEFER = 'DEFER'; BLOCK = 'BLOCK'


@dataclass
class _FakeRadical:
    identity: str | None; position: str; surface_form: str | None
    resolved: bool; evidence_ids: tuple = ()


@dataclass
class _FakeProfile:
    data: dict
    def to_dict(self): return dict(self.data)


@dataclass
class _FakeRootCandidate:
    radicals: tuple; letters: tuple; profile: _FakeProfile


@dataclass
class _FakeCandidate:
    kind: str; value: object


@dataclass
class _FakeDecision:
    directive: object


@dataclass
class _FakeStage:
    stage: str; decision: object; candidates: tuple = ()


@dataclass
class _FakeResidual:
    code: str; stage: str


@dataclass
class _FakeTrace:
    stage: str; message: str = 'governance:VALID'; ids: tuple = ()


@dataclass
class _FakeMorphResult:
    stages_by_name: dict; residuals: tuple = (); trace: tuple = field(default_factory=tuple)
    def stage(self, name): return self.stages_by_name.get(name)


def _rad(identity, position, surface_form=None, resolved=True):
    return _FakeRadical(identity, position, surface_form or (identity or ''),
                        resolved, (f'ev:root:{position}',))


def _fake_result(root_directive='ACCEPT', radicals=None, root_residual=None,
                 restoration_roots=None, profile=None):
    cands = []
    if radicals is not None:
        rc = _FakeRootCandidate(tuple(radicals), tuple(r.identity for r in radicals),
                                _FakeProfile(profile or {'weakness': 'NONE'}))
        cands.append(_FakeCandidate('root', rc))
    if restoration_roots:
        cands.append(_FakeCandidate('restoration',
                     types.SimpleNamespace(root_candidates=tuple(restoration_roots))))
    stages = {'root': _FakeStage('root', _FakeDecision(_Dir(root_directive)), tuple(cands))}
    residuals = ([_FakeResidual(root_residual, 'root')] if root_residual else []) + [
        _FakeResidual('defer:bab:stage_not_implemented', 'bab'),
    ]
    trace = (_FakeTrace('surface'), _FakeTrace('root'), _FakeTrace('bab', 'governance:DEFERRED'))
    return _FakeMorphResult(stages, tuple(residuals), trace)


def _adapter(result):
    engine = MagicMock()
    engine.analyze_surface.return_value = result
    return HR2SRootAdapter(engine=engine), engine


# ══════════════════════════════════════════════════════════════════════════════
# 1. OPEN → HR2S ACCEPT → RootProjection → RootCandidate
# ══════════════════════════════════════════════════════════════════════════════

class TestOpenAcceptPipeline:
    def test_open_accept_canonical_root(self):
        adapter, engine = _adapter(_fake_result(
            'ACCEPT', [_rad('ض', 'fa'), _rad('ر', 'ayn'), _rad('ب', 'lam')]))
        p = project_root(input_surface='ضَرَبَ', analyzed_host='ضَرَبَ',
                         root_path_directive='OPEN', adapter=adapter,
                         boundary=_boundary('ضَرَبَ'))
        assert p.directive == 'ACCEPT'
        assert p.canonical_root == ('ض', 'ر', 'ب')
        engine.analyze_surface.assert_called_once_with('ضَرَبَ')

    def test_open_accept_candidate_mirrors(self):
        adapter, _ = _adapter(_fake_result(
            'ACCEPT', [_rad('ض', 'fa'), _rad('ر', 'ayn'), _rad('ب', 'lam')]))
        p = project_root(input_surface='ضَرَبَ', analyzed_host='ضَرَبَ',
                         root_path_directive='OPEN', adapter=adapter,
                         boundary=_boundary('ضَرَبَ'))
        c = RootCandidate.from_projection(p)
        assert c.directive == 'ACCEPT'
        assert c.canonical_root == ('ض', 'ر', 'ب')

    def test_open_hamza_preserved(self):
        adapter, _ = _adapter(_fake_result(
            'ACCEPT', [_rad('ق', 'fa'), _rad('ر', 'ayn'), _rad('ء', 'lam', 'أَ')]))
        p = project_root(input_surface='قَرَأَ', analyzed_host='قَرَأَ',
                         root_path_directive='OPEN', adapter=adapter,
                         boundary=_boundary('قَرَأَ'))
        assert p.canonical_root == ('ق', 'ر', 'ء')

    def test_open_doubled_root(self):
        adapter, _ = _adapter(_fake_result(
            'ACCEPT', [_rad('م', 'fa'), _rad('د', 'ayn'), _rad('د', 'lam')]))
        p = project_root(input_surface='مَدَّ', analyzed_host='مَدَّ',
                         root_path_directive='OPEN', adapter=adapter,
                         boundary=_boundary('مَدَّ'))
        assert p.canonical_root == ('م', 'د', 'د')


# ══════════════════════════════════════════════════════════════════════════════
# 2. OPEN → HR2S DEFER → canonical_root None
# ══════════════════════════════════════════════════════════════════════════════

class TestOpenDeferPipeline:
    def test_open_defer_none_root(self):
        adapter, _ = _adapter(_fake_result(
            'DEFER',
            [_rad('ق', 'fa'), _rad('?', 'ayn', 'ا', resolved=False), _rad('ل', 'lam')],
            root_residual='defer:root:hollow_underlying_radical_unresolved',
            restoration_roots=[('ق', 'و', 'ل'), ('ق', 'ي', 'ل')]))
        p = project_root(input_surface='قَالَ', analyzed_host='قَالَ',
                         root_path_directive='OPEN', adapter=adapter,
                         boundary=_boundary('قَالَ'))
        assert p.directive == 'DEFER'
        assert p.canonical_root is None
        c = RootCandidate.from_projection(p)
        assert c.directive == 'DEFER' and c.canonical_root is None

    def test_open_defer_lafif_profile(self):
        adapter, _ = _adapter(_fake_result(
            'DEFER', [_rad('و', 'fa'), _rad('ق', 'ayn'), _rad('?', 'lam', 'ى', resolved=False)],
            profile={'weakness': 'LAFIF_MAFRUQ'}))
        p = project_root(input_surface='وَقَى', analyzed_host='وَقَى',
                         root_path_directive='OPEN', adapter=adapter,
                         boundary=_boundary('وَقَى'))
        assert p.root_profile.get('weakness') == 'LAFIF_MAFRUQ'


# ══════════════════════════════════════════════════════════════════════════════
# 3. PreRoot BLOCK/DEFER → HR2S calls=0
# ══════════════════════════════════════════════════════════════════════════════

class TestPreRootShortCircuit:
    def test_block_route_no_hr2s(self):
        engine = MagicMock()
        adapter = HR2SRootAdapter(engine=engine)
        p = project_root(input_surface='مِنْ', analyzed_host='مِنْ',
                         root_path_directive='BLOCK', adapter=adapter)
        assert p.directive == 'BLOCK'
        assert p.stage_state == 'NOT_OPENED'
        assert p.residual_codes == ('block:root:root_path_not_opened_by_pre_root',)
        engine.analyze_surface.assert_not_called()

    def test_defer_route_no_hr2s(self):
        engine = MagicMock()
        adapter = HR2SRootAdapter(engine=engine)
        p = project_root(input_surface='عَلَى', analyzed_host='عَلَى',
                         root_path_directive='DEFER', adapter=adapter)
        assert p.directive == 'DEFER'
        assert p.stage_state == 'NOT_OPENED'
        engine.analyze_surface.assert_not_called()

    def test_operator_host_block_no_hr2s(self):
        # أَنَّهُمْ: operator_host=أَنَّ → BLOCK → HR2S calls=0
        engine = MagicMock()
        adapter = HR2SRootAdapter(engine=engine)
        p = project_root(input_surface='أَنَّهُمْ', analyzed_host='أَنَّ',
                         root_path_directive='BLOCK', adapter=adapter)
        assert p.directive == 'BLOCK'
        engine.analyze_surface.assert_not_called()

    def test_block_candidate_mirrors(self):
        engine = MagicMock()
        adapter = HR2SRootAdapter(engine=engine)
        p = project_root(input_surface='مِنْ', analyzed_host='مِنْ',
                         root_path_directive='BLOCK', adapter=adapter)
        c = RootCandidate.from_projection(p)
        assert c.directive == 'BLOCK' and c.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# 4. المضيف المُحلَّل يُفصل قبل إرسال للمحرّك
# ══════════════════════════════════════════════════════════════════════════════

class TestAnalyzedHostStripping:
    def test_article_stripped_before_hr2s(self):
        # الْأَطْفَالُ → analyzed_host=أَطْفَالُ (لا أداة في payload المحرّك)
        adapter, engine = _adapter(_fake_result(
            'ACCEPT', [_rad('ط', 'fa'), _rad('ف', 'ayn'), _rad('ل', 'lam')]))
        p = project_root(input_surface='الْأَطْفَالُ', analyzed_host='أَطْفَالُ',
                         root_path_directive='OPEN', adapter=adapter,
                         boundary=_boundary('أَطْفَالُ'))
        engine.analyze_surface.assert_called_once_with('أَطْفَالُ')
        assert p.input_surface == 'الْأَطْفَالُ'
        assert p.analyzed_host == 'أَطْفَالُ'

    def test_suffix_stripped_before_hr2s(self):
        # تَرَكَتْهُمْ → analyzed_host=تَرَكَتْ (اللاحقة تُفصل)
        adapter, engine = _adapter(_fake_result(
            'ACCEPT', [_rad('ت', 'fa'), _rad('ر', 'ayn'), _rad('ك', 'lam')]))
        p = project_root(input_surface='تَرَكَتْهُمْ', analyzed_host='تَرَكَتْ',
                         root_path_directive='OPEN', adapter=adapter,
                         boundary=_boundary('تَرَكَتْ'))
        engine.analyze_surface.assert_called_once_with('تَرَكَتْ')
        assert p.input_surface == 'تَرَكَتْهُمْ'


# ══════════════════════════════════════════════════════════════════════════════
# 5. ربط عبر PreRootDecision الحقيقي
# ══════════════════════════════════════════════════════════════════════════════

class TestFromPreRootDecision:
    def test_min_pre_root_block_no_hr2s(self):
        from pipeline.pre_root.pre_root_decision import assess_pre_root
        d = assess_pre_root('مِنْ')
        engine = MagicMock()
        adapter = HR2SRootAdapter(engine=engine)
        p = project_root_from_pre_root(d, adapter=adapter)
        # مِنْ closed function word → BLOCK route → HR2S not called
        assert p.directive in ('BLOCK', 'DEFER')
        assert p.stage_state == 'NOT_OPENED'
        engine.analyze_surface.assert_not_called()

    def test_open_route_reaches_hr2s(self):
        # مسار OPEN من PreRoot يصل المحرّك مرة واحدة
        adapter, engine = _adapter(_fake_result(
            'ACCEPT', [_rad('ض', 'fa'), _rad('ر', 'ayn'), _rad('ب', 'lam')]))

        @dataclass
        class _D:
            input_surface: str; host_surface: str; root_path_directive: str
            evidence_ids: tuple = (); trace_ids: tuple = ()

        d = _D('ضَرَبَ', 'ضَرَبَ', 'OPEN')
        p = project_root_from_pre_root(d, adapter=adapter, boundary=_boundary('ضَرَبَ'))
        assert p.directive == 'ACCEPT'
        engine.analyze_surface.assert_called_once_with('ضَرَبَ')
