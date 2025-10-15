# LLM Code Generation: Prompting Strategies & Agentic Workflow

**CS520 Homework 1** - Prompting, Debugging, and Innovation for Code Generation with LLMs

## Overview

This repository implements and compares different prompting strategies for LLM-based code generation, featuring a novel **test-driven agentic workflow** as the innovation component.

### Three Approaches Compared

1. **Stepwise Chain-of-Thought (SCoT)**: Breaking down problems into explicit step-by-step reasoning
2. **Self-Repair**: Generating code, testing it, and iteratively fixing errors
3. **Test-Driven Agent** (Innovation): Autonomous agent that writes tests first, then generates code to pass them

### Models Tested

- `deepseek/deepseek-chat-v3` (DeepSeek)
- `x-ai/grok-2-vision-1212` (xAI)

All accessed via [OpenRouter API](https://openrouter.ai/) with:

- ✅ Structured outputs (JSON schema validation)
- ✅ Tool/function calling
- ✅ Prompt caching (for efficiency)

## Project Structure

```
.
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
├── openrouter_client.py          # OpenRouter LLM wrapper
├── tools.py                       # Tool definitions (bash, read, write, edit)
├── agent.py                       # Main agentic loop
├── strategies/
│   ├── stepwise_cot.py           # Stepwise CoT implementation
│   ├── self_repair.py            # Self-repair implementation
│   └── test_driven_agent.py      # Test-driven agent (innovation)
├── evaluate.py                    # Evaluation script for all strategies
├── problems/
│   ├── swe_bench_problem.md      # SWE-Bench problem (sklearn)
│   └── humaneval_problems.py     # 9 HumanEval problems
├── results/                       # Evaluation results (generated)
└── problem_10297_context.md      # Example problem (sklearn patch)
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

Get your API key from: https://openrouter.ai/keys

### 3. Verify Setup

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', os.getenv('OPENROUTER_API_KEY')[:20] + '...')"
```

## Usage

### Quick Start: Run Test-Driven Agent

```bash
python agent.py --problem problems/swe_bench_problem.md --model deepseek/deepseek-chat-v3
```

### Compare All Strategies

```bash
python evaluate.py --output results/comparison.json
```

This will:

1. Run all 3 strategies across all 3 models (9 combinations)
2. Test on 10 problems (1 SWE-Bench + 9 HumanEval)
3. Measure pass@k, execution time, and token usage
4. Generate comparison tables and visualizations

### Individual Strategy Testing

```bash
# Stepwise CoT
python strategies/stepwise_cot.py --problem problems/swe_bench_problem.md --model deepseek/deepseek-chat-v3

# Self-Repair
python strategies/self_repair.py --problem problems/humaneval_problems.py --problem-id HumanEval/0 --model x-ai/grok-2-vision-1212

# Test-Driven Agent (Innovation)
python strategies/test_driven_agent.py --problem problems/swe_bench_problem.md --model anthropic/claude-3.5-sonnet
```

## Problems Selected

### 1. SWE-Bench Problem (Real-World)

**Problem**: sklearn `RidgeClassifierCV` missing `store_cv_values` parameter
**File**: `problems/swe_bench_problem.md`
**Difficulty**: Requires understanding inheritance, docstring formatting, and test writing
**Source**: https://github.com/scikit-learn/scikit-learn/issues/10297

### 2. HumanEval Problems (9 selected)

**File**: `problems/humaneval_problems.py`

| ID            | Problem               | Difficulty | Skills Tested                         |
| ------------- | --------------------- | ---------- | ------------------------------------- |
| HumanEval/0   | has_close_elements    | Easy       | List comparison, tolerance checking   |
| HumanEval/1   | separate_paren_groups | Medium     | String parsing, stack manipulation    |
| HumanEval/10  | make_palindrome       | Medium     | String manipulation, algorithm design |
| HumanEval/20  | find_closest_elements | Medium     | Sorting, edge cases                   |
| HumanEval/31  | is_prime              | Easy       | Mathematical reasoning                |
| HumanEval/50  | encode_shift          | Medium     | String encoding/decoding              |
| HumanEval/75  | is_multiply_prime     | Hard       | Factorization, composability          |
| HumanEval/100 | make_a_pile           | Easy       | Arithmetic sequences                  |
| HumanEval/125 | split_words           | Medium     | String parsing, regex alternative     |

**Total**: 10 problems covering diverse programming tasks

## Innovation: Test-Driven Agentic Workflow

### Key Idea

Traditional approaches generate code and then test it. Our **test-driven agent**:

1. **Analyzes the problem** to understand requirements
2. **Writes comprehensive tests first** (TDD approach)
3. **Generates minimal code** to pass each test
4. **Iteratively refines** until all tests pass
5. **Uses tools autonomously** (bash, file operations)

### Advantages

- ✅ Better test coverage (tests written before code)
- ✅ Prevents over-engineering (minimal code to pass tests)
- ✅ Autonomous error recovery (agent fixes its own mistakes)
- ✅ Explicit validation at each step

### Agent Loop Architecture

```
┌─────────────────────────────────────────┐
│  Problem Description                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  LLM: Analyze & Plan Tests              │
│  (with prompt caching)                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Tool: Write Test File                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  LLM: Generate Code (tool calling)      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Tool: Write Code File                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Tool: Run Tests (bash)                 │
└──────────────┬──────────────────────────┘
               │
               ▼
        ┌──────┴──────┐
        │  All Pass?  │
        └──────┬──────┘
               │
        ┌──────┴──────┐
        │             │
       Yes            No
        │             │
        ▼             ▼
     Success   ┌──────────────┐
               │ LLM: Debug   │
               │ & Fix Code   │
               └──────┬───────┘
                      │
                      └──────┐
                             │
                    (max 5 iterations)
```

## OpenRouter Features Used

### 1. Structured Outputs

Forces LLM to return valid JSON matching our tool schemas:

```python
response = client.chat.completions.create(
    model="deepseek/deepseek-chat-v3",
    messages=[...],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "tool_calls",
            "schema": {...}
        }
    }
)
```

### 2. Tool Calling

OpenAI-compatible function calling:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute bash command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"}
                }
            }
        }
    }
]
```

### 3. Prompt Caching

Reuses prompt prefixes to reduce costs:

```python
# OpenRouter automatically caches repeated prompt prefixes
# Saves tokens when making multiple requests with same system prompt
```

## Evaluation Metrics

| Metric             | Description                                    |
| ------------------ | ---------------------------------------------- |
| **pass@k**         | Proportion of test cases passed                |
| **Execution Time** | Total time to generate solution                |
| **Token Usage**    | Total tokens (prompt + completion)             |
| **Tool Calls**     | Number of tool invocations                     |
| **Iterations**     | Number of fix attempts (for self-repair/agent) |

## Results Summary

Results will be generated in `results/` directory after running evaluation:

- `comparison.json`: Raw data for all runs
- `summary.csv`: Aggregate statistics per strategy/model
- `plots/`: Visualizations comparing approaches

## Key Findings

_(To be filled after running experiments)_

1. **Best Model for Code Generation**: TBD
2. **Most Efficient Strategy**: TBD
3. **Test-Driven Agent Advantages**: TBD

## Repository Contents for Submission

✅ Prompts and workflow scripts
✅ Generated code
✅ Test cases (1 SWE-Bench + 9 HumanEval)
✅ Evaluation scripts and results

## References

- OpenRouter Docs: https://openrouter.ai/docs
- Structured Outputs: https://openrouter.ai/docs/features/structured-outputs
- Tool Calling: https://openrouter.ai/docs/features/tool-calling
- Prompt Caching: https://openrouter.ai/docs/features/prompt-caching
- HumanEval Dataset: https://github.com/openai/human-eval
- SWE-Bench: https://github.com/SWE-bench/SWE-bench

## License

MIT (for educational purposes)
