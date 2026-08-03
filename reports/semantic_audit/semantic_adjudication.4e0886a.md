# Semantic Adjudication — Ayat Al-Dayn

HEAD: `4e0886a` | Tokens: 129 | Date: 2026-07-20

| # | Surface | Class | Label | WC_actual | WC_expected | Root_actual | Root_expected | Severity | Defect_Type | Owner |
|---|---------|-------|-------|-----------|-------------|-------------|---------------|----------|-------------|-------|
| 000 | يَا | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 001 | أَيُّهَا | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 002 | الَّذِينَ | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Add الَّذِينَ to mabni/operator catalog |
| 003 | آمَنُوا | F | FALSE_BLOCK | -/- | FI3L | - | ء-م-ن | HIGH | IMPLEMENTATION_GAP | License CVV+V slot pattern for واو الجماعة suffix |
| 004 | إِذَا | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 005 | تَدَايَنْتُمْ | A | CORRECT_ACCEPT | FI3L/VERBAL_PAST | FI3L | - | د-ي-ن | NONE | - | - |
| 006 | بِدَيْنٍ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | د-ي-ن | MEDIUM | IMPLEMENTATION_GAP | Fix consonant counter: tanwin must not be counted as radical |
| 007 | إِلَى | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 008 | أَجَلٍ | A | CORRECT_ACCEPT | ISM/ISM_FA3IL | ISM | ['ء', 'ج', 'ل'] | ء-ج-ل | NONE | - | - |
| 009 | مُسَمًّى | E | FALSE_DEFER | -/- | ISM | - | س-م-ي | MEDIUM | IMPLEMENTATION_GAP | Handle alef maqsura in root counter; assign ISM/ISM_MAFOOL |
| 010 | فَاكْتُبُوهُ | F | FALSE_BLOCK | -/- | FI3L | - | ك-ت-ب | HIGH | IMPLEMENTATION_GAP | License +V slot pattern for hamzat al-wasl tokens; license CVV+V |
| 011 | وَلْيَكْتُبْ | E | FALSE_DEFER | -/- | FI3L | - | ك-ت-ب | HIGH | IMPLEMENTATION_GAP | Strip مضارع prefix ي before consonant counting in pre_root |
| 012 | بَيْنَكُمْ | G | WRONG_OWNER_OR_ROUTE | FI3L/VERBAL_PAST | ISM | ['ب', 'ي', 'ن'] | ب-ي-ن | HIGH | WIRING_GAP | Route بَيْن to ISM/HARF preposition class, not verbal path |
| 013 | كَاتِبٌ | A | CORRECT_ACCEPT | ISM/LEXICAL_NOUN | ISM | ['ك', 'ت', 'ب'] | ك-ت-ب | NONE | - | - |
| 014 | بِالْعَدْلِ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ع-د-ل | MEDIUM | IMPLEMENTATION_GAP | Fix consonant counter for CVC roots with ال article |
| 015 | وَلَا | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Add لَا as HARF to post-proclitic host word-class catalog |
| 016 | يَأْبَ | A | CORRECT_ACCEPT | FI3L/VERBAL_PAST | FI3L | - | ء-ب-ي | NONE | - | - |
| 017 | كَاتِبٌ | A | CORRECT_ACCEPT | ISM/LEXICAL_NOUN | ISM | ['ك', 'ت', 'ب'] | ك-ت-ب | NONE | - | - |
| 018 | أَنْ | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 019 | يَكْتُبَ | E | FALSE_DEFER | FI3L/VERBAL_PAST | FI3L | - | ك-ت-ب | HIGH | IMPLEMENTATION_GAP | pre_root must strip مضارع prefix ي/ت/ن/أ before consonant counting |
| 020 | كَمَا | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Add كَمَا to HARF catalog with full operator entry |
| 021 | عَلَّمَهُ | G | WRONG_OWNER_OR_ROUTE | ISM/MASDAR | FI3L | ['ع', 'ل', 'م'] | ع-ل-م | HIGH | WIRING_GAP | Route فَعَّلَ pattern to FI3L not ISM/MASDAR when verbal inflection present |
| 022 | اللَّهُ | H | SURFACE_OR_PROVENANCE_DEFECT | ISM/MASDAR | ISM | ['ء', 'ل', 'ل'] | none | HIGH | CATALOG_GAP | Add اللَّهُ/اللَّهَ/اللَّهِ to protected catalog (proper noun, no derivational root) |
| 023 | فَلْيَكْتُبْ | E | FALSE_DEFER | -/- | FI3L | - | ك-ت-ب | HIGH | IMPLEMENTATION_GAP | Strip مضارع prefix before consonant counting |
| 024 | وَلْيُمْلِلِ | G | WRONG_OWNER_OR_ROUTE | ISM/LEXICAL_NOUN | FI3L | - | م-ل-ل | HIGH | WIRING_GAP | Route يَفْعُل imperfect with lam al-amr proclitic to FI3L |
| 025 | الَّذِي | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Add الَّذِي to mabni catalog |
| 026 | عَلَيْهِ | C | LEGITIMATE_DEFER | -/- | HARF | - | none | LOW | - | Implement defective preposition host resolution in future stage |
| 027 | الْحَقُّ | G | WRONG_OWNER_OR_ROUTE | FI3L/VERBAL_PAST | ISM | ['ح', 'ق', 'ق'] | ح-ق-ق | HIGH | WIRING_GAP | Route tokens with ال definite article to ISM; block verbal path |
| 028 | وَلْيَتَّقِ | G | WRONG_OWNER_OR_ROUTE | ISM/LEXICAL_NOUN | FI3L | - | و-ق-ي | HIGH | WIRING_GAP | Same as [024]: yaf3ul with lam al-amr must route to FI3L |
| 029 | اللَّهَ | H | SURFACE_OR_PROVENANCE_DEFECT | -/- | ISM | - | none | HIGH | CATALOG_GAP | Protect لفظ الجلالة uniformly across all case forms |
| 030 | رَبَّهُ | G | WRONG_OWNER_OR_ROUTE | FI3L/VERBAL_PAST | ISM | ['ر', 'ب', 'ب'] | ر-ب-ب | MEDIUM | WIRING_GAP | Geminate noun patterns should default to ISM when with pronoun enclitic in nominal slot |
| 031 | وَلَا | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Same as [015] |
| 032 | يَبْخَسْ | E | FALSE_DEFER | FI3L/VERBAL_PAST | FI3L | - | ب-خ-س | HIGH | IMPLEMENTATION_GAP | Same as [019]: strip مضارع prefix |
| 033 | مِنْهُ | C | LEGITIMATE_DEFER | -/- | HARF | - | none | LOW | - | Recognize particle+pronoun compounds as HARF in future stage |
| 034 | شَيْئًا | A | CORRECT_ACCEPT | ISM/LEXICAL_NOUN | ISM | ['ش', 'ي', 'ء'] | ش-ي-ء | NONE | - | - |
| 035 | فَإِنْ | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Add إِنْ as HARF to post-proclitic host catalog |
| 036 | كَانَ | A | CORRECT_ACCEPT | FI3L/VERBAL_OPERATOR | FI3L | - | ك-و-ن | NONE | - | - |
| 037 | الَّذِي | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Same as [025] |
| 038 | عَلَيْهِ | C | LEGITIMATE_DEFER | -/- | HARF | - | none | LOW | - | Same as [026] |
| 039 | الْحَقُّ | G | WRONG_OWNER_OR_ROUTE | FI3L/VERBAL_PAST | ISM | ['ح', 'ق', 'ق'] | ح-ق-ق | HIGH | WIRING_GAP | Same as [027] |
| 040 | سَفِيهًا | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | س-ف-ه | MEDIUM | IMPLEMENTATION_GAP | Strip فَعِيل pattern extension ي before root counting |
| 041 | أَوْ | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 042 | ضَعِيفًا | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ض-ع-ف | MEDIUM | IMPLEMENTATION_GAP | Same as [040] |
| 043 | أَوْ | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 044 | لَا | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 045 | يَسْتَطِيعُ | G | WRONG_OWNER_OR_ROUTE | ISM/MASDAR | FI3L | ['ط', 'ي', 'ع'] | ط-و-ع | HIGH | WIRING_GAP | Route Form X يَسْتَفْعِل to FI3L; fix weak-radical root for Form X |
| 046 | أَنْ | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 047 | يُمِلَّ | E | FALSE_DEFER | FI3L/VERBAL_PAST | FI3L | - | م-ل-ل | HIGH | IMPLEMENTATION_GAP | Deduplicate geminate radical: shadda = one consonant position not two |
| 048 | هُوَ | A | CORRECT_ACCEPT | ISM/PRONOUN | ISM | - | none | NONE | - | - |
| 049 | فَلْيُمْلِلْ | E | FALSE_DEFER | -/- | FI3L | - | م-ل-ل | HIGH | IMPLEMENTATION_GAP | Same as [047]: geminate deduplication + verb prefix stripping |
| 050 | وَلِيُّهُ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | و-ل-ي | MEDIUM | IMPLEMENTATION_GAP | Same as [040]: strip فَعِيل pattern ي before counting |
| 051 | بِالْعَدْلِ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ع-د-ل | MEDIUM | IMPLEMENTATION_GAP | Same as [014] |
| 052 | وَاسْتَشْهِدُوا | F | FALSE_BLOCK | -/- | FI3L | - | ش-ه-د | HIGH | IMPLEMENTATION_GAP | Same as [003]+[010]: license +V and CVV+V slot patterns |
| 053 | شَهِيدَيْنِ | C | LEGITIMATE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ش-ه-د | LOW | - | Implement dual suffix stripping in future morphological stage |
| 054 | مِنْ | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 055 | رِجَالِكُمْ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ر-ج-ل | MEDIUM | IMPLEMENTATION_GAP | Implement broken plural pattern stripping in root extraction |
| 056 | فَإِنْ | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Same as [035] |
| 057 | لَمْ | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 058 | يَكُونَا | E | FALSE_DEFER | -/- | FI3L | - | ك-و-ن | HIGH | IMPLEMENTATION_GAP | Handle medial-waw (أجوف) roots in pre_root; open path for كون/يكون |
| 059 | رَجُلَيْنِ | C | LEGITIMATE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ر-ج-ل | LOW | - | Same as [053]: dual suffix stripping future stage |
| 060 | فَرَجُلٌ | A | CORRECT_ACCEPT | ISM/ISM_FA3IL | ISM | ['ر', 'ج', 'ل'] | ر-ج-ل | NONE | - | - |
| 061 | وَامْرَأَتَانِ | F | FALSE_BLOCK | -/- | ISM | - | ر-ء-م | HIGH | IMPLEMENTATION_GAP | License +V slot pattern for hamzat al-wasl tokens |
| 062 | مِمَّنْ | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Add مَن / مِمَّنْ to function word catalog |
| 063 | تَرْضَوْنَ | E | FALSE_DEFER | FI3L/VERBAL_PAST | FI3L | - | ر-ض-و | HIGH | IMPLEMENTATION_GAP | Strip verb prefix ت and plural suffix ون before consonant counting |
| 064 | مِنَ | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 065 | الشُّهَدَاءِ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ش-ه-د | HIGH | IMPLEMENTATION_GAP | pre_root must open root path for جمع التكسير patterns with ال |
| 066 | أَنْ | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 067 | تَضِلَّ | E | FALSE_DEFER | FI3L/VERBAL_PAST | FI3L | - | ض-ل-ل | HIGH | IMPLEMENTATION_GAP | Same as [047]+[019]: geminate deduplication + verb prefix stripping |
| 068 | إِحْدَاهُمَا | E | FALSE_DEFER | -/- | ISM | - | و-ح-د | MEDIUM | IMPLEMENTATION_GAP | Recognize إِحْدَى as derived ISM from root و-ح-د |
| 069 | فَتُذَكِّرَ | G | WRONG_OWNER_OR_ROUTE | ISM/MASDAR | FI3L | ['ذ', 'ك', 'ر'] | ذ-ك-ر | HIGH | WIRING_GAP | Route Form II imperfect تُفَعِّل to FI3L not ISM/MASDAR |
| 070 | إِحْدَاهُمَا | E | FALSE_DEFER | -/- | ISM | - | و-ح-د | MEDIUM | IMPLEMENTATION_GAP | Same as [068] |
| 071 | الْأُخْرَى | G | WRONG_OWNER_OR_ROUTE | FI3L/VERBAL_PAST | ISM | - | ء-خ-ر | HIGH | WIRING_GAP | Route alef maqsura adjective to ISM; الأُخْرَى is not a verb |
| 072 | وَلَا | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Same as [015] |
| 073 | يَأْبَ | A | CORRECT_ACCEPT | FI3L/VERBAL_PAST | FI3L | - | ء-ب-ي | NONE | - | - |
| 074 | الشُّهَدَاءُ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ش-ه-د | HIGH | IMPLEMENTATION_GAP | Same as [065] |
| 075 | إِذَا | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 076 | مَا | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 077 | دُعُوا | F | FALSE_BLOCK | -/- | FI3L | - | د-ع-و | HIGH | IMPLEMENTATION_GAP | License CVV+V slot pattern; same as [003] |
| 078 | وَلَا | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Same as [015] |
| 079 | تَسْأَمُوا | F | FALSE_BLOCK | -/- | FI3L | - | س-أ-م | HIGH | IMPLEMENTATION_GAP | Same as [003] |
| 080 | أَنْ | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 081 | تَكْتُبُوهُ | E | FALSE_DEFER | FI3L/VERBAL_PAST | FI3L | - | ك-ت-ب | HIGH | IMPLEMENTATION_GAP | Same as [019]: strip verb prefix ت before consonant counting |
| 082 | صَغِيرًا | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ص-غ-ر | MEDIUM | IMPLEMENTATION_GAP | Same as [040]: strip فَعِيل pattern ي |
| 083 | أَوْ | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 084 | كَبِيرًا | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ك-ب-ر | MEDIUM | IMPLEMENTATION_GAP | Same as [040] |
| 085 | إِلَى | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 086 | أَجَلِهِ | A | CORRECT_ACCEPT | ISM/ISM_FA3IL | ISM | ['ء', 'ج', 'ل'] | ء-ج-ل | NONE | - | - |
| 087 | ذَلِكُمْ | E | FALSE_DEFER | -/- | ISM | - | none | MEDIUM | CATALOG_GAP | Add ذَلِكُمْ / ذَلِك to mabni catalog |
| 088 | أَقْسَطُ | A | CORRECT_ACCEPT | ISM/MASDAR | ISM | ['ق', 'س', 'ط'] | ق-س-ط | NONE | - | - |
| 089 | عِنْدَ | G | WRONG_OWNER_OR_ROUTE | FI3L/VERBAL_PAST | ISM | ['ع', 'ن', 'د'] | ع-ن-د | HIGH | WIRING_GAP | Route عِنْد to ISM/HARF ظرف class; block verbal routing |
| 090 | اللَّهِ | H | SURFACE_OR_PROVENANCE_DEFECT | ISM/MASDAR | ISM | ['ء', 'ل', 'ل'] | none | HIGH | CATALOG_GAP | Same as [022] |
| 091 | وَأَقْوَمُ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ق-و-م | MEDIUM | IMPLEMENTATION_GAP | Handle medial-waw (أجوف) roots; ق-و-م = 3 consonants |
| 092 | لِلشَّهَادَةِ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ش-ه-د | HIGH | IMPLEMENTATION_GAP | Same as [065]: open root path for فَعَالَة pattern |
| 093 | وَأَدْنَى | E | FALSE_DEFER | -/- | ISM | - | د-ن-و | MEDIUM | IMPLEMENTATION_GAP | Handle defective lam-waw (ناقص واوي) roots; د-ن-و = 3 consonants |
| 094 | أَلَّا | G | WRONG_OWNER_OR_ROUTE | FI3L/VERBAL_PAST | HARF | - | none | HIGH | WIRING_GAP | Route أَلَّا compound to HARF; not a verb |
| 095 | تَرْتَابُوا | F | FALSE_BLOCK | -/- | FI3L | - | ر-ي-ب | HIGH | IMPLEMENTATION_GAP | Same as [003] |
| 096 | إِلَّا | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 097 | أَنْ | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 098 | تَكُونَ | E | FALSE_DEFER | -/- | FI3L | - | ك-و-ن | HIGH | IMPLEMENTATION_GAP | Open root path for أجوف (medial waw) verb forms: تَكُون/يَكُون |
| 099 | تِجَارَةً | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ت-ج-ر | MEDIUM | IMPLEMENTATION_GAP | Strip فِعَالَة pattern extension before root counting |
| 100 | حَاضِرَةً | A | CORRECT_ACCEPT | ISM/LEXICAL_NOUN | ISM | ['ح', 'ض', 'ر'] | ح-ض-ر | NONE | - | - |
| 101 | تُدِيرُونَهَا | G | WRONG_OWNER_OR_ROUTE | ISM/LEXICAL_NOUN | FI3L | - | د-و-ر | HIGH | WIRING_GAP | Route Form IV تُفْعِل to FI3L not ISM |
| 102 | بَيْنَكُمْ | G | WRONG_OWNER_OR_ROUTE | FI3L/VERBAL_PAST | ISM | ['ب', 'ي', 'ن'] | ب-ي-ن | HIGH | WIRING_GAP | Same as [012] |
| 103 | فَلَيْسَ | E | FALSE_DEFER | -/- | FI3L | - | ل-ي-س | MEDIUM | CATALOG_GAP | Add لَيْسَ to verbal operator catalog |
| 104 | عَلَيْكُمْ | C | LEGITIMATE_DEFER | -/- | HARF | - | none | LOW | - | Same as [026] |
| 105 | جُنَاحٌ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ج-ن-ح | MEDIUM | IMPLEMENTATION_GAP | Same as [040]: pattern extension consonant stripping |
| 106 | أَلَّا | G | WRONG_OWNER_OR_ROUTE | FI3L/VERBAL_PAST | HARF | - | none | HIGH | WIRING_GAP | Same as [094] |
| 107 | تَكْتُبُوهَا | E | FALSE_DEFER | FI3L/VERBAL_PAST | FI3L | - | ك-ت-ب | HIGH | IMPLEMENTATION_GAP | Same as [081]/[019] |
| 108 | وَأَشْهِدُوا | F | FALSE_BLOCK | -/- | FI3L | - | ش-ه-د | HIGH | IMPLEMENTATION_GAP | Same as [003] |
| 109 | إِذَا | B | CORRECT_NOT_OPENED | HARF/CLOSED_FUNCTION_WORD | HARF | - | none | NONE | - | - |
| 110 | تَبَايَعْتُمْ | A | CORRECT_ACCEPT | FI3L/VERBAL_PAST | FI3L | - | ب-ي-ع | NONE | - | - |
| 111 | وَلَا | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Same as [015] |
| 112 | يُضَارَّ | A | CORRECT_ACCEPT | FI3L/VERBAL_PAST | FI3L | - | ض-ر-ر | NONE | - | - |
| 113 | كَاتِبٌ | A | CORRECT_ACCEPT | ISM/LEXICAL_NOUN | ISM | ['ك', 'ت', 'ب'] | ك-ت-ب | NONE | - | - |
| 114 | وَلَا | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Same as [015] |
| 115 | شَهِيدٌ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ش-ه-د | MEDIUM | IMPLEMENTATION_GAP | Same as [040] |
| 116 | وَإِنْ | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Same as [035] |
| 117 | تَفْعَلُوا | F | FALSE_BLOCK | -/- | FI3L | - | ف-ع-ل | HIGH | IMPLEMENTATION_GAP | Same as [003] |
| 118 | فَإِنَّهُ | E | FALSE_DEFER | -/- | HARF | - | none | MEDIUM | CATALOG_GAP | Add إِنَّ to post-proclitic host catalog as HARF |
| 119 | فُسُوقٌ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ف-س-ق | MEDIUM | IMPLEMENTATION_GAP | Strip فُعُول pattern extension before root counting |
| 120 | بِكُمْ | C | LEGITIMATE_DEFER | -/- | HARF | - | none | LOW | - | Document clitic-only resolution as future enhancement |
| 121 | وَاتَّقُوا | F | FALSE_BLOCK | -/- | FI3L | - | و-ق-ي | HIGH | IMPLEMENTATION_GAP | Same as [010]: license +V and CVV+V patterns |
| 122 | اللَّهَ | H | SURFACE_OR_PROVENANCE_DEFECT | -/- | ISM | - | none | HIGH | CATALOG_GAP | Same as [022] |
| 123 | وَيُعَلِّمُكُمُ | E | FALSE_DEFER | FI3L/VERBAL_PAST | FI3L | - | ع-ل-م | HIGH | IMPLEMENTATION_GAP | Strip مضارع prefix ي + handle shadda deduplication in pre_root |
| 124 | اللَّهُ | H | SURFACE_OR_PROVENANCE_DEFECT | ISM/MASDAR | ISM | ['ء', 'ل', 'ل'] | none | HIGH | CATALOG_GAP | Same as [022] |
| 125 | وَاللَّهُ | H | SURFACE_OR_PROVENANCE_DEFECT | ISM/MASDAR | ISM | ['و', 'ل', 'ل'] | none | CRITICAL | CATALOG_GAP | CRITICAL: protect الله; fix proclitic boundary before root extraction for اللَّه |
| 126 | بِكُلِّ | E | FALSE_DEFER | -/- | ISM | - | ك-ل-ل | MEDIUM | IMPLEMENTATION_GAP | Same as [047]: geminate deduplication; add كُلّ to ISM catalog |
| 127 | شَيْءٍ | A | CORRECT_ACCEPT | ISM/LEXICAL_NOUN | ISM | ['ش', 'ي', 'ء'] | ش-ي-ء | NONE | - | - |
| 128 | عَلِيمٌ | E | FALSE_DEFER | ISM/LEXICAL_NOUN | ISM | - | ع-ل-م | MEDIUM | IMPLEMENTATION_GAP | Same as [040] |