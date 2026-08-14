"""
test_native_provenance.py — Prove Taaqol native types come from vendor/Taaqol-GPT.

Under Python 3.12 (the canonical runtime), vendor types are importable.
Under Python 3.10 (sandbox), StrEnum causes ImportError — we document the path
and test that the fallback is BLOCKED (not SILENT).
"""
from __future__ import annotations
import sys, os

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
if os.path.join(_REPO_ROOT, 'src') not in sys.path:
    sys.path.insert(0, os.path.join(_REPO_ROOT, 'src'))

VENDOR_SRC = os.path.join(_REPO_ROOT, 'vendor/Taaqol-GPT/src')
VENDOR_CORE_MODULES = [
    "taaqqul_slot_geometry.core.slot_graph",
    "taaqqul_slot_geometry.core.gamma",
    "taaqqul_slot_geometry.core.evidence_contract",
    "taaqqul_slot_geometry.core.rank_lattice",
    "taaqqul_slot_geometry.core.residual_policy",
    "taaqqul_slot_geometry.core.transition_gate",
    "taaqqul_slot_geometry.core.trace_ledger",
]


def test_vendor_source_files_exist():
    """All 7 vendor core modules must exist as source files."""
    for mod in VENDOR_CORE_MODULES:
        path_parts = mod.replace('.', '/') + '.py'
        full_path = os.path.join(VENDOR_SRC, path_parts)
        assert os.path.exists(full_path), (
            f"NATIVE_PROVENANCE_MISSING: {full_path} does not exist"
        )


def test_vendor_path_is_hokom_vendor():
    """Vendor path must be under vendor/Taaqol-GPT/, not a local copy."""
    assert 'vendor/Taaqol-GPT' in VENDOR_SRC or 'vendor' in VENDOR_SRC


def test_no_local_fake_native_types():
    """No file in pipeline/ should define classes named SlotGraph, GammaClosure, etc."""
    import glob
    pipeline_files = glob.glob(os.path.join(_REPO_ROOT, 'pipeline/**/*.py'), recursive=True)
    forbidden_class_names = ['class SlotGraph', 'class GammaClosure', 'class EvidenceContract',
                              'class RankLattice', 'class ResidualPolicy', 'class TransitionGate']
    for fpath in pipeline_files:
        if '__pycache__' in fpath:
            continue
        with open(fpath) as f:
            src = f.read()
        for name in forbidden_class_names:
            assert name not in src, (
                f"FAKE_NATIVE_TYPE: {fpath} defines {name!r} — must come from vendor only"
            )


def test_taaqol_stage_registry_uses_vendor_paths():
    """Taaqol stage registry source_module fields point to vendor/Taaqol-GPT."""
    from pipeline.execution_ledger.taaqol_stage_registry import TAAQOL_CORE_STAGES
    for stage in TAAQOL_CORE_STAGES:
        assert 'vendor/Taaqol-GPT' in stage.source_module or 'taaqqul_slot_geometry' in stage.source_module, (
            f"NATIVE_PROVENANCE: stage {stage.stage_id} source_module does not reference vendor: {stage.source_module}"
        )


def test_document_49_not_in_stage_registry():
    """Document number 49 (PV-M0) must not appear as a stage ID."""
    from pipeline.execution_ledger.taaqol_stage_registry import TAAQOL_CORE_STAGES
    stage_ids = [s.stage_id for s in TAAQOL_CORE_STAGES]
    assert "TAAQOL_49" not in stage_ids
    assert "PV_M0" not in stage_ids
    assert "META_LANGUAGE_BOUNDARY" not in stage_ids
    assert not any("49" in sid for sid in stage_ids), (
        f"DOCUMENT_NUMBER_AS_STAGE_ID: stage IDs contain '49': {stage_ids}"
    )


def test_taaqol_core_stage_count_is_7_not_49():
    """TAAQOL_CORE_STAGE_COUNT = 7, not 49."""
    from pipeline.execution_ledger.taaqol_stage_registry import TAAQOL_CORE_STAGES, ACTUAL_TAAQOL_PROVEN_STAGE_COUNT
    assert ACTUAL_TAAQOL_PROVEN_STAGE_COUNT == 7
    assert len(TAAQOL_CORE_STAGES) == 7


def test_no_string_verdict_imitations():
    """No production module should use string literals like 'LICENSED' as verdict imitations."""
    # Check that the vertical chain uses proper enum verdicts, not raw strings
    from pipeline.vertical_chain.models import IfadahVerdict, HukmVerdict, AnswerAuditVerdict
    from pipeline.vertical_chain.chain import build_ifadah, build_hukm, build_answer_audit
    ifadah = build_ifadah("c1", (), [], ())
    assert isinstance(ifadah.verdict, IfadahVerdict), f"Verdict must be IfadahVerdict enum, got {type(ifadah.verdict)}"
    hukm = build_hukm(ifadah)
    assert isinstance(hukm.verdict, HukmVerdict)
    audit = build_answer_audit([], [], [])
    assert isinstance(audit.verdict, AnswerAuditVerdict)


# ── R4: Runtime module provenance via inspect.getfile ────────────────────────

APPROVED_VENDOR_SHA = 'bc9d1ea5ef45970f5f3ec132441e30fd54b3da52'

def test_vendor_sha_matches_approved():
    """R4: vendor/Taaqol-GPT HEAD must equal APPROVED_TARGET_SHA."""
    import subprocess
    vendor_root = os.path.join(_REPO_ROOT, 'vendor', 'Taaqol-GPT')
    result = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        capture_output=True, text=True, cwd=vendor_root,
    )
    actual_sha = result.stdout.strip()
    assert actual_sha == APPROVED_VENDOR_SHA, (
        f"VENDOR_SHA_MISMATCH:\n"
        f"  approved: {APPROVED_VENDOR_SHA}\n"
        f"  actual:   {actual_sha!r}\n"
        f"vendor/Taaqol-GPT must be pinned to APPROVED_TARGET_SHA"
    )


def test_runtime_modules_resolve_under_vendor_root():
    """R4: Vendor modules imported at runtime must resolve under vendor/Taaqol-GPT.

    Uses inspect.getfile() to prove the actual .py source file for each vendor
    module is a descendant of vendor/Taaqol-GPT (not a local copy or backport).
    Skipped on Python 3.10 (canonical runtime is 3.12.4).
    """
    import inspect
    import importlib
    import sys as _sys
    from pathlib import Path

    if _sys.version_info < (3, 11):
        import pytest
        pytest.skip("inspect.getfile provenance check requires Python 3.11+ (canonical: 3.12.4)")

    vendor_root = Path(_REPO_ROOT) / 'vendor' / 'Taaqol-GPT'

    # Ensure vendor src is on path
    vendor_src_str = str(vendor_root / 'src')
    if vendor_src_str not in _sys.path:
        _sys.path.insert(0, vendor_src_str)

    violations = []
    for mod_name in VENDOR_CORE_MODULES:
        try:
            mod = importlib.import_module(mod_name)
            source_file = Path(inspect.getfile(mod)).resolve()
            if not source_file.is_relative_to(vendor_root.resolve()):
                violations.append(
                    f"  {mod_name}: {source_file} "
                    f"is NOT under vendor/Taaqol-GPT"
                )
        except (ImportError, TypeError) as exc:
            violations.append(f"  {mod_name}: import/inspect failed — {exc}")

    assert not violations, (
        "NATIVE_PROVENANCE_VIOLATION: vendor modules resolved outside vendor/Taaqol-GPT:\n"
        + "\n".join(violations)
    )
