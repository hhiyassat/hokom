"""
src/hokom/demo/localization.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Presentation-only localization service for Ayat al-Dayn client reports.

Scope:
  - Translates CSV column headers for both report CSVs (results + layers).
  - Translates display-facing enum values (word_class, layer_name, etc.).
  - Translates composite values (booleans, semicolon/space-joined lists).
  - Provides HTML section labels for localized HTML output.
  - Provides terminal labels for render_runtime_identity / render_summary_dashboard.

Out of scope (never touched here):
  - Pipeline enums, internal constants, or runtime state.
  - Canonical identifiers: claim_key, evaluation_id, slot_graph_digest,
    bridge_id, runtime_*_commit, runtime_vendor_sha.
  - Arabic token surfaces, canonical roots, internal JSON blobs, trace IDs.

Missing-translation policy:
  - All public functions emit a UserWarning and fall back to the original
    key/value when no translation is found.  They never return silently
    wrong output and never silently discard a value.

API:
    load_locale(lang: str) -> dict
    translate_header(col_key, lang, section='results') -> str
    translate_value(category, value, lang) -> str
    translate_composite_value(category, value, lang, separators=...) -> str
    get_html_label(key, lang) -> str
    get_terminal_label(key, lang) -> str
"""
from __future__ import annotations

import warnings
from functools import lru_cache
from pathlib import Path

# Locale YAML lives at <repo_root>/config/localization/ayat_al_dayn_report.yaml.
# This file is at <repo_root>/src/hokom/demo/localization.py, so walk up 4 levels.
_YAML_PATH: Path = (
    Path(__file__).parent   # src/hokom/demo/
    .parent                 # src/hokom/
    .parent                 # src/
    .parent                 # <repo_root>
    / 'config'
    / 'localization'
    / 'ayat_al_dayn_report.yaml'
)

_SUPPORTED_LANGS: tuple[str, ...] = ('en', 'ar')

# Separator → Arabic output separator mapping for translate_composite_value.
# When a separator is detected in the input, the output uses the Arabic equivalent.
_SEP_OUTPUT_MAP: dict[str, str] = {
    '; ':  '؛ ',
    ';':   '؛ ',
    ' | ': ' | ',
    '|':   ' | ',
    ', ':  '، ',
    ',':   '، ',
    ' ':   ' ',
}


@lru_cache(maxsize=None)
def _load_yaml() -> dict:
    """
    Load and cache the full locale YAML (once per interpreter session).

    Raises FileNotFoundError if the YAML is absent — fail loudly so
    mis-configured environments are caught immediately.
    """
    try:
        import yaml
    except ImportError as exc:
        raise ImportError(
            "PyYAML is required for localization. "
            "Install it with: pip install pyyaml"
        ) from exc

    if not _YAML_PATH.exists():
        raise FileNotFoundError(
            f"Locale file not found: {_YAML_PATH}. "
            "Expected at config/localization/ayat_al_dayn_report.yaml."
        )

    with _YAML_PATH.open(encoding='utf-8') as fh:
        return yaml.safe_load(fh)


def load_locale(lang: str) -> dict:
    """
    Return the locale sub-dict for *lang* (e.g. 'en', 'ar').

    Raises ValueError for unknown locales so callers fail loudly rather
    than silently producing wrong-language output.
    """
    data = _load_yaml()
    if lang not in data:
        raise ValueError(
            f"Unknown locale {lang!r}. "
            f"Available: {sorted(data.keys())}. "
            f"Check config/localization/ayat_al_dayn_report.yaml."
        )
    return data[lang]


def translate_header(col_key: str, lang: str, section: str = 'results') -> str:
    """
    Return the translated column header for *col_key* in *section*.

    Parameters
    ----------
    col_key : str
        The canonical (English) column name, e.g. 'word_class'.
    lang : str
        Target locale, e.g. 'ar' or 'en'.
    section : str
        CSV section: 'results' (45-col results CSV) or
        'layers' (53-col Taaqol layers CSV).

    Returns the original *col_key* with a UserWarning when no translation
    is found.  Canonical identifier columns (claim_key, evaluation_id,
    etc.) map to themselves in every locale.
    """
    try:
        locale = load_locale(lang)
    except (ValueError, FileNotFoundError, ImportError) as exc:
        warnings.warn(
            f"[localization] Could not load locale {lang!r}: {exc}; "
            f"using col_key {col_key!r} unchanged.",
            UserWarning, stacklevel=2,
        )
        return col_key

    headers = locale.get('csv_headers', {}).get(section, {})
    if col_key in headers:
        return headers[col_key]

    warnings.warn(
        f"[localization] No {lang!r} header translation for {col_key!r} "
        f"in section {section!r}; using key unchanged.",
        UserWarning, stacklevel=2,
    )
    return col_key


