#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_root_analysis.py — Root Analysis Test Suite
═══════════════════════════════════════════════════════
PR 3.4  Hollow (أجوف) — AYN weak
PR 3.5  Defective (ناقص) — LAM weak + assimilated FA-yaiyya fix

Governing rules checked:
  ● ا/ى final → NEVER a root identity (always UnknownRadical)
  ● Past alone  → DEFER
  ● Present alone with visible و/ي LAM → ACCEPT root only, no bab/paradigm
  ● Paired past+present → ACCEPT via lexeme analysis
  ● Lafif (multiple weak positions) → DEFER
  ● Suffix (ون, وا, ي possessive) → not treated as LAM radical
  ● Functional words (عَلَى, إِلَى, مَتَى, فِي) → no ACCEPT
  ● No word-specific exceptions

Run:  pytest tests/test_root_analysis.py -v
"""

import pytest
from root_analysis import (
    extract_radicals,
    analyze_lexeme,
    UnknownRadical,
    WeaknessType,
    WeakPosition,
    EvidenceSufficiency,
    SurfaceAnalysis,
    LexemeAnalysis,
)


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _root(result) -> tuple:
    """Return (fa, ayn, lam) from a SurfaceAnalysis or LexemeAnalysis."""
    if isinstance(result, LexemeAnalysis):
        return result.root
    assert result.candidates, f"No candidates in: {result}"
    return result.candidates[0].radicals


def _decision(result) -> str:
    return result.decision


def _weakness(result) -> WeaknessType:
    if isinstance(result, LexemeAnalysis):
        return result.profile.weakness if result.profile else None
    return result.candidates[0].profile.weakness


def _has_unknown_at(radicals, pos: WeakPosition) -> bool:
    mapping = {WeakPosition.FA: 0, WeakPosition.AYN: 1, WeakPosition.LAM: 2}
    r = radicals[mapping[pos]]
    return isinstance(r, UnknownRadical)


def _unknown_candidates(radicals, pos: WeakPosition) -> frozenset:
    mapping = {WeakPosition.FA: 0, WeakPosition.AYN: 1, WeakPosition.LAM: 2}
    r = radicals[mapping[pos]]
    assert isinstance(r, UnknownRadical), f"Expected UnknownRadical at {pos}, got {r!r}"
    return r.candidates


# ══════════════════════════════════════════════════════════════════════════════
# §A  PR 3.5 — Defective (ناقص)
# ══════════════════════════════════════════════════════════════════════════════

class TestDefectivePastAlone:
    """
    دَعَا and رَمَى alone → DEFER.
    LAM is UnknownRadical{و،ي}.
    Final ا/ى is NEVER declared a root identity.
    """

    def test_daa_alone_defers(self):
        r = extract_radicals('دَعَا')
        assert _decision(r) == 'DEFER'

    def test_daa_alone_lam_unknown(self):
        r = extract_radicals('دَعَا')
        radicals = _root(r)
        assert _has_unknown_at(radicals, WeakPosition.LAM)

    def test_daa_alone_lam_candidates_are_waw_ya(self):
        r = extract_radicals('دَعَا')
        cands = _unknown_candidates(_root(r), WeakPosition.LAM)
        assert cands == frozenset({'و', 'ي'})

    def test_daa_alone_fa_is_dal(self):
        r = extract_radicals('دَعَا')
        assert _root(r)[0] == 'د'

    def test_daa_alone_ayn_is_ayn(self):
        r = extract_radicals('دَعَا')
        assert _root(r)[1] == 'ع'

    def test_daa_lam_never_alef(self):
        """LAM must not be ا (alef is a surface realisation, not a root radical)."""
        r = extract_radicals('دَعَا')
        assert _root(r)[2] != 'ا'

    def test_rama_alone_defers(self):
        r = extract_radicals('رَمَى')
        assert _decision(r) == 'DEFER'

    def test_rama_alone_lam_unknown(self):
        r = extract_radicals('رَمَى')
        assert _has_unknown_at(_root(r), WeakPosition.LAM)

    def test_rama_alone_lam_candidates_are_waw_ya(self):
        r = extract_radicals('رَمَى')
        cands = _unknown_candidates(_root(r), WeakPosition.LAM)
        assert cands == frozenset({'و', 'ي'})

    def test_rama_lam_never_alef_maqsura(self):
        """LAM must not be ى (alef maqsura is a surface realisation, not a root radical)."""
        r = extract_radicals('رَمَى')
        assert _root(r)[2] != 'ى'

    def test_rama_alef_maqsura_evidence_is_contributory_ya(self):
        """ى final provides CONTRIBUTORY evidence for ي."""
        r = extract_radicals('رَمَى')
        ev_list = r.candidates[0].evidence
        alef_maqsura_ev = [e for e in ev_list if e.source == 'ALEF_MAQSURA_FINAL']
        assert alef_maqsura_ev, "Expected ALEF_MAQSURA_FINAL evidence"
        ev = alef_maqsura_ev[0]
        assert ev.admissible is True
        assert ev.supports_claim == 'ي'
        assert ev.sufficiency == EvidenceSufficiency.CONTRIBUTORY

    def test_daa_alef_evidence_is_insufficient(self):
        """ا final provides INSUFFICIENT evidence — does not distinguish و from ي."""
        r = extract_radicals('دَعَا')
        ev_list = r.candidates[0].evidence
        alef_ev = [e for e in ev_list if e.source == 'ALEF_FINAL_PAST']
        assert alef_ev, "Expected ALEF_FINAL_PAST evidence"
        ev = alef_ev[0]
        assert ev.admissible is True
        assert ev.supports_claim is None
        assert ev.sufficiency == EvidenceSufficiency.INSUFFICIENT

    def test_defective_weakness_type(self):
        r = extract_radicals('دَعَا')
        assert _weakness(r) == WeaknessType.DEFECTIVE

    def test_defective_weak_position_lam(self):
        r = extract_radicals('دَعَا')
        assert WeakPosition.LAM in r.candidates[0].profile.weak_positions

    def test_form_type_defective_past(self):
        r = extract_radicals('دَعَا')
        assert r.form_type == 'DEFECTIVE_PAST'
        r2 = extract_radicals('رَمَى')
        assert r2.form_type == 'DEFECTIVE_PAST'


class TestDefectivePresentAlone:
    """
    يَدْعُو and يَرْمِي alone → root ACCEPT (no bab, no paradigm).
    LAM و or ي is visible → SUFFICIENT evidence.
    """

    def test_yaduu_alone_accepts(self):
        r = extract_radicals('يَدْعُو')
        assert _decision(r) == 'ACCEPT'

    def test_yaduu_root(self):
        r = extract_radicals('يَدْعُو')
        assert _root(r) == ('د', 'ع', 'و')

    def test_yaduu_lam_is_waw(self):
        r = extract_radicals('يَدْعُو')
        assert _root(r)[2] == 'و'

    def test_yaduu_no_unknown_radical(self):
        r = extract_radicals('يَدْعُو')
        assert not any(isinstance(x, UnknownRadical) for x in _root(r))

    def test_yarmi_alone_accepts(self):
        r = extract_radicals('يَرْمِي')
        assert _decision(r) == 'ACCEPT'

    def test_yarmi_root(self):
        r = extract_radicals('يَرْمِي')
        assert _root(r) == ('ر', 'م', 'ي')

    def test_yarmi_lam_is_ya(self):
        r = extract_radicals('يَرْمِي')
        assert _root(r)[2] == 'ي'

    def test_pres_defective_evidence_is_sufficient(self):
        """Visible LAM provides SUFFICIENT evidence."""
        r = extract_radicals('يَدْعُو')
        ev_list = r.candidates[0].evidence
        suf_ev = [e for e in ev_list if e.sufficiency == EvidenceSufficiency.SUFFICIENT]
        assert suf_ev, "Expected SUFFICIENT evidence for visible LAM"

    def test_defective_pres_weakness_type(self):
        r = extract_radicals('يَدْعُو')
        assert _weakness(r) == WeaknessType.DEFECTIVE

    def test_form_type_defective_present(self):
        r = extract_radicals('يَدْعُو')
        assert r.form_type == 'DEFECTIVE_PRESENT'
        r2 = extract_radicals('يَرْمِي')
        assert r2.form_type == 'DEFECTIVE_PRESENT'

    def test_yaqdu_root(self):
        r = extract_radicals('يَقْضِي')
        assert _decision(r) == 'ACCEPT'
        assert _root(r) == ('ق', 'ض', 'ي')

    def test_yasaa_root(self):
        r = extract_radicals('يَسْعَى')
        # يَسْعَى: [يَ, سْ, عَ, ى] — ى at phone[3] but ى ∉ {و,ي}
        # → doesn't match DEFECTIVE_PRESENT (ى not in WEAK_LETTERS)
        # → falls to DEFECTIVE_PAST pattern check... but that has a prefix
        # → actually: يَسْعَى = [يَ(prefix-like), سْ(sukun), عَ(fatha), ى(VL-alef-maqsura)]
        # ى ∉ WEAK_LETTERS → _detect_defective_pres returns False
        # 4 phones, no matching pattern → UNRECOGNIZED DEFER
        assert _decision(r) == 'DEFER'


class TestDefectivePairedLexeme:
    """
    دَعَا + يَدْعُو → root د ع و → ACCEPT.
    رَمَى + يَرْمِي → root ر م ي → ACCEPT.
    """

    def test_daa_yaduu_pair_accepts(self):
        r = analyze_lexeme(['دَعَا', 'يَدْعُو'])
        assert r.decision == 'ACCEPT'

    def test_daa_yaduu_root_is_d_ain_waw(self):
        r = analyze_lexeme(['دَعَا', 'يَدْعُو'])
        assert r.root == ('د', 'ع', 'و')

    def test_daa_yaduu_profile_defective(self):
        r = analyze_lexeme(['دَعَا', 'يَدْعُو'])
        assert r.profile.weakness == WeaknessType.DEFECTIVE
        assert WeakPosition.LAM in r.profile.weak_positions

    def test_rama_yarmi_pair_accepts(self):
        r = analyze_lexeme(['رَمَى', 'يَرْمِي'])
        assert r.decision == 'ACCEPT'

    def test_rama_yarmi_root_is_r_m_ya(self):
        r = analyze_lexeme(['رَمَى', 'يَرْمِي'])
        assert r.root == ('ر', 'م', 'ي')

    def test_rama_yarmi_profile_defective(self):
        r = analyze_lexeme(['رَمَى', 'يَرْمِي'])
        assert r.profile.weakness == WeaknessType.DEFECTIVE

    def test_qada_yaqdi_pair(self):
        r = analyze_lexeme(['قَضَى', 'يَقْضِي'])
        assert r.decision == 'ACCEPT'
        assert r.root == ('ق', 'ض', 'ي')

    def test_saa_yasaa_pair_defers(self):
        """سَعَى + يَسْعَى: يَسْعَى is UNRECOGNIZED (ى not in WEAK_LETTERS for pres
        pattern) → lexeme can't close LAM → DEFER."""
        r = analyze_lexeme(['سَعَى', 'يَسْعَى'])
        # يَسْعَى doesn't match DEFECTIVE_PRESENT (ى ∉ WEAK_LETTERS)
        # and يَسْعَى with [يَ,سْ,عَ,ى] fails the pres check
        # So AYN/LAM can't be confirmed from present → DEFER
        assert r.decision == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# §B  PR 3.4 — Hollow (أجوف)
