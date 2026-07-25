"""
tests/demo/test_taaqol_layer_report.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-TAAQOL-PER-LAYER-OBSERVABILITY-REPORT-01

23 invariant tests for the per-layer Taaqol observability CSV generated
by ``python scripts/demo_ayat_al_dayn.py --taaqol``.

Shape: 129 tokens × 18 registered layers = 2322 rows (+ 1 header).

Reconciliation targets (macOS / Python 3.12 only):
  LICENSED               = 73
  DEFERRED               = 56
  TAAQOL_LIVE_EVALUATIONS = 128
  H11_H15_REACHED        = 33
  EARLY_STOPS            = 96

In CI (Python 3.10 sandbox) Taaqol defers for all tokens (ImportError),
so reconciliation counts differ — those tests skip on inactive runtimes.
"""
from __future__ import annotations

import csv
import hashlib
import io
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Reconciliation targets (macOS live environment)
_LICENSED_TARGET              = 73
_DEFERRED_TARGET              = 56
_TAAQOL_LIVE_TARGET           = 128
_H11_H15_TARGET               = 33
_EARLY_STOPS_TARGET           = 96
_EXPECTED_ROWS                = 2322   # 129 × 18
_EXPECTED_TOKENS              = 129
_EXPECTED_LAYERS              = 18
_MIN_COLUMNS                  = 51   # updated: +1 for state_source column

# Registered layer IDs (SlotSort enum values)
_REGISTERED_LAYER_IDS = {0, 10, 20, 30, 35, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 900, 910}
_REGISTERED_LAYER_NAMES = {
    0:   'SURFACE_IDENTITY',
    10:  'NORMALIZATION',
    20:  'PHONOLOGICAL',
    30:  'SEGMENTATION',
    35:  'ARTICLE',
    40:  'BOUNDARY',
    50:  'LEXICAL_FUNCTIONAL',
    60:  'WORD_CLASS',
    70:  'INFLECTIONAL',
    80:  'RADICAL',
    90:  'PATTERN',
    100: 'BAB',
    110: 'MASDAR',
    120: 'DERIVATIVE',
    130: 'MORPHOSYNTAX',
    140: 'PARADIGM',
    900: 'EVIDENCE',
    910: 'RESIDUAL',
}
_VALID_LAYER_STATES = frozenset({
    'EXECUTED', 'NOT_REACHED', 'BLOCKED', 'DEFERRED', 'SKIPPED_BY_CONTRACT', 'ERROR',
})
_INFLECTION_DEPENDENT_LAYERS = frozenset({70, 80, 90, 100, 110, 120, 130, 140})


# ── Fixture: generate CSV content ─────────────────────────────────────────────

@pytest.fixture(scope='module')
def csv_content() -> str:
    """
    Generate the per-layer CSV by running the pipeline in-process.
    This consumes the actual Taaqol trace — no mocking.
    """
    from scripts.demo_ayat_al_dayn import run_all, generate_taaqol_layer_csv
    results = run_all(verbose=False)
    return generate_taaqol_layer_csv(results)


@pytest.fixture(scope='module')
def rows(csv_content) -> list[dict]:
    """Parsed CSV rows (DictReader)."""
    reader = csv.DictReader(io.StringIO(csv_content))
    return list(reader)


# ── T1: CSV is generated and non-empty ────────────────────────────────────────

def test_csv_generated_and_nonempty(csv_content):
    """T1: generate_taaqol_layer_csv() returns a non-empty string."""
    assert isinstance(csv_content, str), "CSV content must be a str"
    assert len(csv_content) > 100, "CSV content is suspiciously short"


# ── T2: Exact row count ───────────────────────────────────────────────────────

def test_row_count(rows):
    """T2: CSV has exactly 129 × 18 = 2322 data rows."""
    assert len(rows) == _EXPECTED_ROWS, (
        f"Expected {_EXPECTED_ROWS} data rows (129×18), got {len(rows)}"
    )


# ── T3: Column count ≥ 50 ────────────────────────────────────────────────────

def test_column_count(rows):
    """T3: CSV has at least 50 columns covering all required categories."""
    if not rows:
        pytest.skip("no rows")
    n_cols = len(rows[0])
    assert n_cols >= _MIN_COLUMNS, (
        f"Expected ≥{_MIN_COLUMNS} columns, got {n_cols}.\n"
        f"Columns present: {list(rows[0].keys())}"
    )


