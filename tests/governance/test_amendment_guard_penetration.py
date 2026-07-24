#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/governance/test_amendment_guard_penetration.py

HOKOM-GOLD-MANIFEST-AMENDMENT-GUARD-PENETRATION-01

Penetration tests for the gold manifest amendment guard.

Proves:
  1. An unauthorized change + recomputed digest → GOVERNANCE_REJECTED.
     A matching new digest ALONE is not sufficient authorization.
  2. An authorized amendment with correct amendment_id, old/new digest diff,
     and all required narrative fields → ACCEPT.
  3. Word-class categorization: machine-readable records, TOTAL accounting,
     no record in more than one category, no blank record omitted.
  4. FORM_X protection tests (run only — expectations unchanged).

No skip. No xfail. Test fixtures are temporary and do not amend the live manifest.
"""
from __future__ import annotations

import dataclasses

import pytest

from pipeline.governance.gold_manifest import (
    AmendmentRecord,
    CORPUS_GOLD,
    GOLD_BY_INDEX,
    MANIFEST_DIGEST,
    WC_JUSTIFIED_REASON_CODES,
    WC_JUSTIFIED_ROUTES,
    _compute_digest_for,
    verify_amendment_authorization,
    verify_manifest_integrity,
)
from pipeline.governance.wc_audit import (
    CATEGORY_JUSTIFIED,
    CATEGORY_UNJUSTIFIED,
    CATEGORY_UNADJUDICATED,
    WcClassificationRecord,
    build_wc_classification_records,
    classify_one,
    verify_wc_accounting,
)
from hokom_pipeline import hokom


# ──────────────────────────────────────────────────────────────────────────────
# Test fixtures — temporary mutations (never committed to CORPUS_GOLD)
# ──────────────────────────────────────────────────────────────────────────────

def _mutated_corpus():
    """Return a modified CORPUS_GOLD with token 9 word_class changed ISM→HARF."""
    original = GOLD_BY_INDEX[9]
    mutated  = dataclasses.replace(original, word_class='HARF')
    return tuple(mutated if r.token_index == 9 else r for r in CORPUS_GOLD)


def _new_digest_for_mutated():
    return _compute_digest_for(_mutated_corpus())


# ══════════════════════════════════════════════════════════════════════════════
# 1. AMENDMENT GUARD — unauthorized: digest match alone is not authorization
# ══════════════════════════════════════════════════════════════════════════════

def test_unauthorized_change_recomputed_digest_rejected():
    """
    An attacker changes token 9's word_class, recomputes the new digest,
    but supplies NO amendment_id.
    Expected result: GOVERNANCE_REJECTED.
    A matching new digest alone does NOT authorize the change.
    """
    proposed = _mutated_corpus()
    new_digest = _compute_digest_for(proposed)

    unauthorized = AmendmentRecord(
        amendment_id='',                   # missing — this is the attack vector
        old_manifest_digest=MANIFEST_DIGEST,
        new_manifest_digest=new_digest,    # correctly recomputed — but irrelevant
        changed_gold_key='token_9.word_class',
        old_expectation='ISM',
        new_expectation='HARF',
        rationale='Test mutation',
        affected_constitutional_contract='HOKOM-HARDENING-02',
    )

    verdict, reason = verify_amendment_authorization(unauthorized, proposed)

    assert verdict == 'GOVERNANCE_REJECTED', (
        f'PENETRATION FAILURE: digest-only amendment was ACCEPTED. reason={reason!r}\n'
        'A matching recomputed digest alone must not authorize a gold change.')
    assert 'AMENDMENT_ID_MISSING' in reason, (
        f'GOVERNANCE_REJECTED but wrong reason: {reason!r}')


def test_unauthorized_change_wrong_amendment_id_rejected():
    """amendment_id that is whitespace only must also be rejected."""
    proposed = _mutated_corpus()
    new_digest = _compute_digest_for(proposed)

    whitespace_id = AmendmentRecord(
        amendment_id='   ',
        old_manifest_digest=MANIFEST_DIGEST,
        new_manifest_digest=new_digest,
        changed_gold_key='token_9.word_class',
        old_expectation='ISM',
        new_expectation='HARF',
        rationale='Test mutation',
        affected_constitutional_contract='HOKOM-HARDENING-02',
    )
    verdict, reason = verify_amendment_authorization(whitespace_id, proposed)
    assert verdict == 'GOVERNANCE_REJECTED', (
        f'Whitespace amendment_id should be rejected. reason={reason!r}')


def test_unauthorized_change_wrong_old_digest_rejected():
    """If old_manifest_digest doesn't match the frozen MANIFEST_DIGEST → REJECTED."""
    proposed = _mutated_corpus()
    new_digest = _compute_digest_for(proposed)

    bad_old = AmendmentRecord(
        amendment_id='AMEND-TEST-001',
        old_manifest_digest='sha256:' + 'a' * 64,   # wrong
        new_manifest_digest=new_digest,
        changed_gold_key='token_9.word_class',
        old_expectation='ISM',
        new_expectation='HARF',
        rationale='Test',
        affected_constitutional_contract='HOKOM-HARDENING-02',
    )
    verdict, reason = verify_amendment_authorization(bad_old, proposed)
    assert verdict == 'GOVERNANCE_REJECTED'
    assert 'OLD_DIGEST_MISMATCH' in reason


