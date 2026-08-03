#!/bin/bash
# C5-C7 REPAIR VERIFICATION SCRIPT
# Verifies pytest.ini src fix, re-runs pip install, then full C6/C7 gates.
# Per C0-C8 mandate — no global set -e; per-step exit capture.

HOKOM="/Users/husseinhiyassat/hokom"
PY="$HOKOM/.venv-py312/bin/python3.12"
PIP="$HOKOM/.venv-py312/bin/pip"
OUT="$HOKOM/reports/taaqol_full_integration"
STATUS="$OUT/c6_c7_status.txt"
SUMMARY="$OUT/c6_c7_summary.json"
mkdir -p "$OUT"
: > "$STATUS"
STAMP=$(date +%Y%m%d_%H%M%S)
LOG="$OUT/c6_c7_run_$STAMP.log"
exec > >(tee -a "$LOG") 2>&1

echo "=== C5-C7 REPAIR+VERIFY START $(date) ==="

# ── STEP 0: Confirm pytest.ini change is in effect ────────────────────────────
echo ""
echo "=== STEP 0: Confirm pytest.ini ==="
cat "$HOKOM/pytest.ini"
grep -q "src" "$HOKOM/pytest.ini" && echo "PYTEST_INI_SRC_PRESENT=1" || echo "PYTEST_INI_SRC_PRESENT=0"

echo ""
echo "=== STEP 0b: Confirm pyproject.toml setuptools.packages.find ==="
grep -A2 "setuptools.packages.find" "$HOKOM/pyproject.toml" || echo "NOT_FOUND"

# ── STEP 1: Re-run pip install now that setuptools config is correct ───────────
echo ""
echo "=== STEP 1: pip install -e . --no-deps (with src layout config) ==="
cd "$HOKOM"
"$PIP" install -e . --no-deps
PIP_EXIT=$?
printf 'PIP_INSTALL_EXIT=%s\n' "$PIP_EXIT" >> "$STATUS"

echo ""
echo "=== STEP 1b: Verify hokom is importable ==="
"$PY" -c "import inspect, hokom; print('HOKOM_PATH=', inspect.getfile(hokom))"
IMPORT_EXIT=$?
printf 'HOKOM_IMPORT_EXIT=%s\n' "$IMPORT_EXIT" >> "$STATUS"

"$PIP" show hokom 2>/dev/null | grep -E "Name|Location|Editable"

# ── STEP 2: C5 re-run — canonical collection probe ────────────────────────────
echo ""
echo "=== STEP 2 (C5): Canonical collection post-repair ==="
cd "$HOKOM"
"$PY" -m pytest tests/canonical/ --collect-only -q --tb=short \
    > "$OUT/c5_postfix_canonical_collect.txt" 2>&1
C5_EXIT=$?
tail -5 "$OUT/c5_postfix_canonical_collect.txt"
C5_ERRORS=$(grep -c "^ERROR" "$OUT/c5_postfix_canonical_collect.txt" 2>/dev/null || echo "0")
C5_COLLECTED=$(grep -E "^[0-9]+ tests? collected" "$OUT/c5_postfix_canonical_collect.txt" | grep -oE "^[0-9]+" || echo "0")
printf 'C5_POSTFIX_EXIT=%s\n' "$C5_EXIT" >> "$STATUS"
printf 'C5_POSTFIX_ERRORS=%s\n' "$C5_ERRORS" >> "$STATUS"
printf 'C5_POSTFIX_COLLECTED=%s\n' "$C5_COLLECTED" >> "$STATUS"

if [ "$C5_ERRORS" -gt 0 ]; then
    echo ""
    echo "=== C5 STILL HAS ERRORS — listing ==="
    grep "^ERROR" "$OUT/c5_postfix_canonical_collect.txt"
    echo "--- traceback details ---"
    grep -A10 "ImportError\|ModuleNotFoundError\|AttributeError" \
        "$OUT/c5_postfix_canonical_collect.txt" | head -60
    echo ""
    echo "C5_GATE=FAIL — canonical collection errors remain after src fix"
    printf 'C5_GATE=FAIL\n' >> "$STATUS"
    echo ""
    echo "=== ABORT: C6/C7 require C5_GATE=PASS ==="
    printf 'C6_GATE=SKIPPED\n' >> "$STATUS"
    printf 'C7_GATE=SKIPPED\n' >> "$STATUS"
    # write partial summary and exit
    "$PY" - << 'PYEOF'
