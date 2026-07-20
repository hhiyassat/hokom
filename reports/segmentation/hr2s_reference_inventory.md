# HR2S Reference Inventory

**Status: HR2S segmenter NOT found in the repository.**

The Hokom segmenter was implemented from first linguistic principles, not from
HR2S source code. No HR2S module was found at:
- `/sessions/lucid-gifted-planck/mnt/hokom/` (repo root)
- `/sessions/lucid-gifted-planck/mnt/` (parent)
- `vendor/` subdirectory

The HR2S integration adapter exists at `pipeline/integrations/hr2s_root_adapter.py`
but this is a Hokom→HR2S interface definition for the root engine, not a segmenter.

## Hokom Native Inventory (independently derived)

### Proclitic Inventory

| Form | Bare | Kind | Priority |
|------|------|------|----------|
| وَ | و | CONJUNCTION | 1 |
| فَ | ف | CONJUNCTION | 2 |
| بِ | ب | PREPOSITION | 3 |
| لِ | ل | PREPOSITION | 4 |
| سَ | س | FUTURE_PARTICLE | 5 |

**Standalone كَ is intentionally excluded** (supported only in multi-proclitic context وَكَ, فَكَ).

### Multi-Proclitic Sequences

| Bare Sequence | Components | Kinds |
|---------------|------------|-------|
| وَلْ | وَ + لْ | CONJUNCTION + JUSSIVE_LAM |
| فَلْ | فَ + لْ | CONJUNCTION + JUSSIVE_LAM |
| وَبِ, فَبِ | وَ/فَ + بِ | CONJUNCTION + PREPOSITION |
| وَلِ, فَلِ | وَ/فَ + لِ | CONJUNCTION + PREPOSITION |
| وَكَ, فَكَ | وَ/فَ + كَ | CONJUNCTION + PREPOSITION |
| وَسَ, فَسَ | وَ/فَ + سَ | CONJUNCTION + FUTURE_PARTICLE |

### Enclitic Inventory (bare forms, longest first)

هنّ, كنّ, هما, كما, هم, كم, نا, ني, ها, يَ, يِ, ه, ك, ي

### Protected Whole Tokens (sample)

اللَّهُ, الله, هُوَ, هِيَ, هَذَا, هَذِهِ, الَّذِي, الَّتِي, ذَلِكَ, إِذَا

### Whole-Token Operators (sample)

مِنْ, عَنْ, إِلَى, عَلَى, فِي, مَعَ, إِنَّ, أَنَّ, لَا, مَا, قَدْ, لَنْ, هَلْ

### Inflectional Suffixes (NEVER treated as enclitics)

وا (واو الجماعة), ون (nominal plural), ان (dual), ن (نون النسوة), تم, تن
