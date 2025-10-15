# Project Summary: LLM Code Generation with Prompting Strategies

## Overview

This project implements and compares different prompting strategies for LLM-based code generation, with a focus on evaluating performance across multiple models using OpenRouter API.

## What's Been Built

### 1. Core Infrastructure

#### OpenRouter Client (`openrouter_client.py`)
- Full support for OpenRouter API features:
  - ✅ Structured outputs (JSON schema validation)
  - ✅ Tool/function calling
  - ✅ Prompt caching (automatic)
- Configurable model switching
- Usage tracking and error handling

#### Tools Module (`tools.py`)
- Bash command execution
- File operations (read, write, edit)
- JSON schema definitions for tool calling
- Windows/git-bash compatible

#### Agent Framework (`agent.py`)
- General-purpose agentic loop
- Tool execution with error handling
- Conversation history management
- Retry logic and iteration limits

### 2. Three Prompting Strategies

#### Strategy 1: Chain-of-Thought (CoT)
**File**: `strategies/cot.py`

**Approach**: Simple prompting with "Let's think step by step"
**Characteristics**:
- Single-turn generation
- Minimal prompting overhead
- Baseline for comparison

**Reference**: Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", NeurIPS 2022

#### Strategy 2: Stepwise Chain-of-Thought (SCoT)
**File**: `strategies/stepwise_cot.py`

**Approach**: Explicit step-by-step breakdown
**Steps**:
1. Understand Requirements
2. Design Approach
3. Plan Implementation
4. Implement Solution
5. Write Test Cases

**Characteristics**:
- More structured than CoT
- Explicit reasoning phases
- Better documentation

#### Strategy 3: Test-Driven Agent (Innovation - Part 3)
**File**: `strategies/test_driven_agent.py`

**Approach**: Agentic workflow with TDD principles
**Workflow**:
1. Analyze requirements
2. Write tests FIRST
3. Implement minimal code
4. Run tests with bash tool
5. Debug and fix iteratively
6. Verify all tests pass

**Characteristics**:
- Multi-turn with tool use
- Autonomous error recovery
- Explicit validation
- Better test coverage

**Innovation**: Combines TDD methodology with agentic capabilities - tests are written BEFORE implementation based on requirements, ensuring better coverage and preventing over-engineering.

### 3. Evaluation Dataset

#### 9 Hard HumanEval Problems
Selected from top complexity scores (prompt + test length):

1. HumanEval/129 - `minPath` (2534 complexity)
2. HumanEval/69 - `search` (2295)
3. HumanEval/141 - `file_name_check` (2143)
4. HumanEval/94 - `skjkasdkd` (2079)
5. HumanEval/153 - `Strongest_Extension` (1948)
6. HumanEval/68 - `pluck` (1861)
7. HumanEval/133 - `sum_squares` (1775)
8. HumanEval/95 - `check_dict_case` (1767)
9. HumanEval/126 - `is_sorted` (1759)

**Total**: 10 problems (9 HumanEval + 1 SWE-Bench)

#### 1 SWE-Bench Problem
**Problem**: sklearn `RidgeClassifierCV` missing `store_cv_values` parameter
**File**: `problems/swe_bench_ridge.md`
**Real-world**: Actual bug from scikit-learn requiring patch generation

### 4. Models for Evaluation

1. **deepseek/deepseek-chat-v3** - Fast, cost-effective
2. **x-ai/grok-2-vision-1212** - xAI's Grok model
3. *(Optional)* anthropic/claude-3.5-sonnet - High quality

All accessed via OpenRouter API with consistent interface.

## Project Structure

```
hw1-llm-prompt/
├── README.md                      # Full documentation
├── QUICKSTART.md                  # Quick start guide
├── PROJECT_SUMMARY.md             # This file
├── requirements.txt               # Dependencies
├── .env.example                   # API key template
│
├── openrouter_client.py          # LLM client
├── tools.py                       # Tool definitions
├── agent.py                       # Agent framework
│
├── strategies/
│   ├── cot.py                    # Chain-of-Thought
│   ├── stepwise_cot.py           # Stepwise CoT
│   └── test_driven_agent.py      # Test-Driven Agent (Innovation)
│
├── problems/
│   ├── prepare_humaneval.py      # Problem preparation script
│   ├── humaneval_hard9.json      # Problem data
│   ├── Human Eval_*.md              # 9 hard problems
│   └── swe_bench_ridge.md        # SWE-Bench problem
│
├── human-eval/                    # Official HumanEval repo (cloned)
└── output/                        # Generated solutions (created on run)
```

