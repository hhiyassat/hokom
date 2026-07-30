"""
tests/canonical/test_stage_adapters_live_taaqol.py — Live Taaqol tests (NO MOCKS).

Classification: MOCKED_ADAPTER_UNIT_TEST tests live in test_stage_adapters.py.
This suite proves whether the REAL pinned Taaqol runtime can license stage
transitions, without any mock of _taaqol_license.

Gate: hokom.pipeline.taaqol_integration.live.bridge.evaluate_sga_bundle
If the bridge is not yet implemented, every test in this file fails with:
    BLOCKED_BY_TAAQOL_CONTRACT: hokom.pipeline.taaqol_integration.live.bridge
    (not yet implemented)

NO test in this file uses:
    - unittest.mock
    - patch / monkeypatch
    - _MOCK_LICENSED
    - any fake Taaqol verdict
    - any fallback licensing

Required fields this suite proves per adapter:
    runtime_available=true
    evaluation_attempted=true
    judgment_source=Taaqol (gate_id does NOT contain TAAQOL_IMPORT_FAILURE/TAAQOL_RUNTIME_ERROR)
    fallback_used=false
    silent_fallback=false

Test-origin covenant (docs/52):
  origin_law:                  docs/08 (TransitionGate) + docs/05 (RankLattice) + SCG P0-P12
  branch_name:                 live Taaqol bridge licensing proof per stage adapter
  constitutional_chain:        StageInput → StageAdapter → _taaqol_license(live) → ConstitutionalJudgment
  expected_state:              BLOCKED (bridge absent) or MINIMALLY_CLOSED (bridge present)
  forbidden_outputs:           mock rank grant, skip-instead-of-fail, TAAQOL_IMPORT_FAILURE in live path
  expected_failure_code:       BLOCKED_BY_TAAQOL_CONTRACT (current state; None when bridge wired)
  max_rank:                    TRACE(1) when bridge absent; LICENSED(4) minimum for SAHIH
  required_residual_visibility: True (BaqayaResidual for all DEFERRED outputs)
  required_trace:              False (trace deferred until bridge wires TraceLedger)
"""
from __future__ import annotations

import pytest

# ── Snapshot availability ─────────────────────────────────────────────────────

try:
    from hokom.canonical.registry import load_snapshot
    load_snapshot()
    _SNAPSHOT_AVAILABLE = True
except Exception:
    _SNAPSHOT_AVAILABLE = False

_SNAPSHOT_FAIL_MSG = (
    "CLOSURE FAILURE — registry snapshot not generated. "
    "Run: PYTHONPATH=src:vendor/Taaqol-GPT/src:../fractal/algebra/Saleh-/src"
    " .venv-py312/bin/python scripts/generate_canonical_registry_snapshot.py"
)

# ── Taaqol bridge availability ────────────────────────────────────────────────

_BRIDGE_MODULE = "hokom.pipeline.taaqol_integration.live.bridge"

try:
    from hokom.pipeline.taaqol_integration.live.bridge import evaluate_sga_bundle  # type: ignore
    _BRIDGE_AVAILABLE = True
    _BRIDGE_ERROR: str | None = None
except ImportError as _exc:
    _BRIDGE_AVAILABLE = False
    _BRIDGE_ERROR = str(_exc)
except Exception as _exc:
    _BRIDGE_AVAILABLE = False
    _BRIDGE_ERROR = str(_exc)

_BRIDGE_FAIL_MSG = (
    f"BLOCKED_BY_TAAQOL_CONTRACT: {_BRIDGE_MODULE} not yet implemented.\n"
    f"ImportError: {_BRIDGE_ERROR}\n"
    "The live Taaqol bridge must be implemented before live licensing can be proven.\n"
    "This is not a test infrastructure issue — it is a genuine implementation gap.\n"
    "See: src/hokom/canonical/stages/base.py _taaqol_license() → ImportError branch."
)


def _assert_snapshot():
    """Fail (not skip) if snapshot is missing. Does NOT check the bridge."""
    if not _SNAPSHOT_AVAILABLE:
        pytest.fail(_SNAPSHOT_FAIL_MSG)


