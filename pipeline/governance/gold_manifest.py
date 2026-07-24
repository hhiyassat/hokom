#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/gold_manifest.py

HOKOM-LIVE-GOLD-ORACLE-COVERAGE-AND-GATE-HARDENING-02
(supersedes HOKOM-LIVE-GOLD-ORACLE-AND-METRICS-CORRECTION-01)

Immutable protected gold manifest for the Ayat al-Dayn 129-token corpus.

Design rules:
  - Frozen dataclasses only — no mutable state.
  - Correlated ambiguity bundles: person/number/gender grouped per reading.
    Never use independent person='2|3' + gender='M' strings.
  - form_family_out_of_scope=True marks KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS
    (FORM_REOPENING = FORBIDDEN — cannot fix without constitutional amendment).
  - FORM_X_PROTECTION is explicit, not incidental.
  - Negative controls are declared alongside the protection set.
  - GOVERNANCE_METADATA must remain as executable Python.
  - MANIFEST_DIGEST is the SHA-256 of the canonical CORPUS_GOLD serialization.
    Any change to protected gold expectations requires a CONSTITUTIONAL_AMENDMENT_ID
    and must update MANIFEST_DIGEST in the same commit.

Any modification to CORPUS_GOLD or FORM_X_PROTECTION requires:
  1. A CONSTITUTIONAL_AMENDMENT_ID string (assigned by the governance lead).
  2. An old/new expectation diff attached to the amendment record.
  3. An updated MANIFEST_DIGEST computed from the new canonical serialization.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Optional

# Constitutional marker — do not remove or move to a docstring.
GOVERNANCE_METADATA = {
    "mandate": "HOKOM-LIVE-GOLD-ORACLE-COVERAGE-AND-GATE-HARDENING-02",
    "supersedes": "HOKOM-LIVE-GOLD-ORACLE-AND-METRICS-CORRECTION-01",
    "start_head": "988d00f",
    "protected": True,
    "amendment_required_to_modify": True,
    "constitutional_amendment_id": None,   # set when an amendment is applied
}

# Amendment guard — set before any protected change is landed.
CONSTITUTIONAL_AMENDMENT_ID: Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────────
# Correlated ambiguity bundle
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AmbiguityCandidate:
    """
    One reading within a structurally ambiguous imperfect surface.

    person / number / gender form a CORRELATED triple — they must not be
    split into independent strings.  E.g. تَ-prefix imperfect:
      AmbiguityCandidate('2', 'SG', 'M', '2MS')
      AmbiguityCandidate('3', 'SG', 'F', '3FS')
    NOT: person='2|3', gender='M'
    """
    person: str
    number: str
    gender: str
    reading: str   # human label: '2MS', '3FS', '3MDU', …


# ──────────────────────────────────────────────────────────────────────────────
# Gold record
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class GoldRecord:
    """
    Immutable gold standard for one token in the Ayat al-Dayn corpus.

    Fields that are None are not checked (the gold does not constrain them).
    When ambiguity_candidates is non-empty, it overrides person/number/gender
    as the authoritative reading set.
    """
    token_index: int
    surface: str

    # ── Pipeline output expectations ─────────────────────────────────────────
    word_class: Optional[str] = None
    tense_aspect: Optional[str] = None
    voice: Optional[str] = None
    number: Optional[str] = None
    gender: Optional[str] = None
    person: Optional[str] = None
    mood: Optional[str] = None

    # ── Correlated ambiguity (overrides person/number/gender when non-empty) ─
    ambiguity_candidates: tuple = ()

    # ── CRA form family ───────────────────────────────────────────────────────
    cra_form_family: Optional[str] = None

    # ── Known form-family residual (FORM_REOPENING=FORBIDDEN) ────────────────
    form_family_out_of_scope: bool = False

    # ── Defect codes (active at start_head = 988d00f) ────────────────────────
    defect_codes: tuple = ()

    notes: str = ''


# ──────────────────────────────────────────────────────────────────────────────
# Corpus gold records (14 total)
# ──────────────────────────────────────────────────────────────────────────────

