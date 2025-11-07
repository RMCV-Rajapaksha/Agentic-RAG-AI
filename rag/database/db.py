"""
Database Connection Module for Agentic RAG System

This module handles database connections and vector store operations
for the RAG (Retrieval-Augmented Generation) system using PostgreSQL
with pgvector extension.
"""

import logging
from typing import List

from sqlalchemy import make_url
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import NodeWithScore

from config import config


# ============================================================================
# Logging Configuration
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# Database Connection Class
# ============================================================================

class DatabaseConnection:
    """
    Handles database connections and vector store initialization.
    
    This class manages connections to a PostgreSQL database with pgvector
    extension for storing and querying vector embeddings.
    
    Attributes:
        connection_string: PostgreSQL connection string
        table_name: Name of the vector store table
        vector_store: Cached PGVectorStore instance
    """

    def __init__(self):
        """Initialize database connection with configuration."""
        self.connection_string = config.get_db_connection_string()
        self.table_name = config.get_db_table_name()
        self.vector_store = None

    def get_vector_store(self, embed_dim: int = 1536) -> PGVectorStore:
        """
        Get or create a configured PGVectorStore instance.

        Args:
            embed_dim: Embedding dimension (default: 1536 for OpenAI embeddings)

        Returns:
            Configured PGVectorStore instance
        """
        url = make_url(self.connection_string)

        vector_store = PGVectorStore.from_params(
            database=url.database,
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

    def query_vector_store(
        self,
        query_text: str,
        embed_model: BaseEmbedding,
        similarity_top_k: int = 5,
    ) -> List[NodeWithScore]:
        """
        Query the vector store to find similar text chunks.

        Args:
            query_text: The text query to search for
            embed_model: The embedding model to vectorize the query
            similarity_top_k: Number of top similar results to retrieve

        Returns:
            List of nodes with similarity scores

        Raises:
            Exception: If vector store query fails
        """
        if not query_text:
            logger.warning("Query text is empty. Returning an empty list.")
            return []

        try:
            # Initialize vector store if not already done
            if self.vector_store is None:
                logger.info("Initializing vector store...")
                self.vector_store = self.get_vector_store()

            logger.info(f"Generating embedding for query: '{query_text[:50]}...'")
            query_embedding = embed_model.get_query_embedding(query_text)

            query = VectorStoreQuery(
                query_embedding=query_embedding,
                similarity_top_k=similarity_top_k,
            )

            logger.info(f"Querying vector store for {similarity_top_k} most similar chunks.")
            result = self.vector_store.query(query)

            nodes_with_scores = []
            if result.nodes and result.similarities:
                for node, similarity in zip(result.nodes, result.similarities):
                    if hasattr(node, 'metadata') and node.metadata:
                        logger.debug(f"Node metadata: {node.metadata}")

                    nodes_with_scores.append(NodeWithScore(node=node, score=similarity))

            logger.info(f"Found {len(nodes_with_scores)} related text chunks with metadata.")
            return nodes_with_scores

        except Exception as e:
            logger.error(f"An error occurred during vector store query: {e}")
            raise
