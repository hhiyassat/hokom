#!/bin/bash
# C0–C8 AUTONOMOUS REPAIR + CANONICAL GATE SCRIPT
# Per F0/F1 mandate — no global set -e; per-step exit capture; JSON summary at end.

HOKOM="/Users/husseinhiyassat/hokom"
PY="$HOKOM/.venv-py312/bin/python3.12"
PIP="$HOKOM/.venv-py312/bin/pip"
FRACTAL_SALEH="$HOKOM/../fractal/algebra/Saleh-/src"
OUT="$HOKOM/reports/taaqol_full_integration"
STATUS="$OUT/c0_c8_status.txt"
SUMMARY="$OUT/c0_c8_summary.json"

mkdir -p "$OUT"
: > "$STATUS"   # clear
STAMP=$(date +%Y%m%d_%H%M%S)
LOG="$OUT/c0_c8_run_$STAMP.log"
exec > >(tee -a "$LOG") 2>&1

echo "=== C0-C8 START $(date) ==="

# ── run_step helper ───────────────────────────────────────────────────────────
run_step() {
    local name="$1"; shift
    echo ""
    echo ">>> STEP: $name"
    "$@"
    local rc=$?
    printf '%s=%s\n' "$name" "$rc" >> "$STATUS"
    echo "<<< $name exit=$rc"
    return 0   # never abort; caller checks STATUS file
}

# ── C0: Capture exact collection errors ──────────────────────────────────────
echo ""
echo "=== C0: Capture canonical collection errors ==="
cd "$HOKOM"
"$PY" -m pytest tests/canonical/ --collect-only -vv --tb=long \
    > "$OUT/F0_CANONICAL_COLLECTION_ERRORS.log" 2>&1
printf 'C0_CANONICAL_COLLECT_EXIT=%s\n' "$?" >> "$STATUS"

# Extract error files and first exception lines
echo "--- C0 error files ---"
grep "^ERROR\|^ERRORS\|ImportError\|ModuleNotFoundError\|AttributeError\|TypeError" \
    "$OUT/F0_CANONICAL_COLLECTION_ERRORS.log" | head -30

# ── C1: Verify hokom import path ─────────────────────────────────────────────
echo ""
echo "=== C1: Verify hokom import path ==="
"$PY" - <<'PY'
import sys, inspect
try:
    import hokom
    print("HOKOM_IMPORT=OK")
    print("HOKOM_PATH=", inspect.getfile(hokom))
except ImportError as e:
    print("HOKOM_IMPORT=FAIL")
    print("HOKOM_ERROR=", e)
print("PYTHON=", sys.executable)
print("PYTHONVERSION=", sys.version.split()[0])
print("SYS_PATH_FIRST5=", sys.path[:5])
PY
printf 'C1_HOKOM_IMPORT_CHECK=%s\n' "$?" >> "$STATUS"

# ── C1a: Check if editable install exists ────────────────────────────────────
echo ""
echo "=== C1a: egg-info / site-packages check ==="
ls "$HOKOM/src/hokom.egg-info/" 2>/dev/null && echo "EGG_INFO_PRESENT" || echo "EGG_INFO_ABSENT"
"$PIP" show hokom 2>/dev/null | grep -E "Name|Location|Editable" || echo "HOKOM_NOT_IN_PIP"

# ── C1b: Repair editable install if needed ───────────────────────────────────
HOKOM_IMPORTABLE=$("$PY" -c "import hokom; print('YES')" 2>/dev/null || echo "NO")
if [ "$HOKOM_IMPORTABLE" != "YES" ]; then
    echo ""
    echo "=== C1b: REPAIR — installing hokom editable ==="
    run_step C1b_PIP_INSTALL "$PIP" install -e "$HOKOM" --no-deps
    # Re-verify
    "$PY" -c "import inspect, hokom; print('HOKOM_PATH_AFTER_REPAIR=', inspect.getfile(hokom))"
    printf 'C1b_REPAIR_NEEDED=1\n' >> "$STATUS"
else
    echo "HOKOM_IMPORTABLE=YES — no editable install repair needed"
    printf 'C1b_REPAIR_NEEDED=0\n' >> "$STATUS"
fi

