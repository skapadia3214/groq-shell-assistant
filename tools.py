from typing import Dict, Any, Callable, List, Optional
import json
import os
import subprocess
import platform
import shutil

class Tool:
    def __init__(
        self, 
        name: str, 
        func: Callable, 
        description: str, 
        parameters: Dict[str, Any],
        required: Optional[List[str]] = None
    ):
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters
        if required:
            for key in required:
                assert key in list(self.parameters.keys()), f"{key} param does not exist."
        else:
            required = list(self.parameters.keys())
        self.required = required

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required,
                },
            },
        }

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def add_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_tool_configs(self) -> List[Dict[str, Any]]:
        return [tool.to_dict() for tool in self.tools.values()]
    
    def get_tools_list_formatted(self) -> str:
        return "\n".join([f"{tool.name} - {tool.description}" for tool in TOOL_MANAGER.tools.values()])

    def call_tool(self, name: str, args: Dict[str, Any]) -> str:
        if name not in self.tools:
            return json.dumps({"error": f"Tool {name} not found"})
        return self.tools[name].func(**args)

TOOL_MANAGER = ToolManager()

# Tools
def shell_command(
        command: str, 
        timeout: str = "60", 
        working_dir: str = None, 
        input_str: str = None
    ) -> str:
    timeout = float(timeout)

    command_parts = command.split()

    # Set working directory, default to current if not specified
    working_dir = working_dir or os.getcwd()

    try:
        process = subprocess.Popen(command_parts, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_dir)
        
        try:
            output, error = process.communicate(input=input_str.encode() if input_str else None, timeout=timeout)
            return json.dumps({
                "stdout": output.decode(),
                "stderr": error.decode(),
                "returncode": process.returncode
            })
        except subprocess.TimeoutExpired:
            process.kill()
            output, error = process.communicate()
            return json.dumps({
                "stdout": output.decode(),
                "stderr": error.decode(),
                "returncode": process.returncode,
                "error": "Command execution timed out"
            })
        
    except Exception as e:
        return json.dumps({"error": str(e)})

shell_tool = Tool(
    name="shell_command",
    func=shell_command,
    description=f"Execute a shell command on a {platform.system()} terminal. The shell command executes from the current working directory.",
    parameters={
        "command": {
            "type": "string",
            "description": "The shell command to execute.",
        },
        "timeout": {
            "type": "string",
            "description": "Maximum amount of time (in seconds) that the command is allowed to run. Defaults to 60."
        },
        "input_str": {
            "type": "string",
            "description": "Input string to be passed to the command's standard input. Use this for commands that require input. When multiple input is required, seperate it by adding a newline character"
        }
    },
    required=['command']
)
TOOL_MANAGER.add_tool(shell_tool)

# File Operation Tools
def copy_file(source: str, destination: str) -> str:
    try:
        shutil.copy2(source, destination)
        return json.dumps({"result": f"File copied from {source} to {destination}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

def delete_file(path: str) -> str:
    try:
        os.remove(path)
        return json.dumps({"result": f"File {path} deleted"})
    except Exception as e:
        return json.dumps({"error": str(e)})

def file_search(directory: str, pattern: str) -> str:
    try:
        results = [f for f in os.listdir(directory) if f.startswith(pattern)]
        return json.dumps({"result": results})
    except Exception as e:
        return json.dumps({"error": str(e)})

def list_directory(path: str) -> str:
    try:
        results = os.listdir(path)
        return json.dumps({"result": results})
    except Exception as e:
        return json.dumps({"error": str(e)})

def move_file(source: str, destination: str) -> str:
    try:
        shutil.move(source, destination)
        return json.dumps({"result": f"File moved from {source} to {destination}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

def read_file(path: str) -> str:
    try:
        with open(path, 'r') as file:
            content = file.read()
        return json.dumps({"result": content})
    except Exception as e:
        return json.dumps({"error": str(e)})

def write_file(path: str, content: str) -> str:
    try:
        with open(path, 'w') as file:
            file.write(content)
        return json.dumps({"result": f"Content written to {path}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

# Add each file operation as a separate tool
# TOOL_MANAGER.add_tool(
#     Tool(
#         name="copy_file",
#         func=copy_file,
#         description="Copy a file from source to destination",
#         parameters={
#             "source": {
#                 "type": "string",
#                 "description": "The source file path",
#             },
#             "destination": {
#                 "type": "string",
#                 "description": "The destination file path",
#             }
#         },
#     )
# )

# TOOL_MANAGER.add_tool(
#     Tool(
#         name="delete_file",
#         func=delete_file,
#         description="Delete a file",
#         parameters={
#             "path": {
#                 "type": "string",
#                 "description": "The path of the file to delete",
#             }
#         },
#     )
# )

# TOOL_MANAGER.add_tool(
#     Tool(
#         name="file_search",
#         func=file_search,
#         description="Search for files in a directory",
#         parameters={
#             "directory": {
#                 "type": "string",
#                 "description": "The directory to search in",
#             },
#             "pattern": {
#                 "type": "string",
#                 "description": "The pattern to search for",
#             }
#         },
#     )
# )

# TOOL_MANAGER.add_tool(
#     Tool(
#         name="list_directory",
#         func=list_directory,
#         description="List contents of a directory",
#         parameters={
#             "path": {
#                 "type": "string",
#                 "description": "The path of the directory to list",
#             }
#         },
#     )
# )

# TOOL_MANAGER.add_tool(
#     Tool(
#         name="move_file",
#         func=move_file,
#         description="Move a file from source to destination",
#         parameters={
#             "source": {
#                 "type": "string",
#                 "description": "The source file path",
#             },
#             "destination": {
#                 "type": "string",
#                 "description": "The destination file path",
#             }
#         },
#     )
# )

TOOL_MANAGER.add_tool(
    Tool(
        name="read_file",
        func=read_file,
        description="Read the contents of a file",
        parameters={
            "path": {
                "type": "string",
                "description": "The path of the file to read",
            }
        },
    )
)

TOOL_MANAGER.add_tool(
    Tool(
        name="write_file",
        func=write_file,
        description="Write content to a file",
        parameters={
            "path": {
                "type": "string",
                "description": "The path of the file to write to",
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file",
            }
        },
    )
)

# Web Search
if  os.getenv("TAVILY_API_KEY"): # Only add the tool if TAVILY_API_KEY is set
    from tavily import TavilyClient
    def web_search(query: str) -> str:
        tavily_client = TavilyClient()

        response = tavily_client.qna_search(query)
        return response

    TOOL_MANAGER.add_tool(
        Tool(
            name="web_search",
            func=web_search,
            description="Perform a web search query",
            parameters={
                "query": {
                    "type": "string",
                    "description": "The search query",
                }
            },
        )
    )

# Human in the loop
# def human_input(question: str) -> str:
#     answer = input(f"\n{question}\n")
#     return answer if answer else "User did not provide an answer."

# TOOL_MANAGER.add_tool(
#     Tool(
#         name="ask_question",
#         func=human_input,
#         description="Ask the user a question to gather additional information needed to complete the task. This tool should be used when you encounter ambiguities, need clarification, or require more details to proceed effectively. It allows for interactive problem-solving by enabling direct communication with the user. Use this tool judiciously to maintain a balance between gathering necessary information and avoiding excessive back-and-forth.", # from https://github.com/saoudrizwan/claude-dev
#         parameters={
#             "question": {
#                 "type": "string",
#                 "description": "The question to ask the user. This should be a clear, specific question that addresses the information you need."
#             }
#         }
#     )
# )