"""
tests/canonical/test_sentence_corpus.py — Sentence geometry corpus validation.

Tests against HOKOM-SALEH-TAAQOL-SENTENCE-GEOMETRY-CORPUS-01:
    30 cases across sections A(10)/B(10)/C(5)/D(5)

Tests:
    01 — Corpus loads and has exactly 30 cases
    02 — Section A (10 cases): all single-word, P9 expected DEFERRED
    03 — Section B (10 cases): two-word sentences, P9 expected SAHIH
    04 — Section C (5 cases): complex sentences, P9 SAHIH
    05 — Section D (5 cases): function words, P3 expected BATIL
    06 — Section A: SentenceGeometryAdapter DEFERS on single-unit input
    07 — Section B-001: SentenceGeometryAdapter SAHIH on 2-unit input
    08 — Section D: RootStemAdapter BATIL on ROOT_PATH_BLOCKED
    09 — All case_ids unique
    10 — All cases have required fields: case_id, section, surface, expected
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from hokom.canonical.stages.base import StageInput, TaaqolLicenseOutcome

_MOCK_LICENSED = TaaqolLicenseOutcome(
    granted_rank=4,
    gate_id="TEST-GATE-LICENSED",
    verdict="LICENSED",
    fallback_used=False,
    trace_ids=("test:mock-trace-001",),
    slot_graph_digest="",
    failure_code=None,
)


# ── Corpus path discovery ─────────────────────────────────────────────────────

def _find_corpus_path() -> Path:
    candidate = Path(__file__).resolve()
    for _ in range(6):
        candidate = candidate.parent
        if (candidate / "pyproject.toml").exists():
            corpus_path = (
                candidate / "data" / "sentence-corpus" /
                "hokom_saleh_taaqol_sentence_geometry_corpus.json"
            )
            if corpus_path.exists():
                return corpus_path
    raise FileNotFoundError(
        "Sentence geometry corpus not found. "
        "Expected at data/sentence-corpus/"
        "hokom_saleh_taaqol_sentence_geometry_corpus.json"
    )


@pytest.fixture(scope="module")
def corpus():
    path = _find_corpus_path()
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cases(corpus):
    return corpus["cases"]


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_01_corpus_loads_30_cases(corpus, cases):
    assert corpus["corpus_id"] == "HOKOM-SALEH-TAAQOL-SENTENCE-GEOMETRY-CORPUS-01"
    assert corpus["total_cases"] == 30
    assert len(cases) == 30


def test_02_section_a_10_single_word_defers_p9(cases):
    section_a = [c for c in cases if c["section"] == "A_single_word_defers_at_p9"]
    assert len(section_a) == 10
    for c in section_a:
        expected = c.get("expected", {})
        p9_exp = expected.get("P9_SENTENCE_GEOMETRY")
        assert p9_exp == "deferred", (
            f"Case {c['case_id']}: P9 expected 'deferred', got '{p9_exp}'"
        )


def test_03_section_b_10_two_word_sahih_p9(cases):
    section_b = [c for c in cases if c["section"] == "B_two_word_sentences"]
    assert len(section_b) == 10
    for c in section_b:
        expected = c.get("expected", {})
        p9_exp = expected.get("P9_SENTENCE_GEOMETRY")
        assert p9_exp == "sahih", (
            f"Case {c['case_id']}: P9 expected 'sahih', got '{p9_exp}'"
        )


def test_04_section_c_5_complex_sahih_p9(cases):
    section_c = [c for c in cases if c["section"] == "C_complex_sentences"]
    assert len(section_c) == 5
    for c in section_c:
        expected = c.get("expected", {})
        p9_exp = expected.get("P9_SENTENCE_GEOMETRY")
        assert p9_exp == "sahih", (
            f"Case {c['case_id']}: P9 expected 'sahih', got '{p9_exp}'"
        )


def test_05_section_d_5_function_words_batil_p3(cases):
    section_d = [c for c in cases if c["section"] == "D_function_words"]
    assert len(section_d) == 5
    for c in section_d:
        expected = c.get("expected", {})
        p3_exp = expected.get("P3_ROOT_STEM_CLOSURE")
        assert p3_exp == "batil", (
            f"Case {c['case_id']}: P3 expected 'batil', got '{p3_exp}'"
        )
        p3_blocker = c.get("expected_p3_blocker")
        assert p3_blocker == "root_path_blocked", (
            f"Case {c['case_id']}: expected_p3_blocker should be 'root_path_blocked', "
            f"got '{p3_blocker}'"
        )


def test_06_section_a_p9_defers_on_single_unit(cases):
    """Live test: SentenceGeometryAdapter DEFERs when only 1 unit provided."""
    from hokom.canonical.stages.p9_p12 import SentenceGeometryAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = SentenceGeometryAdapter()
    section_a = [c for c in cases if c["section"] == "A_single_word_defers_at_p9"]

    for case in section_a[:3]:  # test first 3 to keep test fast
        sent_ev = case.get("sentence_evidence", {}).get("P9_SENTENCE_GEOMETRY", {})
        inp = StageInput(
            layer_id="P9_SENTENCE_GEOMETRY",
            surface=case["surface"],
            hokom_evidence=sent_ev,
            prior_output=None,
            pipeline_run_id="corpus-test",
            word_index=None,
        )
        out = adapter.adapt(inp)
        assert out.judgment.status is ConstitutionalStatus.DEFERRED, (
            f"Case {case['case_id']}: expected DEFERRED, got {out.judgment.status}"
        )


def test_07_section_b_001_p9_sahih(cases):
    """Live test: SGC-B-001 produces SAHIH at P9."""
    from hokom.canonical.stages.p9_p12 import SentenceGeometryAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus
    from hokom.canonical.slot_algebra.types import (
        CanonicalCandidate, CanonicalCandidateSet, CandidateStatus,
        EvidenceAtom, EvidenceSet, ProvenanceRef,
    )

    case = next(c for c in cases if c["case_id"] == "SGC-B-001")
    sent_ev = case["sentence_evidence"]["P9_SENTENCE_GEOMETRY"]

    prov = ProvenanceRef(owner="hokom", module_path="m", rule_id="r", stage_id="P8_AMIL_MAMUL")
    atom = EvidenceAtom(key="k", value="v", confidence=0.9, provenance=prov)
    ev = EvidenceSet.from_atoms("P8_AMIL_MAMUL", (atom,))
    c_cand = CanonicalCandidate(
        candidate_id="C1", candidate_type="AmilMamulCandidate",
        status=CandidateStatus.ACCEPTED, layer_id="P8_AMIL_MAMUL",
        source_rule_id="r", evidence=ev, taaqol_rank=4,
    )
    prior = CanonicalCandidateSet(
        set_id="S1", layer_id="P8_AMIL_MAMUL",
        candidates=(c_cand,), residuals=(), trace_ids=()
    )

    adapter = SentenceGeometryAdapter()
    inp = StageInput(
        layer_id="P9_SENTENCE_GEOMETRY",
        surface=case["surface"],
        hokom_evidence=sent_ev,
        prior_output=prior,
        pipeline_run_id="corpus-test",
        word_index=None,
    )
    with patch.object(adapter, "_taaqol_license", return_value=_MOCK_LICENSED):
        out = adapter.adapt(inp)
    assert out.judgment.status is ConstitutionalStatus.SAHIH


def test_08_section_d_p3_batil_root_path_blocked(cases):
    """Live test: Section D function words produce BATIL at P3."""
    from hokom.canonical.stages.p2_p5 import RootStemAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = RootStemAdapter()
    section_d = [c for c in cases if c["section"] == "D_function_words"]

    for case in section_d:
        p3_ev = case.get("hokom_evidence", {}).get("P3_ROOT_STEM_CLOSURE", {})
        if not p3_ev:
            continue
        inp = StageInput(
            layer_id="P3_ROOT_STEM_CLOSURE",
            surface=case["surface"],
            hokom_evidence=p3_ev,
            prior_output=None,
            pipeline_run_id="corpus-test",
            word_index=0,
        )
        out = adapter.adapt(inp)
        assert out.judgment.status is ConstitutionalStatus.BATIL, (
            f"Case {case['case_id']}: expected BATIL at P3, got {out.judgment.status}"
        )


def test_09_all_case_ids_unique(cases):
    ids = [c["case_id"] for c in cases]
    assert len(ids) == len(set(ids)), "Duplicate case_ids found in corpus"


def test_10_all_cases_required_fields(cases):
    required = {"case_id", "section", "surface", "expected"}
    for c in cases:
        missing = required - set(c.keys())
        assert not missing, f"Case missing fields: {missing} in {c.get('case_id', '?')}"
