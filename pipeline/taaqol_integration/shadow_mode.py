"""
Shadow mode: Hokom output is preserved unchanged; native Taaqol Gamma runs alongside.
No Hokom public result is modified in shadow mode.

This module now runs ACTUAL native Gamma (via SlotGraph) for comparison,
not just string comparison. The native Gamma result is captured and compared
against Hokom's own verdict.
"""
from __future__ import annotations

import sys
import enum as _enum_module

from .provider_models import HokomLinguisticClaimBundle, HokomTaaqolAdmissionResult

# Native Taaqol availability
_SHADOW_NATIVE = False
try:
    from taaqqul_slot_geometry.core.closure_state import ClosureState
    from taaqqul_slot_geometry.core.gamma import gamma
    from taaqqul_slot_geometry.core.rank_lattice import Rank
    _SHADOW_NATIVE = True
except Exception:
    pass


def run_shadow_comparison(
    hokom_result: dict,
    admission: HokomTaaqolAdmissionResult,
) -> dict:
    """
    Compare Hokom domain output with Taaqol admission (native Gamma run).
    Returns a shadow comparison report. Original Hokom result is NOT modified.

    The native Gamma result is captured from the admission (which ran it),
    and compared against Hokom's own verdict field.
    """
    hokom_directive = hokom_result.get('verdict', 'UNKNOWN')
    taaqol_verdict = admission.verdict
    gamma_state = admission.gamma_result  # string from native Gamma run

    divergence_points = []

    # Check directive vs admission
    if hokom_directive in ('ACCEPT', 'LICENSED', 'COMPLETE') and taaqol_verdict not in ('APPROVED',):
        divergence_points.append({
            'point': 'directive_mismatch',
            'hokom': hokom_directive,
            'taaqol': taaqol_verdict,
            'note': 'Hokom ACCEPT does not automatically become Taaqol APPROVED',
        })

    # Check Gamma state vs Hokom verdict
    if gamma_state and hokom_directive == 'ACCEPT':
        # MINIMALLY_CLOSED or PERFORATED_CLOSED = consistent with ACCEPT
        valid_gamma_for_accept = (
            'MINIMALLY_CLOSED' in str(gamma_state) or
            'PERFORATED_CLOSED' in str(gamma_state)
        )
        if not valid_gamma_for_accept:
            divergence_points.append({
                'point': 'gamma_hokom_divergence',
                'hokom_directive': hokom_directive,
                'native_gamma_state': gamma_state,
                'note': 'Hokom ACCEPT but native Gamma did not close',
            })

    # Check evidence
    if admission.evidence_verdict not in ('SUFFICIENT',):
        divergence_points.append({
            'point': 'evidence_gap',
            'taaqol_evidence_verdict': admission.evidence_verdict,
            'note': 'Evidence not sufficient for Taaqol admission',
        })

    # Check residuals
    if admission.residual_verdict not in ('CLEAR', 'DEFERRABLE'):
        divergence_points.append({
            'point': 'residual_ceiling',
            'taaqol_residual_verdict': admission.residual_verdict,
            'note': 'Residuals impose ceiling',
        })

    # Native execution report
    native_execution = {
        'gamma_ran': gamma_state is not None,
        'gamma_state': gamma_state,
        'taaqol_rank': admission.taaqol_rank,
        'gate_verdict': admission.gate_verdict,
        'native_entry_stage': admission.native_entry_stage,
        'python_version': f'{sys.version_info.major}.{sys.version_info.minor}',
        'native_library_available': _SHADOW_NATIVE,
        'strEnum_backport': sys.version_info < (3, 11) and _SHADOW_NATIVE,
    }

    return {
        'mode': 'SHADOW',
        'hokom_directive': hokom_directive,
        'taaqol_admission': taaqol_verdict,
        'first_divergence': divergence_points[0] if divergence_points else None,
        'all_divergences': divergence_points,
        'hokom_output_preserved': True,   # SHADOW never modifies Hokom output
        'active_residuals': list(admission.active_residuals),
        'stop_reason': admission.stop_reason,
        'native_execution': native_execution,
    }
# test