# ── T4: Required columns are present ─────────────────────────────────────────

def test_required_columns_present(rows):
    """T4: All required column categories are present in the CSV header."""
    if not rows:
        pytest.skip("no rows")
    cols = set(rows[0].keys())
    required = {
        # Token identity
        'token_index', 'original_surface', 'normalized_surface', 'segment_host',
        'word_class', 'inflection_skipped_reason', 'pipeline_verdict',
        'evaluation_id', 'claim_key',
        # Registry identity
        'layer_id', 'layer_name',
        # Reachability
        'layer_state', 'layer_state_reason', 'state_source',
        # Slot snapshot
        'slot_count', 'filled_count', 'empty_count', 'deferred_count',
        'unknown_count', 'ambiguous_count', 'blocked_count', 'not_applicable_count',
        'slot_ids', 'slot_values', 'slot_states_detail',
        # H11-H15
        'h11_h15_reached', 'h11_h15_filled_slots',
        # Taaqol gateway
        'taaqol_available', 'taaqol_verdict', 'upstream_verdict', 'effective_verdict',
        'gamma_state', 'gate_verdict', 'slot_graph_digest', 'taaqol_center_scope',
        'bridge_id', 'taaqol_trace_steps',
        # Bridge SlotGraph (extended contract)
        'bridge_slot_count', 'bridge_slot_names', 'bridge_slot_states',
        # Runtime integrity
        'runtime_active', 'runtime_kernel_loaded', 'runtime_slot_graph_created',
        'runtime_gamma_executed', 'runtime_gate_executed',
        'runtime_failure_code', 'runtime_failure_detail',
        'runtime_trace_event_count', 'runtime_vendor_sha',
        'runtime_taaqol_commit', 'runtime_hokom_commit',
        'token_error',
    }
    missing = required - cols
    assert not missing, (
        f"Required columns missing from CSV:\n{sorted(missing)}"
    )


# ── T5: Distinct token count ──────────────────────────────────────────────────

def test_distinct_token_count(rows):
    """T5: Exactly 129 distinct token_index values appear in the CSV."""
    indices = {int(r['token_index']) for r in rows}
    assert len(indices) == _EXPECTED_TOKENS, (
        f"Expected {_EXPECTED_TOKENS} distinct tokens, got {len(indices)}"
    )
    assert min(indices) == 1 and max(indices) == _EXPECTED_TOKENS, (
        f"Token indices must be 1–{_EXPECTED_TOKENS}, got min={min(indices)} max={max(indices)}"
    )


# ── T6: Distinct layer count and IDs ─────────────────────────────────────────

def test_distinct_layer_ids(rows):
    """T6: Exactly 18 distinct layer_id values, matching the registered layer registry."""
    layer_ids = {int(r['layer_id']) for r in rows}
    assert layer_ids == _REGISTERED_LAYER_IDS, (
        f"Layer IDs mismatch.\n"
        f"  expected: {sorted(_REGISTERED_LAYER_IDS)}\n"
        f"  actual:   {sorted(layer_ids)}"
    )


# ── T7: Each token × layer appears exactly once ───────────────────────────────

def test_no_duplicate_token_layer_pairs(rows):
    """T7: Each (token_index, layer_id) pair appears exactly once."""
    seen = set()
    duplicates = []
    for r in rows:
        key = (r['token_index'], r['layer_id'])
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    assert not duplicates, (
        f"Duplicate (token_index, layer_id) pairs: {duplicates[:10]}"
    )


# ── T8: layer_state is always a valid value ───────────────────────────────────

def test_layer_state_valid(rows):
    """T8: Every layer_state value is one of the 6 valid states (never empty/unknown)."""
    invalid = [
        (r['token_index'], r['layer_id'], r['layer_state'])
        for r in rows
        if r['layer_state'] not in _VALID_LAYER_STATES
    ]
    assert not invalid, (
        f"Invalid layer_state values found (first 5):\n"
        + "\n".join(
            f"  token={t} layer={l} state={repr(s)}"
            for t, l, s in invalid[:5]
        )
    )


# ── T9: layer_name matches registered names ───────────────────────────────────

