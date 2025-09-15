# from llama_index.core.agent import FunctionAgent
from llama_index.llms.openai import OpenAI
import os

# # Import the tool you just created
# from .tools.get_similar_text_chunk import get_chunks_tool
from config.config import get_config

config = get_config()
os.environ["OPENAI_API_KEY"] = config.openai_api_key
llm = OpenAI(model="gpt-4o")


# # Create the agent using direct constructor
# agent = FunctionAgent(tools=[get_chunks_tool], llm=llm, verbose=True)

# # Now you can ask the agent questions that require it to use the tool

def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b


from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context


agent = ReActAgent(tools=[multiply, add], llm=llm)

# Create a context to store the conversation history/session state
ctx = Context(agent)


from llama_index.core.agent.workflow import AgentStream, ToolCallResult

handler = agent.run("What is 20+(2*4)?", ctx=ctx)

async for ev in handler.stream_events():
    # if isinstance(ev, ToolCallResult):
    #     print(f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}")
    if isinstance(ev, AgentStream):
        print(f"{ev.delta}", end="", flush=True)

response = await handler


print(str(response))