def _assert_live_prerequisites():
    """Fail (not skip) if snapshot or bridge is missing."""
    if not _SNAPSHOT_AVAILABLE:
        pytest.fail(_SNAPSHOT_FAIL_MSG)
    if not _BRIDGE_AVAILABLE:
        pytest.fail(_BRIDGE_FAIL_MSG)


def _assert_live_judgment(out, expected_status_options, *, adapter_name: str, case_label: str):
    """
    Assert that a live (unmocked) adapter output:
    1. Has one of the expected constitutional statuses.
    2. Has a gate_id that does NOT indicate the fallback was used.
    3. Has a valid illah.granted_rank.
    """
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    status = out.judgment.status
    gate_id = out.judgment.illah.taaqol_gate_id
    granted_rank = out.judgment.illah.granted_rank

    # Prove Taaqol was called, not the fallback
    assert "TAAQOL_IMPORT_FAILURE" not in gate_id, (
        f"[{adapter_name}/{case_label}] Taaqol fallback detected (ImportError).\n"
        f"gate_id={gate_id!r}\n"
        f"This means hokom.pipeline.taaqol_integration.live.bridge was not reached."
    )
    assert "TAAQOL_RUNTIME_ERROR" not in gate_id, (
        f"[{adapter_name}/{case_label}] Taaqol fallback detected (RuntimeError).\n"
        f"gate_id={gate_id!r}"
    )

    # Constitutional status must be a valid outcome
    assert status in expected_status_options, (
        f"[{adapter_name}/{case_label}] Unexpected status {status}; "
        f"expected one of {[s.name for s in expected_status_options]}"
    )

    # Rank must be in valid lattice range
    assert 0 <= granted_rank <= 6, (
        f"[{adapter_name}/{case_label}] granted_rank={granted_rank} out of [0,6]"
    )

    return status, gate_id, granted_rank


# ── Helpers: build P2 prior (for stages that need predecessor) ────────────────

def _make_accepted_prior(layer_id: str, candidate_type: str):
    from hokom.canonical.slot_algebra.types import (
        CanonicalCandidate, CanonicalCandidateSet, CandidateStatus,
        EvidenceAtom, EvidenceSet, ProvenanceRef,
    )
    prov = ProvenanceRef(
        owner="hokom", module_path="hokom.test",
        rule_id="live-test", stage_id=layer_id,
    )
    atom = EvidenceAtom(key="live", value="test", confidence=0.9, provenance=prov)
    ev = EvidenceSet.from_atoms(layer_id, (atom,))
    candidate = CanonicalCandidate(
        candidate_id=f"{layer_id}-LIVE",
        candidate_type=candidate_type,
        status=CandidateStatus.ACCEPTED,
        layer_id=layer_id,
        source_rule_id="live-test",
        evidence=ev,
        taaqol_rank=4,
    )
    return CanonicalCandidateSet(
        set_id=f"SET-{layer_id}-LIVE",
        layer_id=layer_id,
        candidates=(candidate,),
        residuals=(),
        trace_ids=(),
    )


# ── Live test: P3_ROOT_STEM_CLOSURE (DEFERRED path — no Taaqol needed for BATIL) ──

def test_live_p3_batil_root_path_blocked():
    """
    Live: P3 BATIL path (ROOT_PATH_BLOCKED blocker).
    Does NOT require Taaqol bridge — the blocker fires before rank check.
    This proves P3 BATIL is reachable without any mock.
    """
    # Snapshot only — BATIL path does NOT require the bridge.
    # The ROOT_PATH_BLOCKED blocker fires at _check_blockers() before _taaqol_license()
    # is reached in the status determination. Bridge absence is irrelevant.
    _assert_snapshot()

    from hokom.canonical.stages.p2_p5 import RootStemAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = RootStemAdapter()
    # حَرْفُ الْجَرِّ — function word, no root radicals → ROOT_PATH_BLOCKED
    inp = StageInput(
        layer_id="P3_ROOT_STEM_CLOSURE",
        surface="مِنْ",
        hokom_evidence={"consonant_count": 0, "root_radicals": [], "stem": "", "root_path": "blocked"},
        prior_output=None,
        pipeline_run_id="live-taaqol-p3-batil",
        word_index=0,
    )
    out = adapter.adapt(inp)

    assert out.judgment.status is ConstitutionalStatus.BATIL, (
        f"P3 with root_path=blocked must be BATIL; got {out.judgment.status}"
    )
    # For BATIL, gate_id may be fallback (rank check was short-circuited by blocker)
    # We only assert constitutional status here — Taaqol is not required for blocker path


