import csv


def write_csv(result, output_path):
    parents = result.get("aspect_parents", {})
    categories = list(
        dict.fromkeys(
            parents.get(aspect, aspect) for aspect in result["aspect_examples"]
        )
    )
    columns = ["review_id", "sentence_id", "text", "status", *categories]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for segment in result["sentences"]:
            row = {column: segment[column] for column in columns[:4]}
            row.update(
                {
                    category: int(category in segment["candidate_categories"])
                    for category in categories
                }
            )
            writer.writerow(row)


def write_results(result, output_path):
    write_csv(result, output_path)