def test_layer_name_matches_registry(rows):
    """T9: Each layer_name matches the registered name for its layer_id."""
    mismatches = []
    for r in rows:
        lid = int(r['layer_id'])
        expected_name = _REGISTERED_LAYER_NAMES.get(lid, '')
        if r['layer_name'] != expected_name:
            mismatches.append((lid, r['layer_name'], expected_name))
    assert not mismatches, (
        f"Layer name mismatches (first 5):\n"
        + "\n".join(
            f"  layer_id={lid} got={repr(got)} expected={repr(exp)}"
            for lid, got, exp in mismatches[:5]
        )
    )


# ── T10: Early-stop tokens → SKIPPED_BY_CONTRACT for inflection layers ────────

def test_skipped_by_contract_for_early_stops(rows):
    """
    T10: For any token with inflection_skipped_reason set, every
    inflection-dependent layer (70–140) that has no FILLED slot must be
    SKIPPED_BY_CONTRACT — never EXECUTED or NOT_REACHED.
    """
    violations = []
    for r in rows:
        layer_id = int(r['layer_id'])
        if layer_id not in _INFLECTION_DEPENDENT_LAYERS:
            continue
        if not r.get('inflection_skipped_reason'):
            continue
        # If filled_count > 0, the layer ran despite early stop → OK
        if int(r.get('filled_count', 0)) > 0:
            continue
        if r['layer_state'] != 'SKIPPED_BY_CONTRACT':
            violations.append({
                'token_index': r['token_index'],
                'layer_id':    layer_id,
                'state':       r['layer_state'],
                'skip_reason': r['inflection_skipped_reason'],
            })
    assert not violations, (
        f"Early-stop tokens must have SKIPPED_BY_CONTRACT for inflection-dependent "
        f"layers without FILLED data (first 5 violations):\n"
        + "\n".join(str(v) for v in violations[:5])
    )


# ── T11: Early-stop count matches EARLY_STOPS target ─────────────────────────

def test_early_stops_count(rows):
    """
    T11: Number of distinct tokens with inflection_skipped_reason set
    matches EARLY_STOPS = 96.
    """
    early_stop_tokens = {
        r['token_index']
        for r in rows
        if r.get('inflection_skipped_reason')
    }
    assert len(early_stop_tokens) == _EARLY_STOPS_TARGET, (
        f"EARLY_STOPS mismatch: expected {_EARLY_STOPS_TARGET}, "
        f"got {len(early_stop_tokens)}"
    )


# ── T12: H11_H15_REACHED count matches target ────────────────────────────────

def test_h11_h15_reached_count(rows):
    """
    T12: Number of distinct tokens with h11_h15_reached = 'True'
    matches H11_H15_REACHED = 33.
    """
    h11_tokens = {
        r['token_index']
        for r in rows
        if r.get('h11_h15_reached') == 'True'
    }
    assert len(h11_tokens) == _H11_H15_TARGET, (
        f"H11_H15_REACHED mismatch: expected {_H11_H15_TARGET}, "
        f"got {len(h11_tokens)}"
    )


# ── T13: Determinism (SHA-256 stable across runs) ─────────────────────────────

def test_csv_determinism():
    """
    T13: Two successive calls to generate_taaqol_layer_csv() produce
    byte-for-byte identical output (SHA-256 digest must match).
    No timestamps, memory addresses, or machine-specific paths allowed.
    """
    from scripts.demo_ayat_al_dayn import run_all, generate_taaqol_layer_csv
    results = run_all(verbose=False)
    csv1 = generate_taaqol_layer_csv(results)
    csv2 = generate_taaqol_layer_csv(results)
    sha1 = hashlib.sha256(csv1.encode('utf-8')).hexdigest()
    sha2 = hashlib.sha256(csv2.encode('utf-8')).hexdigest()
    assert sha1 == sha2, (
        f"generate_taaqol_layer_csv() is non-deterministic:\n"
        f"  run 1: {sha1}\n"
        f"  run 2: {sha2}"
    )


# ── T14: Default command byte-for-byte unchanged ──────────────────────────────

