"""
dal_provider.py — Evidence-bound Dal (signifier) provider.

CONSTITUTIONAL CONSTRAINTS:
    - No root→meaning direct inference
    - No wazn→meaning direct inference  
    - No word_class→meaning direct inference
    - No LLM-generated meaning as evidence
    - Every dal claim carries source module path
    - Absence of lexical distinguisher → DEFER
    - Multiple senses remain multiple until context constrains
"""
from __future__ import annotations
from .models import DalClaim, DalStatus
import uuid

class DalProvider:
    """Provides typed DalClaim carriers from Hokom pipeline output."""

    SOURCE_MODULE = "pipeline.semantic_providers.dal_provider"

    def from_hokom_result(self, hokom_result: dict) -> DalClaim:
        """
        Build a DalClaim from a Hokom pipeline result dict.
        Never infers meaning. Only extracts identity and grammatical function.
        """
        surface = hokom_result.get("original_surface", "")
        seg = hokom_result.get("segmentation", {})
        wc = hokom_result.get("word_class", {})
        ra = hokom_result.get("root_analysis", {})

        # Lexical identity = surface + word_class + grammatical function (NOT meaning)
        word_class = wc.get("word_class") or "UNKNOWN"
        grammatical_function = wc.get("word_subclass") or ""
        root_state = ra.get("root_state") or "UNKNOWN"

        # Status determination:
        # If word class is accepted AND root is known → DOMAIN_ACCEPTED
        # If word class is accepted but root deferred → CANDIDATE
        # If word class is functional (particle/pronoun) → DOMAIN_ACCEPTED (lexical lookup possible)
        # If error → DEFERRED
        if hokom_result.get("error"):
            status = DalStatus.DEFERRED
        elif word_class in ("HARF", "DAMIR", "KHABAR"):
            # Functional words: domain accepted via closed-class lookup
            status = DalStatus.DOMAIN_ACCEPTED
        elif root_state == "KNOWN" and word_class not in ("UNKNOWN", None):
            status = DalStatus.DOMAIN_ACCEPTED
        elif word_class not in ("UNKNOWN", None):
            status = DalStatus.CANDIDATE
        else:
            status = DalStatus.DEFERRED

        evidence_ids = []
        if word_class:
            evidence_ids.append(f"word_class:{word_class}")
        if root_state == "KNOWN":
            evidence_ids.append(f"root:{ra.get('canonical_root', '')}")

        residuals = []
        if status == DalStatus.DEFERRED:
            residuals.append("NO_LEXICAL_IDENTITY_ESTABLISHED")
        if root_state == "DEFERRED":
            residuals.append("ROOT_DEFERRED_DAL_CANDIDATE_ONLY")

        return DalClaim(
            claim_id=f"DAL-{uuid.uuid4().hex[:8]}",
            surface=surface,
            lexical_identity=f"{word_class}:{grammatical_function}",
            lexical_sense_candidate=None,   # not yet resolved — requires lexical lookup
            contextual_usage=grammatical_function or None,
            status=status,
            evidence_ids=tuple(evidence_ids),
            contradictions=(),
            residuals=tuple(residuals),
            source_module=self.SOURCE_MODULE,
        )