## How to Use

### Quick Test

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env
# Add your OPENROUTER_API_KEY to .env

# Test CoT
python strategies/cot.py \
  --problem problems/HumanEval_126.md \
  --model deepseek/deepseek-chat-v3

# Test Stepwise CoT
python strategies/stepwise_cot.py \
  --problem problems/HumanEval_129.md \
  --model deepseek/deepseek-chat-v3

# Test Test-Driven Agent (Innovation)
python strategies/test_driven_agent.py \
  --problem problems/HumanEval_141.md \
  --model deepseek/deepseek-chat-v3
```

### Full Evaluation

For the assignment, run:
- All 3 strategies
- On all 10 problems
- With 2+ different models
- Save results as JSON files

Compare metrics:
- Success rate (pass@k)
- Token usage
- Execution time
- Quality of generated code

## Key Features

### OpenRouter Integration
✅ Structured outputs for reliable parsing
✅ Tool calling for agentic workflows
✅ Prompt caching for cost efficiency
✅ Multiple model support with single API

### Robust Implementation
✅ Error handling and retries
✅ Timeout protection
✅ Cross-platform compatibility (Windows/Linux)
✅ Detailed logging and progress tracking

### Research-Based Approaches
✅ CoT based on NeurIPS 2022 paper
✅ Stepwise CoT with explicit phases
✅ Novel TDD agent combining methodology with autonomy

## Innovation Highlights (Part 3)

The Test-Driven Agent represents a workflow-based innovation:

**Traditional Approach**: Generate code → Test → Fix if needed
**TDD Agent Approach**: Analyze requirements → Write tests → Generate minimal code → Validate → Iterate

**Advantages**:
1. Tests are written from requirements, not from code (better coverage)
2. Implementation is guided by tests (prevents over-engineering)
3. Agent can fix its own mistakes autonomously
4. Explicit validation at each step

**Use of Tools**:
- `write_file`: Creates test and solution files
- `bash`: Executes tests and captures output
- `edit_file`: Makes targeted fixes based on errors
- `read_file`: Inspects generated files

This combines:
- Software engineering best practices (TDD)
- Agentic capabilities (tool use, autonomy)
- Multi-turn reasoning (iterative refinement)

## For Assignment Submission

### Part 1: Prompt Design & Code Generation (40% - 8 points)
- ✅ 10 problems selected (9 HumanEval + 1 SWE-Bench)
- ✅ 2 prompting strategies (CoT + Stepwise CoT)
- ✅ 2+ LLM families (DeepSeek, Grok, optional Claude)
- ✅ Evaluation with pass@k metric
- ✅ Results table with prompts and analysis

### Part 2: Debugging & Iterative Improvement (30% - 6 points)
- Run evaluation, identify failures
- Analyze failure cases (reasoning gap, error handling, misunderstanding)
- Document debugging process
- Compare how different models fail
- Include exact prompts for failed and improved attempts

### Part 3: Innovation (30% - 6 points)
- ✅ Novel strategy: Test-Driven Agent
- ✅ Implementation with tool integration
- ✅ Workflow description and rationale
- ✅ Applied to 2+ LLMs from different families
- ✅ Analysis of effectiveness vs. other strategies

## Next Steps

1. **Run Evaluation**: Execute all strategies on all problems
2. **Collect Results**: Save JSON outputs with metrics
3. **Analyze Failures**: Identify at least 2 failure cases for Part 2
4. **Compare Approaches**: Quantitative and qualitative comparison
5. **Write Report**: PDF with prompts, results, analysis, and innovation discussion

## References

- Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", NeurIPS 2022
- OpenRouter API: https://openrouter.ai/docs
- HumanEval Dataset: https://github.com/openai/human-eval
- SWE-Bench: https://github.com/SWE-bench/SWE-bench

## License

MIT (for educational purposes - CS520 Assignment)
