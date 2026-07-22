"""
Architecture enforcement tests — prevent forbidden design patterns.
These tests inspect source structure rather than runtime behavior.
HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01 — HARDEN-07
"""
import ast
import os
import inspect
import importlib

import pytest

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
SRC_ROOT = REPO_ROOT


def _read_source(filepath: str) -> str:
    with open(filepath, encoding="utf-8") as f:
        return f.read()


def _find_py_files(
    directory: str,
    exclude_dirs: tuple[str, ...] = ("vendor", "__pycache__", ".venv", ".venv-py312"),
):
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(root, f)


# ── No second slot registry ───────────────────────────────────────────────────

def test_no_parallel_slot_registry():
    """Only contracts.py and slot_registry.py may define a SlotId Enum class."""
    violations = []
    for filepath in _find_py_files(SRC_ROOT):
        basename = os.path.basename(filepath)
        if basename in ("slot_registry.py", "contracts.py"):
            continue
        if "vendor" in filepath or basename.startswith("test_"):
            continue
        src = _read_source(filepath)
        if "class SlotId" in src and "Enum" in src:
            violations.append(filepath)
    assert violations == [], f"Parallel SlotId definitions: {violations}"


# ── No parallel profile registry ─────────────────────────────────────────────

def test_no_parallel_profile_registry():
    """Only contracts.py may define CLAIM_PROFILES with ClaimProfile instances."""
    violations = []
    for filepath in _find_py_files(SRC_ROOT):
        basename = os.path.basename(filepath)
        if basename == "contracts.py":
            continue
        if "vendor" in filepath or basename.startswith("test_"):
            continue
        src = _read_source(filepath)
        if "CLAIM_PROFILES" in src and "ClaimProfile(" in src:
            violations.append(filepath)
    assert violations == [], f"Parallel CLAIM_PROFILES definitions: {violations}"


# ── No vendor tree modifications / injections ─────────────────────────────────

def test_no_vendor_test_injection():
    """
    Hokom must not inject test files into the top-level vendor/Taaqol-GPT/src directory.
    Pre-existing vendor test suites (e.g. enriched_simulation_agent/tests/) are not our concern.
    We check only the canonical source path that Hokom uses.
    """
    vendor_src_dir = os.path.join(SRC_ROOT, "vendor", "Taaqol-GPT", "src")
    vendor_test_files = []
    if os.path.exists(vendor_src_dir):
        for filepath in _find_py_files(vendor_src_dir):
            basename = os.path.basename(filepath)
            if basename.startswith("test_") or basename == "conftest.py":
                vendor_test_files.append(filepath)
    assert vendor_test_files == [], f"Tests injected into vendor/src: {vendor_test_files}"


def test_no_vendor_conftest():
    """conftest.py must not be injected by Hokom into the canonical vendor/Taaqol-GPT/src path."""
    vendor_src_dir = os.path.join(SRC_ROOT, "vendor", "Taaqol-GPT", "src")
    violations = []
    if os.path.exists(vendor_src_dir):
        for root, dirs, files in os.walk(vendor_src_dir):
            for f in files:
                if f == "conftest.py":
                    violations.append(os.path.join(root, f))
    assert violations == [], f"conftest.py in vendor/src: {violations}"


# ── No StrEnum shims ──────────────────────────────────────────────────────────

def test_no_strenum_backport():
    """
    No StrEnum injection/monkey-patching in production pipeline code.
    Detection pattern: code that *assigns* to enum.StrEnum or defines a StrEnum
    replacement class. Fail-closed checks that merely test for StrEnum availability
    (hasattr, try/except ImportError) are permitted and expected.
    """
    violations = []
    # These patterns indicate actual injection / shim creation
    injection_patterns = [
        "enum.StrEnum = ",          # direct assignment to enum.StrEnum
        "builtins.StrEnum =",       # builtins injection
        "class StrEnum(str, Enum)", # replacement class definition
        "class StrEnum(str,Enum)",  # variant spacing
    ]
    for filepath in _find_py_files(SRC_ROOT):
        if "vendor" in filepath:
            continue
        basename = os.path.basename(filepath)
        if basename.startswith("test_") or basename == "conftest.py":
            continue
        src = _read_source(filepath)
        for pattern in injection_patterns:
            if pattern in src:
                violations.append(f"{filepath}: {pattern!r}")
    assert violations == [], f"StrEnum injection in production code: {violations}"


# ── No standard-library injection ────────────────────────────────────────────

def test_no_stdlib_monkey_patching():
    """Standard library modules (enum, builtins) must not be monkey-patched in production code."""
    violations = []
    # These patterns indicate actual monkey-patching, not mere references
    forbidden_patterns = [
        "enum.StrEnum = ",           # assignment to StrEnum
        "sys.modules['enum']",       # swapping enum module
        'sys.modules["enum"]',       # swapping enum module
    ]
    for filepath in _find_py_files(SRC_ROOT):
        if "vendor" in filepath:
            continue
        basename = os.path.basename(filepath)
        # Exclude test files — they may contain forbidden patterns in test strings
        if basename.startswith("test_") or basename == "conftest.py":
            continue
        src = _read_source(filepath)
        for pattern in forbidden_patterns:
            if pattern in src:
                violations.append(f"{filepath}: {pattern!r}")
    assert violations == [], f"Stdlib injection in production code: {violations}"


# ── evaluate_sga_bundle type enforcement ─────────────────────────────────────

