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

from database import DatabaseConnection
from src.pipeline import ingest_documents

from src.utils import (
    fetch_source_documents,
    get_existing_identifiers,
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
    3. Filters URLs to find new documents
    4. Fetches only new documents from all sources (YouTube, Web, Google Drive)
    5. Ingests new documents into the vector store
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger.info("=" * 70)
    logger.info("Starting RAG Data Pipeline")
    logger.info("=" * 70)
    
    try:
        
        db_connection = DatabaseConnection()

        
 
        
        # Load URLs from CSV file
        logger.info("Loading data source URLs from CSV file...")
        csv_path = os.path.join(os.path.dirname(__file__), "data", "URLs.csv")
        website_urls = ["https://wso2.com/integration/ai/"]
        youtube_urls = []
        
        # try:
        #     with open(csv_path, 'r', encoding='utf-8') as file:
        #         csv_reader = csv.DictReader(file)
        #         row_count = 0
                
        #         for row in csv_reader:
        #             row_count += 1
                    
        #             # Safely process Website URLs
        #             website_url = row.get('Website-URLS')
        #             if website_url and website_url.strip():
        #                 website_urls.append(website_url.strip())
                    
        #             # Safely process YouTube URLs
        #             youtube_url = row.get('Youtube-URLS')
        #             if youtube_url and youtube_url.strip():
        #                 youtube_urls.append(youtube_url.strip())
            
        #     logger.info(f"Processed {row_count} rows from CSV file")
        #     logger.info(f"Found {len(website_urls)} website URLs to process")
        #     logger.info(f"Found {len(youtube_urls)} YouTube URLs to process")
            
        #     # Validate that we have at least some URLs
        #     if not website_urls and not youtube_urls and not FOLDER_ID:
        #         logger.warning("No URLs found in CSV and no Google Drive folder configured")
        #         logger.warning("Pipeline will have no documents to process")
        #         return 0
           
        # except FileNotFoundError:
        #     logger.error(f"CSV file not found at {csv_path}")
        #     logger.error("Cannot proceed without data source URLs")
        #     return 1
        # except KeyError as e:
        #     logger.error(f"Missing required column in CSV file: {e}")
        #     logger.error("Expected columns: 'Website-URLS', 'Youtube-URLS'")
        #     return 1
        # except Exception as e:
        #     logger.error(f"Failed to read CSV file: {e}", exc_info=True)
        #     return 1


        # Check Google Drive configuration
        if FOLDER_ID:
            logger.info(f"Google Drive folder ID configured: {FOLDER_ID}")
        else:
            logger.warning("No Google Drive folder ID configured - skipping Google Drive documents")

      
        # Get existing documents from database
        logger.info("Checking for existing documents in database...")
        try:
            existing_urls, existing_filepaths = get_existing_identifiers(db_connection)
            logger.info(f"Found {len(existing_urls)} existing URLs in database")
            logger.info(f"Found {len(existing_filepaths)} existing file paths in database")
        except Exception as e:
            logger.warning(f"Failed to retrieve existing identifiers: {e}")
            logger.warning("Proceeding without duplicate filtering")
            existing_urls, existing_filepaths = set(), set()
        
        # Filter URLs before fetching
        logger.info("Filtering URLs to determine new documents...")
        new_youtube_urls = [url for url in youtube_urls if url not in existing_urls]
        new_web_urls = [url for url in website_urls if url not in existing_urls]
        
        logger.info(f"Filtered results:")
        logger.info(f"  YouTube URLs - Total: {len(youtube_urls)}, New: {len(new_youtube_urls)}, Existing: {len(youtube_urls) - len(new_youtube_urls)}")
        logger.info(f"  Web URLs - Total: {len(website_urls)}, New: {len(new_web_urls)}, Existing: {len(website_urls) - len(new_web_urls)}")
        
        # Check if there's anything to fetch
        if not new_youtube_urls and not new_web_urls and not FOLDER_ID:
            logger.warning("=" * 70)
            logger.warning("No new documents to process")
            logger.warning("All URLs already exist in database")
            logger.warning("=" * 70)
            return 0
        
        # Fetch only new documents from filtered sources
        logger.info("Fetching only new documents from sources...")
        all_documents = []
        
        try:
            # For Google Drive, we'll fetch and filter after since we can't pre-filter by URL
            if FOLDER_ID:
                logger.info(f"Fetching Google Drive documents (will filter after)...")
                drive_documents = fetch_source_documents(
                    youtube_urls=[],
                    web_urls=[],
                    drive_folder_id=FOLDER_ID
                )
                # Filter Google Drive documents by file path
                new_drive_documents = [
                    doc for doc in drive_documents 
                    if doc.metadata.get('file_path') not in existing_filepaths 
                    and doc.metadata.get('original_file_path') not in existing_filepaths
                ]
                logger.info(f"Google Drive - Total: {len(drive_documents)}, New: {len(new_drive_documents)}, Existing: {len(drive_documents) - len(new_drive_documents)}")
                all_documents.extend(new_drive_documents)
            
            # Fetch only new YouTube and web documents
            if new_youtube_urls or new_web_urls:
                logger.info("Fetching new YouTube and web documents...")
                new_url_documents = fetch_source_documents(
                    youtube_urls=new_youtube_urls,
                    web_urls=new_web_urls,
                    drive_folder_id=None
                )
                all_documents.extend(new_url_documents)
            
            logger.info(f"Total new documents to ingest: {len(all_documents)}")
            
        except Exception as e:
            logger.error(f"Failed to fetch documents: {e}", exc_info=True)
            return 1


        # Ingest new documents
        if all_documents:
            logger.info(f"Starting ingestion of {len(all_documents)} new documents...")
            try:
                ingest_documents(all_documents)
                logger.info("=" * 70)
                logger.info(f"Pipeline completed successfully!")
                logger.info(f"Total new documents processed: {len(all_documents)}")
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