"""
Database Connection Module

This module handles database connections and vector store initialization
for the RAG data ingestion pipeline using PostgreSQL with pgvector.
"""

# Standard library imports
from typing import Optional, Tuple, Set
import asyncio
import logging
import os
from dotenv import load_dotenv

# Third-party imports
from sqlalchemy import make_url
import asyncpg

# LlamaIndex imports
from llama_index.vector_stores.postgres import PGVectorStore

# Local imports
from config.exceptions import DatabaseConnectionError
from config.constants import (
    HNSW_M,
    HNSW_EF_CONSTRUCTION,
    HNSW_EF_SEARCH,
    HNSW_DISTANCE_METHOD,
    EMBEDDING_DIMENSION,

)

# Configure logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Environment variables
DB_NAME = os.getenv('DB_NAME')
CONNECTION_STRING = os.getenv('CONNECTION_STRING')
DB_TABLE_NAME = os.getenv('DB_TABLE_NAME')


# ===============================
# Database Connection Class
# ===============================

class DatabaseConnection:
    """
    Handle database connections and vector store initialization for data ingestion.
    
    This class manages PostgreSQL connections with pgvector extension for
    storing and retrieving document embeddings.
    
    Attributes:
        connection_string (str): PostgreSQL connection string
        db_name (str): Database name
        table_name (str): Table name for storing vectors
        
    Raises:
        DatabaseConnectionError: If database connection fails
    """
    
    def __init__(self):
        """
        Initialize database connection parameters from configuration.
        
        Raises:
            DatabaseConnectionError: If required configuration is missing
        """
        try:
            if not CONNECTION_STRING:
                raise ValueError("Missing required environment variable: CONNECTION_STRING")
            if not DB_NAME:
                raise ValueError("Missing required environment variable: DB_NAME")
            if not DB_TABLE_NAME:
                raise ValueError("Missing required environment variable: DB_TABLE_NAME")
                
            self.connection_string = CONNECTION_STRING
            self.db_name = DB_NAME
            self.table_name = DB_TABLE_NAME
            logger.info(f"Database configuration loaded: {self.db_name}/{self.table_name}")
        except Exception as e:
            error_msg = "Database connection failed: {}".format(str(e))
            logger.error(error_msg, exc_info=True)
            raise DatabaseConnectionError(error_msg)
        
    def get_vector_store(self, embed_dim: int = EMBEDDING_DIMENSION) -> PGVectorStore:
        """
        Return a configured PGVectorStore instance.

        Args:
            embed_dim: Embedding dimension (default: 1536 for OpenAI embeddings)
            
        Returns:
            PGVectorStore: Configured vector store instance with HNSW indexing
            
        Raises:
            DatabaseConnectionError: If vector store creation fails
        """
        try:
            url = make_url(self.connection_string)
            
            logger.info(f"Creating vector store connection to {url.host}:{url.port}")
            
            vector_store = PGVectorStore.from_params(
                database=self.db_name,
                host=url.host,
                password=url.password,
                port=url.port,
                user=url.username,
                table_name=self.table_name,
                embed_dim=embed_dim,
                hnsw_kwargs={
                    "hnsw_m": HNSW_M,
                    "hnsw_ef_construction": HNSW_EF_CONSTRUCTION,
                    "hnsw_ef_search": HNSW_EF_SEARCH,
                    "hnsw_dist_method": HNSW_DISTANCE_METHOD,
                },
            )
            
            logger.info("Vector store created successfully")
            return vector_store
            
        except Exception as e:
            error_msg = "Database connection failed: {}".format(str(e))
            logger.error(error_msg, exc_info=True)
            raise DatabaseConnectionError(error_msg)
    
    async def get_all_metadata_async(self) -> Tuple[list, Set[str], Set[str]]:
        """
        Retrieve all data including metadata from the vector store table using asyncpg.
        
        Returns:
            tuple: A tuple containing:
                - list: List of dictionaries containing all columns including metadata
                - set: Set of unique URLs from metadata
                - set: Set of unique file paths from metadata
                
        Raises:
            DatabaseConnectionError: If database query fails
        """
        url = make_url(self.connection_string)
        
        try:
            # Connect to the database using asyncpg
            conn = await asyncpg.connect(
                host=url.host,
                port=url.port,
                user=url.username,
                password=url.password,
                database=self.db_name
            )
            
            logger.info(f"Connected to database for metadata retrieval")
            
            try:
                # Query to get all data
                query = f"""
                    SELECT 
                        id,
                        text,
                        metadata_,
                        node_id,
                        embedding
                    FROM {self.table_name}
                """
                
                result = await conn.fetch(query)
                logger.info(f"Retrieved {len(result)} records from database")
                
                # Convert to list of dicts and extract URLs and file paths
                rows = []
                urls = set()
                filepaths = set()
                
                for row in result:
                    metadata = row['metadata_']
                    
                    rows.append({
                        'id': row['id'],
                        'text': row['text'],
                        'metadata': metadata,
                        'node_id': row['node_id'],
                        'embedding': row['embedding']
                    })
                    
                    # Extract URLs and file paths from metadata
                    if isinstance(metadata, dict):
                        if 'url' in metadata and metadata['url']:
                            urls.add(metadata['url'])
                        if 'file_path' in metadata and metadata['file_path']:
                            filepaths.add(metadata['file_path'])
                
                logger.info(f"Found {len(urls)} unique URLs and {len(filepaths)} unique file paths")
                return rows, urls, filepaths
                
            finally:
                await conn.close()
                logger.debug("Database connection closed")
                
        except Exception as e:
            error_msg = f"Failed to retrieve metadata: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseConnectionError(error_msg)
    
    def get_all_metadata(self) -> Tuple[list, Set[str], Set[str]]:
        """
        Synchronous wrapper for get_all_metadata_async.
        
        Returns:
            tuple: A tuple containing:
                - list: List of dictionaries containing all columns including metadata
                - set: Set of unique URLs from metadata
                - set: Set of unique file paths from metadata
                
        Raises:
            DatabaseConnectionError: If database query fails
        """
        try:
            logger.debug("Fetching metadata from database (synchronous call)")
            return asyncio.run(self.get_all_metadata_async())
        except Exception as e:
            error_msg = f"Failed to retrieve metadata: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise DatabaseConnectionError(error_msg)