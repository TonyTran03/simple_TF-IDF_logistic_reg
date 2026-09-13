"""Read review sentences and validate and exclude reference examples."""

import csv
import json
import re


def split_sentences(text):
    """Split on sentence-ending punctuation or newlines; skip blank pieces."""
    return [
        piece.strip()
        for piece in re.split(r"(?<=[.!?])\s+|[\r\n]+", text)
        if piece.strip()
    ]


def load_sentences(input_path):
    """Split CSV reviews, keeping one-based review and sentence IDs."""
    segments = []
    with input_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if "review" not in (reader.fieldnames or []):
            raise ValueError("Input must have a 'review' column")
        for review_id, row in enumerate(reader, start=1):
            for sentence_id, sentence in enumerate(
                split_sentences(row.get("review") or ""), start=1
            ):
                segments.append(
                    {
                        "review_id": review_id,
                        "sentence_id": sentence_id,
                        "text": sentence,
                    }
                )
    if not segments:
        raise ValueError("No review text found")

    return segments


def load_references(reference_path, segments):
    """Check reference quotes against the CSV and group them by aspect."""
    references = json.loads(reference_path.read_text(encoding="utf-8"))
    lookup = {
        (segment["review_id"], segment["sentence_id"]): segment["text"]
        for segment in segments
    }
    aspects = {}
    for reference in references:
        key = (reference["review_id"], reference["sentence_id"])
        if lookup.get(key) != reference["text"]:
            raise ValueError(
                f"Reference {key} does not match the input CSV; recheck its source"
            )
        if not reference.get("aspects") or not all(
            isinstance(label, str) and label.strip() for label in reference["aspects"]
        ):
            raise ValueError(f"Reference {key} needs aspect labels")
        for aspect in reference["aspects"]:
            aspects.setdefault(aspect, []).append(reference["text"])
    if not references:
        raise ValueError(
            "No references found. Add review excerpts and aspect labels to the references JSON file."
        )
    return references, aspects


def exclude_reference_sentences(segments, references):
    """Keep reference reviews and duplicate reference quotes out of results."""
    # Hold out entire reference reviews and exact duplicate reference sentences.
    # This prevents counting references matching themselves as predictions.
    reference_reviews = {reference["review_id"] for reference in references}
    reference_texts = {reference["text"].strip().casefold() for reference in references}
    segments = [
        segment
        for segment in segments
        if segment["review_id"] not in reference_reviews
        and segment["text"].strip().casefold() not in reference_texts
    ]
    if not segments:
        raise ValueError("No sentences remain outside the reference reviews")
    return segments, sorted(reference_reviews)
