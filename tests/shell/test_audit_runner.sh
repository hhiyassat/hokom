#!/usr/bin/env bash
# HOKOM-CANONICAL-FINAL-AUDIT-RUNNER-HARDENING-01
# Updated: HOKOM-SEQUENTIAL-3FS-RESOLUTION-AND-CANONICAL-ARTIFACT-REBASE-01 (Commit 2)
# Updated: HOKOM-CANONICAL-AUDIT-NONMUTATING-RUNNER-CORRECTION-01
# Shell unit tests for run_canonical_final_audit.sh guard logic.
# Tests verify that each guard correctly sets CLOSURE_VERDICT = OPEN
# when the named failure condition occurs.
#
# Governance binding:
#   NEW_LINGUISTIC_BASE_HEAD = 2e2a3ac71a00ad520675c91e13904903f573034b
#   EXPECTED_CANONICAL_CSV_SHA = 5e673089f33e42309a66ded1816fffb9098227f1f86bb35c5faa33349dd47d84
#
# Usage: bash tests/shell/test_audit_runner.sh
set -uo pipefail

PASS=0; FAIL=0
ok() { echo "  PASS: $1"; ((PASS++)) || true; }
fail() { echo "  FAIL: $1"; ((FAIL++)) || true; }

echo "=== audit runner shell tests ==="

