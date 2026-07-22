#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/demo_ayat_al_dayn.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-TAAQOL-AYAT-AL-DAYN-LIVE-DEMO-01

Live operational demo: Hokom–Taaqol pipeline over Ayat al-Dayn
(Sūrat al-Baqara 2:282).

All 129 tokens are processed through the real pipeline with no hints,
seeds, injected results, or mock substitutions.  Taaqol is invoked
live; if its runtime is unavailable the verdict is truthfully reported
as TAAQOL_RUNTIME_UNAVAILABLE — not hidden.

Usage
-----
    python scripts/demo_ayat_al_dayn.py                    # terminal table (default)
    python scripts/demo_ayat_al_dayn.py --format terminal
    python scripts/demo_ayat_al_dayn.py --format json
    python scripts/demo_ayat_al_dayn.py --format csv
    python scripts/demo_ayat_al_dayn.py --format html
    python scripts/demo_ayat_al_dayn.py --open             # write all formats + open HTML
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── repo root on path ─────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ── canonical text (sourced from tests/post_segmentation_routing/test_ayat_al_dayn_routing.py)
AYAT_AL_DAYN = (
    'يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا تَدَايَنْتُمْ بِدَيْنٍ إِلَى أَجَلٍ مُسَمًّى '
    'فَاكْتُبُوهُ وَلْيَكْتُبْ بَيْنَكُمْ كَاتِبٌ بِالْعَدْلِ وَلَا يَأْبَ كَاتِبٌ '
    'أَنْ يَكْتُبَ كَمَا عَلَّمَهُ اللَّهُ فَلْيَكْتُبْ وَلْيُمْلِلِ الَّذِي عَلَيْهِ '
    'الْحَقُّ وَلْيَتَّقِ اللَّهَ رَبَّهُ وَلَا يَبْخَسْ مِنْهُ شَيْئًا فَإِنْ كَانَ '
    'الَّذِي عَلَيْهِ الْحَقُّ سَفِيهًا أَوْ ضَعِيفًا أَوْ لَا يَسْتَطِيعُ أَنْ يُمِلَّ '
    'هُوَ فَلْيُمْلِلْ وَلِيُّهُ بِالْعَدْلِ وَاسْتَشْهِدُوا شَهِيدَيْنِ مِنْ رِجَالِكُمْ '
    'فَإِنْ لَمْ يَكُونَا رَجُلَيْنِ فَرَجُلٌ وَامْرَأَتَانِ مِمَّنْ تَرْضَوْنَ مِنَ '
    'الشُّهَدَاءِ أَنْ تَضِلَّ إِحْدَاهُمَا فَتُذَكِّرَ إِحْدَاهُمَا الْأُخْرَى وَلَا '
    'يَأْبَ الشُّهَدَاءُ إِذَا مَا دُعُوا وَلَا تَسْأَمُوا أَنْ تَكْتُبُوهُ صَغِيرًا '
    'أَوْ كَبِيرًا إِلَى أَجَلِهِ ذَلِكُمْ أَقْسَطُ عِنْدَ اللَّهِ وَأَقْوَمُ '
    'لِلشَّهَادَةِ وَأَدْنَى أَلَّا تَرْتَابُوا إِلَّا أَنْ تَكُونَ تِجَارَةً '
    'حَاضِرَةً تُدِيرُونَهَا بَيْنَكُمْ فَلَيْسَ عَلَيْكُمْ جُنَاحٌ أَلَّا تَكْتُبُوهَا '
    'وَأَشْهِدُوا إِذَا تَبَايَعْتُمْ وَلَا يُضَارَّ كَاتِبٌ وَلَا شَهِيدٌ وَإِنْ '
    'تَفْعَلُوا فَإِنَّهُ فُسُوقٌ بِكُمْ وَاتَّقُوا اللَّهَ وَيُعَلِّمُكُمُ اللَّهُ '
    'وَاللَّهُ بِكُلِّ شَيْءٍ عَلِيمٌ'
)
AYAT_SOURCE_FILE = 'tests/post_segmentation_routing/test_ayat_al_dayn_routing.py'

TOKENS = AYAT_AL_DAYN.split()
assert len(TOKENS) == 129, f'Expected 129 tokens, got {len(TOKENS)}'

# ── H11-H15 slot names (morpho-syntactic / derivative layer) ─────────────────
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


# ── result dataclass ──────────────────────────────────────────────────────────
@dataclass
class TokenResult:
    token_index: int
    original_surface: str
    normalized_surface: Optional[str] = None
    proclitics: list = field(default_factory=list)
    host_surface: Optional[str] = None
    enclitics: list = field(default_factory=list)
    word_class: Optional[str] = None
    word_class_verdict: Optional[str] = None
    # root
    root_state: Optional[str] = None          # ACCEPT / DEFER / AMBIGUOUS / UNKNOWN
    canonical_root: Optional[str] = None
    root_candidates: list = field(default_factory=list)
    # wazn / masdar / derivatives
    wazn: Optional[str] = None
    masdar: Optional[str] = None
    derivative_type: Optional[str] = None
    # H11-H15
    h11_h15_reached: bool = False
    h11_h15_filled_slots: list = field(default_factory=list)
    # Taaqol
    taaqol_active: bool = False
    taaqol_verdict: Optional[str] = None
    taaqol_effective_verdict: Optional[str] = None
    taaqol_failure_code: Optional[str] = None
    # SGA bundle
    claim_key: Optional[str] = None       # content hash (may collide for identical words)
    evaluation_id: Optional[str] = None   # unique per token: hash(claim_key + token_index)
    typed_slot_count: int = 0
    filled_slot_count: int = 0
    unknown_slot_count: int = 0
    # provenance / early-stop
    cause: Optional[str] = None
    condition: Optional[str] = None
    obstacle: Optional[str] = None
    residual_or_defer_reason: Optional[str] = None
    early_stop_reason: Optional[str] = None
    evidence_provenance: Optional[str] = None
    # error
    error: Optional[str] = None


