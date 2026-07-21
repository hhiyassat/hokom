#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p3_pre_root/ — Canonical Radical Accounting
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01

يُحدِّد مَن يمتلك كل حرف في الكلمة:
  - جذر حقيقي (RADICAL)
  - زيادة اشتقاقية (DERIVATIONAL_EXTENSION)
  - بادئة صرفية (INFLECTIONAL_PREFIX)
  - لاحقة صرفية (INFLECTIONAL_SUFFIX)
  - تضعيف صوتي (PHONOLOGICAL_DUPLICATION)
  - حرف علة سطحي (WEAK_RADICAL_SURFACE)
"""

from pipeline.p3_pre_root.canonical_radical_accounting import (
    CanonicalRadicalAccounting,
    SlotClass,
    process_canonical_radical_accounting,
)

__all__ = [
    'CanonicalRadicalAccounting',
    'SlotClass',
    'process_canonical_radical_accounting',
]
