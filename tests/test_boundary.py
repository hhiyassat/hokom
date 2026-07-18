"""
tests/test_boundary.py — PR 3.7-pre: Internal Boundary Layer

Mandatory test cases from the PR 3.7-pre specification.

Test classes:
  TestClosedFunctionWords           — inventory CLOSED_FUNCTION_WORD path
  TestPossibleFunctionWords         — inventory POSSIBLE_FUNCTION_WORD path
  TestCompressedVerbCandidates      — structural C+sukun compressed-verb path
  TestAmbiguousPrefixForms          — structural muḍāriʿ-prefix ambiguity path
  TestRootEligibleSurfaces          — structural ROOT_ELIGIBLE path
  TestUnderlicensedShortSurfaces    — structural too-short path
  TestDirectiveAndStageState        — OPEN/BLOCK and OPENED/NOT_OPENED invariants
  TestInventoryLookupPreemption     — inventory beats structural for لَمْ/لَنْ overlap
  TestEvidenceProvenance            — evidence source fields
  TestToDict                        — serialization
  TestBoundaryDoesNotModifySource   — surface vs normalized fields
"""

import pytest

from boundary import (
    BoundaryKind,
    RootEligibilityDecision,
    RootPathDirective,
    StageState,
    assess_boundary,
)
from boundary.models import OPEN_KINDS


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _kind(surface: str) -> BoundaryKind:
    return assess_boundary(surface).kind

def _directive(surface: str) -> RootPathDirective:
    return assess_boundary(surface).directive

def _state(surface: str) -> StageState:
    return assess_boundary(surface).stage_state


# ══════════════════════════════════════════════════════════════════════════════
# 1.  Closed function words (inventory path)
# ══════════════════════════════════════════════════════════════════════════════

class TestClosedFunctionWords:
    """Inventory-confirmed particles/prepositions/pronouns → CLOSED_FUNCTION_WORD."""

    @pytest.mark.parametrize("surface", [
        "مِنْ",   # حرف جر
        "هَلْ",   # حرف استفهام
        "لَمْ",   # حرف نفي جازم
        "لَنْ",   # حرف نفي ونصب
        "فِي",    # حرف جر
        "هُوَ",   # ضمير منفصل مذكر
        "هِيَ",   # ضمير منفصل مؤنث
    ])
    def test_kind_is_closed(self, surface):
        assert _kind(surface) == BoundaryKind.CLOSED_FUNCTION_WORD

    @pytest.mark.parametrize("surface", [
        "مِنْ", "هَلْ", "لَمْ", "لَنْ", "فِي", "هُوَ", "هِيَ",
    ])
    def test_directive_is_block(self, surface):
        assert _directive(surface) == RootPathDirective.BLOCK

    @pytest.mark.parametrize("surface", [
        "مِنْ", "هَلْ", "لَمْ", "لَنْ", "فِي", "هُوَ", "هِيَ",
    ])
    def test_stage_state_is_not_opened(self, surface):
        assert _state(surface) == StageState.NOT_OPENED


# ══════════════════════════════════════════════════════════════════════════════
# 2.  Possible function words (inventory path)
# ══════════════════════════════════════════════════════════════════════════════

class TestPossibleFunctionWords:
    """Historically debated particles → POSSIBLE_FUNCTION_WORD.

    PR 3.7-fix: POSSIBLE_FUNCTION_WORD → directive=DEFER (not BLOCK).
    These words are not inventory-confirmed root-ineligible; their root status
    is historically debated. The path is acknowledged (not blocked) but form
    detection is deferred pending paradigm context.
    """

    @pytest.mark.parametrize("surface", [
        "عَلَى",  # preposition, root debated
        "إِلَى",  # preposition, root debated
        "مَتَى",  # interrogative, root debated
    ])
    def test_kind_is_possible(self, surface):
        assert _kind(surface) == BoundaryKind.POSSIBLE_FUNCTION_WORD

    @pytest.mark.parametrize("surface", ["عَلَى", "إِلَى", "مَتَى"])
    def test_directive_is_defer(self, surface):
        """POSSIBLE_FUNCTION_WORD → DEFER (not BLOCK): not inventory-confirmed closed."""
        assert _directive(surface) == RootPathDirective.DEFER

    @pytest.mark.parametrize("surface", ["عَلَى", "إِلَى", "مَتَى"])
    def test_stage_state_is_deferred(self, surface):
        assert _state(surface) == StageState.DEFERRED

    def test_ila_hamza_normalization(self):
        """إِلَى is inventory-keyed under its post-normalize_hamza form ءِلَى."""
        d = assess_boundary("إِلَى")
        assert d.kind == BoundaryKind.POSSIBLE_FUNCTION_WORD
        # normalized form has ء not إ
        assert d.normalized != d.surface


