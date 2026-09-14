# Review aspect matching

Compare restaurant review sentences with labeled examples and report eight broad
customer-experience topics. Start with [the CSV results](results/aspect_results.csv).

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -X utf8 run.py
```

The model may download on the first run. Running again replaces the results.
File paths and the matching cutoff are fixed at the top of `run.py`.
It reads `data/reviews.csv` and writes `results/aspect_results.csv`; no arguments are needed.

## Project layout

| Location | What belongs here |
|---|---|
| `run.py` | Short entry point that runs the analysis steps. |
| `review_aspects/` | Python modules: loading, matching, taxonomy, and CSV export. |
| `data/` | Source reviews and reference examples. |
| [results/aspect_results.csv](results/aspect_results.csv) | One sentence per row, with a 1/0 column for each parent category. |
| `tests/` | Checks for thresholds and deduplicated parent counts. |
| `config/requirements-lock.txt` | Snapshot of installed dependency versions. |

`requirements.txt` and `pyproject.toml` contain installation dependencies and
project metadata. Only `requirements.txt` is needed to install dependencies.

## Checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

The CSV includes `review_id`, `sentence_id`, `text`, `status`, and eight parent
category columns. `1` means matched; `0` means not matched. Unclassified sentences
have zeros for every category. These are sentence rows: summing a category gives
a sentence count, not a distinct-review count. Each run exports only CSV.
