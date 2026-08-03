"""C12 Hokom evidence producers for the Taaqol vertical chain.

Every producer here is fail-closed:
- returns None or a DEFERRED carrier when source-derived evidence is insufficient;
- never invents roots, spans, clauses, relations, maqam, or verdicts;
- carries full provenance/trace/version metadata.

Producers deliberately do not duplicate vendor Taaqol law logic.
They emit the exact typed predecessors that vendor laws consume.
"""
from __future__ import annotations