# ══════════════════════════════════════════════════════════════════════════════
# 3.  Compressed verb candidates (structural path)
# ══════════════════════════════════════════════════════════════════════════════

class TestCompressedVerbCandidates:
    """Two-phone C(mutaharrik)+C(sakin) not in inventory → COMPRESSED_VERB_CANDIDATE."""

    @pytest.mark.parametrize("surface", [
        "قُلْ",   # قول — امر مضغوط
        "قِفْ",   # وقف — امر مضغوط
        "عِدْ",   # وعد — امر مضغوط
        "زِنْ",   # وزن — امر مضغوط
    ])
    def test_kind_is_compressed(self, surface):
        assert _kind(surface) == BoundaryKind.COMPRESSED_VERB_CANDIDATE

    @pytest.mark.parametrize("surface", ["قُلْ", "قِفْ", "عِدْ", "زِنْ"])
    def test_directive_is_open(self, surface):
        """Compressed verbs open the root path."""
        assert _directive(surface) == RootPathDirective.OPEN

    @pytest.mark.parametrize("surface", ["قُلْ", "قِفْ", "عِدْ", "زِنْ"])
    def test_stage_state_is_opened(self, surface):
        assert _state(surface) == StageState.OPENED

    def test_compressed_evidence_source(self):
        d = assess_boundary("قُلْ")
        sources = [e.source for e in d.evidence]
        assert "structural:compressed_verb" in sources


# ══════════════════════════════════════════════════════════════════════════════
# 4.  Ambiguous prefix forms (structural path)
# ══════════════════════════════════════════════════════════════════════════════

class TestAmbiguousPrefixForms:
    """3-phone surfaces with muḍāriʿ-prefix shape + final VL → AMBIGUOUS.

    PR 3.7-fix: AMBIGUOUS → directive=DEFER (not BLOCK).
    Rule: التباس البادئة لا يمنع مسار الجذر — يؤجل الحكم فقط.
    BLOCK requires inventory-confirmed closure; structural ambiguity alone
    does not constitute a structural impossibility, so DEFER is correct.
    """

    @pytest.mark.parametrize("surface", [
        "تَقِي",   # تقي — يَقِي من وَقَى: ambiguous
        "يَقِي",   # يقي — ambiguous
    ])
    def test_kind_is_ambiguous(self, surface):
        assert _kind(surface) == BoundaryKind.AMBIGUOUS

    @pytest.mark.parametrize("surface", ["تَقِي", "يَقِي"])
    def test_directive_is_defer(self, surface):
        """AMBIGUOUS → DEFER: path acknowledged, judgment deferred — NOT BLOCK."""
        assert _directive(surface) == RootPathDirective.DEFER

    @pytest.mark.parametrize("surface", ["تَقِي", "يَقِي"])
    def test_stage_state_is_deferred(self, surface):
        """AMBIGUOUS → stage_state=DEFERRED (not NOT_OPENED)."""
        assert _state(surface) == StageState.DEFERRED

    def test_ambiguous_evidence_source(self):
        d = assess_boundary("تَقِي")
        sources = [e.source for e in d.evidence]
        assert "structural:prefix_ambiguity" in sources

    def test_wa_not_mudaric_prefix(self):
        """وَقَى: phone[0]='و' is NOT in the muḍāriʿ prefix set → not AMBIGUOUS."""
        assert _kind("وَقَى") == BoundaryKind.ROOT_ELIGIBLE

    def test_longer_defective_present_not_ambiguous(self):
        """يَدْعُو has 4 phones (len≠3) → not AMBIGUOUS even though phone[0]='ي'."""
        assert _kind("يَدْعُو") == BoundaryKind.ROOT_ELIGIBLE


# ══════════════════════════════════════════════════════════════════════════════
# 5.  Root-eligible surfaces (structural path)
# ══════════════════════════════════════════════════════════════════════════════

