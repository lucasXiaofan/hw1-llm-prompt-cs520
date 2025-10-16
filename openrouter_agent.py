"""Minimal OpenRouter conversation with tool calling."""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Define tools
bash_tool = {
    "type": "function",
    "function": {
        "name": "bash_command",
        "description": "Execute bash/shell commands. Can create files, list directories, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute"
                }
            },
            "required": ["command"]
        }
    }
}

think_tool = {
    "type": "function",
    "function": {
        "name": "think",
        "description": "Continue internal reasoning and reflection before giving final answer. Use this to analyze, plan, or reconsider your approach.",
        "parameters": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "Your internal thoughts, analysis, or reflection"
                }
            },
            "required": ["thought"]
        }
    }
}

agent_tools = [bash_tool, think_tool]

# Tool executor
def execute_tool(name, args):
    if name == "bash_command":
        import subprocess
        try:
            result = subprocess.run(
                args["command"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return f"Success:\n{result.stdout}" if result.stdout else "Success (no output)"
            else:
                return f"Error (code {result.returncode}):\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Command timeout"
        except Exception as e:
            return f"Error: {str(e)}"
    elif name == "think":
        # Return acknowledgment, allowing agent to continue reasoning
        return "Thought recorded. Continue thinking or provide final answer."
    return "Unknown tool"

# Agent with max iterations
def agent(user_prompt, system_message=None, max_iterations=10, model_name="deepseek/deepseek-chat-v3", tools=None):
    messages = []

    # Use provided tools or default to agent_tools
    if tools is None:
        tools = [think_tool]

    # Add system message if provided
    if system_message:
        messages.append({"role": "system", "content": system_message})

    # Add user prompt
    messages.append({"role": "user", "content": user_prompt})

    for iteration in range(max_iterations):
        print(f"\n{'='*60}")
        print(f"ITERATION {iteration + 1}")
        print(f"{'='*60}")

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools
        )

        msg = response.choices[0].message
        messages.append(msg)

        # Check if assistant made tool calls
        if msg.tool_calls:
            print(f"Type: TOOL_CALL")
            print(f"Assistant wants to use {len(msg.tool_calls)} tool(s):")

            # Execute each tool
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"\n  Tool: {name}")
                print(f"  Args: {json.dumps(args, indent=8)}")

                result = execute_tool(name, args)

                print(f"  Result: {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        else:
            # Final text response
            print(f"Type: TEXT_RESPONSE")
            print(f"Content: {msg.content}")
            return messages, msg.content

    print(f"\n{'='*60}")
    print("MAX ITERATIONS REACHED")
    print(f"{'='*60}")
    return messages, "Max iterations reached"

def string_to_function(code: str, func_name: str):
    """
    Convert a function defined in a string into a callable Python function.

    Parameters
    ----------
    code : str
        String containing the Python function definition.
    func_name : str
        Name of the function to extract from the code.

    Returns
    -------
    function
        The callable Python function.
    """
    # restrict builtins (enough for LeetCode-like problems)
    safe_builtins = {
        "range": range,
        "len": len,
        "print": print,
        "sum": sum,
        "min": min,
        "max": max,
        "abs": abs,
        "sorted": sorted,
        "enumerate": enumerate,
        "zip": zip,
        "map": map,
        "filter": filter,
        "any": any,
        "all": all,
    }
    safe_globals = {"__builtins__": safe_builtins}
    safe_builtins["__import__"] = __import__
    local_vars = {}
    # define function inside this controlled namespace
    exec(code, safe_globals, local_vars)
    return local_vars[func_name]

def clean_json_output(output: str):
    """
    Remove markdown fences (```json, ```python, ```) if they exist.
    Returns clean JSON string.
    """
    output = output.strip()

    # If wrapped in triple backticks
    if output.startswith("```"):
        # split on triple backticks and take the middle part
        parts = output.split("```")
        if len(parts) >= 2:
            output = parts[1].strip()

        # Sometimes it starts with "json\n" or "python\n"
        if output.startswith("json"):
            output = output[len("json"):].strip()
        elif output.startswith("python"):
            output = output[len("python"):].strip()

    return output

# Test
if __name__ == "__main__":
    # Test-driven development system message
    test_driven_agent_system_prompt = """You are a test-driven development agent. Follow these steps:
1. Analyze the problem requirements and extract a SHORT problem name (e.g., "is_prime", "fibonacci", "sort_array")
2. Create directory: mkdir -p test_driven_agent
3. Write test file first: test_driven_agent/test_<problem_name>.py with comprehensive test cases
4. Write solution file: test_driven_agent/<problem_name>.py with the implementation
5. Run the test to see failures: python test_driven_agent/test_<problem_name>.py
6. Fix the code iteratively until all tests pass

IMPORTANT file naming rules:
- All files must be in test_driven_agent/ folder
- Test file: test_driven_agent/test_<problem_name>.py
- Solution file: test_driven_agent/<problem_name>.py
- Use the SAME <problem_name> for both files (e.g., test_is_prime.py and is_prime.py)

Example for "is_prime" problem:
- mkdir -p test_driven_agent
- echo "test code" > test_driven_agent/test_is_prime.py
- echo "solution code" > test_driven_agent/is_prime.py
- python test_driven_agent/test_is_prime.py"""








    user_task = """
        "Given an array representing a branch of a tree that has non-negative integer nodes
    your task is to pluck one of the nodes and return it.
    The plucked node should be the node with the smallest even value.
    If multiple nodes with the same smallest even value are found return the node that has smallest index.

    The plucked node should be returned in a list, [ smalest_value, its index ],
    If there are no even values or the given array is empty, return [].

    Example 1:
        Input: [4,2,3]
        Output: [2, 1]
        Explanation: 2 has the smallest even value, and 2 has the smallest index.

    Example 2:
        Input: [1,2,3]
        Output: [2, 1]
        Explanation: 2 has the smallest even value, and 2 has the smallest index. 

    Example 3:
        Input: []
        Output: []
    
    Example 4:
        Input: [5, 0, 3, 0, 4, 2]
        Output: [0, 1]
        Explanation: 0 is the smallest value, but  there are two zeros,
                     so we will choose the first zero, which has the smallest index.

    Constraints:
        * 1 <= nodes.length <= 10000
        * 0 <= node.value
    """

    normal_coding_agent = """
You are a coding assistant. 
Think step by step first 
Solve the following problem and return ONLY valid JSON.

The JSON format must be:

{
  "name": "<function_name>",
  "code": "<python_function_code>"
}

Requirements:
- Put the entire function in "code" as a valid Python function string.
- Do not include imports unless required.
- Do not include extra text or explanations, only JSON. do not include 
```json
content
```, just output json content
    """
    with open("humaneval_hard9.json",'r') as file:
        hp9 = json.load(file)
    h129 = hp9['HumanEval/129']
    test_p = h129['prompt']
    test_t = h129['test']
    solution = h129['canonical_solution']
    
    string_to_function(test_t,"check")(string_to_function(solution,h129['entry_point']))
    print(f"passed")
    # history, answer = agent(
    #     user_prompt=test_p,
    #     system_message=normal_coding_agent,
    #     max_iterations=10
    # )

    # print(f"\n{'='*60}")
    # print(f"FINAL ANSWER: {answer}")
    # print(f"Total messages: {len(history)}")
    # # print(f"history {history}")
    # print(f"{'='*60}")
    
    # try:
    #     answer = clean_json_output(answer)
    #     print(answer)
    #     name, code = json.loads(answer)['name'],json.loads(answer)['code']
    #     print(f"name {name}, code: {code}")
    #     run_code = string_to_function(code,name)
    #     test_code = string_to_function(test_t,"check")
    #     test_code(run_code)
    # except Exception as e:
    #     print(f"error {e}")


