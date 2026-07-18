"""
text_cleaner.py — Basic text preprocessing utilities
"""

import re
import string


def to_lowercase(text: str) -> str:
    return text.lower()


def remove_punctuation(text: str) -> str:
    return text.translate(str.maketrans("", "", string.punctuation))


def remove_extra_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_urls(text: str) -> str:
    return re.sub(r"https?://\S+|www\.\S+", "", text)


def remove_html_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def remove_numbers(text: str) -> str:
    return re.sub(r"\d+", "", text)


def clean(
    text: str,
    lowercase: bool = True,
    remove_punct: bool = True,
    remove_nums: bool = False,
    remove_urls_flag: bool = True,
    remove_html: bool = True,
) -> str:
    """Full cleaning pipeline. Toggle steps as needed."""
    if remove_html:
        text = remove_html_tags(text)
    if remove_urls_flag:
        text = remove_urls(text)
    if lowercase:
        text = to_lowercase(text)
    if remove_punct:
        text = remove_punctuation(text)
    if remove_nums:
        text = remove_numbers(text)
    return remove_extra_whitespace(text)


if __name__ == "__main__":
    sample = "  Hello, World! Visit https://example.com for <b>more</b> info.  "
    print(clean(sample))
