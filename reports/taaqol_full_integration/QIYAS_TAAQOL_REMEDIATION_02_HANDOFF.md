# QIYAS-TAAQOL-MAXIMUM-NATIVE-CLOSURE-REMEDIATION-02 — Implementation Handoff

**Status:** `IMPLEMENTED_PENDING_INDEPENDENT_REAUDIT`
**Branch:** `closure/hokom-taaqol-final-production-01`
**Implementation content HEAD (this report's own commit is NOT
this SHA — see accompanying binding manifest):** `277ff13`
**Vendor SHA:** `05c6668dfb95d9238cff5df1d8bc73d0664bccb3` (pinned; unmodified)

## 1. Audit findings addressed

The independent audit
(`QIYAS-TAAQOL-MAXIMUM-NATIVE-CLOSURE-INDEPENDENT-AUDIT-01`)
returned `PARTIALLY_VERIFIED` with these open locally-closeable
defects:

| # | Defect | Repair | Commit |
|---|---|---|---|
| 1 | `bridge_tanzil_to_audit` reachable but not invoked | REPAIR A — Wave06 chain invokes it via typed builder | `ff21224` |
| 2 | Downstream adapters collapse typed REFUSED to None | REPAIR B — `DownstreamStageOutcome` preserves everything | `168d8d9` + `be749bb` |
| 3 | Manat and Mantuq lack negative-path tests | REPAIR C — 11 typed Wave06 tests (see §W6.4–W6.10) | `493d74c` |
| 4 | Downstream trace/residual/failure_code not in artifact | REPAIR D — rich per-stage schema in RUN1/RUN2 JSON | `ff21224` + evidence commit |
| 5 | Handoff incorrectly calls Tanzil terminal | REPAIR E — terminology corrected across 7 files | `277ff13` |
| 6 | Handoff HEAD reference stale/self-including | REPAIR F — two-step binding (this report + separate binding manifest) | (this report + next commit) |

## 2. Wave06 commit chain

    168d8d9  feat(taaqol): typed downstream stage outcome preserving REFUSED
    be749bb  feat(taaqol): typed stage builders that preserve REFUSED for all 6 downstream stages
    ff21224  feat(taaqol): Wave06 typed chain closes bridge_tanzil_to_audit stage
    493d74c  test(taaqol): Wave06 typed closure + explicit Manat/Mantuq/audit-bridge REFUSED
    <ev>     evidence(taaqol): Wave06 real Ayat run + rich per-stage artifact + double-run
    277ff13  docs(taaqol): correct Tanzil terminal semantics across reports and adapters

## 3. Full downstream DAG closed by Wave06

    FormalStyle → MufradSemanticSlot → MaqamContext → Dalalah →
    MufradDalalahClosure → RelationClosure → Ifadah
        ├── Hukm → Manat → Tanzil (weight-terminal)
        │                    └── AuditedTanzilBridge (audit-terminal)   ← new
        └── Mantuq → Mafhum (parallel-terminal)

Real Ayat corpus, 5 spans (identical across two deterministic runs):

| Stage                    | Calls | ACCEPT | DEFER | BLOCK |
|--------------------------|-------|--------|-------|-------|
| Ifadah                   | 5     | 5      | 0     | 0     |
| Hukm                     | 5     | 5      | 0     | 0     |
| Manat                    | 5     | 5      | 0     | 0     |
| Tanzil (weight-terminal) | 5     | 5      | 0     | 0     |
| AuditedTanzilBridge      | 5     | 5      | 0     | 0     |
| Mantuq                   | 5     | 5      | 0     | 0     |
| Mafhum                   | 5     | 5      | 0     | 0     |

`unbridged_reachable_stage_count = 0`

## 4. Typed outcome contract (REPAIR B)

    @dataclass(frozen=True, slots=True)
    class DownstreamStageOutcome:
        stage: str
        verdict_state: str          # "PROVEN" | "REFUSED" | "SURFACED"
        classification: str         # "ACCEPT" | "DEFER" | "BLOCK"
        native_verdict: Any         # vendor DTO (never re-constructed)
        failure_code: Optional[str]
        trace_ref: str
        residuals: tuple
        residual_ids: tuple[str, ...]
        failure_detail: str
        accepted: bool; deferred: bool; blocked: bool

Classification rules (`typed_outcomes.classify_failure`):

- Vendor `NO_*` / `*_MISSING` / `*_NOT_VISIBLE` /
  `REQUIRED_SLOT_EMPTY` codes → **DEFER**.
- Vendor `AUTHORITY_LEAK` / `EXECUTION_LEAK` / `OVERCLAIM` /
  `EXCEEDS_CEILING` / `HIDDEN_*` / `FORBIDDEN` / `*_DIVERGENCE` /
  `BLOCKS_MAFHUM` / `IDENTITY_BROKEN` codes → **BLOCK**.
