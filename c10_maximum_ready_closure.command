#!/usr/bin/env bash
# HOKOM-TAAQOL-MAXIMUM-READY-CLOSURE-01 — C10 gate
#
# Runs the full targeted subset, then F0 x2 and F1 x2.
# Writes JSON and text summaries under reports/taaqol_full_integration/.
#
# Exit codes:
#   0  = success
#   2  = trusted-root / python / vendor SHA / frozen-file check failed
#   3  = target validator failed
#   4  = targeted pytest failed
#   5  = F0 gate failed (collect or node-id diff)
#   6  = F1 gate failed
#   7  = canonical artifact mutated
set -o pipefail

REPO_ROOT="/Users/husseinhiyassat/hokom"
PYTHON="${REPO_ROOT}/.venv-py312/bin/python"
TARGET_SHA="05c6668dfb95d9238cff5df1d8bc73d0664bccb3"
OUT_DIR="${REPO_ROOT}/reports/taaqol_full_integration/c10_runtime_output"
STAMP="$(date +%Y%m%d_%H%M%S)"
SUMMARY_JSON="${REPO_ROOT}/reports/taaqol_full_integration/C10_MAXIMUM_READY_CLOSURE.json"
SUMMARY_TXT="${REPO_ROOT}/reports/taaqol_full_integration/C10_MAXIMUM_READY_CLOSURE.txt"

mkdir -p "${OUT_DIR}"

echo "== C10 START ${STAMP} ==" | tee "${OUT_DIR}/c10_run_${STAMP}.log"

# 1. Verify trusted root
[ "$(pwd)" = "${REPO_ROOT}" ] || cd "${REPO_ROOT}"
[ "$(pwd)" = "${REPO_ROOT}" ] || { echo "wrong root"; exit 2; }

# 2. Verify Python 3.12
PYVER="$(${PYTHON} -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
[ "${PYVER}" = "3.12" ] || { echo "wrong python: ${PYVER}"; exit 2; }

# 3. Verify vendor SHA
VENDOR_SHA="$(git -C vendor/Taaqol-GPT rev-parse HEAD)"
[ "${VENDOR_SHA}" = "${TARGET_SHA}" ] || { echo "vendor SHA mismatch: ${VENDOR_SHA} != ${TARGET_SHA}"; exit 2; }

# 4. Verify vendor clean
VENDOR_DIRTY="$(git -C vendor/Taaqol-GPT status --porcelain | wc -l | tr -d ' ')"
[ "${VENDOR_DIRTY}" = "0" ] || { echo "vendor dirty: ${VENDOR_DIRTY} entries"; exit 2; }

# 5. Verify frozen files unchanged (no unstaged modifications on frozen paths)
FROZEN=("pipeline/p3_candidate/root_profiles.py"
        "pipeline/p3_candidate/root_rules.py"
        "pipeline/p3_candidate/root_resolution.py"
        "pipeline/p3_candidate/root_resolution_orchestrator.py"
        "pipeline/p2_projection/root_projection.py")
for f in "${FROZEN[@]}"; do
  MOD="$(git diff --name-only -- "$f")"
  [ -z "${MOD}" ] || { echo "frozen file modified: $f"; exit 2; }
done

# 6. Requirement document validator
echo "-- requirement doc validator" | tee -a "${OUT_DIR}/c10_run_${STAMP}.log"
${PYTHON} scripts/c10_validate_requirements.py > "${OUT_DIR}/c10_req_validator_${STAMP}.json" 2>&1
REQ_EXIT=$?
[ ${REQ_EXIT} -eq 0 ] || { echo "requirement validator exit=${REQ_EXIT}"; exit 3; }

# 7. Ready-inventory verifier
echo "-- ready-inventory verifier" | tee -a "${OUT_DIR}/c10_run_${STAMP}.log"
${PYTHON} scripts/c10_verify_ready_inventory.py > "${OUT_DIR}/c10_inventory_verifier_${STAMP}.json" 2>&1
INV_EXIT=$?
[ ${INV_EXIT} -eq 0 ] || { echo "ready-inventory verifier exit=${INV_EXIT}"; exit 3; }

# 8. Targeted new tests + Taaqol integration subset
echo "-- targeted tests" | tee -a "${OUT_DIR}/c10_run_${STAMP}.log"
${PYTHON} -m pytest tests/taaqol_integration/test_c10_closure_gate.py tests/taaqol_integration/ -q \
  > "${OUT_DIR}/c10_targeted_${STAMP}.log" 2>&1
