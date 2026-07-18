"""
Strict mode: Hokom domain claim may only be displayed as DOMAIN_CLAIM.
Unlicensed successors are blocked.

Three separate tracking states:
  IMPLEMENTATION: Is the strict mode code present? (CLOSED after this batch)
  READINESS: Are the 5 prerequisites met? (see STRICT_MODE_PREREQUISITES)
  ACTIVATION: Is strict mode currently active? (no -- readiness not met)
"""
from __future__ import annotations

import sys

from .provider_models import HokomTaaqolAdmissionResult

# ---------------------------------------------------------------------------
# STRICT MODE IMPLEMENTATION: CLOSED
# The implementation exists. The code below handles strict mode enforcement.
STRICT_MODE_IMPLEMENTATION_STATUS = 'CLOSED'
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# STRICT MODE PREREQUISITES
# All 5 must be True before strict mode can activate.
# ---------------------------------------------------------------------------
STRICT_MODE_PREREQUISITES = {
    # 1. Upstream Taaqol tests: 2824 passed, 19 failed (upstream baseline failures)
    'upstream_taaqol_tests_pass': False,       # 19 upstream failures (missing docs/source files in repo)
    # 2. Protected Hokom tests: baseline 2895 passed, 153 failed -- must not regress
    'protected_hokom_tests_unchanged': False,  # regression check pending full R29 run
    # 3. Shadow corpus stable: all 19 reference tokens shadowed without crash
    'shadow_corpus_stable': True,              # R19 corpus runs without errors
    # 4. No hidden residual: active ∩ resolved = empty (verified in R14)
    'no_hidden_residual': True,                # R14/R15 verified -- OK
    # 5. All public outputs auditable: AnswerAudit wired to output
    'all_public_outputs_auditable': False,     # AnswerAudit requires ModelClient -- DEFERRED
}


def strict_mode_ready() -> tuple[bool, list[str]]:
    """
    Check if strict mode prerequisites are met.
    Returns (ready: bool, missing_prerequisites: list[str]).

    STRICT MODE READINESS: NOT READY
    Blocking prerequisites:
      - upstream_taaqol_tests_pass: 19 upstream failures in repo (missing source files)
      - protected_hokom_tests_unchanged: regression check not run
      - all_public_outputs_auditable: AnswerAudit requires ModelClient
    """
    missing = [k for k, v in STRICT_MODE_PREREQUISITES.items() if not v]
    ready = len(missing) == 0
    return ready, missing


def strict_mode_prerequisites_detail() -> dict:
    """Return detailed status of each prerequisite."""
    return {
        'upstream_taaqol_tests_pass': {
            'met': STRICT_MODE_PREREQUISITES['upstream_taaqol_tests_pass'],
            'detail': 'R9 result: 2824 passed, 19 failed. Failures are upstream baseline (missing source files in repo: ifadah_candidate.py, registry docs/29, etc). Not introduced by migration.',
        },
        'protected_hokom_tests_unchanged': {
            'met': STRICT_MODE_PREREQUISITES['protected_hokom_tests_unchanged'],
            'detail': 'Baseline: 2895 passed, 153 failed (Python 3.10). Full regression pending R29.',
        },
        'shadow_corpus_stable': {
            'met': STRICT_MODE_PREREQUISITES['shadow_corpus_stable'],
            'detail': 'All 19 reference tokens shadowed in R19/R22 without crash.',
        },
        'no_hidden_residual': {
            'met': STRICT_MODE_PREREQUISITES['no_hidden_residual'],
            'detail': 'R14/R15 verified: active ∩ resolved = empty for all test tokens.',
        },
        'all_public_outputs_auditable': {
            'met': STRICT_MODE_PREREQUISITES['all_public_outputs_auditable'],
            'detail': 'AnswerAudit (taaqqul_slot_geometry.audit.answer_audit) requires ModelClient -- DEFERRED. Hokom is not a ModelClient.',
        },
    }


# STRICT MODE ACTIVATION: NOT ACTIVE
STRICT_MODE_ACTIVE = False


def apply_strict_output(
    raw_result: dict,
    admission: HokomTaaqolAdmissionResult,
) -> dict:
    """
    In strict mode: raw Hokom result shown only as DOMAIN_CLAIM.
    Rejected/deferred claims cannot masquerade as licensed outputs.
    Final output must expose residuals and stop reason.

    Raises RuntimeError if prerequisites not met.
    """
    ready, missing = strict_mode_ready()
    if not ready:
        raise RuntimeError(
            f'STRICT mode not ready -- missing prerequisites: {missing}. '
            f'Use mode="shadow" instead.'
        )

    if admission.verdict != 'APPROVED':
        return {
            'output_type': 'DOMAIN_CLAIM',
            'claim_id': admission.claim_id,
            'verdict': admission.verdict,
            'stop_reason': admission.stop_reason,
            'active_residuals': admission.active_residuals,
            'note': 'claim not licensed -- cannot display as certified output',
        }

    return {
        'output_type': 'LICENSED_DOMAIN_CLAIM',
        'claim_id': admission.claim_id,
        'verdict': admission.verdict,
        'constitutional_rank': str(admission.taaqol_rank) if admission.taaqol_rank else None,
        'active_residuals': admission.active_residuals,
        'resolved_residuals': admission.resolved_residuals,
        'stop_reason': admission.stop_reason,
        'python_version': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
    }
