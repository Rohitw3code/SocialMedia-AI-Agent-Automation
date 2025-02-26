from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

@tool
def prepare_email(context: str):
    """Prepare an email for a given context."""
    print(f"Email prepared for: {context}")

# Initialize model with tools
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, max_tokens=1000)
llm_with_tools = llm.bind_tools([prepare_email])

query = "prepare an email for a bank loan"

messages = [HumanMessage(content=query)]
response = llm_with_tools.invoke(messages)

# Extract tool calls
tool_calls = response.additional_kwargs.get("tool_calls", [])

print("Tool calls:", tool_calls)
