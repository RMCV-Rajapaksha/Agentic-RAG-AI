"""
Azure AI Embedding Module

This module provides a wrapper for Azure AI Foundry embeddings to work with LlamaIndex.
"""

# Third-party imports
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential
from pydantic import PrivateAttr

# LlamaIndex imports
from llama_index.core.embeddings import BaseEmbedding


# ===============================
# Custom Embedding Class
# ===============================
class AzureAIEmbedding(BaseEmbedding):
    """
    Wrapper for Azure AI Foundry embeddings to work with LlamaIndex.
    
    This class adapts the Azure AI Foundry embeddings API to be compatible
    with LlamaIndex's BaseEmbedding interface.
    
    Attributes:
        _endpoint (str): Azure AI endpoint URL
        _api_key (str): Azure API key for authentication
        _deployment (str): Deployment name for the embedding model
        _embed_dim (int): Dimension of the embedding vectors
        _client (EmbeddingsClient): Azure embeddings client instance
    """
    
    _endpoint: str = PrivateAttr()
    _api_key: str = PrivateAttr()
    _deployment: str = PrivateAttr()
    _embed_dim: int = PrivateAttr(default=1536)
    _client: EmbeddingsClient = PrivateAttr()
    
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
        self._endpoint = endpoint
        self._api_key = api_key
        self._deployment = deployment
        self._embed_dim = embed_dim
        self._client = EmbeddingsClient(
            endpoint=f"{endpoint}openai/deployments/{deployment}",
            credential=AzureKeyCredential(api_key)
        )
    
    @property
    def embed_dim(self) -> int:
        """Return the embedding dimension."""
        return self._embed_dim
    
    def _get_query_embedding(self, query: str) -> list[float]:
        """
        Get embedding for a query text (required by LlamaIndex).
        
        Args:
            query: Query text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        response = self._client.embed(input=[query])
        return response.data[0].embedding
    
    def _get_text_embedding(self, text: str) -> list[float]:
        """
        Get embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        response = self._client.embed(input=[text])
        return response.data[0].embedding
    
    async def _aget_query_embedding(self, query: str) -> list[float]:
        """
        Async version of get_query_embedding.
        
        Args:
            query: Query text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        return self._get_query_embedding(query)
    
    def _get_text_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        response = self._client.embed(input=texts)
        return [item.embedding for item in response.data]