def test_unauthorized_change_wrong_new_digest_rejected():
    """If new_manifest_digest doesn't match the computed digest of proposed corpus → REJECTED."""
    proposed = _mutated_corpus()

    bad_new = AmendmentRecord(
        amendment_id='AMEND-TEST-001',
        old_manifest_digest=MANIFEST_DIGEST,
        new_manifest_digest='sha256:' + 'b' * 64,   # wrong
        changed_gold_key='token_9.word_class',
        old_expectation='ISM',
        new_expectation='HARF',
        rationale='Test',
        affected_constitutional_contract='HOKOM-HARDENING-02',
    )
    verdict, reason = verify_amendment_authorization(bad_new, proposed)
    assert verdict == 'GOVERNANCE_REJECTED'
    assert 'NEW_DIGEST_MISMATCH' in reason


def test_unauthorized_change_missing_rationale_rejected():
    """Missing rationale field must be rejected even with correct digests + id."""
    proposed = _mutated_corpus()
    new_digest = _compute_digest_for(proposed)

    no_rationale = AmendmentRecord(
        amendment_id='AMEND-TEST-001',
        old_manifest_digest=MANIFEST_DIGEST,
        new_manifest_digest=new_digest,
        changed_gold_key='token_9.word_class',
        old_expectation='ISM',
        new_expectation='HARF',
        rationale='',           # missing
        affected_constitutional_contract='HOKOM-HARDENING-02',
    )
    verdict, reason = verify_amendment_authorization(no_rationale, proposed)
    assert verdict == 'GOVERNANCE_REJECTED'
    assert 'MISSING_REQUIRED_FIELD' in reason


# ══════════════════════════════════════════════════════════════════════════════
# 2. AMENDMENT GUARD — authorized: all fields present + correct digests → ACCEPT
# ══════════════════════════════════════════════════════════════════════════════

def test_authorized_amendment_accepted():
    """
    A properly formed amendment with all required fields → ACCEPT.
    This proves the mechanism works: it rejects unauthorized changes and
    accepts properly authorized ones.

    Note: This test uses a TEMPORARY FIXTURE corpus — it does NOT amend
    the live CORPUS_GOLD.
    """
    proposed   = _mutated_corpus()
    new_digest = _compute_digest_for(proposed)

    authorized = AmendmentRecord(
        amendment_id='AMEND-PENETRATION-TEST-FIXTURE-01',
        old_manifest_digest=MANIFEST_DIGEST,
        new_manifest_digest=new_digest,
        changed_gold_key='token_9.word_class',
        old_expectation='ISM (Qur\'anic noun with tanwin kasra)',
        new_expectation='HARF (test fixture mutation only — not a real linguistic claim)',
        rationale='Penetration test fixture: verifying the ACCEPT path of '
                  'verify_amendment_authorization() with all required fields present.',
        affected_constitutional_contract='HOKOM-GOLD-MANIFEST-AMENDMENT-GUARD-PENETRATION-01',
    )

    verdict, reason = verify_amendment_authorization(authorized, proposed)

    assert verdict == 'ACCEPT', (
        f'Well-formed amendment should be ACCEPTED. reason={reason!r}')
    assert 'AMEND-PENETRATION-TEST-FIXTURE-01' in reason


def test_authorized_amendment_does_not_alter_live_manifest():
    """
    After running the authorized amendment test, the live MANIFEST_DIGEST
    must still be intact.  No test fixture must pollute the live manifest.
    """
    ok, msg = verify_manifest_integrity()
    assert ok, (
        f'LIVE_MANIFEST_CORRUPTED after penetration tests: {msg}')


# ══════════════════════════════════════════════════════════════════════════════
# 3. WORD-CLASS CATEGORIZATION — machine-readable audit records
# ══════════════════════════════════════════════════════════════════════════════

