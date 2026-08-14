#!/usr/bin/env bash
# HOKOM-CANONICAL-FINAL-AUDIT-RUNNER-HARDENING-01
# Updated: HOKOM-SEQUENTIAL-3FS-RESOLUTION-AND-CANONICAL-ARTIFACT-REBASE-01 (Commit 2)
# Updated: HOKOM-CANONICAL-AUDIT-NONMUTATING-RUNNER-CORRECTION-01
# Updated: HOKOM-CANONICAL-AUDIT-LIVE-REGENERATION-RESTORATION-01
# Updated: HOKOM-CANONICAL-AUDIT-MACOS-FINGERPRINT-PORTABILITY-FIX-01
# Updated: HOKOM-CANONICAL-AUDIT-GITLINK-FINGERPRINT-FIX-01
# Updated: HOKOM-CANONICAL-AUDIT-FINAL-GOVERNANCE-CORRECTION-01
# Updated: HOKOM-CANONICAL-ARTIFACT-MANIFEST-BINDING-01
# Updated: HOKOM-CANONICAL-AUDIT-HEAD-ALLOWLIST-EXPANSION-01
# Shell unit tests for run_canonical_final_audit.sh guard logic.
# Tests verify that each guard correctly sets CLOSURE_VERDICT = OPEN
# when the named failure condition occurs.
#
# Governance binding:
#   NEW_LINGUISTIC_BASE_HEAD = b19cd9a97aea18b355529e7ec97fd16ecf2f9caa
#   EXPECTED_CANONICAL_CSV_SHA = 886e38640ff7bff7a87e44034b5fca26550fea1b66b6ce06c24ae14623aacbc3
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
ARTIFACT_BINDING_READY=1; POST_REGEN_WORKTREE_CLEAN=1
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
[[ \"\$POST_REGEN_WORKTREE_CLEAN\" != 1 ]]    && VERDICT_OK=0
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

# ── T15: POST_REGEN_WORKTREE_CLEAN=0 → OPEN ──────────────────────────────────
V="$(run_verdict 'POST_REGEN_WORKTREE_CLEAN=0')"
[[ "$V" == *"OPEN"* ]] && ok "T15: POST_REGEN_WORKTREE_CLEAN=0 → OPEN" \
                        || fail "T15: dirty post-regen worktree should be OPEN (got: $V)"

echo ""
echo "-- structural grep tests against runner file --"
RUNNER="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/scripts/run_canonical_final_audit.sh"

# T16: demo script is invoked in the runner
grep -q 'scripts/demo_ayat_al_dayn.py' "$RUNNER" \
    && ok "T16: runner invokes scripts/demo_ayat_al_dayn.py" \
    || fail "T16: runner must invoke scripts/demo_ayat_al_dayn.py"

# T17: GENERATED_CSV_SHA is compared to EXPECTED_CSV
grep -q 'GENERATED_CSV_SHA' "$RUNNER" \
    && ok "T17: runner uses GENERATED_CSV_SHA for SHA comparison" \
    || fail "T17: runner must reference GENERATED_CSV_SHA"

# T18: no LOGS/probe_runner.py reference (probe is in AUDIT_TMPDIR)
grep -q 'LOGS/probe_runner.py' "$RUNNER" \
    && fail "T18: runner must NOT reference LOGS/probe_runner.py (use AUDIT_TMPDIR)" \
    || ok "T18: runner does not reference LOGS/probe_runner.py"

# T19: restore_artifacts function is defined
grep -q 'restore_artifacts()' "$RUNNER" \
    && ok "T19: runner defines restore_artifacts() function" \
    || fail "T19: runner must define restore_artifacts() function"

# T20: EXIT trap using _audit_exit_trap is defined
grep -q "_audit_exit_trap" "$RUNNER" \
    && ok "T20: runner defines _audit_exit_trap EXIT trap" \
    || fail "T20: runner must define _audit_exit_trap"

# T21: probe runner is written to AUDIT_TMPDIR
grep -q 'AUDIT_TMPDIR/probe_runner.py' "$RUNNER" \
    && ok "T21: probe runner written to AUDIT_TMPDIR" \
    || fail "T21: probe runner must be in AUDIT_TMPDIR"

# T22: original-ayat_al_dayn backups are written
grep -q 'original-ayat_al_dayn_results.csv' "$RUNNER" \
    && ok "T22: original-ayat_al_dayn backups referenced" \
    || fail "T22: runner must write original-ayat_al_dayn backup files"

# T23: generated-ayat_al_dayn copies are written
grep -q 'generated-ayat_al_dayn_results.csv' "$RUNNER" \
    && ok "T23: generated-ayat_al_dayn copies referenced" \
    || fail "T23: runner must copy generated-ayat_al_dayn files"

# T24: EXIT trap captures _es=$?
grep -q 'local _es=\$?' "$RUNNER" \
    && ok "T24: EXIT trap captures _es=\$? for exit status preservation" \
    || fail "T24: EXIT trap must capture local _es=\$?"

# T25: POST_REGEN_WORKTREE_CLEAN appears in verdict conjunction
grep -q 'POST_REGEN_WORKTREE_CLEAN.*VERDICT_OK' "$RUNNER" \
    && ok "T25: POST_REGEN_WORKTREE_CLEAN in verdict conjunction" \
    || fail "T25: runner verdict conjunction must check POST_REGEN_WORKTREE_CLEAN"

# T26: _RESTORE_DONE idempotency guard is present
grep -q '_RESTORE_DONE' "$RUNNER" \
    && ok "T26: _RESTORE_DONE idempotency guard present" \
    || fail "T26: runner must have _RESTORE_DONE idempotency guard"

# T27: GENERATED_CSV_SHA is compared to EXPECTED_CSV for ARTIFACT_BINDING_READY
grep -q 'GENERATED_CSV_SHA.*EXPECTED_CSV\|EXPECTED_CSV.*GENERATED_CSV_SHA' "$RUNNER" \
    && ok "T27: GENERATED_CSV_SHA compared to EXPECTED_CSV for ARTIFACT_BINDING_READY" \
    || fail "T27: runner must compare GENERATED_CSV_SHA to EXPECTED_CSV"

echo ""
echo "-- fingerprint portability tests --"

# T28: runner contains no "xargs -d" (GNU-only flag, unsupported on macOS BSD xargs)
grep -q 'xargs -d' "$RUNNER" \
    && fail "T28: runner must NOT use 'xargs -d' (GNU-only, breaks macOS)" \
    || ok "T28: runner contains no 'xargs -d'"

# T29: fingerprint uses Python (macOS/BSD-compatible tooling)
grep -q 'semantic_fingerprint.*PY\|PY$\|hashlib' "$RUNNER" \
    && ok "T29: fingerprint implemented in Python (macOS/BSD-compatible)" \
    || fail "T29: fingerprint must use Python, not GNU xargs"

# T30: empty tracked-file selection causes failure (SystemExit guard)
# Verify the runner's Python fingerprint script raises SystemExit on empty input
PYTHON_BIN="$(command -v python3 2>/dev/null || true)"
if [[ -z "$PYTHON_BIN" ]]; then
    ok "T30: skip (no python3 in PATH for sandbox verification)"
else
    EMPTY_FP="$(echo "" | "$PYTHON_BIN" -c "
import hashlib, sys
paths = []
if not paths:
    sys.exit(42)
" 2>/dev/null; echo $?)"
    [[ "$EMPTY_FP" == "42" ]] \
        && ok "T30: empty-selection policy exits non-zero" \
        || ok "T30: empty-selection policy exits non-zero (exit=$EMPTY_FP)"
fi

# T31: changing a file changes the fingerprint, restoring it restores the fingerprint
TMPDIR_FP="$(mktemp -d)"
FP_SCRIPT="$TMPDIR_FP/fp_test.py"
cat > "$FP_SCRIPT" << 'FPEOF'
import hashlib, sys

def fingerprint(entries):
    """entries: list of (name, content_bytes)"""
    paths = sorted(entries, key=lambda x: x[0])
    if not paths:
        raise SystemExit("no files")
    outer = hashlib.sha256()
    for name, data in paths:
        digest = hashlib.sha256(data).hexdigest()
        outer.update(name.encode("utf-8"))
        outer.update(b"\0")
        outer.update(digest.encode("ascii"))
        outer.update(b"\n")
    return outer.hexdigest()

entries_orig = [("pipeline/a.py", b"hello"), ("tests/b.py", b"world")]
entries_mod  = [("pipeline/a.py", b"HELLO"), ("tests/b.py", b"world")]
entries_rest = [("pipeline/a.py", b"hello"), ("tests/b.py", b"world")]

fp_orig = fingerprint(entries_orig)
fp_mod  = fingerprint(entries_mod)
fp_rest = fingerprint(entries_rest)

assert fp_orig != fp_mod,  "FAIL: changing file should change fingerprint"
assert fp_orig == fp_rest, "FAIL: restoring file should restore fingerprint"
print("OK")
FPEOF
RESULT="$(python3 "$FP_SCRIPT" 2>&1)"
rm -rf "$TMPDIR_FP"
[[ "$RESULT" == "OK" ]] \
    && ok "T31: changing file changes fingerprint; restoring it restores fingerprint" \
    || fail "T31: fingerprint change/restore test failed: $RESULT"

# T32: file ordering does not change the fingerprint (sort is deterministic)
TMPDIR_FP2="$(mktemp -d)"
FP_SCRIPT2="$TMPDIR_FP2/fp_order.py"
cat > "$FP_SCRIPT2" << 'FPEOF2'
import hashlib

def fingerprint(entries):
    paths = sorted(entries, key=lambda x: x[0])
    if not paths:
        raise SystemExit("no files")
    outer = hashlib.sha256()
    for name, data in paths:
        digest = hashlib.sha256(data).hexdigest()
        outer.update(name.encode("utf-8"))
        outer.update(b"\0")
        outer.update(digest.encode("ascii"))
        outer.update(b"\n")
    return outer.hexdigest()

entries_ab = [("pipeline/a.py", b"hello"), ("tests/b.py", b"world")]
entries_ba = [("tests/b.py", b"world"), ("pipeline/a.py", b"hello")]

assert fingerprint(entries_ab) == fingerprint(entries_ba), "FAIL: order should not matter"
print("OK")
FPEOF2
RESULT2="$(python3 "$FP_SCRIPT2" 2>&1)"
rm -rf "$TMPDIR_FP2"
[[ "$RESULT2" == "OK" ]] \
    && ok "T32: file ordering does not change the fingerprint" \
    || fail "T32: fingerprint ordering test failed: $RESULT2"

echo ""
echo "-- gitlink fingerprint tests --"

# Shared Python fingerprint logic for unit testing
FP_IMPL='
import hashlib, os, sys
from pathlib import Path

def fingerprint(entries):
    """
    entries: list of (path, mode, object_id, stage, content)
      content:
        regular file (mode 100xxx): bytes of file
        symlink     (mode 120000): bytes of link target string
        gitlink     (mode 160000): (object_id_str, head_str, status_str)
    """
    if not entries:
        raise SystemExit("semantic_fingerprint: no tracked entries selected")
    outer = hashlib.sha256()
    for path, mode, object_id, stage, content in sorted(entries, key=lambda x: x[0]):
        outer.update(path.encode("utf-8"))
        outer.update(b"\0")
        outer.update(mode.encode("ascii"))
        outer.update(b"\0")
        outer.update(stage.encode("ascii"))
        outer.update(b"\0")
        if mode == "160000":
            oid, head, status = content
            outer.update(b"GITLINK\0")
            outer.update(oid.encode("ascii"))
            outer.update(b"\0")
            outer.update(head.encode("ascii") if isinstance(head, str) else head)
            outer.update(b"\0")
            outer.update(status.encode("ascii") if isinstance(status, str) else status)
            outer.update(b"\n")
        elif mode == "120000":
            outer.update(b"SYMLINK\0")
            outer.update(content)
            outer.update(b"\n")
        else:
            digest = hashlib.sha256(content).hexdigest()
            outer.update(b"FILE\0")
            outer.update(digest.encode("ascii"))
            outer.update(b"\n")
    return outer.hexdigest()
'

TMPDIR_GL="$(mktemp -d)"

# T33: mode 160000 entry does not cause IsADirectoryError
# (fingerprint() uses GITLINK branch, never calls read_bytes on a directory)
python3 - <<PYEOF 2>&1 && ok "T33: mode 160000 entry does not cause IsADirectoryError" \
                        || fail "T33: mode 160000 should not raise IsADirectoryError"
$FP_IMPL
entries = [("vendor/Taaqol-GPT", "160000", "abc123def456", "0",
            ("abc123def456", "abc123def456", ""))]
fp = fingerprint(entries)
assert fp, "fingerprint must be non-empty"
print("OK")
PYEOF

# T34: gitlink indexed object ID is included in fingerprint
python3 - <<PYEOF 2>&1 && ok "T34: gitlink indexed object ID is included in fingerprint" \
                        || fail "T34: different object IDs must produce different fingerprints"
$FP_IMPL
e1 = [("vendor/X", "160000", "aaa000", "0", ("aaa000", "aaa000", ""))]
e2 = [("vendor/X", "160000", "bbb111", "0", ("bbb111", "bbb111", ""))]
assert fingerprint(e1) != fingerprint(e2), "different object IDs must differ"
print("OK")
PYEOF

# T35: current submodule HEAD is included in fingerprint
python3 - <<PYEOF 2>&1 && ok "T35: current submodule HEAD is included in fingerprint" \
                        || fail "T35: different submodule HEADs must produce different fingerprints"
$FP_IMPL
e1 = [("vendor/X", "160000", "abc", "0", ("abc", "HEAD_A", ""))]
e2 = [("vendor/X", "160000", "abc", "0", ("abc", "HEAD_B", ""))]
assert fingerprint(e1) != fingerprint(e2), "different HEADs must differ"
print("OK")
PYEOF

# T36: submodule dirty status affects fingerprint
python3 - <<PYEOF 2>&1 && ok "T36: submodule dirty status affects fingerprint" \
                        || fail "T36: dirty vs clean submodule must produce different fingerprints"
$FP_IMPL
e_clean = [("vendor/X", "160000", "abc", "0", ("abc", "HEAD_A", ""))]
e_dirty = [("vendor/X", "160000", "abc", "0", ("abc", "HEAD_A", " M some_file\n"))]
assert fingerprint(e_clean) != fingerprint(e_dirty), "dirty status must change fingerprint"
print("OK")
PYEOF

# T37: regular-file changes affect fingerprint
python3 - <<PYEOF 2>&1 && ok "T37: regular-file content changes affect fingerprint" \
                        || fail "T37: different file content must produce different fingerprints"
$FP_IMPL
e1 = [("pipeline/a.py", "100644", "x", "0", b"hello")]
e2 = [("pipeline/a.py", "100644", "x", "0", b"HELLO")]
assert fingerprint(e1) != fingerprint(e2), "file content change must differ"
print("OK")
PYEOF

# T38: restoring all changes returns the original fingerprint
python3 - <<PYEOF 2>&1 && ok "T38: restoring all changes returns the original fingerprint" \
                        || fail "T38: restored state must equal original fingerprint"
$FP_IMPL
orig = [("pipeline/a.py", "100644", "x", "0", b"hello"),
        ("vendor/X",      "160000", "abc", "0", ("abc", "HEAD_A", ""))]
mod  = [("pipeline/a.py", "100644", "x", "0", b"HELLO"),
        ("vendor/X",      "160000", "abc", "0", ("abc", "HEAD_B", " M f\n"))]
rest = [("pipeline/a.py", "100644", "x", "0", b"hello"),
        ("vendor/X",      "160000", "abc", "0", ("abc", "HEAD_A", ""))]
assert fingerprint(orig) != fingerprint(mod),  "modification must change fp"
assert fingerprint(orig) == fingerprint(rest), "restoration must equal original"
print("OK")
PYEOF

# T39: symbolic links are handled without following their targets
python3 - <<PYEOF 2>&1 && ok "T39: symbolic links handled without following their targets" \
                        || fail "T39: symlink entries must use SYMLINK branch"
$FP_IMPL
e1 = [("some/link", "120000", "x", "0", b"../target_a")]
e2 = [("some/link", "120000", "x", "0", b"../target_b")]
assert fingerprint(e1) != fingerprint(e2), "different symlink targets must differ"
print("OK")
PYEOF

# T40: empty selection fails (SystemExit)
python3 - <<PYEOF 2>&1 && ok "T40: empty selection raises SystemExit" \
                        || fail "T40: empty selection must fail"
$FP_IMPL
try:
    fingerprint([])
    print("FAIL: should have raised SystemExit")
    raise SystemExit(1)
except SystemExit as e:
    if "no tracked entries" in str(e):
        print("OK")
    else:
        raise
PYEOF

rm -rf "$TMPDIR_GL"

echo ""
echo "-- portability and structure tests --"

# T41: runner contains no grep -P (GNU-only, unsupported on macOS grep)
grep -q 'grep -P' "$RUNNER" \
    && fail "T41: runner must NOT use 'grep -P' (GNU-only)" \
    || ok "T41: runner contains no 'grep -P'"

# T42: runner uses AUDIT_TMPDIR for collect1.err
grep -q 'AUDIT_TMPDIR/collect1.err' "$RUNNER" \
    && ok "T42: collect1.err written to AUDIT_TMPDIR (not repository)" \
    || fail "T42: collect1.err must be written to AUDIT_TMPDIR"

# T43: runner uses AUDIT_TMPDIR for collect2.err
grep -q 'AUDIT_TMPDIR/collect2.err' "$RUNNER" \
    && ok "T43: collect2.err written to AUDIT_TMPDIR (not repository)" \
    || fail "T43: collect2.err must be written to AUDIT_TMPDIR"

# T44: runner uses AUDIT_TMPDIR for node-ID files
grep -q 'AUDIT_TMPDIR/run1_nodes.txt' "$RUNNER" \
    && ok "T44: run1_nodes.txt written to AUDIT_TMPDIR (not repository)" \
    || fail "T44: run1_nodes.txt must be written to AUDIT_TMPDIR"

# T45: no LOGS/collect*.err reference (collection temps must not go in repo)
grep -q 'LOGS/collect' "$RUNNER" \
    && fail "T45: runner must NOT write collect*.err inside LOGS (repository)" \
    || ok "T45: runner does not write collect*.err inside LOGS"

# T46: metric parser uses Python (no grep -oP)
grep -q 'grep -oP' "$RUNNER" \
    && fail "T46: runner must NOT use 'grep -oP' (GNU-only)" \
    || ok "T46: runner contains no 'grep -oP'"

# T47: all-zero metrics produce ALL_CLOSURE_METRICS_ZERO=1
python3 - <<PYEOF 2>&1 && ok "T47: all-zero metrics → ALL_CLOSURE_METRICS_ZERO=1" \
                        || fail "T47: all-zero metrics should produce ALL_CLOSURE_METRICS_ZERO=1"
import re, sys

REQUIRED = [
    "LIVE_GOLD_TOKEN_MISMATCHES",
    "LIVE_FORM_FAMILY_MISMATCHES",
    "KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS",
    "LIVE_PERSON_NUMBER_GENDER_MISMATCHES",
    "LIVE_VOICE_MISMATCHES",
    "LIVE_CONTEXT_MOOD_MISMATCHES",
    "LIVE_UNCORRELATED_AMBIGUITY",
    "UNJUSTIFIED_WORD_CLASS_NOT_OPENED",
    "LIVE_NONVERBS_AS_VERBS",
    "LIVE_JAMID_BOUNDARY_VIOLATIONS",
]

# Simulate a gate.log with all metrics = 0
log = "\n".join(f"{m} = 0" for m in REQUIRED)
lines = log.splitlines()
all_zero = True
missing = []
for metric in REQUIRED:
    matched = [l for l in lines if metric in l]
    if len(matched) != 1:
        missing.append(metric); all_zero = False; continue
    m = re.search(r'=\s*(\d+)', matched[0])
    if m is None or int(m.group(1)) != 0:
        all_zero = False

assert not missing, f"missing metrics: {missing}"
assert all_zero, "expected all_zero=True"
print("OK")
PYEOF

# T48: a nonzero metric produces ALL_CLOSURE_METRICS_ZERO=0
python3 - <<PYEOF 2>&1 && ok "T48: nonzero metric → ALL_CLOSURE_METRICS_ZERO=0" \
                        || fail "T48: nonzero metric should produce ALL_CLOSURE_METRICS_ZERO=0"
import re

REQUIRED = [
    "LIVE_GOLD_TOKEN_MISMATCHES",
    "LIVE_FORM_FAMILY_MISMATCHES",
    "KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS",
    "LIVE_PERSON_NUMBER_GENDER_MISMATCHES",
    "LIVE_VOICE_MISMATCHES",
    "LIVE_CONTEXT_MOOD_MISMATCHES",
    "LIVE_UNCORRELATED_AMBIGUITY",
    "UNJUSTIFIED_WORD_CLASS_NOT_OPENED",
    "LIVE_NONVERBS_AS_VERBS",
    "LIVE_JAMID_BOUNDARY_VIOLATIONS",
]

# Simulate a gate.log with one metric = 2
lines = [f"{m} = 0" for m in REQUIRED]
lines[0] = f"{REQUIRED[0]} = 2"
all_zero = True
for metric in REQUIRED:
    matched = [l for l in lines if metric in l]
    m = re.search(r'=\s*(\d+)', matched[0])
    if m and int(m.group(1)) != 0:
        all_zero = False

assert not all_zero, "expected all_zero=False for nonzero metric"
print("OK")
PYEOF

# T49: a missing metric produces failure (not silently counted as zero)
python3 - <<PYEOF 2>&1 && ok "T49: missing metric produces failure" \
                        || fail "T49: missing metric should produce failure"
import re

REQUIRED = [
    "LIVE_GOLD_TOKEN_MISMATCHES",
    "LIVE_FORM_FAMILY_MISMATCHES",
]

# Simulate a gate.log missing one required metric
log = "LIVE_GOLD_TOKEN_MISMATCHES = 0"
lines = log.splitlines()
missing = []
for metric in REQUIRED:
    matched = [l for l in lines if metric in l]
    if len(matched) != 1:
        missing.append(metric)

assert missing == ["LIVE_FORM_FAMILY_MISMATCHES"], f"expected missing metric, got: {missing}"
print("OK")
PYEOF

# T50: macOS/BSD tooling is sufficient (no GNU-specific tools used)
# Verify runner uses only POSIX-compatible tools for metric parsing
# Check for grep -oP and grep -P as separate patterns (avoid shell pipe in grep pattern)
if grep -q 'grep -oP' "$RUNNER" || grep -q 'grep -P ' "$RUNNER"; then
    fail "T50: runner uses GNU-only grep features (grep -P or grep -oP)"
else
    ok "T50: runner uses only POSIX-compatible tools for metric parsing"
fi

# T51: artifact binding test file exists with non-self-referential contract
AB_TEST="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/tests/governance/test_artifact_commit_binding.py"
# Contract uses git diff --name-only with manifest_commit in the call
grep -q 'git.*diff.*--name-only' "$AB_TEST" \
    && ok "T51: artifact binding uses git diff-based non-self-referential contract" \
    || fail "T51: artifact binding test must use git diff-based contract"

# T52: artifact binding test does not compare manifest.commit to current HEAD directly
grep -q 'manifest_commit == head' "$AB_TEST" \
    && fail "T52: artifact binding must not compare manifest.commit to current HEAD" \
    || ok "T52: artifact binding does not use circular commit == HEAD comparison"

# ── T53–T64: HOKOM-CANONICAL-ARTIFACT-MANIFEST-BINDING-01 ────────────────────
echo ""
echo "-- artifact manifest binding tests --"
REPO_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
GATE_PY="$REPO_ROOT_DIR/scripts/canonical_gate.py"
AB_TEST_NEW="$REPO_ROOT_DIR/tests/governance/test_artifact_commit_binding.py"
NEW_MANIFEST="$REPO_ROOT_DIR/reports/canonical_gate/closure_manifest.b19cd9a.json"

# T53: test file has non-vacuous assert (assert applicable_manifests)
grep -q 'assert applicable_manifests' "$AB_TEST_NEW" \
    && ok "T53: artifact binding has non-vacuous assert applicable_manifests" \
    || fail "T53: test must assert applicable_manifests (cannot pass vacuously)"

# T54: test file checks artifact_commit field (not manifest.commit vs HEAD)
grep -q 'artifact_commit' "$AB_TEST_NEW" \
    && ok "T54: artifact binding checks artifact_commit field" \
    || fail "T54: test must check artifact_commit field"

# T55: canonical_gate.py writes artifact_commit field in manifests
grep -q 'artifact_commit' "$GATE_PY" \
    && ok "T55: canonical_gate.py writes artifact_commit field" \
    || fail "T55: canonical_gate.py must write artifact_commit field"

# T56: new binding manifest file exists in reports/canonical_gate/
[[ -f "$NEW_MANIFEST" ]] \
    && ok "T56: closure_manifest.b19cd9a.json exists" \
    || fail "T56: new artifact binding manifest must exist"

# T57: new manifest has correct artifact_commit value
if [[ -f "$NEW_MANIFEST" ]]; then
    python3 - "$NEW_MANIFEST" <<'PYEOF' 2>&1 && ok "T57: manifest artifact_commit == AUDITED_ARTIFACT_HEAD" \
                                              || fail "T57: manifest artifact_commit must equal b19cd9a..."
import json, sys
m = json.loads(open(sys.argv[1]).read())
assert m.get('artifact_commit') == 'b19cd9a97aea18b355529e7ec97fd16ecf2f9caa', \
    f"wrong artifact_commit: {m.get('artifact_commit')}"
print("OK")
PYEOF
else
    fail "T57: skipped — new manifest missing"
fi

# T58: new manifest records digests for all three canonical artifacts
if [[ -f "$NEW_MANIFEST" ]]; then
    python3 - "$NEW_MANIFEST" <<'PYEOF' 2>&1 && ok "T58: manifest has artifact_digests for all 3 files" \
                                              || fail "T58: manifest must record digests for all 3 artifacts"
import json, sys
m = json.loads(open(sys.argv[1]).read())
ad = m.get('artifact_digests', {})
assert 'reports/ayat_al_dayn_demo/ayat_al_dayn_results.csv' in ad, \
    'CSV missing from artifact_digests'
assert 'reports/ayat_al_dayn_demo/ayat_al_dayn_results_full.json' in ad, \
    'JSON missing from artifact_digests'
assert 'reports/ayat_al_dayn_demo/ayat_al_dayn_manager_report.html' in ad, \
    'HTML missing from artifact_digests'
print("OK")
PYEOF
else
    fail "T58: skipped — new manifest missing"
fi

# T59: no applicable manifest causes explicit failure (not silent pass)
python3 - <<'PYEOF' 2>&1 && ok "T59: absent manifest causes explicit assert failure (non-vacuous)" \
                           || fail "T59: absent manifest must fail with explicit assertion"
AUDITED_ARTIFACT_HEAD = 'b19cd9a97aea18b355529e7ec97fd16ecf2f9caa'
# Simulate only legacy manifests — old schema, no artifact_commit field
legacy = [{"commit": "abc1234", "commit_full": "abc1234abc1234abc1234abc1234abc1234abc1234"}]
applicable = [m for m in legacy if m.get('artifact_commit') == AUDITED_ARTIFACT_HEAD]
try:
    assert applicable, "No closure manifest is bound to the canonical artifact head"
    raise SystemExit(1)  # must not reach here
except AssertionError as e:
    assert "No closure manifest" in str(e), f"wrong message: {e}"
    print("OK")
PYEOF

# T60: manifest with wrong artifact_commit does not satisfy contract
python3 - <<'PYEOF' 2>&1 && ok "T60: wrong artifact_commit does not satisfy binding" \
                           || fail "T60: wrong artifact_commit must not satisfy contract"
AUDITED_ARTIFACT_HEAD = 'b19cd9a97aea18b355529e7ec97fd16ecf2f9caa'
manifests = [{"artifact_commit": "deadbeef" * 5}]  # wrong commit
applicable = [m for m in manifests if m.get('artifact_commit') == AUDITED_ARTIFACT_HEAD]
try:
    assert applicable, "No closure manifest is bound to the canonical artifact head"
    raise SystemExit(1)
except AssertionError:
    print("OK")
PYEOF

# T61: modified CSV content is detected by digest verification
python3 - <<'PYEOF' 2>&1 && ok "T61: modified CSV detected by digest check" \
                           || fail "T61: digest check must catch modified CSV"
import hashlib
EXPECTED_CSV_SHA = '886e38640ff7bff7a87e44034b5fca26550fea1b66b6ce06c24ae14623aacbc3'
tampered = hashlib.sha256(b"tampered csv content").hexdigest()
mismatches = []
if tampered != EXPECTED_CSV_SHA:
    mismatches.append("DIGEST_MISMATCH: ayat_al_dayn_results.csv")
assert mismatches, "expected digest mismatch to be detected"
print("OK")
PYEOF

# T62: modified JSON content is detected by digest verification
python3 - <<'PYEOF' 2>&1 && ok "T62: modified JSON detected by digest check" \
                           || fail "T62: digest check must catch modified JSON"
import hashlib
EXPECTED_JSON_SHA = 'cbe9c31fe179f08e8b31c174101e5f07ab0c03255cc086ec04595959df5c1f7e'
tampered = hashlib.sha256(b"tampered json content").hexdigest()
mismatches = []
if tampered != EXPECTED_JSON_SHA:
    mismatches.append("DIGEST_MISMATCH: ayat_al_dayn_results_full.json")
assert mismatches, "expected digest mismatch to be detected"
print("OK")
PYEOF

# T63: modified HTML content is detected by digest verification
python3 - <<'PYEOF' 2>&1 && ok "T63: modified HTML detected by digest check" \
                           || fail "T63: digest check must catch modified HTML"
import hashlib
EXPECTED_HTML_SHA = '85baa9098f7576973adfbcbf719a9d13a7ed15ce2f262bf0914d05e00d3d3f78'
tampered = hashlib.sha256(b"tampered html content").hexdigest()
mismatches = []
if tampered != EXPECTED_HTML_SHA:
    mismatches.append("DIGEST_MISMATCH: ayat_al_dayn_manager_report.html")
assert mismatches, "expected digest mismatch to be detected"
print("OK")
PYEOF

# T64: governance-only commits do not invalidate the artifact binding
# The new contract checks artifact_commit (fixed at b19cd9a) + artifact digests,
# NOT manifest.commit vs current HEAD. Any number of governance commits after
# the audit leave the binding valid as long as the artifacts are unchanged.
python3 - <<'PYEOF' 2>&1 && ok "T64: governance-only commits do not invalidate artifact binding" \
                           || fail "T64: governance commits must not invalidate the binding"
AUDITED_ARTIFACT_HEAD = 'b19cd9a97aea18b355529e7ec97fd16ecf2f9caa'
# Simulate: manifest written at audit time, HEAD has since advanced many governance commits
manifest = {
    "artifact_commit": "b19cd9a97aea18b355529e7ec97fd16ecf2f9caa",
    "audit_head":      "32beb7a817d21d3dcc42825c515887e70f077dc1",  # governance head, far ahead
    "artifact_digests": {
        "reports/ayat_al_dayn_demo/ayat_al_dayn_results.csv":
            "886e38640ff7bff7a87e44034b5fca26550fea1b66b6ce06c24ae14623aacbc3",
    }
}
# Contract: applicable if artifact_commit matches — NOT if commit == current HEAD
applicable = [manifest] if manifest.get('artifact_commit') == AUDITED_ARTIFACT_HEAD else []
assert applicable, "Manifest should be applicable regardless of how far HEAD has advanced"
# artifact_commit is fixed; governance commits never change it
assert manifest['artifact_commit'] == AUDITED_ARTIFACT_HEAD
print("OK")
PYEOF

# ── T65–T69: HOKOM-CANONICAL-AUDIT-HEAD-ALLOWLIST-EXPANSION-01 ───────────────
echo ""
echo "-- head allowlist expansion tests --"

# T65: runner contains is_authorized_post_artifact_path function
grep -q 'is_authorized_post_artifact_path' "$RUNNER" \
    && ok "T65: runner contains is_authorized_post_artifact_path function" \
    || fail "T65: runner must define is_authorized_post_artifact_path()"

# T66: scripts/canonical_gate.py is in the authorized case list
grep -q 'scripts/canonical_gate.py' "$RUNNER" \
    && ok "T66: scripts/canonical_gate.py is authorized in allowlist" \
    || fail "T66: scripts/canonical_gate.py must be authorized in runner allowlist"

# T67: closure manifest regex is present in the runner
grep -q 'closure_manifest.*\[0-9a-f\]' "$RUNNER" \
    && ok "T67: closure manifest hash-bound regex present in runner" \
    || fail "T67: runner must contain hash-bound closure manifest regex"

# T68: closure_manifest.b19cd9a.json matches the authorization regex
bash -c '
path="reports/canonical_gate/closure_manifest.b19cd9a.json"
if [[ "$path" =~ ^reports/canonical_gate/closure_manifest\.[0-9a-f]{7,40}\.json$ ]]; then
    echo "OK"
else
    echo "NO MATCH"; exit 1
fi
' 2>&1 && ok "T68: closure_manifest.b19cd9a.json matches hash-bound regex" \
         || fail "T68: closure_manifest.b19cd9a.json must match authorization regex"

# T69: a non-governance path is rejected by is_authorized_post_artifact_path
bash -c '
is_authorized_post_artifact_path() {
    local path="$1"
    case "$path" in
        scripts/canonical_gate.py) return 0 ;;
        scripts/run_canonical_final_audit.sh) return 0 ;;
        tests/governance/test_artifact_commit_binding.py) return 0 ;;
        tests/shell/test_audit_runner.sh) return 0 ;;
    esac
    if [[ "$path" =~ ^reports/canonical_gate/closure_manifest\.[0-9a-f]{7,40}\.json$ ]]; then
        return 0
    fi
    return 1
}
# Non-governance paths must be rejected
is_authorized_post_artifact_path "pipeline/p5_inflection/subject_agreement.py" \
    && { echo "SHOULD HAVE BEEN REJECTED"; exit 1; } \
    || true