class TestRootEligibleSurfaces:
    """Surfaces that pass all structural checks → ROOT_ELIGIBLE."""

    @pytest.mark.parametrize("surface", [
        "ضَرَبَ",    # فَعَلَ — صحيح سالم
        "قَالَ",     # أجوف — hollow past
        "دَعَا",     # ناقص — defective past
        "وَقَى",     # لفيف مفروق
        "قَرَأَ",    # همزة في اللام
        "مَدَّ",     # مضاعف — doubled (shadda expands to 3 phones)
        "يَدْعُو",   # مضارع ناقص — 4 phones
        "فَعَلَ",    # canonical trilateral template
    ])
    def test_kind_is_root_eligible(self, surface):
        assert _kind(surface) == BoundaryKind.ROOT_ELIGIBLE

    @pytest.mark.parametrize("surface", [
        "ضَرَبَ", "قَالَ", "دَعَا", "وَقَى", "قَرَأَ", "مَدَّ", "يَدْعُو",
    ])
    def test_directive_is_open(self, surface):
        assert _directive(surface) == RootPathDirective.OPEN

    @pytest.mark.parametrize("surface", [
        "ضَرَبَ", "قَالَ", "دَعَا", "وَقَى", "قَرَأَ", "مَدَّ", "يَدْعُو",
    ])
    def test_stage_state_is_opened(self, surface):
        assert _state(surface) == StageState.OPENED

    def test_madd_shadda_expands_to_three_phones(self):
        """مَدَّ: shadda on دّ expands to دْ+د → 3 phones → ROOT_ELIGIBLE, not UNDERLICENSED."""
        d = assess_boundary("مَدَّ")
        assert d.kind == BoundaryKind.ROOT_ELIGIBLE
        assert d.directive == RootPathDirective.OPEN

    def test_root_eligible_evidence_source(self):
        d = assess_boundary("ضَرَبَ")
        sources = [e.source for e in d.evidence]
        assert "structural:root_eligible_structure" in sources


# ══════════════════════════════════════════════════════════════════════════════
# 6.  Underlicensed short surfaces (structural path)
# ══════════════════════════════════════════════════════════════════════════════

class TestUnderlicensedShortSurfaces:
    """Two-phone surfaces not in inventory and not C+sukun → UNDERLICENSED_SHORT_SURFACE."""

    def test_two_phone_mutaharrik_mutaharrik(self):
        """هِيَ is in inventory; a hypothetical 2-phone C+C(mutaharrik) not in inventory."""
        # بَا is 2 phones: ب(M)+ا(VL). VL is not sakin in the bool sense but is_sakin()→True
        # actually ا is vowel-letter so is_sakin()=False AND is_mutaharrik()=False
        # That means phone[1] is neither — is_sakin() returns False for VL
        # So _is_compressed_verb_candidate would return False (phone[1].is_sakin()=False)
        # → UNDERLICENSED_SHORT_SURFACE
        # We use a test word that is 2 phones but VL final (not sukun)
        # ثُوَ (hypothetical) — 2 phones, not in inventory
        # For a real case: use a bare particle not in inventory
        # Actually let's just verify the structural path with a synthetic case
        from boundary.eligibility import classify_by_structure
        from syllabifier import Phone
        # Simulate: 2 phones, both mutaharrik (no sukun on second)
        p1 = Phone('ب', ['َ'])
        p2 = Phone('ا', [])   # ا with no diacritics → is VL → is_sakin()=False
        result = classify_by_structure([p1, p2])
        assert result == BoundaryKind.UNDERLICENSED_SHORT_SURFACE

    def test_single_phone_underlicensed(self):
        """A single-phone surface is UNDERLICENSED."""
        from boundary.eligibility import classify_by_structure
        from syllabifier import Phone
        p = Phone('ب', ['ِ'])
        result = classify_by_structure([p])
        assert result == BoundaryKind.UNDERLICENSED_SHORT_SURFACE


# ══════════════════════════════════════════════════════════════════════════════
# 7.  Directive and stage_state invariants
# ══════════════════════════════════════════════════════════════════════════════

