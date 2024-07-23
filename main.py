import json
import os
import subprocess
import shutil

from groq import Groq
from tavily import TavilyClient

from tools import TOOL_MANAGER, Tool

client = Groq()
# MODEL = 'llama3-groq-70b-8192-tool-use-preview'
# llama-3.1-8b-instant
# llama-3.1-70b-versatile
# llama-3.1-405b-reasoning
MODEL = 'llama-3.1-70b-versatile'

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
        description="Execute a shell command on the user's computer",
        parameters={
            "command": {
                "type": "string",
                "description": "The shell command to execute on a MacOS system.",
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

TOOL_MANAGER.add_tool(
    Tool(
        name="copy_file",
        func=copy_file,
        description="Copy a file from source to destination on the user's computer. Root dir is the current working dir",
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
        description="Delete a file on the user's computer. Root dir is the current working dir",
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
        description="Search for files in a directory on the user's computer. Root dir is the current working dir",
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
        description="List contents of a directory on the user's computer. Root dir is the current working dir",
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
        description="Move a file from source to destination on the user's computer. Root dir is the current working dir",
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
        description="Read the contents of a file on the user's computer. Root dir is the current working dir",
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
        description="Write content to a file on the user's computer. Root dir is the current working dir",
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
        description="Perform a web search query for up to date information.",
        parameters={
            "query": {
                "type": "string",
                "description": "The search query",
            }
        },
    )
)

def run_conversation(user_prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": """\
You are personal assistant that helps the user with ALL tasks. \
GUIDELINES:
- Refer to only the tools given to you to respond and perform any tasks. \
- do NOT make up tools and ONLY use the tools provided to you.\
- If a tool fails, errors will be given to you. Always debug and try to fix the errors.\
"""
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_MANAGER.get_tool_configs(),
            tool_choice="auto",
            temperature=0.2,
        )

        response_message = response.choices[0].message
        messages.append(response_message)

        tool_calls = response_message.tool_calls
        if not tool_calls:
            return response_message.content

        print("Calling tool(s)")
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function_response = TOOL_MANAGER.call_tool(function_name, function_args)
            print(f"Function name: {function_name}: {function_response}")
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

        # Add a user message to prompt for continuation
        messages.append({
            "role": "user",
            "content": "Continue the task if not completed."
        })

if __name__ == "__main__":
#     user_prompt = """\
# Can you create a report about this system that includes the current date, hostname, and username.\
# Save it in a file named computer_report.txt in my current directory.\
# """

    # user_prompt = """\
    # Create a file called 'countdown.txt' with numbers from 10 to 1, each on a new line. \
    # Then, use a shell command to reverse the order of lines in this file. \
    # Finally, read the contents of the reversed file.\
    # """

    user_prompt = """\
Create a report about the contents in my current working dir. List all files, their sizes, and creation dates. \
Then, find the largest file and tell me the name of the file. \
Finally, save this report as 'report.txt' in the same directory.\
You have the ability to perform all these tasks.\
"""

    print(run_conversation(user_prompt))