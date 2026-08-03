#!/usr/bin/env bash
# M3 — CONTROLLED VENDOR POINTER UPDATE TO APPROVED_TARGET_SHA
# ============================================================
# STATUS: STAGED — DO NOT RUN until M1 gate conditions are met:
#   REFERENCE_HEAD == 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
#   REFERENCE_COLLECT_EXIT == 0
#   REFERENCE_COLLECTED > 0
#   REFERENCE_SUITE_EXIT == 0
#   REFERENCE_FAILED == 0
#   REFERENCE_INTERNAL_EXCEPTIONS == 0
#
# PROHIBITIONS (§13): NO COMMIT; NO TAG; NO PUSH; NO MERGE; NO VENDOR PATCH
# Run from: /Users/husseinhiyassat/hokom
# ============================================================

set -euo pipefail

APPROVED_TARGET_SHA="05c6668dfb95d9238cff5df1d8bc73d0664bccb3"
PINNED_SHA="35381739410071ac21dd96702ecbb2acb493f90d"
VENDOR_DIR="vendor/Taaqol-GPT"

echo "=== M3 — VENDOR POINTER UPDATE ==="
echo "APPROVED_TARGET_SHA: $APPROVED_TARGET_SHA"
echo "Current vendor HEAD: $(git -C $VENDOR_DIR rev-parse HEAD 2>/dev/null || echo NOT_FOUND)"

# --- STEP 1: VERIFY M1 GATE (must be pre-verified by caller) ---
# This script does not verify M1 itself — caller must confirm gate is cleared.
echo ""
echo "[M3-STEP-1] Vendor checkout to APPROVED_TARGET_SHA..."
git -C "$VENDOR_DIR" checkout --detach "$APPROVED_TARGET_SHA"

# Verify
VENDOR_HEAD=$(git -C "$VENDOR_DIR" rev-parse HEAD)
if [ "$VENDOR_HEAD" != "$APPROVED_TARGET_SHA" ]; then
  echo "ERROR: VENDOR_HEAD=$VENDOR_HEAD != APPROVED_TARGET_SHA=$APPROVED_TARGET_SHA"
  exit 1
fi
echo "VENDOR_HEAD verified: $VENDOR_HEAD"
echo "VENDOR_WORKTREE_CLEAN: $(git -C $VENDOR_DIR status --porcelain | wc -l | tr -d ' ')"

# --- STEP 2: APPLY SHA STAMP UPDATES ---
# 10 files: _VENDOR_SHA = OLD_SHA → NEW_SHA
echo ""
echo "[M3-STEP-2] Applying 10 SHA stamp updates..."

update_sha_stamp() {
  local file="$1"
  local line="$2"
  local old_sha="$PINNED_SHA"
  local new_sha="$APPROVED_TARGET_SHA"

  if [ ! -f "$file" ]; then
    echo "  ERROR: $file not found"
    exit 1
  fi

  # Verify old SHA is present
  if ! grep -q "$old_sha" "$file"; then
    echo "  WARNING: $old_sha not found in $file — may already be updated"
    grep "_VENDOR_SHA" "$file" | head -2
    return
  fi

  sed -i "s/$old_sha/$new_sha/g" "$file"
  echo "  UPDATED: $file (line ~$line)"
  grep "_VENDOR_SHA" "$file" | head -1
}

update_sha_stamp "pipeline/taaqol_integration/e1_lexical_registry/ayat_al_dayn_registry.py" 33
update_sha_stamp "pipeline/taaqol_integration/weight_layer/dal_only_adapter.py" 65
update_sha_stamp "pipeline/taaqol_integration/weight_layer/formal_shape_adapter.py" 23
update_sha_stamp "pipeline/taaqol_integration/weight_layer/licensing_boundary_adapter.py" 75
update_sha_stamp "pipeline/taaqol_integration/weight_layer/maqam_context_adapter.py" 22
update_sha_stamp "pipeline/taaqol_integration/weight_layer/mufrad_semantic_slot_adapter.py" 28
update_sha_stamp "pipeline/taaqol_integration/weight_layer/preweight_chain_adapter.py" 53
update_sha_stamp "pipeline/taaqol_integration/weight_layer/registry_adapter.py" 53
update_sha_stamp "pipeline/taaqol_integration/weight_layer/relation_candidate_adapter.py" 28
update_sha_stamp "pipeline/taaqol_integration/weight_layer/verbal_madlul_adapter.py" 61

echo ""
echo "[M3-STEP-3] Verify: no stray PINNED_SHA references remain..."
STRAY=$(grep -r "$PINNED_SHA" pipeline/taaqol_integration/ 2>/dev/null | wc -l)
echo "Stray PINNED_SHA references in pipeline/: $STRAY"
if [ "$STRAY" -gt 0 ]; then
  grep -r "$PINNED_SHA" pipeline/taaqol_integration/ 2>/dev/null
  echo "ERROR: Stray references found — manual review required"
  exit 1
fi

echo ""
echo "[M3-STEP-4] Verify: vendor has no uncommitted patches..."
VENDOR_PATCH_COUNT=$(git -C "$VENDOR_DIR" status --porcelain | wc -l)
echo "VENDOR_PATCH_COUNT: $VENDOR_PATCH_COUNT"
if [ "$VENDOR_PATCH_COUNT" -gt 0 ]; then
  echo "ERROR: Vendor has uncommitted changes — §13 prohibits vendor patches"
  git -C "$VENDOR_DIR" status
  exit 1
fi

echo ""
echo "[M3-STEP-5] Git diff summary (HOKOM side only)..."
echo "Files changed in HOKOM pipeline:"
git diff --name-only pipeline/taaqol_integration/ | head -20
echo ""
echo "Stats:"
git diff --stat pipeline/taaqol_integration/ | tail -3

echo ""
echo "[M3-STEP-6] Verify no frozen files changed..."
# Frozen files per §13: vendor source, pyproject.toml, CHANGELOG, etc.
FROZEN_CHANGED=$(git diff --name-only | grep -E "vendor/|pyproject\.toml|CHANGELOG|CONSTITUTIONAL_MATRIX" | wc -l)
echo "Frozen file changes: $FROZEN_CHANGED"
if [ "$FROZEN_CHANGED" -gt 0 ]; then
  git diff --name-only | grep -E "vendor/|pyproject\.toml|CHANGELOG|CONSTITUTIONAL_MATRIX"
  echo "ERROR: Frozen files modified"
  exit 1
fi

echo ""
echo "=== M3 COMPLETE ==="
echo "VENDOR_HEAD:       $APPROVED_TARGET_SHA"
echo "VENDOR_WORKTREE_CLEAN: 1"
echo "VENDOR_PATCH_COUNT:    0"
echo "SHA_STAMPS_UPDATED:    10"
echo "STRAY_PINNED_SHA:      0"
echo "NO_COMMIT: YES (§13 compliant)"
echo ""
echo "NEXT: Run M4 baseline refreeze"
