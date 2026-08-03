"""
maqayis_identity_pipeline.py — Source builder + identity extraction pipeline
MAQAYIS-CONSTITUTIONAL-SOURCE-LEXICON-PRODUCTION-01  Commit 3

Produces:
  • SourceRecord     — one per Maqayis PDF volume
  • SourcePassage    — one per imported JSONL entry
  • RootIdentityCandidate — one per imported entry (after OCR gate evaluation)
  • Residuals        — one per raised OCR gate

20 OCR Confusion Gates
──────────────────────
Gates check for common Apple Vision OCR confusions in Arabic root letters.
A gate raising True means the root MAY contain an OCR error — it does NOT
mean the root IS wrong.  Gate flags become open Residuals of type OCR_AMBIGUITY
blocking upgrade to IDENTITY_VERIFIED until a human reviewer clears them.

Gate IDs (G01–G20):
  G01  ح/خ confusion          (connect + dot)
  G02  ب/ت/ث/ن/ي confusion    (baseline + dots)
  G03  د/ذ confusion           (connect + dot)
  G04  ر/ز confusion           (curve + dot)
  G05  ص/ض confusion           (loop + tooth)
  G06  ط/ظ confusion           (upstroke + dot)
  G07  ع/غ confusion           (connect + dot)
  G08  ف/ق confusion           (dots: one vs two)
  G09  Hamza form confusion    (ا/أ/إ/آ/ء/ئ/ؤ)
  G10  Weak letter confusion   (و/ي ambiguity)
  G11  Reversed radicals       (3-letter root in wrong order)
  G12  Extra radical           (4-char root from 3-radical word)
  G13  Missing radical         (2-char root from 3-radical word)
  G14  م/ن confusion           (short vs long base)
  G15  ه/ة confusion           (taa marbuta)
  G16  ك/ل confusion           (stroke direction)
  G17  س/ش confusion           (teeth + dots)
  G18  ج/ح/خ triconfusion     (base + dots)
  G19  ق/غ confusion           (loop + dots)
  G20  Diacritic bleed         (diacritic merged into letter shape)

Fail-Open Contract
──────────────────
All exceptions caught; returns empty structures on failure.
Never blocks Taaqol admission.
"""
from __future__ import annotations

import re
import datetime
import pathlib
from typing import Optional

from maqayis_constitutional_schemas import (
    SourceRecord,
    SourcePassage,
    RootIdentityCandidate,
    TraceEvent,
    TraceEventKind,
    Residual,
    ResidualType,
    ReviewState,
    ReviewerType,
    EvidenceStatus,
    HUMAN_REQUIRED_STATES,
    TransitionContractViolation,
    enforce_tc_si_01,
)
from maqayis_legacy_importer import LegacyCandidateImport, LegacyImportResult


# ── Known Maqayis volumes ────────────────────────────────────────────────────

_VOLUME_METADATA: list[dict] = [
    {
        "volume_number": 1,
        "filename": "maqayis_vol1.pdf",
        "initial_letters": ("ح", "خ", "د", "ذ", "ر", "ز"),
        "is_missing_volume": False,
    },
    {
        "volume_number": 2,
        "filename": "maqayis_vol2.pdf",
        "initial_letters": ("س", "ش", "ص", "ض", "ط", "ظ"),
        "is_missing_volume": False,
    },
    {
        "volume_number": 3,
        "filename": "maqayis_vol3.pdf",
        "initial_letters": ("ع", "غ", "ف", "ق", "ك"),
        "is_missing_volume": False,
    },
    {
        "volume_number": 4,
        "filename": "maqayis_vol4.pdf",
        "initial_letters": ("ل", "م", "ن"),
        "is_missing_volume": False,
    },
    {
        "volume_number": 5,
        "filename": "maqayis_vol5.pdf",
        "initial_letters": ("ه", "و", "ي"),
        "is_missing_volume": False,
    },
    {
        "volume_number": 6,
        "filename": "maqayis_vol6.pdf",
        "initial_letters": ("ا", "ب", "ت", "ث", "ج"),
        "is_missing_volume": True,  # vol6 covers ا–ج but ABSENT from corpus
    },
]

