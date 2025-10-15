"""
Chain-of-Thought (CoT) prompting strategy.

Simple CoT prompting asks the model to "think step by step" before generating the solution.
This is the basic form of CoT without explicit step breakdowns.

Reference:
- Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", NeurIPS 2022
"""

import sys
import os
import time
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openrouter_client import OpenRouterClient


def cot_prompt(problem_description: str) -> str:
    """
    Generate a Chain-of-Thought prompt.

    Standard CoT just adds "Let's think step by step" to encourage reasoning.
    """
    return f"""Solve the following programming problem.

Problem:
{problem_description}

Let's think step by step to solve this problem. After reasoning through the solution, provide your final code and test cases.

Provide your solution in this format:

```python
# Your implementation here
```

Test cases:
```python
# Your test cases here
```"""


def run_cot(
    problem: str,
    model: str = "deepseek/deepseek-chat-v3",
    temperature: float = 0.7,
    verbose: bool = True
) -> dict:
    """
    Run Chain-of-Thought strategy on a problem.

    Args:
        problem: Problem description
        model: Model to use
        temperature: Sampling temperature
        verbose: Print progress

    Returns:
        Dict with success, code, tests, reasoning, tokens, time
    """
    client = OpenRouterClient()

    if verbose:
        print(f"\n{'='*60}")
        print(f"Running Chain-of-Thought with {model}")
        print(f"{'='*60}\n")

    start_time = time.time()

    # Generate CoT prompt
    prompt = cot_prompt(problem)

    # Get LLM response
    try:
        response = client.chat_completion(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert programmer who reasons carefully about problems before coding."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=4000
        )

        content = response["choices"][0]["message"]["content"]
        usage = client.get_usage(response)
        elapsed = time.time() - start_time

        if verbose:
            print("LLM Response:")
            print(content)
            print(f"\n{'='*60}")
            print(f"Time: {elapsed:.2f}s | Tokens: {usage['total_tokens']}")
            print(f"{'='*60}\n")

        # Extract code and tests
        code = extract_code_block(content, 0)  # First code block
        tests = extract_code_block(content, 1)  # Second code block

        return {
            "success": bool(code),
            "code": code,
            "tests": tests,
            "reasoning": content,
            "tokens": usage["total_tokens"],
            "time": elapsed,
            "model": model,
            "strategy": "Chain-of-Thought"
        }

    except Exception as e:
        if verbose:
            print(f"Error: {e}")

        return {
            "success": False,
            "error": str(e),
            "tokens": 0,
            "time": time.time() - start_time,
            "model": model,
            "strategy": "Chain-of-Thought"
        }


def extract_code_block(text: str, index: int = 0) -> str:
    """
    Extract code from markdown code blocks by index.

    Args:
        text: Full response text
        index: Which code block to extract (0-indexed)

    Returns:
        Extracted code or empty string
    """
    import re

    # Find all Python code blocks
    pattern = r'```python\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)

    if not matches:
        # Try without language specifier
        pattern = r'```\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

    if matches and index < len(matches):
        return matches[index].strip()

    return ""


def main():
    """CLI for CoT strategy."""
    import argparse

    parser = argparse.ArgumentParser(description="Run Chain-of-Thought strategy")
    parser.add_argument("--problem", type=str, required=True, help="Problem description file")
    parser.add_argument("--model", type=str, default="deepseek/deepseek-chat-v3", help="Model to use")
    parser.add_argument("--output-dir", type=str, default="output", help="Directory for generated files")
    parser.add_argument("--result-file", type=str, help="JSON file for results")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode")

    args = parser.parse_args()

    # Read problem
    with open(args.problem, 'r', encoding='utf-8') as f:
        problem = f.read()

    # Run strategy
    result = run_cot(
        problem=problem,
        model=args.model,
        verbose=not args.quiet
    )

    # Save generated code and tests
    if result["success"]:
        os.makedirs(args.output_dir, exist_ok=True)

        if result.get("code"):
            code_file = os.path.join(args.output_dir, "solution_cot.py")
            with open(code_file, 'w') as f:
                f.write(result["code"])
            print(f"✓ Saved code to: {code_file}")

        if result.get("tests"):
            test_file = os.path.join(args.output_dir, "test_cot.py")
            with open(test_file, 'w') as f:
                f.write(result["tests"])
            print(f"✓ Saved tests to: {test_file}")

    # Save results
    if args.result_file:
        with open(args.result_file, 'w') as f:
            # Don't save full reasoning to avoid huge files
            save_result = result.copy()
            if "reasoning" in save_result and len(save_result["reasoning"]) > 1000:
                save_result["reasoning"] = save_result["reasoning"][:1000] + "..."
            json.dump(save_result, f, indent=2)
        print(f"✓ Saved results to: {args.result_file}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Chain-of-Thought - {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"Model: {args.model}")
    print(f"Tokens: {result.get('tokens', 0)}")
    print(f"Time: {result.get('time', 0):.2f}s")
    print(f"{'='*60}\n")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