# ══════════════════════════════════════════════════════════════════════════════

class TestHollowPastAlone:
    """
    قَالَ and بَاعَ alone → DEFER.
    AYN is UnknownRadical{و،ي}.
    """

    def test_qala_alone_defers(self):
        r = extract_radicals('قَالَ')
        assert _decision(r) == 'DEFER'

    def test_qala_ayn_unknown(self):
        r = extract_radicals('قَالَ')
        assert _has_unknown_at(_root(r), WeakPosition.AYN)

    def test_qala_ayn_candidates(self):
        r = extract_radicals('قَالَ')
        cands = _unknown_candidates(_root(r), WeakPosition.AYN)
        assert cands == frozenset({'و', 'ي'})

    def test_qala_fa_qaf_lam_lam(self):
        r = extract_radicals('قَالَ')
        assert _root(r)[0] == 'ق'
        assert _root(r)[2] == 'ل'

    def test_baa_alone_defers(self):
        r = extract_radicals('بَاعَ')
        assert _decision(r) == 'DEFER'

    def test_baa_ayn_unknown(self):
        r = extract_radicals('بَاعَ')
        assert _has_unknown_at(_root(r), WeakPosition.AYN)

    def test_hollow_past_weakness(self):
        r = extract_radicals('قَالَ')
        assert _weakness(r) == WeaknessType.HOLLOW

    def test_form_type_hollow_past(self):
        r = extract_radicals('قَالَ')
        assert r.form_type == 'HOLLOW_PAST'


