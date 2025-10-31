"""
Database Connection Module

This module handles database connections and vector store initialization
for the RAG data ingestion pipeline using PostgreSQL with pgvector.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from sqlalchemy import make_url, create_engine

# LlamaIndex imports
from llama_index.vector_stores.postgres import PGVectorStore

# Local imports
from config.config import (
    get_db_connection_string,
    get_db_name,
    get_db_table_name,
)


# ===============================
# Database Connection Class
# ===============================

class DatabaseConnection:
    """
    Handle database connections and vector store initialization for data ingestion.
    
    This class manages PostgreSQL connections with pgvector extension for
    storing and retrieving document embeddings.
    
    Attributes:
        connection_string: PostgreSQL connection string
        db_name: Database name
        table_name: Table name for storing vectors
    """
    
    def __init__(self):
        """Initialize database connection parameters from configuration."""
        self.connection_string = get_db_connection_string()
        self.db_name = get_db_name()
        self.table_name = get_db_table_name()
        
    def get_vector_store(self, embed_dim: int = 1536):
        """
        Return a configured PGVectorStore instance.

        Args:
            embed_dim: Embedding dimension (default: 1536 for OpenAI embeddings)
            
        Returns:
            PGVectorStore: Configured vector store instance with HNSW indexing
        """
        url = make_url(self.connection_string)
        
        vector_store = PGVectorStore.from_params(
            database=self.db_name,
            host=url.host,
            password=url.password,
            port=url.port,
            user=url.username,
            table_name=self.table_name,
            embed_dim=embed_dim,
            hnsw_kwargs={
                "hnsw_m": 16,
                "hnsw_ef_construction": 64,
                "hnsw_ef_search": 40,
                "hnsw_dist_method": "vector_cosine_ops",
            },
        )
        
        return vector_store