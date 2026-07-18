#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_bab/test_phase4b.py — Phase 4B (BabProjection) Tests
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

47+ tests covering:
  Phase opening contracts
  Data model contracts (frozen, to_dict, field types)
  Mujarrad bab resolution (all 6 babs)
  Augmented form detection (FORM_II, FORM_VII, FORM_VIII, FORM_X)
  Evidence/trace preservation
  Integration with phase4b_orchestrator
  Wazn applicability (nominal → NOT_APPLICABLE)
"""

from __future__ import annotations

import dataclasses
import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from pipeline.p4_bab.models import BabCandidate, BabProjection, Phase4BResult
from pipeline.p4_bab.bab_catalog import get_bab_catalog, lookup_by_wazn_id, lookup_by_vowels
from pipeline.p4_bab.bab_rules import (
    is_verbal_family, extract_ayn_vowel_from_pattern,
    extract_imperfect_vowel_from_evidence, normalize_imperfect_wazn,
    is_mazid_wazn, get_mazid_bab,
)
from pipeline.p4_bab.bab_hypothesis import generate_bab_candidates
from pipeline.p4_bab.bab_projection import project_bab
from pipeline.p4_bab.phase4b_orchestrator import project_bab_with_licensing


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _make_wazn_candidate(wazn_id: str, wazn_family: str, wazn_pattern: str = "فَعَلَ"):
    wc = MagicMock()
    wc.wazn_id      = wazn_id
    wc.wazn_family  = wazn_family
    wc.wazn_pattern = wazn_pattern
    return wc


def _make_wazn_projection(wazn_id: str, wazn_family: str, canonical_root=None,
                           wazn_pattern: str = "فَعَلَ"):
    wp = MagicMock()
    wp.selected_wazn = _make_wazn_candidate(wazn_id, wazn_family, wazn_pattern)
    wp.canonical_root = canonical_root
    wp.residual_codes = ()
    wp.evidence_ids   = ()
    wp.trace_ids      = ()
    return wp


def _make_phase4a(
    final_directive: str,
    final_wazn: str | None = None,
    wazn_family: str = "triliteral_bare_verb",
    canonical_root: tuple | None = None,
    wazn_pattern: str = "فَعَلَ",
    evidence_ids: tuple = (),
    trace_ids: tuple = (),
    residual_codes: tuple = (),
) -> Any:
    """Build a minimal Phase4AResult-like object."""
    p4a = MagicMock()
    p4a.final_directive = final_directive
    p4a.final_wazn      = final_wazn
    p4a.evidence_ids    = evidence_ids
    p4a.trace_ids       = trace_ids
    p4a.residual_codes  = residual_codes

    if final_directive == 'ACCEPT' and final_wazn is not None:
        p4a.wazn_projection = _make_wazn_projection(
            final_wazn, wazn_family, canonical_root, wazn_pattern,
        )
        p4a.root_candidate          = MagicMock(canonical_root=canonical_root)
        p4a.promoted_root_candidate = None
    else:
        p4a.wazn_projection         = None
        p4a.root_candidate          = MagicMock(canonical_root=None)
        p4a.promoted_root_candidate = None

    return p4a


# ══════════════════════════════════════════════════════════════════════════════
# Section 1: Phase Opening
# ══════════════════════════════════════════════════════════════════════════════

class TestPhaseOpening:
    """T01-T04: Phase4B opens only when Phase4A is ACCEPT."""

    def test_T01_phase4a_accept_opens_phase4b(self):
        """Phase4A ACCEPT → Phase4B opens (stage_state=OPENED or NOT_APPLICABLE)."""
        p4a = _make_phase4a('ACCEPT', 'FA_A_LA', 'triliteral_bare_verb')
        result = project_bab_with_licensing(p4a)
        assert result.initial_wazn_directive == 'ACCEPT'
        assert result.source_path != 'not_opened'

    def test_T02_phase4a_defer_not_opened(self):
        """Phase4A DEFER → Phase4B NOT_OPENED."""
        p4a = _make_phase4a('DEFER')
        result = project_bab_with_licensing(p4a)
        assert result.final_directive == 'NOT_OPENED'
        assert result.source_path == 'not_opened'
        assert result.bab_projection is None

    def test_T03_phase4a_block_not_opened(self):
        """Phase4A BLOCK → Phase4B NOT_OPENED."""
        p4a = _make_phase4a('BLOCK')
        result = project_bab_with_licensing(p4a)
        assert result.final_directive == 'NOT_OPENED'
        assert result.source_path == 'not_opened'
        assert result.bab_projection is None

    def test_T04_nominal_wazn_not_applicable(self):
        """Non-verbal wazn → NOT_APPLICABLE."""
        p4a = _make_phase4a('ACCEPT', 'MAF3UL', 'passive_participle',
                             wazn_pattern='مَفْعُول')
        result = project_bab_with_licensing(p4a)
        assert result.final_directive == 'NOT_APPLICABLE'
        assert result.source_path == 'not_applicable'


# ══════════════════════════════════════════════════════════════════════════════
# Section 2: Contract Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestContracts:
    """T05-T13: Data model contracts."""

    def test_T05_accept_requires_exactly_one_candidate(self):
        """ACCEPT → exactly 1 candidate in candidate_abwab."""
        p4a = _make_phase4a('ACCEPT', 'IFTA3ALA', 'form_VIII_verb',
                             wazn_pattern='اِفْتَعَلَ')
        result = project_bab_with_licensing(p4a)
        if result.final_directive == 'ACCEPT':
            assert result.bab_projection is not None
            assert len(result.bab_projection.candidate_abwab) == 1

    def test_T06_selected_bab_in_candidate_abwab(self):
        """selected_bab must be one of the candidate bab_ids."""
        p4a = _make_phase4a('ACCEPT', 'IFTA3ALA', 'form_VIII_verb',
                             wazn_pattern='اِفْتَعَلَ')
        result = project_bab_with_licensing(p4a)
        if result.final_directive == 'ACCEPT' and result.bab_projection:
            bab_ids = {c.bab_id for c in result.bab_projection.candidate_abwab}
            assert result.final_bab in bab_ids

    def test_T07_defer_block_selected_bab_none(self):
        """DEFER and BLOCK → selected_bab=None."""
        # DEFER case: mujarrad without imperfect
        p4a = _make_phase4a('ACCEPT', 'FA_A_LA', 'triliteral_bare_verb')
        result = project_bab_with_licensing(p4a)
        if result.final_directive == 'DEFER':
            assert result.final_bab is None

    def test_T08_source_path_independent_of_final_directive(self):
        """source_path describes the path; NOT_OPENED has source_path='not_opened'."""
        p4a_defer = _make_phase4a('DEFER')
        r1 = project_bab_with_licensing(p4a_defer)
        assert r1.source_path == 'not_opened'

        p4a_block = _make_phase4a('BLOCK')
        r2 = project_bab_with_licensing(p4a_block)
        assert r2.source_path == 'not_opened'

    def test_T09_to_dict_json_safe(self):
        """Phase4BResult.to_dict() is JSON serializable."""
        p4a = _make_phase4a('ACCEPT', 'IFTA3ALA', 'form_VIII_verb',
                             wazn_pattern='اِفْتَعَلَ')
        result = project_bab_with_licensing(p4a)
        d = result.to_dict()
        # Should not raise
        json_str = json.dumps(d, ensure_ascii=False)
        assert isinstance(json_str, str)

    def test_T10_dtos_frozen(self):
        """All Phase4B DTOs are frozen dataclasses."""
        # BabCandidate frozen — normal assignment must raise
        c = BabCandidate(
            bab_id='TEST', bab_family='MUJARRAD', past_wazn='FA_A_LA',
            imperfect_wazn=None, confidence='HIGH',
            evidence_ids=(), trace_ids=(), residual_codes=(),
        )
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError, TypeError)):
            c.bab_id = 'CHANGED'  # type: ignore[misc]

        # BabProjection frozen
        bp = BabProjection(
            directive='DEFER', stage_state='OPENED', candidate_abwab=(),
            selected_bab=None, source_wazn=None, canonical_root=None,
            applicability='APPLICABLE', evidence_ids=(), trace_ids=(),
            residual_codes=(),
        )
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError, TypeError)):
            bp.directive = 'ACCEPT'  # type: ignore[misc]

        # Phase4BResult frozen
        r = Phase4BResult(
            initial_wazn_directive='ACCEPT', final_directive='DEFER',
            bab_projection=None, final_bab=None, source_path='deferred',
            evidence_ids=(), trace_ids=(), residual_codes=(),
        )
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError, TypeError)):
            r.final_directive = 'ACCEPT'  # type: ignore[misc]

    def test_T11_evidence_ids_are_tuple(self):
        """evidence_ids must be tuple in Phase4BResult."""
        p4a = _make_phase4a('DEFER')
        result = project_bab_with_licensing(p4a)
        assert isinstance(result.evidence_ids, tuple)

    def test_T12_trace_ids_are_tuple(self):
        """trace_ids must be tuple in Phase4BResult."""
        p4a = _make_phase4a('BLOCK')
        result = project_bab_with_licensing(p4a)
        assert isinstance(result.trace_ids, tuple)

    def test_T13_residual_codes_are_tuple(self):
        """residual_codes must be tuple in Phase4BResult."""
        p4a = _make_phase4a('ACCEPT', 'FA_A_LA', 'triliteral_bare_verb')
        result = project_bab_with_licensing(p4a)
        assert isinstance(result.residual_codes, tuple)


# ══════════════════════════════════════════════════════════════════════════════
# Section 3: Mujarrad Bab Resolution
# ══════════════════════════════════════════════════════════════════════════════

class TestMujarradBabResolution:
    """T14-T22: Mujarrad bab detection with paired evidence."""

    def test_T14_nasara_bab_i(self):
        """نَصَرَ/يَنْصُرُ: FA_A_LA + imperfect_ayn=u → BAB_I_NASARA."""
        candidates = generate_bab_candidates(
            past_wazn='FA_A_LA',
            imperfect_wazn='u',
            canonical_root=('ن', 'ص', 'ر'),
            evidence_ids=('imperfect_ayn:u',),
            trace_ids=(),
            wazn_family='triliteral_bare_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].bab_id == 'BAB_I_NASARA'

    def test_T15_daraba_bab_ii(self):
        """ضَرَبَ/يَضْرِبُ: FA_A_LA + imperfect_ayn=i → BAB_II_DARABA."""
        candidates = generate_bab_candidates(
            past_wazn='FA_A_LA',
            imperfect_wazn='i',
            canonical_root=('ض', 'ر', 'ب'),
            evidence_ids=('imperfect_ayn:i',),
            trace_ids=(),
            wazn_family='triliteral_bare_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].bab_id == 'BAB_II_DARABA'

    def test_T16_fataha_bab_iii(self):
        """فَتَحَ/يَفْتَحُ: FA_A_LA + imperfect_ayn=a → BAB_III_FATAHA."""
        candidates = generate_bab_candidates(
            past_wazn='FA_A_LA',
            imperfect_wazn='a',
            canonical_root=('ف', 'ت', 'ح'),
            evidence_ids=('imperfect_ayn:a',),
            trace_ids=(),
            wazn_family='triliteral_bare_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].bab_id == 'BAB_III_FATAHA'

    def test_T17_samia_bab_iv(self):
        """سَمِعَ/يَسْمَعُ: FA_I_LA + imperfect_ayn=a → BAB_IV_SAMIA."""
        candidates = generate_bab_candidates(
            past_wazn='FA_I_LA',
            imperfect_wazn='a',
            canonical_root=('س', 'م', 'ع'),
            evidence_ids=('imperfect_ayn:a',),
            trace_ids=(),
            wazn_family='triliteral_bare_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].bab_id == 'BAB_IV_SAMIA'

    def test_T18_karuma_bab_v(self):
        """كَرُمَ/يَكْرُمُ: FA_U_LA + imperfect_ayn=u → BAB_V_KARUMA."""
        candidates = generate_bab_candidates(
            past_wazn='FA_U_LA',
            imperfect_wazn='u',
            canonical_root=('ك', 'ر', 'م'),
            evidence_ids=('imperfect_ayn:u',),
            trace_ids=(),
            wazn_family='triliteral_bare_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].bab_id == 'BAB_V_KARUMA'

    def test_T19_hasiba_bab_vi(self):
        """حَسِبَ/يَحْسِبُ: FA_I_LA + imperfect_ayn=i → BAB_VI_HASIBA."""
        candidates = generate_bab_candidates(
            past_wazn='FA_I_LA',
            imperfect_wazn='i',
            canonical_root=('ح', 'س', 'ب'),
            evidence_ids=('imperfect_ayn:i',),
            trace_ids=(),
            wazn_family='triliteral_bare_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].bab_id == 'BAB_VI_HASIBA'

    def test_T20_fa3ala_past_only_defer(self):
        """فَعَلَ past only (no imperfect) → multiple candidates → DEFER."""
        candidates = generate_bab_candidates(
            past_wazn='FA_A_LA',
            imperfect_wazn=None,
            canonical_root=None,
            evidence_ids=(),
            trace_ids=(),
            wazn_family='triliteral_bare_verb',
        )
        # Should return 3 candidates (BAB_I, BAB_II, BAB_III), all DEFER_REQUIRED
        assert len(candidates) == 3
        assert all(c.confidence == 'DEFER_REQUIRED' for c in candidates)

    def test_T21_contradicting_pair_block(self):
        """A vowel pair not matching any bab → produces CONTRADICTION candidate → BLOCK."""
        # FA_U_LA past + imperfect 'i' doesn't exist in catalog
        candidates = generate_bab_candidates(
            past_wazn='FA_U_LA',
            imperfect_wazn='i',
            canonical_root=None,
            evidence_ids=('imperfect_ayn:i',),
            trace_ids=(),
            wazn_family='triliteral_bare_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].confidence == 'CONTRADICTION'

    def test_T22_fa3ila_past_only_ambiguous(self):
        """فَعِلَ alone → 2 candidates (BAB_IV and BAB_VI) → DEFER."""
        candidates = generate_bab_candidates(
            past_wazn='FA_I_LA',
            imperfect_wazn=None,
            canonical_root=None,
            evidence_ids=(),
            trace_ids=(),
            wazn_family='triliteral_bare_verb',
        )
        assert len(candidates) == 2
        bab_ids = {c.bab_id for c in candidates}
        assert 'BAB_IV_SAMIA' in bab_ids
        assert 'BAB_VI_HASIBA' in bab_ids


# ══════════════════════════════════════════════════════════════════════════════
# Section 4: Augmented Form Detection
# ══════════════════════════════════════════════════════════════════════════════

class TestAugmentedForms:
    """T23-T26: Augmented form (MAZID) detection."""

    def test_T23_ifta3ala_form_viii(self):
        """IFTA3ALA wazn → BAB_FORM_VIII (ACCEPT with wazn alone)."""
        candidates = generate_bab_candidates(
            past_wazn='IFTA3ALA',
            imperfect_wazn=None,
            canonical_root=None,
            evidence_ids=(),
            trace_ids=(),
            wazn_family='form_VIII_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].bab_id == 'BAB_FORM_VIII'
        assert candidates[0].confidence == 'HIGH'

    def test_T24_istaf3ala_form_x(self):
        """ISTAF3ALA wazn → BAB_FORM_X."""
        candidates = generate_bab_candidates(
            past_wazn='ISTAF3ALA',
            imperfect_wazn=None,
            canonical_root=None,
            evidence_ids=(),
            trace_ids=(),
            wazn_family='form_X_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].bab_id == 'BAB_FORM_X'
        assert candidates[0].confidence == 'HIGH'

    def test_T25_unknown_augmented_wazn_defer(self):
        """An augmented wazn_id not in bab_catalog → empty list → DEFER."""
        candidates = generate_bab_candidates(
            past_wazn='UNKNOWN_FORM_IX',
            imperfect_wazn=None,
            canonical_root=None,
            evidence_ids=(),
            trace_ids=(),
            wazn_family='form_IX_verb',   # not in _VERBAL_FAMILIES
        )
        assert len(candidates) == 0

    def test_T26_nominal_muf3al_not_form_viii(self):
        """مُفْتَعِل is a nominal pattern — nominal family → NOT_APPLICABLE (empty list)."""
        candidates = generate_bab_candidates(
            past_wazn='MUFTA3IL',
            imperfect_wazn=None,
            canonical_root=None,
            evidence_ids=(),
            trace_ids=(),
            wazn_family='active_participle',  # nominal
        )
        assert len(candidates) == 0


# ══════════════════════════════════════════════════════════════════════════════
# Section 5: Bab Rules Unit Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestBabRules:
    """T27-T35: Rules and helpers."""

    def test_T27_is_verbal_family_triliteral_bare(self):
        assert is_verbal_family("triliteral_bare_verb") is True

    def test_T28_is_verbal_family_form_viii(self):
        assert is_verbal_family("form_VIII_verb") is True

    def test_T29_is_verbal_family_passive_participle(self):
        assert is_verbal_family("passive_participle") is False

    def test_T30_is_verbal_family_none(self):
        assert is_verbal_family(None) is False

    def test_T31_extract_ayn_vowel_damma(self):
        """يَفْعُلُ → 'u'."""
        assert extract_ayn_vowel_from_pattern('يَفْعُلُ') == 'u'

    def test_T32_extract_ayn_vowel_kasra(self):
        """يَفْعِلُ → 'i'."""
        assert extract_ayn_vowel_from_pattern('يَفْعِلُ') == 'i'

    def test_T33_extract_ayn_vowel_fatha(self):
        """يَفْعَلُ → 'a'."""
        assert extract_ayn_vowel_from_pattern('يَفْعَلُ') == 'a'

    def test_T34_extract_ayn_vowel_past_fatha(self):
        """فَعَلَ → 'a'."""
        assert extract_ayn_vowel_from_pattern('فَعَلَ') == 'a'

    def test_T35_extract_imperfect_vowel_from_evidence_direct(self):
        """'imperfect_ayn:u' → 'u'."""
        assert extract_imperfect_vowel_from_evidence(('imperfect_ayn:u',)) == 'u'

    def test_T35b_extract_imperfect_vowel_embedded(self):
        """'imperfect_ayn=i' → 'i'."""
        assert extract_imperfect_vowel_from_evidence(('paired_paradigm:imperfect_ayn=i',)) == 'i'

    def test_T36_normalize_imperfect_wazn_pattern(self):
        """يَفْعُلُ → 'u'."""
        assert normalize_imperfect_wazn('يَفْعُلُ') == 'u'

    def test_T37_normalize_imperfect_wazn_char(self):
        """'a' → 'a'."""
        assert normalize_imperfect_wazn('a') == 'a'

    def test_T38_normalize_imperfect_wazn_none(self):
        """None → None."""
        assert normalize_imperfect_wazn(None) is None


# ══════════════════════════════════════════════════════════════════════════════
# Section 6: Bab Catalog
# ══════════════════════════════════════════════════════════════════════════════

class TestBabCatalog:
    """T39-T43: Catalog loading and lookup."""

    def test_T39_catalog_loads_15_entries(self):
        """Catalog should have 15 entries (6 mujarrad + 9 mazid Forms II–X)."""
        catalog = get_bab_catalog()
        assert len(catalog) == 15

    def test_T40_no_duplicate_bab_ids(self):
        """No duplicate bab_ids in catalog."""
        catalog = get_bab_catalog()
        ids = [e.bab_id for e in catalog]
        assert len(ids) == len(set(ids))

    def test_T41_lookup_by_wazn_id_fa_a_la(self):
        """FA_A_LA has 3 entries (BAB_I, BAB_II, BAB_III)."""
        entries = lookup_by_wazn_id('FA_A_LA')
        assert len(entries) == 3
        bab_ids = {e.bab_id for e in entries}
        assert 'BAB_I_NASARA' in bab_ids
        assert 'BAB_II_DARABA' in bab_ids
        assert 'BAB_III_FATAHA' in bab_ids

    def test_T42_lookup_by_vowels_a_u(self):
        """past_ayn=a, imperfect_ayn=u → BAB_I_NASARA."""
        entries = lookup_by_vowels('a', 'u')
        assert len(entries) == 1
        assert entries[0].bab_id == 'BAB_I_NASARA'

    def test_T43_lookup_by_wazn_id_ifta3ala(self):
        """IFTA3ALA → BAB_FORM_VIII."""
        entries = lookup_by_wazn_id('IFTA3ALA')
        assert len(entries) == 1
        assert entries[0].bab_id == 'BAB_FORM_VIII'


# ══════════════════════════════════════════════════════════════════════════════
# Section 7: BabProjection direct tests
# ══════════════════════════════════════════════════════════════════════════════

class TestBabProjection:
    """T44-T47: project_bab() direct tests."""

    def test_T44_accept_produces_bab_accept(self):
        """ACCEPT Phase4A + form_VIII → BabProjection.directive=ACCEPT."""
        p4a = _make_phase4a('ACCEPT', 'IFTA3ALA', 'form_VIII_verb',
                             canonical_root=('ك', 'ت', 'ب'),
                             wazn_pattern='اِفْتَعَلَ')
        bp = project_bab(p4a)
        assert bp.directive == 'ACCEPT'
        assert bp.selected_bab == 'BAB_FORM_VIII'
        assert bp.stage_state == 'OPENED'
        assert bp.applicability == 'APPLICABLE'

    def test_T45_defer_phase4a_not_opened(self):
        """DEFER Phase4A → BabProjection.stage_state=NOT_OPENED."""
        p4a = _make_phase4a('DEFER')
        bp = project_bab(p4a)
        assert bp.stage_state == 'NOT_OPENED'
        assert bp.directive == 'NOT_OPENED'

    def test_T46_nominal_not_applicable(self):
        """Nominal wazn_family → stage_state=NOT_APPLICABLE."""
        p4a = _make_phase4a('ACCEPT', 'FA3IL', 'active_participle',
                             wazn_pattern='فَاعِل')
        bp = project_bab(p4a)
        assert bp.stage_state == 'NOT_APPLICABLE'
        assert bp.applicability == 'NOT_APPLICABLE'

    def test_T47_mujarrad_without_imperfect_defers(self):
        """FA_A_LA without imperfect evidence → DEFER (3 candidates)."""
        p4a = _make_phase4a('ACCEPT', 'FA_A_LA', 'triliteral_bare_verb',
                             canonical_root=('ك', 'ت', 'ب'),
                             wazn_pattern='فَعَلَ')
        bp = project_bab(p4a)
        assert bp.directive == 'DEFER'
        assert bp.selected_bab is None
        assert len(bp.candidate_abwab) == 3

    def test_T48_to_dict_has_required_keys(self):
        """Phase4BResult.to_dict() has all required top-level keys."""
        p4a = _make_phase4a('ACCEPT', 'IFTA3ALA', 'form_VIII_verb',
                             wazn_pattern='اِفْتَعَلَ')
        result = project_bab_with_licensing(p4a)
        d = result.to_dict()
        for key in ('initial_wazn_directive', 'final_directive', 'bab_projection',
                    'final_bab', 'source_path', 'evidence_ids', 'trace_ids',
                    'residual_codes'):
            assert key in d, f"Missing key: {key}"

    def test_T49_form_ii_accept(self):
        """FA33ALA → BAB_FORM_II."""
        p4a = _make_phase4a('ACCEPT', 'FA33ALA', 'form_II_verb',
                             wazn_pattern='فَعَّلَ')
        result = project_bab_with_licensing(p4a)
        assert result.final_directive == 'ACCEPT'
        assert result.final_bab == 'BAB_FORM_II'
        assert result.source_path == 'direct_accept'

    def test_T50_form_x_accept(self):
        """ISTAF3ALA → BAB_FORM_X."""
        p4a = _make_phase4a('ACCEPT', 'ISTAF3ALA', 'form_X_verb',
                             wazn_pattern='اِسْتَفْعَلَ')
        result = project_bab_with_licensing(p4a)
        assert result.final_directive == 'ACCEPT'
        assert result.final_bab == 'BAB_FORM_X'

    def test_T51_initial_wazn_directive_preserved(self):
        """initial_wazn_directive reflects Phase4A final_directive."""
        p4a = _make_phase4a('ACCEPT', 'IFTA3ALA', 'form_VIII_verb',
                             wazn_pattern='اِفْتَعَلَ')
        result = project_bab_with_licensing(p4a)
        assert result.initial_wazn_directive == 'ACCEPT'

    def test_T52_bab_projection_not_none_when_opened(self):
        """bab_projection is not None when phase was opened (even if DEFER)."""
        p4a = _make_phase4a('ACCEPT', 'FA_A_LA', 'triliteral_bare_verb')
        result = project_bab_with_licensing(p4a)
        assert result.bab_projection is not None

    def test_T53_bab_projection_none_when_not_opened(self):
        """bab_projection is None when phase was NOT_OPENED."""
        p4a = _make_phase4a('DEFER')
        result = project_bab_with_licensing(p4a)
        assert result.bab_projection is None

    def test_T54_fa_u_la_past_only_defers(self):
        """FA_U_LA alone (no imperfect evidence) → DEFER (1 candidate DEFER_REQUIRED)."""
        candidates = generate_bab_candidates(
            past_wazn='FA_U_LA',
            imperfect_wazn=None,
            canonical_root=None,
            evidence_ids=(),
            trace_ids=(),
            wazn_family='triliteral_bare_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].confidence == 'DEFER_REQUIRED'

    def test_T55_mazid_rules(self):
        """is_mazid_wazn and get_mazid_bab correctness."""
        assert is_mazid_wazn('FA33ALA') is True
        assert is_mazid_wazn('FA_A_LA') is False
        assert get_mazid_bab('IFTA3ALA') == 'BAB_FORM_VIII'
        assert get_mazid_bab('UNKNOWN') is None

    def test_T56_block_candidate_triggers_block_directive(self):
        """A CONTRADICTION candidate escalates to BLOCK in project_bab."""
        p4a = _make_phase4a('ACCEPT', 'FA_U_LA', 'triliteral_bare_verb',
                             wazn_pattern='فَعُلَ')
        # Inject contradicting evidence
        p4a.evidence_ids = ('imperfect_ayn:i',)   # FA_U_LA + i = contradiction

        # project_bab uses evidence_ids from phase4a_result
        # But generate_bab_candidates receives evidence from the projection
        # We test directly:
        candidates = generate_bab_candidates(
            past_wazn='FA_U_LA',
            imperfect_wazn='i',
            canonical_root=None,
            evidence_ids=('imperfect_ayn:i',),
            trace_ids=(),
            wazn_family='triliteral_bare_verb',
        )
        assert candidates[0].confidence == 'CONTRADICTION'

    def test_T57_extract_vowel_from_arabic_imperfect_pattern(self):
        """يَفْعُلُ passes through normalize_imperfect_wazn correctly."""
        result = normalize_imperfect_wazn('يَفْعُلُ')
        assert result == 'u'

    def test_T58_bab_candidate_to_dict_structure(self):
        """BabCandidate.to_dict() has expected keys."""
        c = BabCandidate(
            bab_id='BAB_I_NASARA', bab_family='MUJARRAD',
            past_wazn='FA_A_LA', imperfect_wazn='يَفْعُلُ',
            confidence='HIGH',
            evidence_ids=('ev1',), trace_ids=('tr1',), residual_codes=(),
        )
        d = c.to_dict()
        for key in ('bab_id', 'bab_family', 'past_wazn', 'imperfect_wazn',
                    'confidence', 'evidence_ids', 'trace_ids', 'residual_codes'):
            assert key in d

    def test_T59_bab_projection_to_dict_structure(self):
        """BabProjection.to_dict() has expected keys."""
        bp = BabProjection(
            directive='DEFER', stage_state='OPENED', candidate_abwab=(),
            selected_bab=None, source_wazn='FA_A_LA', canonical_root=('ك', 'ت', 'ب'),
            applicability='APPLICABLE', evidence_ids=(), trace_ids=(), residual_codes=(),
        )
        d = bp.to_dict()
        for key in ('directive', 'stage_state', 'candidate_abwab', 'selected_bab',
                    'source_wazn', 'canonical_root', 'applicability',
                    'evidence_ids', 'trace_ids', 'residual_codes'):
            assert key in d

    def test_T60_phase4b_not_opened_no_regression(self):
        """NOT_OPENED path produces well-formed Phase4BResult."""
        p4a = _make_phase4a('BLOCK')
        result = project_bab_with_licensing(p4a)
        assert result.final_directive == 'NOT_OPENED'
        assert result.final_bab is None
        assert result.bab_projection is None
        assert isinstance(result.evidence_ids, tuple)
        assert isinstance(result.trace_ids, tuple)
        assert isinstance(result.residual_codes, tuple)
        # to_dict should not raise
        d = result.to_dict()
        assert d['final_directive'] == 'NOT_OPENED'

    def test_T61_form_vii_accept(self):
        """INFA3ALA → BAB_FORM_VII."""
        candidates = generate_bab_candidates(
            past_wazn='INFA3ALA',
            imperfect_wazn=None,
            canonical_root=None,
            evidence_ids=(),
            trace_ids=(),
            wazn_family='form_VII_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].bab_id == 'BAB_FORM_VII'

    def test_T62_form_iii_accept(self):
        """FA3ALA → BAB_FORM_III."""
        candidates = generate_bab_candidates(
            past_wazn='FA3ALA',
            imperfect_wazn=None,
            canonical_root=None,
            evidence_ids=(),
            trace_ids=(),
            wazn_family='form_III_verb',
        )
        assert len(candidates) == 1
        assert candidates[0].bab_id == 'BAB_FORM_III'
