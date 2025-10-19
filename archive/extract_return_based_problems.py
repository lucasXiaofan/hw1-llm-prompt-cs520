import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

# Identify problems that at least one strategy failed and rank by failure count.
INPUT_PATH = Path("apps_results_2025-10-17_16-38-37.json")
OUTPUT_PATH = Path("true_hard_problems.json")


def load_results(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as infile:
        return json.load(infile)


def extract_hard_problems(results: Dict) -> List[Dict]:
    hard_problems: List[Dict] = []

    for problem_id, problem_data in results.get("tests", {}).items():
        strategies = problem_data.get("strategies", {})
        strategy_summaries = {}
        failed_strategies = []

        for name, details in strategies.items():
            passed = details.get("passed", False)
            strategy_summaries[name] = {
                "passed": passed,
                "pass_rate": details.get("pass_rate"),
                "error": (details.get("error") or "").strip(),
            }
            if not passed:
                failed_strategies.append(name)

        if not failed_strategies:
            continue

        hard_problems.append(
            {
                "problem_id": problem_id,
                "prompt": (problem_data.get("prompt") or "").strip(),
                "failure_count": len(failed_strategies),
                "failed_strategies": failed_strategies,
                "strategy_results": strategy_summaries,
            }
        )

    hard_problems.sort(key=lambda item: (-item["failure_count"], item["problem_id"]))
    return hard_problems


def write_hard_problems(problems: List[Dict], path: Path) -> None:
    with path.open("w", encoding="utf-8") as outfile:
        json.dump(problems, outfile, indent=2, ensure_ascii=False)

import json
from pathlib import Path
import re
def main_generate_hardproblem_json():
    true_hard_prblems_path = Path(OUTPUT_PATH)  # ensure it's a Path
    with true_hard_prblems_path.open("r") as file:
        hd = json.load(file)

    hard_problem_name = set([int(re.search(r'\d+', h['problem_id']).group()) for h in hd])
    print(hard_problem_name)
    with open(r"C:\Users\LangZheZR\Desktop\cs520\hw1-llm-prompt\competition_problems_return_10.json", "r", encoding="utf-8") as apps_file:
        apps = json.load(apps_file)
    # print(hard_problem_name)
    res = []
    print(len(apps))
    res = [apps[i] for i in hard_problem_name]
    print(len(res))
    with open("hard_problem.json", "w", encoding="utf-8") as file:
        json.dump(res, file, indent=2)

            
def main_extract_failed_problem() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    data = load_results(INPUT_PATH)
    hard_problems = extract_hard_problems(data)
    write_hard_problems(hard_problems, OUTPUT_PATH)

    print(f"Identified {len(hard_problems)} hard problems.")
    if hard_problems:
        distribution = Counter(problem["failure_count"] for problem in hard_problems)
        dist_parts = [
            f"{fail_count} failure{'s' if fail_count != 1 else ''}: {distribution[fail_count]}"
            for fail_count in sorted(distribution.keys(), reverse=True)
        ]
        print("Failure count distribution -> " + ", ".join(dist_parts))
        print(f"Wrote results to {OUTPUT_PATH}")
    else:
        print("No problems with failing strategies found.")


if __name__ == "__main__":
    # main()
    main_generate_hardproblem_json()
