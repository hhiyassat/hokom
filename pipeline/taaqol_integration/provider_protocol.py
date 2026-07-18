"""
LinguisticClaimProvider protocol -- the only interface Taaqol uses to receive Hokom output.
Hokom is NOT a ModelClient. Hokom is NOT a concrete LLM adapter.
"""
from __future__ import annotations
from typing import Protocol, runtime_checkable
from .provider_models import HokomLinguisticClaimBundle


@runtime_checkable
class LinguisticClaimProvider(Protocol):
    """
    Hokom must implement this protocol to be admitted as a claim provider.
    This protocol does NOT grant constitutional rank or successor creation.
    """
    provider_id: str
    engine_version: str
    callable_surface: str       # description of what surfaces can be analyzed
    output_schema: str          # description of output bundle schema

    def analyze_token(self, surface: str) -> HokomLinguisticClaimBundle:
        """
        Analyze a single Arabic token surface and return a typed claim bundle.
        MUST NOT:
        - return raw dict
        - inject Taaqol rank
        - write to Taaqol ledger
        - create successors
        - suppress residuals
        - make network calls
        """
        ...