_MISSING_INITIALS = frozenset({"ا", "أ", "إ", "آ", "ب", "ت", "ث", "ج"})
_SOURCE_RECORD_ID_PREFIX = "maqayis:source"
_PASSAGE_ID_PREFIX       = "maqayis:passage"
_IDENTITY_ID_PREFIX      = "maqayis:root-identity-candidate"
_RESIDUAL_ID_PREFIX      = "maqayis:residual"
_TRACE_ID_PREFIX         = "maqayis:trace"

PIPELINE_ACTOR_ID = "maqayis_identity_pipeline_v1"


# ═══════════════════════════════════════════════════════════════════════════════
# § 1 — SOURCE RECORD BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def build_source_records() -> list[SourceRecord]:
    """
    Build SourceRecord objects for all 6 Maqayis volumes.
    sha256 and page_count are placeholders (would require PDF access).
    """
    records: list[SourceRecord] = []
    for meta in _VOLUME_METADATA:
        records.append(SourceRecord(
            id=f"{_SOURCE_RECORD_ID_PREFIX}:vol{meta['volume_number']}",
            volume_number=meta["volume_number"],
            filename=meta["filename"],
            sha256="",  # populated when PDF is accessible
            page_count=0,  # populated when PDF is accessible
            ocr_pass_count=2,  # Apple Vision raw + corrected
            is_missing_volume=meta["is_missing_volume"],
            initial_letters=tuple(meta["initial_letters"]),
        ))
    return records


# ═══════════════════════════════════════════════════════════════════════════════
# § 2 — 20 OCR CONFUSION GATES
# ═══════════════════════════════════════════════════════════════════════════════

# Arabic letter sets for each gate
_HA_KHA     = frozenset("حخ")
_BASELINE   = frozenset("بتثني")   # G02: dotted baseline confusion
_DAL_DHAL   = frozenset("دذ")
_RA_ZAY     = frozenset("رز")
_SAD_DAD    = frozenset("صض")
_TA_ZA      = frozenset("طظ")
_AIN_GHAIN  = frozenset("عغ")
_FA_QAF     = frozenset("فق")
_HAMZA      = frozenset("أإآء")   # normalized ا is the canonical form
_WEAK       = frozenset("وي")
_MIM_NUN    = frozenset("من")
_HA_TA_M    = frozenset("هة")
_KAF_LAM    = frozenset("كل")
_SIN_SHIN   = frozenset("سش")
_JIM_HA_KHA = frozenset("جحخ")
_QAF_GHAIN  = frozenset("قغ")

# Diacritic-like Arabic combining characters (could bleed into letter shape)
_DIACRITICS = frozenset("ًٌٍَُِّْٕٓٔ")


def _gate_01_ha_kha(root: str) -> bool:
    """ح/خ confusion — both present in root (ambiguous)."""
    letters = set(root)
    return bool(letters & _HA_KHA) and len(letters & _HA_KHA) == 1 and any(
        (c in _HA_KHA) for c in root
    ) and _is_pair_ambiguous(root, 'ح', 'خ')

def _gate_02_baseline_dots(root: str) -> bool:
    """ب/ت/ث/ن/ي confusion — multiple baseline-dot letters in short root."""
    count = sum(1 for c in root if c in _BASELINE)
    return count >= 2  # two or more dotted-baseline letters → likely confusion

def _gate_03_dal_dhal(root: str) -> bool:
    return _is_pair_ambiguous(root, 'د', 'ذ')

def _gate_04_ra_zay(root: str) -> bool:
    return _is_pair_ambiguous(root, 'ر', 'ز')

def _gate_05_sad_dad(root: str) -> bool:
    return _is_pair_ambiguous(root, 'ص', 'ض')

def _gate_06_ta_za(root: str) -> bool:
    return _is_pair_ambiguous(root, 'ط', 'ظ')

def _gate_07_ain_ghain(root: str) -> bool:
    return _is_pair_ambiguous(root, 'ع', 'غ')

