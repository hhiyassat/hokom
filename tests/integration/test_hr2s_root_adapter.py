#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_hr2s_root_adapter.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

اختبارات HR2SRootAdapter في مستويين:

§A  اختبارات وحدة — بنتائج HR2S مُزيَّفة تُطابق public schema الحقيقي
    (MorphologyResult: .stage('root').decision.directive / .residuals / .trace).
    تعمل بلا حاجة لتشغيل المحرك.
§B  اختبارات تكامل حقيقية — تُشغِّل MorphologyEngine الفعلي.
    تُعلَّق فقط إذا غابت hr2s_morphology.

القوانين المثبتة:
  - Root Adapter يستهلك مرحلة الجذر فقط؛ بقايا bab/paradigm/masdar/derivation
    لا تُخفِّض جذرًا مقبولًا.
  - سقف الحدود لا يُخرق: BLOCK/DEFER لا يُرقَّيان.
  - ACCEPT لا يحمل UnknownRadical؛ الهمزة ء محفوظة.
  - تغيّر public schema يفشل صراحة (HR2SProjectionContractError).
  - غياب الحزمة يُختبر بالحقن، لا بحالة البيئة.
"""

from __future__ import annotations

import json
import types
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import MagicMock

import pytest

from boundary.models import (
    BoundaryKind,
    RootEligibilityDecision,
    RootPathDirective,
    StageState,
    BoundaryEvidence,
    directive_for,
    stage_state_for,
)
from pipeline.integrations.hr2s_root_adapter import (
    HR2SRootAdapter,
    HR2SUnavailableError,
    HR2SProjectionContractError,
    ExternalRadical,
    ExternalRootAnalysis,
    enforce_boundary_ceiling,
)


# ══════════════════════════════════════════════════════════════════════════════
# أدوات: حدود Hokom + نتيجة HR2S مُزيَّفة تطابق public schema الحقيقي
# ══════════════════════════════════════════════════════════════════════════════

def _make_boundary(
    surface: str = 'ضَرَبَ',
    kind: BoundaryKind = BoundaryKind.ROOT_ELIGIBLE,
) -> RootEligibilityDecision:
    directive = directive_for(kind)
    return RootEligibilityDecision(
        surface     = surface,
        normalized  = surface,
        kind        = kind,
        directive   = directive,
        stage_state = stage_state_for(directive),
        evidence    = [BoundaryEvidence(source='test', note='fixture')],
        note        = None,
    )


class _Dir(str, Enum):
    """يحاكي hr2s.core.Directive: enum له .value."""
    ACCEPT = 'ACCEPT'
    DEFER  = 'DEFER'
    BLOCK  = 'BLOCK'


@dataclass
class _FakeRadical:
    identity: str | None
    position: str
    surface_form: str | None
    resolved: bool
    evidence_ids: tuple = ()


@dataclass
class _FakeProfile:
    data: dict
    def to_dict(self) -> dict:
        return dict(self.data)


@dataclass
class _FakeRootCandidate:
    radicals: tuple
    letters: tuple
    profile: _FakeProfile


@dataclass
class _FakeCandidate:
    kind: str
    value: object


@dataclass
class _FakeDecision:
    directive: object


@dataclass
class _FakeStage:
    stage: str
    decision: object
    candidates: tuple = ()


@dataclass
class _FakeResidual:
    code: str
    stage: str


@dataclass
class _FakeTrace:
    stage: str
    message: str = 'governance:VALID'
    ids: tuple = ()


@dataclass
class _FakeMorphResult:
    """يطابق سطح MorphologyResult العام: .stage(name), .residuals, .trace."""
    stages_by_name: dict
    residuals: tuple = ()
    trace: tuple = field(default_factory=tuple)

    def stage(self, name):
        return self.stages_by_name.get(name)


def _rad(identity, position, surface_form=None, resolved=True) -> _FakeRadical:
    return _FakeRadical(identity, position, surface_form or (identity or ''),
                        resolved, (f'ev:root:{position}',))


def _fake_result(
    root_directive: str = 'ACCEPT',
    radicals: list | None = None,
    root_residual: str | None = None,
    restoration_roots: list | None = None,
    include_root_stage: bool = True,
    directive_obj=None,
) -> _FakeMorphResult:
    """يبني MorphologyResult مُزيَّفًا يطابق public schema، مع بقايا downstream دائمًا
    لإثبات أنها تُصفَّى ولا تُخفِّض الجذر."""
    cands = []
    if radicals is not None:
        rc = _FakeRootCandidate(
            radicals=tuple(radicals),
            letters=tuple(r.identity for r in radicals),
            profile=_FakeProfile({'weakness': 'NONE', 'cardinality': 'TRILITERAL'}),
        )
        cands.append(_FakeCandidate('root', rc))
    if restoration_roots:
        cands.append(_FakeCandidate(
            'restoration', types.SimpleNamespace(root_candidates=tuple(restoration_roots))))

    stages: dict = {}
    if include_root_stage:
        dirv = directive_obj if directive_obj is not None else _Dir(root_directive)
        stages['root'] = _FakeStage('root', _FakeDecision(dirv), tuple(cands))

    residuals = []
    if root_residual:
        residuals.append(_FakeResidual(root_residual, 'root'))
    # بقايا المراحل اللاحقة — يجب أن تُصفَّى دائمًا
    residuals += [
        _FakeResidual('defer:bab:stage_not_implemented', 'bab'),
        _FakeResidual('defer:paradigm:prerequisite_not_closed', 'paradigm'),
        _FakeResidual('defer:masdar:prerequisite_not_closed', 'masdar'),
        _FakeResidual('defer:derivation:prerequisite_not_closed', 'derivation'),
    ]
    trace = (
        _FakeTrace('surface'), _FakeTrace('boundary'), _FakeTrace('root'),
        _FakeTrace('bab', 'governance:DEFERRED'), _FakeTrace('paradigm', 'governance:DEFERRED'),
    )
    return _FakeMorphResult(stages, tuple(residuals), trace)


def _adapter_with(result: _FakeMorphResult):
    engine = MagicMock()
    engine.analyze_surface.return_value = result
    return HR2SRootAdapter(engine=engine), engine


# ══════════════════════════════════════════════════════════════════════════════
# §A-1  جدول سقف الحدود
# ══════════════════════════════════════════════════════════════════════════════

class TestBoundaryCeiling:
    @pytest.mark.parametrize("boundary_dir, hr2s_dir, expected", [
        (RootPathDirective.BLOCK, 'ACCEPT', 'BLOCK'),
        (RootPathDirective.BLOCK, 'DEFER',  'BLOCK'),
        (RootPathDirective.BLOCK, 'BLOCK',  'BLOCK'),
        (RootPathDirective.DEFER, 'ACCEPT', 'DEFER'),
        (RootPathDirective.DEFER, 'DEFER',  'DEFER'),
        (RootPathDirective.DEFER, 'BLOCK',  'DEFER'),
        (RootPathDirective.OPEN,  'ACCEPT', 'ACCEPT'),
        (RootPathDirective.OPEN,  'DEFER',  'DEFER'),
        (RootPathDirective.OPEN,  'BLOCK',  'BLOCK'),
    ])
    def test_ceiling_matrix(self, boundary_dir, hr2s_dir, expected):
        assert enforce_boundary_ceiling(boundary_dir, hr2s_dir) == expected


# ══════════════════════════════════════════════════════════════════════════════
# §A-2  الحدود المغلقة/المؤجلة لا تستدعي HR2S
# ══════════════════════════════════════════════════════════════════════════════

class TestBoundaryShortCircuit:
    def test_block_boundary_does_not_call_hr2s(self):
        engine = MagicMock()
        adapter = HR2SRootAdapter(engine=engine)
        result = adapter.analyze('مِنْ', boundary=_make_boundary('مِنْ', BoundaryKind.CLOSED_FUNCTION_WORD))
        engine.analyze_surface.assert_not_called()
        assert result.directive == 'BLOCK'
        assert result.stage_state == 'NOT_OPENED'
        assert result.canonical_radicals == ()

    def test_defer_boundary_does_not_call_hr2s(self):
        engine = MagicMock()
        adapter = HR2SRootAdapter(engine=engine)
        result = adapter.analyze('عَلَى', boundary=_make_boundary('عَلَى', BoundaryKind.POSSIBLE_FUNCTION_WORD))
        engine.analyze_surface.assert_not_called()
        assert result.directive == 'DEFER'
        assert result.stage_state == 'NOT_OPENED'

    def test_ambiguous_defer_does_not_call_hr2s(self):
        engine = MagicMock()
        adapter = HR2SRootAdapter(engine=engine)
        result = adapter.analyze('تَقِي', boundary=_make_boundary('تَقِي', BoundaryKind.AMBIGUOUS))
        engine.analyze_surface.assert_not_called()
        assert result.directive == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# §A-3  OPEN يستدعي HR2S ويُسقط مرحلة الجذر
# ══════════════════════════════════════════════════════════════════════════════

class TestOpenCallsHR2S:
    def test_open_calls_engine_once(self):
        adapter, engine = _adapter_with(_fake_result(
            'ACCEPT', [_rad('ض', 'fa'), _rad('ر', 'ayn'), _rad('ب', 'lam')]))
        adapter.analyze('ضَرَبَ', boundary=_make_boundary('ضَرَبَ'))
        engine.analyze_surface.assert_called_once_with('ضَرَبَ')

    def test_open_accept_completed_with_radicals(self):
        adapter, _ = _adapter_with(_fake_result(
            'ACCEPT', [_rad('ض', 'fa'), _rad('ر', 'ayn'), _rad('ب', 'lam')]))
        result = adapter.analyze('ضَرَبَ', boundary=_make_boundary('ضَرَبَ'))
        assert result.directive == 'ACCEPT'
        assert result.stage_state == 'COMPLETED'
        assert tuple(r.identity for r in result.canonical_radicals) == ('ض', 'ر', 'ب')
        assert result.canonical_radicals[0].position == 'FA'
        assert result.canonical_radicals[0].resolved is True

    def test_open_defer_deferred_preserves_unknown(self):
        adapter, _ = _adapter_with(_fake_result(
            'DEFER',
            [_rad('ق', 'fa'), _rad('?', 'ayn', 'ا', resolved=False), _rad('ل', 'lam')],
            root_residual='defer:root:hollow_underlying_radical_unresolved',
            restoration_roots=[('ق', 'و', 'ل'), ('ق', 'ي', 'ل')],
        ))
        result = adapter.analyze('قَالَ', boundary=_make_boundary('قَالَ'))
        assert result.directive == 'DEFER'
        assert result.stage_state == 'DEFERRED'
        ayn = result.canonical_radicals[1]
        assert ayn.identity is None and ayn.resolved is False
        assert set(ayn.candidates) == {'و', 'ي'}

    def test_open_block_blocked(self):
        adapter, _ = _adapter_with(_fake_result('BLOCK', radicals=None))
        result = adapter.analyze('س', boundary=_make_boundary('س'))
        assert result.directive == 'BLOCK'
        assert result.stage_state == 'BLOCKED'
        assert result.canonical_radicals == ()


# ══════════════════════════════════════════════════════════════════════════════
# §A-4  السقف يمنع الترقية
# ══════════════════════════════════════════════════════════════════════════════

class TestCeilingPreventsUpgrade:
    def test_block_not_upgraded_by_accept(self):
        adapter, engine = _adapter_with(_fake_result(
            'ACCEPT', [_rad('م', 'fa'), _rad('ن', 'ayn'), _rad('و', 'lam')]))
        result = adapter.analyze('مِنْ', boundary=_make_boundary('مِنْ', BoundaryKind.CLOSED_FUNCTION_WORD))
        assert result.directive == 'BLOCK'
        engine.analyze_surface.assert_not_called()

    def test_defer_not_upgraded_to_accept(self):
        adapter, engine = _adapter_with(_fake_result(
            'ACCEPT', [_rad('ع', 'fa'), _rad('ل', 'ayn'), _rad('و', 'lam')]))
        result = adapter.analyze('عَلَى', boundary=_make_boundary('عَلَى', BoundaryKind.POSSIBLE_FUNCTION_WORD))
        assert result.directive == 'DEFER'
        assert result.canonical_radicals == ()
        engine.analyze_surface.assert_not_called()


# ══════════════════════════════════════════════════════════════════════════════
# §A-5  بقايا المراحل اللاحقة لا تُخفِّض الجذر (جوهر الإصلاح)
# ══════════════════════════════════════════════════════════════════════════════

class TestDownstreamResidualsIgnored:
    def test_downstream_defer_does_not_downgrade_accepted_root(self):
        adapter, _ = _adapter_with(_fake_result(
            'ACCEPT', [_rad('ض', 'fa'), _rad('ر', 'ayn'), _rad('ب', 'lam')]))
        result = adapter.analyze('ضَرَبَ', boundary=_make_boundary('ضَرَبَ'))
        assert result.directive == 'ACCEPT'
        assert result.stage_state == 'COMPLETED'
        assert not any(
            code.startswith(('defer:bab:', 'defer:paradigm:',
                             'defer:masdar:', 'defer:derivation:'))
            for code in result.residual_codes
        )

    def test_only_root_residuals_projected(self):
        adapter, _ = _adapter_with(_fake_result(
            'DEFER',
            [_rad('ق', 'fa'), _rad('?', 'ayn', 'ا', resolved=False), _rad('ل', 'lam')],
            root_residual='defer:root:hollow_underlying_radical_unresolved',
        ))
        result = adapter.analyze('قَالَ', boundary=_make_boundary('قَالَ'))
        assert result.residual_codes == ('defer:root:hollow_underlying_radical_unresolved',)

    def test_trace_scoped_to_surface_boundary_root(self):
        adapter, _ = _adapter_with(_fake_result(
            'ACCEPT', [_rad('ض', 'fa'), _rad('ر', 'ayn'), _rad('ب', 'lam')]))
        result = adapter.analyze('ضَرَبَ', boundary=_make_boundary('ضَرَبَ'))
        scopes = {tid.split(':', 1)[0] for tid in result.trace_ids}
        assert scopes <= {'surface', 'boundary', 'root'}
        assert 'bab' not in scopes and 'paradigm' not in scopes


# ══════════════════════════════════════════════════════════════════════════════
# §A-6  UnknownRadical + هوية الهمزة
# ══════════════════════════════════════════════════════════════════════════════

class TestUnknownRadicalAndHamza:
    def test_defer_preserves_unknown_radical(self):
        adapter, _ = _adapter_with(_fake_result(
            'DEFER',
            [_rad('ق', 'fa'), _rad('?', 'ayn', 'و', resolved=False), _rad('ل', 'lam')],
            restoration_roots=[('ق', 'و', 'ل'), ('ق', 'ي', 'ل')],
        ))
        result = adapter.analyze('قُلْ', boundary=_make_boundary('قُلْ', BoundaryKind.COMPRESSED_VERB_CANDIDATE))
        assert result.directive == 'DEFER'
        assert result.canonical_radicals[1].identity is None
        assert result.canonical_radicals[1].resolved is False

    def test_hamza_identity_preserved(self):
        adapter, _ = _adapter_with(_fake_result(
            'ACCEPT', [_rad('ق', 'fa'), _rad('ر', 'ayn'), _rad('ء', 'lam', 'أَ')]))
        result = adapter.analyze('قَرَأَ', boundary=_make_boundary('قَرَأَ'))
        assert result.canonical_radicals[2].identity == 'ء'
        assert result.canonical_radicals[2].identity not in {'أ', 'إ', 'ؤ', 'ئ', 'آ'}


# ══════════════════════════════════════════════════════════════════════════════
# §A-7  تغيّر schema يفشل صراحة
# ══════════════════════════════════════════════════════════════════════════════

class TestSchemaMismatchFailsLoudly:
    def test_missing_root_stage_raises(self):
        adapter, _ = _adapter_with(_fake_result('ACCEPT', include_root_stage=False))
        with pytest.raises(HR2SProjectionContractError):
            adapter.analyze('ضَرَبَ', boundary=_make_boundary('ضَرَبَ'))

    def test_unsupported_directive_raises(self):
        adapter, _ = _adapter_with(_fake_result(directive_obj='WEIRD_VERDICT',
                                                radicals=[_rad('ض', 'fa')]))
        with pytest.raises(HR2SProjectionContractError):
            adapter.analyze('ضَرَبَ', boundary=_make_boundary('ضَرَبَ'))

    def test_accept_without_resolved_root_raises(self):
        adapter, _ = _adapter_with(_fake_result(
            'ACCEPT',
            [_rad('ض', 'fa'), _rad('?', 'ayn', 'ا', resolved=False), _rad('ب', 'lam')]))
        with pytest.raises(HR2SProjectionContractError):
            adapter.analyze('ضَرَبَ', boundary=_make_boundary('ضَرَبَ'))


# ══════════════════════════════════════════════════════════════════════════════
# §A-8  DTO قابل للتسلسل JSON
# ══════════════════════════════════════════════════════════════════════════════

class TestJSONSerializable:
    def test_external_radical_to_dict(self):
        r = ExternalRadical('ض', 'ضَ', 'FA', True, ())
        assert json.loads(json.dumps(r.to_dict())) == r.to_dict()

    def test_external_root_analysis_to_dict(self):
        adapter, _ = _adapter_with(_fake_result(
            'ACCEPT', [_rad('ض', 'fa'), _rad('ر', 'ayn'), _rad('ب', 'lam')]))
        result = adapter.analyze('ضَرَبَ', boundary=_make_boundary('ضَرَبَ'))
        rt = json.loads(json.dumps(result.to_dict()))
        assert rt['directive'] == 'ACCEPT'
        assert rt['canonical_radicals'][0]['identity'] == 'ض'

    def test_block_result_json_serializable(self):
        engine = MagicMock()
        adapter = HR2SRootAdapter(engine=engine)
        result = adapter.analyze('مِنْ', boundary=_make_boundary('مِنْ', BoundaryKind.CLOSED_FUNCTION_WORD))
        json.dumps(result.to_dict())


# ══════════════════════════════════════════════════════════════════════════════
# §A-9  بيانات المصدر
# ══════════════════════════════════════════════════════════════════════════════

class TestSourceMetadata:
    def test_source_engine_constant(self):
        engine = MagicMock()
        adapter = HR2SRootAdapter(engine=engine)
        result = adapter.analyze('مِنْ', boundary=_make_boundary('مِنْ', BoundaryKind.CLOSED_FUNCTION_WORD))
        assert result.source_engine == 'hr2s_morphology'

    def test_source_version_from_loader(self):
        engine = MagicMock()
        engine.analyze_surface.return_value = _fake_result(
            'ACCEPT', [_rad('ض', 'fa'), _rad('ر', 'ayn'), _rad('ب', 'lam')])
        adapter = HR2SRootAdapter(engine_loader=lambda: (engine, '2.3.1'))
        result = adapter.analyze('ضَرَبَ', boundary=_make_boundary('ضَرَبَ'))
        assert result.source_version == '2.3.1'


# ══════════════════════════════════════════════════════════════════════════════
# §A-10  غياب الحزمة بالحقن (مستقل عن البيئة)
# ══════════════════════════════════════════════════════════════════════════════

class TestHR2SUnavailableInjected:
    def test_missing_loader_raises(self):
        def missing_loader():
            raise HR2SUnavailableError("simulated missing HR2S package")
        adapter = HR2SRootAdapter(engine_loader=missing_loader)
        with pytest.raises(HR2SUnavailableError):
            adapter.analyze('ضَرَبَ', boundary=_make_boundary('ضَرَبَ'))

    def test_block_does_not_load_engine(self):
        def missing_loader():
            raise HR2SUnavailableError("must not be called")
        adapter = HR2SRootAdapter(engine_loader=missing_loader)
        result = adapter.analyze('مِنْ', boundary=_make_boundary('مِنْ', BoundaryKind.CLOSED_FUNCTION_WORD))
        assert result.directive == 'BLOCK'


# ══════════════════════════════════════════════════════════════════════════════
# §A-11  ضمانات الاستيراد والمسارات
# ══════════════════════════════════════════════════════════════════════════════

class TestAdapterHygiene:
    def _source(self):
        import pathlib
        return (pathlib.Path(__file__).parents[2] / 'pipeline' / 'integrations'
                / 'hr2s_root_adapter.py').read_text(encoding='utf-8')

    def test_no_forbidden_hr2s_internal_imports(self):
        import ast
        tree = ast.parse(self._source())
        forbidden = ('hr2s.root', 'hr2s.boundary', 'hr2s.surface')
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or '').startswith(forbidden):
                violations.append(node.module)
            if isinstance(node, ast.Import):
                violations += [a.name for a in node.names if a.name.startswith(forbidden)]
        assert not violations, violations

    def test_no_absolute_paths_in_adapter(self):
        src = self._source()
        assert not any(p in src for p in ('/Users/', '/home/', '/root/', 'C:\\', 'C:/'))


class TestExistingConsumerImportsUnchanged:
    def test_boundary_models_importable(self):
        from boundary.models import RootEligibilityDecision, RootPathDirective, BoundaryKind
        assert RootPathDirective.OPEN is not None

    def test_syllabifier_importable(self):
        from syllabifier import parse_phones, syllabify, word_gate
        assert parse_phones is not None

    def test_normalizer_importable(self):
        from normalizer import normalize, normalize_tracked
        assert normalize is not None

    def test_licensing_importable(self):
        from licensing import license_phone, gate_unicode
        assert license_phone is not None


# ══════════════════════════════════════════════════════════════════════════════
# §B  اختبارات تكامل حقيقية — MorphologyEngine الفعلي
# ══════════════════════════════════════════════════════════════════════════════

_hr2s_skip = pytest.mark.skipif(
    __import__('importlib.util', fromlist=['find_spec']).find_spec('hr2s') is None,
    reason='hr2s_morphology not installed — pip install -e /path/to/hr2s_morphology',
)


@_hr2s_skip
class TestRealHR2SIntegration:

    @pytest.fixture(scope='class')
    def adapter(self):
        return HR2SRootAdapter()

    @pytest.fixture(scope='class')
    def _boundary(self):
        from boundary.service import assess_boundary
        return assess_boundary

    def test_daraba_accept(self, adapter, _boundary):
        r = adapter.analyze('ضَرَبَ', boundary=_boundary('ضَرَبَ'))
        assert r.directive == 'ACCEPT'
        assert tuple(x.identity for x in r.canonical_radicals) == ('ض', 'ر', 'ب')
        assert r.residual_codes == ()

    def test_madda_doubled_accept(self, adapter, _boundary):
        r = adapter.analyze('مَدَّ', boundary=_boundary('مَدَّ'))
        assert r.directive == 'ACCEPT'
        assert tuple(x.identity for x in r.canonical_radicals) == ('م', 'د', 'د')

    def test_qaraa_hamza_accept(self, adapter, _boundary):
        r = adapter.analyze('قَرَأَ', boundary=_boundary('قَرَأَ'))
        assert r.directive == 'ACCEPT'
        identities = [x.identity for x in r.canonical_radicals]
        assert identities == ['ق', 'ر', 'ء']
        assert 'أ' not in identities

    def test_qala_defer_no_alef_identity(self, adapter, _boundary):
        r = adapter.analyze('قَالَ', boundary=_boundary('قَالَ'))
        assert r.directive == 'DEFER'
        identities = [x.identity for x in r.canonical_radicals]
        assert 'ا' not in identities and 'ى' not in identities
        assert any(c.startswith('defer:root:') for c in r.residual_codes)

    def test_daa_defer_no_alef_identity(self, adapter, _boundary):
        r = adapter.analyze('دَعَا', boundary=_boundary('دَعَا'))
        assert r.directive == 'DEFER'
        assert 'ا' not in [x.identity for x in r.canonical_radicals]

    def test_waqa_defer_profile_preserved(self, adapter, _boundary):
        r = adapter.analyze('وَقَى', boundary=_boundary('وَقَى'))
        assert r.directive == 'DEFER'
        assert r.root_profile.get('weakness', '').startswith('LAFIF')

    def test_qul_defer_unknown_radical(self, adapter, _boundary):
        r = adapter.analyze('قُلْ', boundary=_boundary('قُلْ'))
        assert r.directive == 'DEFER'
        assert any((not x.resolved) for x in r.canonical_radicals)

    def test_min_block_hr2s_not_called(self, adapter, _boundary):
        from unittest.mock import patch as p
        boundary = _boundary('مِنْ')
        assert boundary.directive is RootPathDirective.BLOCK
        engine = adapter._get_engine()
        with p.object(engine, 'analyze_surface', wraps=engine.analyze_surface) as spy:
            r = adapter.analyze('مِنْ', boundary=boundary)
            spy.assert_not_called()
        assert r.directive == 'BLOCK'

    def test_ala_defer_hr2s_not_called(self, adapter, _boundary):
        from unittest.mock import patch as p
        boundary = _boundary('عَلَى')
        assert boundary.directive is RootPathDirective.DEFER
        engine = adapter._get_engine()
        with p.object(engine, 'analyze_surface', wraps=engine.analyze_surface) as spy:
            r = adapter.analyze('عَلَى', boundary=boundary)
            spy.assert_not_called()
        assert r.directive == 'DEFER'

    def test_completed_state_and_json_serializable_real(self, adapter, _boundary):
        r = adapter.analyze('ضَرَبَ', boundary=_boundary('ضَرَبَ'))
        assert r.stage_state == 'COMPLETED'
        json.dumps(r.to_dict())
