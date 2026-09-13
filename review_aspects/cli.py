"""Semantic Review Analytics: match customer sentences to reference aspects.

These are similarity-based suggestions, not validated labels or sentiment scores.
"""

import argparse
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent


def parse_arguments():
    """Read file paths and the similarity cutoff from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=PROJECT_DIR / "reviews.csv")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.45,
        help="Uncalibrated cosine similarity cutoff; default: 0.45",
    )
    parser.add_argument(
        "--output", type=Path, default=PROJECT_DIR / "aspect_results.json"
    )
    parser.add_argument(
        "--references",
        type=Path,
        default=PROJECT_DIR / "aspect_references.json",
    )
    args = parser.parse_args()
    if not 0 <= args.threshold <= 1:
        parser.error("--threshold must be between 0 and 1")
    return args
