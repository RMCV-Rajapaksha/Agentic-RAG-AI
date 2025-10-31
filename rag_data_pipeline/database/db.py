"""
Database Connection Module

This module handles database connections and vector store initialization
for the RAG data ingestion pipeline using PostgreSQL with pgvector.
"""

# Standard library imports
from typing import Set, Optional, List, Dict

# Third-party imports
from sqlalchemy import make_url, create_engine, text

# LlamaIndex imports
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import Document

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
        self._engine = None
        
    def _get_engine(self):
        """
        Get or create SQLAlchemy engine for database queries.
        Uses pg8000 driver for PostgreSQL connections.
        
        Returns:
            SQLAlchemy engine instance
        """
        if self._engine is None:
            url = make_url(self.connection_string)
            
            # Replace postgres:// with postgresql+pg8000:// for pg8000 driver
            if url.drivername == "postgres" or url.drivername == "postgresql":
                connection_string = self.connection_string.replace(
                    "postgres://", "postgresql+pg8000://"
                ).replace(
                    "postgresql://", "postgresql+pg8000://"
                )
            else:
                connection_string = self.connection_string
            
            self._engine = create_engine(connection_string)
        return self._engine
    
    def check_url_exists(self, url: str) -> bool:
        """
        Check if a URL already exists in the database.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL exists, False otherwise
        """
        try:
            engine = self._get_engine()
            query = text(f"""
                SELECT COUNT(*) 
                FROM data_{self.table_name} 
                WHERE metadata_->>'url' = :url
            """)
            
            with engine.connect() as conn:
                result = conn.execute(query, {"url": url})
                count = result.scalar()
                return count > 0
        except Exception as e:
            # Table doesn't exist yet - will be created when vector store is initialized
            if "does not exist" in str(e):
                return False
            print(f"Error checking URL existence: {e}")
            return False
    
    def check_file_path_exists(self, file_path: str) -> bool:
        """
        Check if a file path already exists in the database (for Google Drive documents).
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file path exists, False otherwise
        """
        try:
            engine = self._get_engine()
            query = text(f"""
                SELECT COUNT(*) 
                FROM data_{self.table_name} 
                WHERE metadata_->>'original_file_path' = :file_path
                OR metadata_->>'file_path' = :file_path
            """)
            
            with engine.connect() as conn:
                result = conn.execute(query, {"file_path": file_path})
                count = result.scalar()
                return count > 0
        except Exception as e:
            # Table doesn't exist yet - will be created when vector store is initialized
            if "does not exist" in str(e):
                return False
            print(f"Error checking file path existence: {e}")
            return False
    
    def get_existing_urls(self, source: Optional[str] = None) -> Set[str]:
        """
        Get all existing URLs from the database.
        
        Args:
            source: Optional source filter (e.g., 'youtube_transcript', 'web_scraper')
            
        Returns:
            Set of existing URLs
        """
        try:
            engine = self._get_engine()
            
            if source:
                query = text(f"""
                    SELECT DISTINCT metadata_->>'url' as url
                    FROM data_{self.table_name}
                    WHERE metadata_->>'url' IS NOT NULL
                    AND metadata_->>'source' = :source
                """)
                params = {"source": source}
            else:
                query = text(f"""
                    SELECT DISTINCT metadata_->>'url' as url
                    FROM data_{self.table_name}
                    WHERE metadata_->>'url' IS NOT NULL
                """)
                params = {}
            
            with engine.connect() as conn:
                result = conn.execute(query, params)
                urls = {row[0] for row in result if row[0]}
                return urls
        except Exception as e:
            # Table doesn't exist yet - will be created when vector store is initialized
            if "does not exist" in str(e):
                return set()
            print(f"Error getting existing URLs: {e}")
            return set()
    
    def get_existing_file_paths(self) -> Set[str]:
        """
        Get all existing file paths from the database (for Google Drive documents).
        
        Returns:
            Set of existing file paths
        """
        try:
            engine = self._get_engine()
            query = text(f"""
                SELECT DISTINCT 
                    COALESCE(metadata_->>'original_file_path', metadata_->>'file_path') as file_path
                FROM data_{self.table_name}
                WHERE metadata_->>'original_file_path' IS NOT NULL
                OR metadata_->>'file_path' IS NOT NULL
            """)
            
            with engine.connect() as conn:
                result = conn.execute(query)
                file_paths = {row[0] for row in result if row[0]}
                return file_paths
        except Exception as e:
            # Table doesn't exist yet - will be created when vector store is initialized
            if "does not exist" in str(e):
                return set()
            print(f"Error getting existing file paths: {e}")
            return set()
    
    def get_all_existing_metadata(self) -> Dict[str, Set[str]]:
        """
        Get all existing URLs and file paths grouped by source type.
        
        Returns:
            Dictionary with 'urls' and 'file_paths' keys containing sets of existing values
        """
        return {
            'urls': self.get_existing_urls(),
            'file_paths': self.get_existing_file_paths()
        }
    
    def filter_duplicate_documents(self, documents: List) -> List:
        """
        Filter out documents that already exist in the database.
        Checks both URLs (for web/YouTube content) and file paths (for Google Drive).
        
        Args:
            documents: List of Document objects to filter
            
        Returns:
            List of Document objects that don't exist in the database
        """
        if not documents:
            return []
        
        print(f"\n🔍 Checking {len(documents)} documents for duplicates...")
        
        # Get existing data from database
        existing_urls = self.get_existing_urls()
        existing_file_paths = self.get_existing_file_paths()
        
        filtered_documents = []
        skipped_count = 0
        
        for doc in documents:
            is_duplicate = False
            metadata = doc.metadata if hasattr(doc, 'metadata') and doc.metadata else {}
            
            # Check URL-based duplicates (YouTube, Web scraper)
            url = metadata.get('url')
            if url and url in existing_urls:
                print(f"⏭️  Skipping duplicate URL: {url}")
                is_duplicate = True
                skipped_count += 1
            
            # Check file path-based duplicates (Google Drive)
            file_path = metadata.get('original_file_path') or metadata.get('file_path')
            if not is_duplicate and file_path and file_path in existing_file_paths:
                print(f"⏭️  Skipping duplicate file: {file_path}")
                is_duplicate = True
                skipped_count += 1
            
            if not is_duplicate:
                filtered_documents.append(doc)
        
        print(f"✅ Filtered out {skipped_count} duplicate(s)")
        print(f"✅ {len(filtered_documents)} new document(s) ready for ingestion")
        
        return filtered_documents
        
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