TGT_EXIT=$?
[ ${TGT_EXIT} -eq 0 ] || { echo "targeted pytest exit=${TGT_EXIT}"; exit 4; }

# 9. F0 x2
echo "-- F0 run 1" | tee -a "${OUT_DIR}/c10_run_${STAMP}.log"
${PYTHON} -m pytest --collect-only -q 2>&1 | tee "${OUT_DIR}/c10_f0_run1_${STAMP}.txt" | tail -5
F0_R1_EXIT=${PIPESTATUS[0]}
[ ${F0_R1_EXIT} -eq 0 ] || { echo "F0 run 1 exit=${F0_R1_EXIT}"; exit 5; }

echo "-- F0 run 2" | tee -a "${OUT_DIR}/c10_run_${STAMP}.log"
${PYTHON} -m pytest --collect-only -q 2>&1 | tee "${OUT_DIR}/c10_f0_run2_${STAMP}.txt" | tail -5
F0_R2_EXIT=${PIPESTATUS[0]}
[ ${F0_R2_EXIT} -eq 0 ] || { echo "F0 run 2 exit=${F0_R2_EXIT}"; exit 5; }

# 10. Node-ID diff (must be 0)
grep -E '^tests/' "${OUT_DIR}/c10_f0_run1_${STAMP}.txt" | sort > "${OUT_DIR}/c10_f0_run1_${STAMP}.ids"
grep -E '^tests/' "${OUT_DIR}/c10_f0_run2_${STAMP}.txt" | sort > "${OUT_DIR}/c10_f0_run2_${STAMP}.ids"
NODE_DIFF=$(diff "${OUT_DIR}/c10_f0_run1_${STAMP}.ids" "${OUT_DIR}/c10_f0_run2_${STAMP}.ids" | wc -l | tr -d ' ')
[ "${NODE_DIFF}" = "0" ] || { echo "node ID diff = ${NODE_DIFF}"; exit 5; }

# 11. F1 x2 (canonical suite)
echo "-- F1 run 1" | tee -a "${OUT_DIR}/c10_run_${STAMP}.log"
${PYTHON} -m pytest -q -x --tb=short > "${OUT_DIR}/c10_f1_run1_${STAMP}.log" 2>&1
F1_R1_EXIT=$?
F1_R1_RESULT=$(tail -3 "${OUT_DIR}/c10_f1_run1_${STAMP}.log" | tr -d '\n')
[ ${F1_R1_EXIT} -eq 0 ] || { echo "F1 run 1 exit=${F1_R1_EXIT}: ${F1_R1_RESULT}"; exit 6; }

echo "-- F1 run 2" | tee -a "${OUT_DIR}/c10_run_${STAMP}.log"
${PYTHON} -m pytest -q -x --tb=short > "${OUT_DIR}/c10_f1_run2_${STAMP}.log" 2>&1
F1_R2_EXIT=$?
F1_R2_RESULT=$(tail -3 "${OUT_DIR}/c10_f1_run2_${STAMP}.log" | tr -d '\n')
[ ${F1_R2_EXIT} -eq 0 ] || { echo "F1 run 2 exit=${F1_R2_EXIT}: ${F1_R2_RESULT}"; exit 6; }

# 12. Canonical artifact immutability
CANON_DIRTY="$(git status --porcelain reports/ayat_al_dayn_demo/ | wc -l | tr -d ' ')"
[ "${CANON_DIRTY}" = "0" ] || { echo "canonical artifact mutated: ${CANON_DIRTY} entries"; exit 7; }

# 13. Write summaries
${PYTHON} - "${OUT_DIR}" "${STAMP}" "${SUMMARY_JSON}" "${SUMMARY_TXT}" \
           "${OUT_DIR}/c10_f0_run1_${STAMP}.txt" "${OUT_DIR}/c10_f0_run2_${STAMP}.txt" \
           "${OUT_DIR}/c10_f1_run1_${STAMP}.log" "${OUT_DIR}/c10_f1_run2_${STAMP}.log" \
           "${OUT_DIR}/c10_req_validator_${STAMP}.json" "${OUT_DIR}/c10_inventory_verifier_${STAMP}.json" <<'PY'
import json, re, sys, datetime, hashlib, os
OUT_DIR, STAMP, SJ, ST, F01, F02, F11, F12, REQ, INV = sys.argv[1:11]

