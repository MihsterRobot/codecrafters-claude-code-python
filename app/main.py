import argparse
import os
import sys
import json

from openai import OpenAI

from . import tools as t

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def execute_tool(call):
    """
    Executes a tool call using the registry and returns a structured tool
    message. If the tool name isn't registered, returns None.

    Earlier versions used branching (if name == "Read": ...), but the
    registry-based dispatcher makes the system scalable and avoids
    repeating logic for each tool.
    """
    args = json.loads(call.function.arguments)
    name = call.function.name
    
    handler = t.TOOL_HANDLERS.get(name)
    if handler is None: 
        return None

    result = handler(args)

    return {
        "role": "tool",
        "tool_call_id": call.id,
        "content": result
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    messages=[{"role": "user", "content": args.p}] 
    finish_reason = None
    message = None

    while finish_reason != "stop":
        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=t.get_tool_specs()
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("No choices in response")

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
