"""
Tests for two-consonant compressed imperative ambiguity.
PHASE: HOKOM-TAAQOL-SGA-CRA-TWO-CONSONANT-CANDIDATES-01

No root_hint, no lemma_hint, no ambiguity_expected used as evidence.
All assertions based solely on live pipeline output.

NOTE: build_claim_bundle() expects "word" key (via adapt_surface_identity).
      When calling with raw hokom() output, we normalise the dict via
      _hr_for_bundle() which adds "word" from "original".
"""
import pytest
import sys
sys.path.insert(0, '.')

from hokom_pipeline import hokom
from pipeline.sga.adapters import adapt_root_radicals, build_claim_bundle
from pipeline.sga.contracts import SlotState, SlotId


def _hr_for_bundle(hr: dict) -> dict:
    """Return a copy of hr with 'word' set from 'original' (required by adapt_surface_identity)."""
    out = dict(hr)
    if not out.get('word'):
        out['word'] = hr.get('original') or hr.get('input_surface', '')
    return out


# ── Positive controls: 4 confirmed defect surfaces ───────────────────────────

@pytest.mark.parametrize("surface,expected_primary_mid", [
    ("قُلْ", "و"),   # damma → WAW primary
    ("صُمْ", "و"),   # damma → WAW primary
    ("بِعْ", "ي"),   # kasra → YA primary
    ("سِرْ", "ي"),   # kasra → YA primary
])
def test_compressed_imperative_produces_two_candidates(surface, expected_primary_mid):
    """CRA must emit ≥2 candidate_radical_sequences for each compressed imperative."""
    hr = hokom(surface)
    assert isinstance(hr, dict), f"hokom({surface!r}) returned {type(hr)}"
    cra = hr.get('cra_result')
    assert cra is not None, f"cra_result is None for {surface!r}"
    cands = getattr(cra, 'candidate_radical_sequences', None)
    assert cands is not None, f"candidate_radical_sequences is None for {surface!r}"
    assert len(cands) >= 2, (
        f"Expected ≥2 candidates for {surface!r}, got {cands!r}"
    )
    # Primary middle radical must match expected
    primary_mid = cands[0][1]
    assert primary_mid == expected_primary_mid, (
        f"{surface!r}: expected primary_mid={expected_primary_mid!r}, got {primary_mid!r}"
    )
    # Each candidate must be a 3-element sequence
    for cand in cands:
        assert len(cand) == 3, f"Candidate {cand!r} is not length-3 for {surface!r}"


@pytest.mark.parametrize("surface", ["قُلْ", "صُمْ", "بِعْ", "سِرْ"])
def test_adapt_root_radicals_emits_ambiguous(surface):
    """adapt_root_radicals() must return an AMBIGUOUS R1 slot for compressed imperatives."""
    hr = hokom(surface)
    assert isinstance(hr, dict)
    r1, r2, r3, r4 = adapt_root_radicals(hr)
    assert r1.state == SlotState.AMBIGUOUS, (
        f"{surface!r}: R1 state={r1.state!r}, expected AMBIGUOUS"
    )
    assert r1.candidate_set is not None, (
        f"{surface!r}: R1.candidate_set is None"
    )
    assert len(r1.candidate_set.candidates) >= 2, (
        f"{surface!r}: R1.candidate_set has {len(r1.candidate_set.candidates)} entries, expected ≥2"
    )


@pytest.mark.parametrize("surface", ["قُلْ", "صُمْ", "بِعْ", "سِرْ"])
def test_no_first_candidate_selection(surface):
    """T-10 invariant: AMBIGUOUS slot must have selected=None."""
    hr = hokom(surface)
    assert isinstance(hr, dict)
    r1, r2, r3, r4 = adapt_root_radicals(hr)
    if r1.state == SlotState.AMBIGUOUS and r1.candidate_set:
        assert r1.candidate_set.selected is None, (
            f"{surface!r}: AMBIGUOUS R1 has selected={r1.candidate_set.selected!r} "
            f"(T-10 violation: must be None)"
        )


