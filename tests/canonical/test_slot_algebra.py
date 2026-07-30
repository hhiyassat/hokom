"""
tests/canonical/test_slot_algebra.py — Slot Algebra Engineering type tests.

Tests:
    01 — SlotState enum values match canonical spec
    02 — CandidateStatus mirrors Saleh (ACCEPTED/DEFERRED/BLOCKED)
    03 — ProvenanceRef rejects invalid owner
    04 — ProvenanceRef accepts "hokom", "saleh", "taaqol"
    05 — EvidenceAtom rejects confidence outside [0.0, 1.0]
    06 — EvidenceAtom confidence bound: exactly 0.0 and 1.0 accepted
    07 — EvidenceSet.from_atoms computes correct aggregate_confidence
    08 — EvidenceSet with empty atoms produces aggregate_confidence=0.0
    09 — EvidenceSet.as_taaqol_sources returns correct strings
    10 — Residual requires non-empty residual_id
    11 — CanonicalCandidate rejects forbidden output flags
    12 — CanonicalCandidate rejects taaqol_rank outside [0,6]
    13 — CanonicalCandidateSet.accepted filters correctly
    14 — CanonicalCandidateSet.is_licensed True iff taaqol_rank >= 4
    15 — claim_key is deterministic and prefixed with "CK-"
    16 — evaluation_id is deterministic and prefixed with "EV-"
    17 — claim_key invariance: same surface+stage+rule → same key
    18 — NFC normalization: composed and decomposed surface → same key
"""
import pytest

from hokom.canonical.slot_algebra.types import (
    CandidateStatus,
    CanonicalCandidate,
    CanonicalCandidateSet,
    EvidenceAtom,
    EvidenceSet,
    ProvenanceRef,
    Residual,
    ResidualSeverity,
    SlotState,
)
from hokom.canonical.slot_algebra.claim_key import claim_key, evaluation_id


# ── Helpers ───────────────────────────────────────────────────────────────────

def _prov(owner="hokom") -> ProvenanceRef:
    return ProvenanceRef(
        owner=owner,
        module_path="hokom.test",
        rule_id="test_rule",
        stage_id="P0_UNICODE_CANDIDATE",
    )

def _atom(key="k", value="v", confidence=0.9) -> EvidenceAtom:
    return EvidenceAtom(key=key, value=value, confidence=confidence, provenance=_prov())

