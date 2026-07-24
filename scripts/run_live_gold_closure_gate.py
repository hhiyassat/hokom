#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/run_live_gold_closure_gate.py

HOKOM-LIVE-GOLD-ORACLE-COVERAGE-AND-GATE-HARDENING-02

Live gold closure gate.  Exits nonzero whenever any closure metric is nonzero.

This gate is the DEFINITIVE failure signal for open defects.
It is intentionally SEPARATE from the oracle detector tests:

  oracle detector tests       → PASS  (they verify the detector finds defects)
  run_live_gold_closure_gate  → FAIL  (because those defects exist at current HEAD)

Usage:
  python scripts/run_live_gold_closure_gate.py          # exits 0=clean, 1=defects found
  python scripts/run_live_gold_closure_gate.py --report # print full metric table

The gate must NOT be added to the default pytest suite.
It is invoked explicitly at release time or by a dedicated CI step.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

# ── closure metric definitions ────────────────────────────────────────────────
# Each entry: (key, threshold, description)
# The gate FAILS if metric_value > threshold (threshold is usually 0).
CLOSURE_METRICS: tuple[tuple[str, int, str], ...] = (
    ('LIVE_GOLD_TOKEN_MISMATCHES',           0, 'gold manifest token mismatches'),
    ('LIVE_FORM_FAMILY_MISMATCHES',          0, 'CRA form family mismatches'),
    ('KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS',    0, 'out-of-scope form residuals (FORM_REOPENING=FORBIDDEN)'),
    ('LIVE_PERSON_NUMBER_GENDER_MISMATCHES', 0, 'person/number/gender mismatches'),
    ('LIVE_VOICE_MISMATCHES',                0, 'voice mismatches'),
    ('LIVE_CONTEXT_MOOD_MISMATCHES',         0, 'context mood mismatches'),
    ('LIVE_UNCORRELATED_AMBIGUITY',          0, 'uncorrelated ambiguity representations'),
    ('UNJUSTIFIED_WORD_CLASS_NOT_OPENED',    0, 'unjustified word-class deferral'),
    ('LIVE_NONVERBS_AS_VERBS',               0, 'non-verbs misclassified as FI3L'),
    ('LIVE_JAMID_BOUNDARY_VIOLATIONS',       0, 'JAMID_AALAM_BOUNDARY violations'),
)


def _load_demo():
    script = pathlib.Path(__file__).resolve().parent / 'demo_ayat_al_dayn.py'
    spec = importlib.util.spec_from_file_location('demo_ayat_al_dayn', script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_closure_gate(report: bool = False) -> int:
    """
    Run all closure metrics.  Returns 0 if clean, 1 if any closure metric > threshold.
    """
    mod = _load_demo()
    metrics = mod.compute_live_metrics()

    failures: list[tuple[str, int, int, str]] = []
    for key, threshold, description in CLOSURE_METRICS:
        value = metrics.get(key, 0)
        if value > threshold:
            failures.append((key, value, threshold, description))

    if report or failures:
        print('HOKOM LIVE GOLD CLOSURE GATE')
        print('=' * 60)
        for key, threshold, description in CLOSURE_METRICS:
            value = metrics.get(key, 0)
            status = 'FAIL' if value > threshold else 'PASS'
            mark = '✗' if value > threshold else '✓'
            print(f'  {mark} {status:<4}  {key:<45} = {value}')
        print('=' * 60)

    if failures:
        print(f'\nCLOSURE GATE FAILED — {len(failures)} metric(s) above threshold:')
        for key, value, threshold, description in failures:
            print(f'  {key} = {value} (threshold {threshold}) — {description}')
        print('\nDeclare all defects fixed before closing this HEAD.')
        return 1

    print('\nCLOSURE GATE PASSED — all metrics at threshold.')
    return 0


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run live gold closure gate')
    parser.add_argument('--report', action='store_true',
                        help='Always print full metric table')
    args = parser.parse_args()
    sys.exit(run_closure_gate(report=args.report))
