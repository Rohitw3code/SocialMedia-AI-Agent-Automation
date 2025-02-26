from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain.chains.conversation.memory import ConversationSummaryMemory
import json
from functools import wraps


def HumanInvolve(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if input("Approve y/n: ") == 'y':
            res  = func(*args,**kwargs)
            return res
        return f"{func.__name__} is cancelled"
    return wrapper


@tool
def prepare_email(context: str):
    """Always call this tool when a user ask to write something may be Email , any Topic or content"""
    return f"Generated email content for: {context}"

@tool
@HumanInvolve
def email_service(email:str,email_content:str):
    """
    accept a user email , this tool is used to send email to any given mail address
    Args:
        email: the email address    
        email_content: get the email content from past context or from the given prompt only    
    """

    print("email content : ",email_content)
    print("Email sent on : ",email)

    return {"status":"successful","message":f"email successfully sent to {email}"}


# Initialize model and enforce tool use
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, max_tokens=1000)

# Bind tools to model and force tool usage
llm_with_tools = llm.bind_tools([prepare_email,email_service])

# System message that *forces* tool usage
system_message = SystemMessage(
    content="You are an AI that must use the provided tools that best fit for the user query"
)

memory = ConversationSummaryMemory(llm=llm)

FUNCTION_MAP = {
    'prepare_email':prepare_email,
    'email_service':email_service
}

tool_responses = []

while True:
    query = str(input("query : "))

    history = memory.load_memory_variables({})['history']
    messages = []
    if history:
        messages.append(SystemMessage(content=f"""You are an AI that must use the provided tools that best fit for the user query\n 
                                      Past Conversation context: {history}"""))
    messages.append(HumanMessage(content=query))


    response = llm_with_tools.invoke(messages, tool_choice="auto") 
    tool_calls = response.additional_kwargs.get("tool_calls", [])
    for _function in tool_calls:
        function = _function['function']
        print("tool_calls : ",function)
        func_name = function['name']
        args = json.loads(function['arguments'])
        result = FUNCTION_MAP[func_name].invoke(input=args)
        print("result : ", result)
        tool_responses.append(f"tool: {func_name}\nAI: {result}")

    final_response = "\n".join(tool_responses) if tool_responses else response.content
    memory.save_context({"input": query}, {"output": final_response})
