#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
canonical_bridge/bridge.py — real end-to-end wiring:

    corpus token → production hokom() (P0–P5 evidence)
                 → typed evidence bridge (hokom_evidence_by_stage)
                 → HOKOM_CANONICAL_PIPELINE (19-stage runtime, the authoritative
                   P11/P12 judgment owner)
                 → DisputeScope-first (تحرير محل النزاع) → linguistic judgment
                 → honest DEFER / TAWAQQUF

Constitution: LINGUISTIC_STRUCTURAL_JUDGMENT. No fiqh, no tafsir, no shar'i hukm.
The bridge maps ONLY evidence production hokom() genuinely produces (P0–P5); it
NEVER fabricates upstream facts. Sentence-level evidence (P9–P12) is not produced
by the token pipeline → those stages DEFER honestly (declared residual). Root fact
comes only from the single authority pipeline/p3_candidate (resolve_root_pipeline).
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Optional

_HOKOM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_HOKOM, os.path.join(_HOKOM, "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from hokom_pipeline import hokom  # noqa: E402
from hokom.canonical.pipeline import CanonicalPipeline, SentenceInput, WordInput  # noqa: E402

OUT_OF_SCOPE = ("fiqh_hukm", "tafsir")   # AUTHORIZED_OUT_OF_SCOPE (constitutional)


# ── evidence bridge: production hokom() → hokom_evidence_by_stage (real keys only)
def bridge_word_evidence(hk: dict) -> dict[str, dict[str, Any]]:
    """Map genuine hokom() output to the canonical stages' evidence contract.
    Only P0–P5 keys are populated (real production evidence). Absent → stage DEFERs."""
    ev: dict[str, dict[str, Any]] = {}
    rc = hk.get("root_candidate")
    root = hk.get("final_root") or (rc.canonical_root if rc else None)
    prof = (rc.root_profile if rc else {}) or {}
    directive = rc.directive if rc else None

    # P3 — root/stem closure (from the SINGLE root authority)
    if root and directive == "ACCEPT":
        ev["P3_ROOT_STEM_CLOSURE"] = {
            "root_path": "+".join(root),
            "root_radicals": list(root),
            "root_class": prof.get("root_type"),
            "root_soundness": prof.get("root_type"),
            "consonant_count": prof.get("radical_count"),
            "stem": hk.get("morphology_surface"),
        }
    # P4 — jamid/mushtaq + wazn/bab/masdar (real production projections)
    p4 = {}
    if hk.get("word_class"):
        p4["jamid_mushtaq"] = hk.get("jamid_verdict") or hk.get("word_class")
    if hk.get("final_wazn"):
        p4["wazn"] = hk["final_wazn"]
    if hk.get("phase4b_result") is not None:
        p4["bab_id"] = getattr(hk.get("phase4b_result"), "bab_id", None)
    if hk.get("final_masdar"):
        p4["masdar"] = hk["final_masdar"]
    if p4:
        ev["P4_JAMID_MUSHTAQ"] = p4
    # P5 — word class / inflection (real)
    if hk.get("word_class"):
        ev["P5_MUFRAD_WORD_CONTRACTS"] = {
            "word_class": hk.get("word_class"),
            "inflection_class": hk.get("inflectional_form") or hk.get("word_class_subclass"),
        }
    return ev


# ── تحرير محل النزاع — typed DisputeScope (first judgment gate) ──────────────
@dataclass(frozen=True)
class DisputeScope:
    claim_identity: str
    claim_owner: str
    claimed_fact: str
    agreed_facts: tuple[str, ...]
    disputed_facts: tuple[str, ...]
    admissible_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    residuals: tuple[str, ...]
    out_of_scope: tuple[str, ...]
    is_formed: bool

    def to_dict(self) -> dict:
        return {k: (list(v) if isinstance(v, tuple) else v)
                for k, v in self.__dict__.items()}


def build_dispute_scope(surface: str, per_word: list[dict]) -> DisputeScope:
    """Construct the linguistic dispute scope from per-word evidence. If the
    sentence-level admissible evidence is insufficient, is_formed=False → DEFER."""
    agreed, disputed, admissible, missing = [], [], [], []
    for i, hk in enumerate(per_word):
        rc = hk.get("root_candidate")
        d = rc.directive if rc else None
        tag = f"w{i}:{hk.get('input_surface','')}"
        if d == "ACCEPT" and (hk.get("final_root")):
            agreed.append(f"{tag}:root={''.join(hk['final_root'])}")
            admissible.append(f"{tag}:P3_root")
        elif d in ("DEFER", "BLOCK") or d is None:
            disputed.append(f"{tag}:root_{str(d).lower()}")
    # sentence-level evidence (P9–P12) is NOT produced by the token pipeline
    missing.append("sentence_geometry_evidence:P9_P12_not_produced_by_token_pipeline")
    formed = len(admissible) > 0                     # claim scope can be stated
    return DisputeScope(
        claim_identity=f"structural_wellformedness:{surface}",
        claim_owner="HOKOM_CANONICAL_PIPELINE",
        claimed_fact="sentence carries closed irab geometry with potential speech force (ifadah)",
        agreed_facts=tuple(agreed), disputed_facts=tuple(disputed),
        admissible_evidence=tuple(admissible), missing_evidence=tuple(missing),
        residuals=("tawaqquf:sentence_level_evidence_absent",) if True else (),
        out_of_scope=OUT_OF_SCOPE, is_formed=formed)


# ── end-to-end ───────────────────────────────────────────────────────────────
def run_end_to_end(tokens: list[str]) -> dict:
    per_word = [hokom(t) for t in tokens]                      # production P0–P5
    words = tuple(
        WordInput(surface=t, hokom_evidence_by_stage=bridge_word_evidence(hk), word_index=i)
        for i, (t, hk) in enumerate(zip(tokens, per_word)))
    # DisputeScope FIRST (تحرير محل النزاع) — gate before stronger judgment
    dispute = build_dispute_scope(" ".join(tokens), per_word)
    pipeline = CanonicalPipeline.build()
    trace = pipeline.run_sentence(SentenceInput(words=words, sentence_hokom_evidence={}))
    tj = trace.terminal_judgment
    terminal_status = getattr(getattr(tj, "status", None), "value", None)
    # honest gate: no DisputeScope → the judgment result is TAWAQQUF regardless
    judgment = terminal_status if dispute.is_formed else "TAWAQQUF"
    return {
        "tokens": tokens,
        "stages_reached": len(trace.all_stages),
        "p0_p5_evidence_bridged": sum(1 for w in words if w.hokom_evidence_by_stage),
        "dispute_scope": dispute.to_dict(),
        "dispute_scope_formed": dispute.is_formed,
        "terminal_status": terminal_status,      # canonical P12 status (honest DEFER)
        "judgment": judgment,
        "out_of_scope": list(OUT_OF_SCOPE),
        "root_authority": "pipeline/p3_candidate/root_resolution.resolve_root_pipeline",
    }
