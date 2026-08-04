#!/usr/bin/env python3
"""QIYAS-HOKOM-TAAQOL-MAQAYIS-CGPS01-FULL-MAXIMUM-CANONICAL-CLOSURE-01 evidence.

Runs the Wave06 typed downstream chain twice under PYTHONHASHSEED=0,
persists the run artifacts, and additionally emits the live integrity
snapshot from :mod:`pipeline.taaqol_integration.integrity_measurement`.

Outputs in reports/qiyas_hokom_taaqol_canonical_closure_01/:

  RUN1_TYPED_DOWNSTREAM_EXECUTION.json
  RUN2_TYPED_DOWNSTREAM_EXECUTION.json
  DETERMINISM_COMPARE.json
  INTEGRITY_SNAPSHOT.json
  CLOSURE_SUMMARY.md
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
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
from pipeline.taaqol_integration.integrity_measurement import (  # noqa: E402
    build_integrity_snapshot, DECLARED_COUNTERS,
)


def _serialisable(r: dict) -> dict:
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
    out_dir = REPO / "reports" / "qiyas_hokom_taaqol_canonical_closure_01"
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

    # ── Live integrity snapshot ────────────────────────────────────────
    pipeline_root = REPO / "pipeline"
    snap = build_integrity_snapshot(
        [pipeline_root], r1["per_span_downstream"],
    )
    # Sort site tuples so JSON is deterministic
    for name, entry in snap["counter_evidence"].items():
        if "sites" in entry:
            entry["sites"] = sorted(entry["sites"])
        if "violating_records" in entry:
            entry["violating_records"] = sorted(
                entry["violating_records"],
                key=lambda d: (d.get("span_id", ""), d.get("stage", "")),
            )
    (out_dir / "INTEGRITY_SNAPSHOT.json").write_text(
        json.dumps(snap, indent=2, sort_keys=True) + "\n"
    )
    snap_hash = hashlib.sha256(
        json.dumps(snap, sort_keys=True).encode()).hexdigest()

    # ── Closure summary ────────────────────────────────────────────────
    c = r1["counters"]
    lines = [
        "# QIYAS-HOKOM-TAAQOL-MAQAYIS-CGPS01-FULL-MAXIMUM-CANONICAL-CLOSURE-01",
        "# Closure Summary — Taaqol implementation slice",
        "",
        "**Status:** `IMPLEMENTED_PENDING_INDEPENDENT_AUDIT`",
        f"**Determinism (typed downstream):** {'PASS (RUN1 == RUN2)' if identical else 'FAIL'}",
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
        "## Live integrity snapshot (Phase T1 replacement for decorative counters)",
        "",
        "| Counter | Observed | Domain |",
        "|---------|----------|--------|",
    ]
    for name in sorted(DECLARED_COUNTERS):
        obs = snap["counters"][name]
        dom = snap["counter_evidence"][name]["measurement_domain"]
        lines.append(f"| `{name}` | {obs} | {dom} |")
    lines += [
        "",
        f"**meta.HARDCODED_ZERO_COUNTER_COUNT:** {snap['meta']['HARDCODED_ZERO_COUNTER_COUNT']}",
        f"**meta.UNMEASURED_COUNTER_COUNT:** {snap['meta']['UNMEASURED_COUNTER_COUNT']}",
        f"**meta.COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT:** {snap['meta']['COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT']}",
        "",
        "## Vendor SHA",
        "",
        "`05c6668dfb95d9238cff5df1d8bc73d0664bccb3` (vendor/Taaqol-GPT pinned)",
        "",
        "## What changed vs the reaudit-02 HEAD (7febd11)",
        "",
        "1. **T0** — `.claude/` harness-local files excluded from tracking",
        "   (strict cleanliness gate now returns zero bytes).",
        "2. **T1** — decorative 16-zero `integrity_counters` block",
        "   replaced by a live measurement framework",
        "   (`pipeline/taaqol_integration/integrity_measurement.py`) with",
        "   7 AST/regex source scanners + 9 runtime-record predicates +",
        "   4 structural derivations. Mutation-proof tests cover every rule.",
        "3. **T2** — Wave07 test suite (17 tests) closes the typed-REFUSED",
        "   coverage for Hukm/Tanzil/Mafhum, adds missing-predecessor and",
        "   wrong-type paths, and adds THREE end-to-end BLOCK tests via",
        "   real vendor codes: MANTUQ_BLOCKS_MAFHUM, TAHQIQ_OVERCLAIM,",
        "   NO_MAFHUM_CROSS_DOMAIN_LEAP.",
        "4. **T3** — RelationClosure and Ifadah residual under-reporting",
        "   fixed. Real vendor residuals now propagate through the",
        "   per-span artifact instead of being replaced by `[]`.",
        "5. **T4** — this evidence + Wave07 typed ledger + report-binding",
        "   manifest (two-step: content HEAD, report commit HEAD,",
        "   binding manifest HEAD).",
        "",
        "## Artifact hashes",
        "",
        f"- RUN1_TYPED_DOWNSTREAM_EXECUTION.json — sha256={r1_hash}",
        f"- RUN2_TYPED_DOWNSTREAM_EXECUTION.json — sha256={r2_hash}",
        f"- INTEGRITY_SNAPSHOT.json — sha256={snap_hash}",
        "",
        "## No self-declared VERIFIED_CLOSED",
        "",
        "Per the campaign directive, an implementation session must not",
        "issue the final VERIFIED_CLOSED verdict. A fresh strictly",
        "read-only audit session must be started by the owner against this",
        "branch's HEAD after handoff.",
        "",
    ]
    (out_dir / "CLOSURE_SUMMARY.md").write_text("\n".join(lines))

    print(f"Wrote 5 artifacts to {out_dir}")
    print(f"  identical={identical}  run1_sha256[:16]={r1_hash[:16]}")
    print(f"  integrity_snapshot_sha256[:16]={snap_hash[:16]}")
    if not identical:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
