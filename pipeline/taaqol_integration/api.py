"""
Public Hokom-Taaqol integration API.
Three entry points: analyze, admit, continue.
"""
from __future__ import annotations
import sys
import os

# Vendor path: add to sys.path for when taaqqul_slot_geometry becomes importable
_VENDOR_SRC = os.path.join(os.path.dirname(__file__), '..', '..', 'vendor', 'Taaqol-GPT', 'src')
if _VENDOR_SRC not in sys.path:
    sys.path.insert(0, _VENDOR_SRC)

from .provider_models import (
    HokomLinguisticClaimBundle,
    HokomTaaqolAdmissionResult,
    TaaqolVerticalContinuationResult,
    HokomTaaqolResult,
)
from .claim_adapter import bundle_from_hokom_result
from .provider_guard import admit_provider, validate_bundle
from .admission_gate import admit_claim
from .native_continuation import continue_vertical
from .shadow_mode import run_shadow_comparison
from .output_projection import format_constitutional_display


class HokomProvider:
    """
    Hokom as a LinguisticClaimProvider.
    This is NOT a ModelClient. This is NOT a concrete LLM adapter.
    """
    provider_id = 'HOKOM_MORPHOLOGY_ENGINE'
    engine_version = '2026.07.18'
    callable_surface = 'single Arabic token (diacritized or undiacritized)'
    output_schema = 'HokomLinguisticClaimBundle'

    def analyze_token(self, surface: str) -> HokomLinguisticClaimBundle:
        # Import hokom at call time (not at module level) to avoid circular imports
        from hokom_pipeline import hokom
        result = hokom(surface)
        return bundle_from_hokom_result(result)


_DEFAULT_PROVIDER = HokomProvider()


def analyze_token_constitutionally(
    surface: str,
    *,
    mode: str = 'shadow',
) -> HokomTaaqolResult:
    """
    Full constitutional analysis: Hokom claim -> Taaqol admission -> vertical continuation.

    mode: 'shadow' (Hokom output preserved, Taaqol runs alongside)
          'strict'  (requires all prerequisites; raises if not ready)
    """
    if mode not in ('shadow', 'strict'):
        raise ValueError(f"mode must be 'shadow' or 'strict', got {mode!r}")

    # 1. Provider admission
    provider_admission = admit_provider(_DEFAULT_PROVIDER)

    # 2. Get Hokom claim bundle
    from hokom_pipeline import hokom
    hokom_result = hokom(surface)
    bundle = bundle_from_hokom_result(hokom_result)

    # 3. Claim admission
    admission = admit_claim(bundle, provider_admission)

    # 4. Vertical continuation (only if admitted)
    continuation = None
    if admission.verdict == 'APPROVED':
        continuation = continue_vertical(admission)

    # 5. Shadow comparison
    shadow_comparison = None
    if mode == 'shadow':
        shadow_comparison = run_shadow_comparison(hokom_result, admission)

    # 6. Strict mode check
    if mode == 'strict':
        from .strict_mode import strict_mode_ready
        ready, missing = strict_mode_ready()
        if not ready:
            raise RuntimeError(f'STRICT mode prerequisites not met: {missing}')

    return HokomTaaqolResult(
        surface=surface,
        mode=mode,
        hokom_claim_bundle=bundle,
        admission=admission,
        continuation=continuation,
        shadow_comparison=shadow_comparison,
    )


def admit_hokom_claim(bundle: HokomLinguisticClaimBundle) -> HokomTaaqolAdmissionResult:
    """Admit a pre-built HokomLinguisticClaimBundle."""
    provider_admission = admit_provider(_DEFAULT_PROVIDER)
    return admit_claim(bundle, provider_admission)


def continue_taaqol_vertical(
    admission: HokomTaaqolAdmissionResult,
) -> TaaqolVerticalContinuationResult:
    """Continue the Taaqol vertical pipeline after successful admission."""
    return continue_vertical(admission)
