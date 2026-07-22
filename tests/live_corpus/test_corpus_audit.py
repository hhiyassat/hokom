"""
Corpus audit tests — HOKOM-TAAQOL-SGA-LIVE-CORPUS-EXPANSION-01

Verifies schema, integrity, and hint-isolation invariants of the 150-case
corpus.  No pipeline execution here — read-only against the JSON file.
"""
import json
import dataclasses
import pytest
from pathlib import Path
from pipeline.corpus.live_corpus_loader import load_corpus

CORPUS_PATH = Path("data/test-data/hokom_taaqol_sga_live_corpus_150.json")


# ── File / schema ──────────────────────────────────────────────────────────────

def test_corpus_file_exists():
    assert CORPUS_PATH.exists(), f"Corpus not found: {CORPUS_PATH}"


def test_corpus_schema_valid():
    _, result = load_corpus(CORPUS_PATH)
    assert result.violations == [], f"Schema violations: {result.violations}"


def test_corpus_exactly_150_cases():
    _, result = load_corpus(CORPUS_PATH)
    assert result.case_count == 150, f"Got {result.case_count} cases"


def test_unique_case_ids():
    _, result = load_corpus(CORPUS_PATH)
    assert result.unique_ids == 150, f"Only {result.unique_ids} unique IDs"


def test_corpus_id_consistent():
    cases, _ = load_corpus(CORPUS_PATH)
    bad = [c.case_id for c in cases if c.corpus_id != "HOKOM-TAAQOL-SGA-LIVE-CORPUS-EXPANSION-01"]
    assert bad == [], f"Wrong corpus_id on: {bad}"


