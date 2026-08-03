"""
dedup_candidates.py — Maqayis OCR v2 post-processor

Removes near-duplicate corrected_candidates from an existing lines.jsonl.
Near-duplicates are candidates whose texts are identical after normalising
whitespace around Arabic punctuation (a known Apple Vision artefact).

Usage
-----
    python dedup_candidates.py \
        --input  data/maqaees/full/lines.jsonl \
        --output data/maqaees/full/lines_deduped.jsonl

Replace in-place (backup first):
    cp data/maqaees/full/lines.jsonl data/maqaees/full/lines.jsonl.bak
    python dedup_candidates.py -i lines.jsonl.bak -o lines.jsonl

The script only touches `corrected_candidates`; raw_candidates, raw_ocr,
corrected_ocr, and all other fields are left untouched.
"""
from __future__ import annotations

import argparse
import json
import re
import sys


# ── normalisation ─────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """
    Normalise for dedup comparison only — never stored.

    Steps:
    1. Collapse multiple spaces to one.
    2. Remove space immediately before closing punctuation (،  .  :  ؟  )  ]).
    3. Remove space immediately after opening punctuation ((  [).
    """
    s = re.sub(r' {2,}', ' ', text)
    for p in ['،', '.', ':', '؟', ')', ']']:
        s = s.replace(f' {p}', p)
    for p in ['(', '[']:
        s = s.replace(f'{p} ', p)
    return s.strip()


def dedup_candidates(candidates: list[dict]) -> list[dict]:
    """Return candidates with near-duplicates removed (first occurrence wins)."""
    seen: set[str] = set()
    result: list[dict] = []
    for c in candidates:
        key = _normalize(c.get('text', ''))
        if key in seen:
            continue
        seen.add(key)
        result.append(c)
    return result


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('-i', '--input',  required=True, help='Source lines.jsonl')
    ap.add_argument('-o', '--output', required=True, help='Destination lines.jsonl')
    args = ap.parse_args()

    total = removed = lines_touched = 0

    with open(args.input, encoding='utf-8') as fin, \
         open(args.output, 'w', encoding='utf-8') as fout:

        for raw_line in fin:
            record = json.loads(raw_line)
            total += 1

            cands = record.get('corrected_candidates') or []
            deduped = dedup_candidates(cands)
            delta = len(cands) - len(deduped)

            if delta:
                removed += delta
                lines_touched += 1
                record['corrected_candidates'] = deduped

            fout.write(json.dumps(record, ensure_ascii=False) + '\n')

    print(
        f'Done. {total:,} lines processed, '
        f'{lines_touched:,} lines had near-duplicate candidates, '
        f'{removed:,} duplicate candidates removed.',
        file=sys.stderr,
    )


if __name__ == '__main__':
    main()
