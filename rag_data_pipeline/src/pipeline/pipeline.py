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
from sqlalchemy import make_url


from llama_index.core import Document
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.vector_stores.postgres import PGVectorStore

from database.db import DatabaseConnection
from src.embeddings.azure_embedding import AzureAIEmbedding
from config.exceptions import EmbeddingGenerationError

from config.constants import (
    EMBEDDING_DEPLOYMENT_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
   
)


from config.constants import (
    HNSW_M,
    HNSW_EF_CONSTRUCTION,
    HNSW_EF_SEARCH,
    HNSW_DISTANCE_METHOD,
    EMBEDDING_DIMENSION,

)

# Configure logger
logger = logging.getLogger(__name__)

load_dotenv()


# --- Global Components (Reusable) ---

AZURE_ENDPOINT_EMBEDDING = os.getenv('AZURE_ENDPOINT_EMBEDDING')
AZURE_API_KEY_EMBEDDING = os.getenv('AZURE_API_KEY_EMBEDDING')
DB_NAME = os.getenv('DB_NAME')
CONNECTION_STRING = os.getenv('CONNECTION_STRING')
DB_TABLE_NAME = os.getenv('DB_TABLE_NAME')




EMBEDDING_MODEL = AzureAIEmbedding(
        endpoint=AZURE_ENDPOINT_EMBEDDING,
        api_key=AZURE_API_KEY_EMBEDDING,
        deployment=EMBEDDING_DEPLOYMENT_NAME,
        embed_dim=1536
    )

url = make_url(CONNECTION_STRING)

VECTOR_STORE = PGVectorStore.from_params(
                database=DB_NAME,
                host=url.host,
                password=url.password,
                port=url.port,
                user=url.username,
                table_name=DB_TABLE_NAME,
                embed_dim=EMBEDDING_DIMENSION,
                hnsw_kwargs={
                    "hnsw_m": HNSW_M,
                    "hnsw_ef_construction": HNSW_EF_CONSTRUCTION,
                    "hnsw_ef_search": HNSW_EF_SEARCH,
                    "hnsw_dist_method": HNSW_DISTANCE_METHOD,
                },
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
            vector_store=VECTOR_STORE # Use the freshly created vector store
        )

        logger.info(f"Ingesting {len(documents)} document(s)...")
        pipeline.run(documents=documents, show_progress=True)
        logger.info(f"Successfully ingested {len(documents)} documents")
        
    except Exception as e:
        error_msg = f"Document ingestion failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise EmbeddingGenerationError(error_msg)