"""
test_segmenter.py — Tests for generic clause segmenter.

Gold data is imported from tests/evaluation/ayat_al_dayn_gold_corpus (evaluation only).
The segmenter itself is tested with generic token inputs.
"""
from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from pipeline.clause_graph.segmenter import detect_boundaries, segment_into_clauses
from tests.evaluation.ayat_al_dayn_gold_corpus import get_gold_clauses, GOLD_CLAUSES


def test_gold_clauses_not_empty():
    clauses = get_gold_clauses()
    assert len(clauses) >= 7


def test_gold_clauses_start_at_token_1():
    clauses = get_gold_clauses()
    first = clauses[0]
    assert first["token_start"] >= 1


def test_gold_clauses_have_predicates():
    clauses = get_gold_clauses()
    for c in clauses:
        assert len(c["main_predicate_candidates"]) > 0, (
            f"Clause {c['clause_id']} missing main predicate"
        )


def test_gold_clauses_have_operators():
    clauses = get_gold_clauses()
    operator_clauses = [c for c in clauses if c.get("operators")]
    assert len(operator_clauses) >= 4


def test_gold_clauses_ad_c01_is_vocative():
    clauses = get_gold_clauses()
    ad_c01 = next((c for c in clauses if c["clause_id"] == "AD-C01"), None)
    assert ad_c01 is not None
    assert "آمَنُوا" in ad_c01["main_predicate_candidates"] or "يَا" in ad_c01["operators"]


def test_generic_segmenter_detects_conjunction():
    """Generic segmenter must detect وَ as a conjunction boundary."""
    tokens = [
        {"surface": "كَتَبَ"},
        {"surface": "وَ"},
        {"surface": "قَرَأَ"},
    ]
    boundaries = detect_boundaries(tokens)
    assert len(boundaries) == 1
    assert boundaries[0].operator_surface == "وَ"


def test_generic_segmenter_detects_conditional():
    """Generic segmenter must detect إِذَا as a conditional boundary."""
    tokens = [
        {"surface": "إِذَا"},
        {"surface": "جَاءَ"},
        {"surface": "الرَّجُلُ"},
    ]
    boundaries = detect_boundaries(tokens)
    assert len(boundaries) >= 1
    cond = next((b for b in boundaries if b.operator_surface == "إِذَا"), None)
    assert cond is not None


def test_generic_segmenter_returns_clauses():
    """segment_into_clauses returns a list of ClauseCandidate."""
    tokens = [
        {"surface": "كَتَبَ"},
        {"surface": "وَ"},
        {"surface": "قَرَأَ"},
    ]
    clauses = segment_into_clauses(tokens)
    assert len(clauses) >= 1


def test_generic_segmenter_empty_input():
    """Empty token list returns empty clause list."""
    assert segment_into_clauses([]) == []


def test_segmenter_no_gold_import():
    """Verify segmenter module does not reference gold corpus constants."""
    import pipeline.clause_graph.segmenter as seg
    import inspect
    src = inspect.getsource(seg)
    assert "AYAT_AL_DAYN_GOLD_CLAUSES" not in src
    assert "build_gold_clauses" not in src
    assert "tests.evaluation" not in src