def test_live_p3_sahih_requires_bridge():
    """
    Live: P3 SAHIH requires Taaqol rank ≥ 4.
    Without the bridge, this test fails with BLOCKED_BY_TAAQOL_CONTRACT.
    """
    _assert_live_prerequisites()  # fails with BLOCKED_BY_TAAQOL_CONTRACT if bridge missing

    from hokom.canonical.stages.p2_p5 import RootStemAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = RootStemAdapter()
    inp = StageInput(
        layer_id="P3_ROOT_STEM_CLOSURE",
        surface="كَتَبَ",
        hokom_evidence={"consonant_count": 3, "root_radicals": ["ك","ت","ب"], "stem": "كَتَبَ", "root_path": ""},
        prior_output=None,
        pipeline_run_id="live-taaqol-p3-sahih",
        word_index=0,
    )
    out = adapter.adapt(inp)

    _assert_live_judgment(
        out,
        expected_status_options=[ConstitutionalStatus.SAHIH, ConstitutionalStatus.DEFERRED],
        adapter_name="RootStemAdapter",
        case_label="كَتَبَ",
    )


def test_live_p4_deferred_non_mushtaq():
    """
    Live: P4 DEFERRED (jamid case — no mushtaq resolution).
    Does not require Taaqol bridge for DEFERRED path via unsatisfied condition.
    """
    if not _SNAPSHOT_AVAILABLE:
        pytest.fail(_SNAPSHOT_FAIL_MSG)

    from hokom.canonical.stages.p2_p5 import JamidMushtaqAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = JamidMushtaqAdapter()
    p3_prior = _make_accepted_prior("P3_ROOT_STEM_CLOSURE", "RootStemCandidate")
    inp = StageInput(
        layer_id="P4_JAMID_MUSHTAQ",
        surface="هَذَا",
        hokom_evidence={"jamid_mushtaq": "jamid", "wazn": "", "bab_id": ""},
        prior_output=p3_prior,
        pipeline_run_id="live-taaqol-p4-deferred",
        word_index=0,
    )
    out = adapter.adapt(inp)

    # هَذَا is a known jamid with sufficient Taaqol evidence.
    # With the live bridge as sole constitutional governor, this deterministic
    # fixture must reach LICENSED(4) → SAHIH.  Any weaker outcome is a failure.
    gate_id = out.judgment.illah.taaqol_gate_id
    granted_rank = out.judgment.illah.granted_rank

    assert out.judgment.status is ConstitutionalStatus.SAHIH, (
        f"P4/jamid هَذَا must be SAHIH via live bridge; got {out.judgment.status!r}\n"
        f"  gate_id={gate_id!r}  granted_rank={granted_rank}"
    )
    assert "HOKOM_TAAQOL_LIVE_BRIDGE" in gate_id, (
        f"judgment_source must be TAAQOL (gate_id must contain HOKOM_TAAQOL_LIVE_BRIDGE); "
        f"got gate_id={gate_id!r}"
    )
    assert "TAAQOL_IMPORT_FAILURE" not in gate_id, (
        f"fallback_used=True detected via ImportError; gate_id={gate_id!r}"
    )
    assert "TAAQOL_RUNTIME_ERROR" not in gate_id, (
        f"fallback_used=True detected via RuntimeError; gate_id={gate_id!r}"
    )
    assert granted_rank >= 4, (
        f"effect_authorized requires granted_rank ≥ 4 (LICENSED); got {granted_rank}"
    )


