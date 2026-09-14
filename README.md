# Review aspect matching

Compare restaurant review sentences with labeled examples and report eight broad
customer-experience topics using STS (semantic textual similarity).

## Project layout

| Location                                                 | What belongs here                                                 |
| -------------------------------------------------------- | ----------------------------------------------------------------- |
| `run.py`                                                 | Short entry point that runs the analysis steps.                   |
| `review_aspects/`                                        | Python modules: loading, matching, taxonomy, and CSV export.      |
| `data/`                                                  | Source reviews and reference examples.                            |
| [results/aspect_results.csv](results/aspect_results.csv) | One sentence per row, with a 1/0 column for each parent category. |
| `tests/`                                                 | Checks for thresholds and deduplicated parent counts.             |
| `config/requirements-lock.txt`                           | Snapshot of installed dependency versions.                        |
