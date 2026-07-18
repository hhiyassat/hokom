"""
file_io.py — Read/write helpers for common NLP data formats
"""

import json
import csv
from pathlib import Path
from typing import List


def read_txt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_lines(path: str) -> List[str]:
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path: str) -> List[dict]:
    return [json.loads(line) for line in read_lines(path)]


def read_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_json(data, path: str, indent: int = 2):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=indent), encoding="utf-8")


def write_jsonl(data: List[dict], path: str):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
