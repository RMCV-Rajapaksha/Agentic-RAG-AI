"""
RAG Data Pipeline - Main Ingestion Module

This module handles the ingestion of documents from multiple sources into a vector store:
- YouTube video transcripts
- Web scraping (HTML to Markdown)
- Google Drive documents (with format conversion)

The pipeline uses LlamaIndex for document processing and Azure AI for embeddings.
"""

# Standard library imports
from typing import List, Optional

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

    website_urls = [
        "https://wso2.ai/",
    ]
    print(f"Found {len(website_urls)} website URLs to process.")

    youtube_urls = []
    print(f"Found {len(youtube_urls)} YouTube URLs to process.")

    # Get Google Drive folder ID from config
    drive_folder_id = get_google_drive_folder_id()

    try:
        # Fetch all documents from sources
        all_documents = fetch_source_documents(
            youtube_urls=youtube_urls,
            web_urls=website_urls,
            drive_folder_id=drive_folder_id
        )

        # Ingest documents
        if all_documents:
            ingest_documents(all_documents, pipeline)
            print(f"✅ Pipeline completed! Total documents processed: {len(all_documents)}")
        else:
            print("⚠️ No documents found to ingest.")

    except Exception as e:
        print(f"❌ An error occurred during ingestion: {e}")
        raise


if __name__ == "__main__":
    main()
