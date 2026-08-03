#!/usr/bin/env bash
# ============================================================
# c9_taaqol_ready_adapter_wiring.command
# ============================================================
# c9 TARGETED GATE — LICENSING + READY DOWNSTREAM CHAIN.
#
# Strict closure discipline:
#   * uses an ISOLATED output directory
#     (reports/taaqol_full_integration/c9_runtime_output/);
#   * never writes into reports/ayat_al_dayn_demo/;
#   * runs targeted adapter tests → mutation tests → ledger test
#     → native-chain verification → canonical-artifact diff check
#     → F0 twice → canonical suite;
#   * exits 0 only when every required gate passes.
#
# Prohibitions (mandate):
#   NO COMMIT / NO TAG / NO PUSH / NO MERGE
#   NO VENDOR PATCH / NO FROZEN FILE CHANGE
#   NO MANIFEST HASH UPDATE / NO CANONICAL ARTIFACT MUTATION
# ============================================================
set -u -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

PY="$REPO_ROOT/.venv-py312/bin/python"
REPORT_DIR="$REPO_ROOT/reports/taaqol_full_integration"
C9_OUT="$REPORT_DIR/c9_runtime_output"
CANONICAL_DIR="$REPO_ROOT/reports/ayat_al_dayn_demo"
CANONICAL_TRACKED=(
    "reports/ayat_al_dayn_demo/ayat_al_dayn_manager_report.html"
    "reports/ayat_al_dayn_demo/ayat_al_dayn_results.csv"
    "reports/ayat_al_dayn_demo/ayat_al_dayn_results_full.json"
)

mkdir -p "$REPORT_DIR" "$C9_OUT"

TS="$(date +%Y%m%d_%H%M%S)"
LOG="$REPORT_DIR/c9_run_${TS}.log"
STATUS_FILE="$REPORT_DIR/c9_status.txt"
SUMMARY_JSON="$REPORT_DIR/c9_summary.json"

exec > >(tee -a "$LOG") 2>&1

section() { printf '\n============================================================\n%s\n============================================================\n' "$*"; }

if [[ ! -x "$PY" ]]; then
    echo "FATAL: $PY not found — expected .venv-py312 alongside repo root."
    echo "STATUS=FATAL_MISSING_VENV" > "$STATUS_FILE"
    exit 2
fi

TARGETED_COLLECTED=0
TARGETED_PASSED=0
TARGETED_FAILED=0
TARGETED_WARNINGS=0
F0_GATE=FAIL
F1_RUN1_PASSED=0; F1_RUN1_FAILED=0; F1_RUN1_SKIPPED=0; F1_RUN1_WARNINGS=0
F1_RUN2_PASSED=0; F1_RUN2_FAILED=0; F1_RUN2_SKIPPED=0; F1_RUN2_WARNINGS=0
F1_GATE=FAIL
C9_EXIT=1
CANONICAL_ARTIFACT_DIFF_EXIT=1
CANONICAL_UNTRACKED_COUNT=0

fail() { echo "STATUS=$1" > "$STATUS_FILE"; C9_EXIT=${2:-1}; }

# ── 1. Targeted adapter + wiring tests ──────────────────────────────────────
section "1. TARGETED ADAPTER + WIRING TESTS"
TARG_LOG="$REPORT_DIR/c9_targeted_${TS}.log"
"$PY" -m pytest \
    tests/e4c_licensing_boundary/test_licensing_boundary_e4c.py \
    tests/taaqol_integration/test_full_target_orchestrator.py \
    tests/taaqol_integration/test_licensing_wiring_c9.py \
    -q --tb=short 2>&1 | tee "$TARG_LOG"
TARG_STATUS=${PIPESTATUS[0]}
if [[ $TARG_STATUS -ne 0 ]]; then
    fail TARGETED_FAILED $TARG_STATUS
    exit $C9_EXIT
fi
TARGETED_COLLECTED=$(grep -Eo '[0-9]+ passed' "$TARG_LOG" | head -1 | awk '{print $1}')
TARGETED_PASSED=$TARGETED_COLLECTED
TARGETED_FAILED=0
TARGETED_WARNINGS=$(grep -Eo '[0-9]+ warning' "$TARG_LOG" | head -1 | awk '{print $1}')
TARGETED_WARNINGS=${TARGETED_WARNINGS:-0}