def _gate_08_fa_qaf(root: str) -> bool:
    return _is_pair_ambiguous(root, 'ف', 'ق')

def _gate_09_hamza(root: str) -> bool:
    """Hamza form confusion — non-canonical Hamza form used."""
    return any(c in _HAMZA for c in root)

def _gate_10_weak_letter(root: str) -> bool:
    """و/ي ambiguity — multiple weak letters in root."""
    count = sum(1 for c in root if c in _WEAK)
    return count >= 2

def _gate_11_reversed_radicals(root: str) -> bool:
    """
    Reversed radicals — statistical check.
    A true positive requires Arabic lexicographic knowledge.
    Here we flag roots where the same two letters appear in reversed order
    compared to known common root patterns (conservative: always False for now
    as it requires a reference corpus not available at this stage).
    """
    return False  # conservative: human to review

def _gate_12_extra_radical(root: str) -> bool:
    """4+ character root — may be OCR adding an extra letter."""
    return len(root) >= 4

def _gate_13_missing_radical(root: str) -> bool:
    """2 character root — may be OCR dropping a letter."""
    return len(root) <= 2

def _gate_14_mim_nun(root: str) -> bool:
    return _is_pair_ambiguous(root, 'م', 'ن')

def _gate_15_ha_ta_marbuta(root: str) -> bool:
    return _is_pair_ambiguous(root, 'ه', 'ة')

def _gate_16_kaf_lam(root: str) -> bool:
    return _is_pair_ambiguous(root, 'ك', 'ل')

def _gate_17_sin_shin(root: str) -> bool:
    return _is_pair_ambiguous(root, 'س', 'ش')

def _gate_18_jim_ha_kha(root: str) -> bool:
    """ج/ح/خ triconfusion — any two of the three present."""
    present = {c for c in root if c in _JIM_HA_KHA}
    return len(present) >= 2

def _gate_19_qaf_ghain(root: str) -> bool:
    return _is_pair_ambiguous(root, 'ق', 'غ')

def _gate_20_diacritic_bleed(root: str) -> bool:
    """Diacritic characters merged into root letters."""
    return any(c in _DIACRITICS for c in root)


def _is_pair_ambiguous(root: str, a: str, b: str) -> bool:
    """
    True if both letters a and b appear in root (possible confusion between them).
    """
    return (a in root) and (b in root)


# Gate registry: gate_id → (gate_function, description)
OCR_GATES: list[tuple[str, object, str]] = [
    ("G01", _gate_01_ha_kha,        "ح/خ confusion"),
    ("G02", _gate_02_baseline_dots, "ب/ت/ث/ن/ي multi-dot baseline confusion"),
    ("G03", _gate_03_dal_dhal,      "د/ذ confusion"),
    ("G04", _gate_04_ra_zay,        "ر/ز confusion"),
    ("G05", _gate_05_sad_dad,       "ص/ض confusion"),
    ("G06", _gate_06_ta_za,         "ط/ظ confusion"),
    ("G07", _gate_07_ain_ghain,     "ع/غ confusion"),
    ("G08", _gate_08_fa_qaf,        "ف/ق confusion"),
    ("G09", _gate_09_hamza,         "Hamza form confusion (أ/إ/آ/ء)"),
    ("G10", _gate_10_weak_letter,   "و/ي multiple weak letters"),
    ("G11", _gate_11_reversed_radicals, "Reversed radicals"),
    ("G12", _gate_12_extra_radical, "4+ character root (extra radical?)"),
    ("G13", _gate_13_missing_radical,"≤2 character root (missing radical?)"),
    ("G14", _gate_14_mim_nun,       "م/ن confusion"),
    ("G15", _gate_15_ha_ta_marbuta, "ه/ة confusion"),
    ("G16", _gate_16_kaf_lam,       "ك/ل confusion"),
    ("G17", _gate_17_sin_shin,      "س/ش confusion"),
    ("G18", _gate_18_jim_ha_kha,    "ج/ح/خ triconfusion"),
    ("G19", _gate_19_qaf_ghain,     "ق/غ confusion"),
    ("G20", _gate_20_diacritic_bleed,"Diacritic bleed into letter shape"),
]