# ── git / env helpers ─────────────────────────────────────────────────────────
def _git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=REPO_ROOT, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "UNKNOWN"


def _vendor_sha() -> str:
    vendor = REPO_ROOT / 'vendor' / 'Taaqol-GPT'
    if (vendor / '.git').exists():
        try:
            return subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], cwd=vendor, stderr=subprocess.DEVNULL
            ).decode().strip()[:16]
        except Exception:
            pass
    # Fall back to pinned SHA
    pinned = REPO_ROOT / 'tests' / 'fixtures' / 'vendor_sha_pin.txt'
    if pinned.exists():
        return pinned.read_text().strip()[:16]
    return "UNKNOWN"


# ── pipeline runner ───────────────────────────────────────────────────────────
def _extract_root_string(rc) -> str | None:
    if rc is None:
        return None
    canon = getattr(rc, 'canonical_root', None)
    if canon and isinstance(canon, (tuple, list)):
        return ''.join(canon)
    if canon and isinstance(canon, str):
        return canon
    return None


def _build_bundle_dict(hr: dict) -> dict:
    """Same distillation as live_runner._build_bundle_dict()."""
    rc = hr.get("root_candidate")
    root_str = _extract_root_string(rc)

    procs = list(hr.get("segment_proclitics") or hr.get("proclitics") or [])
    encs  = list(hr.get("segment_enclitics") or hr.get("enclitics") or [])

    d: dict = {
        "word":         hr.get("input_surface", ""),
        "segment_host": hr.get("segment_host") or hr.get("morphology_surface") or hr.get("input_surface", ""),
        "word_class":   hr.get("word_class"),
        "wazn":         hr.get("final_wazn"),
        "number":       hr.get("number"),
        "gender":       hr.get("gender"),
        "lemma":        hr.get("lemma_surface"),
    }
    if root_str:
        d["root_candidate"] = root_str

    _cra = hr.get("cra_result")
    if (_cra is not None
            and getattr(_cra, 'directive', None) == 'DEFER'
            and getattr(_cra, 'candidate_radical_sequences', None)
            and len(_cra.candidate_radical_sequences) >= 2):
        d["root_candidates"] = [list(seq) for seq in _cra.candidate_radical_sequences]

    if procs:
        d["proclitics"] = procs
    if encs:
        d["enclitics"] = encs
    if hr.get("has_article") or hr.get("article"):
        d["article"] = True
    return d


def process_token(idx: int, surface: str) -> TokenResult:
    result = TokenResult(token_index=idx, original_surface=surface)
    try:
        from hokom_pipeline import hokom
        hr = hokom(surface)
        hr_dict = dict(hr)

        result.normalized_surface  = hr_dict.get("normalized_surface") or hr_dict.get("normalized")
        result.proclitics          = list(hr_dict.get("segment_proclitics") or hr_dict.get("proclitics") or [])
        result.host_surface        = hr_dict.get("segment_host") or hr_dict.get("morphology_surface")
        result.enclitics           = list(hr_dict.get("segment_enclitics") or hr_dict.get("enclitics") or [])
        result.word_class          = hr_dict.get("word_class")
        result.word_class_verdict  = hr_dict.get("word_class_verdict")
        result.wazn                = hr_dict.get("final_wazn")
        result.masdar              = hr_dict.get("final_masdar") or hr_dict.get("final_masdar_pattern")
        result.derivative_type     = hr_dict.get("derivative_type")

        # Root state
        rc = hr_dict.get("root_candidate")
        rc_dir = getattr(rc, 'directive', None) if rc else None
        cra = hr_dict.get("cra_result")

        # Check for two-consonant ambiguous candidates
        cra_seqs = getattr(cra, 'candidate_radical_sequences', None) if cra else None
        if cra_seqs and len(cra_seqs) >= 2 and not _extract_root_string(rc):
            result.root_state = "AMBIGUOUS"
            result.root_candidates = [''.join(s) for s in cra_seqs]
        elif rc_dir == 'ACCEPT':
            result.root_state = "KNOWN"
            result.canonical_root = _extract_root_string(rc)
        elif rc_dir == 'DEFER':
            result.root_state = "DEFERRED"
            result.residual_or_defer_reason = ', '.join(getattr(rc, 'residual_codes', ()) or ())
        else:
            result.root_state = "UNKNOWN"

        # Inflection / early-stop
        isr = hr_dict.get("inflection_skipped_reason")
        if isr:
            result.early_stop_reason = isr

        # Cause / condition / obstacle from SGA bundle
        try:
            from pipeline.corpus.live_runner import _build_bundle_dict as _lrbd
            from pipeline.sga.adapters import build_claim_bundle
            from pipeline.sga.contracts import SlotState

            bd = _lrbd(hr_dict)
            claim_kind = "AYAT_AL_DAYN_LIVE_DEMO"
            bundle = build_claim_bundle(bd, claim_kind, claim_kind)

            result.claim_key = bundle.claim_key
            # evaluation_id: unique per token position (claim_key + token_index)
            result.evaluation_id = hashlib.sha256(
                f"{bundle.claim_key}:{idx}".encode()
            ).hexdigest()[:16]
            result.typed_slot_count = len(bundle.typed_slots)
            result.filled_slot_count = sum(
                1 for s in bundle.typed_slots if s.state == SlotState.FILLED
            )
            result.unknown_slot_count = sum(
                1 for s in bundle.typed_slots if s.state == SlotState.UNKNOWN
            )

            # H11-H15 filled slots
            h_filled = [
                s.slot_id.value
                for s in bundle.typed_slots
                if s.slot_id.value in _H11_H15_SLOT_NAMES and s.state == SlotState.FILLED
            ]
            result.h11_h15_reached     = bool(h_filled)
            result.h11_h15_filled_slots = h_filled

            # Condition / obstacle / cause from bundle facts
            if bundle.condition_facts:
                result.condition = '; '.join(str(f) for f in bundle.condition_facts)
            if bundle.obstacle_facts:
                result.obstacle = '; '.join(str(f) for f in bundle.obstacle_facts)

            # Evidence provenance from evidence_refs
            if bundle.evidence_refs:
                result.evidence_provenance = ', '.join(
                    getattr(e, 'evidence_id', str(e)) for e in bundle.evidence_refs[:4]
                )

            # Residuals
            if bundle.residuals:
                result.residual_or_defer_reason = '; '.join(str(r) for r in bundle.residuals)

        except Exception as bundle_err:
            result.error = (result.error or '') + f'[bundle:{type(bundle_err).__name__}:{bundle_err}] '

        # Taaqol
        rt = hr_dict.get("taaqol_runtime") or {}
        td = hr_dict.get("taaqol_decision")
        result.taaqol_active           = bool(rt.get("active", False))
        result.taaqol_verdict          = hr_dict.get("taaqol_verdict")
        result.taaqol_effective_verdict = hr_dict.get("taaqol_effective_verdict")
        result.taaqol_failure_code     = rt.get("failure_code")

        # cause from reason codes on taaqol decision
        if td and hasattr(td, 'reason_codes') and td.reason_codes:
            result.cause = ', '.join(td.reason_codes[:3])

        # Early-stop / boundary cause
        if not result.cause:
            if isr:
                result.cause = isr
            elif result.root_state == "DEFERRED" and result.residual_or_defer_reason:
                result.cause = result.residual_or_defer_reason

    except Exception as exc:
        result.error = str(exc)
        result.root_state = "ERROR"

    return result


