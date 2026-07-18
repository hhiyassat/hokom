"""
ner.py — Named Entity Recognition using HuggingFace pipeline
"""

from typing import Union, List


def extract_entities(
    texts: Union[str, List[str]],
    model: str = "dbmdz/bert-large-cased-finetuned-conll03-english",
) -> List[List[dict]]:
    """
    Extract named entities from text.

    Returns a list (one per input) of entity dicts:
        [{'entity_group': 'PER', 'word': 'John', 'score': 0.99, 'start': 0, 'end': 4}, ...]

    Entity types (CoNLL-03): PER, ORG, LOC, MISC

    Requires: pip install transformers torch
    """
    from transformers import pipeline

    ner = pipeline("ner", model=model, aggregation_strategy="simple")
    if isinstance(texts, str):
        texts = [texts]
    return [ner(t) for t in texts]


if __name__ == "__main__":
    text = "Apple was founded by Steve Jobs in Cupertino, California."
    entities = extract_entities(text)[0]
    for ent in entities:
        print(f"[{ent['entity_group']}] {ent['word']} (score: {ent['score']:.2f})")