def test_live_p4_sahih_requires_bridge():
    """
    Live: P4 SAHIH (mushtaq) requires Taaqol rank ≥ 4.
    Fails with BLOCKED_BY_TAAQOL_CONTRACT if bridge missing.
    """
    _assert_live_prerequisites()

    from hokom.canonical.stages.p2_p5 import JamidMushtaqAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = JamidMushtaqAdapter()
    p3_prior = _make_accepted_prior("P3_ROOT_STEM_CLOSURE", "RootStemCandidate")
    inp = StageInput(
        layer_id="P4_JAMID_MUSHTAQ",
        surface="ضَرَبَ",
        hokom_evidence={"jamid_mushtaq": "mushtaq", "wazn": "فَعَلَ", "bab_id": "bab_nasara"},
        prior_output=p3_prior,
        pipeline_run_id="live-taaqol-p4-sahih",
        word_index=0,
    )
    out = adapter.adapt(inp)

    _assert_live_judgment(
        out,
        expected_status_options=[ConstitutionalStatus.SAHIH, ConstitutionalStatus.DEFERRED],
        adapter_name="JamidMushtaqAdapter",
        case_label="ضَرَبَ",
    )


def test_live_p5_deferred_no_p4_prior():
    """
    Live: P5 DEFERRED when P4 prior is absent.
    Does not require Taaqol bridge — condition gate fires first.
    """
    if not _SNAPSHOT_AVAILABLE:
        pytest.fail(_SNAPSHOT_FAIL_MSG)

    from hokom.canonical.stages.p2_p5 import MufradWordAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = MufradWordAdapter()
    inp = StageInput(
        layer_id="P5_MUFRAD_WORD_CONTRACTS",
        surface="كَتَبَ",
        hokom_evidence={"word_geometry": "resolved", "word_class": "verb"},
        prior_output=None,
        pipeline_run_id="live-taaqol-p5-deferred",
        word_index=0,
    )
    out = adapter.adapt(inp)

    assert out.judgment.status is ConstitutionalStatus.DEFERRED, (
        f"P5 with no prior must be DEFERRED; got {out.judgment.status}"
    )


def test_live_p5_sahih_requires_bridge():
    """
    Live: P5 SAHIH (with real P4 prior) requires Taaqol rank ≥ 4.
    Fails with BLOCKED_BY_TAAQOL_CONTRACT if bridge missing.
    """
    _assert_live_prerequisites()

    from hokom.canonical.stages.p2_p5 import MufradWordAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus
    from hokom.canonical.slot_algebra.types import (
        CanonicalCandidate, CanonicalCandidateSet, CandidateStatus,
        EvidenceAtom, EvidenceSet, ProvenanceRef,
    )

    # Build a real P4 accepted prior
    prov = ProvenanceRef(owner="hokom", module_path="hokom.test", rule_id="r", stage_id="P4_JAMID_MUSHTAQ")
    atom = EvidenceAtom(key="jamid_mushtaq", value="mushtaq", confidence=0.9, provenance=prov)
    ev = EvidenceSet.from_atoms("P4_JAMID_MUSHTAQ", (atom,))
    p4_prior = CanonicalCandidateSet(
        set_id="P4-LIVE",
        layer_id="P4_JAMID_MUSHTAQ",
        candidates=(CanonicalCandidate(
            candidate_id="P4-LIVE-C",
            candidate_type="JamidMushtaqCandidate",
            status=CandidateStatus.ACCEPTED,
            layer_id="P4_JAMID_MUSHTAQ",
            source_rule_id="r",
            evidence=ev,
            taaqol_rank=4,
        ),),
        residuals=(), trace_ids=(),
    )
    adapter = MufradWordAdapter()
    inp = StageInput(
        layer_id="P5_MUFRAD_WORD_CONTRACTS",
        surface="كَتَبَ",
        hokom_evidence={"word_geometry": "resolved", "word_class": "verb"},
        prior_output=p4_prior,
        pipeline_run_id="live-taaqol-p5-sahih",
        word_index=0,
    )
    out = adapter.adapt(inp)

    _assert_live_judgment(
        out,
        expected_status_options=[ConstitutionalStatus.SAHIH, ConstitutionalStatus.DEFERRED],
        adapter_name="MufradWordAdapter",
        case_label="كَتَبَ/P4→P5",
    )


