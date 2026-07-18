"""
Provider Guard -- validates that a LinguisticClaimProvider meets the admission contract.
Provider admission != claim approval.
"""
from __future__ import annotations
from .provider_models import HokomLinguisticClaimBundle, ProviderAdmissionResult
from .provider_protocol import LinguisticClaimProvider


REQUIRED_PROVIDER_FIELDS = [
    'provider_id', 'engine_version', 'callable_surface', 'output_schema'
]

FORBIDDEN_OUTPUT_FIELDS = [
    'taaqol_rank', 'constitutional_rank', 'successor', 'ledger_entry',
    'native_verdict', 'licensed', 'certified', 'proven',
]


def admit_provider(provider: object) -> ProviderAdmissionResult:
    """
    Evaluate a provider against the LinguisticClaimProvider contract.
    Returns ProviderAdmissionResult -- NOT a claim approval.
    """
    violations = []

    # Check required fields
    for field in REQUIRED_PROVIDER_FIELDS:
        if not hasattr(provider, field):
            violations.append(f'missing required field: {field}')
        elif not getattr(provider, field):
            violations.append(f'empty required field: {field}')

    # Check analyze_token callable
    if not callable(getattr(provider, 'analyze_token', None)):
        violations.append('analyze_token must be callable')

    # Check it implements the protocol
    if not isinstance(provider, LinguisticClaimProvider):
        violations.append('does not implement LinguisticClaimProvider protocol')

    admitted = len(violations) == 0

    return ProviderAdmissionResult(
        provider_id=getattr(provider, 'provider_id', 'UNKNOWN'),
        admitted=admitted,
        violations=tuple(violations),
        note='Provider admission is not claim approval.',
        IS_CLAIM_APPROVAL=False,
    )


def validate_bundle(bundle: object) -> list:
    """
    Validate that a provider output is a properly typed HokomLinguisticClaimBundle.
    Returns list of violations (empty = valid).
    """
    violations = []

    if not isinstance(bundle, HokomLinguisticClaimBundle):
        violations.append('output must be HokomLinguisticClaimBundle, not raw dict or other type')
        return violations

    if not bundle.claim_id:
        violations.append('claim_id must not be empty')
    if not bundle.token_id:
        violations.append('token_id must not be empty')
    if not bundle.original_surface:
        violations.append('original_surface must not be empty')
    if not bundle.engine_version:
        violations.append('engine_version must not be empty')
    if bundle.domain_directive not in {'ACCEPT', 'DEFER', 'BLOCK', 'NOT_APPLICABLE'}:
        violations.append(f'invalid domain_directive: {bundle.domain_directive!r}')

    # Check no hidden residuals (active & resolved = empty)
    active_set = set(bundle.active_residuals)
    resolved_set = set(bundle.resolved_residuals)
    overlap = active_set & resolved_set
    if overlap:
        violations.append(f'residual appears in both active and resolved: {overlap}')

    return violations
