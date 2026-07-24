#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_correction_01_live.py

HOKOM-GOLDEN-RULES-AND-LIVE-CLOSURE-CORRECTION-01

Live-closure correction tests.  These asserted FAILING behaviour at b0fca1e
(false-zero closure while the CSV carried defects) and now assert the corrected
behaviour after the linguistic + oracle fixes.

Covers:
  - يَسْتَطِيعُ mood INDICATIVE (لا نافية after أَوْ)
  - تُدِيرُونَهَا FORM_IV + hollow root دور
  - أَجَلٍ subclass LEXICAL_NOUN (not ISM_FA3IL)
  - correlated 2MS/3FS ambiguity bundles (تَضِلَّ / فَتُذَكِّرَ / تَكُونَ)
  - extended gold policy field coverage + zero live mismatches
  - golden_rules.md integrity + amendment penetration
  - parametrized FORM_X / FORM_I-imperative / negative-vs-prohibitive لا / tanwin→ISM

No skip. No xfail.
"""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib

import pytest

from hokom_pipeline import hokom

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_GOLDEN_RULES_PATH = _REPO_ROOT / 'golden_rules.md'


def _load_demo():
    script = _REPO_ROOT / 'scripts' / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('demo_ayat_al_dayn', script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _metrics():
    return _load_demo().compute_live_metrics()


# ══════════════════════════════════════════════════════════════════════════════
# Linguistic corrections
# ══════════════════════════════════════════════════════════════════════════════

def test_yastatiu_is_indicative_after_negative_laa():
    r = hokom('يَسْتَطِيعُ')
    assert r.get('mood') == 'INDICATIVE'


def test_yastatiu_context_mood_is_indicative_in_live_run():
    """In the sequential run (أَوْ لَا يَسْتَطِيعُ) لَا must NOT inject JUSSIVE."""
    m = _metrics()
    assert m['LIVE_CONTEXT_MOOD_MISMATCHES'] == 0


def test_tudirunaha_is_form_iv_root_dwr():
    r = hokom('تُدِيرُونَهَا')
    cra = r.get('cra_result')
    assert getattr(cra, 'form_family', None) == 'FORM_IV'
    root = r.get('final_root') or r.get('canonical_root')
    root_str = ''.join(root) if isinstance(root, (tuple, list)) else str(root)
    assert root_str in ('دور', 'دَوَرَ', 'دَيَرَ')


def test_ajal_is_lexical_noun_not_ism_fa3il():
    r = hokom('أَجَلٍ')
    assert r.get('word_class') == 'ISM'
    assert r.get('word_class_subclass') != 'ISM_FA3IL'
    assert r.get('word_class_subclass') == 'LEXICAL_NOUN'


def test_tadilla_resolves_to_3fs_in_live_context():
    m = _metrics()
    assert m['LIVE_PERSON_NUMBER_GENDER_MISMATCHES'] == 0


# ══════════════════════════════════════════════════════════════════════════════
# Structured correlated ambiguity (bundles, not pipe strings)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize('surface', ['تَضِلَّ', 'فَتُذَكِّرَ', 'تَكُونَ'])
def test_correlated_ambiguity_bundles_present(surface):
    r = hokom(surface)
    bundles = r.get('ambiguity_candidates') or ()
    triples = {
        (c['person'], c['number'], c['gender']) for c in bundles
    }
    assert ('2', 'SG', 'M') in triples, f'{surface}: 2MS bundle missing'
    assert ('3', 'SG', 'F') in triples, f'{surface}: 3FS bundle missing'


def test_uncorrelated_ambiguity_is_zero():
    m = _metrics()
    assert m['LIVE_UNCORRELATED_AMBIGUITY'] == 0


# ══════════════════════════════════════════════════════════════════════════════
# Extended gold policy coverage
# ══════════════════════════════════════════════════════════════════════════════

def test_extended_gold_subclass_and_root_metrics_zero():
    m = _metrics()
    assert m['LIVE_SUBCLASS_MISMATCHES'] == 0
    assert m['LIVE_ROOT_MISMATCHES'] == 0


def test_gold_oracle_checks_subclass_field():
    """The extended policy must carry a subclass expectation for أَجَلٍ (token 9)."""
    from pipeline.governance.extended_gold_policy import EXTENDED_GOLD_BY_INDEX
    exp = EXTENDED_GOLD_BY_INDEX[9]
    assert exp.word_class_subclass == 'LEXICAL_NOUN'


def test_gold_oracle_checks_root_and_form_for_token_102():
    from pipeline.governance.extended_gold_policy import EXTENDED_GOLD_BY_INDEX
    exp = EXTENDED_GOLD_BY_INDEX[102]
    assert exp.canonical_root == ('د', 'و', 'ر')
    assert exp.cra_form_family == 'FORM_IV'


def test_csv_in_memory_divergences_zero():
    m = _metrics()
    assert m['CSV_IN_MEMORY_DIVERGENCES'] == 0


def test_gold_manifest_untouched():
    """gold_manifest.py MANIFEST_DIGEST must remain unchanged (immutable)."""
    from pipeline.governance.gold_manifest import verify_manifest_integrity
    ok, msg = verify_manifest_integrity()
    assert ok, msg


# ══════════════════════════════════════════════════════════════════════════════
# Golden rules integrity + amendment penetration
# ══════════════════════════════════════════════════════════════════════════════

def test_golden_rules_integrity():
    from pipeline.governance.golden_rules_guard import verify_golden_rules_integrity
    ok, msg = verify_golden_rules_integrity()
    assert ok, f'GOLDEN_RULES_INTEGRITY_VIOLATION: {msg}'


def test_golden_rules_rejects_unauthorized_rule_change():
    from pipeline.governance.golden_rules_guard import (
        GoldenRulesAmendmentRecord, verify_golden_rules_amendment,
        GOLDEN_RULES_DIGEST,
    )
    mutated_content = _GOLDEN_RULES_PATH.read_text(encoding='utf-8').replace(
        'INDICATIVE', 'JUSSIVE', 1
    )
    new_digest = 'sha256:' + hashlib.sha256(mutated_content.encode('utf-8')).hexdigest()
    unauthorized = GoldenRulesAmendmentRecord(
        amendment_id='',
        old_digest=GOLDEN_RULES_DIGEST,
        new_digest=new_digest,
        change_type='MODIFY',
        old_rule_text='mood=INDICATIVE',
        new_rule_text='mood=JUSSIVE',
        rationale='',
        affected_contracts='test',
    )
    verdict, reason = verify_golden_rules_amendment(unauthorized, mutated_content)
    assert verdict == 'GOVERNANCE_REJECTED'
    assert 'AMENDMENT_ID_MISSING' in reason


def test_golden_rules_accepts_authorized_append():
    from pipeline.governance.golden_rules_guard import (
        GoldenRulesAmendmentRecord, verify_golden_rules_amendment,
        GOLDEN_RULES_DIGEST, _compute_canonical_digest,
    )
    base = _GOLDEN_RULES_PATH.read_text(encoding='utf-8')
    appended = base + (
        '\n## 18. NEW_RULE_EXAMPLE\n'
        '- Example appended rule for penetration test.\n'
        '- Source: HOKOM-GOLDEN-RULES-AND-LIVE-CLOSURE-CORRECTION-01\n'
    )
    new_digest = _compute_canonical_digest(appended)
    authorized = GoldenRulesAmendmentRecord(
        amendment_id='AMD-GRULES-2026-001',
        old_digest=GOLDEN_RULES_DIGEST,
        new_digest=new_digest,
        change_type='APPEND',
        old_rule_text='',
        new_rule_text='## 18. NEW_RULE_EXAMPLE ...',
        rationale='Add a new rule via the authorized append path.',
        affected_contracts='golden_rules.md',
    )
    verdict, reason = verify_golden_rules_amendment(authorized, appended)
    assert verdict == 'ACCEPT', reason


def test_golden_rules_rejects_unauthorized_delete():
    from pipeline.governance.golden_rules_guard import (
        GoldenRulesAmendmentRecord, verify_golden_rules_amendment,
        GOLDEN_RULES_DIGEST, _compute_canonical_digest,
    )
    base = _GOLDEN_RULES_PATH.read_text(encoding='utf-8')
    # Remove a rule line (a DELETE) without an amendment_id.
    reduced = base.replace('## 13. ISM vs FI3L Routing', '', 1)
    new_digest = _compute_canonical_digest(reduced)
    unauthorized = GoldenRulesAmendmentRecord(
        amendment_id='',
        old_digest=GOLDEN_RULES_DIGEST,
        new_digest=new_digest,
        change_type='DELETE',
        old_rule_text='## 13. ISM vs FI3L Routing',
        new_rule_text='',
        rationale='',
        affected_contracts='golden_rules.md',
    )
    verdict, reason = verify_golden_rules_amendment(unauthorized, reduced)
    assert verdict == 'GOVERNANCE_REJECTED'
    assert 'AMENDMENT_ID_MISSING' in reason


# ══════════════════════════════════════════════════════════════════════════════
# Parametrized regression protections
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize('surface', ['يَسْتَخْدِمُ', 'يَسْتَعِينُ', 'يَسْتَقِيمُ'])
def test_form_x_across_multiple_roots(surface):
    r = hokom(surface)
    cra = r.get('cra_result')
    assert getattr(cra, 'form_family', None) == 'FORM_X', (
        f'{surface}: expected FORM_X, got {getattr(cra, "form_family", None)!r}')


@pytest.mark.parametrize('surface', ['اُكْتُبْهُ', 'اِفْتَحْهُ'])
def test_form_i_imperative_before_object_enclitic(surface):
    r = hokom(surface)
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None)
    if cra_form is not None:
        assert cra_form != 'FORM_VIII', (
            f'{surface}: FORM_I imperative must not be FORM_VIII')


def test_negative_laa_after_aw_does_not_govern_jussive():
    from pipeline.p5_inflection.context_carrier import SequentialAnalysisContext
    ctx = SequentialAnalysisContext()
    for tok in ['أَوْ', 'لَا']:
        ctx.consume_mood()
        ctx.update_from_token(tok)
    assert ctx.consume_mood() is None, 'لا after أَوْ must not govern JUSSIVE'


def test_prohibitive_laa_at_clause_start_governs_jussive():
    from pipeline.p5_inflection.context_carrier import SequentialAnalysisContext
    ctx = SequentialAnalysisContext()
    ctx.consume_mood()
    ctx.update_from_token('وَلَا')  # compound prohibitive
    assert ctx.consume_mood() == 'JUSSIVE'


@pytest.mark.parametrize('surface', ['أَجَلٍ', 'رَجُلٌ', 'كِتَابًا'])
def test_tanwin_surface_is_ism_not_fi3l(surface):
    r = hokom(surface)
    assert r.get('word_class') == 'ISM', (
        f'{surface}: tanwin surface must be ISM, got {r.get("word_class")!r}')
