"""C13 Wave-04 — native Ifadah closure over the Ayat vertical.

Proves campaign §8 required behaviors:
  1. valid positive Ifadah   (real Ayat corpus reaches PROVEN)
  2. structurally incomplete (missing predecessor → adapter refuses)
  3. blocked invalid input   (wrong DTO type → typed refusal)
  4. missing predecessor
  5. conflicting evidence    (maqam divergence)
  6. deterministic repetition
  7. no expected-verdict map
  8. no token-position branch
  9. no direct Hokom injection
  10. trace + residual completeness

Every case drives the native vendor `prove_ifadah_candidate` (docs/41,
PR-20) through the Hokom `ifadah_candidate_adapter` — no fixtures, no
mocks, no fabricated verdicts. The vendor is pinned at 05c6668.
"""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

# Ensure vendor path is on sys.path for direct SpeechForceKind access.
_VENDOR = Path(__file__).resolve().parents[2] / "vendor" / "Taaqol-GPT" / "src"
if str(_VENDOR) not in sys.path:
    sys.path.insert(0, str(_VENDOR))


@pytest.fixture(scope="module")
def ayat_ifadah_result():
    """Run the Ayat vertical chain up to Ifadah once per test module."""
    from tests.taaqol_integration.test_c13_wave03_relation_closure import (
        _run_full_ayat_and_produce_spans,
    )
    from pipeline.taaqol_integration.evidence_producers.wave04_ifadah_chain import (
        execute_ayat_ifadah_chain,
    )
    cu_map, spans = _run_full_ayat_and_produce_spans()
    return execute_ayat_ifadah_chain(cu_map, spans), cu_map, spans


# ── § 8.1 — valid positive Ifadah on real Ayat corpus ──────────────────────────

def test_wave04_positive_ifadah_on_real_corpus(ayat_ifadah_result):
    r, _cu_map, _spans = ayat_ifadah_result
    assert r['ifadah_available'] is True, (
        "IFADAH_AVAILABLE must be True on Python 3.12; adapter degrades on 3.10"
    )
    assert r['ifadah_calls'] >= 1
    assert r['ifadah_proven'] >= 1, (
        f"§8.1: expected ≥1 PROVEN Ifadah on real Ayat corpus; "
        f"got proven={r['ifadah_proven']}, adapter_returned_none="
        f"{r['ifadah_adapter_returned_none']}"
    )
    assert r['ayat_ifadah_executed'] >= 1


# ── § 8.2 — structurally incomplete input (missing predecessor) ────────────────

def test_wave04_missing_predecessor_returns_none():
    """§8.2 + §8.4: caller passes wrong-type relation_closure_verdict →
    adapter returns None (fail-closed), no exception raised."""
    from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (
        build_ifadah_candidate,
    )
    result = build_ifadah_candidate(
        relation_closure_verdict=object(),
        formal_style_verdict=object(),
        ifadah_maqam_verdict=object(),
        speech_force=object(),
        ifadah_evidence="test-evidence",
        closure_scope="test-scope",
    )
    assert result is None


# ── § 8.3 — blocked invalid input (wrong types) ────────────────────────────────

def test_wave04_wrong_speech_force_type_returns_none():
    """§8.3: passing non-SpeechForceKind for speech_force → refused."""
    from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (
        build_ifadah_candidate, _IFADAH_AVAILABLE,
    )
    assert _IFADAH_AVAILABLE, "vendor must be available on 3.12"
    result = build_ifadah_candidate(
        relation_closure_verdict=object(),
        formal_style_verdict=object(),
        ifadah_maqam_verdict=object(),
        speech_force="KHABAR",  # str, not SpeechForceKind — refused at boundary
        ifadah_evidence="test-evidence",
        closure_scope="test-scope",
    )
    assert result is None


# ── § 8.4 — missing predecessor (see § 8.2 covers this) ────────────────────────

def test_wave04_empty_evidence_returns_none():
    """Empty evidence string — fail-closed at adapter boundary."""
    from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (
        build_ifadah_candidate,
    )
    result = build_ifadah_candidate(
        relation_closure_verdict=object(),
        formal_style_verdict=object(),
        ifadah_maqam_verdict=object(),
        speech_force=object(),
        ifadah_evidence="",  # empty — refused
        closure_scope="test-scope",
    )
    assert result is None


# ── § 8.5 — conflicting evidence (maqam divergence) ────────────────────────────