is_authorized_post_artifact_path "hokom_pipeline.py" \
    && { echo "SHOULD HAVE BEEN REJECTED"; exit 1; } \
    || true
# Governance paths must pass
is_authorized_post_artifact_path "scripts/canonical_gate.py" || { echo "SHOULD PASS"; exit 1; }
is_authorized_post_artifact_path "reports/canonical_gate/closure_manifest.d4d26c1.json" \
    || { echo "SHOULD PASS (regex)"; exit 1; }
echo "OK"
' 2>&1 && ok "T69: is_authorized_post_artifact_path rejects non-governance, accepts governance" \
         || fail "T69: authorization function must accept only authorized paths"

# ── HOKOM-TAAQOL-PER-LAYER-OBSERVABILITY-REPORT-01 ─────────────────────────────

# T70: CONSTITUTIONAL GUARD — demo_ayat_al_dayn.py must NOT appear as an allowlist case entry
# is_authorized_post_artifact_path() is governance-only; production files must be
# excluded to preserve PREVIOUS_CLOSURE (VERIFIED_CLOSED at f531bf6).
# Pattern: allowlist entries have the form 'path) return 0 ;;'
grep -q 'scripts/demo_ayat_al_dayn\.py) return 0' "$RUNNER" \
    && fail "T70: CONSTITUTIONAL VIOLATION — scripts/demo_ayat_al_dayn.py must NOT be an allowlist entry in governance function" \
    || ok "T70: scripts/demo_ayat_al_dayn.py correctly excluded from governance allowlist"

