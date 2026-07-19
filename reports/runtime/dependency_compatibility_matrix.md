# Dependency Compatibility Matrix

## Mandate: HOKOM-RUNTIME-PYTHON-3.11+-MIGRATION-01

## Python Version Requirements

| Component | Python 3.10 | Python 3.11 | Python 3.12 |
|-----------|-------------|-------------|-------------|
| hokom_pipeline | IMPORTABLE | IMPORTABLE | IMPORTABLE |
| pipeline.word_class | IMPORTABLE | IMPORTABLE | IMPORTABLE |
| pipeline.p5_inflection | IMPORTABLE | IMPORTABLE | IMPORTABLE |
| pipeline.p5_lexical | IMPORTABLE | IMPORTABLE | IMPORTABLE |
| pipeline.taaqol_integration | IMPORTABLE (guards inactive) | IMPORTABLE | IMPORTABLE |
| taaqqul_slot_geometry (vendor) | FAILS (no StrEnum) | OK | OK |

## Stdlib Features

| Feature | Introduced | Used By |
|---------|-----------|---------|
| enum.StrEnum | Python 3.11 | taaqqul_slot_geometry vendor |
| tomllib | Python 3.11 | test_packaging_python_requires.py |
| dataclasses | Python 3.7 | Hokom pipeline models |
| pathlib | Python 3.4 | Various |

## Key Finding
The Hokom pipeline itself is Python 3.10-compatible (no StrEnum usage in core pipeline).
The Python 3.11+ requirement is driven by:
1. The Taaqol vendor (taaqqul_slot_geometry) which uses StrEnum extensively
2. The constitutional contract requiring native StrEnum from stdlib
3. The package metadata establishing >=3.11 as the canonical minimum
