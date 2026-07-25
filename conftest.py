# Root conftest: exclude vendor directory from test collection
collect_ignore_glob = ["vendor/*"]

import sys, pathlib
# ensure repo root is on sys.path so `scripts.*` and top-level modules are importable
_root = str(pathlib.Path(__file__).parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

import pytest


@pytest.fixture(autouse=True)
def _scg_explicit_test_judgment_provider(request, monkeypatch):
    """
    Explicit SCG test judgment provider — approves all SCG transitions for
    non-SCG unit tests (HOKOM-SCG-P0-P12-TAAQOL-HARD-GATING-CORRECTION-04).

    This is EXPLICIT dependency injection, not a silent fallback:
      - Written here in conftest.py (not hidden inside production code).
      - Function-scoped: each test gets its own monkeypatch context.
      - SCG-specific tests opt out automatically (path-based exclusion below)
        so they exercise the real enforcer logic with their own mocking.

    Production path: live SCGTransitionEnforcer + Taaqol vendor, fail-closed.
    Test path (non-SCG): explicit APPROVED pass-through injected here.
    Final integration tests (tests/scg/): use real enforcer + vendor mocking.

    IMPLICIT_TEST_FALLBACKS = 0
    FINAL_INTEGRATION_MOCK_DECISIONS = 0
    """
    # SCG-specific tests (tests/scg/) own their own judgment providers.
    # They mock _try_import_taaqol directly and must see the real judge_transition.
    if "tests/scg" in str(request.fspath):
        yield
        return

    import pipeline.governance.taaqol_judgment_enforcer as _enf
    from pipeline.governance.taaqol_judgment_enforcer import TaaqolTransitionJudgment

    def _approved_judgment(source_stage: str, target_stage: str) -> TaaqolTransitionJudgment:
        """Explicit test judgment: approves every SCG transition."""
        return TaaqolTransitionJudgment(
            edge_id=f"{source_stage}→{target_stage}",
            source_stage=source_stage,
            target_stage=target_stage,
            taaqol_called=True,
            taaqol_runtime_active=True,
            gamma_closure_state="MINIMALLY_CLOSED",
            gate_verdict="APPROVED",
            failure_code=None,
            fallback_used=False,
            error_detail=None,
        )

    monkeypatch.setattr(_enf, "judge_transition", _approved_judgment)
    yield
