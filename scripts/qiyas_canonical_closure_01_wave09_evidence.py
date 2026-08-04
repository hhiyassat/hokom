#!/usr/bin/env python3
"""Wave09 evidence — real 5-span AnswerAudit vertical + integrity snapshot.

Reads the same real Ayat corpus, runs the wave09 chain (which invokes
the native `AnswerAudit` engine per span via a deterministic
`ModelClient`), and persists the per-span audit records + live
integrity snapshot.

Outputs under reports/qiyas_hokom_taaqol_canonical_closure_01/:

  WAVE09_ANSWER_AUDIT_EXECUTION.json
  WAVE09_ANSWER_AUDIT_INTEGRITY_SNAPSHOT.json
  WAVE09_CLOSURE_SUMMARY.md
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
from pipeline.taaqol_integration.audit_layer.wave09_answer_audit_chain import (  # noqa: E402
    execute_wave09_answer_audit_chain,
)
from pipeline.taaqol_integration.audit_layer.answer_audit_integrity import (  # noqa: E402
    ANSWER_AUDIT_DECLARED_COUNTERS,
    build_answer_audit_integrity_snapshot,
)
from pipeline.taaqol_integration.audit_layer.answer_audit_adapter import (  # noqa: E402
    _VENDOR_SHA,
)


def main() -> int:
    out_dir = REPO / "reports" / "qiyas_hokom_taaqol_canonical_closure_01"
    out_dir.mkdir(parents=True, exist_ok=True)

    cu, sp = _run_full_ayat_and_produce_spans()
    result = execute_wave09_answer_audit_chain(cu, sp)
    if not result["vendor_available"]:
        print("vendor unavailable — cannot run wave09; aborting")
        return 1

    # ── Execution artifact ─────────────────────────────────────────────
    payload = {
        "schema_version": "1.0.0",
        "vendor_sha": _VENDOR_SHA,
        "wave": "wave_9",
        "corpus_id": "AYAT_AL_DAYN_5_SPANS",
        "answer_audit_native_call_count": result["counters"][
            "answer_audit_native_call_count"
        ],
        "answer_audit_success_count": result["counters"][
            "answer_audit_success_count"
        ],
        "answer_audit_integration_failure_count": result["counters"][
            "answer_audit_integration_failure_count"
        ],
        "answer_audit_certificate_allowed_count": result["counters"][
            "answer_audit_certificate_allowed_count"
        ],
        "per_span_answer_audit": sorted(
            result["answer_audit_per_span"],
            key=lambda r: r["span_id"],
        ),
    }
    (out_dir / "WAVE09_ANSWER_AUDIT_EXECUTION.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    exec_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()).hexdigest()

    # ── Integrity snapshot ─────────────────────────────────────────────
    pipeline_root = REPO / "pipeline"
    snap = build_answer_audit_integrity_snapshot(
        [pipeline_root], result["answer_audit_per_span"],
    )
    for name, entry in snap["counter_evidence"].items():
        if "sites" in entry:
            entry["sites"] = sorted(entry["sites"])
        if "violating_records" in entry:
            entry["violating_records"] = sorted(
                entry["violating_records"],
                key=lambda d: (d.get("span_id") or "",),
            )
    (out_dir / "WAVE09_ANSWER_AUDIT_INTEGRITY_SNAPSHOT.json").write_text(
        json.dumps(snap, indent=2, sort_keys=True) + "\n"
    )
    integrity_hash = hashlib.sha256(
        json.dumps(snap, sort_keys=True).encode()).hexdigest()

    # ── Closure summary ────────────────────────────────────────────────
    lines = [
        "# QIYAS-...-CANONICAL-CLOSURE-01 Wave09 — AnswerAudit Closure",
        "",
        "**Status:** `IMPLEMENTED_PENDING_INDEPENDENT_AUDIT`",
        "**Wave09 scope:** native AnswerAudit deterministic engine +",
        "                 real 5-span vertical + live integrity.",
        "",
        "## Vendor pin",
        "",
        f"`{_VENDOR_SHA}` (unchanged since Wave08).",
        "",
        "## AnswerAudit native runtime",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| answer_audit_native_call_count | {result['counters']['answer_audit_native_call_count']} |",
        f"| answer_audit_success_count | {result['counters']['answer_audit_success_count']} |",
        f"| answer_audit_integration_failure_count | {result['counters']['answer_audit_integration_failure_count']} |",
        f"| answer_audit_certificate_allowed_count | {result['counters']['answer_audit_certificate_allowed_count']} |",
        "",
        "## Per-span outcomes (5)",
        "",
        "| span_id | gate_state | successor_present | certificate_allowed |",
        "|---------|------------|--------------------|----------------------|",
    ]
    for rec in sorted(result["answer_audit_per_span"], key=lambda r: r["span_id"]):
        lines.append(
            f"| `{rec['span_id']}` | {rec['gate_state']} | "
            f"{rec['successor_present']} | {rec['certificate_allowed']} |"
        )
    lines += [
        "",
        "## Live integrity counters",
        "",
        "| Counter | Observed | Domain |",
        "|---------|----------|--------|",
    ]
    for name in sorted(ANSWER_AUDIT_DECLARED_COUNTERS):
        obs = snap["counters"].get(name, "MISSING")
        dom = snap["counter_evidence"].get(name, {}).get(
            "measurement_domain", "?"
        )
        lines.append(f"| `{name}` | {obs} | {dom} |")
    lines += [
        "",
        f"**meta.HARDCODED_ZERO_COUNTER_COUNT:** {snap['meta']['HARDCODED_ZERO_COUNTER_COUNT']}",
        f"**meta.UNMEASURED_COUNTER_COUNT:** {snap['meta']['UNMEASURED_COUNTER_COUNT']}",
        f"**meta.COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT:** {snap['meta']['COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT']}",
        "",
        "## Artifact hashes",
        "",
        f"- WAVE09_ANSWER_AUDIT_EXECUTION.json — sha256={exec_hash}",
        f"- WAVE09_ANSWER_AUDIT_INTEGRITY_SNAPSHOT.json — sha256={integrity_hash}",
        "",
        "## What Wave09 does NOT do",
        "",
        "* Does NOT implement GPT-R8 runtime (still Phase H+I — deferred).",
        "* Does NOT invoke a live provider — deterministic ModelClient only.",
        "* Does NOT self-declare `VERIFIED_CLOSED`.",
        "* Does NOT allow `certificate_allowed = True` on any outcome",
        "  (docs/56 §2 B4).",
        "",
    ]
    (out_dir / "WAVE09_CLOSURE_SUMMARY.md").write_text("\n".join(lines))

    print(f"Wrote 3 Wave09 artifacts to {out_dir}")
    print(f"  answer_audit_native_call_count = "
          f"{result['counters']['answer_audit_native_call_count']}")
    print(f"  execution sha256[:16] = {exec_hash[:16]}")
    print(f"  integrity sha256[:16] = {integrity_hash[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
