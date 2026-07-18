#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p2_projection/root_projection.py — RootProjection P2 (R-10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

الموقع الوحيد لإسقاط نتيجة الجذر إلى نموذج Hokom على مستوى P2.

القاعدة المعمارية:
  - Hokom (PreRoot) يقرر هل يُفتح مسار الجذر.
  - HR2S (عبر hr2s_root_adapter) يحلّل الجذر إذا فُتح المسار فقط.
  - RootProjection يُسقط نتيجة المحرّك (أو حالة عدم الاستدعاء) إلى DTO ثابت.

قواعد الإسقاط:
  HR2S ACCEPT → canonical_root مملوء، لا UnknownRadical، لا ا/ى كهوية جذرية، ء محفوظة.
  HR2S DEFER  → canonical_root=None، المواضع غير المحلولة محفوظة، لا جذر زائف.
  HR2S BLOCK  → canonical_root=None، دليل العائق محفوظ.
  PreRoot BLOCK/DEFER → HR2S لا يُستدعى → directive=BLOCK/DEFER،
                        stage_state='NOT_OPENED'، canonical_root=None.

هذا الملف لا يستورد أي وحدة داخلية من hr2s (لا hr2s.root/boundary/surface).
يستهلك ناتج المحوّل (ExternalRootAnalysis) بالبنية فقط (duck-typed).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only, no runtime hr2s coupling
    from pipeline.integrations.hr2s_root_adapter import ExternalRootAnalysis


# ══════════════════════════════════════════════════════════════════════════════
# 1.  خطأ عقد الإسقاط
# ══════════════════════════════════════════════════════════════════════════════

class RootProjectionContractError(RuntimeError):
    """يُرفع عند خرق عقد RootProjection:
      - ACCEPT بلا جذر محلول
      - ACCEPT يحتوي UnknownRadical (هوية غير محلولة)
      - ACCEPT يحتوي ا/ى كهوية جذرية
      - directive غير معروف (خارج ACCEPT|DEFER|BLOCK)
    الفشل صريح دائمًا — لا تخفيض صامت إلى BLOCK.
    """
    pass


# الحروف الممنوعة كهوية جذرية نهائية (ألف/ياء اللين والهمزات المحمولة).
# ء (U+0621) المفردة مسموحة — تُحفظ كما هي (قَرَأَ → ء لا أ).
_PROHIBITED_ROOT_IDENTITIES = frozenset({"ا", "ى", "أ", "إ", "ؤ", "ئ", "آ", "?", "", None})

_VALID_DIRECTIVES = ("ACCEPT", "DEFER", "BLOCK")

# إسقاط حالة مرحلة المحوّل إلى مفردات RootProjection: OPENED | DEFERRED | NOT_OPENED
_STAGE_STATE_MAP = {
    "COMPLETED":  "OPENED",      # HR2S ran and resolved the root
    "DEFERRED":   "DEFERRED",    # HR2S ran and deferred
    "BLOCKED":    "OPENED",      # root path was opened; HR2S blocked the form
    "NOT_OPENED": "NOT_OPENED",  # boundary/pre-root short-circuit — HR2S never ran
}