class TestHollowPresentAlone:
    """
    يَقُولُ and يَبِيعُ alone → ACCEPT (root only, no bab, no paradigm).
    """

    def test_yaqulu_accepts(self):
        r = extract_radicals('يَقُولُ')
        assert _decision(r) == 'ACCEPT'

    def test_yaqulu_root(self):
        r = extract_radicals('يَقُولُ')
        assert _root(r) == ('ق', 'و', 'ل')

    def test_yaqulu_ayn_is_waw(self):
        r = extract_radicals('يَقُولُ')
        assert _root(r)[1] == 'و'

    def test_yabiuu_accepts(self):
        r = extract_radicals('يَبِيعُ')
        assert _decision(r) == 'ACCEPT'

    def test_yabiuu_root(self):
        r = extract_radicals('يَبِيعُ')
        assert _root(r) == ('ب', 'ي', 'ع')

    def test_hollow_pres_weakness(self):
        r = extract_radicals('يَقُولُ')
        assert _weakness(r) == WeaknessType.HOLLOW

    def test_form_type_hollow_present(self):
        r = extract_radicals('يَقُولُ')
        assert r.form_type == 'HOLLOW_PRESENT'


class TestHollowPairedLexeme:
    """
    قَالَ + يَقُولُ → root ق و ل → ACCEPT.
    بَاعَ + يَبِيعُ → root ب ي ع → ACCEPT.
    """

    def test_qala_yaqulu_pair_accepts(self):
        r = analyze_lexeme(['قَالَ', 'يَقُولُ'])
        assert r.decision == 'ACCEPT'

    def test_qala_yaqulu_root(self):
        r = analyze_lexeme(['قَالَ', 'يَقُولُ'])
        assert r.root == ('ق', 'و', 'ل')

    def test_qala_yaqulu_profile_hollow(self):
        r = analyze_lexeme(['قَالَ', 'يَقُولُ'])
        assert r.profile.weakness == WeaknessType.HOLLOW
        assert WeakPosition.AYN in r.profile.weak_positions

    def test_baa_yabiuu_pair_accepts(self):
        r = analyze_lexeme(['بَاعَ', 'يَبِيعُ'])
        assert r.decision == 'ACCEPT'

    def test_baa_yabiuu_root(self):
        r = analyze_lexeme(['بَاعَ', 'يَبِيعُ'])
        assert r.root == ('ب', 'ي', 'ع')


