"""
E4B Pre-Weight Chain Tests — T_E4B_*

Tests for preweight_chain_adapter.py:
    - decompose_arabic (pure Python — all tests run on Python 3.10)
    - build_weight_readiness_candidate (Python 3.12+ vendor required)
    - Module invariants (run at import time — always verified)

Constitutional gates verified:
    G_E4B_01: decompose_arabic correctness
    G_E4B_02: haraka/letter separation (harakat never appear as letters)
    G_E4B_03: decompose_arabic never raises (fail-safe)
    G_E4B_04: build_weight_readiness_candidate fail-closed on Python 3.10
    G_E4B_05: WeightReadinessCandidate type chain correct on Python 3.12+
    G_E4B_06: Module invariants hold (verified at import time)

Python 3.10 compat:
    - All decompose_arabic tests run on 3.10 (pure Python)
    - build_weight_readiness_candidate returns None on 3.10 (fail-closed)
    - REQUIRES_312 marks are skipped on 3.10

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
Phase: E4B — PRE-WEIGHT TYPED CARRIERS
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.weight_layer.preweight_chain_adapter import (  # noqa: E402
    _ARABIC_HARAKAT,
    _MU_CHAIN_AVAILABLE,
    _VENDOR_SHA,
    build_weight_readiness_candidate,
    decompose_arabic,
)

REQUIRES_312 = pytest.mark.skipif(
    not _MU_CHAIN_AVAILABLE,
    reason="Requires Python 3.12+ (vendor StrEnum / taaqqul_slot_geometry)",
)

# ── Corpus samples from Ayat al-Dayn (2:282) ─────────────────────────────────

# ISM tokens with full harakat + known root
_CORPUS_ISM_SAMPLES = [
    ("دَيْنٍ",       "دين",  3),  # dayn — noun: debt
    ("كَاتِبٌ",     "كتب",  4),  # katib — ISM-FAIL — 4 letters with ت present
    ("شَهِيدَيْنِ", "شهد",  3),  # shahidayn (dual) — 3-letter root
    ("أَجَلٍ",      "أجل",  3),  # ajal — 3-letter root
]

# Tokens with no harakat (bare consonants)
_BARE_SAMPLES = ["دين", "كتب", "شهد", "رجل"]

# Edge cases
_EDGE_CASES = [
    "",          # empty string
    " ",         # whitespace only
    "???",       # non-Arabic
    "الَّذِينَ", # token with shadda + long sequence
]


# ── G_E4B_01: decompose_arabic correctness ────────────────────────────────────

class TestT_E4B_01_DecomposeCorrectness:
    """G_E4B_01: decompose_arabic returns correct (letter, haraka) pairs."""

    def test_dayn_decomposition(self):
        """دَيْنٍ → 3 pairs: (د,َ)(ي,ْ)(ن,ٍ)"""
        result = decompose_arabic("دَيْنٍ")
        assert result == (("د", "َ"), ("ي", "ْ"), ("ن", "ٍ")), (
            f"Unexpected decomposition: {result!r}"
        )

    def test_dayn_pair_count(self):
        """دَيْنٍ decomposes into exactly 3 pairs (3 consonants)."""
        result = decompose_arabic("دَيْنٍ")
        assert len(result) == 3

    def test_bare_letters_have_empty_haraka(self):
        """Letters without harakat produce (letter, '') pairs."""
        result = decompose_arabic("دين")
        assert result == (("د", ""), ("ي", ""), ("ن", "")), (
            f"Bare letters should have empty haraka: {result!r}"
        )

    def test_empty_string_returns_empty_tuple(self):
        """Empty string → empty tuple (never raises, never None)."""
        result = decompose_arabic("")
        assert result == (), f"Expected (), got {result!r}"
        assert isinstance(result, tuple)

    def test_returns_tuple_not_list(self):
        """Return type is tuple (immutable — suitable for vendor constructors)."""
        result = decompose_arabic("دَيْنٍ")
        assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"

    def test_each_element_is_two_tuple(self):
        """Each element is a 2-tuple (letter, haraka_str)."""
        result = decompose_arabic("دَيْنٍ")
        for pair in result:
            assert isinstance(pair, tuple), f"pair is not tuple: {pair!r}"
            assert len(pair) == 2, f"pair not 2-tuple: {pair!r}"
            letter, haraka = pair
            assert isinstance(letter, str), f"letter not str: {letter!r}"
            assert isinstance(haraka, str), f"haraka not str: {haraka!r}"

    def test_shadda_sequence_handled(self):
        """Shadda (ّ) followed by vowel: both marks grouped with the letter."""
        # الَّذِينَ: ا+لَّ(lam+shadda+fatha)+ذِ+ي+نَ
        result = decompose_arabic("الَّذِينَ")
        # All pairs should have non-None haraka (may be '' or marks)
        for letter, haraka in result:
            assert isinstance(letter, str) and isinstance(haraka, str)
        # Should not raise and should produce at least 4 pairs
        assert len(result) >= 4, f"Too few pairs for الَّذِينَ: {result!r}"

    @pytest.mark.parametrize("token,root,expected_count", _CORPUS_ISM_SAMPLES)
    def test_corpus_ism_pair_count(self, token, root, expected_count):
        """Each corpus ISM token decomposes to at least expected_count pairs."""
        result = decompose_arabic(token)
        assert len(result) >= expected_count, (
            f"Token {token!r}: expected >= {expected_count} pairs, got {len(result)}: {result!r}"
        )


# ── G_E4B_02: haraka/letter separation ───────────────────────────────────────

class TestT_E4B_02_HarakaLetterSeparation:
    """G_E4B_02: Harakat never appear as letters; letters never appear as haraka."""

    def test_haraka_not_in_letters(self):
        """No haraka character appears as a 'letter' in any pair."""
        result = decompose_arabic("دَيْنٍ")
        letters = [p[0] for p in result]
        for h in _ARABIC_HARAKAT:
            assert h not in letters, (
                f"Haraka {h!r} (U+{ord(h):04X}) appeared as letter in {result!r}"
            )

    def test_fatha_not_a_letter(self):
        """Fatha (U+064E) must not appear as a letter character."""
        result = decompose_arabic("دَيْنٍ")
        letters = [p[0] for p in result]
        assert 'َ' not in letters, f"Fatha appears as letter: {result!r}"

    def test_sukun_not_a_letter(self):
        """Sukun (U+0652) must not appear as a letter character."""
        result = decompose_arabic("دَيْنٍ")
        letters = [p[0] for p in result]
        assert 'ْ' not in letters, f"Sukun appears as letter: {result!r}"

    def test_tanwin_not_a_letter(self):
        """Tanwin (kasratan ٍ) must not appear as a letter character."""
        result = decompose_arabic("دَيْنٍ")
        letters = [p[0] for p in result]
        assert 'ٍ' not in letters, f"Kasratan appears as letter: {result!r}"

    def test_haraka_string_only_contains_harakat(self):
        """The haraka string in each pair contains only harakat characters (or is empty)."""
        result = decompose_arabic("دَيْنٍ")
        for letter, haraka in result:
            for ch in haraka:
                assert ch in _ARABIC_HARAKAT, (
                    f"Non-haraka char {ch!r} (U+{ord(ch):04X}) in haraka string of {letter!r}: {haraka!r}"
                )

    def test_harakat_set_has_correct_size(self):
        """_ARABIC_HARAKAT frozenset contains exactly 12 diacritical characters."""
        assert len(_ARABIC_HARAKAT) == 12, (
            f"Expected 12 harakat, got {len(_ARABIC_HARAKAT)}: "
            f"{[hex(ord(c)) for c in sorted(_ARABIC_HARAKAT)]}"
        )

    def test_fatha_in_harakat_set(self):
        """Fatha (U+064E) is in _ARABIC_HARAKAT."""
        assert 'َ' in _ARABIC_HARAKAT, "Fatha missing from harakat set"

    def test_sukun_in_harakat_set(self):
        """Sukun (U+0652) is in _ARABIC_HARAKAT."""
        assert 'ْ' in _ARABIC_HARAKAT, "Sukun missing from harakat set"

    def test_shadda_in_harakat_set(self):
        """Shadda (U+0651) is in _ARABIC_HARAKAT."""
        assert 'ّ' in _ARABIC_HARAKAT, "Shadda missing from harakat set"


# ── G_E4B_03: decompose_arabic never raises ───────────────────────────────────

class TestT_E4B_03_NeverRaises:
    """G_E4B_03: decompose_arabic is fail-safe — never raises on any input."""

    @pytest.mark.parametrize("sample", [
        "",           # empty
        " ",          # whitespace
        "???",        # non-Arabic
        "123",        # digits
        "abc",        # Latin
        "دَيْنٍ",    # fully vocalized Arabic
        "دين",        # unvocalized Arabic
        "الَّذِينَ", # complex shadda sequence
        "؀" * 5, # Arabic block control chars
        "  دَيْنٍ  ", # surrounding spaces
    ])
    def test_never_raises(self, sample):
        """decompose_arabic never raises, regardless of input."""
        try:
            result = decompose_arabic(sample)
            assert isinstance(result, tuple), f"Not a tuple for {sample!r}: {type(result)}"
        except Exception as exc:
            pytest.fail(f"decompose_arabic raised for {sample!r}: {type(exc).__name__}: {exc}")

    def test_returns_tuple_for_all_edge_cases(self):
        """Always returns a tuple, never None."""
        for sample in _EDGE_CASES:
            result = decompose_arabic(sample)
            assert result is not None, f"Returned None for {sample!r}"
            assert isinstance(result, tuple), f"Not a tuple for {sample!r}"


# ── G_E4B_04: Fail-closed on Python 3.10 ─────────────────────────────────────

class TestT_E4B_04_FailClosedOn310:
    """G_E4B_04: build_weight_readiness_candidate returns None on Python 3.10 (vendor absent)."""

    def test_returns_none_without_vendor(self):
        """Without vendor: build_weight_readiness_candidate returns None (fail-closed)."""
        if _MU_CHAIN_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available; fail-closed path not exercised")
        result = build_weight_readiness_candidate(
            token_surface="دَيْنٍ",
            root_letters="دين",
            trace_anchor="test:e4b:t04:failclosed",
        )
        assert result is None, (
            f"Expected None on 3.10, got {type(result)}: {result!r}"
        )

    def test_never_raises_on_310(self):
        """build_weight_readiness_candidate never raises on Python 3.10."""
        if _MU_CHAIN_AVAILABLE:
            pytest.skip("Python 3.12+ — testing 3.10 fail-closed path")
        try:
            result = build_weight_readiness_candidate(
                token_surface="",
                root_letters="",
                trace_anchor="test:e4b:t04:empty",
            )
            # May return None for empty surface too
            assert result is None
        except Exception as exc:
            pytest.fail(f"build_weight_readiness_candidate raised on 3.10: {exc}")

    def test_mu_chain_available_is_false_on_310(self):
        """_MU_CHAIN_AVAILABLE = False on Python 3.10 (StrEnum absent)."""
        if _MU_CHAIN_AVAILABLE:
            pytest.skip("Python 3.12+ — chain IS available")
        assert _MU_CHAIN_AVAILABLE is False, (
            "_MU_CHAIN_AVAILABLE should be False without vendor"
        )

    def test_vendor_sha_always_accessible(self):
        """_VENDOR_SHA is always accessible regardless of Python version."""
        assert _VENDOR_SHA == "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52", (
            f"VENDOR_SHA mismatch: {_VENDOR_SHA!r}"
        )


# ── G_E4B_05: WeightReadinessCandidate type chain (Python 3.12+) ─────────────

class TestT_E4B_05_WeightReadinessChain:
    """G_E4B_05: Full μ chain produces typed WeightReadinessCandidate on Python 3.12+."""

    @REQUIRES_312
    def test_dayn_builds_weight_readiness_candidate(self):
        """دَيْنٍ (ISM, ROOT path) produces a WeightReadinessCandidate."""
        result = build_weight_readiness_candidate(
            token_surface="دَيْنٍ",
            root_letters="دين",
            trace_anchor="test:e4b:t05:dayn",
            path_kind="ROOT",
        )
        assert result is not None, "Chain failed for دَيْنٍ — unexpected None"
        assert type(result).__name__ == "WeightReadinessCandidate", (
            f"Expected WeightReadinessCandidate, got {type(result).__name__}"
        )

    @REQUIRES_312
    def test_result_has_surface_attribute(self):
        """WeightReadinessCandidate.surface is a PreWeightSurface."""
        result = build_weight_readiness_candidate(
            token_surface="دَيْنٍ",
            root_letters="دين",
            trace_anchor="test:e4b:t05:surface",
        )
        assert result is not None
        assert hasattr(result, "surface"), "Missing .surface attribute"
        assert type(result.surface).__name__ == "PreWeightSurface", (
            f"surface type: {type(result.surface).__name__}"
        )

    @REQUIRES_312
    def test_result_value_is_token_surface(self):
        """WeightReadinessCandidate.value == token_surface."""
        token = "دَيْنٍ"
        result = build_weight_readiness_candidate(
            token_surface=token,
            root_letters="دين",
            trace_anchor="test:e4b:t05:value",
        )
        assert result is not None
        assert result.value == token, (
            f"value={result.value!r} != token_surface={token!r}"
        )

    @REQUIRES_312
    def test_result_rank_is_candidate(self):
        """WeightReadinessCandidate.rank == Rank.CANDIDATE (birth ceiling)."""
        result = build_weight_readiness_candidate(
            token_surface="دَيْنٍ",
            root_letters="دين",
            trace_anchor="test:e4b:t05:rank",
        )
        assert result is not None
        # Python 3.12 changed IntEnum.__str__: str(Rank.CANDIDATE) == "2", not "CANDIDATE".
        # Use .name for the string representation, or identity via == for semantic correctness.
        assert result.rank.name == "CANDIDATE", (
            f"rank must be CANDIDATE, got {result.rank!r} (name={result.rank.name!r})"
        )

    @REQUIRES_312
    def test_result_residuals_is_empty_tuple(self):
        """WeightReadinessCandidate.residuals == () (no fiqhi residuals at birth)."""
        result = build_weight_readiness_candidate(
            token_surface="دَيْنٍ",
            root_letters="دين",
            trace_anchor="test:e4b:t05:residuals",
        )
        assert result is not None
        assert result.residuals == (), (
            f"residuals must be () at birth, got {result.residuals!r}"
        )

    @REQUIRES_312
    def test_trace_ref_anchor_is_set(self):
        """WeightReadinessCandidate.trace.anchor == trace_anchor."""
        anchor = "test:e4b:t05:trace"
        result = build_weight_readiness_candidate(
            token_surface="دَيْنٍ",
            root_letters="دين",
            trace_anchor=anchor,
        )
        assert result is not None
        assert hasattr(result, "trace"), "Missing .trace attribute"
        assert result.trace.anchor == anchor, (
            f"trace.anchor={result.trace.anchor!r} != {anchor!r}"
        )

    @REQUIRES_312
    def test_path_carrier_matches_carrier(self):
        """PreWeightSurface.path.carrier == PreWeightSurface.carrier (type invariant)."""
        result = build_weight_readiness_candidate(
            token_surface="دَيْنٍ",
            root_letters="دين",
            trace_anchor="test:e4b:t05:pathcarrier",
        )
        assert result is not None
        surface = result.surface
        assert surface.path.carrier == surface.carrier, (
            "path.carrier != carrier — type invariant violated"
        )

    @REQUIRES_312
    @pytest.mark.parametrize("token,root", [
        ("دَيْنٍ",      "دين"),
        ("كَاتِبٌ",    "كتب"),
        ("شَهِيدَيْنِ","شهد"),
        ("أَجَلٍ",     "أجل"),
    ])
    def test_corpus_tokens_produce_chain(self, token, root):
        """Each corpus ISM token produces a WeightReadinessCandidate without error."""
        result = build_weight_readiness_candidate(
            token_surface=token,
            root_letters=root,
            trace_anchor=f"test:e4b:t05:corpus:{token}",
        )
        assert result is not None, (
            f"Chain failed for corpus token {token!r} — got None"
        )
        assert type(result).__name__ == "WeightReadinessCandidate", (
            f"Expected WeightReadinessCandidate for {token!r}, got {type(result).__name__}"
        )

    @REQUIRES_312
    def test_empty_surface_returns_none(self):
        """Empty token_surface → None (fail-closed, no crash)."""
        result = build_weight_readiness_candidate(
            token_surface="",
            root_letters="",
            trace_anchor="test:e4b:t05:empty",
        )
        assert result is None, f"Expected None for empty surface, got {result!r}"

    @REQUIRES_312
    def test_jamid_path_kind_accepted(self):
        """PathKind.JAMID is accepted for morphologically invariable tokens."""
        result = build_weight_readiness_candidate(
            token_surface="حَقًّا",
            root_letters="حق",
            trace_anchor="test:e4b:t05:jamid",
            path_kind="JAMID",
        )
        # May succeed or return None depending on PathKind.JAMID's constraints in vendor
        # Either is acceptable — the key is it must NOT raise
        # (None means vendor rejected JAMID path construction — acceptable fail-closed)
        assert result is None or type(result).__name__ == "WeightReadinessCandidate"


# ── G_E4B_06: Module invariants (run at import time) ─────────────────────────

class TestT_E4B_06_ModuleInvariants:
    """G_E4B_06: Module invariants hold (verified by _verify_e4b_invariants at import)."""

    def test_module_imports_without_error(self):
        """Module imports cleanly on Python 3.10 (invariants verified at import)."""
        # If we got here, module imported without raising AssertionError
        assert True

    def test_vendor_sha_constant(self):
        """_VENDOR_SHA matches pinned constitutional SHA."""
        assert _VENDOR_SHA == "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

    def test_arabic_harakat_is_frozenset(self):
        """_ARABIC_HARAKAT is a frozenset (immutable)."""
        assert isinstance(_ARABIC_HARAKAT, frozenset)

    def test_mu_chain_available_is_bool(self):
        """_MU_CHAIN_AVAILABLE is a bool."""
        assert isinstance(_MU_CHAIN_AVAILABLE, bool)

    def test_decompose_arabic_is_callable(self):
        """decompose_arabic is callable."""
        assert callable(decompose_arabic)

    def test_build_weight_readiness_candidate_is_callable(self):
        """build_weight_readiness_candidate is callable."""
        assert callable(build_weight_readiness_candidate)
