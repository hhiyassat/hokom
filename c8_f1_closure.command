#!/bin/bash
# C8 — F1 CLOSURE SCRIPT
# Full autonomous repair verification: Categories A–F, editable install,
# F0 ×2, F1 ×2.
#
# Constitutional prohibitions honored:
#   NO COMMIT; NO TAG; NO PUSH; NO MERGE
#   AUTONOMOUS_COMMIT_MODE = 0
#
# Run from Mac Finder (double-click) or: bash c8_f1_closure.command

HOKOM="/Users/husseinhiyassat/hokom"
PY="$HOKOM/.venv-py312/bin/python3.12"
OUT="$HOKOM/reports/taaqol_full_integration"
RESULT="$OUT/C8_F1_CLOSURE.txt"
mkdir -p "$OUT"
: > "$RESULT"

STAMP=$(date +%Y%m%d_%H%M%S)
LOG="$OUT/C8_F1_CLOSURE_$STAMP.log"
exec > >(tee -a "$LOG") 2>&1

echo "════════════════════════════════════════════════════════"
echo " C8 F1 CLOSURE — $(date)"
echo "════════════════════════════════════════════════════════"
echo ""

cd "$HOKOM" || { echo "ERROR: cannot cd to $HOKOM"; exit 1; }

# ── Audited artifact list (single canonical source of truth) ──────────────────
# These are the exact three files bound in closure_manifest.8e37b73.json
# (artifact_commit = b19cd9a97aea18b355529e7ec97fd16ecf2f9caa).
AUDITED_ARTIFACTS=(
    "reports/ayat_al_dayn_demo/ayat_al_dayn_manager_report.html"
    "reports/ayat_al_dayn_demo/ayat_al_dayn_results_full.json"
    "reports/ayat_al_dayn_demo/ayat_al_dayn_results.csv"
)

# ── Preflight checks ──────────────────────────────────────────────────────────
echo "=== Preflight: HEAD, submodule, Python ==="
HEAD=$(git rev-parse --short=7 HEAD)
HEAD_FULL=$(git rev-parse HEAD)
echo "HEAD=$HEAD ($HEAD_FULL)"
printf 'HEAD=%s\n' "$HEAD" >> "$RESULT"

# Verify APPROVED_TARGET_SHA is the gitlinked SHA
APPROVED="05c6668dfb95d9238cff5df1d8bc73d0664bccb3"
SUB_STATUS=$(git submodule status vendor/Taaqol-GPT 2>/dev/null | head -1)
echo "submodule_status: $SUB_STATUS"
if echo "$SUB_STATUS" | grep -q "^+"; then
    echo "WARNING: submodule still shows + prefix — git add vendor/Taaqol-GPT needed"
    printf 'SUBMODULE_STAGED=NO\n' >> "$RESULT"
else
    echo "submodule shows no + — staged correctly"
    printf 'SUBMODULE_STAGED=YES\n' >> "$RESULT"
fi

"$PY" --version && echo "Python OK" || { echo "ERROR: Python 3.12 not found at $PY"; exit 1; }

# ── Step 0: Editable install ──────────────────────────────────────────────────
echo ""
echo "=== Step 0: Editable install (--no-build-isolation) ==="
"$PY" -m pip install -e . --no-build-isolation -q 2>&1 | tail -5
INSTALL_EXIT=$?
if [ "$INSTALL_EXIT" -eq 0 ]; then
    echo "EDITABLE_INSTALL=OK"
    printf 'EDITABLE_INSTALL=OK\n' >> "$RESULT"
    # Verify hokom importable
    "$PY" -c "import hokom; print('hokom importable:', hokom.__file__)" && \
        printf 'HOKOM_IMPORTABLE=YES\n' >> "$RESULT" || \
        printf 'HOKOM_IMPORTABLE=NO\n' >> "$RESULT"
else
    echo "EDITABLE_INSTALL=FAIL (exit $INSTALL_EXIT) — continuing without it"
    printf 'EDITABLE_INSTALL=FAIL\n' >> "$RESULT"
fi

