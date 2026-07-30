"""
hokom.canonical — 19-Stage Canonical Integration Package

Wires three canonical owners into a single runtime pipeline:

    Saleh/Qiyas  — canonical 19-stage SCG registry, stage order, adapter
                   contracts, terminality of P12
    Hokom        — sole owner of Arabic morphological evidence: normalization,
                   segmentation, clitic analysis, root, wazn, bab, masdar,
                   derivatives, inflection, morphosyntax
    Taaqol       — sole constitutional governor and transition licensor; never
                   generates Arabic linguistic facts

Ownership invariants (binding — do not violate):
    - HR2S / H2RS: FORBIDDEN at runtime — no import, no delegation, no fallback
    - No P13: P12 (IFADAH_SPEECH_FORCE) is TERMINAL; target_boundary_opens=()
    - Saleh registry: read-only consumer — never mutated by Hokom
    - Taaqol: never generates Arabic evidence; only licenses transitions
"""
__version__ = "0.1.0"
