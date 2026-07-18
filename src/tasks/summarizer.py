"""
summarizer.py — Text summarization using HuggingFace pipeline
"""

from typing import Union, List


def summarize(
    texts: Union[str, List[str]],
    model: str = "facebook/bart-large-cnn",
    max_length: int = 130,
    min_length: int = 30,
) -> List[str]:
    """
    Summarize one or more texts.

    Args:
        texts:      Single string or list of strings.
        model:      HuggingFace summarization model.
        max_length: Max tokens in the summary.
        min_length: Min tokens in the summary.

    Requires: pip install transformers torch
    """
    from transformers import pipeline

    summarizer = pipeline("summarization", model=model)
    if isinstance(texts, str):
        texts = [texts]
    results = summarizer(texts, max_length=max_length, min_length=min_length, do_sample=False)
    return [r["summary_text"] for r in results]


if __name__ == "__main__":
    long_text = (
        "Natural language processing (NLP) is a subfield of linguistics, computer science, "
        "and artificial intelligence concerned with the interactions between computers and human language, "
        "in particular how to program computers to process and analyze large amounts of natural language data. "
        "The goal is a computer capable of understanding the contents of documents, including the contextual "
        "nuances of the language within them."
    )
    print(summarize(long_text)[0])