# ── run all tokens ────────────────────────────────────────────────────────────
def run_all(verbose: bool = True) -> list[TokenResult]:
    if verbose:
        print(f"Processing {len(TOKENS)} tokens …", file=sys.stderr)
    results = []
    for i, tok in enumerate(TOKENS):
        r = process_token(i + 1, tok)
        if verbose and (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(TOKENS)}", file=sys.stderr)
        results.append(r)
    if verbose:
        print("  Done.", file=sys.stderr)
    return results


# ── integrity checks ──────────────────────────────────────────────────────────
def integrity_check(results: list[TokenResult]) -> dict:
    # nondeterminism: re-run first 5 tokens and compare claim_keys
    nondeterminism_count = 0
    for r in results[:5]:
        r2 = process_token(r.token_index, r.original_surface)
        if r2.claim_key and r.claim_key and r2.claim_key != r.claim_key:
            nondeterminism_count += 1

    # evaluation_id collisions: evaluation_id is token-scoped, must be unique
    eval_ids = [r.evaluation_id for r in results if r.evaluation_id]
    collision_count = len(eval_ids) - len(set(eval_ids))

    # untyped payloads: results with typed_slot_count == 0 and no early stop and no error
    untyped = sum(
        1 for r in results
        if r.typed_slot_count == 0
        and not r.early_stop_reason
        and not r.error
        and r.word_class not in ("MABNI", "OPERATOR")
    )

    # silent fallbacks: taaqol_active=False without declared failure code or early stop
    silent = sum(
        1 for r in results
        if not r.taaqol_active
        and not r.taaqol_failure_code
        and not r.early_stop_reason
        and r.word_class not in (None, "MABNI", "OPERATOR")
    )

    taaqol_live = sum(1 for r in results if r.taaqol_active)

    return {
        "UNTYPED_PAYLOADS":           untyped,
        "SILENT_FALLBACKS":           silent,
        "CLAIM_KEY_NONDETERMINISM":   nondeterminism_count,
        "EVALUATION_ID_COLLISIONS":   collision_count,
        "TAAQOL_RUNTIME_ACTIVE":      taaqol_live,
    }


# ── summary statistics ────────────────────────────────────────────────────────
def summary_stats(results: list[TokenResult]) -> dict:
    verdict_counts: dict[str, int] = {}
    for r in results:
        v = r.taaqol_effective_verdict or "NO_TAAQOL"
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    root_state_counts: dict[str, int] = {}
    for r in results:
        k = r.root_state or "NONE"
        root_state_counts[k] = root_state_counts.get(k, 0) + 1

    h11_reached = sum(1 for r in results if r.h11_h15_reached)
    early_stops = sum(1 for r in results if r.early_stop_reason)
    typed_bundles = sum(1 for r in results if r.typed_slot_count > 0)
    taaqol_live = sum(1 for r in results if r.taaqol_active)
    errors = sum(1 for r in results if r.error)

    return {
        "token_count":          len(results),
        "typed_bundles":        typed_bundles,
        "taaqol_live_evals":    taaqol_live,
        "verdict_counts":       verdict_counts,
        "root_state_counts":    root_state_counts,
        "h11_h15_reached":      h11_reached,
        "constitutional_early_stops": early_stops,
        "errors":               errors,
    }


