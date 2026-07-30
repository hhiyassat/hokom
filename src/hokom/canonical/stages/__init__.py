"""
hokom.canonical.stages — 19-stage canonical pipeline adapters.

Each stage adapter:
    1. Receives a StageInput (previous stage's CanonicalCandidateSet +
       raw Hokom evidence from the appropriate Hokom pipeline module)
    2. Consults the Saleh LayerSpec contract (via registry snapshot)
    3. Evaluates evidence against conditions/blockers
    4. Produces a CanonicalCandidateSet
    5. Requests Taaqol licensing via the bridge

Stage ownership boundaries (BINDING):
    - Hokom owns all Arabic morphological evidence (P0-P12)
    - Saleh owns the transition contracts / stage specs
    - Taaqol owns licensing decisions
    - HR2S / H2RS: FORBIDDEN in any adapter
"""
from .base import StageAdapter, StageInput, StageOutput

__all__ = ["StageAdapter", "StageInput", "StageOutput"]