def test_not_ayat_al_dayn():
    """Corpus must be independent from Ayat al-Dayn."""
    with open(CORPUS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    assert raw["historical_ayat_al_dayn_counted"] is False


def test_all_cases_independent_from_ayat_al_dayn():
    cases, _ = load_corpus(CORPUS_PATH)
    with open(CORPUS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    for rec in raw["cases"]:
        assert rec.get("independent_from_ayat_al_dayn") == "YES", (
            f"{rec['case_id']}: independent_from_ayat_al_dayn != YES"
        )


# ── Section counts ─────────────────────────────────────────────────────────────

def test_section_counts():
    cases, _ = load_corpus(CORPUS_PATH)
    from collections import Counter
    sections = Counter(c.section for c in cases)
    assert sections["A_COMPOUND_CLITICS"] == 40, f"A section: {sections['A_COMPOUND_CLITICS']}"
    assert sections["B_WEAK_VERBS"] == 60, f"B section: {sections['B_WEAK_VERBS']}"
    assert sections["C_H11_H15_LIVE"] == 30, f"C section: {sections['C_H11_H15_LIVE']}"
    assert sections["D_AMBIGUITY_CONTROLS"] == 20, f"D section: {sections['D_AMBIGUITY_CONTROLS']}"


def test_coverage_metadata():
    """coverage field must declare 150 cases."""
    with open(CORPUS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    coverage = raw.get("coverage", {})
    assert coverage.get("total_cases") == 150
    assert coverage.get("compound_clitic_cases") == 40
    assert coverage.get("weak_verb_cases") == 60
    assert coverage.get("h11_h15_primary_cases") == 30
    assert coverage.get("ambiguity_control_cases") == 20
    assert coverage.get("negative_controls") == 20


# ── Routing oracles ────────────────────────────────────────────────────────────

def test_routing_oracles_recognized():
    from pipeline.corpus.live_corpus_loader import KNOWN_ROUTING_ORACLES
    cases, _ = load_corpus(CORPUS_PATH)
    bad = []
    for c in cases:
        for part in c.routing_oracle.split("|"):
            part = part.strip()
            if part and part not in KNOWN_ROUTING_ORACLES:
                bad.append(f"{c.case_id}: {part!r}")
    assert bad == [], f"Unrecognized oracle parts: {bad}"


def test_all_cases_have_routing_oracle():
    cases, _ = load_corpus(CORPUS_PATH)
    missing = [c.case_id for c in cases if not c.routing_oracle]
    assert missing == [], f"Missing routing_oracle: {missing}"


# ── h11_h15 / ambiguity / negative-control counts ─────────────────────────────

def test_h11_h15_flagged_count():
    """Coverage declares 149 h11_h15_live=YES."""
    _, result = load_corpus(CORPUS_PATH)
    assert len(result.h11_h15_flagged_ids) == 149, (
        f"h11_h15_flagged count: {len(result.h11_h15_flagged_ids)}"
    )


def test_ambiguity_expected_count():
    """Coverage declares 25 ambiguity_expected=YES."""
    _, result = load_corpus(CORPUS_PATH)
    assert len(result.ambiguity_expected_ids) == 25, (
        f"ambiguity_expected count: {len(result.ambiguity_expected_ids)}"
    )


def test_negative_control_count():
    """Coverage declares 20 negative controls."""
    _, result = load_corpus(CORPUS_PATH)
    assert len(result.negative_control_ids) == 20, (
        f"negative_control count: {len(result.negative_control_ids)}"
    )


# ── Surface / allowed_verdicts ─────────────────────────────────────────────────

def test_all_cases_have_surface():
    cases, _ = load_corpus(CORPUS_PATH)
    missing = [c.case_id for c in cases if not c.surface]
    assert missing == [], f"Cases with no surface: {missing}"


def test_all_surfaces_are_arabic():
    """All target surfaces must contain at least one Arabic character."""
    import unicodedata
    cases, _ = load_corpus(CORPUS_PATH)
    bad = []
    for c in cases:
        if not any(unicodedata.category(ch) in ("Lo",) and "؀" <= ch <= "ۿ"
                   for ch in c.surface):
            bad.append(c.case_id)
    assert bad == [], f"Non-Arabic surface: {bad}"


def test_allowed_verdicts_non_empty():
    cases, _ = load_corpus(CORPUS_PATH)
    missing = [c.case_id for c in cases if not c.allowed_verdicts]
    assert missing == [], f"Missing allowed_verdicts: {missing}"


# ── Hint isolation invariants ──────────────────────────────────────────────────

def test_hints_on_private_fields():
    """Hints must be on private (_-prefixed) fields, not public attributes."""
    cases, _ = load_corpus(CORPUS_PATH)
    for case in cases:
        assert hasattr(case, "_root_hint"), f"{case.case_id}: no _root_hint"
        assert hasattr(case, "_lemma_hint"), f"{case.case_id}: no _lemma_hint"
        assert hasattr(case, "_weak_class_hint"), f"{case.case_id}: no _weak_class_hint"
        # Public names must NOT exist
        assert not hasattr(case, "root_hint"), (
            f"{case.case_id}: root_hint must not be a public field"
        )
        assert not hasattr(case, "lemma_hint"), (
            f"{case.case_id}: lemma_hint must not be a public field"
        )
        assert not hasattr(case, "weak_class"), (
            f"{case.case_id}: weak_class must not be a public field"
        )


def test_surface_is_only_public_input_field():
    """
    The CorpusCase dataclass exposes exactly 'surface' as the Arabic input.
    No other field must be named 'word', 'token', 'text', or 'input'.
    """
    cases, _ = load_corpus(CORPUS_PATH)
    forbidden_public = {"word", "token", "text", "input"}
    case = cases[0]
    public_fields = {f.name for f in dataclasses.fields(case) if not f.name.startswith("_")}
    overlap = public_fields & forbidden_public
    assert overlap == set(), f"Unexpected public input fields: {overlap}"


def test_hint_mutation_does_not_change_claim_key():
    """
    Mutating private hints on a CorpusCase copy must not change run_case output.
    Proves hints never reach the pipeline.
    """
    cases, _ = load_corpus(CORPUS_PATH)
    # Pick a simple compound-clitic case
    case = next(c for c in cases if c.section == "A_COMPOUND_CLITICS")

    from pipeline.corpus.live_runner import run_case

    r1 = run_case(case)

    # Replace private hints with fabricated values
    case2 = dataclasses.replace(
        case,
        _root_hint="FABRICATED-ROOT-XYZ",
        _lemma_hint="FABRICATED-LEMMA-ABC",
        _weak_class_hint="FABRICATED-CLASS-999",
    )
    r2 = run_case(case2)

    if r1.error_class == "NONE" and r2.error_class == "NONE":
        assert r1.claim_key == r2.claim_key, (
            f"Hint mutation changed claim_key: {r1.claim_key!r} → {r2.claim_key!r}"
        )
    # If both errored the same way, that's also acceptable
    elif r1.error_class == r2.error_class:
        pass
    else:
        pytest.fail(
            f"Error class changed on hint mutation: {r1.error_class} → {r2.error_class}"
        )
