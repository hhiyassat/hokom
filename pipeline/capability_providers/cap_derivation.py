"""
cap_derivation.py — Derivation state and reference form capability providers.

CAP_DERIVATION_STATE: JAMID or MUSHTAQ (derived)
CAP_REFERENCE_FORM: the citation form (masdar, root+pattern, base form)

CONSTITUTIONAL CONSTRAINTS:
    - No root→meaning inference
    - No wazn→meaning inference
    - Reference form is FORMAL IDENTITY only, not semantic interpretation
"""
from __future__ import annotations
from .models import CapabilityResult, CapabilityStatus

SOURCE_MODULE = "pipeline.capability_providers.cap_derivation"

def CAP_DERIVATION_STATE(hokom_result: dict) -> CapabilityResult:
    """Extract derivation state (JAMID/MUSHTAQ)."""
    wc = hokom_result.get("word_class", {})
    morph = hokom_result.get("morphosyntax") or hokom_result.get("morphology") or {}
    ra = hokom_result.get("root_analysis") or {}

    # Direct field
    derivation = morph.get("derivation") or wc.get("derivation")

    if not derivation:
        # Infer from jamid_mushtaq if present
        jamid_mushtaq = ra.get("jamid_mushtaq") or ra.get("classification")
        if jamid_mushtaq:
            derivation = str(jamid_mushtaq).upper()

    if not derivation:
        return CapabilityResult(
            capability_id="CAP_DERIVATION_STATE",
            status=CapabilityStatus.DEFERRED,
            value=None, value_ar=None, value_en=None,
            evidence_ids=(), residuals=("DERIVATION_STATE_UNDETERMINED",),
            source_module=SOURCE_MODULE,
        )

    derivation = str(derivation).upper().strip()
    if derivation in ("JAMID", "JAMID_AALAM", "FROZEN", "NON_DERIVED"):
        ar, en = "جامد", "JAMID"
    elif derivation in ("MUSHTAQ", "DERIVED", "MUSYTAQ"):
        ar, en = "مشتق", "MUSHTAQ"
    else:
        ar, en = derivation, derivation

    return CapabilityResult(
        capability_id="CAP_DERIVATION_STATE",
        status=CapabilityStatus.PROVIDED,
        value=derivation,
        value_ar=ar,
        value_en=en,
        evidence_ids=(f"root_analysis.jamid_mushtaq:{derivation}",),
        residuals=(),
        source_module=SOURCE_MODULE,
    )

def CAP_REFERENCE_FORM(hokom_result: dict) -> CapabilityResult:
    """
    Extract citation/reference form. This is FORMAL IDENTITY, not meaning.
    For verbs: masdar or root+pattern
    For nouns: base (mufrad, mudhakkar, mutlaq) form
    """
    ra = hokom_result.get("root_analysis") or {}
    morph = hokom_result.get("morphosyntax") or {}

    canonical_root = ra.get("canonical_root") or ra.get("root")
    wazn = ra.get("wazn") or ra.get("pattern")
    masdar = ra.get("masdar") or morph.get("masdar")

    if masdar:
        return CapabilityResult(
            capability_id="CAP_REFERENCE_FORM",
            status=CapabilityStatus.PROVIDED,
            value=masdar,
            value_ar=masdar,
            value_en=f"masdar:{masdar}",
            evidence_ids=(f"root_analysis.masdar:{masdar}",),
            residuals=(),
            source_module=SOURCE_MODULE,
        )

    if canonical_root and wazn:
        ref_form = f"{canonical_root} ({wazn})"
        return CapabilityResult(
            capability_id="CAP_REFERENCE_FORM",
            status=CapabilityStatus.PROVIDED,
            value=ref_form,
            value_ar=ref_form,
            value_en=f"root:{canonical_root} pattern:{wazn}",
            evidence_ids=(f"root_analysis.root:{canonical_root}", f"root_analysis.wazn:{wazn}"),
            residuals=(),
            source_module=SOURCE_MODULE,
        )

    if canonical_root:
        return CapabilityResult(
            capability_id="CAP_REFERENCE_FORM",
            status=CapabilityStatus.AMBIGUOUS,
            value=canonical_root,
            value_ar=canonical_root,
            value_en=f"root:{canonical_root}",
            evidence_ids=(f"root_analysis.root:{canonical_root}",),
            residuals=("WAZN_MISSING_REFERENCE_FORM_INCOMPLETE",),
            source_module=SOURCE_MODULE,
        )

    return CapabilityResult(
        capability_id="CAP_REFERENCE_FORM",
        status=CapabilityStatus.DEFERRED,
        value=None, value_ar=None, value_en=None,
        evidence_ids=(), residuals=("NO_ROOT_OR_MASDAR_FOR_REFERENCE_FORM",),
        source_module=SOURCE_MODULE,
    )
