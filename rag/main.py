from src.agent.tools.get_similar_text_chunk import get_chunks_tool
from llama_index.llms.openai import OpenAI
import os
from config.config import get_config

def simple_rag_agent(query: str) -> str:
    """
    A simple RAG agent that uses the search tool and an LLM to provide answers.
    """
    # Get relevant chunks using the tool
    print(f"Searching knowledge base for: {query}")
    relevant_chunks = get_chunks_tool.fn(query)
    
    if "No relevant text chunks found" in relevant_chunks or "An error occurred" in relevant_chunks:
        return f"I couldn't find relevant information for your query: {query}"
    
    # Set up the LLM
    config = get_config()
    os.environ["OPENAI_API_KEY"] = config.openai_api_key
    llm = OpenAI(model="gpt-4o")
    
    # Create a prompt that includes the retrieved chunks
    prompt = f"""
Based on the following relevant information from the knowledge base, please answer the user's question.

Retrieved Information:
{relevant_chunks}

User Question: {query}

Please provide a comprehensive answer based on the retrieved information. If the retrieved informato the user tion doesn't fully answer the question, mention what information is available and what might be missing. and give me the all reference url and documents under the output

i want to supply source url
"""
    
    # Get response from LLM
    response = llm.complete(prompt)
    return str(response)

def main():
    """
    Main function to test the agentic RAG system.
    """
    print("Initializing Simple Agentic RAG system...")
    
    # Test the agent with a sample question
    query = "What are the ai base product in WSO2?"
    print(f"\nAsking agent: {query}")
    
    # Use our simple RAG agent
    response = simple_rag_agent(query)
    print(f"\nAgent response:\n{response}")

if __name__ == "__main__":
    main()