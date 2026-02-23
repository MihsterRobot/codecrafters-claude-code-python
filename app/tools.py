import subprocess

# Each tool is implemented as a simple function.
# Earlier versions used a Tool class, but that added unnecessary structure:
# every tool had only one operation and no shared state.
# Functions keep the design lightweight and easy to extend.
def read(args):
    with open(args["file_path"]) as f: 
        content = f.read()
    return content
        

def write(args):
    with open(args["file_path"], "w") as f: 
        f.write(args["content"])
    return "Write successful"
        

def bash(args):
    # We return only stdout/stderr instead of the full CompletedProcess object.
    # This keeps the tool interface clean and predictable for the model.
    result = subprocess.run(
        ["bash", "-c", args["command"]],
        capture_output=True,
        text=True
    )
    return result.stderr if result.returncode != 0 else result.stdout


# The tool specs define how the LLM sees and calls each tool.
# They are kept separate from the handlers so the logic (Python functions)
# and the interface (JSON schema) stay decoupled.
def get_tool_specs():
    return [
                {
                    "type": "function",
                    "function": {
                        "name": "Read",
                        "description": "Read and return the contents of a file",
                        "parameters": {
                            "type": "object",
                            "required": ["file_path"],
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path to the file to be read"
                                }
                            }
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


# A registry mapping tool names to handler functions.
# This replaces the earlier if/elif chain in execute_tool(),
# making the system extensible: adding a new tool is now one line here.
TOOL_HANDLERS = {
    "Read": read,
    "Write": write,
    "Bash": bash,
}
