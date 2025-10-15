"""
Main agentic loop with error handling and tool execution.
"""

import json
import time
from typing import List, Dict, Any, Optional
from openrouter_client import OpenRouterClient
from tools import TOOL_SCHEMAS, ToolExecutor, format_tool_result


class Agent:
    """
    Autonomous agent that uses LLMs and tools to solve programming tasks.
    """

    def __init__(
        self,
        model: str = "deepseek/deepseek-chat-v3",
        working_dir: str = ".",
        max_iterations: int = 10,
        temperature: float = 0.7,
        verbose: bool = True
    ):
        self.model = model
        self.client = OpenRouterClient()
        self.executor = ToolExecutor(working_dir=working_dir)
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.verbose = verbose

        self.conversation_history: List[Dict[str, Any]] = []
        self.total_tokens = 0
        self.total_tool_calls = 0

    def log(self, message: str):
        """Print message if verbose."""
        if self.verbose:
            print(message)

    def run(
        self,
        task: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the agent on a task.

        Args:
            task: The task description
            system_prompt: Optional system prompt (defaults to generic coding agent prompt)

        Returns:
            Dict with "success", "result", "iterations", "tokens", "tool_calls"
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()

        # Initialize conversation
        self.conversation_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]

        start_time = time.time()
        iterations = 0
        finished = False
        final_result = None

        self.log(f"\n{'='*60}")
        self.log(f"Starting agent with model: {self.model}")
        self.log(f"{'='*60}\n")

        try:
            while iterations < self.max_iterations and not finished:
                iterations += 1
                self.log(f"\n--- Iteration {iterations} ---\n")

                # Get LLM response with tool calling
                response = self.client.chat_with_tools(
                    model=self.model,
                    messages=self.conversation_history,
                    tools=TOOL_SCHEMAS,
                    temperature=self.temperature
                )

                # Track tokens
                usage = self.client.get_usage(response)
                self.total_tokens += usage["total_tokens"]

                message = response["choices"][0]["message"]
                self.conversation_history.append(message)

                # Handle text response
                if message.get("content"):
                    self.log(f"Agent: {message['content']}\n")

                # Handle tool calls
                if message.get("tool_calls"):
                    tool_results = []

                    for tool_call in message["tool_calls"]:
                        self.total_tool_calls += 1
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])

                        self.log(f"🔧 Tool: {tool_name}")
                        self.log(f"   Args: {json.dumps(tool_args, indent=2)}")

                        # Execute tool
                        result = self.executor.execute(tool_name, tool_args)

                        # Check if finished
                        if result.get("finished"):
                            finished = True
                            final_result = result["output"]

                        # Format result for display
                        formatted = format_tool_result(tool_name, result)
                        self.log(f"   Result: {formatted}\n")

                        # Add tool result to conversation
                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(result)
                        })

                    # Add all tool results to conversation
                    self.conversation_history.extend(tool_results)

                else:
                    # No tool calls and no finish - agent might be stuck
                    if iterations >= self.max_iterations - 1:
                        break

            elapsed_time = time.time() - start_time

            # Determine success
            success = finished and final_result is not None

            self.log(f"\n{'='*60}")
            self.log(f"Agent {'succeeded' if success else 'failed'} after {iterations} iterations")
            self.log(f"Time: {elapsed_time:.2f}s | Tokens: {self.total_tokens} | Tool calls: {self.total_tool_calls}")
            self.log(f"{'='*60}\n")

            return {
                "success": success,
                "result": final_result,
                "iterations": iterations,
                "tokens": self.total_tokens,
                "tool_calls": self.total_tool_calls,
                "time": elapsed_time,
                "conversation_history": self.conversation_history
            }

        except Exception as e:
            self.log(f"\n❌ Error: {str(e)}\n")
            return {
                "success": False,
                "error": str(e),
                "iterations": iterations,
                "tokens": self.total_tokens,
                "tool_calls": self.total_tool_calls
            }

    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the agent."""
        return """You are an expert programming agent that solves coding tasks autonomously.

You have access to these tools:
- bash: Execute bash commands (run tests, git operations, etc.)
- read_file: Read file contents
- write_file: Create or overwrite files
- edit_file: Edit files by replacing text
- finish: Mark the task as complete

Your workflow:
1. Understand the task thoroughly
2. Plan your approach
3. Use tools to implement the solution
4. Run tests to validate
5. Fix any errors iteratively
6. Call finish() when all tests pass

Important:
- Always test your code before finishing
- If tests fail, analyze the error and fix it
- Use bash to run tests: e.g., "python test_file.py" or "pytest test_file.py"
- Be thorough but efficient
- When finished, call the finish tool with a summary

Remember: You must call tools to interact with the environment. Just describing what you would do is not enough."""

    def run_with_retry(
        self,
        task: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Run the agent with automatic retry on failure.

        Returns the first successful result or the last failure.
        """
        for attempt in range(max_retries):
            self.log(f"\n{'#'*60}")
            self.log(f"Attempt {attempt + 1}/{max_retries}")
            self.log(f"{'#'*60}\n")

            result = self.run(task, system_prompt)

            if result["success"]:
                return result

            if attempt < max_retries - 1:
                self.log(f"\n⚠️  Attempt {attempt + 1} failed. Retrying...\n")
                # Reset for next attempt
                self.conversation_history = []
                self.total_tokens = 0
                self.total_tool_calls = 0

        return result


def main():
    """Example usage of the agent."""
    import argparse

    parser = argparse.ArgumentParser(description="Run the agentic loop on a programming task")
    parser.add_argument("--problem", type=str, required=True, help="Path to problem description file")
    parser.add_argument("--model", type=str, default="deepseek/deepseek-chat-v3", help="Model to use")
    parser.add_argument("--working-dir", type=str, default=".", help="Working directory for file operations")
    parser.add_argument("--max-iterations", type=int, default=10, help="Maximum iterations")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    parser.add_argument("--quiet", action="store_true", help="Disable verbose output")

    args = parser.parse_args()

    # Read problem description
    with open(args.problem, 'r', encoding='utf-8') as f:
        problem = f.read()

    # Create and run agent
    agent = Agent(
        model=args.model,
        working_dir=args.working_dir,
        max_iterations=args.max_iterations,
        temperature=args.temperature,
        verbose=not args.quiet
    )

    result = agent.run_with_retry(problem, max_retries=3)

    # Print summary
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(f"Success: {result['success']}")
    print(f"Iterations: {result.get('iterations', 0)}")
    print(f"Tokens used: {result.get('tokens', 0)}")
    print(f"Tool calls: {result.get('tool_calls', 0)}")
    if result['success']:
        print(f"\nSummary: {result['result']}")
    else:
        print(f"\nError: {result.get('error', 'Task not completed')}")
    print("="*60)


if __name__ == "__main__":
    main()