@pytest.mark.parametrize("surface", ["قُلْ", "صُمْ", "بِعْ", "سِرْ"])
def test_compressed_imperative_bundle_has_ambiguous_slot(surface):
    """build_claim_bundle must produce at least one AMBIGUOUS slot for compressed imperatives."""
    hr = hokom(surface)
    assert isinstance(hr, dict)
    bundle = build_claim_bundle(_hr_for_bundle(hr), "ROOT_CLAIM", "ROOT_CLAIM")
    ambiguous_slots = [s for s in bundle.typed_slots if s.state == SlotState.AMBIGUOUS]
    assert len(ambiguous_slots) >= 1, (
        f"No AMBIGUOUS slot for {surface!r}. "
        f"Slot states: {[(s.slot_id.value, s.state.value) for s in bundle.typed_slots]}"
    )


@pytest.mark.parametrize("surface", ["قُلْ", "صُمْ", "بِعْ", "سِرْ"])
def test_bundle_ambiguous_selected_is_none(surface):
    """All AMBIGUOUS slots in the bundle must have selected=None."""
    hr = hokom(surface)
    assert isinstance(hr, dict)
    bundle = build_claim_bundle(_hr_for_bundle(hr), "ROOT_CLAIM", "ROOT_CLAIM")
    for slot in bundle.typed_slots:
        if slot.state == SlotState.AMBIGUOUS:
            assert slot.candidate_set is not None
            assert slot.candidate_set.selected is None, (
                f"{surface!r}: AMBIGUOUS slot {slot.slot_id.value} has "
                f"selected={slot.candidate_set.selected!r} (T-10 violation)"
            )


@pytest.mark.parametrize("surface", ["قُلْ", "صُمْ", "بِعْ", "سِرْ"])
def test_candidate_entries_are_valid_triconsonantals(surface):
    """Each CandidateEntry value must be a 3-radical hyphen-separated string like 'ق-و-ل'."""
    hr = hokom(surface)
    assert isinstance(hr, dict)
    r1, r2, r3, r4 = adapt_root_radicals(hr)
    assert r1.state == SlotState.AMBIGUOUS
    for entry in r1.candidate_set.candidates:
        parts = entry.value.split('-')
        assert len(parts) == 3, (
            f"{surface!r}: candidate entry {entry.value!r} is not 3 parts"
        )


# ── Negative controls: must NOT trigger AMBIGUOUS root ───────────────────────

@pytest.mark.parametrize("surface", [
    "كَتَبَ",   # regular 3-consonant past tense
    "ضَرَبَ",   # regular 3-consonant past tense
])
def test_regular_verb_no_overgeneration(surface):
    """3-consonant regular verbs must not produce AMBIGUOUS root slots."""
    hr = hokom(surface)
    if not isinstance(hr, dict):
        pytest.skip(f"hokom({surface!r}) did not return dict: {hr!r}")
    r1, r2, r3, r4 = adapt_root_radicals(hr)
    assert r1.state != SlotState.AMBIGUOUS, (
        f"Overgeneration: {surface!r} produced AMBIGUOUS R1 (state={r1.state!r})"
    )


@pytest.mark.parametrize("surface", [
    "قَالَ",    # full HOLLOW past tense — 3 consonants on surface
    "بَاعَ",    # full HOLLOW past tense
])
def test_full_hollow_past_no_overgeneration(surface):
    """Full hollow past-tense forms have 3 surface consonants — no two-consonant expansion."""
    hr = hokom(surface)
    if not isinstance(hr, dict):
        pytest.skip(f"hokom({surface!r}) returned {type(hr)}")
    r1, r2, r3, r4 = adapt_root_radicals(hr)
    assert r1.state != SlotState.AMBIGUOUS, (
        f"Overgeneration: {surface!r} (full hollow) produced AMBIGUOUS R1"
    )


@pytest.mark.parametrize("surface", ["مَنْ", "مَا", "عَلَى", "فِي", "مِنْ"])
def test_operator_no_overgeneration(surface):
    """Mabni/operator forms must not produce AMBIGUOUS root slots."""
    hr = hokom(surface)
    if not isinstance(hr, dict):
        pytest.skip(f"hokom({surface!r}) returned {type(hr)}")
    r1, r2, r3, r4 = adapt_root_radicals(hr)
    assert r1.state != SlotState.AMBIGUOUS, (
        f"Overgeneration: mabni {surface!r} produced AMBIGUOUS R1 (state={r1.state!r})"
    )