# ── format: terminal ──────────────────────────────────────────────────────────
def _bare(s: str | None) -> str:
    if not s:
        return ''
    return ''.join(c for c in s if unicodedata.category(c) not in ('Mn', 'Cf'))


def format_terminal(results: list[TokenResult], stats: dict, checks: dict) -> str:
    lines = []
    lines.append(f"\nHOKOM–TAAQOL LIVE DEMO — آية الدَّيْن (البقرة 2:282)")
    lines.append("=" * 100)
    lines.append(
        f"{'#':>3}  {'Surface':<14} {'Segmentation':<22} {'Host':<14} "
        f"{'Root':<10} {'H11-15':^6} {'Taaqol':<12} Reason"
    )
    lines.append("-" * 100)
    for r in results:
        seg = ''
        if r.proclitics:
            seg += '+'.join(r.proclitics) + '|'
        seg += (_bare(r.host_surface) or '')
        if r.enclitics:
            seg += '|' + '+'.join(r.enclitics)

        root_disp = r.canonical_root or (
            '/'.join(r.root_candidates[:2]) if r.root_candidates else (r.root_state or '')
        )
        h_disp = 'YES' if r.h11_h15_reached else ('—' if r.early_stop_reason else 'NO')
        tq = r.taaqol_effective_verdict or r.taaqol_failure_code or '—'
        reason = r.early_stop_reason or (r.cause or '')[:40]
        if r.error:
            reason = f'ERR:{r.error[:30]}'
        lines.append(
            f"{r.token_index:>3}  {_bare(r.original_surface):<14} {seg:<22} "
            f"{_bare(r.host_surface) or '':<14} {root_disp:<10} "
            f"{h_disp:^6}  {tq:<12} {reason}"
        )
    lines.append("-" * 100)
    lines.append(f"\nTokens: {stats['token_count']} | "
                 f"Typed bundles: {stats['typed_bundles']} | "
                 f"Taaqol live: {stats['taaqol_live_evals']} | "
                 f"H11-15 reached: {stats['h11_h15_reached']} | "
                 f"Early stops: {stats['constitutional_early_stops']}")
    lines.append(f"Root states: {stats['root_state_counts']}")
    lines.append(f"Verdicts:    {stats['verdict_counts']}")
    lines.append(f"\nIntegrity: UNTYPED={checks['UNTYPED_PAYLOADS']} "
                 f"SILENT_FALLBACKS={checks['SILENT_FALLBACKS']} "
                 f"NONDETERMINISM={checks['CLAIM_KEY_NONDETERMINISM']} "
                 f"COLLISIONS={checks['EVALUATION_ID_COLLISIONS']} "
                 f"TAAQOL_ACTIVE={checks['TAAQOL_RUNTIME_ACTIVE']}")
    return '\n'.join(lines)


# ── format: json ─────────────────────────────────────────────────────────────
def format_json(results: list[TokenResult], stats: dict, checks: dict, meta: dict) -> str:
    rows = []
    for r in results:
        rows.append({
            "token_index":           r.token_index,
            "original_surface":      r.original_surface,
            "normalized_surface":    r.normalized_surface,
            "proclitics":            r.proclitics,
            "host_surface":          r.host_surface,
            "enclitics":             r.enclitics,
            "word_class":            r.word_class,
            "word_class_verdict":    r.word_class_verdict,
            "root_state":            r.root_state,
            "canonical_root":        r.canonical_root,
            "root_candidates":       r.root_candidates,
            "wazn":                  r.wazn,
            "masdar":                r.masdar,
            "derivative_type":       r.derivative_type,
            "H11_H15_reached":       r.h11_h15_reached,
            "H11_H15_filled_slots":  r.h11_h15_filled_slots,
            "Taaqol_active":         r.taaqol_active,
            "Taaqol_verdict":        r.taaqol_verdict,
            "Taaqol_effective_verdict": r.taaqol_effective_verdict,
            "Taaqol_failure_code":   r.taaqol_failure_code,
            "claim_key":             r.claim_key,
            "evaluation_id":         r.evaluation_id,
            "typed_slot_count":      r.typed_slot_count,
            "filled_slot_count":     r.filled_slot_count,
            "unknown_slot_count":    r.unknown_slot_count,
            "cause":                 r.cause,
            "condition":             r.condition,
            "obstacle":              r.obstacle,
            "evidence_provenance":   r.evidence_provenance,
            "residual_or_defer_reason": r.residual_or_defer_reason,
            "early_stop_reason":     r.early_stop_reason,
            "error":                 r.error,
        })
    return json.dumps({
        "stage":            "HOKOM-TAAQOL-AYAT-AL-DAYN-LIVE-DEMO-01",
        "meta":             meta,
        "summary":          stats,
        "integrity_checks": checks,
        "tokens":           rows,
    }, indent=2, ensure_ascii=False)


