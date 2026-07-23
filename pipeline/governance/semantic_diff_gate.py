#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/semantic_diff_gate.py

HOKOM-CLOSED-CONTRACT-SEMANTIC-REGRESSION-FIREWALL-01

Reusable semantic diff gate.  Compares baseline and candidate pipeline
outputs field-by-field and rejects unexpected changes.

Every future phase must declare:
  EXPECTED_CHANGED_TOKENS  — surfaces whose output will change
  EXPECTED_CHANGED_FIELDS  — fields that are expected to change
  EXPECTED_REASON_CODES    — why each change is authorized

The gate fails when:
  UNEXPECTED_SEMANTIC_DIFFS > 0
  CLOSED_CONTRACT_REGRESSIONS > 0
  TERMINAL_BOUNDARY_OVERRIDES > 0

Usage:
    gate = SemanticDiffGate(
        baseline=baseline_snapshot,
        intended_changes={'اللَّهُ': {'word_class': 'ISM'}},
    )
    gate.compare(candidate_snapshot)   # raises DiffRejected on failure
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pipeline.governance.terminal_boundary_guard import is_terminal_boundary

# Fields that are NOT semantic (volatile IDs, timestamps, internal traces)
_NON_SEMANTIC_FIELDS = frozenset({
    'taaqol_runtime',
    'trace_ids',
    'evidence_ids',
    'paradigm_rule_ids',
    'residual_codes',
    '_route_v',           # alias only — not primary semantic
})

# Fields that ARE semantic and must be compared
_SEMANTIC_FIELDS = (
    'word_class',
    'word_class_subclass',
    'boundary_type',
    'jamid_verdict',
    'tense_aspect',
    'mood',
    'voice',
    'person',
    'number',
    'gender',
    'final_root',
    'mabni_verdict',
)


class DiffRejected(Exception):
    """Raised when the semantic diff gate detects unexpected changes."""
    def __init__(self, report: 'DiffReport') -> None:
        self.report = report
        super().__init__(
            f"UNEXPECTED_SEMANTIC_DIFFS={report.unexpected_diffs}, "
            f"CLOSED_CONTRACT_REGRESSIONS={report.closed_contract_regressions}, "
            f"TERMINAL_BOUNDARY_OVERRIDES={report.terminal_boundary_overrides}: "
            f"{report.details}"
        )


@dataclass
class DiffReport:
    unexpected_diffs:             int = 0
    closed_contract_regressions:  int = 0
    terminal_boundary_overrides:  int = 0
    details:                      list[str] = field(default_factory=list)

    @property
    def closed(self) -> bool:
        return (
            self.unexpected_diffs == 0
            and self.closed_contract_regressions == 0
            and self.terminal_boundary_overrides == 0
        )


class SemanticDiffGate:
    """
    Compare baseline and candidate pipeline output snapshots.

    Snapshots are dicts of the form: {surface: hokom_result_dict}.

    Parameters
    ----------
    baseline : dict[str, dict]
        Baseline snapshot (before the candidate phase).
    intended_changes : dict[str, dict]
        Declared intended changes per surface: {surface: {field: new_value}}.
        Only declared changes are allowed; any undeclared change is unexpected.
    """

    def __init__(
        self,
        baseline: dict[str, dict],
        intended_changes: dict[str, dict] | None = None,
    ) -> None:
        self._baseline = baseline
        self._intended = intended_changes or {}

    def compare(self, candidate: dict[str, dict]) -> DiffReport:
        """
        Compare candidate against baseline.  Raises DiffRejected if any
        unexpected change, closed-contract regression, or terminal-boundary
        override is found.

        Returns a closed DiffReport if all changes are expected.
        """
        report = DiffReport()
        all_surfaces = set(self._baseline) | set(candidate)

        for surface in sorted(all_surfaces):
            base_rec   = self._baseline.get(surface, {})
            cand_rec   = candidate.get(surface, {})
            intended   = self._intended.get(surface, {})

            for f in _SEMANTIC_FIELDS:
                bv = base_rec.get(f)
                cv = cand_rec.get(f)
                if bv == cv:
                    continue   # no change

                # Change detected — is it declared?
                if f in intended and intended[f] == cv:
                    continue   # declared intended change — ok

                # Undeclared change
                detail = (
                    f"UNEXPECTED: surface={surface!r} field={f!r} "
                    f"baseline={bv!r} candidate={cv!r}"
                )
                report.details.append(detail)
                report.unexpected_diffs += 1

                # Additional classification: is this a terminal-boundary override?
                from pipeline.governance.terminal_boundary_guard import (
                    _TERMINAL_VERDICTS,
                )
                if bv in _TERMINAL_VERDICTS and cv not in _TERMINAL_VERDICTS:
                    report.terminal_boundary_overrides += 1
                    report.closed_contract_regressions += 1
                    report.details.append(
                        f"TERMINAL_BOUNDARY_OVERRIDE: {surface!r} {f!r} "
                        f"{bv!r}→{cv!r}"
                    )

        if not report.closed:
            raise DiffRejected(report)

        return report

    @staticmethod
    def snapshot(surfaces: list[str]) -> dict[str, dict]:
        """
        Run hokom() on each surface and collect a semantic snapshot dict.
        Filters to semantic fields only.
        """
        from hokom_pipeline import hokom
        snap: dict[str, dict] = {}
        for surface in surfaces:
            try:
                r = hokom(surface)
            except Exception as exc:
                r = {'_error': str(exc)}
            snap[surface] = {f: r.get(f) for f in _SEMANTIC_FIELDS}
        return snap
