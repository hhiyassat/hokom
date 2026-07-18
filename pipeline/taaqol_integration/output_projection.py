"""
Display projection for Hokom-Taaqol constitutional output.
"""
from __future__ import annotations
from .provider_models import HokomLinguisticClaimBundle, HokomTaaqolAdmissionResult, TaaqolVerticalContinuationResult


def format_constitutional_display(
    bundle: HokomLinguisticClaimBundle,
    admission: HokomTaaqolAdmissionResult,
    continuation: TaaqolVerticalContinuationResult | None,
) -> str:
    lines = []

    # Hokom Domain Claim
    lines.append('[Hokom Domain Claim]')
    lines.append(f'  surface        : {bundle.original_surface}')
    root = bundle.root_claim
    root_str = str(getattr(root, 'canonical_root', '?')) if root else '--'
    lines.append(f'  root           : {root_str}')
    wazn = bundle.wazn_claim
    wazn_str = str(getattr(wazn, 'final_wazn', '?')) if wazn else '--'
    lines.append(f'  wazn           : {wazn_str}')
    form = bundle.form_claim
    form_str = str(getattr(form, 'final_bab', '?')) if form else '--'
    lines.append(f'  form           : {form_str}')
    masdar = bundle.masdar_claim
    masdar_str = str(getattr(masdar, 'final_masdar_pattern', '?')) if masdar else '--'
    lines.append(f'  masdar         : {masdar_str}')
    infl = bundle.inflection_claim
    infl_str = str(getattr(infl, 'final_directive', '?')) if infl else '--'
    lines.append(f'  inflection     : {infl_str}')
    lines.append(f'  domain dir     : {bundle.domain_directive}')
    lines.append(f'  active res     : {", ".join(bundle.active_residuals) or "none"}')
    lines.append('')

    # Provider Admission
    lines.append('[Taaqol Provider Admission]')
    lines.append(f'  provider       : {admission.provider_admission.provider_id}')
    lines.append(f'  admitted       : {admission.provider_admission.admitted}')
    lines.append('')

    # Claim Admission
    lines.append('[Taaqol Claim Admission]')
    lines.append(f'  verdict        : {admission.verdict}')
    lines.append(f'  identity       : {admission.identity_continuity}')
    lines.append(f'  evidence       : {admission.evidence_verdict}')
    lines.append(f'  residual policy: {admission.residual_verdict}')
    lines.append(f'  gate           : {admission.gate_verdict}')
    lines.append(f'  native entry   : {admission.native_entry_stage or "--"}')
    lines.append(f'  stop reason    : {admission.stop_reason or "none"}')
    lines.append('')

    # Vertical Continuation
    if continuation:
        lines.append('[Taaqol Vertical Continuation]')
        lines.append(f'  native entry   : {continuation.admission.native_entry_stage or "--"}')
        completed = ', '.join(s for s, _ in continuation.native_stage_results) or '--'
        lines.append(f'  completed stages: {completed}')
        lines.append(f'  highest stage  : {continuation.highest_completed_stage or "--"}')
        lines.append(f'  stop stage     : {continuation.stop_stage or "--"}')
        lines.append(f'  stop reason    : {continuation.stop_reason or "none"}')
        lines.append('')

    # Audited Output
    lines.append('[Audited Output]')
    audited = getattr(continuation, 'audited_output', None) if continuation else None
    if audited:
        lines.append(f'  output: {audited}')
    else:
        lines.append('  not yet available -- lawful output requires completed vertical stages')

    return '\n'.join(lines)
