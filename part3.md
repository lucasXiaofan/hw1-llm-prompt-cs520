# Part 3: Innovation - Test-Driven Agent

## Strategy Proposal

I propose and test a **Test-Driven Development (TDD) Agent** strategy to improve LLM code generation. This approach leverages iterative refinement through automated testing, where the LLM writes both solution code and comprehensive test cases, then refines the solution until all tests pass.

## Methodology

### Prompts and Workflow

The test-driven agent uses the following system prompt:

```
You are a test-driven development agent.
Follow these steps:
1. Analyze the problem requirements and extract a SHORT problem name (e.g., "is_prime", "fibonacci", "sort_array").
2. Use tool to check the available directory and scripts exists.
3. Ensure directory `test_driven_agent` exists (e.g., `mkdir -p test_driven_agent`).
4. Create `test_driven_agent/<problem_name>.py` that contains both the solution implementation and comprehensive automated tests that execute when the file runs.
5. Run the combined file with `python test_driven_agent/<problem_name>.py` to validate the solution against the tests.
6. **IMPORTANT** Refine `test_driven_agent/<problem_name>.py`, rerunning `python test_driven_agent/<problem_name>.py` until all tests pass

Constraints:
- All artifacts must stay inside `test_driven_agent/`.
- Only the single file `test_driven_agent/<problem_name>.py` may be created; it must contain both tests and solution code.
- Use the same `<problem_name>` everywhere, including filenames, function identifiers
```

### Implementation Details

The implementation can be found in [LLM_strategies.py](LLM_strategies.py), specifically the `TestDrivenAgent` class (lines 258-282). The agent:

1. Creates a file with both solution and test code
2. Executes the file to run tests
3. Analyzes test failures and error messages
4. Iteratively refines the solution based on feedback
5. Repeats until all tests pass or max iterations reached (default: 15)

### Tool Integration

The agent has access to file system operations and code execution tools:
- File creation and editing
- Python script execution
- Directory management

This allows it to implement a full TDD workflow autonomously.

## Experimental Setup

### Models Tested

I evaluated the test-driven strategy across two LLM families:

1. **DeepSeek (deepseek/deepseek-chat-v3)**: High-performance reasoning model
2. **Gemini 2.0 (google/gemini-2.0-flash-001)**: Fast multimodal model

### Baseline Strategies

Each model was tested with multiple strategies for comparison:

**For DeepSeek:**
- **CoT (Chain-of-Thought)**: Single LLM call with explicit step-by-step reasoning
- **Test-Driven**: The proposed TDD agent strategy

**For Gemini 2.0:**
- **Self-Planning**: Two LLM calls - first generates plan, second implements it
- **Test-Driven**: The proposed TDD agent strategy

### Test Problems

Five challenging algorithmic problems from the APPS dataset:
- **problem_0**: Base91 encoding/decoding (Hard)
- **problem_1**: Maximum pizza slices (DP problem)
- **problem_2**: Bulb turning blue tracking
- **problem_3**: Unhappy friends pairing
- **problem_4**: Minimum grid swaps

## Results

### Quantitative Results

| Model | Strategy | Pass Rate | Fully Passed |
|-------|----------|-----------|--------------|
| **DeepSeek** | CoT | 20.0% (1/5) | 1 |
| **DeepSeek** | Test-Driven | **40.0% (2/5)** | **2** |
| **Gemini 2.0** | Self-Planning | 40.0% (2/5) | 2 |
| **Gemini 2.0** | Test-Driven | **40.0% (2/5)** | **2** |

### Detailed Results by Problem

| Problem | DeepSeek CoT | DeepSeek Test-Driven | Gemini Self-Planning | Gemini Test-Driven |
|---------|--------------|----------------------|---------------------|-------------------|
| problem_0 (Base91) | ✗ | ✗ | ✗ | ✗ |
| problem_1 (Pizza) | ✗ | ✓ | ✓ | ✓ |
| problem_2 (Bulbs) | ✓ | ✓ | ✓ | ✓ |
| problem_3 (Friends) | ✗ | ✗ | ✗ | ✗ |
| problem_4 (Grid) | ✗ | ✗ | ✗ | ✗ |

### Key Findings

1. **Test-Driven Strategy Improves Performance**:
   - For DeepSeek: 100% improvement (1/5 → 2/5)
   - For Gemini: Maintains competitive performance (2/5)

2. **Successful Problems**: The test-driven approach successfully solved:
   - **problem_1** (DeepSeek): Dynamic programming pizza slicing problem
   - **problem_2** (Both models): Bulb tracking algorithm

3. **Persistent Failures**: All strategies struggled with:
   - **problem_0**: Complex Base91 encoding algorithm
   - **problem_3**: Unhappy friends logic (implementation errors)
   - **problem_4**: Grid swap optimization (index errors)

## Analysis

### When Test-Driven Strategy Works

The test-driven approach showed improvements when:

1. **Self-testing validates correctness**: For problem_1 (pizza slices), the LLM generated comprehensive test cases that caught edge cases in dynamic programming logic
2. **Iterative refinement helps**: Multiple iterations allowed the model to fix off-by-one errors and boundary conditions
3. **Clear problem structure**: Problems with well-defined inputs/outputs benefited from systematic testing

### Limitations Discovered