# ── 2. Previously failing regression trio ────────────────────────────────────
section "2. REGRESSION TESTS (ledger + mutation + digest)"
"$PY" -m pytest \
    tests/test_execution_ledger/test_ledger.py::test_constitutional_violation_raises \
    tests/demo/test_taaqol_layer_report.py::test_write_outputs_no_canonical_mutation \
    tests/governance/test_artifact_commit_binding.py::test_artifact_digests_match \
    -q --tb=short
REG_STATUS=$?
if [[ $REG_STATUS -ne 0 ]]; then
    fail REGRESSION_FAILED $REG_STATUS
    exit $C9_EXIT
fi

# ── 3. Isolated demo regeneration (json + arabic html) ──────────────────────
section "3. DEMO REGENERATION → $C9_OUT"
"$PY" scripts/demo_ayat_al_dayn.py \
    --format json --taaqol --output-dir "$C9_OUT" || {
        fail DEMO_JSON_FAILED $?; exit $C9_EXIT
    }
"$PY" scripts/demo_ayat_al_dayn.py \
    --format html --taaqol --lang ar --output-dir "$C9_OUT" || {
        fail DEMO_HTML_FAILED $?; exit $C9_EXIT
    }

# ── 4. Canonical artifact untouched? ────────────────────────────────────────
section "4. CANONICAL ARTIFACT PRESERVATION CHECK"
git diff --exit-code HEAD -- "${CANONICAL_TRACKED[@]}"
CANONICAL_ARTIFACT_DIFF_EXIT=$?
CANONICAL_UNTRACKED_COUNT=$(git status --porcelain -- "$CANONICAL_DIR" | grep -cE '^\?\?' || true)
if [[ $CANONICAL_ARTIFACT_DIFF_EXIT -ne 0 || $CANONICAL_UNTRACKED_COUNT -ne 0 ]]; then
    echo "FATAL: C9 mutated canonical artifacts or created untracked files under $CANONICAL_DIR"
    git status --porcelain -- "$CANONICAL_DIR"
    fail CANONICAL_MUTATED
    exit $C9_EXIT
fi

# ── 5. Integrity + anti-gold + anti-leap on the isolated JSON ───────────────
section "5. INTEGRITY + ANTI-GOLD + ANTI-LEAP CHECKS"
"$PY" - "$C9_OUT" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]) / 'ayat_al_dayn_taaqol_full.json'
data = json.loads(p.read_text())
records = data['stage_records']
flags = data['integrity_flags']
assert flags['silent_fallbacks'] == 0, flags
assert flags['synthetic_provenance'] == 0, flags
assert flags['gold_leakage'] == 0, flags
assert flags['forbidden_leaps'] == 0, flags
sentinel = 'ayat_al_dayn' + '.' + 'pretty' + '.' + 'txt'
for r in records:
    for f in ('provenance_ids', 'trace_ids', 'evidence_ids'):
        for v in r.get(f, ()):
            assert sentinel not in str(v), f'gold leakage in {r["stage_id"]} {f}: {v}'
lic = data['native_execution']['tokens_reaching_licensing']
core = data['native_execution']['tokens_reaching_core']
assert lic <= core and lic > 0, (lic, core)
print('INTEGRITY_OK')
PY
[[ $? -eq 0 ]] || { fail INTEGRITY_FAILED; exit $C9_EXIT; }

# ── 6. Native-chain verification (37 tokens × 5 native calls) ───────────────
section "6. NATIVE CHAIN VERIFICATION (37 tokens × 5 native calls)"
"$PY" scripts/c9_verify_native_chain.py "$C9_OUT"
NC_STATUS=$?
if [[ $NC_STATUS -ne 0 ]]; then
    fail NATIVE_CHAIN_FAILED $NC_STATUS
    exit $C9_EXIT
fi

# ── 7. F0 collection — twice ────────────────────────────────────────────────
# Determinism check compares the set of collected node IDs, ignoring
# pytest's wall-clock summary line ("N tests collected in X.XXs").
_f0_normalize() {
    local raw="$1" clean="$2"
    grep -Ev '^[0-9]+ tests? collected in .*s$' "$raw" > "$clean"
}
section "7. F0 COLLECTION — RUN 1"
"$PY" -m pytest --collect-only -q > "$REPORT_DIR/c9_f0_run1_${TS}.txt" 2>&1 || true
_f0_normalize "$REPORT_DIR/c9_f0_run1_${TS}.txt" "$REPORT_DIR/c9_f0_run1_${TS}.ids"
tail -3 "$REPORT_DIR/c9_f0_run1_${TS}.txt"

