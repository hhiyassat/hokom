from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from pipeline.clause_graph.models import ClauseBoundaryType, ClauseStatus, ClauseCandidate

def test_clause_status_values():
    assert ClauseStatus.CANDIDATE == "CANDIDATE"
    assert ClauseStatus.BLOCKED == "BLOCKED"

def test_clause_candidate_creation():
    c = ClauseCandidate(
        clause_id="AD-C01",
        token_start=1,
        token_end=4,
        surface="يَا أَيُّهَا",
        boundary_evidence=("structural",),
        operators=("يَا",),
        main_predicate_candidates=("آمَنُوا",),
        argument_candidates=(),
        references=(),
        active_residuals=(),
        status=ClauseStatus.CANDIDATE,
    )
    assert c.clause_id == "AD-C01"
    assert c.token_end == 4
