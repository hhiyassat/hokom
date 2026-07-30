"""
claim_key.py — deterministic canonical identifiers for pipeline artifacts.

claim_key(surface, stage_id, rule_id) → str
    Deterministic SHA-256-based key. Language-neutral. Carries through
    all 19 stages unchanged (canonical ID invariance law).

evaluation_id(surface, pipeline_run_id) → str
    Unique per pipeline invocation, stable across re-runs with same input.

These IDs are used as:
    - Report row identifiers (ayat_al_dayn CSV)
    - Taaqol trace ledger keys
    - Integrity gate cross-references
"""
from __future__ import annotations

import hashlib
import unicodedata


def _normalize_for_key(text: str) -> str:
    """NFC-normalize and strip leading/trailing whitespace."""
    return unicodedata.normalize("NFC", text).strip()


def claim_key(
    surface: str,
    stage_id: str,
    rule_id: str,
    *,
    salt: str = "",
) -> str:
    """
    Produce a deterministic 16-hex-char claim key.

    Parameters
    ----------
    surface   : Arabic surface text (NFC-normalized before hashing)
    stage_id  : Canonical Saleh layer ID (e.g. "P3_ROOT_STEM_CLOSURE")
    rule_id   : Generating rule / adapter method name
    salt      : Optional disambiguation string (default: "")

    Returns
    -------
    str : "CK-" + first 16 hex chars of SHA-256(components)
    """
    surface_n = _normalize_for_key(surface)
    raw = f"{surface_n}\x00{stage_id}\x00{rule_id}\x00{salt}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"CK-{digest[:16]}"


def evaluation_id(
    surface: str,
    pipeline_run_id: str,
) -> str:
    """
    Produce a deterministic 16-hex-char evaluation ID for a full pipeline run.

    Parameters
    ----------
    surface         : Arabic surface text (NFC-normalized)
    pipeline_run_id : Caller-supplied run identifier (e.g. UUID, timestamp)

    Returns
    -------
    str : "EV-" + first 16 hex chars of SHA-256(surface + run_id)
    """
    surface_n = _normalize_for_key(surface)
    raw = f"{surface_n}\x00{pipeline_run_id}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"EV-{digest[:16]}"
