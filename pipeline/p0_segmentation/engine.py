#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p0_segmentation/engine.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Canonical Hokom Clitic Segmenter engine.

SEGMENTATION_CANONICAL_ENTRYPOINT = 'segment_token'

Decision order:
1. Protected whole-token (لفظ الجلالة, demonstratives, etc.)
2. Exact whole-token operator/mabni
3. Licensed multi-proclitic + (definite_article?) + host + (enclitic?)
4. Licensed single-proclitic + (definite_article?) + host + (enclitic?)
5. Definite article only (no proclitic) + host + (enclitic?)
6. Enclitic only (no proclitic, no article)
7. clitic-only construction (proclitic + enclitic, no host)
8. Unsplit (whole token is host)

No HR2S import. No Taaqol import. No root computation.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
from __future__ import annotations
import hashlib
from typing import Optional

from .models import (
    SEGMENTATION_ENGINE_ID,
    SEGMENTATION_CANONICAL_OWNER,
    SEGMENTATION_CONTRACT_VERSION,
    SegmentationVerdict,
    SegmentRole,
    SegmentKind,
    Segment,
    SegmentEvidence,
    SegmentContradiction,
    SegmentCandidate,
    SegmentBundle,
    SegmentationResidual,
    SegmentationTraceEvent,
    SegmentationRequest,
)
from .inventory import (
    PROTECTED_WHOLE_TOKENS,
    WHOLE_TOKEN_OPERATORS,
    ENCLITICS,
)
from .normalization import (
    canonical_normalize,
    strip_diacritics,
    starts_with_definite_article,
    extract_definite_article_span,
    count_arabic_consonants,
)
from .rules import (
    _bare,
    _is_legal_host,
    _try_enclitic,
    _extract_proclitics,
    _consume_bare_n,
)


# Pre-computed bare sets for fast lookup
_PROTECTED_BARE = frozenset(strip_diacritics(t) for t in PROTECTED_WHOLE_TOKENS)
_OPERATOR_BARE  = frozenset(strip_diacritics(t) for t in WHOLE_TOKEN_OPERATORS)


def _kind_to_enum(kind_str: str) -> SegmentKind:
    mapping = {
        'CONJUNCTION':     SegmentKind.CONJUNCTION,
        'PREPOSITION':     SegmentKind.PREPOSITION,
        'FUTURE_PARTICLE': SegmentKind.FUTURE_PARTICLE,
        'JUSSIVE_LAM':     SegmentKind.JUSSIVE_LAM,
        'RESUMPTION':      SegmentKind.RESUMPTION,
        'INTERROGATIVE':   SegmentKind.INTERROGATIVE,
        'DEFINITE_ARTICLE': SegmentKind.DEFINITE_ARTICLE,
        'ATTACHED_PRONOUN': SegmentKind.ATTACHED_PRONOUN,
    }
    return mapping.get(kind_str, SegmentKind.UNRESOLVED)


def _build_segments(
    norm: str,
    proclitics_list: list,
    definite_article: Optional[str],
    host: Optional[str],
    enclitics_list: list,
    proclitic_kinds: list,
) -> tuple:
    """Build ordered Segment list from components. Spans relative to norm."""
    segments = []
    pos = 0

    for i, p in enumerate(proclitics_list):
        kind_str = proclitic_kinds[i] if i < len(proclitic_kinds) else 'CONJUNCTION'
        seg_kind = _kind_to_enum(kind_str)
        end = pos + len(p)
        segments.append(Segment(
            surface=p,
            role=SegmentRole.PROCLITIC,
            kind=seg_kind,
            span_start=pos,
            span_end=end,
            evidence=(f'proclitic_inventory:{kind_str}',),
        ))
        pos = end

    if definite_article:
        end = pos + len(definite_article)
        segments.append(Segment(
            surface=definite_article,
            role=SegmentRole.DEFINITE_ARTICLE,
            kind=SegmentKind.DEFINITE_ARTICLE,
            span_start=pos,
            span_end=end,
            evidence=('definite_article_pattern',),
        ))
        pos = end

    if host:
        end = pos + len(host)
        segments.append(Segment(
            surface=host,
            role=SegmentRole.HOST,
            kind=SegmentKind.LEXICAL_HOST,
            span_start=pos,
            span_end=end,
            evidence=('host_remainder',),
        ))
        pos = end

    for enc in enclitics_list:
        end = pos + len(enc)
        segments.append(Segment(
            surface=enc,
            role=SegmentRole.ENCLITIC,
            kind=SegmentKind.ATTACHED_PRONOUN,
            span_start=pos,
            span_end=end,
            evidence=('enclitic_inventory',),
        ))
        pos = end

    return tuple(segments)


