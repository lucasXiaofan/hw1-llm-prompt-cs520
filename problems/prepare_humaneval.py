"""
Prepare HumanEval problems for evaluation.

Selects the 9 HARDEST problems from the HumanEval dataset based on complexity
(prompt length + test length) and exports them as markdown files.
"""

import json
import os
import sys

# Add parent directory to path to import human_eval
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from human_eval.data import read_problems


# Top 9 hardest problems by complexity
SELECTED_PROBLEMS = [
    "HumanEval/129",  # minPath - Grid/matrix problem
    "HumanEval/69",   # search - Binary search variant
    "HumanEval/141",  # file_name_check - String validation
    "HumanEval/94",   # skjkasdkd - Complex list processing
    "HumanEval/153",  # Strongest_Extension - String manipulation
    "HumanEval/68",   # pluck - List processing with conditions
    "HumanEval/133",  # sum_squares - Mathematical processing
    "HumanEval/95",   # check_dict_case - Dictionary validation
    "HumanEval/126",  # is_sorted - List analysis
]


def save_problem_as_markdown(problem_id: str, problem_data: dict, output_dir: str = "problems"):
    """Save a HumanEval problem as markdown."""
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{problem_id.replace('/', '_')}.md"
    filepath = os.path.join(output_dir, filename)

    # Extract function name from prompt
    import re
    func_match = re.search(r'def (\w+)\(', problem_data['prompt'])
    func_name = func_match.group(1) if func_match else "unknown"

    content = f"""# {problem_id}: {func_name}

## Problem Description

```python
{problem_data['prompt']}```

## Test Cases

The solution must pass the following tests:

```python
{problem_data['test']}```

## Entry Point

Function to implement: `{problem_data['entry_point']}`

## Instructions

1. Implement the function according to the specification in the docstring
2. Ensure your implementation passes all test cases
3. Handle edge cases appropriately
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


def export_problems_json(output_file: str = "humaneval_hard9.json"):
    """Export selected problems as JSON for programmatic access."""
    problems = read_problems()

    selected = {
        pid: problems[pid]
        for pid in SELECTED_PROBLEMS
        if pid in problems
    }

    filepath = os.path.join("problems", output_file)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(selected, f, indent=2)

    return filepath


def main():
    print("="*60)
    print("Preparing HARDEST HumanEval problems for evaluation")
    print("="*60)
    print(f"\nSelected top 9 hardest problems (by complexity)\n")

    problems = read_problems()

    saved_files = []
    for idx, problem_id in enumerate(SELECTED_PROBLEMS, 1):
        if problem_id not in problems:
            print(f"✗ Problem {problem_id} not found in dataset")
            continue

        problem_data = problems[problem_id]

        # Show complexity
        complexity = len(problem_data['prompt']) + len(problem_data['test'])

        filepath = save_problem_as_markdown(problem_id, problem_data)
        saved_files.append(filepath)
        print(f"{idx}. OK {problem_id}: {problem_data['entry_point']} (complexity: {complexity})")

    # Export JSON version
    json_file = export_problems_json()
    print(f"\n[OK] Exported JSON: {json_file}")

    print(f"\n{'='*60}")
    print(f"[OK] Successfully prepared {len(saved_files)} HARD problems")
    print(f"{'='*60}")
    print(f"\nProblems saved in: {os.path.abspath('problems')}")
    print(f"\nUse these for your evaluation to test LLM capabilities on")
    print(f"challenging problems requiring complex reasoning.\n")


if __name__ == "__main__":
    main()
