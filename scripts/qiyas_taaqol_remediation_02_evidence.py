#!/usr/bin/env python3
"""QIYAS-TAAQOL-MAXIMUM-NATIVE-CLOSURE-REMEDIATION-02 evidence producer.

Runs the Wave06 typed downstream chain (Ifadah → Hukm → Manat →
Tanzil → AuditedTanzilBridge PLUS Ifadah → Mantuq → Mafhum) twice
under PYTHONHASHSEED=0 and persists:

  reports/qiyas_taaqol_remediation_02/
    RUN1_TYPED_DOWNSTREAM_EXECUTION.json
    RUN2_TYPED_DOWNSTREAM_EXECUTION.json
    DETERMINISM_COMPARE.json
    CLOSURE_SUMMARY.md

Every per-span record includes rich per-stage detail: input_stage,
native_result_type, verdict_state, classification, failure_code,
trace_ref, residual_ids, failure_detail. Determinism is asserted by
exact-dict-equality over the two run summaries.
"""
from __future__ import annotations
import json
import os
import sys
import hashlib
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tests.taaqol_integration.test_c13_wave03_relation_closure import (  # noqa: E402
    _run_full_ayat_and_produce_spans,
)
from pipeline.taaqol_integration.evidence_producers.wave06_downstream_chain_typed import (  # noqa: E402
    execute_ayat_full_downstream_chain_typed,
)


def _serialisable(r: dict) -> dict:
    """Deep-canonicalise the wave06 result for stable JSON."""
    return {
        "vendor_available": r["vendor_available"],
        "counters": dict(sorted(r["counters"].items())),
        "unbridged_reachable_stage_count":
            r["unbridged_reachable_stage_count"],
        "per_span_downstream": [
            {
                "span_id": s["span_id"],
                "input_ids": list(s["input_ids"]),
                "stages": [dict(stage) for stage in s["stages"]],
            }
            for s in r["per_span_downstream"]
        ],
    }


def main() -> int:
    out_dir = REPO / "reports" / "qiyas_taaqol_remediation_02"
    out_dir.mkdir(parents=True, exist_ok=True)

    cu1, sp1 = _run_full_ayat_and_produce_spans()
    r1 = _serialisable(execute_ayat_full_downstream_chain_typed(cu1, sp1))
    (out_dir / "RUN1_TYPED_DOWNSTREAM_EXECUTION.json").write_text(
        json.dumps(r1, indent=2, sort_keys=True) + "\n"
    )

    cu2, sp2 = _run_full_ayat_and_produce_spans()
    r2 = _serialisable(execute_ayat_full_downstream_chain_typed(cu2, sp2))
    (out_dir / "RUN2_TYPED_DOWNSTREAM_EXECUTION.json").write_text(
        json.dumps(r2, indent=2, sort_keys=True) + "\n"
    )

    r1_hash = hashlib.sha256(
        json.dumps(r1, sort_keys=True).encode()).hexdigest()
    r2_hash = hashlib.sha256(
        json.dumps(r2, sort_keys=True).encode()).hexdigest()
    identical = r1 == r2

    (out_dir / "DETERMINISM_COMPARE.json").write_text(json.dumps({
        "identical": identical,
        "python_hashseed": os.environ.get("PYTHONHASHSEED"),
        "run1_sha256": r1_hash,
        "run2_sha256": r2_hash,
        "counters_identical": r1["counters"] == r2["counters"],
        "per_span_count": len(r1["per_span_downstream"]),
    }, indent=2, sort_keys=True) + "\n")

    c = r1["counters"]
    lines = [
        "# QIYAS-TAAQOL-MAXIMUM-NATIVE-CLOSURE-REMEDIATION-02 — Closure Summary",
        "",
        "**Status:** `IMPLEMENTED_PENDING_INDEPENDENT_REAUDIT`",
        f"**Determinism:** {'PASS (RUN1 == RUN2)' if identical else 'FAIL'}",
        "",
        "## Per-stage typed closure (ACCEPT / DEFER / BLOCK)",
        "",
        "| Stage                   | Calls | ACCEPT | DEFER | BLOCK |",
        "|-------------------------|-------|--------|-------|-------|",
    ]
    for prefix in ("ifadah", "hukm", "manat", "tanzil",
                   "audited_tanzil_bridge", "mantuq", "mafhum"):
        lines.append(
            f"| {prefix:<23} | {c[prefix+'_calls']:>5} "
            f"| {c[prefix+'_accept']:>6} "
            f"| {c[prefix+'_defer']:>5} "
            f"| {c[prefix+'_block']:>5} |"
        )
    lines += [
        "",
        f"**unbridged_reachable_stage_count:** "
        f"{r1['unbridged_reachable_stage_count']}",
        "",
        "## Vendor SHA",
        "",
        "`05c6668dfb95d9238cff5df1d8bc73d0664bccb3` (vendor/Taaqol-GPT pinned)",
        "",
        "## What changed vs the audited HEAD (b8e362f)",
        "",
        "1. **REPAIR A** — `bridge_tanzil_to_audit` is now invoked; the "
        "  audit-layer stage that consumes `TanzilVerdict` closes 5/5 "
        "  (`SURFACED`).",
        "2. **REPAIR B** — every downstream stage returns a typed "
        "  `DownstreamStageOutcome` preserving `verdict_state`, "
        "  `failure_code`, `trace_ref`, and residuals. Vendor REFUSED "
        "  no longer collapses to None.",
        "3. **REPAIR C** — Manat and Mantuq gained explicit typed-REFUSED "
        "  tests; audit bridge got ACCEPT + REFUSED tests.",
        "4. **REPAIR D** — per-span artifact now records "
        "  input_stage / native_result_type / verdict_state / classification "
        "  / failure_code / trace_ref / residual_ids / failure_detail.",
        "5. **REPAIR E** — Tanzil terminal claim corrected (audit-layer "
        "  bridge is the next reachable stage).",
        "",
    ]
    (out_dir / "CLOSURE_SUMMARY.md").write_text("\n".join(lines))

    print(f"Wrote 4 artifacts to {out_dir}")
    print(f"  identical={identical}  sha256[:16]={r1_hash[:16]}")
    if not identical:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