import json, os
status = {}
status_file = os.environ.get('STATUS_FILE', '')
if not status_file:
    status_file = os.path.expanduser(
        "~/hokom/reports/taaqol_full_integration/c6_c7_status.txt")
with open(status_file) as f:
    for line in f:
        line = line.strip()
        if '=' in line:
            k, _, v = line.partition('=')
            status[k] = v
summary = {
    "document_id": "C5-C7-REPAIR-VERIFY",
    "APPROVED_TARGET_SHA": "05c6668dfb95d9238cff5df1d8bc73d0664bccb3",
    "status": status,
    "C5_GATE": status.get("C5_GATE", "FAIL"),
    "C6_GATE": "SKIPPED",
    "C7_GATE": "SKIPPED",
    "F0_GATE": "FAIL",
    "F1_GATE": "FAIL",
}
out = os.path.expanduser(
    "~/hokom/reports/taaqol_full_integration/c6_c7_summary.json")
with open(out, "w") as f:
    json.dump(summary, f, indent=2)
print(json.dumps(summary, indent=2))
PYEOF
    echo ""
    echo "=== C5-C7 COMPLETE (C5 FAILED) $(date) ==="
    cat "$STATUS"
    exit 1
fi

echo "C5_GATE=PASS — canonical collection: $C5_COLLECTED tests, 0 errors"
printf 'C5_GATE=PASS\n' >> "$STATUS"

# ── STEP 3: C6 — Full collection, twice ──────────────────────────────────────
echo ""
echo "=== STEP 3 (C6): Full collection — Run 1 ==="
cd "$HOKOM"
"$PY" -m pytest test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    --collect-only -q \
    > "$OUT/F0_COLLECT_RUN1.log" 2>&1
C6R1_EXIT=$?
tail -3 "$OUT/F0_COLLECT_RUN1.log"
C6R1_COUNT=$(grep -E "^[0-9]+ tests? collected" "$OUT/F0_COLLECT_RUN1.log" | grep -oE "^[0-9]+" || echo "0")
C6R1_ERRORS=$(grep -c "^ERROR" "$OUT/F0_COLLECT_RUN1.log" 2>/dev/null || echo "0")
printf 'COLLECT_RUN1_EXIT=%s\n' "$C6R1_EXIT" >> "$STATUS"
printf 'COLLECT_RUN1_COUNT=%s\n' "$C6R1_COUNT" >> "$STATUS"
printf 'COLLECT_RUN1_ERRORS=%s\n' "$C6R1_ERRORS" >> "$STATUS"
echo "Run1: exit=$C6R1_EXIT collected=$C6R1_COUNT errors=$C6R1_ERRORS"

echo ""
echo "=== STEP 3 (C6): Full collection — Run 2 ==="
"$PY" -m pytest test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    --collect-only -q \
    > "$OUT/F0_COLLECT_RUN2.log" 2>&1
C6R2_EXIT=$?
tail -3 "$OUT/F0_COLLECT_RUN2.log"
C6R2_COUNT=$(grep -E "^[0-9]+ tests? collected" "$OUT/F0_COLLECT_RUN2.log" | grep -oE "^[0-9]+" || echo "0")
C6R2_ERRORS=$(grep -c "^ERROR" "$OUT/F0_COLLECT_RUN2.log" 2>/dev/null || echo "0")
printf 'COLLECT_RUN2_EXIT=%s\n' "$C6R2_EXIT" >> "$STATUS"
printf 'COLLECT_RUN2_COUNT=%s\n' "$C6R2_COUNT" >> "$STATUS"
printf 'COLLECT_RUN2_ERRORS=%s\n' "$C6R2_ERRORS" >> "$STATUS"
echo "Run2: exit=$C6R2_EXIT collected=$C6R2_COUNT errors=$C6R2_ERRORS"

# Node-ID diff
diff <(grep "::" "$OUT/F0_COLLECT_RUN1.log" | sort) \
     <(grep "::" "$OUT/F0_COLLECT_RUN2.log" | sort) \
     > "$OUT/collect_node_diff.txt" 2>&1
NODE_DIFF=$(wc -l < "$OUT/collect_node_diff.txt" | tr -d ' ')
printf 'NODE_ID_DIFF=%s\n' "$NODE_DIFF" >> "$STATUS"

