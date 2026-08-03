#!/usr/bin/env bash
# HOKOM-EVIDENCE-PRODUCTION-CLOSURE-01 — C11 gate
#
# Runs C9 + C10 regression, C11 evidence-graph validation, targeted subset,
# then F0 x2 and F1 x2. Writes JSON and text summaries under
# reports/taaqol_full_integration/.
#
# Exit codes:
#   0  = success
#   2  = trusted-root / python / vendor / frozen-file check failed
#   3  = requirement or evidence validator failed
#   4  = targeted pytest failed
#   5  = F0 gate failed
#   6  = F1 gate failed
#   7  = canonical artifact mutated
set -o pipefail

REPO_ROOT="/Users/husseinhiyassat/hokom"
PYTHON="${REPO_ROOT}/.venv-py312/bin/python"
TARGET_SHA="05c6668dfb95d9238cff5df1d8bc73d0664bccb3"
OUT_DIR="${REPO_ROOT}/reports/taaqol_full_integration/c11_runtime_output"
STAMP="$(date +%Y%m%d_%H%M%S)"
SUMMARY_JSON="${REPO_ROOT}/reports/taaqol_full_integration/C11_HOKOM_EVIDENCE_PRODUCTION_CLOSURE.json"
SUMMARY_TXT="${REPO_ROOT}/reports/taaqol_full_integration/C11_HOKOM_EVIDENCE_PRODUCTION_CLOSURE.txt"

mkdir -p "${OUT_DIR}"
echo "== C11 START ${STAMP} ==" | tee "${OUT_DIR}/c11_run_${STAMP}.log"

# 1-2. Root + Python
[ "$(pwd)" = "${REPO_ROOT}" ] || cd "${REPO_ROOT}"
[ "$(pwd)" = "${REPO_ROOT}" ] || { echo "wrong root"; exit 2; }
PYVER="$(${PYTHON} -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
[ "${PYVER}" = "3.12" ] || { echo "wrong python: ${PYVER}"; exit 2; }

# 3-4. Vendor SHA + clean
VENDOR_SHA="$(git -C vendor/Taaqol-GPT rev-parse HEAD)"
[ "${VENDOR_SHA}" = "${TARGET_SHA}" ] || { echo "vendor SHA mismatch"; exit 2; }
VENDOR_DIRTY="$(git -C vendor/Taaqol-GPT status --porcelain | wc -l | tr -d ' ')"
[ "${VENDOR_DIRTY}" = "0" ] || { echo "vendor dirty"; exit 2; }

# 5. Frozen files
FROZEN=("pipeline/p3_candidate/root_profiles.py"
        "pipeline/p3_candidate/root_rules.py"
        "pipeline/p3_candidate/root_resolution.py"
        "pipeline/p3_candidate/root_resolution_orchestrator.py"
        "pipeline/p2_projection/root_projection.py")
for f in "${FROZEN[@]}"; do
  MOD="$(git diff --name-only -- "$f")"
  [ -z "${MOD}" ] || { echo "frozen file modified: $f"; exit 2; }
done

# 6. Requirement docs validator (from C10)
${PYTHON} scripts/c10_validate_requirements.py > "${OUT_DIR}/c11_req_validator_${STAMP}.json" 2>&1
[ $? -eq 0 ] || { echo "req validator failed"; exit 3; }

# 7. Ready-inventory verifier (from C10)
${PYTHON} scripts/c10_verify_ready_inventory.py > "${OUT_DIR}/c11_inventory_verifier_${STAMP}.json" 2>&1
[ $? -eq 0 ] || { echo "inventory verifier failed"; exit 3; }

# 8. Evidence-graph validator (new C11)
${PYTHON} scripts/c11_validate_evidence_graph.py > "${OUT_DIR}/c11_evidence_validator_${STAMP}.json" 2>&1
[ $? -eq 0 ] || { echo "evidence validator failed"; exit 3; }

# 9. Targeted tests (C10 + C11 closure gates + full taaqol_integration)
${PYTHON} -m pytest tests/taaqol_integration/test_c10_closure_gate.py \
                    tests/taaqol_integration/test_c11_evidence_closure.py \
                    tests/taaqol_integration/ -q \
  > "${OUT_DIR}/c11_targeted_${STAMP}.log" 2>&1
[ $? -eq 0 ] || { echo "targeted pytest failed"; exit 4; }

# 10. F0 x2
${PYTHON} -m pytest --collect-only -q > "${OUT_DIR}/c11_f0_run1_${STAMP}.txt" 2>&1
F0_R1_EXIT=$?
[ ${F0_R1_EXIT} -eq 0 ] || { echo "F0 run 1 failed"; exit 5; }
${PYTHON} -m pytest --collect-only -q > "${OUT_DIR}/c11_f0_run2_${STAMP}.txt" 2>&1
F0_R2_EXIT=$?
[ ${F0_R2_EXIT} -eq 0 ] || { echo "F0 run 2 failed"; exit 5; }

