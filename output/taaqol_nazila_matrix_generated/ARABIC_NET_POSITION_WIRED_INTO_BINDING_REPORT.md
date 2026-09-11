# WIRE_ARABIC_NET_POSITION_SOURCE_INTO_LIVE_DAL_MADLUL_BINDING_01 — Report

One ordered round. Continues `REGISTER_ARABIC_NET_SOURCE_AND_DERIVE_T003_VIA_HOKOM_SURFACE_LEMMA_BRIDGE_01`.
No downstream gate auto-opened. No madlul registry mutation. No commit / push / git add.
`PROJECT_FINISHED = NO`.

## Precondition (nothing rebuilt)

- Arabic-Net registered as `APPROVED_GENERAL_SEMANTIC_SOURCE`
  (`data/governance/approved_semantic_source_registry.csv`).
- Hokom surface→lemma bridge present (`scripts/hokom_surface_lemma_bridge.py`);
  `surface_to_lemma_derive("t003","أُخْتٍ") → SURFACE_TO_LEMMA_DERIVED`,
  entry `sibling.n.01`, families `family.n.02 / relative.n.01`.
- `DO_NOT_REBUILD_ARABIC_NET_API = YES` honoured. The API was already registered; only its
  **live reflection** into `wire_dal_madlul` was missing (flagged by the registration round as
  "a separate, explicit wiring step — not auto-performed").

## What this round wired

The registered source's semantic **position** (synset ids) is now reflected onto the live
`wire_dal_madlul` row for an open-class owner-pending token, via the existing Hokom bridge —
**position only, never a meaning**.

`scripts/taaqol_dal_madlul_wiring.py`:

- `WIRING_COLUMNS` gains three **additive** position-only columns:
  `madlul_position`, `position_source`, `position_status`.
- In the open-class owner-pending branch (after `mp.from_dal_claim_and_hokom`, preserving the
  locked `dp → gate → mp` order), the wiring calls `surface_to_lemma_derive()` and — only on
  `SURFACE_TO_LEMMA_DERIVED` — records the synset position. Wrapped in an env guard so source
  unavailability can never break the pipeline.

```text
POSITION_SOURCE               = ARABIC_NET
POSITION_KIND                 = SYNSET_POSITION (madlul_position), never madlul_text_ar
BINDING_EFFECT                = NONE (binding stays DEFERRED; verdict stays MADLUL_OWNER_PENDING)
REGISTRY_EFFECT               = NONE (owner-curated madlul registry untouched)
GATE_EFFECT                   = NONE (ifadah/hukm/manat/tanzil/answer_audit unchanged)
```

## t003 (أُخْتٍ) — live row, DEFERRED_POSITION_ONLY preserved

| field | value |
|---|---|
| binding_status | DEFERRED |
| verdict | MADLUL_OWNER_PENDING |
| madlul_position | `sibling.n.01;family.n.02;relative.n.01` |
| position_source | ARABIC_NET |
| position_status | POSITION_DERIVED_TEXT_DEFERRED |
| residuals | `POSITION_ONLY_FROM_REGISTERED_SOURCE;madlul_text_ar=NOT_LICENSED_NO_GLOSS;position=…;OWNER_PENDING` |

The position is surfaced; the **meaning is not**. There is no gloss in the source, so
`madlul_text_ar` remains unlicensed, the binding remains DEFERRED, and the verdict is unchanged.
`DEFERRED_POSITION_ONLY` is preserved exactly.

## Invariants (measured before/after)

| invariant | before | after |
|---|---|---|
| document_percent | 80.0 | 80.0 |
| dal_madlul_score_percent | 90.0 | 90.0 |
| dal_madlul_bound_count | 9 | 9 |
| owner_pending_madlul_entries_count | 1 | 1 |
| manat_status | DEFERRED_WITH_CAUSE | DEFERRED_WITH_CAUSE |
| tanzil / answer_audit | NOT_OPENED | NOT_OPENED |
| madlul registry SHA | d3c7b60939b5 | d3c7b60939b5 |
| ifadah / hukm source token_ids | [t000, t001] | [t000, t001] |

`TAAQOL_NAZILA_CLOSURE_SCORE.json` regenerated **byte-identical** (position wiring does not touch
the closure surface). `TAAQOL_NAZILA_MADLUL_PROVIDER_WIRING_RESULT.csv` regenerated with the three
new position columns (16 → 19 columns; t003 now carries the synset position).

## Tests (RED-first)

New guard `tests/governance/test_arabic_net_position_wired_into_binding.py` (W1–W5):
W1 columns present, W2 t003 position from registered source, W3 position never binds
(DEFERRED / MADLUL_OWNER_PENDING), W4 no licensed text fabricated + no relation/root/wazn/lemma
leak, W5 score/bound-count unchanged. RED before the wiring (W1/W2/W4 fail; W3/W5 already green
= the invariants); GREEN after.

```
python3 -m pytest tests/governance/test_arabic_net_position_wired_into_binding.py \
  tests/taaqol_integration/test_nazila_matrix_generator.py \
  tests/governance/test_owner_approval_level_dustur.py \
  tests/governance/test_arabic_net_source_registration_t003.py
  -> 182 passed
```

## Boundaries held

Position ≠ meaning. No `madlul_text_ar` licensed, no gloss authored, no tool paraphrase promoted.
No MANAT / TANZIL / ANSWER_AUDIT opened. Owner-curated madlul registry not edited (SHA unchanged).
Taaqol produced no Arabic analysis (morphology/lemma remain Hokom-owned via the bridge). Axis-2 not
weakened (`exact_axis2_surface_match = NO`). No commit / push / git add. `PROJECT_FINISHED = NO`.

## Artifacts

- `scripts/taaqol_dal_madlul_wiring.py` (3 additive columns + position-only wiring branch)
- `tests/governance/test_arabic_net_position_wired_into_binding.py` (RED-first guards)
- `output/taaqol_nazila_matrix_generated/TAAQOL_NAZILA_MADLUL_PROVIDER_WIRING_RESULT.csv` (regenerated)
- `output/taaqol_nazila_matrix_generated/TAAQOL_NAZILA_CLOSURE_SCORE.json` (regenerated, byte-identical)
- this report + `ARABIC_NET_POSITION_WIRED_INTO_BINDING_RESULT.csv`