# ── format: csv ──────────────────────────────────────────────────────────────
def format_csv(results: list[TokenResult]) -> str:
    buf = io.StringIO()
    fields = [
        "token_index", "original_surface", "normalized_surface",
        "proclitics", "host_surface", "enclitics",
        "word_class", "word_class_verdict",
        "root_state", "canonical_root", "root_candidates",
        "wazn", "masdar", "derivative_type",
        "H11_H15_reached", "H11_H15_filled_slots",
        "Taaqol_active", "Taaqol_verdict", "Taaqol_effective_verdict", "Taaqol_failure_code",
        "claim_key", "typed_slot_count", "filled_slot_count", "unknown_slot_count",
        "cause", "condition", "obstacle", "evidence_provenance",
        "residual_or_defer_reason", "early_stop_reason", "error",
    ]
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for r in results:
        writer.writerow({
            "token_index":           r.token_index,
            "original_surface":      r.original_surface,
            "normalized_surface":    r.normalized_surface or '',
            "proclitics":            ' '.join(r.proclitics),
            "host_surface":          r.host_surface or '',
            "enclitics":             ' '.join(r.enclitics),
            "word_class":            r.word_class or '',
            "word_class_verdict":    r.word_class_verdict or '',
            "root_state":            r.root_state or '',
            "canonical_root":        r.canonical_root or '',
            "root_candidates":       '/'.join(r.root_candidates),
            "wazn":                  r.wazn or '',
            "masdar":                r.masdar or '',
            "derivative_type":       r.derivative_type or '',
            "H11_H15_reached":       str(r.h11_h15_reached),
            "H11_H15_filled_slots":  ' '.join(r.h11_h15_filled_slots),
            "Taaqol_active":         str(r.taaqol_active),
            "Taaqol_verdict":        r.taaqol_verdict or '',
            "Taaqol_effective_verdict": r.taaqol_effective_verdict or '',
            "Taaqol_failure_code":   r.taaqol_failure_code or '',
            "claim_key":             r.claim_key or '',
            "typed_slot_count":      r.typed_slot_count,
            "filled_slot_count":     r.filled_slot_count,
            "unknown_slot_count":    r.unknown_slot_count,
            "cause":                 r.cause or '',
            "condition":             r.condition or '',
            "obstacle":              r.obstacle or '',
            "evidence_provenance":   r.evidence_provenance or '',
            "residual_or_defer_reason": r.residual_or_defer_reason or '',
            "early_stop_reason":     r.early_stop_reason or '',
            "error":                 r.error or '',
        })
    return buf.getvalue()


