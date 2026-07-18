#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_mushtaqat — Phase 4D: Mushtaqat (Arabic Derivative Forms)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يُصدِّر الواجهة العامة لـ Phase 4D.
"""

from pipeline.p4_mushtaqat.models import (
    MushtaqCandidate,
    MushtaqProjection,
    Phase4DResult,
)
from pipeline.p4_mushtaqat.phase4d_orchestrator import project_mushtaqat_with_licensing

__all__ = [
    "MushtaqCandidate",
    "MushtaqProjection",
    "Phase4DResult",
    "project_mushtaqat_with_licensing",
]
