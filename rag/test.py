from src.agent.tools.get_similar_text_chunk import get_chunks, get_chunks_tool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if Azure API key is set
if not os.getenv("AZURE_API_KEY"):
    print("Warning: AZURE_API_KEY environment variable is not set!")
    print("Please set it before running this test.")
else:
    print("Azure API key found ✓")

def test_get_chunks():
    """Test the get_chunks function with a sample query"""
    print("\n" + "="*80)
    print("Testing get_chunks function")
    print("="*80 + "\n")
    
    # Test query
    test_query = "What is machine learning?"
    
    print(f"Query: {test_query}\n")
    print("-"*80 + "\n")
    
    # Call the function
    result = get_chunks(test_query)
    
    # Print results
    print(result)
    print("\n" + "="*80)
    print("Test completed")
    print("="*80)

def test_get_chunks_tool():
    """Test the FunctionTool wrapper"""
    print("\n" + "="*80)
    print("Testing get_chunks_tool (FunctionTool)")
    print("="*80 + "\n")
    
    # Test query
    test_query = "Explain neural networks"
    
    print(f"Query: {test_query}\n")
    print("-"*80 + "\n")
    
    # Call the tool
    result = get_chunks_tool.fn(test_query)
    
    # Print results
    print(result)
    print("\n" + "="*80)
    print("Test completed")
    print("="*80)

if __name__ == "__main__":
    # You can modify the test query here
    print("\n🚀 Starting tests...\n")
    
    # Run both tests
    test_get_chunks()
    print("\n\n")
    test_get_chunks_tool()
    
    print("\n✅ All tests completed!\n")