section "8. F0 COLLECTION — RUN 2"
"$PY" -m pytest --collect-only -q > "$REPORT_DIR/c9_f0_run2_${TS}.txt" 2>&1 || true
_f0_normalize "$REPORT_DIR/c9_f0_run2_${TS}.txt" "$REPORT_DIR/c9_f0_run2_${TS}.ids"
tail -3 "$REPORT_DIR/c9_f0_run2_${TS}.txt"

if diff -q "$REPORT_DIR/c9_f0_run1_${TS}.ids" "$REPORT_DIR/c9_f0_run2_${TS}.ids" >/dev/null; then
    F0_GATE=PASS
else
    F0_GATE=FAIL
    echo "WARN: F0 collection non-deterministic (node IDs diverge between runs)."
    diff "$REPORT_DIR/c9_f0_run1_${TS}.ids" "$REPORT_DIR/c9_f0_run2_${TS}.ids" | head -20 || true
fi

# ── 9. F1 canonical suite — twice ───────────────────────────────────────────
run_f1() {
    local run_no=$1
    local out="$REPORT_DIR/c9_f1_run${run_no}_${TS}.log"
    echo ">>> F1 RUN ${run_no}"
    "$PY" -m pytest -q --tb=short 2>&1 | tee "$out"
    return ${PIPESTATUS[0]}
}
section "9. F1 CANONICAL SUITE — RUN 1"
run_f1 1
F1_RUN1_STATUS=$?
F1_LOG1="$REPORT_DIR/c9_f1_run1_${TS}.log"
F1_RUN1_PASSED=$(grep -Eo '[0-9]+ passed' "$F1_LOG1" | head -1 | awk '{print $1}')
F1_RUN1_FAILED=$(grep -Eo '[0-9]+ failed' "$F1_LOG1" | head -1 | awk '{print $1}')
F1_RUN1_SKIPPED=$(grep -Eo '[0-9]+ skipped' "$F1_LOG1" | head -1 | awk '{print $1}')
F1_RUN1_WARNINGS=$(grep -Eo '[0-9]+ warning' "$F1_LOG1" | head -1 | awk '{print $1}')
F1_RUN1_PASSED=${F1_RUN1_PASSED:-0}; F1_RUN1_FAILED=${F1_RUN1_FAILED:-0}
F1_RUN1_SKIPPED=${F1_RUN1_SKIPPED:-0}; F1_RUN1_WARNINGS=${F1_RUN1_WARNINGS:-0}

section "10. F1 CANONICAL SUITE — RUN 2"
run_f1 2
F1_RUN2_STATUS=$?
F1_LOG2="$REPORT_DIR/c9_f1_run2_${TS}.log"
F1_RUN2_PASSED=$(grep -Eo '[0-9]+ passed' "$F1_LOG2" | head -1 | awk '{print $1}')
F1_RUN2_FAILED=$(grep -Eo '[0-9]+ failed' "$F1_LOG2" | head -1 | awk '{print $1}')
F1_RUN2_SKIPPED=$(grep -Eo '[0-9]+ skipped' "$F1_LOG2" | head -1 | awk '{print $1}')
F1_RUN2_WARNINGS=$(grep -Eo '[0-9]+ warning' "$F1_LOG2" | head -1 | awk '{print $1}')
F1_RUN2_PASSED=${F1_RUN2_PASSED:-0}; F1_RUN2_FAILED=${F1_RUN2_FAILED:-0}
F1_RUN2_SKIPPED=${F1_RUN2_SKIPPED:-0}; F1_RUN2_WARNINGS=${F1_RUN2_WARNINGS:-0}

if [[ $F1_RUN1_STATUS -eq 0 && $F1_RUN2_STATUS -eq 0 && $F1_RUN1_FAILED -eq 0 && $F1_RUN2_FAILED -eq 0 ]]; then
    F1_GATE=PASS
else
    F1_GATE=FAIL
fi

