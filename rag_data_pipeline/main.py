"""
RAG Data Pipeline - Main Ingestion Module

This module handles the ingestion of documents from multiple sources into a vector store:
- YouTube video transcripts
- Web scraping (HTML to Markdown)
- Google Drive documents (with format conversion)

The pipeline uses LlamaIndex for document processing and Azure AI for embeddings.
"""

# Local application imports
from config.config import (
    get_azure_api_key_embedding,
    get_azure_endpoint_embedding,
    get_google_drive_folder_id,
)
from database.db import DatabaseConnection
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
# Constants
# ===============================
AZURE_ENDPOINT = get_azure_endpoint_embedding()
AZURE_API_KEY = get_azure_api_key_embedding()
DEPLOYMENT_NAME = "text-embedding-3-small"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 100
SIMILARITY_TOP_K = 10


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
    
    # Create ingestion pipeline with configuration
    pipeline = create_ingestion_pipeline(
        vector_store=vector_store,
        endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        deployment=DEPLOYMENT_NAME,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    # Fetch YouTube URLs from GitHub markdown file
    github_md_for_youtube_url = (
        "https://raw.githubusercontent.com/RMCV-Rajapaksha/"
        "Agentic-RAG-AI/main/YouTubeURL.md"
    )

    github_md_for_website_url = (
        "https://raw.githubusercontent.com/RMCV-Rajapaksha/"
        "Agentic-RAG-AI/main/WebURLs.md"
    )
    website_urls=["https://wso2.ai/"]
    # website_urls = fetch_website_urls_from_github(github_md_for_website_url)
    print(f"Found {len(website_urls)} website URLs to process.")

    youtube_urls=[]
    #youtube_urls = fetch_youtube_urls_from_github(github_md_for_youtube_url)
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
