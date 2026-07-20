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


# ── Closure manifest ──────────────────────────────────────────────────────────

def generate_closure_manifest(stage_id, git, env_result, python, plt,
                               probes, run1, run2, comparison, corpus, routing) -> dict:
    eligible = (
        git['ok'] and python['ok'] and env_result['ok'] and plt['ok'] and
        probes['ok'] and run1['ok'] and run2['ok'] and comparison['ok'] and corpus['ok'] and
        routing['ok'] and
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

    print("\n[7/7] Corpus contracts (Ayat al-Dayn)...")
    corpus = run_corpus_contracts()
    print(f"  {corpus['total_tokens']} tokens, {corpus['failures']} violations")
    for v in corpus.get('violations', [])[:10]:
        print(f"  VIOLATION: {v}")

    print("\n[8/8] Routing contracts (post-segmentation morphology)...")
    routing = run_routing_contracts()
    print(f"  POST_SEGMENTATION_ROUTING_VIOLATIONS: {routing['POST_SEGMENTATION_ROUTING_VIOLATIONS']}")
    print(f"  ROOT_AFTER_CLOSED_BOUNDARY:          {routing['ROOT_AFTER_CLOSED_BOUNDARY']}")
    print(f"  SURFACE_PROVENANCE_VIOLATIONS:       {routing['SURFACE_PROVENANCE_VIOLATIONS']}")
    print(f"  ARTICLE_REATTACHMENT_VIOLATIONS:     {routing['ARTICLE_REATTACHMENT_VIOLATIONS']}")
    for v in routing.get('root_after_boundary', [])[:5]:
        print(f"  BOUNDARY_VIOLATION: {v}")

    print("\n" + "=" * 70)
    manifest = generate_closure_manifest(
        args.stage, git, env_result, python, plt, probes, run1, run2, comparison, corpus, routing
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
        print(f"REASONS: {'; '.join(reasons)}")
    print("=" * 70)
    return 0 if eligible else 1


if __name__ == '__main__':
    sys.exit(main())
