#!/bin/bash
# C7 Run 3 — TARGETED SHA-REPAIR VERIFICATION
# Verifies 11 tests that had stale PINNED_VENDOR_SHA / EXPECTED_PIN constants.
# SHA repairs applied to disk between Run2 and this run.
# Per C0-C8 mandate — no global set -e.

HOKOM="/Users/husseinhiyassat/hokom"
PY="$HOKOM/.venv-py312/bin/python3.12"
OUT="$HOKOM/reports/taaqol_full_integration"
RESULT="$OUT/C7_RUN3_SHA_VERIFY.txt"
mkdir -p "$OUT"
: > "$RESULT"
STAMP=$(date +%Y%m%d_%H%M%S)
LOG="$OUT/C7_RUN3_$STAMP.log"
exec > >(tee -a "$LOG") 2>&1

echo "=== C7 Run3 — SHA Repair Verification — $(date) ==="
echo "SHA repairs applied: PINNED_VENDOR_SHA = 05c6668dfb95d9238cff5df1d8bc73d0664bccb3"
echo ""

cd "$HOKOM"

# ── Confirm SHA repairs on disk ────────────────────────────────────────────
echo "=== Step 0: Confirm SHA on disk (must show 05c6668, zero 35381739) ==="
OLD_COUNT=$(grep -rc "35381739410071ac21dd96702ecbb2acb493f90d" \
    tests/p2_augmented/test_licensing_boundary_adapter_e0.py \
    tests/p2_augmented/test_registry_adapter_e0.py \
    tests/taaqol_bridge/test_live_bridge_recovery.py 2>/dev/null | \
    awk -F: '{sum+=$2} END{print sum+0}')
echo "OLD_SHA_COUNT=$OLD_COUNT (must be 0)"
printf 'OLD_SHA_COUNT=%s\n' "$OLD_COUNT" >> "$RESULT"

if [ "$OLD_COUNT" -gt 0 ]; then
    echo "ERROR: Old SHA still present — repairs not applied correctly"
    printf 'SHA_REPAIR_CONFIRMED=NO\n' >> "$RESULT"
    exit 1
fi
echo "SHA_REPAIR_CONFIRMED=YES"
printf 'SHA_REPAIR_CONFIRMED=YES\n' >> "$RESULT"

# ── Run3: targeted SHA tests ───────────────────────────────────────────────
echo ""
echo "=== Step 1: Run 11 SHA-repaired tests ==="
"$PY" -m pytest \
    "tests/p2_augmented/test_licensing_boundary_adapter_e0.py::TestT05eVendorSha" \
    "tests/p2_augmented/test_licensing_boundary_adapter_e0.py::TestT05gE5EntryPoint::test_entry_point_embeds_vendor_sha" \
    "tests/p2_augmented/test_registry_adapter_e0.py::TestT24FailClosed::test_module_vendor_sha_pinned" \
    "tests/p2_augmented/test_registry_adapter_e0.py::TestT24FailClosed::test_vendor_sha_always_embedded" \
    "tests/taaqol_bridge/test_live_bridge_recovery.py::test_vendor_sha_matches_pin" \
    "tests/taaqol_bridge/test_live_bridge_recovery.py::test_taaqol_not_modified" \
    "tests/taaqol_bridge/test_live_bridge_recovery.py::test_live_pipeline_integration" \
    -v --tb=short
SHA_EXIT=$?
printf 'SHA_TARGETED_EXIT=%s\n' "$SHA_EXIT" >> "$RESULT"

echo ""
if [ "$SHA_EXIT" -eq 0 ]; then
    echo "SHA_TARGETED_RESULT=PASS — all 11 SHA-repaired tests now PASS"
    printf 'SHA_TARGETED_RESULT=PASS\n' >> "$RESULT"
else
    echo "SHA_TARGETED_RESULT=FAIL — some SHA tests still failing (investigate above)"
    printf 'SHA_TARGETED_RESULT=FAIL\n' >> "$RESULT"
fi

# ── Also run the 14 owner-boundary failures to confirm they still fail ─────
echo ""
echo "=== Step 2: Confirm owner-boundary failures still present (expected FAIL) ==="
"$PY" -m pytest \
    "tests/taaqol_live/test_vendor_integrity.py::test_taaqol_submodule_commit_stable" \
    "tests/p2_augmented/test_licensing_boundary_adapter_e0.py::TestT05dPhonologicalChainBlocked" \
    "tests/p2_augmented/test_licensing_boundary_adapter_e0.py::TestT05cUpstreamDirective::test_accept_directive_passes_through_to_downstream_checks" \
    "tests/p2_augmented/test_registry_adapter_e0.py::TestT03P2BlockerDeactivated::test_ayat_al_dayn_registry_empty_in_e0" \
    "tests/e1_lexical_registry/test_ayat_al_dayn_registry.py::TestT_E1_04_Rank::test_registry_entry_rank_candidate" \
    "tests/e4b_preweight_chain/test_preweight_chain_e4b.py::TestT_E4B_05_WeightReadinessChain::test_result_rank_is_candidate" \
    "tests/e5_dal_only/test_dal_only_e5.py::TestT_E5_03_DalOnlyCandidateFields::test_dal_rank_is_candidate" \
    "tests/e6_verbal_madlul/test_verbal_madlul_e6.py::TestT_E6_03_BindingCandidateFields::test_binding_rank_is_candidate" \
    "tests/governance/test_artifact_commit_binding.py::test_artifact_digests_match" \
    -v --tb=line 2>&1 | tail -20
BOUNDARY_EXIT=$?
printf 'BOUNDARY_EXIT=%s\n' "$BOUNDARY_EXIT" >> "$RESULT"
echo "(expected nonzero — these are owner-decision boundary failures)"

echo ""
echo "=== C7 Run3 COMPLETE === $(date) ==="
echo ""
echo "=== RESULT SUMMARY ==="
cat "$RESULT"
echo ""
echo "LOG: $LOG"
echo "RESULT: $RESULT"
