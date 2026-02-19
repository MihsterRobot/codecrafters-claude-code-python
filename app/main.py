import argparse
import os
import sys
import json

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    messages=[{"role": "user", "content": args.p}]

    while True:
        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=[{ 
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
            }]
        )

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        # Store the model's message
        message = chat.choices[0].message
        messages.append(message)

        # Check if the model requested any tools
        if message.tool_calls: 
            # Iterate through the tool calls
            for call in message.tool_calls:
                # Convert the JSON argument string into a Python dictionary
                args = json.loads(call.function.arguments)

                # Execute the "Read" tool by opening the specified file and reading its contents into a string
                if call.function.name == "Read": 
                    with open(args["file_path"]) as f:
                        content = f.read()

                    # Add the tool's execution result to the conversation history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": content
                    })
        else: 
            print(message.content)
            break

    # Debugging
    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    main()
