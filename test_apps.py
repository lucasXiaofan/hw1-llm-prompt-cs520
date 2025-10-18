"""Test competition problems with input/output - reuses strategies from test_humaneval.py."""

import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from openai import OpenAI
from dotenv import load_dotenv

# Import strategies and prompts from test_humaneval
from test_humaneval import *
from openrouter_agent import clean_json_output

load_dotenv()


# ============================================
# HELPER FUNCTIONS FOR INPUT/OUTPUT TESTING
# ============================================

def parse_input_value(val):
    """Parse input value which may be a JSON string like '"text"' or a direct value."""
    if isinstance(val, str):
        # Handle string literals like '"text"' or "\"text\""
        if val.startswith('"') and val.endswith('"'):
            return val[1:-1]  # Remove outer quotes
        elif val.startswith("'") and val.endswith("'"):
            return val[1:-1]
        # Try to eval for other cases
        try:
            return eval(val)
        except:
            return val
    return val


def normalize_expected_output(val):
    """
    Dataset outputs are wrapped as single-item lists: [[expected_value]].
    Unwrap the outer list so comparisons use the actual return value.
    """
    if isinstance(val, list) and len(val) == 1:
        return val[0]
    return val




def run_test_case(callable_func, inputs, expected_output):
    """Run a single test case and return pass/fail status."""
    try:
        # Parse inputs
        parsed_inputs = [parse_input_value(inp) for inp in inputs]

        # Call the function with the parsed inputs
        actual_output = callable_func(*parsed_inputs)

        # Parse expected output
        normalized_expected = normalize_expected_output(expected_output)
        expected = parse_input_value(normalized_expected) if isinstance(normalized_expected, str) else normalized_expected

        # Compare outputs
        passed = actual_output == expected

        return {
            "passed": passed,
            "expected": str(expected),
            "actual": str(actual_output),
            "error": "" if passed else "Output mismatch"
        }

    except Exception as e:
        return {
            "passed": False,
            "expected": str(expected_output),
            "actual": "",
            "error": str(e)
        }


# ============================================
# TEST FUNCTION
# ============================================

def test_strategy(client, problem, strategy, problem_idx):
    """
    Test a strategy on a problem with input/output test cases.

    Args:
        client: OpenAI client
        problem: Problem dict with 'prompt', 'inputs', 'outputs'
        strategy: Strategy object with generate(client, problem) method
        problem_idx: Index of the problem (for identification)

    Returns:
        dict: {system_prompt, thinking, name, code, passed, error, test_results}
    """
    try:
        total_cases = len(problem.get('inputs', [])) if isinstance(problem, dict) else 0
        # Generate solution using strategy
        result = strategy.generate(client, problem)

        # Get the callable function/method
        callable_func = string_to_function(result['code'], result['name'])

        # Test against all test cases
        test_results = []
        all_passed = True

        for i, (input_data, expected_output) in enumerate(zip(problem['inputs'], problem['outputs'])):
            test_result = run_test_case(callable_func, input_data, expected_output)

            if not test_result['passed']:
                all_passed = False

            test_results.append({
                "test_case": i + 1,
                **test_result
            })

        return {
            **result,
            "passed": all_passed,
            "error": "" if all_passed else "Some test cases failed",
            "test_results": test_results,
            "pass_rate": f"{sum(1 for t in test_results if t['passed'])}/{total_cases or len(test_results)}"
        }

    except Exception as e:
        total_cases = len(problem.get('inputs', [])) if isinstance(problem, dict) else 0
        return {
            **(result if 'result' in locals() else {
                "system_prompt": getattr(strategy, 'system_prompt', ''),
                "thinking": '',
                "name": '',
                "code": ''
            }),
            "passed": False,
            "error": str(e),
            "test_results": [],
            "pass_rate": f"0/{total_cases}" if total_cases else "0/0"
        }


# ============================================
# RUNNER
# ============================================

