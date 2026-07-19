#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p6_derivatives/rule_registry.py — Derivatives rule registry loader
CANONICAL_DERIVATIVES_RULE_REGISTRY = data/derivatives/derivative_rule_registry.jsonl
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

_REPO_ROOT    = Path(__file__).parent.parent.parent
_RULE_PATH    = _REPO_ROOT / 'data' / 'derivatives' / 'derivative_rule_registry.jsonl'
_LEXICON_PATH = _REPO_ROOT / 'data' / 'derivatives' / 'derivative_lexical_inventory.jsonl'
_PATTERN_PATH = _REPO_ROOT / 'data' / 'derivatives' / 'derivative_pattern_definitions.jsonl'


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


class DerivativeRuleRegistry:
    """Canonical derivative rule registry — loaded from tracked data files."""

    def __init__(self) -> None:
        self._rules    = _load_jsonl(_RULE_PATH)
        self._lexicon  = _load_jsonl(_LEXICON_PATH)
        self._patterns = _load_jsonl(_PATTERN_PATH)

        # index by (derivative_type, form_family)
        self._by_dtype_ff: dict[tuple, list] = {}
        for r in self._rules:
            dtype = r.get('derivative_type', '')
            ff    = r.get('input_form_family', '')
            key   = (dtype, ff)
            self._by_dtype_ff.setdefault(key, []).append(r)

        # sort each bucket by priority then rule_id for determinism
        for key in self._by_dtype_ff:
            self._by_dtype_ff[key].sort(
                key=lambda r: (r.get('priority', 99), r.get('rule_id', ''))
            )

        # index lexicon by root tuple
        self._lex_by_root: dict[tuple, list] = {}
        for e in self._lexicon:
            key = tuple(e.get('root', []))
            self._lex_by_root.setdefault(key, []).append(e)

        # sort lexicon entries deterministically
        for k in self._lex_by_root:
            self._lex_by_root[k].sort(key=lambda e: e.get('deriv_id', ''))

    def rules_for_derivative_type_and_form_family(
        self, derivative_type: str, form_family: str
    ) -> list:
        return list(self._by_dtype_ff.get((derivative_type, form_family), []))

    def lexical_entries_for_root(self, root: tuple) -> list:
        return list(self._lex_by_root.get(tuple(root), []))

    def lexical_entries_for_root_and_ff(self, root: tuple, ff: str) -> list:
        return [
            e for e in self.lexical_entries_for_root(root)
            if e.get('form_family') == ff
        ]

    def lexical_entries_for_root_and_dtype(
        self, root: tuple, derivative_type: str
    ) -> list:
        return [
            e for e in self.lexical_entries_for_root(root)
            if e.get('derivative_type') == derivative_type
        ]

    def lexical_entries_for_root_ff_and_dtype(
        self, root: tuple, ff: str, derivative_type: str
    ) -> list:
        return [
            e for e in self.lexical_entries_for_root(root)
            if e.get('form_family') == ff and e.get('derivative_type') == derivative_type
        ]

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


_REGISTRY: Optional[DerivativeRuleRegistry] = None


def get_rule_registry() -> DerivativeRuleRegistry:
    """Returns a cached singleton registry (deterministic across calls)."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = DerivativeRuleRegistry()
    return _REGISTRY
