#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/run_canonical_ancestry_vertical.py

Regenerate ONE coherent canonical run: real corpus tokens → hokom() P0–P5 evidence
→ HOKOM_CANONICAL_PIPELINE 19-stage runtime → typed P8→P12 certificate chain +
ancestry, all stamped with a single CanonicalRunManifest. Writes the artifact to
disk, then re-reads and verifies artifact coherence (any SHA/run_id mismatch = FAIL,
not warn). Deterministic (content-hash IDs, no UUID) → run1 == run2.

Honest by construction: certificates carry the REAL runtime status. With no
sentence-level evidence, P9–P12 DEFER (declared residual). Success = every
applicable stage ACCOUNTED FOR + no-jump + coherent + deterministic — NOT
21/21 CERTIFIED. No fiqh / no tafsir / no real-world truth.

Usage:  python3 scripts/run_canonical_ancestry_vertical.py [out.json]
Exit 0 = coherent + no-jump closed; non-zero = coherence/no-jump failure.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

_HOKOM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_HOKOM, os.path.join(_HOKOM, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hokom_pipeline import hokom
from hokom.canonical.pipeline import CanonicalPipeline, SentenceInput, WordInput
from canonical_bridge.bridge import bridge_word_evidence, build_dispute_scope
from canonical_bridge.government_producer import produce_government
from canonical_bridge.certificates import (
    build_certificate_chain, build_run_manifest, verify_artifact_coherence)

# Real-corpus verticals, all genuine hokom() runs (no fixtures):
#   positive_government  — real cross-token jar→majrur (إِلَىٰ أَجَلٍ, Āyat al-Dayn)
#                          → native government CERTIFIED through P8→P12
#   clause_defer         — a clause with no produced sentence evidence → honest DEFER
#   closed_class_control — a bare closed-class token → NA at P8
VERTICALS = {
    "positive_government": ["إِلَىٰ", "أَجَلٍ"],
    "clause_defer": ["كَتَبَ", "الْكَاتِبُ", "الرِّسَالَةَ"],
    "closed_class_control": ["مِنْ"],
}

_PIPELINE = CanonicalPipeline.build()


def _run_vertical(tokens):
    gov = produce_government(tokens)          # native جار→مجرور government (no oracle)
    per = [hokom(t) for t in tokens]
    words = []
    for i, (t, hk) in enumerate(zip(tokens, per)):
        ev = bridge_word_evidence(hk)
        ev.update(gov["word_evidence"].get(i, {}))
        words.append(WordInput(surface=t, hokom_evidence_by_stage=ev, word_index=i))
    ds = build_dispute_scope(" ".join(tokens), per).to_dict()
    trace = _PIPELINE.run_sentence(SentenceInput(
        words=tuple(words), sentence_hokom_evidence=gov["sentence_evidence"]))
    return build_certificate_chain(trace, ds, government_evidence=gov)


def build_run(manifest):
    verticals = {name: _run_vertical(toks) for name, toks in VERTICALS.items()}
    payload = {
        "run_manifest": manifest,
        "scope": "LINGUISTIC_STRUCTURAL_JUDGMENT",
        "owner": "HOKOM_CANONICAL_PIPELINE",
        "root_owner": "pipeline/p3_candidate/root_resolution.resolve_root_pipeline",
        "out_of_scope": ["fiqh_hukm", "tafsir"],
        "verticals": verticals,
    }
    # artifact stamp — content hash over the payload binds bytes to this run
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    payload["artifact_sha256_of_body"] = hashlib.sha256(body.encode()).hexdigest()
    return payload


def main(argv):
    out = argv[1] if len(argv) > 1 else os.path.join(_HOKOM, "CLOSURE_CW1_CW2",
                                                     "canonical_ancestry_run.json")
    manifest = build_run_manifest()                       # asserts hokom_sha != UNKNOWN
    payload = build_run(manifest)

    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)

    # re-read from disk and verify artifact coherence against the manifest
    reread = json.load(open(out, encoding="utf-8"))
    artifact_ref = {"path": out, "run_id": reread["run_manifest"]["run_id"],
                    "hokom_sha": reread["run_manifest"]["hokom_sha"]}
    coherence = verify_artifact_coherence(manifest, [artifact_ref])

    # determinism: rebuild in-memory and compare (no UUID, no wallclock)
    again = build_run(manifest)
    again.pop("artifact_sha256_of_body", None)
    first = dict(payload); first.pop("artifact_sha256_of_body", None)
    deterministic = (json.dumps(again, sort_keys=True, ensure_ascii=False) ==
                     json.dumps(first, sort_keys=True, ensure_ascii=False))

    no_jump_ok = all(v["res_ancestry_01"] == "CLOSED" for v in payload["verticals"].values())
    unexplained = sum(v["accounting"]["unexplained"] for v in payload["verticals"].values())
    native_gov = sum(v.get("real_native_cross_token_government_certificate_count", 0)
                     for v in payload["verticals"].values())

    report = {
        "artifact": out,
        "run_id": manifest["run_id"],
        "hokom_sha": manifest["hokom_sha"][:12],
        "artifact_coherence": coherence["status"],
        "no_jump_all_closed": no_jump_ok,
        "unexplained_total": unexplained,
        "real_native_cross_token_government_certificate_count": native_gov,
        "deterministic_run1_eq_run2": deterministic,
        "verticals": {n: {"accounting": v["accounting"],
                          "res_ancestry_01": v["res_ancestry_01"],
                          "chain_verdict": v["ancestry_certificate"]["chain_verdict"]}
                      for n, v in payload["verticals"].items()},
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    ok = (coherence["all_same_manifest"] and no_jump_ok and unexplained == 0 and deterministic)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
