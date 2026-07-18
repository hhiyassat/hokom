#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_live_morphology_consistency.py — Fix 13 reference corpus
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

One live hokom() assertion per architectural fix (Fixes 1–12).

Fix  1  — HR2S legacy removal: next_stage must be HOKOM_ROOT_ENGINE
Fix  2  — Proclitic فَ stripping: فَغَارَتْ → SEGMENTED with FA_PREP prefix
Fix  3  — وَحْد sukuun guard: وَحْدَهُمْ → host=وَحْدَ (وَ not stripped)
Fix  4  — WAW_AL_JAMAA damma→fatha restoration: يَكْتُبُونَ host=يَكْتُبَ
Fix  5/6 — Nominal morphology path → Phase4B NOT_APPLICABLE
Fix  7  — Promoted root candidate present when relicensing succeeds
Fix  8  — Resolved residuals not propagated after hypothesis_relicensed
Fix  9  — Residual dedup: no duplicate codes in Phase4A result
Fix 10  — Stale quadriliteral_beyond_scope removed when promoted root is trilateral
Fix 11  — Augmented form companion code (xfail — beyond current trilateral scope)
Fix 12  — Display reorder asserted indirectly via pipeline key ordering

Security constraints:
  - No modifications to /fractal/hr2s_morphology
  - No modifications to frozen files (root_profiles, root_rules, root_resolution,
    root_resolution_orchestrator, root_projection)
  - No git operations
  - No modifications to data/02_mabniyat/