# ══════════════════════════════════════════════════════════════════════════════
# 2.  RootProjection — DTO
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RootProjection:
    """
    إسقاط نتيجة الجذر على مستوى P2.

    input_surface       : السطح الأصلي كما ورد (ثابت).
    analyzed_host       : المضيف الذي حُلِّل فعليًا (بعد فصل السوابق/اللواحق).
    directive           : 'ACCEPT' | 'DEFER' | 'BLOCK'
    stage_state         : 'OPENED' | 'DEFERRED' | 'NOT_OPENED'
    canonical_root      : الجذر الكنوني إن قُبل، وإلا None.
    radicals            : تمثيل المكوّنات (dicts) — يحفظ UnknownRadical عند DEFER.
    root_profile        : بيانات وصفية من المحرّك (وزن/بنية...).
    unresolved_positions: مواضع الجذور غير المحلولة (FA|AYN|LAM...).
    evidence_ids        : مرجعيات الشواهد.
    trace_ids           : مسار التحليل.
    residual_codes      : رموز التحفظ.
    source_engine       : اسم المحرّك المصدر.
    source_version      : نسخة المحرّك إن توفّرت.
    """
    input_surface:        str
    analyzed_host:        str
    directive:            str
    stage_state:          str
    canonical_root:       Optional[tuple]
    radicals:             tuple
    root_profile:         Mapping[str, Any]
    unresolved_positions: tuple
    evidence_ids:         tuple
    trace_ids:            tuple
    residual_codes:       tuple
    source_engine:        str = "hr2s_morphology"
    source_version:       Optional[str] = None

    # ── تسلسل JSON ────────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "input_surface":        self.input_surface,
            "analyzed_host":        self.analyzed_host,
            "directive":            self.directive,
            "stage_state":          self.stage_state,
            "canonical_root":       (list(self.canonical_root)
                                     if self.canonical_root is not None else None),
            "radicals":             [dict(r) for r in self.radicals],
            "root_profile":         dict(self.root_profile),
            "unresolved_positions": list(self.unresolved_positions),
            "evidence_ids":         list(self.evidence_ids),
            "trace_ids":            list(self.trace_ids),
            "residual_codes":       list(self.residual_codes),
            "source_engine":        self.source_engine,
            "source_version":       self.source_version,
        }

    # ── بنّاء: عدم استدعاء HR2S (PreRoot BLOCK/DEFER) ─────────────────────────
    @classmethod
    def not_opened(
        cls,
        *,
        input_surface: str,
        analyzed_host: str,
        directive: str,
        residual_codes: Optional[tuple] = None,
        evidence_ids: tuple = (),
        trace_ids: tuple = (),
        source_engine: str = "hr2s_morphology",
        source_version: Optional[str] = None,
    ) -> "RootProjection":
        """RootProjection عندما لم يُستدعَ HR2S (المسار لم يُفتح من PreRoot).

        directive يجب أن يكون 'BLOCK' أو 'DEFER'.
        stage_state = 'NOT_OPENED'، canonical_root = None.
        residual افتراضي: '<dir>:root:root_path_not_opened_by_pre_root'.
        """
        if directive not in ("BLOCK", "DEFER"):
            raise RootProjectionContractError(
                f"not_opened requires BLOCK|DEFER, got {directive!r}"
            )
        if residual_codes is None:
            residual_codes = (
                f"{directive.lower()}:root:root_path_not_opened_by_pre_root",
            )
        return cls(
            input_surface        = input_surface,
            analyzed_host        = analyzed_host,
            directive            = directive,
            stage_state          = "NOT_OPENED",
            canonical_root       = None,
            radicals             = (),
            root_profile         = {},
            unresolved_positions = (),
            evidence_ids         = tuple(evidence_ids),
            trace_ids            = tuple(trace_ids),
            residual_codes       = tuple(residual_codes),
            source_engine        = source_engine,
            source_version       = source_version,
        )

    # ── بنّاء: إسقاط ناتج المحوّل (HR2S ران فعلاً) ────────────────────────────
    @classmethod
    def from_external_root(
        cls,
        ext: "ExternalRootAnalysis",
        *,
        analyzed_host: Optional[str] = None,
        input_surface: Optional[str] = None,
    ) -> "RootProjection":
        """أسقِط ExternalRootAnalysis (ناتج hr2s_root_adapter) إلى RootProjection.

        يُعامَل ext بالبنية فقط (duck-typed) لتفادي أي ارتباط باستيراد hr2s.
        يُعيد التحقق من عقد ACCEPT استقلالًا عن المحوّل (دفاع في العمق).
        """
        surface = input_surface if input_surface is not None else ext.surface
        host    = analyzed_host if analyzed_host is not None else ext.surface

        directive = str(ext.directive).strip().upper()
        if directive not in _VALID_DIRECTIVES:
            raise RootProjectionContractError(
                f"unknown root directive {ext.directive!r} for {surface!r}"
            )

        raw_stage = str(getattr(ext, "stage_state", "")).strip().upper()
        stage_state = _STAGE_STATE_MAP.get(raw_stage)
        if stage_state is None:
            raise RootProjectionContractError(
                f"unknown external stage_state {raw_stage!r} for {surface!r}"
            )

        radicals = tuple(ext.canonical_radicals or ())
        radical_dicts = tuple(
            r.to_dict() if hasattr(r, "to_dict") else dict(r) for r in radicals
        )
        unresolved_positions = tuple(
            getattr(r, "position", "UNKNOWN")
            for r in radicals
            if not bool(getattr(r, "resolved", False))
        )

        canonical_root: Optional[tuple] = None
        if directive == "ACCEPT":
            # عقد الأمان: ACCEPT = جذر مكتمل محلول، لا UnknownRadical، لا ا/ى.
            identities = tuple(getattr(r, "identity", None) for r in radicals)
            if (not radicals
                    or any(not bool(getattr(r, "resolved", False)) for r in radicals)
                    or any(idn in _PROHIBITED_ROOT_IDENTITIES for idn in identities)):
                raise RootProjectionContractError(
                    f"HR2S ACCEPT with unresolved/prohibited root for {surface!r}: "
                    f"{[r.to_dict() if hasattr(r, 'to_dict') else r for r in radicals]}"
                )
            canonical_root = identities
        # DEFER/BLOCK → canonical_root يبقى None (لا جذر زائف).

        root_profile = dict(getattr(ext, "root_profile", {}) or {})
        if directive == "BLOCK":
            root_profile = {}

        return cls(
            input_surface        = surface,
            analyzed_host        = host,
            directive            = directive,
            stage_state          = stage_state,
            canonical_root       = canonical_root,
            radicals             = radical_dicts,
            root_profile         = root_profile,
            unresolved_positions = unresolved_positions,
            evidence_ids         = tuple(getattr(ext, "evidence_ids", ()) or ()),
            trace_ids            = tuple(getattr(ext, "trace_ids", ()) or ()),
            residual_codes       = tuple(getattr(ext, "residual_codes", ()) or ()),
            source_engine        = getattr(ext, "source_engine", "hr2s_morphology"),
            source_version       = getattr(ext, "source_version", None),
        )

    # ── بنّاء: إسقاط نتيجة Hokom المحلي (RootResolution) ─────────────────────
    @classmethod
    def from_root_resolution(
        cls,
        resolution: Any,   # RootResolution — duck-typed لتجنّب الاستيراد الدائري
        *,
        input_surface: str,
    ) -> "RootProjection":
        """أسقِط RootResolution (محرك Hokom المحلي) إلى RootProjection.

        لا استدعاء لـ HR2S — المحرك المحلي مصدر الحقيقة.

        stage_state:
          ACCEPT → 'OPENED'
          DEFER  → 'DEFERRED'
          BLOCK  → 'NOT_OPENED'
        """
        directive = str(resolution.directive).strip().upper()
        if directive not in _VALID_DIRECTIVES:
            raise RootProjectionContractError(
                f"unknown directive from RootResolution: {resolution.directive!r}"
            )

        stage_state_map = {
            'ACCEPT': 'OPENED',
            'DEFER':  'DEFERRED',
            'BLOCK':  'NOT_OPENED',
        }
        stage_state = stage_state_map[directive]

        # ACCEPT: تحقق من عقد السلامة
        canonical_root = resolution.canonical_root
        if directive == 'ACCEPT':
            if not canonical_root:
                raise RootProjectionContractError(
                    f"ACCEPT resolution without canonical_root for {input_surface!r}"
                )
            if any(idn in _PROHIBITED_ROOT_IDENTITIES for idn in canonical_root):
                raise RootProjectionContractError(
                    f"ACCEPT resolution with prohibited root identity for "
                    f"{input_surface!r}: {canonical_root!r}"
                )
        else:
            canonical_root = None

        root_profile = dict(getattr(resolution, 'root_profile', {}) or {})

        return cls(
            input_surface        = input_surface,
            analyzed_host        = resolution.analyzed_host,
            directive            = directive,
            stage_state          = stage_state,
            canonical_root       = canonical_root,
            radicals             = (),
            root_profile         = root_profile,
            unresolved_positions = (),
            evidence_ids         = tuple(getattr(resolution, 'evidence_ids', ())),
            trace_ids            = tuple(getattr(resolution, 'trace_ids', ())),
            residual_codes       = tuple(getattr(resolution, 'residual_codes', ())),
            source_engine        = 'HOKOM_ROOT_ENGINE',
            source_version       = None,
        )