# ── C2: Audit canonical module exact failures ─────────────────────────────────
echo ""
echo "=== C2: Exact error extraction from F0_CANONICAL_COLLECTION_ERRORS.log ==="
echo "--- Error files ---"
grep "^ERROR" "$OUT/F0_CANONICAL_COLLECTION_ERRORS.log" || true

echo "--- Exception types ---"
grep -E "E  (Import|Module|Attribute|Type|Runtime|Name)Error" \
    "$OUT/F0_CANONICAL_COLLECTION_ERRORS.log" | head -20 || true

echo "--- Full tracebacks (first 80 lines) ---"
grep -A5 "^ERRORS\|^_ ERROR " "$OUT/F0_CANONICAL_COLLECTION_ERRORS.log" | head -80 || true

# ── C3: Branch/baseline consistency ──────────────────────────────────────────
echo ""
echo "=== C3: Branch/baseline ==="
git -C "$HOKOM" rev-parse HEAD
git -C "$HOKOM" branch --show-current
git -C "$HOKOM" submodule status vendor/Taaqol-GPT

# ── C4: Registry snapshot status ─────────────────────────────────────────────
echo ""
echo "=== C4: Registry snapshot ==="
SNAPSHOT="$HOKOM/data/canonical_19_stage_registry.json"
if [ -f "$SNAPSHOT" ]; then
    echo "SNAPSHOT_PRESENT=1"
    echo "SNAPSHOT_SIZE=$(wc -c < "$SNAPSHOT")"
    echo "SNAPSHOT_MTIME=$(stat -f '%Sm' "$SNAPSHOT" 2>/dev/null || stat -c '%y' "$SNAPSHOT" 2>/dev/null)"
    # Validate it loads
    "$PY" -c "
import sys; sys.path.insert(0, '$HOKOM/src')
from hokom.canonical.registry.saleh_snapshot import load_snapshot, RegistrySnapshotMissing
try:
    r = load_snapshot()
    print('SNAPSHOT_VALID=1')
    print('SNAPSHOT_LAYERS=', r.layer_count)
except RegistrySnapshotMissing as e:
    print('SNAPSHOT_VALID=0 (RegistrySnapshotMissing)')
except Exception as e:
    print('SNAPSHOT_VALID=0 ERROR=', e)
"
    printf 'C4_SNAPSHOT_PRESENT=1\n' >> "$STATUS"
else
    echo "SNAPSHOT_PRESENT=0"
    printf 'C4_SNAPSHOT_PRESENT=0\n' >> "$STATUS"
    echo ""
    echo "=== C4: Generating registry snapshot ==="
    PYTHONPATH="$HOKOM/src:$HOKOM/vendor/Taaqol-GPT/src:$FRACTAL_SALEH" \
        "$PY" "$HOKOM/scripts/generate_canonical_registry_snapshot.py"
    printf 'C4_SNAPSHOT_GENERATED=%s\n' "$?" >> "$STATUS"
fi

# ── C5: Identify and repair remaining collection errors ──────────────────────
# Re-run collect after repairs to see if errors are cleared
echo ""
echo "=== C5: Post-repair collection probe ==="
"$PY" -m pytest tests/canonical/ --collect-only -q --tb=short \
    > "$OUT/c5_canonical_collect_postrepair.txt" 2>&1
C5_EXIT=$?
tail -5 "$OUT/c5_canonical_collect_postrepair.txt"
printf 'C5_CANONICAL_COLLECT_EXIT=%s\n' "$C5_EXIT" >> "$STATUS"
C5_ERRORS=$(grep -c "^ERROR" "$OUT/c5_canonical_collect_postrepair.txt" 2>/dev/null || echo "0")
printf 'C5_COLLECTION_ERRORS=%s\n' "$C5_ERRORS" >> "$STATUS"

if [ "$C5_ERRORS" -gt 0 ]; then
    echo ""
    echo "=== C5: Remaining errors after basic repair ==="
    grep "^ERROR" "$OUT/c5_canonical_collect_postrepair.txt"
    echo "--- Traceback details ---"
    grep -A8 "ImportError\|ModuleNotFoundError" "$OUT/c5_canonical_collect_postrepair.txt" | head -40
fi

