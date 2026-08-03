from __future__ import annotations
import csv, io, json
from .ledger import ExecutionLedger
from .models import StageExecutionRecord

def ledger_to_json(ledger: ExecutionLedger) -> str:
    summary = ledger.summary()
    return json.dumps({
        "ledger_id": ledger.ledger_id,
        "analysis_id": ledger.analysis_id,
        "engine": ledger.engine,
        "scope": ledger.scope,
        "subject_ref": ledger.subject_ref,
        "created_at": ledger.created_at,
        "summary": {
            "total_stages": summary.total_stages,
            "executed_approved": summary.executed_approved,
            "executed_deferred": summary.executed_deferred,
            "executed_blocked": summary.executed_blocked,
            "not_opened": summary.not_opened,
            "not_applicable": summary.not_applicable,
            "forbidden": summary.forbidden,
            "runtime_errors": summary.runtime_errors,
            "highest_reached_stage": summary.highest_reached_stage,
            "stop_reason": summary.stop_reason,
            "active_residuals": summary.active_residuals,
            "scope_violations": summary.scope_violations,
        },
        "records": ledger.to_csv_rows(),
    }, ensure_ascii=False, indent=2)

def ledger_to_csv(ledger: ExecutionLedger) -> str:
    rows = ledger.to_csv_rows()
    if not rows:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()
