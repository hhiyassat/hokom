#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# scripts/run_taaqol_full_verification.sh
#
# One-shot idempotent verification for the Full-Target Taaqol pipeline:
#   1. Runs targeted unit tests.
#   2. Runs pytest --collect-only on tests/taaqol_integration/ to catch
#      import errors early.
#   3. Executes the Arabic HTML + JSON demo.
#   4. Prints the captured counts.
#
# Uses only the venv Python (.venv-py312/bin/python).
# No commits, no pushes, no vendor patches.
# ---------------------------------------------------------------------------
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${REPO_ROOT}/.venv-py312/bin/python"

if [[ ! -x "${PY}" ]]; then
    echo "ERROR: venv Python not found at ${PY}" >&2
    exit 2
fi

echo "==> [1/4] targeted tests"
"${PY}" -m pytest -x \
    tests/taaqol_integration/test_full_target_orchestrator.py \
    tests/taaqol_integration/test_constitutional_amendment_01.py \
    tests/taaqol_integration/test_forbidden_leaps.py \
    tests/taaqol_integration/test_architecture_import_boundaries.py \
    2>&1 | tail -60

echo ""
echo "==> [2/4] pytest --collect-only tests/taaqol_integration/"
"${PY}" -m pytest --collect-only -q tests/taaqol_integration/ 2>&1 | tail -20

echo ""
echo "==> [3/4] demo: --format html --taaqol --lang ar"
HTML_STDERR="$(mktemp)"
"${PY}" scripts/demo_ayat_al_dayn.py --format html --taaqol --lang ar 2>"${HTML_STDERR}" >/dev/null || true
tail -60 "${HTML_STDERR}"

echo ""
echo "==> [4/4] demo: --format json --taaqol --lang ar"
JSON_STDERR="$(mktemp)"
"${PY}" scripts/demo_ayat_al_dayn.py --format json --taaqol --lang ar 2>"${JSON_STDERR}" >/dev/null || true
tail -60 "${JSON_STDERR}"

echo ""
echo "==> outputs under reports/ayat_al_dayn_demo/"
ls -la reports/ayat_al_dayn_demo/ 2>/dev/null | tail -20 || true

echo ""
echo "==> DONE."
