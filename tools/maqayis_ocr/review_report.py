"""
review_report.py — Maqayis OCR v2

Generates a self-contained HTML review page for one OCR-processed page.

Layout
------
Two-column, RTL-aware:
  Right column : original page image (PNG rendered by vision_ocr.swift)
  Left  column : table of classified lines with:
                   • region type badge
                   • raw OCR text (readonly)
                   • top-3 candidates with confidence bars
                   • corrected OCR text (readonly)
                   • editable human-text textarea
                   • accept / review / reject radio buttons
                   • confidence indicator

Each line gets a colour-coded row:
  GREEN  → AUTO_AGREED   (high confidence, text matches between passes)
  AMBER  → REVIEW_REQUIRED
  BLUE   → ROOT_ENTRY_START
  GREY   → PAGE_HEADER / PAGE_NUMBER / BOOK_HEADING / CHAPTER_HEADING
  PURPLE → POETRY
  RED    → FOOTNOTE (low confidence)

The page stores all edits in JavaScript state and can export a
review_result.json file that gets merged back into the gold dataset.
"""

from __future__ import annotations
import base64
import html
import json
import os
from pathlib import Path
from typing import Any


# ── colour map ────────────────────────────────────────────────────────────────

REGION_COLORS: dict[str, str] = {
    "BOOK_HEADING":     "#e8f0fe",   # light blue
    "CHAPTER_HEADING":  "#d2e3fc",
    "ROOT_ENTRY_START": "#d4f1d4",   # light green
    "MAIN_TEXT":        "#ffffff",
    "POETRY":           "#f0e6ff",   # lavender
    "FOOTNOTE":         "#fff3cd",   # amber
    "PAGE_HEADER":      "#f1f3f4",   # grey
    "PAGE_NUMBER":      "#f1f3f4",
    "UNKNOWN":          "#fce8e6",   # pale red
}

REVIEW_BADGE: dict[str, tuple[str, str]] = {
    "AUTO_AGREED":        ("#188038", "✓ Auto"),
    "REVIEW_REQUIRED":    ("#e37400", "⚠ Review"),
    "MANUALLY_CORRECTED": ("#1a73e8", "✎ Corrected"),
    "APPROVED":           ("#188038", "✔ Approved"),
    "REJECTED":           ("#d93025", "✗ Rejected"),
}


# ── helpers ───────────────────────────────────────────────────────────────────

def _esc(text: str | None) -> str:
    return html.escape(str(text or ""), quote=True)


