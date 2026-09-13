"""Check multilabel rollups and report counts without loading a model."""

import unittest

import numpy as np

from review_aspects.matching import assign_candidates, build_result
from review_aspects.reporting import build_report
from review_aspects.taxonomy import ASPECT_PARENTS, parent_categories


class FoodRollupTests(unittest.TestCase):
    def test_children_and_standalone_labels_roll_up_once(self):
        self.assertEqual(
            parent_categories(
                [
                    "Food / Taste / seasoning",
                    "Food / Texture / doneness",
                    "Price / value",
                ]
            ),
            ["Food", "Price / value"],
        )

    def test_every_parent_deduplicates_all_its_children(self):
        for parent in set(ASPECT_PARENTS.values()):
            children = [
                child for child, value in ASPECT_PARENTS.items() if value == parent
            ]
            self.assertEqual(parent_categories(children + children), [parent])

    def test_threshold_and_report_deduplication(self):
        segments = [
            {"review_id": 1, "sentence_id": 1, "text": "First sentence."},
            {"review_id": 1, "sentence_id": 2, "text": "Second sentence."},
            {"review_id": 2, "sentence_id": 1, "text": "Unmatched sentence."},
        ]
        scores = {
            "Food / Taste / seasoning": np.array([0.8, 0.45, 0.44999]),
            "Food / Texture / doneness": np.array([0.7, 0.1, 0.2]),
            "Price / value": np.array([0.6, 0.1, 0.1]),
        }
        assign_candidates(segments, scores, 0.45)
        self.assertEqual(segments[0]["candidate_categories"], ["Food", "Price / value"])
        self.assertEqual(segments[1]["candidate_categories"], ["Food"])
        self.assertEqual(segments[2]["candidate_categories"], [])
        self.assertEqual(segments[2]["status"], "unclassified")
        result = build_result(segments, {aspect: [] for aspect in scores}, [], [], 0.45)
        report = build_report(result)
        self.assertIn("| Food | 2 | 1 | 50.0% |", report)
        self.assertIn("Unclassified sentences: 1 of 3 (33.3%).", report)
        self.assertIn("Reviews with no matches: 1.", report)
        self.assertNotIn("Food / Taste / seasoning", report)
        self.assertNotIn("Food / Texture / doneness", report)
        self.assertNotIn("Detailed aspects", report)
        self.assertEqual(
            report.count("First sentence."), 2
        )  # Once for Food and once for Price.


if __name__ == "__main__":
    unittest.main()
