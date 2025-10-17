"""Minimal HumanEval tester with CoT prompts."""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from openrouter_agent import string_to_function, clean_json_output

load_dotenv()
# ============================================
# DETAILED VERSION (Best Practice)
# ============================================

DETAILED_PLAN_PROMPT = """You are an expert programmer creating solution plans.

Your task: Analyze the problem and create a step-by-step solution plan.

Guidelines:
- Break down the problem into clear sub-problems
- Number each step (1, 2, 3, ...)
- Focus on the ALGORITHM and APPROACH, not code syntax
- Be specific about data structures and operations
- Keep steps concise but complete

Example:
Problem: Find the longest substring without repeating characters.
Plan:
1. Initialize a sliding window with two pointers (left, right)
2. Use a hash set to track characters in current window
3. Expand right pointer and add characters to set
4. If duplicate found, shrink window from left until duplicate removed
5. Track maximum window size seen
6. Return the maximum length

Now create a plan for the given problem. Output ONLY the numbered plan."""

DETAILED_CODE_PROMPT = """You are an expert programmer implementing solution plans.

Your task: Write code that follows the given plan step-by-step.

Guidelines:
- Implement each step in the plan sequentially
- Use the plan's structure to organize your code
- Handle edge cases mentioned in the plan
- Write clean, readable code with meaningful variable names
- Match the plan's logic exactly

Output format:
{
  "name": "function_name",
  "code": "def function_name(...):\\n    ..."
}

Provide ONLY valid JSON, no markdown or extra text."""


# ============================================
# MINIMAL VERSION
# ============================================

MINIMAL_PLAN_PROMPT = """Create a numbered step-by-step solution plan. Focus on algorithm, not code. Output only the plan."""

MINIMAL_CODE_PROMPT = """Implement the plan in Python. Output JSON: {"name": "function_name", "code": "def function_name(...):\\n    ..."}"""



# System prompts
STEPWISE_COT = """You are an expert programmer. For each problem, follow this step-by-step reasoning process:

STEP 1 - UNDERSTAND: Read the problem carefully
- What are the inputs and outputs?
- What do the examples show?
- What are the constraints?

STEP 2 - PLAN: Design your solution
- What algorithm or approach should you use?
- What data structures do you need?
- What's the time/space complexity?

STEP 3 - EDGE CASES: Identify special cases
- Empty inputs, single elements, duplicates
- Boundary values (0, negative, maximum)
- Invalid or unusual inputs

STEP 4 - IMPLEMENT: Write clean, correct code
- Handle all edge cases
- Use clear variable names
- Ensure logic is sound

EXAMPLE - Problem: Find the sum of all even numbers in a list
{
  "thinking": "STEP 1 - UNDERSTAND: Input is a list of integers, output is a single integer (the sum). Need to identify even numbers (divisible by 2) and add them together. Example: [1,2,3,4] → 2+4 = 6. STEP 2 - PLAN: Use a filtering approach - iterate through the list, check each number with modulo operator (n % 2 == 0), sum the filtered results. Can use generator expression with sum() for clean implementation. Time: O(n), Space: O(1). STEP 3 - EDGE CASES: Empty list → return 0 (sum of nothing). No even numbers → return 0. All even numbers → sum all. List with zero → 0 is even, include it. Negative evens → -2, -4 are even, include them. STEP 4 - IMPLEMENT: Use sum() with generator expression for clarity. The condition 'n % 2 == 0' handles all cases including negatives and zero correctly.",
  "name": "sum_evens",
  "code": "def sum_evens(numbers):\n    return sum(n for n in numbers if n % 2 == 0)"
}

After your reasoning, output ONLY this JSON format (no markdown fences, no extra text):
{
  "thinking": "<your step-by-step reasoning>",
  "name": "<function_name>",
  "code": "<complete_python_function_code_only>"


CRITICAL: The "code" field must contain ONLY the function code, no thinking or comments."""



class CoT:
    """Chain-of-Thought strategy (one LLM call)."""
    
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
    
    def generate(self, client, problem):
        """Returns: {system_prompt, thinking, name, code}"""
        response = client.chat.completions.create(
            model=client.default_model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": problem['prompt']}
            ],
            temperature=0
        )
        result = json.loads(clean_json_output(response.choices[0].message.content))
        
        return {
            "system_prompt": self.system_prompt,
            "thinking": result.get('thinking', ''),
            "name": result['name'],
            "code": result['code']
        }


class SelfPlanning:
    """Self-Planning strategy (two LLM calls)."""
    
    def __init__(self, plan_prompt, code_prompt):
        self.plan_prompt = plan_prompt
        self.code_prompt = code_prompt
    
    def generate(self, client, problem):
        """Returns: {system_prompt, thinking, name, code}"""
        # Step 1: Plan
        plan_response = client.chat.completions.create(
            model=client.default_model,
            messages=[
                {"role": "system", "content": self.plan_prompt},
                {"role": "user", "content": problem['prompt']}
            ],
            temperature=0
        )
        plan = plan_response.choices[0].message.content.strip()
        
        # Step 2: Code
        code_response = client.chat.completions.create(
            model=client.default_model,
            messages=[
                {"role": "system", "content": self.code_prompt},
                {"role": "user", "content": f"Problem:\n{problem['prompt']}\n\nPlan:\n{plan}"}
            ],
            temperature=0
        )
        code_data = json.loads(clean_json_output(code_response.choices[0].message.content))
        
        return {
            "system_prompt": f"PLAN: {self.plan_prompt}\nCODE: {self.code_prompt}",
            "thinking": plan,
            "name": code_data['name'],
            "code": code_data['code']
        }


# ============================================
# BLACKBOX TEST
# ============================================

