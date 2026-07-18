#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_span_alignment.py — Phase B: P1_POSITION_CARRIER tests

Tests for span_alignment.SpanAlignmentMap and the normalize_tracked()
family in normalizer.py.

Governing rule: every normalized position must be projectable back to a
raw position in the original surface.

Five governing test cases (per Phase B design):
    1. أُمِّهِمْ   — shadda on م: raw=9, normalized=10 (+1)
    2. أَنَّهُمْ  — shadda on ن: raw=9, normalized=10 (+1)
    3. كَتَبَاهُ  — no shadda, no ال: delta=0
    4. بِهِمْ     — no shadda, no ال: delta=0
    5. وَحْدَهُمْ — no shadda, no ال: delta=0

Additionally tests:
    - SpanAlignmentMap API (identity, project_to_raw, project_to_norm, compose)
    - normalize_hamza_tracked (آ expansion, أ replacement)
    - normalize_al_tracked (ال expansion)
    - build_glyph_traces with alignment=... (original_span precision)
    - AttachedMabniSpan.raw_span via recognize_token(alignment=...)
"""

import sys
import os

# Ensure repo root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from span_alignment import SpanAlignmentMap, SpanEntry, ComponentRole, ComponentBoundary
from normalizer import (
    normalize,
    normalize_hamza_tracked,
    normalize_al_tracked,
    normalize_shadda_tracked,
    normalize_tracked,
)
from glyph_classification import build_glyph_traces


# ══════════════════════════════════════════════════════════════════════════════
# SpanAlignmentMap — unit tests
# ══════════════════════════════════════════════════════════════════════════════

class TestSpanAlignmentMapIdentity:
    def test_identity_factory(self):
        m = SpanAlignmentMap.identity(5)
        assert m.raw_len  == 5
        assert m.norm_len == 5
        assert len(m.entries) == 1
        assert m.entries[0].op == 'IDENTITY'

    def test_identity_project_to_norm(self):
        m = SpanAlignmentMap.identity(9)
        assert m.project_to_norm(0, 9) == (0, 9)
        assert m.project_to_norm(2, 5) == (2, 5)
        assert m.project_to_norm(0, 1) == (0, 1)

    def test_identity_project_to_raw(self):
        m = SpanAlignmentMap.identity(9)
        assert m.project_to_raw(0, 9) == (0, 9)
        assert m.project_to_raw(3, 7) == (3, 7)

    def test_identity_zero_length(self):
        m = SpanAlignmentMap.identity(0)
        assert m.raw_len  == 0
        assert m.norm_len == 0
        assert m.entries  == []

    def test_identity_compose_is_identity(self):
        a = SpanAlignmentMap.identity(5)
        b = SpanAlignmentMap.identity(5)
        c = a.compose(b)
        assert c.raw_len  == 5
        assert c.norm_len == 5
        assert c.project_to_norm(1, 3) == (1, 3)
        assert c.project_to_raw(1, 3)  == (1, 3)


class TestSpanAlignmentMapExpand:
    """Simple EXPAND: 1 raw char → 3 norm chars (آ → ءَا)."""

    def _map(self):
        # raw: آ (1 char) → norm: ءَا (3 chars)
        return SpanAlignmentMap.from_entries(
            raw_len=1, norm_len=3,
            entries=[SpanEntry(0, 1, 0, 3, 'EXPAND', 'آ→ءَا')],
        )

    def test_project_to_norm_expand(self):
        m = self._map()
        assert m.project_to_norm(0, 1) == (0, 3)

    def test_project_to_raw_expand(self):
        m = self._map()
        assert m.project_to_raw(0, 3) == (0, 1)
        assert m.project_to_raw(0, 1) == (0, 1)   # sub-query: conservative
        assert m.project_to_raw(1, 2) == (0, 1)   # sub-query: conservative
        assert m.project_to_raw(2, 3) == (0, 1)   # sub-query: conservative


class TestSpanAlignmentMapMixedEntries:
    """Mixed IDENTITY + EXPAND entries."""

    def _map(self):
        # raw:  a(0) b(1) c(2) آ(3) d(4) e(5)  = 6 chars
        # norm: a(0) b(1) c(2) ءَا(3,4,5) d(6) e(7) = 8 chars
        return SpanAlignmentMap.from_entries(
            raw_len=6, norm_len=8,
            entries=[
                SpanEntry(0, 3, 0, 3, 'IDENTITY', ''),
                SpanEntry(3, 4, 3, 6, 'EXPAND',   'آ→ءَا'),
                SpanEntry(4, 6, 6, 8, 'IDENTITY', ''),
            ],
        )

    def test_project_to_norm_before_expand(self):
        m = self._map()
        assert m.project_to_norm(0, 3) == (0, 3)
        assert m.project_to_norm(1, 2) == (1, 2)   # precise IDENTITY

    def test_project_to_norm_at_expand(self):
        m = self._map()
        assert m.project_to_norm(3, 4) == (3, 6)

    def test_project_to_norm_after_expand(self):
        m = self._map()
        assert m.project_to_norm(4, 6) == (6, 8)
        assert m.project_to_norm(4, 5) == (6, 7)   # precise IDENTITY sub-span
        assert m.project_to_norm(5, 6) == (7, 8)   # precise IDENTITY sub-span

    def test_project_to_raw_before_expand(self):
        m = self._map()
        assert m.project_to_raw(0, 3) == (0, 3)
        assert m.project_to_raw(1, 2) == (1, 2)

    def test_project_to_raw_at_expand(self):
        m = self._map()
        assert m.project_to_raw(3, 6) == (3, 4)
        assert m.project_to_raw(3, 4) == (3, 4)   # conservative
        assert m.project_to_raw(4, 5) == (3, 4)   # conservative

    def test_project_to_raw_after_expand(self):
        m = self._map()
        assert m.project_to_raw(6, 8) == (4, 6)
        assert m.project_to_raw(6, 7) == (4, 5)   # precise IDENTITY sub-span
        assert m.project_to_raw(7, 8) == (5, 6)   # precise IDENTITY sub-span


# ══════════════════════════════════════════════════════════════════════════════
# normalize_hamza_tracked
# ══════════════════════════════════════════════════════════════════════════════

class TestNormalizeHamzaTracked:
    def test_output_equals_normalize_hamza(self):
        from normalizer import normalize_hamza
        for s in ['أُمِّهِمْ', 'إِنَّ', 'آ', 'ؤُ', 'ئِ', 'بِالْكِتَابِ']:
            out, _ = normalize_hamza_tracked(s)
            assert out == normalize_hamza(s), f'mismatch for {s!r}'

    def test_alef_madda_expands(self):
        out, m = normalize_hamza_tracked('آ')
        assert out == 'ءَا'
        assert m.raw_len  == 1
        assert m.norm_len == 3
        assert m.project_to_raw(0, 3) == (0, 1)
        assert m.project_to_norm(0, 1) == (0, 3)

    def test_hamza_on_alef_replaces_same_length(self):
        # أُ (2 chars) → ءُ (2 chars): REPLACE, length preserved
        out, m = normalize_hamza_tracked('أُ')
        assert out == 'ءُ'
        assert m.raw_len  == 2
        assert m.norm_len == 2
        assert m.project_to_norm(0, 2) == (0, 2)
        assert m.project_to_raw(0, 2)  == (0, 2)

    def test_identity_passthrough(self):
        # بِكَ has no hamza forms: all IDENTITY
        out, m = normalize_hamza_tracked('بِكَ')
        assert out == 'بِكَ'
        assert m.raw_len  == 4
        assert m.norm_len == 4
        assert m.project_to_norm(0, 4) == (0, 4)
        assert m.project_to_raw(0, 4)  == (0, 4)

    def test_ummi_hihi_m_hamza_stage(self):
        # أُمِّهِمْ: أُ → ءُ (REPLACE, 2→2), rest IDENTITY
        raw = 'أُمِّهِمْ'
        out, m = normalize_hamza_tracked(raw)
        assert len(out) == len(raw)         # normalize_hamza preserves length here
        assert m.raw_len  == len(raw)
        assert m.norm_len == len(raw)
        # First cluster: أُ at [0,2) → ءُ at [0,2): REPLACE
        assert m.project_to_raw(0, 2)  == (0, 2)
        assert m.project_to_norm(0, 2) == (0, 2)


# ══════════════════════════════════════════════════════════════════════════════
# normalize_al_tracked
# ══════════════════════════════════════════════════════════════════════════════

class TestNormalizeAlTracked:
    def test_output_equals_normalize_al(self):
        from normalizer import normalize_al
        for s in ['الْكِتَابُ', 'بِالْقَلَمِ', 'أُمِّهِمْ', 'كَتَبَ']:
            out, _ = normalize_al_tracked(s)
            assert out == normalize_al(s), f'mismatch for {s!r}'

    def test_al_expands_by_one(self):
        # الكتاب (6 chars: ا+ل+ك+ت+ا+ب) → ءَلكتاب (7 chars)
        raw = 'الكتاب'
        out, m = normalize_al_tracked(raw)
        assert len(out) == len(raw) + 1
        assert m.raw_len  == len(raw)
        assert m.norm_len == len(out)
        # ا at [0,1) → ءَ at [0,2): EXPAND
        assert m.project_to_norm(0, 1) == (0, 2)
        assert m.project_to_raw(0, 2)  == (0, 1)
        # ل at [1,2) → at [2,3): IDENTITY (precise)
        assert m.project_to_norm(1, 2) == (2, 3)
        assert m.project_to_raw(2, 3)  == (1, 2)

    def test_no_al_is_identity(self):
        raw = 'أُمِّهِمْ'
        out, m = normalize_al_tracked(raw)
        assert m.raw_len  == len(raw)
        assert m.norm_len == len(raw)
        assert m.project_to_norm(0, len(raw)) == (0, len(raw))
        assert m.project_to_raw(0, len(raw))  == (0, len(raw))

    def test_space_preserved(self):
        raw = 'ال كتاب'   # space between ال and كتاب (unusual but should work)
        out, m = normalize_al_tracked(raw)
        from normalizer import normalize_al
        assert out == normalize_al(raw)


# ══════════════════════════════════════════════════════════════════════════════
# normalize_shadda_tracked
# ══════════════════════════════════════════════════════════════════════════════

class TestNormalizeShadaaTracked:
    def test_output_equals_normalize_shadda(self):
        from normalizer import normalize_shadda
        for s in ['ءُمِّهِمْ', 'ءَنَّهُمْ', 'كَتَبَاهُ', 'بِهِمْ', 'وَحْدَهُمْ']:
            out, _ = normalize_shadda_tracked(s)
            assert out == normalize_shadda(s), f'mismatch for {s!r}'

    def test_shadda_expands_by_one(self):
        # مِّ (م + ِ + ّ = 3 chars) → مْمِ (4 chars)
        raw = 'مِّ'
        out, m = normalize_shadda_tracked(raw)
        assert len(out) == len(raw) + 1
        assert out == 'مْمِ'
        # whole cluster [0,3) → [0,4)
        assert m.project_to_norm(0, 3) == (0, 4)
        assert m.project_to_raw(0, 4)  == (0, 3)

    def test_no_shadda_is_identity(self):
        raw = 'كَتَبَاهُ'
        out, m = normalize_shadda_tracked(raw)
        assert out == raw
        assert m.raw_len == m.norm_len == len(raw)
        assert m.project_to_norm(0, len(raw)) == (0, len(raw))

    def test_ummi_shadda_stage(self):
        # ءُمِّهِمْ (9 chars, after hamza+al): shadda on م at positions [2,5)
        raw = 'ءُمِّهِمْ'
        out, m = normalize_shadda_tracked(raw)
        assert len(out) == len(raw) + 1   # +1 for shadda expansion
        # مِّ cluster at raw[2,5) → expanded at norm[2,6)
        assert m.project_to_norm(2, 5) == (2, 6)
        assert m.project_to_raw(2, 6)  == (2, 5)
        # هِ cluster at raw[5,7) → norm[6,8) IDENTITY
        assert m.project_to_norm(5, 7) == (6, 8)
        assert m.project_to_raw(6, 8)  == (5, 7)
        # مْ cluster at raw[7,9) → norm[8,10) IDENTITY
        assert m.project_to_norm(7, 9) == (8, 10)
        assert m.project_to_raw(8, 10) == (7, 9)


# ══════════════════════════════════════════════════════════════════════════════
# normalize_tracked — five governing cases
# ══════════════════════════════════════════════════════════════════════════════

class TestNormalizeTracked:
    """
    Five governing test cases for Phase B.

    Each test verifies:
      1. Output equals normalize()
      2. Correct raw_len and norm_len
      3. Key project_to_raw spans are correct
    """

    def _check_output(self, raw: str) -> 'tuple[str, SpanAlignmentMap]':
        out, m = normalize_tracked(raw)
        assert out == normalize(raw), f'output mismatch for {raw!r}'
        assert m.raw_len  == len(raw)
        assert m.norm_len == len(out)
        return out, m

    # ── Case 1: أُمِّهِمْ ────────────────────────────────────────────────────

    def test_ummi_output_length(self):
        raw = 'أُمِّهِمْ'
        out, m = self._check_output(raw)
        assert len(raw) == 9
        assert len(out) == 10   # +1 shadda expansion

    def test_ummi_shadda_cluster_projects_to_raw(self):
        # Normalized مْمِ at norm[2,6) ← raw مِّ at raw[2,5)
        raw = 'أُمِّهِمْ'
        out, m = self._check_output(raw)
        assert m.project_to_raw(2, 6) == (2, 5)

    def test_ummi_ha_hi_projects_to_raw(self):
        # Normalized هِ at norm[6,8) ← raw هِ at raw[5,7)
        raw = 'أُمِّهِمْ'
        out, m = self._check_output(raw)
        assert m.project_to_raw(6, 8) == (5, 7)

    def test_ummi_final_mim_projects_to_raw(self):
        # Normalized مْ at norm[8,10) ← raw مْ at raw[7,9)
        raw = 'أُمِّهِمْ'
        out, m = self._check_output(raw)
        assert m.project_to_raw(8, 10) == (7, 9)

    def test_ummi_first_cluster_projects_to_raw(self):
        # Normalized ءُ at norm[0,2) ← raw أُ at raw[0,2) (REPLACE, length 2)
        raw = 'أُمِّهِمْ'
        out, m = self._check_output(raw)
        assert m.project_to_raw(0, 2) == (0, 2)

    # ── Case 2: أَنَّهُمْ ────────────────────────────────────────────────────

    def test_anna_output_length(self):
        raw = 'أَنَّهُمْ'
        out, m = self._check_output(raw)
        assert len(raw) == 9
        assert len(out) == 10   # +1 shadda on ن

    def test_anna_shadda_cluster_projects_to_raw(self):
        # raw أَنَّهُمْ: أ(0) َ(1) ن(2) َ(3) ّ(4) ه(5) ُ(6) م(7) ْ(8)
        # After hamza: ءَنَّهُمْ (9 chars, أَ→ءَ REPLACE 2→2)
        # After shadda: ءَنْنَهُمْ (10 chars)
        # Normalized نَّ cluster at raw[2,5) → norm[2,6)
        raw = 'أَنَّهُمْ'
        out, m = self._check_output(raw)
        assert m.project_to_raw(2, 6) == (2, 5)

    def test_anna_suffix_projects_to_raw(self):
        # هُمْ in normalized → هُمْ in raw
        raw = 'أَنَّهُمْ'
        out, m = self._check_output(raw)
        # هُ at norm[6,8) ← raw[5,7)
        assert m.project_to_raw(6, 8) == (5, 7)
        # مْ at norm[8,10) ← raw[7,9)
        assert m.project_to_raw(8, 10) == (7, 9)

    # ── Case 3: كَتَبَاهُ ────────────────────────────────────────────────────

    def test_katabaahu_delta_zero(self):
        raw = 'كَتَبَاهُ'
        out, m = self._check_output(raw)
        assert len(out) == len(raw)   # no expansion

    def test_katabaahu_full_span_identity(self):
        raw = 'كَتَبَاهُ'
        out, m = self._check_output(raw)
        n = len(raw)
        assert m.project_to_raw(0, n)  == (0, n)
        assert m.project_to_norm(0, n) == (0, n)

    def test_katabaahu_sub_spans_precise(self):
        raw = 'كَتَبَاهُ'
        out, m = self._check_output(raw)
        # Each char projects to itself
        for i in range(len(raw)):
            assert m.project_to_raw(i, i+1) == (i, i+1)

    # ── Case 4: بِهِمْ ───────────────────────────────────────────────────────

    def test_bihim_delta_zero(self):
        raw = 'بِهِمْ'
        out, m = self._check_output(raw)
        assert len(out) == len(raw)
        n = len(raw)
        assert m.project_to_raw(0, n)  == (0, n)
        assert m.project_to_norm(0, n) == (0, n)

    def test_bihim_sub_spans(self):
        raw = 'بِهِمْ'
        out, m = self._check_output(raw)
        for i in range(len(raw)):
            assert m.project_to_raw(i, i+1) == (i, i+1)

    # ── Case 5: وَحْدَهُمْ ───────────────────────────────────────────────────

    def test_wahdahum_delta_zero(self):
        raw = 'وَحْدَهُمْ'
        out, m = self._check_output(raw)
        assert len(out) == len(raw)
        n = len(raw)
        assert m.project_to_raw(0, n)  == (0, n)
        assert m.project_to_norm(0, n) == (0, n)


# ══════════════════════════════════════════════════════════════════════════════
# build_glyph_traces with alignment
# ══════════════════════════════════════════════════════════════════════════════

class TestBuildGlyphTracesWithAlignment:
    """
    Verify that GlyphTrace.original_span is precise when alignment is passed.
    """

    def _traces(self, raw: str):
        norm_str, alignment = normalize_tracked(raw)
        return build_glyph_traces(norm_str, alignment=alignment), raw

    def test_ummi_original_span_hamza(self):
        # أُمِّهِمْ: first glyph is ء in norm, came from أُ in raw → raw[0,2)
        traces, raw = self._traces('أُمِّهِمْ')
        assert traces[0].nfc_base == 'ء'
        assert traces[0].original_span == (0, 2)

    def test_ummi_original_span_shadda_copies(self):
        # After shadda expansion, both copies of م come from raw مِّ at [2,5)
        traces, raw = self._traces('أُمِّهِمْ')
        # traces[1] = first م (مْ), traces[2] = second م (مِ)
        assert traces[1].nfc_base == 'م'
        assert traces[2].nfc_base == 'م'
        assert traces[1].original_span == (2, 5)
        assert traces[2].original_span == (2, 5)

    def test_ummi_original_span_ha(self):
        # ه glyph: raw هِ at [5,7)
        traces, raw = self._traces('أُمِّهِمْ')
        ha_trace = next(t for t in traces if t.nfc_base == 'ه')
        assert ha_trace.original_span == (5, 7)

    def test_anna_original_span_nun_cluster(self):
        # أَنَّهُمْ: both copies of ن come from raw نَّ at [2,5)
        traces, raw = self._traces('أَنَّهُمْ')
        nun_traces = [t for t in traces if t.nfc_base == 'ن']
        assert len(nun_traces) == 2   # shadda expansion
        assert nun_traces[0].original_span == (2, 5)
        assert nun_traces[1].original_span == (2, 5)

    def test_katabaahu_all_identity(self):
        # كَتَبَاهُ: all original_spans are NFC-span (no expansion)
        traces, raw = self._traces('كَتَبَاهُ')
        norm_str, _ = normalize_tracked('كَتَبَاهُ')
        for t in traces:
            # original_span should equal nfc_span (identity transformation)
            assert t.original_span == t.nfc_span, (
                f'glyph {t.nfc_base!r}: original={t.original_span} nfc={t.nfc_span}'
            )

    def test_no_alignment_gives_nfc_span(self):
        # Without alignment, original_span == nfc_span (Phase A behaviour)
        norm_str = normalize('أُمِّهِمْ')
        traces = build_glyph_traces(norm_str)
        for t in traces:
            assert t.original_span == t.nfc_span


# ══════════════════════════════════════════════════════════════════════════════
# AttachedMabniSpan.raw_span via recognize_token(alignment=...)
# ══════════════════════════════════════════════════════════════════════════════

class TestRecognizeTokenRawSpan:
    """
    Verify raw_span is populated on suffix spans when alignment is passed.
    These tests use cases with no shadda so raw==norm for easy verification.
    """

    def test_bihim_suffix_raw_span(self):
        """بِهِمْ: host=بِ + suffix=هِمْ. No shadda, delta=0."""
        from mabniyat_attachment import recognize_token
        raw = 'بِهِمْ'
        norm_str, alignment = normalize_tracked(raw)
        assert norm_str == raw   # no change expected
        result = recognize_token(norm_str, 'ACCEPT', alignment=alignment)
        assert result.segmentation_verdict == 'SEGMENTED'
        for sp in result.attached_mabniyat:
            assert sp.raw_span is not None
            # Since no shadda, raw_span == norm span
            assert sp.raw_span == (sp.span_start, sp.span_end)

    def test_no_alignment_raw_span_is_none(self):
        """Without alignment, raw_span stays None."""
        from mabniyat_attachment import recognize_token
        raw = 'بِهِمْ'
        norm_str, _ = normalize_tracked(raw)
        result = recognize_token(norm_str, 'ACCEPT')
        assert result.segmentation_verdict == 'SEGMENTED'
        for sp in result.attached_mabniyat:
            assert sp.raw_span is None

    def test_katabaahu_suffix_raw_span(self):
        """كَتَبَاهُ: suffix=هُ. No shadda, delta=0."""
        from mabniyat_attachment import recognize_token
        raw = 'كَتَبَاهُ'
        norm_str, alignment = normalize_tracked(raw)
        result = recognize_token(norm_str, 'ACCEPT',
                                 original_surface=raw, alignment=alignment)
        assert result.segmentation_verdict == 'SEGMENTED'
        for sp in result.attached_mabniyat:
            assert sp.raw_span is not None
            assert sp.raw_span == (sp.span_start, sp.span_end)


# ══════════════════════════════════════════════════════════════════════════════
# ComponentBoundary (B-5 sanity check)
# ══════════════════════════════════════════════════════════════════════════════

class TestComponentBoundary:
    def test_create(self):
        cb = ComponentBoundary(
            role      = ComponentRole.SUFFIX,
            raw_span  = (5, 7),
            norm_span = (6, 8),
            surface   = 'هِ',
            mabni_id  = 'ATTACHED_PRONOUN_HA',
        )
        assert cb.role      == ComponentRole.SUFFIX
        assert cb.raw_span  == (5, 7)
        assert cb.norm_span == (6, 8)
        assert cb.surface   == 'هِ'

    def test_all_roles(self):
        roles = list(ComponentRole)
        assert ComponentRole.HOST              in roles
        assert ComponentRole.PREFIX            in roles
        assert ComponentRole.SUFFIX            in roles
        assert ComponentRole.OPERATOR          in roles
        assert ComponentRole.MABNI             in roles
        assert ComponentRole.INFLECTIONAL_TAIL in roles

    def test_best_effort_raw_equals_norm(self):
        # When no alignment available, raw_span == norm_span (best-effort)
        cb = ComponentBoundary(
            role      = ComponentRole.HOST,
            raw_span  = (0, 6),
            norm_span = (0, 6),
            surface   = 'كَتَبَ',
        )
        assert cb.raw_span == cb.norm_span
