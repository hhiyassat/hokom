# MAQAM_ARCHITECTURE_AND_OWNERSHIP

**Label:** `MAQAM_THEORY_FOUNDATION_IMPLEMENTATION_WITH_TRACEABILITY`

## Layers and owners
```
existing core (preserved, evolved — history kept):
  taaqol_maqam_theory_implementation_01/src/taaqol_maqam/birth.py   — four-axis status kernel
  taaqol_maqam_theory_implementation_01/src/taaqol_maqam/maqam.py   — MaqamEvidence / profiles / evaluate_maqam_birth
  taaqol_maqam_theory_implementation_01/src/taaqol_maqam/nazila.py  — nazila internal-cue extraction (candidate-only)

foundation layer (new, this round — does NOT rewrite the core):
  scripts/taaqol_maqam_foundation/foundation.py            — CoreMaqamDimensionRegistry (versioned),
                                                             MaqamExtensionRegistry (open),
                                                             full rank ladder (+EXTERNALLY_SUPPLIED),
                                                             four scholarly branches,
                                                             active scope_within(), MAQAM!=NORMATIVE guard
  scripts/taaqol_maqam_foundation/run_nazila_foundation.py — two deterministic runs + artifact emitters
```

## Ownership boundaries (unchanged)
- **Hokom** remains the owner of Arabic analysis. This round does **not** duplicate Hokom or Taaqol
  functionality and does **not** modify `vendor/Taaqol-GPT`.
- The maqām layer only **constrains / prefers / defers** candidates produced by the linguistic owner;
  it does not replace the analyzer and does not author meaning.

## Integration status
```
MAQAM_RUNTIME_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE
CAUSE = no ratified canonical Hokom↔Taaqol maqām contract is available this round; a representational
        (fake) integration is forbidden. The foundation stays independent and typed.
```
No canonical pipeline gate is opened from a report. No new stage is wired while its parent contract is
unproven.

## Producer discipline
Every emitted artifact is produced by a named script (`producer_file` in the traceability CSV / run
JSONs). No artifact claims `PRODUCED_BY_CODE` for a value that was hand-authored without a rule +
license. The two nazila runs are proven reproducible (byte-identical re-run test).

## Residuals / deferred (honest)
- Heritage example corpus (section 13) → `DEFERRED_SOURCE_TEXT_CORRUPTION` (needs clean source text).
- Coreference / ellipsis / word-order / speech-act gates (section 12) → `DEFERRED_WITH_RESIDUAL`
  (foundation-round scope; birth-law and candidate-only discipline already prevent overreach).
- Canonical Hokom integration → `BLOCKED_WITH_CAUSE`.
