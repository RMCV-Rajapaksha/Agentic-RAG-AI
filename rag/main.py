import asyncio
import json
from src.agent.agent import run_agent_async

def main():
    """Main function that runs the async agent and outputs JSON format."""
    
    # Test the agent with RAG question
    print("=== Testing WSO2 AI Products ===")
    rag_query = "What are the AI-based products in WSO2?"
    print("Initializing Agentic RAG system...")
    
    response = asyncio.run(run_agent_async(rag_query))
    
    # Format the output as requested JSON structure
    if hasattr(response, 'answer') and hasattr(response, 'url'):
        result = {
            "answer": response.answer,
            "url": response.url
        }
    else:
        # Fallback
        result = {
            "answer": str(response),
            "url": []
        }
    
    print("\nWSO2 Knowledge Assistant's response:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()