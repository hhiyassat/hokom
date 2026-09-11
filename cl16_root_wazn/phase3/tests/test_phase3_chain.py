"""CL-16 Phase 3 tests — the root-candidate chain.

Two kinds, kept apart on purpose:
  * checks  — the chain does what the owner's architecture says.
  * poisons — inputs that MUST be refused; a pass here is a refusal.

Every Arabic surface in this file is a bare consonantal skeleton (no marks),
so none of it depends on mark ORDER — the failure mode that once made a
hand-typed vocalized table match 1 row out of 2,704.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_P3 = _HERE.parent
sys.path.insert(0, str(_P3))

import root_candidate_chain as C  # noqa: E402


def _artifacts_present() -> bool:
    try:
        m = C.load_manifest()
    except Exception:
        return False
    return all(Path(C.resolve(a["path"], m)).is_file() for a in m["artifacts"])


pytestmark = pytest.mark.skipif(
    not _artifacts_present(),
    reason="frozen source artifacts are not mounted at their pinned paths")


@pytest.fixture(scope="module")
def chain():
    return C.RootCandidateChain()


# ── checks ────────────────────────────────────────────────────────────────
def test_cl16_is_not_closed_by_this_module():
    assert C.CL16_CLOSED is False


def test_construction_verifies_both_manifests(chain):
    roles = {r for r, _ in chain.provenance}
    assert "ROOT_CANDIDATE_TABLE" in roles          # phase 3
    assert "ROOT_PROOF_TABLE" in roles              # phase 1, inherited
    assert "MAQAYIS_LEXICON_DB" in roles


def test_summary_self_hash_agrees_with_the_pin(chain):
    declared = chain.run_summary["outputs"]["ROOT_CANDIDATES.csv"]["sha256"]
    pinned = C._artifact(chain.manifest, "ROOT_CANDIDATE_TABLE")["sha256"]
    assert declared == pinned


def test_a_full_chain_licenses_at_its_certification_rank(chain):
    ev = chain.assess("قتل")
    assert ev.verdict == C.Verdict.LICENSED
    assert ev.root == "قتل" and ev.baab
    assert ev.rank == C.CertLevel.CERTIFIED
    assert [link for link, _ in ev.chain] == [
        "ROOT_CANDIDATE_SOURCE", "MAQAYIS_LEXICON_SOURCE", "ROOT_PROOF_TABLE"]


def test_every_link_is_recorded_with_what_it_contributed(chain):
    ev = chain.assess("قتل")
    contributions = dict(ev.chain)
    assert "NOT_A_PROVEN_ROOT" in contributions["ROOT_CANDIDATE_SOURCE"]
    assert "PRESENCE_ONLY" in contributions["MAQAYIS_LEXICON_SOURCE"]


def test_a_word_that_is_not_a_candidate_defers(chain):
    ev = chain.assess("زقزق")
    assert ev.verdict == C.Verdict.DEFER
    assert ev.reason_code == C.ChainCode.NOT_A_CANDIDATE


def test_the_chain_is_mark_insensitive_at_its_entry(chain):
    assert chain.assess("قَتَلَ").candidate == chain.assess("قتل").candidate


# ── poisons ───────────────────────────────────────────────────────────────
def test_poison_a_closed_form_is_never_a_root(chain):
    """لكن passes the extractor AND audited_roots (لَكِنَ is a real verb).
    Hokom's own closed inventory refuses it. Measured: 33 of 369 candidates."""
    ev = chain.assess("لكن")
    assert ev.verdict == C.Verdict.DEFER
    assert ev.reason_code == C.ChainCode.CLOSED_FORM_COLLISION
    assert ev.root is None


def test_poison_candidacy_alone_never_licenses(chain):
    """A candidate absent from the certification table stays a candidate."""
    licensed_but_uncertified = [
        k for k, r in chain._candidates.items()
        if r["verdict"] == "ROOT_CANDIDATE" and k not in chain._closed_forms
        and not chain.p1._rows_for(k)]
    assert licensed_but_uncertified, "expected candidates outside audited_roots"
    ev = chain.assess(licensed_but_uncertified[0])
    assert ev.verdict != C.Verdict.LICENSED
    assert ev.rank == C.CertLevel.CANDIDATE


def test_poison_a_source_is_never_read_past_its_limit(chain):
    for asking in ("wazn", "root_proof"):
        with pytest.raises(C.SourceLimitError):
            chain.assess("قتل", asking_for=asking)


def test_poison_model_and_masaq_are_never_authorities(chain):
    for bad in ("model", "gpt", "masaq"):
        ev = chain.assess("قتل", source=bad)
        assert ev.verdict == C.Verdict.BLOCK
        assert ev.reason_code == C.ChainCode.FORBIDDEN_AUTHORITY


def test_poison_no_backflow_into_any_source_law(chain):
    with pytest.raises(C.BackflowForbiddenError):
        chain.record_result_into_law("قتل", "anything")


def test_poison_the_source_root_override_is_a_no_op_when_unset(monkeypatch):
    """On the owner's machine the variable is unset, and the pinned host path
    must be used verbatim. The override can never fire by accident."""
    monkeypatch.delenv("CL16_SOURCE_ROOT", raising=False)
    m = C.load_manifest()
    for art in m["artifacts"]:
        assert C.resolve(art["path"], m) == art["path"]


def test_poison_a_drifted_artifact_blocks_construction(tmp_path):
    m = C.load_manifest()
    m["artifacts"][0]["sha256"] = "0" * 64
    p = tmp_path / "drifted.json"
    p.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(C.ArtifactIntegrityError):
        C.RootCandidateChain(manifest_path=p)


def test_poison_a_missing_artifact_blocks_construction(tmp_path):
    m = C.load_manifest()
    m["artifacts"][0]["path"] = "/nonexistent/root_candidates.csv"
    p = tmp_path / "missing.json"
    p.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(C.ArtifactIntegrityError):
        C.RootCandidateChain(manifest_path=p)


def test_poison_rank_is_never_promoted_by_corroboration(chain):
    """Presence in the lexicon must not add a step. Every licensed result's
    rank equals what Phase 1 alone would have given it."""
    for key, row in list(chain._candidates.items())[:400]:
        if row["verdict"] != "ROOT_CANDIDATE" or key in chain._closed_forms:
            continue
        ev = chain.assess(key)
        if ev.verdict == C.Verdict.LICENSED:
            assert ev.rank == chain.p1.assess(key).rank


def test_poison_the_chain_never_claims_a_proven_root(chain):
    ev = chain.assess("قتل")
    assert not hasattr(ev, "root_proven")
    assert "PROVEN" not in ev.reason_code
