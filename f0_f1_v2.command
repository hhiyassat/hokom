#!/bin/bash
# F0/F1 AUTONOMOUS EXECUTION SCRIPT v2 — no set -e; continues on collection errors
# Writes all outputs to /Users/husseinhiyassat/hokom/f0_f1_results/

HOKOM="/Users/husseinhiyassat/hokom"
PY312="$HOKOM/.venv-py312/bin/python3.12"
OUT="$HOKOM/f0_f1_results"
mkdir -p "$OUT"
STAMP=$(date +%Y%m%d_%H%M%S)
LOG="$OUT/run_$STAMP.log"

tee_log() { tee -a "$LOG"; }

echo "=== F0/F1 START $(date) ===" | tee_log
echo "" | tee_log

# ── F0-0: Python version ──────────────────────────────────────────────
echo "--- F0-0: Python ---" | tee_log
"$PY312" --version 2>&1 | tee_log
PY_VER=$("$PY312" --version 2>&1)
echo "PY312_VERSION=$PY_VER" >> "$OUT/results.txt"

# ── F0-1: Vendor import path ─────────────────────────────────────────
echo "--- F0-1: Vendor import path ---" | tee_log
IMPORT_PATH=$("$PY312" -c "
import inspect, taaqqul_slot_geometry
print(inspect.getfile(taaqqul_slot_geometry))
" 2>&1)
echo "IMPORT_PATH=$IMPORT_PATH" | tee_log
echo "IMPORT_PATH=$IMPORT_PATH" >> "$OUT/results.txt"

EXPECTED="$HOKOM/vendor/Taaqol-GPT"
if echo "$IMPORT_PATH" | grep -q "$EXPECTED"; then
    echo "VENDOR_IMPORT_CHECK=PASS" | tee_log
    echo "VENDOR_IMPORT_CHECK=PASS" >> "$OUT/results.txt"
else
    echo "VENDOR_IMPORT_CHECK=FAIL" | tee_log
    echo "VENDOR_IMPORT_CHECK=FAIL" >> "$OUT/results.txt"
fi

# ── F0-2: Collection pass 1 (with continue-on-error) ─────────────────
echo "--- F0-2: Collection pass 1 ---" | tee_log
"$PY312" -m pytest \
    --collect-only \
    test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    --continue-on-collection-errors \
    -q 2>&1 | tee "$OUT/collect_pass1.txt" | tail -3 | tee_log

COLLECT1_SUMMARY=$(tail -3 "$OUT/collect_pass1.txt" | grep -E "selected|error|collected")
echo "COLLECT1=$COLLECT1_SUMMARY" >> "$OUT/results.txt"

# Extract collected count
PY312_COLLECTED=$(grep -E "^[0-9]+ tests? collected" "$OUT/collect_pass1.txt" | grep -oE "^[0-9]+" || echo "0")
COLLECT1_ERRORS=$(grep -c "^ERROR" "$OUT/collect_pass1.txt" 2>/dev/null || echo "0")
echo "PY312_COLLECTED=$PY312_COLLECTED" | tee_log
echo "COLLECT1_ERRORS=$COLLECT1_ERRORS" | tee_log
echo "PY312_COLLECTED=$PY312_COLLECTED" >> "$OUT/results.txt"
echo "COLLECT1_ERRORS=$COLLECT1_ERRORS" >> "$OUT/results.txt"

# Save error file names
grep "^ERROR" "$OUT/collect_pass1.txt" > "$OUT/collect_errors.txt" 2>/dev/null || true
echo "Collection errors saved to collect_errors.txt" | tee_log

# ── F0-3: Collection pass 2 ──────────────────────────────────────────
echo "--- F0-3: Collection pass 2 ---" | tee_log
"$PY312" -m pytest \
    --collect-only \
    test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    --continue-on-collection-errors \
    -q 2>&1 | tee "$OUT/collect_pass2.txt" | tail -3 | tee_log

# Node-ID diff
diff <(grep "::" "$OUT/collect_pass1.txt" | sort) \
     <(grep "::" "$OUT/collect_pass2.txt" | sort) \
     > "$OUT/collect_diff.txt" 2>&1
DIFF_LINES=$(wc -l < "$OUT/collect_diff.txt" | tr -d ' ')
echo "COLLECT_DIFF_LINES=$DIFF_LINES" | tee_log
echo "COLLECT_DIFF_LINES=$DIFF_LINES" >> "$OUT/results.txt"

# ── F0-4: Full run on Python 3.12 ────────────────────────────────────
echo "--- F0-4: Full test run (py3.12, --continue-on-collection-errors) ---" | tee_log
"$PY312" -m pytest \
    test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    --continue-on-collection-errors \
    -q \
    --tb=short \
    2>&1 | tee "$OUT/f0_full_run.txt"
FULL_EXIT=${PIPESTATUS[0]}

SUMMARY=$(tail -5 "$OUT/f0_full_run.txt" | grep -E "passed|failed|error" | tail -1)
echo "F0_FULL_SUMMARY=$SUMMARY" | tee_log
echo "F0_FULL_EXIT=$FULL_EXIT" | tee_log
echo "F0_FULL_SUMMARY=$SUMMARY" >> "$OUT/results.txt"
echo "F0_FULL_EXIT=$FULL_EXIT" >> "$OUT/results.txt"

PY312_PASSED=$(echo "$SUMMARY" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' || echo "0")
PY312_FAILED=$(echo "$SUMMARY" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' || echo "0")
PY312_SKIPPED=$(echo "$SUMMARY" | grep -oE '[0-9]+ skipped' | grep -oE '[0-9]+' || echo "0")
PY312_XFAILED=$(echo "$SUMMARY" | grep -oE '[0-9]+ xfailed' | grep -oE '[0-9]+' || echo "0")
PY312_ERROR=$(echo "$SUMMARY" | grep -oE '[0-9]+ error' | grep -oE '[0-9]+' || echo "0")
echo "PY312_PASSED=$PY312_PASSED" | tee_log
echo "PY312_FAILED=$PY312_FAILED" | tee_log
echo "PY312_SKIPPED=$PY312_SKIPPED" | tee_log
echo "PY312_XFAILED=$PY312_XFAILED" | tee_log
echo "PY312_INTERNAL_EXCEPTIONS=$PY312_ERROR" | tee_log
{
echo "PY312_PASSED=$PY312_PASSED"
echo "PY312_FAILED=$PY312_FAILED"
echo "PY312_SKIPPED=$PY312_SKIPPED"
echo "PY312_XFAILED=$PY312_XFAILED"
echo "PY312_INTERNAL_EXCEPTIONS=$PY312_ERROR"
} >> "$OUT/results.txt"

# ── F1-1: Canonical run 1 (warnings as errors) ───────────────────────
echo "--- F1-1: Canonical run 1 (warnings as errors) ---" | tee_log
"$PY312" -m pytest \
    test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    --continue-on-collection-errors \
    -q \
    --tb=short \
    -W error::DeprecationWarning \
    -W error::pytest.PytestRemovedIn10Warning \
    2>&1 | tee "$OUT/f1_run1.txt"
F1_RUN1_EXIT=${PIPESTATUS[0]}
F1_RUN1_SUMMARY=$(tail -5 "$OUT/f1_run1.txt" | grep -E "passed|failed|error" | tail -1)
echo "F1_RUN1_EXIT=$F1_RUN1_EXIT" | tee_log
echo "F1_RUN1_SUMMARY=$F1_RUN1_SUMMARY" | tee_log
echo "CANONICAL_RUN1_EXIT=$F1_RUN1_EXIT" >> "$OUT/results.txt"
echo "CANONICAL_RUN1_SUMMARY=$F1_RUN1_SUMMARY" >> "$OUT/results.txt"

# ── F1-2: Canonical run 2 ────────────────────────────────────────────
echo "--- F1-2: Canonical run 2 (warnings as errors) ---" | tee_log
"$PY312" -m pytest \
    test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    --continue-on-collection-errors \
    -q \
    --tb=short \
    -W error::DeprecationWarning \
    -W error::pytest.PytestRemovedIn10Warning \
    2>&1 | tee "$OUT/f1_run2.txt"
F1_RUN2_EXIT=${PIPESTATUS[0]}
F1_RUN2_SUMMARY=$(tail -5 "$OUT/f1_run2.txt" | grep -E "passed|failed|error" | tail -1)
echo "F1_RUN2_EXIT=$F1_RUN2_EXIT" | tee_log
echo "F1_RUN2_SUMMARY=$F1_RUN2_SUMMARY" | tee_log
echo "CANONICAL_RUN2_EXIT=$F1_RUN2_EXIT" >> "$OUT/results.txt"
echo "CANONICAL_RUN2_SUMMARY=$F1_RUN2_SUMMARY" >> "$OUT/results.txt"

if [ "$F1_RUN1_SUMMARY" = "$F1_RUN2_SUMMARY" ]; then
    echo "CANONICAL_COUNTS_IDENTICAL=1" | tee_log
    echo "CANONICAL_COUNTS_IDENTICAL=1" >> "$OUT/results.txt"
else
    echo "CANONICAL_COUNTS_IDENTICAL=0" | tee_log
    echo "CANONICAL_COUNTS_IDENTICAL=0" >> "$OUT/results.txt"
fi

# ── F1-3: git diff check ─────────────────────────────────────────────
echo "--- F1-3: git diff check ---" | tee_log
cd "$HOKOM"
git diff --check HEAD 2>&1 | tee "$OUT/git_diff.txt" | head -3 | tee_log
GIT_EXIT=${PIPESTATUS[0]}
VENDOR_PATCH=$(git diff HEAD -- vendor/Taaqol-GPT/src/ 2>/dev/null | wc -l | tr -d ' ')
echo "GIT_DIFF_CHECK_EXIT=$GIT_EXIT" | tee_log
echo "VENDOR_PATCH_COUNT=$VENDOR_PATCH" | tee_log
echo "GIT_DIFF_CHECK_EXIT=$GIT_EXIT" >> "$OUT/results.txt"
echo "VENDOR_PATCH_COUNT=$VENDOR_PATCH" >> "$OUT/results.txt"

# ── SUMMARY ──────────────────────────────────────────────────────────
echo "" | tee_log
echo "=== F0/F1 COMPLETE $(date) ===" | tee_log
echo "" | tee_log
echo "=== KEY RESULTS ===" | tee_log
cat "$OUT/results.txt" | tee_log
echo "" | tee_log
echo "Full outputs in: $OUT"
