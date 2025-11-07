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
import logging
from typing import List, Optional
import csv
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Environment variables
AZURE_ENDPOINT_EMBEDDING = os.getenv('AZURE_ENDPOINT_EMBEDDING')
AZURE_API_KEY_EMBEDDING = os.getenv('AZURE_API_KEY_EMBEDDING')
FOLDER_ID = os.getenv('FOLDER_ID')

# Local application imports
from config.exceptions import RAGPipelineException
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
    logger.info("=" * 70)
    logger.info("Starting RAG Data Pipeline")
    logger.info("=" * 70)
    
    try:
        # Validate Azure credentials
        if not AZURE_ENDPOINT_EMBEDDING or not AZURE_API_KEY_EMBEDDING:
            logger.error("Azure embedding credentials not configured in environment variables")
            logger.error("Required: AZURE_ENDPOINT_EMBEDDING, AZURE_API_KEY_EMBEDDING")
            return 1
        
        logger.info("Azure embedding credentials validated")

        # Initialize database connection
        logger.info("Initializing database connection...")
        try:
            db_connection = DatabaseConnection()
            vector_store = db_connection.get_vector_store()
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to establish database connection: {e}", exc_info=True)
            return 1
        
 
        # Create ingestion pipeline
        logger.info("Creating ingestion pipeline...")
        try:
            pipeline = create_ingestion_pipeline(
                vector_store=vector_store,
                endpoint=AZURE_ENDPOINT_EMBEDDING,
                api_key=AZURE_API_KEY_EMBEDDING,
                deployment=EMBEDDING_DEPLOYMENT_NAME,
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )
            logger.info("Ingestion pipeline created successfully")
        except Exception as e:
            logger.error(f"Failed to create ingestion pipeline: {e}", exc_info=True)
            return 1


        # Load URLs from CSV file
        logger.info("Loading data source URLs from CSV file...")
        csv_path = os.path.join(os.path.dirname(__file__), "data", "URLs.csv")
        website_urls = []
        youtube_urls = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if row['Website-URLS'].strip():
                        website_urls.append(row['Website-URLS'].strip())
                    
                    if row['Youtube-URLS'].strip():
                        youtube_urls.append(row['Youtube-URLS'].strip())
            
            logger.info(f"Found {len(website_urls)} website URLs to process")
            logger.info(f"Found {len(youtube_urls)} YouTube URLs to process")
           
        except FileNotFoundError:
            logger.error(f"CSV file not found at {csv_path}")
            logger.error("Cannot proceed without data source URLs")
            return 1
        except KeyError as e:
            logger.error(f"Missing required column in CSV file: {e}")
            logger.error("Expected columns: 'Website-URLS', 'Youtube-URLS'")
            return 1
        except Exception as e:
            logger.error(f"Failed to read CSV file: {e}", exc_info=True)
            return 1


      
        # Check Google Drive configuration
        if FOLDER_ID:
            logger.info(f"Google Drive folder ID configured: {FOLDER_ID}")
        else:
            logger.warning("No Google Drive folder ID configured - skipping Google Drive documents")

      
        # Get existing documents from database
        logger.info("Checking for existing documents in database...")
        try:
            existing_urls, existing_filepaths = get_existing_identifiers(db_connection)
        except Exception as e:
            logger.warning(f"Failed to retrieve existing identifiers: {e}")
            logger.warning("Proceeding without duplicate filtering")
            existing_urls, existing_filepaths = set(), set()
        
        # Fetch documents from all sources
        logger.info("Fetching documents from all sources...")
        try:
            all_documents = fetch_source_documents(
                youtube_urls=youtube_urls,
                web_urls=website_urls,
                drive_folder_id=FOLDER_ID
            )
            logger.info(f"Total documents fetched: {len(all_documents)}")
        except Exception as e:
            logger.error(f"Failed to fetch documents: {e}", exc_info=True)
            return 1


        # Filter duplicates
        logger.info("Filtering duplicate documents...")
        try:
            new_documents = filter_duplicate_documents(
                all_documents,
                existing_urls,
                existing_filepaths
            )
        except Exception as e:
            logger.error(f"Failed to filter duplicates: {e}", exc_info=True)
            return 1


        # Ingest new documents
        if new_documents:
            logger.info(f"Starting ingestion of {len(new_documents)} new documents...")
            try:
                ingest_documents(new_documents, pipeline)
                logger.info("=" * 70)
                logger.info(f"Pipeline completed successfully!")
                logger.info(f"Total new documents processed: {len(new_documents)}")
                logger.info("=" * 70)
            except Exception as e:
                logger.error(f"Failed to ingest documents: {e}", exc_info=True)
                return 1
        else:
            logger.warning("=" * 70)
            logger.warning("No new documents to ingest")
            logger.warning("All documents already exist in database")
            logger.warning("=" * 70)
        
        return 0

    except RAGPipelineException as e:
        logger.error("=" * 70)
        logger.error(f"Pipeline error: {e}", exc_info=True)
        logger.error("=" * 70)
        return 1
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"Unexpected error occurred: {e}", exc_info=True)
        logger.error("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
