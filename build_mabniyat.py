#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_mabniyat.py
Build mabniyat_catalog_split_vocalized.csv, mabniyat_layer.py, tests, report.
READ-ONLY on all source JSON files.
"""
import json, csv, re, unicodedata, os, sys
from pathlib import Path

BASE = Path('/sessions/lucid-gifted-planck/mnt/hokom')
DATA = BASE / 'data/02_mabniyat'

# DEPRECATED (Phase A): parallel diacritic pattern — will consolidate into
# glyph_classification.MarkClass as the single source of truth.
# Do not expand this pattern; use build_glyph_traces() in new code.
DIAC_RE = re.compile(r'[ً-ّٰٟ]')

def strip_diacritics(s: str) -> str:
    return re.sub(r'[ً-ٰٟ]', '', s)

def nfc(s: str) -> str:
    return unicodedata.normalize('NFC', s)

def load_json(fname):
    p = DATA / fname
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    return d.get('data', [])

# ─────────────────────────────────────────────────────────────
# Catalog row factory
# ─────────────────────────────────────────────────────────────
COLS = ['mabni_id','surface_vocalized','surface_bare','surface_kind',
        'lexical_class','lexical_family','source_file','source_record_id',
        'blocks_root_path','contract_state','estimated_form',
        'attachment_type','notes']

def row(mid, sv, sk, lc, lf, src, rid, blk=True, cs='NONE',
        ef='', at='', notes=''):
    sv_nfc = nfc(sv)
    sb = strip_diacritics(sv_nfc)
    return {
        'mabni_id': mid,
        'surface_vocalized': sv_nfc,
        'surface_bare': sb,
        'surface_kind': sk,
        'lexical_class': lc,
        'lexical_family': lf,
        'source_file': src,
        'source_record_id': str(rid),
        'blocks_root_path': str(blk),
        'contract_state': cs,
        'estimated_form': ef,
        'attachment_type': at,
        'notes': notes,
    }

catalog = []
seen_ids = set()

def add(r):
    mid = r['mabni_id']
    if mid in seen_ids:
        print(f"  WARN: duplicate mabni_id {mid}, skipping second occurrence")
        return
    seen_ids.add(mid)
    catalog.append(r)

# ══════════════════════════════════════════════════════════
# 1. DETACHED PRONOUNS — pronouns_classification.json
# ══════════════════════════════════════════════════════════
print("Processing pronouns_classification.json ...")
pron = load_json('pronouns_classification.json')

DETACHED_MAP = {
    43: ('ANA',     'أَنَا'),
    44: ('NAHNU',   'نَحْنُ'),
    45: ('ANTA',    'أَنْتَ'),   # source error: pronoun_form shows نحن but pronoun field is correct
    46: ('ANTI',    'أَنْتِ'),
    47: ('ANTUMA',  'أَنْتُمَا'),
    48: ('ANTUM',   'أَنْتُمْ'),
    49: ('ANTUNNA', 'أَنْتُنَّ'),
    50: ('HUWA',    'هُوَ'),
    51: ('HIYA',    'هِيَ'),
    52: ('HUMA',    'هُمَا'),
    53: ('HUM',     'هُمْ'),
    54: ('HUNNA',   'هُنَّ'),
    55: ('IYYAYA',  'إِيَّايَ'),   # source has double shadda (إِيَّايَّ) — normalised
    56: ('IYYAANA', 'إِيَّانَا'),
    57: ('IYYAKA',  'إِيَّاكَ'),
    58: ('IYYAKI',  'إِيَّاكِ'),
    59: ('IYYAKUMA','إِيَّاكُمَا'),
    60: ('IYYAKUM', 'إِيَّاكُمْ'),
    61: ('IYYAKUNNA','إِيَّاكُنَّ'),
    62: ('IYYAHU',  'إِيَّاهُ'),
    63: ('IYYAHA',  'إِيَّاهَا'),
    64: ('IYYAHUMA','إِيَّاهُمَا'),
    65: ('IYYAHUNNA','إِيَّاهُنَّ'),
}
NOTE_45 = 'source error: pronoun_form field shows نَحْنُ instead of أَنْتَ (id=45)'
NOTE_55 = 'source has double shadda إِيَّايَّ — normalised to إِيَّايَ'

for r in pron:
    rid = r['id']
    if rid in DETACHED_MAP:
        mid, sv = DETACHED_MAP[rid]
        notes = ''
        if rid == 45: notes = NOTE_45
        if rid == 55: notes = NOTE_55
        add(row(mid, sv, 'OVERT', 'DETACHED_PRONOUN', 'DETACHED_PRONOUN_SERIES',
                'pronouns_classification.json', rid, blk=True, cs='NONE', notes=notes))

# Attached pronouns — deduplicated by type
ATTACHED_MAP = {
    # id: (mabni_id, surface_vocalized, attachment_type, notes)
    66: ('ATTACHED_PRONOUN_TAU',         'تُ',  'SUFFIX', 'multi-form: تُ تَ تِ; representative form تُ'),
    67: ('ATTACHED_PRONOUN_WAW_AL_JAMAA','وا',  'SUFFIX', ''),
    68: ('ATTACHED_PRONOUN_ALIF_AL_ITHNAYN','ا','SUFFIX', ''),
    69: ('ATTACHED_PRONOUN_NUN_AL_NISWA','نَ',  'SUFFIX', ''),
    70: ('ATTACHED_PRONOUN_YA_AL_MUKHATABA','ي','SUFFIX', ''),
    # 71: skip — CLASSIFICATION_ONLY (ضمائر كان)
    72: ('ATTACHED_PRONOUN_HA',          'هُ',  'SUFFIX', 'also serves as مضاف إليه and جر'),
    73: ('ATTACHED_PRONOUN_KAF',         'كَ',  'SUFFIX', 'also serves as مضاف إليه and جر'),
    74: ('ATTACHED_PRONOUN_YA_AL_MUTAKALLIM','ي','SUFFIX','ياء المتكلم; same glyph as ياء المخاطبة but different role'),
    84: ('ATTACHED_PRONOUN_NA',          'نَا', 'SUFFIX', 'مشترك: رفع/نصب/جر'),
    85: ('ATTACHED_PRONOUN_KUM',         'كُمْ','SUFFIX', ''),
}
for r in pron:
    rid = r['id']
    if rid in ATTACHED_MAP:
        mid, sv, at, notes = ATTACHED_MAP[rid]
        add(row(mid, sv, 'ATTACHED', 'ATTACHED_PRONOUN', 'ATTACHED_PRONOUN_SERIES',
                'pronouns_classification.json', rid, blk=False, cs='NONE',
                at=at, notes=notes))

# ══════════════════════════════════════════════════════════
# 2. LATENT PRONOUNS — hidden_pronouns.json (ids 1-8 only)
# ══════════════════════════════════════════════════════════
print("Processing hidden_pronouns.json ...")
hp = load_json('hidden_pronouns.json')
LATENT_MAP = {
    # id: (mabni_id, estimated_form)
    1: ('LATENT_PRONOUN_ANA',  'أَنَا'),
    2: ('LATENT_PRONOUN_ANTA', 'أَنْتَ'),
    3: ('LATENT_PRONOUN_ANTI', 'أَنْتِ'),
    4: ('LATENT_PRONOUN_HUWA', 'هُوَ'),
    5: ('LATENT_PRONOUN_HIYA', 'هِيَ'),
    6: ('LATENT_PRONOUN_HUM',  'هُمْ'),
    7: ('LATENT_PRONOUN_HUNNA','هُنَّ'),
    8: ('LATENT_PRONOUN_NAHNU','نَحْنُ'),
    # 9,10,11 = CONTRADICTORY
}
for r in hp:
    rid = r['id']
    if rid in LATENT_MAP:
        mid, ef = LATENT_MAP[rid]
        add(row(mid, '', 'LATENT', 'LATENT_PRONOUN', 'LATENT_PRONOUN_SERIES',
                'hidden_pronouns.json', rid, blk=False, cs='NONE', ef=ef))

# ══════════════════════════════════════════════════════════
# 3. DEMONSTRATIVE PRONOUNS — demonstrative_pronouns.json
# ══════════════════════════════════════════════════════════
print("Processing demonstrative_pronouns.json ...")
dem = load_json('demonstrative_pronouns.json')

# Only ids with grammatical_status=مبني, no dual forms (مثنى), deduplicated by surface_bare
DEM_INCLUDE = {
    # id: (mabni_id, canonical_surface)
    1:  ('HADHA',      'هَذَا'),
    2:  ('HADHIHI',    'هَذِهِ'),
    3:  ('HADHIY',     'هَذِي'),
    4:  ('HAHUNA',     'هَاهُنَا'),
    5:  ('DHAKA',      'ذَاكَ'),
    6:  ('TILKA',      'تِلْكَ'),
    7:  ('TIKA',       'تِيكَ'),
    9:  ('DHALIKA',    'ذَلِكَ'),
    11: ('HUNA_ISHARI','هُنَا'),
    12: ('HUNALIKA',   'هُنَالِكَ'),
    13: ('HAAULAI',    'هَؤُلَاءِ'),
    14: ('ULAIKA',     'أُولَئِكَ'),
    28: ('HUNAKA',     'هُنَاكَ'),
    30: ('AULAI',      'أُولَاءِ'),
    33: ('DHA',        'ذَا'),
}
DEM_MURAB = {8, 10, 15, 16}  # grammatical_status = معرب → UNDERLICENSED
seen_dem_bare = set()
for r in dem:
    rid = r['id']
    gs = r.get('grammatical_status','')
    nm = r.get('name','')
    nb = strip_diacritics(nfc(nm))
    if rid not in DEM_INCLUDE:
        continue
    if gs == 'معرب':
        continue
    if nb in seen_dem_bare:
        continue
    seen_dem_bare.add(nb)
    mid, sv = DEM_INCLUDE[rid]
    add(row(mid, sv, 'OVERT', 'DEMONSTRATIVE', 'DEMONSTRATIVE_SERIES',
            'demonstrative_pronouns.json', rid, blk=True, cs='NONE'))

# ══════════════════════════════════════════════════════════
# 4. RELATIVE PRONOUNS — relative_pronouns.json
# ══════════════════════════════════════════════════════════
print("Processing relative_pronouns.json ...")
rel = load_json('relative_pronouns.json')

# Dual forms (مثنى) → UNDERLICENSED
# Deduplicate by surface_bare
# Use only clearly well-formed non-garbage entries
REL_INCLUDE = {
    # id: (mabni_id, canonical_surface)
    1:  ('ALLADHI',     'الَّذِي'),
    2:  ('ALLATI',      'الَّتِي'),
    3:  ('MAN_MAWSUL',  'مَنْ'),
    4:  ('MA_MAWSUL',   'مَا'),
    9:  ('ALLADHINA',   'الَّذِينَ'),
    10: ('ALLALATI',    'اللَّاتِي'),
    11: ('ALLAIY',      'اللَّائِي'),
}
# Skip dual: ids 5,6,7,8,20,21,22,23,24,25 (مثنى)
seen_rel_bare = set()
for r in rel:
    rid = r['id']
    if rid not in REL_INCLUDE:
        continue
    num = r.get('number','')
    if num == 'مثنى':
        continue
    mid, sv = REL_INCLUDE[rid]
    sb = strip_diacritics(nfc(sv))
    if sb in seen_rel_bare:
        continue
    seen_rel_bare.add(sb)
    add(row(mid, sv, 'OVERT', 'RELATIVE_PRONOUN', 'RELATIVE_PRONOUN_SERIES',
            'relative_pronouns.json', rid, blk=True, cs='OPEN'))

# ══════════════════════════════════════════════════════════
# 5. CONDITIONAL — conditional_letters_tools.json
# ══════════════════════════════════════════════════════════
print("Processing conditional_letters_tools.json ...")
cond = load_json('conditional_letters_tools.json')

COND_MAP = {
    # id: (mabni_id, surface, lc, notes)
    1:  ('IN',          'إِنْ',      'CONDITIONAL_PARTICLE', ''),
    2:  ('IDHMA',       'إِذْمَا',   'CONDITIONAL_PARTICLE', ''),
    3:  ('LAW',         'لَوْ',      'CONDITIONAL_PARTICLE', ''),
    4:  ('LAWLA',       'لَوْلَا',   'CONDITIONAL_PARTICLE', ''),
    5:  ('LAWMA',       'لَوْمَا',   'CONDITIONAL_PARTICLE', ''),
    6:  ('AMMA',        'أَمَّا',    'CONDITIONAL_PARTICLE', ''),
    7:  ('AYNA_SHART',  'أَيْنَ',    'CONDITIONAL_NAME', ''),
    8:  ('AYNAMA',      'أَيْنَمَا', 'CONDITIONAL_NAME', ''),
    9:  ('KAYFAMA',     'كَيْفَمَا', 'CONDITIONAL_NAME', ''),
    10: ('MATA',        'مَتَى',     'CONDITIONAL_NAME', ''),
    11: ('MATA_MA',     'مَتَى مَا', 'CONDITIONAL_NAME', 'PHRASE_LEXEME'),
    12: ('HAYTHUMA',    'حَيْثُمَا', 'CONDITIONAL_NAME', ''),
    13: ('ANNA_SHART',  'أَنَّى',    'CONDITIONAL_NAME', ''),
    14: ('MAHMA',       'مَهْمَا',   'CONDITIONAL_NAME', ''),
    15: ('LAWMA2',      'لَوْمَا',   'CONDITIONAL_PARTICLE', 'variant/dup of LAWMA from cond file id15'),
    16: ('IDHA_SHART',  'إِذَا',     'CONDITIONAL_NAME', ''),
    17: ('KULLAMA',     'كُلَّمَا',  'CONDITIONAL_NAME', ''),
    18: ('MA_SHART',    'مَا',       'CONDITIONAL_NAME', ''),
    19: ('LAMMA_COND',  'لَمَّا',    'CONDITIONAL_NAME', ''),
    20: ('MAN_SHART',   'مَنْ',      'CONDITIONAL_NAME', ''),
    # 21: CONTRADICTORY/UNDERLICENSED (أَيَّ, mu'rab, swapped fields)
}
for r in cond:
    rid = r['id']
    if rid == 21:
        continue  # CONTRADICTORY
    if rid not in COND_MAP:
        continue
    mid, sv, lc, notes = COND_MAP[rid]
    if mid == 'LAWMA2':
        # Duplicate of LAWMA — record in notes but don't add separate entry
        continue
    sk = 'PHRASE' if 'PHRASE_LEXEME' in notes else 'OVERT'
    add(row(mid, sv, sk, lc, 'CONDITIONAL_SERIES',
            'conditional_letters_tools.json', rid, blk=True, cs='OPEN',
            notes=notes))

# ══════════════════════════════════════════════════════════
# 6. COPULATIVE PARTICLES — copulative_particle.json
# ══════════════════════════════════════════════════════════
print("Processing copulative_particle.json ...")
cop = load_json('copulative_particle.json')
COP_MAP = {
    1: ('INNA',              'إِنَّ'),
    2: ('ANNA',              'أَنَّ'),
    3: ('KAANNA',            'كَأَنَّ'),
    4: ('LAKINNA',           'لَكِنَّ'),
    5: ('LAYTA',             'لَيْتَ'),
    6: ('LAALLA',            'لَعَلَّ'),
    7: ('LA_NAFIYA_LIL_JINS','لَا'),
}
for r in cop:
    rid = r['id']
    mid, sv = COP_MAP[rid]
    add(row(mid, sv, 'OVERT', 'COPULATIVE_PARTICLE', 'COPULATIVE_SERIES',
            'copulative_particle.json', rid, blk=True, cs='OPEN'))

# ══════════════════════════════════════════════════════════
# 7. JAZM TOOLS — jazm_tools.json
# ══════════════════════════════════════════════════════════
print("Processing jazm_tools.json ...")
jazm = load_json('jazm_tools.json')

JAZM_MAP = {
    # id: (mabni_id, surface, lc)
    1:  ('LAM',          'لَمْ',      'JAZM_PARTICLE'),
    2:  ('LAMMA_JAZM',   'لَمَّا',    'JAZM_PARTICLE'),
    3:  ('LI_JAZM',      'لِ',        'JAZM_PARTICLE'),
    4:  ('LA_NAHY',      'لَا النَّاهِيَة','JAZM_PARTICLE'),
    5:  ('IN_SHART',     'إِنْ',      'JAZM_PARTICLE'),
    6:  ('IDHMA_JAZM',   'إِذْمَا',   'JAZM_PARTICLE'),
    7:  ('MAN_JAZM',     'مَنْ',      'JAZM_NAME'),
    8:  ('MA_JAZM',      'مَا',       'JAZM_NAME'),
    9:  ('MAHMA_JAZM',   'مَهْمَا',   'JAZM_NAME'),
    10: ('MATA_JAZM',    'مَتَى',     'JAZM_NAME'),
    11: ('AYYAANA_JAZM', 'أَيَّانَ',  'JAZM_NAME'),
    12: ('AYNA_JAZM',    'أَيْنَ',    'JAZM_NAME'),
    13: ('HAYTHUMA_JAZM','حَيْثُمَا', 'JAZM_NAME'),
    14: ('ANNA_JAZM',    'أَنَّى',    'JAZM_NAME'),
    15: ('IYY_JAZM',     'أَيُّ',     'JAZM_NAME'),
    16: ('AYYAMA_JAZM',  'أَيَّ',     'JAZM_NAME'),
    17: ('AYYAMA2_JAZM', 'أَيَّ',     'JAZM_NAME'),  # dup
    18: ('AYYAMA3_JAZM', 'أَيَّ',     'JAZM_NAME'),  # dup
    19: ('AYNAMA_JAZM',  'أَيْنَمَا', 'JAZM_NAME'),
    20: ('KAYFAMA_JAZM', 'كَيْفَمَا', 'JAZM_NAME'),
}
seen_jazm = set()
for r in jazm:
    rid = r['id']
    if rid not in JAZM_MAP:
        continue
    mid, sv, lc = JAZM_MAP[rid]
    sb = strip_diacritics(nfc(sv))
    # deduplicate by (lc+bare) to avoid same-surface duplicates within jazm
    key = lc + '|' + sb
    if key in seen_jazm and rid in (17, 18):
        continue
    seen_jazm.add(key)
    # But we allow same surface in different classes (e.g. IN in cond vs jazm get diff IDs)
    add(row(mid, sv, 'OVERT', lc, 'JAZM_SERIES',
            'jazm_tools.json', rid, blk=True, cs='OPEN'))

# ══════════════════════════════════════════════════════════
# 8. COORDINATING CONJUNCTIONS — deduplicated
# ══════════════════════════════════════════════════════════
print("Processing coordinating_conjunctions.json ...")
conj = load_json('coordinating_conjunctions.json')

CONJ_MAP_SURFACE = {
    'وَ':   'WA_ATF',
    'فَ':   'FA_ATF',
    'ثُمَ': 'THUMMA_ATF',   # note: missing shadda in source id 3
    'ثُمَّ':'THUMMA_ATF',   # normalised form
    'حَتّى':'HATTA_ATF',
    'حَتَّى':'HATTA_ATF',
    'أَوْ': 'AW',
    'أَمْ': 'AM',
    'بَلْ': 'BAL',
    'لَكِنْ':'LAKIN_ATF',
    'لَا':  'LA_ATF',
    'إِمَّا':'IMMA',
}
seen_conj = set()
for r in conj:
    rid = r['id']
    letter = r.get('letter','').strip()
    # ids 20,21: أَو missing sukun — report, skip
    bare = strip_diacritics(nfc(letter))
    if letter == 'أَو' or (bare == 'أو' and rid in (20,21)):
        continue  # data entry error
    # Find matching ID
    found_mid = None
    for k, v in CONJ_MAP_SURFACE.items():
        if strip_diacritics(nfc(k)) == bare:
            found_mid = v
            break
    if found_mid is None:
        continue
    if found_mid in seen_conj:
        continue
    seen_conj.add(found_mid)
    # normalise surface
    sv_norm = nfc(letter)
    if bare == 'ثم':
        sv_norm = 'ثُمَّ'  # fix missing shadda
    add(row(found_mid, sv_norm, 'OVERT', 'COORDINATING_CONJUNCTION', found_mid,
            'coordinating_conjunctions.json', rid, blk=True, cs='NONE'))

# ══════════════════════════════════════════════════════════
# 9. INTERROGATIVE PARTICLES — interrogative_letters_tools.json
# ══════════════════════════════════════════════════════════
print("Processing interrogative_letters_tools.json ...")
iq_let = load_json('interrogative_letters_tools.json')
# id 1: هَلْ, ids 2-6: أَ (deduplicate to one)
seen_iq_let = set()
IQ_LET_MAP = {
    1: ('HAL', 'هَلْ', 'INTERROGATIVE_PARTICLE'),
    2: ('HAMZA_ISTIFHAM', 'أَ', 'INTERROGATIVE_PARTICLE'),
}
for r in iq_let:
    rid = r['id']
    if rid in IQ_LET_MAP:
        mid, sv, lc = IQ_LET_MAP[rid]
        if mid not in seen_iq_let:
            seen_iq_let.add(mid)
            add(row(mid, sv, 'OVERT', lc, mid,
                    'interrogative_letters_tools.json', rid, blk=True, cs='NONE'))

# ══════════════════════════════════════════════════════════
# 10. INTERROGATIVE NAMES — interrogative_tools_categories.json
# ══════════════════════════════════════════════════════════
print("Processing interrogative_tools_categories.json ...")
iq_cat = load_json('interrogative_tools_categories.json')
IQ_CAT_MAP = {
    # id: (mabni_id, surface, lc)
    1:  ('MAN_ISTIFHAM',   'مَنْ',   'INTERROGATIVE_NAME'),
    2:  ('MAN_DHA',        'مَنْ ذَا','INTERROGATIVE_NAME'),
    3:  ('MA_ISTIFHAM',    'مَا',    'INTERROGATIVE_NAME'),
    4:  ('MADHA',          'مَاذَا', 'INTERROGATIVE_NAME'),
    5:  ('MATA_ISTIFHAM',  'مَتَى',  'INTERROGATIVE_NAME'),
    6:  ('AYYAAN_ISTIFHAM','أَيَّانَ','INTERROGATIVE_NAME'),
    7:  ('AYNA_ISTIFHAM',  'أَيْنَ', 'INTERROGATIVE_NAME'),
    8:  ('ANNA_ISTIFHAM',  'أَنَّى', 'INTERROGATIVE_NAME'),
    9:  ('KAM_ISTIFHAM2',  'كَمْ',   'INTERROGATIVE_NAME'),
    10: ('KAYFA',          'كَيْفَ', 'INTERROGATIVE_NAME'),
    11: ('AYYA_ISTIFHAM',  'أَيُّ',  'INTERROGATIVE_NAME'),
    # 12,13,14,15,16,17: particles/duplicates — skip
}
for r in iq_cat:
    rid = r['id']
    if rid in IQ_CAT_MAP:
        mid, sv, lc = IQ_CAT_MAP[rid]
        sk = 'PHRASE' if ' ' in sv else 'OVERT'
        add(row(mid, sv, sk, lc, mid,
                'interrogative_tools_categories.json', rid, blk=True, cs='NONE'))

# ══════════════════════════════════════════════════════════
# 11. ANSWER PARTICLES — letters_answers.json
# ══════════════════════════════════════════════════════════
print("Processing letters_answers.json ...")
ans = load_json('letters_answers.json')
ANS_MAP = {
    1:  ('NAAM',      'نَعَمْ'),
    2:  ('BALA',      'بَلَى'),
    3:  ('AJAL',      'أَجَلْ'),
    4:  ('IN_JAWAB',  'إِنَّ'),   # جواب بمعنى أجل (different from copulative إِنَّ)
    5:  ('IY_JAWAB',  'إِيْ'),
    6:  ('AWA',       'أَوَى'),
    7:  ('AFI',       'أَفِي'),
    8:  ('NAAMMA',    'نَعَمَّا'),
    9:  ('KALLA',     'كَلَّا'),
    10: ('BAJAL',     'بَجَلْ'),
}
for r in ans:
    rid = r['id']
    if rid in ANS_MAP:
        mid, sv = ANS_MAP[rid]
        notes = 'answer particle; same surface as copulative إِنَّ but different function' if rid == 4 else ''
        add(row(mid, sv, 'OVERT', 'ANSWER_PARTICLE', mid,
                'letters_answers.json', rid, blk=True, cs='NONE', notes=notes))

# ══════════════════════════════════════════════════════════
# 12. VOCATIVE PARTICLES — vocative_particles.json
# ══════════════════════════════════════════════════════════
print("Processing vocative_particles.json ...")
voc = load_json('vocative_particles.json')
VOC_MAP = {
    1: ('YA_NIDA',   'يَا'),
    2: ('AYYA_NIDA', 'أَيَا'),
    3: ('HAYA_NIDA', 'هَيَا'),
    4: ('AYI_NIDA',  'أَيْ'),
    5: ('AY_NIDA',   'آيْ'),
    6: ('AYYUHA',    'أَيُّهَا'),
    7: ('WA_NIDA',   'وَا'),
    8: ('AA_NIDA',   'آ'),
    9: ('A_NIDA',    'أَ'),
}
for r in voc:
    rid = r['id']
    if rid in VOC_MAP:
        mid, sv = VOC_MAP[rid]
        add(row(mid, sv, 'OVERT', 'VOCATIVE_PARTICLE', mid,
                'vocative_particles.json', rid, blk=True, cs='OPEN'))

# ══════════════════════════════════════════════════════════
# 13. PRESENT NASEB TOOLS — present_naseb_tools.json
# ══════════════════════════════════════════════════════════
print("Processing present_naseb_tools.json ...")
naseb = load_json('present_naseb_tools.json')
NASEB_MAP = {
    1:  ('AN',       'أَنْ'),
    2:  ('LAN',      'لَنْ'),
    3:  ('IDHAN',    'إِذَنْ'),
    4:  ('KAY_NASB', 'كَيْ'),
    5:  ('LI_NASB',  'لِ'),
    6:  ('LI_JUHUD', 'لِ'),     # لام الجحود — same surface, diff function
    7:  ('HATTA_NASB','حَتَّى'),
    8:  ('FA_SABABIYYA','فَ'),
    9:  ('WA_MAIYYA', 'وَ'),
    10: ('AW_NASB',  'أَوْ'),
}
seen_naseb = set()
for r in naseb:
    rid = r['id']
    if rid in NASEB_MAP:
        mid, sv = NASEB_MAP[rid]
        if mid in seen_naseb:
            continue
        seen_naseb.add(mid)
        add(row(mid, sv, 'OVERT', 'NASEB_PARTICLE', mid,
                'present_naseb_tools.json', rid, blk=True, cs='OPEN'))

# ══════════════════════════════════════════════════════════
# 14. PREPOSITIONS — preposition_meanings.json (deduplicate by surface)
# ══════════════════════════════════════════════════════════
print("Processing preposition_meanings.json ...")
prep = load_json('preposition_meanings.json')
PREP_MAP = {
    'بِ':             'BI_PREP',
    'تَ':             'TA_QASAM',
    'وَ':             'WA_QASAM',
    'كَ':             'KA_PREP',
    'عَنْ':           'AN_PREP',
    'عن':             'AN_PREP',
    'فِي ْ':          'FI_PREP',
    'فِيْ':           'FI_PREP',
    'مُذْ وَ مُنْذُ': None,  # compound — handled separately
    'لِ':             'LI_PREP',
    'لَ':             'LA_ISTIGHATHA',
    'مِنَ':           'MIN_PREP',
    'مِنْ':           'MIN_PREP',
    'إِلَى':          'ILA_PREP',
    'رُبَّ':          'RUBBA_PREP',
    'عَلَى':          'ALA_PREP',
    'حَتَّى':         'HATTA_PREP',
    'خَلَا':          'KHALA_PREP',
    'كَيْ':           'KAY_PREP',
    'لَعَلَّ':        'LAALLA_PREP',
    'مَتَى':          'MATA_PREP',
    'لَوْلَا':        'LAWLA_PREP',
    'عَدَا':          'ADAA_PREP',
    'حَاشَا':         'HASHA_PREP',
}
seen_prep = {}
for r in prep:
    rid = r['id']
    surface = r.get('preposition','').strip()
    bare = strip_diacritics(nfc(surface))
    # Map surface to mabni_id
    mid = PREP_MAP.get(surface) or PREP_MAP.get(bare)
    if mid is None:
        # compound مذ ومنذ
        if 'مذ' in bare or 'منذ' in bare:
            if 'MUNDHU_PREP' not in seen_ids:
                add(row('MUNDHU_PREP', 'مُنْذُ', 'OVERT', 'PREPOSITION', 'MUNDHU_PREP',
                        'preposition_meanings.json', rid, blk=True, cs='NONE',
                        notes='compound entry مُذْ وَ مُنْذُ; also MUDH_PREP'))
            if 'MUDH_PREP' not in seen_ids:
                add(row('MUDH_PREP', 'مُذْ', 'OVERT', 'PREPOSITION', 'MUDH_PREP',
                        'preposition_meanings.json', rid, blk=True, cs='NONE',
                        notes='from compound entry مُذْ وَ مُنْذُ'))
        continue
    if mid in seen_prep:
        continue
    seen_prep[mid] = rid
    # Normalize surface
    sv_norm = nfc(surface)
    if bare == 'في':
        sv_norm = 'فِي'
    elif bare == 'عن':
        sv_norm = 'عَنْ'
    add(row(mid, sv_norm, 'OVERT', 'PREPOSITION', mid,
            'preposition_meanings.json', rid, blk=True, cs='NONE'))

# ══════════════════════════════════════════════════════════
# 15. BUILT-IN ADVERBS — built_in_adverbs.json
# ══════════════════════════════════════════════════════════
print("Processing built_in_adverbs.json ...")
adv = load_json('built_in_adverbs.json')
ADV_MAP = {
    1:  ('HAYTHU',        'حَيْثُ',    ''),
    2:  ('MUNDHU_ZARF',   'مُنْذُ',    ''),
    3:  ('QATTU',         'قَطُّ',     ''),
    4:  ('ALAN',          'الْآنَ',    ''),
    5:  ('GHADAN',        'غَدًا',     ''),
    6:  ('ALLAYLATA',     'اللَّيْلَةَ',''),
    7:  ('THUMMA_ZARF',   'ثُمَّ',     'ظرف مكان; different from ثُمَّ conjunction'),
    8:  ('AYYANNA',       'أَيَّانَ',  ''),
    9:  ('HUNAKA',        'هُنَاكَ',   ''),
    10: ('HUNALIKA_ZARF', 'هُنَالِكَ', 'ظرف; note HUNALIKA also in demonstratives'),
    11: ('THAMM',         'ثَمَّ',     ''),
    12: ('THAMMATA',      'ثَمَّةَ',   'id 12: suspicious Unicode (double diacritics on ث and م in source)'),
    13: ('IDH',           'إِذْ',      ''),
    14: ('MUDH_ZARF',     'مُذْ',      ''),
    15: ('LADA',          'لَدَى',     ''),
    16: ('IWADHU',        'عِوَضُ',    ''),
    17: ('AYNA_ZARF',     'أَيْنَ',    ''),
    18: ('MATA_ZARF',     'مَتَى',     ''),
    19: ('HUNA',          'هُنَا',     ''),
    20: ('ANNA_ZARF',     'أَنَّى',    ''),
    21: ('IDHA_ZARF',     'إِذَا',     ''),
}
for r in adv:
    rid = r['id']
    if rid not in ADV_MAP:
        continue
    mid, sv, notes = ADV_MAP[rid]
    if mid in seen_ids:
        continue  # already added from demonstratives (HUNAKA, HUNALIKA, HUNA)
    add(row(mid, sv, 'OVERT', 'ADVERBIAL_MABNI', mid,
            'built_in_adverbs.json', rid, blk=True, cs='NONE', notes=notes))

# ══════════════════════════════════════════════════════════
# 16. VERB NAMES — verb_name.json
# ══════════════════════════════════════════════════════════
print("Processing verb_name.json ...")
vn = load_json('verb_name.json')

# Transliterate Arabic name → ASCII ID
def transliterate_vn(name: str) -> str:
    """Simple transliteration for verb name IDs."""
    name = strip_diacritics(name.strip())
    # Remove spaces and special chars for ID
    parts = name.split()
    if len(parts) > 1:
        return '_'.join(transliterate_vn(p) for p in parts)
    result = []
    MAP = {
        'ا':'A','أ':'A','إ':'I','آ':'A','ء':'',
        'ب':'B','ت':'T','ث':'TH','ج':'J','ح':'H','خ':'KH',
        'د':'D','ذ':'DH','ر':'R','ز':'Z','س':'S','ش':'SH',
        'ص':'S','ض':'D','ط':'T','ظ':'DH','ع':'','غ':'GH',
        'ف':'F','ق':'Q','ك':'K','ل':'L','م':'M','ن':'N',
        'ه':'H','و':'W','ي':'Y','ى':'A','ة':'A',
        'ع':'','ى':'A','/':'_','-':'_',
    }
    for ch in name:
        result.append(MAP.get(ch, ''))
    r = ''.join(result).upper().strip('_')
    # Clean up
    r = re.sub(r'_+','_', r)
    r = re.sub(r'[^A-Z0-9_]','', r)
    return r or 'VN'

seen_vn_bare = set()
VN_MANUAL = {
    56: 'AAMEEN',
    57: 'HAYYA',
    58: 'HAYYA2',
    59: 'HIYTA',
    60: 'HALUMMA_ILA',
    61: 'HALUMMA_KADHA',
    62: 'HAOUM',
    63: 'SAH',
    64: 'IYHI',
    65: 'MIH',
    66: 'RUWAYDAKA',
    67: 'BALHA',
    68: 'HAKUM',
    69: 'DUNAK',
    70: 'HISSA',
    71: 'TIYD',
    72: 'HIYHALA',
    73: 'HUDAYYAKA',
    74: 'BAS',
    75: 'ALNAJAA',
    76: 'IYHA',
    77: 'FIDAA',
    78: 'QADK',
    79: 'KADHAK',
    80: 'HADADIYK',
    81: 'LADAYK',
    82: 'INDAK',
    83: 'WAYHA',
    84: 'WARAAK',
    85: 'ILAYK',
    86: 'ILAYK_AN',
    87: 'ILAYY',
    88: 'ALAYK',
    89: 'MAKANAK',
    90: 'AMAMAK',
    91: 'HADHARI',
    92: 'NIZALI',
    93: 'HIYHATA',
    94: 'BUTAAN',
    95: 'SHATTAN',
    96: 'SURAAN',
    97: 'WASHKAAN',
    98: 'DUHDURRAYN',
    99: 'QAD_VN',
    100: 'HASBUK',
    101: 'BAJLU',
    102: 'UFF',
    103: 'WAY',
    104: 'WAHA',
    105: 'AAH',
    106: 'AWAHU',
    107: 'QATTU_VN',
    108: 'BAKH',
    109: 'ZUH',
    110: 'AKH',
    111: 'HAKA',
    112: 'QATTUK',
}
for r in vn:
    rid = r['id']
    name = r.get('name','').strip()
    sv = nfc(name)
    sb = strip_diacritics(sv)
    # Multi-word → PHRASE
    sk = 'PHRASE' if ' ' in sb else 'OVERT'
    mid = VN_MANUAL.get(rid)
    if not mid:
        mid = 'VN_' + transliterate_vn(name)
    if mid in seen_ids:
        # make unique
        mid = mid + f'_{rid}'
    seen_vn_bare.add(sb)
    add(row(mid, sv, sk, 'VERB_NAME', mid,
            'verb_name.json', rid, blk=True, cs='NONE'))

# ══════════════════════════════════════════════════════════
# 17. KINAYA NAMES — kinaya_names.json
# ══════════════════════════════════════════════════════════
print("Processing kinaya_names.json ...")
kin = load_json('kinaya_names.json')
KIN_MAP = {
    1: ('KAM_ISTIFHAMIYYA', 'كَمْ'),
    2: ('KAM_KHABARIYYA',   'كَمْ'),
    3: ('KAAYYIN',          'كَأَيِّنْ'),
    4: ('KAAIN',            'كَائِنْ'),
    5: ('KAAIYY',           'كَأَيٍّ'),
    6: ('KADHDHAK',         'كَذَا'),
    7: ('KAYT',             'كَيْتَ'),
    8: ('KAYYIT',           'ذَيْتَ'),
    9: ('BIDA',             'بِضْع'),
}
for r in kin:
    rid = r['id']
    if rid in KIN_MAP:
        mid, sv = KIN_MAP[rid]
        notes = f"type: {r.get('type','')}"
        add(row(mid, sv, 'OVERT', 'KINAYA_NAME', mid,
                'kinaya_names.json', rid, blk=True, cs='NONE', notes=notes))

# ══════════════════════════════════════════════════════════
# Write CSV
# ══════════════════════════════════════════════════════════
OUT_CSV = BASE / 'mabniyat_catalog_split_vocalized.csv'
with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(catalog)

print(f"\n✓ Catalog written: {OUT_CSV}")
print(f"  Total rows: {len(catalog)}")

# ──────────────────────────────────────────────────────────
# Verify operators catalog unchanged
# ──────────────────────────────────────────────────────────
import subprocess
result = subprocess.run(['md5sum', str(BASE/'operators_catalog_split_vocalized.csv')],
                       capture_output=True, text=True)
print(f"\nOperators catalog md5: {result.stdout.strip()}")
