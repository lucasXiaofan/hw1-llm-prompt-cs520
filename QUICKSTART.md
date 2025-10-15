# Quick Start Guide

This guide will help you get started with testing LLM code generation strategies.

## Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

Get your API key from: https://openrouter.ai/keys

### 3. Verify Setup

```bash
python openrouter_client.py
```

You should see successful test outputs.

## Running Individual Strategies

### Strategy 1: Chain-of-Thought (CoT)

Simple prompting that asks the model to "think step by step":

```bash
python strategies/cot.py \
  --problem problems/HumanEval_126.md \
  --model deepseek/deepseek-chat-v3 \
  --output-dir output/cot
```

### Strategy 2: Stepwise Chain-of-Thought (SCoT)

Breaks down reasoning into explicit numbered steps:

```bash
python strategies/stepwise_cot.py \
  --problem problems/HumanEval_129.md \
  --model deepseek/deepseek-chat-v3 \
  --output-dir output/scot
```

### Strategy 3: Test-Driven Agent (Innovation - Part 3)

Agentic workflow that writes tests first, then implements code:

```bash
python strategies/test_driven_agent.py \
  --problem problems/HumanEval_141.md \
  --model deepseek/deepseek-chat-v3 \
  --working-dir output/tdd
```

## Testing on Different Models

### DeepSeek (Fast, Cost-Effective)

```bash
python strategies/test_driven_agent.py \
  --problem problems/HumanEval_94.md \
  --model deepseek/deepseek-chat-v3
```

### Grok (xAI)

```bash
python strategies/cot.py \
  --problem problems/HumanEval_153.md \
  --model x-ai/grok-2-vision-1212
```

### Claude (High Quality)

```bash
python strategies/stepwise_cot.py \
  --problem problems/swe_bench_ridge.md \
  --model anthropic/claude-3.5-sonnet
```

## Available Problems

### 9 Hard HumanEval Problems

Located in `problems/`:
- `HumanEval_129.md` - minPath (grid/matrix problem)
- `HumanEval_69.md` - search (binary search variant)
- `HumanEval_141.md` - file_name_check (string validation)
- `HumanEval_94.md` - skjkasdkd (complex list processing)
- `HumanEval_153.md` - Strongest_Extension (string manipulation)
- `HumanEval_68.md` - pluck (list processing)
- `HumanEval_133.md` - sum_squares (mathematical)
- `HumanEval_95.md` - check_dict_case (dictionary validation)
- `HumanEval_126.md` - is_sorted (list analysis)

### 1 SWE-Bench Problem

- `problems/swe_bench_ridge.md` - Real sklearn bug fix (adding store_cv_values parameter)

## Understanding the Output

Each strategy generates:

1. **Code files**: The generated solution
2. **Test files**: Test cases (if applicable)
3. **Result JSON**: Metadata about the run (tokens, time, success)

Example output structure:
```
output/
├── cot/
│   ├── solution_cot.py
│   └── test_cot.py
├── scot/
│   ├── solution_scot.py
│   └── test_scot.py
└── tdd/
    ├── solution.py
    ├── test_solution.py
    └── [agent working files]
```

## Quick Comparison

Run all three strategies on the same problem:

```bash
# CoT
python strategies/cot.py \
  --problem problems/HumanEval_126.md \
  --model deepseek/deepseek-chat-v3 \
  --result-file results/cot_126.json

# Stepwise CoT
python strategies/stepwise_cot.py \
  --problem problems/HumanEval_126.md \
  --model deepseek/deepseek-chat-v3 \
  --result-file results/scot_126.json

# Test-Driven Agent
python strategies/test_driven_agent.py \
  --problem problems/HumanEval_126.md \
  --model deepseek/deepseek-chat-v3 \
  --result-file results/tdd_126.json
```

Then compare results:

```bash
cat results/*_126.json
```

## Tips for Best Results

1. **Start with easier problems** to understand each strategy
2. **Use DeepSeek for initial testing** (faster, cheaper)
3. **Try different models** for difficult problems
4. **Check generated code** before running tests
5. **Increase max-iterations** for complex problems with TDD agent

## Troubleshooting

### API Key Issues

```bash
# Verify .env file
cat .env

# Test API connection
python -c "from openrouter_client import OpenRouterClient; c = OpenRouterClient(); print('Connected!')"
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Model Not Available

Check available models at: https://openrouter.ai/models

Replace model name in commands with any supported model.

## Next Steps

1. Run all strategies on a few problems
2. Compare success rates and token usage
3. Analyze where each strategy succeeds/fails
4. Test on the SWE-Bench problem for real-world complexity

## For Assignment Submission

Your evaluation should include:
- **Part 1**: Results from CoT and Stepwise CoT on 10 problems (9 HumanEval + 1 SWE-Bench) across 2 models
- **Part 2**: Debugging analysis of at least 2 failure cases
- **Part 3**: Test-Driven Agent results and comparison with other strategies

Good luck! 🚀
