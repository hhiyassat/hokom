# HARDEN-08: Expanded Hardening Corpus
Stage: HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01

## Corpus Version: 1.0.0
## Corpus Size: 47 tokens

## Category Breakdown
| Category         | Count | Examples                                         |
|------------------|-------|--------------------------------------------------|
| HAS_PROCLITIC    | 6     | وَكَتَبَ، فَقَالَ، بِاللَّهِ، لِلَّهِ، سَيَكْتُبُ، كَالْكِتَابِ |
| HAS_ENCLITIC     | 5     | رَبَّهُ، كِتَابُهُ، قَالَهَا، أَخَذَهُمْ، رَبَّنَا |
| HAS_ARTICLE      | 6     | الشَّمْسُ، الْقَمَرُ، الرَّجُلُ، الْكِتَابُ، النُّورُ، الْبَابُ |
| CLOSED_BOUNDARY  | 14    | اللَّهُ، مَنْ، مَا، كَيْفَ، مَتَى، مَهْمَا، الَّذِي، هُوَ، هِيَ، إِنْ، أَنْ، مِنْ، وَاللَّهُ، بِاللَّهِ |
| OPEN_MORPHOLOGY  | 12    | كَتَبَ، يَكْتُبُ، كِتَابٌ، مَكْتَبٌ، قَالَ، بَاعَ، دَعَا، رَمَى، وَجَدَ، رَدَّ، مَدَّ، اسْتَغْفَرَ، انْكَسَرَ |
| H11_H15_OUTPUT   | 4     | كَاتِبٌ، مَكْتُوبٌ، مُعَلِّمٌ، مِفْتَاحٌ |

## Contract Violations: 0
## Judgment Changes from Baseline: 0
## original_surface preservation: 100%
## Ambiguity AMBIGUOUS_COLLAPSE violations: 0
## claim_key format (64 hex chars): 100%

## Reproducibility: CONFIRMED (two independent runs produce identical claim_keys)

## Tests
tests/sga/test_expanded_corpus.py — 56 tests, 56 passed (47 parametrized + 9 structural)
