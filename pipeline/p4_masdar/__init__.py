#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_masdar/ — Phase 4C: Masdar Projection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Governing principle:
  Accepting root + wazn + bab does NOT automatically accept masdar.

  - Mujarrad (thulathi bare) masadars are sami'i (heard/lexical) —
    they cannot be predicted structurally. → DEFER / SAMI3I_REQUIRED
  - Augmented form (mazid) masadars follow structural patterns from
    the form number. → STRUCTURAL_INFERENCE / ACCEPT (tentative)

Public API:
  from pipeline.p4_masdar.phase4c_orchestrator import project_masdar_with_licensing
  from pipeline.p4_masdar.models import Phase4CResult, MasdarProjection, MasdarCandidate
"""

from pipeline.p4_masdar.models import (
    MasdarCandidate,
    MasdarProjection,
    Phase4CResult,
)
from pipeline.p4_masdar.phase4c_orchestrator import project_masdar_with_licensing

__all__ = [
    "MasdarCandidate",
    "MasdarProjection",
    "Phase4CResult",
    "project_masdar_with_licensing",
]
