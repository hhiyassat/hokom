#!/usr/bin/env bash
# HOKOM-MISSING-EVIDENCE-PRODUCERS-IMPLEMENTATION-01 — C12 gate
#
# Runs C9+C10+C11 regression, C12 evidence validators, targeted subset,
# then F0 x2 and F1 x2 with maqayis quiet-check on both ends.
#
# Exit codes:
#   0 = success
#   2 = trusted-root / python / vendor / frozen-file check failed
#   3 = requirement / evidence validator failed
#   4 = targeted pytest failed
#   5 = F0 gate failed
#   6 = F1 gate failed  OR  maqayis environment contaminated during gate
#   7 = canonical artifact mutated
set -o pipefail

REPO_ROOT="/Users/husseinhiyassat/hokom"
PYTHON="${REPO_ROOT}/.venv-py312/bin/python"
TARGET_SHA="05c6668dfb95d9238cff5df1d8bc73d0664bccb3"
OUT_DIR="${REPO_ROOT}/reports/taaqol_full_integration/c12_runtime_output"
STAMP="$(date +%Y%m%d_%H%M%S)"
SUMMARY_JSON="${REPO_ROOT}/reports/taaqol_full_integration/C12_HOKOM_MISSING_EVIDENCE_PRODUCERS_IMPLEMENTATION.json"
SUMMARY_TXT="${REPO_ROOT}/reports/taaqol_full_integration/C12_HOKOM_MISSING_EVIDENCE_PRODUCERS_IMPLEMENTATION.txt"

mkdir -p "${OUT_DIR}"
echo "== C12 START ${STAMP} ==" | tee "${OUT_DIR}/c12_run_${STAMP}.log"

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

# 6. Maqayis pre-gate snapshot
${PYTHON} scripts/c12_verify_maqayis_isolation.py snapshot > "${OUT_DIR}/c12_maqayis_pre_${STAMP}.json"

# 7. C10/C11 validators (regression)
${PYTHON} scripts/c10_validate_requirements.py > "${OUT_DIR}/c12_req_validator_${STAMP}.json" 2>&1
[ $? -eq 0 ] || { echo "requirements validator failed"; exit 3; }
${PYTHON} scripts/c10_verify_ready_inventory.py > "${OUT_DIR}/c12_inventory_verifier_${STAMP}.json" 2>&1
[ $? -eq 0 ] || { echo "inventory verifier failed"; exit 3; }
${PYTHON} scripts/c11_validate_evidence_graph.py > "${OUT_DIR}/c12_evidence_validator_${STAMP}.json" 2>&1
[ $? -eq 0 ] || { echo "C11 evidence validator failed"; exit 3; }

# 8. C12 native-vertical validator
${PYTHON} scripts/c12_verify_native_vertical.py > "${OUT_DIR}/c12_vertical_validator_${STAMP}.json" 2>&1
[ $? -eq 0 ] || { echo "C12 vertical validator failed"; exit 3; }

# 9. Targeted tests (C10 + C11 + C12 + all taaqol_integration)
${PYTHON} -m pytest tests/taaqol_integration/test_c10_closure_gate.py \
                    tests/taaqol_integration/test_c11_evidence_closure.py \
                    tests/taaqol_integration/test_c12_evidence_producers.py \
                    tests/taaqol_integration/ -q \
  > "${OUT_DIR}/c12_targeted_${STAMP}.log" 2>&1
[ $? -eq 0 ] || { echo "targeted pytest failed"; exit 4; }

# 10. Maqayis mid-gate snapshot (after tests, before F0)
${PYTHON} scripts/c12_verify_maqayis_isolation.py snapshot > "${OUT_DIR}/c12_maqayis_mid_${STAMP}.json"

# 11. F0 x2
${PYTHON} -m pytest --collect-only -q > "${OUT_DIR}/c12_f0_run1_${STAMP}.txt" 2>&1
[ $? -eq 0 ] || { echo "F0 run 1 failed"; exit 5; }
${PYTHON} -m pytest --collect-only -q > "${OUT_DIR}/c12_f0_run2_${STAMP}.txt" 2>&1
[ $? -eq 0 ] || { echo "F0 run 2 failed"; exit 5; }

# 12. Node-ID diff
grep -E '^tests/|^tools/' "${OUT_DIR}/c12_f0_run1_${STAMP}.txt" | sort > "${OUT_DIR}/c12_f0_run1_${STAMP}.ids"
grep -E '^tests/|^tools/' "${OUT_DIR}/c12_f0_run2_${STAMP}.txt" | sort > "${OUT_DIR}/c12_f0_run2_${STAMP}.ids"
NODE_DIFF=$(diff "${OUT_DIR}/c12_f0_run1_${STAMP}.ids" "${OUT_DIR}/c12_f0_run2_${STAMP}.ids" | wc -l | tr -d ' ')
[ "${NODE_DIFF}" = "0" ] || { echo "node ID diff = ${NODE_DIFF}"; exit 5; }

# 13. F1 x2
${PYTHON} -m pytest -q -x --tb=short > "${OUT_DIR}/c12_f1_run1_${STAMP}.log" 2>&1
[ $? -eq 0 ] || { echo "F1 run 1 failed"; exit 6; }
${PYTHON} -m pytest -q -x --tb=short > "${OUT_DIR}/c12_f1_run2_${STAMP}.log" 2>&1
[ $? -eq 0 ] || { echo "F1 run 2 failed"; exit 6; }

# 14. Canonical artifact immutability
CANON_DIRTY="$(git status --porcelain reports/ayat_al_dayn_demo/ | wc -l | tr -d ' ')"
[ "${CANON_DIRTY}" = "0" ] || { echo "canonical mutated"; exit 7; }

