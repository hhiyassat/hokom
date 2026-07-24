#!/usr/bin/env bash
# HOKOM-CANONICAL-FINAL-AUDIT-RUNNER-HARDENING-01
# HOKOM-CANONICAL-AUDIT-RUNNER-BOOTSTRAP-CLOSURE-01
# HOKOM-CANONICAL-AUDIT-NONMUTATING-RUNNER-CORRECTION-01
# Canonical closure audit — must run on macOS with .venv-py312
# Usage: cd /path/to/hokom && bash scripts/run_canonical_final_audit.sh
# Exits 0 only for VERIFIED_CLOSED; exits nonzero for any OPEN condition.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"
VENV="$REPO_DIR/.venv-py312/bin/python"
LOGS="$REPO_DIR/reports/canonical_gate"
mkdir -p "$LOGS"

# LINGUISTIC_BASE_HEAD: last linguistic commit — immutable
LINGUISTIC_BASE_HEAD="2e2a3ac71a00ad520675c91e13904903f573034b"
# AUDITED_HEAD: computed dynamically — the actual HEAD being audited
AUDITED_HEAD="$(git rev-parse HEAD)"

# ── verdict flags ────────────────────────────────────────────────────────────
HEAD_OK=0; INITIAL_TREE_CLEAN=0; DARWIN_OK=0; PYTHON_3124_OK=0; VENV_OK=0
RUNTIME_CONTRACT_EXIT=1; GOLDEN_RULES_INTEGRITY_EXIT=1; GOLD_MANIFEST_INTEGRITY_EXIT=1
PROBE_EXIT=1; CSV_VERIFIER_EXIT=1; CSV_IN_MEMORY_DIVERGENCES=-1
RUN1_COLLECT_EXIT=1; RUN2_COLLECT_EXIT=1; NODE_IDS_EQUAL=0
RUN1_COLLECTED_COUNT=0; RUN2_COLLECTED_COUNT=0
RUN1_EXIT=1; RUN2_EXIT=1; TREE_STABLE_BETWEEN_RUNS=0
CLOSURE_GATE_EXIT=1; ALL_REQUIRED_METRICS_PRESENT=0; ALL_CLOSURE_METRICS_ZERO=0
ARTIFACT_BINDING_READY=0

OPEN_REASONS=()
fail_flag() { OPEN_REASONS+=("$1"); echo "FAIL: $1"; }

# Probe runner lives outside the repository in a temp file; cleaned up on any exit.
PROBE_SCRIPT="$(mktemp /tmp/hokom_probe_XXXXXX.py)"
trap 'rm -f "$PROBE_SCRIPT"' EXIT

# ── §1 Repository identity ───────────────────────────────────────────────────
START_HEAD="$AUDITED_HEAD"
echo "START_HEAD=$START_HEAD"
echo "LINGUISTIC_BASE_HEAD=$LINGUISTIC_BASE_HEAD"
echo "AUDITED_HEAD=$AUDITED_HEAD"

# HEAD must be a descendant of LINGUISTIC_BASE_HEAD
if git merge-base --is-ancestor "$LINGUISTIC_BASE_HEAD" HEAD 2>/dev/null; then
    # Only governance runner files may differ from the linguistic baseline
    DIFF_FROM_BASE="$(git diff "$LINGUISTIC_BASE_HEAD"..HEAD --name-only | sort)"
    ALLOWED_DIFF="$(printf 'scripts/run_canonical_final_audit.sh\ntests/shell/test_audit_runner.sh')"
    if [[ "$DIFF_FROM_BASE" == "$ALLOWED_DIFF" ]]; then
        HEAD_OK=1
        echo "HEAD_OK=1 (descendant of LINGUISTIC_BASE_HEAD; diff=$DIFF_FROM_BASE)"
    else
        fail_flag "HEAD_DIFF_VIOLATION: files changed beyond governance runner: $DIFF_FROM_BASE"
    fi
else
    fail_flag "HEAD_NOT_DESCENDANT_OF_LINGUISTIC_BASE: $AUDITED_HEAD is not after $LINGUISTIC_BASE_HEAD"
fi

# Require exactly clean working tree; caller must remove .DS_Store beforehand
DIRTY="$(git status --porcelain --untracked-files=all 2>&1)"
if [[ -z "$DIRTY" ]]; then
    INITIAL_TREE_CLEAN=1
