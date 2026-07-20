#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p0_segmentation/__init__.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hokom Clitic Segmenter — canonical package entry point.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
SEGMENTATION_ENGINE_ID = 'HOKOM_CLITIC_SEGMENTER'
"""
from .models import (
    SEGMENTATION_ENGINE_ID,
    SEGMENTATION_CANONICAL_OWNER,
    SEGMENTATION_CONTRACT_VERSION,
    SEGMENTATION_CANONICAL_ENTRYPOINT,
    SegmentationVerdict,
    SegmentRole,
    SegmentKind,
    SegmentationRequest,
    Segment,
    SegmentCandidate,
    SegmentEvidence,
    SegmentContradiction,
    SegmentBundle,
    SegmentationResidual,
    SegmentationTraceEvent,
    SegmentationOwnershipGate,
)
from .engine import segment_token

__all__ = [
    'SEGMENTATION_ENGINE_ID',
    'SEGMENTATION_CANONICAL_OWNER',
    'SEGMENTATION_CONTRACT_VERSION',
    'SEGMENTATION_CANONICAL_ENTRYPOINT',
    'SegmentationVerdict',
    'SegmentRole',
    'SegmentKind',
    'SegmentationRequest',
    'Segment',
    'SegmentCandidate',
    'SegmentEvidence',
    'SegmentContradiction',
    'SegmentBundle',
    'SegmentationResidual',
    'SegmentationTraceEvent',
    'SegmentationOwnershipGate',
    'segment_token',
]
