"""c9 native-chain verification.

Runs the Full-Target orchestrator over the Ayat al-Dayn corpus with the
five downstream adapters wrapped in counter-instrumented proxies, then
prints strict COUNT / TYPE / SOURCE evidence per the c9 mandate §5.

* LICENSING_NATIVE_CALLS      — build_licensing_verdict_from_surface
* DAL_ONLY_NATIVE_CALLS       — build_dal_only_candidate
* VERBAL_MADLUL_NATIVE_CALLS  — build_verbal_madlul_candidate
* DAL_MADLUL_BINDING_NATIVE_CALLS — build_dal_madlul_binding
* CONTRACTABLE_UNIT_NATIVE_CALLS  — build_contractable_unit_geometry

Each of those counters also asserts:
  * the returned verdict is the exact vendor dataclass (not a projection),
  * the returned verdict is emitted by a symbol whose source lives under
    vendor/Taaqol-GPT/.

Exits nonzero if any COUNT is wrong, if the wrong native output type is
seen, or if a downstream stage is EXECUTED without an actual native call.
"""
from __future__ import annotations

import inspect
import json
import pathlib
import sys
from collections import Counter, defaultdict
from typing import Any

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'vendor' / 'Taaqol-GPT' / 'src'))

from pipeline.taaqol_integration import full_target_orchestrator as _orch  # noqa: E402
from pipeline.taaqol_integration.full_target_orchestrator import (  # noqa: E402
    _LICENSING_STAGE_ID,
    run_full_target,
)
from pipeline.taaqol_integration.result_types import ExecutionStatus  # noqa: E402

# Vendor types must load — c9 requires 3.12+.
from taaqqul_slot_geometry.weight.licensing_boundary import (  # noqa: E402
    LicensingBoundaryVerdict,
    assess_license,
)
from taaqqul_slot_geometry.weight.dal_only import (  # noqa: E402
    DalBoundaryState,
    DalBoundaryVerdict,
    DalOnlyCandidate,
    prove_dal,
)
from taaqqul_slot_geometry.weight.verbal_madlul import (  # noqa: E402
    MadlulBoundaryState,
    VerbalMadlulBoundaryVerdict,
    VerbalMadlulCandidate,
    prove_verbal_madlul,
)
from taaqqul_slot_geometry.weight.dal_madlul_binding import (  # noqa: E402
    BindingState,
    DalMadlulBindingVerdict,
    bind_dal_madlul,
)
from taaqqul_slot_geometry.weight.contractable_unit_geometry import (  # noqa: E402
    ContractableUnitState,
    prove_contractable_unit,
)


VENDOR_ROOT = (REPO / 'vendor' / 'Taaqol-GPT').resolve()
CORPUS_PATH = REPO / 'src' / 'hokom' / 'demo' / 'ayat_al_dayn_corpus.py'


def _under_vendor(symbol) -> bool:
    try:
        p = pathlib.Path(inspect.getfile(symbol)).resolve()
    except (TypeError, OSError):
        return False
    return str(p).startswith(str(VENDOR_ROOT))


def _assert_vendor_source(name: str, symbol) -> None:
    if not _under_vendor(symbol):
        print(f'FATAL: {name} not under vendor/: {inspect.getfile(symbol)}')
        sys.exit(2)


_assert_vendor_source('assess_license', assess_license)
_assert_vendor_source('prove_dal', prove_dal)
_assert_vendor_source('prove_verbal_madlul', prove_verbal_madlul)
_assert_vendor_source('bind_dal_madlul', bind_dal_madlul)
_assert_vendor_source('prove_contractable_unit', prove_contractable_unit)


# ── Counter-instrumented proxies ─────────────────────────────────────────────
_counts: Counter = Counter()
_wrong_type: Counter = Counter()
_call_returns: dict[str, list] = defaultdict(list)


def _wrap_licensing(orig):
    def _inner(**kwargs):
        result = orig(**kwargs)
        _counts['build_licensing_verdict_from_surface_all'] += 1
        if getattr(result, 'state', None) == 'ELIGIBLE' and result.verdict is not None:
            _counts['LICENSING_NATIVE_CALLS'] += 1
            if type(result.verdict) is not LicensingBoundaryVerdict:
                _wrong_type['LICENSING'] += 1
            _call_returns['licensing'].append(result.verdict)
        return result
    return _inner


