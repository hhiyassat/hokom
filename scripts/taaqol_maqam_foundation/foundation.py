#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_THEORY_FOUNDATION_IMPLEMENTATION_WITH_TRACEABILITY — foundation layer.

Founds the maqām theory programmatically (it does NOT claim to close the whole theory). It adds, on top
of the existing core in taaqol_maqam_theory_implementation_01:
  - a versioned CORE dimension registry + an OPEN extension registry (unknown => DEFER_OR_REGISTER,
    never a silent drop),
  - the full evidence-rank ladder including EXTERNALLY_SUPPLIED,
  - the four scholarly branches (linguists / rhetoricians / uṣūliyyīn / tafsīr),
  - an ACTIVE scope-match check (scope is enforced, not merely stored),
  - the MAQAM != NORMATIVE guard set.

Constitutional limit: maqām never produces a normative source / ḥukm / ʿillah / manāṭ / tanzīl / final
answer. This module contains no fiqh rule and authors no owner data.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from enum import Enum, IntEnum

FOUNDATION_LABEL = "MAQAM_THEORY_FOUNDATION_IMPLEMENTATION_WITH_TRACEABILITY"
CORE_REGISTRY_VERSION = "v1.0.0"


# ---------------------------------------------------------------- evidence rank ladder (full)
class EvidenceRankFull(IntEnum):
    GENERATED = 10
    TEXTUAL_INFERENCE = 20
    OBSERVED = 30
    EXTERNALLY_SUPPLIED = 40
    OWNER_DECLARED = 50
    RATIFIED = 60


RANK_LADDER = [r.name for r in sorted(EvidenceRankFull, key=int)]


# ---------------------------------------------------------------- four scholarly branches
class MaqamScholarlyBranch(str, Enum):
    MAQAM_IN_LINGUISTS = "MAQAM_IN_LINGUISTS"
    MAQAM_IN_RHETORICIANS = "MAQAM_IN_RHETORICIANS"
    MAQAM_IN_USULIYYIN = "MAQAM_IN_USULIYYIN"
    MAQAM_IN_TAFSIR = "MAQAM_IN_TAFSIR"

    def __str__(self) -> str:
        return self.value


FOUR_BRANCHES = tuple(b.value for b in MaqamScholarlyBranch)


# ---------------------------------------------------------------- MAQAM != NORMATIVE guard
MAQAM_FORBIDDEN_TARGETS = frozenset({
    "NORMATIVE_SOURCE", "NORMATIVE_HUKM", "ILLAH", "MANAT", "TANZIL",
    "FINAL_ANSWER", "SPEECH_ACT_ONLY", "GENRE_ONLY", "FACTUAL_CLAIM", "PROVEN_FACT",
})


class MaqamOverreachError(Exception):
    """Raised if the maqām layer is asked to become/produce a normative artifact."""


def assert_maqam_not_normative(target: str) -> str:
    """Guard: maqām may not be equated with or produce a normative/downstream artifact."""
    t = str(target).strip().upper()
    if t in MAQAM_FORBIDDEN_TARGETS:
        raise MaqamOverreachError(f"MAQAM_MUST_NOT_PRODUCE_OR_EQUAL:{t}")
    return "MAQAM_SCOPE_OK"


# ---------------------------------------------------------------- dimension registries
CORE_DIMENSIONS = (
    "SPEAKER", "SPEAKER_ROLE", "SPEAKER_INTENT", "ADDRESSEE", "ADDRESSEE_ROLE",
    "ADDRESSEE_KNOWLEDGE", "PURPOSE", "SPEECH_EVENT", "SPEECH_ACT", "COMMITMENT",
    "GENRE", "DOMAIN", "TIME", "PLACE", "SOURCE_PROVENANCE", "REFERENCE_WORLD",
    "SHARED_KNOWLEDGE", "SOCIAL_CUSTOM", "LINGUISTIC_CUSTOM", "HISTORICAL_CONTEXT",
    "CULTURAL_CONTEXT", "PRIOR_DISCOURSE", "FOLLOWING_DISCOURSE", "PHYSICAL_SITUATION",
    "EMBODIED_CUE", "GESTURE", "FACIAL_EXPRESSION", "PROSODY", "MEDIUM",
    "AUTHORITY_CONTEXT", "DISPUTE_CONTEXT",
)

# resolution outcomes for a dimension key
RESOLVE_CORE = "CORE"
RESOLVE_EXTENSION = "EXTENSION_REGISTERED"
RESOLVE_DEFER = "DEFER_UNKNOWN_DIMENSION"