if [ "$C6R1_EXIT" -eq 0 ] && [ "$C6R2_EXIT" -eq 0 ]; then
    echo ""
    echo "C6_GATE=PASS — Run1=$C6R1_COUNT Run2=$C6R2_COUNT NODE_DIFF=$NODE_DIFF"
    printf 'C6_GATE=PASS\n' >> "$STATUS"
else
    echo ""
    echo "C6_GATE=FAIL — Run1 exit=$C6R1_EXIT errors=$C6R1_ERRORS / Run2 exit=$C6R2_EXIT errors=$C6R2_ERRORS"
    printf 'C6_GATE=FAIL\n' >> "$STATUS"
    # Show remaining errors
    if [ "$C6R1_ERRORS" -gt 0 ]; then
        echo "--- C6 Run1 errors ---"
        grep "^ERROR" "$OUT/F0_COLLECT_RUN1.log"
        grep -A6 "ModuleNotFoundError\|ImportError" "$OUT/F0_COLLECT_RUN1.log" | head -40
    fi
fi

# ── STEP 4: C7 — Full double run (only if C6 clean) ─────────────────────────
echo ""
if [ "$C6R1_EXIT" -eq 0 ] && [ "$C6R2_EXIT" -eq 0 ]; then
    echo "=== STEP 4 (C7): Full test run — Run 1 ==="
    cd "$HOKOM"
    "$PY" -m pytest test_hokom.py tests/ \
        --ignore=tests/compatibility \
        --ignore=tests/external_oracle \
        -q --tb=short \
        -W error::DeprecationWarning \
        -W error::pytest.PytestRemovedIn10Warning \
        > "$OUT/F1_CANONICAL_RUN1.log" 2>&1
    C7R1_EXIT=$?
    C7R1_SUMMARY=$(tail -5 "$OUT/F1_CANONICAL_RUN1.log" | grep -E "passed|failed|error" | tail -1)
    echo "Run1 exit=$C7R1_EXIT summary=$C7R1_SUMMARY"
    printf 'CANONICAL_RUN1_EXIT=%s\n' "$C7R1_EXIT" >> "$STATUS"
    printf 'CANONICAL_RUN1_SUMMARY=%s\n' "$C7R1_SUMMARY" >> "$STATUS"

    # Print any failures
    if [ "$C7R1_EXIT" -ne 0 ]; then
        echo "--- FAILURES (Run1) ---"
        grep -E "^FAILED|^ERROR" "$OUT/F1_CANONICAL_RUN1.log" | head -30
    fi

    echo ""
    echo "=== STEP 4 (C7): Full test run — Run 2 ==="
    "$PY" -m pytest test_hokom.py tests/ \
        --ignore=tests/compatibility \
        --ignore=tests/external_oracle \
        -q --tb=short \
        -W error::DeprecationWarning \
        -W error::pytest.PytestRemovedIn10Warning \
        > "$OUT/F1_CANONICAL_RUN2.log" 2>&1
    C7R2_EXIT=$?
    C7R2_SUMMARY=$(tail -5 "$OUT/F1_CANONICAL_RUN2.log" | grep -E "passed|failed|error" | tail -1)
    echo "Run2 exit=$C7R2_EXIT summary=$C7R2_SUMMARY"
    printf 'CANONICAL_RUN2_EXIT=%s\n' "$C7R2_EXIT" >> "$STATUS"
    printf 'CANONICAL_RUN2_SUMMARY=%s\n' "$C7R2_SUMMARY" >> "$STATUS"

    if [ "$C7R1_SUMMARY" = "$C7R2_SUMMARY" ]; then
        printf 'CANONICAL_COUNTS_IDENTICAL=1\n' >> "$STATUS"
        echo "CANONICAL_COUNTS_IDENTICAL=1"
    else
        printf 'CANONICAL_COUNTS_IDENTICAL=0\n' >> "$STATUS"
        echo "CANONICAL_COUNTS_IDENTICAL=0 (run1: $C7R1_SUMMARY | run2: $C7R2_SUMMARY)"
    fi

    if [ "$C7R1_EXIT" -eq 0 ] && [ "$C7R2_EXIT" -eq 0 ]; then
        printf 'C7_GATE=PASS\n' >> "$STATUS"
    else
        printf 'C7_GATE=FAIL\n' >> "$STATUS"
    fi