# ══════════════════════════════════════════════════════════════════════════════
# §C  PR 3.4 standalone fix — Assimilated FA-yaiyya (فاء يائية ظاهرة)
# ══════════════════════════════════════════════════════════════════════════════

class TestAssimilatedFaYai:
    """
    يَئِسَ → root ي ء س, weakness=ASSIMILATED, hamza_position='AYN' → ACCEPT.
    يَبِسَ → root ي ب س, weakness=ASSIMILATED → ACCEPT.
    يَ here is FA of the root, NOT a mudaric prefix.
    """

    def test_yaisa_accepts(self):
        r = extract_radicals('يَئِسَ')
        assert _decision(r) == 'ACCEPT'

    def test_yaisa_root(self):
        r = extract_radicals('يَئِسَ')
        # After normalize_hamza: ئ → ء
        assert _root(r) == ('ي', 'ء', 'س')

    def test_yaisa_weakness_assimilated(self):
        r = extract_radicals('يَئِسَ')
        assert _weakness(r) == WeaknessType.ASSIMILATED

    def test_yaisa_hamza_position_ayn(self):
        r = extract_radicals('يَئِسَ')
        assert r.candidates[0].profile.hamza_position == 'AYN'

    def test_yaisa_fa_position_weak(self):
        r = extract_radicals('يَئِسَ')
        assert WeakPosition.FA in r.candidates[0].profile.weak_positions

    def test_yabisa_accepts(self):
        r = extract_radicals('يَبِسَ')
        assert _decision(r) == 'ACCEPT'

    def test_yabisa_root(self):
        r = extract_radicals('يَبِسَ')
        assert _root(r) == ('ي', 'ب', 'س')

    def test_yabisa_weakness_assimilated(self):
        r = extract_radicals('يَبِسَ')
        assert _weakness(r) == WeaknessType.ASSIMILATED

    def test_yabisa_no_hamza_position(self):
        r = extract_radicals('يَبِسَ')
        assert r.candidates[0].profile.hamza_position is None

    def test_form_type_assimilated_past(self):
        r = extract_radicals('يَئِسَ')
        assert r.form_type == 'ASSIMILATED_PAST_FA_YAI'


# ══════════════════════════════════════════════════════════════════════════════
# §D  Lafif detection — DEFER to PR 3.6
# ══════════════════════════════════════════════════════════════════════════════

class TestLafif:
    """
    Lafif (multiple weak positions) must be detected and DEFERRED.
    Never reduced to a simple defective or hollow root.
    """

    def test_waqa_lafif_defers(self):
        """وَقَى: FA=و (weak) + LAM=? (VL) → LAFIF DEFER."""
        r = extract_radicals('وَقَى')
        assert _decision(r) == 'DEFER'
        assert r.candidates[0].profile.weakness == WeaknessType.LAFIF

    def test_tawa_lafif_defers(self):
        """طَوَى: AYN=و (consonantal, weak) + LAM=? (VL) → LAFIF DEFER."""
        r = extract_radicals('طَوَى')
        assert _decision(r) == 'DEFER'
        assert r.candidates[0].profile.weakness == WeaknessType.LAFIF

    def test_rawa_lafif_defers(self):
        """رَوَى: AYN=و (consonantal, weak) + LAM=? (VL) → LAFIF DEFER."""
        r = extract_radicals('رَوَى')
        assert _decision(r) == 'DEFER'
        assert r.candidates[0].profile.weakness == WeaknessType.LAFIF

    def test_wafa_lafif_defers(self):
        """وَفَى: FA=و (weak) + LAM=? (VL) → LAFIF DEFER."""
        r = extract_radicals('وَفَى')
        assert _decision(r) == 'DEFER'
        assert r.candidates[0].profile.weakness == WeaknessType.LAFIF

    def test_lafif_residual_code(self):
        r = extract_radicals('وَقَى')
        assert 'defer:root:lafif_multiple_weak_positions' in r.residuals

    def test_lafif_lexeme_also_defers(self):
        """Even with paired forms, lafif is not resolved in PR 3.5."""
        r = analyze_lexeme(['وَقَى', 'يَقِي'])
        assert r.decision == 'DEFER'
        assert 'defer:root:lafif_multiple_weak_positions' in r.residuals


