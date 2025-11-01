"""
RAG Data Pipeline - Main Ingestion Module

This module handles the ingestion of documents from multiple sources into a vector store:
- YouTube video transcripts
- Web scraping (HTML to Markdown)
- Google Drive documents (with format conversion)

The pipeline uses LlamaIndex for document processing and Azure AI for embeddings.
"""

# Standard library imports
from typing import List, Optional, Set, Tuple
import json

# LlamaIndex imports
from llama_index.core import Document
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser

# Local application imports
from config.config import (
    get_azure_api_key_embedding,
    get_azure_endpoint_embedding,
    get_google_drive_folder_id,
)
from database.db import DatabaseConnection
from src.drive_reader.drive_reader import convert_drive_documents_to_markdown
from src.embeddings.azure_embedding import AzureAIEmbedding
from src.scraper.web_scraper import fetch_website_urls_from_github, scrape_web_urls
from src.youtube_transcripts.youtube_transcript_to_md import (
    fetch_youtube_urls_from_github,
    process_youtube_videos,
)

# ===============================
# Constants
# ===============================
AZURE_ENDPOINT = get_azure_endpoint_embedding()
AZURE_API_KEY = get_azure_api_key_embedding()
DEPLOYMENT_NAME = "text-embedding-3-small"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 100
SIMILARITY_TOP_K = 10


# ===============================
# Pure Helper Functions
# ===============================

def get_existing_identifiers(db_connection: DatabaseConnection) -> Tuple[Set[str], Set[str]]:
    """
    Get existing URLs and file paths from the database.
    
    Args:
        db_connection: Database connection instance
        
    Returns:
        Tuple of (existing_urls, existing_filepaths)
    """
    print("\n🔍 Checking existing documents in database...")
    
    try:
        all_data, urls, filepaths = db_connection.get_all_metadata()
        
        # Parse metadata if it's a string
        for record in all_data:
            if isinstance(record['metadata'], str):
                try:
                    record['metadata'] = json.loads(record['metadata'])
                except json.JSONDecodeError:
                    record['metadata'] = {}
        
        # Extract unique URLs
        existing_urls = urls if urls else {
            r['metadata'].get('url') 
            for r in all_data 
            if r['metadata'].get('url')
        }
        
        # Extract unique file paths
        existing_filepaths = filepaths if filepaths else {
            r['metadata'].get('file_path') 
            for r in all_data 
            if r['metadata'].get('file_path')
        }
        
        print(f"✅ Found {len(existing_urls)} existing URLs")
        print(f"✅ Found {len(existing_filepaths)} existing file paths")
        
        return existing_urls, existing_filepaths
        
    except Exception as e:
        print(f"⚠️ Error fetching existing data: {e}")
        print("Proceeding without duplicate filtering...")
        return set(), set()


def filter_duplicate_documents(
    documents: List[Document],
    existing_urls: Set[str],
    existing_filepaths: Set[str]
) -> List[Document]:
    """
    Filter out documents that already exist in the database.
    
    Args:
        documents: List of documents to filter
        existing_urls: Set of existing URLs in database
        existing_filepaths: Set of existing file paths in database
        
    Returns:
        List of new documents not yet in database
    """
    if not documents:
        return []
    
    new_documents = []
    duplicates_count = 0
    
    for doc in documents:
        metadata = doc.metadata
        doc_url = metadata.get('url')
        doc_filepath = metadata.get('file_path') or metadata.get('original_file_path')
        
        # Check if document already exists
        is_duplicate = False
        
        if doc_url and doc_url in existing_urls:
            is_duplicate = True
            print(f"⏭️  Skipping duplicate URL: {doc_url}")
        
        if doc_filepath and doc_filepath in existing_filepaths:
            is_duplicate = True
            print(f"⏭️  Skipping duplicate file: {doc_filepath}")
        
        if is_duplicate:
            duplicates_count += 1
        else:
            new_documents.append(doc)
    
    print(f"\n📊 Filtering Results:")
    print(f"   Total documents: {len(documents)}")
    print(f"   Duplicates filtered: {duplicates_count}")
    print(f"   New documents to ingest: {len(new_documents)}")
    
    return new_documents