def _image_b64(png_path: str) -> str | None:
    try:
        with open(png_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except OSError:
        return None


def _conf_bar(confidence: float) -> str:
    pct = int(confidence * 100)
    color = "#188038" if pct >= 75 else "#e37400" if pct >= 45 else "#d93025"
    return (
        f'<div style="display:inline-block;width:{pct}px;max-width:100px;'
        f'height:8px;background:{color};border-radius:4px;"></div>'
        f'<small style="margin-left:4px;color:{color}">{pct}%</small>'
    )


def _candidates_html(candidates: list[dict]) -> str:
    rows = []
    for i, cand in enumerate(candidates[:3]):
        text = cand.get("text", "")
        conf = float(cand.get("confidence", 0))
        rows.append(
            f'<tr><td style="padding:2px 6px;font-size:0.85em;direction:rtl;'
            f'font-family:serif">{_esc(text)}</td>'
            f'<td style="padding:2px 6px">{_conf_bar(conf)}</td></tr>'
        )
    return '<table style="border-collapse:collapse">' + "".join(rows) + "</table>"


# ── line row HTML ──────────────────────────────────────────────────────────────

def _line_row(line: dict, idx: int) -> str:
    lid          = _esc(line.get("line_id", f"line_{idx}"))
    region       = line.get("region_type", "UNKNOWN")
    review_st    = line.get("review_status", "AUTO_AGREED")
    raw_ocr      = _esc(line.get("raw_ocr", ""))
    corr_ocr     = _esc(line.get("corrected_ocr", ""))
    human_text   = _esc(line.get("human_text") or "")

    bg_color     = REGION_COLORS.get(region, "#ffffff")
    badge_color, badge_label = REVIEW_BADGE.get(review_st, ("#555", review_st))

    raw_cands    = _candidates_html(line.get("raw_candidates", []))
    corr_cands   = _candidates_html(line.get("corrected_candidates", []))

    # Bounding box for display
    bb = line.get("bounding_box", {})
    bb_str = f"x={bb.get('x', 0):.3f} y={bb.get('y', 0):.3f} w={bb.get('w', 0):.3f} h={bb.get('h', 0):.3f}"

    return f"""
<tr id="row-{idx}" style="background:{bg_color};border-bottom:1px solid #e0e0e0">
  <td style="padding:6px;font-size:0.8em;color:#555;white-space:nowrap;vertical-align:top">
    <code>{lid}</code><br>
    <span style="background:{bg_color};border:1px solid #ccc;border-radius:3px;
          padding:2px 5px;font-size:0.85em">{_esc(region)}</span><br>
    <span style="background:{badge_color};color:#fff;border-radius:3px;
          padding:2px 5px;font-size:0.8em;margin-top:3px;display:inline-block">{badge_label}</span><br>
    <small style="color:#999">{_esc(bb_str)}</small>
  </td>

  <td style="padding:6px;vertical-align:top">
    <div style="font-size:0.75em;color:#888;margin-bottom:2px">Raw candidates</div>
    {raw_cands}
    <div style="font-size:0.75em;color:#888;margin:4px 0 2px">Corrected candidates</div>
    {corr_cands}
  </td>

  <td style="padding:6px;vertical-align:top;min-width:260px">
    <div style="font-size:0.75em;color:#888;margin-bottom:2px">Corrected OCR (immutable)</div>
    <div style="direction:rtl;font-family:serif;font-size:1.1em;
         background:#f8f9fa;border:1px solid #dadce0;padding:4px 8px;
         border-radius:4px;margin-bottom:6px">{corr_ocr}</div>

    <div style="font-size:0.75em;color:#888;margin-bottom:2px">Human text (editable)</div>
    <textarea id="human-{idx}"
              rows="2"
              style="width:100%;direction:rtl;font-family:serif;font-size:1.05em;
                     border:1px solid #4285f4;border-radius:4px;padding:4px 8px;
                     resize:vertical"
              onchange="markChanged({idx})">{human_text}</textarea>
  </td>

  <td style="padding:6px;vertical-align:top;white-space:nowrap">
    <div style="font-size:0.75em;color:#888;margin-bottom:4px">Status</div>
    <label style="display:block;margin:2px 0">
      <input type="radio" name="status-{idx}" value="APPROVED"
             {'checked' if review_st == 'APPROVED' else ''}
             onchange="setStatus({idx},'APPROVED')"> ✔ Approved
    </label>
    <label style="display:block;margin:2px 0">
      <input type="radio" name="status-{idx}" value="MANUALLY_CORRECTED"
             {'checked' if review_st == 'MANUALLY_CORRECTED' else ''}
             onchange="setStatus({idx},'MANUALLY_CORRECTED')"> ✎ Corrected
    </label>
    <label style="display:block;margin:2px 0">
      <input type="radio" name="status-{idx}" value="REVIEW_REQUIRED"
             {'checked' if review_st == 'REVIEW_REQUIRED' else ''}
             onchange="setStatus({idx},'REVIEW_REQUIRED')"> ⚠ Review
    </label>
    <label style="display:block;margin:2px 0">
      <input type="radio" name="status-{idx}" value="REJECTED"
             {'checked' if review_st == 'REJECTED' else ''}
             onchange="setStatus({idx},'REJECTED')"> ✗ Rejected
    </label>
  </td>
</tr>"""


# ── full page HTML ─────────────────────────────────────────────────────────────

def generate_review_html(
    page_data: dict,
    lines: list[dict],
    root_entries: list[dict],
    png_path: str | None = None,
    reviewer: str = "",
) -> str:
    """
    Generate the full review HTML document.

    Parameters
    ----------
    page_data    : raw dict from vision_ocr.swift JSON
    lines        : classified OcrLine dicts
    root_entries : RootEntry dicts from entry_parser
    png_path     : path to the rendered PNG (overrides page_data["png_tmp_path"])
    reviewer     : reviewer name/id to embed

    Returns
    -------
    HTML string
    """
    source_pdf = page_data.get("source_pdf", "")
    pdf_page   = page_data.get("pdf_page", 0)
    img_hash   = page_data.get("image_hash", "")
    ocr_ts     = page_data.get("ocr_timestamp", "")
    dpi        = page_data.get("dpi", 400)

    title = f"Review — {source_pdf} page {pdf_page}"

    # Image
    actual_png = png_path or page_data.get("png_tmp_path", "")
    img_b64 = _image_b64(actual_png) if actual_png else None
    if img_b64:
        img_tag = (
            f'<img src="data:image/png;base64,{img_b64}" '
            f'style="width:100%;border:1px solid #dadce0" alt="Page scan">'
        )
    else:
        img_tag = '<div style="color:#d93025;padding:20px">⚠ Image not available</div>'

    # Line rows
    rows_html = "".join(_line_row(ln, i) for i, ln in enumerate(lines))

    # Summary stats
    region_counts: dict[str, int] = {}
    review_counts: dict[str, int] = {}
    for ln in lines:
        rt = ln.get("region_type", "UNKNOWN")
        rs = ln.get("review_status", "AUTO_AGREED")
        region_counts[rt] = region_counts.get(rt, 0) + 1
        review_counts[rs] = review_counts.get(rs, 0) + 1

    root_summary = ""
    if root_entries:
        items = []
        for e in root_entries:
            root = e.get("root_letters") or "?"
            otype = e.get("semantic_origin_type", "")
            phrase = e.get("semantic_origin_text") or otype
            items.append(f"<li><b>({root})</b> — {_esc(phrase)}</li>")
        root_summary = "<ul style='margin:0;padding-left:20px'>" + "".join(items) + "</ul>"
    else:
        root_summary = "<em style='color:#888'>No root entries detected on this page</em>"

    # Serialise full data for JS export
    export_data = json.dumps({
        "source_pdf":    source_pdf,
        "pdf_page":      pdf_page,
        "image_hash":    img_hash,
        "ocr_timestamp": ocr_ts,
        "dpi":           dpi,
        "reviewer":      reviewer,
        "lines":         lines,
        "root_entries":  root_entries,
    }, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(title)}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f8f9fa; }}
  .topbar {{ background: #1a73e8; color: #fff; padding: 10px 20px;
             display:flex; align-items:center; justify-content:space-between; }}
  .topbar h1 {{ margin:0; font-size:1.1em; }}
  .layout {{ display: flex; height: calc(100vh - 50px); overflow: hidden; }}
  .col-image {{ flex: 0 0 38%; overflow-y: auto; padding: 12px;
                border-left: 1px solid #dadce0; background: #fff; }}
  .col-review {{ flex: 1; overflow-y: auto; padding: 0; }}
  table.lines {{ width: 100%; border-collapse: collapse; }}
  table.lines th {{ background: #f1f3f4; padding: 8px; font-size: 0.85em;
                    border-bottom: 2px solid #dadce0; text-align: right; }}
  .stats {{ padding: 8px 16px; background: #e8f0fe;
            font-size: 0.85em; border-bottom: 1px solid #c5cae9; }}
  .export-btn {{ background: #188038; color: #fff; border: none; padding: 6px 16px;
                 border-radius: 4px; cursor: pointer; font-size: 0.9em; }}
  .export-btn:hover {{ background: #0d652d; }}
  textarea {{ box-sizing: border-box; }}
</style>
</head>
<body>

<div class="topbar">
  <h1>📖 {_esc(title)}</h1>
  <div style="font-size:0.85em;opacity:0.85">
    {_esc(source_pdf)} · p.{pdf_page} · {dpi} DPI · {_esc(img_hash[:12])}…
  </div>
  <button class="export-btn" onclick="exportJSON()">⬇ Export review_result.json</button>
</div>

<div class="stats">
  <b>Lines:</b> {len(lines)} &nbsp;|&nbsp;
  <b>Root entries:</b> {len(root_entries)} &nbsp;|&nbsp;
  {'&nbsp;|&nbsp;'.join(f'<b>{k}:</b> {v}' for k, v in review_counts.items())}
  &nbsp;&nbsp;
  <b>Reviewer:</b> <input id="reviewer-field" type="text"
    value="{_esc(reviewer)}"
    style="border:1px solid #ccc;border-radius:3px;padding:2px 6px;font-size:0.9em">
</div>

<div style="padding:8px 16px;background:#e6f4ea;border-bottom:1px solid #b7dfb8;font-size:0.85em">
  <b>Root entries detected:</b> {root_summary}
</div>

<div class="layout">
  <div class="col-image">
    <div style="text-align:center;font-size:0.8em;color:#888;margin-bottom:6px">
      Original scan ({dpi} DPI)
    </div>
    {img_tag}
  </div>
  <div class="col-review">
    <table class="lines">
      <thead>
        <tr>
          <th style="width:160px">Line / Region</th>
          <th style="width:260px">Candidates</th>
          <th>OCR Text</th>
          <th style="width:140px">Status</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </div>
</div>

<script>
// ── in-memory state ──────────────────────────────────────────────────────────
const INITIAL_DATA = {export_data};
const state = JSON.parse(JSON.stringify(INITIAL_DATA));

function markChanged(idx) {{
  const ta = document.getElementById('human-' + idx);
  if (state.lines[idx]) {{
    state.lines[idx].human_text = ta.value;
    const curStatus = state.lines[idx].review_status;
    if (curStatus === 'AUTO_AGREED' || curStatus === 'REVIEW_REQUIRED') {{
      setStatusRadio(idx, 'MANUALLY_CORRECTED');
      state.lines[idx].review_status = 'MANUALLY_CORRECTED';
    }}
  }}
}}

function setStatus(idx, val) {{
  if (state.lines[idx]) {{
    state.lines[idx].review_status = val;
    // Sync human_text from textarea
    const ta = document.getElementById('human-' + idx);
    if (ta) state.lines[idx].human_text = ta.value;
  }}
}}

function setStatusRadio(idx, val) {{
  const radios = document.querySelectorAll('input[name="status-' + idx + '"]');
  radios.forEach(r => {{ r.checked = (r.value === val); }});
}}

function exportJSON() {{
  const reviewer = document.getElementById('reviewer-field').value.trim();
  const today = new Date().toISOString().slice(0, 10);

  // Sync all textareas and radios into state
  state.lines.forEach((ln, idx) => {{
    const ta = document.getElementById('human-' + idx);
    if (ta) ln.human_text = ta.value || null;
    const checked = document.querySelector('input[name="status-' + idx + '"]:checked');
    if (checked) ln.review_status = checked.value;
    if (ln.human_text && !ln.reviewer) {{
      ln.reviewer = reviewer;
      ln.review_date = today;
    }}
  }});
  state.reviewer = reviewer;

  const blob = new Blob([JSON.stringify(state, null, 2)],
                         {{type: 'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'review_result_{_esc(source_pdf)}_p{pdf_page}.json';
  a.click();
}}
</script>
</body>
</html>"""


# ── write to file ─────────────────────────────────────────────────────────────

def write_review_html(
    output_path: str,
    page_data: dict,
    lines: list[dict],
    root_entries: list[dict],
    png_path: str | None = None,
    reviewer: str = "",
) -> None:
    html_content = generate_review_html(
        page_data, lines, root_entries, png_path=png_path, reviewer=reviewer
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python review_report.py <page_data.json> <lines.json> [root_entries.json] [out.html]")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        page_data = json.load(f)
    with open(sys.argv[2], encoding="utf-8") as f:
        lines = json.load(f)

    root_entries: list[dict] = []
    if len(sys.argv) >= 4 and sys.argv[3].endswith(".json"):
        with open(sys.argv[3], encoding="utf-8") as f:
            root_entries = json.load(f)

    out_html = sys.argv[4] if len(sys.argv) >= 5 else "review.html"
    write_review_html(out_html, page_data, lines, root_entries)
    print(f"[review_report] Written: {out_html}")