# ── C6: Full collection clean run (twice) ────────────────────────────────────
echo ""
echo "=== C6: Full collection — Run 1 ==="
"$PY" -m pytest test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    --collect-only -q \
    > "$OUT/F0_COLLECT_RUN1.log" 2>&1
C6_RUN1_EXIT=$?
tail -3 "$OUT/F0_COLLECT_RUN1.log"
C6_RUN1_COLLECTED=$(grep -E "^[0-9]+ tests? collected" "$OUT/F0_COLLECT_RUN1.log" | grep -oE "^[0-9]+" || echo "0")
C6_RUN1_ERRORS=$(grep -c "^ERROR" "$OUT/F0_COLLECT_RUN1.log" 2>/dev/null || echo "0")
printf 'COLLECT_RUN1_EXIT=%s\n' "$C6_RUN1_EXIT" >> "$STATUS"
printf 'COLLECT_RUN1_COUNT=%s\n' "$C6_RUN1_COLLECTED" >> "$STATUS"
printf 'COLLECT_RUN1_ERRORS=%s\n' "$C6_RUN1_ERRORS" >> "$STATUS"

echo ""
echo "=== C6: Full collection — Run 2 ==="
"$PY" -m pytest test_hokom.py tests/ \
    --ignore=tests/compatibility \
    --ignore=tests/external_oracle \
    --collect-only -q \
    > "$OUT/F0_COLLECT_RUN2.log" 2>&1
C6_RUN2_EXIT=$?
tail -3 "$OUT/F0_COLLECT_RUN2.log"
C6_RUN2_COLLECTED=$(grep -E "^[0-9]+ tests? collected" "$OUT/F0_COLLECT_RUN2.log" | grep -oE "^[0-9]+" || echo "0")
C6_RUN2_ERRORS=$(grep -c "^ERROR" "$OUT/F0_COLLECT_RUN2.log" 2>/dev/null || echo "0")
printf 'COLLECT_RUN2_EXIT=%s\n' "$C6_RUN2_EXIT" >> "$STATUS"
printf 'COLLECT_RUN2_COUNT=%s\n' "$C6_RUN2_COLLECTED" >> "$STATUS"
printf 'COLLECT_RUN2_ERRORS=%s\n' "$C6_RUN2_ERRORS" >> "$STATUS"

# Node-ID diff
diff <(grep "::" "$OUT/F0_COLLECT_RUN1.log" | sort) \
     <(grep "::" "$OUT/F0_COLLECT_RUN2.log" | sort) \
     > "$OUT/collect_node_diff.txt" 2>&1
NODE_DIFF=$(wc -l < "$OUT/collect_node_diff.txt" | tr -d ' ')
printf 'NODE_ID_DIFF=%s\n' "$NODE_DIFF" >> "$STATUS"

# ── C7: Full canonical double run ────────────────────────────────────────────
# Only run if C6 collection exits cleanly
echo ""
if [ "$C6_RUN1_EXIT" -eq 0 ] && [ "$C6_RUN2_EXIT" -eq 0 ]; then
    echo "=== C7: Canonical Run 1 ==="
    "$PY" -m pytest test_hokom.py tests/ \
        --ignore=tests/compatibility \
        --ignore=tests/external_oracle \
        -q --tb=short \
        -W error::DeprecationWarning \
        -W error::pytest.PytestRemovedIn10Warning \
        > "$OUT/F1_CANONICAL_RUN1.log" 2>&1
    C7_RUN1_EXIT=$?
    C7_RUN1_SUMMARY=$(tail -5 "$OUT/F1_CANONICAL_RUN1.log" | grep -E "passed|failed|error" | tail -1)
    echo "Run1 exit=$C7_RUN1_EXIT summary=$C7_RUN1_SUMMARY"
    printf 'CANONICAL_RUN1_EXIT=%s\n' "$C7_RUN1_EXIT" >> "$STATUS"
    printf 'CANONICAL_RUN1_SUMMARY=%s\n' "$C7_RUN1_SUMMARY" >> "$STATUS"

    echo ""
    echo "=== C7: Canonical Run 2 ==="
    "$PY" -m pytest test_hokom.py tests/ \
        --ignore=tests/compatibility \
        --ignore=tests/external_oracle \
        -q --tb=short \
        -W error::DeprecationWarning \
        -W error::pytest.PytestRemovedIn10Warning \
        > "$OUT/F1_CANONICAL_RUN2.log" 2>&1
    C7_RUN2_EXIT=$?
    C7_RUN2_SUMMARY=$(tail -5 "$OUT/F1_CANONICAL_RUN2.log" | grep -E "passed|failed|error" | tail -1)
    echo "Run2 exit=$C7_RUN2_EXIT summary=$C7_RUN2_SUMMARY"
    printf 'CANONICAL_RUN2_EXIT=%s\n' "$C7_RUN2_EXIT" >> "$STATUS"
    printf 'CANONICAL_RUN2_SUMMARY=%s\n' "$C7_RUN2_SUMMARY" >> "$STATUS"

    if [ "$C7_RUN1_SUMMARY" = "$C7_RUN2_SUMMARY" ]; then
        printf 'CANONICAL_COUNTS_IDENTICAL=1\n' >> "$STATUS"
    else
        printf 'CANONICAL_COUNTS_IDENTICAL=0\n' >> "$STATUS"
    fi
