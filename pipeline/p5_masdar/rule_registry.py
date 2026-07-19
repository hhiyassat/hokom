#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p5_masdar/rule_registry.py — Masdar rule registry loader
CANONICAL_MASDAR_RULE_REGISTRY = data/masdar/masdar_rule_registry.jsonl
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

_REPO_ROOT    = Path(__file__).parent.parent.parent
_RULE_PATH    = _REPO_ROOT / 'data' / 'masdar' / 'masdar_rule_registry.jsonl'
_LEXICON_PATH = _REPO_ROOT / 'data' / 'masdar' / 'masdar_lexical_inventory.jsonl'
_PATTERN_PATH = _REPO_ROOT / 'data' / 'masdar' / 'masdar_pattern_definitions.jsonl'


def _load_jsonl(path: Path) -> list:
    records = []
    with path.open(encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                obj = json.loads(line)
                if not obj.get('_comment'):
                    records.append(obj)
    return records


class MasdarRuleRegistry:
    """Canonical rule registry — loaded from tracked data files, not from Python constants."""

    def __init__(self) -> None:
        self._rules    = _load_jsonl(_RULE_PATH)
        self._lexicon  = _load_jsonl(_LEXICON_PATH)
        self._patterns = _load_jsonl(_PATTERN_PATH)
        # index by form_family
        self._by_ff: dict[str, list] = {}
        for r in self._rules:
            ff = r.get('input_form_family', '')
            self._by_ff.setdefault(ff, []).append(r)
        # sort each bucket by priority for determinism
        for ff in self._by_ff:
            self._by_ff[ff].sort(key=lambda r: (r.get('priority', 99), r.get('rule_id', '')))
        # index lexicon by root tuple
        self._lex_by_root: dict[tuple, list] = {}
        for e in self._lexicon:
            key = tuple(e.get('root', []))
            self._lex_by_root.setdefault(key, []).append(e)
        # sort lexicon entries deterministically
        for k in self._lex_by_root:
            self._lex_by_root[k].sort(key=lambda e: e.get('masdar_id', ''))

    def rules_for_form_family(self, ff: str) -> list:
        return list(self._by_ff.get(ff, []))

    def lexical_entries_for_root(self, root: tuple) -> list:
        return list(self._lex_by_root.get(tuple(root), []))

    def lexical_entries_for_root_and_ff(self, root: tuple, ff: str) -> list:
        return [e for e in self.lexical_entries_for_root(root) if e.get('form_family') == ff]

    def all_rules(self) -> list:
        return list(self._rules)

    def all_lexicon(self) -> list:
        return list(self._lexicon)

    def all_patterns(self) -> list:
        return list(self._patterns)

    def pattern_for_id(self, pattern_id: str) -> Optional[dict]:
        for p in self._patterns:
            if p.get('pattern_id') == pattern_id:
                return p
        return None


_REGISTRY: Optional[MasdarRuleRegistry] = None


def get_rule_registry() -> MasdarRuleRegistry:
    """Returns a cached singleton registry (deterministic across calls)."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = MasdarRuleRegistry()
    return _REGISTRY
