from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=".env")
print("GROQ key:", os.getenv("GROQ_API_KEY"))
import subprocess
import smtplib
import json
from langchain.tools import tool
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Annotated, TypedDict
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY", "")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")


class AgentState(TypedDict):
    messages: list


llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)


@tool
def google_search(query: str) -> str:
    """Search Google for information."""
    search = TavilySearchResults(max_results=5)
    results = search.invoke({"query":query})

    if not results:
        return "No results found."
    
    formatted = []
    for r in results:
        formatted.append(f"Title: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\nContent: {r.get('content', 'N/A')[:300]}...\n")
    return "\n".join(formatted)


@tool
def send_email(to_email: str, subject: str, body: str) -> str:
    """Send an email. Requires SMTP config in environment variables."""
    smtp_server = os.getenv("SMTP_SERVER", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    if not smtp_server or not smtp_user:
        return "Email not configured. Set SMTP_SERVER, SMTP_USER, SMTP_PASSWORD env vars."
    
    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return f"Email sent to {to_email}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"


@tool
def read_file(path: str) -> str:
    """Read a file from the filesystem."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File written successfully to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"



@tool
def list_files(path: str = ".") -> str:
    """List files in a directory."""
    try:
        files = os.listdir(path)
        return "\n".join(files) if files else "Directory is empty"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def run_command(command: str) -> str:
    """Run a system command. Use with caution - only safe commands."""
    dangerous = ["rm -rf", "del /", "format", "shutdown", "reboot"]
    if any(d in command.lower() for d in dangerous):
        return "Command blocked for safety"
    
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout or result.stderr
        return output if output else "Command executed successfully (no output)"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_current_time() -> str:
    """Get current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


tools = [
    google_search,
    send_email,
    read_file,
    write_file,
    list_files,
    run_command,
    get_current_time,
    
    
]

tool_map = {t.name: t for t in tools}
tool_node = ToolNode(tools)

llm_with_tools = llm.bind_tools(tools)


def should_continue(state: AgentState) -> str:
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "continue"
    return "end"


def call_model(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def call_tool(state: AgentState):
    last_msg = state["messages"][-1]
    tool_name = last_msg.tool_calls[0]["name"]
    tool_args = last_msg.tool_calls[0]["args"]
    
    if tool_name in tool_map:
        result = tool_map[tool_name].invoke(tool_args)
        print(result)
    else:
        result = f"Unknown tool: {tool_name}"
    
    return {"messages": [{"role": "tool", "content": str(result), "tool_call_id": last_msg.tool_calls[0]["id"]}]}


graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("action", call_tool)
graph.add_edge("__start__", "agent")
graph.add_conditional_edges("agent", should_continue, {"continue": "action", "end": END})
graph.add_edge("action", "agent")

agent = graph.compile()


def run_agent(query: str):
    print(f"\n🤖 Processing: {query}\n")
    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    final_msg = result["messages"][-1]
    
    if hasattr(final_msg, "content"):
        print(f"📌 Result: {final_msg.content}")
        return final_msg.content
    return str(result)


def main():
    print("=" * 50)
    print("🤖 AI Agent - Google Search & Task Automation")
    print("=" * 50)
    print("\nAvailable commands:")
    print("- Type your request naturally")
    print("- Example: 'Search for Python tutorials'")
    print("- Example: 'Write hello world to test.txt'")
    print("- Example: 'List files in Downloads'")
    print("- Type 'exit' to quit\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not user_input:
                continue
            run_agent(user_input)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
