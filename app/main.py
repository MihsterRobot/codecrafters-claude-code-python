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

    messages_list = []
    tool_requested = True
    i = 0

    # Iterate until the model responds without requesting any tools
    while tool_requested: 
        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=[{"role": "user", "content": args.p}],
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
    
        # Get and store the message
        message = chat.choices[i].message 
        messages_list.append(message) 
        i += 1

        # Check if the model requested to use any tools
        if message.tool_calls:
            for call in message.tool_calls: 
                args = json.loads(call.function.arguments)
                if call.function.name == "Read":
                    with open(args["file_path"]) as f:
                        messages_list.append(f)
        else:
            tool_requested = False
            print(message.content)
            

    # Debugging
    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    main()
