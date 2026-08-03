#!/usr/bin/env python3
"""C12 early-stop state diagnostic.

Runs scripts.demo_ayat_al_dayn.run_all() in the current process and
emits, for every token, its early-stop status and the fields that
identify it. Meant to be invoked twice:
  1. In a fresh subprocess (clean baseline)
  2. After running a suspect test prefix (polluted state)

The diff of these two snapshots identifies the exact tokens whose
early-stop status flipped.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def snapshot(out_path: Path) -> dict:
    from scripts.demo_ayat_al_dayn import run_all, generate_taaqol_layer_csv
    import csv
    import io

    results = run_all(verbose=False)
    csv_text = generate_taaqol_layer_csv(results)
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)

    # A token is "early-stopped" iff any of its rows has inflection_skipped_reason set
    per_token: dict[str, dict] = {}
    for r in rows:
        tid = r["token_index"]
        if tid not in per_token:
            per_token[tid] = {
                "token_index": tid,
                "surface": r.get("original_surface", ""),
                "normalized_surface": r.get("normalized_surface", ""),
                "word_class": r.get("word_class", ""),
                "word_class_verdict": r.get("word_class_verdict", ""),
                "inflection_skipped_reason": "",
                "pipeline_verdict": r.get("pipeline_verdict", ""),
                "layer_states": [],
                "runtime_failure_code": r.get("runtime_failure_code", ""),
                "runtime_taaqol_commit": r.get("runtime_taaqol_commit", ""),
                "runtime_hokom_commit": r.get("runtime_hokom_commit", ""),
            }
        # inflection_skipped_reason is per-row; capture first non-empty
        if r.get("inflection_skipped_reason") and not per_token[tid]["inflection_skipped_reason"]:
            per_token[tid]["inflection_skipped_reason"] = r["inflection_skipped_reason"]
        per_token[tid]["layer_states"].append({
            "layer_id": r.get("layer_id", ""),
            "layer_name": r.get("layer_name", ""),
            "layer_state": r.get("layer_state", ""),
        })

    early_stop_ids = sorted(
        [t for t, d in per_token.items() if d["inflection_skipped_reason"]],
        key=lambda x: int(x),
    )
    not_early_stop_ids = sorted(
        [t for t, d in per_token.items() if not d["inflection_skipped_reason"]],
        key=lambda x: int(x),
    )

    result = {
        "totals": {
            "tokens": len(per_token),
            "early_stops": len(early_stop_ids),
            "not_early_stops": len(not_early_stop_ids),
        },
        "early_stop_token_ids": early_stop_ids,
        "not_early_stop_token_ids": not_early_stop_ids,
        "per_token": {tid: {
            "surface": per_token[tid]["surface"],
            "word_class": per_token[tid]["word_class"],
            "inflection_skipped_reason": per_token[tid]["inflection_skipped_reason"],
            "pipeline_verdict": per_token[tid]["pipeline_verdict"],
        } for tid in sorted(per_token.keys(), key=lambda x: int(x))},
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def diff(fresh: dict, polluted: dict) -> dict:
    fresh_ids = set(fresh["early_stop_token_ids"])
    polluted_ids = set(polluted["early_stop_token_ids"])
    lost = sorted(fresh_ids - polluted_ids, key=lambda x: int(x))
    gained = sorted(polluted_ids - fresh_ids, key=lambda x: int(x))
    changed = lost + gained
    return {
        "fresh_early_stops": fresh["totals"]["early_stops"],
        "polluted_early_stops": polluted["totals"]["early_stops"],
        "changed_token_count": len(changed),
        "lost_early_stops_polluted": [
            {"token_id": t, "surface": fresh["per_token"].get(t, {}).get("surface"),
             "fresh_reason": fresh["per_token"].get(t, {}).get("inflection_skipped_reason"),
             "polluted_reason": polluted["per_token"].get(t, {}).get("inflection_skipped_reason"),
             "fresh_verdict": fresh["per_token"].get(t, {}).get("pipeline_verdict"),
             "polluted_verdict": polluted["per_token"].get(t, {}).get("pipeline_verdict")}
            for t in lost
        ],
        "gained_early_stops_polluted": [
            {"token_id": t, "surface": polluted["per_token"].get(t, {}).get("surface")}
            for t in gained
        ],
    }


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
    out_dir = REPO / "reports/taaqol_full_integration/c12_runtime_output"
    if action == "snapshot":
        label = sys.argv[2] if len(sys.argv) > 2 else "fresh"
        out = snapshot(out_dir / f"early_stops_{label}.json")
        print(json.dumps({"label": label, "totals": out["totals"]}, ensure_ascii=False, indent=2))
        return 0
    if action == "diff":
        fresh = json.loads((out_dir / "early_stops_fresh.json").read_text())
        polluted = json.loads((out_dir / "early_stops_polluted.json").read_text())
        d = diff(fresh, polluted)
        (out_dir / "early_stops_diff.json").write_text(json.dumps(d, ensure_ascii=False, indent=2))
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return 0 if d["changed_token_count"] == 0 else 3
    print(f"unknown action: {action}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