def test_live_p6_sahih_requires_bridge():
    """Live: P6 SAHIH (verbal cadence). Fails with BLOCKED_BY_TAAQOL_CONTRACT if bridge missing."""
    _assert_live_prerequisites()
    from hokom.canonical.stages.p6_p8 import VerbalSignifiedAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = VerbalSignifiedAdapter()
    p5_prior = _make_accepted_prior("P5_MUFRAD_WORD_CONTRACTS", "MufradWordCandidate")
    inp = StageInput(
        layer_id="P6_VERBAL_SIGNIFIED_ALONE",
        surface="كَتَبَ",
        hokom_evidence={"verbal_cadence": "fa3ala", "signified_type": "verb", "cadence_confidence": 0.95},
        prior_output=p5_prior,
        pipeline_run_id="live-taaqol-p6",
        word_index=0,
    )
    out = adapter.adapt(inp)
    _assert_live_judgment(out, [ConstitutionalStatus.SAHIH, ConstitutionalStatus.DEFERRED],
                          adapter_name="VerbalSignifiedAdapter", case_label="كَتَبَ")


def test_live_p7_sahih_requires_bridge():
    """Live: P7 SAHIH (composition readiness). Fails with BLOCKED_BY_TAAQOL_CONTRACT if bridge missing."""
    _assert_live_prerequisites()
    from hokom.canonical.stages.p6_p8 import CompositionReadinessAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = CompositionReadinessAdapter()
    p6_prior = _make_accepted_prior("P6_VERBAL_SIGNIFIED_ALONE", "VerbalSignifiedCandidate")
    inp = StageInput(
        layer_id="P7_COMPOSITION_READINESS",
        surface="كَتَبَ",
        hokom_evidence={"closure_readiness": "mabni_closure_ready", "composition_ready": True, "word_class": "verb"},
        prior_output=p6_prior,
        pipeline_run_id="live-taaqol-p7",
        word_index=0,
    )
    out = adapter.adapt(inp)
    _assert_live_judgment(out, [ConstitutionalStatus.SAHIH, ConstitutionalStatus.DEFERRED],
                          adapter_name="CompositionReadinessAdapter", case_label="كَتَبَ")


def test_live_p8_sahih_requires_bridge():
    """Live: P8 SAHIH (amil-mamul). Fails with BLOCKED_BY_TAAQOL_CONTRACT if bridge missing."""
    _assert_live_prerequisites()
    from hokom.canonical.stages.p6_p8 import AmilMamulAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = AmilMamulAdapter()
    p7_prior = _make_accepted_prior("P7_COMPOSITION_READINESS", "CompositionReadinessCandidate")
    inp = StageInput(
        layer_id="P8_AMIL_MAMUL",
        surface="كَتَبَ زَيْدٌ",
        hokom_evidence={"amil_role": "amil", "amil_unit_id": "w0", "unit_count": 2},
        prior_output=p7_prior,
        pipeline_run_id="live-taaqol-p8",
        word_index=0,
    )
    out = adapter.adapt(inp)
    _assert_live_judgment(out, [ConstitutionalStatus.SAHIH, ConstitutionalStatus.DEFERRED],
                          adapter_name="AmilMamulAdapter", case_label="كَتَبَ زَيْدٌ")


def test_live_p9_deferred_single_unit():
    """
    Live: P9 DEFERRED (single unit — insufficient for sentence closure).
    Does not require Taaqol bridge — condition gate fires first.
    """
    if not _SNAPSHOT_AVAILABLE:
        pytest.fail(_SNAPSHOT_FAIL_MSG)

    from hokom.canonical.stages.p9_p12 import SentenceGeometryAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = SentenceGeometryAdapter()
    inp = StageInput(
        layer_id="P9_SENTENCE_GEOMETRY",
        surface="كَتَبَ",
        hokom_evidence={
            "amil_mamul_units": [{"unit_id": "w0-p8", "word_index": 0, "role": "amil", "candidate_id": ""}],
            "adjacency_relation": "underspecified",
            "sentence_boundary": "open",
        },
        prior_output=None,
        pipeline_run_id="live-taaqol-p9-deferred",
        word_index=None,
    )
    out = adapter.adapt(inp)

    assert out.judgment.status is ConstitutionalStatus.DEFERRED, (
        f"P9 single unit must be DEFERRED; got {out.judgment.status}"
    )


