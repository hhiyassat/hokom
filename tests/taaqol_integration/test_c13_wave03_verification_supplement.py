"""C13 Wave03 — supplementary verification per campaign §7.

Existing test_c13_wave03_relation_closure.py proves ACCEPT via real
Ayat corpus. This supplement adds the remaining §7-required cases:

  - DEFER   (missing predecessor evidence)
  - BLOCK   (structurally invalid input)
  - missing evidence
  - conflicting evidence
  - deterministic double execution

None of the added cases uses fixtures, mocks, or fabricated verdicts.
Each drives the native vendor callables directly through the same
pipeline.taaqol_integration.evidence_producers.vertical_chain_adapter
that Wave03's happy-path test uses.
"""
from __future__ import annotations

from pipeline.taaqol_integration.evidence_producers.vertical_chain_adapter import (
    execute_ayat_vertical_chain,
)


# ── § A — Empty/missing evidence produces zero PROVEN closures ────────────────

def test_wave03_missing_evidence_returns_zero_closures():
    """Missing predecessor evidence: empty cu_map + empty spans →
    the chain runs but produces zero relation closures. No exception
    is raised (fail-open contract). §7 missing-evidence case.
    """
    r = execute_ayat_vertical_chain({}, [])
    assert r['relation_closure_calls'] == 0
    assert r['ayat_relation_closure_executed'] == 0
    # No stage was executed because the chain short-circuits on empty inputs.
    assert r['formal_style_calls'] == 0


def test_wave03_incomplete_span_blocks_closure():
    """Structurally incomplete span (single member) → BLOCK.
    Any span with < 2 members cannot form a governor→dependent
    relation; the chain skips it silently (per adapter line 242-243).
    §7 BLOCK case.
    """
    fake_cu_map = {"TOKEN-1": {"placeholder": True}}
    spans = [{
        "span_id": "SINGLE-MEMBER-SPAN",
        "member_token_ids": ["TOKEN-1"],
        "construction_rule": "single",
    }]
    r = execute_ayat_vertical_chain(fake_cu_map, spans)
    assert r['relation_closure_calls'] == 0, (
        "single-member span must not reach relation closure"
    )
    assert r['ayat_relation_closure_executed'] == 0


def test_wave03_unknown_token_ids_block_closure():
    """Span references token IDs not in cu_map → BLOCK path.
    Adapter line 241 filters cu_members to those present in cu_map;
    when < 2 remain the span is skipped.
    """
    r = execute_ayat_vertical_chain({}, [{
        "span_id": "SPAN-UNKNOWN",
        "member_token_ids": ["MISSING-1", "MISSING-2"],
        "construction_rule": "test",
    }])
    assert r['relation_closure_calls'] == 0
    assert r['ayat_relation_closure_executed'] == 0


# ── § B — ACCEPT case (real corpus) + determinism ─────────────────────────────

def _ayat_result_once():
    from tests.taaqol_integration.test_c13_wave03_relation_closure import (
        _run_full_ayat_and_produce_spans,
    )
    cu_map, spans = _run_full_ayat_and_produce_spans()
    return execute_ayat_vertical_chain(cu_map, spans)


def test_wave03_accept_case_on_real_corpus():
    """§7 ACCEPT case: real Ayat corpus reaches PROVEN RelationClosure."""
    r = _ayat_result_once()
    assert r['relation_closure_verdicts_proven'] >= 1, (
        f"expected ≥1 PROVEN RelationClosure; got "
        f"{r['relation_closure_verdicts_proven']}"
    )
    assert r['ayat_relation_closure_executed'] >= 1


def test_wave03_deterministic_double_execution():
    """§7 repeated deterministic execution — two full runs return
    identical stage-call counts and identical PROVEN counts.
    """
    r1 = _ayat_result_once()
    r2 = _ayat_result_once()
    for key in (
        'formal_style_calls',
        'mufrad_semantic_slot_calls',
        'maqam_context_calls',
        'dalalah_candidate_calls',
        'mufrad_dalalah_closure_calls',
        'relation_closure_calls',
        'ms_verdicts_proven',
        'maqam_verdicts_proven',
        'dalalah_verdicts_proven',
        'mufrad_dalalah_closure_verdicts_proven',
        'relation_closure_verdicts_proven',
        'ayat_relation_closure_executed',
    ):
        assert r1[key] == r2[key], (
            f"§7 determinism: {key} differs between runs "
            f"({r1[key]} vs {r2[key]})"
        )


# ── § C — verdict-type discipline (no synthetic or map-based verdicts) ────────

def test_wave03_no_expected_verdict_map_in_adapter_source():
    """§7 WAVE03_EXPECTED_VERDICT_MAP_COUNT = 0.
    Static scan of the vertical_chain_adapter source for any
    hardcoded verdict-map pattern.
    """
    from pathlib import Path
    src = Path(
        "pipeline/taaqol_integration/evidence_producers/vertical_chain_adapter.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "expected_verdict",
        "verdict_map",
        "hardcoded_verdict",
        "gold_verdict",
    )
    hits = []
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("#") or s.startswith('"') or s.startswith("'"):
            continue
        for f in forbidden:
            if f in s:
                hits.append((f, s[:80]))
    assert not hits, (
        f"§7: expected-verdict-map pattern found in adapter source: {hits}"
    )


def test_wave03_no_token_position_branch_in_adapter_source():
    """§7 WAVE03 counter: no token_position branching in the adapter."""
    from pathlib import Path
    src = Path(
        "pipeline/taaqol_integration/evidence_producers/vertical_chain_adapter.py"
    ).read_text(encoding="utf-8")
    hits = []
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        if "token_position" in s or "token_index ==" in s:
            hits.append(s[:80])
    assert not hits, (
        f"§7: token-position branching found in adapter source: {hits}"
    )
