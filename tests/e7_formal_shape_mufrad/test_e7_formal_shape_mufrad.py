"""
E7 Formal Shape + Mufrad Semantic Slot Geometry Tests — T_E7_*

Tests for:
    formal_shape_adapter.py:
        - get_formal_shape_registry() — PR-F2 FormalShapeRegistry (CLOSED)
        - get_formal_closure_state() — FormalShapeClosureState.CLOSED
        - build_formal_style_candidate() — PR-F8 FormalStyleVerdict

    mufrad_semantic_slot_adapter.py:
        - build_contractable_unit_geometry() — PR-18 ContractableUnitVerdict
        - build_mufrad_semantic_slot_geometry() — PR-D1 MufradSemanticSlotGeometryVerdict
        - build_e7_chain_from_e6_verdict() — E6→E7 chain
        - build_e7_from_surface() — E4B+E4C+E5+E6+E7 full chain

Constitutional gates verified:
    G_E7_01: Fail-closed on Python 3.10 (all functions return None)
    G_E7_02: FormalShapeRegistry.closure_state == CLOSED on Python 3.12+
    G_E7_03: FormalStyleCandidate PROVEN for corpus tokens on Python 3.12+
    G_E7_04: ContractableUnitGeometry PROVEN for corpus tokens on Python 3.12+
    G_E7_05: SemanticSlotFrame PROVEN + fields correct on Python 3.12+
    G_E7_06: Identity constraints enforced (wrong instances → None) on Python 3.12+
    G_E7_07: Module invariants pass on Python 3.10+

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
Phase: E7 — FORMAL SHAPE + MUFRAD DALALAH
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.weight_layer.formal_shape_adapter import (  # noqa: E402
    _E6_AVAILABLE,
    _FORMAL_SHAPE_AVAILABLE,
    _VENDOR_SHA as _FSA_VENDOR_SHA,
    build_formal_style_candidate,
    get_formal_closure_state,
    get_formal_shape_registry,
)
from pipeline.taaqol_integration.weight_layer.mufrad_semantic_slot_adapter import (  # noqa: E402
    _E6_AVAILABLE as _MSA_E6_AVAILABLE,
    _FORMAL_SHAPE_ADAPTER_AVAILABLE,
    _MUFRAD_SLOT_AVAILABLE,
    _VENDOR_SHA as _MSA_VENDOR_SHA,
    build_contractable_unit_geometry,
    build_e7_chain_from_e6_verdict,
    build_e7_from_surface,
    build_mufrad_semantic_slot_geometry,
)

REQUIRES_312 = pytest.mark.skipif(
    not _MUFRAD_SLOT_AVAILABLE,
    reason="Requires Python 3.12+ (vendor StrEnum / taaqqul_slot_geometry)",
)

_CORPUS_ISM = [
    ("دَيْنٍ",        "دين"),
    ("كَاتِبٌ",      "كتب"),
    ("شَهِيدَيْنِ",  "شهد"),
    ("أَجَلٍ",       "أجل"),
]


# ── G_E7_01: Fail-closed on Python 3.10 ──────────────────────────────────────


class TestT_E7_01_FailClosed:
    """G_E7_01: All E7 functions return None on Python 3.10 (vendor absent)."""

    def test_get_formal_shape_registry_returns_none_on_310(self):
        """get_formal_shape_registry returns None without vendor."""
        if _FORMAL_SHAPE_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = get_formal_shape_registry()
        assert result is None

    def test_get_formal_closure_state_returns_none_on_310(self):
        """get_formal_closure_state returns None without vendor."""
        if _FORMAL_SHAPE_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = get_formal_closure_state()
        assert result is None

    def test_build_formal_style_candidate_returns_none_on_310(self):
        """build_formal_style_candidate returns None without vendor."""
        if _FORMAL_SHAPE_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_formal_style_candidate(
            style_family_name="DECLARATIVE_STYLE_FORM",
            composition_evidence_ref="test:e7:t01:comp",
            formal_closure_ref="test:e7:t01:closure",
        )
        assert result is None

    def test_build_contractable_unit_geometry_returns_none_on_310(self):
        """build_contractable_unit_geometry returns None without vendor."""
        if _MUFRAD_SLOT_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_contractable_unit_geometry(
            dal_madlul_binding_verdict=object(),
            word_class="ISM",
        )
        assert result is None

    def test_build_mufrad_semantic_slot_geometry_returns_none_on_310(self):
        """build_mufrad_semantic_slot_geometry returns None without vendor."""
        if _MUFRAD_SLOT_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_mufrad_semantic_slot_geometry(
            e6_binding_verdict=object(),
            formal_style_verdict=object(),
            token_surface="دَيْنٍ",
        )
        assert result is None

    def test_build_e7_chain_from_e6_verdict_returns_none_on_310(self):
        """build_e7_chain_from_e6_verdict returns None without vendor."""
        if _MUFRAD_SLOT_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_e7_chain_from_e6_verdict(
            e6_binding_verdict=object(),
            token_surface="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e7:t01:chain",
        )
        assert result is None

    def test_build_e7_from_surface_returns_none_on_310(self):
        """build_e7_from_surface returns None without vendor."""
        if _MUFRAD_SLOT_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_e7_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e7:t01:surface",
        )
        assert result is None

    def test_never_raises_on_310(self):
        """E7 functions never raise on Python 3.10."""
        if _MUFRAD_SLOT_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        for fn, args in [
            (get_formal_shape_registry, ()),
            (get_formal_closure_state, ()),
            (build_formal_style_candidate, ("DECLARATIVE_STYLE_FORM", "ref", "ref")),
            (build_contractable_unit_geometry, (None, "ISM")),
            (build_mufrad_semantic_slot_geometry, (None, None, "")),
            (build_e7_chain_from_e6_verdict, (None, "", "ISM", "")),
            (build_e7_from_surface, ("", "", "", "", "")),
        ]:
            try:
                result = fn(*args)
                assert result is None
            except Exception as exc:
                pytest.fail(f"{fn.__name__} raised on 3.10: {exc}")

    def test_mufrad_slot_available_false_on_310(self):
        """_MUFRAD_SLOT_AVAILABLE = False on Python 3.10."""
        if _MUFRAD_SLOT_AVAILABLE:
            pytest.skip("Python 3.12+")
        assert _MUFRAD_SLOT_AVAILABLE is False

    def test_formal_shape_available_false_on_310(self):
        """_FORMAL_SHAPE_AVAILABLE = False on Python 3.10."""
        if _FORMAL_SHAPE_AVAILABLE:
            pytest.skip("Python 3.12+")
        assert _FORMAL_SHAPE_AVAILABLE is False

    def test_e6_available_true(self):
        """_E6_AVAILABLE = True (verbal_madlul_adapter importable on 3.10)."""
        assert _E6_AVAILABLE is True
        assert _MSA_E6_AVAILABLE is True

    def test_formal_shape_adapter_available_true(self):
        """_FORMAL_SHAPE_ADAPTER_AVAILABLE = True (formal_shape_adapter importable)."""
        assert _FORMAL_SHAPE_ADAPTER_AVAILABLE is True


# ── G_E7_02: FormalShapeRegistry.CLOSED on Python 3.12+ ─────────────────────


class TestT_E7_02_FormalShapeRegistryOn312:
    """G_E7_02: FormalShapeRegistry is CLOSED on Python 3.12+."""

    @REQUIRES_312
    def test_registry_not_none(self):
        """get_formal_shape_registry() returns non-None on 3.12+."""
        registry = get_formal_shape_registry()
        assert registry is not None, "FormalShapeRegistry is None on 3.12+"

    @REQUIRES_312
    def test_registry_closure_state_closed(self):
        """FormalShapeRegistry.closure_state == CLOSED."""
        registry = get_formal_shape_registry()
        assert registry is not None
        closure_state_str = str(registry.closure_state)
        assert "CLOSED" in closure_state_str, (
            f"Expected CLOSED, got closure_state={closure_state_str!r}"
        )

    @REQUIRES_312
    def test_formal_closure_state_not_none(self):
        """get_formal_closure_state() returns non-None on 3.12+."""
        state = get_formal_closure_state()
        assert state is not None

    @REQUIRES_312
    def test_formal_closure_state_is_closed(self):
        """get_formal_closure_state() is FormalShapeClosureState.CLOSED."""
        state = get_formal_closure_state()
        assert state is not None
        assert "CLOSED" in str(state), f"Expected CLOSED, got {state!r}"

    @REQUIRES_312
    def test_registry_singleton_cached(self):
        """Registry singleton is reused (same object on second call)."""
        registry1 = get_formal_shape_registry()
        registry2 = get_formal_shape_registry()
        assert registry1 is registry2, "Registry singleton must be same object on repeat calls"


# ── G_E7_03: FormalStyleCandidate PROVEN on Python 3.12+ ─────────────────────


class TestT_E7_03_FormalStyleCandidateOn312:
    """G_E7_03: build_formal_style_candidate produces PROVEN FormalStyleVerdict on 3.12+."""

    @REQUIRES_312
    def test_declarative_style_proven(self):
        """DECLARATIVE_STYLE_FORM produces PROVEN FormalStyleVerdict."""
        result = build_formal_style_candidate(
            style_family_name="DECLARATIVE_STYLE_FORM",
            composition_evidence_ref="test:e7:t03:comp",
            formal_closure_ref="test:e7:t03:closure",
        )
        assert result is not None, "Expected FormalStyleVerdict, got None"
        assert "PROVEN" in str(result.verdict_state), (
            f"Expected PROVEN, got {result.verdict_state!r}"
        )

    @REQUIRES_312
    def test_proven_verdict_has_candidate(self):
        """PROVEN FormalStyleVerdict carries a FormalStyleCandidate."""
        result = build_formal_style_candidate(
            style_family_name="DECLARATIVE_STYLE_FORM",
            composition_evidence_ref="test:e7:t03:cand",
            formal_closure_ref="test:e7:t03:cand_closure",
        )
        assert result is not None
        assert result.candidate is not None, "PROVEN verdict must carry a FormalStyleCandidate"
        assert type(result.candidate).__name__ == "FormalStyleCandidate", (
            f"Expected FormalStyleCandidate, got {type(result.candidate).__name__}"
        )

    @REQUIRES_312
    def test_formal_closure_ref_preserved(self):
        """FormalStyleCandidate.formal_closure_ref == the ref passed in."""
        closure_ref = "test:e7:t03:closure_ref_check"
        result = build_formal_style_candidate(
            style_family_name="DECLARATIVE_STYLE_FORM",
            composition_evidence_ref="test:e7:t03:comp2",
            formal_closure_ref=closure_ref,
        )
        assert result is not None
        assert result.candidate.formal_closure_ref == closure_ref, (
            f"formal_closure_ref mismatch: {result.candidate.formal_closure_ref!r}"
        )

    @REQUIRES_312
    def test_empty_style_family_returns_none(self):
        """Empty style_family_name → None (fail-closed)."""
        result = build_formal_style_candidate(
            style_family_name="",
            composition_evidence_ref="test:e7:t03:comp",
            formal_closure_ref="test:e7:t03:closure",
        )
        assert result is None

    @REQUIRES_312
    def test_empty_composition_evidence_returns_none(self):
        """Empty composition_evidence_ref → None (fail-closed)."""
        result = build_formal_style_candidate(
            style_family_name="DECLARATIVE_STYLE_FORM",
            composition_evidence_ref="",
            formal_closure_ref="test:e7:t03:closure",
        )
        assert result is None

    @REQUIRES_312
    def test_empty_formal_closure_ref_returns_none(self):
        """Empty formal_closure_ref → None (fail-closed)."""
        result = build_formal_style_candidate(
            style_family_name="DECLARATIVE_STYLE_FORM",
            composition_evidence_ref="test:e7:t03:comp",
            formal_closure_ref="",
        )
        assert result is None


# ── G_E7_04: ContractableUnitGeometry PROVEN on Python 3.12+ ─────────────────


class TestT_E7_04_ContractableUnitOn312:
    """G_E7_04: build_contractable_unit_geometry produces PROVEN verdict on 3.12+."""

    @REQUIRES_312
    def test_dayn_contractable_unit_proven(self):
        """دَيْنٍ: ContractableUnitGeometry PROVEN via full E4B+E4C+E5+E6+PR-18 chain."""
        from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (
            build_e6_from_surface,
        )
        e6_verdict = build_e6_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e7:t04:dayn",
        )
        assert e6_verdict is not None, "E6 chain failed for دَيْنٍ"
        result = build_contractable_unit_geometry(
            dal_madlul_binding_verdict=e6_verdict,
            word_class="ISM",
        )
        assert result is not None, "ContractableUnitGeometry is None for دَيْنٍ"
        assert "PROVEN" in str(result.verdict_state), (
            f"Expected PROVEN, got {result.verdict_state!r}"
        )

    @REQUIRES_312
    def test_contractable_unit_has_candidate(self):
        """PROVEN ContractableUnitVerdict carries ContractableUnitGeometry."""
        from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (
            build_e6_from_surface,
        )
        e6_verdict = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e7:t04:cand",
        )
        assert e6_verdict is not None
        result = build_contractable_unit_geometry(e6_verdict, "ISM")
        assert result is not None
        assert result.candidate is not None, "Must carry ContractableUnitGeometry"
        assert type(result.candidate).__name__ == "ContractableUnitGeometry", (
            f"Expected ContractableUnitGeometry, got {type(result.candidate).__name__}"
        )

    @REQUIRES_312
    def test_none_verdict_returns_none(self):
        """None dal_madlul_binding_verdict → None (fail-closed)."""
        result = build_contractable_unit_geometry(None, "ISM")
        assert result is None

    @REQUIRES_312
    def test_unit_identity_is_token_surface(self):
        """ContractableUnitGeometry.unit_identity == token_surface (signifier_identity)."""
        from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (
            build_e6_from_surface,
        )
        token = "دَيْنٍ"
        e6_verdict = build_e6_from_surface(
            token_surface=token, root_letters="دين",
            segment_host=token, word_class="ISM",
            trace_id="test:e7:t04:identity",
        )
        assert e6_verdict is not None
        result = build_contractable_unit_geometry(e6_verdict, "ISM")
        assert result is not None
        assert result.candidate.unit_identity == token, (
            f"unit_identity={result.candidate.unit_identity!r} != {token!r}"
        )


# ── G_E7_05: SemanticSlotFrame PROVEN on Python 3.12+ ────────────────────────


class TestT_E7_05_SemanticSlotFrameOn312:
    """G_E7_05: build_e7_from_surface produces PROVEN SemanticSlotFrame on 3.12+."""

    @REQUIRES_312
    def test_dayn_produces_proven_semantic_slot(self):
        """دَيْنٍ: full E4B+E4C+E5+E6+E7 chain produces PROVEN SemanticSlotFrame."""
        result = build_e7_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e7:t05:dayn",
        )
        assert result is not None, "E7 chain failed for دَيْنٍ — unexpected None"
        assert "PROVEN" in str(result.verdict_state), (
            f"Expected PROVEN, got {result.verdict_state!r}"
        )

    @REQUIRES_312
    def test_proven_verdict_has_semantic_slot_frame(self):
        """PROVEN MufradSemanticSlotGeometryVerdict carries SemanticSlotFrame."""
        result = build_e7_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e7:t05:frame",
        )
        assert result is not None
        assert result.candidate is not None, "PROVEN verdict must carry SemanticSlotFrame"
        assert type(result.candidate).__name__ == "SemanticSlotFrame", (
            f"Expected SemanticSlotFrame, got {type(result.candidate).__name__}"
        )

    @REQUIRES_312
    @pytest.mark.parametrize("token,root", _CORPUS_ISM)
    def test_corpus_ism_all_proven(self, token, root):
        """All corpus ISM tokens produce PROVEN SemanticSlotFrame via full chain."""
        result = build_e7_from_surface(
            token_surface=token,
            root_letters=root,
            segment_host=token,
            word_class="ISM",
            trace_id=f"test:e7:t05:corpus:{token}",
        )
        assert result is not None, f"E7 chain failed for {token!r}"
        assert "PROVEN" in str(result.verdict_state), (
            f"Token {token!r}: expected PROVEN, got {result.verdict_state!r}"
        )

    @REQUIRES_312
    def test_semantic_slot_frame_dal_identity_ref_set(self):
        """SemanticSlotFrame.dal_identity_ref is non-empty (proves E5 identity continuity)."""
        result = build_e7_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e7:t05:dal_ref",
        )
        assert result is not None
        frame = result.candidate
        assert isinstance(frame.dal_identity_ref, str)
        assert frame.dal_identity_ref.strip(), "dal_identity_ref must be non-empty"

    @REQUIRES_312
    def test_semantic_slot_frame_residuals_non_empty(self):
        """SemanticSlotFrame.residuals carries the 16 constitutional deferred residuals."""
        result = build_e7_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e7:t05:residuals",
        )
        assert result is not None
        frame = result.candidate
        assert isinstance(frame.residuals, tuple)
        assert len(frame.residuals) > 0, "SemanticSlotFrame must carry deferred residuals"

    @REQUIRES_312
    def test_harf_returns_none(self):
        """HARF tokens return None from build_e7_from_surface (E4A guard upstream)."""
        result = build_e7_from_surface(
            token_surface="إِلَى",
            root_letters="",
            segment_host="إِلَى",
            word_class="HARF",
            trace_id="test:e7:t05:harf",
        )
        assert result is None, f"Expected None for HARF, got {result!r}"

    @REQUIRES_312
    def test_empty_token_returns_none(self):
        """Empty token_surface → None (fail-closed)."""
        result = build_e7_from_surface(
            token_surface="",
            root_letters="دين",
            segment_host="",
            word_class="ISM",
            trace_id="test:e7:t05:empty",
        )
        assert result is None


# ── G_E7_06: Identity constraints enforced on Python 3.12+ ───────────────────


class TestT_E7_06_IdentityConstraintsOn312:
    """G_E7_06: Identity constraints enforced — wrong instances → None on 3.12+."""

    @REQUIRES_312
    def test_wrong_formal_style_type_returns_none(self):
        """Non-FormalStyleVerdict as formal_style_verdict → None (fail-closed)."""
        from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (
            build_e6_from_surface,
        )
        e6_verdict = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e7:t06:wrong_style",
        )
        assert e6_verdict is not None
        # Pass a plain object as formal_style_verdict — vendor will reject non-FormalStyleCandidate
        result = build_mufrad_semantic_slot_geometry(
            e6_binding_verdict=e6_verdict,
            formal_style_verdict=object(),  # wrong type — candidate will be None or wrong type
            token_surface="دَيْنٍ",
        )
        # result is None either from None candidate or REFUSED verdict
        assert result is None

    @REQUIRES_312
    def test_none_e6_verdict_returns_none(self):
        """None e6_binding_verdict → None (fail-closed)."""
        from pipeline.taaqol_integration.weight_layer.formal_shape_adapter import (
            build_formal_style_candidate,
        )
        formal_style = build_formal_style_candidate(
            style_family_name="DECLARATIVE_STYLE_FORM",
            composition_evidence_ref="test:e7:t06:comp",
            formal_closure_ref="test:e7:t06:closure",
        )
        assert formal_style is not None
        result = build_mufrad_semantic_slot_geometry(
            e6_binding_verdict=None,
            formal_style_verdict=formal_style,
            token_surface="دَيْنٍ",
        )
        assert result is None

    @REQUIRES_312
    def test_empty_token_surface_returns_none(self):
        """Empty token_surface → None in build_mufrad_semantic_slot_geometry."""
        from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (
            build_e6_from_surface,
        )
        from pipeline.taaqol_integration.weight_layer.formal_shape_adapter import (
            build_formal_style_candidate,
        )
        e6_verdict = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e7:t06:empty_surface",
        )
        assert e6_verdict is not None
        formal_style = build_formal_style_candidate(
            style_family_name="DECLARATIVE_STYLE_FORM",
            composition_evidence_ref="test:e7:t06:comp2",
            formal_closure_ref="test:e7:t06:closure2",
        )
        assert formal_style is not None
        result = build_mufrad_semantic_slot_geometry(
            e6_binding_verdict=e6_verdict,
            formal_style_verdict=formal_style,
            token_surface="",  # empty — guard fails
        )
        assert result is None

    @REQUIRES_312
    def test_chain_from_verdict_empty_trace_returns_none(self):
        """build_e7_chain_from_e6_verdict with empty trace_id → None."""
        from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (
            build_e6_from_surface,
        )
        e6_verdict = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e7:t06:trace_guard",
        )
        assert e6_verdict is not None
        result = build_e7_chain_from_e6_verdict(
            e6_binding_verdict=e6_verdict,
            token_surface="دَيْنٍ",
            word_class="ISM",
            trace_id="",  # empty — guard fails
        )
        assert result is None


# ── G_E7_07: Module invariants ────────────────────────────────────────────────


class TestT_E7_07_ModuleInvariants:
    """G_E7_07: Module invariants hold at import time on Python 3.10+."""

    def test_formal_shape_adapter_imports_without_error(self):
        """formal_shape_adapter imports cleanly (invariants run at import time)."""
        assert True  # import at top of module — would have raised if broken

    def test_mufrad_slot_adapter_imports_without_error(self):
        """mufrad_semantic_slot_adapter imports cleanly."""
        assert True

    def test_vendor_sha_constants_match(self):
        """Both adapters: _VENDOR_SHA == pinned constitutional SHA."""
        sha = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"
        assert _FSA_VENDOR_SHA == sha, f"formal_shape_adapter SHA mismatch: {_FSA_VENDOR_SHA!r}"
        assert _MSA_VENDOR_SHA == sha, f"mufrad_slot_adapter SHA mismatch: {_MSA_VENDOR_SHA!r}"

    def test_availability_flags_are_bool(self):
        """All availability flags are bool."""
        assert isinstance(_FORMAL_SHAPE_AVAILABLE, bool)
        assert isinstance(_MUFRAD_SLOT_AVAILABLE, bool)
        assert isinstance(_E6_AVAILABLE, bool)
        assert isinstance(_MSA_E6_AVAILABLE, bool)
        assert isinstance(_FORMAL_SHAPE_ADAPTER_AVAILABLE, bool)

    def test_all_functions_callable(self):
        """All public E7 functions are callable."""
        for fn in [
            get_formal_shape_registry,
            get_formal_closure_state,
            build_formal_style_candidate,
            build_contractable_unit_geometry,
            build_mufrad_semantic_slot_geometry,
            build_e7_chain_from_e6_verdict,
            build_e7_from_surface,
        ]:
            assert callable(fn), f"{fn.__name__} is not callable"

    def test_e6_available_true_on_310(self):
        """_E6_AVAILABLE = True (verbal_madlul_adapter importable on 3.10)."""
        assert _E6_AVAILABLE is True

    def test_formal_shape_adapter_available_true(self):
        """_FORMAL_SHAPE_ADAPTER_AVAILABLE = True (formal_shape_adapter importable)."""
        assert _FORMAL_SHAPE_ADAPTER_AVAILABLE is True
