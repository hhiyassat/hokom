#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WIRE_ARABIC_NET_POSITION_SOURCE_INTO_LIVE_DAL_MADLUL_BINDING_01 — guards.

Continues REGISTER_ARABIC_NET_SOURCE_AND_DERIVE_T003_VIA_HOKOM_SURFACE_LEMMA_BRIDGE_01:
the registered Arabic-Net source + the Hokom surface→lemma bridge are now reflected into the
LIVE wiring (`wire_dal_madlul`) as a POSITION-ONLY signal, not a licensed meaning.

Constitutional intent (DEFERRED_POSITION_ONLY, preserved):
  - t003 (أُخْتٍ) gains a source-derived `madlul_position` (synset ids) carried on the live row,
  - but there is NO licensed `madlul_text_ar` (no gloss in source), so the binding stays DEFERRED
    and the verdict stays MADLUL_OWNER_PENDING (the position never becomes a meaning),
  - the madlul registry is not mutated, no gate opens, and the dal_madlul score does not move.
"""
import pytest

from scripts import hokom_taaqol_bridge as _b
from scripts.taaqol_dal_madlul_wiring import wire_dal_madlul, WIRING_COLUMNS

NAZILA = ("مَاتَ", "مَلِكٌ", "عَنْ", "أُخْتٍ", "سَاكِنَةٍ", "مَعَهُ،",
          "فَأَرَادَ", "وَارِثُهُ", "طَرْدَهَا،", "فَتَحَاكَمَا.")


@pytest.fixture(scope="module")
def wiring():
    return wire_dal_madlul(_b.analyze_sentence(NAZILA)["tokens"])


def _t003(wiring):
    # أُخْتٍ is the 4th token (index 3) → t003
    rows = {r["token_id"]: r for r in wiring["rows"]}
    return rows["t003"]


# ── W1: the live wiring schema now carries position-only columns ────────────────
def test_W1_position_columns_present():
    for col in ("madlul_position", "position_source", "position_status"):
        assert col in WIRING_COLUMNS


# ── W2: t003 carries the source-derived POSITION on the live row ────────────────
def test_W2_t003_position_derived_from_registered_source(wiring):
    t = _t003(wiring)
    assert t["position_source"] == "ARABIC_NET"
    assert t["position_status"] == "POSITION_DERIVED_TEXT_DEFERRED"
    assert "sibling.n.01" in t["madlul_position"]        # synset position, not a meaning


# ── W3: position is NOT a meaning — t003 stays DEFERRED / OWNER_PENDING ──────────
def test_W3_position_only_never_binds(wiring):
    t = _t003(wiring)
    assert t["binding_status"] == "DEFERRED"
    assert t["madlul_status"] != "LICENSED"
    assert t["verdict"] == "MADLUL_OWNER_PENDING"
    assert "t003" not in wiring["bound_tokens"]


# ── W4: no licensed madlul TEXT is fabricated (no gloss in source) ──────────────
def test_W4_no_licensed_text_fabricated(wiring):
    t = _t003(wiring)
    assert "NOT_LICENSED_NO_GLOSS" in t["residuals"]
    # the position value never leaks a relation / root / wazn / lemma token into the binding
    for bad in ("→", "canonical_root", "wazn", "lemma"):
        assert bad not in t["madlul_position"]


# ── W5: score invariant — position wiring does not raise the dal_madlul score ────
def test_W5_score_and_bound_count_unchanged(wiring):
    s = wiring["summary"]
    assert s["bound"] == 9                       # t003 still unbound (9 of 10)
    assert s["dal_madlul_score_percent"] == 90.0
