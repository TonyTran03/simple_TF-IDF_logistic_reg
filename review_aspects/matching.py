"""Compute sentence similarities and attach candidate aspect labels."""

import numpy as np
from sentence_transformers import SentenceTransformer

from review_aspects.taxonomy import ASPECT_PARENTS, parent_categories

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def score_aspects(segments, aspects):
    """For each sentence, take its best reference similarity for each aspect."""
    model = SentenceTransformer(MODEL_NAME)
    reference_texts = [text for examples in aspects.values() for text in examples]
    sentence_vectors = model.encode(
        [segment["text"] for segment in segments], normalize_embeddings=True
    )
    reference_vectors = model.encode(reference_texts, normalize_embeddings=True)
    # Normalized vectors have length 1, so their dot product is cosine similarity.
    similarities = sentence_vectors @ reference_vectors.T
    # References were flattened in aspect order. Each slice belongs to one aspect.
    offset = 0
    scores = {}
    for aspect, examples in aspects.items():
        scores[aspect] = np.max(
            similarities[:, offset : offset + len(examples)], axis=1
        )
        offset += len(examples)
    return scores


def assign_candidates(segments, scores, threshold):
    """Attach scores and every aspect passing the cutoff to each sentence."""
    for sentence_index, segment in enumerate(segments):
        segment["scores"] = {
            aspect: round(float(values[sentence_index]), 4)
            for aspect, values in scores.items()
        }
        segment["candidate_aspects"] = [
            aspect
            for aspect, values in scores.items()
            if values[sentence_index] >= threshold
        ]
        segment["candidate_categories"] = parent_categories(
            segment["candidate_aspects"]
        )
        segment["status"] = (
            "candidate matches" if segment["candidate_aspects"] else "unclassified"
        )

    return segments


def build_result(segments, aspects, references, excluded_reviews, threshold):
    """Package the results and the references used to produce them."""
    return {
        "model": MODEL_NAME,
        "threshold": threshold,
        "note": "Unvalidated similarity suggestions; scores are not probabilities. Multiple aspects may match. English-focused anchors.",
        "aspect_examples": aspects,
        "aspect_parents": {
            label: parent
            for label, parent in ASPECT_PARENTS.items()
            if label in aspects
        },
        "reference_records": references,
        "excluded_reference_reviews": excluded_reviews,
        "sentences": segments,
    }
