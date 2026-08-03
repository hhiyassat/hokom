"""
c9 primary repair — Full-target LicensingBoundary wiring tests.

Proves — for the runtime path that the orchestrator now walks per token:

  * At least one genuine corpus token emits a LicensingBoundary stage
    record with execution_status=EXECUTED.
  * That EXECUTED record was produced by invoking the *native* Taaqol
    licensing law under vendor/Taaqol-GPT, not by a Hokom-side shim.
  * The record carries the exact vendor LicensingBoundaryVerdict fields
    (eligibility_verdict, evidence_summary, eligibility_rank) — no
    projection, no dict, no synthetic surrogate.
  * evidence_ids / provenance_ids / trace_ids are non-empty on EXECUTED.
  * If admission is unavailable, the record is NOT_OPENED with
    ADMISSION_NOT_AVAILABLE — never with a fabricated claim_id.
  * If Stage 0 did not execute, the record is NOT_OPENED with
    PREDECESSOR_NOT_EXECUTED::CoreSlotGraph_Gamma.
  * The orchestrator source contains no _dummy_admission helper and no
    direct injection of a LicensingBoundaryVerdict outside the adapter
    chain.

VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from pipeline.taaqol_integration import full_target_orchestrator as _orch  # noqa: E402
from pipeline.taaqol_integration.full_target_orchestrator import (  # noqa: E402
    _LICENSING_STAGE_ID,
    _LICENSING_STAGE_NAME,
    _record_licensing_stage,
    run_full_target,
)
from pipeline.taaqol_integration.result_types import (  # noqa: E402
    ExecutionStatus,
    ScopeType,
)
from pipeline.taaqol_integration.weight_layer.licensing_boundary_adapter import (  # noqa: E402
    _E4B_MU_CHAIN_AVAILABLE,
    _WEIGHT_LAYER_AVAILABLE,
)

REQUIRES_312 = pytest.mark.skipif(
    not (_WEIGHT_LAYER_AVAILABLE and _E4B_MU_CHAIN_AVAILABLE),
    reason='Requires Python 3.12+ (vendor StrEnum + mu chain)',
)

_CORPUS = ('كِتَابٌ', 'رَجُلٌ', 'دَيْنٍ')


# ── One record per token; correct stage id + owner + module ───────────────────
@REQUIRES_312
def test_exactly_one_licensing_record_per_token():
    r = run_full_target(_CORPUS, depth='full')
    per_scope: dict[str, int] = {}
    for rec in r.stage_records:
        if rec.stage_id == _LICENSING_STAGE_ID:
            per_scope[rec.scope_id] = per_scope.get(rec.scope_id, 0) + 1
    # every TOKEN::* scope must have exactly one licensing record
    token_scopes = {
        rec.scope_id for rec in r.stage_records
        if rec.scope_type == ScopeType.TOKEN
        and rec.scope_id.startswith('TOKEN::')
    }
    assert token_scopes, 'no TOKEN records emitted'
    for scope in token_scopes:
        assert per_scope.get(scope) == 1, (
            f'{scope}: expected exactly 1 licensing record, '
            f'got {per_scope.get(scope, 0)}'
        )


@REQUIRES_312
def test_licensing_record_carries_native_vendor_metadata():
    r = run_full_target(_CORPUS, depth='full')
    lic = [rec for rec in r.stage_records if rec.stage_id == _LICENSING_STAGE_ID]
    assert lic, 'no licensing records in run'
    for rec in lic:
        assert rec.stage_name == _LICENSING_STAGE_NAME
        assert rec.native_module.startswith('taaqqul_slot_geometry.weight.licensing_boundary')
        assert rec.native_symbol == 'assess_license'


# ── EXECUTED records: real vendor verdict + non-empty proof ───────────────────
@REQUIRES_312
def test_executed_licensing_has_native_verdict_and_proof():
    r = run_full_target(_CORPUS, depth='full')
    executed = [
        rec for rec in r.stage_records
        if rec.stage_id == _LICENSING_STAGE_ID
        and rec.execution_status == ExecutionStatus.EXECUTED
    ]
    assert executed, (
        'No LicensingBoundary record was EXECUTED for the corpus — '
        'the c9 wiring did not open the vendor law for any token.'
    )
    for rec in executed:
        # Vendor verdict text shape (see licensing_boundary.py:460)
        assert rec.verdict and rec.verdict.startswith('boundary_eligible:'), (
            f'unexpected verdict text: {rec.verdict!r}'
        )
        # eligibility_rank is stringified (Rank enum member).
        assert rec.rank, f'rank missing on EXECUTED licensing {rec.scope_id}'
        # evidence_ids carry the vendor evidence_summary
        assert rec.evidence_ids, (
            f'evidence_ids empty on EXECUTED {rec.scope_id}'
        )
        assert any(str(e).startswith('LICENSE_EVIDENCE::') for e in rec.evidence_ids)
        # provenance and trace anchors are non-empty and non-synthetic —
        # they must come from Hokom's own trace_refs (real Hokom
        # provenance) or the vendor trace anchor.
        assert rec.provenance_ids, (
            f'provenance_ids empty on EXECUTED {rec.scope_id}'
        )
        for p in rec.provenance_ids:
            assert str(p).strip(), (
                f'blank provenance on {rec.scope_id}: {p!r}'
            )
        assert rec.trace_ids, f'trace_ids empty on EXECUTED {rec.scope_id}'
        for t in rec.trace_ids:
            assert str(t).strip(), f'blank trace_id on {rec.scope_id}: {t!r}'
        # trace_ids must include the deterministic orchestrator anchor
        # (a real pipeline anchor, not a random claim_id derivative).
        assert any(str(t).startswith('ORCH::LICENSING::') for t in rec.trace_ids)


# ── Vendor origin: the native licensing law lives under vendor/Taaqol-GPT ─────
@REQUIRES_312
def test_native_licensing_symbol_source_under_vendor():
    import inspect
    from taaqqul_slot_geometry.weight import licensing_boundary as lb

    src = inspect.getfile(lb.assess_license)
    src_path = Path(src).resolve()
    vendor_root = (REPO_ROOT / 'vendor' / 'Taaqol-GPT').resolve()
    assert str(src_path).startswith(str(vendor_root)), (
        f'assess_license source not under vendor root: {src_path}'
    )


# ── Missing admission → NOT_OPENED, no fabricated claim_id ────────────────────
def test_missing_admission_yields_not_opened():
    rec = _record_licensing_stage(
        token_id='TOKEN::TEST',
        bundle=None,
        stage_0_executed=True,
        admission=None,
    )
    assert rec.execution_status == ExecutionStatus.NOT_OPENED
    assert 'ADMISSION_NOT_AVAILABLE' in rec.blocker_codes
    assert rec.provenance_ids == ()
    assert rec.trace_ids == ()
    assert rec.verdict is None


def test_stage_0_failure_yields_not_opened():
    class _FakeAdmission:
        claim_id = 'HOKOM::test'

    rec = _record_licensing_stage(
        token_id='TOKEN::TEST',
        bundle=object(),
        stage_0_executed=False,
        admission=_FakeAdmission(),
    )
    assert rec.execution_status == ExecutionStatus.NOT_OPENED
    assert any(
        'PREDECESSOR_NOT_EXECUTED::CoreSlotGraph_Gamma' in b
        for b in rec.blocker_codes
    )
    assert rec.provenance_ids == ()
    assert rec.trace_ids == ()


def test_missing_bundle_yields_not_opened_when_admission_present():
    class _FakeAdmission:
        claim_id = 'HOKOM::test'

    rec = _record_licensing_stage(
        token_id='TOKEN::TEST',
        bundle=None,
        stage_0_executed=True,
        admission=_FakeAdmission(),
    )
    assert rec.execution_status == ExecutionStatus.NOT_OPENED
    assert 'HOKOM_CLAIM_BUNDLE_NOT_AVAILABLE' in rec.blocker_codes


# ── No dummy admission and no direct verdict injection in source ─────────────
_ORCH_SRC = (
    REPO_ROOT / 'pipeline' / 'taaqol_integration'
    / 'full_target_orchestrator.py'
).read_text(encoding='utf-8')


def _strip_comments(src: str) -> str:
    out = []
    for line in src.splitlines():
        idx = line.find('#')
        out.append(line if idx == -1 else line[:idx])
    return '\n'.join(out)


_ORCH_CODE_ONLY = _strip_comments(_ORCH_SRC)


def test_no_dummy_admission_helper_in_source():
    forbidden = ('_dummy_admission', 'dummy_admission', 'fake_admission')
    for name in forbidden:
        assert name not in _ORCH_CODE_ONLY, (
            f'orchestrator must not define/use {name!r}'
        )


def test_no_direct_licensing_verdict_construction_in_source():
    # Only the vendor law and the adapter may construct
    # LicensingBoundaryVerdict.  The orchestrator must never do so
    # directly (either by constructor or dataclass replace).
    bad_patterns = (
        r'LicensingBoundaryVerdict\s*\(',
        r'replace\s*\(\s*LicensingBoundaryVerdict',
    )
    for pat in bad_patterns:
        assert not re.search(pat, _ORCH_CODE_ONLY), (
            f'orchestrator source contains direct LicensingBoundaryVerdict '
            f'construction matching {pat!r}'
        )


def test_orchestrator_uses_adapter_symbol_only():
    # The only allowed way to reach the native law from the orchestrator
    # is via the E4B+E4C adapter.
    assert 'build_licensing_verdict_from_surface' in _ORCH_CODE_ONLY


# ── tokens_reaching_licensing counter is present + bounded ────────────────────
@REQUIRES_312
def test_tokens_reaching_licensing_counter_is_bounded():
    r = run_full_target(_CORPUS, depth='full')
    core = r.native_execution['tokens_reaching_core']
    lic = r.native_execution['tokens_reaching_licensing']
    assert isinstance(lic, int)
    assert 0 <= lic <= core
    # And it must match a fresh count over the stage_records.
    counted = sum(
        1 for rec in r.stage_records
        if rec.stage_id == _LICENSING_STAGE_ID
        and rec.execution_status == ExecutionStatus.EXECUTED
    )
    assert counted == lic


# ── No accidental gold-file leakage in the licensing wiring ──────────────────
def test_no_gold_leakage_via_licensing_records():
    _sentinel = 'ayat_al_dayn' + '.' + 'pretty' + '.' + 'txt'
    r = run_full_target(_CORPUS, depth='full')
    for rec in r.stage_records:
        if rec.stage_id != _LICENSING_STAGE_ID:
            continue
        for p in rec.provenance_ids:
            assert _sentinel not in str(p)
        for e in rec.evidence_ids:
            assert _sentinel not in str(e)
        for t in rec.trace_ids:
            assert _sentinel not in str(t)
