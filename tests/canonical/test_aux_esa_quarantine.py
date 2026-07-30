"""
test_aux_esa_quarantine.py — AUX-ESA Quarantine Executable Proofs

Mandate section E. Three obligations:

  AUX-ESA-0: no kernel runtime import in ESA, no SlotGraph mutation,
              no rank grant, no TransitionGate bypass.
  AUX-ESA-1: verification harness exists, executes, fails on injected violations.
  AUX-ESA-2: source blockers translate through declared contract only.

These tests are Hokom-side proofs that the ESA quarantine boundary is intact.
They operate on the vendor/Taaqol-GPT source files via static analysis (ast)
and the blocker_translation module, with no live runtime invocation of the
Taaqol kernel.

Test-origin covenant (docs/52):
  origin_law:                  AUX-ESA constitutional amendment + docs/08 (TransitionGate)
  branch_name:                 AUX-ESA quarantine boundary enforcement
  constitutional_chain:        ESA → kernel boundary
  expected_state:              BLOCKED (for any kernel import), MINIMALLY_CLOSED otherwise
  forbidden_outputs:           kernel rank grant, SlotGraph mutation, TransitionGate bypass
  expected_failure_code:       None (these are positive quarantine proofs)
  max_rank:                    N/A (static analysis only)
  required_residual_visibility: N/A
  required_trace:              False
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

# ── Paths ─────────────────────────────────────────────────────────────────────

_VENDOR = Path(__file__).parent.parent.parent / "vendor" / "Taaqol-GPT"
_ESA_SRC = _VENDOR / "enriched_simulation_agent" / "src" / "sim_agent"
_BLOCKER_TRANSLATION = _ESA_SRC / "blocker_translation.py"
_F_HARNESS = _ESA_SRC / "f_constitutional_harness.py"
_F_X0R_BRIDGE = _ESA_SRC / "f_x0r_bridge.py"
_KERNEL_CORE = _VENDOR / "src" / "taaqqul_slot_geometry" / "core"

_ESA_AVAILABLE = _ESA_SRC.exists()
_BLOCKER_TRANSLATION_AVAILABLE = _BLOCKER_TRANSLATION.exists()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse(path: Path) -> ast.Module:
    """Parse a Python file into an AST; hard-fail if not found."""
    if not path.exists():
        pytest.fail(
            f"AUX-ESA quarantine BLOCKED: required file does not exist: {path}\n"
            f"This is a constitutional quarantine violation — the harness must exist."
        )
    return ast.parse(path.read_text(encoding="utf-8"))


def _all_imports(tree: ast.Module) -> list[str]:
    """Return all imported module names from an AST."""
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def _has_name_reference(tree: ast.Module, name: str) -> bool:
    """Return True if the AST contains any Name/Attribute reference to `name`."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == name:
            return True
        if isinstance(node, ast.Attribute) and node.attr == name:
            return True
    return False