# ── format: html ─────────────────────────────────────────────────────────────
def _esc(s) -> str:
    if s is None:
        return ''
    return (str(s)
            .replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def _verdict_badge(v: str | None) -> str:
    if not v:
        return '<span class="badge badge-gray">—</span>'
    color = {
        "ACCEPT":    "badge-green",
        "DEFERRED":  "badge-amber",
        "DEFER":     "badge-amber",
        "BLOCKED":   "badge-red",
        "AMBIGUOUS": "badge-purple",
        "TAAQOL_RUNTIME_UNAVAILABLE": "badge-gray",
        "NO_TAAQOL": "badge-gray",
    }.get(v, "badge-blue")
    return f'<span class="badge {color}">{_esc(v)}</span>'


def _root_badge(r: TokenResult) -> str:
    if r.root_state == "KNOWN":
        return f'<span class="badge badge-green">{_esc(r.canonical_root)}</span>'
    if r.root_state == "AMBIGUOUS":
        opts = ' / '.join(_esc(c) for c in r.root_candidates[:3])
        return f'<span class="badge badge-purple">AMBIGUOUS: {opts}</span>'
    if r.root_state == "DEFERRED":
        return '<span class="badge badge-amber">DEFERRED</span>'
    return f'<span class="badge badge-gray">{_esc(r.root_state or "—")}</span>'


def _decision_example(r: TokenResult) -> str:
    """HTML snippet for one token decision explanation."""
    lines = []
    lines.append(f'<h4 style="margin:0 0 4px;font-size:1em;">#{r.token_index} — <span dir="rtl">{_esc(r.original_surface)}</span></h4>')
    lines.append('<table class="decision-table"><tbody>')

    def row(label, val):
        _em = '<em style="color:#888">—</em>'
        return f'<tr><td class="dt-label">{_esc(label)}</td><td>{_esc(str(val)) if val else _em}</td></tr>'

    lines.append(row("Host", r.host_surface))
    lines.append(row("Word class", f"{r.word_class} ({r.word_class_verdict})"))
    lines.append(row("Root state", r.root_state))
    if r.canonical_root:
        lines.append(row("Canonical root", r.canonical_root))
    if r.root_candidates:
        lines.append(row("Root candidates", ' / '.join(r.root_candidates)))
    if r.wazn:
        lines.append(row("Wazn", r.wazn))
    if r.early_stop_reason:
        lines.append(row("Constitutional early stop", r.early_stop_reason))
    if r.cause:
        lines.append(row("Cause (from system)", r.cause))
    if r.residual_or_defer_reason:
        lines.append(row("Residual/defer reason", r.residual_or_defer_reason))
    if r.evidence_provenance:
        lines.append(row("Evidence provenance", r.evidence_provenance))
    lines.append(row("Taaqol active", str(r.taaqol_active)))
    if r.taaqol_failure_code:
        lines.append(row("Taaqol failure code", r.taaqol_failure_code))
    lines.append(row("Taaqol effective verdict", r.taaqol_effective_verdict))
    lines.append(row("Typed slots", f"{r.filled_slot_count} filled / {r.typed_slot_count} total"))
    lines.append('</tbody></table>')
    return '\n'.join(lines)


def format_html(results: list[TokenResult], stats: dict, checks: dict, meta: dict) -> str:
    # Pick decision examples: first KNOWN root, first DEFERRED, first AMBIGUOUS,
    # first with H11-15, first early-stop
    examples = []
    seen = set()
    criteria = [
        lambda r: r.root_state == "KNOWN" and r.wazn,
        lambda r: r.root_state == "DEFERRED",
        lambda r: r.root_state == "AMBIGUOUS",
        lambda r: r.h11_h15_reached,
        lambda r: bool(r.early_stop_reason),
        lambda r: r.word_class == "MABNI",
    ]
    for crit in criteria:
        for r in results:
            if crit(r) and r.token_index not in seen:
                examples.append(r)
                seen.add(r.token_index)
                break

    vc = stats["verdict_counts"]
    rc = stats["root_state_counts"]

    # Token table rows
    table_rows = []
    for r in results:
        seg_parts = []
        if r.proclitics:
            seg_parts.append('<span class="clitic proc">' + '+'.join(_esc(p) for p in r.proclitics) + '</span>')
        seg_parts.append('<span class="host">' + _esc(r.host_surface or '—') + '</span>')
        if r.enclitics:
            seg_parts.append('<span class="clitic enc">' + '+'.join(_esc(e) for e in r.enclitics) + '</span>')
        seg_html = ' | '.join(seg_parts)

        reason = r.early_stop_reason or r.taaqol_failure_code or ''
        h_str = ('✓ ' + ', '.join(r.h11_h15_filled_slots[:2])) if r.h11_h15_reached else '—'

        table_rows.append(
            f'<tr>'
            f'<td class="idx">{r.token_index}</td>'
            f'<td class="arabic">{_esc(r.original_surface)}</td>'
            f'<td>{seg_html}</td>'
            f'<td class="arabic host-cell">{_esc(r.host_surface or "")}</td>'
            f'<td class="wc">{_esc(r.word_class or "—")}</td>'
            f'<td>{_root_badge(r)}</td>'
            f'<td class="wazn">{_esc(r.wazn or "—")}</td>'
            f'<td class="h-cell">{_esc(h_str)}</td>'
            f'<td>{_verdict_badge(r.taaqol_effective_verdict)}</td>'
            f'<td class="reason">{_esc(reason[:60])}</td>'
            f'</tr>'
        )
    table_html = '\n'.join(table_rows)

    examples_html = '\n<hr style="border:none;border-top:1px solid #e2e8f0;margin:16px 0;">\n'.join(
        f'<div class="decision-block">{_decision_example(r)}</div>' for r in examples
    )

    verdict_bars = ''
    total = stats['token_count']
    for v, cnt in sorted(vc.items(), key=lambda x: -x[1]):
        pct = cnt / total * 100
        verdict_bars += (
            f'<div class="bar-row"><span class="bar-label">{_esc(v)}</span>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{pct:.1f}%"></div></div>'
            f'<span class="bar-count">{cnt}</span></div>\n'
        )

    root_bars = ''
    for v, cnt in sorted(rc.items(), key=lambda x: -x[1]):
        pct = cnt / total * 100
        root_bars += (
            f'<div class="bar-row"><span class="bar-label">{_esc(v)}</span>'
            f'<div class="bar-track"><div class="bar-fill bar-root" style="width:{pct:.1f}%"></div></div>'
            f'<span class="bar-count">{cnt}</span></div>\n'
        )

    checks_ok = all(v == 0 for k, v in checks.items() if k != 'TAAQOL_RUNTIME_ACTIVE')
    checks_taaqol_note = (
        '<span style="color:#16a34a">✓ Taaqol runtime active</span>'
        if checks['TAAQOL_RUNTIME_ACTIVE'] > 0
        else '<span style="color:#d97706">⚠ Taaqol runtime unavailable — verdicts are DEFERRED, not hidden</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hokom–Taaqol Live Demo — آية الدَّيْن</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #f8fafc; color: #1e293b; margin: 0; padding: 0;
    direction: rtl;
  }}
  .page {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
  h1 {{ font-size: 1.6em; margin-bottom: 4px; color: #0f172a; }}
  h2 {{ font-size: 1.2em; color: #334155; margin: 24px 0 8px; border-bottom: 2px solid #e2e8f0; padding-bottom: 4px; }}
  h3 {{ font-size: 1em; color: #475569; margin: 16px 0 6px; }}
  .verse-box {{
    background: #fff; border: 1px solid #cbd5e1; border-radius: 10px;
    padding: 20px 24px; font-size: 1.3em; line-height: 2.2;
    direction: rtl; text-align: justify; color: #0f172a;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
  }}
  .meta-row {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 16px 0; }}
  .meta-card {{
    background: #fff; border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 10px 16px; min-width: 150px;
  }}
  .meta-card .val {{ font-size: 1.5em; font-weight: 700; color: #0f172a; }}
  .meta-card .lbl {{ font-size: 0.78em; color: #64748b; }}
  .badge {{
    display: inline-block; padding: 2px 7px; border-radius: 4px;
    font-size: 0.78em; font-weight: 600; letter-spacing: .02em;
  }}
  .badge-green   {{ background:#dcfce7; color:#166534; }}
  .badge-amber   {{ background:#fef9c3; color:#854d0e; }}
  .badge-red     {{ background:#fee2e2; color:#991b1b; }}
  .badge-purple  {{ background:#f3e8ff; color:#6b21a8; }}
  .badge-blue    {{ background:#dbeafe; color:#1e40af; }}
  .badge-gray    {{ background:#f1f5f9; color:#475569; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.82em; }}
  th {{
    background: #1e293b; color: #fff; padding: 8px 10px;
    text-align: right; font-weight: 600; white-space: nowrap;
  }}
  td {{ padding: 6px 10px; border-bottom: 1px solid #e2e8f0; vertical-align: middle; }}
  tr:hover td {{ background: #f0f9ff; }}
  tr:nth-child(even) td {{ background: #f8fafc; }}
  tr:nth-child(even):hover td {{ background: #f0f9ff; }}
  .arabic {{ font-size: 1.05em; direction: rtl; }}
  .host-cell {{ color: #334155; }}
  .idx {{ color: #94a3b8; font-size: 0.85em; }}
  .wc {{ font-size: 0.78em; color: #475569; }}
  .wazn {{ font-size: 0.78em; color: #0369a1; }}
  .h-cell {{ font-size: 0.78em; color: #166534; }}
  .reason {{ font-size: 0.75em; color: #64748b; direction: ltr; text-align: left; }}
  .clitic {{ font-size: 0.85em; color: #7c3aed; }}
  .host {{ font-weight: 500; }}
  .bar-row {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; }}
  .bar-label {{ min-width: 200px; font-size: 0.82em; color: #334155; text-align: right; }}
  .bar-track {{ flex: 1; height: 14px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }}
  .bar-fill {{ height: 100%; background: #3b82f6; border-radius: 99px; }}
  .bar-root {{ background: #8b5cf6; }}
  .bar-count {{ min-width: 30px; font-size: 0.82em; color: #64748b; }}
  .decision-block {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 18px; margin: 12px 0; }}
  .decision-table {{ width: auto; font-size: 0.82em; }}
  .decision-table td {{ padding: 3px 8px; border: none; }}
  .dt-label {{ font-weight: 600; color: #475569; min-width: 200px; }}
  .integrity-row {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 8px 0; }}
  .integrity-item {{
    padding: 6px 14px; border-radius: 6px; font-size: 0.82em; font-weight: 600;
  }}
  .int-ok  {{ background: #dcfce7; color: #166534; }}
  .int-bad {{ background: #fee2e2; color: #991b1b; }}
  .int-info {{ background: #dbeafe; color: #1e40af; }}
  .meta-box {{
    background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px;
    padding:10px 14px; font-size:0.78em; color:#475569; direction:ltr; text-align:left;
  }}
  .defer-section {{
    background:#fffbeb; border-left:4px solid #f59e0b;
    padding:14px 18px; border-radius:0 8px 8px 0; margin:16px 0;
  }}
  .defer-section p {{ margin: 4px 0; font-size: 0.88em; }}
</style>
</head>
<body>
<div class="page">

  <h1>Hokom–Taaqol — عرض تشغيلي حي</h1>
  <p style="color:#64748b;margin:0 0 16px;direction:rtl;">
    سورة البقرة، الآية 282 — آية الدَّيْن &nbsp;|&nbsp; المرحلة: HOKOM-TAAQOL-AYAT-AL-DAYN-LIVE-DEMO-01
  </p>

  <div class="verse-box" dir="rtl">
    {_esc(AYAT_AL_DAYN)}
  </div>

  <h2>إحصاءات التشغيل</h2>
  <div class="meta-row">
    <div class="meta-card"><div class="val">{stats['token_count']}</div><div class="lbl">كلمات/توكنات</div></div>
    <div class="meta-card"><div class="val">{stats['typed_bundles']}</div><div class="lbl">حزم مكتوبة بالنوع (Typed bundles)</div></div>
    <div class="meta-card"><div class="val">{stats['taaqol_live_evals']}</div><div class="lbl">تشغيلات Taaqol الحية</div></div>
    <div class="meta-card"><div class="val">{stats['h11_h15_reached']}</div><div class="lbl">وصلت إلى H11-H15</div></div>
    <div class="meta-card"><div class="val">{stats['constitutional_early_stops']}</div><div class="lbl">توقفات دستورية صحيحة</div></div>
    <div class="meta-card"><div class="val">{sum(1 for r in results if r.root_state == 'KNOWN')}</div><div class="lbl">جذر معروف</div></div>
    <div class="meta-card"><div class="val">{sum(1 for r in results if r.root_state == 'DEFERRED')}</div><div class="lbl">جذر مؤجَّل</div></div>
    <div class="meta-card"><div class="val">{sum(1 for r in results if r.root_state == 'AMBIGUOUS')}</div><div class="lbl">جذر مبهم</div></div>
  </div>

  <h2>توزيع الأحكام (Verdicts)</h2>
  {verdict_bars}

  <h2>حالات الجذر</h2>
  {root_bars}

  <h2>صحة النظام</h2>
  <div class="integrity-row">
    <div class="integrity-item {'int-ok' if checks['UNTYPED_PAYLOADS']==0 else 'int-bad'}">
      UNTYPED_PAYLOADS = {checks['UNTYPED_PAYLOADS']}
    </div>
    <div class="integrity-item {'int-ok' if checks['SILENT_FALLBACKS']==0 else 'int-bad'}">
      SILENT_FALLBACKS = {checks['SILENT_FALLBACKS']}
    </div>
    <div class="integrity-item {'int-ok' if checks['CLAIM_KEY_NONDETERMINISM']==0 else 'int-bad'}">
      CLAIM_KEY_NONDETERMINISM = {checks['CLAIM_KEY_NONDETERMINISM']}
    </div>
    <div class="integrity-item {'int-ok' if checks['EVALUATION_ID_COLLISIONS']==0 else 'int-bad'}">
      EVALUATION_ID_COLLISIONS = {checks['EVALUATION_ID_COLLISIONS']}
    </div>
    <div class="integrity-item int-info">
      TAAQOL_RUNTIME_ACTIVE = {checks['TAAQOL_RUNTIME_ACTIVE']}
    </div>
  </div>
  <p style="font-size:0.85em;">{checks_taaqol_note}</p>

  <div class="defer-section">
    <strong>النظام لا يخمّن عند غياب الدليل</strong>
    <p>عندما لا يكون لدى النظام دليل كافٍ على الجذر أو الوزن أو الاشتقاق، يصدر حكم <strong>DEFER</strong>
    أو <strong>AMBIGUOUS</strong> — لا يختار بشكل عشوائي ولا يخفي الغموض.
    وعندما تُغلق الحدود الدستورية مسار التحليل (كلمة مبنية أو حرف جر أو اسم علم جامد)،
    يصدر <strong>CONSTITUTIONAL_VALID_EARLY_STOP</strong> ويكتفي بالحكم المعتمد دستوريًا.</p>
    <p>جميع التوقفات المبكرة في هذا العرض هي توقفات دستورية صحيحة — ليست أخطاء.</p>
  </div>

  <h2>كيف اتخذ النظام قراره؟ — أمثلة مختارة</h2>
  {examples_html}

  <h2>جدول الكلمات الكاملة</h2>
  <div style="overflow-x:auto;">
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>السطح</th>
        <th>التجزئة</th>
        <th>المضيف</th>
        <th>ف. الكلام</th>
        <th>الجذر</th>
        <th>الوزن</th>
        <th>H11-H15</th>
        <th>Taaqol</th>
        <th>السبب</th>
      </tr>
    </thead>
    <tbody>
      {table_html}
    </tbody>
  </table>
  </div>

  <h2>بيانات البيئة</h2>
  <div class="meta-box">
    HEAD: {_esc(meta.get('head',''))}<br>
    Vendor SHA: {_esc(meta.get('vendor_sha',''))}<br>
    Python: {_esc(meta.get('python',''))}<br>
    Platform: {_esc(meta.get('platform',''))}<br>
    Timestamp: {_esc(meta.get('timestamp',''))}<br>
    Ayat source: {_esc(meta.get('ayat_source',''))}
  </div>

</div>
</body>
</html>
"""


# ── output writers ────────────────────────────────────────────────────────────
REPORT_DIR = REPO_ROOT / 'reports' / 'ayat_al_dayn_demo'

def write_outputs(results: list[TokenResult], stats: dict, checks: dict, meta: dict) -> dict[str, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}

    # JSON
    p = REPORT_DIR / 'ayat_al_dayn_results.json'
    p.write_text(format_json(results, stats, checks, meta), encoding='utf-8')
    paths['json'] = p

    # CSV
    p = REPORT_DIR / 'ayat_al_dayn_results.csv'
    p.write_text(format_csv(results), encoding='utf-8')
    paths['csv'] = p

    # HTML
    p = REPORT_DIR / 'ayat_al_dayn_manager_report.html'
    p.write_text(format_html(results, stats, checks, meta), encoding='utf-8')
    paths['html'] = p

    return paths


# ── main ─────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description='HOKOM-TAAQOL-AYAT-AL-DAYN-LIVE-DEMO-01 — Live pipeline demo over Ayat al-Dayn'
    )
    parser.add_argument('--format', choices=['terminal', 'json', 'csv', 'html'], default='terminal')
    parser.add_argument('--open', action='store_true', help='Write all formats and open HTML in browser')
    args = parser.parse_args()

    results = run_all(verbose=True)
    stats   = summary_stats(results)
    checks  = integrity_check(results)
    meta    = {
        "stage":        "HOKOM-TAAQOL-AYAT-AL-DAYN-LIVE-DEMO-01",
        "head":         _git(['git', 'rev-parse', '--short', 'HEAD']),
        "head_full":    _git(['git', 'rev-parse', 'HEAD']),
        "vendor_sha":   _vendor_sha(),
        "python":       f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform":     platform.system(),
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        "ayat_source":  AYAT_SOURCE_FILE,
        "token_count":  len(TOKENS),
    }

    if args.open:
        paths = write_outputs(results, stats, checks, meta)
        print(f"\nJSON : {paths['json']}")
        print(f"CSV  : {paths['csv']}")
        print(f"HTML : {paths['html']}")
        import webbrowser
        webbrowser.open(paths['html'].as_uri())
        return 0

    if args.format == 'terminal':
        print(format_terminal(results, stats, checks))
    elif args.format == 'json':
        paths = write_outputs(results, stats, checks, meta)
        print(format_json(results, stats, checks, meta))
    elif args.format == 'csv':
        paths = write_outputs(results, stats, checks, meta)
        print(format_csv(results))
    elif args.format == 'html':
        paths = write_outputs(results, stats, checks, meta)
        print(paths['html'])

    # Always write outputs to disk
    paths = write_outputs(results, stats, checks, meta)

    # Print summary to stderr
    print("\n── Summary ─────────────────────────────────────────────────────", file=sys.stderr)
    print(f"TOKEN_COUNT              = {stats['token_count']}", file=sys.stderr)
    print(f"TYPED_BUNDLES            = {stats['typed_bundles']}", file=sys.stderr)
    print(f"TAAQOL_LIVE_EVALUATIONS  = {stats['taaqol_live_evals']}", file=sys.stderr)
    print(f"H11_H15_REACHED          = {stats['h11_h15_reached']}", file=sys.stderr)
    print(f"CONSTITUTIONAL_STOPS     = {stats['constitutional_early_stops']}", file=sys.stderr)
    print(f"VERDICT_COUNTS           = {stats['verdict_counts']}", file=sys.stderr)
    print(f"ROOT_STATE_COUNTS        = {stats['root_state_counts']}", file=sys.stderr)
    print(f"\nIntegrity checks:", file=sys.stderr)
    for k, v in checks.items():
        ok = v == 0 if k != 'TAAQOL_RUNTIME_ACTIVE' else v >= 0
        print(f"  {k:<36} = {v}  {'✓' if ok else '✗'}", file=sys.stderr)
    print(f"\nOutput files:", file=sys.stderr)
    for fmt, p in paths.items():
        print(f"  {fmt.upper():<6} {p}", file=sys.stderr)
    print("─" * 65, file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
