#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p5_inflection/subject_agreement.py

HOKOM-SEQUENTIAL-3FS-RESOLUTION-AND-CANONICAL-ARTIFACT-REBASE-01

Sequential subject-agreement refinement for correlated 2MS/3FS ambiguity.

Ownership: sequential context layer — operates on pre-computed (surface, result)
pairs; does NOT call hokom() internally, does NOT modify hokom() internals.

Constitutional constraints:
  - Does NOT create FI3L or change word_class
  - Does NOT change root, form family, JAMID boundaries
  - Does NOT use token index, ayah number, or exact-token runtime lists
  - Does NOT force 3FS without subject evidence
  - Does NOT refine non-verbal or JAMID records
  - ONLY refines a record whose hokom() already returned a correlated
    ambiguity_candidates bundle containing a licensed 3FS candidate
"""
from __future__ import annotations

from typing import Sequence


def is_feminine_sg_subject_evidence(surface: str, r: dict) -> bool:
    """
    General feminine singular subject evidence detector.

    Returns True when the token provides morphological evidence for a
    feminine singular subject.  Uses four independent checks — no token
    lists, no index-based conditions.

    1. Explicit taa marbuta (ة) at the end of the stripped surface.
    2. Alif maqsura (ى) at the end — common in inherently-feminine nouns
       (إحدى, أنثى, كبرى, etc.).
    3. The pipeline already reported gender='F'.
    4. Alif-maqsura construct state before a pronoun enclitic:
       when إحدى (or similar) precedes هما/ها/… the ى becomes ا (alif)
       orthographically.  Detected as: ISM with a pronoun enclitic whose
       bare host ends in ا (≥3 letters).
    """
    from pipeline.p5_inflection.feature_system import strip_diacritics as _sd

    bare = _sd(surface)

    # 1. Explicit taa marbuta
    if bare.endswith('ة'):
        return True

    # 2. Alif maqsura (standalone)
    if bare.endswith('ى'):
        return True

    # 3. Pipeline-reported feminine gender
    if r.get('gender') == 'F':
        return True

    # 4. Alif-maqsura in construct state before a pronoun enclitic
    #    e.g. إحداهما (إحدى + هما), كلتاهما (كلتا + هما)
    enclitics = r.get('segment_enclitics') or ()
    if enclitics and r.get('word_class') == 'ISM':
        from pipeline.p5_inflection.feature_system import strip_diacritics as _sd2
        bare_host = _sd2(r.get('segment_host', ''))
        if len(bare_host) >= 3 and bare_host.endswith('ا'):
            return True

    return False


def apply_subject_agreement_context(
    hokom_results: Sequence[tuple[str, dict]],
) -> tuple[list[tuple[str, dict]], int]:
    """
    Apply sequential subject-agreement 3FS resolution to pre-computed results.

    Algorithm for each token with a correlated 2MS/3FS ambiguity:
      A. LOOKAHEAD: scan the next up to 3 tokens.
         - If any token is feminine-singular subject evidence → resolve to 3FS.
         - Stop scanning at a non-coordinated FI3L verb (clause boundary).
      B. INHERITED CONTEXT: if the immediately active feminine context was
         established and the current verb has a فَ/وَ conjunction prefix
         → inherit the resolved feminine context.

    The active feminine context is reset at any unambiguous, uncoordinated
    FI3L verb with an explicit (non-ambiguous) person value.

    HARD GUARDS — never touched:
      - Records where word_class != 'FI3L'
      - Records without a 3FS candidate in ambiguity_candidates
      - JAMID / terminal-boundary records (person=None → skipped naturally)
      - Records with explicit non-ambiguous person

    Returns:
        (resolved_results, count_3fs_resolved)
        where resolved_results is a new list of shallow-copied dicts with
        context-resolved person/gender fields applied.
    """
    from pipeline.p5_inflection.feature_system import strip_diacritics as _sd

    resolved_results: list[tuple[str, dict]] = []
    context_3fs_resolved: int = 0
    active_fem_context: bool = False

    hokom_list = list(hokom_results)
    n = len(hokom_list)

    for i, (tok, r) in enumerate(hokom_list):
        r = dict(r)  # shallow mutable copy — never mutate caller's dict

        # Only consider correlated 2MS/3FS ambiguous imperfect verbs
        if (r.get('word_class') == 'FI3L'
                and r.get('person') in ('2|3',)
                and r.get('number') == 'SG'
                and any(
                    isinstance(c, dict) and c.get('reading') == '3FS'
                    for c in r.get('ambiguity_candidates', ())
                )):

            resolved = False

            # A. Lookahead: scan up to 3 tokens for feminine-singular subject
            for lk in range(i + 1, min(i + 4, n)):
                lk_tok, lk_r = hokom_list[lk]
                if is_feminine_sg_subject_evidence(lk_tok, lk_r):
                    resolved = True
                    break
                # Stop at an uncoordinated FI3L clause boundary
                if (lk_r.get('word_class') == 'FI3L'
                        and not _sd(lk_tok).startswith(('ف', 'و'))):
                    break

            # B. Coordinated fa/wa verb inherits active feminine context
            if not resolved and active_fem_context:
                bare_tok = _sd(tok)
                if bare_tok and bare_tok[0] in ('ف', 'و'):
                    resolved = True

            if resolved:
                r['person'] = '3'
                r['gender'] = 'F'
                context_3fs_resolved += 1
                active_fem_context = True

        elif r.get('word_class') == 'FI3L':
            # Reset active context at an unambiguous, uncoordinated FI3L verb
            person = r.get('person', '')
            if (person not in ('2|3', None)
                    and not _sd(tok).startswith(('ف', 'و'))):
                active_fem_context = False

        resolved_results.append((tok, r))

    return resolved_results, context_3fs_resolved
