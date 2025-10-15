"""
OpenRouter LLM Client with support for:
- Structured outputs (JSON schema)
- Tool/function calling
- Prompt caching
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class OpenRouterClient:
    """Client for OpenRouter API with advanced features."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        site_url: Optional[str] = None,
        app_name: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.site_url = site_url or os.getenv("OPENROUTER_SITE_URL", "")
        self.app_name = app_name or os.getenv("OPENROUTER_APP_NAME", "cs520-hw1")

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")

        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if self.site_url:
            self.headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            self.headers["X-Title"] = self.app_name

    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_caching: bool = True,
    ) -> Dict[str, Any]:
        """
        Make a chat completion request to OpenRouter.

        Args:
            model: Model ID (e.g., "deepseek/deepseek-chat-v3")
            messages: List of message dicts with "role" and "content"
            tools: List of tool definitions (OpenAI format)
            tool_choice: "auto", "none", or {"type": "function", "function": {"name": "..."}}
            response_format: For structured outputs, e.g.:
                {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "response",
                        "schema": {...}
                    }
                }
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            use_caching: Whether to enable prompt caching (automatic)

        Returns:
            Response dict with "choices", "usage", etc.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice

        if response_format:
            payload["response_format"] = response_format

        # OpenRouter automatically handles caching for repeated prompt prefixes
        # No special header needed - it's enabled by default

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except:
                error_detail = e.response.text
            raise Exception(f"OpenRouter API error: {e}\nDetail: {error_detail}")

        except Exception as e:
            raise Exception(f"Request failed: {e}")

    def simple_chat(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Simple chat completion without tools.

        Returns:
            Just the text content of the response.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.chat_completion(
            model=model,
            messages=messages,
            temperature=temperature
        )

        return response["choices"][0]["message"]["content"]

    def chat_with_tools(
        self,
        model: str,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Chat completion with tool calling enabled.

        Returns:
            Full response dict. Check response["choices"][0]["message"] for:
            - "content": Text response
            - "tool_calls": List of tool calls if any
        """
        return self.chat_completion(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=temperature
        )

    def structured_output(
        self,
        model: str,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        schema_name: str = "response",
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Chat completion with structured JSON output.

        Args:
            schema: JSON schema for the expected response structure
            schema_name: Name for the schema

        Returns:
            Parsed JSON object matching the schema.
        """
        response = self.chat_completion(
            model=model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "schema": schema,
                    "strict": True
                }
            },
            temperature=temperature
        )

        content = response["choices"][0]["message"]["content"]
        return json.loads(content)

    def get_usage(self, response: Dict[str, Any]) -> Dict[str, int]:
        """Extract token usage from response."""
        usage = response.get("usage", {})
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "cached_tokens": usage.get("prompt_tokens_cached", 0),  # Cached prompt tokens
        }


def test_client():
    """Test the OpenRouter client."""
    client = OpenRouterClient()

    print("Testing simple chat...")
    response = client.simple_chat(
        model="deepseek/deepseek-chat-v3",
        prompt="What is 2+2? Answer in one word.",
        temperature=0
    )
    print(f"Response: {response}\n")

    print("Testing structured output...")
    schema = {
        "type": "object",
        "properties": {
            "answer": {"type": "number"},
            "explanation": {"type": "string"}
        },
        "required": ["answer", "explanation"]
    }
    result = client.structured_output(
        model="deepseek/deepseek-chat-v3",
        messages=[{"role": "user", "content": "What is 5+7? Respond with JSON."}],
        schema=schema,
        temperature=0
    )
    print(f"Structured result: {json.dumps(result, indent=2)}\n")

    print("Testing tool calling...")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Perform a calculation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"]
                        },
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["operation", "a", "b"]
                }
            }
        }
    ]

    response = client.chat_with_tools(
        model="deepseek/deepseek-chat-v3",
        messages=[{"role": "user", "content": "What is 10 multiplied by 5?"}],
        tools=tools,
        temperature=0
    )

    message = response["choices"][0]["message"]
    if message.get("tool_calls"):
        for tool_call in message["tool_calls"]:
            print(f"Tool: {tool_call['function']['name']}")
            print(f"Args: {tool_call['function']['arguments']}")

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_client()
