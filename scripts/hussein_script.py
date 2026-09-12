#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HUSSEIN SCRIPT — alias entry point.

Thin wrapper so the owner can run the neutral sentence report generator by its given name:

  python3 scripts/hussein_script.py --sentence "..." --out output/neutral_sentence_reports

It delegates entirely to scripts/neutral_sentence_report_generator.py (same behaviour, same outputs).
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from neutral_sentence_report_generator import main  # noqa: E402

if __name__ == "__main__":
    main()
