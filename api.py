from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from functools import wraps
import uvicorn

app = FastAPI()

# Mocking the model and tools for demonstration
class ChatOpenAI:
    def bind_tools(self, tools):
        return self

    def invoke(self, messages, tool_choice="auto"):
        # Mock response
        return MockResponse(additional_kwargs={"tool_calls": []})

class MockResponse:
    def __init__(self, additional_kwargs):
        self.additional_kwargs = additional_kwargs

llm = ChatOpenAI()
llm_with_tools = llm.bind_tools([])

# Decorator for human involvement
def HumanInvolve(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Here, you would typically wait for approval from the frontend
        # For simplicity, we'll assume approval is always granted
        approval = await get_approval_from_frontend()
        if approval:
            res = func(*args, **kwargs)
            return res
        return f"{func.__name__} is cancelled"
    return wrapper

async def get_approval_from_frontend():
    # Simulate frontend approval
    return True

@app.post("/query")
async def query_endpoint(query: str):
    messages = [{"role": "user", "content": query}]
    response = llm_with_tools.invoke(messages)
    tool_calls = response.additional_kwargs.get("tool_calls", [])

    tool_responses = []
    for _function in tool_calls:
        function = _function['function']
        func_name = function['name']
        args = json.loads(function['arguments'])
        result = await FUNCTION_MAP[func_name](**args)
        tool_responses.append(f"tool: {func_name}\nAI: {result}")

    final_response = "\n".join(tool_responses) if tool_responses else response.content
    return {"response": final_response}

# Mock tools
@HumanInvolve
async def email_service(email: str, email_content: str):
    return {"status": "successful", "message": f"email successfully sent to {email}"}

FUNCTION_MAP = {
    'email_service': email_service,
}

# Run the app with `uvicorn script_name:app --reload`
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
