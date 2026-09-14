from pathlib import Path

from review_aspects.data import (
    exclude_reference_sentences,
    load_references,
    load_sentences,
)
from review_aspects.matching import assign_candidates, build_result, score_aspects
from review_aspects.reporting import write_results

BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "data" / "reviews.csv"
OUTPUT_CSV = BASE_DIR / "results" / "aspect_results.csv"
REFERENCES = BASE_DIR / "data" / "aspect_references.json"
THRESHOLD = 0.45


def main():
    segments = load_sentences(INPUT_CSV)
    references, aspects = load_references(REFERENCES)
    segments, excluded_reviews = exclude_reference_sentences(segments, references)

    scores = score_aspects(segments, aspects)
    segments = assign_candidates(segments, scores, THRESHOLD)
    result = build_result(segments, aspects, references, excluded_reviews, THRESHOLD)
    write_results(result, OUTPUT_CSV)


if __name__ == "__main__":
    main()
