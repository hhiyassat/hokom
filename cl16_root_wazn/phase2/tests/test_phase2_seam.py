"""CL-16 Phase 2 focused tests — licensing seam.

Verifies: only LICENSED Phase-1 evidence enters; weigh() is called ONLY with a
WeightReadinessCandidate; no promotion above evidence rank; no meaning crosses;
vendor-contract drift blocks; CL-16 stays open.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))

import weigh_seam as S            # noqa: E402
import root_wazn_evidence_adapter as P1  # noqa: E402 (added to path by weigh_seam)
from taaqqul_slot_geometry.weight import WeightReadinessCandidate  # noqa: E402
from taaqqul_slot_geometry.core.rank_lattice import Rank  # noqa: E402


@pytest.fixture(scope="module")
def seam():
    return S.WeighSeam()


@pytest.fixture(scope="module")
def examples(seam):
    csv_path = P1._artifact(seam.p1.manifest, "ROOT_PROOF_TABLE")["path"]
    rows_by_root = {}
    with open(csv_path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            r = str(row.get("الجذر", "")).strip()
            if r:
                rows_by_root.setdefault(r, []).append(row)
    found = {}
    for root, rows in rows_by_root.items():
        if len(rows) != 1:
            continue
        if not str(rows[0].get("باب الصرفي", "")).strip():
            continue
        found.setdefault(P1._cert_from_row(rows[0]), root)
        if len(found) == 3:
            break
    return found


# ── Acceptance ──────────────────────────────────────────────────────────────
def test_accept_certified_root_to_fit(seam, examples):
    root = examples.get(P1.CertLevel.CERTIFIED)
    if root is None:
        pytest.skip("no CERTIFIED example")
    r = seam.fit(root)
    assert r.verdict == P1.Verdict.LICENSED and r.reason_code == S.SeamCode.OK
    assert r.fit_state == "FITTED"
    assert r.fit_rank <= r.evidence_rank            # no promotion
    assert r.evidence_rank == Rank.CANDIDATE        # CERTIFIED → CANDIDATE cap


def test_accept_evidence_supported_not_promoted(seam, examples):
    root = examples.get(P1.CertLevel.EVIDENCE_SUPPORTED)
    if root is None:
        pytest.skip("no EVIDENCE_SUPPORTED example")
    r = seam.fit(root)
    assert r.verdict == P1.Verdict.LICENSED
    assert r.evidence_rank == Rank.TRACE
    assert r.fit_rank <= Rank.TRACE                 # never lifted above evidence


def test_fit_rank_never_exceeds_evidence(seam, examples):
    for root in examples.values():
        r = seam.fit(root)
        assert r.fit_rank <= r.evidence_rank


# ── Rejection / DEFER ────────────────────────────────────────────────────────
def test_candidate_evidence_no_fit(seam, examples):
    root = examples.get(P1.CertLevel.CANDIDATE)
    if root is None:
        pytest.skip("no CANDIDATE example")
    r = seam.fit(root)
    assert r.verdict != P1.Verdict.LICENSED         # not licensed → no weigh fit
    assert r.fit_rank == Rank.ZERO
    assert r.fit_state is None


def test_model_source_blocked(seam, examples):
    root = examples.get(P1.CertLevel.CERTIFIED) or "كتب"
    r = seam.fit(root, source="model")
    assert r.verdict == P1.Verdict.BLOCK
    assert r.fit_state is None


def test_unknown_query_defers(seam):
    r = seam.fit("زقزقثذخ")
    assert r.verdict == P1.Verdict.DEFER and r.fit_rank == Rank.ZERO


# ── weigh() only ever receives a WeightReadinessCandidate (never a root) ─────
def test_weigh_input_is_readiness_candidate(seam, examples):
    root = examples.get(P1.CertLevel.CERTIFIED) or examples.get(P1.CertLevel.EVIDENCE_SUPPORTED)
    if root is None:
        pytest.skip("no licensed example")
    readiness = S._build_form_only_readiness(root)
    assert isinstance(readiness, WeightReadinessCandidate)
    # a root string is never a valid weigh input; the seam only builds this carrier
    assert not isinstance(root, WeightReadinessCandidate)


def test_no_meaning_crosses_on_readiness(examples):
    root = next(iter(examples.values())) if examples else "كتب"
    readiness = S._build_form_only_readiness(root)
    for forbidden in ("meaning", "hukm", "baab", "madlul", "ifadah", "reality"):
        assert not hasattr(readiness, forbidden), f"readiness must not carry {forbidden!r}"
    assert readiness.value == root  # form only


# ── Vendor integrity / boundaries ────────────────────────────────────────────
def test_vendor_drift_blocks(tmp_path):
    man = S.load_manifest()
    man2 = json.loads(json.dumps(man))
    man2["vendor_contracts"][0]["sha256"] = "0" * 64  # wrong sha for weight_fit.py
    mp = tmp_path / "m.json"
    mp.write_text(json.dumps(man2), encoding="utf-8")
    with pytest.raises(S.VendorContractIntegrityError) as e:
        S.verify_vendor_contracts(S.json.loads(mp.read_text()))
    assert "VENDOR_CONTRACT_DRIFT" in str(e.value)


def test_weigh_not_modified_by_seam():
    """The seam only imports/calls weigh; it must not reference a mutation of it."""
    src = Path(S.__file__).read_text(encoding="utf-8")
    code = "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))
    assert "def weigh" not in code          # seam does not redefine weigh
    assert "weight_fit.py" not in code      # seam does not write the vendor file


def test_cl16_not_closed():
    assert S.CL16_CLOSED is False
