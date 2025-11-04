"""
Vector Database Query Tool for Agentic RAG System

This module provides functionality to query a vector database for similar
text chunks using Azure AI embeddings and format results for the AI agent.
"""

import re
from typing import List

from llama_index.core.tools import FunctionTool
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential

from database.db import DatabaseConnection
from config import config


# ============================================================================
# Constants
# ============================================================================

# Regex pattern to extract YouTube timestamps like [123.45s]
TIMESTAMP_PATTERN = r"\[(\d+\.?\d*)s\]"

# Azure AI Foundry configuration
AZURE_ENDPOINT = config.get_azure_endpoint_embedding()
AZURE_API_KEY = config.get_azure_api_key_embedding()
DEPLOYMENT_NAME = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
SIMILARITY_TOP_K = 10


# ============================================================================
# Azure Embedding Wrapper
# ============================================================================

class AzureAIEmbedding:
    """
    Wrapper for Azure AI Foundry embeddings to work with llama_index.
    
    This class provides a compatible interface for Azure AI embeddings
    that can be used with LlamaIndex's vector store queries.
    
    Attributes:
        client: Azure EmbeddingsClient instance
        embed_dim: Dimension of embedding vectors
        deployment: Azure deployment name
    """
    
    def __init__(self, endpoint: str, api_key: str, deployment: str, embed_dim: int = EMBEDDING_DIMENSION):
        """
        Initialize Azure AI embedding client.
        
        Args:
            endpoint: Azure AI endpoint URL
            api_key: Azure API key for authentication
            deployment: Name of the deployment
            embed_dim: Embedding dimension (default: 1536)
        """
        self.client = EmbeddingsClient(
            endpoint=f"{endpoint}openai/deployments/{deployment}",
            credential=AzureKeyCredential(api_key)
        )
        self.embed_dim = embed_dim
        self.deployment = deployment
    
    def get_text_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        response = self.client.embed(input=[text])
        return response.data[0].embedding
    
    def get_query_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a query text (required by llama_index).
        
        Args:
            text: Query text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        return self.get_text_embedding(text)
    
    def get_text_embedding_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        response = self.client.embed(input=texts)
        return [item.embedding for item in response.data]


# ============================================================================
# Query Function
# ============================================================================

def get_chunks(query_text: str) -> str:
    """
    Search vector database for text chunks similar to the input query.
    
    This function embeds the query text using Azure AI embeddings and searches
    the vector database for the most similar chunks. Results are formatted
    with metadata including source, title, URL, and content.
    
    Args:
        query_text: The user's query text to search for
        
    Returns:
        Formatted string containing top relevant chunks with metadata,
        or error message if no results found or error occurs
    """
    print(f"Tool 'get_chunks' called with query: '{query_text}'")

    if not query_text:
        return "Error: A query text must be provided."

    try:
        # Initialize database connection and embedding model
        db_connection = DatabaseConnection()
        
        embed_model = AzureAIEmbedding(
            endpoint=AZURE_ENDPOINT,
            api_key=AZURE_API_KEY,
            deployment=DEPLOYMENT_NAME,
            embed_dim=EMBEDDING_DIMENSION
        )

        # Query vector database
        results = db_connection.query_vector_store(
            query_text=query_text,
            embed_model=embed_model,
            similarity_top_k=SIMILARITY_TOP_K,
        )

        if not results:
            return f"No relevant text chunks found for the query: '{query_text}'"

        # Format results
        formatted_output = f"Found {len(results)} relevant chunks for '{query_text}':\n\n"

        for i, res in enumerate(results):
            # Extract content and metadata
            content = res.node.get_content().strip().replace('\n', ' ')
            source = res.node.metadata.get('source', 'N/A')
            title = res.node.metadata.get('title', 'N/A')
            url = res.node.metadata.get('url', 'N/A')

            # Add timestamp to YouTube URLs if applicable
            youtube_timestamps = re.findall(TIMESTAMP_PATTERN, content)
            if source == "youtube_transcript" and youtube_timestamps:
                url = f"{url}&t={int(float(youtube_timestamps[0]))}s"

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


# ============================================================================
# LlamaIndex Tool Configuration
# ============================================================================

get_chunks_tool = FunctionTool.from_defaults(
    fn=get_chunks,
    name="get_similar_text_chunks",
    description=(
        "Use this tool to search the knowledge base for information to answer a user's query. "
        "It queries a vector database and returns a single formatted string containing the most relevant text chunks. "
        "Each chunk explicitly includes its content, source, URL, and title, which you can use to formulate your answer."
    )
)