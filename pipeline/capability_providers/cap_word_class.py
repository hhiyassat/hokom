"""
CAP_WORD_CLASS — Formal word class capability provider.

Maps Hokom pipeline word_class output to formal linguistic categories.
Does NOT infer meaning. Provides typed classification only.

Formal categories:
    FI3L (فعل) — Verb
    ISM (اسم) — Noun/Name (includes verbal nouns, adjectives, participles)
    HARF (حرف) — Particle (invariable, grammatical function only)
    KHABAR (خبر) — Predicate (used in special subclasses)

CONSTITUTIONAL: word_class output is FORMAL, not semantic.
    - FI3L_MADI (past verb) ≠ "past event" — timing must come from context
    - ISM_MAFOOL (passive participle) ≠ "something acted upon" — requires clause
    - HARF_JAR ≠ "prepositional meaning" — requires complement
"""
from __future__ import annotations
from .models import CapabilityResult, CapabilityStatus

CAP_WORD_CLASS_ID = "CAP_WORD_CLASS"
SOURCE_MODULE = "pipeline.capability_providers.cap_word_class"

# Formal word class taxonomy (Hokom output → formal label)
WORD_CLASS_MAP: dict[str, tuple[str, str]] = {
    # Verbs
    "FI3L": ("فعل", "Verb"),
    "FI3L_MADI": ("فعل ماضٍ", "Past Verb"),
    "FI3L_MUDARI": ("فعل مضارع", "Present/Future Verb"),
    "FI3L_AMR": ("فعل أمر", "Imperative Verb"),
    # Nouns
    "ISM": ("اسم", "Noun"),
    "ISM_MAFOOL": ("اسم مفعول", "Passive Participle"),
    "ISM_FAIL": ("اسم فاعل", "Active Participle"),
    "ISM_MASDAR": ("مصدر", "Verbal Noun (Masdar)"),
    "ISM_AALAM": ("اسم علم", "Proper Noun"),
    "ISM_NISBAH": ("اسم نسبة", "Relative Adjective"),
    "ISM_TAFDIL": ("اسم تفضيل", "Elative/Comparative"),
    "ISM_ZAMAN": ("اسم زمان", "Noun of Time"),
    "ISM_MAKAN": ("اسم مكان", "Noun of Place"),
    # Pronouns
    "DAMIR": ("ضمير", "Pronoun"),
    "DAMIR_MUNFASIL": ("ضمير منفصل", "Detached Pronoun"),
    "DAMIR_MUTTASIL": ("ضمير متصل", "Attached Pronoun"),
    # Particles
    "HARF": ("حرف", "Particle"),
    "HARF_JAR": ("حرف جر", "Preposition"),
    "HARF_ATF": ("حرف عطف", "Conjunction"),
    "HARF_NIDA": ("حرف نداء", "Vocative Particle"),
    "HARF_SHART": ("حرف شرط", "Conditional Particle"),
    "HARF_NAFI": ("حرف نفي", "Negation Particle"),
    "HARF_JAWAB": ("حرف جواب", "Response Particle"),
    "HARF_TAHQIQ": ("حرف تحقيق", "Affirmation Particle"),
    # Special
    "ISM_MAWSOOL": ("اسم موصول", "Relative Pronoun/Noun"),
    "ISM_ISHARAH": ("اسم إشارة", "Demonstrative"),
    "ISM_SHART": ("اسم شرط", "Conditional Noun"),
    "ISM_ISTIFHAM": ("اسم استفهام", "Interrogative Noun"),
    "UNKNOWN": ("مجهول", "Unknown"),
}

def CAP_WORD_CLASS(hokom_result: dict) -> CapabilityResult:
    """
    Extract word class capability from Hokom pipeline result.
    Returns CapabilityResult with formal Arabic/English labels.
    """
    wc = hokom_result.get("word_class", {})
    word_class = wc.get("word_class") or wc.get("class") or "UNKNOWN"
    verdict = wc.get("verdict", "")

    if not word_class or word_class == "UNKNOWN":
        return CapabilityResult(
            capability_id=CAP_WORD_CLASS_ID,
            status=CapabilityStatus.DEFERRED,
            value=None,
            value_ar=None,
            value_en=None,
            evidence_ids=(),
            residuals=("WORD_CLASS_NOT_DETERMINED",),
            source_module=SOURCE_MODULE,
        )

    ar_label, en_label = WORD_CLASS_MAP.get(word_class, ("مجهول", word_class))
    status = CapabilityStatus.PROVIDED if "ACCEPT" in verdict.upper() else CapabilityStatus.AMBIGUOUS

    return CapabilityResult(
        capability_id=CAP_WORD_CLASS_ID,
        status=status,
        value=word_class,
        value_ar=ar_label,
        value_en=en_label,
        evidence_ids=(f"hokom.word_class:{word_class}",),
        residuals=() if status == CapabilityStatus.PROVIDED else ("WORD_CLASS_VERDICT_UNCLEAR",),
        source_module=SOURCE_MODULE,
    )