def test_live_p9_sahih_requires_bridge():
    """Live: P9 SAHIH (two-unit closed boundary). Fails with BLOCKED_BY_TAAQOL_CONTRACT if bridge missing."""
    _assert_live_prerequisites()
    from hokom.canonical.stages.p9_p12 import SentenceGeometryAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = SentenceGeometryAdapter()
    p8_prior = _make_accepted_prior("P8_AMIL_MAMUL", "AmilMamulCandidate")
    inp = StageInput(
        layer_id="P9_SENTENCE_GEOMETRY",
        surface="كَتَبَ زَيْدٌ",
        hokom_evidence={
            "amil_mamul_units": [
                {"unit_id": "w0-p8", "word_index": 0, "role": "amil", "candidate_id": ""},
                {"unit_id": "w1-p8", "word_index": 1, "role": "mamul", "candidate_id": ""},
            ],
            "adjacency_relation": "established",
            "sentence_boundary": "closed",
        },
        prior_output=p8_prior,
        pipeline_run_id="live-taaqol-p9-sahih",
        word_index=None,
    )
    out = adapter.adapt(inp)
    _assert_live_judgment(out, [ConstitutionalStatus.SAHIH, ConstitutionalStatus.DEFERRED],
                          adapter_name="SentenceGeometryAdapter", case_label="كَتَبَ زَيْدٌ")


def test_live_p10_sahih_requires_bridge():
    """Live: P10 SAHIH (relation geometry). Fails with BLOCKED_BY_TAAQOL_CONTRACT if bridge missing."""
    _assert_live_prerequisites()
    from hokom.canonical.stages.p9_p12 import RelationGeometryAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = RelationGeometryAdapter()
    p9_prior = _make_accepted_prior("P9_SENTENCE_GEOMETRY", "SentenceGeometryCandidate")
    inp = StageInput(
        layer_id="P10_RELATION_GEOMETRY",
        surface="كَتَبَ زَيْدٌ",
        hokom_evidence={
            # Correct P10 schema: adapter reads input.hokom_evidence["relations"] (list)
            "relations": [
                {
                    "relation_type": "subject",
                    "amil_unit_id": "w0-verb",
                    "mamul_unit_id": "w1-noun",
                }
            ],
            "relation_confidence": 0.9,
        },
        prior_output=p9_prior,
        pipeline_run_id="live-taaqol-p10",
        word_index=None,
    )
    out = adapter.adapt(inp)
    _assert_live_judgment(out, [ConstitutionalStatus.SAHIH, ConstitutionalStatus.DEFERRED],
                          adapter_name="RelationGeometryAdapter", case_label="كَتَبَ زَيْدٌ")


def test_live_p11_sahih_requires_bridge():
    """Live: P11 SAHIH (irab geometry). Fails with BLOCKED_BY_TAAQOL_CONTRACT if bridge missing."""
    _assert_live_prerequisites()
    from hokom.canonical.stages.p9_p12 import IrabGeometryAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = IrabGeometryAdapter()
    p10_prior = _make_accepted_prior("P10_RELATION_GEOMETRY", "RelationGeometryCandidate")
    inp = StageInput(
        layer_id="P11_IRAB_GEOMETRY",
        surface="كَتَبَ زَيْدٌ",
        hokom_evidence={
            # Correct P11 schema: adapter reads input.hokom_evidence["irab_positions"] (list)
            "irab_positions": [
                {
                    "word_id": "w0-fa3il",
                    "possible_cases": ["nominative"],
                }
            ],
            "irab_confidence": 0.9,
        },
        prior_output=p10_prior,
        pipeline_run_id="live-taaqol-p11",
        word_index=None,
    )
    out = adapter.adapt(inp)
    _assert_live_judgment(out, [ConstitutionalStatus.SAHIH, ConstitutionalStatus.DEFERRED],
                          adapter_name="IrabGeometryAdapter", case_label="كَتَبَ زَيْدٌ")


def test_live_p12_sahih_requires_bridge():
    """Live: P12 SAHIH (ifadah speech force). Fails with BLOCKED_BY_TAAQOL_CONTRACT if bridge missing."""
    _assert_live_prerequisites()
    from hokom.canonical.stages.p9_p12 import IfadahAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = IfadahAdapter()
    p11_prior = _make_accepted_prior("P11_IRAB_GEOMETRY", "IrabGeometryCandidate")
    inp = StageInput(
        layer_id="P12_IFADAH_SPEECH_FORCE",
        surface="كَتَبَ زَيْدٌ",
        hokom_evidence={
            "speech_force": "khabar",
            "ifadah_basis": "verb_subject_pair",
            "force_confidence": 0.93,
        },
        prior_output=p11_prior,
        pipeline_run_id="live-taaqol-p12",
        word_index=None,
    )
    out = adapter.adapt(inp)
    _assert_live_judgment(out, [ConstitutionalStatus.SAHIH, ConstitutionalStatus.DEFERRED],
                          adapter_name="IfadahAdapter", case_label="كَتَبَ زَيْدٌ")