CORPUS_GOLD: tuple[GoldRecord, ...] = (

    # ── Token 4 ──────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=4,
        surface='آمَنُوا',
        word_class='FI3L',
        tense_aspect='PAST',
        person='3',
        number='PL',
        gender='M',
        voice='ACTIVE',
        cra_form_family='FORM_IV',
        form_family_out_of_scope=True,
        defect_codes=('KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL',),
        notes='آمَنَ = Form IV (أَفْعَلَ). '
              'CRA at 988d00f returns cra_form=None (Form IV prefix not recognized). '
              'FORM_REOPENING=FORBIDDEN.',
    ),

    # ── Token 9 ──────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=9,
        surface='أَجَلٍ',
        word_class='ISM',
        defect_codes=('WORD_CLASS_MISCLASSIFICATION',),
        notes='Tanwin kasra marks a common noun; must be ISM not FI3L. '
              'Pipeline at 988d00f: wc=FI3L, tense=PAST.',
    ),

    # ── Token 11 ─────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=11,
        surface='فَاكْتُبُوهُ',
        word_class='FI3L',
        tense_aspect='IMPERATIVE',
        person='2',
        number='PL',
        gender='M',
        voice='ACTIVE',
        cra_form_family='FORM_I',
        form_family_out_of_scope=True,
        defect_codes=('KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL',),
        notes='كَتَبَ = Form I imperative with obj-enclitic ه. '
              'CRA at 988d00f gives FORM_VIII (اِفْتَعَلَ misfire). '
              'FORM_REOPENING=FORBIDDEN.',
    ),

    # ── Token 29 ─────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=29,
        surface='وَلْيَتَّقِ',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        person='3',
        number='SG',
        gender='M',
        voice='ACTIVE',
        cra_form_family='FORM_VIII',
        form_family_out_of_scope=True,
        defect_codes=('KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL',),
        notes='اتَّقَى = Form VIII (اِفْتَعَلَ, تَ+وَ assimilation → تَّ). '
              'Jussive 3MS with لَامُ الأَمْر (وَلْ proclitic). '
              'CRA at 988d00f gives FORM_II. FORM_REOPENING=FORBIDDEN.',
    ),

    # ── Token 46 ─────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=46,
        surface='يَسْتَطِيعُ',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        person='3',
        number='SG',
        gender='M',
        voice='ACTIVE',
        mood='INDICATIVE',
        cra_form_family='FORM_X',
        defect_codes=(),
        notes='CONTEXT BOUNDARY PROTECTION: أَوْ لَا يَسْتَطِيعُ — '
              'لَا is NEGATIVE (نَافِيَة) not JASSIM (جَازِمَة) in this position. '
              'The context carrier must NOT inject JUSSIVE here. '
              'Pipeline at 988d00f correctly gives mood=INDICATIVE, cra=FORM_X. '
              'This record protects against regression where لَا is mistakenly '
              'treated as a jussive particle after أَوْ.',
    ),

    # ── Token 48 ─────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=48,
        surface='يُمِلَّ',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        person='3',
        number='SG',
        gender='M',
        voice='ACTIVE',
        cra_form_family='FORM_IV',
        form_family_out_of_scope=True,
        defect_codes=('VOICE_MISMATCH', 'KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL'),
        notes='أَمَلَّ = Form IV (أَفْعَلَ) geminate; يُمِلَّ = 3MS subjunctive (أَنْ يُمِلَّ). '
              'Pipeline at 988d00f: voice=PASSIVE (damma on يُ prefix triggers passive '
              'heuristic; Form IV active override missing), cra=FORM_I_IMPERFECT. '
              'FORM_REOPENING=FORBIDDEN.',
    ),

    # ── Token 53 ─────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=53,
        surface='وَاسْتَشْهِدُوا',
        word_class='FI3L',
        tense_aspect='IMPERATIVE',
        person='2',
        number='PL',
        gender='M',
        voice='ACTIVE',
        cra_form_family='FORM_X',
        defect_codes=(),
        notes='Form X (اِسْتَفْعَلَ) imperative 2MPL. '
              'FORM_X explicit protection — incidental CRA success is not sufficient. '
              'Pipeline at 988d00f correctly gives cra=FORM_X.',
    ),

    # ── Token 59 ─────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=59,
        surface='يَكُونَا',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        person='3',
        number='DU',
        gender='M',
        defect_codes=('NUMBER_MISMATCH',),
        notes='يَكُونَا: 3MDU jussive (dual alif suffix). '
              'Pipeline at 988d00f: number=SG (attachment strips suffix → '
              'feature extraction on truncated stem).',
    ),

    # ── Token 68 ─────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=68,
        surface='تَضِلَّ',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        # Correlated ambiguity — do NOT split into person='2|3' + gender='M'
        ambiguity_candidates=(
            AmbiguityCandidate(person='2', number='SG', gender='M', reading='2MS'),
            AmbiguityCandidate(person='3', number='SG', gender='F', reading='3FS'),
        ),
        defect_codes=('UNCORRELATED_AMBIGUITY',),
        notes='تَ prefix subjunctive: 2MS (أنتَ تَضِلَّ) or 3FS (هي تَضِلَّ). '
              'Pipeline at 988d00f: person=2|3 but gender=M only — '
              'the 3FS candidate (gender=F) is absent.',
    ),

    # ── Token 70 ─────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=70,
        surface='فَتُذَكِّرَ',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        ambiguity_candidates=(
            AmbiguityCandidate(person='2', number='SG', gender='M', reading='2MS'),
            AmbiguityCandidate(person='3', number='SG', gender='F', reading='3FS'),
        ),
        cra_form_family='FORM_II',
        form_family_out_of_scope=True,
        defect_codes=('UNCORRELATED_AMBIGUITY', 'KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL'),
        notes='ذَكَّرَ = Form II imperfect. '
              'CRA at 988d00f gives FORM_V. '
              'FORM_REOPENING=FORBIDDEN. '
              'gender=M only; 3FS candidate missing.',
    ),

    # ── Token 80 ─────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=80,
        surface='تَسْأَمُوا',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        person='2',
        number='PL',
        gender='M',
        mood='JUSSIVE',
        defect_codes=('CONTEXT_MOOD_MISMATCH',),
        notes='وَلَا تَسْأَمُوا: وَلَا is prohibitive (لَا النَّاهِيَة) — '
              'requires JUSSIVE mood. '
              'Raw hokom() (stateless, no sequential context) gives mood=INDICATIVE. '
              'Context carrier injects JUSSIVE only in the process_token_full() '
              'sequential run; compute_live_metrics() uses raw hokom() and therefore '
              'cannot detect the context-injected JUSSIVE here.',
    ),

    # ── Token 99 ─────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=99,
        surface='تَكُونَ',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        person='3',
        number='SG',
        gender='F',
        mood='SUBJUNCTIVE',
        defect_codes=('PERSON_NUMBER_GENDER_MISMATCH',),
        notes='إِلَّا أَنْ تَكُونَ تِجَارَةً: "unless it be a commercial transaction" '
              '— 3FS subjunctive. Pipeline at 988d00f: person=2, number=PL, gender=M '
              '(bare تكون endswith ون → plural path misfires on hollow stem).',
    ),

    # ── Token 102 ────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=102,
        surface='تُدِيرُونَهَا',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        voice='ACTIVE',
        person='2',
        number='PL',
        gender='M',
        defect_codes=('VOICE_MISMATCH',),
        notes='Form IV active imperfect 2MPL (تُفْعِلُونَ pattern). '
              'Pipeline at 988d00f: voice=PASSIVE (damma on تُ prefix '
              'triggers passive heuristic, Form IV active override missing).',
    ),

    # ── Token 122 ────────────────────────────────────────────────────────────
    GoldRecord(
        token_index=122,
        surface='وَاتَّقُوا',
        word_class='FI3L',
        tense_aspect='IMPERATIVE',
        person='2',
        number='PL',
        gender='M',
        voice='ACTIVE',
        cra_form_family='FORM_VIII',
        form_family_out_of_scope=True,
        defect_codes=('KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL',),
        notes='اتَّقَى = Form VIII imperative (اِفْتَعَلَ, assimilation ت+و→تّ). '
              'CRA at 988d00f gives FORM_II. '
              'FORM_REOPENING=FORBIDDEN.',
    ),
)

