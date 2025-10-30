"""
RAG Data Pipeline - Main Ingestion Module

This module handles the ingestion of documents from multiple sources into a vector store:
- YouTube video transcripts
- Web scraping (HTML to Markdown)
- Google Drive documents (with format conversion)

The pipeline uses LlamaIndex for document processing and Azure AI for embeddings.
"""

# Standard library imports
from typing import List

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


# ===============================
# Pipeline and Processing Functions
# ===============================

def create_ingestion_pipeline(vector_store):
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
                chunk_size=512,
                chunk_overlap=100,
                include_metadata=True,
                include_prev_next_rel=True
            ),
            TitleExtractor(),
            AzureAIEmbedding(
                endpoint=AZURE_ENDPOINT,
                api_key=AZURE_API_KEY,
                deployment=DEPLOYMENT_NAME,
                embed_dim=1536
            )
        ],
        vector_store=vector_store,
    )


# ===============================
# Document Filtering and Ingestion Functions
# ===============================

def filter_duplicate_documents(
    documents: List[Document],
    vector_store
) -> List[Document]:
    """
    Filter out documents with duplicate URLs.
    
    Args:
        documents: List of documents to filter
        vector_store: Vector store instance to check for existing URLs
        
    Returns:
        List of documents without duplicates
    """
    if not documents:
        return []
    
    filtered_documents = []
    
    try:
        existing_urls = set()
        
        # Fetch existing URLs from vector store
        try:
            all_nodes = (
                vector_store._get_all()
                if hasattr(vector_store, '_get_all')
                else []
            )
            for node in all_nodes:
                url = (
                    node.metadata.get('url')
                    if hasattr(node, 'metadata') and node.metadata
                    else None
                )
                if url:
                    existing_urls.add(url)
                    
        except Exception as e:
            print(f"Could not fetch existing URLs from vector store: {e}")

        # Filter documents
        for doc in documents:
            url = doc.metadata.get('url') if doc.metadata else None
            if url and url in existing_urls:
                print(f"Skipping duplicate URL: {url}")
                continue
            filtered_documents.append(doc)
            
    except Exception as e:
        print(f"Error during duplicate filtering: {e}")
        filtered_documents = documents

    return filtered_documents


def ingest_documents(
    documents: List[Document],
    pipeline,
    vector_store
) -> None:
    """
    Ingest documents into the vector store using the pipeline.
    
    Args:
        documents: List of documents to ingest
        pipeline: Ingestion pipeline instance
        vector_store: Vector store instance
    """
    if not documents:
        return

    filtered_documents = filter_duplicate_documents(documents, vector_store)

    if not filtered_documents:
        print("No new documents to ingest after filtering.")
        return

    pipeline.run(documents=filtered_documents, show_progress=True)


# ===============================
# Main Entry Point
# ===============================
def main():
    """
    Main entry point for the RAG data pipeline.
    
    This function:
    1. Initializes database connection and vector store
    2. Creates ingestion pipeline
    3. Fetches YouTube URLs from GitHub
    4. Processes documents from all sources (YouTube, Web, Google Drive)
    5. Ingests documents into the vector store
    """
    # Initialize database connection and vector store
    db_connection = DatabaseConnection()
    vector_store = db_connection.get_vector_store()
    
    # Create ingestion pipeline
    pipeline = create_ingestion_pipeline(vector_store)

    # URLs to scrape (currently empty - add URLs as needed)
    urls_to_scrape = [
        # "https://wso2.ai/",
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
    
    urls_to_videos = fetch_youtube_urls_from_github(github_md_url)
    print(f"YouTube URLs to process: {urls_to_videos}")

    drive_folder_id = get_google_drive_folder_id()

    try:
        all_documents = []

        # Process YouTube videos
        if urls_to_videos:
            youtube_documents = process_youtube_videos(urls_to_videos)
            all_documents.extend(youtube_documents)

        # Scrape web URLs
        if urls_to_scrape:
            url_documents = scrape_web_urls(urls_to_scrape)
            all_documents.extend(url_documents)

        # Load and convert Google Drive documents
        if drive_folder_id:
            print("Loading and converting Google Drive documents...")
            drive_documents = convert_drive_documents_to_markdown(drive_folder_id)
            print(
                f"Loaded and converted {len(drive_documents)} "
                "documents from Google Drive."
            )
            all_documents.extend(drive_documents)

        # Ingest all documents
        if all_documents:
            print(f"Ingesting {len(all_documents)} documents...")
            ingest_documents(all_documents, pipeline, vector_store)
            print("✅ Data ingestion completed successfully!")
        else:
            print("⚠️ No documents to ingest.")

    except Exception as e:
        print(f"❌ An error occurred during ingestion: {e}")


if __name__ == "__main__":
    main()