# 11. Node-ID diff
grep -E '^tests/|^tools/' "${OUT_DIR}/c11_f0_run1_${STAMP}.txt" | sort > "${OUT_DIR}/c11_f0_run1_${STAMP}.ids"
grep -E '^tests/|^tools/' "${OUT_DIR}/c11_f0_run2_${STAMP}.txt" | sort > "${OUT_DIR}/c11_f0_run2_${STAMP}.ids"
NODE_DIFF=$(diff "${OUT_DIR}/c11_f0_run1_${STAMP}.ids" "${OUT_DIR}/c11_f0_run2_${STAMP}.ids" | wc -l | tr -d ' ')
[ "${NODE_DIFF}" = "0" ] || { echo "node ID diff = ${NODE_DIFF}"; exit 5; }

# 12. F1 x2
${PYTHON} -m pytest -q -x --tb=short > "${OUT_DIR}/c11_f1_run1_${STAMP}.log" 2>&1
[ $? -eq 0 ] || { echo "F1 run 1 failed"; exit 6; }
${PYTHON} -m pytest -q -x --tb=short > "${OUT_DIR}/c11_f1_run2_${STAMP}.log" 2>&1
[ $? -eq 0 ] || { echo "F1 run 2 failed"; exit 6; }

# 13. Canonical artifact immutability
CANON_DIRTY="$(git status --porcelain reports/ayat_al_dayn_demo/ | wc -l | tr -d ' ')"
[ "${CANON_DIRTY}" = "0" ] || { echo "canonical mutated"; exit 7; }

# 14. Write summaries
${PYTHON} - "${OUT_DIR}" "${STAMP}" "${SUMMARY_JSON}" "${SUMMARY_TXT}" \
  "${OUT_DIR}/c11_f0_run1_${STAMP}.txt" "${OUT_DIR}/c11_f0_run2_${STAMP}.txt" \
  "${OUT_DIR}/c11_f1_run1_${STAMP}.log" "${OUT_DIR}/c11_f1_run2_${STAMP}.log" \
  "${OUT_DIR}/c11_req_validator_${STAMP}.json" \
  "${OUT_DIR}/c11_inventory_verifier_${STAMP}.json" \
  "${OUT_DIR}/c11_evidence_validator_${STAMP}.json" <<'PY'
import json, re, sys, datetime
OUT_DIR, STAMP, SJ, ST, F01, F02, F11, F12, REQ, INV, EV = sys.argv[1:12]

def counts(text):
    def find(pat): m = re.search(pat, text); return int(m.group(1)) if m else 0
    return {
        "passed": find(r'(\d+)\s+passed'),
        "failed": find(r'(\d+)\s+failed'),
        "skipped": find(r'(\d+)\s+skipped'),
        "warnings": find(r'(\d+)\s+warning'),
        "errors": find(r'(\d+)\s+error'),
    }
def collected(text):
    m = re.search(r'(\d+)\s+tests?\s+collected', text)
    return int(m.group(1)) if m else 0

f01 = open(F01).read(); f02 = open(F02).read()
f11 = open(F11).read(); f12 = open(F12).read()
req = json.load(open(REQ)); inv = json.load(open(INV)); ev = json.load(open(EV))

c1, c2 = collected(f01), collected(f02)
r1, r2 = counts(f11), counts(f12)

summary = {
    "phase": "HOKOM-EVIDENCE-PRODUCTION-CLOSURE-01",
    "gate": "C11",
    "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "target_taaqol_sha": "05c6668dfb95d9238cff5df1d8bc73d0664bccb3",
    "c11_exit": 0,
    "f0": {"run1_collected": c1, "run2_collected": c2, "counts_identical": c1==c2, "gate": "PASS" if c1==c2 else "FAIL"},
    "f1": {"run1": r1, "run2": r2, "counts_identical": r1==r2,
           "gate": "PASS" if (r1["failed"]==0 and r2["failed"]==0 and r1==r2) else "FAIL"},
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
    },
    "evidence": {
        "artifacts_present": ev["totals"].get("artifacts_present", 0),
        "invariants_passed": ev["totals"].get("invariants_passed", 0),
        "invariants_total": ev["totals"].get("invariants_total", 0),
    },
}
open(SJ, "w").write(json.dumps(summary, ensure_ascii=False, indent=2))
lines = [
    "== C11 HOKOM EVIDENCE PRODUCTION CLOSURE SUMMARY ==",
    f"target_taaqol_sha  = {summary['target_taaqol_sha']}",
    f"F0 collected r1/r2 = {c1} / {c2}   identical={c1==c2}",
    f"F1 r1 p/f/s/w/e = {r1['passed']}/{r1['failed']}/{r1['skipped']}/{r1['warnings']}/{r1['errors']}",
    f"F1 r2 p/f/s/w/e = {r2['passed']}/{r2['failed']}/{r2['skipped']}/{r2['warnings']}/{r2['errors']}",
    f"REQ docs = {summary['requirements']['document_count']} tech={summary['requirements']['technical_status_counts']}",
    f"READY unwired R/I = {summary['ready_inventory']['READY_RUNTIME_UNWIRED_COUNT']} / {summary['ready_inventory']['READY_INTEGRATION_UNWIRED_COUNT']}",
    f"EVIDENCE invariants = {summary['evidence']['invariants_passed']} / {summary['evidence']['invariants_total']}",
    "C11_EXIT = 0",
]
open(ST, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
PY

echo "== C11 END OK ==" | tee -a "${OUT_DIR}/c11_run_${STAMP}.log"
exit 0
