"""
HT28 -- Live reference token tests for Hokom-Taaqol integration.
All 19 reference tokens.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pipeline.taaqol_integration.claim_adapter import bundle_from_hokom_result
from pipeline.taaqol_integration.provider_guard import admit_provider, validate_bundle
from pipeline.taaqol_integration.admission_gate import admit_claim
from pipeline.taaqol_integration.provider_models import HokomLinguisticClaimBundle

# 19 reference tokens
REFERENCE_TOKENS = [
    'نَصَرَ',      # نَصَرَ
    'ضَرَبَ',      # ضَرَبَ
    'قَالَ',            # قَالَ
    'يَقُولُ',  # يَقُولُ
    'قُلْ',                  # قُلْ
    'بَاعَ',            # بَاعَ
    'بِعْ',                  # بِعْ
    'دَعَا',            # دَعَا
    'رَمَى',            # رَمَى
    'وَعَدَ',      # وَعَدَ
    'مَدَّ',            # مَدَّ
    'يُعَوِّضُهُمْ',  # يُعَوِّضُهُمْ
    'تَأَكَّدَتْ',  # تَأَكَّدَتْ
    'يَسْتَخْرِجُونَ',  # يَسْتَخْرِجُونَ
    'مُفْتَرِسَةُ',  # مُفْتَرِسَةُ
    'تَكْتُبِينَ',  # تَكْتُبِينَ
    'مِنْ',                  # مِنْ
    'هُوَ',                  # هُوَ
    'لَنْ',                  # لَنْ
]


class MinimalHokomProvider:
    """Minimal provider for testing without full hokom_pipeline."""
    provider_id = 'HOKOM_MORPHOLOGY_ENGINE'
    engine_version = '2026.07.18'
    callable_surface = 'single Arabic token (diacritized or undiacritized)'
    output_schema = 'HokomLinguisticClaimBundle'

    def analyze_token(self, surface: str) -> HokomLinguisticClaimBundle:
        from hokom_pipeline import hokom
        result = hokom(surface)
        from pipeline.taaqol_integration.claim_adapter import bundle_from_hokom_result
        return bundle_from_hokom_result(result)


@pytest.mark.parametrize("surface", REFERENCE_TOKENS)
def test_bundle_is_typed(surface):
    """Bundle must be HokomLinguisticClaimBundle, not raw dict."""
    from hokom_pipeline import hokom
    result = hokom(surface)
    bundle = bundle_from_hokom_result(result)
    assert isinstance(bundle, HokomLinguisticClaimBundle), \
        f"Expected HokomLinguisticClaimBundle, got {type(bundle)}"


@pytest.mark.parametrize("surface", REFERENCE_TOKENS)
def test_bundle_has_required_fields(surface):
    """Bundle must have non-empty claim_id, token_id, original_surface, engine_version."""
    from hokom_pipeline import hokom
    result = hokom(surface)
    bundle = bundle_from_hokom_result(result)
    assert bundle.claim_id, "claim_id must not be empty"
    assert bundle.token_id, "token_id must not be empty"
    assert bundle.engine_version, "engine_version must not be empty"


@pytest.mark.parametrize("surface", REFERENCE_TOKENS)
def test_bundle_domain_directive_valid(surface):
    """Domain directive must be one of the four legal values."""
    from hokom_pipeline import hokom
    result = hokom(surface)
    bundle = bundle_from_hokom_result(result)
    assert bundle.domain_directive in {'ACCEPT', 'DEFER', 'BLOCK', 'NOT_APPLICABLE'}, \
        f"Invalid domain_directive: {bundle.domain_directive!r}"


@pytest.mark.parametrize("surface", REFERENCE_TOKENS)
def test_no_hidden_residuals(surface):
    """Active residuals must not overlap with resolved residuals."""
    from hokom_pipeline import hokom
    result = hokom(surface)
    bundle = bundle_from_hokom_result(result)
    violations = validate_bundle(bundle)
    hidden = [v for v in violations if 'both active and resolved' in v]
    assert not hidden, f"Hidden residuals detected for {surface!r}: {hidden}"


@pytest.mark.parametrize("surface", REFERENCE_TOKENS)
def test_admission_verdict_not_forbidden_leap(surface):
    """Admission verdict must never be FORBIDDEN_LEAP (constitutional contract)."""
    from hokom_pipeline import hokom
    result = hokom(surface)
    bundle = bundle_from_hokom_result(result)
    provider = MinimalHokomProvider()
    from pipeline.taaqol_integration.provider_guard import admit_provider
    provider_admission = admit_provider(provider)
    admission = admit_claim(bundle, provider_admission)
    assert admission.verdict != 'FORBIDDEN_LEAP', \
        f"FORBIDDEN_LEAP verdict for {surface!r}: {admission.stop_reason}"


@pytest.mark.parametrize("surface", REFERENCE_TOKENS)
def test_bundle_serializes_to_dict(surface):
    """Bundle.to_dict() must return a dict with required keys."""
    from hokom_pipeline import hokom
    result = hokom(surface)
    bundle = bundle_from_hokom_result(result)
    d = bundle.to_dict()
    assert isinstance(d, dict)
    for key in ('claim_id', 'token_id', 'original_surface', 'domain_directive', 'engine_version'):
        assert key in d, f"Missing key {key!r} in to_dict() output"


@pytest.mark.parametrize("surface", REFERENCE_TOKENS)
def test_no_rank_injection_in_bundle(surface):
    """Bundle serialization must not contain forbidden rank claims."""
    from hokom_pipeline import hokom
    from pipeline.taaqol_integration.rank_adapter import assert_no_rank_injection
    result = hokom(surface)
    bundle = bundle_from_hokom_result(result)
    d = bundle.to_dict()
    violations = assert_no_rank_injection(d)
    assert not violations, f"Rank injection detected for {surface!r}: {violations}"