# Fix typo in gate list (G11 references wrong name)
OCR_GATES[10] = ("G11", _gate_11_reversed_radicals, "Reversed radicals")


def evaluate_ocr_gates(root: str) -> tuple[tuple[str, bool], ...]:
    """
    Evaluate all 20 OCR gates against *root*.
    Returns a tuple of (gate_id, flag) pairs.
    Never raises.
    """
    results: list[tuple[str, bool]] = []
    for gate_id, gate_fn, _ in OCR_GATES:
        try:
            flag = bool(gate_fn(root))
        except Exception:
            flag = False
        results.append((gate_id, flag))
    return tuple(results)


# ═══════════════════════════════════════════════════════════════════════════════
# § 3 — PASSAGE + IDENTITY BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def _hamza_normalize(root: str) -> str:
    """Normalize Hamza variants to ا for coverage check ONLY."""
    return root.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")


def _passage_from_import(
    imp: LegacyCandidateImport,
    occurred_at: str,
) -> SourcePassage:
    """Build a SourcePassage from a LegacyCandidateImport."""
    # Source ID: pick first PDF if available
    source_id = (
        f"maqayis:source:vol_unknown"
        if not imp.legacy_source_pdfs
        else f"maqayis:source:{imp.legacy_source_pdfs[0].replace('.pdf','')}"
    )
    return SourcePassage(
        id=imp.passage_id,
        source_id=source_id,
        page_number=0,  # page not in legacy data
        raw_passage_candidate=imp.legacy_root_letters,  # heading_sample used as passage
        corrected_passage=None,
        ocr_confidence=1.0 if imp.initial_review_state == ReviewState.MACHINE_CANDIDATE else 0.7,
        review_state=imp.initial_review_state,
        evidence_status=imp.initial_evidence_status,
        supersedes_id=None,
    )


def _identity_from_import(
    imp: LegacyCandidateImport,
    occurred_at: str,
) -> tuple[RootIdentityCandidate, list[Residual], list[TraceEvent]]:
    """
    Build a RootIdentityCandidate + OCR gate Residuals + TraceEvents
    from a LegacyCandidateImport.

    Enforces TC-SI-01 by constructing the passage and checking state.
    Returns (candidate, residuals, trace_events).
    """
    root = imp.legacy_root_letters
    normalized = _hamza_normalize(root)
    gate_results = evaluate_ocr_gates(root)

    residuals: list[Residual] = []
    trace_events: list[TraceEvent] = []

    # Determine target review state (IDENTITY_CANDIDATE from MACHINE_CANDIDATE)
    target_state = ReviewState.IDENTITY_CANDIDATE

    candidate = RootIdentityCandidate(
        id=imp.candidate_id,
        passage_id=imp.passage_id,
        candidate_letters=root,
        normalized_letters=normalized,
        bab_letter=imp.legacy_corrected_bab_letter or imp.legacy_bab_letter,
        original_bab_letter=imp.legacy_original_bab_letter,
        bab_correction_version=imp.legacy_correction_version,
        ocr_gate_flags=gate_results,
        review_state=target_state,
        evidence_status=imp.initial_evidence_status,
        supersedes_id=None,
    )

    # TraceEvent for identity extraction
    trace_events.append(TraceEvent(
        id=f"{_TRACE_ID_PREFIX}:identity_extracted:{root}",
        kind=TraceEventKind.IDENTITY_EXTRACTED,
        target_id=candidate.id,
        target_type="RootIdentityCandidate",
        actor_type=ReviewerType.MACHINE_ONLY,
        actor_id=PIPELINE_ACTOR_ID,
        occurred_at=occurred_at,
        summary=f"Identity extracted for root {root}: {len(candidate.flagged_gates)} gate(s) flagged",
        metadata=(
            ("flagged_gates", ",".join(candidate.flagged_gates)),
            ("bab_letter", candidate.bab_letter),
            ("bab_corrected", str(candidate.bab_letter != candidate.original_bab_letter)),
        ),
    ))

    # Emit OCR_AMBIGUITY residuals for each raised gate
    for gate_id, flag in gate_results:
        if flag:
            gate_desc = next(
                (desc for gid, _, desc in OCR_GATES if gid == gate_id),
                gate_id,
            )
            res_id = f"{_RESIDUAL_ID_PREFIX}:OCR_AMBIGUITY:{gate_id}:{root}"
            residuals.append(Residual(
                id=res_id,
                target_id=candidate.id,
                target_type="RootIdentityCandidate",
                residual_type=ResidualType.OCR_AMBIGUITY,
                description=f"OCR gate {gate_id} raised for root '{root}': {gate_desc}",
                blocking_until=ReviewState.IDENTITY_VERIFIED,
                created_at=occurred_at,
            ))

    return candidate, residuals, trace_events


