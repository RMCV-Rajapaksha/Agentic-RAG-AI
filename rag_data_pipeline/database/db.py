# import psycopg2
from sqlalchemy import make_url
from llama_index.vector_stores.postgres import PGVectorStore
from config.config import get_config
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Handles database connections and vector store initialization for data ingestion.

    """
    
    def __init__(self):
        self.config = get_config()
        self.connection_string = self.config.db_connection_string
        self.db_name = self.config.db_name
        self.table_name = self.config.db_table_name
        
    # def create_database_if_not_exists(self):
    #     """
    #     Creates the database if it doesn't exist.
    #     """
    #     try:
    #         # Connect to postgres server (not specific database)
    #         conn = psycopg2.connect(self.connection_string)
    #         conn.autocommit = True
            
    #         with conn.cursor() as cursor:
    #             # Check if database exists
    #             cursor.execute(
    #                 "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", 
    #                 (self.db_name,)
    #             )
    #             exists = cursor.fetchone()
                
    #             if not exists:
    #                 cursor.execute(f"CREATE DATABASE {self.db_name}")
    #                 logger.info(f"Created database: {self.db_name}")
    #             else:
    #                 logger.info(f"Database {self.db_name} already exists")
                    
    #         conn.close()
            
    #     except Exception as e:
    #         logger.error(f"Error creating database: {e}")
    #         raise
            
    def get_vector_store(self, embed_dim: int = 1536):
        """
        Returns a configured PGVectorStore instance.

        Args:
            embed_dim (int): Embedding dimension (default: 1536 for OpenAI)
            
        Returns:
            PGVectorStore: Configured vector store instance
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