# ══════════════════════════════════════════════════════════════════════════════
# §E  Suffix guards — و/ي as suffix ≠ LAM radical
# ══════════════════════════════════════════════════════════════════════════════

class TestSuffixGuards:
    """
    Suffixes (ون, وا, ي possessive) must not be confused with LAM radical.
    """

    def test_yadribuun_not_defective(self):
        """يَضْرِبُونَ: 6 phones — و followed by نَ → not defective."""
        r = extract_radicals('يَضْرِبُونَ')
        assert _decision(r) == 'DEFER'
        # Must not produce root ض ر و
        cands = r.candidates[0].radicals
        if cands != (None, None, None):
            assert cands[2] != 'و', "و in ونَ suffix must not be declared LAM radical"

    def test_yaktubuu_not_defective(self):
        """يَكْتُبُوا: P4 BLOCKS it, but if it reached root analysis → not defective.
        Surface is 6 phones — no 4-phone defective pattern match."""
        r = extract_radicals('يَكْتُبُوا')
        assert _decision(r) == 'DEFER'

    def test_kitabi_not_defective(self):
        """كِتَابِي: 5 phones (2 VLs) — does not match any 3/4-phone pattern."""
        r = extract_radicals('كِتَابِي')
        assert _decision(r) == 'DEFER'

    def test_yaduu_with_nun_not_defective(self):
        """يَدْعُونَ: 5 phones — و followed by نَ → not a defective present."""
        r = extract_radicals('يَدْعُونَ')
        assert _decision(r) == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# §F  Functional word guards — no accepted defective root
# ══════════════════════════════════════════════════════════════════════════════

class TestFunctionalWordGuards:
    """
    Functional surfaces must not produce ACCEPT.
    Until the Internal Boundary Layer (PR 3.6.5) is implemented, they
    receive DEFER (not ACCEPT, not REJECT).
    """

    def test_ala_not_accept(self):
        r = extract_radicals('عَلَى')
        assert _decision(r) != 'ACCEPT'

    def test_ila_not_accept(self):
        r = extract_radicals('إِلَى')
        assert _decision(r) != 'ACCEPT'

    def test_mata_not_accept(self):
        r = extract_radicals('مَتَى')
        assert _decision(r) != 'ACCEPT'

    def test_fi_not_accept(self):
        r = extract_radicals('فِي')
        assert _decision(r) != 'ACCEPT'

    def test_hiya_not_accept(self):
        r = extract_radicals('هِيَ')
        assert _decision(r) != 'ACCEPT'

    def test_huwa_not_accept(self):
        r = extract_radicals('هُوَ')
        assert _decision(r) != 'ACCEPT'


# ══════════════════════════════════════════════════════════════════════════════
# §G  Root identity invariants — ا/ى are never root consonants
# ══════════════════════════════════════════════════════════════════════════════

class TestRootIdentityInvariants:
    """
    Core invariants that must hold in all outputs.
    """

    def test_daa_root_never_dal_ayn_alef(self):
        """دَعَا root must never be ('د','ع','ا')."""
        r = extract_radicals('دَعَا')
        radicals = _root(r)
        assert radicals != ('د', 'ع', 'ا'), "ا must not appear as root identity"

    def test_daa_lam_never_alef(self):
        r = extract_radicals('دَعَا')
        assert _root(r)[2] != 'ا'

    def test_rama_root_never_ra_mim_alef_maqsura(self):
        """رَمَى root must never be ('ر','م','ى')."""
        r = extract_radicals('رَمَى')
        radicals = _root(r)
        assert radicals != ('ر', 'م', 'ى'), "ى must not appear as root identity"

    def test_rama_lam_never_alef_maqsura(self):
        r = extract_radicals('رَمَى')
        assert _root(r)[2] != 'ى'

    @pytest.mark.parametrize("surface", ['دَعَا', 'رَمَى', 'قَضَى', 'سَعَى'])
    def test_past_defective_lam_never_final_surface_char(self, surface):
        """For any defective past form, LAM must be UnknownRadical, not the surface ا/ى."""
        r = extract_radicals(surface)
        if r.decision == 'DEFER' and r.form_type == 'DEFECTIVE_PAST':
            lam = _root(r)[2]
            assert isinstance(lam, UnknownRadical), \
                f"LAM should be UnknownRadical for {surface}, got {lam!r}"
            assert lam.candidates == frozenset({'و', 'ي'})


