"""
Live execution runner for HOKOM-TAAQOL-SGA-LIVE-CORPUS-EXPANSION-01.

Runs every case through the actual Hokom pipeline via hokom().
No mocking.  No hint injection.  No silent fallback.

INVARIANT: case._root_hint, case._lemma_hint, case._weak_class_hint
are never accessed inside run_case().  The only pipeline input is
case.surface.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from pipeline.corpus.live_corpus_loader import CorpusCase


# ── Routing-oracle → actual routing class map ─────────────────────────────────

_ORACLE_CLITIC_SEGMENT = "SEGMENT_CLITICS_THEN_POST_SEGMENTATION_MORPHOLOGY"
_ORACLE_H11_H15 = "POST_SEGMENTATION_MORPHOLOGY_TO_H11_H15"
_ORACLE_PRESERVE = "POST_SEGMENTATION_MORPHOLOGY_PRESERVE_CANDIDATE_SET"
_ORACLE_AMBIG = "SEGMENTATION_AMBIGUITY_THEN_TYPED_MORPHOLOGY"


@dataclass
class CaseResult:
    case_id: str
    surface: str
    section: str
    evaluation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Raw pipeline output dict
    hokom_result: Optional[dict] = None

    # Segmentation (from hokom output)
    segment_host: Optional[str] = None
    segment_proclitics: tuple = field(default_factory=tuple)
    segment_enclitics: tuple = field(default_factory=tuple)
    article_present: bool = False

    # Morphological
    word_class: Optional[str] = None
    root_str: Optional[str] = None          # extracted string from RootCandidate
    root_directive: Optional[str] = None    # DEFER / ACCEPT / BLOCK
    final_root: Optional[str] = None
    final_wazn: Optional[str] = None

    # Boundary / routing
    morphology_blocked: bool = False
    boundary_type: Optional[str] = None
    routing_actual: Optional[str] = None
    routing_oracle_match: bool = False
    routing_oracle_miss_reason: Optional[str] = None

    # SGA bundle
    claim_key: Optional[str] = None
    typed_slot_count: int = 0
    ambiguous_slots: list[str] = field(default_factory=list)
    h11_h15_slots_reached: list[str] = field(default_factory=list)

    # Taaqol
    taaqol_effective_verdict: Optional[str] = None
    taaqol_verdict: Optional[str] = None
    taaqol_active: bool = False
    taaqol_gate_executed: bool = False
    taaqol_trace_count: int = 0
    taaqol_failure_code: Optional[str] = None

    # Segmentation assertions (populated for A_COMPOUND_CLITICS cases)
    seg_clitic_chain_match: Optional[bool] = None
    seg_host_match: Optional[bool] = None

    # Inflectional analysis gate (populated from hokom_result)
    # True when hokom sets inflection_skipped_reason (WORD_CLASS_DEFERRED /
    # WORD_CLASS_ACCEPTED / WORD_CLASS_BLOCKED), meaning the pipeline
    # constitutionally cannot populate H11-H15 derivative slots.
    inflection_skipped: bool = False

    # Performance
    latency_ms: float = 0.0

    # Error tracking
    error: Optional[str] = None
    error_class: str = "NONE"
    # NONE | SEGMENTATION_DEFECT | ROUTING_DEFECT | IMPLEMENTATION_DEFECT
    # | UNDERLICENSED | EVIDENCE_GAP | UNSUPPORTED_CASE | BUNDLE_BUILD_DEFECT


def _extract_root_string(rc) -> tuple[Optional[str], Optional[str]]:
    """
    Extract (root_str, directive) from a RootCandidate object or raw string.
    Never raises; returns (None, None) on failure.
    """
    if rc is None:
        return None, None
    if isinstance(rc, str):
        return rc or None, None
    # RootCandidate object
    directive = None
    root_str = None
    if hasattr(rc, "directive"):
        directive = str(rc.directive) if rc.directive else None
    if hasattr(rc, "canonical_root") and rc.canonical_root is not None:
        root_str = str(rc.canonical_root)
    elif hasattr(rc, "surface") and rc.surface:
        root_str = None  # surface is not the root
    return root_str, directive


def _build_bundle_dict(hr: dict) -> dict:
    """
    Distil the full hokom() result into the simplified dict that
    build_claim_bundle() accepts.  Only primitive types — no RootCandidate
    objects, no None-canonical_root chains.
    """
    # Root candidate → string (or absent if not resolved)
    rc = hr.get("root_candidate")
    root_str, _ = _extract_root_string(rc)

    # Proclitics / enclitics
    procs = list(hr.get("segment_proclitics") or hr.get("proclitics") or [])
    encs = list(hr.get("segment_enclitics") or hr.get("enclitics") or [])

    d: dict = {
        "word": hr.get("input_surface", ""),
        "segment_host": hr.get("segment_host") or hr.get("morphology_surface") or hr.get("input_surface", ""),
        "word_class": hr.get("word_class"),
        "wazn": hr.get("final_wazn"),
        "number": hr.get("number"),
        "gender": hr.get("gender"),
        "lemma": hr.get("lemma_surface"),
    }
    if root_str:
        d["root_candidate"] = root_str
    if procs:
        d["proclitics"] = procs
    if encs:
        d["enclitics"] = encs
    if hr.get("has_article") or hr.get("article"):
        d["article"] = True

    return d


def _determine_routing(hr: dict) -> str:
    """
    Classify the actual pipeline routing from a hokom() result.
    Returns one of the ORACLE_* strings used in reporting.
    """
    # Closed / mabni / jamid boundary
    pre_root = hr.get("pre_root")
    if pre_root is not None and hasattr(pre_root, "structural_type"):
        st = str(pre_root.structural_type)
        if "OPERATOR" in st or "MABNI" in st or "JAMID" in st:
            return "CLOSED_BOUNDARY"

    morphology_blocked = bool(hr.get("morphology_blocked"))
    if morphology_blocked:
        return "CLOSED_BOUNDARY"

    procs = hr.get("segment_proclitics") or hr.get("proclitics") or ()
    encs = hr.get("segment_enclitics") or hr.get("enclitics") or ()
    article = hr.get("has_article") or hr.get("article")

    if procs and encs:
        return _ORACLE_CLITIC_SEGMENT
    if procs:
        return _ORACLE_CLITIC_SEGMENT
    if encs:
        return "HAS_ENCLITIC"
    if article:
        return "HAS_ARTICLE"
    return _ORACLE_H11_H15


def _check_routing_oracle(case: CorpusCase, routing_actual: str) -> tuple[bool, Optional[str]]:
    """Return (match, miss_reason)."""
    declared = case.routing_oracles
    if not declared:
        return True, None
    if routing_actual in declared:
        return True, None
    # Loose match: if the declared oracle is the catch-all H11_H15 oracle and
    # actual is open morphology / segment, treat as match
    if (
        _ORACLE_H11_H15 in declared
        and routing_actual in (_ORACLE_H11_H15, _ORACLE_PRESERVE, _ORACLE_AMBIG, "OPEN_MORPHOLOGY")
    ):
        return True, None
    if (
        _ORACLE_CLITIC_SEGMENT in declared
        and routing_actual in (_ORACLE_CLITIC_SEGMENT, "HAS_PROCLITIC", "HAS_ENCLITIC", "HAS_ARTICLE")
    ):
        return True, None
    if (
        _ORACLE_PRESERVE in declared
        and routing_actual in (_ORACLE_PRESERVE, _ORACLE_H11_H15, _ORACLE_AMBIG)
    ):
        return True, None
    return False, f"declared={case.routing_oracle!r} actual={routing_actual!r}"


# H11-H15 slot IDs used to detect derivative / morphosyntactic output
_H11_H15_SLOT_NAMES: frozenset[str] = frozenset({
    "BAB_CANDIDATE_SET",
    "MASDAR_CANDIDATE_SET",
    "DERIVATIVE_CANDIDATE_SET",
    "NUMBER_SLOT",
    "GENDER_SLOT",
    "DEFINITENESS_SLOT",
    "NISBA_SLOT",
    "COLLECTIVE_SLOT",
    "UNIT_NOUN_SLOT",
    "LEMMA_SLOT",
    "PARADIGM_SLOT",
    "INFLECTIONAL_FAMILY_SLOT",
    "DERIVATIONAL_FAMILY_SLOT",
})


def run_case(case: CorpusCase) -> CaseResult:
    """
    Run one corpus case through the live Hokom pipeline.

    INPUT: case.surface — the only pipeline input.
    PROHIBITED: case._root_hint, case._lemma_hint, case._weak_class_hint
                must not be accessed here.
    """
    result = CaseResult(
        case_id=case.case_id,
        surface=case.surface,
        section=case.section,
    )
    t0 = time.perf_counter()

    try:
        import sys
        sys.path.insert(0, ".")
        from hokom_pipeline import hokom
        from pipeline.sga.adapters import build_claim_bundle
        from pipeline.sga.contracts import SlotId, SlotState

        # ── Step 1: Run the pipeline ──────────────────────────────────────
        hr = hokom(case.surface)
        result.hokom_result = hr if isinstance(hr, dict) else {}

        if not isinstance(hr, dict):
            result.error = f"hokom() returned {type(hr).__name__}, expected dict"
            result.error_class = "IMPLEMENTATION_DEFECT"
            result.latency_ms = (time.perf_counter() - t0) * 1000
            return result

        # ── Step 2: Extract segmentation ─────────────────────────────────
        result.segment_host = hr.get("segment_host")
        result.segment_proclitics = tuple(
            hr.get("segment_proclitics") or hr.get("proclitics") or ()
        )
        result.segment_enclitics = tuple(
            hr.get("segment_enclitics") or hr.get("enclitics") or ()
        )
        result.article_present = bool(hr.get("has_article") or hr.get("article"))

        # ── Step 3: Morphological extraction ─────────────────────────────
        result.word_class = hr.get("word_class")
        result.root_str, result.root_directive = _extract_root_string(
            hr.get("root_candidate")
        )
        result.final_root = hr.get("final_root")
        result.final_wazn = hr.get("final_wazn")
        result.morphology_blocked = bool(hr.get("morphology_blocked"))

        # inflection_skipped_reason: set by hokom when word-class analysis
        # cannot complete (DEFERRED / ACCEPTED-but-no-inflection / BLOCKED).
        # When True, the H11-H15 derivative stage is constitutionally
        # unreachable — treat as VALID_EARLY_STOP at the gate level.
        result.inflection_skipped = bool(hr.get("inflection_skipped_reason"))

        # ── Step 4: Routing ───────────────────────────────────────────────
        result.routing_actual = _determine_routing(hr)
        result.routing_oracle_match, result.routing_oracle_miss_reason = (
            _check_routing_oracle(case, result.routing_actual)
        )

        # ── Step 5: SGA bundle ────────────────────────────────────────────
        bundle_dict = _build_bundle_dict(hr)

        # Determine claim_kind from routing
        if result.morphology_blocked or result.routing_actual == "CLOSED_BOUNDARY":
            claim_kind = "WORD_CLASS_CLAIM"
        elif result.word_class in ("MABNI",):
            claim_kind = "FUNCTIONAL_OWNER_CLAIM"
        else:
            claim_kind = "ROOT_CLAIM"

        try:
            bundle = build_claim_bundle(bundle_dict, claim_kind, claim_kind)
            result.claim_key = bundle.claim_key
            result.typed_slot_count = len(bundle.typed_slots)

            result.ambiguous_slots = [
                s.slot_id.value
                for s in bundle.typed_slots
                if s.state == SlotState.AMBIGUOUS
            ]
            result.h11_h15_slots_reached = [
                s.slot_id.value
                for s in bundle.typed_slots
                if s.slot_id.value in _H11_H15_SLOT_NAMES and s.state == SlotState.FILLED
            ]
        except Exception as bundle_err:
            result.error = f"bundle_build: {type(bundle_err).__name__}: {bundle_err}"
            result.error_class = "BUNDLE_BUILD_DEFECT"
            # Do not abort — continue to Taaqol extraction

        # ── Step 6: Taaqol ────────────────────────────────────────────────
        rt = hr.get("taaqol_runtime") or {}
        result.taaqol_active = bool(rt.get("active", False))
        result.taaqol_gate_executed = bool(rt.get("gate_executed", False))
        result.taaqol_trace_count = int(rt.get("trace_event_count", 0))
        result.taaqol_failure_code = rt.get("failure_code")
        result.taaqol_effective_verdict = hr.get("taaqol_effective_verdict")
        result.taaqol_verdict = hr.get("taaqol_verdict")

        # ── Step 7: Segmentation assertions (A_COMPOUND_CLITICS) ─────────
        if case.section == "A_COMPOUND_CLITICS" and case.proclitics_expected is not None:
            expected_procs = [
                p.strip() for p in case.proclitics_expected.split("+") if p.strip()
            ]
            actual_procs = list(result.segment_proclitics)
            result.seg_clitic_chain_match = expected_procs == actual_procs

        if case.section == "A_COMPOUND_CLITICS" and case.host_expected is not None:
            expected_host = case.host_expected.strip()
            result.seg_host_match = (
                expected_host == (result.segment_host or "").strip()
            ) if expected_host else None

    except Exception as e:
        import traceback
        result.error = f"{type(e).__name__}: {e}"
        result.error_class = "IMPLEMENTATION_DEFECT"

    result.latency_ms = (time.perf_counter() - t0) * 1000
    return result


def run_corpus(cases: list[CorpusCase], runs: int = 3) -> list[list[CaseResult]]:
    """
    Run all corpus cases `runs` times for stability verification.
    Returns list-of-runs, each a list[CaseResult] parallel to `cases`.
    """
    all_runs: list[list[CaseResult]] = []
    for run_idx in range(runs):
        run_results: list[CaseResult] = []
        for case in cases:
            r = run_case(case)
            run_results.append(r)
        ok = sum(1 for r in run_results if not r.error)
        print(
            f"Run {run_idx + 1}/{runs}: {len(run_results)} cases, "
            f"{ok} ok, {len(run_results) - ok} errors"
        )
        all_runs.append(run_results)
    return all_runs
