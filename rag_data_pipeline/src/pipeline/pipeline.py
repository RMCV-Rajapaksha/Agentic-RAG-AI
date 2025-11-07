"""
Pipeline Module

This module handles the creation and execution of the ingestion pipeline.
It includes functions for:
- Creating embedding models
- Building ingestion pipelines with transformations
- Ingesting documents into the vector store
"""

import logging
from typing import List
import os

from dotenv import load_dotenv


from llama_index.core import Document
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser

from database.db import DatabaseConnection
from src.embeddings.azure_embedding import AzureAIEmbedding
from config.exceptions import EmbeddingGenerationError

from config.constants import (
    EMBEDDING_DEPLOYMENT_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
   
)


# Configure logger
logger = logging.getLogger(__name__)

load_dotenv()


# --- Global Components (Reusable) ---

AZURE_ENDPOINT_EMBEDDING = os.getenv('AZURE_ENDPOINT_EMBEDDING')
AZURE_API_KEY_EMBEDDING = os.getenv('AZURE_API_KEY_EMBEDDING')

# The embedding model can be global as it's stateless and reusable
EMBEDDING_MODEL = AzureAIEmbedding(
        endpoint=AZURE_ENDPOINT_EMBEDDING,
        api_key=AZURE_API_KEY_EMBEDDING,
        deployment=EMBEDDING_DEPLOYMENT_NAME,
        embed_dim=1536
    )



def ingest_documents(
    documents: List[Document],
) -> None:
    """
    Ingest documents into the vector store using the pipeline.
    
    Args:
        documents: List of documents to ingest
        
    Raises:
        EmbeddingGenerationError: If ingestion fails
    """
    if not documents:
        logger.warning("No documents provided for ingestion")
        return

    try:
        # --- Create DB connection and pipeline here ---
        logger.info("Connecting to database to get vector store...")
        db_connection = DatabaseConnection()
        vector_store = db_connection.get_vector_store()
        
        logger.info("Building ingestion pipeline...")
        pipeline = IngestionPipeline(
            transformations=[
                MarkdownNodeParser(
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=CHUNK_OVERLAP,
                    include_metadata=True,
                    include_prev_next_rel=True
                ),
                TitleExtractor(),
                EMBEDDING_MODEL  # Use the global embedding model
            ],
            vector_store=vector_store # Use the freshly created vector store
        )

        logger.info(f"Ingesting {len(documents)} document(s)...")
        pipeline.run(documents=documents, show_progress=True)
        logger.info(f"Successfully ingested {len(documents)} documents")
        
    except Exception as e:
        error_msg = f"Document ingestion failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise EmbeddingGenerationError(error_msg)