# Synthetic results_raw fixture covering all three categories.
# Format matches demo_ayat_al_dayn.py's internal (token_index, result_dict) pairs.
_SYNTHETIC_WC_FIXTURE: list[tuple] = [
    # JAMID_AALAM_BOUNDARY → JUSTIFIED
    (1, {'word_class': None, 'inflection_skipped_reason': 'WORD_CLASS_NOT_AVAILABLE',
          'jamid_verdict': 'JAMID_AALAM_BOUNDARY', '_route_v': None,
          'surface': 'اللَّهُ'}),
    # SEGMENTATION_NO_LEXICAL_HOST → JUSTIFIED
    (2, {'word_class': None, 'inflection_skipped_reason': 'SEGMENTATION_NO_LEXICAL_HOST',
          'jamid_verdict': None, '_route_v': None, 'surface': 'بِكُمْ'}),
    # OPERATOR_BOUNDARY route → JUSTIFIED
    (3, {'word_class': None, 'inflection_skipped_reason': None,
          'jamid_verdict': None, '_route_v': 'OPERATOR_BOUNDARY', 'surface': 'وَلَا'}),
    # Plain WORD_CLASS_DEFERRED → UNJUSTIFIED
    (4, {'word_class': None, 'inflection_skipped_reason': 'WORD_CLASS_DEFERRED',
          'jamid_verdict': None, '_route_v': None, 'surface': 'إِنَّ'}),
    # Another UNJUSTIFIED (no skip reason)
    (5, {'word_class': None, 'inflection_skipped_reason': None,
          'jamid_verdict': None, '_route_v': None, 'surface': 'مِنْ'}),
    # Has word_class — must be EXCLUDED from classification
    (6, {'word_class': 'FI3L', 'surface': 'كَتَبَ'}),
]

_EXPECTED_WC_TOTAL      = 5  # token 6 excluded
_EXPECTED_WC_JUSTIFIED  = 3  # tokens 1, 2, 3
_EXPECTED_WC_UNJUSTIFIED = 2  # tokens 4, 5


def test_build_wc_classification_records_returns_only_blank_wc():
    """Tokens with word_class != None must be excluded from classification records."""
    records = build_wc_classification_records(_SYNTHETIC_WC_FIXTURE)
    indices = [r.token_index for r in records]
    assert 6 not in indices, (
        'Token 6 (word_class=FI3L) must not appear in wc classification records.')
    assert len(records) == _EXPECTED_WC_TOTAL, (
        f'Expected {_EXPECTED_WC_TOTAL} blank-wc records, got {len(records)}.')


def test_wc_classification_categories():
    """Each token must land in exactly one category with the correct value."""
    records = build_wc_classification_records(_SYNTHETIC_WC_FIXTURE)
    by_index = {r.token_index: r for r in records}

    assert by_index[1].category == CATEGORY_JUSTIFIED,  f"token 1: {by_index[1].category}"
    assert by_index[2].category == CATEGORY_JUSTIFIED,  f"token 2: {by_index[2].category}"
    assert by_index[3].category == CATEGORY_JUSTIFIED,  f"token 3: {by_index[3].category}"
    assert by_index[4].category == CATEGORY_UNJUSTIFIED, f"token 4: {by_index[4].category}"
    assert by_index[5].category == CATEGORY_UNJUSTIFIED, f"token 5: {by_index[5].category}"


def test_wc_classification_no_duplicate_indices():
    """No token_index may appear in more than one classification record."""
    records = build_wc_classification_records(_SYNTHETIC_WC_FIXTURE)
    seen: set[int] = set()
    for rec in records:
        assert rec.token_index not in seen, (
            f'token_index={rec.token_index} appears in more than one wc record.')
        seen.add(rec.token_index)


def test_wc_verify_accounting_passes_on_valid_fixture():
    """verify_wc_accounting must return ok=True for the synthetic fixture."""
    records = build_wc_classification_records(_SYNTHETIC_WC_FIXTURE)
    ok, msg = verify_wc_accounting(records, _EXPECTED_WC_TOTAL)
    assert ok, f'verify_wc_accounting failed: {msg}'


def test_wc_verify_accounting_detects_wrong_total():
    """verify_wc_accounting must FAIL when expected_total is wrong."""
    records = build_wc_classification_records(_SYNTHETIC_WC_FIXTURE)
    ok, msg = verify_wc_accounting(records, _EXPECTED_WC_TOTAL + 1)
    assert not ok, 'verify_wc_accounting should fail with wrong total.'
    assert 'RECORD_COUNT_MISMATCH' in msg


def test_wc_jamid_classified_as_justified_not_unjustified():
    """JAMID_AALAM_BOUNDARY must NEVER appear in the UNJUSTIFIED category."""
    records = build_wc_classification_records(_SYNTHETIC_WC_FIXTURE)
    unjust = [r for r in records if r.category == CATEGORY_UNJUSTIFIED]
    for rec in unjust:
        assert 'JAMID' not in (rec.reason_code or ''), (
            f'JAMID token appears as UNJUSTIFIED: {rec!r}')


