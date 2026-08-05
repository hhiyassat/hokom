"""
maqayis_body_loader.py — Body text resolver for Maqayis JSONL corpus
MAQAYIS-CONSTITUTIONAL-SOURCE-LEXICON-PRODUCTION-01

Resolves body_line_ids from root_entries JSONL against lines.jsonl
to retrieve full lexical entry text — excluding poetry_line_ids per
constitutional contract ("بدون الشعر").

Design
──────
- Lazy-loaded singleton: lines.jsonl is loaded once on first use.
- Text priority per line: human_text > corrected_ocr > raw_ocr.
- Poetry lines (poetry_line_ids) are NEVER returned — constitutional
  exclusion, not a filtering option.
- Footnote lines (footnote_line_ids) excluded by default; caller may
  opt in via include_footnotes=True.
- Missing line IDs are silently skipped (OCR gap, not a crash).

API
───
    loader = MaqayisBodyLoader(lines_jsonl_path)

    # Body text only (no heading, no poetry, no footnotes)
    text = loader.get_body_text(entry)

    # Full entry: heading + body (no poetry, no footnotes)
    text = loader.get_entry_text(entry)
"""
from __future__ import annotations

import json
import pathlib
import threading
from typing import Any, Optional


# ── Line text selection ───────────────────────────────────────────────────────

def _best_text(line_obj: dict[str, Any]) -> str:
    """
    Return the best available text for a line, in order of quality:
    human_text → corrected_ocr → raw_ocr → "".
    """
    for key in ("human_text", "corrected_ocr", "raw_ocr"):
        val = line_obj.get(key)
        if val and str(val).strip():
            return str(val).strip()
    return ""


# ── MaqayisBodyLoader ─────────────────────────────────────────────────────────

class MaqayisBodyLoader:
    """
    Lazy-loaded, thread-safe resolver from line_id → text.

    Parameters
    ──────────
    lines_jsonl : path to the lines.jsonl file (52 K lines).
    """

    def __init__(self, lines_jsonl: "pathlib.Path | str") -> None:
        self._path   = pathlib.Path(lines_jsonl)
        self._lock   = threading.Lock()
        self._loaded = False
        self._index: dict[str, dict[str, Any]] = {}

    # ── Loading ───────────────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load lines.jsonl into an in-memory dict keyed by line_id."""
        index: dict[str, dict[str, Any]] = {}
        with open(self._path, encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                    lid = obj.get("line_id")
                    if lid:
                        index[lid] = obj
                except json.JSONDecodeError:
                    pass
        self._index  = index
        self._loaded = True

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            with self._lock:
                if not self._loaded:
                    self._load()

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def line_count(self) -> int:
        """Number of lines indexed (triggers load if needed)."""
        self._ensure_loaded()
        return len(self._index)

    def get_line_text(self, line_id: str) -> str:
        """Return the best text for a single line_id. Returns '' if unknown."""
        self._ensure_loaded()
        obj = self._index.get(line_id)
        if obj is None:
            return ""
        return _best_text(obj)

    def get_lines_text(
        self,
        line_ids: list,
        *,
        exclude: Optional[set] = None,
        separator: str = "\n",
    ) -> str:
        """Return joined text for an ordered list of line_ids."""
        self._ensure_loaded()
        exclude = exclude or set()
        parts: list[str] = []
        for lid in line_ids:
            if lid in exclude:
                continue
            text = self.get_line_text(lid)
            if text:
                parts.append(text)
        return separator.join(parts)

    def get_body_text(
        self,
        entry: dict[str, Any],
        *,
        include_footnotes: bool = False,
        separator: str = " ",
    ) -> str:
        """
        Return body text for a root entry dict.

        Poetry lines are ALWAYS excluded (constitutional: بدون الشعر).
        Footnote lines excluded by default; set include_footnotes=True to include.
        """
        body_ids     = entry.get("body_line_ids", []) or []
        poetry_ids   = set(entry.get("poetry_line_ids", []) or [])
        footnote_ids = entry.get("footnote_line_ids", []) or []

        ids_to_fetch = list(body_ids)
        if include_footnotes:
            ids_to_fetch.extend(footnote_ids)

        return self.get_lines_text(ids_to_fetch, exclude=poetry_ids, separator=separator)

    def get_entry_text(
        self,
        entry: dict[str, Any],
        *,
        include_footnotes: bool = False,
        heading_separator: str = "\n",
        line_separator: str = " ",
    ) -> str:
        """
        Return the full entry text: heading + body (no poetry, no footnotes).

        heading is taken from root_heading_text (OCR of the heading line).
        """
        heading = (entry.get("root_heading_text") or "").strip()
        body    = self.get_body_text(
            entry,
            include_footnotes=include_footnotes,
            separator=line_separator,
        )

        if heading and body:
            return heading + heading_separator + body
        return heading or body

    def entry_summary(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Return a structured dict with all key fields for an entry."""
        root_letters = entry.get("root_letters", "?")
        heading      = (entry.get("root_heading_text") or "").strip()
        body         = self.get_body_text(entry)
        body_ids     = entry.get("body_line_ids", []) or []
        poetry_ids   = entry.get("poetry_line_ids", []) or []
        footnote_ids = entry.get("footnote_line_ids", []) or []

        poetry_texts: list[str] = []
        for lid in poetry_ids:
            t = self.get_line_text(lid)
            if t:
                poetry_texts.append(t)

        return {
            "root_letters":    root_letters,
            "source":          f"{entry.get('source_pdf', '?')} p.{entry.get('pdf_page', '?')}",
            "semantic_origin": entry.get("semantic_origin_type", "?"),
            "review_status":   entry.get("review_status", "?"),
            "heading":         heading,
            "body":            body,
            "body_line_count": len(body_ids),
            "body_resolved":   bool(body),
            "poetry_excluded": len(poetry_ids),
            "footnote_count":  len(footnote_ids),
            "poetry_texts":    poetry_texts,
        }


# ── Auto-discovery helper ─────────────────────────────────────────────────────

def _find_lines_jsonl(start: Optional[pathlib.Path] = None) -> Optional[pathlib.Path]:
    """Walk up from start looking for data/maqaees/full/lines.jsonl."""
    here = (start or pathlib.Path(__file__).resolve().parent)
    for _ in range(6):
        candidate = here / "data" / "maqaees" / "full" / "lines.jsonl"
        if candidate.is_file():
            return candidate
        if here.parent == here:
            break
        here = here.parent
    return None


# ── Module-level singleton ────────────────────────────────────────────────────

_DEFAULT_LOADER: Optional[MaqayisBodyLoader] = None
_LOADER_LOCK    = threading.Lock()


def get_default_loader(lines_jsonl: Optional[pathlib.Path] = None) -> MaqayisBodyLoader:
    """
    Return the module-level singleton loader, auto-discovering lines.jsonl.
    Subsequent calls return the cached instance.
    """
    global _DEFAULT_LOADER
    if _DEFAULT_LOADER is None:
        with _LOADER_LOCK:
            if _DEFAULT_LOADER is None:
                if lines_jsonl is None:
                    lines_jsonl = _find_lines_jsonl()
                if lines_jsonl is None:
                    raise FileNotFoundError(
                        "Could not locate lines.jsonl. "
                        "Pass an explicit path to MaqayisBodyLoader()."
                    )
                _DEFAULT_LOADER = MaqayisBodyLoader(lines_jsonl)
    return _DEFAULT_LOADER
