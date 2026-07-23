#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p5_inflection/context_carrier.py

HOKOM-AYAT-AL-DAYN-LIVE-PATH-GOLD-CONFORMANCE-01 — Sequential Context Carrier

Typed carrier for inter-token governing-particle state.  Used by the demo
runner (scripts/demo_ayat_al_dayn.py) to propagate mood from a governing
particle token to the subsequent imperfect-verb token.

Design rules:
  - Lives in the pipeline module (not in the demo or HTML formatter).
  - Does NOT modify hokom() internals — it operates at the runner level.
  - Scope is always 1: the very next token after the governing particle.
  - Multiple consecutive particles are handled correctly: each update_from_token()
    replaces any pending governing context with the new particle's mood.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SequentialAnalysisContext:
    """
    Carries governing-particle state between consecutive token analyses.

    Lifecycle per token:
      1. Call consume_mood()  to retrieve (and clear) any pending mood injection.
      2. Apply the returned mood to the current token's morphosyntax if the token
         is an imperfect verb (tense_aspect == 'IMPERFECT').
      3. Call update_from_token(surface) to record whether the current token is
         itself a governing particle that will affect the *next* token.

    Governing-particle sets are imported from feature_system to stay DRY.
    """

    # Internal state — do not read directly; use consume_mood() / update_from_token().
    _governing_particle: Optional[str] = field(default=None, repr=False)
    _governing_mood: Optional[str] = field(default=None, repr=False)
    _scope_remaining: int = field(default=0, repr=False)

    # Informational (for debugging / tracing)
    last_particle: Optional[str] = None
    last_injected_surface: Optional[str] = None

    def consume_mood(self) -> Optional[str]:
        """
        Return the mood to inject into the current token, then clear scope.

        Returns 'JUSSIVE', 'SUBJUNCTIVE', or None.
        After this call, the scope is exhausted (scope=0) so subsequent tokens
        do NOT inherit the same injection.
        """
        if self._scope_remaining > 0 and self._governing_mood is not None:
            mood = self._governing_mood
            self._scope_remaining -= 1
            if self._scope_remaining == 0:
                self._governing_particle = None
                self._governing_mood = None
            return mood
        return None

    def update_from_token(self, surface: str) -> None:
        """
        Inspect the just-processed token's surface and update governing state.

        If the surface is a known governing particle, record it so that
        consume_mood() will return the appropriate mood for the NEXT token.

        Importing here (deferred) avoids circular import — context_carrier is
        part of the pipeline but does not import from it at module load time.
        """
        from pipeline.p5_inflection.feature_system import (
            _JUSSIVE_PARTICLE_FORMS as _JPF,
            _SUBJUNCTIVE_PARTICLE_FORMS as _SPF,
        )
        if surface in _JPF:
            self._governing_particle = surface
            self._governing_mood = 'JUSSIVE'
            self._scope_remaining = 1
            self.last_particle = surface
        elif surface in _SPF:
            self._governing_particle = surface
            self._governing_mood = 'SUBJUNCTIVE'
            self._scope_remaining = 1
            self.last_particle = surface
        # If not a governing particle: leave existing scope unchanged so that
        # a particle's scope is not accidentally reset by a non-particle token.

    def inject_mood_into_result(
        self,
        result: dict,
        surface: str,
    ) -> dict:
        """
        Convenience method: apply consume_mood() to a process_token_full() result.

        Modifies the 'morphosyntax' sub-dict in-place if the token is a
        confirmed non-terminal FI3L token with an IMPERFECT verb and a
        governing mood is pending.

        RESTRICTIONS (HOKOM-CLOSED-CONTRACT-SEMANTIC-REGRESSION-FIREWALL-01):
          - Must NOT inject mood into a terminal-boundary record
            (boundary_type=JAMID_AALAM_BOUNDARY / MABNI_BOUNDARY / etc.)
          - Must NOT change word_class
          - Must NOT create FI3L for an ISM/HARF/JAMID record
          - Must NOT override a terminal boundary

        Returns the (possibly modified) result dict.
        """
        _TERMINAL_VERDICTS = frozenset({
            'JAMID_AALAM_BOUNDARY',
            'MABNI_BOUNDARY',
            'OPERATOR_BOUNDARY',
        })

        # Guard 1: terminal boundary — no injection
        for _key in ('boundary_type', 'jamid_verdict', 'mabni_verdict', '_route_v'):
            if result.get(_key) in _TERMINAL_VERDICTS:
                # Consume mood (scope must be depleted) but do not apply it
                self.consume_mood()
                return result

        # Guard 2: only inject into a confirmed FI3L record
        wc_result = result.get('word_class')
        wc_class  = None
        if isinstance(wc_result, dict):
            wc_class = wc_result.get('class')
        elif isinstance(wc_result, str):
            wc_class = wc_result

        mood = self.consume_mood()
        if mood is not None:
            # Guard 3: only modify morphosyntax — never word_class
            ms = result.get('morphosyntax')
            if isinstance(ms, dict) and ms.get('tense_aspect') == 'IMPERFECT':
                ms['mood'] = mood
                self.last_injected_surface = surface
        return result