else
    fail_flag "DIRTY_TREE"
    echo "$DIRTY"
    echo "REMEDIATION: git clean -fdx for untracked; add .DS_Store to .gitignore or remove before audit."
fi

# ── §2 Canonical environment ─────────────────────────────────────────────────
if [[ "$(uname -s)" == "Darwin" ]]; then DARWIN_OK=1
else fail_flag "NOT_DARWIN: uname=$(uname -s)"; fi

if [[ ! -x "$VENV" ]]; then
    fail_flag "VENV_NOT_FOUND: $VENV"
else
    PY_VER="$("$VENV" -c 'import sys; v=sys.version_info; print(f"{v.major}.{v.minor}.{v.micro}")')"
    PY_EXE="$("$VENV" -c 'import sys; print(sys.executable)')"
    PY_PFX="$("$VENV" -c 'import sys; print(sys.prefix)')"
    if [[ "$PY_VER" == "3.12.4" ]]; then PYTHON_3124_OK=1
    else fail_flag "PYTHON_VERSION: got=$PY_VER expected=3.12.4"; fi
    if [[ "$PY_PFX" == *".venv-py312" ]]; then VENV_OK=1
    else fail_flag "VENV_PREFIX: exe=$PY_EXE prefix=$PY_PFX"; fi
fi

# Abort early: no point running tests on wrong env
if [[ "$HEAD_OK" == 0 || "$INITIAL_TREE_CLEAN" == 0 || "$DARWIN_OK" == 0 \
   || "$PYTHON_3124_OK" == 0 || "$VENV_OK" == 0 ]]; then
    echo "ABORT: pre-flight failed — fix above and re-run"; exit 1
fi

# ── §2b Runtime contract tests ───────────────────────────────────────────────
echo "--- §2b runtime contract ---"
if "$VENV" -m pytest tests/governance/test_canonical_runtime_contract.py \
       -q --tb=short 2>&1 | tee "$LOGS/runtime_contract.log"; then
    RUNTIME_CONTRACT_EXIT=0
else
    RUNTIME_CONTRACT_EXIT=$?
    fail_flag "RUNTIME_CONTRACT_EXIT=$RUNTIME_CONTRACT_EXIT"
fi

# ── §3 Integrity checks (fatal) ──────────────────────────────────────────────
echo "--- §3 digest integrity ---"
if "$VENV" -c "
import sys; sys.path.insert(0,'.')
from pipeline.governance.golden_rules_guard import verify_golden_rules_integrity
ok, msg = verify_golden_rules_integrity()
print('GOLDEN_RULES_INTEGRITY:', 'OK' if ok else 'FAIL', msg)
sys.exit(0 if ok else 1)
" 2>&1 | tee "$LOGS/golden_rules_integrity.log"; then
    GOLDEN_RULES_INTEGRITY_EXIT=0
else
    GOLDEN_RULES_INTEGRITY_EXIT=$?
    fail_flag "GOLDEN_RULES_INTEGRITY_EXIT=$GOLDEN_RULES_INTEGRITY_EXIT"
fi

if "$VENV" -c "
import sys; sys.path.insert(0,'.')
from pipeline.governance.gold_manifest import MANIFEST_DIGEST, _compute_digest_for, CORPUS_GOLD
c = _compute_digest_for(CORPUS_GOLD)
match = (c == MANIFEST_DIGEST)
print('GOLD_MANIFEST_INTEGRITY:', 'OK' if match else 'FAIL', f'stored={MANIFEST_DIGEST} computed={c}')
sys.exit(0 if match else 1)
" 2>&1 | tee "$LOGS/gold_manifest_integrity.log"; then
    GOLD_MANIFEST_INTEGRITY_EXIT=0
else
    GOLD_MANIFEST_INTEGRITY_EXIT=$?
    fail_flag "GOLD_MANIFEST_INTEGRITY_EXIT=$GOLD_MANIFEST_INTEGRITY_EXIT"
fi

# ── §4 Live probes (17 tokens) ───────────────────────────────────────────────
echo "--- §4 live probes ---"
cat > "$PROBE_SCRIPT" << 'PROBE_EOF'
import sys, os
sys.path.insert(0, os.getcwd())
from hokom_pipeline import hokom

def root_str(r):
    fr = r.get('final_root') or r.get('canonical_root')
    return ''.join(fr) if isinstance(fr, (tuple, list)) else (fr or '')