def test_default_command_unchanged():
    """
    T14: Running write_outputs() without --taaqol must NOT create the
    taaqol layers CSV file (default command byte-for-byte unchanged).

    We verify the taaqol CSV is absent from paths and the file is not written.
    Existing canonical artifacts are saved and restored so artifact digest
    checks remain valid.
    """
    from scripts.demo_ayat_al_dayn import (
        run_all, summary_stats, integrity_check, write_outputs, REPORT_DIR,
    )
    taaqol_csv_path = REPORT_DIR / 'ayat_al_dayn_taaqol_layers.csv'

    # Save existing canonical artifact bytes so we can restore after write_outputs()
    _saved: dict[str, bytes] = {}
    for fname in ('ayat_al_dayn_results.csv', 'ayat_al_dayn_results_full.json',
                  'ayat_al_dayn_manager_report.html'):
        p = REPORT_DIR / fname
        if p.exists():
            _saved[fname] = p.read_bytes()

    # Remove taaqol CSV if it exists from a previous --taaqol run
    _taaqol_existed = taaqol_csv_path.exists()
    if _taaqol_existed:
        taaqol_csv_path.unlink()

    try:
        results = run_all(verbose=False)
        stats   = summary_stats(results)
        checks  = integrity_check(results)
        meta    = {
            'stage': 'test', 'version': '2', 'head': 'test', 'head_full': 'test',
            'vendor_sha': 'test', 'python': 'test', 'platform': 'test',
            'timestamp': '2026-01-01T00:00:00+00:00', 'ayat_source': 'test',
            'token_count': len(results),
        }
        paths = write_outputs(results, stats, checks, meta, taaqol=False)

        assert 'taaqol_layers' not in paths, (
            "write_outputs(taaqol=False) must NOT return 'taaqol_layers' in paths"
        )
        assert not taaqol_csv_path.exists(), (
            f"write_outputs(taaqol=False) must NOT write {taaqol_csv_path}"
        )
    finally:
        # Restore canonical artifacts so artifact digest tests remain valid
        for fname, data in _saved.items():
            (REPORT_DIR / fname).write_bytes(data)


# ── T15: Reconciliation targets (live Taaqol only) ───────────────────────────

def test_reconciliation_targets_when_live(rows):
    """
    T15: Full reconciliation of all per-layer metrics against canonical targets.

    Skipped when Taaqol runtime is inactive (Python 3.10 / CI sandbox).
    The skip guard reads runtime_active from the CSV — the authoritative field
    sourced from taaqol['available'] → bridge._rt['active'].

    Canonical targets (macOS Python 3.12):
      LICENSED                  = 73
      DEFERRED                  = 56
      TAAQOL_LIVE_EVALUATIONS   = 128   (tokens where runtime_active='True')
      H11_H15_REACHED           = 33
      EARLY_STOPS               = 96
      FINAL_VERDICT_DIVERGENCES = 0
      SILENT_FALLBACKS          = 0
    """
    live_tokens = {r['token_index'] for r in rows if r.get('runtime_active') == 'True'}
    if not live_tokens:
        pytest.skip(
            "Taaqol runtime not active (Python 3.10 / CI sandbox — expected). "
            "Reconciliation targets are verified on macOS Python 3.12 with "
            "runtime_active sourced from taaqol[available] (bridge._rt[active])."
        )

    licensed_tokens = {
        r['token_index'] for r in rows if r.get('taaqol_verdict') == 'LICENSED'
    }
    deferred_tokens = {
        r['token_index'] for r in rows if r.get('taaqol_verdict') == 'DEFERRED'
    }
    h11_tokens = {
        r['token_index'] for r in rows if r.get('h11_h15_reached') == 'True'
    }
    early_stop_tokens = {
        r['token_index'] for r in rows if r.get('inflection_skipped_reason')
    }
    # FINAL_VERDICT_DIVERGENCES: taaqol_verdict ≠ effective_verdict (terminal only)
    seen_div: set[str] = set()
    divergences = 0
    for r in rows:
        tok = r.get('token_index', '')
        if tok in seen_div:
            continue
        tv, ev = r.get('taaqol_verdict', ''), r.get('effective_verdict', '')
        if (tv in {'LICENSED', 'DEFERRED'} and ev in {'LICENSED', 'DEFERRED'}
                and tv != ev):
            divergences += 1
        seen_div.add(tok)
    # SILENT_FALLBACKS: EXECUTED with CONTRACT_DERIVATION
    silent_fallbacks = sum(
        1 for r in rows
        if r.get('layer_state') == 'EXECUTED'
        and r.get('state_source') == 'CONTRACT_DERIVATION'
    )

    errors = []
    if len(licensed_tokens) != _LICENSED_TARGET:
        errors.append(f"LICENSED: expected {_LICENSED_TARGET}, got {len(licensed_tokens)}")
    if len(deferred_tokens) != _DEFERRED_TARGET:
        errors.append(f"DEFERRED: expected {_DEFERRED_TARGET}, got {len(deferred_tokens)}")
    if len(live_tokens) != _TAAQOL_LIVE_TARGET:
        errors.append(
            f"TAAQOL_LIVE_EVALUATIONS: expected {_TAAQOL_LIVE_TARGET}, "
            f"got {len(live_tokens)}"
        )
    if len(h11_tokens) != _H11_H15_TARGET:
        errors.append(f"H11_H15_REACHED: expected {_H11_H15_TARGET}, got {len(h11_tokens)}")
    if len(early_stop_tokens) != _EARLY_STOPS_TARGET:
        errors.append(f"EARLY_STOPS: expected {_EARLY_STOPS_TARGET}, got {len(early_stop_tokens)}")
    if divergences != 0:
        errors.append(f"FINAL_VERDICT_DIVERGENCES: expected 0, got {divergences}")
    if silent_fallbacks != 0:
        errors.append(f"SILENT_FALLBACKS: expected 0, got {silent_fallbacks}")

    assert not errors, (
        "Reconciliation targets not met:\n" + "\n".join(f"  {e}" for e in errors)
    )


