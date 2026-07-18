#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sentence_pipeline.py — تقرير Qiyas بتنسيق المراحل الكاملة

الاستخدام:
  python sentence_pipeline.py "ضَرَبَ ضَارِبٌ مَضْرُوبًا"
  python sentence_pipeline.py -v "ضَرَبَ ضَارِبٌ مَضْرُوبًا"
"""

import sys
from tokenizer      import tokenize, words_only
from normalizer     import normalize
from syllabifier    import parse_phones, syllabify, word_gate
from licensing      import license_phone, LAYER_NAMES
from mabni_layer         import process_mabni, MabniBoundary, MabniOpen, MabniBlocked
from mabniyat_attachment import recognize_token

W  = 60
W2 = 60

def sep(char='─'): return char * W
def sep2(char='='): return char * W2


# ══════════════════════════════════════════════════════════════════════════════
# تقرير كلمة واحدة
# ══════════════════════════════════════════════════════════════════════════════

def report_word(surface: str, index: int, total: int, verbose: bool = False):

    # ── normalize ─────────────────────────────────────────────────────────────
    normalized  = normalize(surface)
    changed     = normalized != surface

    # ── licensing ─────────────────────────────────────────────────────────────
    phones      = parse_phones(normalized)
    real_phones = [p for p in phones if p.char != ' ']
    lic_results = [license_phone(p.char, p.diacritics) for p in real_phones]
    lic_blocked = [r for r in lic_results if not r['passed']]

    # ── slot engineering ──────────────────────────────────────────────────────
    slots              = syllabify(phones)
    slot_verdict, viols = word_gate(slots)
    real_slots         = [s for s in slots if s['surface'] != ' ']

    # ── mabni lookup ─────────────────────────────────────────────────────────
    mabni = process_mabni(normalized, normalized, slots, slot_verdict, viols)

    # ══ PRINT ════════════════════════════════════════════════════════════════
    print()
    print(sep2('='))
    print(f"  TOKEN: {surface}")
    print(sep2('='))

    # ── P0-P3: الترخيص ───────────────────────────────────────────────────────
    print()
    print(sep())
    print("  P0–P3  Licensing")
    print(sep())

    if changed:
        print(f"  [normalize]  {surface}  →  {normalized}")

    hamza_resolved = changed or any(
        c in 'أإؤئآ' for p in real_phones for c in p.char
    )
    # بعد التطبيع لا توجد همزة غير محلولة
    print(f"  [HAMZA]  {'RESOLVED' if True else 'UNRESOLVED'}"
          f"  (normalize_hamza active)")

    if lic_blocked:
        for r in lic_blocked:
            print(f"  [P0] BLOCK — {r['note']}")
    else:
        # عرض موجز P0→P3
        for lr in lic_results:
            g3 = next((g for g in lr['gates'] if g.layer == 'P3'), None)
            cell = lr['cell'] if g3 else '?'
            char_s = lr['char']
            print(f"  [P0→P3] ✓  {char_s}  → Cell={cell}")

    # ── P4: Slot Engineering ─────────────────────────────────────────────────
    print()
    print(sep())
    print("  P4  Slot Engineering  (DAL-A4)")
    print(sep())

    # A4 boundary
    if lic_blocked or slot_verdict == 'BLOCK':
        print(f"  [A4]  status=BLOCK  failure={'LICENSING_FAILED' if lic_blocked else 'INVALID_SLOTS'}")
    else:
        print(f"  [A4]  status=ACCEPT  boundaries=({len(real_slots)} slots)")
        for i, s in enumerate(real_slots, 1):
            icon = '✓' if s['gate'] == 'ACCEPT' else ('⏸' if s['gate'] == 'DEFER' else '✗')
            print(f"    [Slot{i}]  surface={s['surface']:8}  "
                  f"pattern={s['pattern']:6}  status={icon} {s['gate']}")

    # A5-A8: خارج نطاق P4 حاليًا
    if verbose:
        print(f"  [A5→A8]  status=PENDING  (not yet implemented in Qiyas)")

    # ── P5: Mabni Lookup ─────────────────────────────────────────────────────
    print()
    print(sep())
    print("  P5  Mabni / Operator Lookup")
    print(sep())

    if isinstance(mabni, MabniBoundary):
        print(f"  [P5]  status=MABNI  surface={normalized}")
        print(f"        category={mabni.category}")
        print(f"        source={mabni.source}")
        print(f"        blocks_root_path=True")
        print(f"  [BRIDGE]  → MabniBoundary — لا HR2S")

    elif isinstance(mabni, MabniOpen):
        patterns = ' | '.join(mabni.slot_patterns)
        print(f"  [P5]  status=OPEN  slots=[{patterns}]")

        # ── P5.2: Attached Mabniyat Detection ────────────────────────────────
        attachment = recognize_token(normalized, slot_verdict,
                                    original_surface=surface)
        _seg   = attachment.segmentation_verdict
        _route = attachment.host_route

        if _seg == 'SEGMENTED':
            print(f"  [P5.ATTACH]  segmentation=SEGMENTED  host={attachment.host_surface!r}  route={_route}")
            for sp in attachment.prefix_operators:
                print(f"  [P5.PREFIX]  {sp.surface_matched!r} → {sp.mabni_id}")
            for sp in attachment.attached_mabniyat:
                allomorph_note = f"  allomorph_of={sp.allomorph_of!r}" if sp.is_allomorph else ""
                print(f"  [P5.SUFFIX]  {sp.surface_matched!r} → {sp.mabni_id}{allomorph_note}")
            if _route == 'EMPTY':
                print(f"  [BRIDGE]  → COMPOSITE_CLOSED — token fully consumed by prefix+suffix")
            else:
                hr2s_surface = attachment.host_surface
                print(f"  [BRIDGE]  → COMPOSITE_BOUNDARY — residual host يكمل إلى HR2S")
                print()
                print(sep())
                print("  HR2S  H0 → H6  (pending)")
                print(sep())
                print(f"  [H0]  type=LicensedWordSurfaceBoundary  surface={hr2s_surface}")
                print(f"  [H1]  type=StructuralHypothesisSet  slot_shape=[{patterns}]")
                print(f"  [H2]  type=RootCandidate  status=PENDING")
                print(f"  [H3]  type=BabCandidate   status=PENDING")
                print(f"  [H4]  type=WaznCandidate  status=PENDING")
                print(f"  [H5]  type=DerivationCandidate  status=PENDING")
                print(f"  [H6]  type=StemCandidate  status=PENDING")
                print(f"  [BRIDGE]  HR2S not yet implemented in Qiyas")
        elif _seg == 'AMBIGUOUS':
            print(f"  [P5.ATTACH]  segmentation=AMBIGUOUS  candidates={len(attachment.candidate_segmentations)}")
            print(f"  [BRIDGE]  → OPEN — يكمل إلى HR2S")
            print()
            print(sep())
            print("  HR2S  H0 → H6  (pending)")
            print(sep())
            print(f"  [H0]  type=LicensedWordSurfaceBoundary  surface={normalized}")
            print(f"  [H1]  type=StructuralHypothesisSet  slot_shape=[{patterns}]")
            print(f"  [H2]  type=RootCandidate  status=PENDING")
            print(f"  [H3]  type=BabCandidate   status=PENDING")
            print(f"  [H4]  type=WaznCandidate  status=PENDING")
            print(f"  [H5]  type=DerivationCandidate  status=PENDING")
            print(f"  [H6]  type=StemCandidate  status=PENDING")
            print(f"  [BRIDGE]  HR2S not yet implemented in Qiyas")
        elif _seg == 'NOT_SEGMENTED' and _route == 'MABNI_BOUNDARY':
            print(f"  [P5.ATTACH]  segmentation=NOT_SEGMENTED  host_route=MABNI_BOUNDARY")
            print(f"  [BRIDGE]  → MABNI_BOUNDARY — standalone mabni، لا HR2S")
        else:
            print(f"  [P5.ATTACH]  segmentation=NOT_SEGMENTED")
            print(f"  [BRIDGE]  → OPEN — يكمل إلى HR2S")
            print()
            print(sep())
            print("  HR2S  H0 → H6  (pending)")
            print(sep())
            print(f"  [H0]  type=LicensedWordSurfaceBoundary  surface={normalized}")
            print(f"  [H1]  type=StructuralHypothesisSet  slot_shape=[{patterns}]")
            print(f"  [H2]  type=RootCandidate  status=PENDING")
            print(f"  [H3]  type=BabCandidate   status=PENDING")
            print(f"  [H4]  type=WaznCandidate  status=PENDING")
            print(f"  [H5]  type=DerivationCandidate  status=PENDING")
            print(f"  [H6]  type=StemCandidate  status=PENDING")
            print(f"  [BRIDGE]  HR2S not yet implemented in Qiyas")

    elif isinstance(mabni, MabniBlocked):
        print(f"  [P5]  status=BLOCK  reason={mabni.reason}")
        print(f"  [BRIDGE]  → BLOCKED — لا HR2S")


# ══════════════════════════════════════════════════════════════════════════════
# تقرير الجملة
# ══════════════════════════════════════════════════════════════════════════════

def sentence_pipeline(text: str, verbose: bool = False):
    tokens = words_only(tokenize(text))
    n      = len(tokens)

    print()
    print('█' * W)
    print(f"  SENTENCE PIPELINE  (Qiyas)")
    print(f"  Input: {text}")
    print('█' * W)

    for i, tok in enumerate(tokens, 1):
        print()
        print(f"▶▶▶  Word {i}/{n}: {tok.surface}")
        report_word(tok.surface, i, n, verbose=verbose)

    print()
    print('█' * W)
    print(f"  SENTENCE COMPLETE  ({n} tokens)")
    print('█' * W)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# تشغيل
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    args    = sys.argv[1:]
    verbose = '-v' in args
    args    = [a for a in args if a != '-v']

    text = ' '.join(args) if args else 'ضَرَبَ ضَارِبٌ مَضْرُوبًا'
    sentence_pipeline(text, verbose=verbose)
