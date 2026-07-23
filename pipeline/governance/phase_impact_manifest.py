#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/phase_impact_manifest.py

HOKOM-CLOSED-CONTRACT-SEMANTIC-REGRESSION-FIREWALL-01

Machine-readable impact manifest for every implementation phase.

Every phase must produce a PhaseImpactManifest before commit.
Closure requires:
  unexpected_changes = 0
  closed_contract_regressions = 0
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class PhaseImpactManifest:
    """
    Machine-readable record of a phase's semantic impact.

    Populate from SemanticDiffGate.compare() output and your phase
    declaration, then call assert_closed() before committing.
    """
    phase_id:                    str
    baseline_head:               str
    candidate_head:              str
    intended_tokens:             List[str]
    intended_fields:             List[str]
    actual_changed_tokens:       List[str]
    actual_changed_fields:       List[str]
    unexpected_changes:          int
    closed_contract_regressions: int

    def assert_closed(self) -> None:
        """
        Raise AssertionError if this manifest is not closed.

        Closure conditions:
          unexpected_changes = 0
          closed_contract_regressions = 0
        """
        if self.unexpected_changes != 0:
            raise AssertionError(
                f"PhaseImpactManifest[{self.phase_id}] NOT CLOSED: "
                f"unexpected_changes={self.unexpected_changes} "
                f"(must be 0)"
            )
        if self.closed_contract_regressions != 0:
            raise AssertionError(
                f"PhaseImpactManifest[{self.phase_id}] NOT CLOSED: "
                f"closed_contract_regressions={self.closed_contract_regressions} "
                f"(must be 0)"
            )

    @property
    def unexpected_tokens(self) -> List[str]:
        """Tokens that changed but were not declared as intended."""
        return [t for t in self.actual_changed_tokens
                if t not in self.intended_tokens]

    @property
    def unexpected_field_list(self) -> List[str]:
        """Fields that changed but were not declared as intended."""
        return [f for f in self.actual_changed_fields
                if f not in self.intended_fields]

    def to_json(self) -> str:
        """Serialize to JSON for storage in reports/."""
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_diff_gate_result(
        cls,
        phase_id: str,
        baseline_head: str,
        candidate_head: str,
        intended_tokens: list[str],
        intended_fields: list[str],
        diff_report,    # DiffReport from SemanticDiffGate.compare()
    ) -> 'PhaseImpactManifest':
        """
        Build a manifest from a SemanticDiffGate DiffReport.
        """
        from pipeline.governance.semantic_diff_gate import DiffReport
        changed_tokens: list[str] = []
        changed_fields: list[str] = []
        for detail in (diff_report.details if diff_report else []):
            # Parse "UNEXPECTED: surface=... field=..."
            if 'surface=' in detail and 'field=' in detail:
                parts = dict(
                    p.split('=', 1)
                    for p in detail.replace('UNEXPECTED: ', '').split(' ')
                    if '=' in p
                )
                tok = parts.get('surface', '').strip("'\"")
                fld = parts.get('field', '').strip("'\"")
                if tok:
                    changed_tokens.append(tok)
                if fld:
                    changed_fields.append(fld)

        return cls(
            phase_id=phase_id,
            baseline_head=baseline_head,
            candidate_head=candidate_head,
            intended_tokens=intended_tokens,
            intended_fields=intended_fields,
            actual_changed_tokens=list(dict.fromkeys(changed_tokens)),
            actual_changed_fields=list(dict.fromkeys(changed_fields)),
            unexpected_changes=diff_report.unexpected_diffs if diff_report else 0,
            closed_contract_regressions=(
                diff_report.closed_contract_regressions if diff_report else 0
            ),
        )
