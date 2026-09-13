# Review aspect matching

This project reads restaurant reviews and suggests which topics each sentence
mentions: food, staff/service, price/value, wait times, atmosphere/facilities,
and business operations.

`okay_its_not_so_simple_anymore_sorry.py` uses a pretrained Sentence Transformer to compare sentences
with labeled example quotes. It does not train a classifier or measure sentiment.

## Run it (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe okay_its_not_so_simple_anymore_sorry.py
```

The first run may download the model. Open
`semantic-review-analytics.code-workspace` in VS Code to use the project environment.

Optional settings:

```powershell
.\.venv\Scripts\python.exe okay_its_not_so_simple_anymore_sorry.py --input reviews.csv --references aspect_references.json --threshold 0.45 --output aspect_results.json
```

Running the script replaces the selected JSON output and its matching `.md` report.

## What to read

| File | Purpose |
|---|---|
| [okay_its_not_so_simple_anymore_sorry.py](okay_its_not_so_simple_anymore_sorry.py) | Small entry point: runs the analysis steps in order. |
| [review_aspects/cli.py](review_aspects/cli.py) | Command-line options and default file paths. |
| [review_aspects/data.py](review_aspects/data.py) | Read and split reviews, validate references, and exclude reference sentences. |
| [review_aspects/matching.py](review_aspects/matching.py) | Model embeddings, similarity scores, candidate labels, and result metadata. |
| [review_aspects/reporting.py](review_aspects/reporting.py) | Build the Markdown report and write output files. |
| [aspect_results.md](aspect_results.md) | Readable output: counts and strongest matching examples. |
| `aspect_results.json` | Detailed output: every analyzed sentence, score, and candidate label. |
| [aspect_references_review.md](aspect_references_review.md) | Readable table of the reference quotes and their labels. |
| `aspect_references.json` | Reference quotes used by the script; edit this to change the examples. |
| `reviews.csv` | Original input; the script reads its `review` column. |
| `requirements.txt` | Direct dependencies to install for the aspect script. |
| `requirements-lock.txt` | Snapshot of installed dependency versions; not study notes. |
| `pyproject.toml` | Project metadata and direct dependencies. |

There are no notebook (`.ipynb`) files in the current project folder.

## How the code flows

Start in `okay_its_not_so_simple_anymore_sorry.py`; its imports point to the module for each step.

1. `parse_arguments()` reads the file paths and cutoff.
2. `load_sentences()` splits reviews and keeps their review/sentence IDs.
3. `load_references()` checks the example quotes and groups them by aspect.
4. `exclude_reference_sentences()` removes reference reviews and exact duplicate quotes.
5. `score_aspects()` compares each remaining sentence with the examples.
6. `assign_candidates()` attaches every aspect whose score meets the cutoff.
7. `build_result()` and `write_results()` save the JSON and Markdown report.

For each aspect, the score is the **highest cosine similarity to any of its
reference examples**. Multiple aspects can match the same sentence.

## How to read the outputs

- `scores`: similarity to each aspect's examples, rounded to four decimal places.
- `candidate_aspects`: labels whose unrounded score meets the cutoff (default `0.45`).
- `unclassified`: no label met the cutoff; it does not mean the sentence has no topic.
- Review and sentence IDs start at 1. Review IDs are CSV data-row positions.
- Counts overlap because one sentence can match several aspects.
- Report examples are the five highest-scoring matches, not a representative sample.

Scores are **not probabilities, sentiment, or validated predictions**. The cutoff
has not been calibrated. Reference reviews are excluded to avoid self-matches,
but this is not a separate evaluation set. The model/examples focus on English,
and simple sentence splitting can miss abbreviations or context.

To change reference examples, edit `aspect_references.json` using exact quotes
and IDs from the CSV, then keep the readable reference table in sync.

## Food subcategories

Food is now a parent category with five children: taste/seasoning,
texture/doneness, temperature/freshness, portion size, and general food comments.
The general category includes dish mentions and broad food opinions; it is not
an exclusive fallback. A sentence can match several children.

`review_aspects/taxonomy.py` defines the parent mapping. `candidate_aspects` contains
specific labels; `candidate_categories` contains deduplicated parent labels plus
standalone aspects such as Wait times. The report counts Food sentences and
reviews once each, regardless of how many children match. Portions can also match
Price / value when both apply.

The expanded reference quotes use the original 14 excluded reviews. The cutoff
remains 0.45. This is example-based matching, not model training. More matches
measure coverage, not accuracy; a separately labeled evaluation set is still needed.
The report now shows matched and unclassified coverage explicitly.

After expanding to 30 reference quotes, unclassified sentences decreased from
1,030 (64.1%) to 677 (42.1%) on the same 1,607 sentences, with the same cutoff
and excluded reviews. This is a coverage comparison, not an accuracy evaluation.
A spot check still found incorrect child labels: "Sadly, the poutine was cold
and limp." matched Portion size as well as Temperature / freshness. Shared dish
wording can overwhelm the specific aspect, so child labels need manual validation
and cutoff calibration before being treated as reliable counts.

Run the rollup checks with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Expanded category map

Each parent is deduplicated across its children. Positive and negative wording
share topic labels; these are not sentiment predictions.

| Parent | Subcategories |
|---|---|
| Food | Taste / seasoning; Texture / doneness; Temperature / freshness; Portion size; General food comments |
| Staff / service | Friendliness / helpfulness; Communication; Service speed |
| Price / value | Prices / charges; Value for money |
| Wait times | Queue length / duration; Queue movement |
| Atmosphere / facilities | Cleanliness; Ambience; Seating / crowding |
| Business operations | Parking / location; Ordering / payment; Takeout / packaging; Entry rules |
| Recommendations / loyalty | Recommendation; Return intention; Reputation / discovery |
| Overall experience | General satisfaction |

The category map lives in `review_aspects/taxonomy.py`. Only labels with reference
examples are scored. Opening hours and other topics without selected examples
remain gaps; they are not silently forced into unrelated labels.

With 74 references and 23 subcategories, 454 of 1,607 sentences (28.3%) remain
unclassified, compared with 677 before this expansion. The same sentences,
14 excluded reviews, and 0.45 cutoff were used. This measures coverage only;
shared wording can still produce incorrect subcategory matches.

## Report for the paper

`aspect_results.md` displays only parent categories, including counts, percentage
of analyzed reviews mentioning each category, and example sentences. Each review
counts once per parent. Percentages use all analyzed reviews (including reviews
with no match), and can sum above 100% because categories overlap. These are
mention percentages, not average sentiment or satisfaction scores.

Subcategories remain internal matching labels, retained in `aspect_results.json`
and reference files for inspection. Report examples use the strongest child score
as their parent similarity; scores are not averaged across children.