def _candidate(
    candidate_id="C1",
    status=CandidateStatus.ACCEPTED,
    taaqol_rank=4,
    output_flags=frozenset(),
) -> CanonicalCandidate:
    ev = EvidenceSet.from_atoms("P0_UNICODE_CANDIDATE", (_atom(),))
    return CanonicalCandidate(
        candidate_id=candidate_id,
        candidate_type="UnicodeCandidate",
        status=status,
        layer_id="P0_UNICODE_CANDIDATE",
        source_rule_id="test_rule",
        evidence=ev,
        taaqol_rank=taaqol_rank,
        output_flags=output_flags,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_01_slot_state_values():
    states = {s.value for s in SlotState}
    assert "unknown" in states
    assert "licensed" in states
    assert "deferred" in states
    assert "blocked" in states
    assert len(states) == 9


def test_02_candidate_status_mirrors_saleh():
    assert CandidateStatus.ACCEPTED.value == "accepted"
    assert CandidateStatus.DEFERRED.value == "deferred"
    assert CandidateStatus.BLOCKED.value == "blocked"


def test_03_provenance_ref_rejects_invalid_owner():
    with pytest.raises(ValueError, match="owner"):
        ProvenanceRef(
            owner="hr2s",   # FORBIDDEN
            module_path="hokom.test",
            rule_id="r",
            stage_id="P0_UNICODE_CANDIDATE",
        )


def test_04_provenance_ref_accepts_valid_owners():
    for owner in ("hokom", "saleh", "taaqol"):
        ref = ProvenanceRef(owner=owner, module_path="m", rule_id="r", stage_id="P0_UNICODE_CANDIDATE")
        assert ref.owner == owner


def test_05_evidence_atom_rejects_out_of_range_confidence():
    with pytest.raises(ValueError, match="confidence"):
        EvidenceAtom(key="k", value="v", confidence=1.5, provenance=_prov())
    with pytest.raises(ValueError, match="confidence"):
        EvidenceAtom(key="k", value="v", confidence=-0.1, provenance=_prov())


def test_06_evidence_atom_accepts_boundary_confidence():
    a0 = EvidenceAtom(key="k", value="v", confidence=0.0, provenance=_prov())
    a1 = EvidenceAtom(key="k", value="v", confidence=1.0, provenance=_prov())
    assert a0.confidence == 0.0
    assert a1.confidence == 1.0


def test_07_evidence_set_aggregate_confidence():
    atoms = (
        _atom("k1", confidence=0.9),
        _atom("k2", confidence=0.7),
        _atom("k3", confidence=0.8),
    )
    ev = EvidenceSet.from_atoms("P0_UNICODE_CANDIDATE", atoms)
    assert abs(ev.aggregate_confidence - 0.7) < 1e-9


def test_08_evidence_set_empty_atoms_zero_confidence():
    ev = EvidenceSet.from_atoms("P0_UNICODE_CANDIDATE", ())
    assert ev.aggregate_confidence == 0.0


def test_09_evidence_set_as_taaqol_sources():
    atom = EvidenceAtom(
        key="root_r1",
        value="ك",
        confidence=0.9,
        provenance=ProvenanceRef(
            owner="hokom",
            module_path="hokom.pipeline.p3_pre_root",
            rule_id="root_extraction",
            stage_id="P3_ROOT_STEM_CLOSURE",
        ),
    )
    ev = EvidenceSet.from_atoms("P3_ROOT_STEM_CLOSURE", (atom,))
    sources = ev.as_taaqol_sources()
    assert len(sources) == 1
    assert "P3_ROOT_STEM_CLOSURE" in sources[0]
    assert "root_r1" in sources[0]


def test_10_residual_requires_non_empty_id():
    with pytest.raises(ValueError, match="residual_id"):
        Residual(
            residual_id="",
            stage_id="P3_ROOT_STEM_CLOSURE",
            reason_code="test",
            severity=ResidualSeverity.WARNING,
            detail="test",
        )


def test_11_canonical_candidate_rejects_forbidden_flags():
    forbidden_flags = [
        frozenset({"HukmCandidate"}),
        frozenset({"RealityClaim"}),
        frozenset({"FinalMeaning"}),
        frozenset({"FinalCaseJudgment"}),
        frozenset({"HukmCandidate", "RealityClaim"}),
    ]
    for flags in forbidden_flags:
        with pytest.raises(ValueError, match="forbidden"):
            _candidate(output_flags=flags)


def test_12_canonical_candidate_rejects_invalid_taaqol_rank():
    with pytest.raises(ValueError, match="taaqol_rank"):
        _candidate(taaqol_rank=7)
    with pytest.raises(ValueError, match="taaqol_rank"):
        _candidate(taaqol_rank=-1)


def test_13_candidate_set_accepted_filter():
    c_acc = _candidate("C1", CandidateStatus.ACCEPTED, 4)
    c_def = _candidate("C2", CandidateStatus.DEFERRED, 2)
    c_blk = _candidate("C3", CandidateStatus.BLOCKED, 0)
    cs = CanonicalCandidateSet(
        set_id="S1",
        layer_id="P0_UNICODE_CANDIDATE",
        candidates=(c_acc, c_def, c_blk),
        residuals=(),
        trace_ids=(),
    )
    assert cs.accepted == (c_acc,)
    assert cs.deferred == (c_def,)
    assert cs.blocked == (c_blk,)


def test_14_candidate_set_is_licensed():
    c_licensed = _candidate("C1", CandidateStatus.ACCEPTED, taaqol_rank=4)
    c_unlicensed = _candidate("C2", CandidateStatus.DEFERRED, taaqol_rank=3)

    cs_licensed = CanonicalCandidateSet(
        set_id="S1", layer_id="P0_UNICODE_CANDIDATE",
        candidates=(c_licensed,), residuals=(), trace_ids=()
    )
    cs_unlicensed = CanonicalCandidateSet(
        set_id="S2", layer_id="P0_UNICODE_CANDIDATE",
        candidates=(c_unlicensed,), residuals=(), trace_ids=()
    )
    assert cs_licensed.is_licensed is True
    assert cs_unlicensed.is_licensed is False


def test_15_claim_key_prefixed():
    ck = claim_key("كَتَبَ", "P3_ROOT_STEM_CLOSURE", "root_extraction")
    assert ck.startswith("CK-")
    assert len(ck) == 3 + 16  # "CK-" + 16 hex


def test_16_evaluation_id_prefixed():
    ev = evaluation_id("كَتَبَ", "run-001")
    assert ev.startswith("EV-")
    assert len(ev) == 3 + 16


def test_17_claim_key_deterministic():
    ck1 = claim_key("كَتَبَ", "P3_ROOT_STEM_CLOSURE", "root_extraction")
    ck2 = claim_key("كَتَبَ", "P3_ROOT_STEM_CLOSURE", "root_extraction")
    assert ck1 == ck2


def test_18_claim_key_nfc_invariance():
    import unicodedata
    surface_composed = "كَتَبَ"   # NFC
    surface_decomp = unicodedata.normalize("NFD", surface_composed)
    # claim_key should normalize to NFC before hashing
    ck_composed = claim_key(surface_composed, "P3_ROOT_STEM_CLOSURE", "root_extraction")
    ck_decomp = claim_key(surface_decomp, "P3_ROOT_STEM_CLOSURE", "root_extraction")
    assert ck_composed == ck_decomp


# ── Phase A — EvidenceAtom provenance guard tests (G-004) ────────────────────

def test_evidence_atom_none_provenance_rejected_at_construction():
    """G-004: EvidenceAtom(provenance=None) must raise ValueError at construction."""
    with pytest.raises((ValueError, TypeError)):
        EvidenceAtom(key="k", value="v", confidence=0.9, provenance=None)


def test_evidence_atom_wrong_provenance_type_rejected():
    """G-004: EvidenceAtom(provenance="string") must raise TypeError."""
    with pytest.raises(TypeError, match="ProvenanceRef"):
        EvidenceAtom(key="k", value="v", confidence=0.9, provenance="string_not_prov")


def test_evidence_atom_empty_stage_id_rejected():
    """G-004: ProvenanceRef with stage_id='' must be rejected (ProvenanceRef itself validates)."""
    with pytest.raises(ValueError):
        ProvenanceRef(
            owner="hokom",
            module_path="hokom.test",
            rule_id="r",
            stage_id="",  # empty — ProvenanceRef.__post_init__ rejects this
        )


def test_evidence_atom_valid_provenance_accepted():
    """G-004 happy path: valid ProvenanceRef accepted with no exception."""
    prov = ProvenanceRef(
        owner="hokom",
        module_path="hokom.pipeline.p3_pre_root",
        rule_id="root_stem_extraction",
        stage_id="P3_ROOT_STEM_CLOSURE",
    )
    atom = EvidenceAtom(key="root_class", value="trilateral", confidence=0.92, provenance=prov)
    assert atom.provenance is prov
    assert atom.key == "root_class"


def test_evidence_set_as_taaqol_sources_succeeds_with_valid_provenance():
    """G-004: as_taaqol_sources() works when provenance is valid."""
    prov = ProvenanceRef(
        owner="hokom",
        module_path="hokom.pipeline.p3_pre_root",
        rule_id="root_stem_extraction",
        stage_id="P3_ROOT_STEM_CLOSURE",
    )
    atom = EvidenceAtom(key="root_r1", value="ك", confidence=0.92, provenance=prov)
    ev = EvidenceSet.from_atoms("P3_ROOT_STEM_CLOSURE", (atom,))
    sources = ev.as_taaqol_sources()
    assert len(sources) == 1
    assert "P3_ROOT_STEM_CLOSURE:root_r1=ك" in sources[0]


def test_invalid_evidence_atom_cannot_reach_as_taaqol_sources():
    """G-004: Provenance=None is rejected at construction, never reaches as_taaqol_sources."""
    with pytest.raises((ValueError, TypeError)):
        # Must raise at EvidenceAtom construction, not later
        atom = EvidenceAtom(key="k", value="v", confidence=0.9, provenance=None)
        # This line must never be reached:
        EvidenceSet.from_atoms("P3_ROOT_STEM_CLOSURE", (atom,)).as_taaqol_sources()


def test_provenance_guard_exception_message_is_stable():
    """G-004: ValueError message for provenance=None contains 'provenance' and 'None'."""
    try:
        EvidenceAtom(key="k", value="v", confidence=0.9, provenance=None)
        pytest.fail("Expected ValueError or TypeError was not raised")
    except (ValueError, TypeError) as exc:
        msg = str(exc).lower()
        assert "provenance" in msg, f"Expected 'provenance' in error message, got: {exc!r}"
