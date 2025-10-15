"""
Stepwise Chain-of-Thought (SCoT) prompting strategy.

Non-agentic approach: Prompts the LLM to think step-by-step and generate code.
The LLM explains its reasoning at each step before producing the final solution.
"""

import sys
import os
import time
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openrouter_client import OpenRouterClient


def stepwise_cot_prompt(problem_description: str) -> str:
    """
    Generate a Stepwise Chain-of-Thought prompt.

    SCoT asks the model to explicitly break down reasoning into steps.
    """
    return f"""You are tasked with solving the following programming problem.

Think through this problem step by step:

Step 1: Understand the Requirements
- What is the problem asking for?
- What are the inputs and outputs?
- What are the constraints and edge cases?

Step 2: Design the Approach
- What algorithm or strategy will you use?
- Break down the solution into smaller sub-problems

Step 3: Plan the Implementation
- What functions/classes are needed?
- What is the data flow?
- What are potential pitfalls?

Step 4: Implement the Solution
- Write clean, well-documented code
- Handle edge cases properly

Step 5: Write Test Cases
- Design tests for normal cases
- Design tests for edge cases
- Design tests for error handling

After thinking through each step, provide your final solution in the following format:

```python
# Your implementation here
```

And test cases:

```python
# Your test cases here
```

Problem:
{problem_description}

Now, work through each step systematically:"""


def run_stepwise_cot(
    problem: str,
    model: str = "deepseek/deepseek-chat-v3",
    temperature: float = 0.3,
    verbose: bool = True
) -> dict:
    """
    Run Stepwise CoT strategy on a problem.

    Returns:
        Dict with success, code, tests, reasoning, tokens, time
    """
    client = OpenRouterClient()

    if verbose:
        print(f"\n{'='*60}")
        print(f"Running Stepwise CoT with {model}")
        print(f"{'='*60}\n")

    start_time = time.time()

    # Generate the prompt
    prompt = stepwise_cot_prompt(problem)

    # Get LLM response
    try:
        response = client.chat_completion(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert programmer who solves problems through systematic step-by-step reasoning."
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

        # Extract code and tests from response
        code = extract_code_block(content, "implementation")
        tests = extract_code_block(content, "test")

        return {
            "success": bool(code),  # Success if we got code
            "code": code,
            "tests": tests,
            "reasoning": content,
            "tokens": usage["total_tokens"],
            "time": elapsed,
            "model": model,
            "strategy": "Stepwise Chain-of-Thought"
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
            "strategy": "Stepwise Chain-of-Thought"
        }


def extract_code_block(text: str, block_type: str = "implementation") -> str:
    """
    Extract code from markdown code blocks.

    Args:
        text: Full response text
        block_type: "implementation" or "test"

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

    if not matches:
        return ""

    # First block is usually implementation, later blocks are tests
    if block_type == "implementation":
        return matches[0] if matches else ""
    elif block_type == "test":
        return matches[1] if len(matches) > 1 else matches[0] if matches else ""

    return ""


def main():
    """CLI for Stepwise CoT strategy."""
    import argparse

    parser = argparse.ArgumentParser(description="Run Stepwise CoT strategy")
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
    result = run_stepwise_cot(
        problem=problem,
        model=args.model,
        verbose=not args.quiet
    )

    # Save generated code and tests
    if result["success"]:
        os.makedirs(args.output_dir, exist_ok=True)

        if result.get("code"):
            code_file = os.path.join(args.output_dir, "solution_scot.py")
            with open(code_file, 'w') as f:
                f.write(result["code"])
            print(f"✓ Saved code to: {code_file}")

        if result.get("tests"):
            test_file = os.path.join(args.output_dir, "test_scot.py")
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
    print(f"Stepwise CoT - {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"Model: {args.model}")
    print(f"Tokens: {result.get('tokens', 0)}")
    print(f"Time: {result.get('time', 0):.2f}s")
    print(f"{'='*60}\n")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