# ── Gold index for O(1) lookup ────────────────────────────────────────────────
GOLD_BY_INDEX: dict[int, GoldRecord] = {r.token_index: r for r in CORPUS_GOLD}
GOLD_BY_SURFACE: dict[str, tuple[GoldRecord, ...]] = {}
for _r in CORPUS_GOLD:
    GOLD_BY_SURFACE.setdefault(_r.surface, ())
    GOLD_BY_SURFACE[_r.surface] = GOLD_BY_SURFACE[_r.surface] + (_r,)


# ──────────────────────────────────────────────────────────────────────────────
# Manifest digest (SHA-256 of canonical CORPUS_GOLD serialization)
# ──────────────────────────────────────────────────────────────────────────────
# This digest is computed from the canonical JSON serialization of CORPUS_GOLD
# (sorted by token_index, all fields included, ensure_ascii=False).
# Any modification to CORPUS_GOLD must:
#   1. Assign a CONSTITUTIONAL_AMENDMENT_ID above.
#   2. Recompute and update MANIFEST_DIGEST using _compute_manifest_digest().
#   3. Record the old/new diff in the amendment.

def _compute_digest_for(corpus: tuple) -> str:
    """Compute SHA-256 of canonical serialization for an arbitrary GoldRecord tuple."""
    canonical = []
    for rec in sorted(corpus, key=lambda r: r.token_index):
        canonical.append({
            'token_index': rec.token_index,
            'surface': rec.surface,
            'word_class': rec.word_class,
            'tense_aspect': rec.tense_aspect,
            'voice': rec.voice,
            'number': rec.number,
            'gender': rec.gender,
            'person': rec.person,
            'mood': rec.mood,
            'cra_form_family': rec.cra_form_family,
            'form_family_out_of_scope': rec.form_family_out_of_scope,
            'defect_codes': sorted(rec.defect_codes),
            'ambiguity_candidates': [
                {
                    'gender': c.gender,
                    'number': c.number,
                    'person': c.person,
                    'reading': c.reading,
                }
                for c in rec.ambiguity_candidates
            ],
        })
    serialized = json.dumps(canonical, ensure_ascii=False, sort_keys=True)
    return 'sha256:' + hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def _compute_manifest_digest() -> str:
    """Compute SHA-256 of canonical CORPUS_GOLD serialization."""
    return _compute_digest_for(CORPUS_GOLD)


