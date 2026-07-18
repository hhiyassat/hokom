"""
main.py — Entry point: pick a task and run it.
"""

from src.preprocessing.text_cleaner import clean
from src.preprocessing.tokenizer import word_tokenize, sentence_tokenize

# Uncomment the task you want to use:
# from src.tasks.sentiment import analyze
# from src.tasks.summarizer import summarize
# from src.tasks.ner import extract_entities
# from src.tasks.classifier import classify


def main():
    text = "  Apple Inc. was founded by Steve Jobs in Cupertino, California. It's an amazing company!  "

    # --- Preprocessing ---
    cleaned = clean(text)
    print("Cleaned:", cleaned)
    print("Tokens:", word_tokenize(cleaned))
    print("Sentences:", sentence_tokenize(text.strip()))

    # --- Uncomment to run a task ---
    # print("\nSentiment:", analyze(text))
    # print("\nSummary:", summarize(text))
    # print("\nEntities:", extract_entities(text))
    # print("\nClassification:", classify(text, ["tech", "sports", "politics"]))


if __name__ == "__main__":
    main()
