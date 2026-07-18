#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/integrations/hr2s_root_adapter.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hokom ↔ HR2S morphology engine integration layer.

المبدأ:
  Hokom يقرر هل يُفتح مسار الجذر (boundary ceiling).
  HR2S يحلل الجذر إذا فُتح المسار.
  لا يجوز لـHR2S أن يرقّي قرار Hokom من BLOCK أو DEFER.
  يجوز لـHR2S أن يخفض OPEN إلى DEFER أو BLOCK.

الاستخدام المعتمد فقط:
  from hr2s import MorphologyEngine      ← public API
  لا استيراد من hr2s.root, hr2s.boundary, hr2s.surface

هذا الملف لا يعتمد على أي shim جذري.
لا مسارات مطلقة داخل منطق التطبيق.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Mapping, Any


# ══════════════════════════════════════════════════════════════════════════════
# استيراد نماذج Hokom فقط
# ══════════════════════════════════════════════════════════════════════════════

from boundary.models import RootEligibilityDecision, RootPathDirective


# ══════════════════════════════════════════════════════════════════════════════
# 1.  خطأ الغياب
# ══════════════════════════════════════════════════════════════════════════════

class HR2SUnavailableError(RuntimeError):
    """Raised when hr2s_morphology package is required but not installed."""
    pass


class HR2SProjectionContractError(RuntimeError):
    """Raised when the HR2S public result violates the projection contract:
    a missing directive/root stage, an unsupported directive value, or an ACCEPT
    whose root is not fully resolved. A silent downgrade to BLOCK is forbidden —
    a schema change must fail loudly, never pass through as bad data.
    """
    pass


def _enum_value(value):
    """Return the ``.value`` of an Enum (Directive.ACCEPT → 'ACCEPT'), else the value
    itself. Never rely on ``str(enum)`` — it yields 'Directive.ACCEPT'."""
    return getattr(value, "value", value)


# the ONLY HR2S stages this root adapter consumes; downstream stages (bab, paradigm,
# masdar, derivation) are deliberately ignored — their residuals never downgrade a root.
_ROOT_STAGE = "root"
_ROOT_SCOPE_STAGES = frozenset({"surface", "boundary", "root"})
_POSITION = {"fa": "FA", "ayn": "AYN", "lam": "LAM"}
_PROHIBITED_IDENTITIES = frozenset({"ا", "ى", "أ", "إ", "ؤ", "ئ", "آ", "?", ""})


# ══════════════════════════════════════════════════════════════════════════════
# 2.  نماذج البيانات (DTO) — معزولة عن نماذج HR2S الداخلية
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExternalRadical:
    """
    تمثيل جذري واحد معزول عن تفاصيل HR2S.

    identity:     الحرف المحدد، أو None إذا لم يُحدَّد.
    surface_form: الشكل السطحي للحرف (مع حركة)، أو None.
    position:     'FA' | 'AYN' | 'LAM' | 'UNKNOWN'
    resolved:     True إذا كانت الهوية محددة نهائيًا.
    candidates:   مجموعة المرشحين المحتملين إذا كان غير محدد.
    """
    identity:     str | None
    surface_form: str | None
    position:     str
    resolved:     bool
    candidates:   tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            'identity':     self.identity,
            'surface_form': self.surface_form,
            'position':     self.position,
            'resolved':     self.resolved,
            'candidates':   list(self.candidates),
        }