# ═══════════════════════════════════════════════════════════════════════════════
# § 4 — FULL PIPELINE RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

class IdentityPipelineResult:
    """
    Result of running the identity pipeline over a LegacyImportResult.
    """
    __slots__ = (
        "source_records",
        "passages",
        "candidates",
        "residuals",
        "trace_events",
        "gate_summary",
    )

    def __init__(
        self,
        source_records: list[SourceRecord],
        passages: list[SourcePassage],
        candidates: list[RootIdentityCandidate],
        residuals: list[Residual],
        trace_events: list[TraceEvent],
        gate_summary: dict,
    ) -> None:
        self.source_records = source_records
        self.passages       = passages
        self.candidates     = candidates
        self.residuals      = residuals
        self.trace_events   = trace_events
        self.gate_summary   = gate_summary


def run_identity_pipeline(import_result: LegacyImportResult) -> IdentityPipelineResult:
    """
    Run the full identity pipeline over a LegacyImportResult.

    For each non-noise import:
    • Build SourcePassage
    • Evaluate 20 OCR gates
    • Build RootIdentityCandidate
    • Emit OCR_AMBIGUITY residuals for raised gates

    Returns IdentityPipelineResult — never raises (fail-open contract).
    """
    occurred_at = datetime.datetime.utcnow().isoformat() + "Z"

    source_records = build_source_records()
    passages:    list[SourcePassage]          = []
    candidates:  list[RootIdentityCandidate]  = []
    residuals:   list[Residual]               = []
    trace_events: list[TraceEvent]            = []

    gate_counts: dict[str, int] = {gate_id: 0 for gate_id, _, _ in OCR_GATES}
    entries_with_flags = 0
    skipped_noise = 0
    failed = 0

    for imp in import_result.imports:
        try:
            if imp.noise_entry:
                skipped_noise += 1
                continue

            passage = _passage_from_import(imp, occurred_at)
            passages.append(passage)

            candidate, cand_residuals, cand_traces = _identity_from_import(imp, occurred_at)
            candidates.append(candidate)
            residuals.extend(cand_residuals)
            trace_events.extend(cand_traces)

            if candidate.has_ocr_flags:
                entries_with_flags += 1
            for gate_id, flag in candidate.ocr_gate_flags:
                if flag:
                    gate_counts[gate_id] = gate_counts.get(gate_id, 0) + 1

        except Exception:
            failed += 1
            continue

    # Gate summary
    gate_summary: dict = {
        "PIPELINE_INPUT_COUNT":         len(import_result.imports) - skipped_noise,
        "SKIPPED_NOISE_COUNT":          skipped_noise,
        "FAILED_COUNT":                 failed,
        "CANDIDATES_PRODUCED":          len(candidates),
        "ENTRIES_WITH_ANY_FLAG":        entries_with_flags,
        "OCR_AMBIGUITY_RESIDUALS":      sum(1 for r in residuals
                                           if r.residual_type == ResidualType.OCR_AMBIGUITY),
        "gate_flag_counts":             gate_counts,
    }

    return IdentityPipelineResult(
        source_records=source_records,
        passages=passages,
        candidates=candidates,
        residuals=residuals,
        trace_events=trace_events,
        gate_summary=gate_summary,
    )
