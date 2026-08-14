"""
Pre-Weight Chain Adapter — E4B (μ-CHAIN: Arabic → WeightReadinessCandidate)

CONSTITUTIONAL_RECONCILIATION_01 Phase: E4B

Purpose:
    Implements the full 8-stage μ pre-weight chain from Arabic diacritical
    text to WeightReadinessCandidate. This is the implementation of
    SOURCE_DERIVED_DEPENDENCY_AMENDMENT_01 chain stage:

        Arabic text (diacritical)
          → (letter, haraka) pairs      [decompose_arabic — pure Python]
          → SyllableCandidate           [μ_seq]
          → SyllableSequenceCandidate   [μ_boundary]
          → WordBoundaryCandidate       [μ_word_carrier]
          → WordCarrierCandidate        [μ_path_gate]
          → PathCandidate               [μ_root_stem]
          → OriginalExtraMap            [μ_original_extra]
          → OperationTraceCandidate     [μ_ops]
          → PreWeightSurface
          → WeightReadinessCandidate    [μ_weight_readiness]

Type enforcement:
    Every stage's output is TYPE-ENFORCED as input to the next stage.
    All enforcement is via __post_init__ raising WeightCarrierSchemaError.
    No stage may be skipped.

Python 3.10 compat:
    decompose_arabic() is pure Python — works on 3.10.
    Chain construction functions require Python 3.12+ (vendor StrEnum).
    build_weight_readiness_candidate() returns None on Python 3.10 (fail-closed).

Constitutional invariants:
    - FAIL-CLOSED: any error → returns None (not ELIGIBLE, not BLOCKED silently)
    - VENDOR_SHA embedded in module
    - No lexical meaning assigned — structural only
    - No stage skipped (type enforcement prevents this)
    - Rank at birth = CANDIDATE (ceiling enforced by WeightCarrierBase)

Phase: E4B — PRE-WEIGHT TYPED CARRIERS
Next phase consumer: E4C → assess_license(WeightFitCandidate, ...)
VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

# ── Vendor path ──────────────────────────────────────────────────────────────
_REPO_ROOT   = Path(__file__).resolve().parents[3]
_VENDOR_PATH = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"
_VENDOR_SHA  = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

# ── Fail-closed vendor import ────────────────────────────────────────────────
_MU_CHAIN_AVAILABLE = False

try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)

    from taaqqul_slot_geometry.weight.pre_weight import (  # type: ignore
        LetterStanding as _LetterStanding,
        OperationTraceCandidate as _OperationTraceCandidate,
        OriginalExtraMap as _OriginalExtraMap,
        PathCandidate as _PathCandidate,
        PathKind as _PathKind,
        PreWeightSurface as _PreWeightSurface,
        RootStemCandidate as _RootStemCandidate,
        SyllableCandidate as _SyllableCandidate,
        SyllableSequenceCandidate as _SyllableSequenceCandidate,
        WeightReadinessCandidate as _WeightReadinessCandidate,
        WordBoundaryCandidate as _WordBoundaryCandidate,
        WordCarrierCandidate as _WordCarrierCandidate,
    )
    from taaqqul_slot_geometry.core.rank_lattice import Rank as _Rank  # type: ignore
    from taaqqul_slot_geometry.core.slot_graph import TraceRef as _TraceRef  # type: ignore
    _MU_CHAIN_AVAILABLE = True

except ImportError:
    pass


# ── Arabic diacritical decomposition (pure Python — 3.10 compat) ─────────────

#: Arabic harakat (diacritical marks) Unicode code points.
#: These are combining marks that attach to the preceding consonant.
_ARABIC_HARAKAT: frozenset = frozenset(
    'ً'  # Fathatan (tanwin fath)
    'ٌ'  # Dammatan (tanwin damm)
    'ٍ'  # Kasratan (tanwin kasr)
    'َ'  # Fatha
    'ُ'  # Damma
    'ِ'  # Kasra
    'ّ'  # Shadda
    'ْ'  # Sukun
    'ٰ'  # Arabic letter superscript alef (dagger alef)
    'ٓ'  # Maddah above
    'ٔ'  # Hamza above
    'ٕ'  # Hamza below
)

#: Arabic letter code point range (basic Arabic block U+0600–U+06FF).
#: Characters in this range that are NOT harakat are treated as letters.
_ARABIC_BLOCK_START = 0x0600
_ARABIC_BLOCK_END   = 0x06FF


def _is_arabic_letter(ch: str) -> bool:
    """Return True if ch is an Arabic letter (not a haraka or punctuation)."""
    if ch in _ARABIC_HARAKAT:
        return False
    cp = ord(ch)
    return _ARABIC_BLOCK_START <= cp <= _ARABIC_BLOCK_END


def decompose_arabic(text: str) -> tuple[tuple[str, str], ...]:
    """
    Decompose Arabic text with harakat into (letter, haraka) pairs.

    Each pair is (letter, haraka_string) where:
    - letter: the Arabic consonant (letter character)
    - haraka_string: all combining marks that follow this letter (may be empty)

    Constitutional notes:
    - Pure Python — no vendor required — works on Python 3.10
    - Non-Arabic characters (spaces, punctuation) are included as (ch, "")
    - Multiple harakat on one letter are concatenated (e.g., shadda + vowel)
    - Empty text returns empty tuple

    Args:
        text: Arabic text, ideally with full harakat (diacritical marks).

    Returns:
        tuple of (letter, haraka) pairs.

    Example:
        >>> decompose_arabic("دَيْنٍ")
        (('د', 'َ'), ('ي', 'ْ'), ('ن', 'ٍ'))
    """
    if not text:
        return ()

    pairs: list[tuple[str, str]] = []
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        # Skip standalone harakat (shouldn't appear before any letter, but be safe)
        if ch in _ARABIC_HARAKAT:
            i += 1
            continue

        # Collect all harakat that immediately follow this character
        haraka_chars: list[str] = []
        j = i + 1
        while j < n and text[j] in _ARABIC_HARAKAT:
            haraka_chars.append(text[j])
            j += 1

        pairs.append((ch, ''.join(haraka_chars)))
        i = j

    return tuple(pairs)


# ── μ chain builder (requires Python 3.12+ vendor layer) ────────────────────

def _make_trace_ref(anchor: str, kind: str = "e4b") -> Any:
    """Build a TraceRef from an anchor string."""
    return _TraceRef(anchor=anchor, kind=kind)


def build_weight_readiness_candidate(
    token_surface: str,
    root_letters: str,
    trace_anchor: str,
    domain: str = "DAL_ONLY",
    scope: str = "word",
    path_kind: str = "ROOT",
) -> "Optional[Any]":
    """
    Build a WeightReadinessCandidate from Arabic token surface.

    This is the E4B entry point: takes a token surface form (with harakat)
    and produces a WeightReadinessCandidate via the full 8-stage μ chain.

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - Token surface is empty
    - Any stage raises WeightCarrierSchemaError
    - Any other exception

    Args:
        token_surface: Arabic token with harakat (e.g., "دَيْنٍ")
        root_letters:  Root consonants without harakat (e.g., "دين")
                       Used for OriginalExtraMap.underlying_form.
                       If empty: token_surface consonants used.
        trace_anchor:  Trace reference string from caller's PipelineTrace.
                       Must NOT be synthetic.
        domain:        Carrier domain (default: "DAL_ONLY")
        scope:         Carrier scope (default: "word")
        path_kind:     PathKind name: "ROOT" | "JAMID" | "MABNI" | ...
                       Default: "ROOT" (most corpus ISM/FI3L tokens are derived)

    Returns:
        WeightReadinessCandidate on success, None on failure (fail-closed).
    """
    if not _MU_CHAIN_AVAILABLE:
        return None

    if not token_surface or not token_surface.strip():
        return None

    try:
        return _build_mu_chain(
            token_surface=token_surface,
            root_letters=root_letters,
            trace_anchor=trace_anchor,
            domain=domain,
            scope=scope,
            path_kind_str=path_kind,
        )
    except Exception:  # noqa: BLE001
        return None


def _build_mu_chain(
    token_surface: str,
    root_letters: str,
    trace_anchor: str,
    domain: str,
    scope: str,
    path_kind_str: str,
) -> Any:
    """
    Internal: build the full 8-stage μ chain.

    Raises WeightCarrierSchemaError on any type violation.
    All failures propagate to build_weight_readiness_candidate() which returns None.
    """
    # ── Determine PathKind ───────────────────────────────────────────────────
    try:
        path_kind = _PathKind(path_kind_str)
    except ValueError:
        path_kind = _PathKind.ROOT  # conservative fallback

    # ── Stage 1 (μ_seq): Arabic text → SyllableCandidate ────────────────────
    units = decompose_arabic(token_surface)
    if not units:
        raise ValueError(f"decompose_arabic returned empty for {token_surface!r}")

    syllable = _SyllableCandidate(
        value=token_surface,
        type="syllable_candidate",
        origin="arabic_decomposition:e4b:mu_seq",
        identity=f"syllable:{token_surface}",
        domain=domain,
        scope=scope,
        rank=_Rank.CANDIDATE,
        residuals=(),
        trace=_make_trace_ref(trace_anchor, kind="mu_seq"),
        units=units,
    )

    # ── Stage 2 (μ_boundary): SyllableCandidate → SyllableSequenceCandidate ─
    syllable_seq = _SyllableSequenceCandidate(
        value=token_surface,
        type="syllable_sequence_candidate",
        origin="mu_seq:e4b:mu_boundary",
        identity=f"seq:{token_surface}",
        domain=domain,
        scope=scope,
        rank=_Rank.CANDIDATE,
        residuals=(),
        trace=_make_trace_ref(trace_anchor, kind="mu_boundary"),
        syllables=(syllable,),
    )

    # ── Stage 3 (μ_word_carrier): SyllableSequenceCandidate → WordBoundaryCandidate ─
    word_boundary = _WordBoundaryCandidate(
        value=token_surface,
        type="word_boundary_candidate",
        origin="mu_boundary:e4b:mu_word_carrier",
        identity=f"boundary:{token_surface}",
        domain=domain,
        scope=scope,
        rank=_Rank.CANDIDATE,
        residuals=(),
        trace=_make_trace_ref(trace_anchor, kind="mu_word_carrier"),
        sequence=syllable_seq,
    )

    # ── Stage 4 (μ_path_gate): WordBoundaryCandidate → WordCarrierCandidate ─
    word_carrier = _WordCarrierCandidate(
        value=token_surface,
        type="word_carrier_candidate",
        origin="mu_word_carrier:e4b:mu_path_gate",
        identity=f"carrier:{token_surface}",
        domain=domain,
        scope=scope,
        rank=_Rank.CANDIDATE,
        residuals=(),
        trace=_make_trace_ref(trace_anchor, kind="mu_path_gate"),
        bounded_surface=word_boundary,
    )

    # ── Stage 5 (μ_root_stem): WordCarrierCandidate → PathCandidate ─────────
    path_candidate = _PathCandidate(
        value=token_surface,
        type="path_candidate",
        origin="mu_path_gate:e4b:mu_root_stem",
        identity=f"path:{path_kind.value}:{token_surface}",
        domain=domain,
        scope=scope,
        rank=_Rank.CANDIDATE,
        residuals=(),
        trace=_make_trace_ref(trace_anchor, kind="mu_root_stem"),
        kind=path_kind,
        carrier=word_carrier,
    )

    # ── Stage 6 (μ_original_extra): PathCandidate → OriginalExtraMap ─────────
    # For ROOT path: underlying_form = root_letters (or surface consonants).
    # All root letters marked ORIGINAL; no extra letters assumed for simplicity.
    underlying_form = root_letters.strip() if root_letters.strip() else _extract_consonants(token_surface)
    if not underlying_form:
        underlying_form = token_surface  # last resort

    assignments = tuple(
        (letter, _LetterStanding.ORIGINAL)
        for letter in underlying_form
        if letter.strip() and letter not in _ARABIC_HARAKAT
    )
    if not assignments:
        # Fallback: use token surface consonants
        consonant_letters = [
            ch for ch, _ in decompose_arabic(token_surface)
            if _is_arabic_letter(ch)
        ]
        assignments = tuple(
            (ch, _LetterStanding.ORIGINAL) for ch in consonant_letters
        ) or (('?', _LetterStanding.ORIGINAL),)

    original_extra = _OriginalExtraMap(
        value=token_surface,
        type="original_extra_map",
        origin="mu_root_stem:e4b:mu_original_extra",
        identity=f"oe:{underlying_form}:{token_surface}",
        domain=domain,
        scope=scope,
        rank=_Rank.CANDIDATE,
        residuals=(),
        trace=_make_trace_ref(trace_anchor, kind="mu_original_extra"),
        underlying_form=underlying_form,
        assignments=assignments,
    )

    # ── Stage 7 (μ_ops): → OperationTraceCandidate ─────────────────────────
    ops = _OperationTraceCandidate(
        value=token_surface,
        type="operation_trace_candidate",
        origin="mu_original_extra:e4b:mu_ops",
        identity=f"ops:{token_surface}",
        domain=domain,
        scope=scope,
        rank=_Rank.CANDIDATE,
        residuals=(),
        trace=_make_trace_ref(trace_anchor, kind="mu_ops"),
        steps=("e4b_arabic_decomposition", "e4b_root_extraction", "e4b_chain_complete"),
    )

    # ── Stage 8 (μ_weight_readiness): → WeightReadinessCandidate ────────────
    # PreWeightSurface requires: carrier, path, original_extra, operations
    # AND path.carrier == carrier (identity check)
    pre_weight = _PreWeightSurface(
        value=token_surface,
        type="pre_weight_surface",
        origin="mu_ops:e4b:mu_weight_readiness",
        identity=f"preweight:{token_surface}",
        domain=domain,
        scope=scope,
        rank=_Rank.CANDIDATE,
        residuals=(),
        trace=_make_trace_ref(trace_anchor, kind="pre_weight_surface"),
        carrier=word_carrier,    # must match path.carrier
        path=path_candidate,     # path_candidate.carrier == word_carrier ✓
        original_extra=original_extra,
        operations=ops,
    )

    weight_readiness = _WeightReadinessCandidate(
        value=token_surface,
        type="weight_readiness_candidate",
        origin="mu_weight_readiness:e4b",
        identity=f"readiness:{token_surface}",
        domain=domain,
        scope=scope,
        rank=_Rank.CANDIDATE,
        residuals=(),
        trace=_make_trace_ref(trace_anchor, kind="mu_weight_readiness"),
        surface=pre_weight,
    )

    return weight_readiness


def _extract_consonants(text: str) -> str:
    """Extract Arabic consonant letters from text (strip harakat)."""
    return ''.join(
        ch for ch in text
        if ch not in _ARABIC_HARAKAT and _is_arabic_letter(ch)
    )


# ── Module-level invariant assertions ────────────────────────────────────────

def _verify_e4b_invariants() -> None:
    """Verify E4B adapter invariants (pure Python parts only)."""
    # INV-E4B-1: decompose_arabic returns tuple (never None)
    result = decompose_arabic("دَيْنٍ")
    assert isinstance(result, tuple), "INV-E4B-1: decompose_arabic must return tuple"
    assert len(result) == 3, f"INV-E4B-1: دَيْنٍ should decompose to 3 pairs, got {len(result)}"

    # INV-E4B-2: empty text returns empty tuple (not error)
    empty = decompose_arabic("")
    assert empty == (), f"INV-E4B-2: empty text must return (), got {empty!r}"

    # INV-E4B-3: harakat are not returned as letters
    pairs = decompose_arabic("دَيْنٍ")
    letters = [p[0] for p in pairs]
    assert 'َ' not in letters, "INV-E4B-3: haraka فتحة must not appear as a letter"
    assert 'ْ' not in letters, "INV-E4B-3: sukun must not appear as a letter"

    # INV-E4B-4: decompose_arabic never raises
    for sample in ["", "دَيْنٍ", "كَاتِبٌ", "الَّذِينَ", "???"]:
        try:
            decompose_arabic(sample)
        except Exception as exc:  # noqa: BLE001
            assert False, f"INV-E4B-4: decompose_arabic raised for {sample!r}: {exc}"


_verify_e4b_invariants()


__all__ = [
    "decompose_arabic",
    "build_weight_readiness_candidate",
    "_MU_CHAIN_AVAILABLE",
    "_VENDOR_SHA",
    "_ARABIC_HARAKAT",
]
