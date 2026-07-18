"""
IdentityContinuity -- verifies that the surface identity chain is unbroken.
"""
from __future__ import annotations
from dataclasses import dataclass
from .provider_models import HokomLinguisticClaimBundle


@dataclass(frozen=True)
class IdentityContinuityResult:
    verdict: str            # ACCEPT | DEFER | BLOCK
    original_surface: str
    normalized_surface: str
    refined_host: str | None
    transformations: tuple
    missing_traces: tuple
    violations: tuple


def verify_identity_continuity(bundle: HokomLinguisticClaimBundle) -> IdentityContinuityResult:
    """
    Verify that original -> normalized -> refined_host -> root/wazn carrier is unbroken.
    """
    violations = []
    missing_traces = []
    transformations = []

    # Surface must be non-empty
    if not bundle.original_surface:
        violations.append('original_surface is empty')
    if not bundle.normalized_surface:
        violations.append('normalized_surface is empty')

    # Track transformations
    if bundle.original_surface != bundle.normalized_surface:
        transformations.append(f'normalization: {bundle.original_surface!r} -> {bundle.normalized_surface!r}')
        # Trace must exist for normalization
        if not any('normal' in t.lower() or 'norm' in t.lower() for t in bundle.trace_ids):
            missing_traces.append('normalization_trace')

    if bundle.refined_host and bundle.refined_host != bundle.normalized_surface:
        transformations.append(f'refinement: {bundle.normalized_surface!r} -> {bundle.refined_host!r}')
        if not any('host' in t.lower() or 'refin' in t.lower() for t in bundle.trace_ids):
            missing_traces.append('host_refinement_trace')

    # Root claim must relate to the surface for root-path tokens.
    # Exception: function words (particles, pronouns, prepositions) take the
    # mabniyat path -- they have root_claim=None AND wazn_claim=None by design.
    # If both root_claim and wazn_claim are None with ACCEPT, this is a function-
    # word token (mabniyat path), not a root-analysis failure.
    if bundle.root_claim is None and bundle.domain_directive == 'ACCEPT':
        is_function_word_path = (
            bundle.wazn_claim is None and
            bundle.form_claim is None and
            not bundle.mushtaq_claims
        )
        if not is_function_word_path:
            violations.append('domain_directive=ACCEPT but root_claim is None')

    # Determine verdict
    if violations:
        verdict = 'BLOCK'
    elif missing_traces:
        verdict = 'DEFER'
    else:
        verdict = 'ACCEPT'

    return IdentityContinuityResult(
        verdict=verdict,
        original_surface=bundle.original_surface,
        normalized_surface=bundle.normalized_surface,
        refined_host=bundle.refined_host,
        transformations=tuple(transformations),
        missing_traces=tuple(missing_traces),
        violations=tuple(violations),
    )
