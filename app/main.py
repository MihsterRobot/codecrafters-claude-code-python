import argparse
import os
import sys
import json
import subprocess

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def execute_tool(call):
    """Execute a tool call and return its result as a structured message, or None if the tool is unsupported."""
    args = json.loads(call.function.arguments)

    if call.function.name == "Read":
        with open(args["file_path"]) as f: 
            content = f.read()
        return {
            "role": "tool",
            "tool_call_id": call.id,
            "content": content
        }

    if call.function.name == "Write":
        with open(args["file_path"], "w") as f: 
            f.write(args["content"])
        return {
            "role": "tool",
            "tool_call_id": call.id,
            "content": "write successful"
        }
    
    if call.function.name == "Bash":
        result = subprocess.run(
            ["bash", "-c", args["command"]],
            capture_output=True,
            text=True
        )
        return {
            "role": "tool",
            "tool_call_id": call.id,
            "content": [result.stdout, result.stderr, result.returncode]
        }

    return None 


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    messages=[{"role": "user", "content": args.p}] # Initial conversation
    finish_reason = None
    message = None

    while finish_reason != "stop":
        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "Read",
                        "description": "Read and return the contents of a file",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path to the file to be read"
                                }
                            },
                            "required": ["file_path"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "Write",
                        "description": "Write content to a file",
                        "parameters": {
                            "type": "object",
                            "required": ["file_path", "content"],
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path of the file to write to"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The content to write to the file"
                                }
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "Bash",
                        "description": "Execute a shell command",
                        "parameters": {
                            "type": "object",
                            "required": ["command"],
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "The command to execute"
                                }
                            }
                        }
                    }
                }
            ]
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        message = chat.choices[0].message
        finish_reason = chat.choices[0].finish_reason
        messages.append(message)

        # Execute any requested tools
        if message.tool_calls: 
            for call in message.tool_calls:
                tool_message = execute_tool(call)
                if tool_message:
                    messages.append(tool_message)

    print(message.content)

    # Debugging
    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    main()
