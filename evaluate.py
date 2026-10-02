import json
from datetime import datetime, timezone
from time import perf_counter

from answer import answer_question
from ingest import PROJECT_DIR


def main():
    evaluation_dir = PROJECT_DIR / "evaluation"
    cases = json.loads(
        (evaluation_dir / "cases.json").read_text(encoding="utf-8")
    )

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output_path = evaluation_dir / f"results_{run_id}.json"
    results = []

    for case in cases:
        print(f"Running {case['id']}: {case['category']}...")
        started = perf_counter()

        record = {
            "id": case["id"],
            "question": case["question"],
            "expected": case["expected"],
            "required_sources": case["required_sources"],
            "correctness": "not_reviewed",
            "citation_support": "not_reviewed",
            "review_notes": "",
        }

        try:
            answer, sources = answer_question(case["question"])

            cited = {
                (source["source"], source["section"])
                for source in sources
            }

            missing = [
                source
                for source in case["required_sources"]
                if tuple(source) not in cited
            ]

            for group in case.get("acceptable_source_groups", []):
                if not any(tuple(source) in cited for source in group):
                    missing.append({
                        "at_least_one_of": group
                    })

            record.update({
                "status": "completed",
                "answer": answer,
                "cited_sources": sources,
                "missing_required_sources": missing,
                "source_coverage_pass": not missing,
            })

            if missing:
                print("  Source coverage: missing expected sections")
            else:
                print("  Source coverage: PASS")

        except Exception as error:
            # Save the error type without recording possible credentials.
            record.update({
                "status": "error",
                "error_type": type(error).__name__,
                "source_coverage_pass": False,
            })
            print(f"  Error: {type(error).__name__}")

        record["seconds"] = round(perf_counter() - started, 2)
        results.append(record)

        # Save after each case so completed results are preserved.
        output_path.write_text(
            json.dumps(
                {"run_id": run_id, "results": results},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    completed = sum(
        result["status"] == "completed" for result in results
    )
    coverage_passes = sum(
        result["source_coverage_pass"] for result in results
    )

    print(f"\nCompleted: {completed}/{len(cases)}")
    print(
        f"Expected-source coverage: "
        f"{coverage_passes}/{len(cases)}"
    )
    print("Answer correctness and citation support need manual review.")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()