# ── Computed at import time from the live CORPUS_GOLD ────────────────────────
# To update: run python3 -c "from pipeline.governance.gold_manifest import
# _compute_manifest_digest; print(_compute_manifest_digest())"
# and paste the result here along with a CONSTITUTIONAL_AMENDMENT_ID.
MANIFEST_DIGEST: str = 'sha256:7d09c9f5ce6c536e00ca41d3249b9c3829cbb104c3994c44fb3b9d911bc0d512'

# ── Digest guard ──────────────────────────────────────────────────────────────
# After seeding, MANIFEST_DIGEST must be frozen to a literal string so that
# tests can detect unauthorized changes.  The governance test checks that
# _compute_manifest_digest() == MANIFEST_DIGEST.
# See tests/integration/test_gold_oracle_compliance.py::test_manifest_digest_stable.


def verify_manifest_integrity() -> tuple[bool, str]:
    """
    Return (ok, message).  ok=True if CORPUS_GOLD is unchanged since MANIFEST_DIGEST
    was last computed and frozen.

    IMPORTANT: While MANIFEST_DIGEST = _compute_manifest_digest() (self-seeding),
    this always returns True.  The freeze step (replacing the RHS with a literal
    string) is required for the governance gate to be meaningful.
    """
    computed = _compute_manifest_digest()
    if computed == MANIFEST_DIGEST:
        return True, 'MANIFEST_INTEGRITY_OK'
    return False, (
        f'MANIFEST_INTEGRITY_VIOLATION: '
        f'expected={MANIFEST_DIGEST!r} computed={computed!r}. '
        'A CONSTITUTIONAL_AMENDMENT_ID is required to modify CORPUS_GOLD.'
    )