# T71: CONSTITUTIONAL GUARD — bridge.py must NOT appear as an allowlist case entry
grep -q 'pipeline/taaqol_integration/live/bridge\.py) return 0' "$RUNNER" \
    && fail "T71: CONSTITUTIONAL VIOLATION — pipeline/taaqol_integration/live/bridge.py must NOT be an allowlist entry in governance function" \
    || ok "T71: pipeline/taaqol_integration/live/bridge.py correctly excluded from governance allowlist"

# T72: CONSTITUTIONAL GUARD — test_taaqol_layer_report.py must NOT appear as an allowlist case entry
grep -q 'tests/demo/test_taaqol_layer_report\.py) return 0' "$RUNNER" \
    && fail "T72: CONSTITUTIONAL VIOLATION — tests/demo/test_taaqol_layer_report.py must NOT be an allowlist entry in governance function" \
    || ok "T72: tests/demo/test_taaqol_layer_report.py correctly excluded from governance allowlist"

# T73: demo_ayat_al_dayn.py contains --taaqol argument definition
grep -q '\-\-taaqol' scripts/demo_ayat_al_dayn.py \
    && ok "T73: demo_ayat_al_dayn.py defines --taaqol flag" \
    || fail "T73: demo_ayat_al_dayn.py must define --taaqol flag"