@dataclass(frozen=True)
class ExternalRootAnalysis:
    """
    نتيجة تحليل الجذر عبر HR2S، مُسقطة إلى نموذج Hokom.

    surface:            السطح الأصلي المُحلَّل.
    directive:          'ACCEPT' | 'DEFER' | 'BLOCK'
    stage_state:        'COMPLETED' | 'DEFERRED' | 'BLOCKED'  (إسقاط HR2S)
                        أو 'NOT_OPENED' عند إغلاق الحدود قبل استدعاء HR2S.
    canonical_radicals: مكونات الجذر (محفوظة مع UnknownRadical عند DEFER؛ فارغة عند BLOCK).
    root_profile:       بيانات وصفية من HR2S (وزن، بنية، ...).
    evidence_ids:       مرجعيات الشواهد التي استند إليها HR2S.
    trace_ids:          مسار التحليل الداخلي في HR2S.
    residual_codes:     رموز التحفظ (متسقة مع Hokom residual pattern).
    source_engine:      'hr2s_morphology' ثابت.
    source_version:     نسخة package HR2S إن أمكن استرجاعها.
    """
    surface:            str
    directive:          str
    stage_state:        str
    canonical_radicals: tuple[ExternalRadical, ...]
    root_profile:       Mapping[str, Any]
    evidence_ids:       tuple[str, ...]
    trace_ids:          tuple[str, ...]
    residual_codes:     tuple[str, ...]
    source_engine:      str = 'hr2s_morphology'
    source_version:     str | None = None

    def to_dict(self) -> dict:
        """قابل للتسلسل إلى JSON."""
        return {
            'surface':            self.surface,
            'directive':          self.directive,
            'stage_state':        self.stage_state,
            'canonical_radicals': [r.to_dict() for r in self.canonical_radicals],
            'root_profile':       dict(self.root_profile),
            'evidence_ids':       list(self.evidence_ids),
            'trace_ids':          list(self.trace_ids),
            'residual_codes':     list(self.residual_codes),
            'source_engine':      self.source_engine,
            'source_version':     self.source_version,
        }


# ══════════════════════════════════════════════════════════════════════════════
# 3.  قاعدة عدم الترقية (Boundary Ceiling)
# ══════════════════════════════════════════════════════════════════════════════

def enforce_boundary_ceiling(
    boundary_directive: RootPathDirective,
    hr2s_directive: str,
) -> str:
    """
    طبّق سقف الحدود: Hokom boundary لا يُرقَّى أبدًا بنتيجة HR2S.

    القانون:
      BLOCK + أي نتيجة    → 'BLOCK'
      DEFER + أي نتيجة    → 'DEFER'
      OPEN  + 'ACCEPT'    → 'ACCEPT'
      OPEN  + 'DEFER'     → 'DEFER'
      OPEN  + 'BLOCK'     → 'BLOCK'

    Parameters
    ----------
    boundary_directive : RootPathDirective
        قرار Hokom boundary قبل استدعاء HR2S.
    hr2s_directive : str
        القرار الذي أعاده HR2S: 'ACCEPT' | 'DEFER' | 'BLOCK'.

    Returns
    -------
    str : القرار النهائي: 'ACCEPT' | 'DEFER' | 'BLOCK'
    """
    if boundary_directive is RootPathDirective.BLOCK:
        return 'BLOCK'
    if boundary_directive is RootPathDirective.DEFER:
        return 'DEFER'
    # OPEN: HR2S يملك القرار
    if hr2s_directive not in ('ACCEPT', 'DEFER', 'BLOCK'):
        # قيمة غير متوقعة من HR2S → حافظ على التحفظ
        return 'DEFER'
    return hr2s_directive


def _projected_stage_state(directive: str) -> str:
    """State of the ROOT stage after HR2S actually ran (path was OPEN).

    Distinct from a boundary short-circuit (NOT_OPENED): here the root engine
    executed, so ACCEPT→COMPLETED, DEFER→DEFERRED, BLOCK→BLOCKED.
    """
    if directive == 'ACCEPT':  return 'COMPLETED'
    if directive == 'DEFER':   return 'DEFERRED'
    return 'BLOCKED'


# ══════════════════════════════════════════════════════════════════════════════
# 4.  نتائج مُعلَّبة لـ BLOCK/DEFER قبل استدعاء HR2S
# ══════════════════════════════════════════════════════════════════════════════

