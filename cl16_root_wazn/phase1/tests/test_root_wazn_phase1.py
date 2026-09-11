"""CL-16 Phase 1 focused tests — artifact binding + unlicensed-promotion guards.

Scope: Hokom-side evidence adapter ONLY. Does not touch vendor/Taaqol, does not
call weigh(), does not close CL-16.
"""
from __future__ import annotations

import csv
import json
import sys
import shutil
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))

import root_wazn_evidence_adapter as A  # noqa: E402


@pytest.fixture(scope="module")
def adapter():
    return A.RootWaznEvidenceAdapter()


@pytest.fixture(scope="module")
def examples(adapter):
    """Find one CERTIFIED, one EVIDENCE_SUPPORTED, one CANDIDATE root that is UNAMBIGUOUS
    (appears in exactly one row, with a baab) so the acceptance path is deterministic."""
    csv_path = A._artifact(adapter.manifest, "ROOT_PROOF_TABLE")["path"]
    rows_by_root = {}
    with open(csv_path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            root = str(row.get("الجذر", "")).strip()
            if root:
                rows_by_root.setdefault(root, []).append(row)
    found = {}
    for root, rows in rows_by_root.items():
        if len(rows) != 1:
            continue  # unambiguous roots only
        row = rows[0]
        if not str(row.get("باب الصرفي", "")).strip():
            continue
        lvl = A._cert_from_row(row)
        found.setdefault(lvl, root)
        if len(found) == 3:
            break
    return found


# ── Security / integrity ───────────────────────────────────────────────────
def test_artifacts_verify_ok(adapter):
    prov = A.verify_artifacts(adapter.manifest)
    assert prov and all(len(sha) == 12 for _, sha in prov)


def test_sha256_change_blocks(tmp_path):
    """Tamper a copied artifact → sha mismatch → ArtifactIntegrityError (BLOCK)."""
    man = A.load_manifest()
    art = A._artifact(man, "ROOT_PROOF_TABLE")
    tampered = tmp_path / "audited_roots.csv"
    shutil.copy(art["path"], tampered)
    tampered.write_bytes(tampered.read_bytes() + b"\n# tamper\n")  # change bytes
    man2 = json.loads(json.dumps(man))
    for a in man2["artifacts"]:
        if a["role"] == "ROOT_PROOF_TABLE":
            a["path"] = str(tampered)  # keep the OLD sha256 → must mismatch now
    mpath = tmp_path / "manifest.json"
    mpath.write_text(json.dumps(man2), encoding="utf-8")
    with pytest.raises(A.ArtifactIntegrityError) as e:
        A.RootWaznEvidenceAdapter(mpath)
    assert A.Code.ARTIFACT_SHA_MISMATCH in str(e.value)


def test_missing_artifact_blocks(tmp_path):
    man = A.load_manifest()
    man2 = json.loads(json.dumps(man))
    for a in man2["artifacts"]:
        if a["role"] == "MAQAYIS_LEXICON_DB":
            a["path"] = str(tmp_path / "does_not_exist.db")
    mpath = tmp_path / "m.json"
    mpath.write_text(json.dumps(man2), encoding="utf-8")
    with pytest.raises(A.ArtifactIntegrityError) as e:
        A.RootWaznEvidenceAdapter(mpath)
    assert A.Code.ARTIFACT_MISSING in str(e.value)


# ── Acceptance ──────────────────────────────────────────────────────────────
def test_accept_certified_root(adapter, examples):
    root = examples.get(A.CertLevel.CERTIFIED)
    if root is None:
        pytest.skip("no CERTIFIED example in data")
    ev = adapter.assess(root)
    assert ev.verdict == A.Verdict.LICENSED
    assert ev.cert_level == A.CertLevel.CERTIFIED
    assert ev.rank == A.CertLevel.CERTIFIED
    assert ev.baab is not None


def test_accept_evidence_supported_not_promoted(adapter, examples):
    root = examples.get(A.CertLevel.EVIDENCE_SUPPORTED)
    if root is None:
        pytest.skip("no EVIDENCE_SUPPORTED example in data")
    ev = adapter.assess(root)
    assert ev.verdict == A.Verdict.LICENSED
    assert ev.cert_level == A.CertLevel.EVIDENCE_SUPPORTED
    # never promoted to CERTIFIED
    assert ev.rank == A.CertLevel.EVIDENCE_SUPPORTED
    assert ev.rank < A.CertLevel.CERTIFIED


# ── Rejection / DEFER / BLOCK ────────────────────────────────────────────────
def test_reject_candidate_root_no_wazn(adapter, examples):
    root = examples.get(A.CertLevel.CANDIDATE)
    if root is None:
        pytest.skip("no CANDIDATE example in data")
    ev = adapter.assess(root)
    assert ev.verdict == A.Verdict.REFUSED
    assert ev.reason_code == A.Code.UNLICENSED_ROOT_TO_WEIGHT
    assert ev.rank == A.CertLevel.CANDIDATE  # no promotion


def test_model_source_blocked(adapter, examples):
    root = examples.get(A.CertLevel.CERTIFIED) or "كتب"
    ev = adapter.assess(root, source="model")
    assert ev.verdict == A.Verdict.BLOCK and ev.reason_code == A.Code.FORBIDDEN_AUTHORITY


def test_masaq_source_blocked(adapter):
    ev = adapter.assess("كتب", source="masaq")
    assert ev.verdict == A.Verdict.BLOCK and ev.reason_code == A.Code.FORBIDDEN_AUTHORITY


def test_unknown_query_defers(adapter):
    ev = adapter.assess("زقزقثذخ")  # not a real root
    assert ev.verdict == A.Verdict.DEFER


def _mini_adapter(tmp_path, rows, cols):
    """Build an adapter over a tiny temp CSV (+temp manifest) to exercise DEFER/BLOCK paths."""
    csvp = tmp_path / "mini.csv"
    with open(csvp, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    man = A.load_manifest()
    man2 = json.loads(json.dumps(man))
    import hashlib
    sha = hashlib.sha256(csvp.read_bytes()).hexdigest()
    man2["artifacts"] = [a for a in man2["artifacts"] if a["role"] != "ROOT_PROOF_TABLE"]
    man2["artifacts"].insert(0, {"role": "ROOT_PROOF_TABLE", "path": str(csvp),
                                 "size_bytes": csvp.stat().st_size, "sha256": sha})
    # drop the other pinned artifacts for isolation of this unit path
    man2["artifacts"] = [man2["artifacts"][0]]
    mp = tmp_path / "m.json"
    mp.write_text(json.dumps(man2), encoding="utf-8")
    return A.RootWaznEvidenceAdapter(mp)


_COLS = ["id", "الفعل الماضي", "الجذر", "باب الصرفي", "تم إعادة تدقيقه", "صحيح (الجذر حقيقي)"]


def test_multi_candidate_defers(tmp_path):
    ad = _mini_adapter(tmp_path, [
        {"id": "1", "الفعل الماضي": "س", "الجذر": "كتب", "باب الصرفي": "ب", "تم إعادة تدقيقه": "1", "صحيح (الجذر حقيقي)": "1"},
        {"id": "2", "الفعل الماضي": "س", "الجذر": "كتم", "باب الصرفي": "ب", "تم إعادة تدقيقه": "1", "صحيح (الجذر حقيقي)": "1"},
    ], _COLS)
    ev = ad.assess("س")
    assert ev.verdict == A.Verdict.DEFER and ev.reason_code == A.Code.MULTI_CANDIDATE


def test_missing_baab_defers(tmp_path):
    ad = _mini_adapter(tmp_path, [
        {"id": "1", "الفعل الماضي": "ك", "الجذر": "كتب", "باب الصرفي": "", "تم إعادة تدقيقه": "1", "صحيح (الجذر حقيقي)": "1"},
    ], _COLS)
    ev = ad.assess("كتب")
    assert ev.verdict == A.Verdict.DEFER and ev.reason_code == A.Code.MISSING_BAAB


# ── Invariants / boundaries ──────────────────────────────────────────────────
def test_no_promotion_invariant_over_sample(adapter, examples):
    for root in examples.values():
        ev = adapter.assess(root)
        assert ev.rank <= ev.cert_level  # rank NEVER exceeds evidence


def test_no_backflow(adapter):
    with pytest.raises(A.BackflowForbiddenError):
        adapter.record_result_into_law("ktb", "wazn")


def test_cl16_not_closed():
    assert A.CL16_CLOSED is False


def test_adapter_does_not_import_vendor_or_model():
    """Check import STATEMENTS + calls, not docstring/comment mentions."""
    src_lines = (Path(A.__file__)).read_text(encoding="utf-8").splitlines()
    code = [ln for ln in src_lines if not ln.lstrip().startswith("#")]
    imports = [ln.strip() for ln in code if ln.lstrip().startswith(("import ", "from "))]
    for imp in imports:
        assert "taaqqul_slot_geometry" not in imp, f"forbidden vendor import: {imp}"
        assert "openai" not in imp and "anthropic" not in imp, f"forbidden model import: {imp}"
    # no actual weigh() call outside comments/docstring
    joined = "\n".join(code)
    assert ".weigh(" not in joined and "\nweigh(" not in joined, "must not call weigh()"