# ──────────────────────────────────────────────────────────────────────────────
# FORM_X explicit protection set
# ──────────────────────────────────────────────────────────────────────────────
# Incidental CRA success is not protection.
# These surfaces must pass form-level checks independently of whether
# they happen to appear in the live corpus run.

@dataclass(frozen=True)
class FormXRecord:
    surface: str
    expected_word_class: str
    expected_tense_aspect: str
    expected_cra_form: str
    notes: str = ''


FORM_X_PROTECTION: tuple[FormXRecord, ...] = (
    FormXRecord(
        surface='سَيَسْتَغْفِرُونَ',
        expected_word_class='FI3L',
        expected_tense_aspect='IMPERFECT',
        expected_cra_form='FORM_X',
        notes='سَ future prefix + Form X imperfect. Pipeline at 988d00f: wc=None '
              '(سَ prefix unsupported → UNJUSTIFIED_WORD_CLASS_NOT_OPENED).',
    ),
    FormXRecord(
        surface='يَسْتَغْفِرُونَ',
        expected_word_class='FI3L',
        expected_tense_aspect='IMPERFECT',
        expected_cra_form='FORM_X',
        notes='Form X imperfect 3MPL. Pipeline at 988d00f: cra_form=FORM_I_IMPERFECT '
              '(CRA does not recognise اِسْتَ as Form X marker).',
    ),
    FormXRecord(
        surface='اِسْتَغْفِرُوا',
        expected_word_class='FI3L',
        expected_tense_aspect='IMPERATIVE',
        expected_cra_form='FORM_X',
        notes='Form X imperative 2MPL. CRA at 988d00f: FORM_X ✓ (passing).',
    ),
    FormXRecord(
        surface='وَاسْتَشْهِدُوا',
        expected_word_class='FI3L',
        expected_tense_aspect='IMPERATIVE',
        expected_cra_form='FORM_X',
        notes='Form X imperative 2MPL (token 53 in corpus). '
              'CRA at 988d00f: FORM_X ✓ (passing).',
    ),
)

# Negative controls: these must NOT be classified as FORM_X.
FORM_X_NEGATIVE_CONTROLS: tuple[tuple[str, str], ...] = (
    ('سَيَكْتُبُونَ', 'FORM_I'),   # Form I imperfect; يَ prefix with سَ
    ('أَكْرَمُوا',    'FORM_IV'),  # Form IV past 3MPL
)

FORM_X_PROTECTION_INDEX: dict[str, FormXRecord] = {
    r.surface: r for r in FORM_X_PROTECTION
}


# ──────────────────────────────────────────────────────────────────────────────
# Word-class justification register
# ──────────────────────────────────────────────────────────────────────────────
# Documents which kinds of word_class=None are JUSTIFIED, which are UNJUSTIFIED,
# and which are UNADJUDICATED.  Used by compute_live_metrics() to split
# WORD_CLASS_NOT_OPENED_TOTAL into three subcategories.

# Justification reason codes for word_class=None tokens
WC_JUSTIFIED_REASON_CODES: frozenset[str] = frozenset({
    'WORD_CLASS_NOT_AVAILABLE',     # JAMID_AALAM_BOUNDARY (لفظ الجلالة)
    'SEGMENTATION_NO_LEXICAL_HOST', # proclitic-only token, no analyzable host
})

# Route codes that produce JUSTIFIED word_class=None
WC_JUSTIFIED_ROUTES: frozenset[str] = frozenset({
    'OPERATOR_BOUNDARY',  # grammatical operators/particles handled by boundary layer
})

