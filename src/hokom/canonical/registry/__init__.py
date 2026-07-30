"""
hokom.canonical.registry — Saleh/Qiyas registry provenance snapshot.

Public API:
    load_snapshot()            → RegistrySnapshot
    get_layer(layer_id)        → LayerEntry
    canonical_order()          → list[str]
    terminal_layer_id()        → str
    assert_no_p13()
"""
from .saleh_snapshot import (
    RegistrySnapshot,
    LayerEntry,
    ProvenanceRecord,
    load_snapshot,
    get_layer,
    canonical_order,
    terminal_layer_id,
    assert_no_p13,
    CANONICAL_LAYER_IDS,
)

__all__ = [
    "RegistrySnapshot",
    "LayerEntry",
    "ProvenanceRecord",
    "load_snapshot",
    "get_layer",
    "canonical_order",
    "terminal_layer_id",
    "assert_no_p13",
    "CANONICAL_LAYER_IDS",
]