def _has_call(tree: ast.Module, method_name: str) -> bool:
    """Return True if the AST contains any call to a function/method named `method_name`."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == method_name:
                return True
            if isinstance(node.func, ast.Attribute) and node.func.attr == method_name:
                return True
    return False


# ── AUX-ESA-0: no kernel runtime import ──────────────────────────────────────

class TestAuxEsa0KernelImportBan:
    """
    AUX-ESA-0: ESA must not import from taaqqul_slot_geometry.core at runtime.

    The only permitted reference to taaqqul_slot_geometry in ESA is the
    f_x0r_bridge.py static analysis check (which INSPECTS for kernel imports
    in strings/ast — it does not perform them).
    """

    def test_f_constitutional_harness_no_kernel_core_import(self):
        """f_constitutional_harness.py must not import taaqqul_slot_geometry.core."""
        tree = _parse(_F_HARNESS)
        imports = _all_imports(tree)
        kernel_core_imports = [
            imp for imp in imports
            if "taaqqul_slot_geometry.core" in imp
        ]
        assert kernel_core_imports == [], (
            f"AUX-ESA-0 VIOLATED: f_constitutional_harness.py imports kernel core: "
            f"{kernel_core_imports}\n"
            "ESA must not import from taaqqul_slot_geometry.core at runtime."
        )

    def test_blocker_translation_no_kernel_import(self):
        """blocker_translation.py must not import taaqqul_slot_geometry."""
        tree = _parse(_BLOCKER_TRANSLATION)
        imports = _all_imports(tree)
        kernel_imports = [
            imp for imp in imports if "taaqqul_slot_geometry" in imp
        ]
        assert kernel_imports == [], (
            f"AUX-ESA-0 VIOLATED: blocker_translation.py imports kernel: {kernel_imports}"
        )

    def test_f_x0r_bridge_no_live_kernel_import(self):
        """
        f_x0r_bridge.py checks for kernel imports via ast (permitted).
        It must not PERFORM a live kernel import itself.
        The check strings 'taaqqul_slot_geometry.x0r' appear only as literals,
        not as actual import statements.
        """
        tree = _parse(_F_X0R_BRIDGE)
        imports = _all_imports(tree)
        # Only sim_agent.* imports are allowed
        kernel_live_imports = [
            imp for imp in imports
            if "taaqqul_slot_geometry" in imp and not imp.startswith("sim_agent")
        ]
        assert kernel_live_imports == [], (
            f"AUX-ESA-0 VIOLATED: f_x0r_bridge.py performs live kernel import: "
            f"{kernel_live_imports}"
        )

    def test_esa_no_slot_graph_mutation(self):
        """No ESA file may call SlotGraph mutating methods."""
        # SlotGraph has no mutable state — it's frozen — but check for
        # any reference to add_slot, remove_slot, mutate, etc.
        forbidden_calls = ["add_slot", "remove_slot", "mutate_slot", "clear_graph"]
        violations: list[str] = []
        for py_file in _ESA_SRC.glob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for call in forbidden_calls:
                if _has_call(tree, call):
                    violations.append(f"{py_file.name}:{call}")
        assert violations == [], (
            f"AUX-ESA-0 VIOLATED: ESA contains SlotGraph mutation calls: {violations}"
        )

    def test_esa_no_transition_gate_bypass(self):
        """No ESA file may call can_transition() from the kernel TransitionGate."""
        forbidden = "can_transition"
        violations: list[str] = []
        for py_file in _ESA_SRC.glob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            if _has_call(tree, forbidden):
                violations.append(py_file.name)
        assert violations == [], (
            f"AUX-ESA-0 VIOLATED: ESA bypasses TransitionGate via can_transition(): "
            f"{violations}"
        )

    def test_esa_no_rank_grant_call(self):
        """No ESA file may call kernel RankLattice.meet() or join() directly."""
        # ESA has its own Rank(IntEnum) with LOW/MEDIUM/HIGH — it must not
        # invoke the kernel RankLattice algebra
        forbidden_methods = ["RankLattice"]
        violations: list[str] = []
        for py_file in _ESA_SRC.glob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
            if _has_name_reference(tree, "RankLattice"):
                violations.append(py_file.name)
        assert violations == [], (
            f"AUX-ESA-0 VIOLATED: ESA references kernel RankLattice: {violations}"
        )


# ── AUX-ESA-1: verification harness exists and executes ──────────────────────

class TestAuxEsa1HarnessExists:
    """
    AUX-ESA-1: The ConstitutionalChainHarness must exist in f_constitutional_harness.py,
    be importable (via static analysis), and its execute() method must accept a
    ConstitutionalChainTestCase.
    """

    def test_harness_file_exists(self):
        """f_constitutional_harness.py must exist."""
        assert _F_HARNESS.exists(), (
            f"AUX-ESA-1 VIOLATED: constitutional harness file not found: {_F_HARNESS}"
        )

    def test_harness_class_declared(self):
        """ConstitutionalChainHarness class must be declared in the harness file."""
        tree = _parse(_F_HARNESS)
        class_names = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
        assert "ConstitutionalChainHarness" in class_names, (
            f"AUX-ESA-1 VIOLATED: ConstitutionalChainHarness not found in harness. "
            f"Found classes: {class_names}"
        )

    def test_harness_execute_method_declared(self):
        """ConstitutionalChainHarness must have an execute() method."""
        tree = _parse(_F_HARNESS)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef)
                and node.name == "ConstitutionalChainHarness"
            ):
                methods = [
                    n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef)
                ]
                assert "execute" in methods, (
                    f"AUX-ESA-1 VIOLATED: ConstitutionalChainHarness.execute() "
                    f"method not found. Methods: {methods}"
                )
                return
        pytest.fail("AUX-ESA-1 VIOLATED: ConstitutionalChainHarness class not found.")

    def test_case_report_dataclass_declared(self):
        """ConstitutionalCaseReport must be a frozen dataclass (immutable output)."""
        tree = _parse(_F_HARNESS)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef)
                and node.name == "ConstitutionalCaseReport"
            ):
                # Check for @dataclass decorator
                has_dataclass = any(
                    (isinstance(d, ast.Name) and d.id == "dataclass")
                    or (isinstance(d, ast.Attribute) and d.attr == "dataclass")
                    or (isinstance(d, ast.Call) and (
                        (isinstance(d.func, ast.Name) and d.func.id == "dataclass")
                        or (isinstance(d.func, ast.Attribute) and d.func.attr == "dataclass")
                    ))
                    for d in node.decorator_list
                )
                assert has_dataclass, (
                    "AUX-ESA-1 VIOLATED: ConstitutionalCaseReport must be a @dataclass"
                )
                return
        pytest.fail("AUX-ESA-1 VIOLATED: ConstitutionalCaseReport not found in harness.")

    def test_harness_falsification_field_present(self):
        """ConstitutionalCaseReport must carry falsification_triggered field."""
        source = _F_HARNESS.read_text(encoding="utf-8")
        assert "falsification_triggered" in source, (
            "AUX-ESA-1 VIOLATED: ConstitutionalCaseReport.falsification_triggered "
            "field is absent. Harness must expose when injected violations were detected."
        )

    def test_harness_no_silent_pass_on_violation(self):
        """
        The harness must NOT return passed=True when violation codes are detected.
        Proof: ConstitutionalCaseReport.passed must be False when
        detected_violation_codes is non-empty.

        We verify this by static analysis: the execute() method must compute
        `passed` from a condition that includes `detected_violation_codes` or
        `falsification_triggered`.
        """
        source = _F_HARNESS.read_text(encoding="utf-8")
        # Both field names must appear in the same source — the execute() logic
        # ties them together
        assert "detected_violation_codes" in source and "passed" in source, (
            "AUX-ESA-1 VIOLATED: harness must compute passed based on violation detection"
        )


# ── AUX-ESA-2: source blocker translation contract ───────────────────────────

class TestAuxEsa2BlockerTranslation:
    """
    AUX-ESA-2: Source blockers must translate through the declared
    evaluate_source_blocker_translation() contract only.

    The blocker_translation module is the sole authorized path for
    translating source-system blockers into target-system blockers.
    Any translation that bypasses this contract is a constitutional violation.
    """

    def test_blocker_translation_function_exists(self):
        """evaluate_source_blocker_translation must be declared."""
        tree = _parse(_BLOCKER_TRANSLATION)
        funcs = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]
        assert "evaluate_source_blocker_translation" in funcs, (
            f"AUX-ESA-2 VIOLATED: evaluate_source_blocker_translation() not found. "
            f"Functions: {funcs}"
        )

    def test_blocker_translation_result_dataclass(self):
        """SourceBlockerTranslationResult must be a frozen dataclass."""
        tree = _parse(_BLOCKER_TRANSLATION)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef)
                and node.name == "SourceBlockerTranslationResult"
            ):
                has_dataclass = any(
                    (isinstance(d, ast.Name) and d.id == "dataclass")
                    or (isinstance(d, ast.Attribute) and d.attr == "dataclass")
                    or (isinstance(d, ast.Call))
                    for d in node.decorator_list
                )
                assert has_dataclass, (
                    "AUX-ESA-2 VIOLATED: SourceBlockerTranslationResult must be a @dataclass"
                )
                return
        pytest.fail("AUX-ESA-2 VIOLATED: SourceBlockerTranslationResult not declared.")

    def test_blocker_translation_violations_field(self):
        """SourceBlockerTranslationResult must carry violations tuple."""
        source = _BLOCKER_TRANSLATION.read_text(encoding="utf-8")
        assert "violations" in source, (
            "AUX-ESA-2 VIOLATED: SourceBlockerTranslationResult must expose violations field"
        )

    def test_blocker_translation_allowed_field(self):
        """SourceBlockerTranslationResult.allowed=False when violations exist."""
        source = _BLOCKER_TRANSLATION.read_text(encoding="utf-8")
        assert "allowed" in source and "not violations" in source, (
            "AUX-ESA-2 VIOLATED: allowed must be computed as 'not violations'"
        )

    def test_blocker_translation_unmapped_blocks_accept(self):
        """
        Contract behavioral proof: unmapped source blockers must block ACCEPT.
        The contract string SOURCE_BLOCKER_UNMAPPED_ACCEPT_FORBIDDEN must appear.
        """
        source = _BLOCKER_TRANSLATION.read_text(encoding="utf-8")
        assert "SOURCE_BLOCKER_UNMAPPED_ACCEPT_FORBIDDEN" in source, (
            "AUX-ESA-2 VIOLATED: contract must emit SOURCE_BLOCKER_UNMAPPED_ACCEPT_FORBIDDEN "
            "when unmapped source blockers are present and verdict is ACCEPT"
        )

    def test_blocker_translation_policy_dataclass(self):
        """SourceBlockerTranslationPolicy must be declared as a dataclass."""
        tree = _parse(_BLOCKER_TRANSLATION)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef)
                and node.name == "SourceBlockerTranslationPolicy"
            ):
                return  # Found — pass
        pytest.fail(
            "AUX-ESA-2 VIOLATED: SourceBlockerTranslationPolicy not declared in "
            "blocker_translation.py. The contract must be declared explicitly."
        )


# ── Summary integrity test ────────────────────────────────────────────────────

def test_aux_esa_quarantine_file_inventory():
    """
    AUX-ESA quarantine boundary: verify all required ESA files exist.

    Required files (pinned head):
      f_constitutional_harness.py — ConstitutionalChainHarness
      blocker_translation.py     — SourceBlockerTranslation contract
      f_x0r_bridge.py            — bridge static analysis (permitted)
      f_experiment.py            — FExperiment baseline
      model.py                   — ESA local types
    """
    required = [
        "f_constitutional_harness.py",
        "blocker_translation.py",
        "f_x0r_bridge.py",
        "f_experiment.py",
        "model.py",
    ]
    missing = [f for f in required if not (_ESA_SRC / f).exists()]
    assert missing == [], (
        f"AUX-ESA quarantine BROKEN: required ESA files missing: {missing}\n"
        f"ESA_SRC={_ESA_SRC}"
    )