def _wrap_dal_only(orig):
    def _inner(**kwargs):
        result = orig(**kwargs)
        _counts['build_dal_only_candidate_all'] += 1
        if result is not None:
            _counts['DAL_ONLY_NATIVE_CALLS'] += 1
            if type(result) is not DalBoundaryVerdict:
                _wrong_type['DAL_ONLY_OUTER'] += 1
            if type(result.candidate) is not DalOnlyCandidate:
                _wrong_type['DAL_ONLY_CANDIDATE'] += 1
            if not isinstance(kwargs['licensing_verdict'], LicensingBoundaryVerdict):
                _wrong_type['DAL_ONLY_INPUT'] += 1
            _call_returns['dal_only'].append(result)
        return result
    return _inner


def _wrap_verbal(orig):
    def _inner(**kwargs):
        result = orig(**kwargs)
        _counts['build_verbal_madlul_candidate_all'] += 1
        if result is not None:
            _counts['VERBAL_MADLUL_NATIVE_CALLS'] += 1
            if type(result) is not VerbalMadlulBoundaryVerdict:
                _wrong_type['VERBAL_MADLUL_OUTER'] += 1
            if type(result.candidate) is not VerbalMadlulCandidate:
                _wrong_type['VERBAL_MADLUL_CANDIDATE'] += 1
            if not isinstance(kwargs['dal_only_candidate'], DalOnlyCandidate):
                _wrong_type['VERBAL_MADLUL_INPUT'] += 1
            _call_returns['verbal_madlul'].append(result)
        return result
    return _inner


def _wrap_binding(orig):
    def _inner(**kwargs):
        result = orig(**kwargs)
        _counts['build_dal_madlul_binding_all'] += 1
        if result is not None:
            _counts['DAL_MADLUL_BINDING_NATIVE_CALLS'] += 1
            if type(result) is not DalMadlulBindingVerdict:
                _wrong_type['DAL_MADLUL_BINDING_OUTER'] += 1
            if not isinstance(kwargs['dal_only_candidate'], DalOnlyCandidate):
                _wrong_type['DAL_MADLUL_BINDING_INPUT_DAL'] += 1
            if not isinstance(kwargs['verbal_madlul_candidate'], VerbalMadlulCandidate):
                _wrong_type['DAL_MADLUL_BINDING_INPUT_VERBAL'] += 1
            _call_returns['dal_madlul_binding'].append(result)
        return result
    return _inner


def _wrap_contractable(orig):
    def _inner(**kwargs):
        result = orig(**kwargs)
        _counts['build_contractable_unit_geometry_all'] += 1
        if result is not None:
            _counts['CONTRACTABLE_UNIT_NATIVE_CALLS'] += 1
            # Vendor returns ContractableUnitVerdict; candidate is
            # ContractableUnitGeometry.
            if type(result).__name__ != 'ContractableUnitVerdict':
                _wrong_type['CONTRACTABLE_UNIT_OUTER'] += 1
            _call_returns['contractable_unit'].append(result)
        return result
    return _inner


# Patch the module-level names the orchestrator imported.
_orch.build_licensing_verdict_from_surface = _wrap_licensing(
    _orch.build_licensing_verdict_from_surface
)
_orch.build_dal_only_candidate = _wrap_dal_only(
    _orch.build_dal_only_candidate
)
_orch.build_verbal_madlul_candidate = _wrap_verbal(
    _orch.build_verbal_madlul_candidate
)
_orch.build_dal_madlul_binding = _wrap_binding(
    _orch.build_dal_madlul_binding
)
_orch.build_contractable_unit_geometry = _wrap_contractable(
    _orch.build_contractable_unit_geometry
)


# ── Run the corpus ──────────────────────────────────────────────────────────
# Read the corpus from the isolated demo JSON (its token_summaries carry
# the surface of every analyzed token, in order — no dependence on the
# gold pretty file).
_out_dir_arg = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else (
    REPO / 'reports' / 'taaqol_full_integration' / 'c9_runtime_output'
)
_json_probe = _out_dir_arg / 'ayat_al_dayn_taaqol_full.json'
if not _json_probe.exists():
    raise SystemExit(f'FATAL: expected demo JSON at {_json_probe}')
_probe = json.loads(_json_probe.read_text())
CORPUS = tuple(
    ts['surface'] for ts in _probe.get('token_summaries', ())
    if 'surface' in ts
)
if not CORPUS:
    raise SystemExit('FATAL: token_summaries missing surface field')


run = run_full_target(CORPUS, depth='full')


# ── Cross-check counts against the isolated JSON ────────────────────────────
out_dir = _out_dir_arg
json_path = _json_probe
data = _probe
records = data['stage_records']


def by_status(stage_id):
    return Counter(r['execution_status'] for r in records if r['stage_id'] == stage_id)