# ══════════════════════════════════════════════════════════════════════════════
# §H  Serialisation (JSON contract)
# ══════════════════════════════════════════════════════════════════════════════

class TestSerialisation:
    """Output must be JSON-serialisable via to_dict()."""

    def test_surface_analysis_to_dict(self):
        import json
        r = extract_radicals('دَعَا')
        d = r.to_dict()
        # Must not raise
        json.dumps(d, ensure_ascii=False)

    def test_lexeme_analysis_to_dict(self):
        import json
        r = analyze_lexeme(['دَعَا', 'يَدْعُو'])
        d = r.to_dict()
        json.dumps(d, ensure_ascii=False)

    def test_unknown_radical_in_dict_has_candidates(self):
        r = extract_radicals('دَعَا')
        d = r.to_dict()
        lam = d['candidates'][0]['radicals'][2]
        assert lam['type'] == 'UnknownRadical'
        assert set(lam['candidates']) == {'و', 'ي'}

    def test_accepted_lexeme_dict_has_string_root(self):
        import json
        r = analyze_lexeme(['دَعَا', 'يَدْعُو'])
        d = r.to_dict()
        assert d['root'] == ['د', 'ع', 'و']
        assert d['decision'] == 'ACCEPT'


# ══════════════════════════════════════════════════════════════════════════════
# §I  Residuals are populated on DEFER
# ══════════════════════════════════════════════════════════════════════════════

class TestResiduals:

    def test_defective_past_has_residual(self):
        r = extract_radicals('دَعَا')
        assert r.residuals
        assert 'defer:root:defective_final_radical_unresolved' in r.residuals

    def test_hollow_past_has_residual(self):
        r = extract_radicals('قَالَ')
        assert r.residuals
        assert 'defer:root:hollow_medial_radical_unresolved' in r.residuals

    def test_accepted_root_has_empty_residuals(self):
        r = extract_radicals('يَدْعُو')
        assert r.residuals == []

    def test_accepted_lexeme_has_empty_residuals(self):
        r = analyze_lexeme(['دَعَا', 'يَدْعُو'])
        assert r.residuals == []

    def test_lafif_has_correct_residual(self):
        r = extract_radicals('وَقَى')
        assert 'defer:root:lafif_multiple_weak_positions' in r.residuals


# ══════════════════════════════════════════════════════════════════════════════
# §J  PR 3.7-A  Boundary gate integration
# ══════════════════════════════════════════════════════════════════════════════

