"""
Test-Driven Agentic Workflow (Innovation - Part 3 of Assignment)

This is a novel strategy that combines Test-Driven Development principles with
agentic tool use. Unlike traditional approaches that generate code then test it,
this agent:

1. Analyzes the problem to understand requirements
2. Writes comprehensive tests FIRST (TDD approach)
3. Generates minimal code to pass each test
4. Iteratively refines until all tests pass
5. Uses tools autonomously (bash, file operations)

Advantages over CoT/Stepwise CoT:
- Better test coverage (tests written before code based on requirements)
- Prevents over-engineering (minimal code to pass tests)
- Autonomous error recovery (agent fixes its own mistakes)
- Explicit validation at each step

This represents a workflow-based innovation combining:
- Test-Driven Development methodology
- Agentic tool use
- Multi-step generation with refinement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent


class TestDrivenAgent(Agent):
    """Agent using Test-Driven Development workflow."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strategy_name = "Test-Driven Agent"

    def _get_default_system_prompt(self) -> str:
        """System prompt for Test-Driven Agent."""
        return """You are an expert programming agent that follows Test-Driven Development (TDD) principles.

YOUR WORKFLOW (STRICTLY FOLLOW THIS ORDER):

Phase 1: UNDERSTAND REQUIREMENTS
- Carefully read the problem statement
- Identify ALL inputs, outputs, and constraints
- List edge cases and error conditions
- State your understanding clearly

Phase 2: WRITE TESTS FIRST (TDD Core Principle)
- Based on requirements, write comprehensive test cases BEFORE any implementation
- Cover:
  * Normal/happy path cases
  * Edge cases (empty inputs, boundaries, max values)
  * Error cases (invalid inputs, type errors)
- Use write_file to create a test file (e.g., test_solution.py)
- Tests should import from a solution module that doesn't exist yet

Phase 3: IMPLEMENT MINIMAL CODE
- Now write the SIMPLEST code that could pass the tests
- Don't over-engineer - just make tests pass
- Use write_file to create the solution file

Phase 4: RUN TESTS
- Use bash to execute the test file: "python test_solution.py"
- Observe results carefully

Phase 5: DEBUG AND FIX (if tests fail)
- Read the error message carefully
- Identify what's wrong in the code
- Use edit_file to make targeted fixes
- Return to Phase 4 (re-run tests)

Phase 6: VERIFY AND COMPLETE
- Ensure ALL tests pass
- Review code for correctness and completeness
- Call finish() with a summary of what was accomplished

IMPORTANT TDD PRINCIPLES:
1. TESTS FIRST - Always write tests before implementation
2. RED-GREEN-REFACTOR - Write failing test → make it pass → improve code
3. MINIMAL CODE - Only write enough to pass current tests
4. ONE STEP AT A TIME - Don't jump ahead

Tools available:
- bash: Run commands (execute tests, check files, etc.)
- read_file: Read file contents
- write_file: Create new files
- edit_file: Modify existing files
- finish: Mark task as complete (only when all tests pass!)

Remember: The key innovation is writing comprehensive tests BEFORE any implementation code.
This ensures better test coverage and prevents bugs."""


def main():
    """CLI for Test-Driven Agent strategy."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Run Test-Driven Agent strategy (Innovation)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This is the INNOVATION component (Part 3) of the assignment.

Example usage:
  python test_driven_agent.py --problem ../problems/humaneval_0.md --model deepseek/deepseek-chat-v3

The agent will:
1. Read the problem
2. Write tests first (TDD)
3. Implement code to pass tests
4. Fix any failures iteratively
5. Report when all tests pass
        """
    )

    parser.add_argument("--problem", type=str, required=True, help="Problem description file")
    parser.add_argument("--model", type=str, default="deepseek/deepseek-chat-v3", help="Model to use")
    parser.add_argument("--working-dir", type=str, default="output/tdd", help="Working directory for files")
    parser.add_argument("--max-iterations", type=int, default=15, help="Maximum iterations")
    parser.add_argument("--result-file", type=str, help="JSON file for results")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode")

    args = parser.parse_args()

    # Create working directory
    os.makedirs(args.working_dir, exist_ok=True)

    # Read problem
    with open(args.problem, 'r', encoding='utf-8') as f:
        problem = f.read()

    # Create agent
    agent = TestDrivenAgent(
        model=args.model,
        working_dir=args.working_dir,
        max_iterations=args.max_iterations,
        temperature=0.7,
        verbose=not args.quiet
    )

    print(f"\n{'='*60}")
    print(f"TEST-DRIVEN AGENT (Innovation - Part 3)")
    print(f"Model: {args.model}")
    print(f"Working dir: {args.working_dir}")
    print(f"{'='*60}\n")

    # Run agent
    result = agent.run_with_retry(problem, max_retries=2)

    # Save results
    if args.result_file:
        # Don't save full conversation to keep file size reasonable
        save_result = {
            "strategy": "Test-Driven Agent (Innovation)",
            "model": args.model,
            "problem": args.problem,
            "success": result["success"],
            "iterations": result.get("iterations", 0),
            "tokens": result.get("tokens", 0),
            "tool_calls": result.get("tool_calls", 0),
            "time": result.get("time", 0),
            "result": result.get("result", "")
        }
        if not result["success"]:
            save_result["error"] = result.get("error", "")

        with open(args.result_file, 'w') as f:
            json.dump(save_result, f, indent=2)
        print(f"\n✓ Saved results to: {args.result_file}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST-DRIVEN AGENT - {'SUCCESS ✓' if result['success'] else 'FAILED ✗'}")
    print(f"{'='*60}")
    print(f"Model: {args.model}")
    print(f"Iterations: {result.get('iterations', 0)}")
    print(f"Tool calls: {result.get('tool_calls', 0)}")
    print(f"Tokens used: {result.get('tokens', 0)}")
    print(f"Time: {result.get('time', 0):.2f}s")

    if result["success"]:
        print(f"\n✓ Summary: {result.get('result', '')}")
        print(f"\nGenerated files in: {args.working_dir}")
    else:
        print(f"\n✗ Error: {result.get('error', 'Unknown error')}")

    print(f"{'='*60}\n")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
