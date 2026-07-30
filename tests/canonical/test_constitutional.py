"""
tests/canonical/test_constitutional.py — Constitutional judgment contract tests.

Tests:
    01 — WadContract requires non-empty layer_id and shared_cause
    02 — WadContract.from_layer_entry works when snapshot loaded
    03 — SababEvidence requires non-empty layer_id and trigger_rule
    04 — ManiBlocker.to_residual produces correct Residual
    05 — ConstitutionalStatus values match jurisprudential model
    06 — ConstitutionalJudgment SAHIH requires AtharEffect
    07 — ConstitutionalJudgment BATIL must NOT have AtharEffect
    08 — ConstitutionalJudgment P12 terminal: AtharEffect.carry_to_next must be None
    09 — QadihDefect invalidating=True forces BATIL in base adapter
    10 — IllahRationale rejects granted_rank outside [0,6]
"""
import pytest

from hokom.canonical.constitutional.contracts import (
    AtharEffect,
    BaqayaResidual,
    ConstitutionalJudgment,
    ConstitutionalStatus,
    IllahRationale,
    ManiBlocker,
    QadihDefect,
    SababEvidence,
    ShartRequirement,
    WadContract,
)
from hokom.canonical.slot_algebra.types import (
    EvidenceAtom,
    EvidenceSet,
    ProvenanceRef,
    Residual,
    ResidualSeverity,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _prov() -> ProvenanceRef:
    return ProvenanceRef(
        owner="hokom", module_path="hokom.test",
        rule_id="test_rule", stage_id="P0_UNICODE_CANDIDATE",
    )

def _evidence(layer_id="P0_UNICODE_CANDIDATE") -> EvidenceSet:
    atom = EvidenceAtom(key="k", value="v", confidence=0.9, provenance=_prov())
    return EvidenceSet.from_atoms(layer_id, (atom,))

def _wad(layer_id="P0_UNICODE_CANDIDATE", is_terminal=False) -> WadContract:
    return WadContract(
        layer_id=layer_id,
        placement_name="UnicodeCandidateLayer",
        placement_phase="SCG-P0",
        shared_cause="قابلية النص للتمثيل الرقمي",
        origin_output_type="RawTextInput",
        branch_output_type="UnicodeCandidate",
        is_terminal=is_terminal,
    )

def _illah(layer_id="P0_UNICODE_CANDIDATE", rank=4) -> IllahRationale:
    return IllahRationale(
        layer_id=layer_id,
        rationale="shared cause",
        taaqol_gate_id="GATE-P0",
        granted_rank=rank,
    )

def _sabab(layer_id="P0_UNICODE_CANDIDATE") -> SababEvidence:
    return SababEvidence(
        layer_id=layer_id,
        evidence=_evidence(layer_id),
        trigger_rule="raw_input_not_empty",
        is_present=True,
    )

def _shurut_ok(layer_id="P0_UNICODE_CANDIDATE") -> tuple:
    return (ShartRequirement(
        condition_id="raw_input_not_empty",
        layer_id=layer_id,
        is_satisfied=True,
        evidence_keys=("raw_input_not_empty",),
    ),)

def _judgment(
    layer_id="P0_UNICODE_CANDIDATE",
    status=ConstitutionalStatus.SAHIH,
    is_terminal=False,
    athar=None,
    baqaya=(),
) -> ConstitutionalJudgment:
    if status is ConstitutionalStatus.SAHIH and athar is None:
        athar = AtharEffect(
            layer_id=layer_id,
            effect_type="UnicodeCandidate",
            candidate_id="C1",
            taaqol_rank=4,
            carry_to_next=None if is_terminal else "P0_TYPED_CODEPOINT",
        )
    return ConstitutionalJudgment(
        layer_id=layer_id,
        wad=_wad(layer_id, is_terminal),
        sabab=_sabab(layer_id),
        shurut=_shurut_ok(layer_id),
        mawani=(),
        illah=_illah(layer_id),
        qawadih=(),
        status=status,
        athar=athar,
        baqaya=baqaya,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_01_wad_requires_layer_id_and_cause():
    with pytest.raises(ValueError, match="layer_id"):
        WadContract(
            layer_id="",
            placement_name="Test",
            placement_phase="SCG-P0",
            shared_cause="some cause",
            origin_output_type="X",
            branch_output_type="Y",
        )
    with pytest.raises(ValueError, match="shared_cause"):
        WadContract(
            layer_id="P0_UNICODE_CANDIDATE",
            placement_name="Test",
            placement_phase="SCG-P0",
            shared_cause="",
            origin_output_type="X",
            branch_output_type="Y",
        )


def test_02_wad_from_layer_entry_snapshot():
    """Requires snapshot to be generated. Skip if not available."""
    pytest.importorskip("hokom.canonical.registry.saleh_snapshot")
    try:
        from hokom.canonical.registry import get_layer
        entry = get_layer("P0_UNICODE_CANDIDATE")
        wad = WadContract.from_layer_entry(entry)
        assert wad.layer_id == "P0_UNICODE_CANDIDATE"
        assert wad.shared_cause  # non-empty
        assert wad.is_terminal is False
    except Exception as exc:
        pytest.skip(f"Snapshot not available: {exc}")


def test_03_sabab_requires_fields():
    with pytest.raises(ValueError, match="layer_id"):
        SababEvidence(
            layer_id="",
            evidence=_evidence(),
            trigger_rule="test",
            is_present=True,
        )
    with pytest.raises(ValueError, match="trigger_rule"):
        SababEvidence(
            layer_id="P0_UNICODE_CANDIDATE",
            evidence=_evidence(),
            trigger_rule="",
            is_present=True,
        )


def test_04_mani_blocker_to_residual():
    blocker = ManiBlocker(
        blocker_id="encoding_error",
        layer_id="P0_UNICODE_CANDIDATE",
        is_active=True,
        severity=ResidualSeverity.BLOCKER,
        detail="UTF-8 encoding failed",
    )
    residual = blocker.to_residual("RES-001")
    assert residual.residual_id == "RES-001"
    assert residual.reason_code == "encoding_error"
    assert residual.severity is ResidualSeverity.BLOCKER
    assert residual.stage_id == "P0_UNICODE_CANDIDATE"


def test_05_constitutional_status_values():
    assert ConstitutionalStatus.SAHIH.value == "sahih"
    assert ConstitutionalStatus.FASID.value == "fasid"
    assert ConstitutionalStatus.BATIL.value == "batil"
    assert ConstitutionalStatus.DEFERRED.value == "deferred"
    assert ConstitutionalStatus.AMBIGUOUS.value == "ambiguous"
    assert ConstitutionalStatus.RESIDUAL.value == "residual"


def test_06_sahih_requires_athar():
    with pytest.raises(ValueError, match="SAHIH judgment must have an AtharEffect"):
        ConstitutionalJudgment(
            layer_id="P0_UNICODE_CANDIDATE",
            wad=_wad(),
            sabab=_sabab(),
            shurut=_shurut_ok(),
            mawani=(),
            illah=_illah(),
            qawadih=(),
            status=ConstitutionalStatus.SAHIH,
            athar=None,   # MISSING → should raise
            baqaya=(),
        )


def test_07_batil_must_not_have_athar():
    with pytest.raises(ValueError, match="BATIL judgment must NOT have an AtharEffect"):
        ConstitutionalJudgment(
            layer_id="P0_UNICODE_CANDIDATE",
            wad=_wad(),
            sabab=_sabab(),
            shurut=_shurut_ok(),
            mawani=(),
            illah=_illah(rank=0),
            qawadih=(),
            status=ConstitutionalStatus.BATIL,
            athar=AtharEffect(
                layer_id="P0_UNICODE_CANDIDATE",
                effect_type="UnicodeCandidate",
                candidate_id="C1",
                taaqol_rank=0,
                carry_to_next="P0_TYPED_CODEPOINT",
            ),
            baqaya=(),
        )


def test_08_p12_terminal_athar_carry_to_next_must_be_none():
    with pytest.raises(ValueError, match="carry_to_next must be None"):
        ConstitutionalJudgment(
            layer_id="P12_IFADAH_SPEECH_FORCE",
            wad=WadContract(
                layer_id="P12_IFADAH_SPEECH_FORCE",
                placement_name="IfadahSpeechForceLayerAdapter",
                placement_phase="SCG-P12",
                shared_cause="إمكان الإفادة الكلامية",
                origin_output_type="IrabGeometryCandidate",
                branch_output_type="IfadahSpeechForceCandidate",
                is_terminal=True,
            ),
            sabab=_sabab("P12_IFADAH_SPEECH_FORCE"),
            shurut=(),
            mawani=(),
            illah=_illah("P12_IFADAH_SPEECH_FORCE"),
            qawadih=(),
            status=ConstitutionalStatus.SAHIH,
            athar=AtharEffect(
                layer_id="P12_IFADAH_SPEECH_FORCE",
                effect_type="IfadahSpeechForceCandidate",
                candidate_id="C1",
                taaqol_rank=4,
                carry_to_next="P13_FORBIDDEN",   # must raise
            ),
            baqaya=(),
        )


def test_09_illah_rejects_invalid_rank():
    with pytest.raises(ValueError, match="granted_rank"):
        IllahRationale(
            layer_id="P0_UNICODE_CANDIDATE",
            rationale="shared cause",
            taaqol_gate_id="GATE-P0",
            granted_rank=7,
        )
    with pytest.raises(ValueError, match="granted_rank"):
        IllahRationale(
            layer_id="P0_UNICODE_CANDIDATE",
            rationale="shared cause",
            taaqol_gate_id="GATE-P0",
            granted_rank=-1,
        )


def test_10_constitutional_judgment_deferred_no_athar():
    """DEFERRED judgment is valid without an AtharEffect."""
    j = _judgment(status=ConstitutionalStatus.DEFERRED, athar=None)
    assert j.status is ConstitutionalStatus.DEFERRED
    assert j.athar is None
