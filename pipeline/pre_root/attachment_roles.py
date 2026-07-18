#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/pre_root/attachment_roles.py — SHIM (R-9 refactoring)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The canonical implementation has moved to:
  pipeline/p2_projection/attachment_projection.py

This file exists solely to preserve import compatibility for existing code
and tests that import from the pre_root path. All names are re-exported
unchanged. Do not add logic here.
"""

from pipeline.p2_projection.attachment_projection import *  # noqa: F401,F403
from pipeline.p2_projection.attachment_projection import (  # noqa: F401
    AttachmentRole,
    AttachmentProjection,
    INFLECTIONAL_SUBJECT_WAW_AL_JAMAA,
)

__all__ = [
    "AttachmentRole",
    "AttachmentProjection",
    "INFLECTIONAL_SUBJECT_WAW_AL_JAMAA",
]