def cra_ff(r):
    cra = r.get('cra_result')
    return getattr(cra, 'form_family', None) if cra else None

def check(surface, r, **expects):
    fails = []
    field_map = {
        'wc': 'word_class', 'ta': 'tense_aspect', 'mood': 'mood',
        'n': 'number', 'p': 'person', 'g': 'gender', 'voice': 'voice',
        'sc': 'word_class_subclass',
    }
    for k, v in expects.items():
        if k == 'jamid':
            got = r.get('jamid_verdict') or r.get('boundary_type')
            if got != v: fails.append(f'jamid={got!r}!={v!r}')
        elif k == 'cra':
            got = cra_ff(r)
            if got != v: fails.append(f'cra={got!r}!={v!r}')
        elif k == 'root':
            got = root_str(r)
            if got != v: fails.append(f'root={got!r}!={v!r}')
        elif k in field_map:
            got = r.get(field_map[k])
            if got != v: fails.append(f'{k}={got!r}!={v!r}')
    return fails

all_pass = True
results = []

# Non-context tokens: direct hokom() calls with full field checks
DIRECT = [
    ('اللَّهُ',         dict(wc=None, jamid='JAMID_AALAM_BOUNDARY')),
    ('اللَّهَ',         dict(wc=None, jamid='JAMID_AALAM_BOUNDARY')),
    ('اللَّهِ',         dict(wc=None, jamid='JAMID_AALAM_BOUNDARY')),
    ('وَاللَّهُ',        dict(wc=None, jamid='JAMID_AALAM_BOUNDARY')),
    ('سَيَسْتَغْفِرُونَ', dict(wc='FI3L', ta='IMPERFECT', cra='FORM_X', root='غفر', p='3', n='PL')),
    ('يَسْتَغْفِرُونَ',  dict(wc='FI3L', ta='IMPERFECT', cra='FORM_X', root='غفر', p='3', n='PL')),
    ('وَاسْتَشْهِدُوا',  dict(wc='FI3L', ta='IMPERATIVE', cra='FORM_X', root='شهد', p='2', n='PL')),
    ('فَاكْتُبُوهُ',     dict(wc='FI3L', ta='IMPERATIVE', cra='FORM_I', root='كتب', p='2', n='PL')),
    ('وَاتَّقُوا',       dict(wc='FI3L', ta='IMPERATIVE', cra='FORM_VIII', p='2', n='PL')),
    ('وَلْيَتَّقِ',      dict(wc='FI3L', ta='IMPERFECT', cra='FORM_VIII', mood='JUSSIVE', p='3', n='SG')),
    ('أَجَلٍ',           dict(wc='ISM', sc='LEXICAL_NOUN')),
    ('يَسْتَطِيعُ',     dict(wc='FI3L', ta='IMPERFECT', cra='FORM_X', mood='INDICATIVE', n='SG')),
    ('يَكُونَا',         dict(wc='FI3L', ta='IMPERFECT', n='DU', mood='SUBJUNCTIVE')),
    ('تُدِيرُونَهَا',    dict(wc='FI3L', ta='IMPERFECT', cra='FORM_IV', voice='ACTIVE', root='دور', p='2', n='PL')),
]
for surface, expects in DIRECT:
    r = hokom(surface)
    fails = check(surface, r, **expects)
    status = 'PASS' if not fails else ('FAIL: ' + '; '.join(fails))
    print(f'  PROBE {surface}: {status}')
    results.append((surface, not fails))
    if fails: all_pass = False

# Context-dependent tokens: use sequential live runner
# verify correlated-ambiguity bundles AND sequential 3FS resolution
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location(
    'demo_ayat_al_dayn',
    pathlib.Path(os.getcwd()) / 'scripts' / 'demo_ayat_al_dayn.py'
)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
metrics = demo.compute_live_metrics()

CONTEXT_TOKENS = ['تَضِلَّ', 'فَتُذَكِّرَ', 'تَكُونَ']
for surface in CONTEXT_TOKENS:
    r = hokom(surface)
    cands = r.get('ambiguity_candidates') or []
    has_3fs_bundle = any(
        isinstance(c, dict) and c.get('reading') == '3FS'
        for c in cands
    )
    if not has_3fs_bundle:
        print(f'  PROBE {surface}: FAIL: missing 3FS dict bundle in ambiguity_candidates')
        all_pass = False
    else:
        print(f'  PROBE {surface}: PASS (correlated-ambiguity bundle, 3FS candidate present)')
    results.append((surface, has_3fs_bundle))