# ══════════════════════════════════════════════════════════════════════════════
# 3.  أوركسترا الربط: PreRoot → (HR2S أو عدم استدعاء) → RootProjection
# ══════════════════════════════════════════════════════════════════════════════

def project_root(
    *,
    input_surface: str,
    analyzed_host: str,
    root_path_directive: str,
    adapter: Any,
    boundary: Any = None,
    evidence_ids: tuple = (),
    trace_ids: tuple = (),
) -> RootProjection:
    """اربط قرار PreRoot بمحرّك الجذر وأنتج RootProjection.

    root_path_directive : 'OPEN' | 'DEFER' | 'BLOCK' (من PreRootDecision).
      OPEN         → استدعِ المحوّل مرة واحدة على analyzed_host ثم أسقِط.
      DEFER/BLOCK  → لا تستدعِ HR2S إطلاقًا → RootProjection.not_opened.

    adapter  : HR2SRootAdapter (أو ما يماثله ببنية .analyze(surface, boundary=...)).
    boundary : RootEligibilityDecision للمضيف — لازم عند OPEN.
    """
    directive = str(root_path_directive).strip().upper()

    if directive in ("BLOCK", "DEFER"):
        # لا استدعاء لـ HR2S — المسار لم يُفتح من PreRoot.
        return RootProjection.not_opened(
            input_surface = input_surface,
            analyzed_host = analyzed_host,
            directive     = directive,
            evidence_ids  = evidence_ids,
            trace_ids     = trace_ids,
        )

    if directive != "OPEN":
        raise RootProjectionContractError(
            f"unknown root_path_directive {root_path_directive!r}"
        )

    if boundary is None:
        raise RootProjectionContractError(
            "OPEN route requires a boundary decision for the analyzed host."
        )

    ext = adapter.analyze(analyzed_host, boundary=boundary)
    return RootProjection.from_external_root(
        ext,
        analyzed_host = analyzed_host,
        input_surface = input_surface,
    )


def project_root_from_pre_root(decision: Any, *, adapter: Any, boundary: Any = None) -> RootProjection:
    """راحة: اقرأ الحقول من PreRootDecision ثم استدعِ project_root.

    يستهلك: decision.input_surface, decision.host_surface,
             decision.root_path_directive, decision.evidence_ids, decision.trace_ids.
    """
    return project_root(
        input_surface       = decision.input_surface,
        analyzed_host       = decision.host_surface,
        root_path_directive = decision.root_path_directive,
        adapter             = adapter,
        boundary            = boundary,
        evidence_ids        = tuple(getattr(decision, "evidence_ids", ()) or ()),
        trace_ids           = tuple(getattr(decision, "trace_ids", ()) or ()),
    )
