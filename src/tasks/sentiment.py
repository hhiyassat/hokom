"""
sentiment.py — Sentiment analysis using HuggingFace pipeline
"""

from typing import Union, List


def analyze(texts: Union[str, List[str]], model: str = "distilbert-base-uncased-finetuned-sst-2-english") -> list:
    """
    Returns a list of {'label': 'POSITIVE'/'NEGATIVE', 'score': float} dicts.

    Args:
        texts: A single string or list of strings.
        model:  HuggingFace model name. Default is a fast SST-2 model.

    Requires: pip install transformers torch
    """
    from transformers import pipeline

    classifier = pipeline("sentiment-analysis", model=model)
    if isinstance(texts, str):
        texts = [texts]
    return classifier(texts)


if __name__ == "__main__":
    samples = [
        "I love this product, it's amazing!",
        "This is the worst experience I've ever had.",
    ]
    results = analyze(samples)
    for text, result in zip(samples, results):
        print(f"[{result['label']} {result['score']:.2f}] {text}")