def test_strategy(client, problem, strategy):
    """
    Blackbox test - works with any strategy object.
    
    Args:
        client: OpenAI client
        problem: Problem dict with 'prompt' and 'test'
        strategy: Any object with generate(client, problem) method
    
    Returns:
        dict: {system_prompt, thinking, name, code, passed, error}
    """
    try:
        result = strategy.generate(client, problem)
        
        # Test the code
        func = string_to_function(result['code'], result['name'])
        test = string_to_function(problem['test'], "check")
        test(func)
        
        return {
            **result,
            "passed": True,
            "error": ""
        }
    except Exception as e:
        # Need parentheses around the ternary expression
        return {
            **(result if 'result' in locals() else {
                "system_prompt": getattr(strategy, 'system_prompt', ''),
                "thinking": '',
                "name": '',
                "code": ''
            }),
            "passed": False,
            "error": str(e)
        }


# ============================================
# RUNNER
# ============================================

def run_tests(model_name, strategies, save_file):
    """
    Run tests with multiple strategies.
    
    Args:
        model_name: Model to use
        strategies: Dict of {name: strategy_object}
        save_file: Where to save results
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    client.default_model = model_name
    
    with open("humaneval_hard9.json") as f:
        problems = json.load(f)
    
    results = {"model": model_name, "tests": {}}
    
    for task_id, problem in problems.items():
        print(f"\nTesting {task_id}...")
        results["tests"][task_id] = {}
        
        for name, strategy in strategies.items():
            result = test_strategy(client, problem, strategy)
            results["tests"][task_id][name] = result
            print(f"  {name}: {'✓' if result['passed'] else '✗'}")
    
    # Save
    with open(save_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSaved to {save_file}")
    return results


# ============================================
# USAGE
# ============================================

if __name__ == "__main__":
    from datetime import datetime

# Add this function
    def get_timestamp():
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # 1. Initialize strategies
    cot = CoT(system_prompt=STEPWISE_COT)
    
    self_planning = SelfPlanning(
        plan_prompt=MINIMAL_PLAN_PROMPT,
        code_prompt=MINIMAL_CODE_PROMPT
    )
    
    # 2. Pass to test (blackbox)
    run_tests(
        model_name="deepseek/deepseek-chat-v3",
        strategies={
            "cot": cot,
            "self_planning": self_planning
        },
        save_file=f"results_{get_timestamp()}.json"
    )

# def test_problem(client, problem, prompt_type):
#     """Test single problem. Returns (passed, error, full_output_dict)."""
#     try:
#         # Call LLM
#         response = client.chat.completions.create(
#             model=client.default_model,
#             messages=[
#                 {"role": "system", "content": PROMPTS[prompt_type]},
#                 {"role": "user", "content": problem['prompt']}
#             ],
#             temperature=0
#         )

#         answer = response.choices[0].message.content
#         cleaned = clean_json_output(answer)
#         result = json.loads(cleaned)

#         # Run test
#         func = string_to_function(result['code'], result['name'])
#         test = string_to_function(problem['test'], "check")
#         test(func)

#         # Return full output including thinking, name, and code
#         output = {
#             "thinking": result.get('thinking', ''),
#             "name": result.get('name', ''),
#             "code": result.get('code', ''),
#             "raw_response": answer
#         }
#         return True, "", output
#     except Exception as e:
#         # On error, return whatever we have
#         output = {
#             "thinking": result.get('thinking', '') if 'result' in locals() else '',
#             "name": result.get('name', '') if 'result' in locals() else '',
#             "code": result.get('code', '') if 'result' in locals() else '',
#             "raw_response": answer if 'answer' in locals() else ''
#         }
#         return False, str(e), output


# def run_humaneval(model_name, prompt_type, save_file=None):
#     """
#     Run HumanEval tests.

#     Args:
#         model_name: Model to use (e.g., "deepseek/deepseek-chat-v3")
#         prompt_type: "stepwise_cot" or "cot"
#         save_file: Where to save results (optional)

#     Returns:
#         dict: Results with pass rate and details
#     """
#     # Setup
#     client = OpenAI(
#         base_url="https://openrouter.ai/api/v1",
#         api_key=os.getenv("OPENROUTER_API_KEY"),
#     )
#     client.default_model = model_name

#     # Load problems
#     with open("humaneval_hard9.json") as f:
#         problems = json.load(f)

#     # Run tests
#     results = {
#         "model": model_name,
#         "prompt_type": prompt_type,
#         "system_prompt": PROMPTS[prompt_type],
#         "tests": {}
#     }
#     passed = 0

#     for task_id, problem in problems.items():
#         print(f"\nTesting {task_id}...", end=" ")

#         ok, err, output = test_problem(client, problem, prompt_type)
#         results["tests"][task_id] = {
#             "passed": ok,
#             "error": err,
#             "thinking": output["thinking"],
#             "name": output["name"],
#             "code": output["code"],
#             "raw_response": output["raw_response"]
#         }

#         if ok:
#             passed += 1
#             print("✓")
#         else:
#             print(f"✗ {err[:50]}")

#     # Summary
#     total = len(problems)
#     results["passed"] = passed
#     results["total"] = total
#     results["pass_rate"] = f"{passed}/{total} ({100*passed/total:.1f}%)"

#     print(f"\n{'='*60}")
#     print(f"Results: {results['pass_rate']}")
#     print(f"{'='*60}")

#     # Save
#     if save_file:
#         with open(save_file, 'w') as f:
#             json.dump(results, f, indent=2)
#         print(f"Saved to {save_file}")

#     return results


# if __name__ == "__main__":
#     # Example usage
#     run_humaneval(
#         model_name="deepseek/deepseek-chat-v3",
#         prompt_type="stepwise_cot",
#         save_file="results_stepwise_improved_exec.json"
#     )
