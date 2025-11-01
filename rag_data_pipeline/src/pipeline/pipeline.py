"""
Pipeline Module

This module handles the creation and execution of the ingestion pipeline.
It includes functions for:
- Creating embedding models
- Building ingestion pipelines with transformations
- Ingesting documents into the vector store
"""

from typing import List

from llama_index.core import Document
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser

from src.embeddings.azure_embedding import AzureAIEmbedding


def create_embedding_model(
    endpoint: str,
    api_key: str,
    deployment: str,
    embed_dim: int = 1536
) -> AzureAIEmbedding:
    """
    Create Azure AI embedding model instance.
    
    Args:
        endpoint: Azure endpoint URL
        api_key: Azure API key
        deployment: Deployment name
        embed_dim: Embedding dimension (default: 1536)
        
    Returns:
        Configured AzureAIEmbedding instance
    """
    return AzureAIEmbedding(
        endpoint=endpoint,
        api_key=api_key,
        deployment=deployment,
        embed_dim=embed_dim
    )


def create_ingestion_pipeline(
    vector_store,
    endpoint: str,
    api_key: str,
    deployment: str,
    chunk_size: int = 512,
    chunk_overlap: int = 100
) -> IngestionPipeline:
    """
    Create and return an ingestion pipeline with transformations.
    
    The pipeline includes:
    - MarkdownNodeParser for chunking documents
    - TitleExtractor for extracting titles
    - AzureAIEmbedding for generating embeddings
    
    Args:
        vector_store: Vector store instance for storing embeddings
        endpoint: Azure endpoint URL
        api_key: Azure API key
        deployment: Deployment name
        chunk_size: Size of document chunks (default: 512)
        chunk_overlap: Overlap between chunks (default: 100)
        
    Returns:
        Configured ingestion pipeline
    """
    return IngestionPipeline(
        transformations=[
            MarkdownNodeParser(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                include_metadata=True,
                include_prev_next_rel=True
            ),
            TitleExtractor(),
            create_embedding_model(endpoint, api_key, deployment)
        ],
        vector_store=vector_store,
    )


def ingest_documents(
    documents: List[Document],
    pipeline: IngestionPipeline
) -> None:
    """
    Ingest documents into the vector store using the pipeline.
    
    Args:
        documents: List of documents to ingest
        pipeline: Ingestion pipeline instance
    """
    if not documents:
        print("No documents provided for ingestion.")
        return

    print(f"\n📥 Ingesting {len(documents)} document(s)...")
    pipeline.run(documents=documents, show_progress=True)
    print("✅ Documents ingested successfully!")
