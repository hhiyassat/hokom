# Ayat al-Dayn Taaqol Diff — Before vs After Resume

## Token Count
Total: 129 tokens (full verse 2:282)

## Before Resume (b992d7e)

- `taaqol_center_scope`: field did not exist in hokom() return dict
- `Center.scope` = `bundle.original_surface` (full token with clitics)
- Clitic-only tokens: no gate — full token passed as center (VIOLATION)
- `segment_host`, `segment_proclitics`, etc.: NOT in HokomLinguisticClaimBundle

## After Resume (this commit)

- `taaqol_center_scope`: exposed in hokom() return dict and HokomTaaqolDecision
- `Center.scope` = `segment_host` (canonical lexical host)
- Clitic-only tokens: immediate DEFERRED, center=None
- All segment fields wired through claim bundle to bridge

## Changed Center Scopes (sample)

| Token | Before | After |
|-------|--------|-------|
| بِدَيْنٍ | 'بِدَيْنٍ' | 'دَيْنٍ' |
| بِالْعَدْلِ | 'بِالْعَدْلِ' | 'عَدْلِ' |
| وَلْيَكْتُبْ | 'وَلْيَكْتُبْ' | 'يَكْتُبْ' |
| فَلْيَكْتُبْ | 'فَلْيَكْتُبْ' | 'يَكْتُبْ' |
| مِنْهُ | 'مِنْهُ' | 'مِنْ' |
| لِلشَّهَادَةِ | 'لِلشَّهَادَةِ' | 'شْشَهَادَةِ' |
| بِكُمْ | 'بِكُمْ' (VIOLATION) | None (DEFERRED) |
| وَلَا | 'وَلَا' | 'لَا' |
| أَجَلِهِ | 'أَجَلِهِ' | 'ءَجَلِ' |

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| FULL_TOKEN_CENTER_VIOLATIONS | N (unknown) | 0 |
| CLITIC_ONLY_LICENSED_VIOLATIONS | N (unknown) | 0 |
| ERRORS | 0 | 0 |
| taaqol_center_scope available | No | Yes |
