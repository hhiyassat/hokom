#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p3_candidate/root_candidate.py — RootCandidate P3 (R-10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يستهلك RootProjection من P2 ويُنتج RootCandidate.

قواعد P3 (رتابة صارمة):
  Projection ACCEPT → Candidate ACCEPT
  Projection DEFER  → Candidate DEFER
  Projection BLOCK  → Candidate BLOCK
  P3 لا يرقّي ولا يخفض من تلقاء نفسه.
  P3 لا يستدعي HR2S ولا يقرأ السطح مباشرة — يستهلك الإسقاط فقط.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pipeline.p2_projection.root_projection import RootProjection


class RootCandidateContractError(RuntimeError):
    """يُرفع عند خرق عقد RootCandidate:
      - ACCEPT بلا جذر محلول
      - ACCEPT يحتوي ا/ى كهوية جذرية
      - directive غير معروف (خارج ACCEPT|DEFER|BLOCK)
    """
    pass


_PROHIBITED_ROOT_IDENTITIES = frozenset({"ا", "ى", "أ", "إ", "ؤ", "ئ", "آ", "?", "", None})
_VALID_DIRECTIVES = ("ACCEPT", "DEFER", "BLOCK")


@dataclass(frozen=True)
class RootCandidate:
    """
    مرشّح الجذر على مستوى P3.

    surface           : السطح الأصلي (منقول من الإسقاط، لا يُقرأ مباشرة).
    host_surface      : المضيف المُحلَّل (analyzed_host من الإسقاط).
    directive         : 'ACCEPT' | 'DEFER' | 'BLOCK' (= directive الإسقاط).
    canonical_root    : الجذر الكنوني أو None (= canonical_root الإسقاط).
    root_profile      : بيانات وصفية.
    evidence_ids      : مرجعيات الشواهد.
    trace_ids         : مسار التحليل.
    residual_codes    : رموز التحفظ.
    source_projection : اسم الإسقاط المصدر (ثابت 'RootProjection').
    """
    surface:           str
    host_surface:      str
    directive:         str
    canonical_root:    Optional[tuple]
    root_profile:      Mapping[str, Any]
    evidence_ids:      tuple
    trace_ids:         tuple
    residual_codes:    tuple
    source_projection: str = "RootProjection"

    def to_dict(self) -> dict:
        return {
            "surface":           self.surface,
            "host_surface":      self.host_surface,
            "directive":         self.directive,
            "canonical_root":    (list(self.canonical_root)
                                  if self.canonical_root is not None else None),
            "root_profile":      dict(self.root_profile),
            "evidence_ids":      list(self.evidence_ids),
            "trace_ids":         list(self.trace_ids),
            "residual_codes":    list(self.residual_codes),
            "source_projection": self.source_projection,
        }

    @classmethod
    def from_projection(cls, projection: "RootProjection") -> "RootCandidate":
        """اشتق RootCandidate من RootProjection دون ترقية أو تخفيض.

        لا استدعاء لـ HR2S، لا قراءة للسطح — يُنسخ directive/canonical_root كما هما.
        """
        directive = str(projection.directive).strip().upper()
        if directive not in _VALID_DIRECTIVES:
            raise RootCandidateContractError(
                f"unknown projection directive {projection.directive!r}"
            )

        canonical_root = projection.canonical_root

        if directive == "ACCEPT":
            if not canonical_root:
                raise RootCandidateContractError(
                    f"ACCEPT projection without a resolved root for "
                    f"{projection.input_surface!r}"
                )
            if any(idn in _PROHIBITED_ROOT_IDENTITIES for idn in canonical_root):
                raise RootCandidateContractError(
                    f"ACCEPT projection with prohibited root identity for "
                    f"{projection.input_surface!r}: {canonical_root!r}"
                )
        else:
            # DEFER/BLOCK لا يجوز أن يحملا جذرًا كنونيًا (رتابة الإسقاط).
            if canonical_root is not None:
                raise RootCandidateContractError(
                    f"{directive} projection must not carry a canonical_root: "
                    f"{canonical_root!r}"
                )

        return cls(
            surface           = projection.input_surface,
            host_surface      = projection.analyzed_host,
            directive         = directive,
            canonical_root    = canonical_root,
            root_profile      = dict(projection.root_profile),
            evidence_ids      = tuple(projection.evidence_ids),
            trace_ids         = tuple(projection.trace_ids),
            residual_codes    = tuple(projection.residual_codes),
            source_projection = "RootProjection",
        )