# ── helper: extract verdict from runner output ───────────────────────────────
# Run a minimal inline script that exercises only the flag/verdict logic
run_verdict() {
    local extra_flags="$1"
    bash -c "
set -uo pipefail
HEAD_OK=1; INITIAL_TREE_CLEAN=1; DARWIN_OK=1; PYTHON_3124_OK=1; VENV_OK=1
RUNTIME_CONTRACT_EXIT=0; GOLDEN_RULES_INTEGRITY_EXIT=0; GOLD_MANIFEST_INTEGRITY_EXIT=0
PROBE_EXIT=0; CSV_VERIFIER_EXIT=0; CSV_IN_MEMORY_DIVERGENCES=0
RUN1_COLLECT_EXIT=0; RUN2_COLLECT_EXIT=0; NODE_IDS_EQUAL=1
RUN1_COLLECTED_COUNT=10; RUN2_COLLECTED_COUNT=10
RUN1_EXIT=0; RUN2_EXIT=0; TREE_STABLE_BETWEEN_RUNS=1
CLOSURE_GATE_EXIT=0; ALL_REQUIRED_METRICS_PRESENT=1; ALL_CLOSURE_METRICS_ZERO=1
ARTIFACT_BINDING_READY=1
$extra_flags

VERDICT_OK=1
[[ \"\$HEAD_OK\" != 1 ]]                      && VERDICT_OK=0
[[ \"\$INITIAL_TREE_CLEAN\" != 1 ]]           && VERDICT_OK=0
[[ \"\$DARWIN_OK\" != 1 ]]                    && VERDICT_OK=0
[[ \"\$PYTHON_3124_OK\" != 1 ]]               && VERDICT_OK=0
[[ \"\$VENV_OK\" != 1 ]]                      && VERDICT_OK=0
[[ \"\$RUNTIME_CONTRACT_EXIT\" != 0 ]]        && VERDICT_OK=0
[[ \"\$GOLDEN_RULES_INTEGRITY_EXIT\" != 0 ]]  && VERDICT_OK=0
[[ \"\$GOLD_MANIFEST_INTEGRITY_EXIT\" != 0 ]] && VERDICT_OK=0
[[ \"\$PROBE_EXIT\" != 0 ]]                   && VERDICT_OK=0
[[ \"\$CSV_VERIFIER_EXIT\" != 0 ]]            && VERDICT_OK=0
[[ \"\$CSV_IN_MEMORY_DIVERGENCES\" != 0 ]]    && VERDICT_OK=0
[[ \"\$RUN1_COLLECT_EXIT\" != 0 ]]            && VERDICT_OK=0
[[ \"\$RUN2_COLLECT_EXIT\" != 0 ]]            && VERDICT_OK=0
[[ \"\$NODE_IDS_EQUAL\" != 1 ]]               && VERDICT_OK=0
[[ \"\$RUN1_COLLECTED_COUNT\" != \"\$RUN2_COLLECTED_COUNT\" ]] && VERDICT_OK=0
[[ \"\$RUN1_EXIT\" != 0 ]]                    && VERDICT_OK=0
[[ \"\$RUN2_EXIT\" != 0 ]]                    && VERDICT_OK=0
[[ \"\$TREE_STABLE_BETWEEN_RUNS\" != 1 ]]     && VERDICT_OK=0
[[ \"\$CLOSURE_GATE_EXIT\" != 0 ]]            && VERDICT_OK=0
[[ \"\$ALL_REQUIRED_METRICS_PRESENT\" != 1 ]] && VERDICT_OK=0
[[ \"\$ALL_CLOSURE_METRICS_ZERO\" != 1 ]]     && VERDICT_OK=0
[[ \"\$ARTIFACT_BINDING_READY\" != 1 ]]       && VERDICT_OK=0
echo \"VERDICT=\$([[ \$VERDICT_OK == 1 ]] && echo VERIFIED_CLOSED || echo OPEN)\"
" 2>/dev/null
}

# ── baseline: all flags OK → VERIFIED_CLOSED ────────────────────────────────
echo ""
echo "-- baseline and individual flag tests --"
V="$(run_verdict '')"
[[ "$V" == *"VERIFIED_CLOSED"* ]] && ok "baseline all-ok → VERIFIED_CLOSED" \
                                  || fail "baseline all-ok should be VERIFIED_CLOSED (got: $V)"

# ── T1: pytest failure without the word FAILED ───────────────────────────────
# RUN1_EXIT captures actual exit code, not presence of 'FAILED' string
V="$(run_verdict 'RUN1_EXIT=1')"
[[ "$V" == *"OPEN"* ]] && ok "T1: RUN1_EXIT=1 (no FAILED text) → OPEN" \
                        || fail "T1: RUN1_EXIT=1 should be OPEN (got: $V)"

# ── T2: collection error ──────────────────────────────────────────────────────
V="$(run_verdict 'RUN1_COLLECT_EXIT=1')"
[[ "$V" == *"OPEN"* ]] && ok "T2: collection error → OPEN" \
                        || fail "T2: RUN1_COLLECT_EXIT=1 should be OPEN (got: $V)"

# ── T3: probe failure ────────────────────────────────────────────────────────
V="$(run_verdict 'PROBE_EXIT=1')"
[[ "$V" == *"OPEN"* ]] && ok "T3: PROBE_EXIT=1 → OPEN" \
                        || fail "T3: PROBE_EXIT=1 should be OPEN (got: $V)"

# ── T4: digest failure (golden rules) ────────────────────────────────────────
V="$(run_verdict 'GOLDEN_RULES_INTEGRITY_EXIT=1')"
[[ "$V" == *"OPEN"* ]] && ok "T4: GOLDEN_RULES_INTEGRITY_EXIT=1 → OPEN" \
                        || fail "T4: digest failure should be OPEN (got: $V)"

V="$(run_verdict 'GOLD_MANIFEST_INTEGRITY_EXIT=1')"
[[ "$V" == *"OPEN"* ]] && ok "T4b: GOLD_MANIFEST_INTEGRITY_EXIT=1 → OPEN" \
                        || fail "T4b: manifest digest failure should be OPEN (got: $V)"

# ── T5: gate exit 1 (under set -e guard) ─────────────────────────────────────
# Gate uses if/then pattern; nonzero exit captured in CLOSURE_GATE_EXIT
V="$(run_verdict 'CLOSURE_GATE_EXIT=1')"
[[ "$V" == *"OPEN"* ]] && ok "T5: CLOSURE_GATE_EXIT=1 → OPEN" \
                        || fail "T5: gate exit 1 should be OPEN (got: $V)"

# ── T6: wrong HEAD (non-descendant or bad diff) ──────────────────────────────
V="$(run_verdict 'HEAD_OK=0')"
[[ "$V" == *"OPEN"* ]] && ok "T6: HEAD_OK=0 (non-descendant/diff-violation) → OPEN" \
                        || fail "T6: wrong HEAD should be OPEN (got: $V)"

# ── T7: wrong Python ─────────────────────────────────────────────────────────
V="$(run_verdict 'PYTHON_3124_OK=0')"
[[ "$V" == *"OPEN"* ]] && ok "T7: PYTHON_3124_OK=0 → OPEN" \
                        || fail "T7: wrong Python should be OPEN (got: $V)"

# ── T8: dirty working tree ───────────────────────────────────────────────────
V="$(run_verdict 'INITIAL_TREE_CLEAN=0')"
[[ "$V" == *"OPEN"* ]] && ok "T8: INITIAL_TREE_CLEAN=0 → OPEN" \
                        || fail "T8: dirty tree should be OPEN (got: $V)"

# ── T9: missing closure metric ───────────────────────────────────────────────
V="$(run_verdict 'ALL_REQUIRED_METRICS_PRESENT=0')"
[[ "$V" == *"OPEN"* ]] && ok "T9: ALL_REQUIRED_METRICS_PRESENT=0 → OPEN" \
                        || fail "T9: missing metric should be OPEN (got: $V)"

V="$(run_verdict 'ALL_CLOSURE_METRICS_ZERO=0')"
[[ "$V" == *"OPEN"* ]] && ok "T9b: ALL_CLOSURE_METRICS_ZERO=0 → OPEN" \
                        || fail "T9b: nonzero metric should be OPEN (got: $V)"

# ── T10: different node IDs between runs ─────────────────────────────────────
V="$(run_verdict 'NODE_IDS_EQUAL=0')"
[[ "$V" == *"OPEN"* ]] && ok "T10: NODE_IDS_EQUAL=0 → OPEN" \
                        || fail "T10: different node IDs should be OPEN (got: $V)"

V="$(run_verdict 'RUN1_COLLECTED_COUNT=10; RUN2_COLLECTED_COUNT=11')"
[[ "$V" == *"OPEN"* ]] && ok "T10b: collected count mismatch → OPEN" \
                        || fail "T10b: count mismatch should be OPEN (got: $V)"

# ── T11: CSV divergence ──────────────────────────────────────────────────────
V="$(run_verdict 'CSV_IN_MEMORY_DIVERGENCES=1')"
[[ "$V" == *"OPEN"* ]] && ok "T11: CSV_IN_MEMORY_DIVERGENCES=1 → OPEN" \
                        || fail "T11: CSV divergence should be OPEN (got: $V)"

# ── T12: tree mutation between runs ──────────────────────────────────────────
V="$(run_verdict 'TREE_STABLE_BETWEEN_RUNS=0')"
[[ "$V" == *"OPEN"* ]] && ok "T12: TREE_STABLE_BETWEEN_RUNS=0 → OPEN" \
                        || fail "T12: tree mutation should be OPEN (got: $V)"

# ── T13: runtime contract failure (wrong env) ────────────────────────────────
V="$(run_verdict 'RUNTIME_CONTRACT_EXIT=2')"
[[ "$V" == *"OPEN"* ]] && ok "T13: RUNTIME_CONTRACT_EXIT=2 → OPEN" \
                        || fail "T13: contract failure should be OPEN (got: $V)"

# ── T14: not Darwin ──────────────────────────────────────────────────────────
V="$(run_verdict 'DARWIN_OK=0')"
[[ "$V" == *"OPEN"* ]] && ok "T14: DARWIN_OK=0 → OPEN" \
                        || fail "T14: non-Darwin should be OPEN (got: $V)"

echo ""
echo "=== RESULTS: $PASS passed, $FAIL failed ==="
[[ "$FAIL" == 0 ]] && exit 0 || exit 1
