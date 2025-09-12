import psycopg2
from sqlalchemy import make_url
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import NodeWithScore
from typing import List
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
        self.vector_store = None
        
    def create_database_if_not_exists(self):
        """
        Creates the database if it doesn't exist.
        """
        try:
            # Connect to postgres server (not specific database)
            conn = psycopg2.connect(self.connection_string)
            conn.autocommit = True
            
            with conn.cursor() as cursor:
                # Check if database exists
                cursor.execute(
                    "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", 
                    (self.db_name,)
                )
                exists = cursor.fetchone()
                
                if not exists:
                    cursor.execute(f"CREATE DATABASE {self.db_name}")
                    logger.info(f"Created database: {self.db_name}")
                else:
                    logger.info(f"Database {self.db_name} already exists")
                    
            conn.close()
            
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            raise
            
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
    def query_vector_store(
        self,
        query_text: str,
        embed_model: BaseEmbedding,
        similarity_top_k: int = 5,
    ) -> List[NodeWithScore]:
        """
        Queries the vector store to find the most similar text chunks for a given query.

        Args:
            query_text (str): The text query to search for.
            embed_model (BaseEmbedding): The embedding model to use for vectorizing the query text.
            similarity_top_k (int): The number of top similar results to retrieve.

        Returns:
            List[NodeWithScore]: A list of nodes, each containing the text chunk
                                 and its corresponding similarity score.
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
                    nodes_with_scores.append(NodeWithScore(node=node, score=similarity))

            logger.info(f"Found {len(nodes_with_scores)} related text chunks.")
            return nodes_with_scores

        except Exception as e:
            logger.error(f"An error occurred during vector store query: {e}")
            # Depending on desired behavior, you might want to return [] or raise
            raise