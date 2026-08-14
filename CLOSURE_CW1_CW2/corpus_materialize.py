#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
corpus_materialize.py — CW1 Strategy B: SHA-pinned deterministic corpus materialization.

Fresh-clone reproducibility WITHOUT committing the Quran text (licensing not proven).
The source URL / immutable asset is an OWNER-SUPPLIED, APPROVED parameter — this
harness NEVER invents a source. It fetches/copies from the approved source, then
verifies SHA256 + token count against the pinned corpus contract, and refuses on
any mismatch.

Usage:
  HOKOM_CORPUS_SOURCE=<approved-url-or-path> python3 corpus_materialize.py --out data/quran-uthmani.txt

If HOKOM_CORPUS_SOURCE is unset → exits AUTHORITATIVE_CORPUS_MATERIALIZATION_SOURCE_REQUIRED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request

# ── pinned corpus contract (authority: Hokom production Quran source) ───────
CORPUS_ID = "HOKOM_QURAN_UTHMANI_TANZIL"
CORPUS_VERSION = "tanzil-uthmani"
EXPECTED_SHA256 = "1130fc9f99f8e64bd0aca4735d52e2ae3030263fe2e0c8ef35a549347dd471ff"
EXPECTED_OCCURRENCES = 77374
EXPECTED_AYAH_LINES = 6226


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _count_occurrences(text: str) -> int:
    n = 0
    for line in text.splitlines():
        if not line:
            continue
        parts = line.split("|", 2)
        if len(parts) == 3:
            n += len(parts[2].split())
    return n


def materialize(source: str, out_path: str) -> dict:
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=60) as resp:
            data = resp.read()
    else:  # approved local/immutable asset path
        with open(source, "rb") as fh:
            data = fh.read()

    sha = _sha256_bytes(data)
    text = data.decode("utf-8")
    occ = _count_occurrences(text)
    ayah = sum(1 for l in text.splitlines() if l.strip())

    checks = {
        "sha256_match": sha == EXPECTED_SHA256,
        "occurrences_match": occ == EXPECTED_OCCURRENCES,
        "ayah_lines_match": ayah == EXPECTED_AYAH_LINES,
    }
    if not all(checks.values()):
        return {"status": "CORPUS_VERIFICATION_FAILED", "actual_sha256": sha,
                "actual_occurrences": occ, "actual_ayah_lines": ayah, "checks": checks}

    with open(out_path, "wb") as fh:
        fh.write(data)
    return {"status": "CORPUS_MATERIALIZED_VERIFIED", "corpus_id": CORPUS_ID,
            "sha256": sha, "occurrences": occ, "out_path": out_path, "checks": checks}


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "data", "quran-uthmani.txt"))
    ap.add_argument("--source", default=os.environ.get("HOKOM_CORPUS_SOURCE"))
    args = ap.parse_args(argv[1:])
    if not args.source:
        print(json.dumps({
            "status": "AUTHORITATIVE_CORPUS_MATERIALIZATION_SOURCE_REQUIRED",
            "message": "No approved source URL / immutable asset supplied. Set "
                       "HOKOM_CORPUS_SOURCE to an owner-approved, stable source. "
                       "Do NOT substitute MASAQ or an unverified URL.",
            "corpus_contract": {"corpus_id": CORPUS_ID, "sha256": EXPECTED_SHA256,
                                "occurrences": EXPECTED_OCCURRENCES}}, indent=2))
        return 2
    rep = materialize(args.source, args.out)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep["status"] == "CORPUS_MATERIALIZED_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