def fetch_source_documents(
    youtube_urls: List[str],
    web_urls: List[str],
    drive_folder_id: Optional[str]
) -> List[Document]:
    """
    Fetch documents from all sources (YouTube, Web, Google Drive).
    
    Args:
        youtube_urls: List of YouTube URLs to process
        web_urls: List of web URLs to scrape
        drive_folder_id: Google Drive folder ID
        
    Returns:
        Combined list of documents from all sources
    """
    all_documents = []

    # Process YouTube videos
    if youtube_urls:
        print(f"\n📹 Processing YouTube videos...")
        youtube_documents = process_youtube_videos(youtube_urls)
        all_documents.extend(youtube_documents)
        print(f"✅ Loaded {len(youtube_documents)} YouTube documents.")

    # Scrape web URLs
    if web_urls:
        print(f"\n🌐 Processing web URLs...")
        url_documents = scrape_web_urls(web_urls)
        all_documents.extend(url_documents)
        print(f"✅ Loaded {len(url_documents)} web documents.")

    # Load Google Drive documents
    if drive_folder_id:
        print(f"\n📁 Processing Google Drive documents...")
        drive_documents = convert_drive_documents_to_markdown(drive_folder_id)
        all_documents.extend(drive_documents)
        print(f"✅ Loaded {len(drive_documents)} Google Drive documents.")

    return all_documents


# ===============================
# Pipeline Creation Functions
# ===============================

def create_embedding_model() -> AzureAIEmbedding:
    """
    Create Azure AI embedding model instance.
    
    Returns:
        Configured AzureAIEmbedding instance
    """
    return AzureAIEmbedding(
        endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        deployment=DEPLOYMENT_NAME,
        embed_dim=1536
    )


def create_ingestion_pipeline(vector_store) -> IngestionPipeline:
    """
    Create and return an ingestion pipeline with transformations.
    
    The pipeline includes:
    - MarkdownNodeParser for chunking documents
    - TitleExtractor for extracting titles
    - AzureAIEmbedding for generating embeddings
    
    Args:
        vector_store: Vector store instance for storing embeddings
        
    Returns:
        IngestionPipeline: Configured ingestion pipeline
    """
    return IngestionPipeline(
        transformations=[
            MarkdownNodeParser(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                include_metadata=True,
                include_prev_next_rel=True
            ),
            TitleExtractor(),
            create_embedding_model()
        ],
        vector_store=vector_store,
    )


# ===============================
# Ingestion Functions
# ===============================

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


# ===============================
# Main Entry Point
# ===============================
def main():
    """
    Main entry point for the RAG data pipeline.
    
    This function:
    1. Initializes database connection and vector store
    2. Creates ingestion pipeline
    3. Fetches documents from all sources (YouTube, Web, Google Drive)
    4. Filters duplicates and ingests documents into the vector store
    """
    print("🚀 Starting RAG Data Pipeline...")
    
    # Initialize database connection and vector store
    db_connection = DatabaseConnection()
    vector_store = db_connection.get_vector_store()
    
    # Create ingestion pipeline
    pipeline = create_ingestion_pipeline(vector_store)


    # Fetch YouTube URLs from GitHub markdown file
    github_md_for_youtube_url = (
        "https://raw.githubusercontent.com/RMCV-Rajapaksha/"
        "Agentic-RAG-AI/main/YouTubeURL.md"
    )

    github_md_for_website_url = (
        "https://raw.githubusercontent.com/RMCV-Rajapaksha/"
        "Agentic-RAG-AI/main/WebURLs.md"
    )

    website_urls = fetch_website_urls_from_github(github_md_for_website_url)
    print(f"Found {len(website_urls)} website URLs to process.")

    youtube_urls = fetch_youtube_urls_from_github(github_md_for_youtube_url)
    print(f"Found {len(youtube_urls)} YouTube URLs to process.")

    # Get Google Drive folder ID from config
    drive_folder_id = get_google_drive_folder_id()

    try:
        # Get existing URLs and file paths from database
        existing_urls, existing_filepaths = get_existing_identifiers(db_connection)
        
        # Fetch all documents from sources
        all_documents = fetch_source_documents(
            youtube_urls=youtube_urls,
            web_urls=website_urls,
            drive_folder_id=drive_folder_id
        )

        # Filter out duplicate documents
        new_documents = filter_duplicate_documents(
            all_documents,
            existing_urls,
            existing_filepaths
        )

        # Ingest only new documents
        if new_documents:
            ingest_documents(new_documents, pipeline)
            print(f"✅ Pipeline completed! Total new documents processed: {len(new_documents)}")
        else:
            print("⚠️ No new documents to ingest. All documents already exist in database.")

    except Exception as e:
        print(f"❌ An error occurred during ingestion: {e}")
        raise


if __name__ == "__main__":
    main()