class TestBoundaryGateIntegration:
    """
    PR 3.7-A: assess_boundary() is called before _FORM_DETECTORS.

    BLOCK decision:
      • Root stage not opened — decision='BLOCK', not 'DEFER'
      • candidates list is empty (form detectors never ran)
      • root_path_directive == 'BLOCK'
      • boundary_kind matches the inventory classification

    Distinction: BLOCK ≠ DEFER.
      DEFER means the root engine ran but could not close.
      BLOCK means the root engine was not entered at all.
    """

    # ── Closed function words → BLOCK ────────────────────────────────────────

    @pytest.mark.parametrize("surface", [
        "مِنْ", "هَلْ", "لَمْ", "لَنْ", "فِي", "هُوَ", "هِيَ",
    ])
    def test_closed_function_word_decision_is_block(self, surface):
        r = extract_radicals(surface)
        assert r.decision == 'BLOCK', (
            f"{surface}: expected BLOCK (boundary blocked root path), got {r.decision}"
        )

    @pytest.mark.parametrize("surface", [
        "مِنْ", "هَلْ", "لَمْ", "لَنْ", "فِي", "هُوَ", "هِيَ",
    ])
    def test_closed_function_word_candidates_empty(self, surface):
        r = extract_radicals(surface)
        assert r.candidates == [], (
            f"{surface}: form detectors must not run when boundary blocks; got candidates={r.candidates}"
        )

    @pytest.mark.parametrize("surface", [
        "مِنْ", "هَلْ", "فِي",
    ])
    def test_closed_function_word_boundary_kind(self, surface):
        r = extract_radicals(surface)
        assert r.boundary_kind == 'CLOSED_FUNCTION_WORD'
        assert r.root_path_directive == 'BLOCK'

    # ── Possible function words → DEFER (not BLOCK) ─────────────────────────
    # PR 3.7-fix: POSSIBLE_FUNCTION_WORD is not inventory-confirmed closed;
    # the path is acknowledged (DEFER) not hard-blocked (BLOCK).

    @pytest.mark.parametrize("surface", ["عَلَى", "إِلَى", "مَتَى"])
    def test_possible_function_word_decision_is_defer(self, surface):
        """POSSIBLE_FUNCTION_WORD → decision=DEFER, root_path_directive=DEFER."""
        r = extract_radicals(surface)
        assert r.decision == 'DEFER'
        assert r.root_path_directive == 'DEFER'
        assert r.boundary_kind == 'POSSIBLE_FUNCTION_WORD'

    def test_mata_does_not_enter_defective_detector(self):
        """مَتَى would match _detect_defective_past structurally but boundary intercepts first."""
        r = extract_radicals('مَتَى')
        assert r.decision == 'DEFER'
        assert r.form_type == 'BOUNDARY_DEFERRED'   # DEFER form type, not BLOCKED
        assert r.candidates == []

    # ── Ambiguous surfaces → DEFER (not BLOCK) ───────────────────────────────
    # PR 3.7-fix: structural ambiguity ≠ structural impossibility.
    # BLOCK only for inventory-confirmed closed words.

    @pytest.mark.parametrize("surface", ["تَقِي", "يَقِي"])
    def test_ambiguous_prefix_form_is_defer(self, surface):
        """تَقِي/يَقِي are structurally ambiguous; path is DEFER not BLOCK."""
        r = extract_radicals(surface)
        assert r.decision == 'DEFER'
        assert r.root_path_directive == 'DEFER'
        assert r.boundary_kind == 'AMBIGUOUS'

    # ── BLOCK ≠ DEFER: decision values are semantically distinct ─────────────

    def test_block_is_distinct_from_defer(self):
        blocked = extract_radicals('مِنْ')
        deferred = extract_radicals('دَعَا')
        assert blocked.decision == 'BLOCK'
        assert deferred.decision == 'DEFER'
        assert blocked.decision != deferred.decision

    def test_root_eligible_surfaces_not_blocked(self):
        for surface in ['ضَرَبَ', 'قَالَ', 'دَعَا', 'وَقَى']:
            r = extract_radicals(surface)
            assert r.decision != 'BLOCK', f"{surface} must not be BLOCK"
            assert r.root_path_directive == 'OPEN'

    def test_ambiguous_surfaces_not_blocked(self):
        """تَقِي/يَقِي must not receive BLOCK — structural ambiguity ≠ structural impossibility."""
        for surface in ['تَقِي', 'يَقِي']:
            r = extract_radicals(surface)
            assert r.decision != 'BLOCK', (
                f"{surface}: BLOCK requires inventory-confirmed closure; got decision={r.decision}"
            )

    def test_three_way_distinction_preserved(self):
        """BLOCK ≠ DEFER ≠ OPEN — all three must be distinct in practice."""
        blocked  = extract_radicals('مِنْ')    # CLOSED_FUNCTION_WORD → BLOCK
        deferred = extract_radicals('تَقِي')   # AMBIGUOUS → DEFER
        opened   = extract_radicals('دَعَا')   # ROOT_ELIGIBLE → OPEN / DEFER from root engine
        assert blocked.decision  == 'BLOCK'
        assert deferred.decision == 'DEFER'
        assert deferred.root_path_directive == 'DEFER'
        assert opened.root_path_directive   == 'OPEN'
        assert blocked.root_path_directive  == 'BLOCK'

    # ── to_dict includes boundary fields when present ─────────────────────────

    def test_block_to_dict_has_boundary_fields(self):
        r = extract_radicals('مِنْ')
        d = r.to_dict()
        assert d['decision'] == 'BLOCK'
        assert d['root_path_directive'] == 'BLOCK'
        assert d['boundary_kind'] == 'CLOSED_FUNCTION_WORD'

    def test_defer_to_dict_has_boundary_fields(self):
        r = extract_radicals('تَقِي')
        d = r.to_dict()
        assert d['decision'] == 'DEFER'
        assert d['root_path_directive'] == 'DEFER'
        assert d['boundary_kind'] == 'AMBIGUOUS'

    def test_open_to_dict_has_boundary_fields(self):
        r = extract_radicals('دَعَا')
        d = r.to_dict()
        assert d.get('root_path_directive') == 'OPEN'
        assert d.get('boundary_kind') == 'ROOT_ELIGIBLE'

    # ── Additional cases from PR 3.7-fix spec ────────────────────────────────

    @pytest.mark.parametrize("surface", ["تَقِي", "يَقِي"])
    def test_ambiguous_prefix_form_is_boundary_deferred(self, surface):
        r = extract_radicals(surface)
        assert r.form_type == 'BOUNDARY_DEFERRED'
        assert r.candidates == []
        assert 'defer:root:ambiguous_prefix_form' in r.residuals

    @pytest.mark.parametrize("surface", ["عَلَى", "إِلَى", "مَتَى"])
    def test_possible_function_word_is_boundary_deferred(self, surface):
        r = extract_radicals(surface)
        assert r.form_type == 'BOUNDARY_DEFERRED'
        assert r.candidates == []
        assert 'defer:root:possible_function_word' in r.residuals


