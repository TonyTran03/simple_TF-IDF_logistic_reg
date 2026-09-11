"""Semantic Review Analytics: match customer sentences to confirmed aspects.

These are similarity-based suggestions, not validated labels or sentiment scores.
"""
import argparse
import csv
import json
import re
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


def split_sentences(text):
    # Lightweight boundary detection; abbreviations and missing punctuation
    # can produce imperfect segments. Keep the text intact for inspection.
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|[\r\n]+', text) if s.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("reviews.csv"))
    parser.add_argument("--threshold", type=float, default=0.45,
                        help="Uncalibrated cosine similarity cutoff; default: 0.45")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("aspect_results.json"))
    parser.add_argument("--references", type=Path, default=Path(__file__).with_name("aspect_references.json"))
    args = parser.parse_args()
    if not 0 <= args.threshold <= 1:
        parser.error("--threshold must be between 0 and 1")
    segments = []
    with args.input.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if "review" not in (reader.fieldnames or []):
            parser.error("Input must have a 'review' column")
        for review_id, row in enumerate(reader, start=1):
            for sentence_id, sentence in enumerate(split_sentences(row.get("review") or ""), start=1):
                segments.append(dict(review_id=review_id, sentence_id=sentence_id, text=sentence))
    if not segments:
        parser.error("No review text found")

    references = json.loads(args.references.read_text(encoding="utf-8"))
    lookup = {(s["review_id"], s["sentence_id"]): s["text"] for s in segments}
    aspects = {}
    approved = []
    for ref in references:
        if ref.get("approved") is not True:
            continue
        key = (ref["review_id"], ref["sentence_id"])
        if lookup.get(key) != ref["text"]:
            parser.error(f"Reference {key} does not match the input CSV; recheck its source")
        if not ref.get("aspects") or not all(isinstance(a, str) and a.strip() for a in ref["aspects"]):
            parser.error(f"Reference {key} needs aspect labels")
        approved.append(ref)
        for aspect in ref["aspects"]:
            aspects.setdefault(aspect, []).append(ref["text"])
    if not approved:
        parser.error("No approved references. Review aspect_references.json and set approved to true for confirmed labels.")
    # Hold out entire reference reviews and exact duplicate reference sentences.
    # This prevents counting references matching themselves as predictions.
    reference_reviews = {r["review_id"] for r in approved}
    reference_texts = {r["text"].strip().casefold() for r in approved}
    segments = [s for s in segments if s["review_id"] not in reference_reviews
                and s["text"].strip().casefold() not in reference_texts]
    if not segments:
        parser.error("No sentences remain outside the reference reviews")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    anchors = [text for examples in aspects.values() for text in examples]
    vectors = model.encode([s["text"] for s in segments], normalize_embeddings=True)
    anchor_vectors = model.encode(anchors, normalize_embeddings=True)
    similarities = vectors @ anchor_vectors.T
    offset = 0
    scores = {}
    for aspect, examples in aspects.items():
        scores[aspect] = np.max(similarities[:, offset:offset + len(examples)], axis=1)
        offset += len(examples)
    for i, segment in enumerate(segments):
        segment["scores"] = {aspect: round(float(values[i]), 4) for aspect, values in scores.items()}
        segment["candidate_aspects"] = [aspect for aspect, values in scores.items() if values[i] >= args.threshold]
        segment["status"] = "candidate matches" if segment["candidate_aspects"] else "unclassified"

    result = dict(model="sentence-transformers/all-MiniLM-L6-v2", threshold=args.threshold,
                  note="Unvalidated similarity suggestions; scores are not probabilities. Multiple aspects may match. English-focused anchors.",
                  aspect_examples=aspects, reference_records=approved, excluded_reference_reviews=sorted(reference_reviews), sentences=segments)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = ["# Semantic Review Analytics: candidate aspects", "", result["note"], "",
              f"Analyzed {len(segments)} sentences. Threshold: {args.threshold}. Counts overlap across aspects.", "",
              "| Aspect | Matching sentences | Distinct reviews |", "|---|---:|---:|"]
    for aspect in aspects:
        matches = [s for s in segments if aspect in s["candidate_aspects"]]
        count = len(matches)
        reviews = len({s["review_id"] for s in matches})
        print(f"{aspect}: {count} candidate sentences across {reviews} reviews")
        report.append(f"| {aspect} | {count} | {reviews} |")
    report.extend(["", "Examples below are highest-scoring matches, not representative samples."])
    for aspect in aspects:
        report.extend(["", f"## {aspect}", ""])
        matches = sorted((s for s in segments if aspect in s["candidate_aspects"]),
                         key=lambda s: s["scores"][aspect], reverse=True)
        if not matches:
            report.append("No sentences passed the cutoff; this does not prove the aspect is absent.")
        for s in matches[:5]:
            report.append(f'- Review {s["review_id"]}, sentence {s["sentence_id"]} (similarity {s["scores"][aspect]:.3f}): ' + s["text"])
    args.output.with_suffix(".md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Full sentence scores: {args.output}")


if __name__ == "__main__":
    main()