@dataclass
class MaqamDimensionRegistry:
    """Versioned core set (ratified) + open extension set under governance.

    An unknown key is NEVER silently dropped: it is either registered as an extension (governed) or
    deferred with a reason. Silent drop is forbidden by construction (resolve() always returns a status).
    """
    version: str = CORE_REGISTRY_VERSION
    core: tuple = CORE_DIMENSIONS
    extensions: dict = field(default_factory=dict)  # key -> governance note
    deferred: dict = field(default_factory=dict)    # key -> reason

    def is_core(self, key: str) -> bool:
        return key in self.core

    def register_extension(self, key: str, governance_note: str) -> str:
        key = str(key).strip()
        if not key:
            raise ValueError("extension key must be non-empty")
        if key in self.core:
            return RESOLVE_CORE
        if not governance_note.strip():
            # cannot register without governance -> defer, do not drop
            self.deferred[key] = "NO_GOVERNANCE_NOTE"
            return RESOLVE_DEFER
        self.extensions[key] = governance_note.strip()
        self.deferred.pop(key, None)
        return RESOLVE_EXTENSION

    def resolve(self, key: str) -> str:
        key = str(key).strip()
        if key in self.core:
            return RESOLVE_CORE
        if key in self.extensions:
            return RESOLVE_EXTENSION
        # unknown -> defer (register a reason); NEVER drop silently
        self.deferred.setdefault(key, "UNKNOWN_DIMENSION_DEFERRED_PENDING_GOVERNANCE")
        return RESOLVE_DEFER


# ---------------------------------------------------------------- active scope match
def scope_within(evidence_scope: str, required_scope: str) -> bool:
    """A scope is enforced (not just stored): evidence scope must equal the required scope or be a
    strict sub-scope of it (path-prefixed with '/')."""
    e = str(evidence_scope).strip()
    r = str(required_scope).strip()
    if not e or not r:
        return False
    return e == r or e.startswith(r + "/")


# ---------------------------------------------------------------- artifact emitters
def core_registry_payload() -> dict:
    return {"label": FOUNDATION_LABEL, "version": CORE_REGISTRY_VERSION,
            "core_dimensions": list(CORE_DIMENSIONS), "count": len(CORE_DIMENSIONS),
            "core_dimensions_policy": "VERSIONED_RATIFIED_SET",
            "silent_dimension_drop": "FORBIDDEN"}


def extension_registry_payload() -> dict:
    return {"label": FOUNDATION_LABEL, "extension_policy": "OPEN_UNDER_GOVERNANCE",
            "unknown_dimension_policy": "DEFER_OR_REGISTER",
            "silent_dimension_drop": "FORBIDDEN",
            "seed_extensions": []}


def evidence_schema_payload() -> dict:
    return {"label": FOUNDATION_LABEL,
            "rank_ladder": RANK_LADDER,
            "required_fields": ["evidence_id", "dimension_key", "value", "source_ref", "producer",
                                "evidence_type", "rank", "scope", "reference_world", "valid_from",
                                "valid_to", "trace_ref", "confidence_rank", "owner_approval_status",
                                "residuals"],
            "rank_separation_rule": "TEXTUAL_INFERENCE < EXTERNALLY_SUPPLIED < OWNER_DECLARED < RATIFIED",
            "text_cue_is_not_owner_decision": "YES"}


def consumer_profiles_payload() -> dict:
    return {"label": FOUNDATION_LABEL,
            "consumers": [
                {"consumer": "EARLY_INTERPRETATION", "required_scope": "ARABIC_UNDERSTANDING/EARLY_INTERPRETATION",
                 "note": "interpretive; may constrain/prefer candidates, never authors meaning"},
                {"consumer": "PROPOSITION_INTERPRETATION", "required_scope": "ARABIC_UNDERSTANDING/PROPOSITION_INTERPRETATION",
                 "note": "defers if a reference world is required and undeclared"},
                {"consumer": "FACTUAL_CLAIM_BIRTH", "required_scope": "ARABIC_UNDERSTANDING/FACTUAL_CLAIM_BIRTH",
                 "note": "requires owner-declared speaker/addressee/purpose/speech_act/commitment/reference_world"},
            ],
            "scholarly_branches": list(FOUR_BRANCHES),
            "maqam_forbidden_targets": sorted(MAQAM_FORBIDDEN_TARGETS)}


def write_artifacts(out_dir: str) -> dict:
    d = pathlib.Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    files = {
        "MAQAM_CORE_DIMENSION_REGISTRY.json": core_registry_payload(),
        "MAQAM_EXTENSION_REGISTRY.json": extension_registry_payload(),
        "MAQAM_EVIDENCE_SCHEMA.json": evidence_schema_payload(),
        "MAQAM_CONSUMER_PROFILES.json": consumer_profiles_payload(),
    }
    written = {}
    for name, payload in files.items():
        (d / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        written[name] = str(d / name)
    return written


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    for name, path in write_artifacts(a.out_dir).items():
        print("ARTIFACT=" + path)
    print("FOUR_BRANCHES=" + ";".join(FOUR_BRANCHES))
    print("RANK_LADDER=" + ";".join(RANK_LADDER))
    print("CORE_DIMENSIONS=" + str(len(CORE_DIMENSIONS)))
