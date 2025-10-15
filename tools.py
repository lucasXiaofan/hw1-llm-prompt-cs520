"""
Tool definitions for the agentic loop.
Each tool has a JSON schema for structured calling and an execution function.
"""

import os
import subprocess
from typing import Dict, Any, List


# Tool schemas for OpenRouter tool calling
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a bash command and return stdout/stderr. Use for running tests, git operations, etc.",
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
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file (creates or overwrites)",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit a file by replacing old_text with new_text",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to edit"
                    },
                    "old_text": {
                        "type": "string",
                        "description": "Text to find and replace"
                    },
                    "new_text": {
                        "type": "string",
                        "description": "Text to replace with"
                    }
                },
                "required": ["file_path", "old_text", "new_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": "Mark the task as complete. Call this when all tests pass and the solution is ready.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Brief summary of what was accomplished"
                    }
                },
                "required": ["summary"]
            }
        }
    }
]


class ToolExecutor:
    """Executes tools and returns results."""

    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given arguments.

        Returns:
            Dict with "success", "output", and optional "error"
        """
        try:
            if tool_name == "bash":
                return self.bash(arguments["command"])
            elif tool_name == "read_file":
                return self.read_file(arguments["file_path"])
            elif tool_name == "write_file":
                return self.write_file(arguments["file_path"], arguments["content"])
            elif tool_name == "edit_file":
                return self.edit_file(
                    arguments["file_path"],
                    arguments["old_text"],
                    arguments["new_text"]
                )
            elif tool_name == "finish":
                return {"success": True, "output": arguments["summary"], "finished": True}
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def bash(self, command: str) -> Dict[str, Any]:
        """Execute a bash command."""
        try:
            # Use shell=True for Windows compatibility with git-bash
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout + result.stderr
            success = result.returncode == 0

            return {
                "success": success,
                "output": output.strip(),
                "return_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 60 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute command: {str(e)}"
            }

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file."""
        try:
            # Handle both absolute and relative paths
            full_path = os.path.join(self.working_dir, file_path) if not os.path.isabs(file_path) else file_path

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "output": content
            }

        except FileNotFoundError:
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}"
            }

    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        try:
            # Handle both absolute and relative paths
            full_path = os.path.join(self.working_dir, file_path) if not os.path.isabs(file_path) else file_path

            # Create parent directories if needed
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "output": f"Successfully wrote to {file_path}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to write file: {str(e)}"
            }

    def edit_file(self, file_path: str, old_text: str, new_text: str) -> Dict[str, Any]:
        """Edit a file by replacing old_text with new_text."""
        try:
            # Read current content
            read_result = self.read_file(file_path)
            if not read_result["success"]:
                return read_result

            content = read_result["output"]

            # Check if old_text exists
            if old_text not in content:
                return {
                    "success": False,
                    "error": f"Text to replace not found in {file_path}"
                }

            # Replace and write back
            new_content = content.replace(old_text, new_text, 1)  # Replace first occurrence
            return self.write_file(file_path, new_content)

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to edit file: {str(e)}"
            }


def format_tool_result(tool_name: str, result: Dict[str, Any]) -> str:
    """Format a tool execution result for display."""
    if result["success"]:
        output = result.get("output", "")
        if tool_name == "bash":
            return f"✓ Command executed (exit code: {result.get('return_code', 0)})\n{output}"
        else:
            return f"✓ {output}"
    else:
        return f"✗ Error: {result.get('error', 'Unknown error')}"


if __name__ == "__main__":
    # Test the tools
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    print(f"Testing in: {temp_dir}\n")

    try:
        executor = ToolExecutor(working_dir=temp_dir)

        # Test write_file
        print("1. Testing write_file...")
        result = executor.execute("write_file", {
            "file_path": "test.txt",
            "content": "Hello, World!"
        })
        print(format_tool_result("write_file", result))
        print()

        # Test read_file
        print("2. Testing read_file...")
        result = executor.execute("read_file", {"file_path": "test.txt"})
        print(format_tool_result("read_file", result))
        print()

        # Test edit_file
        print("3. Testing edit_file...")
        result = executor.execute("edit_file", {
            "file_path": "test.txt",
            "old_text": "World",
            "new_text": "Python"
        })
        print(format_tool_result("edit_file", result))

        result = executor.execute("read_file", {"file_path": "test.txt"})
        print(f"After edit: {result['output']}")
        print()

        # Test bash
        print("4. Testing bash...")
        result = executor.execute("bash", {"command": "echo 'Testing bash'"})
        print(format_tool_result("bash", result))
        print()

        print("All tools working correctly!")

    finally:
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up: {temp_dir}")