def re_extract_counts(text):
    m = re.search(r'(\d+)\s+passed', text)
    passed = int(m.group(1)) if m else 0
    m = re.search(r'(\d+)\s+failed', text)
    failed = int(m.group(1)) if m else 0
    m = re.search(r'(\d+)\s+skipped', text)
    skipped = int(m.group(1)) if m else 0
    m = re.search(r'(\d+)\s+warning', text)
    warnings = int(m.group(1)) if m else 0
    m = re.search(r'(\d+)\s+error', text)
    errors = int(m.group(1)) if m else 0
    return {"passed": passed, "failed": failed, "skipped": skipped, "warnings": warnings, "errors": errors}

def re_extract_collected(text):
    m = re.search(r'(\d+)\s+tests?\s+collected', text)
    if m: return int(m.group(1))
    m = re.search(r'(\d+)\s+/\s+\d+\s+selected', text)
    return int(m.group(1)) if m else 0

f0_r1_txt = open(F01).read()
f0_r2_txt = open(F02).read()
f1_r1_txt = open(F11).read()
f1_r2_txt = open(F12).read()
req = json.load(open(REQ))
inv = json.load(open(INV))

f0_r1_c = re_extract_collected(f0_r1_txt)
f0_r2_c = re_extract_collected(f0_r2_txt)
f1_r1 = re_extract_counts(f1_r1_txt)
f1_r2 = re_extract_counts(f1_r2_txt)

summary = {
    "phase": "HOKOM-TAAQOL-MAXIMUM-READY-CLOSURE-01",
    "gate": "C10",
    "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "target_taaqol_sha": "05c6668dfb95d9238cff5df1d8bc73d0664bccb3",
    "c10_exit": 0,
    "f0": {"run1_collected": f0_r1_c, "run2_collected": f0_r2_c,
           "counts_identical": f0_r1_c == f0_r2_c,
           "gate": "PASS" if f0_r1_c == f0_r2_c else "FAIL"},
    "f1": {"run1": f1_r1, "run2": f1_r2,
           "counts_identical": f1_r1 == f1_r2,
           "gate": "PASS" if (f1_r1["failed"]==0 and f1_r2["failed"]==0 and f1_r1==f1_r2) else "FAIL"},
    "requirements": {
        "document_count": req.get("requirement_document_count", 0),
        "technical_status_counts": req.get("technical_status_counts", {}),
        "owner_status_counts": req.get("owner_status_counts", {}),
        "technically_invalid": req.get("requirement_technically_invalid", 0),
    },
    "ready_inventory": {
        "adapter_count": inv.get("adapter_count", 0),
        "READY_RUNTIME_UNWIRED_COUNT": inv.get("READY_RUNTIME_UNWIRED_COUNT", 0),
        "READY_INTEGRATION_UNWIRED_COUNT": inv.get("READY_INTEGRATION_UNWIRED_COUNT", 0),
        "summary": inv.get("summary", {}),
    },
    "artifacts": {
        "run_log": f"{OUT_DIR}/c10_run_{STAMP}.log",
        "f0_run1": F01, "f0_run2": F02, "f1_run1": F11, "f1_run2": F12,
    },
}
with open(SJ, "w") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=2)
lines = [
    "== C10 MAXIMUM READY CLOSURE SUMMARY ==",
    f"target_taaqol_sha  = {summary['target_taaqol_sha']}",
    f"F0 collected r1/r2 = {f0_r1_c} / {f0_r2_c}   identical={f0_r1_c==f0_r2_c}",
    f"F1 r1 passed/failed/skipped/warn/err = {f1_r1['passed']}/{f1_r1['failed']}/{f1_r1['skipped']}/{f1_r1['warnings']}/{f1_r1['errors']}",
    f"F1 r2 passed/failed/skipped/warn/err = {f1_r2['passed']}/{f1_r2['failed']}/{f1_r2['skipped']}/{f1_r2['warnings']}/{f1_r2['errors']}",
    f"REQ docs count={summary['requirements']['document_count']} invalid={summary['requirements']['technically_invalid']} tech_status={summary['requirements']['technical_status_counts']}",
    f"READY unwired R/I = {summary['ready_inventory']['READY_RUNTIME_UNWIRED_COUNT']} / {summary['ready_inventory']['READY_INTEGRATION_UNWIRED_COUNT']}",
    "C10_EXIT = 0",
]
open(ST, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
PY

echo "== C10 END OK ==" | tee -a "${OUT_DIR}/c10_run_${STAMP}.log"
exit 0