def test_wc_segmentation_no_host_classified_as_justified():
    """SEGMENTATION_NO_LEXICAL_HOST must be JUSTIFIED."""
    records = build_wc_classification_records(_SYNTHETIC_WC_FIXTURE)
    no_host = [r for r in records if 'SEGMENTATION' in (r.reason_code or '')]
    assert no_host, 'No SEGMENTATION_NO_LEXICAL_HOST record found in fixture.'
    for rec in no_host:
        assert rec.category == CATEGORY_JUSTIFIED, (
            f'SEGMENTATION_NO_LEXICAL_HOST classified as {rec.category}: {rec!r}')


def test_wc_classification_records_have_constitutional_owner():
    """Every WcClassificationRecord must have a non-empty constitutional_owner."""
    records = build_wc_classification_records(_SYNTHETIC_WC_FIXTURE)
    for rec in records:
        assert rec.constitutional_owner, (
            f'token {rec.token_index}: constitutional_owner is empty.')


# ══════════════════════════════════════════════════════════════════════════════
# 4. FORM_X PROTECTION — existing expectations unchanged
# ══════════════════════════════════════════════════════════════════════════════

def _cra_form(r: dict) -> str | None:
    cra = r.get('cra_result')
    return getattr(cra, 'form_family', None) if cra else None


def test_form_x_sayastghfiruna_defect_present():
    """سَيَسْتَغْفِرُونَ: wc=None (سَ prefix unsupported). Defect still present."""
    r = hokom('سَيَسْتَغْفِرُونَ')
    # Pipeline at 988d00f: wc=None
    assert r.get('word_class') is None, (
        f"سَيَسْتَغْفِرُونَ wc={r.get('word_class')!r}: expected None (UNJUSTIFIED_WORD_CLASS_NOT_OPENED). "
        "Defect fixed — update gold manifest + closure gate.")


def test_form_x_yastghfiruna_imperfect_cra_defect_present():
    """يَسْتَغْفِرُونَ: cra_form != FORM_X at current HEAD. Defect still present."""
    r = hokom('يَسْتَغْفِرُونَ')
    assert r.get('word_class') == 'FI3L', f"wc={r.get('word_class')!r}"
    assert r.get('tense_aspect') == 'IMPERFECT', f"ta={r.get('tense_aspect')!r}"
    assert _cra_form(r) != 'FORM_X', (
        f"يَسْتَغْفِرُونَ cra={_cra_form(r)!r}: FORM_X defect unexpectedly fixed. "
        "Update gold manifest + closure gate.")


def test_form_x_istaghfiru_imperative_passing():
    """اِسْتَغْفِرُوا: wc=FI3L, IMPERATIVE, cra=FORM_X. Must still pass (protection)."""
    r = hokom('اِسْتَغْفِرُوا')
    assert r.get('word_class') == 'FI3L',     f"wc={r.get('word_class')!r}"
    assert r.get('tense_aspect') == 'IMPERATIVE', f"ta={r.get('tense_aspect')!r}"
    assert _cra_form(r) == 'FORM_X', (
        f"اِسْتَغْفِرُوا cra={_cra_form(r)!r}: FORM_X REGRESSION.")


def test_form_x_wastashhhidu_imperative_passing():
    """وَاسْتَشْهِدُوا: wc=FI3L, IMPERATIVE, cra=FORM_X. Must still pass (protection)."""
    r = hokom('وَاسْتَشْهِدُوا')
    assert r.get('word_class') == 'FI3L',     f"wc={r.get('word_class')!r}"
    assert r.get('tense_aspect') == 'IMPERATIVE', f"ta={r.get('tense_aspect')!r}"
    assert _cra_form(r) == 'FORM_X', (
        f"وَاسْتَشْهِدُوا cra={_cra_form(r)!r}: FORM_X REGRESSION.")


def test_form_x_negative_control_sayaktubu():
    """سَيَكْتُبُونَ must NOT be classified as FORM_X."""
    r = hokom('سَيَكْتُبُونَ')
    cf = _cra_form(r)
    if cf is not None:
        assert cf != 'FORM_X', (
            f"سَيَكْتُبُونَ cra={cf!r}: Form I must never be FORM_X.")


def test_form_x_negative_control_akramu():
    """أَكْرَمُوا must NOT be classified as FORM_X."""
    r = hokom('أَكْرَمُوا')
    cf = _cra_form(r)
    if cf is not None:
        assert cf != 'FORM_X', (
            f"أَكْرَمُوا cra={cf!r}: Form IV must never be FORM_X.")
