"""
Azure AI Embedding Module

This module provides a streamlined wrapper for Azure AI Foundry embeddings to work with LlamaIndex.
Optimized to reduce redundancy and improve performance.
"""

# Third-party imports
from typing import List
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential
from pydantic import PrivateAttr

# LlamaIndex imports
from llama_index.core.embeddings import BaseEmbedding


# ===============================
# LlamaIndex-Compatible Wrapper Class
# ===============================

class AzureAIEmbedding(BaseEmbedding):
    """
    Optimized wrapper for Azure AI Foundry embeddings to work with LlamaIndex.
    
    This class provides a clean interface for generating embeddings using Azure AI,
    with both single and batch processing capabilities.
    
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
        self._client = self._create_client(endpoint, api_key, deployment)
    
    @staticmethod
    def _create_client(endpoint: str, api_key: str, deployment: str) -> EmbeddingsClient:
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
    
    @property
    def embed_dim(self) -> int:
        """Return the embedding dimension."""
        return self._embed_dim
    
    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Core method to generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        response = self._client.embed(input=texts)
        return [item.embedding for item in response.data]
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """
        Get embedding for a query text (required by LlamaIndex).
        
        Args:
            query: Query text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        return self._embed_texts([query])[0]
    
    def _get_text_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        return self._embed_texts([text])[0]
    
    async def _aget_query_embedding(self, query: str) -> List[float]:
        """
        Async version of get_query_embedding.
        For now, calls the sync version as Azure AI client doesn't provide async methods.
        
        Args:
            query: Query text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        return self._get_query_embedding(query)
    
    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return self._embed_texts(texts)
