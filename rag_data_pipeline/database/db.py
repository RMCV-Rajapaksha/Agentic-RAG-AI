import psycopg2
from psycopg2.extras import Json
from typing import List, Set, Optional
import os

from config.config import get_config

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        self.config = get_config()
        self.conn = psycopg2.connect(
            dbname=self.config.db_name,
            user=self.config.db_user,
            password=self.config.db_password,
            host=self.config.db_host,
            port=self.config.db_port
        )
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def insert_embedding(self, vector: List[float], chunked_text: str, metadata: dict, source: str):
        self.cursor.execute(
            """
            INSERT INTO embeddings (vector, chunked_text, metadata, source)
            VALUES (%s, %s, %s, %s)
            """,
            (vector, chunked_text, Json(metadata), source)
        )

    def url_exists(self, source_url: str) -> bool:
        """Check if a URL already exists in the database"""
        self.cursor.execute(
            "SELECT COUNT(*) FROM embeddings WHERE source = %s",
            (source_url,)
        )
        count = self.cursor.fetchone()[0]
        return count > 0

    def get_existing_urls(self) -> Set[str]:
        """Get all existing URLs in the database"""
        self.cursor.execute("SELECT DISTINCT source FROM embeddings")
        urls = self.cursor.fetchall()
        return {url[0] for url in urls}

    def batch_insert_embeddings(self, embeddings_batch: List[dict]):
        """Insert multiple embeddings in a batch"""
        insert_query = """
            INSERT INTO embeddings (vector, chunked_text, metadata, source)
            VALUES (%s, %s, %s, %s)
        """
        batch_data = [
            (item['vector'], item['chunked_text'], Json(item['metadata']), item['source'])
            for item in embeddings_batch
        ]
        self.cursor.executemany(insert_query, batch_data)




