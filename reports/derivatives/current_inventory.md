# Derivative Ownership Inventory
## HOKOM-MORPHOLOGY-DERIVATIVES-OWNERSHIP-01

**Date**: 2026-07-19
**Baseline**: HEAD = ad376de (HOKOM-MORPHOLOGY-MASDAR-OWNERSHIP-01)

## Existing Derivative Implementations Before This Mandate

Searched codebase for existing ISM_FA3IL / ISM_MAF3UL / derivative ownership:

| Module | Reference | Type | Notes |
|--------|-----------|------|-------|
| pipeline/p4_mushtaqat/ | mushtaq_hypothesis.py, mushtaq_rules.py | partial mushtaqat routing | No canonical ownership contract |
| pipeline/p2_augmented/models.py | FA3IL_PARTICIPLE form_family | routing tag only | Not a derivative verdict |
| pipeline/p5_masdar/engine.py | _BLOCK_FAMILIES = {'FA3IL_PARTICIPLE'} | masdar block only | Not derivative ownership |

## Conclusion

No canonical derivative ownership existed prior to this mandate.
All 7 derivative types (ISM_FA3IL, ISM_MAF3UL, SIFA_MUSHABBAHA, MUBALGHA, ISM_ZAMAN, ISM_MAKAN, ISM_ALA)
were unowned. This mandate establishes full canonical ownership via pipeline/p6_derivatives/.