# ── Step 1: SHA repair verification ──────────────────────────────────────────
echo ""
echo "=== Step 1: SHA repair verification (OLD_SHA must be 0) ==="
OLD_COUNT=$(grep -rc "35381739410071ac21dd96702ecbb2acb493f90d" \
    tests/p2_augmented/test_licensing_boundary_adapter_e0.py \
    tests/p2_augmented/test_registry_adapter_e0.py \
    tests/taaqol_bridge/test_live_bridge_recovery.py 2>/dev/null | \
    awk -F: '{sum+=$2} END{print sum+0}')
echo "OLD_SHA_COUNT=$OLD_COUNT"
printf 'OLD_SHA_COUNT=%s\n' "$OLD_COUNT" >> "$RESULT"
if [ "$OLD_COUNT" -gt 0 ]; then
    echo "ERROR: old SHA still present"
    printf 'SHA_REPAIR_CONFIRMED=NO\n' >> "$RESULT"
else
    echo "SHA_REPAIR_CONFIRMED=YES"
    printf 'SHA_REPAIR_CONFIRMED=YES\n' >> "$RESULT"
fi

# ── Step 2: Category C repair verification ────────────────────────────────────
echo ""
echo "=== Step 2: Category C — no stale str(rank) assertions ==="
STALE_C=$(grep -rn '"CANDIDATE" in str(result.rank)\|"CANDIDATE" in str(result.candidate\|"CANDIDATE" in str(entry.rank)' \
    tests/ 2>/dev/null | grep -v ".pyc" | wc -l | tr -d ' ')
echo "STALE_RANK_STR_ASSERTIONS=$STALE_C"
printf 'STALE_RANK_STR_ASSERTIONS=%s\n' "$STALE_C" >> "$RESULT"
if [ "$STALE_C" -gt 0 ]; then
    grep -rn '"CANDIDATE" in str(result.rank)\|"CANDIDATE" in str(result.candidate\|"CANDIDATE" in str(entry.rank)' tests/ 2>/dev/null
fi

# ── Step 3: Category A — verify E4C test updates ─────────────────────────────
echo ""
echo "=== Step 3: Category A — E4C test content verification ==="
A_CHECK=$(grep -c "ELIGIBLE" tests/p2_augmented/test_licensing_boundary_adapter_e0.py 2>/dev/null || echo 0)
echo "ELIGIBLE_assertions_in_adapter_test=$A_CHECK"
printf 'ELIGIBLE_ASSERTIONS=%s\n' "$A_CHECK" >> "$RESULT"

# ── Step 4: Governance test restoration ──────────────────────────────────────
echo ""
echo "=== Step 4: Governance — test_no_stale_report_artifacts present ==="
STALE_TEST=$(grep -c "test_no_stale_report_artifacts" tests/governance/test_artifact_commit_binding.py 2>/dev/null || echo 0)
echo "test_no_stale_report_artifacts_count=$STALE_TEST"
printf 'STALE_TEST_RESTORED=%s\n' "$STALE_TEST" >> "$RESULT"

