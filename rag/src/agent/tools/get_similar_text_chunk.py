from llama_index.core.tools import FunctionTool
from llama_index.embeddings.openai import OpenAIEmbedding


from database.db import DatabaseConnection
from config.config import get_config 
import os


config = get_config()

def get_chunks(query_text: str) -> str:
    """
    Searches a vector database for text chunks similar to the input query.
    Returns the top 7 most relevant chunks as a formatted string.
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
            similarity_top_k=4,  
        )

       
        if not results:
            return f"No relevant text chunks found for the query: '{query_text}'"

        formatted_output = f"Found {len(results)} relevant chunks for '{query_text}':\n\n"
        
        for i, res in enumerate(results):
            content = res.node.get_content().strip().replace('\n', ' ')
            source = res.node.metadata.get('source_name', 'N/A')
            url = res.node.metadata.get('url', 'N/A')
            title = res.node.metadata.get('title', 'N/A')
            start_time = res.node.metadata.get('start_seconds', 'N/A')
            end_time = res.node.metadata.get('end_seconds', 'N/A')
            source = res.node.metadata.get('source', 'N/A')


            formatted_output += f"--- Chunk {i + 1} ---\n"
            formatted_output += f"Title: {title}\n"
            if source == "youtube_transcript":
                url = f"{url}&t={start_time}s"
            
            formatted_output += f"Source: {source}\n"
            formatted_output += f"URL: {url}\n"
            formatted_output += f"Content: {content}\n\n"


        print(formatted_output)    
        return formatted_output.strip()

    except Exception as e:
        
        print(f"Error in get_chunks tool: {e}")
        return f"An error occurred while trying to retrieve text chunks: {e}"



get_chunks_tool = FunctionTool.from_defaults(
    fn=get_chunks,
    name="get_similar_text_chunks", 
    description=(
    "Use this tool to search the knowledge base for information to answer a user's query. "
    "It queries a vector database and returns a single formatted string containing the most relevant text chunks. "
    "Each chunk explicitly includes its content, source, URL, and title, which you can use to formulate your answer."
)
)