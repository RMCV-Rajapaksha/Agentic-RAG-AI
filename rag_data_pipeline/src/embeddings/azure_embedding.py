"""
Azure AI Embedding Module

This module provides functional wrappers for Azure AI Foundry embeddings to work with LlamaIndex.
"""

# Third-party imports
from typing import List, Callable
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential
from pydantic import PrivateAttr

# LlamaIndex imports
from llama_index.core.embeddings import BaseEmbedding


# ===============================
# Functional Helper Functions
# ===============================

def create_embeddings_client(
    endpoint: str,
    api_key: str,
    deployment: str
) -> EmbeddingsClient:
    """
    Create and return an Azure Embeddings Client.
    
    Args:
        endpoint: Azure AI endpoint URL
        api_key: Azure API key for authentication
        deployment: Deployment name for the embedding model
        
    Returns:
        EmbeddingsClient: Configured Azure embeddings client
    """
    return EmbeddingsClient(
        endpoint=f"{endpoint}openai/deployments/{deployment}",
        credential=AzureKeyCredential(api_key)
    )


def get_embedding(client: EmbeddingsClient, text: str) -> List[float]:
    """
    Get embedding for a single text using the provided client.
    
    Args:
        client: Azure embeddings client
        text: Text to embed
        
    Returns:
        List of floats representing the embedding vector
    """
    response = client.embed(input=[text])
    return response.data[0].embedding


def get_embeddings_batch(
    client: EmbeddingsClient,
    texts: List[str]
) -> List[List[float]]:
    """
    Get embeddings for multiple texts using the provided client.
    
    Args:
        client: Azure embeddings client
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    response = client.embed(input=texts)
    return [item.embedding for item in response.data]


# ===============================
# LlamaIndex-Compatible Wrapper Class
# ===============================

class AzureAIEmbedding(BaseEmbedding):
    """
    Wrapper for Azure AI Foundry embeddings to work with LlamaIndex.
    
    This class adapts functional Azure AI embeddings to be compatible
    with LlamaIndex's BaseEmbedding interface.
    
    Attributes:
        _client (EmbeddingsClient): Azure embeddings client instance
        _embed_dim (int): Dimension of the embedding vectors
    """
    
    _client: EmbeddingsClient = PrivateAttr()
    _embed_dim: int = PrivateAttr(default=1536)
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment: str,
        embed_dim: int = 1536,
        **kwargs
    ):
        """
        Initialize the Azure AI Embedding wrapper.
        
        Args:
            endpoint: Azure AI endpoint URL
            api_key: Azure API key for authentication
            deployment: Deployment name for the embedding model
            embed_dim: Dimension of embedding vectors (default: 1536)
            **kwargs: Additional keyword arguments for BaseEmbedding
        """
        super().__init__(**kwargs)
        self._embed_dim = embed_dim
        self._client = create_embeddings_client(endpoint, api_key, deployment)
    
    @property
    def embed_dim(self) -> int:
        """Return the embedding dimension."""
        return self._embed_dim
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """
        Get embedding for a query text (required by LlamaIndex).
        
        Args:
            query: Query text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        return get_embedding(self._client, query)
    
    def _get_text_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        return get_embedding(self._client, text)
    
    async def _aget_query_embedding(self, query: str) -> List[float]:
        """
        Async version of get_query_embedding.
        
        Args:
            query: Query text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        return get_embedding(self._client, query)
    
    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return get_embeddings_batch(self._client, texts)