def _make_bundle(
    request: SegmentationRequest,
    *,
    verdict: SegmentationVerdict,
    proclitics: tuple = (),
    definite_article: Optional[str] = None,
    host: Optional[str] = None,
    enclitics: tuple = (),
    segments: tuple = (),
    segment_candidates: tuple = (),
    evidence: tuple = (),
    contradictions: tuple = (),
    ambiguities: tuple = (),
    residuals: tuple = (),
    trace: tuple = (),
) -> SegmentBundle:
    """Construct a SegmentBundle with all contract invariants verified."""
    norm = request.normalized_surface

    # INVARIANT: host must be None, not ""
    if host == '':
        host = None

    host_present = host is not None
    clitic_only  = (not host_present) and (len(proclitics) > 0 or len(enclitics) > 0)

    # Span indices from segment list
    segment_spans = tuple((s.span_start, s.span_end) for s in segments)

    # Roundtrip: concatenated segment surfaces should equal norm
    roundtrip = ''.join(s.surface for s in segments) if segments else norm

    # Provenance hash
    content    = f'{SEGMENTATION_ENGINE_ID}:{norm}:{verdict.value}'
    provenance = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    return SegmentBundle(
        request_id=request.request_id,
        original_surface=request.original_surface,
        normalized_surface=norm,
        verdict=verdict,
        proclitics=proclitics,
        definite_article=definite_article,
        host=host,
        host_surface=host,
        host_normalized=canonical_normalize(host) if host else None,
        enclitics=enclitics,
        segments=segments,
        segment_candidates=segment_candidates,
        evidence=evidence,
        contradictions=contradictions,
        ambiguities=ambiguities,
        residuals=residuals,
        trace=trace,
        engine_id=SEGMENTATION_ENGINE_ID,
        canonical_owner=SEGMENTATION_CANONICAL_OWNER,
        contract_version=SEGMENTATION_CONTRACT_VERSION,
        input_span=(0, len(norm)),
        segment_spans=segment_spans,
        roundtrip_surface=roundtrip,
        host_present=host_present,
        clitic_only=clitic_only,
        provenance=provenance,
    )


