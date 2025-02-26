from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain.chains.conversation.memory import ConversationSummaryMemory
import json
from functools import wraps

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailRequest(BaseModel):
    query: str

class ApprovalRequest(BaseModel):
    toolName: str
    args: Dict[str, Any]

def HumanInvolve(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Instead of asking for input, we'll return the need for approval
        return {
            "requiresApproval": True,
            "toolName": func.__name__,
            "args": kwargs
        }
    return wrapper

@tool
def prepare_email(context: str):
    """Always call this tool when a user ask to write something may be Email, any Topic or content"""
    return f"Generated email content for: {context}"

@tool
@HumanInvolve
def email_service(email: str, email_content: str):
    """Send email to any given mail address"""
    print("email content : ", email_content)
    print("Email sent on : ", email)
    return {"status": "successful", "message": f"email successfully sent to {email}"}

# Initialize LangChain components
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, max_tokens=1000)
llm_with_tools = llm.bind_tools([prepare_email, email_service])
memory = ConversationSummaryMemory(llm=llm)

FUNCTION_MAP = {
    'prepare_email': prepare_email,
    'email_service': email_service
}

@app.post("/process")
async def process_request(request: EmailRequest):
    try:
        history = memory.load_memory_variables({})['history']
        messages = []
        if history:
            messages.append(SystemMessage(content=f"""You are an AI that must use the provided tools that best fit for the user query\n 
                                          Past Conversation context: {history}"""))
        messages.append(HumanMessage(content=request.query))

        response = llm_with_tools.invoke(messages, tool_choice="auto")
        tool_calls = response.additional_kwargs.get("tool_calls", [])
        
        if not tool_calls:
            return {"requiresApproval": False, "result": response.content}

        for tool_call in tool_calls:
            function = tool_call['function']
            func_name = function['name']
            args = json.loads(function['arguments'])
            result = FUNCTION_MAP[func_name].invoke(input=args)
            
            if isinstance(result, dict) and result.get("requiresApproval"):
                return result
            
            memory.save_context({"input": request.query}, {"output": str(result)})
            return {"requiresApproval": False, "result": str(result)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/approve")
async def approve_action(request: ApprovalRequest):
    try:
        if request.toolName not in FUNCTION_MAP:
            raise HTTPException(status_code=400, detail="Invalid tool name")

        func = FUNCTION_MAP[request.toolName]
        # Remove the HumanInvolve decorator effect for actual execution
        original_func = func.__wrapped__ if hasattr(func, '__wrapped__') else func
        result = original_func.invoke(input=request.args)
        
        return {"requiresApproval": False, "result": str(result)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))