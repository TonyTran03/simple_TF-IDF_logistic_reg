# Semantic Review Analytics

Sentence-level customer feedback analysis using Semantic Textual Similarity
(STS). A pretrained Sentence Transformer embeds review sentences and confirmed
reference examples. Cosine similarity suggests one or more business aspects.
No model is trained or fine-tuned by this script. TF-IDF is not used.

## Retail analytics case

The business question is which customer experiences warrant investigation:
product quality, service speed, price/value, and staff behavior. The current
CSV contains restaurant reviews, so food is the product-quality example;
it is not evidence about a different retailer. Additional categories capture
facilities and business operations. The existing labels and quotes are retained
for review rather than silently relabeled for a new dataset.

This project implements aspect matching only. To complete the case study:

1. Confirm diverse real reference sentences for each aspect, including positive,
   negative, and neutral wording. The 14 proposed excerpts are only a starter set.
2. Manually label separate reviews for validation and a held-out test set.
   Keep duplicates and sentences from the same review in the same partition.
   Tune similarity cutoffs on validation data and report per-aspect precision,
   recall, and F1 on the untouched test set.
3. Add and evaluate sentence/aspect sentiment separately. Similarity scores
   measure related meaning, not satisfaction, probability, or complaint severity.
4. Inspect unmatched sentences and cluster their embeddings to investigate
   new themes. Predefined aspect matching alone does not discover hidden topics.
5. Combine verified aspect and sentiment counts with review examples to propose
   actions. Compare dates/platforms only if that metadata is available; review
   mentions alone cannot establish why loyalty declined or prove causation.

TF-IDF plus a classifier could be an optional evaluated baseline, but neither
TF-IDF nor BERTopic is required for this STS pipeline. Sentence Transformers
still uses scikit-learn internally; that dependency does not mean this project
is using TF-IDF.

## Setup and run (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_aspects.py
```

Open `semantic-review-analytics.code-workspace` in VS Code to use the project
name and environment. Use `python -m pip` through the environment as shown.

Before running, review `aspect_references_review.md` and edit
`aspect_references.json`: correct the `aspects` labels, then set `approved` to
`true` for examples you have confirmed. Multiple labels are allowed. The script
stops if none are approved and validates exact quote/row/sentence provenance.
Review IDs are one-based CSV data-row positions. Approved reference reviews
and exact duplicate reference sentences are excluded from prediction counts.
This exclusion is not a substitute for a separately labeled evaluation set.

The script reads the `review` column of `reviews.csv` and writes
`aspect_results.json` (all candidate labels/scores) and `aspect_results.md`
(counts and highest-scoring examples). Counts can overlap across categories.
Only categories with approved examples are scored. The initial cutoff of 0.45
is uncalibrated; adjust using `--threshold` after validation. English-focused
embeddings and simple punctuation splitting can miss other languages,
abbreviations, and context spanning sentences.

## Files

- `run_aspects.py`: current STS analysis entry point.
- `reviews.csv`: original source data, preserved.
- `aspect_references.json`: real excerpts and proposed/confirmed aspect labels.
- `aspect_references_review.md`: readable reference-label review table.
- `requirements.txt` / `pyproject.toml`: direct dependencies and project metadata.
- `requirements-lock.txt`: installed dependency versions after cleanup.
- `legacy_experiments.zip`: previous TF-IDF/BERTopic scripts, dependency list,
  old documentation and synthetic-reference outputs, archived for recovery.

Method reference: [Sentence Transformers STS documentation](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html).
