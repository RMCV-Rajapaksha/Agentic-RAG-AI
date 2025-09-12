from llama_index.core.agent import FunctionAgent
from llama_index.llms.openai import OpenAI

# Import the tool you just created
from .tools.get_similar_text_chunk import get_chunks_tool

# Initialize the LLM
llm = OpenAI(model="gpt-4o")

# Create the agent using direct constructor
agent = FunctionAgent(tools=[get_chunks_tool], llm=llm, verbose=True)

# Now you can ask the agent questions that require it to use the tool
