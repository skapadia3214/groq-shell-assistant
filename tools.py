import json
import os
import subprocess
import shutil
from typing import Dict, Any, Callable, List

from tavily import TavilyClient

class Tool:
    def __init__(self, name: str, func: Callable, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.func = func
        self.description = description
        self.parameters = parameters

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "id": self.name,
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": list(self.parameters.keys()),
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

    def call_tool(self, name: str, args: Dict[str, Any]) -> str:
        if name not in self.tools:
            return json.dumps({"error": f"Tool {name} not found"})
        return self.tools[name].func(**args)

TOOL_MANAGER = ToolManager()

# Tools
# Shell Tool (remains the same)
def shell_command(command: str) -> str:
    command_parts = command.split()
    try:
        result = subprocess.run(command_parts, capture_output=True, text=True, timeout=5)
        return json.dumps({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        })
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "Command execution timed out"})
    except Exception as e:
        return json.dumps({"error": str(e)})

TOOL_MANAGER.add_tool(
    Tool(
        name="shell_command",
        func=shell_command,
        description="Execute a shell command (limited to safe commands)",
        parameters={
            "command": {
                "type": "string",
                "description": "The shell command to execute",
            }
        },
    )
)

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
TOOL_MANAGER.add_tool(
    Tool(
        name="copy_file",
        func=copy_file,
        description="Copy a file from source to destination",
        parameters={
            "source": {
                "type": "string",
                "description": "The source file path",
            },
            "destination": {
                "type": "string",
                "description": "The destination file path",
            }
        },
    )
)

TOOL_MANAGER.add_tool(
    Tool(
        name="delete_file",
        func=delete_file,
        description="Delete a file",
        parameters={
            "path": {
                "type": "string",
                "description": "The path of the file to delete",
            }
        },
    )
)

TOOL_MANAGER.add_tool(
    Tool(
        name="file_search",
        func=file_search,
        description="Search for files in a directory",
        parameters={
            "directory": {
                "type": "string",
                "description": "The directory to search in",
            },
            "pattern": {
                "type": "string",
                "description": "The pattern to search for",
            }
        },
    )
)

TOOL_MANAGER.add_tool(
    Tool(
        name="list_directory",
        func=list_directory,
        description="List contents of a directory",
        parameters={
            "path": {
                "type": "string",
                "description": "The path of the directory to list",
            }
        },
    )
)

TOOL_MANAGER.add_tool(
    Tool(
        name="move_file",
        func=move_file,
        description="Move a file from source to destination",
        parameters={
            "source": {
                "type": "string",
                "description": "The source file path",
            },
            "destination": {
                "type": "string",
                "description": "The destination file path",
            }
        },
    )
)

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