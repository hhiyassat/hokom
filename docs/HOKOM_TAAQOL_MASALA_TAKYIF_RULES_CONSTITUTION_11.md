# HOKOM/TAAQOL — MASALA_TAKYIF_LAYER Rules Constitution (round 11)

**ROUND = 11 · MODE = CODE_AND_DOCUMENTATION_ONLY · COMMIT = NO · PROJECT_FINISHED = NO**
This round builds a constitution + candidate rules + guards. It produces **no** final takyīf, no domain
classification, no normative source, no ḥukm/manāṭ/tanzīl/final answer.

## Layer definition
```
MASALA_TAKYIF_LAYER = طبقة تكييف المسألة
MASALA_TAKYIF_LAYER_STATUS = PROPOSED_NOT_CANONICAL
OWNER_RATIFICATION_REQUIRED = YES
```
`DOMAIN_ROUTING_LAYER` is **not** a canonical name and is not used as one.

## Purpose
Organize the transition from **TEXT_SIGNALS + FRAME_CANDIDATES** (round 10) to
**MASALA_TAKYIF_CANDIDATES** only — never to DOMAIN_CLASSIFICATION, NORMATIVE_SOURCE, HUKM, MANAT,
TANZIL, or ANSWER. The output is a constitution + candidate rules + guards, not a final takyīf.

## Relation to Hokom / Taaqol
- **Hokom** owns Arabic analysis (segmentation, class, surface, lexical-sense candidates). It does not
  classify a domain.
- **Taaqol** hosts `MASALA_TAKYIF_LAYER` as a proposed layer that only *organizes candidates*; it does
  not select a normative source and does not rule.

## Inputs / Outputs / Prohibitions
```
INPUT  : TEXT_SIGNALS (round 10) + FRAME_CANDIDATES (round 10)  — both candidate/surface only
OUTPUT : MASALA_TAKYIF_CANDIDATES (candidate only, owner_ratified = NO, verdict = DEFER)
BLOCKS : DOMAIN_CLASSIFICATION, NORMATIVE_SOURCE, HUKM, MANAT, TANZIL, FINAL_ANSWER
```

## Guarded chain
```
TEXT_SIGNAL ≠ FRAME ≠ MASALA_TAKYIF ≠ NORMATIVE_SOURCE ≠ HUKM ≠ MANAT ≠ TANZIL ≠ FINAL_ANSWER
WORD_PRESENT ≠ DOMAIN_CLASSIFICATION · LINGUISTIC_MEANING ≠ DOMAIN_CLASSIFICATION
IFADAH ≠ DOMAIN_CLASSIFICATION · FACTUAL_CLAIM ≠ DOMAIN_CLASSIFICATION
DOMAIN_CANDIDATE ≠ NORMATIVE_SOURCE · SOURCE_CANDIDATE ≠ SOURCE_RATIFICATION
```
The surface word «وارثه» is **not** a sufficient cause to birth a mīrāth domain; «فتحاكما» is **not**
sufficient to birth a qaḍāʾ domain.

## Cause / Condition / Preventer rule (every takyīf candidate)
- **CAUSE:** presence of round-10 text signals / frame candidates.
- **CONDITIONS:** an owner-ratified takyīf rule; a ratified relation between signals and the candidate;
  a ratified scope; traceable evidence from a prior artifact.
- **PREVENTERS:** missing owner ratification; conflating a text signal with a domain; conflating a
  frame candidate with final takyīf; choosing a normative source before takyīf; producing a ḥukm or
  tanzīl before a normative source.
- **VERDICT:** DEFER or BLOCK — never ACCEPT for any final takyīf.

## Layer separation table
| stage | example on this nazila | born this round? |
|-------|------------------------|------------------|
| TEXT_SIGNAL | surface cue «وَارِثُهُ», «فَتَحَاكَمَا» | recorded (round 10), surface only |
| FRAME_CANDIDATE | Death_event / Dispute_event candidates | candidate (round 10), unratified |
| MASALA_TAKYIF_CANDIDATE | MIRATH/QADA/TURKAH/SUKNA takyīf **candidates** | **candidate only, owner_ratified = NO, DEFER** |
| DOMAIN_CLASSIFICATION | (mīrāth? qaḍāʾ? …) | **NO — not born** |
| NORMATIVE_SOURCE | authority+text+scope+evidence+link | **NO — not opened** |
| HUKM | — | **NO** |
| MANAT | — | **NO** |
| TANZIL | — | **NO** |
| FINAL_ANSWER | — | **NO** |

## Explicit statement
This round does **not** produce a final takyīf, a domain classification, a normative source, or any
ḥukm/manāṭ/tanzīl/answer. All takyīf rules and candidates are `PROPOSED_NOT_CANONICAL` /
`OWNER_RATIFIED = NO` / `VERDICT = DEFER_UNTIL_OWNER_RATIFIES_TAKYIF_RULE`.