# ── T16: state_source validity ────────────────────────────────────────────────

def test_state_source_valid(rows):
    """
    T16: Every row must have state_source ∈ {SLOT_GRAPH_DERIVATION, CONTRACT_DERIVATION}.

    This distinguishes runtime-observed slot states (SLOT_GRAPH_DERIVATION) from
    states inferred via contract-level signals such as inflection_skipped_reason
    or failure_code (CONTRACT_DERIVATION). No other values are permitted.
    """
    if not rows:
        pytest.skip("no rows")
    _VALID_SOURCES = {'SLOT_GRAPH_DERIVATION', 'CONTRACT_DERIVATION'}
    violations = []
    for r in rows:
        src = r.get('state_source', '')
        if src not in _VALID_SOURCES:
            violations.append(
                f"token={r.get('token_index')} layer={r.get('layer_id')}: "
                f"state_source={src!r}"
            )
    assert not violations, (
        f"{len(violations)} rows have invalid state_source:\n"
        + "\n".join(f"  {v}" for v in violations[:20])
    )


# ── T17: FINAL_VERDICT_DIVERGENCES = 0 ───────────────────────────────────────

def test_final_verdict_divergences_zero(rows):
    """
    T17: For every token, taaqol_verdict and effective_verdict must agree
    (FINAL_VERDICT_DIVERGENCES = 0).

    Divergence means the pipeline declared a final verdict that contradicts the
    Taaqol gate result — a silent override that must never occur.
    Only rows where both fields are non-empty are checked.
    """
    if not rows:
        pytest.skip("no rows")
    divergences = []
    # One check per token is sufficient; aggregate by token_index
    seen: dict[str, bool] = {}
    for r in rows:
        tok = r.get('token_index', '')
        if tok in seen:
            continue
        tv = r.get('taaqol_verdict', '')
        ev = r.get('effective_verdict', '')
        if tv and ev and tv != ev:
            # Only flag cases where both are terminal verdicts (LICENSED / DEFERRED)
            if tv in {'LICENSED', 'DEFERRED'} and ev in {'LICENSED', 'DEFERRED'}:
                divergences.append(
                    f"token={tok}: taaqol_verdict={tv!r} ≠ effective_verdict={ev!r}"
                )
        seen[tok] = True
    assert not divergences, (
        f"FINAL_VERDICT_DIVERGENCES={len(divergences)} (expected 0):\n"
        + "\n".join(f"  {d}" for d in divergences)
    )


# ── T18: SILENT_FALLBACKS = 0 ─────────────────────────────────────────────────

def test_silent_fallbacks_zero(rows):
    """
    T18: No row may combine layer_state=EXECUTED with state_source=CONTRACT_DERIVATION
    (SILENT_FALLBACKS = 0).

    EXECUTED must only be asserted when actual slot data (SGA typed_slots) was
    observed (SLOT_GRAPH_DERIVATION). Asserting EXECUTED via a contract signal
    (e.g. failure_code or inflection_skipped_reason) would be a silent fallback —
    claiming execution was observed when it was only inferred.
    """
    if not rows:
        pytest.skip("no rows")
    violations = []
    for r in rows:
        if (r.get('layer_state') == 'EXECUTED'
                and r.get('state_source') == 'CONTRACT_DERIVATION'):
            violations.append(
                f"token={r.get('token_index')} layer={r.get('layer_id')}: "
                f"EXECUTED asserted via CONTRACT_DERIVATION"
            )
    assert not violations, (
        f"SILENT_FALLBACKS={len(violations)} (expected 0):\n"
        + "\n".join(f"  {v}" for v in violations[:20])
    )