"""

import pytest

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def pipeline():
    """Import hokom() once for the whole module."""
    from hokom_pipeline import hokom as _hokom
    return _hokom


def _run(pipeline, word):
    """Run pipeline and return result dict."""
    return pipeline(word)


def _p4a(result):
    return result.get('phase4a_result')


def _p4b(result):
    return result.get('phase4b_result')


def _pre_root(result):
    return result.get('pre_root')


def _attachment(result):
    return result.get('attachment')


def _root_candidate(result):
    return result.get('root_candidate')


# ---------------------------------------------------------------------------
# Fix 1 — HR2S legacy removal
# ---------------------------------------------------------------------------

class TestFix1_HR2SLegacyRemoval:
    """next_stage must be 'HOKOM_ROOT_ENGINE', never 'HR2S'."""

    def test_mahabbatin_next_stage_hokom_root_engine(self, pipeline):
        r = _run(pipeline, 'مَحَبَّةِ')
        pre = _pre_root(r)
        routing = getattr(pre, 'routing', None)
        next_stage = getattr(routing, 'next_stage', None)
        assert next_stage == 'HOKOM_ROOT_ENGINE', (
            f'expected HOKOM_ROOT_ENGINE, got {next_stage!r}'
        )

    def test_kataba_next_stage_hokom_root_engine(self, pipeline):
        r = _run(pipeline, 'كَتَبَ')
        pre = _pre_root(r)
        routing = getattr(pre, 'routing', None)
        next_stage = getattr(routing, 'next_stage', None)
        assert next_stage == 'HOKOM_ROOT_ENGINE'

    def test_next_stage_never_hr2s(self, pipeline):
        """Spot-check several words — none should route to HR2S."""
        words = ['مَحَبَّةِ', 'كَتَبَ', 'يَكْتُبُونَ', 'وَحْدَهُمْ', 'فَغَارَتْ']
        for word in words:
            r = _run(pipeline, word)
            pre = _pre_root(r)
            routing = getattr(pre, 'routing', None)
            next_stage = getattr(routing, 'next_stage', None) or ''
            assert 'HR2S' not in next_stage, (
                f'{word!r}: got next_stage={next_stage!r}, expected no HR2S'
            )


# ---------------------------------------------------------------------------
# Fix 2 — Proclitic فَ stripping
# ---------------------------------------------------------------------------

class TestFix2_ProcliticFaStripping:
    """فَغَارَتْ must be SEGMENTED with فَ as prefix operator."""

    def test_fagharat_is_segmented(self, pipeline):
        r = _run(pipeline, 'فَغَارَتْ')
        att = _attachment(r)
        seg = getattr(att, 'segmentation_verdict', None)
        assert seg == 'SEGMENTED', f'expected SEGMENTED, got {seg!r}'

    def test_fagharat_prefix_is_fa_prep(self, pipeline):
        r = _run(pipeline, 'فَغَارَتْ')
        att = _attachment(r)
        prefixes = [sp.mabni_id for sp in getattr(att, 'prefix_operators', [])]
        assert 'FA_PREP' in prefixes, f'prefix_operators={prefixes}'

    def test_fagharat_host_without_fa(self, pipeline):
        r = _run(pipeline, 'فَغَارَتْ')
        att = _attachment(r)
        host = getattr(att, 'host_surface', None) or ''
        assert host.startswith('غَ'), f'host={host!r}, expected غَارَتْ'
        assert not host.startswith('فَ'), f'فَ must be removed from host: {host!r}'

    def test_wahda_sukuun_guard_not_stripped(self, pipeline):
        """وَحْدَ alone must NOT have وَ stripped (حْ has sukuun — guard fires)."""
        from mabniyat_attachment import recognize_token
        r = recognize_token('وَحْدَ', 'ACCEPT')
        assert r.segmentation_verdict == 'NOT_SEGMENTED', (
            f'وَحْدَ should be NOT_SEGMENTED; got {r.segmentation_verdict!r}'
        )
        prefixes = [sp.mabni_id for sp in r.prefix_operators]
        assert 'WA_PREP' not in prefixes, f'وَ must not be stripped from وَحْدَ'


# ---------------------------------------------------------------------------
# Fix 3 — وَحْد guard (وَحْدَهُمْ)
# ---------------------------------------------------------------------------

class TestFix3_WahdGuard:
    """وَحْدَهُمْ must strip هُمْ as a suffix but keep وَحْدَ intact as host."""

    def test_wahdahum_host_is_wahda(self, pipeline):
        r = _run(pipeline, 'وَحْدَهُمْ')
        att = _attachment(r)
        host = getattr(att, 'host_surface', None)
        assert host == 'وَحْدَ', f'host={host!r}'

    def test_wahdahum_suffix_is_hum(self, pipeline):
        r = _run(pipeline, 'وَحْدَهُمْ')
        att = _attachment(r)
        suffix_ids = [sp.mabni_id for sp in getattr(att, 'attached_mabniyat', [])]
        assert 'ATTACHED_PRONOUN_HUM_SUFFIX' in suffix_ids, (
            f'expected HUM_SUFFIX in {suffix_ids}'
        )

    def test_wahdahum_no_wa_prefix(self, pipeline):
        r = _run(pipeline, 'وَحْدَهُمْ')
        att = _attachment(r)
        prefix_ids = [sp.mabni_id for sp in getattr(att, 'prefix_operators', [])]
        assert 'WA_PREP' not in prefix_ids, (
            f'وَ must not be a prefix for وَحْدَهُمْ; prefixes={prefix_ids}'
        )


# ---------------------------------------------------------------------------
# Fix 4 — WAW_AL_JAMAA damma→fatha restoration
# ---------------------------------------------------------------------------

class TestFix4_WawAlJamaaDammaRestoration:
    """يَكْتُبُونَ host must be يَكْتُبَ (fatha), not يَكْتُبُ (damma)."""

    def test_yaktubuna_suffix_is_waw_al_jamaa(self, pipeline):
        r = _run(pipeline, 'يَكْتُبُونَ')
        att = _attachment(r)
        suffix_ids = [sp.mabni_id for sp in getattr(att, 'attached_mabniyat', [])]
        assert 'ATTACHED_PRONOUN_WAW_AL_JAMAA' in suffix_ids, (
            f'expected WAW_AL_JAMAA in {suffix_ids}'
        )

    def test_yaktubuna_root_candidate_host_has_fatha(self, pipeline):
        """Root engine must receive يَكْتُبَ (fatha) not يَكْتُبُ (damma)."""
        r = _run(pipeline, 'يَكْتُبُونَ')
        rc = _root_candidate(r)
        host = getattr(rc, 'host_surface', None) or ''
        # The last vowel in the host must be fatha (َ), not damma (ُ)
        assert host.endswith('بَ'), (
            f'Expected host to end with بَ (fatha restored); got host={host!r}'
        )


# ---------------------------------------------------------------------------
# Fix 5/6 — Nominal morphology path → Phase4B NOT_APPLICABLE
# ---------------------------------------------------------------------------

class TestFix5_6_NominalMorphologyPathGate:
    """Nominal words must get Phase4B = NOT_APPLICABLE, not verbal Bab analysis."""

    def test_kalimatin_p4b_not_applicable(self, pipeline):
        r = _run(pipeline, 'كَلِمَةٍ')
        p4b = _p4b(r)
        assert p4b is not None, 'phase4b_result is None — Phase4A must be ACCEPT first'
        directive = getattr(p4b, 'final_directive', None)
        assert directive == 'NOT_APPLICABLE', (
            f'كَلِمَةٍ nominal path: expected NOT_APPLICABLE, got {directive!r}'
        )

    def test_rajulin_p4b_not_applicable(self, pipeline):
        r = _run(pipeline, 'رَجُلٍ')
        p4b = _p4b(r)
        if p4b is None:
            pytest.skip('phase4a did not ACCEPT رَجُلٍ — skip P4B check')
        directive = getattr(p4b, 'final_directive', None)
        assert directive == 'NOT_APPLICABLE'

    def test_kalimatin_morphology_path_is_nominal(self, pipeline):
        r = _run(pipeline, 'كَلِمَةٍ')
        pre = _pre_root(r)
        mp = getattr(pre, 'morphology_path', None)
        mp_val = getattr(mp, 'value', str(mp))
        assert mp_val == 'nominal_morphology_path', f'got {mp_val!r}'

    def test_p4b_source_path_nominal(self, pipeline):
        r = _run(pipeline, 'كَلِمَةٍ')
        p4b = _p4b(r)
        if p4b is None:
            pytest.skip('phase4b is None')
        source_path = getattr(p4b, 'source_path', None)
        assert source_path == 'not_applicable'


# ---------------------------------------------------------------------------
# Fix 7 — Promoted root candidate present
# ---------------------------------------------------------------------------

class TestFix7_PromotedRootCandidate:
    """When relicensing accepts a root, promoted_root_candidate must be set."""

    def test_mahabbatin_promoted_root_present(self, pipeline):
        r = _run(pipeline, 'مَحَبَّةِ')
        p4a = _p4a(r)
        assert p4a is not None
        promoted = getattr(p4a, 'promoted_root_candidate', None)
        # Relicensing identifies ح-ب-ب as the promoted trilateral root
        assert promoted is not None, 'promoted_root_candidate must not be None'

    def test_mahabbatin_promoted_root_is_habb(self, pipeline):
        r = _run(pipeline, 'مَحَبَّةِ')
        p4a = _p4a(r)
        promoted = getattr(p4a, 'promoted_root_candidate', None)
        if promoted is None:
            pytest.skip('no promoted root candidate')
        canon = getattr(promoted, 'canonical_root', None)
        assert canon is not None, 'canonical_root must not be None on promoted candidate'
        root_str = ''.join(canon)
        assert root_str == 'حبب', f'expected حبب, got {root_str!r}'


# ---------------------------------------------------------------------------
# Fix 8 — Resolved residuals not propagated
# ---------------------------------------------------------------------------

class TestFix8_ResolvedResidualsPartition:
    """defer:root:* residuals must be removed when phase4a source_path='hypothesis_relicensed'."""

    def test_mahabbatin_no_stale_residuals_in_p4b(self, pipeline):
        """مَحَبَّةِ is nominal → P4B NOT_APPLICABLE, but residuals must be clean."""
        r = _run(pipeline, 'مَحَبَّةِ')
        p4a = _p4a(r)
        if p4a is None:
            pytest.skip('no phase4a')
        residuals = getattr(p4a, 'residual_codes', ()) or ()
        # quadriliteral_beyond_scope must NOT appear when promoted root is trilateral
        assert 'defer:root:quadriliteral_beyond_scope' not in residuals, (
            f'stale residual still present: {residuals}'
        )

    def test_hypothesis_relicensed_no_defer_root_codes(self, pipeline):
        """Any word with source_path=hypothesis_relicensed & trilateral promoted root
        must NOT carry defer:root:* in its final Phase4A residuals."""
        r = _run(pipeline, 'مَحَبَّةِ')
        p4a = _p4a(r)
        if p4a is None:
            pytest.skip('no phase4a')
        source_path = getattr(p4a, 'source_path', None)
        promoted = getattr(p4a, 'promoted_root_candidate', None)
        if source_path != 'hypothesis_relicensed' or promoted is None:
            pytest.skip('not hypothesis_relicensed path or no promoted root')
        canon = getattr(promoted, 'canonical_root', None) or ()
        if len(canon) != 3:
            pytest.skip('promoted root is not trilateral')
        residuals = set(getattr(p4a, 'residual_codes', ()) or ())
        stale = {'defer:root:quadriliteral_beyond_scope',
                 'defer:root:non_standard_consonant_count'}
        overlap = residuals & stale
        assert not overlap, f'stale residuals still present: {overlap}'


# ---------------------------------------------------------------------------
# Fix 9 — Residual dedup
# ---------------------------------------------------------------------------

class TestFix9_ResidualDedup:
    """No duplicate residual codes in Phase4A result."""

    def _check_no_dups(self, residuals, label):
        codes = list(residuals or ())
        assert len(codes) == len(set(codes)), (
            f'{label}: duplicate residuals found: {codes}'
        )

    def test_kataba_no_duplicate_residuals(self, pipeline):
        r = _run(pipeline, 'كَتَبَ')
        p4a = _p4a(r)
        self._check_no_dups(getattr(p4a, 'residual_codes', ()), 'كَتَبَ phase4a')

    def test_mahabbatin_no_duplicate_residuals(self, pipeline):
        r = _run(pipeline, 'مَحَبَّةِ')
        p4a = _p4a(r)
        self._check_no_dups(getattr(p4a, 'residual_codes', ()), 'مَحَبَّةِ phase4a')

    def test_yaktubuna_no_duplicate_residuals(self, pipeline):
        r = _run(pipeline, 'يَكْتُبُونَ')
        p4a = _p4a(r)
        self._check_no_dups(getattr(p4a, 'residual_codes', ()), 'يَكْتُبُونَ phase4a')

    def test_kataba_p4b_no_duplicate_residuals(self, pipeline):
        r = _run(pipeline, 'كَتَبَ')
        p4b = _p4b(r)
        if p4b is None:
            pytest.skip('phase4b is None')
        self._check_no_dups(getattr(p4b, 'residual_codes', ()), 'كَتَبَ phase4b')


# ---------------------------------------------------------------------------
# Fix 10 — Stale quadriliteral residuals removed for trilateral relicensed root
# ---------------------------------------------------------------------------

class TestFix10_StaleQuadriliteralFiltered:
    """When promoted root is trilateral, quadriliteral_beyond_scope must be absent."""

    def test_mahabbatin_quadriliteral_code_absent(self, pipeline):
        r = _run(pipeline, 'مَحَبَّةِ')
        p4a = _p4a(r)
        if p4a is None:
            pytest.skip('no phase4a')
        promoted = getattr(p4a, 'promoted_root_candidate', None)
        if promoted is None:
            pytest.skip('no promoted root')
        canon = getattr(promoted, 'canonical_root', None) or ()
        if len(canon) != 3:
            pytest.skip('promoted root is not trilateral')
        residuals = getattr(p4a, 'residual_codes', ()) or ()
        assert 'defer:root:quadriliteral_beyond_scope' not in residuals, (
            f'stale quadriliteral code still present: {residuals}'
        )


# ---------------------------------------------------------------------------
# Fix 11 — Augmented form companion code
# FULLY RESOLVED: AugmentedHostRefinement + AugmentedWaznShortcut now handle
# Forms II–X directly through all phases:
#   - تَكَلَّمَ (Form V)    → Phase4A ACCEPT (augmented_direct), Phase4B ACCEPT
#   - يَسْتَخْرِجُ (Form X) → Phase4A ACCEPT (augmented_direct), Phase4B ACCEPT
# The xfail test for Phase4A DEFER on يَسْتَخْرِجُ is now resolved.
# The old companion codes (augmented_form_beyond_scope, non_standard_consonant_count)
# are no longer emitted; replaced by HOKOM_AUGMENTED_ENGINE metadata.
# ---------------------------------------------------------------------------

class TestFix11_AugmentedFormCompanionCode:
    """Augmented (mazid) forms are now fully resolved by HOKOM_AUGMENTED_ENGINE.

    Fix 11 CLOSED: AugmentedWaznShortcut in build_augmented_phase4a() now
    directly produces Phase4AResult ACCEPT for all Forms II–X, using the
    known wazn_id from the detected form family (bypassing WaznHypothesis).
    """

    def test_yastakhriju_phase4a_accept_via_augmented_direct(self, pipeline):
        """يَسْتَخْرِجُ (Form X) — Phase4A now ACCEPT via augmented_direct shortcut."""
        r = _run(pipeline, 'يَسْتَخْرِجُ')
        p4a = _p4a(r)
        assert p4a is not None, 'phase4a_result expected'
        directive = getattr(p4a, 'final_directive', None)
        assert directive == 'ACCEPT', (
            f'Form X يَسْتَخْرِجُ: expected ACCEPT got {directive!r}'
        )
        source_path = getattr(p4a, 'source_path', None)
        assert source_path == 'augmented_direct', (
            f'expected augmented_direct got {source_path!r}'
        )
        final_wazn = getattr(p4a, 'final_wazn', None)
        assert final_wazn == 'ISTAF3ALA', (
            f'Form X wazn_id expected ISTAF3ALA got {final_wazn!r}'
        )

    def test_yastakhriju_root_resolved_by_augmented_engine(self, pipeline):
        """يَسْتَخْرِجُ root is now resolved by HOKOM_AUGMENTED_ENGINE."""
        r = _run(pipeline, 'يَسْتَخْرِجُ')
        rc = r.get('root_candidate')
        aug = r.get('augmented_analysis')
        assert aug is not None, 'augmented_analysis should be present for Form X'
        assert aug.form_family == 'FORM_X'
        assert rc is not None
        assert rc.canonical_root == ('خ', 'ر', 'ج'), (
            f'root expected (خ,ر,ج) got {rc.canonical_root!r}'
        )
        profile = rc.root_profile or {}
        assert profile.get('source_engine') == 'HOKOM_AUGMENTED_ENGINE'

    def test_yastakhriju_phase4a_wazn_accept_augmented_direct(self, pipeline):
        """يَسْتَخْرِجُ Phase4A ACCEPT with ISTAF3ALA — augmented_direct path."""
        r = _run(pipeline, 'يَسْتَخْرِجُ')
        p4a = _p4a(r)
        if p4a is None:
            pytest.skip('no phase4a')
        directive = getattr(p4a, 'final_directive', None)
        source_path = getattr(p4a, 'source_path', None)
        assert directive == 'ACCEPT', f'expected ACCEPT got {directive!r}'
        assert source_path == 'augmented_direct', (
            f'expected augmented_direct got {source_path!r}'
        )

    def test_takallama_full_analysis_now_succeeds(self, pipeline):
        """تَكَلَّمَ (Form V) — AugmentedHostRefinement resolves root; Phase4A accepts."""
        r = _run(pipeline, 'تَكَلَّمَ')
        rc = r.get('root_candidate')
        aug = r.get('augmented_analysis')
        assert aug is not None, 'augmented_analysis should be present for Form V'
        assert aug.form_family == 'FORM_V'
        assert rc is not None
        assert rc.canonical_root == ('ك', 'ل', 'م'), (
            f'root expected (ك,ل,م) got {rc.canonical_root!r}'
        )
        p4a = _p4a(r)
        directive = getattr(p4a, 'final_directive', None)
        assert directive == 'ACCEPT', (
            f'تَكَلَّمَ Form V: expected Phase4A ACCEPT got {directive!r}'
        )


# ---------------------------------------------------------------------------
# Fix 12 — Display reorder (P2/P3 before Phase4A in output)
# ---------------------------------------------------------------------------

class TestFix12_DisplayReorder:
    """Verify pipeline result dict contains the expected keys in the correct order.

    The actual display reorder is in the verbose display function.  Here we
    assert the structural keys exist and are populated correctly, which is
    the prerequisite for correct ordering.
    """

    def test_result_has_root_projection_before_phase4a(self, pipeline):
        r = _run(pipeline, 'كَتَبَ')
        keys = list(r.keys())
        # Verify structural ordering: root_projection appears before phase4a_result
        assert 'root_projection' in keys
        assert 'phase4a_result' in keys
        rp_idx = keys.index('root_projection')
        p4a_idx = keys.index('phase4a_result')
        assert rp_idx < p4a_idx, (
            f'root_projection (index {rp_idx}) must appear before '
            f'phase4a_result (index {p4a_idx}) in result keys'
        )

    def test_result_has_root_candidate_before_phase4a(self, pipeline):
        r = _run(pipeline, 'كَتَبَ')
        keys = list(r.keys())
        rc_idx = keys.index('root_candidate')
        p4a_idx = keys.index('phase4a_result')
        assert rc_idx < p4a_idx
