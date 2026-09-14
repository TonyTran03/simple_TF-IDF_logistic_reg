import csv
import json
import re


def split_sentences(text):
    return [
        piece.strip()
        for piece in re.split(r"(?<=[.!?])\s+|[\r\n]+", text)
        if piece.strip()
    ]


def load_sentences(input_path):
    segments = []
    with input_path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        for review_id, row in enumerate(reader, start=1):
            for sentence_id, sentence in enumerate(
                split_sentences(row["review"]), start=1
            ):
                segments.append(
                    {
                        "review_id": review_id,
                        "sentence_id": sentence_id,
                        "text": sentence,
                    }
                )

    return segments


def load_references(reference_path):
    references = json.loads(reference_path.read_text())
    aspects = {}
    for reference in references:
        for aspect in reference["aspects"]:
            aspects.setdefault(aspect, []).append(reference["text"])
    return references, aspects


def exclude_reference_sentences(segments, references):
    reference_reviews = {reference["review_id"] for reference in references}
    reference_texts = {reference["text"].strip().casefold() for reference in references}
    segments = [
        segment
        for segment in segments
        if segment["review_id"] not in reference_reviews
        and segment["text"].strip().casefold() not in reference_texts
    ]
    return segments, sorted(reference_reviews)
