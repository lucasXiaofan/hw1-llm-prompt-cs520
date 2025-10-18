# LLM Prompting Comparison (First 10 Return-Based Problems)

| Problem   | Gemini CoT   | Gemini Self-Planning | DeepSeek CoT | DeepSeek Self-Planning |
| --------- | ------------ | -------------------- | ------------ | ---------------------- |
| problem_0 | Fail (JSON)  | Fail (Tests)         | Fail (Tests) | Fail (Tests)           |
| problem_1 | Fail (JSON)  | Pass                 | Fail (JSON)  | Pass                   |
| problem_2 | Fail (JSON)  | Pass                 | Fail (Tests) | Fail (Tests)           |
| problem_3 | Fail (Tests) | Fail (Tests)         | Fail (JSON)  | Fail (Tests)           |
| problem_4 | Fail (JSON)  | Fail (Tests)         | Fail (Tests) | Fail (Tests)           |
| problem_5 | Fail (Parse) | Fail (Parse)         | Pass         | Pass                   |
| problem_6 | Fail (Tests) | Fail (Tests)         | Fail (Tests) | Fail (Tests)           |
| problem_7 | Fail (JSON)  | Pass                 | Pass         | Pass                   |
| problem_8 | Fail (JSON)  | Pass                 | Pass         | Pass                   |
| problem_9 | Fail (Parse) | Fail (Parse)         | Fail (Tests) | Fail (Tests)           |

- Gemini's raw Chain-of-Thought could not complete any of the ten problems due to JSON serialization errors, while its self-planning variant solved four.
- DeepSeek succeeded on three problems with CoT and four with self-planning; both strategies handled basic parsing more reliably than Gemini.

**Pass@1 Summary**

| Model & Strategy       | Pass | Total | Pass@1 |
| ---------------------- | ---- | ----- | ------ |
| Gemini CoT             | 0    | 10    | 0%     |
| Gemini Self-Planning   | 4    | 10    | 40%    |
| DeepSeek CoT           | 3    | 10    | 30%    |
| DeepSeek Self-Planning | 4    | 10    | 40%    |

**Prompts Used**

- CoT system prompt:

  ```
  You are an expert programmer. For each problem, follow this step-by-step reasoning process:

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
    "thinking": "STEP 1 - UNDERSTAND: Input is a list of integers, output is a single integer (the sum). Need to identify even numbers (divisible by 2) and add them together. Example: [1,2,3,4] … 2+4 = 6. STEP 2 - PLAN: Use a filtering approach - iterate through the list, check each number with modulo operator (n % 2 == 0), sum the filtered results. Can use generator expression with sum() for clean implementation. Time: O(n), Space: O(1). STEP 3 - EDGE CASES: Empty list … return 0 (sum of nothing). No even numbers … return 0. All even numbers … sum all. List with zero … 0 is even, include it. Negative evens … -2, -4 are even, include them. STEP 4 - IMPLEMENT: Use sum() with generator expression for clarity. The condition 'n % 2 == 0' handles all cases including negatives and zero correctly.",
    "name": "sum_evens",
    "code": "def sum_evens(numbers):\n      return sum(n for n in numbers if n % 2 == 0)"
  }

  After your reasoning, output ONLY this JSON format (no markdown fences, no extra text):
  {
    "thinking": "<your step-by-step reasoning>",
    "name": "<function_name>",
    "code": "<complete_python_function_code_only>"


  CRITICAL: The "code" field must contain ONLY the function code, no thinking or comments.
  ```

- Self-Planning system prompt:
  ```
  PLAN: Create a numbered step-by-step solution plan. Focus on algorithm, not code. Output only the plan.
  CODE: Implement the plan in Python. Output JSON: {"name": "function_name", "code": "def function_name(...):\n      ..."}
  ```

**Improved Prompt Drafts**

- CoT v2 system prompt:

  ```
  You are an expert Python programmer.
  Follow this loop for each problem:
  1. UNDERSTAND: Summarize inputs, outputs, constraints in one sentence.
  2. PLAN: Outline the algorithm, data structures, and complexity.
  3. EDGE CASES: List at least two non-trivial edge cases.
  4. IMPLEMENT: Write the final function.

  Output specification (hard requirement):
  - Respond with RFC8259-compliant JSON: {"thinking": "...", "name": "...", "code": "..."}.
  - Use only plain ASCII; escape all newlines as \n and all quotes inside strings.
  - Ensure "code" holds only the Python function definition with consistent indentation.
  - If you detect schema drift or accidental commentary, rebuild the JSON and resend.
  ```

- Self-Planning v2 system prompt:

  ```
  ROLE: Senior Python engineer.
  STAGE 1 (PLAN): Emit a numbered algorithmic plan (no code, no prose paragraphs). Cover data structures, complexity, and tricky cases.

  STAGE 2 (CODE): Return JSON {"name": "...", "code": "..."} where "code" is the final Python function. Keep ASCII only; escape newlines with \n.
  QUALITY GUARDRAILS:
  - Before sending the JSON, mentally dry-run the plan on edge inputs and confirm the code handles them.
  - If validation fails, refine the plan and regenerate the code once before responding.
  ```

**Failure Analysis & Improvements**

- Recurrent JSON parsing failures stemmed from unescaped control characters in prompts or outputs; sanitizing prompts and enforcing escaped Unicode would unblock CoT runs.
- Several failed test cases indicate incomplete algorithmic reasoning (e.g., BasE91 decode, triangle DP); adding targeted unit tests and few-shot exemplars for tricky formats should guide corrections.
- Empty or malformed JSON responses (parse errors) suggest the need for stricter output validation and automatic re-tries when the model deviates from schema.
- Self-planning helped both models reach working code more often; combining it with lightweight self-debug instructions or automatic diff-based feedback should further raise pass rates.
