"""Hokom runtime bootstrap utilities (C13 §6 identity + §7 provenance)."""
from __future__ import annotations

from .pipeline_identity import ensure_hokom_pipeline_identity, verify_hokom_pipeline_identity
from .provenance import (
    canonical_source_head,
    canonical_source_head_full,
    provenance_metadata,
    read_governed_source_head,
    read_dynamic_git_head,
)

__all__ = [
    "ensure_hokom_pipeline_identity",
    "verify_hokom_pipeline_identity",
    "canonical_source_head",
    "canonical_source_head_full",
    "provenance_metadata",
    "read_governed_source_head",
    "read_dynamic_git_head",
]
