#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taaqol-style manager-report renderer (generalized).

This module generalizes the executive manager-report STYLE used by the Taaqol rounds — most directly the
Round-44 report (owner_supplied_scenario_full_manat_44.render_manager): the same CSS shell, numbered <h2>
sections, sentence box, key/value + multi-column tables, the standalone independent traceability table, the
closure-flags block, and the tests-result line.

It carries NO Taaqol content, NO domain knowledge, NO verdict of its own. Callers pass a neutral `spec`
describing sections/tables/flags; the renderer only lays them out. This is the "report renderer separated
from Round-44 content" requested: reuse the shape, never the content.

`render_taaqol_style_manager_report(spec)` returns an HTML string. It stamps a marker
`<!-- taaqol-style-manager-report --> RENDERER=TAAQOL_STYLE` so consumers/tests can prove the shared
renderer was used.
"""
from __future__ import annotations

import html as _html

RENDERER_MARKER = "RENDERER=TAAQOL_STYLE"

_CSS = (
    '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
    'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
    'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
    'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
    'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
    '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
    '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
    '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
    'pre{background:#f4f4f4;border:1px solid #ccc;border-radius:.4rem;padding:.5rem;white-space:pre-wrap;font-size:.78rem}'
    '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style>'
)


def _e(x):
    return _html.escape(str(x))


def _note(text, kind="info"):
    style = ' class="note n" style="background:#fdecec"' if kind == "warn" else ' class="note"'
    return f'<div{style}>{text}</div>'


def _kv_table(rows):
    # rows: list of [header, value, cls?]
    out = ['<div class="wrap"><table><tbody>']
    for r in rows:
        header = _e(r[0])
        value = _e(r[1])
        cls = f' class="{r[2]}"' if len(r) > 2 and r[2] else ""
        out.append(f"<tr><th>{header}</th><td{cls}>{value}</td></tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def _cols_table(headers, rows, row_classes=None):
    out = ['<div class="wrap"><table><thead><tr>']
    out += [f"<th>{_e(h)}</th>" for h in headers]
    out.append("</tr></thead><tbody>")
    for i, row in enumerate(rows):
        out.append("<tr>")
        for j, cell in enumerate(row):
            cls = ""
            if row_classes and i < len(row_classes) and j < len(row_classes[i]) and row_classes[i][j]:
                cls = f' class="{row_classes[i][j]}"'
            tag = "th" if j == 0 else "td"
            out.append(f"<{tag}{cls}>{_e(cell)}</{tag}>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def _list_block(items, kind="info"):
    inner = "<ul>" + "".join(f"<li>{_e(x)}</li>" for x in items) + "</ul>"
    return _note(inner, kind)


def _render_block(b):
    if "note" in b:
        return _note(_e(b["note"]) if b.get("escape", True) else b["note"], b.get("kind", "info"))
    if "raw_note" in b:
        return _note(b["raw_note"], b.get("kind", "info"))
    if "kv" in b:
        return _kv_table(b["kv"])
    if "cols" in b:
        c = b["cols"]
        return _cols_table(c["headers"], c["rows"], c.get("row_classes"))
    if "list" in b:
        return _list_block(b["list"], b.get("kind", "info"))
    if "pre" in b:
        return f"<pre>{_e(b['pre'])}</pre>"
    if "h_bullets" in b:
        return "<ul>" + "".join(f"<li>{_e(x)}</li>" for x in b["h_bullets"]) + "</ul>"
    return ""


def _trace_table(title, rows):
    out = [f"<h2>{_e(title)}</h2>",
           '<div class="wrap"><table><thead><tr>'
           '<th>requirement</th><th>source</th><th>artifact</th><th>test</th><th>status</th>'
           '</tr></thead><tbody>']
    for r in rows:
        cls = "y" if r.get("status") == "TRACEABLE" else "n"
        out.append(f'<tr><th>{_e(r["req"])}</th><td>{_e(r["source"])}</td><td>{_e(r["artifact"])}</td>'
                   f'<td>{_e(r["test"])}</td><td class="{cls}">{_e(r["status"])}</td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)


def render_taaqol_style_manager_report(spec):
    """Render a rich Taaqol-style manager report from a neutral spec dict.

    spec keys:
      title, lang (default 'ar'), top_banners [(kind, html)], sentence {label,text,id},
      sections [{n,title,body:[block,...]}], trace {title,rows[...]},
      closure_flags (html str), tests_result (str), footer (str).
    """
    lang = spec.get("lang", "ar")
    P = [f'<!doctype html><html lang="{lang}" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         f'<!-- taaqol-style-manager-report {RENDERER_MARKER} -->',
         f'<title>{_e(spec["title"])}</title>',
         _CSS, '</head><body>']
    P.append(f'<h1>{_e(spec["title"])}</h1>')
    P.append(f'<div class="foot" style="border:0;margin:0;padding:0">{RENDERER_MARKER}</div>')
    for kind, banner_html in spec.get("top_banners", []):
        P.append(_note(banner_html, kind))
    # sections
    sent = spec.get("sentence")
    tr = spec.get("trace")
    trace_rendered = False
    for sec in spec.get("sections", []):
        P.append(f'<h2>{sec["n"]}. {_e(sec["title"])}</h2>')
        # optional inline sentence box for the section that declares it
        if sec.get("sentence_box") and sent:
            P.append('<div class="sentbox"><div class="sent" id="' + _e(sent.get("id", "input-sentence"))
                     + '">' + _e(sent["text"]) + '</div></div>')
        for b in sec.get("body", []):
            P.append(_render_block(b))
        # place the standalone traceability table right after the declaring section
        # (mirrors Round-44: trace table sits between §12 and §13)
        if sec.get("trace_here") and tr and not trace_rendered:
            P.append(_trace_table(tr["title"], tr["rows"]))
            trace_rendered = True
    if tr and not trace_rendered:
        P.append(_trace_table(tr["title"], tr["rows"]))
    if spec.get("closure_flags"):
        P.append(_note("<b>أعلام الإغلاق داخل التقرير:</b> " + spec["closure_flags"]))
    if spec.get("tests_result"):
        P.append(_note("<b>نتيجة الاختبارات:</b> " + _e(spec["tests_result"])))
    if spec.get("footer"):
        P.append(f'<div class="foot">{_e(spec["footer"])}</div>')
    P.append("</body></html>")
    return "\n".join(P)
