"""Canonical source-head / artifact-head provenance contract (C13 §7).

Solves the self-referential head problem exposed in
HOKOM-AYAT-AL-DAYN-CANONICAL-BASELINE-REBIND-01:

  regen(HEAD=X)  → baseline.head = X
  commit baseline → HEAD becomes Y (governance mutation, not source)
  regen(HEAD=Y)  → baseline.head = Y ≠ X → mutation test fails

Three governed levels:

  ANALYSIS_SOURCE_HEAD =
      the commit containing the executable source code whose behavior
      the canonical artifact family reflects. Stable across artifact-only
      or governance-only commits.

  CANONICAL_ARTIFACT_COMMIT =
      the commit that adds/updates the canonical artifact family.
      Does NOT bump analysis_source_head.

  GOVERNANCE_CLOSURE_COMMIT =
      the commit that adds closure reports and requirement statuses.
      Does NOT bump analysis_source_head.

Owners update `governance/analysis_source_head.txt` explicitly only
when the executable source code that produces artifacts changes.

If the governance file is absent, the current git HEAD is used
(preserving legacy behavior for demo/runtime modes).
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional

_HOKOM_ROOT: Path = Path(__file__).resolve().parents[3]
_GOVERNANCE_HEAD_FILE: Path = _HOKOM_ROOT / "governance" / "analysis_source_head.txt"


def read_governed_source_head() -> Optional[str]:
    """Return the owner-declared analysis source head SHA, or None if not set.

    Reserved sentinel values are treated as "not set" so the caller
    falls back to dynamic git HEAD:
      - CANDIDATE_ONLY
      - TEMPORARY_INVALID_FOR_FINAL_PROVENANCE
    Any value that does not look like a 40-char hex SHA is also rejected.
    """
    if not _GOVERNANCE_HEAD_FILE.is_file():
        return None
    content = _GOVERNANCE_HEAD_FILE.read_text().strip()
    if not content:
        return None
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Reject sentinels
        if line in ("CANDIDATE_ONLY", "TEMPORARY_INVALID_FOR_FINAL_PROVENANCE"):
            return None
        # Only accept 40-char hex SHAs
        if len(line) == 40 and all(c in "0123456789abcdefABCDEF" for c in line):
            return line
    return None


def read_dynamic_git_head(short: bool = False) -> str:
    """Return the current git HEAD SHA via subprocess."""
    cmd = ["git", "rev-parse", "--short", "HEAD"] if short else ["git", "rev-parse", "HEAD"]
    try:
        return subprocess.check_output(
            cmd, cwd=_HOKOM_ROOT, stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "UNKNOWN"


def canonical_source_head(short: bool = False) -> str:
    """Return the source head for canonical artifact generation.

    Priority:
      1. governance/analysis_source_head.txt (owner-declared)
      2. Dynamic git HEAD (fallback for runtime/demo modes)

    When called during canonical generation, this returns the stable
    owner-declared SHA so regenerating an artifact produces byte-identical
    provenance metadata across artifact-only commits.
    """
    governed = read_governed_source_head()
    if governed:
        return governed[:12] if short else governed
    return read_dynamic_git_head(short=short)


def canonical_source_head_full() -> str:
    """Return the full 40-char source head SHA."""
    return canonical_source_head(short=False)


def provenance_metadata() -> dict:
    """Return provenance metadata for embedding in canonical artifacts."""
    return {
        "analysis_source_head": canonical_source_head_full(),
        "analysis_source_head_short": canonical_source_head(short=True),
        "governance_head_file_present": _GOVERNANCE_HEAD_FILE.is_file(),
        "governance_head_file": str(_GOVERNANCE_HEAD_FILE),
    }