def test_bridge_enforces_typed_input():
    """Bridge source must check isinstance(sga_bundle, HokomClaimBundle)."""
    bridge_path = os.path.join(
        SRC_ROOT, "pipeline/taaqol_integration/live/bridge.py"
    )
    src = _read_source(bridge_path)
    assert "HokomClaimBundle" in src, "Bridge must reference HokomClaimBundle"
    assert "isinstance" in src, "Bridge must use isinstance() check"


def test_bridge_evaluate_sga_bundle_has_type_check():
    """evaluate_sga_bundle function must reject non-HokomClaimBundle."""
    from pipeline.taaqol_integration.live.bridge import evaluate_sga_bundle
    # Verify it is a callable
    assert callable(evaluate_sga_bundle)
    # Verify rejection of dict input (runtime enforcement)
    result = evaluate_sga_bundle({"word": "test"})
    assert result is not None
    assert result.effective_verdict != "LICENSED"


# ── No dict-based slot transport at public boundaries ─────────────────────────

def test_bridge_entry_signature_exists():
    """The canonical bridge entry must exist and be importable."""
    from pipeline.taaqol_integration.live.bridge import evaluate_sga_bundle
    sig = inspect.signature(evaluate_sga_bundle)
    params = list(sig.parameters.values())
    assert len(params) >= 1, "evaluate_sga_bundle must have at least one parameter"


# ── Taaqol not duplicated in Hokom pipeline ───────────────────────────────────

def test_no_slot_graph_in_hokom_pipeline():
    """Hokom pipeline must not implement its own SlotGraph outside taaqol_integration."""
    pipeline_dir = os.path.join(SRC_ROOT, "pipeline")
    violations = []
    for filepath in _find_py_files(pipeline_dir):
        if "taaqol_integration" in filepath or "sga" in filepath:
            continue
        src = _read_source(filepath)
        if "class SlotGraph" in src:
            violations.append(filepath)
    assert violations == [], f"SlotGraph duplicated in Hokom pipeline: {violations}"


# ── No HR2S required dependency ──────────────────────────────────────────────

def test_hr2s_not_required_in_pipeline():
    """HR2S must not be imported in production pipeline code."""
    pipeline_dir = os.path.join(SRC_ROOT, "pipeline")
    violations = []
    for filepath in _find_py_files(pipeline_dir):
        src = _read_source(filepath)
        if "import HR2S" in src or "from HR2S" in src or "import hr2s" in src:
            violations.append(filepath)
    assert violations == [], f"HR2S is required in pipeline: {violations}"


# ── No parallel SlotSort definition ──────────────────────────────────────────

def test_no_parallel_slot_sort_registry():
    """Only contracts.py may define SlotSort as an Enum class."""
    violations = []
    for filepath in _find_py_files(SRC_ROOT):
        basename = os.path.basename(filepath)
        if basename == "contracts.py":
            continue
        if "vendor" in filepath or basename.startswith("test_"):
            continue
        src = _read_source(filepath)
        if "class SlotSort" in src and "Enum" in src:
            violations.append(filepath)
    assert violations == [], f"Parallel SlotSort definitions: {violations}"


# ── evaluate_sga_bundle violation counters ────────────────────────────────────

def test_violation_counters_are_zero():
    """All violation counters in bridge.py must be zero."""
    from pipeline.taaqol_integration.live import bridge
    assert bridge.RAW_BRIDGE_CALLER_VIOLATIONS == 0
    assert bridge.CLAIM_BUNDLE_BYPASS_VIOLATIONS == 0
    assert bridge.OPAQUE_BRIDGE_INPUT_VIOLATIONS == 0
    assert bridge.AMBIGUITY_COLLAPSE_VIOLATIONS == 0
    assert bridge.AMBIGUOUS_SET_LOSS_VIOLATIONS == 0
    assert bridge.AMBIGUOUS_SILENT_SELECTION_VIOLATIONS == 0
    assert bridge.AMBIGUOUS_SELECTED_NOT_NONE_VIOLATIONS == 0
    assert bridge.AMBIGUOUS_RESIDUAL_MISSING_VIOLATIONS == 0


# ── No silent coercion in adapters ────────────────────────────────────────────

def test_adapters_do_not_silently_coerce():
    """Adapters must return UNKNOWN state, not coerce UNKNOWN to a default value."""
    from pipeline.sga.adapters import adapt_root_radicals
    # Empty hokom_result: all radicals must be UNKNOWN
    slots = adapt_root_radicals({})
    from pipeline.sga.contracts import SlotState
    for slot in slots:
        assert slot.state == SlotState.UNKNOWN or slot.state == SlotState.NOT_APPLICABLE, \
            f"Slot {slot.slot_id} should be UNKNOWN/NOT_APPLICABLE when no root, got {slot.state}"


def test_adapters_no_silent_first_candidate_selection():
    """When multiple root candidates, R1/R2/R3 must remain UNKNOWN (T-10)."""
    from pipeline.sga.adapters import adapt_root_radicals
    from pipeline.sga.contracts import SlotState
    slots = adapt_root_radicals({"root_candidate": ["ك-ت-ب", "ق-ر-أ"]})
    for slot in slots:
        assert slot.state == SlotState.UNKNOWN, \
            f"Slot {slot.slot_id} must be UNKNOWN for ambiguous root, got {slot.state}"
        assert slot.value is None, \
            f"Slot {slot.slot_id} must have value=None for ambiguous root, got {slot.value!r}"
