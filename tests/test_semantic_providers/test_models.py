from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from pipeline.semantic_providers.models import DalStatus, MadlulStatus, DalClaim

def test_dal_claim_is_licensed_only_when_constitutionally_licensed():
    dc = DalClaim(
        claim_id="DAL-test",
        surface="كَاتِبٌ",
        lexical_identity="FI3L_MUFRAD",
        lexical_sense_candidate=None,
        contextual_usage="agent",
        status=DalStatus.DOMAIN_ACCEPTED,
        evidence_ids=("word_class:FI3L",),
        contradictions=(),
        residuals=(),
        source_module="test",
    )
    assert not dc.is_licensed(), (
        "DOMAIN_ACCEPTED is NOT licensed — only CONSTITUTIONALLY_LICENSED passes is_licensed()"
    )

def test_dal_claim_is_licensed_when_constitutionally_licensed():
    dc = DalClaim(
        claim_id="DAL-test2",
        surface="كَاتِبٌ",
        lexical_identity="FI3L_MUFRAD",
        lexical_sense_candidate=None,
        contextual_usage=None,
        status=DalStatus.CONSTITUTIONALLY_LICENSED,
        evidence_ids=(),
        contradictions=(),
        residuals=(),
        source_module="test",
    )
    assert dc.is_licensed()
