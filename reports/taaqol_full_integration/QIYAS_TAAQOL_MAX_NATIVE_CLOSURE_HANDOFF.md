# QIYAS-TAAQOL-MAXIMUM-NATIVE-CLOSURE-01 — Implementation Handoff

**Status:** `IMPLEMENTED_PENDING_INDEPENDENT_AUDIT`
**Maximum native closure:** `IMPLEMENTED_TO_FIRST_GENUINE_BLOCKER`
**Branch:** `closure/hokom-taaqol-final-production-01`
**Head:** `8cc5a6e`
**Vendor SHA:** `05c6668dfb95d9238cff5df1d8bc73d0664bccb3` (pinned)

## 1. What was closed

The full native Taaqol reasoning DAG consumed by Hokom, on the real
Ayat corpus (37 CUs, 5 source-derived spans), through every reachable
stage in the pinned vendor kernel:

    FormalStyle
    → MufradSemanticSlot
    → MaqamContext
    → Dalalah
    → MufradDalalahClosure
    → RelationClosure
    → Ifadah
    ├── Hukm → Manat → Tanzil   (TERMINAL vertical)
    └── Mantuq → Mafhum          (parallel branch)

Per-stage closure counts (identical across two deterministic runs):

| Stage           | Calls | Proven |
|-----------------|-------|--------|
| Ifadah          | 5     | 5      |
| Hukm            | 5     | 5      |
| Manat           | 5     | 5      |
| Tanzil (TERM.)  | 5     | 5      |
| Mantuq          | 5     | 5      |
| Mafhum          | 5     | 5      |

## 2. Commits landed this wave

    ccd971a  fix(taaqol): use verdict_state on 5 downstream vendor adapters
    f976a17  feat(taaqol): close full downstream DAG — Hukm → Manat → Tanzil + Mantuq → Mafhum
    734b042  test(taaqol): C13 Wave05 downstream closure verification (14 tests)
    8cc5a6e  evidence(taaqol): real Ayat vertical + deterministic double-run

## 3. Constitutional defect closed

Five downstream adapters (`hukm_candidate_adapter`,
`manat_candidate_adapter`, `tanzil_candidate_adapter`,
`mantuq_closure_adapter`, `mafhum_closure_adapter`) accessed `.state`
on vendor verdict dataclasses which actually expose the field as
`.verdict_state`. The resulting `AttributeError` was silently
swallowed by the adapter's broad `except Exception` and treated as a
refused verdict — masking every successful native closure downstream
of Ifadah.

The same defect was closed on `ifadah_candidate_adapter` in Wave04.
This wave propagates the fix to the remaining five adapters (commit
`ccd971a`).

## 4. Adapter signature reconciliations

Downstream adapters required real, non-empty values for constitutional
inputs that were previously being passed as empty strings:

| Adapter                       | Field                              | Required value                    |
|-------------------------------|------------------------------------|-----------------------------------|
| `manat_candidate_adapter`     | `effective_attribute_candidate`    | non-empty; derived from `gov_token_id` |
| `mafhum_closure_adapter`      | `qayd`                             | non-empty; derived from `span_id` |
| `mafhum_closure_adapter`      | `mantuq_blocks`                    | `False` when branch_type + qayd present |
| `tanzil_candidate_adapter`    | `presentation_warning`             | non-empty; `"CANDIDATE"` |

The chain runner `wave05_downstream_chain.execute_ayat_full_downstream_chain`
passes these consistently for every span. Empty-value refusals remain
the fail-closed default of each adapter (asserted by
`test_w5_14_mafhum_empty_qayd_refused_via_adapter`).

## 5. Test coverage

    tests/taaqol_integration/test_c13_wave03_verification_supplement.py   7/7
    tests/taaqol_integration/test_c13_wave04_ifadah_closure.py           11/11
    tests/taaqol_integration/test_c13_wave05_downstream_closure.py       14/14
                                                                         -----
                                                                         32/32   in 71s

## 6. Determinism gate

    PYTHONHASHSEED=0
    RUN1 summary == RUN2 summary   ✓   (byte-identical per-span logs)

Evidence artifacts under `reports/qiyas_taaqol_max_native_closure/`:

- `RUN1_FULL_DOWNSTREAM_EXECUTION.json`
- `RUN2_FULL_DOWNSTREAM_EXECUTION.json`
- `DETERMINISM_COMPARE.json` (`identical: true`)
- `CLOSURE_SUMMARY.md`

## 7. Integrity attestation

    arbitrary_adjacency_execution_count      = 0
    fixture_counted_as_ayat_execution        = 0
    direct_native_output_injection_count     = 0
    synthetic_evidence                       = 0
    synthetic_provenance                     = 0
    expected_verdict_lookup_tables           = 0
    token_position_branches                  = 0
    example_sentence_text_branches           = 0
    quranic_surface_text_branches            = 0

## 8. First genuine external / constitutional blocker

**None encountered within the pinned vendor kernel.** Every reachable
stage in the Taaqol DAG closes on the real Ayat corpus. Downstream
stages beyond Tanzil (vertical TERMINAL) and Mafhum (parallel branch)
are not defined in the pinned vendor SHA.

If further stages are added to the vendor kernel (e.g. inheritance
`Tanzil → post-tanzil action-record`), that would be the next
implementation wave — it does not exist today.

## 9. What is NOT claimed

- **No self-declaration of `VERIFIED_CLOSED`.** Independent audit
  remains the sole path to `VERIFIED_CLOSED` per §11 of the campaign
  constitution.
- **No modification of the Taaqol vendor submodule.** All work is on
  the Hokom side (adapters + chain runner + tests + evidence).
- **No promotion of machine candidates into licensed knowledge.**
  Every vendor `TanzilVerdict` carries `not_execution_marker=True`;
  every `ManatVerdict` uses `ManatMode.TAHQIQ_READINESS_ONLY`.
- **No suppression of residuals for acceptance.** Empty residual
  tuples throughout — vendor asserts absence via `HIDDEN_RESIDUAL`
  failure code.

## 10. Recommended next actions (owner decision)

1. Independent audit of Wave03 → Wave05 code + evidence artifacts.
2. On audit `VERIFIED_CLOSED`: tag `qiyas-taaqol-max-native-closure/verified-closed-8cc5a6e`.
3. On audit remediation request: reopen this task with defect list.