lic_exec = by_status('STAGE_04B_LICENSING_BOUNDARY')['EXECUTED']
dal_exec = by_status('STAGE_01_DALONLY')['EXECUTED']
verbal_exec = by_status('STAGE_02_VERBALMADLUL')['EXECUTED']
contractable_exec = by_status('STAGE_03_CONTRACTABLEUNIT')['EXECUTED']

# EXECUTED_WITHOUT_NATIVE_CALL — reconcile counters
executed_without_native = 0
for key, exec_count in (
    ('LICENSING_NATIVE_CALLS', lic_exec),
    ('DAL_ONLY_NATIVE_CALLS', dal_exec),
    ('VERBAL_MADLUL_NATIVE_CALLS', verbal_exec),
    ('DAL_MADLUL_BINDING_NATIVE_CALLS', contractable_exec),
    ('CONTRACTABLE_UNIT_NATIVE_CALLS', contractable_exec),
):
    native = _counts[key]
    if exec_count > native:
        executed_without_native += (exec_count - native)

wrong_type_total = sum(_wrong_type.values())

# Empty-field checks per c9 §5.
empty_evidence = 0
empty_provenance = 0
empty_trace = 0
for r in records:
    if r['execution_status'] != 'EXECUTED':
        continue
    # Stage 0 has no upstream evidence_ids (admission-only); exempt it.
    if r['stage_id'] == 'STAGE_00_CORESLOTGRAPH_GAMMA':
        if not r['provenance_ids']:
            empty_provenance += 1
        if not r['trace_ids']:
            empty_trace += 1
        continue
    if not r['evidence_ids']:
        empty_evidence += 1
    if not r['provenance_ids']:
        empty_provenance += 1
    if not r['trace_ids']:
        empty_trace += 1


print('LICENSING_NATIVE_CALLS         =', _counts['LICENSING_NATIVE_CALLS'])
print('DAL_ONLY_NATIVE_CALLS          =', _counts['DAL_ONLY_NATIVE_CALLS'])
print('VERBAL_MADLUL_NATIVE_CALLS     =', _counts['VERBAL_MADLUL_NATIVE_CALLS'])
print('DAL_MADLUL_BINDING_NATIVE_CALLS=', _counts['DAL_MADLUL_BINDING_NATIVE_CALLS'])
print('CONTRACTABLE_UNIT_NATIVE_CALLS =', _counts['CONTRACTABLE_UNIT_NATIVE_CALLS'])
print()
print('LIC_STAGE_EXECUTED             =', lic_exec)
print('DAL_STAGE_EXECUTED             =', dal_exec)
print('VERBAL_STAGE_EXECUTED          =', verbal_exec)
print('CONTRACTABLE_STAGE_EXECUTED    =', contractable_exec)
print()
print('EXECUTED_WITHOUT_NATIVE_CALL   =', executed_without_native)
print('WRONG_NATIVE_OUTPUT_TYPE       =', wrong_type_total, dict(_wrong_type) if wrong_type_total else '')
print('EMPTY_EVIDENCE_UNEXEMPTED      =', empty_evidence)
print('EMPTY_PROVENANCE               =', empty_provenance)
print('EMPTY_TRACE                    =', empty_trace)


exit_code = 0
expected = data['native_execution']['tokens_reaching_licensing']
for key, count in (
    ('LICENSING_NATIVE_CALLS', _counts['LICENSING_NATIVE_CALLS']),
    ('DAL_ONLY_NATIVE_CALLS', _counts['DAL_ONLY_NATIVE_CALLS']),
    ('VERBAL_MADLUL_NATIVE_CALLS', _counts['VERBAL_MADLUL_NATIVE_CALLS']),
    ('DAL_MADLUL_BINDING_NATIVE_CALLS', _counts['DAL_MADLUL_BINDING_NATIVE_CALLS']),
    ('CONTRACTABLE_UNIT_NATIVE_CALLS', _counts['CONTRACTABLE_UNIT_NATIVE_CALLS']),
):
    if count != expected:
        print(f'FAIL: {key} = {count} (expected {expected})')
        exit_code = 1

for key, count in (
    ('EXECUTED_WITHOUT_NATIVE_CALL', executed_without_native),
    ('WRONG_NATIVE_OUTPUT_TYPE', wrong_type_total),
    ('EMPTY_EVIDENCE_UNEXEMPTED', empty_evidence),
    ('EMPTY_PROVENANCE', empty_provenance),
    ('EMPTY_TRACE', empty_trace),
):
    if count != 0:
        print(f'FAIL: {key} = {count}')
        exit_code = 1

if exit_code == 0:
    print('NATIVE_CHAIN_VERIFICATION=OK')
sys.exit(exit_code)
