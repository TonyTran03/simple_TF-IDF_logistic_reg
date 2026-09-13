"""Run review aspect analysis. See review_aspects/ for the implementation."""

from review_aspects.cli import parse_arguments
from review_aspects.data import (
    exclude_reference_sentences,
    load_references,
    load_sentences,
)
from review_aspects.matching import assign_candidates, build_result, score_aspects
from review_aspects.reporting import write_results


def main():
    args = parse_arguments()
    try:
        segments = load_sentences(args.input)
        references, aspects = load_references(args.references, segments)
        segments, excluded_reviews = exclude_reference_sentences(segments, references)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    scores = score_aspects(segments, aspects)
    segments = assign_candidates(segments, scores, args.threshold)
    result = build_result(
        segments, aspects, references, excluded_reviews, args.threshold
    )
    write_results(result, args.output)


if __name__ == "__main__":
    main()
