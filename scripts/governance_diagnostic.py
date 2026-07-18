#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
governance_diagnostic.py — Attachment Guard Governance Diagnostic (read-only)

Fixed (G1–G5 post-implementation): exposes raw_candidates, accepted_candidates,
deferred_candidates, and rejected_candidates as separate lists — not raw
_strip_suffixes output passed off as "accepted".

Run:  python3 scripts/governance_diagnostic.py
"""

from __future__ import annotations
import sys, os, unicodedata
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mabniyat_attachment import (
    recognize_token, _reset_cache,
    _get_suffix_indices, _strip_suffixes,
    _OPS_LAYER_AVAILABLE,
)

# Import _analyze_host / _classify_host (prefer the richer version)
try:
    from mabniyat_attachment import _analyze_host as _host_analyze
    _ANALYZE_HOST_AVAILABLE = True
except ImportError:
    from mabniyat_attachment import _classify_host as _host_classify
    _ANALYZE_HOST_AVAILABLE = False

from mabniyat_layer import load_catalog

try:
    from mabni_layer import get_inventory as _get_ops_inv
except ImportError:
    _get_ops_inv = None

_reset_cache()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _raw_strip(surface: str):
    top, cont = _get_suffix_indices()
    return _strip_suffixes(surface, top, cont)


def _ops_lookup(surface: str) -> bool:
    if _get_ops_inv is None:
        return False
    try:
        return bool(_get_ops_inv().lookup(surface))
    except Exception:
        return False


def _mabni_lookup(surface: str) -> str | None:
    cat = load_catalog(None)
    key = unicodedata.normalize('NFC', surface)
    row = cat['by_vocalized'].get(key)
    if row:
        return row.get('mabni_id', '?')
    return None


def _host_route(host: str, p4: str) -> str:
    if _ANALYZE_HOST_AVAILABLE:
        return _host_analyze(host, p4, None).route
    else:
        return _host_classify(host, p4, None)


def _host_mabni(host: str, p4: str) -> str | None:
    if _ANALYZE_HOST_AVAILABLE:
        return _host_analyze(host, p4, None).mabni_id
    return None


def _host_operator(host: str, p4: str) -> str | None:
    if _ANALYZE_HOST_AVAILABLE:
        return _host_analyze(host, p4, None).operator_id
    return None


def _host_identity(host: str, p4: str) -> str:
    if _ANALYZE_HOST_AVAILABLE:
        return _host_analyze(host, p4, None).identity_status
    return 'N/A'


# ─────────────────────────────────────────────────────────────────────────────
# Candidate partitioner (approximates recognize_token's internal partitioning)
# _valid_multi is internal, so we replicate the essential check:
#   a span sequence is multi-valid if all non-rightmost spans have a
#   mabni_id in _MULTI_SPAN_VALID_IDS | _DEPTH_GUARDED_CATALOG_IDS
#   OR are allomorph spans matching _DEPTH_GUARDED_SUFFIX_ALLOMORPHS.
# For diagnostic purposes we classify ONLY by host route.
# ─────────────────────────────────────────────────────────────────────────────

def _partition_candidates(surface: str, p4: str):
    """
    Returns (raw_candidates, accepted_cands, deferred_cands, rejected_cands).

    raw_candidates    — everything _strip_suffixes yields
    accepted_cands    — host_route not MABNI_DEFERRED
    deferred_cands    — host_route == MABNI_DEFERRED
    rejected_cands    — (empty in this implementation — formerly NOT_SEGMENTED
                         structural rejections before host check; kept for API
                         symmetry and future use)
    """
    raw = _raw_strip(surface)
    raw_cands    = []
    accepted     = []
    deferred     = []
    rejected     = []

    for host, spans in raw:
        ids   = [s.mabni_id for s in spans]
        route = _host_route(host, p4)
        entry = {
            'host':     host,
            'mabni_ids': ids,
            'route':    route,
            'mabni_id': _host_mabni(host, p4),
            'op_id':    _host_operator(host, p4),
            'identity': _host_identity(host, p4),
        }
        raw_cands.append(entry)
        if route == 'MABNI_DEFERRED':
            deferred.append(entry)
        else:
            accepted.append(entry)

    return raw_cands, accepted, deferred, rejected


# ─────────────────────────────────────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────────────────────────────────────

def report(case_num: int, label: str, surface: str, p4: str,
           original_surface: str | None = None):
    r = recognize_token(surface, p4, original_surface=original_surface)

    raw_cands, accepted_cands, deferred_cands, rejected_cands = \
        _partition_candidates(surface, p4)

    attached_ids = [s.mabni_id for s in r.attached_mabniyat]
    prefix_ids   = [s.mabni_id for s in r.prefix_operators]

    ops_match   = _ops_lookup(original_surface or surface)
    mabni_match = _mabni_lookup(original_surface or surface)

    print(f"\n{'─'*72}")
    print(f"  Case {case_num}: {label}")
    print(f"{'─'*72}")
    print(f"  original_surface   : {original_surface or '(same)'}")
    print(f"  residual_surface   : {surface}")
    print(f"  p4                 : {p4}")
    print(f"  whole op match     : {ops_match}")
    print(f"  whole mabni match  : {mabni_match}")
    print()
    print(f"  RESULT:")
    print(f"    token_verdict    : {r.segmentation_verdict}")
    print(f"    host_surface     : {r.host_surface!r}")
    print(f"    host_route       : {r.host_route}")
    print(f"    host_mabni_id    : {getattr(r, 'host_mabni_id', 'N/A')}")
    print(f"    host_operator_id : {getattr(r, 'host_operator_id', 'N/A')}")
    print(f"    host_identity    : {getattr(r, 'host_identity_status', 'N/A')}")
    print(f"    inflectional_tail: {r.inflectional_tail!r}")
    print(f"    prefix_operators : {prefix_ids}")
    print(f"    attached_mabniyat: {attached_ids}")
    print(f"    notes            : {r.notes}")
    print()
    print(f"  CANDIDATES:")
    print(f"    raw_candidates ({len(raw_cands)}):")
    for c in raw_cands:
        print(f"      host={c['host']!r:30s}  suffixes={c['mabni_ids']}  route={c['route']}")
    print(f"    accepted_candidates ({len(accepted_cands)}):")
    for c in accepted_cands:
        ident = f"  identity={c['identity']}" if c['identity'] != 'NONE' else ''
        print(f"      host={c['host']!r:30s}  suffixes={c['mabni_ids']}  route={c['route']}"
              f"  mabni_id={c['mabni_id']}  op_id={c['op_id']}{ident}")
    print(f"    deferred_candidates ({len(deferred_cands)}):")
    for c in deferred_cands:
        print(f"      host={c['host']!r:30s}  suffixes={c['mabni_ids']}  route={c['route']}"
              f"  mabni_id={c['mabni_id']}")
    print(f"    rejected_candidates ({len(rejected_cands)}): {rejected_cands}")


# ─────────────────────────────────────────────────────────────────────────────
# Ten governance cases
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "═"*72)
print("  ATTACHMENT GUARD GOVERNANCE DIAGNOSTIC (post G1–G5 implementation)")
print("═"*72)

# G1 — NUN_AL_NISWA morphological gate
report(1, "يَرْمِينَ — mudāri' verb-final ي (NUN_AL_NISWA must survive)",
       "يَرْمِينَ", "ACCEPT")

report(2, "يَسْعَيْنَ — assimilated verb-final ى (NUN_AL_NISWA must survive)",
       "يَسْعَيْنَ", "ACCEPT")

report(3, "نَاءِمِينَ — nominal plural ي (NUN_AL_NISWA must remain blocked)",
       "نَاءِمِينَ", "ACCEPT")

report(4, "ءَلْمَسَاكِينَ — nominal plural after definite article (blocked)",
       "ءَلْمَسَاكِينَ", "ACCEPT")

# G2 — deferred ambiguity (no change)
report(5, "يَدْعُونَ — G2 DEFERRED: WAW+نون رفع vs radical-و+NUN_AL_NISWA",
       "يَدْعُونَ", "ACCEPT")

# G3 — ALIF_AL_ITHNAYN at depth 0 with host validation
report(6, "كَتَبَا — māḍī verb dual (ALIF_AL_ITHNAYN at depth 0, must segment)",
       "كَتَبَا", "ACCEPT")

report(7, "حِينَمَا — مَا suffix (not dual verb, ALIF_AL_ITHNAYN must be blocked)",
       "حِينَمَا", "ACCEPT")

report(8, "كَتَبَاهُ — ALIF_AL_ITHNAYN + HA recursive",
       "كَتَبَاهُ", "ACCEPT")

# G4 — MABNI_DEFERRED monotonicity
report(9, "ذَلِكَهُمْ p4=DEFER — all deferred → must return DEFERRED not OPEN_TO_HR2S",
       "ذَلِكَهُمْ", "DEFER")

# G5 — Dual lexical identity
report(10, "ءَنْنَهُمْ / أَنَّهُمْ — DUAL_LICENSED: host has both mabni_id and operator_id",
       "ءَنْنَهُمْ", "ACCEPT", original_surface="أَنَّهُمْ")

# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*72)
print("  GOVERNANCE SUMMARY (expected outcomes after G1–G5 fixes)")
print("═"*72)
print("""
  G1 — NUN_AL_NISWA morphological gate:
     يَرْمِينَ, يَسْعَيْنَ → SEGMENTED with NUN_AL_NISWA (previously blocked).
     نَاءِمِينَ, ءَلْمَسَاكِينَ → NOT_SEGMENTED (guard still applies to nominals).
     Detection: _is_mudaric_form() checks يَ/تَ prefix + fatha + sukun pattern.

  G2 — يَدْعُونَ ambiguity (DEFERRED — not changed):
     Treated as WAW_AL_JAMAA + inflectional نَ (MSA default).
     Documented as TODO in _VERBAL_PLURAL_PATTERNS.
     No word-specific exception created.

  G3 — ALIF_AL_ITHNAYN host validation:
     Removed from _DEPTH_GUARDED_CATALOG_IDS; added to _MULTI_SPAN_VALID_IDS.
     كَتَبَا, ذَهَبَا → SEGMENTED at depth 0 (previously blocked by depth guard).
     حِينَمَا → NOT_SEGMENTED (kasra on first letter fails _is_verbal_dual_host).
     كَتَبَاهُ → SEGMENTED with ALIF_AL_ITHNAYN + HA (multi-span valid).

  G4 — P4 monotonicity for MABNI_DEFERRED candidates:
     When all candidates are MABNI_DEFERRED, returns DEFERRED segmentation_verdict
     with host_route=MABNI_DEFERRED — not NOT_SEGMENTED/OPEN_TO_HR2S.

  G5 — Dual lexical identity in TokenAnalysis:
     host_mabni_id, host_operator_id, host_identity_status fields added.
     أَنَّهُمْ → OPERATOR_BOUNDARY, DUAL_LICENSED, mabni_id=ANNA, op_id=ANNA.
     Operator-first routing preserved; mabni identity not erased.
""")
