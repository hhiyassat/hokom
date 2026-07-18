"""
classifier.py — Zero-shot text classification (no training data needed)
"""

from typing import Union, List


def classify(
    texts: Union[str, List[str]],
    candidate_labels: List[str],
    model: str = "facebook/bart-large-mnli",
    multi_label: bool = False,
) -> List[dict]:
    """
    Classify texts into one of the candidate_labels without any training.

    Args:
        texts:             Single string or list of strings.
        candidate_labels:  List of category names, e.g. ["sports", "politics", "tech"].
        model:             HuggingFace zero-shot model.
        multi_label:       If True, labels are scored independently (not forced to sum to 1).

    Returns a list of dicts: {'sequence': ..., 'labels': [...], 'scores': [...]}

    Requires: pip install transformers torch
    """
    from transformers import pipeline

    clf = pipeline("zero-shot-classification", model=model)
    if isinstance(texts, str):
        texts = [texts]
    return [clf(t, candidate_labels=candidate_labels, multi_label=multi_label) for t in texts]


if __name__ == "__main__":
    text = "NASA launched a new mission to explore Mars."
    labels = ["space", "politics", "sports", "technology"]
    result = classify(text, labels)[0]
    print(f"Top label: {result['labels'][0]} ({result['scores'][0]:.2f})")
