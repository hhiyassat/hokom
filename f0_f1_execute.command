#!/bin/bash
# F0/F1 AUTONOMOUS EXECUTION SCRIPT — HOKOM × TAAQOL-GPT
# Writes all outputs to /Users/husseinhiyassat/hokom/f0_f1_results/
set -euo pipefail

HOKOM="/Users/husseinhiyassat/hokom"
PY312="$HOKOM/.venv-py312/bin/python3.12"
OUT="$HOKOM/f0_f1_results"
mkdir -p "$OUT"
STAMP=$(date +%Y%m%d_%H%M%S)
LOG="$OUT/f0_f1_run_$STAMP.log"

echo "=== F0/F1 START $(date) ===" | tee "$LOG"

cd "$HOKOM"

# ── F0-0: Python version ──────────────────────────────────────────────
echo "--- F0-0: Python version ---" | tee -a "$LOG"
"$PY312" --version 2>&1 | tee -a "$LOG"
echo "PY312_VERSION=$("$PY312" --version 2>&1)" > "$OUT/f0_meta.txt"

# ── F0-1: Vendor import path ─────────────────────────────────────────
echo "--- F0-1: Vendor import path ---" | tee -a "$LOG"
IMPORT_PATH=$("$PY312" -c "
import inspect, taaqqul_slot_geometry
print(inspect.getfile(taaqqul_slot_geometry))
" 2>&1)
echo "IMPORT_PATH=$IMPORT_PATH" | tee -a "$LOG"
echo "IMPORT_PATH=$IMPORT_PATH" >> "$OUT/f0_meta.txt"

EXPECTED_IMPORT="$HOKOM/vendor/Taaqol-GPT"
if echo "$IMPORT_PATH" | grep -q "$EXPECTED_IMPORT"; then
    echo "VENDOR_IMPORT_CHECK=PASS" | tee -a "$LOG"
    echo "VENDOR_IMPORT_CHECK=PASS" >> "$OUT/f0_meta.txt"
else
    echo "VENDOR_IMPORT_CHECK=FAIL — expected $EXPECTED_IMPORT" | tee -a "$LOG"
    echo "VENDOR_IMPORT_CHECK=FAIL" >> "$OUT/f0_meta.txt"
fi

# ── F0-2: Collection pass 1 ──────────────────────────────────────────
echo "--- F0-2: Collection pass 1 ---" | tee -a "$LOG"
"$PY312" -m pytest \
    --collect-only \
    test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    -q 2>&1 | tee "$OUT/collect_pass1.txt" | tail -5 | tee -a "$LOG"

# ── F0-3: Collection pass 2 ──────────────────────────────────────────
echo "--- F0-3: Collection pass 2 ---" | tee -a "$LOG"
"$PY312" -m pytest \
    --collect-only \
    test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    -q 2>&1 | tee "$OUT/collect_pass2.txt" | tail -5 | tee -a "$LOG"

# Node-ID diff
echo "--- F0-4: Node-ID diff ---" | tee -a "$LOG"
diff <(grep "^tests/" "$OUT/collect_pass1.txt" | sort) \
     <(grep "^tests/" "$OUT/collect_pass2.txt" | sort) \
     > "$OUT/collect_diff.txt" 2>&1 && echo "COLLECT_DIFF=0" | tee -a "$LOG" || \
     echo "COLLECT_DIFF_NONZERO — see collect_diff.txt" | tee -a "$LOG"

PY312_COLLECTED=$(grep -c "::" "$OUT/collect_pass1.txt" 2>/dev/null || echo "0")
echo "PY312_COLLECTED=$PY312_COLLECTED" | tee -a "$LOG"
echo "PY312_COLLECTED=$PY312_COLLECTED" >> "$OUT/f0_meta.txt"

# ── F0-5: Run REQUIRES_312 tests (all skipped tests) ─────────────────
echo "--- F0-5: Full test run on Python 3.12 ---" | tee -a "$LOG"
"$PY312" -m pytest \
    test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    -q \
    --tb=short \
    2>&1 | tee "$OUT/f0_full_run.txt" | tail -20 | tee -a "$LOG"

# Parse counts
SUMMARY_LINE=$(tail -5 "$OUT/f0_full_run.txt" | grep -E "passed|failed|error" | tail -1)
echo "SUMMARY=$SUMMARY_LINE" | tee -a "$LOG"
echo "SUMMARY=$SUMMARY_LINE" >> "$OUT/f0_meta.txt"

PY312_PASSED=$(echo "$SUMMARY_LINE" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' || echo "0")
PY312_FAILED=$(echo "$SUMMARY_LINE" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' || echo "0")
PY312_SKIPPED=$(echo "$SUMMARY_LINE" | grep -oE '[0-9]+ skipped' | grep -oE '[0-9]+' || echo "0")
PY312_XFAILED=$(echo "$SUMMARY_LINE" | grep -oE '[0-9]+ xfailed' | grep -oE '[0-9]+' || echo "0")
PY312_ERROR=$(echo "$SUMMARY_LINE" | grep -oE '[0-9]+ error' | grep -oE '[0-9]+' || echo "0")

echo "PY312_PASSED=$PY312_PASSED" | tee -a "$LOG"
echo "PY312_FAILED=$PY312_FAILED" | tee -a "$LOG"
echo "PY312_SKIPPED=$PY312_SKIPPED" | tee -a "$LOG"
echo "PY312_XFAILED=$PY312_XFAILED" | tee -a "$LOG"
echo "PY312_INTERNAL_EXCEPTIONS=$PY312_ERROR" | tee -a "$LOG"
{
echo "PY312_PASSED=$PY312_PASSED"
echo "PY312_FAILED=$PY312_FAILED"
echo "PY312_SKIPPED=$PY312_SKIPPED"
echo "PY312_XFAILED=$PY312_XFAILED"
echo "PY312_INTERNAL_EXCEPTIONS=$PY312_ERROR"
} >> "$OUT/f0_meta.txt"

# ── F1-1: Canonical run 1 ────────────────────────────────────────────
echo "--- F1-1: Canonical run 1 ---" | tee -a "$LOG"
"$PY312" -m pytest \
    test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    -q \
    --tb=short \
    -W error::DeprecationWarning \
    -W error::pytest.PytestRemovedIn10Warning \
    2>&1 | tee "$OUT/f1_canonical_run1.txt" | tail -20 | tee -a "$LOG"
F1_RUN1_EXIT=${PIPESTATUS[0]}
echo "F1_RUN1_EXIT=$F1_RUN1_EXIT" | tee -a "$LOG"
echo "CANONICAL_RUN1_EXIT=$F1_RUN1_EXIT" >> "$OUT/f0_meta.txt"

# ── F1-2: Canonical run 2 ────────────────────────────────────────────
echo "--- F1-2: Canonical run 2 ---" | tee -a "$LOG"
"$PY312" -m pytest \
    test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    -q \
    --tb=short \
    -W error::DeprecationWarning \
    -W error::pytest.PytestRemovedIn10Warning \
    2>&1 | tee "$OUT/f1_canonical_run2.txt" | tail -20 | tee -a "$LOG"
F1_RUN2_EXIT=${PIPESTATUS[0]}
echo "F1_RUN2_EXIT=$F1_RUN2_EXIT" | tee -a "$LOG"
echo "CANONICAL_RUN2_EXIT=$F1_RUN2_EXIT" >> "$OUT/f0_meta.txt"

# Compare runs
RUN1_SUMMARY=$(tail -5 "$OUT/f1_canonical_run1.txt" | grep -E "passed|failed" | tail -1)
RUN2_SUMMARY=$(tail -5 "$OUT/f1_canonical_run2.txt" | grep -E "passed|failed" | tail -1)
if [ "$RUN1_SUMMARY" = "$RUN2_SUMMARY" ]; then
    echo "CANONICAL_COUNTS_IDENTICAL=1" | tee -a "$LOG"
    echo "CANONICAL_COUNTS_IDENTICAL=1" >> "$OUT/f0_meta.txt"
else
    echo "CANONICAL_COUNTS_IDENTICAL=0 (run1: $RUN1_SUMMARY | run2: $RUN2_SUMMARY)" | tee -a "$LOG"
    echo "CANONICAL_COUNTS_IDENTICAL=0" >> "$OUT/f0_meta.txt"
fi

# ── F1-3: Project-owned warnings check ───────────────────────────────
echo "--- F1-3: Warnings check ---" | tee -a "$LOG"
WARN_COUNT=$(grep -cE "W (DeprecationWarning|PytestRemovedIn10Warning)" "$OUT/f1_canonical_run1.txt" 2>/dev/null || echo "0")
echo "PROJECT_OWNED_WARNINGS=$WARN_COUNT" | tee -a "$LOG"
echo "PROJECT_OWNED_WARNINGS=$WARN_COUNT" >> "$OUT/f0_meta.txt"

# ── F1-4: git diff check ─────────────────────────────────────────────
echo "--- F1-4: git diff check ---" | tee -a "$LOG"
git diff --check HEAD 2>&1 | tee "$OUT/git_diff_check.txt" | head -5 | tee -a "$LOG"
GIT_DIFF_EXIT=${PIPESTATUS[0]}
echo "GIT_DIFF_CHECK_EXIT=$GIT_DIFF_EXIT" | tee -a "$LOG"
echo "GIT_DIFF_CHECK_EXIT=$GIT_DIFF_EXIT" >> "$OUT/f0_meta.txt"

# Vendor patch check
VENDOR_PATCHES=$(git diff HEAD -- vendor/Taaqol-GPT/src/ 2>/dev/null | wc -l | tr -d ' ')
echo "VENDOR_PATCH_COUNT=$VENDOR_PATCHES" | tee -a "$LOG"
echo "VENDOR_PATCH_COUNT=$VENDOR_PATCHES" >> "$OUT/f0_meta.txt"

echo "=== F0/F1 COMPLETE $(date) ===" | tee -a "$LOG"
echo "Results in: $OUT" | tee -a "$LOG"
echo ""
echo "KEY RESULTS:"
cat "$OUT/f0_meta.txt" | tee -a "$LOG"
