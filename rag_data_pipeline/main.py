"""
RAG Data Pipeline - Main Ingestion Module

This module handles the ingestion of documents from multiple sources into a vector store:
- YouTube video transcripts
- Web scraping (HTML to Markdown)
- Google Drive documents (with format conversion)

The pipeline uses LlamaIndex for document processing and Azure AI for embeddings.
"""

# Standard library imports
from typing import List, Set, Optional

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
from src.scraper.web_scraper import scrape_web_urls
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

def filter_new_urls(
    urls: List[str],
    existing_urls: Set[str],
    source_type: str
) -> List[str]:
    """
    Filter out URLs that already exist in the database.
    
    Args:
        urls: List of URLs to check
        existing_urls: Set of existing URLs from database
        source_type: Type of source (e.g., 'YouTube', 'Web')
        
    Returns:
        List of new URLs not in database
    """
    new_urls = []
    for url in urls:
        if url in existing_urls:
            print(f"⏭️  Skipping {source_type} URL (already in database): {url}")
        else:
            new_urls.append(url)
    
    if new_urls:
        print(f"✅ Found {len(new_urls)} new {source_type} URL(s) to process")
    else:
        print(f"ℹ️  No new {source_type} URLs to process")
    
    return new_urls


def fetch_source_documents(
    youtube_urls: List[str],
    web_urls: List[str],
    drive_folder_id: Optional[str],
    db_connection: DatabaseConnection
) -> List[Document]:
    """
    Fetch documents from all sources (YouTube, Web, Google Drive).
    Only fetches content that doesn't already exist in the database.
    
    Args:
        youtube_urls: List of YouTube URLs to process
        web_urls: List of web URLs to scrape
        drive_folder_id: Google Drive folder ID
        db_connection: Database connection instance for checking existing data
        
    Returns:
        Combined list of documents from all sources
    """
    all_documents = []

    # Check existing URLs in database
    print("\n🔍 Checking database for existing content...")
    existing_urls = db_connection.get_existing_urls()
    existing_file_paths = db_connection.get_existing_file_paths()
    print(f"Found {len(existing_urls)} existing URLs in database")
    print(f"Found {len(existing_file_paths)} existing file paths in database")

    # Process YouTube videos - filter out existing URLs
    if youtube_urls:
        print(f"\n📹 Processing YouTube videos...")
        new_youtube_urls = filter_new_urls(youtube_urls, existing_urls, "YouTube")
        
        if new_youtube_urls:
            youtube_documents = process_youtube_videos(new_youtube_urls)
            all_documents.extend(youtube_documents)
            print(f"✅ Loaded {len(youtube_documents)} new YouTube documents.")
        else:
            print("ℹ️  All YouTube videos already in database")

    # Scrape web URLs - filter out existing URLs
    if web_urls:
        print(f"\n🌐 Processing web URLs...")
        new_web_urls = filter_new_urls(web_urls, existing_urls, "Web")
        
        if new_web_urls:
            url_documents = scrape_web_urls(new_web_urls)
            all_documents.extend(url_documents)
            print(f"✅ Loaded {len(url_documents)} new web documents.")
        else:
            print("ℹ️  All web URLs already in database")

    # Load Google Drive documents - check by file path
    if drive_folder_id:
        print(f"\n📁 Processing Google Drive documents...")
        drive_documents = convert_drive_documents_to_markdown(drive_folder_id)
        
        # Filter out documents with existing file paths
        new_drive_documents = []
        for doc in drive_documents:
            file_path = doc.metadata.get('original_file_path') or doc.metadata.get('file_path')
            if file_path and file_path in existing_file_paths:
                print(f"⏭️  Skipping Google Drive file (already in database): {file_path}")
            else:
                new_drive_documents.append(doc)
        
        if new_drive_documents:
            all_documents.extend(new_drive_documents)
            print(f"✅ Loaded {len(new_drive_documents)} new Google Drive documents.")
        else:
            print("ℹ️  All Google Drive documents already in database")

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
    pipeline: IngestionPipeline,
    vector_store,
    db_connection: DatabaseConnection
) -> None:
    """
    Ingest documents into the vector store using the pipeline.
    Includes a final safety check for duplicates before ingestion.
    
    Args:
        documents: List of documents to ingest
        pipeline: Ingestion pipeline instance
        vector_store: Vector store instance
        db_connection: Database connection for duplicate checking
    """
    if not documents:
        print("No documents provided for ingestion.")
        return

    # Final safety check - filter duplicates one more time
    # This catches any duplicates that might have been added since initial fetch
    print(f"\n🛡️  Final safety check for duplicates before ingestion...")
    filtered_documents = db_connection.filter_duplicate_documents(documents)
    
    if not filtered_documents:
        print("ℹ️  No new documents to ingest after final duplicate check.")
        return

    print(f"\n📥 Ingesting {len(filtered_documents)} document(s)...")
    pipeline.run(documents=filtered_documents, show_progress=True)
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

    # URLs to scrape (add URLs as needed)
    urls_to_scrape = [
        "https://wso2.ai/",
        # "https://wso2.com/api-management/ai/",
        # "https://wso2.com/integration/ai/",
        # "https://wso2.com/identity-and-access-management/ai/",
        # "https://wso2.com/internal-developer-platform/ai/"
    ]

    # Fetch YouTube URLs from GitHub markdown file
    github_md_url = (
        "https://raw.githubusercontent.com/RMCV-Rajapaksha/"
        "Agentic-RAG-AI/main/YouTubeURL.md"
    )
    
    youtube_urls = []
    print(f"Found {len(youtube_urls)} YouTube URLs to process.")

    # Get Google Drive folder ID from config
    drive_folder_id = get_google_drive_folder_id()

    try:
        # Fetch all documents from sources (with database checks)
        all_documents = fetch_source_documents(
            youtube_urls=youtube_urls,
            web_urls=urls_to_scrape,
            drive_folder_id=drive_folder_id,
            db_connection=db_connection
        )

        # Ingest documents
        if all_documents:
            ingest_documents(all_documents, pipeline, vector_store, db_connection)
            print(f"✅ Pipeline completed! Total documents processed: {len(all_documents)}")
        else:
            print("⚠️ No new documents found to ingest.")

    except Exception as e:
        print(f"❌ An error occurred during ingestion: {e}")
        raise


if __name__ == "__main__":
    main()
