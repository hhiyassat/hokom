# MAQAM_CANONICAL_INTEGRATION_BLOCKER_REPORT_02

**CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE** · maqām remains a *foundation*, not a canonical closure.
This round does **not** open canonical integration; it only sharpens the blocker.

## Precise cause
- No **ratified canonical contract** defines how a scoped maqām certificate enters the runtime pipeline.
- No **ratified typed adapter** exists between `maqam_foundation` and the Hokom/Taaqol canonical path.
- Canonical must **not** be opened from a report or from an example context.
- An example maqām must **not** be turned into an owner decision.
- maqām must **not** generate any normative output.

## required_contracts
1. A ratified canonical contract: maqām-certificate → runtime consumer (binds dimension + scope + rank).
2. A ratified handoff contract stating which consumers may consume maqām certificates in canonical runtime.

## required_adapters
1. Typed adapter `maqam_foundation → Hokom` (Hokom stays the Arabic-analysis owner; no free dicts).
2. Typed adapter `maqam_foundation → Taaqol canonical path` (typed certificates only).

## required_tests
- adapter schema tests; scope/rank preservation across the adapter;
- no-normative-leak across integration; determinism across integration.

## forbidden_shortcuts
- opening canonical from a report; example-context → owner decision;
- producing normative output from maqām; any silent fallback.

## owner_decisions_needed
- ratify the canonical maqām contract;
- ratify the typed adapters;
- declare the canonical-runtime maqām consumers.

Until these are ratified, the maqām foundation stays **independent and typed**; no canonical gate opens.