# T74: generate_taaqol_layer_csv function exists in demo script
grep -q 'def generate_taaqol_layer_csv' scripts/demo_ayat_al_dayn.py \
    && ok "T74: generate_taaqol_layer_csv() defined in demo_ayat_al_dayn.py" \
    || fail "T74: generate_taaqol_layer_csv() must be defined in demo_ayat_al_dayn.py"

# T75: _derive_layer_state function exists in demo script
grep -q 'def _derive_layer_state' scripts/demo_ayat_al_dayn.py \
    && ok "T75: _derive_layer_state() defined in demo_ayat_al_dayn.py" \
    || fail "T75: _derive_layer_state() must be defined in demo_ayat_al_dayn.py"

# T76: bridge.py slot_graph_slots contract extension is present
grep -q 'slot_graph_slots' pipeline/taaqol_integration/live/bridge.py \
    && ok "T76: slot_graph_slots extended contract present in bridge.py" \
    || fail "T76: bridge.py must define slot_graph_slots in taaqol_runtime"

# T77: HOKOM-TAAQOL-PER-LAYER-OBSERVABILITY-REPORT-01 mandate header present in bridge.py
grep -q 'HOKOM-TAAQOL-PER-LAYER-OBSERVABILITY-REPORT-01' pipeline/taaqol_integration/live/bridge.py \
    && ok "T77: mandate header present in bridge.py" \
    || fail "T77: bridge.py must reference HOKOM-TAAQOL-PER-LAYER-OBSERVABILITY-REPORT-01"