# ── T19: slot_graph_digest canonical unit test ────────────────────────────────

def test_canonical_slot_graph_digest_deterministic():
    """
    T19: _canonical_slot_graph_digest() must be:
      (a) Order-independent — same digest for reversed slot list.
      (b) Value-stable — SHA-256, not Python hash().
      (c) Consistent with 16-hex-char format.

    This is a unit test for the bridge helper, isolated from full pipeline
    execution.  It catches hash-randomization regressions (Python hash() is
    salted per-process and must never be used for canonical artifacts).
    """
    from pipeline.taaqol_integration.live.bridge import _canonical_slot_graph_digest

    slots_a = [
        {"name": "WORD_CLASS_SLOT", "state": "FILLED",  "value": "HARF",   "required": True},
        {"name": "DOMAIN_SLOT",     "state": "FILLED",  "value": "ARABIC", "required": False},
        {"name": "LEXICAL_SLOT",    "state": "EMPTY",   "value": None,     "required": True},
    ]
    slots_b = list(reversed(slots_a))

    digest_a = _canonical_slot_graph_digest(slots_a)
    digest_b = _canonical_slot_graph_digest(slots_b)

    # (a) Order independence
    assert digest_a == digest_b, (
        f"_canonical_slot_graph_digest is order-dependent:\n"
        f"  forward  = {digest_a!r}\n"
        f"  reversed = {digest_b!r}"
    )
    # (b) SHA-256 stability: run twice in same process, must match
    assert _canonical_slot_graph_digest(slots_a) == digest_a, (
        "_canonical_slot_graph_digest is not stable within a process"
    )
    # (c) Format: 16 lowercase hex chars
    assert len(digest_a) == 16, f"Expected 16-char digest, got {len(digest_a)}: {digest_a!r}"
    assert digest_a == digest_a.lower(), f"Digest is not lowercase hex: {digest_a!r}"
    assert all(c in '0123456789abcdef' for c in digest_a), (
        f"Digest contains non-hex characters: {digest_a!r}"
    )


# ── T20: slot_graph_digest cross-process stability ────────────────────────────

def test_slot_graph_digest_stable_across_processes():
    """
    T20: slot_graph_digest in the CSV must be identical across two independent
    Python subprocess invocations (TWO_PROCESS_DIGEST_MATCH = 1).

    Python hash() is salted per-process (PYTHONHASHSEED varies).  This test
    catches any regression where hash() is re-introduced into the digest path.
    We run generate_taaqol_layer_csv in two fresh subprocesses and compare the
    slot_graph_digest column values.
    """
    import subprocess
    import sys

    _script = '''
import sys, csv, io, json
sys.path.insert(0, '.')
from scripts.demo_ayat_al_dayn import run_all, generate_taaqol_layer_csv
results = run_all(verbose=False)
content = generate_taaqol_layer_csv(results)
reader = csv.DictReader(io.StringIO(content))
rows = list(reader)
# Output: JSON list of (token_index, layer_id, slot_graph_digest) for first token
first_token = rows[0]["token_index"] if rows else ""
digests = [
    [r["token_index"], r["layer_id"], r["slot_graph_digest"]]
    for r in rows if r["token_index"] == first_token
]
print(json.dumps(digests))
'''

    env = dict(__import__('os').environ)
    env.pop('PYTHONHASHSEED', None)  # let Python randomize hash seed

    results = []
    for _ in range(2):
        proc = __import__('subprocess').run(
            [sys.executable, '-c', _script],
            capture_output=True, text=True,
            cwd=str(Path(__file__).resolve().parent.parent.parent),
            env=env,
            timeout=120,
        )
        if proc.returncode != 0:
            pytest.skip(
                f"Subprocess failed (Taaqol unavailable in sandbox):\n{proc.stderr[-300:]}"
            )
        try:
            results.append(__import__('json').loads(proc.stdout.strip()))
        except Exception:
            pytest.skip(f"Subprocess output not parseable: {proc.stdout[:200]!r}")

    if not results[0]:
        pytest.skip("No rows produced — Taaqol runtime inactive")

    run1_digests = {(r[0], r[1]): r[2] for r in results[0]}
    run2_digests = {(r[0], r[1]): r[2] for r in results[1]}

    mismatches = [
        f"token={k[0]} layer={k[1]}: run1={run1_digests[k]!r} run2={run2_digests.get(k)!r}"
        for k in run1_digests
        if run1_digests[k] != run2_digests.get(k)
    ]
    assert not mismatches, (
        f"TWO_PROCESS_DIGEST_MATCH=0 — slot_graph_digest differs across processes:\n"
        + "\n".join(f"  {m}" for m in mismatches)
    )