# Verify sequential runner resolved at least one 3FS context
resolved = metrics.get('LIVE_CONTEXT_3FS_RESOLVED', 0)
print(f'  SEQUENTIAL_CONTEXT_3FS_RESOLVED={resolved}')
if resolved == 0:
    print('  FAIL: sequential runner resolved 0 context-dependent 3FS tokens')
    all_pass = False

print()
print(f'PROBE_VERDICT: {"ALL_PASS" if all_pass else "FAILURES_PRESENT"} ({sum(1 for _,ok in results if ok)}/{len(results)} tokens)')
raise SystemExit(0 if all_pass else 1)
PROBE_EOF

if "$VENV" "$PROBE_SCRIPT" 2>&1 | tee "$LOGS/probe.log"; then
    PROBE_EXIT=0
else
    PROBE_EXIT=$?
    fail_flag "PROBE_EXIT=$PROBE_EXIT"
fi

# ── §5 Canonical artifact verification (non-mutating) ────────────────────────
# HOKOM-CANONICAL-AUDIT-NONMUTATING-RUNNER-CORRECTION-01
# Do NOT delete or regenerate committed artifacts. JSON and HTML carry
# a timestamp and are non-deterministic across runs; only the CSV SHA
# is bound and verified. The working tree must remain clean throughout.
echo "--- §5 canonical artifact verification (non-mutating) ---"
REPORT_DIR="$REPO_DIR/reports/ayat_al_dayn_demo"
CSV_FILE="$REPORT_DIR/ayat_al_dayn_results.csv"
JSON_FILE="$REPORT_DIR/ayat_al_dayn_results_full.json"
HTML_FILE="$REPORT_DIR/ayat_al_dayn_manager_report.html"
CSV_SHA=""; JSON_SHA="(non-deterministic)"; HTML_SHA="(non-deterministic)"

if [[ ! -f "$CSV_FILE" ]]; then
    fail_flag "ARTIFACT_MISSING: $CSV_FILE"
else
    CSV_SHA="$("$VENV" -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('$CSV_FILE').read_bytes()).hexdigest())")"
    echo "CSV_SHA256=sha256:$CSV_SHA"
    EXPECTED_CSV="5e673089f33e42309a66ded1816fffb9098227f1f86bb35c5faa33349dd47d84"
    if [[ "$CSV_SHA" == "$EXPECTED_CSV" ]]; then
        echo "CSV_DETERMINISM=OK"
        ARTIFACT_BINDING_READY=1
    else
        fail_flag "CSV_SHA_MISMATCH: got=$CSV_SHA expected=$EXPECTED_CSV"
    fi
fi

# ── §6 Independent CSV verifier (separate process) ───────────────────────────
echo "--- §6 CSV verifier ---"
if "$VENV" -c "
import sys, os, csv
sys.path.insert(0, os.getcwd())
import importlib.util, pathlib

spec = importlib.util.spec_from_file_location(
    'demo_ayat_al_dayn', pathlib.Path('scripts/demo_ayat_al_dayn.py'))
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

metrics = demo.compute_live_metrics()
divergences = metrics.get('CSV_IN_MEMORY_DIVERGENCES', -1)
print(f'CSV_IN_MEMORY_DIVERGENCES={divergences}')