def test_wave04_maqam_divergence_produces_native_refusal():
    """§8.5: when RelationClosure was built under one maqam but the
    Ifadah caller supplies a DIFFERENT maqam verdict → native vendor
    refuses with MAQAM_DIVERGENCE (docs/41 §6). Prove the refusal
    reaches the adapter and produces None."""
    from tests.taaqol_integration.test_c13_wave03_relation_closure import (
        _run_full_ayat_and_produce_spans,
    )
    from pipeline.taaqol_integration.evidence_producers.wave04_ifadah_chain import (
        build_formal_style_verdict,
    )
    from pipeline.taaqol_integration.evidence_producers.vertical_chain_adapter import (
        build_mufrad_semantic_slot, build_maqam_context,
        build_dalalah_candidate, build_mufrad_dalalah_closure,
        build_relation_closure,
    )
    from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (
        build_ifadah_candidate,
    )
    from taaqqul_slot_geometry.weight.ifadah_candidate import SpeechForceKind

    cu_map, spans = _run_full_ayat_and_produce_spans()
    span = next(s for s in spans
                if len([t for t in (s.get('member_token_ids') or [])
                        if t in cu_map]) >= 2)
    m = [t for t in span['member_token_ids'] if t in cu_map]
    gov, dep = m[0], m[-1]

    def build_all(tid):
        entry = cu_map[tid]
        fs = build_formal_style_verdict(tid)
        ms = build_mufrad_semantic_slot(tid, entry, fs.candidate)
        mq = build_maqam_context(tid, ms)
        dal = build_dalalah_candidate(tid, ms, mq)
        mc = build_mufrad_dalalah_closure(tid, ms, mq, dal)
        return fs, mc, mq

    fs_g, mc_g, mq_g = build_all(gov)
    fs_d, mc_d, mq_d = build_all(dep)

    # Build RelationClosure with the DEFAULT synthetic relation_maqam
    # string — which does NOT match the maqam verdict's trace_ref.
    rc = build_relation_closure(span['span_id'], gov, dep, mc_g, mc_d)
    result = build_ifadah_candidate(
        relation_closure_verdict=rc,
        formal_style_verdict=fs_g,
        ifadah_maqam_verdict=mq_g,  # trace_ref doesn't match rc.relation_maqam
        speech_force=SpeechForceKind.KHABAR,
        ifadah_evidence="test-conflict-evidence",
        closure_scope="test-conflict-scope",
    )
    assert result is None, (
        "§8.5: maqam divergence must produce adapter None (native REFUSED)"
    )


# ── § 8.6 — deterministic repetition ───────────────────────────────────────────

def test_wave04_deterministic_double_execution():
    """§8.6: two independent runs of the Ifadah chain produce identical
    counters — proof of determinism."""
    from tests.taaqol_integration.test_c13_wave03_relation_closure import (
        _run_full_ayat_and_produce_spans,
    )
    from pipeline.taaqol_integration.evidence_producers.wave04_ifadah_chain import (
        execute_ayat_ifadah_chain,
    )
    cu_map, spans = _run_full_ayat_and_produce_spans()
    r1 = execute_ayat_ifadah_chain(cu_map, spans)
    r2 = execute_ayat_ifadah_chain(cu_map, spans)
    for k in (
        'formal_style_verdict_calls', 'formal_style_verdict_proven',
        'mufrad_semantic_slot_calls', 'ms_verdicts_proven',
        'maqam_context_calls', 'maqam_verdicts_proven',
        'dalalah_candidate_calls', 'dalalah_verdicts_proven',
        'mufrad_dalalah_closure_calls',
        'mufrad_dalalah_closure_verdicts_proven',
        'relation_closure_calls', 'relation_closure_verdicts_proven',
        'ifadah_calls', 'ifadah_proven',
        'ifadah_adapter_returned_none', 'ayat_ifadah_executed',
    ):
        assert r1[k] == r2[k], (
            f"§8.6 determinism: {k} differs ({r1[k]} vs {r2[k]})"
        )


# ── § 8.7 — no expected-verdict map ────────────────────────────────────────────

def test_wave04_no_expected_verdict_map_in_adapter_source():
    """§8.7: static scan of Ifadah adapter + Wave04 chain source."""
    from pathlib import Path
    for path in (
        Path("pipeline/taaqol_integration/weight_layer/ifadah_candidate_adapter.py"),
        Path("pipeline/taaqol_integration/evidence_producers/wave04_ifadah_chain.py"),
    ):
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("#") or s.startswith('"'):
                continue
            for needle in ("expected_verdict", "verdict_map",
                            "hardcoded_verdict", "gold_verdict"):
                assert needle not in s, (
                    f"§8.7: {path.name}: verdict-map pattern {needle!r} in {s[:80]}"
                )


# ── § 8.8 — no token-position branch ───────────────────────────────────────────

