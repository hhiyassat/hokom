"""
hokom.canonical.constitutional — Constitutional judgment model.

Implements the jurisprudential method:
    الوضع → السبب → الشرط → المانع → العلة → القادح
    → الصحة → الفساد → البطلان → التأجيل → الأثر → البقايا

Public API:
    WadContract, SababEvidence, ShartRequirement, ManiBlocker
    IllahRationale, QadihDefect
    ConstitutionalStatus, ConstitutionalJudgment
    AtharEffect, BaqayaResidual
"""
from .contracts import (
    WadContract,
    SababEvidence,
    ShartRequirement,
    ManiBlocker,
    IllahRationale,
    QadihDefect,
    ConstitutionalStatus,
    ConstitutionalJudgment,
    AtharEffect,
    BaqayaResidual,
)

__all__ = [
    "WadContract",
    "SababEvidence",
    "ShartRequirement",
    "ManiBlocker",
    "IllahRationale",
    "QadihDefect",
    "ConstitutionalStatus",
    "ConstitutionalJudgment",
    "AtharEffect",
    "BaqayaResidual",
]