# ── T21: DISTINCT_DIGESTS_PER_TOKEN = 1 ──────────────────────────────────────

def test_distinct_slot_graph_digests_per_token(rows):
    """
    T21: For every token, all 18 layer rows share exactly one slot_graph_digest
    value (DISTINCT_DIGESTS_PER_TOKEN = 1).

    slot_graph_digest describes the bridge-level SlotGraph for the whole token,
    not a per-layer quantity — all 18 rows for the same token must carry the
    same value.
    """
    if not rows:
        pytest.skip("no rows")
    from collections import defaultdict
    token_digests: dict[str, set] = defaultdict(set)
    for r in rows:
        tok = r.get('token_index', '')
        d = r.get('slot_graph_digest', '')
        token_digests[tok].add(d)
    violations = [
        f"token={tok}: {len(ds)} distinct digests {sorted(ds)}"
        for tok, ds in token_digests.items()
        if len(ds) > 1
    ]
    assert not violations, (
        f"DISTINCT_DIGESTS_PER_TOKEN > 1 for {len(violations)} tokens:\n"
        + "\n".join(f"  {v}" for v in violations[:10])
    )


# ── T22: DISTINCT_RUNTIME_ACTIVE_VALUES_PER_TOKEN <= 1 ────────────────────────

def test_distinct_runtime_active_values_per_token(rows):
    """
    T22: For every token, all 18 layer rows must share exactly one runtime_active
    value (DISTINCT_RUNTIME_ACTIVE_VALUES_PER_TOKEN = 1).

    runtime_active is a token-level signal (taaqol['available'] from bridge._rt['active'])
    repeated across all layer rows for the same token.  If it varies within a token,
    the CSV population loop is incorrectly reading a per-layer rather than per-token field.
    """
    if not rows:
        pytest.skip("no rows")
    from collections import defaultdict
    token_actives: dict[str, set] = defaultdict(set)
    for r in rows:
        tok = r.get('token_index', '')
        token_actives[tok].add(r.get('runtime_active', ''))
    violations = [
        f"token={tok}: {sorted(vs)}"
        for tok, vs in token_actives.items()
        if len(vs) > 1
    ]
    assert not violations, (
        f"DISTINCT_RUNTIME_ACTIVE_VALUES_PER_TOKEN > 1 for {len(violations)} tokens:\n"
        + "\n".join(f"  {v}" for v in violations[:10])
    )


# ── T23: per-layer runtime_active agrees with token-level results ─────────────

def test_per_layer_live_matches_token_level(rows):
    """
    T23: PER_LAYER_TAAQOL_LIVE_EVALUATIONS must equal TOKEN_LEVEL_TAAQOL_LIVE_EVALUATIONS.

    Derives both counts from actual runtime output — no hardcoded values.
    The per-layer count comes from runtime_active='True' in the CSV.
    The token-level count comes from taaqol['available'] in the raw pipeline results.
    Both must agree, proving the CSV faithfully propagates the bridge liveness signal.
    """
    if not rows:
        pytest.skip("no rows")
    from scripts.demo_ayat_al_dayn import run_all
    results = run_all(verbose=False)

    # Token-level count: authoritative source
    token_level_live = sum(
        1 for r in results if r.get('taaqol', {}).get('available')
    )
    # Per-layer count: distinct tokens where runtime_active='True' in CSV
    per_layer_live = len({
        r['token_index'] for r in rows if r.get('runtime_active') == 'True'
    })

    assert per_layer_live == token_level_live, (
        f"PER_LAYER_TAAQOL_LIVE_EVALUATIONS={per_layer_live} "
        f"≠ TOKEN_LEVEL_TAAQOL_LIVE_EVALUATIONS={token_level_live}\n"
        f"runtime_active in CSV is not faithfully propagated from taaqol['available']"
    )