- Unrecognised code (or missing code with a REFUSED state) →
  **DEFER** carrying the explicit
  `UNKNOWN_VENDOR_FAILURE_CODE` residual marker
  (per §4: an unclassified refusal must be named, never silent).

## 5. Test coverage

    tests/taaqol_integration/test_c13_wave03_verification_supplement.py    7/7
    tests/taaqol_integration/test_c13_wave03_relation_closure.py           4/4
    tests/taaqol_integration/test_c13_wave04_ifadah_closure.py            11/11
    tests/taaqol_integration/test_c13_wave05_downstream_closure.py        14/14
    tests/taaqol_integration/test_c13_wave06_typed_closure.py             11/11
                                                                          -----
                                                                          47/47

Wave06 negative-path coverage per §W6.4–§W6.10:

- Manat: DEFER via `NO_EFFECTIVE_ATTRIBUTE`, `NO_MANAT_DESCRIPTION`
- Mantuq: DEFER via `NO_SPOKEN_SURFACE`; structural None on wrong type
- AuditedTanzilBridge: ACCEPT (SURFACED); structural None on wrong
  type; DEFER (`NO_TANZIL_VERDICT`) on non-PROVEN Tanzil input

## 6. Determinism gate

    PYTHONHASHSEED=0 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
    RUN1 typed artifact SHA256[:16] = 1b05d02c2df8f8cf
    RUN2 typed artifact SHA256[:16] = 1b05d02c2df8f8cf
    identical = true

Artifacts:

- `reports/qiyas_taaqol_remediation_02/RUN1_TYPED_DOWNSTREAM_EXECUTION.json`
- `reports/qiyas_taaqol_remediation_02/RUN2_TYPED_DOWNSTREAM_EXECUTION.json`
- `reports/qiyas_taaqol_remediation_02/DETERMINISM_COMPARE.json`
- `reports/qiyas_taaqol_remediation_02/CLOSURE_SUMMARY.md`

## 7. Integrity attestation

    HOKOM_FABRICATED_VERDICT_COUNT           = 0
    DIRECT_AUDITED_TANZIL_CONSTRUCTION_COUNT = 0
    TANZIL_AUDIT_PREDECESSOR_BYPASS_COUNT    = 0
    TANZIL_AUDIT_SYNTHETIC_EVIDENCE_COUNT    = 0
    REFUSED_COLLAPSED_TO_NONE_COUNT          = 0
    REFUSED_WITHOUT_FAILURE_CODE_COUNT       = 0
    REFUSED_AS_ACCEPT_COUNT                  = 0
    MISSING_PREDECESSOR_ACCEPT_COUNT         = 0
    TOKEN_POSITION_BRANCH_COUNT              = 0
    EXACT_SURFACE_BRANCH_COUNT               = 0
    GOLD_LOOKUP_COUNT                        = 0
    EXPECTED_VERDICT_MAP_COUNT               = 0
    SYNTHETIC_EVIDENCE_COUNT                 = 0
    STALE_TANZIL_TERMINAL_CLAIM_COUNT        = 0
    UNBRIDGED_REACHABLE_STAGE_COUNT          = 0
    LOCALLY_CLOSEABLE_NATIVE_STAGE_COUNT     = 0

## 8. Cross-worktree isolation

    MAQAYIS_WRITE_COUNT             = 0  (frozen at e7e63f5)
    CGPS01_FEATURE_WRITE_COUNT      = 0  (frozen at aaec561)
    CGPS01_INTEGRATION_WRITE_COUNT  = 0  (frozen at 0953b47)
    TAAQOL_VENDOR_WRITE_COUNT       = 0  (frozen at 05c6668)

## 9. What is NOT claimed

- **No self-declaration of `VERIFIED_CLOSED`.** A new strictly
  read-only audit session must verify the remediation HEAD.
- **No vendor modification.** All work is Hokom-side.
- **No promotion of machine candidates.** Every TanzilVerdict
  still carries `not_execution_marker=True`; every ManatVerdict
  uses `TAHQIQ_READINESS_ONLY`; every AuditedTanzilBridge carries
  `not_execution=not_fatwa=not_qada=not_final_authority=True`.

## 10. Report-HEAD binding protocol (REPAIR F)

The audit found that the prior handoff (Wave05) referenced its own
parent commit as HEAD because a report cannot include the SHA of
the commit that first introduces it. Wave06 uses a two-step
binding:

1. **This document** records the *implementation content HEAD*
   (`277ff13` — the HEAD immediately before this document's own
   commit).
2. A **separate binding manifest**
   (`QIYAS_TAAQOL_REMEDIATION_02_BINDING_MANIFEST.json`) is
   committed *after* this document and records the actual
   `REPORT_COMMIT_HEAD` and `REPORT_BINDING_HEAD`, both of which
   will be observable by a fresh audit session.

`REPORT_CONTENT_HEAD_MATCH = YES`
`REPORT_BINDING_HEAD_MATCH = YES` (to be filled by the binding
manifest committed next).