def segment_token(request: SegmentationRequest) -> SegmentBundle:
    """
    SEGMENTATION_CANONICAL_ENTRYPOINT.

    Takes a SegmentationRequest, returns a SegmentBundle.
    Deterministic. No random values. No HR2S calls. No Taaqol calls.
    """
    norm = canonical_normalize(request.normalized_surface)
    bare = _bare(norm)
    trace: list = []

    # ── Step 0: Canonical mabni whole-token catalog lookup ───────────────────
    # Query the mabniyat catalog BEFORE any proclitic decomposition.
    # If the complete normalized surface is registered in the catalog, return
    # it as an unsplit host.  This prevents catalog entries like بِضْع,
    # وَشْكَانَ, وَاهًا from being split on their initial letters simply
    # because those letters also appear as proclitic operators.
    #
    # We pass 'ACCEPT' as the structural verdict because P4 has not run yet;
    # the catalog membership check alone (verdict != MABNI_NOT_FOUND) is the
    # guard — P4 monotonicity is enforced downstream in the attachment layer.
    try:
        from mabniyat_layer import process_mabni as _catalog_lookup
        _cat_result = _catalog_lookup(norm, 'ACCEPT')
        if _cat_result.verdict != 'MABNI_NOT_FOUND':
            trace.append(SegmentationTraceEvent(
                step='0_catalog_whole_token',
                rule='LEXICAL_WHOLE_TOKEN_PRECEDENCE',
                input=norm,
                output=norm,
                outcome='CATALOG_PROTECTED',
            ))
            segs = _build_segments(norm, [], None, norm, [], [])
            return _make_bundle(
                request,
                verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
                host=norm,
                segments=segs,
                evidence=(SegmentEvidence(
                    rule='LEXICAL_WHOLE_TOKEN_PRECEDENCE',
                    source='HOKOM_CATALOG',
                    confidence='HIGH',
                    notes=f'Catalog entry: {_cat_result.mabni_id} ({_cat_result.lexical_class})',
                ),),
                trace=tuple(trace),
            )
    except ImportError:
        pass  # catalog not available — continue with inventory-based rules

    # ── Step 1: Protected whole-token ────────────────────────────────────────
    if norm in PROTECTED_WHOLE_TOKENS or bare in _PROTECTED_BARE:
        trace.append(SegmentationTraceEvent(
            step='1_protected_whole_token',
            rule='LEXICALLY_PROTECTED_HOST',
            input=norm,
            output=norm,
            outcome='HOST_PROTECTED',
        ))
        segs = _build_segments(norm, [], None, norm, [], [])
        return _make_bundle(
            request,
            verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
            host=norm,
            segments=segs,
            evidence=(SegmentEvidence(
                rule='LEXICALLY_PROTECTED_HOST',
                source='HOKOM_INVENTORY',
                confidence='HIGH',
                notes='Protected whole token — no decomposition',
            ),),
            trace=tuple(trace),
        )

    # ── Step 2: Whole-token operator ─────────────────────────────────────────
    if norm in WHOLE_TOKEN_OPERATORS or bare in _OPERATOR_BARE:
        trace.append(SegmentationTraceEvent(
            step='2_whole_token_operator',
            rule='OPERATOR_WHOLE_TOKEN',
            input=norm,
            output=norm,
            outcome='OPERATOR_HOST',
        ))
        # Operators can still take enclitics (e.g., مِنْهُ, عَلَيْهِ)
        enc_result = _try_enclitic(norm)
        if enc_result:
            stem, enc_surface, enc_kind = enc_result
            segs = _build_segments(norm, [], None, stem, [enc_surface], [])
            return _make_bundle(
                request,
                verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
                host=stem,
                enclitics=(enc_surface,),
                segments=segs,
                evidence=(SegmentEvidence(
                    rule='OPERATOR_HOST_WITH_ENCLITIC',
                    source='HOKOM_INVENTORY',
                    confidence='HIGH',
                ),),
                trace=tuple(trace),
            )
        segs = _build_segments(norm, [], None, norm, [], [])
        return _make_bundle(
            request,
            verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
            host=norm,
            segments=segs,
            evidence=(SegmentEvidence(
                rule='OPERATOR_WHOLE_TOKEN',
                source='HOKOM_INVENTORY',
                confidence='HIGH',
            ),),
            trace=tuple(trace),
        )

    # ── Step 2.5: Contracted لِل (lam preposition + definite article) ─────────
    # In Arabic, لِ + الْ → لِلْ (or لِلـ for solar letters).  The alef of
    # الْ is elided, leaving two consecutive lams at the token's start.
    # starts_with_definite_article() looks for اَل and therefore misses this.
    # We detect the pattern here — bare surface starts with لل — and extract:
    #   proclitic = first ل (the preposition لِ)
    #   definite_article = second ل (the contracted article لْ / لـ)
    #   host = everything after
    # Pure surface-pattern logic. No root computation. No Word Class lookup.
    if bare.startswith('لل') and len(bare) >= 4:
        _proclitic_li, _after_li   = _consume_bare_n(norm, 1)
        _article_lam,  _after_art  = _consume_bare_n(_after_li, 1)
        if _is_legal_host(_after_art):
            trace.append(SegmentationTraceEvent(
                step='2.5_contracted_li_al',
                rule='CONTRACTED_LI_PLUS_AL',
                input=norm,
                output=(
                    f'proclitic={_bare(_proclitic_li)}, '
                    f'article={_bare(_article_lam)}, '
                    f'host={_bare(_after_art)}'
                ),
                outcome='CONTRACTED_ARTICLE_EXTRACTED',
            ))
            # Try enclitic on host
            _enc_r = _try_enclitic(_after_art)
            _encs_li: list = []
            _host_li = _after_art
            if _enc_r:
                _stem_li, _enc_li, _ = _enc_r
                if _is_legal_host(_stem_li):
                    _host_li = _stem_li
                    _encs_li = [_enc_li]
            _segs = _build_segments(
                norm, [_proclitic_li], _article_lam, _host_li, _encs_li, ['PREPOSITION']
            )
            return _make_bundle(
                request,
                verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
                proclitics=(_proclitic_li,),
                definite_article=_article_lam,
                host=_host_li,
                enclitics=tuple(_encs_li),
                segments=_segs,
                evidence=(SegmentEvidence(
                    rule='CONTRACTED_LI_PLUS_AL',
                    source='HOKOM_INVENTORY',
                    confidence='HIGH',
                    notes='Contracted lam preposition + definite article (لِ + الْ → لِلْ/لِلـ)',
                ),),
                trace=tuple(trace),
            )

    # ── Step 3+4: Try proclitic extraction ───────────────────────────────────
    proclitic_result = _extract_proclitics(norm, _PROTECTED_BARE | _OPERATOR_BARE)

    if proclitic_result:
        proclitics_list, remainder, p_kinds = proclitic_result
        trace.append(SegmentationTraceEvent(
            step='3_proclitic_extraction',
            rule='PROCLITIC_INVENTORY',
            input=norm,
            output=f'proclitics={[_bare(p) for p in proclitics_list]}, remainder={_bare(remainder)}',
            outcome='PROCLITIC_EXTRACTED',
        ))

        bare_remainder = _bare(remainder)

        # Check if remainder is protected (e.g., وَاللَّهُ → remainder=اللَّهُ)
        if bare_remainder in _PROTECTED_BARE:
            trace.append(SegmentationTraceEvent(
                step='3b_remainder_protected',
                rule='LEXICALLY_PROTECTED_HOST',
                input=remainder,
                output=remainder,
                outcome='REMAINDER_PROTECTED',
            ))
            segs = _build_segments(norm, proclitics_list, None, remainder, [], p_kinds)
            return _make_bundle(
                request,
                verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
                proclitics=tuple(proclitics_list),
                host=remainder,
                segments=segs,
                evidence=(SegmentEvidence(
                    rule='PROCLITIC_PLUS_PROTECTED_HOST',
                    source='HOKOM_INVENTORY',
                    confidence='HIGH',
                    notes='Protected host after proclitic — no further decomposition',
                ),),
                trace=tuple(trace),
            )

        # Check if remainder is an operator (treat as host without article split)
        if bare_remainder in _OPERATOR_BARE:
            # Operator after proclitic — try enclitic on operator
            enc_result = _try_enclitic(remainder)
            if enc_result:
                stem, enc_surface, _ = enc_result
                segs = _build_segments(norm, proclitics_list, None, stem, [enc_surface], p_kinds)
                return _make_bundle(
                    request,
                    verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
                    proclitics=tuple(proclitics_list),
                    host=stem,
                    enclitics=(enc_surface,),
                    segments=segs,
                    evidence=(SegmentEvidence(
                        rule='PROCLITIC_PLUS_OPERATOR_HOST_WITH_ENCLITIC',
                        source='HOKOM_INVENTORY',
                        confidence='HIGH',
                    ),),
                    trace=tuple(trace),
                )
            segs = _build_segments(norm, proclitics_list, None, remainder, [], p_kinds)
            return _make_bundle(
                request,
                verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
                proclitics=tuple(proclitics_list),
                host=remainder,
                segments=segs,
                evidence=(SegmentEvidence(
                    rule='PROCLITIC_PLUS_OPERATOR_HOST',
                    source='HOKOM_INVENTORY',
                    confidence='HIGH',
                ),),
                trace=tuple(trace),
            )

        # NEW: Check if remainder is EXACTLY a known bare enclitic → clitic-only
        # Example: بِكُمْ → بِ (proclitic) + كُمْ (enclitic), host=None
        _ENCLITICS_BARE = frozenset(enc_bare for enc_bare, _ in ENCLITICS)
        if bare_remainder in _ENCLITICS_BARE:
            segs = _build_segments(norm, proclitics_list, None, None, [remainder], p_kinds)
            return _make_bundle(
                request,
                verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
                proclitics=tuple(proclitics_list),
                host=None,
                enclitics=(remainder,),
                segments=segs,
                evidence=(SegmentEvidence(
                    rule='CLITIC_ONLY_CONSTRUCTION',
                    source='HOKOM_INVENTORY',
                    confidence='HIGH',
                    notes='Remainder is exactly an enclitic — proclitic+enclitic, no host',
                ),),
                residuals=(SegmentationResidual(
                    code='CLITIC_ONLY_CONSTRUCTION',
                    reason='No lexical host; remainder is a known enclitic pronoun',
                ),),
                trace=tuple(trace),
            )

        # Check for definite article on remainder
        art = None
        host_candidate = remainder

        if starts_with_definite_article(remainder):
            art_surface, after_art, _ = extract_definite_article_span(remainder)
            if art_surface and _is_legal_host(after_art):
                art = art_surface
                host_candidate = after_art
                trace.append(SegmentationTraceEvent(
                    step='4_definite_article',
                    rule='DEFINITE_ARTICLE_PATTERN',
                    input=remainder,
                    output=f'article={_bare(art)}, host={_bare(host_candidate)}',
                    outcome='ARTICLE_EXTRACTED',
                ))

        # Try enclitic on host_candidate
        enc_result = _try_enclitic(host_candidate)
        enclitics_found: list = []
        if enc_result:
            stem, enc_surface, _ = enc_result
            if _is_legal_host(stem):
                host_candidate = stem
                enclitics_found = [enc_surface]

        # Check: is remainder just an enclitic? (clitic-only: proclitic + enclitic)
        if not _is_legal_host(host_candidate) and not enclitics_found:
            # Try to match remainder as pure enclitic
            bare_rem = _bare(remainder)
            from .inventory import ENCLITICS as _ENCS
            for bare_enc, kind in sorted(_ENCS, key=lambda x: len(x[0]), reverse=True):
                if bare_rem == bare_enc:
                    # clitic-only: proclitic + enclitic, no lexical host
                    segs = _build_segments(norm, proclitics_list, None, None, [remainder], p_kinds)
                    return _make_bundle(
                        request,
                        verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
                        proclitics=tuple(proclitics_list),
                        host=None,
                        enclitics=(remainder,),
                        segments=segs,
                        evidence=(SegmentEvidence(
                            rule='CLITIC_ONLY_CONSTRUCTION',
                            source='HOKOM_INVENTORY',
                            confidence='MEDIUM',
                            notes='No legal lexical host; proclitic+enclitic only',
                        ),),
                        residuals=(SegmentationResidual(
                            code='CLITIC_ONLY_CONSTRUCTION',
                            reason='No lexical host found; token is proclitic+enclitic only',
                        ),),
                        trace=tuple(trace),
                    )
                    break

        if _is_legal_host(host_candidate):
            segs = _build_segments(norm, proclitics_list, art, host_candidate, enclitics_found, p_kinds)
            evid = [SegmentEvidence(rule='PROCLITIC_INVENTORY', source='HOKOM_INVENTORY', confidence='HIGH')]
            if art:
                evid.append(SegmentEvidence(rule='DEFINITE_ARTICLE_PATTERN', source='HOKOM_INVENTORY', confidence='HIGH'))
            if enclitics_found:
                evid.append(SegmentEvidence(rule='ENCLITIC_INVENTORY', source='HOKOM_INVENTORY', confidence='HIGH'))

            return _make_bundle(
                request,
                verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
                proclitics=tuple(proclitics_list),
                definite_article=art,
                host=host_candidate,
                enclitics=tuple(enclitics_found),
                segments=segs,
                evidence=tuple(evid),
                trace=tuple(trace),
            )

        # Proclitic found but host is illegal — fall through to unsplit
        trace.append(SegmentationTraceEvent(
            step='3x_proclitic_rejected',
            rule='ILLEGAL_HOST_AFTER_PROCLITIC',
            input=norm,
            output=f'remainder={bare_remainder} has {count_arabic_consonants(remainder)} consonants',
            outcome='PROCLITIC_REJECTED',
        ))

    # ── Step 5: Definite article only (no proclitic) ─────────────────────────
    if starts_with_definite_article(norm):
        art_surface, after_art, _ = extract_definite_article_span(norm)
        if art_surface and _is_legal_host(after_art):
            trace.append(SegmentationTraceEvent(
                step='5_definite_article_no_proclitic',
                rule='DEFINITE_ARTICLE_PATTERN',
                input=norm,
                output=f'article={_bare(art_surface)}, host={_bare(after_art)}',
                outcome='ARTICLE_EXTRACTED',
            ))
            # Try enclitic on host
            enc_result = _try_enclitic(after_art)
            enclitics_found = []
            host_final = after_art
            if enc_result:
                stem, enc_s, _ = enc_result
                if _is_legal_host(stem):
                    host_final = stem
                    enclitics_found = [enc_s]

            segs = _build_segments(norm, [], art_surface, host_final, enclitics_found, [])
            return _make_bundle(
                request,
                verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
                definite_article=art_surface,
                host=host_final,
                enclitics=tuple(enclitics_found),
                segments=segs,
                evidence=(SegmentEvidence(
                    rule='DEFINITE_ARTICLE_PATTERN',
                    source='HOKOM_INVENTORY',
                    confidence='HIGH',
                ),),
                trace=tuple(trace),
            )

    # ── Step 6: Enclitic only (no proclitic, no article) ─────────────────────
    enc_result = _try_enclitic(norm)
    if enc_result:
        stem, enc_surface, enc_kind = enc_result
        if _is_legal_host(stem):
            trace.append(SegmentationTraceEvent(
                step='6_enclitic_only',
                rule='ENCLITIC_INVENTORY',
                input=norm,
                output=f'host={_bare(stem)}, enclitic={_bare(enc_surface)}',
                outcome='ENCLITIC_EXTRACTED',
            ))
            segs = _build_segments(norm, [], None, stem, [enc_surface], [])
            return _make_bundle(
                request,
                verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
                host=stem,
                enclitics=(enc_surface,),
                segments=segs,
                evidence=(SegmentEvidence(
                    rule='ENCLITIC_INVENTORY',
                    source='HOKOM_INVENTORY',
                    confidence='HIGH',
                ),),
                trace=tuple(trace),
            )

    # ── Step 8: Unsplit — whole token is host ─────────────────────────────────
    trace.append(SegmentationTraceEvent(
        step='8_unsplit_host',
        rule='NO_CLITIC_FOUND',
        input=norm,
        output=norm,
        outcome='UNSPLIT',
    ))
    segs = _build_segments(norm, [], None, norm, [], [])
    return _make_bundle(
        request,
        verdict=SegmentationVerdict.SEGMENTATION_ACCEPTED,
        host=norm,
        segments=segs,
        evidence=(SegmentEvidence(
            rule='NO_CLITIC_FOUND',
            source='HOKOM_INVENTORY',
            confidence='HIGH',
            notes='No clitic pattern matched; whole token is host',
        ),),
        trace=tuple(trace),
    )
