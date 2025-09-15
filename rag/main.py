import asyncio
from src.agent.agent import run_agent_async

def main():
    """Main function that runs the async agent."""
    
    # Test the agent with math question
    print("=== Testing Math Capabilities ===")
    math_query = "What is 20+(2*4)?"
    print("Initializing Agentic RAG system...")
    
    response = asyncio.run(run_agent_async(math_query))
    print("\nMath Assistant's response:\n")
    print(response)
    
    print("\n" + "="*50 + "\n")
    
    # Test the agent with RAG question
    print("=== Testing RAG Capabilities ===")
    rag_query = "What are the AI-based products in WSO2? who is the head of AI in WSO2?"
    
    response = asyncio.run(run_agent_async(rag_query))
    print("\nRAG Assistant's response:\n")
    print(response)

if __name__ == "__main__":
    main()