def _blocked_by_boundary(surface: str, boundary: RootEligibilityDecision) -> ExternalRootAnalysis:
    return ExternalRootAnalysis(
        surface            = surface,
        directive          = 'BLOCK',
        stage_state        = 'NOT_OPENED',
        canonical_radicals = (),
        root_profile       = {},
        evidence_ids       = (),
        trace_ids          = (),
        residual_codes     = (
            f'block:root:root_path_closed_by_hokom_boundary:{boundary.kind.value.lower()}',
        ),
        source_engine      = 'hr2s_morphology',
        source_version     = None,
    )


def _deferred_by_boundary(surface: str, boundary: RootEligibilityDecision) -> ExternalRootAnalysis:
    return ExternalRootAnalysis(
        surface            = surface,
        directive          = 'DEFER',
        stage_state        = 'NOT_OPENED',
        canonical_radicals = (),
        root_profile       = {},
        evidence_ids       = (),
        trace_ids          = (),
        residual_codes     = (
            f'defer:root:root_path_not_opened_by_hokom_boundary:{boundary.kind.value.lower()}',
        ),
        source_engine      = 'hr2s_morphology',
        source_version     = None,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 5.  إسقاط نتيجة HR2S إلى ExternalRootAnalysis
# ══════════════════════════════════════════════════════════════════════════════

def _root_stage(hr2s_result: Any):
    """The HR2S ROOT StageResult, or None. Uses ONLY the public schema."""
    stage_fn = getattr(hr2s_result, 'stage', None)
    if callable(stage_fn):
        return stage_fn(_ROOT_STAGE)
    for st in getattr(hr2s_result, 'stages', ()) or ():
        if _enum_value(getattr(st, 'stage', None)) == _ROOT_STAGE:
            return st
    return None


def _selected_root_candidate(root_stage: Any):
    """The selected root candidate (kind == 'root'), or None."""
    for cand in getattr(root_stage, 'candidates', ()) or ():
        if _enum_value(getattr(cand, 'kind', None)) == 'root':
            return getattr(cand, 'value', None)
    return None


def _restoration_candidate_roots(root_stage: Any) -> tuple:
    """The restoration's proposed root tuples (for preserving DEFER candidates)."""
    for cand in getattr(root_stage, 'candidates', ()) or ():
        if _enum_value(getattr(cand, 'kind', None)) == 'restoration':
            return tuple(getattr(getattr(cand, 'value', None), 'root_candidates', ()) or ())
    return ()


def _project_radicals(root_candidate: Any, restoration_roots: tuple) -> tuple[ExternalRadical, ...]:
    """Map HR2S RootRadicals to isolated ExternalRadicals, preserving UnknownRadicals
    (identity=None, resolved=False) and their surface-derived candidate letters."""
    if root_candidate is None:
        return ()
    pos_index = {'fa': 0, 'ayn': 1, 'lam': 2}
    cand_by_pos: dict[str, tuple[str, ...]] = {}
    for pos, idx in pos_index.items():
        letters = {rt[idx] for rt in restoration_roots if len(rt) > idx}
        if len(letters) > 1:
            cand_by_pos[pos] = tuple(sorted(letters))
    out = []
    for r in getattr(root_candidate, 'radicals', ()) or ():
        identity = getattr(r, 'identity', None)
        resolved = bool(getattr(r, 'resolved', False)) and identity not in _PROHIBITED_IDENTITIES
        position = str(getattr(r, 'position', 'UNKNOWN'))
        out.append(ExternalRadical(
            identity     = identity if resolved else None,
            surface_form = getattr(r, 'surface_form', None),
            position     = _POSITION.get(position, position.upper() or 'UNKNOWN'),
            resolved     = resolved,
            candidates   = cand_by_pos.get(position, ()),
        ))
    return tuple(out)


def _project_hr2s_result(
    surface: str,
    hr2s_result: Any,
    *,
    boundary: RootEligibilityDecision,
    engine_version: str | None,
) -> ExternalRootAnalysis:
    """
    Project the REAL HR2S ``MorphologyResult`` (public schema) — the ROOT STAGE ONLY —
    into an ``ExternalRootAnalysis``. Downstream stages (bab/paradigm/masdar/derivation)
    are never consulted: their deferred residuals must NOT downgrade an accepted root.

    Public schema consumed (see docs/integrations/HR2S_ROOT_ENGINE.md):
      hr2s_result.stage('root').decision.directive → Directive enum
      hr2s_result.stage('root').candidates[i].value → RootCandidate (.radicals, .profile)
      hr2s_result.residuals → Residual(.code, .stage)   — filtered to stage == 'root'
      hr2s_result.trace     → TraceEvent(.stage, .message, .ids) — surface/boundary/root
    """
    root_stage = _root_stage(hr2s_result)
    if root_stage is None or getattr(root_stage, 'decision', None) is None:
        raise HR2SProjectionContractError(
            "HR2S result exposes no 'root' stage decision — public schema mismatch."
        )

    raw_directive = getattr(root_stage.decision, 'directive', None)
    if raw_directive is None:
        raise HR2SProjectionContractError("HR2S root stage decision has no directive field.")
    hr2s_directive = str(_enum_value(raw_directive)).strip().upper()
    if hr2s_directive not in ('ACCEPT', 'DEFER', 'BLOCK'):
        raise HR2SProjectionContractError(
            f"unsupported HR2S root directive: {raw_directive!r} → {hr2s_directive!r}"
        )

    # سقف الحدود: Hokom boundary لا يُرقَّى (هنا OPEN، فالقرار قرار الجذر).
    final_directive = enforce_boundary_ceiling(boundary.directive, hr2s_directive)
    stage_state = _projected_stage_state(final_directive)

    # الجذور من مرشح الجذر المختار فقط (لا نقبل ACCEPT ناقصًا).
    root_candidate = _selected_root_candidate(root_stage)
    restoration_roots = _restoration_candidate_roots(root_stage)
    radicals: tuple[ExternalRadical, ...] = ()
    root_profile: Mapping[str, Any] = {}
    if final_directive in ('ACCEPT', 'DEFER') and root_candidate is not None:
        radicals = _project_radicals(root_candidate, restoration_roots)
        profile = getattr(root_candidate, 'profile', None)
        if profile is not None and hasattr(profile, 'to_dict'):
            root_profile = profile.to_dict()

    if final_directive == 'ACCEPT':
        # عقد الأمان: ACCEPT يجب أن يكون جذرًا مكتملًا — لا UnknownRadical، لا ا/ى.
        if len(radicals) != 3 or any((not r.resolved) or (r.identity is None) for r in radicals):
            raise HR2SProjectionContractError(
                f"HR2S returned ACCEPT with an unresolved/incomplete root for {surface!r}: "
                f"{[r.to_dict() for r in radicals]}"
            )
        radicals_out = radicals
    elif final_directive == 'DEFER':
        radicals_out = radicals            # preserve UnknownRadical + candidate radicals
    else:  # BLOCK — no accepted canonical root
        radicals_out = ()
        root_profile = {}

    # البقايا: رموز مرحلة الجذر فقط — لا bab/paradigm/masdar/derivation.
    root_residual_codes = tuple(
        r.code for r in (getattr(hr2s_result, 'residuals', ()) or ())
        if _enum_value(getattr(r, 'stage', None)) == _ROOT_STAGE
    )
    if final_directive != hr2s_directive:
        root_residual_codes = root_residual_codes + (
            f'ceiling:hokom_boundary_lowered_{hr2s_directive.lower()}_to_{final_directive.lower()}',
        )

    # trace: surface/boundary/root فقط — bab governance:DEFERRED ليس قادحًا في الجذر.
    trace_ids = tuple(
        tid
        for ev in (getattr(hr2s_result, 'trace', ()) or ())
        if _enum_value(getattr(ev, 'stage', None)) in _ROOT_SCOPE_STAGES
        for tid in (tuple(getattr(ev, 'ids', ()) or ())
                    or (f"{_enum_value(getattr(ev, 'stage', ''))}:{getattr(ev, 'message', '')}",))
    )

    evidence_ids = tuple(
        e for r in (getattr(root_candidate, 'radicals', ()) or ())
        for e in (getattr(r, 'evidence_ids', ()) or ())
    ) if root_candidate is not None else ()

    return ExternalRootAnalysis(
        surface            = surface,
        directive          = final_directive,
        stage_state        = stage_state,
        canonical_radicals = radicals_out,
        root_profile       = dict(root_profile),
        evidence_ids       = evidence_ids,
        trace_ids          = trace_ids,
        residual_codes     = root_residual_codes,
        source_engine      = 'hr2s_morphology',
        source_version     = engine_version,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 6.  تحميل المحرك الافتراضي (قابل للحقن)
# ══════════════════════════════════════════════════════════════════════════════

def _load_default_engine() -> tuple[Any, str | None]:
    """Load the real HR2S engine via its PUBLIC API only, with its package version.

    Raises HR2SUnavailableError if the package is not installed. Injected in tests via
    ``engine_loader`` so the missing-package path is exercised without touching the env.
    """
    try:
        from hr2s import MorphologyEngine          # public API only
    except ImportError as exc:
        raise HR2SUnavailableError(
            "HR2S morphology package is required for external root analysis. "
            "Install the approved hr2s_morphology package:\n"
            "  pip install -e /path/to/hr2s_morphology"
        ) from exc
    # لا استيراد من hr2s.root, hr2s.boundary, hr2s.surface
    engine = MorphologyEngine()
    try:
        import importlib.metadata as meta
        version = meta.version('hr2s_morphology')
    except Exception:
        version = None
    return engine, version


# ══════════════════════════════════════════════════════════════════════════════
# 7.  HR2SRootAdapter
# ══════════════════════════════════════════════════════════════════════════════

class HR2SRootAdapter:
    """
    Adapter بين Hokom ومحرك hr2s_morphology الخارجي.

    يُهيئ MorphologyEngine مرة واحدة ويُعيد استخدامه.
    يفرض سقف الحدود قبل كل استدعاء لـHR2S.

    الاستخدام:
        adapter = HR2SRootAdapter()
        result = adapter.analyze("ضَرَبَ", boundary=assess_boundary("ضَرَبَ"))

    الحقن (للاختبار): مرّر ``engine`` جاهزًا أو ``engine_loader`` قابلًا للاستدعاء.
    """

    def __init__(self, engine: Any = None, engine_loader=None) -> None:
        self._engine: Any = engine
        self._engine_version: str | None = None
        self._engine_loader = engine_loader or _load_default_engine

    def _get_engine(self) -> Any:
        """تهيئة بطيئة للمحرك عبر الـ loader المحقون — يُرفع استثناء واضح عند الغياب."""
        if self._engine is not None:
            return self._engine
        loaded = self._engine_loader()
        if isinstance(loaded, tuple):
            self._engine, self._engine_version = loaded
        else:
            self._engine = loaded
        return self._engine

    def analyze(
        self,
        surface: str,
        *,
        boundary: RootEligibilityDecision,
    ) -> ExternalRootAnalysis:
        """
        حلّل السطح بعد تطبيق سقف الحدود.

        BLOCK → لا استدعاء لـHR2S
        DEFER → لا استدعاء لـHR2S
        OPEN  → استدعاء HR2S مرة واحدة بالضبط
        """
        if boundary.directive is RootPathDirective.BLOCK:
            return _blocked_by_boundary(surface, boundary)

        if boundary.directive is RootPathDirective.DEFER:
            return _deferred_by_boundary(surface, boundary)

        # OPEN: استدعاء HR2S
        engine = self._get_engine()
        hr2s_result = engine.analyze_surface(surface)

        return _project_hr2s_result(
            surface,
            hr2s_result,
            boundary=boundary,
            engine_version=self._engine_version,
        )

    def analyze_surface_raw(self, surface: str) -> Any:
        """
        للاختبار المباشر فقط: يُعيد نتيجة HR2S الخام بلا إسقاط.
        لا تستخدم هذا في منطق Hokom الإنتاجي.
        """
        return self._get_engine().analyze_surface(surface)