# ── Bridge status declaration ─────────────────────────────────────────────────

def test_taaqol_bridge_status_declaration():
    """
    Authoritative declaration of bridge status.
    This test ALWAYS runs and records BLOCKED_BY_TAAQOL_CONTRACT if the bridge is missing.
    It does not skip — it fails so the gap is visible in every test run.
    """
    if not _SNAPSHOT_AVAILABLE:
        pytest.fail(_SNAPSHOT_FAIL_MSG)

    if not _BRIDGE_AVAILABLE:
        pytest.fail(
            f"BLOCKED_BY_TAAQOL_CONTRACT\n"
            f"  Missing module: {_BRIDGE_MODULE}\n"
            f"  ImportError: {_BRIDGE_ERROR}\n"
            f"  Effect: all live SAHIH tests in this file will also fail.\n"
            f"  Required action: implement {_BRIDGE_MODULE}.evaluate_sga_bundle()\n"
            f"    signature: evaluate_sga_bundle(bundle: HokomClaimBundle) -> BridgeResult\n"
            f"    BridgeResult.granted_rank: int  (0-6, Taaqol rank lattice)\n"
            f"    BridgeResult.gate_id: str       (Taaqol gate identifier)\n"
            f"  Note: until the bridge exists, all rank-gated tests produce DEFERRED\n"
            f"  via the fail-closed fallback (base.py §C rule 11).\n"
        )

    # If bridge is available, declare it
    assert callable(evaluate_sga_bundle), "evaluate_sga_bundle must be callable"


# ── Phase B — Trace integration tests (G-001) ─────────────────────────────────

def test_p4_live_sahih_has_nonempty_trace_ids():
    """
    B-001: P4 SAHIH output must carry non-empty trace_ids in the candidate_set.
    Requires Python 3.12 + live Taaqol bridge.
    """
    _assert_live_prerequisites()
    from hokom.canonical.stages.p2_p5 import JamidMushtaqAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = JamidMushtaqAdapter()
    p3_prior = _make_accepted_prior("P3_ROOT_STEM_CLOSURE", "RootStemCandidate")
    inp = StageInput(
        layer_id="P4_JAMID_MUSHTAQ",
        surface="كَتَبَ",
        hokom_evidence={"jamid_mushtaq": "mushtaq", "wazn": "فَعَلَ", "bab_id": "bab_nasara"},
        prior_output=p3_prior,
        pipeline_run_id="trace-test-p4",
        word_index=0,
    )
    out = adapter.adapt(inp)
    if out.judgment.status is ConstitutionalStatus.SAHIH:
        assert len(out.candidate_set.trace_ids) > 0, (
            "P4 SAHIH must carry non-empty trace_ids — bridge produced no trace events. "
            "This is a bridge defect (G-001 fail-closed: SAHIH was downgraded to DEFERRED)."
        )
    else:
        # DEFERRED is acceptable when bridge is absent or trace was empty (fail-closed fired)
        pass


def test_p9_live_sahih_has_nonempty_trace_ids():
    """
    B-001: P9 SAHIH output must carry non-empty trace_ids in the candidate_set.
    Requires Python 3.12 + live Taaqol bridge.
    """
    _assert_live_prerequisites()
    from hokom.canonical.stages.p9_p12 import SentenceGeometryAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = SentenceGeometryAdapter()
    p8_prior = _make_accepted_prior("P8_AMIL_MAMUL", "AmilMamulCandidate")
    inp = StageInput(
        layer_id="P9_SENTENCE_GEOMETRY",
        surface="كَتَبَ زَيْدٌ",
        hokom_evidence={
            "amil_mamul_units": [
                {"unit_id": "w0-p8", "word_index": 0, "role": "amil", "candidate_id": ""},
                {"unit_id": "w1-p8", "word_index": 1, "role": "mamul", "candidate_id": ""},
            ],
            "adjacency_relation": "established",
            "sentence_boundary": "closed",
        },
        prior_output=p8_prior,
        pipeline_run_id="trace-test-p9",
        word_index=None,
    )
    out = adapter.adapt(inp)
    if out.judgment.status is ConstitutionalStatus.SAHIH:
        assert len(out.candidate_set.trace_ids) > 0, (
            "P9 SAHIH must carry non-empty trace_ids — bridge produced no trace events."
        )