# Everything else (skip_reason=WORD_CLASS_DEFERRED with no known route) is
# UNJUSTIFIED until explicitly adjudicated.


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
# Amendment record + authorization gate
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AmendmentRecord:
    """
    Explicit amendment record required for any protected gold change.

    A matching recomputed new_manifest_digest alone does NOT authorize the change.
    All fields must be non-empty.  amendment_id must be assigned by the governance
    lead before the commit is landed.
    """
    amendment_id: str                       # governance-assigned ID
    old_manifest_digest: str                # must equal the frozen MANIFEST_DIGEST before the change
    new_manifest_digest: str                # must equal _compute_digest_for(proposed_corpus_gold)
    changed_gold_key: str                   # e.g. "token_9.word_class"
    old_expectation: str                    # human-readable before value
    new_expectation: str                    # human-readable after value
    rationale: str                          # linguistic or pipeline justification
    affected_constitutional_contract: str   # mandate / contract ID being amended


def verify_amendment_authorization(
    amendment: AmendmentRecord,
    proposed_corpus_gold: tuple,
) -> tuple[str, str]:
    """
    Return ('ACCEPT', reason) or ('GOVERNANCE_REJECTED', reason).

    Rules (all must pass):
      1. amendment_id must be non-empty — a recomputed digest ALONE is insufficient.
      2. old_manifest_digest must equal the current frozen MANIFEST_DIGEST.
      3. new_manifest_digest must equal _compute_digest_for(proposed_corpus_gold).
      4. All narrative fields must be non-empty.
    """
    # Rule 1 — amendment_id is mandatory; digest match alone is not authorization.
    if not (amendment.amendment_id or '').strip():
        return (
            'GOVERNANCE_REJECTED',
            'AMENDMENT_ID_MISSING: A CONSTITUTIONAL_AMENDMENT_ID is required. '
            'A matching recomputed digest alone does not authorize the change.',
        )

    # Rule 2 — old digest must match the current frozen manifest.
    if amendment.old_manifest_digest != MANIFEST_DIGEST:
        return (
            'GOVERNANCE_REJECTED',
            f'OLD_DIGEST_MISMATCH: amendment.old_manifest_digest='
            f'{amendment.old_manifest_digest!r} does not match frozen '
            f'MANIFEST_DIGEST={MANIFEST_DIGEST!r}.',
        )

    # Rule 3 — new digest must match the proposed corpus.
    computed_new = _compute_digest_for(proposed_corpus_gold)
    if amendment.new_manifest_digest != computed_new:
        return (
            'GOVERNANCE_REJECTED',
            f'NEW_DIGEST_MISMATCH: amendment.new_manifest_digest='
            f'{amendment.new_manifest_digest!r} does not match computed='
            f'{computed_new!r}.',
        )

    # Rule 4 — all narrative fields must be present.
    for field_name in (
        'changed_gold_key', 'old_expectation', 'new_expectation',
        'rationale', 'affected_constitutional_contract',
    ):
        if not (getattr(amendment, field_name, '') or '').strip():
            return (
                'GOVERNANCE_REJECTED',
                f'MISSING_REQUIRED_FIELD: {field_name} must not be empty.',
            )

    return (
        'ACCEPT',
        f'AMENDMENT_AUTHORIZED: amendment_id={amendment.amendment_id!r} '
        f'approved for {amendment.changed_gold_key}.',
    )


def active_defect_surfaces() -> frozenset[str]:
    """Return surfaces with declared defects at start_head."""
    return frozenset(
        r.surface for r in CORPUS_GOLD if r.defect_codes
    )


def known_oos_surfaces() -> frozenset[str]:
    """Return surfaces with known out-of-scope form residuals."""
    return frozenset(
        r.surface for r in CORPUS_GOLD if r.form_family_out_of_scope
    )


def protection_surfaces() -> frozenset[str]:
    """Return surfaces that are protection records (defect_codes=())."""
    return frozenset(
        r.surface for r in CORPUS_GOLD if not r.defect_codes
    )
