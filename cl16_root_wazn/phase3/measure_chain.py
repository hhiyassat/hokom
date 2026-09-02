#!/usr/bin/env python3
"""CL-16 Phase 3 — measured yield of the root-candidate chain.

MEASURED_NOT_PRESET: every number this prints comes from reading the pinned
artifacts in this run. Nothing is copied from a document.

    python3 measure_chain.py [--json OUT.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import root_candidate_chain as C  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()

    chain = C.RootCandidateChain()
    codes = collections.Counter()
    licensed: list[tuple[str, str, str]] = []
    collisions: list[str] = []

    for key, row in chain._candidates.items():
        ev = chain.assess(key)
        codes[f"{ev.verdict}:{ev.reason_code}"] += 1
        if ev.verdict == C.Verdict.LICENSED:
            licensed.append((ev.root, ev.baab, ev.rank.name))
        elif ev.reason_code == C.ChainCode.CLOSED_FORM_COLLISION:
            collisions.append(key)

    summary = chain.run_summary
    total = len(chain._candidates)
    print("# المحور: سلسلة الجذر المرشح — CL-16 المرحلة الثالثة\n")
    print("## البصمات المتحقّقة")
    for role, sha in chain.provenance:
        print(f"  {role:32} {sha}")
    print(f"\n  شهودُ القائمة المغلقة = {', '.join(chain.closed_form_witness) or 'لا شاهد'}")

    print("\n## مصدر المرشحات — بحدّه المعلن")
    print(f"  analysis_status = {summary['analysis_status']}")
    print(f"  مرشحات مرخّصة   = {summary['root_candidate_count']}")
    print(f"  مرشحات مؤجّلة   = {summary['deferred_root_candidate_count']}")
    npc = summary["null_pass_count"]
    print(f"  النموذج الصفريّ = z {npc['z']:.2f} ، p {npc['empirical_p']:.4f}")

    print(f"\n## مخارج السلسلة على {total} مدخلة")
    for code, n in codes.most_common():
        print(f"  {n:5}  {code}")

    print(f"\n## ما رُخّص ({len(licensed)})")
    for root, baab, rank in sorted(licensed):
        print(f"  {root:8} {rank:18} {baab}")

    print(f"\n## ما رفضته القائمة المغلقة ({len(collisions)})")
    print("  " + " ، ".join(sorted(collisions)))

    print("\n## ما لا تثبته هذه السلسلة")
    print("  ROOT_PROVEN        = NO — الرتبة من جدول الاعتماد وحده")
    print("  WAZN               = NO — لا يُطلب من هذه المرحلة ولا تملكه")
    print("  CL16_CLOSED        = NO")
    print("  جبر: CANDIDATE ≠ ROOT   ،   PRESENCE ≠ CERTIFICATION")
    print("  جبر: SKELETON_MATCH ≠ ROOT_PROOF   ،   CORROBORATION ↛ RANK+1")

    if args.json:
        args.json.write_text(json.dumps({
            "measured": True,
            "total_rows": total,
            "outcomes": dict(codes),
            "licensed": [{"root": r, "baab": b, "rank": k} for r, b, k in sorted(licensed)],
            "closed_form_collisions": sorted(collisions),
            "provenance": [list(p) for p in chain.provenance],
            "cl16_closed": C.CL16_CLOSED,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nكُتب القياس في {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