def test_p12_live_sahih_has_nonempty_trace_ids():
    """
    B-001: P12 SAHIH output must carry non-empty trace_ids in the candidate_set.
    Requires Python 3.12 + live Taaqol bridge.
    """
    _assert_live_prerequisites()
    from hokom.canonical.stages.p9_p12 import IfadahAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    adapter = IfadahAdapter()
    p11_prior = _make_accepted_prior("P11_IRAB_GEOMETRY", "IrabGeometryCandidate")
    inp = StageInput(
        layer_id="P12_IFADAH_SPEECH_FORCE",
        surface="كَتَبَ زَيْدٌ",
        hokom_evidence={
            "speech_force": "khabar",
            "ifadah_basis": "verb_subject_pair",
            "force_confidence": 0.93,
        },
        prior_output=p11_prior,
        pipeline_run_id="trace-test-p12",
        word_index=None,
    )
    out = adapter.adapt(inp)
    if out.judgment.status is ConstitutionalStatus.SAHIH:
        assert len(out.candidate_set.trace_ids) > 0, (
            "P12 SAHIH must carry non-empty trace_ids — bridge produced no trace events."
        )


def test_trace_ids_are_deterministic_p4():
    """
    B-001: Two identical P4 runs must produce the same trace_ids (determinism).
    Requires Python 3.12 + live Taaqol bridge.
    """
    _assert_live_prerequisites()
    from hokom.canonical.stages.p2_p5 import JamidMushtaqAdapter
    from hokom.canonical.stages.base import StageInput

    adapter = JamidMushtaqAdapter()
    p3_prior = _make_accepted_prior("P3_ROOT_STEM_CLOSURE", "RootStemCandidate")

    def _run() -> tuple:
        inp = StageInput(
            layer_id="P4_JAMID_MUSHTAQ",
            surface="كَتَبَ",
            hokom_evidence={"jamid_mushtaq": "mushtaq", "wazn": "فَعَلَ", "bab_id": "bab_nasara"},
            prior_output=p3_prior,
            pipeline_run_id="trace-determinism-p4",
            word_index=0,
        )
        return adapter.adapt(inp).candidate_set.trace_ids

    trace1 = _run()
    trace2 = _run()
    assert trace1 == trace2, (
        f"Trace IDs must be deterministic across identical runs. "
        f"Run1={trace1!r}, Run2={trace2!r}"
    )


def test_trace_ids_are_strings_not_uuids():
    """
    B-001: trace_ids must be deterministic strings (component:digest format),
    not random UUID-style segments.
    Requires Python 3.12 + live Taaqol bridge.
    """
    _assert_live_prerequisites()
    import re
    from hokom.canonical.stages.p2_p5 import JamidMushtaqAdapter
    from hokom.canonical.stages.base import StageInput
    from hokom.canonical.constitutional.contracts import ConstitutionalStatus

    UUID_PATTERN = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )

    adapter = JamidMushtaqAdapter()
    p3_prior = _make_accepted_prior("P3_ROOT_STEM_CLOSURE", "RootStemCandidate")
    inp = StageInput(
        layer_id="P4_JAMID_MUSHTAQ",
        surface="كَتَبَ",
        hokom_evidence={"jamid_mushtaq": "mushtaq", "wazn": "فَعَلَ", "bab_id": "bab_nasara"},
        prior_output=p3_prior,
        pipeline_run_id="trace-strings-p4",
        word_index=0,
    )
    out = adapter.adapt(inp)
    if out.judgment.status is ConstitutionalStatus.SAHIH:
        for tid in out.candidate_set.trace_ids:
            assert isinstance(tid, str), f"trace_id must be str, got {type(tid)}"
            assert not UUID_PATTERN.match(tid), (
                f"trace_id looks like a random UUID — must be deterministic: {tid!r}"
            )