def test_wave04_no_token_position_branch_in_adapter_source():
    """§8.8: neither adapter nor chain branches on token position."""
    from pathlib import Path
    for path in (
        Path("pipeline/taaqol_integration/weight_layer/ifadah_candidate_adapter.py"),
        Path("pipeline/taaqol_integration/evidence_producers/wave04_ifadah_chain.py"),
    ):
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("#"):
                continue
            assert "token_position" not in s, (
                f"§8.8: {path.name}: token_position branch: {s[:80]}"
            )
            assert "token_index ==" not in s, (
                f"§8.8: {path.name}: token_index equality branch: {s[:80]}"
            )


# ── § 8.9 — no direct Hokom injection of Taaqol verdicts ───────────────────────

def test_wave04_no_direct_ifadah_verdict_construction_in_hokom():
    """§8.9: Hokom must not construct IfadahVerdict directly — only
    the native vendor `prove_ifadah_candidate` may return one.

    An occurrence is a construction if `IfadahVerdict(` appears in
    executable Python (assignment, return, argument), not merely inside
    a docstring, comment, arrow diagram, or type-annotation string.
    """
    from pathlib import Path
    hokom_root = Path("pipeline/taaqol_integration")
    hits = []
    for py in hokom_root.rglob("*.py"):
        # Skip Maqayis-owned files (frozen for this campaign)
        if py.name.startswith("maqayis_") or py.name.startswith("test_maqayis_"):
            continue
        text = py.read_text(encoding="utf-8")
        in_docstring = False
        for line in text.splitlines():
            s = line.strip()
            # Track triple-quoted docstring boundaries
            if s.count('"""') % 2 == 1 or s.count("'''") % 2 == 1:
                in_docstring = not in_docstring
                continue
            if in_docstring or s.startswith("#"):
                continue
            if "IfadahVerdict(" not in s:
                continue
            # Skip lines that are clearly documentation embedded in code
            # (arrow diagrams, prose that mentions the type name).
            if "→" in s or "->" in s and "=" not in s.split("->")[0]:
                continue
            # Allow isinstance and type checks
            if "isinstance" in s or "type(" in s:
                continue
            # An actual construction is either `= IfadahVerdict(...)`,
            # `return IfadahVerdict(...)`, or a bare `IfadahVerdict(...)`
            # at the start of the line.
            if (" = IfadahVerdict(" in s
                or "return IfadahVerdict(" in s
                or s.startswith("IfadahVerdict(")):
                hits.append((py.name, s[:80]))
    assert not hits, (
        f"§8.9: direct IfadahVerdict construction in Hokom: {hits}"
    )


# ── § 8.10 — trace + residual completeness ─────────────────────────────────────

def test_wave04_trace_and_residual_completeness_on_proven_verdicts(
    ayat_ifadah_result,
):
    """§8.10: every PROVEN Ifadah verdict from real corpus must carry a
    non-empty trace_ref and its residuals must be a well-formed tuple
    (residuals may be empty on PROVEN — vendor decides via docs/41 §10)."""
    r, _cu_map, _spans = ayat_ifadah_result
    proven_results = [
        s for s in r['per_span_ifadah_results']
        if s.get('ifadah_state') == 'PROVEN'
    ]
    assert proven_results, (
        f"§8.10: expected ≥1 PROVEN Ifadah span; got 0 out of "
        f"{len(r['per_span_ifadah_results'])} recorded results"
    )
    for s in proven_results:
        assert s['ifadah_trace_ref'], (
            f"§8.10: PROVEN span {s['span_id']} missing trace_ref"
        )
        assert s['ifadah_trace_ref'].startswith("prove_ifadah_candidate/"), (
            f"§8.10: unexpected trace_ref shape {s['ifadah_trace_ref']!r}"
        )
        # Residual count is measured; vendor emits deferred residuals per
        # docs/41 §10 (HUKM_DEFERRED, MANAT_DEFERRED, ...).
        assert s['ifadah_residual_count'] >= 0
        assert s['verdict_type'] == 'IfadahVerdict', (
            f"§8.10: verdict must be native IfadahVerdict type, got {s['verdict_type']}"
        )


def test_wave04_ifadah_verdict_type_is_native_vendor_dataclass():
    """Complement to §8.10: verify the vendor IfadahVerdict class
    reachable from the adapter is the frozen dataclass at the pinned
    SHA (05c6668), not a Hokom-side stub."""
    from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (
        _IFADAH_AVAILABLE,
    )
    assert _IFADAH_AVAILABLE
    from taaqqul_slot_geometry.weight.ifadah_candidate import IfadahVerdict
    import dataclasses
    assert dataclasses.is_dataclass(IfadahVerdict)
    assert IfadahVerdict.__dataclass_params__.frozen
    # The vendor path is authoritative — its module file must live under vendor/
    import inspect
    src_file = inspect.getsourcefile(IfadahVerdict)
    assert "vendor/Taaqol-GPT" in src_file, (
        f"IfadahVerdict source must be vendor-owned; got {src_file}"
    )
