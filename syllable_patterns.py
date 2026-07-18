#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
syllable_patterns.py
الأنماط المقطعية للعربية

Σ = {C, V}
VV = V²
S = CV^n C^m  |  n ∈ {1,2},  m ∈ {0,1,2}

القيد: m=2 في آخر الكلمة فقط
"""

onset   = "C"
nucleus = ["V", "VV"]    # n ∈ {1,2}
coda    = ["", "C", "CC"]  # m ∈ {0,1,2}

PATTERNS = [onset + n + c for n in nucleus for c in coda]

WORD_FINAL_ONLY = {"CVCC", "CVVCC"}   # m = 2

if __name__ == "__main__":
    print(f"Count = {len(PATTERNS)}")
    for p in PATTERNS:
        note = "  ← آخر الكلمة فقط" if p in WORD_FINAL_ONLY else ""
        print(f"  {p}{note}")
