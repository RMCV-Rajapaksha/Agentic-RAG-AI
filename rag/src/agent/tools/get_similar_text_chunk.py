from llama_index.core.tools import FunctionTool
from llama_index.embeddings.openai import OpenAIEmbedding
import re
from database.db import DatabaseConnection
from config.config import get_config
import os

# Load configuration
config = get_config()

# Regex pattern to extract YouTube timestamps like [123.45s]
timestamp_pattern = r"\[(\d+\.?\d*)s\]"


def get_chunks(query_text: str) -> str:
    """
    Searches a vector database for text chunks similar to the input query.
    Returns the top 7 most relevant chunks as a formatted string.
    """
    print(f"Tool 'get_chunks' called with query: '{query_text}'")

    if not query_text:
        return "Error: A query text must be provided."

    try:
        # Initialize database connection and embedding model
        db_connection = DatabaseConnection()
        embed_model = OpenAIEmbedding()

        # Query vector database
        results = db_connection.query_vector_store(
            query_text=query_text,
            embed_model=embed_model,
            similarity_top_k=10,
        )

        if not results:
            return f"No relevant text chunks found for the query: '{query_text}'"

        formatted_output = f"Found {len(results)} relevant chunks for '{query_text}':\n\n"

        for i, res in enumerate(results):
            # Extract content and metadata
            content = res.node.get_content().strip().replace('\n', ' ')
            source = res.node.metadata.get('source', 'N/A')
            title = res.node.metadata.get('title', 'N/A')
            url = res.node.metadata.get('url', 'N/A')

            # Extract timestamps if present
            youtube_time_stamps = re.findall(timestamp_pattern, content)
            if source == "youtube_transcript" and youtube_time_stamps:
                url = f"{url}&t={int(float(youtube_time_stamps[0]))}s"

            # Build formatted chunk
            formatted_output += f"--- Chunk {i + 1} ---\n"
            formatted_output += f"Title: {title}\n"
            formatted_output += f"Source: {source}\n"
            formatted_output += f"URL: {url}\n"
            formatted_output += f"Content: {content}\n\n"

        
        return formatted_output.strip()

    except Exception as e:
        print(f"Error in get_chunks tool: {e}")
        return f"An error occurred while trying to retrieve text chunks: {e}"


# Create FunctionTool for llama_index
get_chunks_tool = FunctionTool.from_defaults(
    fn=get_chunks,
    name="get_similar_text_chunks",
    description=(
        "Use this tool to search the knowledge base for information to answer a user's query. "
        "It queries a vector database and returns a single formatted string containing the most relevant text chunks. "
        "Each chunk explicitly includes its content, source, URL, and title, which you can use to formulate your answer."
    )
)
