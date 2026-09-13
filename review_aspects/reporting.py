"""Create the readable report and save JSON and Markdown outputs."""

import json


def build_report(result):
    """Summarize parent-category counts and their strongest matching sentences."""
    segments = result["sentences"]
    aspects = result["aspect_examples"]
    threshold = result["threshold"]
    unmatched = sum(not segment["candidate_aspects"] for segment in segments)
    total_reviews = len({segment["review_id"] for segment in segments})
    matched_reviews = len(
        {segment["review_id"] for segment in segments if segment["candidate_aspects"]}
    )
    report = [
        "# Semantic Review Analytics: candidate aspects",
        "",
        result["note"],
        "",
        f"Analyzed {len(segments)} sentences. Threshold: {threshold}. Counts overlap across aspects.",
        "",
        "## Coverage",
        "",
        f"- Matched sentences: {len(segments) - unmatched} of {len(segments)}.",
        f"- Unclassified sentences: {unmatched} of {len(segments)} ({unmatched / len(segments):.1%}).",
        f"- Reviews with at least one match: {matched_reviews} of {total_reviews}.",
        f"- Reviews with no matches: {total_reviews - matched_reviews}.",
        f"- Reference reviews excluded: {len(result['excluded_reference_reviews'])}.",
        "",
        "## Parent categories",
        "",
        "Each sentence and review counts once per category. Review percentages use all analyzed reviews as the denominator; categories overlap.",
        "",
        "| Category | Matching sentences | Distinct reviews | % of analyzed reviews |",
        "|---|---:|---:|---:|",
    ]
    parents = result.get("aspect_parents", {})
    categories = list(dict.fromkeys(parents.get(aspect, aspect) for aspect in aspects))
    for category in categories:
        matches = [
            segment
            for segment in segments
            if category in segment["candidate_categories"]
        ]
        review_count = len({segment["review_id"] for segment in matches})
        share = 100 * review_count / total_reviews if total_reviews else 0
        report.append(
            f"| {category} | {len(matches)} | {review_count} | {share:.1f}% |"
        )
        print(
            f"{category}: {len(matches)} candidate sentences across {review_count} reviews"
        )
    report.extend(
        ["", "Examples below are highest-scoring matches, not representative samples."]
    )
    for category in categories:
        report.extend(["", f"## {category}", ""])
        category_aspects = [
            aspect for aspect in aspects if parents.get(aspect, aspect) == category
        ]

        def category_score(segment, category_aspects=category_aspects):
            return max(segment["scores"][aspect] for aspect in category_aspects)

        matches = sorted(
            (
                segment
                for segment in segments
                if category in segment["candidate_categories"]
            ),
            key=category_score,
            reverse=True,
        )
        if not matches:
            report.append(
                "No sentences passed the cutoff; this does not prove the aspect is absent."
            )
        for segment in matches[:5]:
            report.append(
                f"- Review {segment['review_id']}, sentence {segment['sentence_id']} (similarity {category_score(segment):.3f}): "
                + segment["text"]
            )
    return "\n".join(report) + "\n"


def write_results(result, output_path):
    """Save detailed JSON and a readable Markdown report beside it."""
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    output_path.with_suffix(".md").write_text(build_report(result), encoding="utf-8")
    print(f"Full sentence scores: {output_path}")