def translate_value(category: str, value: str, lang: str) -> str:
    """
    Return the translated display string for enum *value* in *category*.

    Parameters
    ----------
    category : str
        Enum category key as defined in the YAML, e.g. 'word_class',
        'layer_name', 'layer_state', 'gamma_state', 'slot_id',
        'reason_code', 'cra_reason_code', 'booleans', etc.
    value : str
        The canonical (English) enum value, e.g. 'FI3L', 'EXECUTED'.
    lang : str
        Target locale, e.g. 'ar' or 'en'.

    Rules:
      - Returns *value* unchanged when *value* is empty/None.
      - Returns *value* unchanged when lang == 'en' (English is canonical).
      - Emits UserWarning and returns *value* unchanged when no translation
        is found in the YAML.
      - Never call this for canonical identifiers (claim_key, evaluation_id,
        SHAs, slot_graph_digest, trace steps, Arabic token surfaces).
    """
    if not value or lang == 'en':
        return value

    try:
        locale = load_locale(lang)
    except (ValueError, FileNotFoundError, ImportError) as exc:
        warnings.warn(
            f"[localization] Could not load locale {lang!r}: {exc}; "
            f"returning value {value!r} unchanged.",
            UserWarning, stacklevel=2,
        )
        return value

    enums = locale.get('enums', {})
    cat_dict = enums.get(category, {})
    if value in cat_dict:
        return cat_dict[value]

    warnings.warn(
        f"[localization] No {lang!r} translation for "
        f"enum {category!r}[{value!r}]; using original value unchanged.",
        UserWarning, stacklevel=2,
    )
    return value


def translate_composite_value(
    category: str,
    value: object,
    lang: str,
    separators: tuple[str, ...] = ('; ', ';', ' | ', '|'),
) -> str:
    """
    Translate a composite value: boolean string, separator-joined list, or scalar.

    Parameters
    ----------
    category : str
        Enum category for individual token translation (e.g. 'layer_name',
        'slot_id', 'reason_code', 'cra_reason_code', 'booleans').
    value : object
        The raw field value.  Converted to str; None/empty returned as-is.
    lang : str
        Target locale.  When 'en', returns str(value) unchanged.
    separators : tuple[str, ...]
        Ordered list of separator strings to detect.  The first one found in
        the value string is used to split.  Single-space ' ' is handled
        specially — pass (' ',) explicitly for space-separated lists.

    Behaviour
    ---------
    - Empty / None input → returns '' without warnings.
    - Boolean strings ('True'/'False') → delegates to translate_value('booleans', ...).
    - Separator-joined strings → splits, translates each token via translate_value,
      rejoins with the Arabic-equivalent separator (e.g. '; ' → '؛ ').
    - Single token (no separator found) → delegates to translate_value(category, ...).
    - Preserves member ordering; never silently discards a member.
    - Emits UserWarning for each token not found in the YAML category.
    """
    if value is None:
        return ''

    str_val = str(value).strip()
    if not str_val:
        return str_val

    if lang == 'en':
        return str_val

    # Boolean handling: intercept before separator detection
    if str_val in ('True', 'False', 'true', 'false'):
        return translate_value('booleans', str_val, lang)

    # Detect separator (try each candidate in order)
    detected_sep: str | None = None
    for sep in separators:
        if sep in str_val:
            detected_sep = sep
            break

    if detected_sep is None:
        # No separator found — treat as single scalar token
        return translate_value(category, str_val, lang)

    # Split on detected separator, strip each token, discard empty strings
    raw_tokens = str_val.split(detected_sep)
    tokens = [t.strip() for t in raw_tokens]
    tokens = [t for t in tokens if t]

    if not tokens:
        return str_val

    # Translate each token
    translated = [translate_value(category, t, lang) for t in tokens]

    # Choose output separator: Arabic equivalent of detected_sep
    out_sep = _SEP_OUTPUT_MAP.get(detected_sep, detected_sep)

    return out_sep.join(translated)


def get_html_label(key: str, lang: str) -> str:
    """
    Return the HTML section label for *key* in *lang*.

    Used by format_html() to localise page titles, section headings,
    stat card labels, and the defer-notice block.  Falls back to *key*
    with a UserWarning when the translation is absent.
    """
    try:
        locale = load_locale(lang)
    except (ValueError, FileNotFoundError, ImportError) as exc:
        warnings.warn(
            f"[localization] Could not load locale {lang!r}: {exc}; "
            f"using label key {key!r} unchanged.",
            UserWarning, stacklevel=2,
        )
        return key

    labels = locale.get('html_labels', {})
    if key in labels:
        return labels[key]

    warnings.warn(
        f"[localization] No {lang!r} HTML label for {key!r}; "
        f"using key unchanged.",
        UserWarning, stacklevel=2,
    )
    return key


def get_terminal_label(key: str, lang: str) -> str:
    """
    Return the terminal output label for *key* in *lang*.

    Used by render_runtime_identity() and render_summary_dashboard() to
    localise row labels when --lang ar is active.  Falls back to *key*
    with a UserWarning when the translation is absent.

    Technical names (Python, Hokom, Taaqol) remain unchanged in Arabic
    because they are product/tool names, not descriptive labels.
    """
    try:
        locale = load_locale(lang)
    except (ValueError, FileNotFoundError, ImportError) as exc:
        warnings.warn(
            f"[localization] Could not load locale {lang!r}: {exc}; "
            f"using terminal label key {key!r} unchanged.",
            UserWarning, stacklevel=2,
        )
        return key

    labels = locale.get('terminal_labels', {})
    if key in labels:
        return labels[key]

    warnings.warn(
        f"[localization] No {lang!r} terminal label for {key!r}; "
        f"using key unchanged.",
        UserWarning, stacklevel=2,
    )
    return key
