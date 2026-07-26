# Root conftest: exclude vendor directory from test collection
collect_ignore_glob = ["vendor/*"]

import sys, pathlib
# ensure repo root is on sys.path so `scripts.*` and top-level modules are importable
_root = str(pathlib.Path(__file__).parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

import pytest


@pytest.fixture
def scg_approved_judgment_provider(monkeypatch):
    """
    Named SCG judgment provider — approves all SCG transitions.

    HOKOM-SCG-P0-P12-TAAQOL-HARD-GATING-MACOS-CANONICAL-VALIDATION-05:
    This fixture is NOT autouse (AUTOUSE_JUDGMENT_FIXTURES=0).

    Permitted model:
      unit tests:    explicit fixture request via parameter list
      live tests:    real vendor only — do NOT request this fixture

    On the canonical macOS/Python 3.12.4 environment the real Taaqol vendor
    is available and returns APPROVED for valid transitions, so no explicit
    injection is required for integration tests.  This fixture exists for
    isolated sub-component unit tests that run on Python 3.10 (no vendor)
    and need APPROVED pass-through to exercise linguistic logic in isolation.

    AUTOUSE_JUDGMENT_FIXTURES = 0
    IMPLICIT_TEST_JUDGMENT_INJECTION = 0
    LIVE_TESTS_RECEIVING_INJECTED_JUDGMENTS = 0
    FINAL_INTEGRATION_MOCK_DECISIONS = 0
    """
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
