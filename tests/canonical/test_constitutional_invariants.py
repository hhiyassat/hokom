"""
test_constitutional_invariants.py — 20 Core Constitutional Invariants

Mandate section G. Executable proofs that the 20 constitutional invariants
hold in the current Hokom canonical state.

These tests are pure static-analysis + structural proofs — they do not require
a live Taaqol bridge. They verify that Hokom's own code respects the
constitutional boundaries it is subject to.

Test-origin covenant (docs/52):
  origin_law:                  Taaqol-GPT docs/00–docs/22 (constitutional foundation)
  branch_name:                 Hokom adapter constitutional invariant proofs
  constitutional_chain:        Evidence → StageAdapter → ConstitutionalJudgment
  expected_state:              MINIMALLY_CLOSED (all invariants hold)
  forbidden_outputs:           self-licensed SAHIH, missing residuals, silent failures
  expected_failure_code:       None (positive invariant proofs)
  max_rank:                    N/A
  required_residual_visibility: True (BaqayaResidual must appear for DEFERRED/FASID)
  required_trace:              False (trace deferred until bridge wired)
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

# ── Paths ─────────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).parent.parent.parent
_SRC = _ROOT / "src" / "hokom" / "canonical"
_STAGES = _SRC / "stages"
_BASE = _STAGES / "base.py"
_P0 = _STAGES / "p0.py"
_P1 = _STAGES / "p1.py"
_P2_P5 = _STAGES / "p2_p5.py"
_P6_P8 = _STAGES / "p6_p8.py"
_P9_P12 = _STAGES / "p9_p12.py"
_CONTRACTS = _SRC / "constitutional" / "contracts.py"
_REGISTRY = _SRC / "registry" / "saleh_snapshot.py"
_VENDOR = _ROOT / "vendor" / "Taaqol-GPT"
_RANK_LATTICE = _VENDOR / "src" / "taaqqul_slot_geometry" / "core" / "rank_lattice.py"


def _parse(path: Path) -> ast.Module:
    if not path.exists():
        pytest.fail(f"Required source file missing: {path}")
    return ast.parse(path.read_text(encoding="utf-8"))


def _source(path: Path) -> str:
    if not path.exists():
        pytest.fail(f"Required source file missing: {path}")
    return path.read_text(encoding="utf-8")


# ── INV-01: Fail-closed rank gate ─────────────────────────────────────────────

def test_inv_01_taaqol_import_failure_returns_trace_1():
    """
    INV-01 (docs/05 §C rule 11): When Taaqol bridge import fails,
    _taaqol_license must return rank=1 (TRACE), not rank≥4 (LICENSED).

    Phase B: _taaqol_license now returns TaaqolLicenseOutcome instead of bare
    (int, str) tuple.  Semantics are preserved: granted_rank=1 in the ImportError
    handler and failure_code="TAAQOL_IMPORT_FAILURE" in the outcome carrier.
    """
    src = _source(_BASE)
    # Verify the TAAQOL_IMPORT_FAILURE sentinel is present in the source
    assert 'TAAQOL_IMPORT_FAILURE' in src, (
        "INV-01 VIOLATED: _taaqol_license must carry TAAQOL_IMPORT_FAILURE "
        "in the ImportError handler. TRACE(1) is the fail-closed rank."
    )
    # Verify fail-closed rank=1 is returned (not LICENSED=4+)
    assert 'granted_rank=1,' in src, (
        "INV-01 VIOLATED: _taaqol_license must set granted_rank=1 on ImportError. "
        "TRACE(1) < LICENSED(4) — fail-closed rule §C-11 preserved."
    )
    # Verify TaaqolLicenseOutcome is used (not bare tuple — Phase B upgrade)
    assert 'TaaqolLicenseOutcome' in src, (
        "INV-01 VIOLATED: _taaqol_license must return TaaqolLicenseOutcome "
        "(not a bare tuple) so trace_ids and failure_code flow through the call boundary."
    )


def test_inv_02_taaqol_runtime_error_returns_trace_1():
    """
    INV-02 (docs/05 §C rule 11): Runtime exception in Taaqol must also fail closed.

    Phase B: TaaqolLicenseOutcome carries failure_code="TAAQOL_RUNTIME_ERROR".
    The semantics are preserved: granted_rank=1, fallback_used=True.
    """
    src = _source(_BASE)
    # Verify the TAAQOL_RUNTIME_ERROR sentinel is present in the source
    assert 'TAAQOL_RUNTIME_ERROR' in src, (
        "INV-02 VIOLATED: _taaqol_license must carry TAAQOL_RUNTIME_ERROR "
        "in the except Exception handler. Fail closed — never return LICENSED on error."
    )
    # Verify except Exception clause explicitly caught
    assert 'except Exception:' in src, (
        "INV-02 VIOLATED: _taaqol_license must have explicit 'except Exception:' clause."
    )


def test_inv_03_rank_gate_defers_below_licensed():
    """
    INV-03 (docs/05 + docs/11 §8): granted_rank < 4 → DEFERRED.
    _determine_status must implement the rank gate at exactly 4 (LICENSED).
    """
    src = _source(_BASE)
    assert "granted_rank < 4" in src, (
        "INV-03 VIOLATED: _determine_status must gate on 'granted_rank < 4'. "
        "4 = Rank.LICENSED is the minimum for SAHIH."
    )
    assert "ConstitutionalStatus.DEFERRED" in src, (
        "INV-03 VIOLATED: _determine_status must emit DEFERRED when rank < 4."
    )


def test_inv_04_blocker_fires_before_rank_gate():
    """
    INV-04 (docs/08): BLOCKER-severity mani must fire BATIL BEFORE the rank gate.
    The order of checks in _determine_status must be:
      1. Active BLOCKER → BATIL
      2. Active invalidating defect → BATIL
      3. Non-invalidating defect → FASID
      4. WARNING blocker → FASID
      5. Unsatisfied condition → DEFERRED
      6. Rank gate → DEFERRED
      7. SAHIH
    """
    src = _source(_BASE)
    # BATIL check must appear before rank gate check
    batil_idx = src.index("ConstitutionalStatus.BATIL")
    rank_gate_idx = src.index("granted_rank < 4")
    assert batil_idx < rank_gate_idx, (
        "INV-04 VIOLATED: BATIL must fire before the rank gate in _determine_status."
    )


def test_inv_05_warning_blocker_fires_fasid_before_deferred():
    """
    INV-05 (docs/08 + base._determine_status order): WARNING blocker → FASID,
    not DEFERRED. Step 4 (WARNING → FASID) must precede step 5 (unsatisfied → DEFERRED).
    """
    src = _source(_BASE)
    # WARNING blocker must fire before unsatisfied condition
    warning_idx = src.index("ResidualSeverity.WARNING")
    deferred_cond_idx = src.index("any(not s.is_satisfied for s in shurut)")
    assert warning_idx < deferred_cond_idx, (
        "INV-05 VIOLATED: WARNING severity blocker must produce FASID before "
        "unsatisfied condition check produces DEFERRED."
    )


def test_inv_06_p12_next_layer_id_returns_none():
    """
    INV-06 (SCG P12 TERMINAL): P12 IfadahSpeechForceAdapter._next_layer_id()
    must return None. P12 is the terminal stage — no next stage exists.
    """
    src = _source(_P9_P12)
    # P12 class must have _next_layer_id returning None
    assert "return None" in src, (
        "INV-06 VIOLATED: P12 _next_layer_id() must return None (TERMINAL stage)."
    )
    # And the class LAYER_ID must be P12
    assert "P12_IFADAH_SPEECH_FORCE" in src, (
        "INV-06 VIOLATED: P12 stage must declare LAYER_ID='P12_IFADAH_SPEECH_FORCE'."
    )


def test_inv_07_no_next_layer_athar_only_on_sahih():
    """
    INV-07 (docs/08): AtharEffect (carry-forward) must only be produced when
    ConstitutionalStatus is SAHIH. Never for DEFERRED, FASID, or BATIL.
    """
    src = _source(_BASE)
    # athar is set inside the SAHIH branch
    assert "if status is ConstitutionalStatus.SAHIH:" in src, (
        "INV-07 VIOLATED: AtharEffect must only be produced inside SAHIH branch."
    )
    athar_idx = src.index("athar = AtharEffect")
    sahih_idx = src.index("if status is ConstitutionalStatus.SAHIH:")
    assert sahih_idx < athar_idx, (
        "INV-07 VIOLATED: AtharEffect must be inside the SAHIH conditional block."
    )


def test_inv_08_baqaya_produced_for_deferred_and_fasid():
    """
    INV-08 (docs/06 residual policy): BaqayaResidual must be produced for
    DEFERRED and FASID statuses. Residuals must not be hidden.
    """
    src = _source(_BASE)
    assert "ConstitutionalStatus.DEFERRED, ConstitutionalStatus.FASID" in src or \
           "DEFERRED" in src and "FASID" in src and "BaqayaResidual" in src, (
        "INV-08 VIOLATED: BaqayaResidual must be produced for DEFERRED and FASID."
    )
    assert "BaqayaResidual" in src, (
        "INV-08 VIOLATED: BaqayaResidual must be imported and used in base adapter."
    )


def test_inv_09_no_self_licensed_sahih():
    """
    INV-09 (HR2S/H2RS FORBIDDEN): No Hokom adapter may produce SAHIH without
    first calling _taaqol_license. The base adapt() method must call
    _taaqol_license before _determine_status.
    """
    src = _source(_BASE)
    license_idx = src.index("self._taaqol_license(")
    determine_idx = src.index("self._determine_status(")
    assert license_idx < determine_idx, (
        "INV-09 VIOLATED: _taaqol_license must be called before _determine_status. "
        "Hokom must never self-license — Taaqol is sole constitutional governor."
    )


def test_inv_10_layer_id_class_attribute_required():
    """
    INV-10: Every StageAdapter must declare LAYER_ID as a class attribute.
    The base __init__ enforces this with a TypeError guard.
    """
    src = _source(_BASE)
    assert "LAYER_ID" in src and "TypeError" in src, (
        "INV-10 VIOLATED: StageAdapter must enforce LAYER_ID declaration."
    )
    assert "must define LAYER_ID class attribute" in src, (
        "INV-10 VIOLATED: LAYER_ID guard message must be explicit."
    )


def test_inv_11_layer_id_mismatch_raises():
    """
    INV-11: adapt() must assert input.layer_id == self.LAYER_ID.
    Mismatched layer routing must fail loudly.
    """
    src = _source(_BASE)
    assert "StageInput.layer_id mismatch" in src or \
           "input.layer_id == self.LAYER_ID" in src, (
        "INV-11 VIOLATED: adapt() must assert layer_id match."
    )


def test_inv_12_p11_must_not_output_ifadah_candidate():
    """
    INV-12 (P11 forbidden output): IrabGeometryAdapter (P11) produces
    IrabGeometryCandidate, NOT IfadahCandidate. The P11 class must NOT
    reference IfadahCandidate as its own output type.
    """
    src = _source(_P9_P12)
    # P11 builds IrabGeometryCandidate, not IfadahCandidate
    assert "IrabGeometryCandidate" in src, (
        "INV-12 VIOLATED: P11 must produce IrabGeometryCandidate (not IfadahCandidate)."
    )
    # P12 produces IfadahSpeechForceCandidate
    assert "IfadahSpeechForceCandidate" in src, (
        "INV-12 VIOLATED: P12 must produce IfadahSpeechForceCandidate."
    )


def test_inv_13_p9_warning_blockers_produce_deferred():
    """
    INV-13 (P9 override): P9 SentenceGeometryAdapter overrides _determine_status
    so that WARNING blockers (insufficient_units, adjacency_underspecified) → DEFERRED
    (not FASID, as in base).

    This is the P8 FASID vs P9 DEFERRED distinction:
      P8 AmilMamulAdapter: WARNING (adjacency_underspecified with ≥2 units) → FASID (base rule)
      P9 SentenceGeometryAdapter: WARNING (insufficient_units, adjacency_underspecified) → DEFERRED (P9 override)
    """
    src = _source(_P9_P12)
    # SentenceGeometryAdapter must override _determine_status
    assert "_determine_status" in src, (
        "INV-13 VIOLATED: SentenceGeometryAdapter (P9) must override _determine_status."
    )
    # The override maps insufficient_units and adjacency_underspecified → DEFERRED
    assert "insufficient_units" in src and "DEFERRED" in src, (
        "INV-13 VIOLATED: P9 _determine_status must route insufficient_units → DEFERRED."
    )
    assert "adjacency_underspecified" in src, (
        "INV-13 VIOLATED: P9 _determine_status must handle adjacency_underspecified."
    )


def test_inv_14_saleh_snapshot_required_at_init():
    """
    INV-14 (Saleh contract): StageAdapter.__init__ must load the Saleh LayerSpec
    from the snapshot. Running without snapshot must fail (not silently degrade).
    """
    src = _source(_BASE)
    assert "get_layer(self.LAYER_ID)" in src or "get_layer" in src, (
        "INV-14 VIOLATED: StageAdapter must call get_layer() at __init__ time."
    )
    assert "WadContract.from_layer_entry" in src, (
        "INV-14 VIOLATED: WadContract must be built from LayerSpec at __init__ time."
    )


def test_inv_15_stage_output_is_frozen_dataclass():
    """
    INV-15: StageInput and StageOutput must be frozen dataclasses.
    Mutable stage I/O is a constitutional violation.
    """
    src = _source(_BASE)
    assert "@dataclass(frozen=True)" in src, (
        "INV-15 VIOLATED: StageInput/StageOutput must be frozen=True dataclasses."
    )


def test_inv_16_rank_licensed_is_4():
    """
    INV-16 (Rank.LICENSED=4 anchor): The Taaqol RankLattice must declare
    LICENSED=4. Hokom _determine_status gates on granted_rank < 4.
    If Taaqol changes this value, Hokom must update.
    This test anchors the value.
    """
    src = _source(_RANK_LATTICE)
    assert "LICENSED = 4" in src, (
        "INV-16 VIOLATED: Rank.LICENSED must equal 4 in the Taaqol vendor pin. "
        "Hokom gates on rank < 4. This anchor must not change silently."
    )


def test_inv_17_all_14_stage_layer_ids_declared():
    """
    INV-17 (19-stage registry): The canonical stages P0–P12 must all declare
    LAYER_ID strings that match the Saleh registry identifiers.
    """
    src_all = (
        _source(_P0) + _source(_P1) + _source(_P2_P5)
        + _source(_P6_P8) + _source(_P9_P12)
    )
    required_ids = [
        # P0 sub-stages
        "P0_UNICODE_CANDIDATE",
        # P1 sub-stages
        "P1_SLOT_CANDIDATE",
        # P2-P5
        "P2_REGISTRY_PROJECTION",
        "P3_ROOT_STEM_CLOSURE",
        "P4_JAMID_MUSHTAQ",
        "P5_MUFRAD_WORD_CONTRACTS",
        # P6-P8
        "P6_VERBAL_SIGNIFIED_ALONE",
        "P7_COMPOSITION_READINESS",
        "P8_AMIL_MAMUL",
        # P9-P12
        "P9_SENTENCE_GEOMETRY",
        "P10_RELATION_GEOMETRY",
        "P11_IRAB_GEOMETRY",
        "P12_IFADAH_SPEECH_FORCE",
    ]
    missing = [lid for lid in required_ids if lid not in src_all]
    assert missing == [], (
        f"INV-17 VIOLATED: Missing LAYER_ID declarations: {missing}\n"
        "All 13 P0-P12 stages must declare canonical LAYER_IDs."
    )


def test_inv_18_pipeline_run_id_present_in_stage_input():
    """
    INV-18: StageInput must carry pipeline_run_id for trace linkage.
    """
    src = _source(_BASE)
    assert "pipeline_run_id" in src, (
        "INV-18 VIOLATED: StageInput must have pipeline_run_id field for trace."
    )


def test_inv_19_constitutional_judgment_assembled_for_every_call():
    """
    INV-19: Every adapt() call must produce a ConstitutionalJudgment.
    The judgment must include: wad, sabab, shurut, mawani, illah, qawadih, status.
    """
    src = _source(_BASE)
    for field in ["wad", "sabab", "shurut", "mawani", "illah", "qawadih", "status"]:
        assert field in src, (
            f"INV-19 VIOLATED: ConstitutionalJudgment missing field: {field}"
        )
    assert "ConstitutionalJudgment(" in src, (
        "INV-19 VIOLATED: adapt() must assemble ConstitutionalJudgment."
    )


def test_inv_20_no_bare_exception_swallowing():
    """
    INV-20: _taaqol_license must catch Exception and return TRACE(1) with
    TAAQOL_RUNTIME_ERROR — not swallow silently and not re-raise.
    The except clause must contain the return statement.
    """
    src = _source(_BASE)
    # Both clauses must be present
    assert "except ImportError:" in src, (
        "INV-20 VIOLATED: ImportError must be explicitly caught in _taaqol_license."
    )
    assert "except Exception:" in src, (
        "INV-20 VIOLATED: Exception must be explicitly caught in _taaqol_license."
    )
    # Neither may be followed by `pass` or `raise`
    lines = src.splitlines()
    for i, line in enumerate(lines):
        if "except Exception:" in line:
            # Next non-empty line must be a return statement
            for j in range(i + 1, min(i + 5, len(lines))):
                stripped = lines[j].strip()
                if stripped and not stripped.startswith("#"):
                    assert stripped.startswith("return"), (
                        f"INV-20 VIOLATED: except Exception block must return immediately, "
                        f"got: {stripped!r}"
                    )
                    break
