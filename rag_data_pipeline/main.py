"""
RAG Data Pipeline - Main Ingestion Module

This module handles the ingestion of documents from multiple sources into a vector store:
- YouTube video transcripts
- Web scraping (HTML to Markdown)
- Google Drive documents (with format conversion)

The pipeline uses LlamaIndex for document processing and Azure AI for embeddings.
"""

# Standard library imports
import sys
from typing import List, Optional

# Local application imports
from config import (
    get_azure_api_key_embedding,
    get_azure_endpoint_embedding,
    get_google_drive_folder_id,
    RAGPipelineException,
)
from config.constants import (
    EMBEDDING_DEPLOYMENT_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    GITHUB_YOUTUBE_URLS_MD,
    GITHUB_WEBSITE_URLS_MD,
)
from database import DatabaseConnection
from src.pipeline import create_ingestion_pipeline, ingest_documents
from src.scraper.web_scraper import fetch_website_urls_from_github
from src.utils import (
    fetch_source_documents,
    filter_duplicate_documents,
    get_existing_identifiers,
)
from src.youtube_transcripts.youtube_transcript_to_md import (
    fetch_youtube_urls_from_github,
)


# ===============================
# Main Entry Point
# ===============================
def main() -> int:
    """
    Main entry point for the RAG data pipeline.
    
    This function:
    1. Initializes database connection and vector store
    2. Creates ingestion pipeline
    3. Fetches documents from all sources (YouTube, Web, Google Drive)
    4. Filters duplicates and ingests documents into the vector store
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("=" * 70)
    print("Starting RAG Data Pipeline")
    print("=" * 70)
    
    try:
        # Get Azure credentials
        azure_endpoint = get_azure_endpoint_embedding()
        azure_api_key = get_azure_api_key_embedding()
        
        if not azure_endpoint or not azure_api_key:
            print("ERROR: Azure embedding credentials not configured")
            return 1
        
        # Initialize database connection and vector store
        print("Initializing database connection...")
        db_connection = DatabaseConnection()
        vector_store = db_connection.get_vector_store()
        print("Database connection established")
        
        # Create ingestion pipeline with configuration
        print("Creating ingestion pipeline...")
        pipeline = create_ingestion_pipeline(
            vector_store=vector_store,
            endpoint=azure_endpoint,
            api_key=azure_api_key,
            deployment=EMBEDDING_DEPLOYMENT_NAME,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        print("Ingestion pipeline created")

        # Fetch URLs from GitHub markdown files
        print("Fetching data source URLs from GitHub...")
        
        # For demo, using hardcoded URLs - you can uncomment the GitHub fetching
        website_urls = ["https://wso2.ai/"]
        # website_urls = fetch_website_urls_from_github(GITHUB_WEBSITE_URLS_MD)
        print(f"Found {len(website_urls)} website URLs to process")

        youtube_urls = []
        # youtube_urls = fetch_youtube_urls_from_github(GITHUB_YOUTUBE_URLS_MD)
        print(f"Found {len(youtube_urls)} YouTube URLs to process")

        # Get Google Drive folder ID from config
        drive_folder_id = get_google_drive_folder_id()
        if drive_folder_id:
            print(f"Google Drive folder ID configured: {drive_folder_id}")
        else:
            print("WARNING: No Google Drive folder ID configured")

        # Get existing URLs and file paths from database
        print("Checking for existing documents in database...")
        existing_urls, existing_filepaths = get_existing_identifiers(db_connection)
        
        # Fetch all documents from sources
        print("Fetching documents from all sources...")
        all_documents = fetch_source_documents(
            youtube_urls=youtube_urls,
            web_urls=website_urls,
            drive_folder_id=drive_folder_id
        )
        print(f"Total documents fetched: {len(all_documents)}")

        # Filter out duplicate documents
        print("Filtering duplicate documents...")
        new_documents = filter_duplicate_documents(
            all_documents,
            existing_urls,
            existing_filepaths
        )

        # Ingest only new documents
        if new_documents:
            print(f"Starting ingestion of {len(new_documents)} new documents...")
            ingest_documents(new_documents, pipeline)
            print("=" * 70)
            print(f"Pipeline completed successfully!")
            print(f"Total new documents processed: {len(new_documents)}")
            print("=" * 70)
        else:
            print("=" * 70)
            print("WARNING: No new documents to ingest")
            print("All documents already exist in database")
            print("=" * 70)
        
        return 0

    except RAGPipelineException as e:
        print("=" * 70)
        print(f"ERROR: Pipeline error: {e}")
        print("=" * 70)
        return 1
        
    except Exception as e:
        print("=" * 70)
        print(f"ERROR: Unexpected error occurred: {e}")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
