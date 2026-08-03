from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from pipeline.execution_ledger.scope import validate_token_ledger, build_token_ledger_template
from pipeline.execution_ledger.models import StageStatus

def test_build_token_ledger_template_19_rows():
    records = build_token_ledger_template(
        surface="تَدَايَنْتُمْ",
        analysis_id="test-analysis",
        executed_stages={},
    )
    assert len(records) == 19, f"Expected 19 records, got {len(records)}"

def test_build_token_ledger_higher_scope_not_applicable():
    records = build_token_ledger_template("test", "aid", {})
    higher_scope_ids = {
        "P6_VERBAL_SIGNIFIED_ALONE", "P7_COMPOSITION_READINESS", "P8_AMIL_MAMUL",
        "P9_SENTENCE_GEOMETRY", "P10_RELATION_GEOMETRY", "P11_IRAB_GEOMETRY",
        "P12_IFADAH_SPEECH_FORCE",
    }
    for rec in records:
        if rec.stage_id in higher_scope_ids:
            assert rec.status == StageStatus.NOT_APPLICABLE_AT_TOKEN_SCOPE, (
                f"Stage {rec.stage_id} should be NOT_APPLICABLE_AT_TOKEN_SCOPE in token ledger"
            )

def test_validate_token_ledger_no_violations_on_template():
    records = build_token_ledger_template("test", "aid", {})
    # The template doesn't execute higher-scope stages, so no scope violations
    violations = validate_token_ledger(records)
    scope_violations = [v for v in violations if "TOKEN_SCOPE_AS_RELATION_SCOPE" in v]
    assert not scope_violations, f"Unexpected scope violations: {scope_violations}"