class TestDirectiveAndStageState:
    """Three-way directive: OPEN ↔ OPENED, DEFER ↔ DEFERRED, BLOCK ↔ NOT_OPENED.

    PR 3.7-fix: AMBIGUOUS and POSSIBLE_FUNCTION_WORD now map to DEFER (not BLOCK).
    Rule: BLOCK only for inventory-confirmed closed words and structural impossibilities.
    """

    OPEN_SURFACES = [
        "ضَرَبَ", "قَالَ", "دَعَا", "مَدَّ",  # ROOT_ELIGIBLE
        "قُلْ", "قِفْ",                          # COMPRESSED_VERB_CANDIDATE
    ]
    DEFER_SURFACES = [
        "عَلَى", "إِلَى", "مَتَى",   # POSSIBLE_FUNCTION_WORD — debated, not closed
        "تَقِي", "يَقِي",             # AMBIGUOUS — structurally ambiguous, not impossible
    ]
    BLOCK_SURFACES = [
        "مِنْ", "هَلْ", "فِي",        # CLOSED_FUNCTION_WORD — inventory-confirmed
        "لَمْ", "لَنْ",               # CLOSED_FUNCTION_WORD
    ]
    # UNDERLICENSED_SHORT_SURFACE → DEFER (لا BLOCK)
    # العجز هنا بنيوي من أثر التجزئة أو قصر السطح، ليس منعًا معجميًا مُثبَتًا.
    # BLOCK يُعني "ثبت أن المسار مستحيل"؛ DEFER يُعني "البنية غير مكتملة بعد".
    UNDERLICENSED_SURFACES = [
        "حْدَ",   # مضيف متبقٍّ بعد تجزئة حْدَهُمْ — يبدأ بساكن (orphan C)
    ]

    @pytest.mark.parametrize("surface", OPEN_SURFACES)
    def test_open_kinds_give_open_directive(self, surface):
        d = assess_boundary(surface)
        assert d.kind in OPEN_KINDS
        assert d.directive == RootPathDirective.OPEN
        assert d.stage_state == StageState.OPENED

    @pytest.mark.parametrize("surface", DEFER_SURFACES)
    def test_defer_kinds_give_defer_directive(self, surface):
        """AMBIGUOUS and POSSIBLE_FUNCTION_WORD → DEFER (not BLOCK)."""
        from boundary.models import DEFER_KINDS
        d = assess_boundary(surface)
        assert d.kind in DEFER_KINDS
        assert d.directive == RootPathDirective.DEFER
        assert d.stage_state == StageState.DEFERRED

    @pytest.mark.parametrize("surface", BLOCK_SURFACES)
    def test_block_kinds_give_block_directive(self, surface):
        """Only inventory-confirmed CLOSED_FUNCTION_WORD surfaces receive BLOCK."""
        from boundary.models import BLOCK_KINDS
        d = assess_boundary(surface)
        assert d.kind in BLOCK_KINDS
        assert d.directive == RootPathDirective.BLOCK
        assert d.stage_state == StageState.NOT_OPENED

    @pytest.mark.parametrize("surface", ["حْدَ"])
    def test_underlicensed_gives_defer_not_block(self, surface):
        """UNDERLICENSED_SHORT_SURFACE → directive=DEFER (لا BLOCK)

        الحجة: العجز البنيوي في `حْدَ` (يبدأ بساكن) ناتج عن أثر التجزئة —
        لم يثبت منع معجمي. الفرق الدلالي:
          BLOCK  = "ثبت مستحيل" (مخزون مغلق: مِنْ، هَلْ، ...)
          DEFER  = "البنية غير مكتملة" (قد تُحل عند السياق الكامل)
        UNDERLICENSED_SHORT_SURFACE هو عجز بنيوي لا منع معجمي → DEFER.
        """
        from boundary.models import DEFER_KINDS
        d = assess_boundary(surface)
        assert d.kind == BoundaryKind.UNDERLICENSED_SHORT_SURFACE
        assert d.kind in DEFER_KINDS, (
            f"UNDERLICENSED_SHORT_SURFACE يجب أن يكون في DEFER_KINDS، لكنه في BLOCK_KINDS"
        )
        assert d.directive == RootPathDirective.DEFER, (
            f"directive={d.directive.value} (expected DEFER)"
        )
        assert d.stage_state == StageState.DEFERRED

    def test_directive_stage_consistency_all_samples(self):
        """For every surface tested, directive and stage_state must be internally consistent."""
        from boundary.models import DEFER_KINDS
        all_surfaces = self.OPEN_SURFACES + self.DEFER_SURFACES + self.BLOCK_SURFACES
        for surface in all_surfaces:
            d = assess_boundary(surface)
            if d.directive == RootPathDirective.OPEN:
                assert d.stage_state == StageState.OPENED, f"Inconsistent for {surface}"
            elif d.directive == RootPathDirective.DEFER:
                assert d.stage_state == StageState.DEFERRED, f"Inconsistent for {surface}"
            else:
                assert d.stage_state == StageState.NOT_OPENED, f"Inconsistent for {surface}"


# ══════════════════════════════════════════════════════════════════════════════
# 8.  Inventory lookup preempts structural rules
# ══════════════════════════════════════════════════════════════════════════════

