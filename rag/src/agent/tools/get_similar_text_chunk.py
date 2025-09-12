from llama_index.core.tools import FunctionTool
from llama_index.embeddings.openai import OpenAIEmbedding


from database.db import DatabaseConnection
from config.config import get_config 
import os


config = get_config()
os.environ["OPENAI_API_KEY"] = config.openai_api_key

def get_chunks(query_text: str) -> str:
    """
    Searches a vector database for text chunks similar to the input query.
    Returns the top 3 most relevant chunks as a formatted string.
    """

    print(f"Tool 'get_chunks' called with query: '{query_text}'")
    
    if not query_text:
        return "Error: A query text must be provided."

    try:
   
        db_connection = DatabaseConnection()
        embed_model = OpenAIEmbedding()

  
        results = db_connection.query_vector_store(
            query_text=query_text,
            embed_model=embed_model,
            similarity_top_k=5,  
        )

       
        if not results:
            return f"No relevant text chunks found for the query: '{query_text}'"

        formatted_output = f"Found {len(results)} relevant chunks for '{query_text}':\n\n"
        for i, res in enumerate(results):
            content = res.node.get_content().strip().replace('\n', ' ')
            source = res.node.metadata.get('source_name', 'N/A')
            
            formatted_output += f"--- Chunk {i + 1} (Source: {source}) ---\n"
            formatted_output += f"Content: {content}\n\n"
            
        return formatted_output.strip()

    except Exception as e:
        
        print(f"Error in get_chunks tool: {e}")
        return f"An error occurred while trying to retrieve text chunks: {e}"



get_chunks_tool = FunctionTool.from_defaults(
    fn=get_chunks,
    name="get_similar_text_chunks", 
    description="Use this tool to search and retrieve relevant text chunks from the knowledge base (vector database) based on a user's query.",
)