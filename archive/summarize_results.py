import json
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).parent


def load_results(filename: str) -> Dict:
    path = BASE_DIR / filename
    return json.loads(path.read_text())


def flatten_results(data: Dict) -> List[Dict]:
    model = data["model"]
    strategies = data["strategies"]
    # Build a readable name for each strategy
    strat_meta = {
        key: {
            "system_prompt": value.get("system_prompt", "").strip(),
            "description": value.get("description", ""),
        }
        for key, value in strategies.items()
    }
    rows: List[Dict] = []
    for pid, pinfo in data["tests"].items():
        prompt = pinfo.get("prompt", "").strip()
        for strat_key, sinfo in pinfo.get("strategies", {}).items():
            row = {
                "problem_id": pid,
                "model": model,
                "strategy": strat_key,
                "strategy_description": strat_meta.get(strat_key, {}).get(
                    "description", ""
                ),
                "system_prompt": strat_meta.get(strat_key, {}).get("system_prompt", ""),
                "pass_rate": sinfo.get("pass_rate"),
                "passed": sinfo.get("passed"),
                "error": sinfo.get("error"),
                "raw_name": sinfo.get("name"),
                "raw_code": sinfo.get("code"),
                "prompt": prompt,
            }
            rows.append(row)
    return rows


def summarize_group(rows: List[Dict]) -> Dict[Tuple[str, str], Dict[str, Dict]]:
    summary: Dict[Tuple[str, str], Dict[str, Dict]] = {}
    for row in rows:
        key = (row["problem_id"], row["strategy"])
        per_model = summary.setdefault(key, {})
        per_model[row["model"]] = {
            "pass_rate": row["pass_rate"],
            "passed": row["passed"],
            "error": row["error"],
            "system_prompt": row["system_prompt"],
            "strategy_description": row["strategy_description"],
            "prompt": row["prompt"],
        }
    return summary


def merge_files(filenames: List[str]) -> List[Dict]:
    merged = []
    for fname in filenames:
        merged.extend(flatten_results(load_results(fname)))
    return merged


def compute_titles(rows: List[Dict]) -> Dict[str, str]:
    titles: Dict[str, str] = {}
    for row in rows:
        pid = row["problem_id"]
        if pid in titles:
            continue
        prompt = row["prompt"].splitlines()
        first_non_empty = ""
        for line in prompt:
            stripped = line.strip()
            if stripped:
                first_non_empty = stripped
                break
        titles[pid] = first_non_empty[:100]
    return titles


def print_plain_summary(grouped: Dict[Tuple[str, str], Dict[str, Dict]]) -> None:
    for (problem_id, strategy), per_model in sorted(grouped.items()):
        print(f"{problem_id} :: {strategy}")
        for model, info in per_model.items():
            print(
                f"  {model} - pass_rate={info['pass_rate']} passed={info['passed']} error={info['error']}"
            )
        print()


def print_markdown_table(
    grouped: Dict[Tuple[str, str], Dict[str, Dict]], titles: Dict[str, str]
) -> None:
    header = "| Problem | Strategy | Task Summary | Model | pass@k | Notes |"
    divider = "| --- | --- | --- | --- | --- | --- |"
    print(header)
    print(divider)
    for (problem_id, strategy), per_model in sorted(grouped.items()):
        title = titles.get(problem_id, "")
        for model, info in per_model.items():
            notes = info["error"] or ("pass" if info["passed"] else "")
            notes = notes.replace("|", "\\|")
            print(
                f"| {problem_id} | {strategy} | {title} | {model} | {info['pass_rate']} | {notes} |"
            )


def print_compact_markdown_table(
    grouped: Dict[Tuple[str, str], Dict[str, Dict]],
    titles: Dict[str, str],
    model_order: List[str],
) -> None:
    model_aliases = [model.split("/")[-1] for model in model_order]
    header = (
        "| Problem | Strategy | Task Summary | "
        + " | ".join(f"{alias} pass@k" for alias in model_aliases)
        + " | Notes |"
    )
    divider = (
        "| --- | --- | --- | " + " | ".join("---" for _ in model_order) + " | --- |"
    )
    print(header)
    print(divider)
    for (problem_id, strategy), per_model in sorted(grouped.items()):
        title = titles.get(problem_id, "")
        passcols = []
        notes_parts = []
        for idx, model in enumerate(model_order):
            info = per_model.get(model)
            if info:
                passcols.append(info["pass_rate"] or "")
                if info["error"]:
                    notes_parts.append(f"{model_aliases[idx]}: {info['error']}")
                elif info["passed"]:
                    notes_parts.append(f"{model_aliases[idx]}: pass")
            else:
                passcols.append("")
        notes = "; ".join(notes_parts).replace("|", "\\|")
        print(
            f"| {problem_id} | {strategy} | {title} | "
            + " | ".join(passcols)
            + f" | {notes} |"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Summarize LLM results JSON.")
    parser.add_argument("filenames", nargs="+", help="Result JSON filenames to load")
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Print markdown table instead of plain summary",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Use a compact markdown table with one row per problem/strategy",
    )
    args = parser.parse_args()

    rows = merge_files(args.filenames)
    grouped = summarize_group(rows)
    if args.markdown:
        titles = compute_titles(rows)
        if args.compact:
            # preserve insertion order from filenames for model columns
            model_order = []
            for row in rows:
                if row["model"] not in model_order:
                    model_order.append(row["model"])
            print_compact_markdown_table(grouped, titles, model_order)
        else:
            print_markdown_table(grouped, titles)
    else:
        print_plain_summary(grouped)