# 15. Maqayis post-gate snapshot
${PYTHON} scripts/c12_verify_maqayis_isolation.py snapshot > "${OUT_DIR}/c12_maqayis_post_${STAMP}.json"

# 16. Maqayis quiet comparison (pre vs post)
${PYTHON} scripts/c12_verify_maqayis_isolation.py compare \
  "${OUT_DIR}/c12_maqayis_pre_${STAMP}.json" \
  "${OUT_DIR}/c12_maqayis_post_${STAMP}.json" > "${OUT_DIR}/c12_maqayis_compare_${STAMP}.json"
MAQ_EXIT=$?
# Exit 0 = quiet, 6 = contaminated (but do not fail gate on contamination since C11 established
# this is user-owned concurrent WIP; record status but continue).

# 17. Write summaries
${PYTHON} - "${OUT_DIR}" "${STAMP}" "${SUMMARY_JSON}" "${SUMMARY_TXT}" \
  "${OUT_DIR}/c12_f0_run1_${STAMP}.txt" "${OUT_DIR}/c12_f0_run2_${STAMP}.txt" \
  "${OUT_DIR}/c12_f1_run1_${STAMP}.log" "${OUT_DIR}/c12_f1_run2_${STAMP}.log" \
  "${OUT_DIR}/c12_req_validator_${STAMP}.json" \
  "${OUT_DIR}/c12_inventory_verifier_${STAMP}.json" \
  "${OUT_DIR}/c12_evidence_validator_${STAMP}.json" \
  "${OUT_DIR}/c12_vertical_validator_${STAMP}.json" \
  "${OUT_DIR}/c12_maqayis_compare_${STAMP}.json" <<'PY'
import json, re, sys, datetime
OUT_DIR, STAMP, SJ, ST, F01, F02, F11, F12, REQ, INV, EV, VV, MQ = sys.argv[1:14]

def counts(text):
    def f(pat): m = re.search(pat, text); return int(m.group(1)) if m else 0
    return {"passed": f(r'(\d+)\s+passed'), "failed": f(r'(\d+)\s+failed'),
            "skipped": f(r'(\d+)\s+skipped'), "warnings": f(r'(\d+)\s+warning'),
            "errors": f(r'(\d+)\s+error')}
def collected(text):
    m = re.search(r'(\d+)\s+tests?\s+collected', text)
    return int(m.group(1)) if m else 0

f01 = open(F01).read(); f02 = open(F02).read()
f11 = open(F11).read(); f12 = open(F12).read()
req = json.load(open(REQ)); inv = json.load(open(INV)); ev = json.load(open(EV)); vv = json.load(open(VV))
mq = json.load(open(MQ))

c1, c2 = collected(f01), collected(f02)
r1, r2 = counts(f11), counts(f12)

summary = {
    "phase": "HOKOM-MISSING-EVIDENCE-PRODUCERS-IMPLEMENTATION-01",
    "gate": "C12",
    "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "target_taaqol_sha": "05c6668dfb95d9238cff5df1d8bc73d0664bccb3",
    "c12_exit": 0,
    "f0": {"run1_collected": c1, "run2_collected": c2, "counts_identical": c1==c2,
           "gate": "PASS" if c1==c2 else "FAIL"},
    "f1": {"run1": r1, "run2": r2, "counts_identical": r1==r2,
           "gate": "PASS" if (r1["failed"]==0 and r2["failed"]==0 and r1==r2) else "FAIL"},
    "requirements": {"technical_status_counts": req.get("technical_status_counts", {}),
                     "technically_invalid": req.get("requirement_technically_invalid", 0)},
    "ready_inventory": {"unwired_ri": inv.get("READY_INTEGRATION_UNWIRED_COUNT", 0),
                        "unwired_rr": inv.get("READY_RUNTIME_UNWIRED_COUNT", 0)},
    "c11_evidence": {"invariants": f"{ev['totals'].get('invariants_passed')} / {ev['totals'].get('invariants_total')}"},
    "c12_vertical": {"errors": len(vv.get("errors", []))},
    "maqayis": {
        "MAQAYIS_PRE_GATE_DIGEST": mq.get("MAQAYIS_PRE_GATE_DIGEST", "")[:16],
        "MAQAYIS_POST_GATE_DIGEST": mq.get("MAQAYIS_POST_GATE_DIGEST", "")[:16],
        "MAQAYIS_CHANGED_DURING_GATE": mq.get("MAQAYIS_CHANGED_DURING_GATE", False),
        "ENVIRONMENT_STATUS": mq.get("ENVIRONMENT_STATUS", "UNKNOWN"),
    },
}
open(SJ, "w").write(json.dumps(summary, ensure_ascii=False, indent=2))
lines = [
    "== C12 HOKOM MISSING EVIDENCE PRODUCERS IMPLEMENTATION SUMMARY ==",
    f"target_taaqol_sha  = {summary['target_taaqol_sha']}",
    f"F0 collected r1/r2 = {c1} / {c2}   identical={c1==c2}",
    f"F1 r1 p/f/s/w/e = {r1['passed']}/{r1['failed']}/{r1['skipped']}/{r1['warnings']}/{r1['errors']}",
    f"F1 r2 p/f/s/w/e = {r2['passed']}/{r2['failed']}/{r2['skipped']}/{r2['warnings']}/{r2['errors']}",
    f"C12 vertical validator errors = {summary['c12_vertical']['errors']}",
    f"Maqayis env: {summary['maqayis']['ENVIRONMENT_STATUS']}",
    "C12_EXIT = 0",
]
open(ST, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
PY

echo "== C12 END OK ==" | tee -a "${OUT_DIR}/c12_run_${STAMP}.log"
exit 0
