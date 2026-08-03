"""
madlul_provider.py — Evidence-bound Madlul (signified) candidate provider.

CONSTITUTIONAL CONSTRAINTS:
    - Every madlul needs sense_id and source_type (LEXICAL_ENTRY | CORPUS_EVIDENCE | GRAMMATICAL_FUNCTION)
    - Multiple senses remain multiple until context constrains them
    - Absence of distinguisher → AMBIGUOUS or DEFERRED, not arbitrarily picked
    - No LLM-generated sense as primary evidence
"""
from __future__ import annotations
from .models import MadlulCandidate, MadlulStatus
import uuid

class MadlulProvider:
    SOURCE_MODULE = "pipeline.semantic_providers.madlul_provider"

    def from_dal_claim_and_hokom(self, dal_claim, hokom_result: dict) -> MadlulCandidate:
        """
        Build MadlulCandidate from a licensed DalClaim + Hokom result.
        Does not infer meaning. Only provides grammatical-function sense for
        closed-class words and defers for open-class without lexical evidence.
        """
        from .models import DalStatus
        surface = hokom_result.get("original_surface", "")
        wc = hokom_result.get("word_class", {})
        word_class = wc.get("word_class") or "UNKNOWN"

        # Closed-class functional words have grammatical-function senses
        CLOSED_CLASS = {"HARF", "DAMIR", "DAMIR_MUNFASIL", "DAMIR_MUTTASIL"}

        if not dal_claim.is_licensed():
            return MadlulCandidate(
                candidate_id=f"MADLUL-{uuid.uuid4().hex[:8]}",
                sense_id="DEFERRED_DAL_NOT_LICENSED",
                source_type="NONE",
                source_reference="dal_not_licensed",
                ambiguity=False,
                constraining_context=None,
                status=MadlulStatus.DEFERRED,
                evidence_ids=(),
                residuals=("DAL_NOT_LICENSED",),
            )

        if word_class in CLOSED_CLASS:
            return MadlulCandidate(
                candidate_id=f"MADLUL-{uuid.uuid4().hex[:8]}",
                sense_id=f"GF:{word_class}:{surface}",
                source_type="GRAMMATICAL_FUNCTION",
                source_reference=f"hokom.word_class.closed_class:{word_class}",
                ambiguity=False,
                constraining_context=None,
                status=MadlulStatus.LICENSED,
                evidence_ids=(f"word_class:{word_class}",),
                residuals=(),
            )

        # Open-class words without explicit lexical evidence → DEFERRED
        return MadlulCandidate(
            candidate_id=f"MADLUL-{uuid.uuid4().hex[:8]}",
            sense_id="DEFERRED_REQUIRES_LEXICAL_SOURCE",
            source_type="NONE",
            source_reference="no_lexical_evidence_available",
            ambiguity=True,
            constraining_context="requires explicit lexical_evidence corpus entry",
            status=MadlulStatus.DEFERRED,
            evidence_ids=tuple(dal_claim.evidence_ids),
            residuals=("NO_LEXICAL_EVIDENCE_SOURCE", "OPEN_CLASS_WITHOUT_CORPUS_ENTRY"),
        )
