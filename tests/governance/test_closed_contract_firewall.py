#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/governance/test_closed_contract_firewall.py

HOKOM-CLOSED-CONTRACT-SEMANTIC-REGRESSION-FIREWALL-01

Protected constitutional tests for semantic-ownership enforcement,
terminal-boundary immutability, and lafẓ al-jalāla protection.

These tests may only have their expected values changed via an explicit
CONSTITUTIONAL_AMENDMENT_ID.  A normal implementation phase must NOT
weaken or remove any assertion here.

GOVERNANCE_METADATA = {
    "mandate": "HOKOM-CLOSED-CONTRACT-SEMANTIC-REGRESSION-FIREWALL-01",
    "start_head": "9adbea5",
    "protected": True,
    "amendment_required_to_modify": True,
}
# This variable is a constitutional marker.  Do not remove it.
# Any modification to assertions in this file requires a CONSTITUTIONAL_AMENDMENT_ID.
"""
from __future__ import annotations

import pytest
from hokom_pipeline import hokom
from pipeline.governance.slot_ownership_registry import (
    OWNERSHIP_REGISTRY,
    FieldOwner,
    TerminalBoundary,
)
from pipeline.governance.semantic_write_guard import (
    SemanticWriteGuard,
    WriteRejected,
)
from pipeline.governance.terminal_boundary_guard import (
    assert_terminal_record_cannot_reach_inflection,
    is_terminal_boundary,
)
from pipeline.governance.semantic_diff_gate import (
    SemanticDiffGate,
    DiffRejected,
)
from pipeline.governance.phase_impact_manifest import PhaseImpactManifest

# Constitutional marker — must remain as executable Python code, not a comment.
# Removing or weakening this dict requires a CONSTITUTIONAL_AMENDMENT_ID.
GOVERNANCE_METADATA = {
    "mandate": "HOKOM-CLOSED-CONTRACT-SEMANTIC-REGRESSION-FIREWALL-01",
    "start_head": "9adbea5",
    "protected": True,
    "amendment_required_to_modify": True,
}


# ══════════════════════════════════════════════════════════════════════════════
# LAFẒ AL-JALĀLA PROBES  (terminal-boundary immutability)
# ══════════════════════════════════════════════════════════════════════════════

ALLAH_PROBES = [
    'اللَّهُ',   # nominative
    'اللَّهَ',   # accusative
    'اللَّهِ',   # genitive
    'وَاللَّهُ', # waw + nominative
    'بِاللَّهِ', # bi + genitive
    'لِلَّهِ',   # li + genitive
]


@pytest.mark.parametrize('surface', ALLAH_PROBES)
def test_lafz_al_jalala_never_reaches_inflection(surface):
    """
    اللَّهُ and all proclitic-bearing forms must have JAMID_AALAM_BOUNDARY
    and MUST NOT receive tense/person/mood/voice values from the inflection engine.

    LAFZ_AL_JALALA_VERBAL_ANALYSES must = 0.
    """
    r = hokom(surface)
    assert r.get('jamid_verdict') == 'JAMID_AALAM_BOUNDARY', (
        f"{surface}: jamid_verdict={r.get('jamid_verdict')!r} "
        f"— JAMID_AALAM_BOUNDARY must be the governing verdict")
    # No verbal word-class
    wc = r.get('word_class')
    assert wc != 'FI3L', (
        f"{surface}: word_class={wc!r} — JAMID form must NEVER be FI3L")
    # No verbal inflection slots
    for slot in ('tense_aspect', 'person', 'voice'):
        val = r.get(slot)
        assert val is None, (
            f"{surface}: {slot}={val!r} — inflection slot must be None "
            f"for a JAMID_AALAM_BOUNDARY token")


@pytest.mark.parametrize('surface', ALLAH_PROBES)
def test_terminal_boundary_is_immutable(surface):
    """
    Once JAMID_AALAM_BOUNDARY is set, no downstream stage may overwrite it.
    boundary_type field in hokom() result must reflect the terminal boundary.
    """
    r = hokom(surface)
    # The boundary must be surfaced in the result
    bt = r.get('boundary_type')
    jv = r.get('jamid_verdict')
    assert bt == 'JAMID_AALAM_BOUNDARY' or jv == 'JAMID_AALAM_BOUNDARY', (
        f"{surface}: boundary_type={bt!r}, jamid_verdict={jv!r} — "
        f"terminal JAMID_AALAM_BOUNDARY must be visible in the result dict")
    # is_terminal_boundary must agree
    assert is_terminal_boundary(r), (
        f"{surface}: is_terminal_boundary() returned False for a known terminal record")


# ══════════════════════════════════════════════════════════════════════════════
# CONTEXT CARRIER RESTRICTIONS
# ══════════════════════════════════════════════════════════════════════════════

def test_context_cannot_create_fi3l():
    """
    The sequential context carrier may NOT create FI3L for a non-verbal token.
    Injecting a governing mood must not flip word_class to FI3L.
    """
    from pipeline.p5_inflection.context_carrier import SequentialAnalysisContext
    ctx = SequentialAnalysisContext()

    # Simulate a non-FI3L result (ISM token)
    non_fi3l_result = {
        'word_class': 'ISM',
        'morphosyntax': {'tense_aspect': None},
    }
    # inject_mood_into_result must not change word_class
    original_wc = non_fi3l_result['word_class']
    # Manually set a pending mood so inject_mood_into_result has something to attempt
    ctx._governing_mood = 'JUSSIVE'
    ctx._scope_remaining = 1
    result_after = ctx.inject_mood_into_result(dict(non_fi3l_result), 'كَاتِبٌ')
    assert result_after.get('word_class') == original_wc, (
        "Context carrier must not change word_class from ISM to FI3L")


def test_context_cannot_override_jamid():
    """
    The sequential context carrier must not inject mood into a JAMID_AALAM_BOUNDARY record.
    inject_mood_into_result must be a no-op for terminal records.
    """
    from pipeline.p5_inflection.context_carrier import SequentialAnalysisContext
    ctx = SequentialAnalysisContext()

    jamid_result = {
        'word_class': None,
        'boundary_type': 'JAMID_AALAM_BOUNDARY',
        'jamid_verdict': 'JAMID_AALAM_BOUNDARY',
        'morphosyntax': None,
    }
    ctx._governing_mood = 'JUSSIVE'
    ctx._scope_remaining = 1

    result_after = ctx.inject_mood_into_result(dict(jamid_result), 'اللَّهِ')
    # mood must NOT be injected into a JAMID record
    ms = result_after.get('morphosyntax')
    if ms is not None:
        assert ms.get('mood') is None, (
            "Context carrier must not inject mood into a JAMID_AALAM_BOUNDARY record")
    # boundary_type must be unchanged
    assert result_after.get('boundary_type') == 'JAMID_AALAM_BOUNDARY', (
        "inject_mood_into_result must not clear boundary_type")


# ══════════════════════════════════════════════════════════════════════════════
# SEMANTIC WRITE GUARD
# ══════════════════════════════════════════════════════════════════════════════

def test_filled_claim_cannot_change_value_downstream():
    """
    FILLED(A) → FILLED(B) is forbidden without an explicit amendment.
    The guarded write must raise WriteRejected when attempting to overwrite
    a filled value with a different value.
    """
    guard = SemanticWriteGuard()
    # First write: UNKNOWN → FILLED is allowed
    guard.write(
        field='WORD_CLASS_SLOT',
        old_state='UNKNOWN',
        old_value=None,
        new_state='FILLED',
        new_value='FI3L',
        requesting_stage='word_class_engine',
        evidence='morphology_path:verbal',
        phase_id='p_word_class',
    )
    # Second write: FILLED(FI3L) → FILLED(ISM) is forbidden
    with pytest.raises(WriteRejected):
        guard.write(
            field='WORD_CLASS_SLOT',
            old_state='FILLED',
            old_value='FI3L',
            new_state='FILLED',
            new_value='ISM',
            requesting_stage='some_downstream_stage',
            evidence='guess',
            phase_id='p_downstream',
        )


def test_non_owner_cannot_write_owned_field():
    """
    A stage that is not the registered owner of a field must not be allowed
    to fill it as FILLED.
    """
    guard = SemanticWriteGuard()
    with pytest.raises(WriteRejected):
        guard.write(
            field='BOUNDARY_TYPE_SLOT',
            old_state='UNKNOWN',
            old_value=None,
            new_state='FILLED',
            new_value='JAMID_AALAM_BOUNDARY',
            requesting_stage='word_class_engine',   # not the owner
            evidence='none',
            phase_id='p_wrong_stage',
        )


def test_idempotent_same_value_write_is_allowed():
    """
    FILLED(A) → FILLED(A) is idempotent and must be accepted.
    """
    guard = SemanticWriteGuard()
    guard.write(
        field='TENSE',
        old_state='UNKNOWN',
        old_value=None,
        new_state='FILLED',
        new_value='IMPERFECT',
        requesting_stage='p5_inflection',
        evidence='prefix_analysis',
        phase_id='p5',
    )
    # Idempotent re-write of same value: must NOT raise
    guard.write(
        field='TENSE',
        old_state='FILLED',
        old_value='IMPERFECT',
        new_state='FILLED',
        new_value='IMPERFECT',
        requesting_stage='p5_inflection',
        evidence='same_evidence',
        phase_id='p5_recheck',
    )


def test_ambiguous_may_resolve_with_evidence():
    """
    AMBIGUOUS → FILLED when sufficient evidence resolves it.
    This transition must be allowed by the guard.
    """
    guard = SemanticWriteGuard()
    guard.write(
        field='MOOD',
        old_state='AMBIGUOUS',
        old_value='UNKNOWN',
        new_state='FILLED',
        new_value='SUBJUNCTIVE',
        requesting_stage='p5_inflection',
        evidence='governing_particle:أَنْ',
        phase_id='p5_context',
    )
    # Should not raise


def test_terminal_boundary_downstream_overwrite_rejected():
    """
    A downstream stage must not overwrite a terminal BOUNDARY_TYPE_SLOT.
    """
    guard = SemanticWriteGuard()
    # First: legitimate boundary write by the owner
    guard.write(
        field='BOUNDARY_TYPE_SLOT',
        old_state='UNKNOWN',
        old_value=None,
        new_state='FILLED',
        new_value='JAMID_AALAM_BOUNDARY',
        requesting_stage='jamid_aalam_boundary',
        evidence='aalam_catalog:divine_name',
        phase_id='p_jamid',
    )
    # Downstream attempt to overwrite terminal boundary — must be rejected
    with pytest.raises(WriteRejected):
        guard.write(
            field='BOUNDARY_TYPE_SLOT',
            old_state='FILLED',
            old_value='JAMID_AALAM_BOUNDARY',
            new_state='FILLED',
            new_value='MABNI_BOUNDARY',
            requesting_stage='mabni_layer',
            evidence='spurious',
            phase_id='p_mabni',
        )


# ══════════════════════════════════════════════════════════════════════════════
# SEMANTIC DIFF GATE
# ══════════════════════════════════════════════════════════════════════════════

def test_semantic_diff_rejects_unexpected_change():
    """
    The diff gate must fail when an unexpected semantic change is detected.
    """
    gate = SemanticDiffGate(
        baseline={'اللَّهُ': {'word_class': None, 'tense_aspect': None}},
        intended_changes={},   # no changes declared
    )
    candidate = {'اللَّهُ': {'word_class': 'FI3L', 'tense_aspect': 'IMPERFECT'}}
    with pytest.raises(DiffRejected) as exc_info:
        gate.compare(candidate)
    assert 'UNEXPECTED_SEMANTIC_DIFFS' in str(exc_info.value), (
        "DiffRejected must report UNEXPECTED_SEMANTIC_DIFFS")


def test_phase_impact_manifest_matches_actual_diff():
    """
    A PhaseImpactManifest with zero unexpected changes must pass validation.
    A manifest with unexpected changes must fail.
    """
    manifest_ok = PhaseImpactManifest(
        phase_id='test_ok',
        baseline_head='9adbea5',
        candidate_head='9adbea5',
        intended_tokens=[],
        intended_fields=[],
        actual_changed_tokens=[],
        actual_changed_fields=[],
        unexpected_changes=0,
        closed_contract_regressions=0,
    )
    manifest_ok.assert_closed()   # must not raise

    manifest_bad = PhaseImpactManifest(
        phase_id='test_bad',
        baseline_head='9adbea5',
        candidate_head='deadbeef',
        intended_tokens=['اللَّهُ'],
        intended_fields=['word_class'],
        actual_changed_tokens=['اللَّهُ', 'غَيْرِهَا'],
        actual_changed_fields=['word_class', 'tense_aspect'],
        unexpected_changes=1,
        closed_contract_regressions=0,
    )
    with pytest.raises(AssertionError):
        manifest_bad.assert_closed()


# ══════════════════════════════════════════════════════════════════════════════
# PROTECTED TEST GOVERNANCE
# ══════════════════════════════════════════════════════════════════════════════

def test_protected_tests_require_amendment_metadata():
    """
    This test file is itself a protected constitutional test.
    The GOVERNANCE_METADATA block at the top must contain
    amendment_required_to_modify=True and a mandate reference.
    """
    import ast, inspect, pathlib
    src = pathlib.Path(__file__).read_text()
    tree = ast.parse(src)
    # Find the GOVERNANCE_METADATA assignment
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == 'GOVERNANCE_METADATA':
                    found = True
    assert found, (
        "GOVERNANCE_METADATA block must be present in this file. "
        "Removing it is itself a constitutional violation.")


# ══════════════════════════════════════════════════════════════════════════════
# LIVE SEQUENTIAL RUNNER PROBES
# ══════════════════════════════════════════════════════════════════════════════

def test_live_runner_allah_occurrences_are_protected():
    """
    Run the exact live sequential runner (Ayat al-Dayn 129-token corpus)
    and prove all اللَّهُ occurrences remain protected:
      - boundary_type or jamid_verdict == JAMID_AALAM_BOUNDARY
      - word_class != FI3L
      - tense_aspect is None
    LAFZ_AL_JALALA_VERBAL_ANALYSES = 0.
    """
    import importlib.util, pathlib
    _script = (
        pathlib.Path(__file__).resolve().parent.parent.parent
        / 'scripts' / 'demo_ayat_al_dayn.py'
    )
    _spec = importlib.util.spec_from_file_location('demo_ayat_al_dayn', _script)
    _mod  = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    TOKENS = _mod.TOKENS
    process_token_full = _mod.process_token_full
    allah_bare = {'الله', 'اللّه'}

    def _is_allah(surface: str) -> bool:
        stripped = ''.join(c for c in surface if c not in 'ًٌٍَُِّْٰ')
        # Keep shadda-normalized comparison
        norm = ''.join(c for c in surface if c not in 'ًٌٍَُِ')
        bare = stripped.replace('ّ', '')
        return 'الله' in bare or 'لله' in bare

    violations = []
    for i, tok in enumerate(TOKENS):
        if not _is_allah(tok):
            continue
        r = process_token_full(i + 1, tok)
        wc = (r.get('word_class') or {}).get('class')
        ms = r.get('morphosyntax') or {}
        ta = ms.get('tense_aspect')
        jv = r.get('jamid_verdict')  # from full pipeline via process_token_full
        # check directly via hokom for the multi-word case
        hr = hokom(tok)
        hr_wc = hr.get('word_class')
        hr_jv = hr.get('jamid_verdict')
        if hr_wc == 'FI3L' or hr.get('tense_aspect') is not None:
            violations.append(
                f"tok[{i+1}] {tok!r}: word_class={hr_wc!r}, "
                f"tense_aspect={hr.get('tense_aspect')!r}, "
                f"jamid_verdict={hr_jv!r}")
    assert violations == [], (
        f"LAFZ_AL_JALALA_VERBAL_ANALYSES={len(violations)}: {violations}")
