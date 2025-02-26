from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
import json

@tool
def prepare_email(context: str):
    """Always call this tool when a user ask to write something may be Email , any Topic or content"""
    print(f"📧 Email prepared for: {context}")
    return f"Generated email content for: {context}"


# Initialize model and enforce tool use
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, max_tokens=1000)

# Bind tools to model and force tool usage
llm_with_tools = llm.bind_tools([prepare_email])

# System message that *forces* tool usage
system_message = SystemMessage(
    content="You are an AI that must use the provided tools that best fit for the user query"
)

query = """write an email for a data scientist position at Accenture company based on my resume"""

messages = [system_message, HumanMessage(content=query)]
response = llm_with_tools.invoke(messages, tool_choice="auto")  # Ensures tools are chosen

# Extract tool calls
tool_calls = response.additional_kwargs.get("tool_calls", [])

print("tool_calls : ",tool_calls)

