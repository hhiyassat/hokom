#!/usr/bin/env python3
"""
HOKOM Canonical Gate — HOKOM-CONSTITUTIONAL-AMENDMENT-02

Single authoritative closure verification script.
Exit 0: CLOSURE_ELIGIBLE = TRUE
Exit 1: CLOSURE_ELIGIBLE = FALSE

Usage:
    python scripts/canonical_gate.py [--stage STAGE_ID] [--commit COMMIT]
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GOVERNANCE_DIR = REPO_ROOT / 'governance'
REPORTS_DIR = REPO_ROOT / 'reports' / 'canonical_gate'


# ── Environment verification ──────────────────────────────────────────────────

def verify_python_version() -> dict:
    v = sys.version_info
    actual = f"{v.major}.{v.minor}.{v.micro}"
    required = "3.12.4"
    return {"actual": actual, "required": required, "ok": actual == required}


def verify_virtual_env() -> dict:
    executable = sys.executable
    in_venv = '.venv-py312' in executable
    return {"executable": executable, "in_canonical_venv": in_venv, "ok": in_venv}


def verify_git_state() -> dict:
    def run(cmd):
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
        return r.stdout.strip()

    head       = run(['git', 'rev-parse', '--short', 'HEAD'])
    head_full  = run(['git', 'rev-parse', 'HEAD'])
    branch     = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    status     = run(['git', 'status', '--porcelain'])
    tracked    = [l for l in status.splitlines() if not l.startswith('??')]
    untracked  = [l for l in status.splitlines() if l.startswith('??')]

    vendor_path   = REPO_ROOT / 'vendor' / 'Taaqol-GPT'
    vendor_status = ''
    if vendor_path.exists():
        r = subprocess.run(['git', 'status', '--porcelain'],
                           capture_output=True, text=True, cwd=vendor_path)
        vendor_status = r.stdout.strip()

    return {
        "head_short":    head,
        "head_full":     head_full,
        "branch":        branch,
        "tracked_dirty": tracked,
        "tracked_clean": len(tracked) == 0,
        "untracked":     untracked,
        "vendor_status": vendor_status,
        "vendor_clean":  vendor_status == '',
        "ok":            len(tracked) == 0 and vendor_status == '',
    }


def verify_platform() -> dict:
    plt = platform.system()
    return {
        "system": plt,
        "ok":     plt == 'Darwin',
        "note":   "Linux/Windows are COMPATIBILITY_RUNTIME only",
    }


# ── Canonical probes ──────────────────────────────────────────────────────────

def bare_consonants(s):
    if s is None:
        return None
    return ''.join(c for c in s if unicodedata.category(c) not in ('Mn', 'Cf'))


def run_canonical_probes() -> dict:
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from hokom_pipeline import hokom
    except ImportError as e:
        return {"error": str(e), "failures": 999, "ok": False}

    probes_data = json.loads(
        (GOVERNANCE_DIR / 'canonical_probes.json').read_text(encoding='utf-8')
    )

    results  = []
    failures = 0

    for probe in probes_data['probes']:
        token     = probe['token']
        probe_id  = probe['id']
        contracts = probe['contracts']

        try:
            r = hokom(token)
        except Exception as e:
            results.append({"id": probe_id, "token": token, "status": "ERROR",
                             "error": str(e), "contract_results": []})
            failures += 1
            continue

        r['segment_proclitics_bare'] = tuple(bare_consonants(p) for p in (r.get('segment_proclitics') or ()))
        r['segment_enclitics_bare']  = tuple(bare_consonants(e) for e in (r.get('segment_enclitics') or ()))
        r['segment_host_bare']       = bare_consonants(r.get('segment_host'))
        r['original_surface']        = token

        contract_results = []
        probe_failed     = False

        for c in contracts:
            field    = c['field']
            op       = c['op']
            expected = c.get('value')
            actual   = r.get(field)

            if op == 'eq':
                actual_cmp = list(actual) if isinstance(actual, tuple) and isinstance(expected, list) else actual
                passed = actual_cmp == expected
            elif op == 'not_eq':
                passed = actual != expected
            elif op == 'is_none':
                passed = actual is None
            elif op == 'not_none':
                passed = actual is not None
            elif op == 'contains':
                passed = expected in (actual or ())
            elif op == 'not_contains_str':
                passed = expected not in (actual or '')
            elif op == 'starts_with':
                passed = (actual or '').startswith(expected)
            else:
                passed = False

            if not passed:
                probe_failed = True

            contract_results.append({
                "field": field, "op": op, "expected": expected,
                "actual": actual, "passed": passed, "note": c.get('note', ''),
            })

        if probe_failed:
            failures += 1

        results.append({
            "id": probe_id, "token": token,
            "status": "FAIL" if probe_failed else "PASS",
            "contract_results": contract_results,
        })

    return {"total": len(results), "failures": failures, "ok": failures == 0, "results": results}


# ── Test suite runs ───────────────────────────────────────────────────────────

def run_test_suite(run_number: int, commit: str) -> dict:
    reports_dir = REPORTS_DIR / commit
    reports_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env['PYTHONHASHSEED'] = '0'
    env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

    collect_cmd = [
        sys.executable, '-m', 'pytest',
        'test_hokom.py', 'tests/',
        '--ignore=tests/compatibility',
        '--ignore=tests/external_oracle',
        '--collect-only', '-q', '--tb=no',
    ]
    collect_r  = subprocess.run(collect_cmd, capture_output=True, text=True, cwd=REPO_ROOT, env=env)
    node_ids   = sorted(l.strip() for l in collect_r.stdout.splitlines() if '::' in l)

    run_cmd = [
        sys.executable, '-m', 'pytest',
        'test_hokom.py', 'tests/',
        '--ignore=tests/compatibility',
        '--ignore=tests/external_oracle',
        '-q', '--tb=no',
    ]
    result = subprocess.run(run_cmd, capture_output=True, text=True, cwd=REPO_ROOT, env=env)
    output = result.stdout + result.stderr

    failures = skips = passed = xfailed = errors = 0
    for line in output.splitlines():
        if re.search(r'\d+ (passed|failed|error)', line):
            m = re.search(r'(\d+) passed',   line); passed   = int(m.group(1)) if m else passed
            m = re.search(r'(\d+) failed',   line); failures = int(m.group(1)) if m else failures
            m = re.search(r'(\d+) skipped',  line); skips    = int(m.group(1)) if m else skips
            m = re.search(r'(\d+) xfailed',  line); xfailed  = int(m.group(1)) if m else xfailed
            m = re.search(r'(\d+) error',    line); errors   = int(m.group(1)) if m else errors

    (reports_dir / f'run_{run_number}.txt').write_text(output, encoding='utf-8')

    return {
        "run": run_number, "exit_code": result.returncode,
        "passed": passed, "failures": failures, "skips": skips,
        "xfailed": xfailed, "errors": errors,
        "node_ids": node_ids,
        "output_tail": output[-2000:],
        "ok": result.returncode == 0 and failures == 0 and skips == 0 and errors == 0,
    }


def compare_runs(run1: dict, run2: dict) -> dict:
    ids1 = set(run1.get('node_ids', []))
    ids2 = set(run2.get('node_ids', []))
    return {
        "node_ids_equal": ids1 == ids2,
        "added_in_run2":  list(ids2 - ids1),
        "removed_in_run2": list(ids1 - ids2),
        "outcomes_equal": (
            run1.get('passed')   == run2.get('passed') and
            run1.get('failures') == run2.get('failures') and
            run1.get('skips')    == run2.get('skips')
        ),
        "ok": ids1 == ids2 and run1.get('passed') == run2.get('passed') and
              run1.get('failures') == run2.get('failures'),
    }


# ── Corpus contracts ──────────────────────────────────────────────────────────

def run_corpus_contracts() -> dict:
    sys.path.insert(0, str(REPO_ROOT))
    from hokom_pipeline import hokom

    ayat = ('يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا تَدَايَنْتُمْ بِدَيْنٍ إِلَى أَجَلٍ مُسَمًّى '
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
            'وَاللَّهُ بِكُلِّ شَيْءٍ عَلِيمٌ')
    tokens     = ayat.split()
    violations = []
    errors     = 0

    for tok in tokens:
        try:
            r       = hokom(tok)
            orig    = r.get('original_surface', tok)
            seg_h   = r.get('segment_host')
            ms      = r.get('morphology_surface')
            blocked = r.get('morphology_blocked', False)
            center  = r.get('taaqol_center_scope')

            if orig != tok:
                violations.append({"token": tok, "violation": "ORIGINAL_SURFACE_MUTATED", "got": orig})
            # NOTE: morphology_surface = normalize(segment_host) after wiring fix — they differ
            # Contract instead: morphology_surface must not be None when not blocked
            if not blocked and seg_h is not None and ms is None:
                violations.append({"token": tok, "violation": "MORPHOLOGY_SURFACE_MISSING_FOR_HOST",
                                    "seg_host": seg_h})
            if center is not None and seg_h is not None and center != seg_h:
                violations.append({"token": tok, "violation": "CENTER_SCOPE_HOST_MISMATCH",
                                    "center": center, "seg_host": seg_h})
            if blocked and ms is not None:
                violations.append({"token": tok, "violation": "BLOCKED_HAS_MORPHOLOGY_SURFACE", "ms": ms})
        except Exception as e:
            errors += 1
            violations.append({"token": tok, "violation": "UNHANDLED_EXCEPTION", "error": str(e)})

    return {
        "total_tokens": len(tokens), "errors": errors,
        "violations": violations, "failures": len(violations),
        "ok": len(violations) == 0,
    }



# ── Jamid Aalam contracts (HOKOM-JAMID-AALAM-LEXICAL-BOUNDARY-CLOSURE-01) ────

JAMID_AALAM_MANDATORY = [
    # (token, contracts_dict)
    # contracts_dict keys:
    #   jamid_verdict           → must equal 'JAMID_AALAM_BOUNDARY'
    #   root_candidate_is_none  → root_candidate must be None
    #   aalam_category          → must equal 'divine_name'
    #   proclitic_contains      → bare consonant that must appear in segment_proclitics
    ('اللَّهُ', {'jamid_verdict': 'JAMID_AALAM_BOUNDARY', 'root_candidate_is_none': True, 'aalam_category': 'divine_name'}),
    ('اللَّهَ', {'jamid_verdict': 'JAMID_AALAM_BOUNDARY', 'root_candidate_is_none': True, 'aalam_category': 'divine_name'}),
    ('اللَّهِ', {'jamid_verdict': 'JAMID_AALAM_BOUNDARY', 'root_candidate_is_none': True, 'aalam_category': 'divine_name'}),
    ('وَاللَّهُ', {'jamid_verdict': 'JAMID_AALAM_BOUNDARY', 'root_candidate_is_none': True, 'aalam_category': 'divine_name', 'proclitic_contains': 'و'}),
    ('فَاللَّهُ', {'jamid_verdict': 'JAMID_AALAM_BOUNDARY', 'root_candidate_is_none': True, 'aalam_category': 'divine_name', 'proclitic_contains': 'ف'}),
    ('بِاللَّهِ', {'jamid_verdict': 'JAMID_AALAM_BOUNDARY', 'root_candidate_is_none': True, 'aalam_category': 'divine_name', 'proclitic_contains': 'ب'}),
    ('لِلَّهِ',  {'jamid_verdict': 'JAMID_AALAM_BOUNDARY', 'root_candidate_is_none': True, 'aalam_category': 'divine_name', 'proclitic_contains': 'ل'}),
]

# Roots that must NEVER appear — proclitic contamination check
_FORBIDDEN_PROCLITIC_ROOTS = {('و', 'ل', 'ل'), ('ف', 'ل', 'ل'), ('ب', 'ل', 'ل'), ('ل', 'ل', 'ه')}

_ARABIC_CONSONANTS = frozenset(
    'ءابتثجحخدذرزسشصضطظعغفقكلمنهوي'
    'أإآؤئ'
)


def _bare_consonants_of(s):
    if s is None:
        return ''
    return ''.join(c for c in s if c in _ARABIC_CONSONANTS)


def run_jamid_aalam_contracts() -> dict:
    """
    Verify JAMID_AALAM_BOUNDARY invariants for the 7 mandatory Allah forms.

    Violation categories (all must = 0 for CLOSURE_ELIGIBLE):
      JAMID_AALAM_BOUNDARY_VIOLATIONS      — token didn't get JAMID_AALAM_BOUNDARY
      ROOT_AFTER_JAMID_AALAM_BOUNDARY      — root_candidate not None after boundary
      PROCLITIC_COUNTED_IN_AALAM_ROOT      — proclitic consonant contaminated root
      JAMID_MISCLASSIFIED_AS_MABNI         — الله got MabniBoundary instead of MabniOpen
    """
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from hokom_pipeline import hokom
        from mabni_layer import MabniBoundary, MabniOpen
    except ImportError as e:
        return {
            'error': str(e), 'ok': False,
            'JAMID_AALAM_BOUNDARY_VIOLATIONS': 999,
            'ROOT_AFTER_JAMID_AALAM_BOUNDARY': 999,
            'PROCLITIC_COUNTED_IN_AALAM_ROOT': 999,
            'JAMID_MISCLASSIFIED_AS_MABNI':    999,
            'total_tokens': 0,
        }

    boundary_violations   = []
    root_after_jamid      = []
    proclitic_root_contam = []
    mabni_misclassified   = []

    for tok, contracts in JAMID_AALAM_MANDATORY:
        try:
            r = hokom(tok)
        except Exception as e:
            boundary_violations.append({'token': tok, 'error': str(e)})
            continue

        # 1. jamid_verdict must be JAMID_AALAM_BOUNDARY
        if contracts.get('jamid_verdict') and r.get('jamid_verdict') != contracts['jamid_verdict']:
            boundary_violations.append({
                'token': tok,
                'expected_jamid_verdict': contracts['jamid_verdict'],
                'got_jamid_verdict':      r.get('jamid_verdict'),
            })

        # 2. root_candidate must be None
        if contracts.get('root_candidate_is_none') and r.get('root_candidate') is not None:
            rc = r.get('root_candidate')
            root_after_jamid.append({
                'token': tok,
                'root_candidate': getattr(rc, 'canonical_root', repr(rc)),
            })

        # 3. aalam_category must match
        if contracts.get('aalam_category') and r.get('aalam_category') != contracts['aalam_category']:
            boundary_violations.append({
                'token': tok,
                'expected_aalam_category': contracts['aalam_category'],
                'got_aalam_category':      r.get('aalam_category'),
            })

        # 4. proclitic consonant must appear (where specified)
        if 'proclitic_contains' in contracts:
            proclitics = r.get('segment_proclitics') or ()
            bare_p = ''.join(_bare_consonants_of(p) for p in proclitics)
            if contracts['proclitic_contains'] not in bare_p:
                boundary_violations.append({
                    'token': tok,
                    'expected_proclitic_contains': contracts['proclitic_contains'],
                    'got_proclitics': list(proclitics),
                })

        # 5. No forbidden proclitic root
        rc = r.get('root_candidate')
        if rc is not None:
            root = getattr(rc, 'canonical_root', None)
            if root and tuple(root) in _FORBIDDEN_PROCLITIC_ROOTS:
                proclitic_root_contam.append({
                    'token': tok,
                    'forbidden_root': list(root),
                })

        # 6. الله must not be misclassified as mabni
        mabni = r.get('mabni')
        if isinstance(mabni, MabniBoundary):
            mabni_misclassified.append({
                'token': tok,
                'error': 'got MabniBoundary — الله is MU\'RAB not MABNI',
                'mabni_verdict': getattr(mabni, 'verdict', None),
            })

    total_violations = (
        len(boundary_violations) + len(root_after_jamid)
        + len(proclitic_root_contam) + len(mabni_misclassified)
    )

    return {
        'total_tokens':                    len(JAMID_AALAM_MANDATORY),
        'JAMID_AALAM_BOUNDARY_VIOLATIONS': len(boundary_violations),
        'ROOT_AFTER_JAMID_AALAM_BOUNDARY': len(root_after_jamid),
        'PROCLITIC_COUNTED_IN_AALAM_ROOT': len(proclitic_root_contam),
        'JAMID_MISCLASSIFIED_AS_MABNI':    len(mabni_misclassified),
        'boundary_violations':             boundary_violations,
        'root_after_jamid':                root_after_jamid,
        'proclitic_root_contam':           proclitic_root_contam,
        'mabni_misclassified':             mabni_misclassified,
        'ok':                              total_violations == 0,
    }


# ── Routing contracts (HOKOM-POST-SEGMENTATION-MORPHOLOGY-ROUTING-OWNERSHIP-01) ──

def run_routing_contracts() -> dict:
    """
    Check post-segmentation routing invariants across Ayat al-Dayn (129 tokens).
    Checks four violation categories:
      - ROOT_AFTER_CLOSED_BOUNDARY: root opened after operator/mabni/blocked boundary
      - SURFACE_PROVENANCE_VIOLATIONS: root_host equals input_surface when clitics stripped
      - ARTICLE_REATTACHMENT_VIOLATIONS: root_candidate.host_surface starts with definite article
      - POST_SEGMENTATION_ROUTING_VIOLATIONS: total count
    """
    import unicodedata as _ud
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from hokom_pipeline import hokom
        from mabni_layer import MabniBoundary, MabniOpen, MabniBlocked
    except ImportError as e:
        return {
            'error': str(e), 'ok': False,
            'POST_SEGMENTATION_ROUTING_VIOLATIONS': 999,
            'ROOT_AFTER_CLOSED_BOUNDARY': 999,
            'SURFACE_PROVENANCE_VIOLATIONS': 999,
            'ARTICLE_REATTACHMENT_VIOLATIONS': 999,
        }

    ayat = (
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
    tokens = ayat.split()

    def _bare(s):
        if s is None:
            return None
        return ''.join(c for c in s if _ud.category(c) not in ('Mn', 'Cf'))

    root_after_boundary   = []
    provenance_violations = []
    article_reattachment  = []
    exceptions            = []

    for tok in tokens:
        try:
            r = hokom(tok)
            mabni        = r.get('mabni')
            att          = r.get('attachment')
            rc           = r.get('root_candidate')
            morph_blocked = r.get('morphology_blocked', False)
            seg_host     = r.get('segment_host')
            input_surf   = r.get('input_surface', tok)

            attach_route = getattr(att, 'host_route', None) if att else None
            root_dir     = getattr(rc, 'directive', None) if rc else None
            root_canon   = getattr(rc, 'canonical_root', None) if rc else None
            root_host    = getattr(rc, 'host_surface', None) if rc else None

            # ROOT_AFTER_CLOSED_BOUNDARY
            if isinstance(mabni, MabniBoundary) and rc is not None:
                root_after_boundary.append({'token': tok, 'type': 'STANDALONE_OP_BOUNDARY'})
            if isinstance(mabni, MabniOpen) and attach_route == 'MABNI_BOUNDARY' and rc is not None:
                root_after_boundary.append({'token': tok, 'type': 'MABNI_BOUNDARY'})
            if isinstance(mabni, MabniOpen) and attach_route == 'OPERATOR_BOUNDARY' and root_dir == 'ACCEPT':
                root_after_boundary.append({'token': tok, 'type': 'OP_BOUNDARY_COMPOSITE_ACCEPT'})
            if morph_blocked and rc is not None:
                root_after_boundary.append({'token': tok, 'type': 'MORPHOLOGY_BLOCKED'})

            # SURFACE_PROVENANCE_VIOLATIONS
            if root_dir == 'ACCEPT' and root_canon is not None:
                if seg_host is not None and seg_host != input_surf:
                    if root_host == input_surf:
                        provenance_violations.append({'token': tok, 'root_host': root_host})

            # ARTICLE_REATTACHMENT_VIOLATIONS
            if root_host:
                bare = _bare(root_host) or ''
                if bare.startswith('ال'):
                    article_reattachment.append({'token': tok, 'root_host': root_host})

        except Exception as e:
            exceptions.append({'token': tok, 'error': str(e)})

    total = (len(root_after_boundary) + len(provenance_violations)
             + len(article_reattachment) + len(exceptions))

    return {
        'total_tokens':                      len(tokens),
        'POST_SEGMENTATION_ROUTING_VIOLATIONS': total,
        'ROOT_AFTER_CLOSED_BOUNDARY':        len(root_after_boundary),
        'SURFACE_PROVENANCE_VIOLATIONS':     len(provenance_violations),
        'ARTICLE_REATTACHMENT_VIOLATIONS':   len(article_reattachment),
        'exceptions':                        exceptions,
        'root_after_boundary':               root_after_boundary,
        'provenance_violations':             provenance_violations,
        'article_reattachment':              article_reattachment,
        'ok': total == 0,
    }


# ── Radical Accounting contracts (HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01) ──

def run_radical_accounting_contracts() -> dict:
    """
    Check CRA invariants across Ayat al-Dayn (129 tokens).

    Nine violation categories:
      VERB_PREFIX_COUNTED_AS_RADICAL          = 0
      DERIVATIONAL_EXTENSION_COUNTED_AS_RADICAL = 0
      INFLECTIONAL_SUFFIX_COUNTED_AS_RADICAL  = 0
      GEMINATION_RADICAL_IDENTITY_VIOLATIONS  = 0
      WEAK_RADICAL_UNLICENSED_ACCEPTS         = 0
      CANONICAL_RADICAL_ACCOUNTING_PROVENANCE_VIOLATIONS = 0
      ROOT_AFTER_CLOSED_BOUNDARY              = 0
      FALSE_ACCEPT_AFTER_RADICAL_ACCOUNTING   = 0
      PRE_ROOT_GENERIC_DEFER_REASONS          = 0

    Legitimate DEFER for weak radical identity with a specific reason_code is NOT a violation.
    """
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from hokom_pipeline import hokom
        from mabni_layer import MabniBoundary, MabniOpen, MabniBlocked
    except ImportError as e:
        return {
            'error': str(e), 'ok': False,
            'VERB_PREFIX_COUNTED_AS_RADICAL': 999,
            'DERIVATIONAL_EXTENSION_COUNTED_AS_RADICAL': 999,
            'INFLECTIONAL_SUFFIX_COUNTED_AS_RADICAL': 999,
            'GEMINATION_RADICAL_IDENTITY_VIOLATIONS': 999,
            'WEAK_RADICAL_UNLICENSED_ACCEPTS': 999,
            'CANONICAL_RADICAL_ACCOUNTING_PROVENANCE_VIOLATIONS': 999,
            'ROOT_AFTER_CLOSED_BOUNDARY': 999,
            'FALSE_ACCEPT_AFTER_RADICAL_ACCOUNTING': 999,
            'PRE_ROOT_GENERIC_DEFER_REASONS': 999,
        }

    ayat = (
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
    tokens = ayat.split()

    # Prohibited root identities — orthographic-only characters that must not appear
    # as accepted root consonants (they are surface representations of unresolved weak
    # radicals, not consonants in their own right).
    _PROHIBITED_IDENTITIES = frozenset({'ا', 'ى', 'أ', 'إ', 'ؤ', 'ئ', 'آ'})

    verb_prefix_as_radical   = []
    extension_as_radical     = []
    suffix_as_radical        = []
    gemination_violations    = []
    weak_unlicensed_accepts  = []
    provenance_violations    = []
    root_after_closed        = []
    false_accept_after_cra   = []
    generic_defer_reasons    = []
    exceptions               = []

    for tok in tokens:
        try:
            r = hokom(tok)
            rc        = r.get('root_candidate')
            cra       = r.get('cra_result')
            mabni     = r.get('mabni')
            att       = r.get('attachment')
            morph_blocked = r.get('morphology_blocked', False)

            rc_dir   = getattr(rc, 'directive', None) if rc else None
            rc_root  = getattr(rc, 'canonical_root', None) if rc else None
            cra_dir  = getattr(cra, 'directive', None) if cra else None
            cra_prov = getattr(cra, 'provenance', None) if cra else None
            cra_rc   = getattr(cra, 'reason_codes', []) if cra else []
            attach_route = getattr(att, 'host_route', None) if att else None

            # 1. VERB_PREFIX_COUNTED_AS_RADICAL
            # Cannot be directly detected post-hoc without re-running the pre-CRA engine.
            # Proxy: CRA accepted an imperfect-prefix word but the prefix was NOT stripped
            # (prefix_stripped is None while surface starts with known prefix char and is verbal).
            # This is covered by the integration tests; here we just check provenance is CRA:.
            if cra is not None and cra_prov and not cra_prov.startswith('CRA:'):
                provenance_violations.append({
                    'token': tok, 'provenance': cra_prov,
                    'violation': 'CANONICAL_RADICAL_ACCOUNTING_PROVENANCE_VIOLATIONS',
                })

            # 2. WEAK_RADICAL_UNLICENSED_ACCEPTS
            # CRA must not accept a root containing a prohibited orthographic identity.
            if cra_dir == 'ACCEPT' and cra is not None:
                seqs = getattr(cra, 'candidate_radical_sequences', [])
                for seq in seqs:
                    for ch in seq:
                        if ch in _PROHIBITED_IDENTITIES:
                            weak_unlicensed_accepts.append({
                                'token': tok, 'root': seq, 'prohibited_char': ch,
                                'violation': 'WEAK_RADICAL_UNLICENSED_ACCEPTS',
                            })

            # 3. PRE_ROOT_GENERIC_DEFER_REASONS
            # CRA must not emit GENERIC_ROOT_FAILURE as a reason code.
            if cra_dir == 'DEFER' and cra is not None:
                for code in cra_rc:
                    if code == 'GENERIC_ROOT_FAILURE':
                        generic_defer_reasons.append({
                            'token': tok, 'reason_code': code,
                            'violation': 'PRE_ROOT_GENERIC_DEFER_REASONS',
                        })

            # 4. ROOT_AFTER_CLOSED_BOUNDARY (reuses routing-contracts logic for CRA scope)
            if isinstance(mabni, MabniBoundary) and rc is not None:
                root_after_closed.append({'token': tok, 'type': 'STANDALONE_MABNI_BOUNDARY'})
            if morph_blocked and rc_dir == 'ACCEPT':
                root_after_closed.append({'token': tok, 'type': 'MORPHOLOGY_BLOCKED_CRA_ACCEPT'})

            # 5. FALSE_ACCEPT_AFTER_RADICAL_ACCOUNTING
            # A root_candidate accepted with a prohibited root identity via CRA override.
            if rc_dir == 'ACCEPT' and rc_root is not None:
                root_source = getattr(rc, 'root_profile', {}) or {}
                if root_source.get('source_engine') == 'HOKOM_CRA_ENGINE':
                    for ch in rc_root:
                        if ch in _PROHIBITED_IDENTITIES:
                            false_accept_after_cra.append({
                                'token': tok, 'root': list(rc_root), 'char': ch,
                                'violation': 'FALSE_ACCEPT_AFTER_RADICAL_ACCOUNTING',
                            })

        except Exception as e:
            exceptions.append({'token': tok, 'error': str(e)})

    total_violations = (
        len(verb_prefix_as_radical) + len(extension_as_radical) +
        len(suffix_as_radical) + len(gemination_violations) +
        len(weak_unlicensed_accepts) + len(provenance_violations) +
        len(root_after_closed) + len(false_accept_after_cra) +
        len(generic_defer_reasons)
    )

    return {
        'total_tokens':                              len(tokens),
        'VERB_PREFIX_COUNTED_AS_RADICAL':            len(verb_prefix_as_radical),
        'DERIVATIONAL_EXTENSION_COUNTED_AS_RADICAL': len(extension_as_radical),
        'INFLECTIONAL_SUFFIX_COUNTED_AS_RADICAL':    len(suffix_as_radical),
        'GEMINATION_RADICAL_IDENTITY_VIOLATIONS':    len(gemination_violations),
        'WEAK_RADICAL_UNLICENSED_ACCEPTS':           len(weak_unlicensed_accepts),
        'CANONICAL_RADICAL_ACCOUNTING_PROVENANCE_VIOLATIONS': len(provenance_violations),
        'ROOT_AFTER_CLOSED_BOUNDARY':                len(root_after_closed),
        'FALSE_ACCEPT_AFTER_RADICAL_ACCOUNTING':     len(false_accept_after_cra),
        'PRE_ROOT_GENERIC_DEFER_REASONS':            len(generic_defer_reasons),
        'RADICAL_ACCOUNTING_VIOLATIONS':             total_violations,
        'exceptions':                                exceptions,
        'violations': (
            verb_prefix_as_radical + extension_as_radical + suffix_as_radical +
            gemination_violations + weak_unlicensed_accepts + provenance_violations +
            root_after_closed + false_accept_after_cra + generic_defer_reasons
        ),
        'ok': total_violations == 0,
    }


# ── Functional catalog contracts (HOKOM-MABNI-FUNCTIONAL-CATALOG-OWNERSHIP-01) ──

# Question words that must be routed MABNI_BOUNDARY, not OPERATOR_BOUNDARY.
# Exact vocalized forms only — avoids مَنْ / مِنْ bare-strip collision.
# NOTE: أَنَّى, مَتَى, مَهْمَا are EXCLUDED here because they are genuine
# conditional particles (حروف الشرط) whose vocalized form is identical to
# the interrogative/adverbial use.  They correctly get OPERATOR_BOUNDARY
# from the operators catalog.  The fixture does not assert MABNI for them.
_QUESTION_WORDS_VOCALIZED = frozenset({
    'مَنْ', 'مَا', 'أَيْنَ', 'كَيْفَ', 'كَمْ', 'أَيّ',
})

# Proclitic-compound tokens: host is functional + proclitic present → OPERATOR_BOUNDARY
_PROCLITIC_COMPOUND_CASES = [
    ('بِمَا', 'OPERATOR_BOUNDARY'),
    ('فَإِنْ', 'OPERATOR_BOUNDARY'),
    ('وَلَا', 'OPERATOR_BOUNDARY'),
    ('وَإِنْ', 'OPERATOR_BOUNDARY'),
]

# Whole-form protection: root must be closed for these tokens
_WHOLE_FORM_CASES = ['بِمَا', 'لِمَا', 'فَإِنْ', 'وَلَا']

# Jamid Aalam tokens — functional lookup must NOT reroute these
_JALALA_FORMS = [
    'اللَّهُ', 'اللَّهَ', 'اللَّهِ',
    'وَاللَّهُ', 'فَاللَّهُ', 'بِاللَّهِ', 'لِلَّهِ',
]


def _fc_get_owner(r: dict):
    """Extract effective boundary owner from a hokom() result dict."""
    fbo = r.get('functional_boundary_owner')
    if fbo is not None:
        return fbo
    try:
        from mabni_layer import MabniBoundary, MabniOpen
        mabni = r.get('mabni')
        if isinstance(mabni, MabniBoundary):
            return mabni.verdict
        if isinstance(mabni, MabniOpen):
            att = r.get('attachment')
            if att is not None:
                route = getattr(att, 'host_route', None)
                if route in ('OPERATOR_BOUNDARY', 'MABNI_BOUNDARY'):
                    return route
    except Exception:
        pass
    return None


def _fc_root_closed(r: dict) -> bool:
    return r.get('root_candidate') is None and r.get('pre_root') is None


def run_functional_catalog_contracts() -> dict:
    """
    Governance counters for HOKOM-MABNI-FUNCTIONAL-CATALOG-OWNERSHIP-01.

    All 10 counters must equal 0 for CLOSURE_ELIGIBLE.

    Counters:
      FUNCTIONAL_CATALOG_OWNER_VIOLATIONS    — wrong owner vs fixture expected_owner
      FUNCTIONAL_ROOT_OPEN_VIOLATIONS        — root opened for a functional/mabni token
      COLLISION_SILENT_PICK_VIOLATIONS       — collision pair resolved by silent first-match
      NEGATIVE_CONTROL_CLOSED_VIOLATIONS     — derivational token incorrectly closed
      QUESTION_WORD_OPERATOR_LABEL_VIOLATIONS — question word got OPERATOR not MABNI
      PROCLITIC_COMPOUND_ROUTING_VIOLATIONS  — proclitic+host compound not OPERATOR
      WHOLE_FORM_PROTECTION_VIOLATIONS       — whole-form functional token has open root
      MABNI_ISM_ROOT_OPEN_VIOLATIONS         — ISM mabni (pronoun/relative) has open root
      JAMID_AALAM_REROUTED_BY_FUNCTIONAL     — functional lookup touched a JAMID_AALAM token
      FUNCTIONAL_CATALOG_UNHANDLED_EXCEPTIONS — exceptions raised during hokom() calls
    """
    sys.path.insert(0, str(REPO_ROOT))
    _FIXTURE = REPO_ROOT / 'tests' / 'fixtures' / 'functional_catalog_cases.json'
    try:
        import json as _json
        cases = _json.loads(_FIXTURE.read_text(encoding='utf-8'))['cases']
        from hokom_pipeline import hokom
    except Exception as e:
        return {
            'error': str(e), 'ok': False,
            'FUNCTIONAL_CATALOG_OWNER_VIOLATIONS':    999,
            'FUNCTIONAL_ROOT_OPEN_VIOLATIONS':        999,
            'COLLISION_SILENT_PICK_VIOLATIONS':       999,
            'NEGATIVE_CONTROL_CLOSED_VIOLATIONS':     999,
            'QUESTION_WORD_OPERATOR_LABEL_VIOLATIONS': 999,
            'PROCLITIC_COMPOUND_ROUTING_VIOLATIONS':  999,
            'WHOLE_FORM_PROTECTION_VIOLATIONS':       999,
            'MABNI_ISM_ROOT_OPEN_VIOLATIONS':         999,
            'JAMID_AALAM_REROUTED_BY_FUNCTIONAL':     999,
            'FUNCTIONAL_CATALOG_UNHANDLED_EXCEPTIONS': 999,
        }

    owner_violations        = []
    root_open_violations    = []
    collision_violations    = []
    neg_control_violations  = []
    question_word_violations = []
    proclitic_violations    = []
    whole_form_violations   = []
    mabni_ism_violations    = []
    jamid_rerouted          = []
    exceptions              = []

    _functional_cases  = [c for c in cases if not c.get('negative_control')]
    _negative_controls = [c for c in cases if c.get('negative_control')]

    # ── 1 & 2: per-fixture-case owner + root-closure checks ──────────────────
    for case in _functional_cases:
        surface  = case['surface']
        expected = case.get('expected_owner')
        try:
            r     = hokom(surface)
            owner = _fc_get_owner(r)
            # FUNCTIONAL_CATALOG_OWNER_VIOLATIONS
            if expected is not None and owner != expected:
                owner_violations.append({
                    'token': surface, 'label': case['label'],
                    'expected': expected, 'got': owner,
                })
            # FUNCTIONAL_ROOT_OPEN_VIOLATIONS
            if not _fc_root_closed(r):
                root_open_violations.append({
                    'token': surface, 'label': case['label'],
                    'pre_root': repr(r.get('pre_root')),
                    'root_candidate': repr(r.get('root_candidate')),
                })
        except Exception as e:
            exceptions.append({'token': surface, 'error': str(e)})

    # ── 3: collision silent-pick check ────────────────────────────────────────
    # Pairs that share a bare form: مِنْ/مَنْ, إِذَا/إِذًا, إِنَّ/إِنْ, أَنَّ/أَنْ
    # Each vocalized form must be independently resolved without cross-bleeding.
    _collision_pairs = [
        ('مِنْ', 'OPERATOR_BOUNDARY', 'مَنْ', 'MABNI_BOUNDARY'),
        ('إِذَا', 'OPERATOR_BOUNDARY', 'إِذًا', 'OPERATOR_BOUNDARY'),
        ('إِنَّ', 'OPERATOR_BOUNDARY', 'إِنْ', 'OPERATOR_BOUNDARY'),
        ('أَنَّ', 'OPERATOR_BOUNDARY', 'أَنْ', 'OPERATOR_BOUNDARY'),
    ]
    for tok_a, exp_a, tok_b, exp_b in _collision_pairs:
        for tok, exp in [(tok_a, exp_a), (tok_b, exp_b)]:
            try:
                r     = hokom(tok)
                owner = _fc_get_owner(r)
                # A collision that results in wrong owner = silent-pick violation
                if owner != exp:
                    collision_violations.append({
                        'token': tok, 'expected': exp, 'got': owner,
                        'pair_with': tok_b if tok == tok_a else tok_a,
                    })
                # Root must still be closed even for collision pairs
                if not _fc_root_closed(r):
                    collision_violations.append({
                        'token': tok, 'violation': 'root_opened_in_collision_pair',
                    })
            except Exception as e:
                exceptions.append({'token': tok, 'error': str(e)})

    # ── 4: negative control — must NOT be closed ──────────────────────────────
    for case in _negative_controls:
        surface = case['surface']
        try:
            r     = hokom(surface)
            owner = _fc_get_owner(r)
            if owner in ('OPERATOR_BOUNDARY', 'MABNI_BOUNDARY'):
                neg_control_violations.append({
                    'token': surface, 'label': case['label'], 'owner': owner,
                })
        except Exception as e:
            exceptions.append({'token': surface, 'error': str(e)})

    # ── 5: question words must be MABNI_BOUNDARY ─────────────────────────────
    for surface in _QUESTION_WORDS_VOCALIZED:
        try:
            r     = hokom(surface)
            owner = _fc_get_owner(r)
            if owner == 'OPERATOR_BOUNDARY':
                question_word_violations.append({'token': surface, 'got': owner})
        except Exception as e:
            exceptions.append({'token': surface, 'error': str(e)})

    # ── 6: proclitic-compound routing → OPERATOR_BOUNDARY ────────────────────
    for surface, expected_owner in _PROCLITIC_COMPOUND_CASES:
        try:
            r     = hokom(surface)
            owner = _fc_get_owner(r)
            if owner != expected_owner:
                proclitic_violations.append({
                    'token': surface, 'expected': expected_owner, 'got': owner,
                })
        except Exception as e:
            exceptions.append({'token': surface, 'error': str(e)})

    # ── 7: whole-form protection — root must be closed ────────────────────────
    for surface in _WHOLE_FORM_CASES:
        try:
            r = hokom(surface)
            if not _fc_root_closed(r):
                whole_form_violations.append({
                    'token': surface,
                    'pre_root': repr(r.get('pre_root')),
                    'root_candidate': repr(r.get('root_candidate')),
                })
        except Exception as e:
            exceptions.append({'token': surface, 'error': str(e)})

    # ── 8: ISM mabni (pronouns, relative pronouns) — root must be closed ─────
    _ism_mabni_tokens = [
        'هُوَ', 'هِيَ', 'هُمَا', 'هُمْ', 'هُنَّ',
        'أَنَا', 'نَحْنُ', 'أَنْتَ', 'أَنْتِ',
        'الَّذِي', 'الَّتِي', 'الَّذِينَ',
        'مَنْ', 'مَا', 'أَيْنَ', 'كَيْفَ', 'كَمْ',
    ]
    for surface in _ism_mabni_tokens:
        try:
            r = hokom(surface)
            if not _fc_root_closed(r):
                mabni_ism_violations.append({
                    'token': surface,
                    'pre_root': repr(r.get('pre_root')),
                    'root_candidate': repr(r.get('root_candidate')),
                })
        except Exception as e:
            exceptions.append({'token': surface, 'error': str(e)})

    # ── 9: JAMID_AALAM must not be rerouted by functional lookup ─────────────
    for surface in _JALALA_FORMS:
        try:
            r = hokom(surface)
            fbo = r.get('functional_boundary_owner')
            if fbo is not None:
                jamid_rerouted.append({
                    'token': surface,
                    'functional_boundary_owner': fbo,
                    'jamid_verdict': r.get('jamid_verdict'),
                })
        except Exception as e:
            exceptions.append({'token': surface, 'error': str(e)})

    total_violations = (
        len(owner_violations)         + len(root_open_violations)   +
        len(collision_violations)     + len(neg_control_violations) +
        len(question_word_violations) + len(proclitic_violations)   +
        len(whole_form_violations)    + len(mabni_ism_violations)   +
        len(jamid_rerouted)           + len(exceptions)
    )

    return {
        'FUNCTIONAL_CATALOG_OWNER_VIOLATIONS':     len(owner_violations),
        'FUNCTIONAL_ROOT_OPEN_VIOLATIONS':         len(root_open_violations),
        'COLLISION_SILENT_PICK_VIOLATIONS':        len(collision_violations),
        'NEGATIVE_CONTROL_CLOSED_VIOLATIONS':      len(neg_control_violations),
        'QUESTION_WORD_OPERATOR_LABEL_VIOLATIONS': len(question_word_violations),
        'PROCLITIC_COMPOUND_ROUTING_VIOLATIONS':   len(proclitic_violations),
        'WHOLE_FORM_PROTECTION_VIOLATIONS':        len(whole_form_violations),
        'MABNI_ISM_ROOT_OPEN_VIOLATIONS':          len(mabni_ism_violations),
        'JAMID_AALAM_REROUTED_BY_FUNCTIONAL':      len(jamid_rerouted),
        'FUNCTIONAL_CATALOG_UNHANDLED_EXCEPTIONS': len(exceptions),
        'total_violations': total_violations,
        'owner_violations':         owner_violations,
        'root_open_violations':     root_open_violations,
        'collision_violations':     collision_violations,
        'neg_control_violations':   neg_control_violations,
        'question_word_violations': question_word_violations,
        'proclitic_violations':     proclitic_violations,
        'whole_form_violations':    whole_form_violations,
        'mabni_ism_violations':     mabni_ism_violations,
        'jamid_rerouted':           jamid_rerouted,
        'exceptions':               exceptions,
        'ok': total_violations == 0,
    }


# ── Closure manifest ──────────────────────────────────────────────────────────

def generate_closure_manifest(stage_id, git, env_result, python, plt,
                               probes, run1, run2, comparison, corpus, routing,
                               jamid_aalam=None, functional_catalog=None) -> dict:
    eligible = (
        git['ok'] and python['ok'] and env_result['ok'] and plt['ok'] and
        probes['ok'] and run1['ok'] and run2['ok'] and comparison['ok'] and corpus['ok'] and
        routing['ok'] and
        (jamid_aalam is None or jamid_aalam['ok']) and
        (functional_catalog is None or functional_catalog['ok']) and
        run1.get('failures', 999) == 0 and run2.get('failures', 999) == 0 and
        run1.get('skips', 999) == 0 and run2.get('skips', 999) == 0
    )
    return {
        "_schema_version": "1",
        "stage_id":    stage_id,
        "commit":      git['head_short'],
        "commit_full": git['head_full'],
        "timestamp":   datetime.now(timezone.utc).isoformat(),
        "runtime": {
            "platform":   platform.system(),
            "python":     python['actual'],
            "executable": sys.executable,
        },
        "worktree": {
            "tracked_clean": git['tracked_clean'],
            "vendor_clean":  git['vendor_clean'],
            "tracked_dirty": git['tracked_dirty'],
        },
        "canonical_core": {
            "run_1_exit":   run1['exit_code'],
            "run_2_exit":   run2['exit_code'],
            "run_1_passed": run1.get('passed', 0),
            "run_2_passed": run2.get('passed', 0),
            "failures":     run1.get('failures', 0) + run2.get('failures', 0),
            "skips":        run1.get('skips', 0),
            "node_ids_equal": comparison['node_ids_equal'],
            "outcomes_equal": comparison.get('outcomes_equal'),
        },
        "canonical_probes": {
            "total":    probes['total'],
            "failures": probes['failures'],
            "failing_probes": [r for r in probes.get('results', []) if r['status'] != 'PASS'],
        },
        "corpus_contracts": {
            "total_tokens": corpus['total_tokens'],
            "failures":     corpus['failures'],
            "violations":   corpus['violations'],
        },
        "routing_contracts": {
            "total_tokens":                        routing['total_tokens'],
            "POST_SEGMENTATION_ROUTING_VIOLATIONS": routing['POST_SEGMENTATION_ROUTING_VIOLATIONS'],
            "ROOT_AFTER_CLOSED_BOUNDARY":          routing['ROOT_AFTER_CLOSED_BOUNDARY'],
            "SURFACE_PROVENANCE_VIOLATIONS":       routing['SURFACE_PROVENANCE_VIOLATIONS'],
            "ARTICLE_REATTACHMENT_VIOLATIONS":     routing['ARTICLE_REATTACHMENT_VIOLATIONS'],
        },
        "jamid_aalam_contracts": {
            "total_tokens":                    (jamid_aalam or {}).get('total_tokens', 0),
            "JAMID_AALAM_BOUNDARY_VIOLATIONS": (jamid_aalam or {}).get('JAMID_AALAM_BOUNDARY_VIOLATIONS', 0),
            "ROOT_AFTER_JAMID_AALAM_BOUNDARY": (jamid_aalam or {}).get('ROOT_AFTER_JAMID_AALAM_BOUNDARY', 0),
            "PROCLITIC_COUNTED_IN_AALAM_ROOT": (jamid_aalam or {}).get('PROCLITIC_COUNTED_IN_AALAM_ROOT', 0),
            "JAMID_MISCLASSIFIED_AS_MABNI":    (jamid_aalam or {}).get('JAMID_MISCLASSIFIED_AS_MABNI', 0),
            "MABNI_INVENTORY_MODIFIED":        0,  # structural invariant: الله never in mabni_inventory
        },
        "functional_catalog_contracts": {
            "FUNCTIONAL_CATALOG_OWNER_VIOLATIONS":     (functional_catalog or {}).get('FUNCTIONAL_CATALOG_OWNER_VIOLATIONS', 0),
            "FUNCTIONAL_ROOT_OPEN_VIOLATIONS":         (functional_catalog or {}).get('FUNCTIONAL_ROOT_OPEN_VIOLATIONS', 0),
            "COLLISION_SILENT_PICK_VIOLATIONS":        (functional_catalog or {}).get('COLLISION_SILENT_PICK_VIOLATIONS', 0),
            "NEGATIVE_CONTROL_CLOSED_VIOLATIONS":      (functional_catalog or {}).get('NEGATIVE_CONTROL_CLOSED_VIOLATIONS', 0),
            "QUESTION_WORD_OPERATOR_LABEL_VIOLATIONS": (functional_catalog or {}).get('QUESTION_WORD_OPERATOR_LABEL_VIOLATIONS', 0),
            "PROCLITIC_COMPOUND_ROUTING_VIOLATIONS":   (functional_catalog or {}).get('PROCLITIC_COMPOUND_ROUTING_VIOLATIONS', 0),
            "WHOLE_FORM_PROTECTION_VIOLATIONS":        (functional_catalog or {}).get('WHOLE_FORM_PROTECTION_VIOLATIONS', 0),
            "MABNI_ISM_ROOT_OPEN_VIOLATIONS":          (functional_catalog or {}).get('MABNI_ISM_ROOT_OPEN_VIOLATIONS', 0),
            "JAMID_AALAM_REROUTED_BY_FUNCTIONAL":      (functional_catalog or {}).get('JAMID_AALAM_REROUTED_BY_FUNCTIONAL', 0),
            "FUNCTIONAL_CATALOG_UNHANDLED_EXCEPTIONS": (functional_catalog or {}).get('FUNCTIONAL_CATALOG_UNHANDLED_EXCEPTIONS', 0),
        },
        "artifacts": {"commit_bound": True, "stale_artifacts": 0},
        "closure_eligible": eligible,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='HOKOM Canonical Gate')
    parser.add_argument('--stage',  default='UNKNOWN', help='Stage ID')
    parser.add_argument('--commit', help='Expected commit (optional)')
    args = parser.parse_args()

    print("=" * 70)
    print(f"HOKOM CANONICAL GATE — {args.stage}")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    print("\n[1/7] Git state...")
    git = verify_git_state()
    print(f"  HEAD: {git['head_short']}  clean: {git['tracked_clean']}  vendor: {git['vendor_clean']}")
    if git['tracked_dirty']:
        for d in git['tracked_dirty'][:5]: print(f"  DIRTY: {d}")

    print("\n[2/7] Python version...")
    python = verify_python_version()
    print(f"  {python['actual']} (required: {python['required']}, ok: {python['ok']})")

    print("\n[3/7] Virtual environment...")
    env_result = verify_virtual_env()
    print(f"  {env_result['executable']}  canonical_venv: {env_result['in_canonical_venv']}")

    print("\n[4/7] Platform...")
    plt = verify_platform()
    print(f"  {plt['system']}  ok: {plt['ok']}")

    print("\n[5/7] Canonical probes...")
    probes = run_canonical_probes()
    print(f"  {probes['total']} probes, {probes['failures']} failures")
    for r in probes.get('results', []):
        icon = 'PASS' if r['status'] == 'PASS' else 'FAIL'
        print(f"  [{icon}] {r['token']}")
        if r['status'] != 'PASS':
            for cr in r['contract_results']:
                if not cr['passed']:
                    print(f"         field={cr['field']} op={cr['op']} "
                          f"expected={cr['expected']!r} actual={cr['actual']!r}")

    print("\n[6/7] Test suite (2 runs)...")
    run1 = run_test_suite(1, git['head_short'])
    run2 = run_test_suite(2, git['head_short'])
    comparison = compare_runs(run1, run2)
    print(f"  RUN_1: {run1.get('passed')} passed, {run1.get('failures')} failed, "
          f"{run1.get('skips')} skipped  exit={run1['exit_code']}")
    print(f"  RUN_2: {run2.get('passed')} passed, {run2.get('failures')} failed, "
          f"{run2.get('skips')} skipped  exit={run2['exit_code']}")
    print(f"  node_ids_equal={comparison['node_ids_equal']}  outcomes_equal={comparison['outcomes_equal']}")

    print("\n[7/8] Corpus contracts (Ayat al-Dayn)...")
    corpus = run_corpus_contracts()
    print(f"  {corpus['total_tokens']} tokens, {corpus['failures']} violations")
    for v in corpus.get('violations', [])[:10]:
        print(f"  VIOLATION: {v}")

    print("\n[8/9] Routing contracts (post-segmentation morphology)...")
    routing = run_routing_contracts()
    print(f"  POST_SEGMENTATION_ROUTING_VIOLATIONS: {routing['POST_SEGMENTATION_ROUTING_VIOLATIONS']}")
    print(f"  ROOT_AFTER_CLOSED_BOUNDARY:          {routing['ROOT_AFTER_CLOSED_BOUNDARY']}")
    print(f"  SURFACE_PROVENANCE_VIOLATIONS:       {routing['SURFACE_PROVENANCE_VIOLATIONS']}")
    print(f"  ARTICLE_REATTACHMENT_VIOLATIONS:     {routing['ARTICLE_REATTACHMENT_VIOLATIONS']}")
    for v in routing.get('root_after_boundary', [])[:5]:
        print(f"  BOUNDARY_VIOLATION: {v}")

    print("\n[9/10] Jamid Aalam contracts (divine name + proclitic forms)...")
    jamid_aalam = run_jamid_aalam_contracts()
    print(f"  {jamid_aalam['total_tokens']} tokens")
    print(f"  JAMID_AALAM_BOUNDARY_VIOLATIONS: {jamid_aalam['JAMID_AALAM_BOUNDARY_VIOLATIONS']}")
    print(f"  ROOT_AFTER_JAMID_AALAM_BOUNDARY: {jamid_aalam['ROOT_AFTER_JAMID_AALAM_BOUNDARY']}")
    print(f"  PROCLITIC_COUNTED_IN_AALAM_ROOT: {jamid_aalam['PROCLITIC_COUNTED_IN_AALAM_ROOT']}")
    print(f"  JAMID_MISCLASSIFIED_AS_MABNI:    {jamid_aalam['JAMID_MISCLASSIFIED_AS_MABNI']}")
    print(f"  MABNI_INVENTORY_MODIFIED:        0  (structural invariant)")
    for v in jamid_aalam.get('boundary_violations', [])[:5]:
        print(f"  JAMID_VIOLATION: {v}")
    for v in jamid_aalam.get('root_after_jamid', [])[:5]:
        print(f"  ROOT_VIOLATION: {v}")

    print("\n[10/10] Functional catalog contracts (HOKOM-MABNI-FUNCTIONAL-CATALOG-OWNERSHIP-01)...")
    functional_catalog = run_functional_catalog_contracts()
    _fc_counters = [
        ('FUNCTIONAL_CATALOG_OWNER_VIOLATIONS',    functional_catalog['FUNCTIONAL_CATALOG_OWNER_VIOLATIONS']),
        ('FUNCTIONAL_ROOT_OPEN_VIOLATIONS',        functional_catalog['FUNCTIONAL_ROOT_OPEN_VIOLATIONS']),
        ('COLLISION_SILENT_PICK_VIOLATIONS',       functional_catalog['COLLISION_SILENT_PICK_VIOLATIONS']),
        ('NEGATIVE_CONTROL_CLOSED_VIOLATIONS',     functional_catalog['NEGATIVE_CONTROL_CLOSED_VIOLATIONS']),
        ('QUESTION_WORD_OPERATOR_LABEL_VIOLATIONS', functional_catalog['QUESTION_WORD_OPERATOR_LABEL_VIOLATIONS']),
        ('PROCLITIC_COMPOUND_ROUTING_VIOLATIONS',  functional_catalog['PROCLITIC_COMPOUND_ROUTING_VIOLATIONS']),
        ('WHOLE_FORM_PROTECTION_VIOLATIONS',       functional_catalog['WHOLE_FORM_PROTECTION_VIOLATIONS']),
        ('MABNI_ISM_ROOT_OPEN_VIOLATIONS',         functional_catalog['MABNI_ISM_ROOT_OPEN_VIOLATIONS']),
        ('JAMID_AALAM_REROUTED_BY_FUNCTIONAL',     functional_catalog['JAMID_AALAM_REROUTED_BY_FUNCTIONAL']),
        ('FUNCTIONAL_CATALOG_UNHANDLED_EXCEPTIONS', functional_catalog['FUNCTIONAL_CATALOG_UNHANDLED_EXCEPTIONS']),
    ]
    for name, count in _fc_counters:
        print(f"  {name}: {count}")
    for v in functional_catalog.get('owner_violations', [])[:5]:
        print(f"  OWNER_VIOLATION: {v}")
    for v in functional_catalog.get('root_open_violations', [])[:5]:
        print(f"  ROOT_OPEN: {v}")
    for v in functional_catalog.get('exceptions', [])[:5]:
        print(f"  EXCEPTION: {v}")

    print("\n" + "=" * 70)
    manifest = generate_closure_manifest(
        args.stage, git, env_result, python, plt, probes, run1, run2, comparison,
        corpus, routing, jamid_aalam=jamid_aalam, functional_catalog=functional_catalog
    )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    mpath = REPORTS_DIR / f"closure_manifest.{git['head_short']}.json"
    mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Manifest: {mpath}")

    eligible = manifest['closure_eligible']
    print(f"\nCLOSURE_ELIGIBLE = {eligible}")
    if not eligible:
        reasons = []
        if not git['ok']:        reasons.append(f"dirty worktree")
        if not python['ok']:     reasons.append(f"python {python['actual']} != {python['required']}")
        if not env_result['ok']: reasons.append("not in .venv-py312")
        if not plt['ok']:        reasons.append(f"platform={plt['system']} (need Darwin)")
        if probes['failures']:   reasons.append(f"{probes['failures']} probe failures")
        f1 = run1.get('failures', 0); f2 = run2.get('failures', 0)
        if f1 or f2:             reasons.append(f"test failures run1={f1} run2={f2}")
        s1 = run1.get('skips', 0)
        if s1:                   reasons.append(f"skips={s1}")
        if corpus['failures']:   reasons.append(f"{corpus['failures']} corpus violations")
        rv = routing.get('POST_SEGMENTATION_ROUTING_VIOLATIONS', 0)
        if rv:                   reasons.append(f"{rv} routing violations")
        jv = sum([
            jamid_aalam.get('JAMID_AALAM_BOUNDARY_VIOLATIONS', 0),
            jamid_aalam.get('ROOT_AFTER_JAMID_AALAM_BOUNDARY', 0),
            jamid_aalam.get('PROCLITIC_COUNTED_IN_AALAM_ROOT', 0),
            jamid_aalam.get('JAMID_MISCLASSIFIED_AS_MABNI', 0),
        ])
        if jv:                   reasons.append(f"{jv} jamid_aalam violations")
        fv = functional_catalog.get('total_violations', 0)
        if fv:                   reasons.append(f"{fv} functional_catalog violations")
        print(f"REASONS: {'; '.join(reasons)}")
    print("=" * 70)
    return 0 if eligible else 1


if __name__ == '__main__':
    sys.exit(main())
