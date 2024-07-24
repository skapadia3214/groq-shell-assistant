import json
import os
import argparse
from functools import partial

from groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.theme import Theme
from dotenv import load_dotenv; load_dotenv()

from tools import TOOL_MANAGER
# Define Groq colors
groq_theme = Theme({
    "info": "bold #F55036",
    "warning": "yellow",
    "danger": "bold red",
    "user": "bold white",
    "ai": "#F55036",
    "tool": "blue",
})

client = Groq()
DEFAULT_MODEL = 'llama-3.1-70b-versatile'
SYSTEM_PROMPT = f"""
You are Groq Shell. An AI assistant embedded in the user's terminal, acting as a personal shell assistant. 
Your primary goal is to assist the user with various tasks using the tools provided to you. 
Always strive to be concise, precise, accurate, and to the point in your responses.

Here are the tools you have access to:
{TOOL_MANAGER.get_tools_list_formatted()}

Guidelines for interaction:
1. Always quietly think carefully before responding to ensure you provide the most accurate answers possible.
2. Use only the tools listed above. Do not assume you have access to any other capabilities.
3. If a task cannot be completed with the available tools, explain why and suggest alternatives if possible.
4. When using the shell_command tool, utilize the input_str parameter for commands that require user input. \
This is particularly useful for interactive processes or scripts that prompt for more  information.

Remember to use these tools effectively to assist the user with their tasks and make sure you use the correct format when calling tools.\
"""

console = Console(theme=groq_theme)

def query_agent(
    query: str,
    model: str,
    messages: list[dict],
    max_cycles: int = 20,
) -> str:
    messages.append({
        'role': 'user',
        'content': query
    })
    for _ in range(max_cycles):
        with console.status("[info]Hmm...", spinner="dots"):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOL_MANAGER.get_tool_configs(),
                tool_choice="auto",
            )

        response_message = response.choices[0].message
        messages.append(response_message)

        tool_calls = response_message.tool_calls
        if not tool_calls:
            return response_message.content

        console.print(Panel("[tool]Calling tool(s)", expand=False))
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function_response = TOOL_MANAGER.call_tool(function_name, function_args)
            console.print(f"[tool]Function:[/tool] {function_name}")
            console.print(Syntax(function_response, "python", theme="monokai", line_numbers=True))
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

def main(
    model: str, 
    messages: list[dict], 
    current_dir: str
):
    if current_dir != os.getcwd():
        from tools import shell_tool, shell_command
        new_shell_command = partial(shell_command, working_dir=current_dir)
        shell_tool.func = new_shell_command
        TOOL_MANAGER.add_tool(shell_tool)

    os.chdir(current_dir)
    console.clear()
    console.print(Panel.fit(
        f"[info]Groq-Shell Assistant[/info]\nModel: {model}\nTools: {TOOL_MANAGER.get_tools_list_formatted()}",
        border_style="info"
    ))

    while True:
        user_input = Prompt.ask("\n[user]You")
        ai_output = query_agent(user_input, model, messages)
        console.print(Panel(Markdown(ai_output), title="[ai]Groq Shell", border_style="ai", expand=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Groq-powered AI Assistant")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Groq powered Model to use")
    parser.add_argument("--messages", type=json.loads, default=None, help="Initial messages in JSON format")
    parser.add_argument("--current_dir", type=str, default=os.getcwd(), help="Current working directory")
    
    args = parser.parse_args()
    
    initial_messages = args.messages if args.messages is not None else [{"role": "system", "content": SYSTEM_PROMPT}]
    
    main(args.model, initial_messages, args.current_dir)