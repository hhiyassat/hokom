"""
Proofs for the P8→P12 proof-carrying certificate chain + ancestry + coherence.
Honest: certificates carry the REAL canonical runtime status (DEFER where evidence
is absent). Success = accounted-for + no-jump + coherent + deterministic (§30),
not 21/21 certified.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PKG = os.path.dirname(_HERE)
_HOKOM = os.path.dirname(_PKG)
for p in (_HOKOM, os.path.join(_HOKOM, "src"), _PKG):
    if p not in sys.path:
        sys.path.insert(0, p)

from hokom_pipeline import hokom                                   # noqa: E402
from hokom.canonical.pipeline import CanonicalPipeline, SentenceInput, WordInput  # noqa: E402
from canonical_bridge.bridge import bridge_word_evidence, build_dispute_scope    # noqa: E402
from canonical_bridge.certificates import (                        # noqa: E402
    build_certificate_chain, build_run_manifest, verify_artifact_coherence,
    CERTIFIED, DEFER, NOT_APPLICABLE, _no_jump)

_P = CanonicalPipeline.build()


def _vertical(tokens):
    per = [hokom(t) for t in tokens]
    words = tuple(WordInput(surface=t, hokom_evidence_by_stage=bridge_word_evidence(hk),
                            word_index=i) for i, (t, hk) in enumerate(zip(tokens, per)))
    ds = build_dispute_scope(" ".join(tokens), per).to_dict()
    tr = _P.run_sentence(SentenceInput(words=words, sentence_hokom_evidence={}))
    return build_certificate_chain(tr, ds)


def test_six_typed_certificates_accounted_for():
    r = _vertical(["كَتَبَ", "الْكَاتِبُ", "الرِّسَالَةَ"])
    assert len(r["certificates"]) == 5   # P8..P12 chain (+ ancestry)
    acc = r["accounting"]
    assert acc["unexplained"] == 0                       # every stage accounted for
    assert acc["certified"] + acc["deferred"] + acc["ambiguous"] + acc["blocked"] \
        + acc["not_applicable"] == acc["total_applicable"]


def test_res_ancestry_01_closed_via_no_jump():
    r = _vertical(["كَتَبَ", "الْكَاتِبُ", "الرِّسَالَةَ"])
    assert r["res_ancestry_01"] == "CLOSED"
    assert r["ancestry_certificate"]["no_jump_failures"] == 0
    assert r["ancestry_certificate"]["dispute_scope_first"] is True


def test_no_jump_law_rejects_certified_successor_from_defer():
    ok, checks = _no_jump(DEFER, CERTIFIED)             # forbidden jump
    assert ok is False
    assert any(c.result == "FAIL" for c in checks)
    ok2, _ = _no_jump(CERTIFIED, CERTIFIED)             # licensed transition
    assert ok2 is True
    ok3, _ = _no_jump(NOT_APPLICABLE, DEFER)            # NA permits
    assert ok3 is True


def test_run_manifest_no_unknown_head():
    m = build_run_manifest()
    assert m["hokom_sha"] != "UNKNOWN"
    assert m["corpus_sha"].startswith("1130fc9f")
    assert m["canonical_registry_hash"] not in ("ABSENT", None)


def test_artifact_coherence_fails_on_mismatch():
    m = build_run_manifest()
    ok = verify_artifact_coherence(m, [{"path": "x", "run_id": m["run_id"],
                                        "hokom_sha": m["hokom_sha"]}])
    assert ok["all_same_manifest"] is True
    bad = verify_artifact_coherence(m, [{"path": "x", "run_id": "WRONG",
                                         "hokom_sha": m["hokom_sha"]}])
    assert bad["all_same_manifest"] is False and bad["problems"]


def test_determinism_no_random_ids():
    a = json.dumps(_vertical(["كَتَبَ", "الْكَاتِبُ"]), ensure_ascii=False, sort_keys=True)
    b = json.dumps(_vertical(["كَتَبَ", "الْكَاتِبُ"]), ensure_ascii=False, sort_keys=True)
    assert a == b


def test_owner_and_no_fiqh_leakage():
    r = _vertical(["كَتَبَ"])
    for c in r["certificates"]:
        assert c["owner"] == "HOKOM_CANONICAL_PIPELINE"
        d = json.dumps(c, ensure_ascii=False)
        for banned in ("tafsir", "fiqh", "hukm", "fatwa"):
            assert banned not in d.lower()
