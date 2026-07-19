# Integration Architecture — HOKOM-TAAQOL-LIVE-INTEGRATION-01

## Overview

STRICT, FAIL-CLOSED integration of Taaqol constitutional slot governance into the Hokom Arabic morphology pipeline.

## Module Layout

```
pipeline/
  taaqol_integration/           # Existing integration package
    claim_adapter.py            # bundle_from_hokom_result()
    provider_models.py          # HokomLinguisticClaimBundle
    strict_mode.py              # Existing strict mode (prerequisite tracking)
    live/                       # NEW: Live Taaqol governance (INTEGRATION-01)
      __init__.py               # Package exports
      models.py                 # HokomTaaqolDecision, constants, exceptions
      bridge.py                 # evaluate_hokom_claim_bundle() ← canonical entrypoint
      decision_composition.py   # compose_effective_verdict() ← monotonic composition
      projection.py             # project_bundle_to_claim(), _deterministic_claim_id()
vendor/
  Taaqol-GPT/                   # Unmodified submodule
    src/taaqqul_slot_geometry/  # Python 3.11+ package (StrEnum)
```

## Fail-Closed Pattern

On Python 3.10 (or any ImportError): bridge returns `HokomTaaqolDecision` with:
- `taaqol_verdict = 'DEFERRED'`
- `effective_verdict = 'DEFERRED'` (never LICENSED)
- `fail_closed = True`
- trace event recording the failure

## Monotonic Composition Rule

Upstream Hokom verdict CANNOT be upgraded by Taaqol:
- BLOCKED upstream → always BLOCKED
- DEFERRED upstream → BLOCKED or DEFERRED (never LICENSED)
- ACCEPTED upstream → Taaqol decides (LICENSED / DEFERRED / BLOCKED)

## Gate Constants

- `HOKOM_TAAQOL_BRIDGE_ID = 'HOKOM_TAAQOL_LIVE_BRIDGE'`
- `TAAQOL_INTEGRATION_OWNER = 'HOKOM'`
- `TAAQOL_INTEGRATION_MODE = 'STRICT'`
- `TAAQOL_LIVE_CANONICAL_ENTRYPOINT = 'evaluate_hokom_claim_bundle'`
- `GATE_RANK_CEILING = Rank.STRONG` (from Taaqol)
- `UNGATED_RANK_CEILING = Rank.HYPOTHESIS` (from Taaqol)
