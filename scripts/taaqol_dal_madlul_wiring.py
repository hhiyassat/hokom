#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_NAZILA_DAL_LICENSE_AND_MINI_MADLUL_REGISTRY_01
taaqol_dal_madlul_wiring.py

Wires the EXISTING Hokom semantic providers into the Taaqol layer:
    Hokom analysis → DalProvider → dal_licensing_gate → MadlulProvider → DalMadlulBinding

Constitutional constraints:
  - Hokom OWNS the Arabic analysis (word_class/dal_kind come from Hokom; the wiring only
    LICENSES the dal on explicit conditions, it does not re-analyze).
  - Dal is promoted to CONSTITUTIONALLY_LICENSED ONLY under explicit conditions (no blanket
    promotion), carrying cause/conditions/preventers/verdict/evidence_refs/residuals.
  - MadlulProvider is called AFTER the licensing gate.
  - MADLUL is a real signified: GRAMMATICAL_FUNCTION for closed-class function words (code-derived),
    or a LEXICAL_ENTRY/CORPUS_EVIDENCE that is OWNER-APPROVED in the mini-registry. Otherwise
    OWNER_PENDING → no madlul (never invented, never from the reference, never root/wazn/lemma/relation).
"""
from __future__ import annotations
import csv
import dataclasses
import os

REPO = "/Users/husseinhiyassat/hokom"
REGISTRY_PATH = os.path.join(REPO, "data", "taaqol", "approved_madlul_registry_nazila_minimal.csv")

REGISTRY_COLUMNS = [
    "entry_id", "token_id", "surface", "normalized_surface", "lemma", "hokom_pos", "dal_kind",
    "sense_id", "madlul_text_ar", "source_type", "source_reference",
    "owner_approval_status", "license_status", "evidence_refs", "residuals",
]

# owner-approval vocabulary (TAAQOL_NAZILA_OWNER_APPROVE_MINIMAL_MADLUL_ENTRIES_01)
OWNER_APPROVED_STATUS = "OWNER_APPROVED_FOR_NAZILA_FIXTURE"
OWNER_APPROVED_SOURCE_REF = "OWNER_APPROVED_NAZILA_MINIMAL_FIXTURE"

WIRING_COLUMNS = [
    "token_id", "surface", "dal_status", "dal_license_status", "dal_license_cause",
    "dal_license_conditions", "dal_license_preventers", "madlul_status", "madlul_source_type",
    "madlul_sense_id", "binding_status", "registry_lookup", "owner_approval_status",
    "verdict", "evidence_refs", "residuals",
    # position-only wiring (WIRE_ARABIC_NET_POSITION_SOURCE_INTO_LIVE_DAL_MADLUL_BINDING_01):
    # a registered-source semantic POSITION reflected onto the live row, never a licensed meaning.
    "madlul_position", "position_source", "position_status",
]

CLOSED_CLASS = ("HARF", "DAMIR", "DAMIR_MUNFASIL", "DAMIR_MUTTASIL")


def _corrected_hokom_result(hr):
    """Map Hokom's word_class key `class` → the key the providers read (`word_class`),
    using Hokom's OWN value. This is an adapter, not a re-analysis."""
    hr2 = dict(hr)
    wc = dict(hr.get("word_class") or {})
    wc["word_class"] = wc.get("class")
    wc["word_subclass"] = wc.get("subclass")
    hr2["word_class"] = wc
    return hr2


def dal_licensing_gate(dal, hr, corrected):
    """Promote a DalClaim to CONSTITUTIONALLY_LICENSED ONLY if explicit conditions hold."""
    from pipeline.semantic_providers.models import DalStatus
    wc = (corrected.get("word_class") or {}).get("word_class")
    verdict_hokom = (hr.get("word_class") or {}).get("verdict")
    conditions, preventers = [], []

    # explicit conditions
    (conditions if wc else preventers).append("hokom_word_class_present" if wc else "NO_WORD_CLASS")
    (conditions if not hr.get("error") else preventers).append(
        "no_hokom_error" if not hr.get("error") else "HOKOM_ERROR")
    blocked = (verdict_hokom == "WORD_CLASS_BLOCKED")
    (conditions if not blocked else preventers).append(
        "no_hokom_block" if not blocked else "HOKOM_WORD_CLASS_BLOCKED")
    contradiction = (dal.status == DalStatus.BLOCKED)
    (conditions if not contradiction else preventers).append(
        "no_dal_analysis_contradiction" if not contradiction else "DAL_ANALYSIS_CONTRADICTION")
    ev_ok = bool(dal.evidence_ids) or bool(dal.surface)
    (conditions if ev_ok else preventers).append("evidence_refs_present" if ev_ok else "NO_EVIDENCE_REFS")

    licensed = not preventers
    status = DalStatus.CONSTITUTIONALLY_LICENSED if licensed else dal.status
    dal2 = dataclasses.replace(dal, status=status)
    return {
        "dal": dal2, "licensed": licensed,
        "cause": "hokom_evidence_meets_explicit_license_conditions" if licensed else "conditions_not_met",
        "conditions": ";".join(conditions) or "none",
        "preventers": ";".join(preventers) or "none",
        "verdict": "CONSTITUTIONALLY_LICENSED" if licensed else "DAL_" + getattr(dal.status, "value", str(dal.status)),
        "evidence_refs": ";".join(dal.evidence_ids) or f"surface:{dal.surface}",
        "residuals": ";".join(dal.residuals) or "none",
    }


