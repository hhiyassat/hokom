"""CL-16 Phase 1 — Root/Wazn Evidence Adapter (Hokom-side, read-only, artifact-bound).

Boundary discipline (Phase 1 ONLY):
  * Reads ONLY the sha256-pinned artifacts declared in artifact_manifest.json.
  * Performs NO git/network operation; does NOT read the external repo's live state.
  * Does NOT import taaqqul_slot_geometry / vendor / Taaqol.  Does NOT call weigh().
  * Never promotes a root/wazn above its evidence rank.
  * Never sources a root/wazn from a model or from MASAQ.
  * Read-only: no backflow from Hokom into the root/wazn law.

This module does NOT wire anything into Taaqol's weight branch and does NOT close CL-16.
It produces a licensed-or-refused *evidence record*; the WeightReadinessCandidate/weigh()
seam is deliberately absent (Phase 2, separate authorization).
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Optional

# CL-16 is NOT closed by this module. This constant is asserted by the tests.
CL16_CLOSED = False

_MANIFEST_PATH = Path(__file__).with_name("artifact_manifest.json")


# ── Certification lattice (from the source law: مرشح < مدعوم_بدليل < مُثبَت) ──
class CertLevel(IntEnum):
    CANDIDATE = 0          # مرشح
    EVIDENCE_SUPPORTED = 1 # مدعوم_بدليل
    CERTIFIED = 2          # مُثبَت


class Verdict:
    LICENSED = "LICENSED"   # evidence produced, at (never above) its own rank
    DEFER = "DEFER"
    BLOCK = "BLOCK"
    REFUSED = "REFUSED"


# Named refusal/preventer codes (Phase-1 guards)
class Code:
    OK = "OK"
    ARTIFACT_MISSING = "ARTIFACT_MISSING"
    ARTIFACT_SHA_MISMATCH = "ARTIFACT_SHA_MISMATCH"
    UNLICENSED_ROOT_TO_WEIGHT = "UNLICENSED_ROOT_TO_WEIGHT"   # candidate → no wazn
    MULTI_CANDIDATE = "MULTI_CANDIDATE"                        # >1 root → DEFER
    MISSING_BAAB = "MISSING_BAAB"                              # no baab → DEFER
    MULTI_BAAB = "MULTI_BAAB"                                  # root has >1 baab → DEFER (ambiguous)
    FORBIDDEN_AUTHORITY = "FORBIDDEN_AUTHORITY"                # model/MASAQ → BLOCK
    NO_BACKFLOW = "NO_BACKFLOW"                                # write attempt → BLOCK
    RANK_PROMOTION_FORBIDDEN = "RANK_PROMOTION_FORBIDDEN"


class ArtifactIntegrityError(Exception):
    """Raised (BLOCK) when a pinned artifact is missing or its sha256 differs."""


class BackflowForbiddenError(Exception):
    """Raised (BLOCK) on any attempt to write back into the root/wazn law."""


_FORBIDDEN_SOURCES = {"model", "llm", "gpt", "masaq", "masaq.csv"}


@dataclass(frozen=True)
class RootWaznEvidence:
    query: str
    root: Optional[str]
    baab: Optional[str]
    cert_level: CertLevel
    rank: CertLevel            # invariant: rank <= cert_level (never promoted)
    verdict: str
    reason_code: str
    provenance: tuple = field(default_factory=tuple)  # (artifact_role, sha256[:12]) pairs


# ── Artifact binding / integrity ──────────────────────────────────────────
def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(manifest_path: Path = _MANIFEST_PATH) -> dict:
    return json.loads(Path(manifest_path).read_text(encoding="utf-8"))


def verify_artifacts(manifest: Optional[dict] = None) -> list[tuple[str, str]]:
    """Verify every pinned artifact's sha256. BLOCK (raise) on missing/mismatch.

    Returns a provenance list of (role, sha256[:12]).
    """
    manifest = manifest or load_manifest()
    provenance: list[tuple[str, str]] = []
    for art in manifest["artifacts"]:
        p = art["path"]
        if not os.path.isfile(p):
            raise ArtifactIntegrityError(f"{Code.ARTIFACT_MISSING}: {art['role']} @ {p}")
        actual = _sha256(p)
        if actual != art["sha256"]:
            raise ArtifactIntegrityError(
                f"{Code.ARTIFACT_SHA_MISMATCH}: {art['role']} expected {art['sha256'][:12]} got {actual[:12]}"
            )
        provenance.append((art["role"], actual[:12]))
    return provenance


def _artifact(manifest: dict, role: str) -> dict:
    for a in manifest["artifacts"]:
        if a["role"] == role:
            return a
    raise ArtifactIntegrityError(f"{Code.ARTIFACT_MISSING}: role {role} not in manifest")


# ── Cert-level mapping from the frozen proof table (audited_roots.csv) ──────
def _cert_from_row(row: dict) -> CertLevel:
    real = str(row.get("صحيح (الجذر حقيقي)", "0")).strip() == "1"
    reaudited = str(row.get("تم إعادة تدقيقه", "0")).strip() == "1"
    if real and reaudited:
        return CertLevel.CERTIFIED
    if real or reaudited:
        return CertLevel.EVIDENCE_SUPPORTED
    return CertLevel.CANDIDATE


class RootWaznEvidenceAdapter:
    """Read-only adapter over the frozen root proof table + maqayis lexicon."""

    def __init__(self, manifest_path: Path = _MANIFEST_PATH):
        self.manifest = load_manifest(manifest_path)
        # Integrity gate: BLOCK if any pinned artifact drifted.
        self.provenance = tuple(verify_artifacts(self.manifest))
        self._csv_path = _artifact(self.manifest, "ROOT_PROOF_TABLE")["path"]

    # -- read-only lookup over the pinned CSV; keyed by root or past-verb --
    def _rows_for(self, query: str) -> list[dict]:
        q = query.strip()
        out = []
        with open(self._csv_path, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                if str(row.get("الجذر", "")).strip() == q or str(row.get("الفعل الماضي", "")).strip() == q:
                    out.append(row)
        return out

    def assess(self, query: str, *, source: str = "audited_roots") -> RootWaznEvidence:
        """Return a guarded evidence record for a root/verb query. No promotion, ever."""
        # G6: model / MASAQ may never be an authority.
        if source.lower() in _FORBIDDEN_SOURCES:
            return RootWaznEvidence(query, None, None, CertLevel.CANDIDATE, CertLevel.CANDIDATE,
                                    Verdict.BLOCK, Code.FORBIDDEN_AUTHORITY, self.provenance)

        rows = self._rows_for(query)
        if not rows:
            return RootWaznEvidence(query, None, None, CertLevel.CANDIDATE, CertLevel.CANDIDATE,
                                    Verdict.DEFER, Code.MISSING_BAAB, self.provenance)

        roots = {str(r.get("الجذر", "")).strip() for r in rows}
        # G4: multiple distinct root candidates → DEFER (no silent winner).
        if len(roots) > 1:
            return RootWaznEvidence(query, None, None, CertLevel.CANDIDATE, CertLevel.CANDIDATE,
                                    Verdict.DEFER, Code.MULTI_CANDIDATE, self.provenance)

        row = rows[0]
        root = str(row.get("الجذر", "")).strip() or None
        baab = str(row.get("باب الصرفي", "")).strip() or None
        cert = _cert_from_row(row)

        # G5: baab presence.
        baabs = {str(r.get("باب الصرفي", "")).strip() for r in rows if str(r.get("باب الصرفي", "")).strip()}
        if len(baabs) > 1:
            # A root with several verbs/baabs is ambiguous for a root-key → DEFER (not BLOCK).
            return RootWaznEvidence(query, root, None, cert, CertLevel.CANDIDATE,
                                    Verdict.DEFER, Code.MULTI_BAAB, self.provenance)
        if not baab:
            return RootWaznEvidence(query, root, None, cert, CertLevel.CANDIDATE,
                                    Verdict.DEFER, Code.MISSING_BAAB, self.provenance)

        # G1: a CANDIDATE root yields no weight evidence.
        if cert == CertLevel.CANDIDATE:
            return RootWaznEvidence(query, root, baab, cert, CertLevel.CANDIDATE,
                                    Verdict.REFUSED, Code.UNLICENSED_ROOT_TO_WEIGHT, self.provenance)

        # G2/G3: LICENSED, carried at EXACTLY its own cert rank (never promoted).
        rank = cert  # invariant enforced below
        assert rank <= cert, Code.RANK_PROMOTION_FORBIDDEN
        return RootWaznEvidence(query, root, baab, cert, rank,
                                Verdict.LICENSED, Code.OK, self.provenance)

    # G7: no backflow — any write into the root/wazn law is refused.
    def record_result_into_law(self, *args, **kwargs):
        raise BackflowForbiddenError(Code.NO_BACKFLOW)
