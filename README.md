# LLM Code Generation: Prompting Strategies & Test-Driven Agent

**CS520 Homework 1** - Prompting, Debugging, and Innovation for Code Generation with LLMs

**Author:** XiaoFan Lu

## Overview

This repository systematically investigates how different prompting strategies affect LLM code generation performance through iterative experimentation and prompt refinement. The project implements three prompting strategies and introduces a novel **test-driven agentic framework** that autonomously writes tests and refines code through tool use.

### Three Prompting Strategies Evaluated

1. **Chain-of-Thought (CoT)**: Structured step-by-step reasoning before code generation
2. **Self-Planning**: Two-phase approach separating planning from implementation
3. **Test-Driven Agent** (Innovation): Autonomous agent that writes tests first, then generates and refines code iteratively using tool calls

### Models Tested

- `deepseek/deepseek-chat-v3` (DeepSeek V3)
- `google/gemini-2.0-flash-001` (Gemini 2.0 Flash)

All models accessed via [OpenRouter API](https://openrouter.ai/)

## Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd hw1-llm-prompt
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env and add: OPENROUTER_API_KEY=your_key_here

# 3. Run the main experiment
cd src
python test_apps.py

# 4. Or test the agent interactively
python openrouter_agent.py
```

See [How to Run This Repository](#how-to-run-this-repository) for detailed instructions.

## Project Structure

```
hw1-llm-prompt/
├── README.md                                    # This file
├── prompt improvement for llm coding.md         # Full report with methodology & analysis
├── requirements.txt                             # Python dependencies
├── .env.example                                 # API key template
├── hard_apps_problem.json                       # Test problems (APPS dataset)
│
├── src/                                         # Main source code
│   ├── LLM_strategies.py                        # All prompting strategies & implementations
│   ├── openrouter_agent.py                      # Tool-calling agent framework
│   └── test_apps.py                             # Testing harness for APPS problems
│
├── test_driven_agent/                           # Generated solutions (Part 3)
│   ├── base91.py                                # Base91 encoding solution
│   ├── max_pizza_slices.py                      # Pizza slicing DP solution
│   ├── num_times_all_blue.py                    # Bulb tracking solution
│   ├── unhappy_friends.py                       # Friend pairing solution
│   └── min_swaps_valid_grid.py                  # Grid swap solution
│
├── part_1_testing_results/                      # Baseline results
│   ├── deepseek_apps_results_2025-10-18_14-31-37.json
│   └── gemini-2_0_apps_results_2025-10-18_14-25-01.json
│
├── part_2_testing_results/                      # Improved prompts results
│   ├── deepseek_apps_results_2025-10-18_10-02-38.json
│   └── gemini-2_0_apps_results_2025-10-18_13-02-04.json
│
└── part_3_testing_results/                      # Test-driven agent results
    ├── t_deepseek_apps_results_2025-10-19_15-32-11.json
    └── t_gemini-2_0_apps_results_2025-10-19_15-38-52.json
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `requests>=2.31.0` - HTTP requests for OpenRouter API
- `python-dotenv>=1.0.0` - Environment variable management
- Optional: `pydantic`, `pandas`, `matplotlib`, `seaborn` for analysis

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

Get your API key from: https://openrouter.ai/keys

Your `.env` file should contain:
```
OPENROUTER_API_KEY=your_key_here
```

### 3. Verify Setup

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', os.getenv('OPENROUTER_API_KEY')[:20] + '...')"
```

## How to Navigate This Repository

### Key Files to Check

1. **[prompt improvement for llm coding.md](prompt%20improvement%20for%20llm%20coding.md)** - Complete report with:
   - Part 1: Initial prompts and baseline results
   - Part 2: Iterative debugging and prompt refinement
   - Part 3: Test-driven agent innovation and analysis

2. **[src/LLM_strategies.py](src/LLM_strategies.py)** - All prompt definitions and strategy implementations:
   - Lines 131-168: `STEPWISE_COT` prompt (improved CoT)
   - Lines 78-79: `MINIMAL_PLAN_PROMPT` and `MINIMAL_CODE_PROMPT` (Self-Planning)
   - Lines 13-29: `test_driven_agent_system_prompt` (TDD Agent)
   - Lines 194-217: `CoT` class implementation
   - Lines 220-256: `SelfPlanning` class implementation
   - Lines 258-289: `TestDrivenAgent` class implementation

3. **[src/openrouter_agent.py](src/openrouter_agent.py)** - Agentic framework with tool calling:
   - Lines 19-55: Tool definitions (bash, think)
   - Lines 58-81: Tool executor
   - Lines 83-168: Agent loop with max iterations
   - Lines 169-298: `string_to_function()` - Safe code execution

4. **[src/test_apps.py](src/test_apps.py)** - Main testing harness:
   - Lines 86-143: `test_strategy()` - Test a single strategy on a problem
   - Lines 150-247: `run_tests()` - Run all strategies with threading
   - Lines 258-315: Usage example

### Generated Code Examples

Check the **[test_driven_agent/](test_driven_agent/)** directory to see LLM-generated solutions:

- **[base91.py](test_driven_agent/base91.py)** - Base91 encoding/decoding implementation
- **[max_pizza_slices.py](test_driven_agent/max_pizza_slices.py)** - Dynamic programming solution
- **[num_times_all_blue.py](test_driven_agent/num_times_all_blue.py)** - Array tracking algorithm

Each file contains both the solution code and unit tests generated by the test-driven agent.

### Experiment Results

Results are organized by experiment phase:

**Part 1 - Baseline (Initial Prompts):**
- [part_1_testing_results/deepseek_apps_results_2025-10-18_14-31-37.json](part_1_testing_results/deepseek_apps_results_2025-10-18_14-31-37.json)
- [part_1_testing_results/gemini-2_0_apps_results_2025-10-18_14-25-01.json](part_1_testing_results/gemini-2_0_apps_results_2025-10-18_14-25-01.json)

**Part 2 - Improved (Refined Prompts):**
- [part_2_testing_results/deepseek_apps_results_2025-10-18_10-02-38.json](part_2_testing_results/deepseek_apps_results_2025-10-18_10-02-38.json)
- [part_2_testing_results/gemini-2_0_apps_results_2025-10-18_13-02-04.json](part_2_testing_results/gemini-2_0_apps_results_2025-10-18_13-02-04.json)

**Part 3 - Test-Driven Agent:**
- [part_3_testing_results/t_deepseek_apps_results_2025-10-19_15-32-11.json](part_3_testing_results/t_deepseek_apps_results_2025-10-19_15-32-11.json)
- [part_3_testing_results/t_gemini-2_0_apps_results_2025-10-19_15-38-52.json](part_3_testing_results/t_gemini-2_0_apps_results_2025-10-19_15-38-52.json)

Each JSON file contains:
```json
{
  "model": "model_name",
  "strategies": {
    "strategy_name": {
      "system_prompt": "...",
      "description": "..."
    }
  },
  "tests": {
    "problem_0": {
      "prompt": "...",
      "strategies": {
        "strategy_name": {
          "thinking": "...",
          "name": "function_name",
          "code": "...",
          "passed": true/false,
          "test_results": [...],
          "pass_rate": "3/3"
        }
      }
    }
  },
  "summary": {
    "strategy_name": {
      "total_problems": 14,
      "fully_passed": 6,
      "pass_rate": "6/14 (42.9%)"
    }
  }
}
```

## How to Run This Repository

### Option 1: Run Main Testing Script (Recommended)

Test all strategies on the APPS dataset:

```bash
cd src
python test_apps.py
```

This will:
1. Load 14 problems from `hard_apps_problem.json` (first 5 used by default)
2. Test each strategy (CoT, Self-Planning, Test-Driven Agent)
3. Run tests in parallel for efficiency
4. Save timestamped results to current directory
5. Print summary statistics

**Customize the run:**
Edit lines 258-315 in `test_apps.py` to:
- Change model: `model_name="google/gemini-2.0-flash-001"`
- Select strategies: Comment/uncomment in the `strategies` dict
- Adjust problems: Change `problems[:5]` on line 169

### Option 2: Run Individual Agent Test

Test the tool-calling agent interactively:

```bash
cd src
python openrouter_agent.py
```

This demonstrates the test-driven agent:
- Reads a problem from `hard_apps_problem.json`
- Shows iteration-by-iteration tool calls
- Prints bash commands and their outputs
- Returns final JSON solution

Watch the agent autonomously:
1. Create the `test_driven_agent/` directory
2. Write combined test + solution files
3. Execute tests with `python test_driven_agent/<problem>.py`
4. Iterate on failures until tests pass

### Option 3: Custom Strategy Testing

Create your own test script:

```python
from LLM_strategies import CoT, SelfPlanning, TestDrivenAgent, STEPWISE_COT
from test_apps import run_tests

# Define your strategies
my_strategies = {
    "cot": CoT(system_prompt=STEPWISE_COT),
    "planning": SelfPlanning(
        plan_prompt="Create a solution plan...",
        code_prompt="Implement the plan..."
    )
}

# Run tests
run_tests(
    model_name="deepseek/deepseek-chat-v3",
    strategies=my_strategies,
    problems_file="../hard_apps_problem.json",
    save_file="my_results.json",
    max_workers=4  # Parallel execution
)
```

## Dataset: APPS Benchmark

This project uses problems from the [APPS dataset](https://github.com/hendrycks/apps) (Automated Programming Progress Standard), which contains competitive programming challenges.

**Selected Problems:** 14 interview-level problems with expected return values
- All problems require implementing class methods or functions
- Includes input/output test cases for validation
- Covers diverse algorithmic challenges

**Problem Types:**
1. **Base91 Encoding** (problem_0) - String manipulation, encoding algorithms
2. **Maximum Pizza Slices** (problem_1) - Dynamic programming
3. **Bulb Tracking** (problem_2) - Array simulation
4. **Unhappy Friends** (problem_3) - Graph/pairing logic
5. **Grid Swaps** (problem_4) - Matrix operations
6. **String Mixing** (problem_5) - String processing
7. **Tree Problems** (problem_6) - Binary tree algorithms
8. **Permutation Sequences** (problem_7) - Combinatorics
9. **Consecutive Numbers** (problem_13) - Hashing, set operations
10. Additional LeetCode-style problems (problem_8-12)

Each problem includes:
- Problem statement with constraints
- Input format specification
- Expected output format
- Multiple test cases with inputs/outputs

## Innovation: Test-Driven Agentic Framework

### Overview

Unlike traditional single-shot code generation, this project implements an **autonomous test-driven development agent** that:

1. **Writes tests first** based on problem understanding
2. **Generates code to pass those tests**
3. **Executes code automatically** using tool calls
4. **Iteratively debugs failures** through error analysis
5. **Refines until success** (or max iterations reached)

### System Architecture

```
User Prompt (Problem)
       │
       ▼
┌──────────────────────────────────────────┐
│  LLM receives system prompt:             │
│  "You are a test-driven dev agent..."    │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Agent decides: Use "think" tool         │
│  Analyzes problem, extracts problem name │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Tool call: bash_command                 │
│  "mkdir -p test_driven_agent"            │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Tool call: bash_command                 │
│  Create <problem>.py with tests + code   │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Tool call: bash_command                 │
│  "python test_driven_agent/<problem>.py" │
└──────────────┬───────────────────────────┘
               │
         ┌─────┴─────┐
         │ Tests Pass?│
         └─────┬─────┘
               │
      ┌────────┴────────┐
     YES               NO
      │                 │
      ▼                 ▼
  Success!    ┌──────────────────────┐
              │ LLM analyzes error   │
              │ Edits code in file   │
              │ Reruns tests         │
              └──────┬───────────────┘
                     │
                     └──> Loop (max 15 iterations)

Final: Extract solution from file
```

### Tool Definitions

The agent has access to two tools:

**1. `bash_command`** - Execute shell commands
```python
{
    "name": "bash_command",
    "description": "Execute bash/shell commands. Can create files, list directories, etc.",
    "parameters": {
        "command": {"type": "string"}
    }
}
```

**2. `think`** - Internal reasoning
```python
{
    "name": "think",
    "description": "Continue internal reasoning before giving final answer",
    "parameters": {
        "thought": {"type": "string"}
    }
}
```

### Example Agent Trajectory

See a complete iteration log in the report: [prompt improvement for llm coding.md](prompt%20improvement%20for%20llm%20coding.md#one-example-trajectory-of-test-driven-agent) (lines 407-607)

Key observations:
- **Iteration 1**: Agent thinks about problem and extracts name "base91"
- **Iteration 2**: Creates directory with `mkdir -p test_driven_agent`
- **Iteration 3**: Writes initial code skeleton to file
- **Iteration 4**: Runs tests, sees failures
- **Iterations 5-9**: Iteratively fixes implementation bugs (syntax errors, algorithm issues)
- **Iteration 10**: Tests pass, agent provides final answer

### Critical Innovation: Autonomous Refinement

The agent doesn't just generate code once—it:
- **Observes** test failures and error messages
- **Reasons** about what went wrong
- **Acts** by editing the file and rerunning tests
- **Repeats** until convergence or timeout

This mimics how human developers debug code, but fully automated.

## Experimental Results Summary

### Part 1: Baseline Performance (Initial Prompts)

| Model       | Strategy      | Pass Rate | Notes                                      |
| ----------- | ------------- | --------- | ------------------------------------------ |
| **DeepSeek** | CoT           | 6/28 (21%) | Strong on standalone functions, weak on classes |
| **DeepSeek** | Self-Planning | 6/28 (21%) | Similar to CoT                             |
| **Gemini**   | CoT           | 3/28 (11%) | JSON formatting errors plagued results     |
| **Gemini**   | Self-Planning | 3/28 (11%) | Same JSON issues as CoT                    |

**Key Issues Identified:**
- Missing function parameters (`self` argument in class methods)
- JSON parse errors (control characters, delimiter issues)
- Logic errors in complex algorithms

### Part 2: After Prompt Refinement

| Model       | Strategy      | Pass Rate  | Improvement |
| ----------- | ------------- | ---------- | ----------- |
| **DeepSeek** | CoT           | 14/28 (50%) | **+133%**   |
| **DeepSeek** | Self-Planning | 14/28 (50%) | **+133%**   |
| **Gemini**   | CoT           | 6/28 (21%)  | **+100%**   |
| **Gemini**   | Self-Planning | 12/28 (43%) | **+300%**   |

**Overall:** 9/56 → 26/56 passing tests (**+189% improvement**)

**What Worked:**
- Explicit STEP-by-STEP reasoning structure
- Concrete examples in prompts
- Stronger JSON format enforcement
- Edge case enumeration requirements

### Part 3: Test-Driven Agent Innovation

Testing on 5 challenging problems:

| Model       | Baseline Strategy | Test-Driven Agent | Improvement |
| ----------- | ----------------- | ----------------- | ----------- |
| **DeepSeek** | CoT: 1/5 (20%)    | **2/5 (40%)**     | **+100%**   |
| **Gemini**   | Self-Plan: 2/5 (40%) | **2/5 (40%)**  | Maintained  |

**Successes:**
- ✅ **problem_1** (Pizza Slices DP): Test-driven agent caught edge cases
- ✅ **problem_2** (Bulb Tracking): All strategies succeeded

**Persistent Failures:**
- ❌ **problem_0** (Base91): Algorithm too complex, error messages unhelpful
- ❌ **problem_3** (Unhappy Friends): Logic errors in graph pairing
- ❌ **problem_4** (Grid Swaps): Index errors, optimization issues

### Key Insights

**When Test-Driven Agent Works:**
1. Problems with clear test-case specifications
2. Well-structured algorithmic challenges (DP, array operations)
3. Iterative refinement can fix off-by-one errors

**When It Fails:**
1. **Self-generated tests ≠ actual test coverage** - Critical limitation!
2. Complex algorithms requiring domain knowledge (Base91 encoding)
3. Error messages provide insufficient debugging guidance
4. 3-5x higher computational cost than single-shot strategies

**Cross-Model Observations:**
- DeepSeek benefits most from structured reasoning (CoT improvements)
- Gemini is sensitive to JSON formatting (Self-Planning with minimal template works best)
- Both models struggle with specialized algorithms regardless of strategy

## Repository Contents

This repository contains all required deliverables:

✅ **Prompts**: All prompts in [src/LLM_strategies.py](src/LLM_strategies.py)
✅ **Generated Code**: 5+ examples in [test_driven_agent/](test_driven_agent/)
✅ **Test Problems**: 14 APPS problems in [hard_apps_problem.json](hard_apps_problem.json)
✅ **Evaluation Scripts**: [src/test_apps.py](src/test_apps.py) and [src/openrouter_agent.py](src/openrouter_agent.py)
✅ **Results**: JSON files in [part_1_testing_results/](part_1_testing_results/), [part_2_testing_results/](part_2_testing_results/), [part_3_testing_results/](part_3_testing_results/)
✅ **Full Report**: [prompt improvement for llm coding.md](prompt%20improvement%20for%20llm%20coding.md)

## References

- **APPS Dataset**: [Hendrycks et al. 2021](https://github.com/hendrycks/apps) - Measuring Coding Challenge Competence With APPS
- **OpenRouter API**: https://openrouter.ai/docs
- **Tool Calling with LLMs**: OpenAI function calling format
- **Test-Driven Development**: Kent Beck, "Test-Driven Development by Example"

## Citation

If you use this work, please cite:

```
XiaoFan Lu. "Prompting Strategies for LLM Code Generation:
A Test-Driven Agentic Approach." CS520 Homework 1, 2025.
```

## License

MIT License - For educational and research purposes.