def _pending_row(entry_id, token_id, surface, pos, dal_kind):
    """A canonical OWNER_PENDING registry row (rule 1). No meaning is entered."""
    return {
        "entry_id": entry_id, "token_id": token_id, "surface": surface,
        "normalized_surface": surface, "lemma": "PENDING", "hokom_pos": pos,
        "dal_kind": dal_kind, "sense_id": "OWNER_PENDING", "madlul_text_ar": "OWNER_PENDING",
        "source_type": "NONE", "source_reference": "PENDING",
        "owner_approval_status": "OWNER_PENDING", "license_status": "NOT_LICENSED",
        "evidence_refs": f"surface:{surface}",
        "residuals": "OWNER_APPROVAL_REQUIRED;MEANING_NOT_INVENTED",
    }


def _ensure_registry(open_class_tokens):
    """Create/UPDATE the mini-registry. The registry is OWNER-CURATED: any row already present
    is PRESERVED verbatim (owner approvals, owner-set residuals, verbatim madlul) — only its
    token_id is kept current. A canonical OWNER_PENDING row is created ONLY for a token that has
    no entry yet. Owner-approved rows that are not open-class content tokens (e.g. the particle
    عَنْ) are also kept. Nothing is ever clobbered and no meaning is invented."""
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    existing = {}
    if os.path.exists(REGISTRY_PATH):
        for r in csv.DictReader(open(REGISTRY_PATH, encoding="utf-8")):
            existing[r.get("surface")] = r
    rows, seen = [], set()
    for i, (token_id, surface, pos, dal_kind) in enumerate(open_class_tokens):
        if surface in existing:
            row = {c: existing[surface].get(c, "") for c in REGISTRY_COLUMNS}
            row["token_id"] = token_id  # keep token_id current
        else:
            row = _pending_row(f"MADLUL-PENDING-{i:03d}", token_id, surface, pos, dal_kind)
        rows.append(row); seen.add(surface)
    # keep any existing rows not among the open-class tokens (e.g. the approved particle عَنْ)
    for surface, src in existing.items():
        if surface not in seen:
            rows.append({c: src.get(c, "") for c in REGISTRY_COLUMNS})
    with open(REGISTRY_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(REGISTRY_COLUMNS)
        for row in rows:
            w.writerow([row.get(c, "") for c in REGISTRY_COLUMNS])


def load_registry():
    if not os.path.exists(REGISTRY_PATH):
        return {}
    out = {}
    for r in csv.DictReader(open(REGISTRY_PATH, encoding="utf-8")):
        out[r["surface"]] = r
    return out


OWNER_APPROVED_SOURCE_TYPES = ("LEXICAL_ENTRY", "GRAMMATICAL_FUNCTION")


def _registry_approved_madlul(reg):
    """Return an owner-APPROVED madlul dict for a registry row, or None (rule 2).
    Only an explicit owner approval with a real madlul_text_ar counts — never invented,
    never from reference/relation/root/wazn/lemma. The owner declares the source_type
    (LEXICAL_ENTRY for a lexical sense, or GRAMMATICAL_FUNCTION for a function word)."""
    if not reg:
        return None
    if (reg.get("owner_approval_status") == OWNER_APPROVED_STATUS
            and reg.get("license_status") == "CONSTITUTIONALLY_LICENSED"
            and reg.get("source_type") in OWNER_APPROVED_SOURCE_TYPES
            and reg.get("madlul_text_ar") not in ("", None, "OWNER_PENDING", "PENDING")
            and reg.get("sense_id") not in ("", None, "OWNER_PENDING", "PENDING")):
        return {"sense_id": reg["sense_id"], "madlul_text_ar": reg["madlul_text_ar"],
                "source_type": reg["source_type"],
                "source_reference": reg.get("source_reference") or OWNER_APPROVED_SOURCE_REF,
                "evidence_refs": reg.get("evidence_refs") or f"owner_approval:{reg.get('token_id')}"}
    return None


def wire_dal_madlul(analyses):
    """Full wiring over the sentence. Returns per-token rows + summary + bound token ids."""
    from scripts.demo_ayat_al_dayn import process_token_full
    from pipeline.semantic_providers.dal_provider import DalProvider
    from pipeline.semantic_providers.madlul_provider import MadlulProvider
    dp, mp = DalProvider(), MadlulProvider()

    # ensure a mini-registry exists for the open-class content tokens (token_id carried)
    open_rows = []
    for i, a in enumerate(analyses):
        wc = (a.get("word_class") or "").split("/")[0]
        if wc not in CLOSED_CLASS and wc not in ("HARF_CANDIDATE",):
            open_rows.append((a.get("token_id") or f"t{i:03d}", a.get("original_surface"),
                              wc or "UNKNOWN", "OPEN_CLASS_DAL"))
    _ensure_registry(open_rows)
    registry = load_registry()

    rows, bound_tokens = [], set()
    for i, a in enumerate(analyses):
        surface = a.get("original_surface")
        hr = process_token_full(0, surface)
        corrected = _corrected_hokom_result(hr)
        wc = (corrected.get("word_class") or {}).get("word_class")
        is_closed = wc in CLOSED_CLASS
        dal = dp.from_hokom_result(corrected)
        gate = dal_licensing_gate(dal, hr, corrected)
        madlul = mp.from_dal_claim_and_hokom(gate["dal"], corrected)
        m_status = getattr(madlul.status, "value", str(madlul.status))
        m_src = madlul.source_type
        m_sense = madlul.sense_id

        # registry lookup for open-class: an owner-APPROVED lexical entry is the ONLY
        # licensed lexical madlul source (the reference/relation/root/wazn/lemma/LLM are not).
        reg = registry.get(surface)
        approved = _registry_approved_madlul(reg)
        owner_status = (reg or {}).get("owner_approval_status", "N/A" if is_closed else "OWNER_PENDING")
        if is_closed:
            reg_lookup = "GRAMMATICAL_FUNCTION"
        elif approved:
            reg_lookup = "OWNER_APPROVED"
        else:
            reg_lookup = "OWNER_PENDING"

        # position-only wiring defaults (reflected onto the row below; never a licensed meaning)
        madlul_position, position_source, position_status = "none", "NONE", "NOT_DERIVED"

        # binding: licensed dal + licensed madlul (GF for closed; owner-approved lexical for open)
        if gate["licensed"] and m_status == "LICENSED" and m_src == "GRAMMATICAL_FUNCTION":
            binding = "BOUND"; verdict = "DAL_MADLUL_BOUND_GRAMMATICAL_FUNCTION"; bound_tokens.add(f"t{i:03d}")
            resid = "closed_class_grammatical_function_madlul"
        elif gate["licensed"] and approved:
            # owner-approved madlul supplied from the registry (never invented); the owner
            # declared the source_type (LEXICAL_ENTRY sense, or GRAMMATICAL_FUNCTION function word)
            m_status = "LICENSED"; m_src = approved["source_type"]; m_sense = approved["sense_id"]
            binding = "BOUND"; bound_tokens.add(f"t{i:03d}")
            verdict = ("DAL_MADLUL_BOUND_OWNER_APPROVED_LEXICON" if m_src == "LEXICAL_ENTRY"
                       else "DAL_MADLUL_BOUND_OWNER_APPROVED_GRAMMATICAL_FUNCTION")
            resid = "owner_approved_madlul;" + approved["evidence_refs"]
        elif not gate["licensed"]:
            binding = "DEFERRED"; verdict = "DAL_LICENSE_BLOCKED"; resid = "DAL_NOT_LICENSED;" + gate["preventers"]
        else:
            binding = "DEFERRED"; verdict = "MADLUL_OWNER_PENDING"; resid = "APPROVED_LEXICAL_MADLUL_SOURCE_MISSING;OWNER_PENDING"
            # Position-only wiring: reflect a registered-source semantic POSITION (synset) onto the
            # live row via the Hokom surface→lemma bridge. This is DEFERRED_POSITION_ONLY — there is
            # no licensed madlul_text_ar (no gloss in source), so the binding stays DEFERRED and the
            # verdict stays MADLUL_OWNER_PENDING. The position is never promoted to a meaning, opens
            # no gate, and does not touch the owner-curated madlul registry.
            try:
                from scripts.hokom_surface_lemma_bridge import surface_to_lemma_derive
                b = surface_to_lemma_derive(f"t{i:03d}", surface)
                if b.get("verdict") == "SURFACE_TO_LEMMA_DERIVED":
                    parts = [p for p in (b.get("arabic_net_entry_ids"), b.get("semantic_family_ids"))
                             if p and p != "none"]
                    madlul_position = ";".join(parts) or "none"
                    position_source = "ARABIC_NET"
                    position_status = "POSITION_DERIVED_TEXT_DEFERRED"
                    resid = ("POSITION_ONLY_FROM_REGISTERED_SOURCE;madlul_text_ar=NOT_LICENSED_NO_GLOSS;"
                             "position=" + madlul_position + ";" + resid)
            except Exception as e:  # pragma: no cover - env guard; source unavailability never breaks wiring
                position_status = "POSITION_SOURCE_UNAVAILABLE:" + type(e).__name__

        rows.append({
            "token_id": f"t{i:03d}", "surface": surface,
            "dal_status": getattr(dal.status, "value", str(dal.status)),
            "dal_license_status": "CONSTITUTIONALLY_LICENSED" if gate["licensed"] else "NOT_LICENSED",
            "dal_license_cause": gate["cause"],
            "dal_license_conditions": gate["conditions"],
            "dal_license_preventers": gate["preventers"],
            "madlul_status": m_status, "madlul_source_type": m_src or "NONE",
            "madlul_sense_id": m_sense,
            "binding_status": binding, "registry_lookup": reg_lookup,
            "owner_approval_status": owner_status,
            "verdict": verdict,
            "evidence_refs": f"token:t{i:03d};dal:{gate['verdict']};madlul:{m_status}",
            "residuals": resid,
            "madlul_position": madlul_position,
            "position_source": position_source,
            "position_status": position_status,
        })
    return {"rows": rows, "bound_tokens": bound_tokens, "summary": wiring_summary(rows)}


def wiring_summary(rows):
    total = len(rows)
    dal_lic = sum(1 for r in rows if r["dal_license_status"] == "CONSTITUTIONALLY_LICENSED")
    bound = sum(1 for r in rows if r["binding_status"] == "BOUND")
    owner_pending = sum(1 for r in rows if r["verdict"] == "MADLUL_OWNER_PENDING")
    gf_bound = [r["token_id"] for r in rows
                if r["binding_status"] == "BOUND" and r["madlul_source_type"] == "GRAMMATICAL_FUNCTION"]
    lexical_bound = [r["token_id"] for r in rows
                     if r["binding_status"] == "BOUND" and r["madlul_source_type"] == "LEXICAL_ENTRY"]
    return {
        "total": total, "dal_licensed": dal_lic, "bound": bound, "owner_pending": owner_pending,
        "gf_bound_token_ids": gf_bound, "lexical_bound_token_ids": lexical_bound,
        "grammatical_function_madlul_found": len(gf_bound) > 0,
        "approved_lexical_madlul_source_found": len(lexical_bound) > 0,
        "dal_madlul_binding_produced": bound > 0,
        "dal_madlul_score_percent": round(bound / total * 100, 2) if total else 0.0,
        "madlul_provider_wired": True, "madlul_provider_produced": bound,
    }


def registry_summary():
    reg = load_registry()
    appr = [r for r in reg.values() if _registry_approved_madlul(r) is not None]
    approved = len(appr)
    approved_lexical = sum(1 for r in appr if r.get("source_type") == "LEXICAL_ENTRY")
    approved_gf = sum(1 for r in appr if r.get("source_type") == "GRAMMATICAL_FUNCTION")
    pending = sum(1 for r in reg.values() if r.get("owner_approval_status") == "OWNER_PENDING")
    return {"present": bool(reg), "entries": len(reg), "approved": approved,
            "approved_lexical": approved_lexical, "approved_grammatical_function": approved_gf,
            "owner_pending": pending,
            "owner_approval_score_percent": round(approved / len(reg) * 100, 2) if reg else 0.0}


def emit_wiring_result(csv_path, analyses):
    from pathlib import Path
    res = wire_dal_madlul(analyses)
    p = Path(csv_path); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(WIRING_COLUMNS)
        for r in res["rows"]:
            w.writerow([r[c] for c in WIRING_COLUMNS])
    return res
