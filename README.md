# NLP Project

A modular Python NLP starter project. Pick the task that fits your needs and extend from there.

## Project Structure

```
nlp_project/
├── data/                  # Put your raw / processed data here
├── models/                # Saved model checkpoints
├── notebooks/             # Jupyter notebooks for exploration
├── src/
│   ├── preprocessing/
│   │   ├── text_cleaner.py   # Clean & normalize text
│   │   └── tokenizer.py      # Word / sentence / HF tokenization
│   ├── tasks/
│   │   ├── sentiment.py      # Sentiment analysis
│   │   ├── summarizer.py     # Text summarization
│   │   ├── ner.py            # Named entity recognition
│   │   └── classifier.py     # Zero-shot text classification
│   └── utils/
│       └── file_io.py        # Read/write txt, json, jsonl, csv
├── tests/
├── main.py                # Entry point
└── requirements.txt
```

## Setup

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Tasks

| Task | File | Model (default) |
|---|---|---|
| Sentiment analysis | `src/tasks/sentiment.py` | distilbert-base-uncased-finetuned-sst-2-english |
| Summarization | `src/tasks/summarizer.py` | facebook/bart-large-cnn |
| Named entity recognition | `src/tasks/ner.py` | dbmdz/bert-large-cased-finetuned-conll03-english |
| Zero-shot classification | `src/tasks/classifier.py` | facebook/bart-large-mnli |

All tasks use HuggingFace `transformers` pipelines — swap the `model` argument for any compatible model from [huggingface.co/models](https://huggingface.co/models).