def run_tests(model_name, strategies, problems_file, save_file, max_workers=None):
    """
    Run tests with multiple strategies on competition problems.

    Args:
        model_name: Model to use
        strategies: Dict of {name: strategy_object}
        problems_file: JSON file with problems (array format)
        save_file: Where to save results
        max_workers: Optional override for concurrent strategy execution
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    client.default_model = model_name

    with open(problems_file, encoding='utf-8') as f:
        problems = json.load(f)

    results = {
        "model": model_name,
        "strategies": {
            name: {
                "system_prompt": getattr(strategy, "system_prompt", ""),
                "description": getattr(strategy, "__doc__", "") or ""
            }
            for name, strategy in strategies.items()
        },
        "tests": {}
    }

    total_tasks = len(problems) * len(strategies)
    resolved_workers = max_workers if max_workers is not None else max(1, min(32, total_tasks))
    lock = Lock()

    for idx, problem in enumerate(problems):
        problem_id = f"problem_{idx}"
        print(f"\nTesting {problem_id}...")
        results["tests"][problem_id] = {
            "prompt": problem.get("prompt", ""),
            "strategies": {}
        }

    def _run_strategy(problem_idx, problem_data, strategy_name, strategy_obj):
        """Execute a single strategy against a problem; runs inside the thread pool."""
        strategy_result = test_strategy(client, problem_data, strategy_obj, problem_idx)
        return problem_idx, strategy_name, strategy_result

    with ThreadPoolExecutor(max_workers=resolved_workers) as executor:
        futures = [
            executor.submit(_run_strategy, idx, problem, name, strategy)
            for idx, problem in enumerate(problems)
            for name, strategy in strategies.items()
        ]

        for future in as_completed(futures):
            idx, name, result = future.result()
            problem_id = f"problem_{idx}"
            problem_result = {k: v for k, v in result.items() if k != "system_prompt"}
            with lock:
                if not results["strategies"][name].get("system_prompt") and result.get("system_prompt"):
                    results["strategies"][name]["system_prompt"] = result.get("system_prompt", "")
                results["tests"][problem_id]["strategies"][name] = problem_result
            status = "success" if problem_result.get("passed") else "failed"
            print(f"  {problem_id} - {name}: {status} ({problem_result.get('pass_rate', '0/0')})")

    # Calculate summary statistics
    summary = {}
    executed_total = len(results["tests"])
    for strategy_name in strategies.keys():
        total = executed_total
        fully_passed = sum(
            1
            for task in results["tests"].values()
            if strategy_name in task["strategies"] and task["strategies"][strategy_name]["passed"]
        )
        pass_rate_pct = 100 * fully_passed / total if total else 0.0
        summary[strategy_name] = {
            "total_problems": total,
            "fully_passed": fully_passed,
            "pass_rate": f"{fully_passed}/{total} ({pass_rate_pct:.1f}%)" if total else "0/0 (0.0%)"
        }

    results["summary"] = summary

    # Save
    with open(save_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print("SUMMARY:")
    for strategy_name, stats in summary.items():
        print(f"  {strategy_name}: {stats['pass_rate']}")
    print(f"{'='*60}")
    print(f"\nSaved to {save_file}")
    return results


# ============================================
# USAGE
# ============================================

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


if __name__ == "__main__":
    # 1. Initialize strategies (imported from test_humaneval)
    # cot = CoT(system_prompt=STEPWISE_COT)

    # self_planning = SelfPlanning(
    #     plan_prompt=MINIMAL_PLAN_PROMPT,
    #     code_prompt=MINIMAL_CODE_PROMPT
    # )
    
    cot = CoT(system_prompt=STEPWISE_COT)

    self_planning = SelfPlanning(
        plan_prompt=MINIMAL_PLAN_PROMPT,
        code_prompt=MINIMAL_CODE_PROMPT
    )

    # 2. Run tests on competition problems
    run_tests(
        model_name="deepseek/deepseek-chat-v3",
        strategies={
            "cot": cot,
            "self_planning": self_planning
        },
        problems_file="hard_apps_problem.json",
        save_file=f"why_deepseek_apps_results_{get_timestamp()}.json"
    )
    
    model_name_2 = 'google/gemini-2.0-flash-001'
    run_tests(
        model_name=model_name_2,
        strategies={
            "cot": cot,
            "self_planning": self_planning
        },
        problems_file="hard_apps_problem.json",
        save_file=f"why_gemini-2_0_apps_results_{get_timestamp()}.json"
    )

