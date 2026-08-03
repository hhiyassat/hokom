#!/usr/bin/env python3
"""
root_letters_repair.py — Maqayis OCR v2
Re-derives root_letters from the letter-name formula in the heading text,
correcting OCR corruption in both the parenthesised root and the letter-names.

Algorithm
─────────
1. Build a lookup: (OCR letter-name string) → (Arabic letter character)
   covering clean forms (الجيم → ج) and all confirmed OCR variants.
2. For every entry, parse the heading to extract 2–4 letter names and
   reconstruct the root string (e.g. "الجيم واللام والسين" → "جلس").
3. Compare the parsed root with the existing root_letters:
     AGREE    — parsed == current root_letters      → no change, log as verified
     REPAIR   — parsed differs, parsed looks valid  → update root_letters
     CONFLICT — parsing failed or ambiguous          → skip, leave unchanged
4. Write root_entries.jsonl (atomic) and a repair report JSON.

Input : data/maqaees/full/root_entries.jsonl
Output: data/maqaees/full/root_entries.jsonl   (updated in-place, atomic)
        data/maqaees/full/root_letters_repair_report.json

Usage:
    python3 tools/maqayis_ocr/root_letters_repair.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO_ROOT  = Path(__file__).resolve().parents[2]
_JSONL_IN   = _REPO_ROOT / "data" / "maqaees" / "full" / "root_entries.jsonl"
_REPORT_OUT = _REPO_ROOT / "data" / "maqaees" / "full" / "root_letters_repair_report.json"

# ── Arabic diacritics strip ────────────────────────────────────────────────────
_DIAC = re.compile(r"[ً-ٰٟ]")
def _sd(t: str) -> str:
    return _DIAC.sub("", t)

# ── Letter-name → Arabic character ────────────────────────────────────────────
# Keys are normalised (diacritics stripped).
# Each tuple: (canonical_name, letter_char)
# We add both the clean form AND every confirmed OCR variant.

_NAME_MAP: dict[str, str] = {
    # ─── Clean canonical forms ────────────────────────────────────────────────
    "الالف":   "ا",  "الهمزة": "ء",
    "الباء":   "ب",
    "التاء":   "ت",
    "الثاء":   "ث",
    "الجيم":   "ج",
    "الحاء":   "ح",
    "الخاء":   "خ",
    "الدال":   "د",
    "الذال":   "ذ",
    "الراء":   "ر",
    "الزاء":   "ز",  "الزاي": "ز",
    "السين":   "س",
    "الشين":   "ش",
    "الصاد":   "ص",
    "الضاد":   "ض",
    "الطاء":   "ط",
    "الظاء":   "ظ",
    "العين":   "ع",
    "الغين":   "غ",
    "الفاء":   "ف",
    "القاف":   "ق",
    "الكاف":   "ك",
    "اللام":   "ل",
    "الميم":   "م",
    "النون":   "ن",
    "الهاء":   "ه",
    "الواو":   "و",
    "الياء":   "ي",
    # ─── OCR variants (confirmed from corpus analysis) ────────────────────────
    # ع ← م glyph confusion  (272 cases — most common corruption)
    "المين":   "ع",
    # ح prefix ان instead of ال
    "انحاء":   "ح",
    # غ ← ف underdot dropped
    "الفين":   "غ",
    # م → يم (drops initial م)
    "اليم":    "م",  "اليمم": "م",
    # ك ← سك prefix noise
    "السكاف":  "ك",  "المكاف": "ك",
    # ث ← ن dot confusion
    "الناء":   "ث",
    # خ → دا + ان prefix
    "انداء":   "خ",
    # ش ← ث dot confusion
    "الثين":   "ش",
    # غ → ذ+ين
    "الذين":   "غ",
    # م → مم (letter drop)
    "المم":    "م",
    # ء ← مم instead of هم
    "الممزة":  "ء",  "المزة": "ء",
    # ق ← ف initial confusion
    "الفاف":   "ق",
    # ف ← غ initial confusion
    "الغاء":   "ف",
    # ض → فاد / صاء / داد / داض
    "الفاد":   "ض",  "الصاء": "ض",  "الداد": "ض",  "الداض": "ض",
    "الفاض":   "ض",  "اتضاد": "ض",
    # ج → جم (truncation)
    "الجم":    "ج",
    # ح → داء confusion
    "الداء":   "ح",
    # ر prefix mis-read
    "اترأء":   "ر",
    # ط prefix ان or double alef
    "انطاء":   "ط",  "الطااء": "ط",
    # ن → فون
    "الفون":   "ن",  "النين": "ن",
    # ل → لم (truncation)
    "اللم":    "ل",
    # ذ OCR variants
    "الذاء":   "ذ",  "انذاء": "ذ",
    # و → وار
    "الوار":   "و",
    # Additional low-count variants
    "انلحاء":  "ح",  "الحام": "ح",
    "التاف":   "ت",
    "انجاء":   "ج",
    "اندال":   "د",
    "القام":   "ق",
    "انلاء":   "ل",
    "الفم":    "م",
}

# Words that describe root characteristics — NOT a radical name
_NON_RADICAL = {
    "الحرف", "المعتل", "المهموز", "الممتل", "المتل", "المعمل",
    "المضاعف", "المطابق", "المعل", "المنقوص", "المقصور",
    "اللين", "الصحيح", "الناقص",
}

# ── Heading parser ─────────────────────────────────────────────────────────────

# Matches "ال..." or "ان..." or "ات..." Arabic words (letter-name prefix patterns)
_LETTER_NAME_RE = re.compile(r"\b(ا[لنت][ء-ي]{2,7})\b", re.UNICODE)


def _parse_root_from_heading(heading: str) -> str | None:
    """
    Parse the letter-name formula from a heading and return the reconstructed
    root string (2–4 chars), or None if parsing fails.

    Input example (after diacritic strip):
      "( جلس ) الجيم واللام والسين اصل واحد يدل على..."
    Output: "جلس"
    """
    normalised = _sd(heading)

    # Detach the Arabic conjunction prefix 'و' from letter-name tokens.
    # In headings letter names appear as "الحاء واللام والدال" — the 'و'
    # (and) is written attached to 'ال', turning 'اللام' into 'واللام'.
    # That collapses the \b word-boundary before 'ا', so the regex misses it.
    # Inserting a space restores the boundary without changing meaning.
    normalised = re.sub(r"و(ا[لنت])", r" \1", normalised)

    # Find all Arabic letter-name candidates in the heading
    candidates = _LETTER_NAME_RE.findall(normalised)

    letters: list[str] = []
    for name in candidates:
        if name in _NON_RADICAL:
            break                          # stop at non-radical annotations
        if name in _NAME_MAP:
            letters.append(_NAME_MAP[name])
        # else: unknown name — skip but don't break (might be noise)

    if len(letters) < 2:
        return None                        # could not extract enough letters

    # Ibn Faris roots: 2–4 radicals; the formula lists them in order
    root = "".join(letters[:4])
    return root if 2 <= len(root) <= 4 else None


# ── Quality classifier ────────────────────────────────────────────────────────

# ى (alef maqsura U+0649) differs from ي (yeh U+064A) — both are valid root letters
_ARABIC_ONLY = re.compile(r"^[ابتثجحخدذرزسشصضطظعغفقكلمنهوىيأإءؤئآا]+$")
_GAP_LETTERS = set("ابتثج")  # OCR coverage-gap bab letters


def _root_quality(rl: str) -> str:
    """Classify current root_letters quality."""
    if not rl:                          return "empty"
    if len(rl) == 1:                    return "single_letter"
    if not _ARABIC_ONLY.match(rl):      return "non_arabic"
    if len(rl) > 4:                     return "too_long"
    return "ok"


def _should_repair(entry: dict, parsed: str | None) -> tuple[bool, str]:
    """
    Decide whether to repair this entry's root_letters.

    Returns (should_repair: bool, reason: str).
    """
    if parsed is None:
        return False, "parse_failed"

    rl = (entry.get("root_letters") or "").strip()
    quality = _root_quality(rl)

    if quality in ("empty", "single_letter", "non_arabic", "too_long"):
        return True, f"bad_quality:{quality}"

    if parsed == rl:
        return False, "already_correct"

    # parsed differs from current — only repair when we're confident
    # High confidence: current root starts with an OCR-gap letter AND parsed
    # root's first letter is different (OCR mismatch corrected)
    if rl and rl[0] in _GAP_LETTERS and parsed[0] != rl[0]:
        return True, f"first_letter_corrected:{rl[0]}→{parsed[0]}"

    # High confidence: 2 of 3 radicals agree AND current root starts with a
    # gap letter (OCR unreliable there).  We do NOT apply this broadly because
    # the heading letter-names also carry OCR errors (e.g. الخاء → الحاء),
    # which would turn correct خ… roots into wrong ح… roots.
    if len(rl) == 3 and len(parsed) == 3 and rl[0] in _GAP_LETTERS:
        overlap = sum(1 for a, b in zip(rl, parsed) if a == b)
        if overlap == 2:
            return True, f"one_radical_corrected:{rl}→{parsed}"

    # ── ح↔خ first-letter swap (dot confusion, bab-anchored) ─────────────────
    # OCR frequently confuses ح and خ (same base glyph, differ only by the dot
    # above خ).  When ONLY the first letter differs and that diff is ح↔خ, the
    # bab_letter field provides an independent anchor:
    #   • 84 of 101 cases have bab_letter=الحاء confirming the ح form
    #   • 0 cases have bab_letter=الخاء contradicting the repair
    # Positions 1 and 2 are excluded: the OCR confusion is bidirectional at
    # those positions (الخاء is mis-read as الحاء in the heading just as often
    # as the parenthesized radical), so no reliable repair direction can be
    # inferred.  E.g. all دخ.../دح... pairs have headings saying "الحاء" even
    # though the stored دخ form is correct (the heading is wrong, not the root).
    if len(parsed) == len(rl):
        diffs = [i for i in range(len(rl)) if rl[i] != parsed[i]]
        if len(diffs) == 1 and diffs[0] == 0:
            if {rl[0], parsed[0]} == {"ح", "خ"}:
                direction = f"{rl[0]}→{parsed[0]}"
                return True, f"ha_kha_swap_pos0:{direction}:{rl}→{parsed}"

    # Medium confidence: full root differs — flag but only repair if parsed
    # root plausibly replaces a known wrong value
    return False, f"conflict:{rl}≠{parsed}"


# ── Main ──────────────────────────────────────────────────────────────────────

def _process(jsonl_path: Path, dry_run: bool) -> dict:
    entries: list[dict] = []
    with open(jsonl_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    repaired:   list[dict] = []
    conflicts:  list[dict] = []
    parse_fail: int = 0

    for entry in entries:
        heading = (entry.get("root_heading_text") or "").strip()
        parsed  = _parse_root_from_heading(heading)
        do_repair, reason = _should_repair(entry, parsed)

        if parsed is None:
            parse_fail += 1
            continue

        old_rl = (entry.get("root_letters") or "").strip()

        if do_repair:
            repaired.append({
                "entry_id":   entry.get("entry_id"),
                "source_pdf": entry.get("source_pdf"),
                "old_root":   old_rl,
                "new_root":   parsed,
                "reason":     reason,
                "heading":    heading[:80],
            })
            if not dry_run:
                entry["root_letters"]     = parsed
                entry["root_repaired"]    = True
                entry["root_repair_from"] = old_rl
        elif parsed != old_rl:
            conflicts.append({
                "entry_id":   entry.get("entry_id"),
                "old_root":   old_rl,
                "parsed":     parsed,
                "reason":     reason,
                "heading":    heading[:80],
            })

    # ── report ────────────────────────────────────────────────────────────────
    report = {
        "total_entries":   len(entries),
        "parse_failed":    parse_fail,
        "repaired":        len(repaired),
        "conflicts":       len(conflicts),
        "dry_run":         dry_run,
        "repairs":         repaired[:50],   # first 50 samples
        "conflict_sample": conflicts[:20],
    }

    if not dry_run:
        tmp = jsonl_path.with_suffix(".jsonl.tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            for e in entries:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
        tmp.replace(jsonl_path)

        with open(_REPORT_OUT, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Repair root_letters from letter-name formula in headings."
    )
    parser.add_argument(
        "--jsonl", default=str(_JSONL_IN),
        help=f"Path to root_entries.jsonl (default: {_JSONL_IN})"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without writing files"
    )
    args = parser.parse_args()

    jsonl_path = Path(args.jsonl)
    if not jsonl_path.exists():
        print(f"ERROR: {jsonl_path} not found", file=sys.stderr)
        sys.exit(1)

    print(f"{'DRY RUN — ' if args.dry_run else ''}Processing {jsonl_path} …")
    report = _process(jsonl_path, dry_run=args.dry_run)

    print(f"\nTotal entries   : {report['total_entries']:,}")
    print(f"Parse failed    : {report['parse_failed']:,}  (no letter-name formula found)")
    print(f"Repaired        : {report['repaired']:,}")
    print(f"Conflicts       : {report['conflicts']:,}  (parsed ≠ current but not repaired)")

    if report["repairs"]:
        print(f"\nSample repairs (first 10):")
        for r in report["repairs"][:10]:
            print(f"  [{r['source_pdf']}] {r['old_root']!r:8s} → {r['new_root']!r:6s}  ({r['reason']})")
            print(f"    {r['heading'][:70]}")

    if report["conflict_sample"]:
        print(f"\nSample conflicts (first 5 — not repaired):")
        for c in report["conflict_sample"][:5]:
            print(f"  {c['old_root']!r} parsed={c['parsed']!r}  ({c['reason']})")

    if args.dry_run:
        print("\n(dry run — no files written)")
    else:
        print(f"\n✓ root_entries.jsonl updated.")
        print(f"  Report → {_REPORT_OUT}")


if __name__ == "__main__":
    main()