# Row count check
with open('$CSV_FILE', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
print(f'CSV_ROW_COUNT={len(rows)}')

if len(rows) != 129:
    print(f'FAIL: expected 129 rows, got {len(rows)}')
    sys.exit(1)
if divergences != 0:
    print(f'FAIL: CSV_IN_MEMORY_DIVERGENCES={divergences} (expected 0)')
    sys.exit(1)
print('CSV_VERIFIER=OK')
sys.exit(0)
" 2>&1 | tee "$LOGS/csv_verifier.log"; then
    CSV_VERIFIER_EXIT=0
    CSV_IN_MEMORY_DIVERGENCES=0
else
    CSV_VERIFIER_EXIT=$?
    fail_flag "CSV_VERIFIER_EXIT=$CSV_VERIFIER_EXIT"
    CSV_IN_MEMORY_DIVERGENCES="$(grep 'CSV_IN_MEMORY_DIVERGENCES=' "$LOGS/csv_verifier.log" | tail -1 | cut -d= -f2 || echo -1)"
fi

# ── §9 Semantic tree fingerprint (before RUN1) ───────────────────────────────
semantic_fingerprint() {
    git ls-files -- pipeline/ tests/ golden_rules.md vendor/ \
        | sort | xargs -d'\n' sha256sum 2>/dev/null | sha256sum | awk '{print $1}'
}
FINGERPRINT_PRE="$(semantic_fingerprint)"

# ── §8 Collect RUN1 node IDs ─────────────────────────────────────────────────
echo "--- §8 collect RUN1 ---"
if "$VENV" -m pytest tests/ --import-mode=importlib --collect-only -q \
   2>"$LOGS/collect1.err" | grep "::" | sort > "$LOGS/run1_nodes.txt"; then
    RUN1_COLLECT_EXIT=0
    RUN1_COLLECTED_COUNT="$(wc -l < "$LOGS/run1_nodes.txt" | tr -d ' ')"
    echo "RUN1_COLLECT_EXIT=0  RUN1_COLLECTED_COUNT=$RUN1_COLLECTED_COUNT"
else
    RUN1_COLLECT_EXIT=$?
    fail_flag "RUN1_COLLECT_EXIT=$RUN1_COLLECT_EXIT ($(cat "$LOGS/collect1.err" | tail -3))"
fi

# ── §7 Full suite RUN1 ───────────────────────────────────────────────────────
echo "--- §7 full suite RUN1 ---"
if "$VENV" -m pytest tests/ --import-mode=importlib -q --tb=line \
   2>&1 | tee "$LOGS/run1.log"; then
    RUN1_EXIT=0
else
    RUN1_EXIT=$?
    fail_flag "RUN1_EXIT=$RUN1_EXIT"
fi
echo "RUN1_EXIT=$RUN1_EXIT"

# ── §9 Tree fingerprint between runs ────────────────────────────────────────
FINGERPRINT_MID="$(semantic_fingerprint)"
if [[ "$FINGERPRINT_PRE" == "$FINGERPRINT_MID" ]]; then
    echo "TREE_STABLE_AFTER_RUN1=OK"
else
    fail_flag "TREE_MUTATED_AFTER_RUN1"
fi

# ── §8 Collect RUN2 node IDs ─────────────────────────────────────────────────
echo "--- §8 collect RUN2 ---"
if "$VENV" -m pytest tests/ --import-mode=importlib --collect-only -q \
   2>"$LOGS/collect2.err" | grep "::" | sort > "$LOGS/run2_nodes.txt"; then
    RUN2_COLLECT_EXIT=0
    RUN2_COLLECTED_COUNT="$(wc -l < "$LOGS/run2_nodes.txt" | tr -d ' ')"
    echo "RUN2_COLLECT_EXIT=0  RUN2_COLLECTED_COUNT=$RUN2_COLLECTED_COUNT"
else
    RUN2_COLLECT_EXIT=$?
    fail_flag "RUN2_COLLECT_EXIT=$RUN2_COLLECT_EXIT"
fi

if [[ "$RUN1_COLLECT_EXIT" == 0 && "$RUN2_COLLECT_EXIT" == 0 ]]; then
    if diff -q "$LOGS/run1_nodes.txt" "$LOGS/run2_nodes.txt" > /dev/null; then
        NODE_IDS_EQUAL=1
        echo "NODE_IDS_EQUAL=1  COUNT=$RUN1_COLLECTED_COUNT"
    else
        fail_flag "NODE_IDS_DIFFER"
        diff "$LOGS/run1_nodes.txt" "$LOGS/run2_nodes.txt" | head -20
    fi
fi

# ── §7 Full suite RUN2 ───────────────────────────────────────────────────────
echo "--- §7 full suite RUN2 ---"
if "$VENV" -m pytest tests/ --import-mode=importlib -q --tb=line \
   2>&1 | tee "$LOGS/run2.log"; then
    RUN2_EXIT=0
else
    RUN2_EXIT=$?
    fail_flag "RUN2_EXIT=$RUN2_EXIT"
fi
echo "RUN2_EXIT=$RUN2_EXIT"

# ── §9 Tree fingerprint after RUN2 ───────────────────────────────────────────
FINGERPRINT_POST="$(semantic_fingerprint)"
if [[ "$FINGERPRINT_PRE" == "$FINGERPRINT_POST" ]]; then
    TREE_STABLE_BETWEEN_RUNS=1
    echo "TREE_STABLE_BETWEEN_RUNS=1"
else
    fail_flag "TREE_MUTATED_BETWEEN_RUNS"
fi

# ── §10 Closure gate (safe under set -e) ────────────────────────────────────
echo "--- §10 closure gate ---"
if "$VENV" scripts/run_live_gold_closure_gate.py --report 2>&1 | tee "$LOGS/gate.log"; then
    CLOSURE_GATE_EXIT=0
else
    CLOSURE_GATE_EXIT=$?
    fail_flag "CLOSURE_GATE_EXIT=$CLOSURE_GATE_EXIT"
fi
echo "CLOSURE_GATE_EXIT=$CLOSURE_GATE_EXIT"

# Verify each required metric appears exactly once
REQUIRED_METRICS=(
    LIVE_GOLD_TOKEN_MISMATCHES
    LIVE_FORM_FAMILY_MISMATCHES
    KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS
    LIVE_PERSON_NUMBER_GENDER_MISMATCHES
    LIVE_VOICE_MISMATCHES
    LIVE_CONTEXT_MOOD_MISMATCHES
    LIVE_UNCORRELATED_AMBIGUITY
    UNJUSTIFIED_WORD_CLASS_NOT_OPENED
    LIVE_NONVERBS_AS_VERBS
    LIVE_JAMID_BOUNDARY_VIOLATIONS
)
ALL_METRICS_OK=1
ALL_ZERO=1
for METRIC in "${REQUIRED_METRICS[@]}"; do
    COUNT="$(grep -c "$METRIC" "$LOGS/gate.log" 2>/dev/null || echo 0)"
    if [[ "$COUNT" != 1 ]]; then
        fail_flag "METRIC_NOT_EXACTLY_ONCE: $METRIC appears $COUNT times"
        ALL_METRICS_OK=0
    fi
    VAL="$(grep "$METRIC" "$LOGS/gate.log" | grep -oP '= \K\d+' || echo -1)"
    if [[ "$VAL" != "0" ]]; then ALL_ZERO=0; fi
done
[[ "$ALL_METRICS_OK" == 1 ]] && ALL_REQUIRED_METRICS_PRESENT=1
[[ "$ALL_ZERO" == 1 ]] && ALL_CLOSURE_METRICS_ZERO=1
[[ "$ALL_METRICS_OK" != 1 ]] && fail_flag "ALL_REQUIRED_METRICS_PRESENT=0"
[[ "$ALL_ZERO" != 1 ]] && fail_flag "ALL_CLOSURE_METRICS_ZERO=0"

# ── §11 Final verdict conjunction ─────────────────────────────────────────────
FINAL_HEAD="$(git rev-parse HEAD)"
echo "FINAL_HEAD=$FINAL_HEAD"
echo "LINGUISTIC_BASE_HEAD=$LINGUISTIC_BASE_HEAD"
echo "AUDITED_HEAD=$AUDITED_HEAD"
[[ "$FINAL_HEAD" != "$AUDITED_HEAD" ]] && fail_flag "HEAD_CHANGED_DURING_AUDIT: was=$AUDITED_HEAD now=$FINAL_HEAD"

echo ""
echo "=== VERDICT CONJUNCTION ==="
printf "  HEAD_OK=%s\n  INITIAL_TREE_CLEAN=%s\n  DARWIN_OK=%s\n" \
    "$HEAD_OK" "$INITIAL_TREE_CLEAN" "$DARWIN_OK"
printf "  PYTHON_3124_OK=%s\n  VENV_OK=%s\n  RUNTIME_CONTRACT_EXIT=%s\n" \
    "$PYTHON_3124_OK" "$VENV_OK" "$RUNTIME_CONTRACT_EXIT"
printf "  GOLDEN_RULES_INTEGRITY_EXIT=%s\n  GOLD_MANIFEST_INTEGRITY_EXIT=%s\n" \
    "$GOLDEN_RULES_INTEGRITY_EXIT" "$GOLD_MANIFEST_INTEGRITY_EXIT"
printf "  PROBE_EXIT=%s\n  CSV_VERIFIER_EXIT=%s\n  CSV_IN_MEMORY_DIVERGENCES=%s\n" \
    "$PROBE_EXIT" "$CSV_VERIFIER_EXIT" "$CSV_IN_MEMORY_DIVERGENCES"
printf "  RUN1_COLLECT_EXIT=%s\n  RUN2_COLLECT_EXIT=%s\n  NODE_IDS_EQUAL=%s\n" \
    "$RUN1_COLLECT_EXIT" "$RUN2_COLLECT_EXIT" "$NODE_IDS_EQUAL"
printf "  RUN1_COLLECTED_COUNT=%s\n  RUN2_COLLECTED_COUNT=%s\n" \
    "$RUN1_COLLECTED_COUNT" "$RUN2_COLLECTED_COUNT"
printf "  RUN1_EXIT=%s\n  RUN2_EXIT=%s\n  TREE_STABLE_BETWEEN_RUNS=%s\n" \
    "$RUN1_EXIT" "$RUN2_EXIT" "$TREE_STABLE_BETWEEN_RUNS"
printf "  CLOSURE_GATE_EXIT=%s\n  ALL_REQUIRED_METRICS_PRESENT=%s\n  ALL_CLOSURE_METRICS_ZERO=%s\n" \
    "$CLOSURE_GATE_EXIT" "$ALL_REQUIRED_METRICS_PRESENT" "$ALL_CLOSURE_METRICS_ZERO"
printf "  ARTIFACT_BINDING_READY=%s\n" "$ARTIFACT_BINDING_READY"
echo ""
echo "  CSV_SHA256=sha256:$CSV_SHA"
echo "  JSON_SHA256=sha256:$JSON_SHA"
echo "  HTML_SHA256=sha256:$HTML_SHA"
echo ""

VERDICT_OK=1
[[ "$HEAD_OK" != 1 ]]                      && VERDICT_OK=0
[[ "$INITIAL_TREE_CLEAN" != 1 ]]           && VERDICT_OK=0
[[ "$DARWIN_OK" != 1 ]]                    && VERDICT_OK=0
[[ "$PYTHON_3124_OK" != 1 ]]               && VERDICT_OK=0
[[ "$VENV_OK" != 1 ]]                      && VERDICT_OK=0
[[ "$RUNTIME_CONTRACT_EXIT" != 0 ]]        && VERDICT_OK=0
[[ "$GOLDEN_RULES_INTEGRITY_EXIT" != 0 ]]  && VERDICT_OK=0
[[ "$GOLD_MANIFEST_INTEGRITY_EXIT" != 0 ]] && VERDICT_OK=0
[[ "$PROBE_EXIT" != 0 ]]                   && VERDICT_OK=0
[[ "$CSV_VERIFIER_EXIT" != 0 ]]            && VERDICT_OK=0
[[ "$CSV_IN_MEMORY_DIVERGENCES" != 0 ]]    && VERDICT_OK=0
[[ "$RUN1_COLLECT_EXIT" != 0 ]]            && VERDICT_OK=0
[[ "$RUN2_COLLECT_EXIT" != 0 ]]            && VERDICT_OK=0
[[ "$NODE_IDS_EQUAL" != 1 ]]               && VERDICT_OK=0
[[ "$RUN1_COLLECTED_COUNT" != "$RUN2_COLLECTED_COUNT" ]] && VERDICT_OK=0
[[ "$RUN1_EXIT" != 0 ]]                    && VERDICT_OK=0
[[ "$RUN2_EXIT" != 0 ]]                    && VERDICT_OK=0
[[ "$TREE_STABLE_BETWEEN_RUNS" != 1 ]]     && VERDICT_OK=0
[[ "$CLOSURE_GATE_EXIT" != 0 ]]            && VERDICT_OK=0
[[ "$ALL_REQUIRED_METRICS_PRESENT" != 1 ]] && VERDICT_OK=0
[[ "$ALL_CLOSURE_METRICS_ZERO" != 1 ]]     && VERDICT_OK=0
[[ "$ARTIFACT_BINDING_READY" != 1 ]]       && VERDICT_OK=0

if [[ "$VERDICT_OK" == 1 ]]; then
    echo "CLOSURE_VERDICT = VERIFIED_CLOSED"
    exit 0
else
    echo "CLOSURE_VERDICT = OPEN"
    echo "FAILED_CONDITIONS:"
    for reason in "${OPEN_REASONS[@]}"; do echo "  - $reason"; done
    exit 1
fi