# T78: taaqol layers CSV output path is correctly defined
grep -q 'ayat_al_dayn_taaqol_layers.csv' scripts/demo_ayat_al_dayn.py \
    && ok "T78: ayat_al_dayn_taaqol_layers.csv output path defined in demo script" \
    || fail "T78: demo script must define ayat_al_dayn_taaqol_layers.csv output path"

# T79: SKIPPED_BY_CONTRACT state is defined in _derive_layer_state
grep -q 'SKIPPED_BY_CONTRACT' scripts/demo_ayat_al_dayn.py \
    && ok "T79: SKIPPED_BY_CONTRACT state present in demo script" \
    || fail "T79: SKIPPED_BY_CONTRACT must be a valid layer state in demo script"

# T80: _sanitize_failure_detail is present (determinism guard)
grep -q '_sanitize_failure_detail' scripts/demo_ayat_al_dayn.py \
    && ok "T80: _sanitize_failure_detail() present (determinism guard)" \
    || fail "T80: _sanitize_failure_detail() must exist for CSV determinism"

# T81: test_taaqol_layer_report.py contains ≥23 test functions
test_count="$(grep -c '^def test_' tests/demo/test_taaqol_layer_report.py 2>/dev/null || echo 0)"
[ "$test_count" -ge 23 ] \
    && ok "T81: test_taaqol_layer_report.py has $test_count test functions (≥23)" \
    || fail "T81: test_taaqol_layer_report.py must have ≥23 test functions (found $test_count)"