# ── 11. Post-run canonical preservation check ───────────────────────────────
section "11. POST-RUN CANONICAL PRESERVATION CHECK"
git diff --exit-code HEAD -- "${CANONICAL_TRACKED[@]}"
CANONICAL_ARTIFACT_DIFF_EXIT=$?
CANONICAL_UNTRACKED_COUNT=$(git status --porcelain -- "$CANONICAL_DIR" | grep -cE '^\?\?' || true)
if [[ $CANONICAL_ARTIFACT_DIFF_EXIT -ne 0 || $CANONICAL_UNTRACKED_COUNT -ne 0 ]]; then
    echo "FATAL: canonical artifacts mutated during C9 (post-run check)"
    git status --porcelain -- "$CANONICAL_DIR"
    fail POST_RUN_CANONICAL_MUTATED
    exit $C9_EXIT
fi

# ── 12. Summary ─────────────────────────────────────────────────────────────
if [[ $F0_GATE == PASS && $F1_GATE == PASS && $CANONICAL_ARTIFACT_DIFF_EXIT -eq 0 && $CANONICAL_UNTRACKED_COUNT -eq 0 ]]; then
    C9_EXIT=0
    echo "STATUS=OK" > "$STATUS_FILE"
else
    C9_EXIT=1
    _fail_reason='GATE_FAILED'
    [[ $F0_GATE != PASS ]] && _fail_reason="${_fail_reason}:F0"
    [[ $F1_GATE != PASS ]] && _fail_reason="${_fail_reason}:F1"
    [[ $CANONICAL_ARTIFACT_DIFF_EXIT -ne 0 ]] && _fail_reason="${_fail_reason}:CANONICAL_DIFF"
    [[ $CANONICAL_UNTRACKED_COUNT -ne 0 ]] && _fail_reason="${_fail_reason}:CANONICAL_UNTRACKED"
    echo "STATUS=$_fail_reason" > "$STATUS_FILE"
fi

"$PY" - <<PY
import json, pathlib
data = json.loads(pathlib.Path('$C9_OUT/ayat_al_dayn_taaqol_full.json').read_text())
records = data['stage_records']
def by_status(sid):
    from collections import Counter
    c = Counter()
    for r in records:
        if r['stage_id'] == sid:
            c[r['execution_status']] += 1
    return dict(c)
summary = {
    'target_taaqol_sha': data.get('target_taaqol_sha'),
    'tokens_reaching_core': data['native_execution']['tokens_reaching_core'],
    'tokens_reaching_licensing': data['native_execution']['tokens_reaching_licensing'],
    'licensing': by_status('STAGE_04B_LICENSING_BOUNDARY'),
    'dal_only': by_status('STAGE_01_DALONLY'),
    'verbal_madlul': by_status('STAGE_02_VERBALMADLUL'),
    'contractable_unit': by_status('STAGE_03_CONTRACTABLEUNIT'),
    'integrity_flags': data['integrity_flags'],
    'targeted_collected': ${TARGETED_COLLECTED},
    'targeted_passed': ${TARGETED_PASSED},
    'targeted_failed': ${TARGETED_FAILED},
    'targeted_warnings': ${TARGETED_WARNINGS},
    'f0_gate': '${F0_GATE}',
    'f1_run1': {
        'passed': ${F1_RUN1_PASSED}, 'failed': ${F1_RUN1_FAILED},
        'skipped': ${F1_RUN1_SKIPPED}, 'warnings': ${F1_RUN1_WARNINGS},
    },
    'f1_run2': {
        'passed': ${F1_RUN2_PASSED}, 'failed': ${F1_RUN2_FAILED},
        'skipped': ${F1_RUN2_SKIPPED}, 'warnings': ${F1_RUN2_WARNINGS},
    },
    'f1_gate': '${F1_GATE}',
    'canonical_artifact_diff_exit': ${CANONICAL_ARTIFACT_DIFF_EXIT},
    'canonical_untracked_count': ${CANONICAL_UNTRACKED_COUNT},
    'c9_output_directory': '${C9_OUT}',
    'c9_exit': ${C9_EXIT},
}
pathlib.Path('${SUMMARY_JSON}').write_text(
    json.dumps(summary, indent=2, ensure_ascii=False)
)
print('WROTE ${SUMMARY_JSON}')
PY

echo "C9_EXIT=${C9_EXIT}"
exit $C9_EXIT
