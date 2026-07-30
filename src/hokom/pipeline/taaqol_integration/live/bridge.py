"""
Namespace shim: makes hokom.pipeline.taaqol_integration.live.bridge importable
within the src/hokom package namespace (PYTHONPATH=src:).

Root cause of the gap:
  - PYTHONPATH=src: causes 'hokom' → src/hokom/ (canonical stages).
  - src/hokom/ has no pipeline/ subdirectory; the real bridge lives at
    repo-root pipeline/taaqol_integration/live/bridge.py.
  - Any 'from hokom.pipeline...' import therefore raised ImportError.

This shim creates the src/hokom/pipeline/ namespace and re-exports the
canonical bridge symbols so that:

    from hokom.pipeline.taaqol_integration.live.bridge import evaluate_sga_bundle
    from hokom.pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle

resolve correctly in any Python process where the repo root is on sys.path
(guaranteed by pytest.ini pythonpath=. and conftest.py sys.path.insert(0, root)).

No mock. No fake. No patch. The re-exported symbols ARE the canonical bridge.
TAAQOL_FILES_CHANGED=0  SALEH_FILES_CHANGED=0  PIN_CHANGED=NO
"""
from __future__ import annotations

# 'pipeline' here resolves to repo-root pipeline/ (not src/hokom/pipeline/)
# because repo root appears on sys.path before src/ after conftest.py runs.
from pipeline.taaqol_integration.live.bridge import (  # type: ignore[import]
    evaluate_sga_bundle,
    evaluate_hokom_claim_bundle,
)
from pipeline.taaqol_integration.live.models import (  # type: ignore[import]
    HokomTaaqolDecision,
    HokomTaaqolTraceEvent,
)

__all__ = [
    "evaluate_sga_bundle",
    "evaluate_hokom_claim_bundle",
    "HokomTaaqolDecision",
    "HokomTaaqolTraceEvent",
]