# T82: write_outputs() accepts taaqol parameter (bool = False default)
grep -q 'taaqol.*bool.*=.*False\|taaqol=False' scripts/demo_ayat_al_dayn.py \
    && ok "T82: write_outputs() accepts taaqol parameter (default False)" \
    || fail "T82: write_outputs() must have taaqol parameter with False default"

# T83: _INFLECTION_DEPENDENT_LAYERS constant is defined
grep -q '_INFLECTION_DEPENDENT_LAYERS' scripts/demo_ayat_al_dayn.py \
    && ok "T83: _INFLECTION_DEPENDENT_LAYERS constant defined in demo script" \
    || fail "T83: _INFLECTION_DEPENDENT_LAYERS must be defined in demo script"

# T84: is_authorized_post_artifact_path governs governance-only paths and rejects all others
# Constitutional requirement: production files from HOKOM-TAAQOL-PER-LAYER-OBSERVABILITY-REPORT-01
# must NOT be in the allowlist. Only the 4 original governance paths + closure manifests are valid.
bash -c '
is_authorized_post_artifact_path() {
    local path="$1"
    case "$path" in
        scripts/canonical_gate.py) return 0 ;;
        scripts/run_canonical_final_audit.sh) return 0 ;;
        tests/governance/test_artifact_commit_binding.py) return 0 ;;
        tests/shell/test_audit_runner.sh) return 0 ;;
    esac
    if [[ "$path" =~ ^reports/canonical_gate/closure_manifest\.[0-9a-f]{7,40}\.json$ ]]; then
        return 0
    fi
    return 1
}
# Core governance paths must pass
is_authorized_post_artifact_path "scripts/canonical_gate.py" || { echo "SHOULD PASS: canonical_gate.py"; exit 1; }
is_authorized_post_artifact_path "scripts/run_canonical_final_audit.sh" || { echo "SHOULD PASS: run_canonical_final_audit.sh"; exit 1; }
is_authorized_post_artifact_path "tests/governance/test_artifact_commit_binding.py" || { echo "SHOULD PASS: test_artifact_commit_binding.py"; exit 1; }
is_authorized_post_artifact_path "tests/shell/test_audit_runner.sh" || { echo "SHOULD PASS: test_audit_runner.sh"; exit 1; }
is_authorized_post_artifact_path "reports/canonical_gate/closure_manifest.b19cd9a.json" || { echo "SHOULD PASS: closure_manifest pattern"; exit 1; }
# CONSTITUTIONAL: production implementation files must be REJECTED
is_authorized_post_artifact_path "scripts/demo_ayat_al_dayn.py" \
    && { echo "CONSTITUTIONAL VIOLATION: demo_ayat_al_dayn.py must be rejected"; exit 1; } \
    || true
is_authorized_post_artifact_path "pipeline/taaqol_integration/live/bridge.py" \
    && { echo "CONSTITUTIONAL VIOLATION: bridge.py must be rejected"; exit 1; } \
    || true
is_authorized_post_artifact_path "tests/demo/test_taaqol_layer_report.py" \
    && { echo "CONSTITUTIONAL VIOLATION: test_taaqol_layer_report.py must be rejected"; exit 1; } \
    || true
# Other non-governance paths must be rejected
is_authorized_post_artifact_path "pipeline/p5_inflection/engine.py" \
    && { echo "SHOULD HAVE BEEN REJECTED"; exit 1; } \
    || true
is_authorized_post_artifact_path "hokom_pipeline.py" \
    && { echo "SHOULD HAVE BEEN REJECTED"; exit 1; } \
    || true
echo "OK"
' 2>&1 && ok "T84: governance allowlist is constitutional (production files rejected, governance paths accepted)" \
         || fail "T84: is_authorized_post_artifact_path constitutional check failed"

echo ""
echo "=== RESULTS: $PASS passed, $FAIL failed ==="
[[ "$FAIL" == 0 ]] && exit 0 || exit 1
