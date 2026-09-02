"""CL-16 Phase 2 — Licensing seam (Hokom-side; feeds vendor weigh() read-only).

The seam carries a Phase-1 LICENSED RootWaznEvidence into Taaqol's weight branch
through licensed vendor contracts ONLY:

  Phase-1 evidence (EVIDENCE_SUPPORTED|CERTIFIED, root, baab, rank_e)
   -> EvidenceContract  (rank cap only; opaque identifier; NO lexical/meaning payload)
   -> form-only WeightReadinessCandidate (root SURFACE letters imaged; NO meaning)
   -> Ω ResidualGovernanceVerdict (GRANTED, rank <= rank_e)
   -> weigh(WeightReadinessCandidate, Ω)  [vendor, UNCHANGED]  -> WeightFitCandidate
   -> RootWaznFitResult { root, baab (Phase-1 evidence), pattern fit, rank <= rank_e }

Constitution (docs/19/20/24):
  * weigh(root) is NEVER called — only weigh(WeightReadinessCandidate).
  * No lexicon/meaning/root crosses into the weight branch; only a form-only
    readiness candidate + a rank-cap EvidenceContract.
  * weigh() and vendor are not modified.  Vendor contracts are sha256-pinned.
  * Rank of the result never exceeds the Phase-1 evidence rank.

This module does NOT close CL-16.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
_P1_DIR = _HERE.parent / "phase1"
_MANIFEST = _HERE / "phase2_manifest.json"

# CL-16 is NOT closed by this module.
CL16_CLOSED = False

# ── Phase-1 evidence adapter (verifies its own frozen artifacts on init) ────
sys.path.insert(0, str(_P1_DIR))
import root_wazn_evidence_adapter as P1  # noqa: E402


class VendorContractIntegrityError(Exception):
    """Raised (BLOCK) when a pinned vendor weight/evidence contract drifted."""


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict:
    return json.loads(_MANIFEST.read_text(encoding="utf-8"))


def verify_vendor_contracts(manifest: Optional[dict] = None) -> None:
    manifest = manifest or load_manifest()
    for c in manifest["vendor_contracts"]:
        if not os.path.isfile(c["path"]):
            raise VendorContractIntegrityError(f"VENDOR_CONTRACT_MISSING: {c['path']}")
        actual = _sha256(c["path"])
        if actual != c["sha256"]:
            raise VendorContractIntegrityError(
                f"VENDOR_CONTRACT_DRIFT: {os.path.basename(c['path'])} "
                f"expected {c['sha256'][:12]} got {actual[:12]}"
            )


# Verify vendor integrity BEFORE importing the vendor package.
_manifest = load_manifest()
verify_vendor_contracts(_manifest)
if _manifest["vendor_root"] not in sys.path:
    sys.path.insert(0, _manifest["vendor_root"])

# ── Vendor licensed carriers / operations (read-only import; nothing edited) ──
from taaqqul_slot_geometry.core.rank_lattice import Rank  # noqa: E402
from taaqqul_slot_geometry.core.slot_graph import TraceRef  # noqa: E402
from taaqqul_slot_geometry.core.evidence_contract import (  # noqa: E402
    EvidenceSource,
    EvidenceContract,
)
from taaqqul_slot_geometry.weight import (  # noqa: E402
    PathCandidate,
    PathKind,
    PreWeightSurface,
    SyllableCandidate,
    SyllableSequenceCandidate,
    WeightReadinessCandidate,
    WordBoundaryCandidate,
    WordCarrierCandidate,
    omega_governance,
    weigh,
)
from taaqqul_slot_geometry.weight.pre_weight import (  # noqa: E402
    LetterStanding,
    OperationTraceCandidate,
    OriginalExtraMap,
)
from taaqqul_slot_geometry.weight.mu_chain import OmegaGovernanceState  # noqa: E402
from taaqqul_slot_geometry.weight.weight_fit import WeightFitState  # noqa: E402


# Phase-1 certification → a bounded evidence rank (never above chain ceiling,
# never CERTIFICATE). EVIDENCE_SUPPORTED < CERTIFIED, both kept low.
_CERT_TO_RANK = {
    P1.CertLevel.EVIDENCE_SUPPORTED: Rank.TRACE,     # 1
    P1.CertLevel.CERTIFIED: Rank.CANDIDATE,          # 2  (still << CERTIFICATE)
}


class SeamCode:
    OK = "OK"
    NOT_LICENSED = "NOT_LICENSED"              # Phase-1 did not license → no seam
    OMEGA_NOT_GRANTED = "OMEGA_NOT_GRANTED"
    RANK_PROMOTION_FORBIDDEN = "RANK_PROMOTION_FORBIDDEN"
    WEIGH_REFUSED = "WEIGH_REFUSED"


@dataclass(frozen=True)
class RootWaznFitResult:
    query: str
    root: Optional[str]
    baab: Optional[str]
    verdict: str                 # LICENSED / DEFER / BLOCK / REFUSED
    reason_code: str
    evidence_rank: Rank          # the Phase-1-derived cap
    fit_rank: Rank               # weigh() output rank; invariant: <= evidence_rank
    fit_state: Optional[str]     # WeightFitState value or None
    fit_verdict: Optional[str]   # pattern-space fit assessment (opaque str)
    provenance: tuple


def _base(kind: str, ident: str, value: str, root: str) -> dict:
    return {
        "value": value,
        "type": kind,
        "origin": "cl16_phase2_seam",
        "identity": ident,
        "domain": "arabic_morphophonology",
        "scope": "cl16-phase2-seam",
        "rank": Rank.CANDIDATE,
        "residuals": (),
        "trace": TraceRef(anchor=f"trace://cl16/phase2/{root}", kind="DECLARED_ENTRY"),
    }


def _build_form_only_readiness(root: str) -> WeightReadinessCandidate:
    """Image the root's SURFACE letters into a licensed readiness candidate.

    Form only: one syllable per letter (consonant + neutral vowel).  No meaning,
    no baab, no lexical content is placed on any carrier.
    """
    letters = [c for c in root if c.strip()]
    sylls = tuple(
        SyllableCandidate(**_base("syllable", f"syll-{root}-{i}", f"{l}a", root),
                          units=((l, "a"),))
        for i, l in enumerate(letters)
    )
    seq = SyllableSequenceCandidate(
        **_base("syllable_sequence", f"seq-{root}", "-".join(letters), root),
        syllables=sylls,
    )
    boundary = WordBoundaryCandidate(
        **_base("word_boundary", f"wb-{root}", root, root), sequence=seq)
    carrier = WordCarrierCandidate(
        **_base("word_carrier", f"wc-{root}", root, root), bounded_surface=boundary)
    oem = OriginalExtraMap(
        **_base("original_extra_map", f"oem-{root}", root, root),
        underlying_form=root,
        assignments=tuple((l, LetterStanding.ORIGINAL) for l in letters),
    )
    ops = OperationTraceCandidate(
        **_base("operation_trace", f"ops-{root}", "declared-steps", root),
        steps=("declared_seq", "declared_boundary"),
    )
    surface = PreWeightSurface(
        **_base("pre_weight_surface", f"pws-{root}", root, root),
        carrier=carrier,
        path=PathCandidate(**_base("path", f"path-{root}", "root_path", root),
                           kind=PathKind.ROOT, carrier=carrier),
        original_extra=oem,
        operations=ops,
    )
    return WeightReadinessCandidate(
        **_base("weight_readiness", f"wr-{root}", root, root), surface=surface)


class WeighSeam:
    """Phase-2 seam over Phase-1 evidence + the vendor weight branch (read-only)."""

    def __init__(self):
        verify_vendor_contracts()                 # vendor integrity gate (BLOCK on drift)
        self.p1 = P1.RootWaznEvidenceAdapter()    # Phase-1 artifact integrity gate

    def fit(self, query: str, *, source: str = "audited_roots") -> RootWaznFitResult:
        ev = self.p1.assess(query, source=source)

        # S-G2: only a Phase-1 LICENSED evidence may enter the seam.
        if ev.verdict != P1.Verdict.LICENSED:
            return RootWaznFitResult(query, ev.root, ev.baab, ev.verdict,
                                     ev.reason_code if ev.verdict != P1.Verdict.LICENSED
                                     else SeamCode.NOT_LICENSED,
                                     Rank.ZERO, Rank.ZERO, None, None, ev.provenance)

        # S1: rank-cap EvidenceContract (opaque identifier; no meaning payload).
        ev_rank = _CERT_TO_RANK[ev.cert_level]
        _contract = EvidenceContract(sources=(
            EvidenceSource(
                name=f"phase1_root_wazn:{ev.root}",  # opaque; imposes no rank semantics
                kind="cl16_phase1_certified_root",
                rank=ev_rank,
                trace_ref=TraceRef(anchor=f"trace://cl16/phase1/{ev.root}",
                                   kind="DECLARED_ENTRY"),
            ),
        ))

        # S2: form-only readiness carrier (root SURFACE only).
        readiness = _build_form_only_readiness(ev.root)

        # S3: Ω governance, surface_rank capped at the evidence rank.
        gov = omega_governance((), ev_rank)
        if gov.state is not OmegaGovernanceState.GRANTED:
            return RootWaznFitResult(query, ev.root, ev.baab, P1.Verdict.DEFER,
                                     SeamCode.OMEGA_NOT_GRANTED, ev_rank, Rank.ZERO,
                                     None, None, ev.provenance)

        # S4: the ONLY licensed weigh call — a WeightReadinessCandidate, never a root.
        result = weigh(readiness, gov)
        if result.state is not WeightFitState.FITTED or result.candidate is None:
            return RootWaznFitResult(query, ev.root, ev.baab, P1.Verdict.DEFER,
                                     SeamCode.WEIGH_REFUSED, ev_rank, Rank.ZERO,
                                     None, None, ev.provenance)

        fit = result.candidate
        state_value = result.state.value  # WeightFitState lives on the RESULT, not the candidate
        # S-G4: no promotion above the evidence rank.
        if fit.fit_rank > ev_rank:
            return RootWaznFitResult(query, ev.root, ev.baab, P1.Verdict.BLOCK,
                                     SeamCode.RANK_PROMOTION_FORBIDDEN, ev_rank,
                                     fit.fit_rank, state_value, fit.fit_verdict,
                                     ev.provenance)

        return RootWaznFitResult(query, ev.root, ev.baab, P1.Verdict.LICENSED,
                                 SeamCode.OK, ev_rank, fit.fit_rank,
                                 state_value, fit.fit_verdict, ev.provenance)