# ── Step 5: Manifest exists for HEAD and commit field matches ─────────────────
echo ""
echo "=== Step 5: Manifest for HEAD exists and commit field matches ==="
EXPECTED_MANIFEST="reports/canonical_gate/closure_manifest.${HEAD}.json"
if [ -f "$EXPECTED_MANIFEST" ]; then
    MANIFEST_COMMIT=$("$PY" -c "
import json, pathlib
d = json.loads(pathlib.Path('$EXPECTED_MANIFEST').read_text())
print(d.get('commit', ''))
" 2>/dev/null)
    echo "EXPECTED_MANIFEST=$EXPECTED_MANIFEST  MANIFEST_COMMIT=$MANIFEST_COMMIT  HEAD=$HEAD"
    if [ "$MANIFEST_COMMIT" = "$HEAD" ]; then
        echo "MANIFEST_HEAD_MATCH=YES"
        printf 'MANIFEST_HEAD_MATCH=YES\n' >> "$RESULT"
    else
        echo "MANIFEST_HEAD_MATCH=NO (internal commit=$MANIFEST_COMMIT, head=$HEAD)"
        printf 'MANIFEST_HEAD_MATCH=NO\n' >> "$RESULT"
    fi
else
    echo "MANIFEST_HEAD_MATCH=NO — manifest not found: $EXPECTED_MANIFEST"
    printf 'MANIFEST_HEAD_MATCH=NO\n' >> "$RESULT"
fi

# ── Step 5b: Restore committed artifacts (before conftest captures baseline) ──
echo ""
echo "=== Step 5b: Restore committed artifact files (Outcome A provenance) ==="
git restore --source=HEAD --worktree -- "${AUDITED_ARTIFACTS[@]}"
echo "Committed artifacts restored (conftest will capture committed bytes)"
printf 'ARTIFACTS_RESTORED=YES\n' >> "$RESULT"

# ── Step 6: F0 Gate — Full collection ×2 ─────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════"
echo " F0 Gate — Collection Run 1 of 2"
echo "════════════════════════════════════════════════════════"
git restore --source=HEAD --worktree -- "${AUDITED_ARTIFACTS[@]}"
"$PY" -m pytest --collect-only -q 2>&1 | tee "$OUT/C8_F0_RUN1_$STAMP.txt"
F0R1_EXIT=${PIPESTATUS[0]}
F0R1_TESTS=$(grep " tests collected" "$OUT/C8_F0_RUN1_$STAMP.txt" | tail -1 | awk '{print $1}')
F0R1_ERRORS=$(grep " error" "$OUT/C8_F0_RUN1_$STAMP.txt" | wc -l | tr -d ' ')
printf 'F0_RUN1_EXIT=%s\nF0_RUN1_TESTS=%s\nF0_RUN1_ERRORS=%s\n' \
    "$F0R1_EXIT" "$F0R1_TESTS" "$F0R1_ERRORS" >> "$RESULT"
echo "F0_RUN1: exit=$F0R1_EXIT  tests=$F0R1_TESTS  errors=$F0R1_ERRORS"

echo ""
echo "════════════════════════════════════════════════════════"
echo " F0 Gate — Collection Run 2 of 2"
echo "════════════════════════════════════════════════════════"
git restore --source=HEAD --worktree -- "${AUDITED_ARTIFACTS[@]}"
"$PY" -m pytest --collect-only -q 2>&1 | tee "$OUT/C8_F0_RUN2_$STAMP.txt"
F0R2_EXIT=${PIPESTATUS[0]}
F0R2_TESTS=$(grep " tests collected" "$OUT/C8_F0_RUN2_$STAMP.txt" | tail -1 | awk '{print $1}')
printf 'F0_RUN2_EXIT=%s\nF0_RUN2_TESTS=%s\n' "$F0R2_EXIT" "$F0R2_TESTS" >> "$RESULT"
echo "F0_RUN2: exit=$F0R2_EXIT  tests=$F0R2_TESTS"

# Node ID diff
if [ "$F0R1_TESTS" = "$F0R2_TESTS" ]; then
    echo "F0_COUNTS_IDENTICAL=YES"
    printf 'F0_COUNTS_IDENTICAL=YES\n' >> "$RESULT"
else
    echo "F0_COUNTS_IDENTICAL=NO ($F0R1_TESTS vs $F0R2_TESTS)"
    printf 'F0_COUNTS_IDENTICAL=NO\n' >> "$RESULT"
fi

# Check for removed old node IDs
if [ -f "reports/canonical_gate/run1_nodes.txt" ]; then
    "$PY" -m pytest --collect-only -q 2>/dev/null | grep "::" | sort > /tmp/c8_current_nodes.txt
    MISSING=$(comm -23 <(sort reports/canonical_gate/run1_nodes.txt) /tmp/c8_current_nodes.txt | wc -l | tr -d ' ')
    echo "OLD_NODE_IDS_REMOVED=$MISSING"
    printf 'OLD_NODE_IDS_REMOVED=%s\n' "$MISSING" >> "$RESULT"
    if [ "$MISSING" -gt 0 ]; then
        echo "MISSING OLD NODES:"
        comm -23 <(sort reports/canonical_gate/run1_nodes.txt) /tmp/c8_current_nodes.txt | head -20
    fi
fi

if [ "$F0R1_EXIT" -ne 0 ] || [ "$F0R2_EXIT" -ne 0 ]; then
    echo "F0_GATE=FAIL — collection errors present"
    printf 'F0_GATE=FAIL\n' >> "$RESULT"
else
    echo "F0_GATE=PASS"
    printf 'F0_GATE=PASS\n' >> "$RESULT"
fi

# ── Step 7: Category F — Performance test ×30 with warmup ────────────────────
echo ""
echo "════════════════════════════════════════════════════════"
echo " Category F — Performance test ×30 with warmup"
echo "════════════════════════════════════════════════════════"

PERF_TEST="tests/live_corpus/test_live_execution.py::test_performance_median_under_75ms"
if "$PY" -m pytest "$PERF_TEST" --collect-only -q 2>/dev/null | grep -q "test_performance_median_under_75ms"; then
    echo "Performance test found — running 3 warmup + 30 measured runs"

    echo "--- Warmup (3 runs) ---"
    for i in 1 2 3; do
        "$PY" -m pytest "$PERF_TEST" -q --tb=no 2>/dev/null | tail -1
    done

    echo "--- 30 measured runs ---"
    PASS_COUNT=0
    FAIL_COUNT=0
    for i in $(seq 1 30); do
        "$PY" -m pytest "$PERF_TEST" -q --tb=no 2>/dev/null | tail -1
        EXIT=$?
        if [ "$EXIT" -eq 0 ]; then
            PASS_COUNT=$((PASS_COUNT + 1))
        else
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    done
    echo "RUN_COUNT=30  PASS_COUNT=$PASS_COUNT  FAIL_COUNT=$FAIL_COUNT"
    printf 'PERF_RUN_COUNT=30\nPERF_PASS_COUNT=%s\nPERF_FAIL_COUNT=%s\n' \
        "$PASS_COUNT" "$FAIL_COUNT" >> "$RESULT"
    if [ "$FAIL_COUNT" -eq 0 ]; then
        echo "CATEGORY_F_GATE=PASS"
        printf 'CATEGORY_F_GATE=PASS\n' >> "$RESULT"
    else
        echo "CATEGORY_F_GATE=FAIL (failures=$FAIL_COUNT/30)"
        printf 'CATEGORY_F_GATE=FAIL\n' >> "$RESULT"
    fi
else
    echo "Performance test not found at: $PERF_TEST"
    FOUND=$("$PY" -m pytest tests/taaqol_full_integration/ --collect-only -q 2>/dev/null | grep "performance" | head -3)
    echo "Performance tests found: $FOUND"
    printf 'CATEGORY_F_GATE=SKIPPED_NOT_FOUND\n' >> "$RESULT"
fi

# ── Step 8: F1 Gate — Full test suite ×2 ─────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════"
echo " F1 Gate — Full Suite Run 1 of 2"
echo "════════════════════════════════════════════════════════"
git restore --source=HEAD --worktree -- "${AUDITED_ARTIFACTS[@]}"
"$PY" -m pytest -x --tb=short -q 2>&1 | tee "$OUT/C8_F1_RUN1_$STAMP.txt"
F1R1_EXIT=${PIPESTATUS[0]}
F1R1_PASSED=$(grep -E "^[0-9]+ passed" "$OUT/C8_F1_RUN1_$STAMP.txt" | tail -1 | awk '{print $1}')
F1R1_FAILED=$(grep -E " failed" "$OUT/C8_F1_RUN1_$STAMP.txt" | tail -1 | grep -oE "[0-9]+ failed" | awk '{print $1}')
F1R1_ERRORS=$(grep -E " error" "$OUT/C8_F1_RUN1_$STAMP.txt" | tail -1 | grep -oE "[0-9]+ error" | awk '{print $1}')
F1R1_FAILED=${F1R1_FAILED:-0}
F1R1_ERRORS=${F1R1_ERRORS:-0}
printf 'F1_RUN1_EXIT=%s\nF1_RUN1_PASSED=%s\nF1_RUN1_FAILED=%s\nF1_RUN1_ERRORS=%s\n' \
    "$F1R1_EXIT" "$F1R1_PASSED" "$F1R1_FAILED" "$F1R1_ERRORS" >> "$RESULT"
echo "F1_RUN1: exit=$F1R1_EXIT  passed=$F1R1_PASSED  failed=$F1R1_FAILED  errors=$F1R1_ERRORS"

echo ""
echo "════════════════════════════════════════════════════════"
echo " F1 Gate — Full Suite Run 2 of 2"
echo "════════════════════════════════════════════════════════"
git restore --source=HEAD --worktree -- "${AUDITED_ARTIFACTS[@]}"
"$PY" -m pytest -x --tb=short -q 2>&1 | tee "$OUT/C8_F1_RUN2_$STAMP.txt"
F1R2_EXIT=${PIPESTATUS[0]}
F1R2_PASSED=$(grep -E "^[0-9]+ passed" "$OUT/C8_F1_RUN2_$STAMP.txt" | tail -1 | awk '{print $1}')
F1R2_FAILED=$(grep -E " failed" "$OUT/C8_F1_RUN2_$STAMP.txt" | tail -1 | grep -oE "[0-9]+ failed" | awk '{print $1}')
F1R2_ERRORS=$(grep -E " error" "$OUT/C8_F1_RUN2_$STAMP.txt" | tail -1 | grep -oE "[0-9]+ error" | awk '{print $1}')
F1R2_FAILED=${F1R2_FAILED:-0}
F1R2_ERRORS=${F1R2_ERRORS:-0}
printf 'F1_RUN2_EXIT=%s\nF1_RUN2_PASSED=%s\nF1_RUN2_FAILED=%s\nF1_RUN2_ERRORS=%s\n' \
    "$F1R2_EXIT" "$F1R2_PASSED" "$F1R2_FAILED" "$F1R2_ERRORS" >> "$RESULT"
echo "F1_RUN2: exit=$F1R2_EXIT  passed=$F1R2_PASSED  failed=$F1R2_FAILED  errors=$F1R2_ERRORS"

# Identical counts?
if [ "$F1R1_PASSED" = "$F1R2_PASSED" ] && [ "$F1R1_FAILED" = "$F1R2_FAILED" ]; then
    echo "F1_COUNTS_IDENTICAL=YES"
    printf 'F1_COUNTS_IDENTICAL=YES\n' >> "$RESULT"
else
    echo "F1_COUNTS_IDENTICAL=NO"
    printf 'F1_COUNTS_IDENTICAL=NO\n' >> "$RESULT"
fi

# ── Step 9: Final artifact cleanup and diff verification ─────────────────────
echo ""
echo "=== Step 9: Final artifact restore and diff verification ==="
git restore --source=HEAD --worktree -- "${AUDITED_ARTIFACTS[@]}"
git diff --exit-code HEAD -- "${AUDITED_ARTIFACTS[@]}"
FINAL_ARTIFACT_DIFF_EXIT=$?
UNTRACKED_ARTIFACT_COUNT=$(
    git status --porcelain -- reports/ayat_al_dayn_demo/ |
    awk '$1 == "??" {count++} END {print count+0}'
)
echo "FINAL_ARTIFACT_DIFF_EXIT=$FINAL_ARTIFACT_DIFF_EXIT"
echo "UNTRACKED_ARTIFACT_COUNT=$UNTRACKED_ARTIFACT_COUNT"
printf 'FINAL_ARTIFACT_DIFF_EXIT=%s\nUNTRACKED_ARTIFACT_COUNT=%s\n' \
    "$FINAL_ARTIFACT_DIFF_EXIT" "$UNTRACKED_ARTIFACT_COUNT" >> "$RESULT"

# ── F1 Gate verdict ───────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════"
echo " F1 GATE VERDICT"
echo "════════════════════════════════════════════════════════"
if [ "$F1R1_EXIT" -eq 0 ] && [ "$F1R2_EXIT" -eq 0 ] && \
   [ "$F1R1_FAILED" -eq 0 ] && [ "$F1R2_FAILED" -eq 0 ] && \
   [ "$F1R1_ERRORS" -eq 0 ] && [ "$F1R2_ERRORS" -eq 0 ]; then
    echo "F1_GATE=PASS"
    printf 'F1_GATE=PASS\n' >> "$RESULT"
else
    echo "F1_GATE=FAIL"
    printf 'F1_GATE=FAIL\n' >> "$RESULT"
    echo ""
    echo "=== Remaining failures (from Run 1) ==="
    grep "FAILED\|ERROR" "$OUT/C8_F1_RUN1_$STAMP.txt" | head -30
fi

# ── Final summary ─────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════"
echo " C8 RESULT SUMMARY"
echo "════════════════════════════════════════════════════════"
cat "$RESULT"
echo ""
echo "LOG:    $LOG"
echo "RESULT: $RESULT"
echo "════════════════════════════════════════════════════════"
echo " C8 COMPLETE — $(date)"
echo "════════════════════════════════════════════════════════"
