#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_bab/bab_hypothesis.py — توليد مرشحي الباب
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

generate_bab_candidates() — المدخل الوحيد.

المنطق:
  1. إن كان wazn_family اسميًا → قائمة فارغة (NOT_APPLICABLE على مستوى أعلى)
  2. إن كان وزن مزيد فريد (FA33ALA، IFTA3ALA...) → مرشّح واحد HIGH
  3. إن كان مجردًا + imperfect_vowel → بحث في catalog بالحركتين → مرشّح واحد أو أكثر
  4. إن كان مجردًا + بلا imperfect_vowel → كل المرشحين الممكنين بـ DEFER_REQUIRED

اصطلاح imperfect_wazn:
  - حرف واحد 'a'/'i'/'u'
  - نمط وزن عربي مُشكَّل "يَفْعُلُ" (تُستخرج حركة ع)
  - None إن لم يُحدَّد

اصطلاح evidence_ids:
  - "imperfect_ayn:u" / "imperfect_ayn:i" / "imperfect_ayn:a" (مباشر)
  - "imperfect_ayn=u" (مضمَّن)
  - "paired:{x}:imperfect_ayn:{v}" (مُركَّب)
"""

from __future__ import annotations

from .bab_catalog import get_bab_catalog, lookup_by_wazn_id, lookup_by_vowels
from .bab_rules import (
    is_verbal_family,
    is_mazid_wazn,
    get_mazid_bab,
    normalize_imperfect_wazn,
    extract_imperfect_vowel_from_evidence,
    mujarrad_ambiguity_count,
)
from .models import BabCandidate


def generate_bab_candidates(
    past_wazn: str,
    imperfect_wazn: str | None,
    canonical_root: tuple[str, ...] | None,
    evidence_ids: tuple[str, ...],
    trace_ids: tuple[str, ...],
    wazn_family: str | None,
) -> list[BabCandidate]:
    """
    أنتِج قائمة BabCandidate بناءً على الوزن والدليل.

    past_wazn       : wazn_id من catalog (FA_A_LA | IFTA3ALA | ...)
    imperfect_wazn  : حركة ع ('a'/'i'/'u') أو نمط عربي أو None
    canonical_root  : الجذر الكنوني أو None
    evidence_ids    : شواهد (قد تحتوي imperfect_ayn:u...)
    trace_ids       : مسار
    wazn_family     : عائلة الوزن من wazn catalog (triliteral_bare_verb | form_*_verb | ...)

    الإرجاع: قائمة BabCandidate (فارغة → DEFER، أكثر من واحد → DEFER، واحد → ACCEPT ممكن)
    """
    # ── 1. أوزان اسمية → قائمة فارغة ────────────────────────────────────────
    if not is_verbal_family(wazn_family):
        return []

    # ── 2. حلّ حركة المضارع من المعاملات أو الشواهد ──────────────────────
    imperfect_vowel = normalize_imperfect_wazn(imperfect_wazn)
    if imperfect_vowel is None:
        imperfect_vowel = extract_imperfect_vowel_from_evidence(evidence_ids)

    # ── 3. المزيد الفريد ─────────────────────────────────────────────────────
    if is_mazid_wazn(past_wazn):
        bab_id = get_mazid_bab(past_wazn)
        if bab_id is None:
            return []

        # ابحث في catalog عن التعريف الكامل
        catalog_entries = lookup_by_wazn_id(past_wazn)
        if not catalog_entries:
            return []

        entry = catalog_entries[0]
        ev = evidence_ids + ('bab:mazid:wazn_unique_identification',)
        tr = trace_ids + ('p4b:mazid_direct',)

        return [BabCandidate(
            bab_id         = entry.bab_id,
            bab_family     = entry.family,
            past_wazn      = entry.past_wazn_id,
            imperfect_wazn = entry.imperfect_pattern if imperfect_vowel else None,
            confidence     = 'HIGH',
            evidence_ids   = ev,
            trace_ids      = tr,
            residual_codes = (),
        )]

    # ── 4. المجرد ─────────────────────────────────────────────────────────────
    ambiguity = mujarrad_ambiguity_count(past_wazn)
    if ambiguity == 0:
        # وزن ماضٍ غير موجود في catalog (قد يكون خطأ في المدخل أو وزن جديد)
        return []

    if imperfect_vowel is not None:
        # استخرج حركة ع الماضي من catalog entry
        past_entries = lookup_by_wazn_id(past_wazn)
        if not past_entries:
            return []
        past_ayn = past_entries[0].past_ayn_vowel

        # ابحث عن الباب المحدَّد بالحركتين
        matching = [
            e for e in past_entries
            if e.imperfect_ayn_vowel == imperfect_vowel
        ]

        if not matching:
            # الحركتان لا تطابقان أي باب → BLOCK (تناقض)
            tr = trace_ids + ('p4b:mujarrad:vowel_contradiction',)
            return [BabCandidate(
                bab_id         = 'CONTRADICTION',
                bab_family     = 'MUJARRAD',
                past_wazn      = past_wazn,
                imperfect_wazn = imperfect_wazn,
                confidence     = 'CONTRADICTION',
                evidence_ids   = evidence_ids,
                trace_ids      = tr,
                residual_codes = ('bab:mujarrad:imperfect_vowel_no_match',),
            )]

        # في العادة طابَق مرشّح واحد
        ev = evidence_ids + ('bab:mujarrad:paired_paradigm_resolved',)
        tr = trace_ids + ('p4b:mujarrad_paired',)

        return [BabCandidate(
            bab_id         = e.bab_id,
            bab_family     = e.family,
            past_wazn      = e.past_wazn_id,
            imperfect_wazn = e.imperfect_pattern,
            confidence     = 'HIGH',
            evidence_ids   = ev,
            trace_ids      = tr,
            residual_codes = (),
        ) for e in matching]

    else:
        # مجرد بلا دليل مضارع → كل المرشحين بـ DEFER_REQUIRED
        past_entries = lookup_by_wazn_id(past_wazn)
        tr = trace_ids + ('p4b:mujarrad_ambiguous',)
        ev = evidence_ids + ('bab:mujarrad:imperfect_required',)

        return [BabCandidate(
            bab_id         = e.bab_id,
            bab_family     = e.family,
            past_wazn      = e.past_wazn_id,
            imperfect_wazn = None,
            confidence     = 'DEFER_REQUIRED',
            evidence_ids   = ev,
            trace_ids      = tr,
            residual_codes = ('bab:mujarrad:imperfect_vowel_not_known',),
        ) for e in past_entries]
