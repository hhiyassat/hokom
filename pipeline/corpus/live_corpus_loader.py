"""
Safe corpus loader for HOKOM-TAAQOL-SGA-LIVE-CORPUS-EXPANSION-01.

Adapted for the actual corpus schema (target_surface field, corpus-specific
routing oracle values, section names A_COMPOUND_CLITICS / B_WEAK_VERBS /
C_H11_H15_LIVE / D_AMBIGUITY_CONTROLS).

Hints (root_hint, lemma_hint, weak_class, notes) are NEVER used as
runtime evidence.  They are stored on private (_-prefixed) fields and
must not be passed to any pipeline call.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


# ── Routing-oracle values as they appear in the actual corpus ─────────────────

KNOWN_ROUTING_ORACLES: frozenset[str] = frozenset({
    # Actual corpus values
    "SEGMENT_CLITICS_THEN_POST_SEGMENTATION_MORPHOLOGY",
    "POST_SEGMENTATION_MORPHOLOGY_TO_H11_H15",
    "POST_SEGMENTATION_MORPHOLOGY_PRESERVE_CANDIDATE_SET",
    "SEGMENTATION_AMBIGUITY_THEN_TYPED_MORPHOLOGY",
    # Expanded-corpus / spec values (kept for forward compatibility)
    "OPEN_MORPHOLOGY",
    "CLOSED_BOUNDARY",
    "HAS_PROCLITIC",
    "HAS_ENCLITIC",
    "HAS_ARTICLE",
    "SOLAR",
    "LUNAR",
    "HOLLOW_WAW",
    "HOLLOW_YA",
    "DEFECTIVE_WAW",
    "DEFECTIVE_YA",
    "INITIAL_WAW",
    "INITIAL_YA",
    "GEMINATED",
    "LAFIF",
    "AMBIGUOUS_ROOT",
    "AMBIGUOUS_DERIVATIVE",
    "AMBIGUOUS_H13",
    "AMBIGUOUS_BAB",
})

VALID_VERDICT_CLASSES: frozenset[str] = frozenset({
    "LICENSED", "DEFERRED", "BLOCKED", "RESIDUAL",
    "AMBIGUOUS", "OPEN", "UNDERLICENSED", "UNKNOWN",
    # Taaqol / hokom effective-verdict strings
    "ACCEPT", "DEFER", "BLOCK", "RESIDUAL", "AMBIGUOUS",
})

KNOWN_SECTIONS: frozenset[str] = frozenset({
    "A_COMPOUND_CLITICS",
    "B_WEAK_VERBS",
    "C_H11_H15_LIVE",
    "D_AMBIGUITY_CONTROLS",
    # spec section names kept for forward compatibility
    "COMPOUND_CLITIC",
    "WEAK_VERB",
    "H11_H15_PRIMARY",
    "AMBIGUITY_CONTROL",
})


@dataclass(frozen=True)
class CorpusCase:
    case_id: str
    corpus_id: str
    baseline_head: str
    # Pipeline input — the ONLY field fed to hokom()
    surface: str
    section: str
    routing_oracle: str
    expected_verdict_class: str
    h11_h15_live: bool
    ambiguity_expected: bool
    negative_control: bool
    segmentation_sensitive: bool
    min_candidate_count: Optional[int]
    proclitics_expected: Optional[str]   # reporting-only
    host_expected: Optional[str]         # reporting-only
    enclitics_expected: Optional[str]    # reporting-only
    assertions: tuple
    allowed_verdicts: tuple
    # Hints — reporting / audit only, NEVER passed to the pipeline
    _weak_class_hint: Optional[str]
    _lemma_hint: Optional[str]
    _root_hint: Optional[str]
    _notes: str
    _h11_h15_contract: str
    _original_record: dict = field(compare=False, hash=False)

    @property
    def routing_oracles(self) -> frozenset[str]:
        """Pipe-separated oracle string → frozenset."""
        return frozenset(
            part.strip()
            for part in self.routing_oracle.split("|")
            if part.strip()
        )


@dataclass
class CorpusValidationResult:
    is_valid: bool
    case_count: int
    unique_ids: int
    violations: list[str] = field(default_factory=list)
    h11_h15_flagged_ids: list[str] = field(default_factory=list)
    ambiguity_expected_ids: list[str] = field(default_factory=list)
    negative_control_ids: list[str] = field(default_factory=list)
    segmentation_sensitive_ids: list[str] = field(default_factory=list)


def load_corpus(path: str | Path) -> tuple[list[CorpusCase], CorpusValidationResult]:
    """
    Load and validate the 150-case live corpus.

    Returns (cases, validation_result).

    INVARIANT: root_hint, lemma_hint, weak_class, notes are stored on
    private fields and must never be injected into the pipeline.
    """
    path = Path(path)
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    violations: list[str] = []

    # ── Header checks ─────────────────────────────────────────────────────────

    if raw.get("historical_ayat_al_dayn_counted") is not False:
        violations.append("AYAT_AL_DAYN_COUNTED_MUST_BE_FALSE")

    if raw.get("corpus_id") != "HOKOM-TAAQOL-SGA-LIVE-CORPUS-EXPANSION-01":
        violations.append(
            f"WRONG_CORPUS_ID: {raw.get('corpus_id')}"
        )

    # total_cases may be top-level or nested under coverage
    coverage = raw.get("coverage") or {}
    declared_total = raw.get("total_cases") or coverage.get("total_cases")

    # ── Parse cases ───────────────────────────────────────────────────────────

    cases_raw = raw.get("cases", [])
    seen_ids: dict[str, int] = {}
    cases: list[CorpusCase] = []
    h11_flagged: list[str] = []
    ambig_flagged: list[str] = []
    neg_ctrl: list[str] = []
    seg_sensitive: list[str] = []

    for i, rec in enumerate(cases_raw):
        case_id = rec.get("case_id", f"MISSING_ID_{i}")

        # Duplicate ID
        if case_id in seen_ids:
            violations.append(
                f"DUPLICATE_ID: {case_id} (indices {seen_ids[case_id]}, {i})"
            )
        seen_ids[case_id] = i

        # corpus_id consistency
        if rec.get("corpus_id") != raw.get("corpus_id"):
            violations.append(f"CORPUS_ID_MISMATCH: {case_id}")

        # surface — actual corpus uses target_surface
        surface = rec.get("target_surface") or rec.get("surface") or ""
        if not surface:
            violations.append(f"MISSING_SURFACE: {case_id}")

        # routing oracle validation
        routing = rec.get("routing_oracle", "")
        for part in routing.split("|"):
            part = part.strip()
            if part and part not in KNOWN_ROUTING_ORACLES:
                violations.append(f"UNKNOWN_ROUTING_ORACLE: {case_id}.{part}")

        # section
        section = rec.get("section", "")
        if section not in KNOWN_SECTIONS:
            violations.append(f"UNKNOWN_SECTION: {case_id}.{section}")

        # Boolean fields
        h11 = rec.get("h11_h15_live") == "YES"
        ambig = rec.get("ambiguity_expected") == "YES"
        neg = rec.get("negative_control") == "YES"
        seg_sens = rec.get("segmentation_sensitive") == "YES"

        if h11:
            h11_flagged.append(case_id)
        if ambig:
            ambig_flagged.append(case_id)
        if neg:
            neg_ctrl.append(case_id)
        if seg_sens:
            seg_sensitive.append(case_id)

        # min_candidate_count — may be empty string or int
        raw_min = rec.get("min_candidate_count", "")
        try:
            min_cand = int(raw_min) if raw_min != "" and raw_min is not None else None
        except (ValueError, TypeError):
            min_cand = None

        # allowed_verdicts — pipe-separated string
        av_raw = rec.get("allowed_verdicts", "")
        allowed_v = tuple(v.strip() for v in av_raw.split("|") if v.strip())

        # required_assertions
        ra_raw = rec.get("required_assertions", "")
        assertions = tuple(a.strip() for a in ra_raw.split(";") if a.strip())

        c = CorpusCase(
            case_id=case_id,
            corpus_id=rec.get("corpus_id", ""),
            baseline_head=rec.get("baseline_head", raw.get("baseline_head", "")),
            surface=surface,
            section=section,
            routing_oracle=routing,
            expected_verdict_class="OPEN",
            h11_h15_live=h11,
            ambiguity_expected=ambig,
            negative_control=neg,
            segmentation_sensitive=seg_sens,
            min_candidate_count=min_cand,
            proclitics_expected=rec.get("proclitics_expected"),
            host_expected=rec.get("host_expected"),
            enclitics_expected=rec.get("enclitics_expected"),
            assertions=assertions,
            allowed_verdicts=allowed_v,
            _weak_class_hint=rec.get("weak_class") or None,
            _lemma_hint=rec.get("lemma_hint") or None,
            _root_hint=rec.get("root_hint") or None,
            _notes=rec.get("notes", ""),
            _h11_h15_contract=rec.get("h11_h15_contract", ""),
            _original_record=rec,
        )
        cases.append(c)

    # Count check
    if declared_total is not None and len(cases) != declared_total:
        violations.append(
            f"CASE_COUNT_MISMATCH: declared={declared_total} actual={len(cases)}"
        )

    result = CorpusValidationResult(
        is_valid=len(violations) == 0,
        case_count=len(cases),
        unique_ids=len(seen_ids),
        violations=violations,
        h11_h15_flagged_ids=h11_flagged,
        ambiguity_expected_ids=ambig_flagged,
        negative_control_ids=neg_ctrl,
        segmentation_sensitive_ids=seg_sensitive,
    )

    return cases, result
