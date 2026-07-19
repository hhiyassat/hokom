# Live Transition Matrix — HOKOM-TAAQOL-LIVE-INTEGRATION-01

## TransitionState → taaqol_verdict Mapping

| TransitionState | taaqol_verdict |
|----------------|---------------|
| APPROVED | LICENSED |
| DEFERRED | DEFERRED |
| BLOCKED | BLOCKED |
| REJECTED | BLOCKED |
| FORBIDDEN_LEAP | BLOCKED |

## GammaResult ClosureState → used as diagnostic only

| ClosureState | Meaning |
|-------------|---------|
| MINIMALLY_CLOSED | All required slots filled, no blocking residuals |
| PERFORATED_CLOSED | Deferrable/non-blocking residuals present |
| BLOCKED | Blocking residuals present |
| OPEN | Required slots empty |
| INVALID | Boundary or structural violation |
| FORBIDDEN_LEAP | Layer jump violation |

## TransitionGate Configuration

- Gate name: `HOKOM_TAAQOL_GATE`
- Gate rank: `Rank.STRONG` (= GATE_RANK_CEILING)
- Target layer: `Layer.CANDIDATE`
- Evidence rank: `Rank.HYPOTHESIS` (from bundle evidence_ids)
- Decision sequence: Γ → Registry → UngatedRank → Evidence → Meet → Approve
