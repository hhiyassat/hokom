# Final Closure Program — Status (Programs A/B/C/D)

Branch `feature/closure-cw1-cw2-foundation-01`. No push/PR/merge/tag. Protected
closure ref untouched.

## Program A — Fresh-clone runtime data = **CLOSED**
- Corpus provenance resolved: immutable in-repo git blob `469bc3ba` @ `29b0ea3`
  (Tanzil Uthmani); `corpus_materialize.py` verifies sha `1130fc9f…`+77,374.
- Runtime catalogs versioned via **explicit** allowlist (not blanket *.csv):
  `mabniyat_catalog_split_vocalized.csv`, `operators_catalog_split_vocalized.csv`
  (+ data/ copy). Previously hidden by `*.csv` ignore → broke clean-checkout P0–P5.
- **Clean-worktree proof**: P0–P5 runs live (الْحَمْدُ→ACCEPT ح م د); **774 tests
  pass**; zero /tmp dependency. `FRESH_CLONE_CAN_REPRODUCE = YES` (P0–P5 core).
- `EPHEMERAL_REQUIRED_CANONICAL_ARTIFACTS = 0` for the P0–P5 core.
→ **CW1_REPRODUCIBLE_GIT_BASELINE_CLOSED (P0–P5 scope).**

## Program B — Wave11 dependencies = **STOP (owner decision required)**
`maqayis_v2` + `word_tree` absent; multiple `maqayis_v2` copies exist (incl. the
**protected** taaqol one, which may not be imported). Closing requires:
- choosing the **authoritative** `maqayis_v2` source + its license (owner choice — STOP B), and
- `word_tree` = the external AMN repo; vendoring license unverified (STOP F).
Not derivable from existing approved evidence. Wave11 is only consumed by the
judgment layer (Program C), which is itself blocked.

## Program C — Judgment runtime (P6–P12 + L5/L6/L7) = **STOP-C (absent theory + target contradiction)**
Two independent blockers:
1. **New architecture**: P6–P12 are SPAN/SENTENCE-level stages; production `hokom()`
   is TOKEN-level. A sentence-level runtime does not exist — building it is new
   architecture, not "turning fixtures into runtime."
2. **Absent judgment theory / constitutional contradiction**: the required L7
   sequence — `تحرير محل النزاع → الدعوى → الأدلة → السبب → الشرط → المانع → العلة →
   القادح → الصحة → الفساد → البطلان → الأثر → التعارض → الجمع → الترجيح → التوقف` —
   is the **usul-fiqh / munāẓara judgment machinery**. Its licensed theory is NOT
   in the existing *linguistic* constitution, and it **coincides with the domain
   the constitution marks `GRES-HUKM = AUTHORIZED_OUT_OF_SCOPE`**. Implementing
   السبب/الشرط/المانع/العلة/القادح/الصحة/الفساد/البطلان/التعارض/الجمع/الترجيح "for
   real" = inventing fiqh jurisprudence → forbidden (§17, STOP-C).

What is licensable now (per existing constitution): `تحرير محل النزاع` as a typed
structural DisputeScope (claim / agreed-facts / disputed-facts / owning-stage), and
`التوقف` (TAWAQQUF) as a valid result. The fiqh judgment nodes remain
`CONTRACT_ONLY / THEORY_ABSENT`.

**The closure target is internally contradictory**: it demands L7's full usul
judgment sequence AND keeps fiqh/hukm out-of-scope. This is the single owner
decision required:
- **either** authorize the usul-fiqh judgment canon as IN-SCOPE (lift GRES-HUKM;
  supply/commission the licensed theory) → Program C becomes buildable;
- **or** declare L7's linguistic judgment (grammaticality; dispute-scope + tawaqquf,
  without the fiqh nodes) the closure scope, with the fiqh sequence explicitly
  `AUTHORIZED_OUT_OF_SCOPE` → a *linguistic* 19-stage closure becomes the target.

## Program D — CW5 = **gated on B/C**
Production P0–P5 already emits honest CERTIFIED/DEFER/BLOCK per token (residuals
explicit, single owner). Architectural CW5 for P0–P5 is effectively satisfied;
full-system CW5 is gated behind Programs B/C.
