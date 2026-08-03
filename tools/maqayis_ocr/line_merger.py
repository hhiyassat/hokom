"""
line_merger.py — Maqayis OCR v2

Merges Apple Vision observations that belong to the same visual line.

Apple Vision may split a single printed line into multiple observations
(e.g. a marginalia note alongside the main text, or a wide line split at
a column boundary).  This module groups observations whose vertical centres
are within a tolerance band and merges them into a single OcrLine record.

Input : the "observations" list produced by vision_ocr.swift (already
        sorted top-to-bottom by vision_ocr.swift).
Output: list of merged line dicts matching schemas/line.schema.json
        (minus region_type / review_status, which are filled by downstream
        modules).
"""

from __future__ import annotations
import re
from typing import Any


# ── configuration ─────────────────────────────────────────────────────────────

# Two observations are "on the same line" when their normalised-Y-centre
# difference is below this threshold.  0.008 ≈ 6 px on a 720 pt page at 72 dpi.
SAME_LINE_Y_TOLERANCE = 0.010


# ── helpers ───────────────────────────────────────────────────────────────────

def _centre_y(obs: dict) -> float:
    bb = obs["bounding_box"]
    return bb["y"] + bb["h"] / 2.0


def _merge_bboxes(bboxes: list[dict]) -> dict:
    """Union of all bounding boxes."""
    xs = [b["x"] for b in bboxes]
    ys = [b["y"] for b in bboxes]
    x2 = [b["x"] + b["w"] for b in bboxes]
    y2 = [b["y"] + b["h"] for b in bboxes]
    x = min(xs); y = min(ys)
    return {"x": x, "y": y, "w": max(x2) - x, "h": max(y2) - y}


def _concat_rtl(texts: list[str]) -> str:
    """
    Concatenate text fragments from right-to-left observations.
    Vision may return fragments in visual order (left-to-right on the rendered
    image), but Arabic reads RTL.  We reverse the fragment order so the joined
    text reads correctly.
    """
    return " ".join(reversed(texts)) if len(texts) > 1 else (texts[0] if texts else "")


def _best_candidates(observations: list[dict],
                     field: str,
                     max_candidates: int = 3) -> list[dict]:
    """
    Collect all candidates from every observation in the group, de-duplicate
    by text (keep highest confidence), sort by confidence desc, return top N.
    """
    seen: dict[str, float] = {}
    for obs in observations:
        for cand in obs.get(field, []):
            t = cand.get("text", "")
            c = float(cand.get("confidence", 0))
            if t and c > seen.get(t, -1):
                seen[t] = c
    ranked = sorted(seen.items(), key=lambda kv: kv[1], reverse=True)
    return [{"text": t, "confidence": c} for t, c in ranked[:max_candidates]]


# ── core grouping ─────────────────────────────────────────────────────────────

def _group_into_lines(
    observations: list[dict],
    y_tolerance: float = SAME_LINE_Y_TOLERANCE,
) -> list[list[dict]]:
    """
    Group observations into visual lines using a greedy sweep.
    observations must already be sorted top-to-bottom (highest Y first).
    """
    groups: list[list[dict]] = []

    for obs in observations:
        cy = _centre_y(obs)
        matched = False
        for group in reversed(groups):   # try recent groups first
            group_cy = sum(_centre_y(o) for o in group) / len(group)
            if abs(cy - group_cy) <= y_tolerance:
                group.append(obs)
                matched = True
                break
        if not matched:
            groups.append([obs])

    # Within each group sort by X (right → left for Arabic)
    for group in groups:
        group.sort(key=lambda o: o["bounding_box"]["x"], reverse=True)

    return groups


# ── public API ────────────────────────────────────────────────────────────────

def merge_observations(
    observations: list[dict],
    source_pdf: str,
    pdf_page: int,
    y_tolerance: float = SAME_LINE_Y_TOLERANCE,
) -> list[dict]:
    """
    Convert a flat list of Vision observations into merged OcrLine dicts.

    Parameters
    ----------
    observations : list of observation dicts from vision_ocr.swift JSON
    source_pdf   : e.g. "02.pdf"
    pdf_page     : 1-based page number
    y_tolerance  : max normalised-Y-centre gap to merge

    Returns
    -------
    list of line dicts (sorted top → bottom)
    """
    groups = _group_into_lines(observations, y_tolerance)

    lines: list[dict] = []
    for line_n, group in enumerate(groups, start=1):
        raw_texts       = [o.get("raw_ocr", "")       for o in group if o.get("raw_ocr")]
        corrected_texts = [o.get("corrected_ocr", "")  for o in group if o.get("corrected_ocr")]

        raw_top       = _concat_rtl(raw_texts)       if raw_texts       else ""
        corrected_top = _concat_rtl(corrected_texts)  if corrected_texts else ""

        raw_cands  = _best_candidates(group, "raw_candidates")
        corr_cands = _best_candidates(group, "corrected_candidates")

        # Merge bounding boxes
        bbox = _merge_bboxes([o["bounding_box"] for o in group])

        line_id = f"{source_pdf}:p{pdf_page}:l{line_n:04d}"

        line: dict[str, Any] = {
            "line_id":               line_id,
            "source_pdf":            source_pdf,
            "pdf_page":              pdf_page,
            "bounding_box":          bbox,
            "raw_candidates":        raw_cands,
            "corrected_candidates":  corr_cands,
            "raw_ocr":               raw_top,
            "corrected_ocr":         corrected_top,
            "region_type":           "UNKNOWN",       # filled by page_regions.py
            "review_status":         "AUTO_AGREED",   # updated by entry_parser / review
            "human_text":            None,
            "reviewer":              None,
            "review_date":           None,
            "notes":                 None,
            "observation_ids":       [o.get("observation_index", -1) for o in group],
        }
        lines.append(line)

    return lines


# ── CLI self-test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json, sys

    if len(sys.argv) < 2:
        print("Usage: python line_merger.py <vision_ocr_output.json>")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        page_data = json.load(f)

    lines = merge_observations(
        page_data["observations"],
        source_pdf=page_data["source_pdf"],
        pdf_page=page_data["pdf_page"],
    )

    print(json.dumps(lines, ensure_ascii=False, indent=2))
    print(f"\n[line_merger] {len(page_data['observations'])} observations → {len(lines)} lines",
          file=sys.stderr)
