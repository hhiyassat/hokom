"""
tokenizer.py — Tokenization helpers (word, sentence, subword via HuggingFace)
"""

from typing import List


def word_tokenize(text: str) -> List[str]:
    """Simple whitespace tokenizer. Swap for NLTK/spaCy if needed."""
    return text.split()


def sentence_tokenize(text: str) -> List[str]:
    """Split on period/newline. Replace with NLTK sent_tokenize for production."""
    import re
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if s]


def hf_tokenize(text: str, model_name: str = "bert-base-uncased") -> dict:
    """
    Tokenize with a HuggingFace tokenizer.
    Requires: pip install transformers
    """
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return tokenizer(text, return_tensors="pt", truncation=True, padding=True)


if __name__ == "__main__":
    text = "Natural language processing is fun. Let's tokenize this text!"
    print("Words:", word_tokenize(text))
    print("Sentences:", sentence_tokenize(text))