else
    echo "=== C7: SKIPPED — C6 collection not clean ==="
    printf 'CANONICAL_RUN1_EXIT=SKIPPED\n' >> "$STATUS"
    printf 'CANONICAL_RUN2_EXIT=SKIPPED\n' >> "$STATUS"
    printf 'CANONICAL_COUNTS_IDENTICAL=SKIPPED\n' >> "$STATUS"
    printf 'C7_GATE=SKIPPED\n' >> "$STATUS"
fi

# ── Git checks ───────────────────────────────────────────────────────────────
echo ""
echo "=== GIT DIFF CHECK ==="
cd "$HOKOM"
git diff --check HEAD 2>&1 | head -5
GIT_EXIT=${PIPESTATUS[0]}
VENDOR_PATCH=$(git diff HEAD -- vendor/Taaqol-GPT/src/ 2>/dev/null | wc -l | tr -d ' ')
printf 'GIT_DIFF_CHECK_EXIT=%s\n' "$GIT_EXIT" >> "$STATUS"
printf 'VENDOR_PATCH_COUNT=%s\n' "$VENDOR_PATCH" >> "$STATUS"

echo ""
echo "=== git diff --stat HEAD (non-vendor) ==="
git diff HEAD --stat 2>&1 | head -10

# ── C8: Write JSON summary ────────────────────────────────────────────────────
echo ""
echo "=== C8: Writing JSON summary ==="
export STATUS_FILE="$STATUS"
"$PY" - << 'PYEOF'
import json, os
status_file = os.environ.get('STATUS_FILE', '')
status = {}
with open(status_file) as f:
    for line in f:
        line = line.strip()
        if '=' in line:
            k, _, v = line.partition('=')
            status[k] = v

def gate(key1, key2=None):
    v1 = status.get(key1, "")
    if key2:
        v2 = status.get(key2, "")
        return "PASS" if v1 == "0" and v2 == "0" else ("SKIPPED" if "SKIPPED" in [v1, v2] else "FAIL")
    return status.get(key1, "UNKNOWN")

summary = {
    "document_id": "C5-C7-REPAIR-VERIFY",
    "APPROVED_TARGET_SHA": "05c6668dfb95d9238cff5df1d8bc73d0664bccb3",
    "REPAIR_APPLIED": {
        "pytest_ini_pythonpath": "added src",
        "pyproject_toml_packages_find": "where = [\"src\"]"
    },
    "status": status,
    "C5_GATE": status.get("C5_GATE", "UNKNOWN"),
    "C6_GATE": status.get("C6_GATE", "UNKNOWN"),
    "C7_GATE": status.get("C7_GATE", "UNKNOWN"),
    "F0_GATE": "PASS" if status.get("COLLECT_RUN1_EXIT") == "0" and status.get("COLLECT_RUN2_EXIT") == "0" else "FAIL",
    "F1_GATE": "PASS" if status.get("CANONICAL_RUN1_EXIT") == "0" and status.get("CANONICAL_RUN2_EXIT") == "0" else "FAIL",
    "COLLECTION_RUN1_COUNT": status.get("COLLECT_RUN1_COUNT", "UNKNOWN"),
    "COLLECTION_RUN2_COUNT": status.get("COLLECT_RUN2_COUNT", "UNKNOWN"),
    "CANONICAL_RUN1_SUMMARY": status.get("CANONICAL_RUN1_SUMMARY", "UNKNOWN"),
    "CANONICAL_RUN2_SUMMARY": status.get("CANONICAL_RUN2_SUMMARY", "UNKNOWN"),
    "CANONICAL_COUNTS_IDENTICAL": status.get("CANONICAL_COUNTS_IDENTICAL", "UNKNOWN"),
    "VENDOR_PATCH_COUNT": status.get("VENDOR_PATCH_COUNT", "UNKNOWN"),
    "GIT_DIFF_CHECK_EXIT": status.get("GIT_DIFF_CHECK_EXIT", "UNKNOWN"),
}
out = os.path.expanduser(
    "~/hokom/reports/taaqol_full_integration/c6_c7_summary.json")
with open(out, "w") as f:
    json.dump(summary, f, indent=2)
print(json.dumps(summary, indent=2))
PYEOF

# ── Final status ─────────────────────────────────────────────────────────────
echo ""
echo "=== C5-C7 COMPLETE $(date) ==="
echo "STATUS: $STATUS"
echo "SUMMARY: $SUMMARY"
echo "LOG: $LOG"
echo ""
echo "=== FINAL STATUS ==="
cat "$STATUS"