class TestInventoryLookupPreemption:
    """Surfaces that would match structural rules but are in the inventory as
    function words must be resolved by inventory, not by structural rules."""

    def test_lam_preempts_compressed_candidate(self):
        """لَمْ matches C+sukun structurally (like قُلْ) but inventory wins → CLOSED_FUNCTION_WORD."""
        assert _kind("لَمْ") == BoundaryKind.CLOSED_FUNCTION_WORD

    def test_lan_preempts_compressed_candidate(self):
        """لَنْ same pattern."""
        assert _kind("لَنْ") == BoundaryKind.CLOSED_FUNCTION_WORD

    def test_mata_preempts_root_eligible(self):
        """مَتَى is 3 phones (structural path would give ROOT_ELIGIBLE) but inventory gives POSSIBLE."""
        assert _kind("مَتَى") == BoundaryKind.POSSIBLE_FUNCTION_WORD

    def test_ala_preempts_root_eligible(self):
        """عَلَى would be ROOT_ELIGIBLE structurally but is in inventory as POSSIBLE."""
        assert _kind("عَلَى") == BoundaryKind.POSSIBLE_FUNCTION_WORD


# ══════════════════════════════════════════════════════════════════════════════
# 9.  Evidence provenance
# ══════════════════════════════════════════════════════════════════════════════

class TestEvidenceProvenance:
    """Evidence list must be non-empty and source must match the decision path."""

    def test_inventory_hit_has_inventory_source(self):
        d = assess_boundary("مِنْ")
        assert len(d.evidence) >= 1
        assert d.evidence[0].source == "inventory"

    def test_structural_eligible_has_count_and_eligible_sources(self):
        d = assess_boundary("ضَرَبَ")
        sources = {e.source for e in d.evidence}
        assert "structural:phone_count" in sources
        assert "structural:root_eligible_structure" in sources

    def test_ambiguous_has_prefix_source(self):
        d = assess_boundary("تَقِي")
        sources = {e.source for e in d.evidence}
        assert "structural:prefix_ambiguity" in sources

    def test_compressed_has_compressed_source(self):
        d = assess_boundary("قُلْ")
        sources = {e.source for e in d.evidence}
        assert "structural:compressed_verb" in sources


# ══════════════════════════════════════════════════════════════════════════════
# 10.  Serialization (to_dict)
# ══════════════════════════════════════════════════════════════════════════════

class TestToDict:
    """RootEligibilityDecision.to_dict() must produce a serializable dict."""

    def test_to_dict_has_required_keys(self):
        d = assess_boundary("ضَرَبَ")
        result = d.to_dict()
        for key in ("surface", "normalized", "kind", "directive", "stage_state", "evidence"):
            assert key in result, f"Missing key: {key}"

    def test_to_dict_kind_is_string(self):
        d = assess_boundary("مِنْ")
        assert isinstance(d.to_dict()["kind"], str)

    def test_to_dict_directive_is_string(self):
        d = assess_boundary("مِنْ")
        assert isinstance(d.to_dict()["directive"], str)

    def test_to_dict_evidence_is_list(self):
        d = assess_boundary("قُلْ")
        result = d.to_dict()
        assert isinstance(result["evidence"], list)
        assert all(isinstance(e, dict) for e in result["evidence"])

    def test_to_dict_values_for_root_eligible(self):
        d = assess_boundary("ضَرَبَ")
        result = d.to_dict()
        assert result["kind"] == "ROOT_ELIGIBLE"
        assert result["directive"] == "OPEN"
        assert result["stage_state"] == "OPENED"

    def test_to_dict_values_for_closed_function_word(self):
        d = assess_boundary("مِنْ")
        result = d.to_dict()
        assert result["kind"] == "CLOSED_FUNCTION_WORD"
        assert result["directive"] == "BLOCK"
        assert result["stage_state"] == "NOT_OPENED"


# ══════════════════════════════════════════════════════════════════════════════
# 11.  Surface vs normalized fields
# ══════════════════════════════════════════════════════════════════════════════

class TestBoundaryDoesNotModifySource:
    """The original surface must be preserved; normalized is a separate field."""

    def test_surface_preserved_for_hamza_word(self):
        """إِلَى: surface stays as supplied; normalized differs."""
        d = assess_boundary("إِلَى")
        assert d.surface == "إِلَى"
        # normalized has ء (from normalize_hamza)
        assert "ء" in d.normalized

    def test_surface_preserved_for_sound_verb(self):
        d = assess_boundary("ضَرَبَ")
        assert d.surface == "ضَرَبَ"

    def test_normalized_preserves_non_hamza(self):
        """Words with no hamza variants: normalized == surface."""
        d = assess_boundary("ضَرَبَ")
        assert d.surface == d.normalized

    def test_return_type(self):
        d = assess_boundary("قُلْ")
        assert isinstance(d, RootEligibilityDecision)
