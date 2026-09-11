"""CL-16 Phase 3 — Root-candidate chain (Hokom-side, read-only, artifact-bound).

WHY THIS STAGE EXISTS
---------------------
Phase 1 is keyed by a *root*: `assess("قتل")`. Nothing in CL-16 produced a root
from a surface, so the law had a head with no neck. This module is that neck —
and only that. It answers one question:

    given a query, is there a *candidate* root, and what is that candidate's
    evidence rank once every named source has been read within its own limit?

It is an evidence chain, not a root prover. `ROOT_PROVEN` is never emitted.

THE OWNER'S ARCHITECTURE (verbatim)
-----------------------------------
    «ليس أن ننقل كل هذه المشاريع داخل Hokom، ولا أن نغيّر Taaqol.
     الصحيح أن نجعلها مصادر أدلة مجمّدة: نثبت ملفاتها المهمة بالبصمة،
     ثم يقرأها Hokom عبر وسيط صغير، ويمنع أي ترقية غير مأذونة.»

Each source carries a ROLE and a LIMIT, and is never read past its limit:

    abo-fareed-8-2026   role: قانون مرشح للجذر     limit: لا يثبت الجذر ولا يعطي وزنًا
    maqayis_v2          role: معجم جذور            limit: ليس قانون وزن
    audited_roots.csv   role: جدول اعتماد          limit: يحتاج حارس رتبة مصدر
    Arabic-Mother-…-net role: مصدر الجذر والباب    limit: لا يغلق الوزن وحده
    …-wazn-net          role: مصدر قانون الوزن     limit: لا يستخرج الجذر من السطح وحده

BOUNDARY DISCIPLINE
-------------------
  * Reads ONLY sha256-pinned artifacts (phase3_manifest.json + Phase-1's).
  * NO git, NO network, NO live read of any source repository.
  * Imports NO source-repo module — not the extractor, not maqayis_v2's adapter.
    The extractor's frozen OUTPUT is consumed; the extractor is never re-run.
  * Does NOT import taaqqul_slot_geometry / vendor / Taaqol.  Never calls weigh().
  * FAIL-CLOSED. A missing artifact or a drifted sha256 is a hard BLOCK.
    (maqayis_v2_adapter.py declares the opposite — «خطأ في المعجم لا يوقف
     الـ pipeline أبداً» — which is why it is pinned but never imported.)
  * Read-only: no backflow from Hokom into any source law.

RANK ALGEBRA
------------
    CORROBORATION_NEVER_RAISES_RANK
        Rank comes from the certification source alone (audited_roots, via
        Phase 1). Candidacy and lexicon presence are corroboration: each may
        lower the verdict to DEFER; neither may raise the rank by one step.

    SKELETON_MATCH_IS_NOT_A_ROOT_PROOF
        The extractor works on consonantal skeletons and cannot know whether
        the surface it generalised was a particle. A skeleton that matches a
        form in Hokom's own closed inventory is DEFER, never LICENSED.

This module does NOT close CL-16.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sqlite3
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
_P1_DIR = _HERE.parent / "phase1"
_MANIFEST = _HERE / "phase3_manifest.json"

#: CL-16 is NOT closed by this module. Asserted by the tests.
CL16_CLOSED = False

sys.path.insert(0, str(_P1_DIR))
import root_wazn_evidence_adapter as P1  # noqa: E402

CertLevel = P1.CertLevel
Verdict = P1.Verdict


class ArtifactIntegrityError(P1.ArtifactIntegrityError):
    """Raised (BLOCK) when a Phase-3 pinned artifact is missing or drifted."""


class SourceLimitError(Exception):
    """Raised (BLOCK) when a source is asked for something its LIMIT forbids."""


class BackflowForbiddenError(P1.BackflowForbiddenError):
    """Raised (BLOCK) on any attempt to write back into a source law."""


class ChainCode:
    OK = "OK"
    # ── integrity / boundary (BLOCK) ──
    ARTIFACT_MISSING = "ARTIFACT_MISSING"
    ARTIFACT_SHA_MISMATCH = "ARTIFACT_SHA_MISMATCH"
    SUMMARY_SELF_HASH_MISMATCH = "SUMMARY_SELF_HASH_MISMATCH"
    SOURCE_BEYOND_ITS_LIMIT = "SOURCE_BEYOND_ITS_LIMIT"
    FORBIDDEN_AUTHORITY = "FORBIDDEN_AUTHORITY"
    NO_BACKFLOW = "NO_BACKFLOW"
    RANK_PROMOTION_FORBIDDEN = "RANK_PROMOTION_FORBIDDEN"
    # ── chain outcomes (DEFER) ──
    NOT_A_CANDIDATE = "NOT_A_CANDIDATE"
    CANDIDATE_DEFERRED_BY_EXTRACTOR = "CANDIDATE_DEFERRED_BY_EXTRACTOR"
    CLOSED_FORM_COLLISION = "CLOSED_FORM_COLLISION"
    NOT_IN_LEXICON = "NOT_IN_LEXICON"
    NOT_CERTIFIED = "NOT_CERTIFIED"


#: What each source may NOT be asked for. Asking is a BLOCK, not a DEFER:
#: a DEFER admits an incomplete argument; this is a category error.
SOURCE_LIMITS = {
    "ROOT_CANDIDATE_SOURCE": frozenset({"root_proof", "wazn"}),
    "MAQAYIS_LEXICON_SOURCE": frozenset({"wazn", "baab"}),
}

_FORBIDDEN_SOURCES = P1._FORBIDDEN_SOURCES


def strip_marks(text: str) -> str:
    """Consonantal skeleton — combining marks removed. Never used as a proof."""
    return "".join(c for c in text if not unicodedata.combining(c)).strip()


@dataclass(frozen=True)
class RootCandidateEvidence:
    query: str
    candidate: Optional[str]
    root: Optional[str]
    baab: Optional[str]
    rank: CertLevel
    verdict: str
    reason_code: str
    #: every link that was actually read, in order, with what it contributed
    chain: tuple = field(default_factory=tuple)
    provenance: tuple = field(default_factory=tuple)


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(manifest_path: Path = _MANIFEST) -> dict:
    return json.loads(Path(manifest_path).read_text(encoding="utf-8"))


def resolve(path: str, manifest: dict) -> str:
    """Map a pinned host path onto this machine.

    The manifest pins ABSOLUTE host paths — that is deliberate: a pin that
    moves is not a pin. But the same frozen artifacts are sometimes reachable
    under a different mount (a checkout, a review sandbox). `CL16_SOURCE_ROOT`
    declares that mount EXPLICITLY; it is never guessed, and it changes nothing
    else: the sha256 of every artifact is still verified, so a wrong root is a
    hard ARTIFACT_MISSING rather than a quiet substitution.
    """
    root = os.environ.get("CL16_SOURCE_ROOT")
    host = manifest.get("host_root", "/Users/husseinhiyassat/")
    if root and path.startswith(host):
        return os.path.join(root.rstrip("/") + "/", path[len(host):])
    return path


def verify_artifacts(manifest: Optional[dict] = None) -> list[tuple[str, str]]:
    """Verify every Phase-3 pinned artifact. BLOCK (raise) on missing/mismatch."""
    manifest = manifest or load_manifest()
    provenance: list[tuple[str, str]] = []
    for art in manifest["artifacts"]:
        p = resolve(art["path"], manifest)
        if not os.path.isfile(p):
            raise ArtifactIntegrityError(f"{ChainCode.ARTIFACT_MISSING}: {art['role']} @ {p}")
        actual = _sha256(p)
        if actual != art["sha256"]:
            raise ArtifactIntegrityError(
                f"{ChainCode.ARTIFACT_SHA_MISMATCH}: {art['role']} "
                f"expected {art['sha256'][:12]} got {actual[:12]}"
            )
        provenance.append((art["role"], actual[:12]))
    return provenance


def _artifact(manifest: dict, role: str) -> dict:
    for a in manifest["artifacts"]:
        if a["role"] == role:
            return a
    raise ArtifactIntegrityError(f"{ChainCode.ARTIFACT_MISSING}: role {role} not in manifest")


class RootCandidateChain:
    """Read-only chain: candidate → lexicon presence → certification (+باب).

    Construction verifies BOTH manifests. A drift anywhere refuses the object,
    so a caller can never hold a chain bound to artifacts it did not verify.
    """

    def __init__(self, manifest_path: Path = _MANIFEST,
                 closed_form_catalogs: Optional[list[Path]] = None):
        self.manifest = load_manifest(manifest_path)
        self.provenance = tuple(verify_artifacts(self.manifest))
        # Phase 1 verifies its own pinned artifacts on construction.
        self.p1 = P1.RootWaznEvidenceAdapter(self._phase1_manifest_path())
        self.provenance += self.p1.provenance

        self._candidates = self._load_candidates()
        self._verify_summary_self_hash()
        self._db_path = resolve(
            P1._artifact(self.p1.manifest, "MAQAYIS_LEXICON_DB")["path"], self.manifest)
        self._closed_forms = self._load_closed_forms(closed_form_catalogs)

    def _phase1_manifest_path(self) -> Path:
        """Phase 1's manifest, re-pathed ONLY under an explicit alternate mount.

        With `CL16_SOURCE_ROOT` unset — the normal case, and the case on the
        owner's machine — this returns Phase 1's manifest untouched, so Phase 1
        behaves exactly as it does standalone. When the variable IS set, the
        paths are rewritten in a temp copy and **every sha256 is carried over
        verbatim from Phase 1's own manifest**: no hash is recomputed here, so
        this can relax an integrity check but never fabricate one.
        """
        p1_manifest = _P1_DIR / "artifact_manifest.json"
        if not os.environ.get("CL16_SOURCE_ROOT"):
            return p1_manifest
        import tempfile
        m = json.loads(p1_manifest.read_text(encoding="utf-8"))
        m.setdefault("host_root", self.manifest.get("host_root", "/Users/husseinhiyassat/"))
        for art in m["artifacts"]:
            art["path"] = resolve(art["path"], m)
        tmp = Path(tempfile.mkdtemp(prefix="cl16_p1_")) / "artifact_manifest.json"
        tmp.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        return tmp

    # ── link 0: the extractor's own self-declared hash of its own table ──
    def _verify_summary_self_hash(self) -> None:
        """The run summary declares the sha256 of the candidate table it wrote.

        Cross-checking it costs nothing and catches the one drift a manifest
        cannot: a table and a summary re-pinned from two different runs.
        """
        summary = json.loads(
            Path(resolve(_artifact(self.manifest, "ROOT_CANDIDATE_RUN_SUMMARY")["path"],
                         self.manifest)).read_text(encoding="utf-8"))
        declared = summary.get("outputs", {}).get("ROOT_CANDIDATES.csv", {}).get("sha256")
        pinned = _artifact(self.manifest, "ROOT_CANDIDATE_TABLE")["sha256"]
        if declared and declared != pinned:
            raise ArtifactIntegrityError(
                f"{ChainCode.SUMMARY_SELF_HASH_MISMATCH}: summary says {declared[:12]}, "
                f"manifest pins {pinned[:12]}")
        self.run_summary = summary

    def _load_candidates(self) -> dict:
        path = resolve(_artifact(self.manifest, "ROOT_CANDIDATE_TABLE")["path"],
                       self.manifest)
        out: dict[str, dict] = {}
        with open(path, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                out[strip_marks(row["candidate"])] = row
        return out

    def _load_closed_forms(self, paths: Optional[list[Path]]) -> frozenset:
        """Hokom's own closed inventory — the only non-pinned input, and it is
        Hokom's own, not a source repo's. Absent catalogs mean the guard has no
        witness; that is declared in `closed_form_witness`, never silently
        treated as 'no collision'."""
        if paths is None:
            hokom = _HERE.parent.parent
            paths = [hokom / "mabniyat_catalog_split_vocalized.csv",
                     hokom / "operators_catalog_split_vocalized.csv"]
        forms: set[str] = set()
        found = []
        for p in paths:
            if not Path(p).is_file():
                continue
            found.append(Path(p).name)
            with open(p, encoding="utf-8-sig", newline="") as fh:
                for row in csv.DictReader(fh):
                    if str(row.get("blocks_root_path", "")).strip() == "True":
                        forms.add(strip_marks(row.get("surface_bare", "")))
                    if row.get("Operator"):
                        forms.add(strip_marks(row["Operator"]))
        self.closed_form_witness = tuple(found)
        forms.discard("")
        return frozenset(forms)

    # ── link 2: lexicon presence, read-only over the pinned DB ──
    def in_lexicon(self, root: str) -> bool:
        uri = f"file:{self._db_path}?mode=ro"
        con = sqlite3.connect(uri, uri=True)
        try:
            q = strip_marks(root)
            for col in ("root_letters", "root_display"):
                cur = con.execute(
                    f"SELECT 1 FROM entries WHERE replace(replace({col},' ',''),'ـ','') = ? LIMIT 1",
                    (q,))
                if cur.fetchone():
                    return True
            # marks in the stored value are stripped in Python, not in SQL
            for col in ("root_letters", "root_display"):
                for (val,) in con.execute(f"SELECT {col} FROM entries WHERE {col} IS NOT NULL"):
                    if strip_marks(val) == q:
                        return True
            return False
        finally:
            con.close()

    # ── the chain ──
    def assess(self, query: str, *, source: str = "root_candidate_chain",
               asking_for: str = "root_candidate") -> RootCandidateEvidence:
        prov = self.provenance
        skel = strip_marks(query)

        if source.lower() in _FORBIDDEN_SOURCES:
            return RootCandidateEvidence(query, None, None, None, CertLevel.CANDIDATE,
                                         Verdict.BLOCK, ChainCode.FORBIDDEN_AUTHORITY,
                                         (), prov)
        for src, forbidden in SOURCE_LIMITS.items():
            if asking_for in forbidden:
                raise SourceLimitError(
                    f"{ChainCode.SOURCE_BEYOND_ITS_LIMIT}: {src} may not be asked for "
                    f"'{asking_for}'")

        chain: list[tuple[str, str]] = []

        # link 1 — candidacy (abo-fareed). Contributes identity, never rank.
        row = self._candidates.get(skel)
        if row is None:
            return RootCandidateEvidence(query, None, None, None, CertLevel.CANDIDATE,
                                         Verdict.DEFER, ChainCode.NOT_A_CANDIDATE,
                                         tuple(chain), prov)
        if row["verdict"] != "ROOT_CANDIDATE":
            chain.append(("ROOT_CANDIDATE_SOURCE", row["verdict"]))
            return RootCandidateEvidence(query, skel, None, None, CertLevel.CANDIDATE,
                                         Verdict.DEFER,
                                         ChainCode.CANDIDATE_DEFERRED_BY_EXTRACTOR,
                                         tuple(chain), prov)
        chain.append(("ROOT_CANDIDATE_SOURCE", "ROOT_CANDIDATE(NOT_A_PROVEN_ROOT)"))

        # guard — a skeleton that is also a closed form is never a root here.
        if skel in self._closed_forms:
            chain.append(("HOKOM_CLOSED_INVENTORY", "COLLISION"))
            return RootCandidateEvidence(query, skel, None, None, CertLevel.CANDIDATE,
                                         Verdict.DEFER, ChainCode.CLOSED_FORM_COLLISION,
                                         tuple(chain), prov)

        # link 2 — lexicon presence (maqayis). Corroboration only.
        if not self.in_lexicon(skel):
            chain.append(("MAQAYIS_LEXICON_SOURCE", "ABSENT"))
            return RootCandidateEvidence(query, skel, None, None, CertLevel.CANDIDATE,
                                         Verdict.DEFER, ChainCode.NOT_IN_LEXICON,
                                         tuple(chain), prov)
        chain.append(("MAQAYIS_LEXICON_SOURCE", "PRESENT(PRESENCE_ONLY)"))

        # link 3 — certification + باب (Phase 1 over audited_roots). Sets rank.
        ev = self.p1.assess(skel)
        chain.append(("ROOT_PROOF_TABLE", f"{ev.verdict}:{ev.reason_code}"))
        if ev.verdict != Verdict.LICENSED:
            return RootCandidateEvidence(query, skel, ev.root, ev.baab,
                                         CertLevel.CANDIDATE, Verdict.DEFER,
                                         ev.reason_code if ev.verdict == Verdict.DEFER
                                         else ChainCode.NOT_CERTIFIED,
                                         tuple(chain), prov)

        # CORROBORATION_NEVER_RAISES_RANK — the rank is Phase 1's, unchanged.
        rank = ev.rank
        if rank > ev.cert_level:
            raise AssertionError(ChainCode.RANK_PROMOTION_FORBIDDEN)
        return RootCandidateEvidence(query, skel, ev.root, ev.baab, rank,
                                     Verdict.LICENSED, ChainCode.OK,
                                     tuple(chain), prov)

    # no backflow — any write into a source law is refused.
    def record_result_into_law(self, *args, **kwargs):
        raise BackflowForbiddenError(ChainCode.NO_BACKFLOW)