# ══════════════════════════════════════════════════════════════════════════════
# §K  PR 3.7-B  Compressed-form detector
# ══════════════════════════════════════════════════════════════════════════════

class TestCompressedFormDetector:
    """
    PR 3.7-B: COMPRESSED_VERB_CANDIDATE surfaces open the root path but
    cannot close it from the surface alone.

    Rules:
      • decision = DEFER (root engine opened, but radical unknown)
      • Two visible radicals extracted at FA and LAM positions
      • AYN = UnknownRadical with candidates=frozenset() (elided radical not invented)
      • residual = 'defer:root:compressed_form_unknown_medial_radical'
      • form_type = 'COMPRESSED_VERB_CANDIDATE'
      • boundary_kind = 'COMPRESSED_VERB_CANDIDATE'
      • root_path_directive = 'OPEN'

    Governing constraint:
      لا يُرفع الحرف المحذوف إلى هوية جذرية من السطح وحده.
    """

    COMPRESSED_SURFACES = ["قُلْ", "قِفْ", "عِدْ", "زِنْ"]

    @pytest.mark.parametrize("surface", COMPRESSED_SURFACES)
    def test_decision_is_defer(self, surface):
        """Compressed verbs open the root path but cannot close it without a paired form."""
        r = extract_radicals(surface)
        assert r.decision == 'DEFER'

    @pytest.mark.parametrize("surface", COMPRESSED_SURFACES)
    def test_form_type_is_compressed(self, surface):
        r = extract_radicals(surface)
        assert r.form_type == 'COMPRESSED_VERB_CANDIDATE'

    @pytest.mark.parametrize("surface", COMPRESSED_SURFACES)
    def test_root_path_is_open(self, surface):
        r = extract_radicals(surface)
        assert r.root_path_directive == 'OPEN'
        assert r.boundary_kind == 'COMPRESSED_VERB_CANDIDATE'

    @pytest.mark.parametrize("surface", COMPRESSED_SURFACES)
    def test_has_one_candidate(self, surface):
        r = extract_radicals(surface)
        assert len(r.candidates) == 1

    @pytest.mark.parametrize("surface", COMPRESSED_SURFACES)
    def test_residual_compressed(self, surface):
        r = extract_radicals(surface)
        assert 'defer:root:compressed_form_unknown_medial_radical' in r.residuals

    def test_qul_visible_radicals_fa_and_lam(self):
        """قُلْ: FA=ق, LAM=ل visible; AYN = UnknownRadical (elided و not asserted)."""
        from root_analysis import UnknownRadical
        r = extract_radicals('قُلْ')
        rads = r.candidates[0].radicals
        assert rads[0] == 'ق', f"FA should be ق, got {rads[0]}"
        assert isinstance(rads[1], UnknownRadical), f"AYN should be UnknownRadical, got {rads[1]}"
        assert rads[2] == 'ل', f"LAM should be ل, got {rads[2]}"

    def test_qid_visible_radicals(self):
        """عِدْ: FA=ع, LAM=د visible; AYN = UnknownRadical (elided و not asserted)."""
        from root_analysis import UnknownRadical
        r = extract_radicals('عِدْ')
        rads = r.candidates[0].radicals
        assert rads[0] == 'ع'
        assert isinstance(rads[1], UnknownRadical)
        assert rads[2] == 'د'

    def test_unknown_ayn_candidates_empty(self):
        """The elided radical must NOT be guessed — candidates must be empty frozenset."""
        from root_analysis import UnknownRadical
        r = extract_radicals('قُلْ')
        unknown = r.candidates[0].radicals[1]
        assert isinstance(unknown, UnknownRadical)
        assert unknown.candidates == frozenset(), (
            "Elided radical must not be asserted from surface alone — candidates must be empty"
        )

    def test_compressed_not_accept(self):
        """No compressed surface may return ACCEPT — root cannot be closed from surface alone."""
        for surface in self.COMPRESSED_SURFACES:
            r = extract_radicals(surface)
            assert r.decision != 'ACCEPT', (
                f"{surface}: compressed surface must not ACCEPT — "
                "elided radical not recoverable from surface alone"
            )

    def test_compressed_serializable(self):
        """to_dict() must not raise — UnknownRadical must serialize."""
        import json
        r = extract_radicals('قُلْ')
        d = r.to_dict()
        # Verify it round-trips through JSON
        json.dumps(d)
        # Verify boundary fields present
        assert d['decision'] == 'DEFER'
        assert d['boundary_kind'] == 'COMPRESSED_VERB_CANDIDATE'