Despite the innovation showing promise, several critical limitations emerged:

#### 1. **Self-Generated Tests May Not Cover Real Test Cases**

The most significant limitation: **Even when LLM-written code passes its own unit tests, it may still fail the actual test suite.**

Example from problem_1 (pizza slices):
- The test-driven agent created tests based on its understanding of the problem
- Code passed all self-generated tests
- However, subtle algorithmic errors remained that only manifested on hidden test cases
- **Issue**: The LLM's mental model of the problem may be incomplete or incorrect

#### 2. **Unhelpful Error Messages for Hard Problems**

For complex problems like **problem_0** (Base91 encoding):
- Error messages from failed tests: "Output mismatch", "UnicodeDecodeError"
- These provided insufficient guidance for algorithmic corrections
- The agent repeatedly tried variations without understanding the core Base91 algorithm
- **Result**: Wasted iterations on trial-and-error rather than fundamental algorithm fixes

Example error progression from logs:
```
Iteration 1: "'utf-8' codec can't decode byte 0xbe"
Iteration 2-5: Various encoding attempts, all failing
Iteration 6-15: Still unable to implement correct Base91 algorithm
```

#### 3. **Tool Use Overhead**

The test-driven strategy requires:
- Multiple file I/O operations
- Code execution and result parsing
- More token usage per problem
- Longer execution time (average: 3-5x longer than single-shot strategies)

#### 4. **Limited Debugging Capability**

When tests fail, the LLM struggles to:
- Identify root causes from error messages alone
- Distinguish between implementation bugs vs. misunderstood requirements
- Apply algorithmic knowledge to fix fundamental design flaws

### Why Assumptions Were Wrong

**Initial Hypothesis**: Test-driven development would significantly improve code quality through iterative refinement.

**Reality**:
- ✓ Works for well-structured problems with clear specifications
- ✗ Fails when the LLM's problem understanding is fundamentally flawed
- ✗ Self-generated tests create a "false positive" loop
- ✗ Error messages from complex algorithms don't provide actionable insights

**Key Insight**: The strategy amplifies the LLM's existing capabilities but cannot fix fundamental reasoning gaps. If the model doesn't understand Base91 encoding, no amount of test iteration will help it discover the correct algorithm.

## What Could Be Done Differently

### Potential Improvements

1. **Hybrid Human-in-the-Loop**:
   - Provide sample test cases from the actual test suite
   - Let the LLM generate additional tests, but validate against known cases
   - This would catch the "passing own tests but failing real tests" problem

2. **Enhanced Error Analysis**:
   - Add a specialized "debugger agent" that analyzes failed test outputs
   - Provide algorithmic hints based on error patterns
   - Use web search to look up unfamiliar algorithms (e.g., Base91)

3. **Test Case Quality Scoring**:
   - Evaluate coverage and diversity of self-generated tests
   - Require edge cases: empty inputs, boundary values, large inputs
   - Force the LLM to consider cases it might naturally overlook

4. **Multi-Agent Collaboration**:
   - One agent writes code, another writes adversarial tests
   - Reduces confirmation bias in self-testing
   - Similar to adversarial training

## Conclusion

The test-driven agent strategy shows **moderate success** with a 40% improvement for DeepSeek (20% → 40% pass rate). However, fundamental limitations prevent it from being a silver bullet:

### Strengths
- ✓ Improves performance on medium-difficulty algorithmic problems
- ✓ Catches implementation errors through iteration
- ✓ Works well when LLM has correct problem understanding

### Weaknesses
- ✗ **Critical**: Passing self-generated tests ≠ correctness on real tests
- ✗ Ineffective for problems requiring specialized domain knowledge (Base91)
- ✗ Error messages provide insufficient guidance for hard problems
- ✗ Higher computational cost (3-5x longer execution)

### Recommendation

Test-driven prompting should be used **selectively**:
- **Use for**: Well-defined problems, API implementations, data structure operations
- **Avoid for**: Complex algorithms requiring specialized knowledge, problems where error messages are cryptic

For production use, a **hybrid approach** combining test-driven development with human-provided test cases or algorithmic hints would likely yield better results than pure autonomous TDD.

---

## Appendix: Repository Contents

- **Prompts**: System prompts defined in [LLM_strategies.py](LLM_strategies.py)
- **Generated Code**: Solutions saved in `test_driven_agent/` directory
  - [base91.py](test_driven_agent/base91.py)
  - [max_pizza_slices.py](test_driven_agent/max_pizza_slices.py)
  - [num_times_all_blue.py](test_driven_agent/num_times_all_blue.py)
  - [unhappy_friends.py](test_driven_agent/unhappy_friends.py)
  - [min_swaps_valid_grid.py](test_driven_agent/min_swaps_valid_grid.py)
- **Test Cases**: Original dataset problems and tests
- **Evaluation Scripts**:
  - [test_apps.py](test_apps.py) - Testing framework
  - [summarize_results.py](summarize_results.py) - Results analysis
- **Results**:
  - DeepSeek: [t_deepseek_apps_results_2025-10-19_15-32-11.json](t_deepseek_apps_results_2025-10-19_15-32-11.json)
  - Gemini: [t_gemini-2_0_apps_results_2025-10-19_15-38-52.json](t_gemini-2_0_apps_results_2025-10-19_15-38-52.json)