else
    echo "=== C7: SKIPPED — collection not clean (run1=$C6_RUN1_EXIT run2=$C6_RUN2_EXIT) ==="
    printf 'CANONICAL_RUN1_EXIT=SKIPPED\n' >> "$STATUS"
    printf 'CANONICAL_RUN2_EXIT=SKIPPED\n' >> "$STATUS"
    printf 'CANONICAL_COUNTS_IDENTICAL=SKIPPED\n' >> "$STATUS"
fi

# ── Git checks ───────────────────────────────────────────────────────────────
echo ""
echo "=== GIT DIFF CHECK ==="
git -C "$HOKOM" diff --check HEAD 2>&1 | head -5
GIT_EXIT=${PIPESTATUS[0]}
VENDOR_PATCH=$(git -C "$HOKOM" diff HEAD -- vendor/Taaqol-GPT/src/ 2>/dev/null | wc -l | tr -d ' ')
printf 'GIT_DIFF_CHECK_EXIT=%s\n' "$GIT_EXIT" >> "$STATUS"
printf 'VENDOR_PATCH_COUNT=%s\n' "$VENDOR_PATCH" >> "$STATUS"

# ── C8: Write JSON summary ────────────────────────────────────────────────────
echo ""
echo "=== C8: Writing JSON summary ==="

# Determine final gate
FINAL=0
for key in C6_RUN1_EXIT C6_RUN2_EXIT CANONICAL_RUN1_EXIT CANONICAL_RUN2_EXIT; do
    val=$(grep "^${key}=" "$STATUS" | cut -d= -f2 | head -1)
    if [ "$val" != "0" ] && [ "$val" != "" ]; then
        FINAL=1
    fi
done

python3 - << PYEOF
import json, datetime
status = {}
with open("$STATUS") as f:
    for line in f:
        line = line.strip()
        if '=' in line:
            k, _, v = line.partition('=')
            status[k] = v

summary = {
    "document_id": "C0-C8-EXECUTION-SUMMARY",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "APPROVED_TARGET_SHA": "05c6668dfb95d9238cff5df1d8bc73d0664bccb3",
    "status": status,
    "F0_GATE": "PASS" if status.get("COLLECT_RUN1_EXIT") == "0" and status.get("COLLECT_RUN2_EXIT") == "0" else "FAIL",
    "F1_GATE": "PASS" if status.get("CANONICAL_RUN1_EXIT") == "0" and status.get("CANONICAL_RUN2_EXIT") == "0" else "FAIL",
    "COLLECTION_ERRORS": status.get("COLLECT_RUN1_ERRORS", "UNKNOWN"),
    "COLLECTION_COUNTS_MATCH": status.get("COLLECT_RUN1_COUNT") == status.get("COLLECT_RUN2_COUNT"),
}
with open("$SUMMARY", "w") as f:
    json.dump(summary, f, indent=2)
print(json.dumps(summary, indent=2))
PYEOF

# ── Final exit ───────────────────────────────────────────────────────────────
echo ""
echo "=== C0-C8 COMPLETE $(date) ==="
echo "STATUS FILE: $STATUS"
echo "SUMMARY: $SUMMARY"
echo "LOG: $LOG"
echo ""
echo "=== STATUS ==="
cat "$STATUS"

exit $FINAL
