#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hokom_pipeline.py — خط أنابيب الحكم الكامل
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

المراحل:
  1. tokenizer           → تجزئة النص، فصل الـ clitics، تنظيف الترقيم
  2. normalizer          → ال التعريف + الشدة
  3. Unicode Candidate   → هل الحرف من الـ 25 أو حروف العلة؟
  4. Character Licensing → دور الحرف: C أو VL
  5. Diacritic Licensing → هل الحركات مرخصة؟
  6. Cell Construction   → ترميز الخلية: C | CV | V
  7. Slot Engineering    → توزيع على الأنماط الستة → ACCEPT | DEFER | BLOCK

الاستخدام:
  python hokom_pipeline.py
  python hokom_pipeline.py "وَالْمُلُوكُ إِذَا دَخَلُوا"
"""

import sys
import uuid as _uuid
from tokenizer    import tokenize, words_only
from normalizer   import normalize
from pipeline.p0_segmentation.normalization import canonical_normalize
from syllabifier  import parse_phones, syllabify, word_gate, GATE_ICON
from licensing    import license_phone
from mabni_layer         import process_mabni, MabniBoundary, MabniOpen, MabniBlocked
from mabniyat_attachment import recognize_token
from pipeline.word_class import classify_word_class, WordClassRequest
from pipeline.word_class.models import WordClass, WordClassVerdict
from pipeline.word_class.catalog import extract_mabni_id_from_notes

W = 80

STAGE_WIDTH = 22


# ══════════════════════════════════════════════════════════════════════════════
# الحكم الكامل على كلمة واحدة
# ══════════════════════════════════════════════════════════════════════════════

def hokom(word: str) -> dict:
    """
    أجرِ جميع المراحل على كلمة واحدة.
    أعِد dict شامل بنتيجة كل مرحلة.

    نموذج التمثيل الرباعي:
      input_surface      — الرمز كما وصل (ثابت)
      canonical_surface  — الهوية المعجمية (= input_surface حاليًا)
      normalized_surface — الشكل الداخلي (بعد normalize(): شدة + همزة)
      structural_encoding — أنماط الـ slots (CVC | CV | …)
    """
    # ── التمثيل الرباعي ───────────────────────────────────────────────────────
    input_surface      = word
    canonical_surface  = word                  # سياسة محافظة: لا تعديل على الهوية
    normalized_surface = normalize(word)       # for phonological pipeline (syllabifier, phones)

    # ── P0: Clitic Segmentation (HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01) ────
    # Runs immediately after normalization, before all downstream stages.
    # Produces SegmentBundle; segment_host is passed where the full token
    # was previously used for root/word-class input.
    #
    # WIRING FIX (HOKOM-CONSTITUTIONAL-AMENDMENT-02):
    #   The segmenter requires canonical_normalize() — NOT normalize().
    #   normalize() expands shadda (شَّ→شْشَ) and madda (آ→ءَا), corrupting
    #   segmenter input. canonical_normalize() preserves shadda and applies
    #   only hamza/alef normalizations the segmenter expects.
    _seg_normalized_surface = canonical_normalize(word)   # segmenter input only

    segment_bundle = None
    segment_host   = None   # None until set by segmenter; NEVER defaults to full token
    segment_proclitics = ()
    segment_enclitics  = ()
    segment_clitic_only = False
    _seg_failure_reason = None
    try:
        from pipeline.p0_segmentation import segment_token, SegmentationRequest
        _seg_req = SegmentationRequest(
            request_id=f'hokom:{input_surface}',
            original_surface=input_surface,
            normalized_surface=_seg_normalized_surface,  # canonical form for segmenter
        )
        segment_bundle = segment_token(_seg_req)
        segment_host        = segment_bundle.host  # None for clitic-only; NEVER falls back to full token
        segment_proclitics  = segment_bundle.proclitics
        segment_enclitics   = segment_bundle.enclitics
        segment_clitic_only = segment_bundle.clitic_only
    except Exception as _seg_exc:
        # Segmentation failure: fail-closed — morphology is not opened
        segment_bundle      = None
        segment_host        = None
        _seg_failure_reason = f'SEGMENTATION_ENGINE_FAILED:{type(_seg_exc).__name__}:{_seg_exc}'
        segment_proclitics  = ()
        segment_enclitics   = ()
        segment_clitic_only = False

    # ── Morphology Surface Gate ───────────────────────────────────────────────
    # segment_host is None for clitic-only constructions (بِكُمْ) or segmentation
    # failure. In either case morphology is NOT opened.
    if segment_host is None:
        morphology_surface = None
        morphology_blocked = True
        morphology_block_reason = (
            'SEGMENTATION_NO_LEXICAL_HOST'
            if (segment_bundle is not None and segment_bundle.clitic_only)
            else 'SEGMENTATION_FAILED'
        )
    else:
        # WIRING FIX (HOKOM-CONSTITUTIONAL-AMENDMENT-02):
        # segment_host is in canonical form (from canonical_normalize-based segmenter).
        # parse_phones() requires the expanded form: bare hamza (ء not أ/إ) and
        # expanded shadda (كَّ → كْكَ). Apply normalize() to the canonical host so
        # the phonological pipeline receives the form it expects.
        # segment_host (canonical) is returned in the result dict for callers.
        morphology_surface = normalize(segment_host)
        morphology_blocked = False
        morphology_block_reason = None

    # ── 2. Parse → phones ────────────────────────────────────────────────────
    # Phonological analysis runs on the morphological host (segment_host), not
    # the full token. When morphology is blocked, there is no host to analyse.
    phones      = parse_phones(morphology_surface) if morphology_surface else []
    real_phones = [p for p in phones if p.char != ' ']

    # ── 3-6. Licensing (بوابات الترخيص) ──────────────────────────────────────
    licensing_results = []
    licensing_blocked = []

    for p in real_phones:
        r = license_phone(p.char, p.diacritics)
        licensing_results.append(r)
        if not r['passed']:
            licensing_blocked.append(r['note'])

    # ── 7. Slot Engineering ───────────────────────────────────────────────────
    if licensing_blocked:
        return {
            'original':          word,
            'input_surface':     input_surface,
            'canonical_surface': canonical_surface,
            'normalized_surface': normalized_surface,
            'normalized':        normalized_surface,   # backward compat
            'stage':             'licensing',
            'licensing':         licensing_results,
            'slots':             [],
            'verdict':           'BLOCK',
            'violations':        licensing_blocked,
            # ── P0 Clitic Segmentation ───────────────────────────────────
            'segment_bundle':         segment_bundle,
            'segment_host':           segment_host,
            'segment_proclitics':     segment_proclitics,
            'segment_enclitics':      segment_enclitics,
            'segment_clitic_only':    segment_clitic_only,
            'morphology_surface':     morphology_surface,
            'morphology_blocked':     morphology_blocked,
            'morphology_block_reason': morphology_block_reason,
        }

    slots   = syllabify(phones)
    verdict, word_viols = word_gate(slots)

    # ── P5: Mabni Lookup ─────────────────────────────────────────────────────
    mabni = process_mabni(input_surface, normalized_surface, slots, verdict, word_viols)

    # ── P5.2: Attached Mabniyat Detection ────────────────────────────────────
    attachment = recognize_token(normalized_surface, verdict,
                                original_surface=input_surface) if isinstance(mabni, MabniOpen) else None

    # ── P5.3: Jamid Aalam Boundary (HOKOM-JAMID-AALAM-LEXICAL-BOUNDARY-CLOSURE-01) ─
    # Classify segment_host as JAMID_AALAM_BOUNDARY before root admission.
    # الله and its declined forms are MU'RAB (not mabni) — they MUST NOT enter
    # mabni_inventory. They are jawamid (اسم علم/اسم ذات) with no licensed root.
    # Lookup is on segment_host ONLY (after clitic stripping) — never original_surface.
    # If JAMID_AALAM_BOUNDARY: pre_root and root_candidate remain None.
    jamid_boundary  = None
    _is_jamid_aalam = False
    if isinstance(mabni, MabniOpen) and segment_host is not None:
        try:
            from pipeline.p5_lexical.jamid_aalam_boundary import (
                process_jamid_aalam,
                JamidAalamBoundary as _JamidAalamBoundary,
            )
            jamid_boundary  = process_jamid_aalam(segment_host)
            _is_jamid_aalam = isinstance(jamid_boundary, _JamidAalamBoundary)
        except Exception:
            jamid_boundary  = None
            _is_jamid_aalam = False

    # ── P5.4: Functional Lexical Lookup (HOKOM-MABNI-FUNCTIONAL-CATALOG-OWNERSHIP-01) ─
    # Resolves segment_host against the unified functional catalog BEFORE root
    # admission. Handles three cases:
    #
    #   OPERATOR_BOUNDARY  — segment_host is a known operator; root path closed.
    #   MABNI_BOUNDARY     — segment_host is a known ISM mabni; root path closed.
    #   FUNCTIONAL_AMBIGUITY — bare collision; root path still closed (no silent pick).
    #
    # Monotonic routing: skipped if JAMID_AALAM_BOUNDARY or MabniBoundary already
    # delivered a definitive verdict.  Does NOT skip for OPERATOR_BOUNDARY from
    # mabni_inventory (some question words carry is_operator=True there but are
    # grammatically ISM mabni — the functional lookup corrects the label).
    #
    # Proclitic-compound rule: when segment_proclitics is non-empty AND the functional
    # lookup on segment_host finds any result (MABNI or OPERATOR), the overall token
    # routing is OPERATOR_BOUNDARY (the proclitic heads the compound as a preposition).
    # This handles بِمَا (segment_host='مَا' → MABNI, but بِ makes it preposition-compound).
    _functional_result      = None
    _functional_owner       = None           # OPERATOR_BOUNDARY | MABNI_BOUNDARY | None
    _functional_collision   = False
    _functional_match_type  = None

    # Only skip functional lookup for JAMID_AALAM (already authoritatively closed).
    # MabniBlocked means the phonological slot pattern is invalid for mabni classification,
    # but the token may still be a known functional word in the catalog (e.g. أَيّ whose
    # shadda normalization yields an unrecognised slot string).  We still run the catalog
    # lookup for MabniBlocked tokens so the functional owner can be set correctly.
    _already_closed = _is_jamid_aalam
    if not _already_closed and segment_host is not None and not morphology_blocked:
        try:
            from pipeline.p5_lexical.functional_lexical_lookup import (
                lookup as _fl_lookup,
            )
            _fl_host = segment_host   # lookup on segment_host ONLY (after clitic strip)
            _functional_result = _fl_lookup(_fl_host)

            if _functional_result is not None:
                if _functional_result.collision:
                    # Collision: ambiguity confirmed — root still closed, no silent pick
                    _functional_owner     = None
                    _functional_collision = True
                else:
                    _functional_owner     = _functional_result.owner
                    _functional_collision = False
                    # Proclitic-compound rule: any token with operator proclitics
                    # (بِ, لِ, فَ, وَ, كَ) and a functional host → OPERATOR_BOUNDARY
                    if segment_proclitics and _functional_owner is not None:
                        _functional_owner = 'OPERATOR_BOUNDARY'
                _functional_match_type = _functional_result.match_type
        except Exception:
            _functional_result     = None
            _functional_owner      = None
            _functional_collision  = False

    # ── Route override for MabniBoundary tokens ────────────────────────────────
    # For tokens already caught by mabni_inventory (e.g. مَنْ as OPERATOR_BOUNDARY),
    # the functional lookup may correct the owner to MABNI_BOUNDARY.  Store the
    # corrected label in _functional_owner so the result dict reflects the right owner.
    # The root path is already closed by MabniBoundary; this is label-only correction.
    if isinstance(mabni, MabniBoundary) and _functional_owner is not None:
        pass   # _functional_owner already set; MabniBoundary keeps root closed

    # ── Pre-Root Decision (طبقة ما قبل الجذر) ────────────────────────────────
    # تُشغَّل بعد P5 فقط عند MabniOpen — تُقرِّر ما إذا كان مسار الجذر مفتوحًا.
    # تُعيد PreRootDecision أو None عند الفشل.
    # JAMID_AALAM_BOUNDARY: root admission is closed — skip pre_root entirely.
    # FUNCTIONAL_LOOKUP: OPERATOR_BOUNDARY or MABNI_BOUNDARY → root admission closed.
    pre_root = None
    if not morphology_blocked and isinstance(mabni, MabniOpen) and not _is_jamid_aalam:
        _seg_v   = attachment.segmentation_verdict if attachment else None
        _route_v = attachment.host_route           if attachment else None

        # ── Functional lookup override: close root if functional word found ───
        if _functional_owner in ('OPERATOR_BOUNDARY', 'MABNI_BOUNDARY'):
            pre_root = None     # Functional boundary: root path closed
        elif _functional_collision:
            pre_root = None     # Collision: root must not open under ambiguity
        # ── Existing routing from attachment ──────────────────────────────────
        # وضع MABNI_BOUNDARY المستقل (هِيَ، هُوَ، ...): المضيف نفسه مبني —
        # التحليل ذهب إلى DAL، لا حاجة لطبقة ما قبل الجذر.
        elif _seg_v == 'NOT_SEGMENTED' and _route_v == 'MABNI_BOUNDARY':
            pre_root = None
        elif _route_v == 'OPERATOR_BOUNDARY':
            # Operator host: root admission is closed. The host after proclitic
            # stripping is itself a mabni operator (e.g. لَيْسَ after فَ).
            # Opening root analysis here would be a routing violation.
            pre_root = None
        else:
            # P5 المُجزَّأ: أرسل المضيف المتبقي (لا السطح الأصلي الكامل) إلى Pre-Root.
            # تَرَكَتْهُمْ: P5 يُعطي host='تَرَكَتْ' → Pre-Root يحلل 'تَرَكَتْ'.
            # بدون هذا: Pre-Root يحلل 'تَرَكَتْهُمْ' (خطأ — الهاء+الميم ليست جذرًا).
            _p5_host = (
                attachment.host_surface
                if attachment and _seg_v == 'SEGMENTED' and attachment.host_surface
                else input_surface
            )
            # Fix 4: Restore lemma vowel after WAW_AL_JAMAA stripping.
            # When واو الجماعة is stripped from a past-tense verb (فَقَدُوهُ → فَقَدُ),
            # the host retains the damma from the plural paradigm. Restore to fatha
            # so the morphology classifier recognises the verbal form, not nominal.
            if (attachment and _seg_v == 'SEGMENTED' and _p5_host
                    and _p5_host.endswith('ُ')):   # ends in damma (ُ)
                _waw_stripped = any(
                    sp.mabni_id == 'ATTACHED_PRONOUN_WAW_AL_JAMAA'
                    for sp in attachment.attached_mabniyat
                )
                if _waw_stripped:
                    _p5_host = _p5_host[:-1] + 'َ'   # replace damma → fatha
            try:
                from pipeline.pre_root.pre_root_decision import assess_pre_root
                pre_root = assess_pre_root(_p5_host, p4_verdict=verdict)
            except Exception:
                pre_root = None

    # ── Root Host Refinement (تنقية المضيف الطرفية) ──────────────────────────
    # تُشغَّل بين PreRoot والمحرك المحلي عند OPEN/DEFER — تُزيل اللواحق الطرفية
    # اليقينية (تاء التأنيث الماضية، التاء المربوطة).
    # لا ترفع DEFER، ولا تعمل عند BLOCK.
    root_refinement = None
    if pre_root is not None and pre_root.root_path_directive in ('OPEN', 'DEFER'):
        try:
            from pipeline.p2_projection.root_host_refinement import refine_root_host
            root_refinement = refine_root_host(
                pre_root.host_surface,
                morphology_path    = pre_root.morphology_path.value,
                pre_root_directive = pre_root.root_path_directive,
            )
        except Exception:
            root_refinement = None

    # ── P3 RootCandidate — المحرك المحلي (HOKOM_ROOT_ENGINE) ─────────────────
    # يستبدل HR2S بالكامل. يُستدعى عند OPEN فقط بالمضيف المنقَّح.
    # BLOCK/DEFER من PreRoot → not_opened مباشرة بلا استدعاء المحرك.
    root_projection   = None
    root_candidate    = None
    augmented_analysis = None   # AugmentedRootAnalysis | None
    if pre_root is not None:
        try:
            from pipeline.p2_projection.root_projection import RootProjection
            from pipeline.p3_candidate.root_candidate import RootCandidate
            from pipeline.p3_candidate.root_resolution_orchestrator import resolve_root_pipeline
            from pipeline.p2_augmented.augmented_host_refinement import analyze_augmented_host

            _directive = pre_root.root_path_directive

            if _directive == 'OPEN':
                # المضيف المنقَّح (بعد إزالة اللواحق الطرفية) هو المدخل للمحرك.
                _resolved_host = (
                    root_refinement.refined_host
                    if root_refinement is not None and root_refinement.directive == 'OPEN'
                    else pre_root.host_surface
                )

                # ── محاولة AugmentedHostRefinement أولاً ──────────────────────
                # يكتشف أفعال المزيد (Form II–X) ويستخلص الجذر الثلاثي مباشرةً.
                # إذا نجح → نتجاوز المحرك الثلاثي. وإلا → المسار الثلاثي كالمعتاد.
                augmented_analysis = analyze_augmented_host(
                    refined_host    = _resolved_host,
                    original_host   = pre_root.host_surface,
                    morphology_path = pre_root.morphology_path.value,
                    evidence_ids    = pre_root.evidence_ids,
                    trace_ids       = pre_root.trace_ids,
                )

                if augmented_analysis is not None:
                    # ── مسار فعل مزيد: بناء RootCandidate مباشرةً ──────────
                    import types as _types
                    _aug_profile = {
                        'source_engine': 'HOKOM_AUGMENTED_ENGINE',
                        'form_family':   augmented_analysis.form_family,
                        'trilateral_root': list(augmented_analysis.trilateral_root),
                        'confidence':    augmented_analysis.confidence,
                    }
                    _resolution_ns = _types.SimpleNamespace(
                        analyzed_host  = _resolved_host,
                        directive      = 'ACCEPT',
                        canonical_root = augmented_analysis.trilateral_root,
                        root_profile   = _aug_profile,
                        evidence_ids   = augmented_analysis.evidence_ids,
                        trace_ids      = augmented_analysis.trace_ids,
                        residual_codes = augmented_analysis.residual_codes,
                    )
                    root_projection = RootProjection.from_root_resolution(
                        _resolution_ns,
                        input_surface = pre_root.input_surface,
                    )
                    root_candidate = RootCandidate.from_projection(root_projection)

                else:
                    # ── المسار الثلاثي الأصلي ─────────────────────────────────
                    _rc_local = resolve_root_pipeline(
                        original_host      = pre_root.host_surface,
                        refined_host       = _resolved_host,
                        pre_root_directive = 'OPEN',
                        morphology_path    = pre_root.morphology_path.value,
                        evidence_ids       = pre_root.evidence_ids,
                        trace_ids          = pre_root.trace_ids,
                    )
                    # from_root_resolution يتوقع .analyzed_host (duck-typed).
                    # RootCandidate يحمل نفس المعلومات بـ host_surface.
                    import types as _types
                    _resolution_ns = _types.SimpleNamespace(
                        analyzed_host  = _resolved_host,
                        directive      = _rc_local.directive,
                        canonical_root = _rc_local.canonical_root,
                        root_profile   = _rc_local.root_profile,
                        evidence_ids   = _rc_local.evidence_ids,
                        trace_ids      = _rc_local.trace_ids,
                        residual_codes = _rc_local.residual_codes,
                    )
                    root_projection = RootProjection.from_root_resolution(
                        _resolution_ns,
                        input_surface = pre_root.input_surface,
                    )
                    root_candidate = RootCandidate.from_projection(root_projection)

            elif _directive in ('BLOCK', 'DEFER'):
                root_projection = RootProjection.not_opened(
                    input_surface = pre_root.input_surface,
                    analyzed_host = pre_root.host_surface,
                    directive     = _directive,
                    evidence_ids  = pre_root.evidence_ids,
                    trace_ids     = pre_root.trace_ids,
                )
                root_candidate = RootCandidate.from_projection(root_projection)

        except Exception:
            root_projection   = None
            root_candidate    = None
            augmented_analysis = None

    # ── Canonical Radical Accounting (HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01) ──
    # يُشغَّل بعد المحرك الثلاثي/المزيد الحالي ويعمل على segment_host مباشرةً.
    # يُصحِّح حالتين رئيسيتين لم يعالجهما المحرك الحالي:
    #   1. الفعل المضارع الثلاثي (يَكْتُبُ): البادئة يَ/تَ/نَ/أَ تُحتسب غلطًا حرفًا رابعًا.
    #   2. المضيف المُعرَّف بالسابقة (وَاسْتَشْهِدُوا): segment_host صحيح بينما
    #      pre_root.host_surface قد يحمل الواو بسبب مسار الربط.
    # إذا أنتج المحرك الحالي DEFER وأنتج CRA ACCEPT → أعِد بناء root_candidate.
    # لا يُلغي ACCEPT موجودًا. لا يُلغي حدًّا مغلقًا.
    cra_result = None
    if pre_root is not None and not morphology_blocked:
        try:
            from pipeline.p3_pre_root.canonical_radical_accounting import (
                process_canonical_radical_accounting as _cra_process,
            )
            cra_result = _cra_process(
                input_surface      = input_surface,
                segment_host       = segment_host,
                morphology_surface = morphology_surface,
                pre_root           = pre_root,
                route              = _route_v,
            )
            # تجاوز root_candidate فقط إذا نجح CRA حيث أخفق المحرك الحالي
            _rc_directive = getattr(root_candidate, 'directive', None)
            if (cra_result.directive == 'ACCEPT'
                    and cra_result.candidate_radical_sequences
                    and _rc_directive in (None, 'DEFER')):
                import types as _cra_types
                _cra_root = tuple(cra_result.candidate_radical_sequences[0])
                _cra_profile = {
                    'source_engine': 'HOKOM_CRA_ENGINE',
                    'form_family':   cra_result.form_family or 'FORM_I',
                    'trilateral_root': list(_cra_root),
                    'confidence':    'HIGH',
                }
                _cra_res_ns = _cra_types.SimpleNamespace(
                    analyzed_host  = cra_result.canonical_stem,
                    directive      = 'ACCEPT',
                    canonical_root = _cra_root,
                    root_profile   = _cra_profile,
                    evidence_ids   = tuple(cra_result.evidence),
                    trace_ids      = ('cra:canonical_radical_accounting',),
                    residual_codes = (),
                )
                from pipeline.p2_projection.root_projection import RootProjection as _CRAProj
                from pipeline.p3_candidate.root_candidate import RootCandidate as _CRACand
                _cra_proj     = _CRAProj.from_root_resolution(
                    _cra_res_ns,
                    input_surface = pre_root.input_surface,
                )
                root_candidate  = _CRACand.from_projection(_cra_proj)
                root_projection = _cra_proj
                # أعِد بناء augmented_analysis إذا كشف CRA صيغةً مزيدةً لم يكتشفها المحرك
                if (cra_result.augmented_detection is not None
                        and augmented_analysis is None):
                    _det = cra_result.augmented_detection
                    from pipeline.p2_augmented.models import AugmentedRootAnalysis as _CRAAUG
                    augmented_analysis = _CRAAUG(
                        form_family      = _det.form_family,
                        trilateral_root  = _cra_root,
                        past_surface     = cra_result.canonical_stem,
                        imperfect_prefix = _det.imperfect_prefix,
                        confidence       = _det.confidence_hint,
                        evidence_ids     = tuple(cra_result.evidence),
                        trace_ids        = ('cra:canonical_radical_accounting',),
                        residual_codes   = (),
                    )
        except Exception:
            cra_result = None

    # ── Phase 4A — WaznProjection عبر الأوركسترا ─────────────────────────────
    # يُستدعى دائمًا إن وُجد root_candidate — حتى BLOCK/DEFER (تُنتج NOT_OPENED).
    #
    # مسار قصير للأفعال المزيدة (Form II–X):
    #   إذا كان augmented_analysis موجودًا، فالوزن معروف مباشرة من عائلة الصيغة.
    #   نتجاوز WaznHypothesis ونبني Phase4AResult مباشرةً.
    phase4a_result = None
    if root_candidate is not None:
        try:
            if augmented_analysis is not None:
                # ── مسار فعل مزيد: الوزن معروف مباشرة ──────────────────────
                from pipeline.p4_wazn.augmented_wazn import build_augmented_phase4a
                phase4a_result = build_augmented_phase4a(
                    augmented_analysis,
                    root_candidate,
                    root_refinement=root_refinement,
                )
            else:
                # ── المسار الثلاثي الأصلي ────────────────────────────────────
                from pipeline.p4_wazn.phase4a_orchestrator import project_wazn_with_relicensing
                phase4a_result = project_wazn_with_relicensing(
                    root_candidate,
                    root_refinement=root_refinement,
                )
        except Exception:
            phase4a_result = None

    # ── Phase 4B — BabProjection ──────────────────────────────────────────────
    # Fix 5/6: Pass morphology_path so nominal words get NOT_APPLICABLE in Bab.
    phase4b_result = None
    if phase4a_result is not None and phase4a_result.final_directive == 'ACCEPT':
        try:
            from pipeline.p4_bab.phase4b_orchestrator import project_bab_with_licensing
            _morphology_path = (
                pre_root.morphology_path.value if pre_root is not None else None
            )
            phase4b_result = project_bab_with_licensing(
                phase4a_result,
                root_refinement=root_refinement,
                morphology_path=_morphology_path,
            )
        except Exception:
            phase4b_result = None

    # ── Phase 4C — MasdarProjection ───────────────────────────────────────────
    phase4c_result = None
    if phase4a_result is not None and phase4a_result.final_directive == 'ACCEPT':
        try:
            from pipeline.p4_masdar.phase4c_orchestrator import project_masdar_with_licensing
            phase4c_result = project_masdar_with_licensing(
                phase4a_result,
                phase4b_result=phase4b_result,
                root_refinement=root_refinement,
            )
        except Exception:
            phase4c_result = None

    # ── Phase 4D — MushtaqProjection ─────────────────────────────────────────
    phase4d_result = None
    if phase4a_result is not None and phase4a_result.final_directive == 'ACCEPT':
        try:
            from pipeline.p4_mushtaqat.phase4d_orchestrator import project_mushtaqat_with_licensing
            phase4d_result = project_mushtaqat_with_licensing(
                phase4a_result,
                phase4b_result=phase4b_result,
                phase4c_result=phase4c_result,
                root_refinement=root_refinement,
            )
        except Exception:
            phase4d_result = None

    # ── حقول الملخص ─────────────────────────────────────────────────────────
    # final_root: الجذر النهائي المُرخَّص
    _prc = getattr(phase4a_result, 'promoted_root_candidate', None) if phase4a_result else None
    _rc  = root_candidate
    if _prc is not None:
        _final_root = getattr(_prc, 'canonical_root', None)
    elif _rc is not None:
        _final_root = getattr(_rc, 'canonical_root', None)
    else:
        _final_root = None

    # final_wazn, final_form, final_masdar
    _final_wazn    = getattr(phase4a_result, 'final_wazn', None) if phase4a_result else None
    _final_form    = getattr(phase4b_result, 'final_bab',  None) if phase4b_result else None
    _final_masdar  = getattr(phase4c_result, 'final_masdar', None) if phase4c_result else None
    _final_masdar_pattern = getattr(phase4c_result, 'final_masdar_pattern', None) if phase4c_result else None

    # accepted_mushtaqat: tuple of (type, pattern) or {}
    _accepted_mushtaqat = getattr(phase4d_result, 'accepted_mushtaqat', ()) if phase4d_result else ()

    # active and resolved residuals
    _active_residuals   = _collect_active_residuals(phase4a_result, phase4b_result, phase4c_result, phase4d_result)
    _resolved_residuals = _collect_resolved_residuals(phase4a_result, phase4b_result)

    # ── Word Class Engine ─────────────────────────────────────────────────────
    # Canonical ISM / FI3L / HARF classification.
    # Must run BEFORE Phase 5 inflection so the gate can block non-FI3L tokens.
    # Word class uses morphology_surface (segment_host), not the full token.
    # When morphology is blocked (clitic-only or segmentation failure), skip.
    word_class_result = None
    if not morphology_blocked and morphology_surface:
        try:
            word_class_result = _run_word_class_engine(
                input_surface      = input_surface,
                normalized_surface = morphology_surface,
                mabni              = mabni,
                attachment         = attachment,
                pre_root           = pre_root,
                phase4a_result     = phase4a_result,
                phase4b_result     = phase4b_result,
                phase4c_result     = phase4c_result,
                phase4d_result     = phase4d_result,
                _final_form        = _final_form,
                _final_masdar      = _final_masdar,
                augmented_analysis = augmented_analysis,
            )
        except Exception:
            word_class_result = None

    # ── Phase 5 — Paradigm/Inflection ────────────────────────────────────────
    # B-01 fix: gate verbal inflection on confirmed FI3L word class.
    # Non-FI3L tokens (HARF, ISM, DEFERRED) do NOT open verbal inflection.
    phase5_result    = None
    inflectional_form = None
    _inflection_skipped_reason = None

    _is_confirmed_fi3l = (
        not morphology_blocked
        and word_class_result is not None
        and word_class_result.verdict == WordClassVerdict.ACCEPTED
        and word_class_result.word_class == WordClass.FI3L
    )

    if not _is_confirmed_fi3l:
        _inflection_skipped_reason = (
            morphology_block_reason
            if morphology_blocked
            else (
                word_class_result.verdict.value
                if word_class_result is not None
                else 'WORD_CLASS_NOT_AVAILABLE'
            )
        )
    else:
        try:
            from pipeline.p5_inflection.phase5_orchestrator import project_inflection_with_licensing
            # Phase 5 always analyses the full normalized surface for tense/PNG features.
            # Attached pronouns are detected separately inside the orchestrator via `attachment`.
            _p5_surface = normalized_surface
            _p5_morphpath = (
                pre_root.morphology_path.value if pre_root is not None else None
            )
            phase5_result = project_inflection_with_licensing(
                surface       = _p5_surface,
                root          = _final_root,
                bab_id        = _final_form,
                form_family   = getattr(augmented_analysis, 'form_family', None) if augmented_analysis else None,
                wazn_id       = _final_wazn,
                morphology_path = _p5_morphpath,
                phase4a_result  = phase4a_result,
                phase4b_result  = phase4b_result,
                attachment      = attachment,
            )
            inflectional_form = phase5_result.inflectional_form if phase5_result else None
        except Exception:
            phase5_result     = None
            inflectional_form = None

    # ── حقول الملخص Phase 5 ───────────────────────────────────────────────────
    _paradigm_id  = (phase5_result.paradigm_candidate.paradigm_id
                     if phase5_result and phase5_result.paradigm_candidate else None)
    _tense_aspect = inflectional_form.tense_aspect if inflectional_form else None
    _mood         = inflectional_form.mood         if inflectional_form else None
    _voice        = inflectional_form.voice        if inflectional_form else None
    _person       = inflectional_form.person       if inflectional_form else None
    _number       = inflectional_form.number       if inflectional_form else None
    _gender       = inflectional_form.gender       if inflectional_form else None
    _lemma_surface = inflectional_form.lemma_surface if inflectional_form else None

    # ── Taaqol Live Governance (HOKOM-TAAQOL-LIVE-INTEGRATION-01) ────────────
    # Build claim bundle from pipeline state and run strict Taaqol evaluation.
    # Fail-closed: any Taaqol runtime error → DEFERRED (never LICENSED).
    # No try/except here: evaluate_hokom_claim_bundle handles all failures internally.
    # ── Jamid Aalam summary fields ────────────────────────────────────────────
    _jamid_verdict   = getattr(jamid_boundary, 'verdict',        None) if _is_jamid_aalam else None
    _jamid_category  = getattr(jamid_boundary, 'jamid_category', None) if _is_jamid_aalam else None
    _aalam_category  = getattr(jamid_boundary, 'aalam_category', None) if _is_jamid_aalam else None

    _hokom_result_partial = {
        'original':            word,
        'input_surface':       input_surface,
        'canonical_surface':   canonical_surface,
        'normalized_surface':  normalized_surface,
        'normalized':          normalized_surface,
        'stage':               'slot_engineering',
        'licensing':           licensing_results,
        'slots':               slots,
        'verdict':             verdict,
        'violations':          word_viols,
        'mabni':               mabni,
        'attachment':          attachment,
        # ── Jamid Aalam Boundary ─────────────────────────────────────────
        'jamid_boundary':      jamid_boundary,
        'jamid_verdict':       _jamid_verdict,
        'jamid_category':      _jamid_category,
        'aalam_category':      _aalam_category,
        'pre_root':            pre_root,
        'cra_result':          cra_result,
        'root_refinement':     root_refinement,
        'augmented_analysis':  augmented_analysis,
        'root_projection':     root_projection,
        'root_candidate':      root_candidate,
        'phase4a_result':      phase4a_result,
        'phase4b_result':      phase4b_result,
        'phase4c_result':      phase4c_result,
        'phase4d_result':      phase4d_result,
        'phase5_result':       phase5_result,
        'inflectional_form':   inflectional_form,
        'final_root':          _final_root,
        'final_wazn':          _final_wazn,
        'final_form':          _final_form,
        'final_masdar':        _final_masdar,
        'final_masdar_pattern':_final_masdar_pattern,
        'accepted_mushtaqat':  _accepted_mushtaqat,
        'active_residuals':    _active_residuals,
        'resolved_residuals':  _resolved_residuals,
        'word_class_result':   word_class_result,
        # Segmentation boundary fields (HOKOM-TAAQOL-LIVE-INTEGRATION-01)
        'segment_bundle':         segment_bundle,
        'morphology_surface':     morphology_surface,
        'morphology_blocked':     morphology_blocked,
        'morphology_block_reason': morphology_block_reason,
        # RESUME: canonical SegmentBundle fields for bridge pass-through
        'segment_host':           segment_host,
        'segment_proclitics':     segment_proclitics,
        'segment_enclitics':      segment_enclitics,
        'segment_clitic_only':    segment_clitic_only,
        'segment_definite_article': (
            segment_bundle.definite_article if segment_bundle else None
        ),
        # Functional catalog ownership (for taaqol bridge pass-through)
        'functional_boundary_owner': _functional_owner,
        'functional_collision':      _functional_collision,
        '_route_v': (
            _functional_owner
            if _functional_owner is not None
            else (
                mabni.verdict
                if isinstance(mabni, MabniBoundary)
                else None
            )
        ),
    }
    _taaqol_decision = None
    _taaqol_effective_verdict = None
    _taaqol_runtime = None
    _taaqol_verdict = None  # None = runtime unavailable; semantic string = live evaluation
    try:
        from pipeline.taaqol_integration.claim_adapter import bundle_from_hokom_result
        from pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle
        _claim_bundle = bundle_from_hokom_result(_hokom_result_partial)
        _taaqol_decision = evaluate_hokom_claim_bundle(_claim_bundle)
        _taaqol_effective_verdict = _taaqol_decision.effective_verdict
        _taaqol_runtime = getattr(_taaqol_decision, 'taaqol_runtime', None)
        # taaqol_verdict is the semantic gate verdict ONLY when runtime executed successfully.
        # When runtime is unavailable (import/path failure), taaqol_verdict stays None
        # so callers can distinguish infrastructure failure from semantic DEFER/ACCEPT/BLOCK.
        if _taaqol_runtime is not None and _taaqol_runtime.get('active'):
            _taaqol_verdict = _taaqol_decision.taaqol_verdict
        # else: _taaqol_verdict remains None — runtime did not execute
    except Exception:
        # Integration not yet wired or unavailable — record None, do not raise.
        # This is NOT a silent fallback: taaqol_decision=None signals unavailable.
        pass

    return {
        'original':            word,
        'input_surface':       input_surface,
        'canonical_surface':   canonical_surface,
        'normalized_surface':  normalized_surface,
        'normalized':          normalized_surface,   # backward compat
        'stage':               'slot_engineering',
        'licensing':           licensing_results,
        'slots':               slots,
        'verdict':             verdict,
        'violations':          word_viols,
        'mabni':               mabni,
        'attachment':          attachment,
        # ── Jamid Aalam Boundary (HOKOM-JAMID-AALAM-LEXICAL-BOUNDARY-CLOSURE-01) ─
        'jamid_boundary':      jamid_boundary,
        'jamid_verdict':       _jamid_verdict,
        'jamid_category':      _jamid_category,
        'aalam_category':      _aalam_category,
        'pre_root':            pre_root,
        'cra_result':          cra_result,
        'root_refinement':     root_refinement,
        'augmented_analysis':  augmented_analysis,
        'root_projection':     root_projection,
        'root_candidate':      root_candidate,
        'phase4a_result':      phase4a_result,
        'phase4b_result':      phase4b_result,
        'phase4c_result':      phase4c_result,
        'phase4d_result':      phase4d_result,
        'phase5_result':       phase5_result,
        'inflectional_form':   inflectional_form,
        # ── حقول الملخص ──────────────────────────────────────────────────
        'final_root':              _final_root,
        'final_wazn':              _final_wazn,
        'final_form':              _final_form,
        'final_masdar':            _final_masdar,
        'final_masdar_pattern':    _final_masdar_pattern,
        'accepted_mushtaqat':      _accepted_mushtaqat,
        'active_residuals':        _active_residuals,
        'resolved_residuals':      _resolved_residuals,
        # ── حقول Phase 5 ──────────────────────────────────────────────────
        'paradigm_id':   _paradigm_id,
        'tense_aspect':  _tense_aspect,
        'mood':          _mood,
        'voice':         _voice,
        'person':        _person,
        'number':        _number,
        'gender':        _gender,
        'lemma_surface': _lemma_surface,
        # ── Word Class Engine (canonical ISM/FI3L/HARF) ───────────────────
        'word_class_result':           word_class_result,
        'word_class_verdict':          (word_class_result.verdict.value
                                        if word_class_result else None),
        'word_class':                  (word_class_result.word_class.value
                                        if word_class_result and word_class_result.word_class
                                        else None),
        'word_class_subclass':         (word_class_result.subclass.value
                                        if word_class_result and word_class_result.subclass
                                        else None),
        'inflection_skipped_reason':   _inflection_skipped_reason,
        # ── Taaqol Live Governance ────────────────────────────────────────
        'taaqol_decision':             _taaqol_decision,
        'taaqol_effective_verdict':    _taaqol_effective_verdict,
        'taaqol_verdict':              _taaqol_verdict,
        'taaqol_runtime':              _taaqol_runtime,
        'taaqol_center_scope':         (
            getattr(_taaqol_decision, 'taaqol_center_scope', None)
            if _taaqol_decision else None
        ),
        # ── P0 Clitic Segmentation (HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01) ─
        'segment_bundle':              segment_bundle,
        'segment_host':                segment_host,
        'segment_proclitics':          segment_proclitics,
        'segment_enclitics':           segment_enclitics,
        'segment_clitic_only':         segment_clitic_only,
        # ── Morphology Surface (what actually entered morphology) ─────────
        'morphology_surface':          morphology_surface,
        'morphology_blocked':          morphology_blocked,
        'morphology_block_reason':     morphology_block_reason,
        # ── Functional Catalog Ownership (HOKOM-MABNI-FUNCTIONAL-CATALOG-OWNERSHIP-01) ─
        # functional_boundary_owner: definitive owner after functional lookup.
        #   For MabniBoundary tokens the functional lookup may correct the label
        #   (e.g. مَنْ: mabni_inventory gives OPERATOR_BOUNDARY, functional gives MABNI_BOUNDARY).
        #   For MabniOpen tokens where functional lookup closed the root path,
        #   functional_boundary_owner records why root was closed.
        # _route_v: convenience field for canonical gate / downstream consumers.
        #   Priority: functional_boundary_owner > mabni.verdict (for MabniBoundary) > None.
        'functional_boundary_result':  _functional_result,
        'functional_boundary_owner':   _functional_owner,
        'functional_collision':        _functional_collision,
        '_route_v': (
            _functional_owner
            if _functional_owner is not None
            else (
                mabni.verdict
                if isinstance(mabni, MabniBoundary)
                else (
                    (attachment.host_route
                     if attachment and getattr(attachment, 'host_route', None)
                        in ('OPERATOR_BOUNDARY', 'MABNI_BOUNDARY')
                     else None)
                    if isinstance(mabni, MabniOpen)
                    else None
                )
            )
        ),
        # mabni_verdict: canonical verdict for downstream contracts and gate counters.
        # Alias of _route_v restricted to OPERATOR_BOUNDARY and MABNI_BOUNDARY only.
        # Priority: functional_boundary_owner (overrides operator-catalog verdict for
        # conditional and interrogative nouns) > mabni.verdict for MabniBoundary.
        'mabni_verdict': (
            _functional_owner
            if _functional_owner in ('OPERATOR_BOUNDARY', 'MABNI_BOUNDARY')
            else (
                mabni.verdict
                if isinstance(mabni, MabniBoundary)
                   and mabni.verdict in ('OPERATOR_BOUNDARY', 'MABNI_BOUNDARY')
                else None
            )
        ),
    }


def _run_word_class_engine(
    input_surface,
    normalized_surface,
    mabni,
    attachment,
    pre_root,
    phase4a_result,
    phase4b_result,
    phase4c_result,
    phase4d_result,
    _final_form,
    _final_masdar,
    augmented_analysis,
):
    """
    Build WordClassRequest from pipeline state and call classify_word_class().

    This is the single wiring point for the word class engine.
    It translates the hokom_pipeline internal state into the DTO contract.
    """
    # ── p5 fields ─────────────────────────────────────────────────────────────
    if isinstance(mabni, MabniBoundary):
        p5_verdict      = mabni.verdict          # OPERATOR_BOUNDARY | MABNI_BOUNDARY | OPERATOR_DEFERRED
        p5_lexical_class = mabni.lexical_class   # 'Closed Function Word' | 'Verbal Operator' | ...
        operator_status = any(getattr(e, 'is_operator', False) for e in (mabni.entries or []))
        mabni_status    = 'boundary'
    elif isinstance(mabni, MabniBlocked):
        p5_verdict       = 'BLOCK'
        p5_lexical_class = ''
        operator_status  = False
        mabni_status     = 'blocked'
    else:  # MabniOpen
        p5_verdict       = mabni.verdict  # 'OPEN'
        p5_lexical_class = ''
        operator_status  = False
        mabni_status     = 'open'

    # ── morphology path ────────────────────────────────────────────────────────
    morphology_path = ''
    if pre_root is not None:
        try:
            morphology_path = pre_root.morphology_path.value
        except AttributeError:
            morphology_path = str(getattr(pre_root, 'morphology_path', ''))

    # ── masdar evidence ────────────────────────────────────────────────────────
    masdar_accepted = False
    masdar_surface  = ''
    if phase4c_result is not None:
        _dir = getattr(phase4c_result, 'final_directive', '')
        if str(_dir).upper() == 'ACCEPT':
            masdar_accepted = True
            masdar_surface  = str(_final_masdar or '')

    # ── derivative evidence ────────────────────────────────────────────────────
    derivative_accepted = False
    derivative_type     = ''
    if phase4d_result is not None:
        _dir4d = str(getattr(phase4d_result, 'final_directive', '')).upper()
        if _dir4d in ('ACCEPT', 'PARTIAL_ACCEPT'):
            _accepted_mushtaqat = getattr(phase4d_result, 'accepted_mushtaqat', ()) or ()
            if _accepted_mushtaqat:
                derivative_accepted = True
                # first accepted type
                derivative_type = list(dict(_accepted_mushtaqat).keys())[0] if _accepted_mushtaqat else ''

    # ── verbal host evidence ───────────────────────────────────────────────────
    licensed_verbal_host = False
    bab_id               = ''
    form_family_val      = ''
    if phase4b_result is not None:
        _dir4b = str(getattr(phase4b_result, 'final_directive', '')).upper()
        if _dir4b == 'ACCEPT':
            licensed_verbal_host = True
            bab_id               = str(_final_form or '')
    if augmented_analysis is not None:
        form_family_val = str(getattr(augmented_analysis, 'form_family', '') or '')
        if form_family_val:
            licensed_verbal_host = True

    # ── attachment evidence ────────────────────────────────────────────────────
    attachment_route   = ''
    attachment_notes   = ''
    attachment_mabni_id = ''
    if attachment is not None:
        attachment_route = str(getattr(attachment, 'host_route', '') or '')
        attachment_notes = str(getattr(attachment, 'notes', '') or '')
        attachment_mabni_id = extract_mabni_id_from_notes(attachment_notes)
    elif isinstance(mabni, MabniBoundary) and mabni.verdict == 'MABNI_BOUNDARY':
        # Commit 3: tokens caught directly by mabni_inventory (e.g. هُوَ, الَّذِي)
        # do not produce an attachment record.  Synthesise attachment_route so
        # word class engine STEP 5 can still classify them as ISM (PRONOUN, etc.).
        attachment_route = 'MABNI_BOUNDARY'
        if mabni.entries:
            from pipeline.word_class.catalog import mabni_id_for_vocalized as _mid_lookup
            attachment_mabni_id = _mid_lookup(mabni.entries[0].surface_vocalized)

    # ── available evidence summary (includes phase4a) ─────────────────────────
    avail = []
    # Include phase4a acceptance: needed for FI3L on ambiguous_morphology_path
    if phase4a_result is not None:
        _dir4a = str(getattr(phase4a_result, 'final_directive', '')).upper()
        if _dir4a == 'ACCEPT':
            _wazn4a = str(getattr(phase4a_result, 'final_wazn', '') or '')
            avail.append(f'p4a:accept:{_wazn4a}' if _wazn4a else 'p4a:accept')
    if licensed_verbal_host:
        avail.append('bab:accept')
    upstream_verdicts = tuple(avail)

    # ── Build request ──────────────────────────────────────────────────────────
    request = WordClassRequest(
        request_id           = _uuid.uuid4().hex[:12],
        original_surface     = input_surface,
        normalized_surface   = normalized_surface,
        p5_verdict           = p5_verdict,
        p5_lexical_class     = p5_lexical_class,
        operator_status      = operator_status,
        mabni_status         = mabni_status,
        morphology_path      = morphology_path,
        masdar_accepted      = masdar_accepted,
        masdar_surface       = masdar_surface,
        derivative_accepted  = derivative_accepted,
        derivative_type      = derivative_type,
        licensed_verbal_host = licensed_verbal_host,
        bab_id               = bab_id,
        form_family          = form_family_val,
        attachment_route     = attachment_route,
        attachment_notes     = attachment_notes,
        attachment_mabni_id  = attachment_mabni_id,
        available_evidence   = tuple(avail),
        upstream_verdicts    = upstream_verdicts,
        upstream_trace       = (),
    )

    return classify_word_class(request)


def _collect_active_residuals(
    phase4a_result=None,
    phase4b_result=None,
    phase4c_result=None,
    phase4d_result=None,
) -> tuple:
    """
    اجمع الرموز التحفظية النشطة (غير المحلولة) من جميع مراحل Phase 4.

    الرموز المحلولة (resolved) تُستبعَد:
      - defer:root:quadriliteral_beyond_scope → يُحلَّل عند relicensing ACCEPT.
    """
    all_res: list = []

    for result in (phase4a_result, phase4b_result, phase4c_result, phase4d_result):
        if result is None:
            continue
        res = tuple(getattr(result, 'residual_codes', ()) or ())
        all_res.extend(res)

    # ازِل المكررات مع حفظ الترتيب
    seen: dict = {}
    for r in all_res:
        seen[r] = None

    return tuple(seen.keys())


def _collect_resolved_residuals(
    phase4a_result=None,
    phase4b_result=None,
) -> tuple:
    """
    اجمع الرموز التحفظية المحلولة — تلك التي أُنتِجت ثم حُلَّت بواسطة
    آليات لاحقة (مثل relicensing ACCEPT).

    حاليًا: defer:root:quadriliteral_beyond_scope يُعدّ محلولًا عند
    source_path='hypothesis_relicensed' و final_directive='ACCEPT'.
    """
    if phase4a_result is None:
        return ()

    source_path    = str(getattr(phase4a_result, 'source_path', '') or '')
    final_dir      = str(getattr(phase4a_result, 'final_directive', '') or '').upper()

    if source_path == 'hypothesis_relicensed' and final_dir == 'ACCEPT':
        return ('defer:root:quadriliteral_beyond_scope',)

    return ()


# ══════════════════════════════════════════════════════════════════════════════
# العرض
# ══════════════════════════════════════════════════════════════════════════════

def _display_pre_root_section(
    pre_root,
    root_projection=None,
    root_candidate=None,
    root_refinement=None,
    phase4a_result=None,
    phase4b_result=None,
    phase4c_result=None,
    phase4d_result=None,
    phase5_result=None,
    *,
    indent: str = '  ',
):
    """
    اعرض طبقة ما قبل الجذر (Pre-Root Decision) والمحرك المحلي،
    ثم P2 RootProjection وP3 RootCandidate وPhase4A/B/C/D.

    يُستدعى بعد عرض P5 في كل من display() و display_verbose().
    """
    p = pre_root
    i = indent

    # ── رأس الطبقة ─────────────────────────────────────────────────────────
    print(f"\n{i}[Pre-Root Decision]")

    # أداة التعريف
    if p.prefixes:
        for pref in p.prefixes:
            pref_type = 'شمسية' if 'solar' in pref.notes else 'قمرية'
            print(f"{i}  prefix              : {pref.surface!r} → {pref.role.value}  ({pref_type})")
    else:
        print(f"{i}  prefix              : (none)")

    print(f"{i}  host                : {p.host_surface!r}")
    print(f"{i}  boundary            : {p.lexical_boundary}")
    print(f"{i}  morphology_path     : {p.morphology_path.value}")
    print(f"{i}  structural_verdict  : {p.structural_verdict}")

    # اللواحق (المشغّل المركب)
    if p.suffixes:
        for suf in p.suffixes:
            print(f"{i}  suffix              : {suf.surface!r} → {suf.role.value}")

    # التوجيه
    directive_icon = {'OPEN': '→', 'DEFER': '◌', 'BLOCK': '✗'}.get(p.root_path_directive, '?')
    print(f"{i}  route               : {p.routing.route}")
    print(f"{i}  root_path_directive : {directive_icon} {p.root_path_directive}")
    print(f"{i}  next_stage          : {p.next_stage}")

    # رموز التحفظ
    if p.residual_codes:
        for rc in p.residual_codes:
            print(f"{i}  residual            : {rc}")

    # ── Root Host Refinement ────────────────────────────────────────────────
    if root_refinement is not None:
        rr = root_refinement
        print(f"\n{i}[Root Host Refinement]")
        print(f"{i}  input_host       : {rr.input_host!r}")
        if rr.removed_suffixes and rr.refined_host != rr.input_host:
            removed_surface = rr.input_host[len(rr.refined_host):]
            print(f"{i}  refined_host     : {rr.refined_host!r}")
            for suf in rr.removed_suffixes:
                print(f"{i}  removed_suffix   : {suf}  ({removed_surface})")
            for ev in rr.evidence_ids:
                if ev not in ('no_terminal_suffix_to_refine',):
                    print(f"{i}  evidence         : {ev}")
        else:
            print(f"{i}  refined_host     : {rr.refined_host!r}  ← (no change)")
        for rc in rr.residual_codes:
            print(f"{i}  residual         : {rc}")

    # ── P2 RootProjection (initial) ─────────────────────────────────────────
    # Fix 12: P2/P3 displayed BEFORE Phase4A (correct architectural order).
    # Add '(initial — superseded by relicensing)' note when Phase4A promotes.
    _has_promoted = (
        phase4a_result is not None
        and getattr(phase4a_result, 'promoted_root_candidate', None) is not None
    )
    if root_projection is not None:
        rp = root_projection
        dir_icon = {'ACCEPT': '✓', 'DEFER': '◌', 'BLOCK': '✗'}.get(rp.directive, '?')
        _initial_note = '  (initial — superseded by relicensing)' if _has_promoted else ''
        print(f"\n{i}[P2 RootProjection]{_initial_note}")
        print(f"{i}  analyzed_host       : {rp.analyzed_host!r}")
        print(f"{i}  directive           : {dir_icon} {rp.directive}")
        print(f"{i}  stage_state         : {rp.stage_state}")
        if rp.canonical_root:
            root_str = '، '.join(str(r) for r in rp.canonical_root)
            print(f"{i}  canonical_root      : ({root_str})")
        else:
            print(f"{i}  canonical_root      : None")
        if rp.unresolved_positions:
            print(f"{i}  unresolved          : {', '.join(rp.unresolved_positions)}")
        if rp.root_profile:
            for k, v in list(rp.root_profile.items())[:3]:   # أهم 3 حقول فقط
                print(f"{i}  profile.{k:<12}: {v}")
        if rp.residual_codes:
            for rc in rp.residual_codes:
                print(f"{i}  residual            : {rc}")
        # Fix 1: Translate legacy source_engine name for display.
        _se = rp.source_engine
        if _se == 'hr2s_morphology':
            _se = 'HOKOM_BOUNDARY'
        print(f"{i}  source_engine       : {_se}")

    # ── P3 RootCandidate (initial) ──────────────────────────────────────────
    if root_candidate is not None:
        rc = root_candidate
        dir_icon = {'ACCEPT': '✓', 'DEFER': '◌', 'BLOCK': '✗'}.get(rc.directive, '?')
        _initial_note = '  (initial — superseded by relicensing)' if _has_promoted else ''
        print(f"\n{i}[P3 RootCandidate]{_initial_note}")
        print(f"{i}  directive           : {dir_icon} {rc.directive}")
        if rc.canonical_root:
            root_str = '، '.join(str(r) for r in rc.canonical_root)
            print(f"{i}  canonical_root      : ({root_str})")
        else:
            print(f"{i}  canonical_root      : None")
        if rc.residual_codes:
            for code in rc.residual_codes:
                print(f"{i}  residual            : {code}")

    # ── Phase 4A WaznProjection ─────────────────────────────────────────────
    if phase4a_result is not None:
        p4 = phase4a_result
        dir_icon = {'ACCEPT': '✓', 'DEFER': '◌', 'BLOCK': '✗'}.get(p4.final_directive, '?')
        print(f"\n{i}[Phase 4A — WaznProjection & Relicensing]")
        print(f"{i}  final_directive     : {dir_icon} {p4.final_directive}")
        print(f"{i}  source_path         : {p4.source_path}")
        if p4.final_wazn:
            print(f"{i}  wazn                : {p4.final_wazn}")
        wp = p4.wazn_projection
        if wp is not None and wp.selected_wazn is not None:
            print(f"{i}  wazn_pattern        : {wp.selected_wazn.wazn_pattern}")
            root_str = '، '.join(str(r) for r in (wp.canonical_root or ()))
            if root_str:
                print(f"{i}  canonical_root      : ({root_str})")
        if wp is not None and wp.residual_codes:
            for code in wp.residual_codes:
                print(f"{i}  residual            : {code}")
        # Fix 7: Display final promoted root after relicensing.
        if p4.promoted_root_candidate is not None:
            prc = p4.promoted_root_candidate
            print(f"\n{i}[Final Root — After Relicensing]")
            if prc.canonical_root:
                root_str = '، '.join(str(r) for r in prc.canonical_root)
                print(f"{i}  canonical_root      : ({root_str})")
            print(f"{i}  source              : ROOT_RELICENSING")
            print(f"{i}  directive           : ACCEPT")

    # ── Phase 4B BabProjection ──────────────────────────────────────────────
    if phase4b_result is not None:
        p4b = phase4b_result
        dir_icon = {
            'ACCEPT': '✓', 'DEFER': '◌', 'BLOCK': '✗',
            'NOT_OPENED': '—', 'NOT_APPLICABLE': '∅',
        }.get(p4b.final_directive, '?')
        print(f"\n{i}[Phase 4B — BabProjection]")
        print(f"{i}  final_directive     : {dir_icon} {p4b.final_directive}")
        if p4b.final_bab:
            print(f"{i}  selected_bab        : {p4b.final_bab}")
        print(f"{i}  source_path         : {p4b.source_path}")
        bp = p4b.bab_projection
        if bp is not None and bp.residual_codes:
            for code in bp.residual_codes:
                print(f"{i}  residual            : {code}")

    # ── Phase 4C MasdarProjection ───────────────────────────────────────────
    if phase4c_result is not None:
        p4c = phase4c_result
        dir_icon = {
            'ACCEPT': '✓', 'DEFER': '◌', 'BLOCK': '✗',
            'NOT_OPENED': '—', 'NOT_APPLICABLE': '∅',
        }.get(p4c.final_directive, '?')
        print(f"\n{i}[Phase 4C — MasdarProjection]")
        print(f"{i}  final_directive     : {dir_icon} {p4c.final_directive}")
        print(f"{i}  source_path         : {p4c.source_path}")
        if p4c.final_masdar:
            print(f"{i}  selected_masdar     : {p4c.final_masdar}")
        if p4c.final_masdar_pattern:
            print(f"{i}  masdar_pattern      : {p4c.final_masdar_pattern}")
        mp = p4c.masdar_projection
        if mp is not None and mp.source_type:
            print(f"{i}  source_type         : {mp.source_type}")
        if p4c.residual_codes:
            for code in p4c.residual_codes:
                print(f"{i}  residual            : {code}")

    # ── Phase 4D MushtaqProjection ──────────────────────────────────────────
    if phase4d_result is not None:
        p4d = phase4d_result
        _DIR_ICONS = {
            'ACCEPT': '✓', 'PARTIAL_ACCEPT': '◑',
            'DEFER': '◌', 'BLOCK': '✗',
            'NOT_OPENED': '—', 'NOT_APPLICABLE': '∅',
        }
        dir_icon = _DIR_ICONS.get(p4d.final_directive, '?')
        print(f"\n{i}[Phase 4D — MushtaqProjection]")
        print(f"{i}  final_directive  : {dir_icon} {p4d.final_directive}")
        mp4d = p4d.mushtaq_projection
        if mp4d is not None:
            accepted_dict = dict(mp4d.accepted_mushtaqat)
            type_order = [
                'ISM_FA3IL', 'ISM_MAF3UL', 'SIFA_MUSHABBAHA',
                'SIYAG_MUBALAGHAH', 'ISM_ZAMAN', 'ISM_MAKAN',
                'ISM_ALA', 'TAFDHIL',
            ]
            for mtype in type_order:
                if mtype in accepted_dict:
                    print(f"{i}  {mtype:<20}: ✓ {accepted_dict[mtype]}")
                elif mtype in mp4d.deferred_mushtaqat:
                    print(f"{i}  {mtype:<20}: ◌ DEFER")
                elif mtype in mp4d.blocked_mushtaqat:
                    print(f"{i}  {mtype:<20}: ✗ BLOCK")
                # NOT_APPLICABLE → silent (not printed)
            if mp4d.residual_codes:
                for code in mp4d.residual_codes:
                    print(f"{i}  residual         : {code}")

    # ── Phase 5 — Paradigm/Inflection ──────────────────────────────────────────
    if phase5_result is not None:
        p5 = phase5_result
        _dir5 = p5.final_directive
        _dir5_icon = {'ACCEPT': '✓', 'DEFER': '◌', 'BLOCK': '✗',
                      'NOT_APPLICABLE': '∅'}.get(_dir5, '?')
        print(f"\n{i}[Phase 5 — Inflection]")
        print(f"{i}  directive       : {_dir5_icon} {_dir5}")
        if p5.paradigm_candidate is not None:
            pc = p5.paradigm_candidate
            print(f"{i}  paradigm        : {pc.paradigm_id}")
        if p5.inflectional_form is not None:
            _if = p5.inflectional_form
            if _if.tense_aspect:
                print(f"{i}  tense           : {_if.tense_aspect}")
            if _if.mood:
                print(f"{i}  mood            : {_if.mood}")
            if _if.voice:
                print(f"{i}  voice           : {_if.voice}")
            if _if.person:
                print(f"{i}  person          : {_if.person}")
            if _if.number:
                print(f"{i}  number          : {_if.number}")
            if _if.gender:
                print(f"{i}  gender          : {_if.gender}")
            if _if.lemma_surface:
                print(f"{i}  lemma           : {_if.lemma_surface}")
        if p5.residual_codes:
            for code in p5.residual_codes:
                print(f"{i}  residual        : {code}")

    # ── ملخص نهائي (يُعرض فقط عند Phase4A ACCEPT) ───────────────────────────
    if (phase4a_result is not None
            and getattr(phase4a_result, 'final_directive', None) == 'ACCEPT'):
        print(f"\n{i}[Summary]")
        # الجذر النهائي
        _prc = getattr(phase4a_result, 'promoted_root_candidate', None)
        if _prc is not None:
            _root = getattr(_prc, 'canonical_root', None)
        elif root_candidate is not None:
            _root = getattr(root_candidate, 'canonical_root', None)
        else:
            _root = None
        if _root:
            root_str = ' '.join(str(c) for c in _root)
            print(f"{i}  final_root    : {root_str}")
        # الوزن
        _fwazn = getattr(phase4a_result, 'final_wazn', None)
        if _fwazn:
            wp = getattr(phase4a_result, 'wazn_projection', None)
            _wpat = None
            if wp is not None and getattr(wp, 'selected_wazn', None) is not None:
                _wpat = getattr(wp.selected_wazn, 'wazn_pattern', None)
            if _wpat:
                print(f"{i}  final_wazn    : {_fwazn}  ({_wpat})")
            else:
                print(f"{i}  final_wazn    : {_fwazn}")
        # الباب
        if phase4b_result is not None:
            _fbab = getattr(phase4b_result, 'final_bab', None)
            if _fbab:
                print(f"{i}  final_form    : {_fbab}")
        # المصدر
        if phase4c_result is not None:
            _fmasdar = getattr(phase4c_result, 'final_masdar', None)
            _fmpat   = getattr(phase4c_result, 'final_masdar_pattern', None)
            if _fmasdar:
                print(f"{i}  final_masdar  : {_fmasdar}")
            elif _fmpat:
                print(f"{i}  masdar_pattern: {_fmpat}")
        # المشتقات
        if phase4d_result is not None:
            _accepted = getattr(phase4d_result, 'accepted_mushtaqat', ())
            _adict    = dict(_accepted) if _accepted else {}
            for mtype in ('ISM_FA3IL', 'ISM_MAF3UL'):
                if mtype in _adict:
                    print(f"{i}  {mtype:<14}: {_adict[mtype]}")


def display(r: dict):
    input_surface      = r.get('input_surface',      r['original'])
    canonical_surface  = r.get('canonical_surface',  r['original'])
    normalized_surface = r.get('normalized_surface', r['normalized'])

    real_slots = [s for s in r.get('slots', []) if s['surface'] != ' ']
    syl_str    = ' | '.join(s['surface']  for s in real_slots)
    pat_str    = ' | '.join(s['pattern']  for s in real_slots)
    struct_enc = '.'.join(s['pattern']    for s in real_slots)

    cells   = ' '.join(lr['cell'] for lr in r.get('licensing', []))
    verdict = r['verdict']
    viols   = r.get('violations', [])
    mabni   = r.get('mabni')

    print()
    print('─' * W)
    # ── نموذج التمثيل الرباعي ─────────────────────────────────────────────────
    print(f"  Input Surface       : {input_surface}")
    print(f"  Canonical Surface   : {canonical_surface}")
    print(f"  Normalized Surface  : {normalized_surface}")
    if struct_enc:
        print(f"  Structural Encoding : {struct_enc}")
    if cells:
        print(f"  الخلايا (C/V) : {cells}")
    if syl_str:
        print(f"  التقطيع       : {syl_str}")

    # P4 — الحكم الهيكلي
    print(f"  [P4] Slot     : {GATE_ICON.get(verdict,'')} {verdict}")

    # P5 — بحسب نوع الحد
    if isinstance(mabni, MabniBoundary):
        rc = mabni.relation_contract
        sv_icon = '✓' if mabni.structural_verdict == 'ACCEPT' else '◌'
        print(f"  [P5] Operator Lookup:")
        print(f"       {mabni.verdict}")
        print(f"       operator_id         : {mabni.operator_id}")
        print(f"       lexical_family      : {mabni.lexical_family}")
        print(f"       structural_verdict  : {sv_icon} {mabni.structural_verdict}")
        print(f"       input_surface       : {mabni.input_surface}")
        print(f"       canonical_surface   : {mabni.canonical_surface}")
        print(f"       normalized_surface  : {mabni.normalized_surface}")
        print(f"       matched_surface     : {mabni.matched_surface}")
        print(f"       lexical_class       : {mabni.lexical_class}")
        print(f"       inventory_status    : {mabni.inventory_status}")
        print(f"       blocks_root_path    : {mabni.blocks_root_path}")
        print(f"       opens_relation      : {mabni.opens_relation}")
        print(f"       source              : {mabni.source}")
        print(f"  Relation Contract")
        print(f"       contract_id         : {rc.contract_id}")
        print(f"       contract_state      : {rc.contract_state}")
        print(f"  Structural Verdict  : {sv_icon} {mabni.structural_verdict}")
        lv_icon = '◈' if mabni.verdict == 'OPERATOR_BOUNDARY' else '◌'
        print(f"  Lexical Verdict     : {lv_icon} {mabni.verdict}")
        final = 'PENDING' if mabni.structural_verdict == 'ACCEPT' else 'DEFERRED'
        print(f"  Final Verdict       : {final}")
    elif isinstance(mabni, MabniOpen):
        attachment = r.get('attachment')
        _seg  = attachment.segmentation_verdict if attachment else None
        _route = attachment.host_route          if attachment else None
        if _seg == 'SEGMENTED':
            print(f"  [P5] Lexical  : COMPOSITE_BOUNDARY")
            print(f"  [P5.ATTACH]  segmentation=SEGMENTED  host={attachment.host_surface!r}  route={_route}")
            for sp in attachment.prefix_operators:
                print(f"  [P5.PREFIX]  {sp.surface_matched!r} → {sp.mabni_id}")
            for sp in attachment.attached_mabniyat:
                allomorph_note = f"  allomorph_of={sp.allomorph_of!r}" if sp.is_allomorph else ""
                print(f"  [P5.SUFFIX]  {sp.surface_matched!r} → {sp.mabni_id}{allomorph_note}")
        elif _seg == 'AMBIGUOUS':
            print(f"  [P5] Lexical  : → OPEN_TO_ROOT_ENGINE")
            print(f"  [P5.ATTACH]  segmentation=AMBIGUOUS  candidates={len(attachment.candidate_segmentations)}")
        elif _seg == 'NOT_SEGMENTED' and _route == 'MABNI_BOUNDARY':
            print(f"  [P5] Lexical  : MABNI_BOUNDARY (standalone — mabniyat catalog)")
            print(f"  [P5.ATTACH]  segmentation=NOT_SEGMENTED  host_route=MABNI_BOUNDARY")
        else:
            print(f"  [P5] Lexical  : → OPEN_TO_ROOT_ENGINE")
            print(f"  [P5.ATTACH]  segmentation=NOT_SEGMENTED")
        # ── طبقة ما قبل الجذر (الحكم الاعتمادي) ────────────────────────────
        pre_root = r.get('pre_root')
        if pre_root is not None:
            _display_pre_root_section(
                pre_root,
                r.get('root_projection'), r.get('root_candidate'),
                r.get('root_refinement'), r.get('phase4a_result'),
                r.get('phase4b_result'),
                r.get('phase4c_result'),
                r.get('phase4d_result'),
                r.get('phase5_result'),
            )
        else:
            # احتياط: لا Pre-Root — عرض المسار القديم
            if _seg == 'SEGMENTED':
                if _route == 'EMPTY':
                    print(f"  Next Stage          : NONE (token fully consumed by prefix+suffix)")
                    print(f"  Final Verdict       : COMPOSITE_CLOSED")
                else:
                    print(f"  Next Stage          : HOKOM_ROOT_ENGINE (residual_host={attachment.host_surface!r})")
                    print(f"  Final Verdict       : COMPOSITE_PENDING_HOKOM_ROOT_ENGINE")
            elif _seg == 'NOT_SEGMENTED' and _route == 'MABNI_BOUNDARY':
                print(f"  Next Stage          : DAL")
                print(f"  Final Verdict       : PENDING")
            else:
                print(f"  Next Stage          : HOKOM_ROOT_ENGINE")
                print(f"  Final Verdict       : PENDING_HOKOM_ROOT_ENGINE")
    elif isinstance(mabni, MabniBlocked):
        print(f"  [P5] Mabni    : ✗ BLOCK  {mabni.reason}")
        print(f"  Final Verdict       : BLOCK")

    if viols:
        print(f"  ⚠ تفاصيل:")
        for v in viols:
            print(f"     • {v}")
    print('─' * W)


def display_verbose(r: dict):
    """عرض تفصيلي يظهر كل بوابة على حدة."""
    input_surface      = r.get('input_surface',      r['original'])
    canonical_surface  = r.get('canonical_surface',  r['original'])
    normalized_surface = r.get('normalized_surface', r['normalized'])

    print()
    print('═' * W)
    print(f"  Input Surface       : {input_surface}")
    print(f"  Canonical Surface   : {canonical_surface}")
    print(f"  Normalized Surface  : {normalized_surface}")
    print('═' * W)

    if normalized_surface != input_surface:
        print(f"\n  [Normalization] {input_surface} → {normalized_surface}")

    # عرض الطبقات بأسمائها P0→P3
    for layer_id, layer_name in [('P0','Unicode Candidate'),
                                  ('P1','Character Licensing'),
                                  ('P2','Diacritic Licensing'),
                                  ('P3','Cell Construction')]:
        print(f"\n  [{layer_id}] {layer_name}:")
        for lr in r.get('licensing', []):
            gate = next((g for g in lr['gates'] if g.layer == layer_id), None)
            if gate is None: continue
            icon = '✓' if gate.passed else '✗'
            print(f"    {icon}  {lr['char']:3}  {gate.note}")

    real_slots = [s for s in r.get('slots', []) if s['surface'] != ' ']
    if real_slots:
        print(f"\n  [P4] Syllable Slot Engineering:")
        for i, s in enumerate(real_slots, 1):
            icon        = GATE_ICON.get(s['gate'], '')
            close_r     = s.get('close_reason', '')
            status      = s.get('status_at_close', '')
            sat_reason  = s.get('saturation_reason', '')
            print(f"    Slot{i}: {s['surface']:8} → {s['pattern']:6}  {icon} {s['gate']}")
            if close_r:
                print(f"             status  : {status}")
                if close_r == 'SATURATED':
                    print(f"             ↓ SATURATED")
                    if sat_reason:
                        print(f"             (reason: {sat_reason})")
                elif close_r == 'WORD_END':
                    print(f"             ↓ WORD_END")
                else:
                    print(f"             ↓ {close_r}")

    mabni = r.get('mabni')
    print(f"\n  [P5] Operator Lookup:")
    if isinstance(mabni, MabniBoundary):
        # function_candidates محفوظة داخليًا — P5 لا يُصدر حكمًا وظيفيًا
        rc = mabni.relation_contract
        sv_icon = '✓' if mabni.structural_verdict == 'ACCEPT' else '◌'
        lv_icon = '◈' if mabni.verdict == 'OPERATOR_BOUNDARY' else '◌'
        print(f"    {lv_icon} {mabni.verdict}")
        print(f"      operator_id         : {mabni.operator_id}")
        print(f"      lexical_family      : {mabni.lexical_family}")
        print(f"      structural_verdict  : {sv_icon} {mabni.structural_verdict}")
        print(f"      input_surface       : {mabni.input_surface}")
        print(f"      canonical_surface   : {mabni.canonical_surface}")
        print(f"      normalized_surface  : {mabni.normalized_surface}")
        print(f"      matched_surface     : {mabni.matched_surface}")
        print(f"      lexical_class       : {mabni.lexical_class}")
        print(f"      inventory_status    : {mabni.inventory_status}")
        print(f"      blocks_root_path    : {mabni.blocks_root_path}")
        print(f"      opens_relation      : {mabni.opens_relation}")
        print(f"      source              : {mabni.source}")
        print(f"    Relation Contract")
        print(f"      contract_id         : {rc.contract_id}")
        print(f"      contract_state      : {rc.contract_state}")
    elif isinstance(mabni, MabniOpen):
        attachment = r.get('attachment')
        _seg   = attachment.segmentation_verdict if attachment else None
        _route = attachment.host_route           if attachment else None
        print(f"      input_surface       : {mabni.input_surface}")
        print(f"      canonical_surface   : {mabni.canonical_surface}")
        print(f"      normalized_surface  : {mabni.normalized_surface}")
        if _seg == 'SEGMENTED':
            print(f"    → COMPOSITE_BOUNDARY  — attached mabni detected")
            print(f"    [P5.ATTACH]  segmentation=SEGMENTED  host={attachment.host_surface!r}  route={_route}")
            for sp in attachment.prefix_operators:
                print(f"    [P5.PREFIX]  {sp.surface_matched!r} → {sp.mabni_id}")
            for sp in attachment.attached_mabniyat:
                allomorph_note = f"  allomorph_of={sp.allomorph_of!r}" if sp.is_allomorph else ""
                print(f"    [P5.SUFFIX]  {sp.surface_matched!r} → {sp.mabni_id}{allomorph_note}")
        elif _seg == 'AMBIGUOUS':
            print(f"    → OPEN  — valid slots, not mabni → HOKOM_ROOT_ENGINE")
            print(f"    [P5.ATTACH]  segmentation=AMBIGUOUS  candidates={len(attachment.candidate_segmentations)}")
        elif _seg == 'NOT_SEGMENTED' and _route == 'MABNI_BOUNDARY':
            print(f"    → MABNI_BOUNDARY  — standalone mabni (mabniyat catalog)")
            print(f"    [P5.ATTACH]  segmentation=NOT_SEGMENTED  host_route=MABNI_BOUNDARY")
        else:
            print(f"    → OPEN  — valid slots, not mabni → HOKOM_ROOT_ENGINE")
            print(f"    [P5.ATTACH]  segmentation=NOT_SEGMENTED")
    elif isinstance(mabni, MabniBlocked):
        print(f"    ✗ BLOCK — {mabni.reason}")

    verdict = r['verdict']
    viols   = r.get('violations', [])

    # الحكم النهائي — بحسب نوع الحد
    print()
    if isinstance(mabni, MabniBoundary):
        sv_icon = '✓' if mabni.structural_verdict == 'ACCEPT' else '◌'
        lv_icon = '◈' if mabni.verdict == 'OPERATOR_BOUNDARY' else '◌'
        print(f"  Structural Verdict : {sv_icon} {mabni.structural_verdict}")
        print(f"  Lexical Verdict    : {lv_icon} {mabni.verdict}")
        final = 'PENDING' if mabni.structural_verdict == 'ACCEPT' else 'DEFERRED'
        print(f"  Final Verdict      : {final}")
    elif isinstance(mabni, MabniOpen):
        attachment = r.get('attachment')
        _seg   = attachment.segmentation_verdict if attachment else None
        _route = attachment.host_route           if attachment else None
        print(f"  Structural Verdict : ✓ ACCEPT")
        if _seg == 'SEGMENTED':
            print(f"  Lexical Verdict    : COMPOSITE_BOUNDARY")
            print(f"  Attachment Verdict : MABNI_ATTACHED")
        elif _seg == 'NOT_SEGMENTED' and _route == 'MABNI_BOUNDARY':
            print(f"  Lexical Verdict    : MABNI_BOUNDARY")
        else:
            print(f"  Lexical Verdict    : → OPEN_TO_ROOT_ENGINE")
        # ── طبقة ما قبل الجذر (الحكم الاعتمادي) ────────────────────────────
        pre_root = r.get('pre_root')
        if pre_root is not None:
            _display_pre_root_section(
                pre_root,
                r.get('root_projection'), r.get('root_candidate'),
                r.get('root_refinement'), r.get('phase4a_result'),
                r.get('phase4b_result'),
                r.get('phase4c_result'),
                r.get('phase4d_result'),
                r.get('phase5_result'),
                indent='  ',
            )
        else:
            # احتياط
            if _seg == 'SEGMENTED':
                if _route == 'EMPTY':
                    print(f"  Next Stage         : NONE (token fully consumed by prefix+suffix)")
                    print(f"  Final Verdict      : COMPOSITE_CLOSED")
                else:
                    print(f"  Next Stage         : HOKOM_ROOT_ENGINE  (residual_host={attachment.host_surface!r})")
                    print(f"  Final Verdict      : COMPOSITE_PENDING_HOKOM_ROOT_ENGINE")
            elif _seg == 'NOT_SEGMENTED' and _route == 'MABNI_BOUNDARY':
                print(f"  Next Stage         : DAL")
                print(f"  Final Verdict      : PENDING")
            else:
                print(f"  Next Stage         : HOKOM_ROOT_ENGINE  (surface={normalized_surface!r})")
                print(f"  Final Verdict      : PENDING_HOKOM_ROOT_ENGINE")
    elif isinstance(mabni, MabniBlocked):
        print(f"  Final Verdict      : BLOCK")
    else:
        print(f"  الحكم النهائي: {GATE_ICON.get(verdict,'')} {verdict}")
    if viols:
        for v in viols:
            print(f"    • {v}")
    print('═' * W)


# ══════════════════════════════════════════════════════════════════════════════
# Pipeline
# ══════════════════════════════════════════════════════════════════════════════

def run(text: str, verbose: bool = False):
    tokens = words_only(tokenize(text))
    for token in tokens:
        r = hokom(token.surface)
        if verbose:
            display_verbose(r)
        else:
            display(r)


# ══════════════════════════════════════════════════════════════════════════════
# تشغيل
# ══════════════════════════════════════════════════════════════════════════════

def main():
    verbose = '-v' in sys.argv
    args    = [a for a in sys.argv[1:] if a != '-v']

    print('\n' + '═' * W)
    print('  Hokom Pipeline  |  خط أنابيب الحكم')
    print('  token → normalize → license → cell → slot → gate')
    print('═' * W)

    # ── ملف نصي: python hokom_pipeline.py -f path/to/file.txt ────────────────
    if '-f' in sys.argv:
        idx = sys.argv.index('-f')
        if idx + 1 >= len(sys.argv):
            print('  ⚠ خطأ: يجب تحديد مسار الملف بعد -f')
            sys.exit(1)
        filepath = sys.argv[idx + 1]
        try:
            with open(filepath, encoding='utf-8') as fh:
                lines = [l.strip() for l in fh if l.strip()]
        except FileNotFoundError:
            print(f'  ⚠ الملف غير موجود: {filepath}')
            sys.exit(1)
        for i, line in enumerate(lines, 1):
            print(f'\n  ── سطر {i}/{len(lines)}: {line}')
            run(line, verbose=verbose)
        return

    # ── نص مباشر: python hokom_pipeline.py "النص هنا" ───────────────────────
    if args:
        run(' '.join(args), verbose=verbose)
        return

    # ── وضع تفاعلي ────────────────────────────────────────────────────────────
    while True:
        try:
            text = input('\n  أدخل نصًا (q للخروج): ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\n  وداعًا.')
            break
        if not text or text.lower() == 'q':
            break
        parts   = text.split()
        verbose = '-v' in parts
        words   = [p for p in parts if p != '-v']
        run(' '.join(words), verbose=verbose)


if __name__ == '__main__':
    main()
