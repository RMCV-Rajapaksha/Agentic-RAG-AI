"""
Document Utilities Module

This module provides utility functions for:
- Retrieving existing document identifiers from the database
- Filtering duplicate documents
- Fetching documents from multiple sources (YouTube, Web, Google Drive)
"""

import json
import logging
from typing import List, Optional, Set, Tuple

from llama_index.core import Document

from database.db import DatabaseConnection
from src.drive_reader.drive_reader import convert_drive_documents_to_markdown
from src.scraper.web_scraper import scrape_web_urls
from src.youtube_transcripts.youtube_transcript_to_md import process_youtube_videos

# Configure logger
logger = logging.getLogger(__name__)


def get_existing_identifiers(
    db_connection: DatabaseConnection
) -> Tuple[Set[str], Set[str]]:
    """
    Get existing URLs and file paths from the database.
    
    Args:
        db_connection: Database connection instance
        
    Returns:
        Tuple of (existing_urls, existing_filepaths)
    """
    logger.info("Checking existing documents in database...")
    
    try:
        all_data, urls, filepaths = db_connection.get_all_metadata()
        
        # Parse metadata if it's a string
        for record in all_data:
            if isinstance(record['metadata'], str):
                try:
                    record['metadata'] = json.loads(record['metadata'])
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse metadata for record {record.get('id')}")
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
        
        logger.info(f"Found {len(existing_urls)} existing URLs")
        logger.info(f"Found {len(existing_filepaths)} existing file paths")
        
        return existing_urls, existing_filepaths
        
    except Exception as e:
        logger.error(f"Error fetching existing data: {e}", exc_info=True)
        logger.warning("Proceeding without duplicate filtering...")
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
            logger.debug(f"Skipping duplicate URL: {doc_url}")
        
        if doc_filepath and doc_filepath in existing_filepaths:
            is_duplicate = True
            logger.debug(f"Skipping duplicate file: {doc_filepath}")
        
        if is_duplicate:
            duplicates_count += 1
        else:
            new_documents.append(doc)
    
    logger.info(f"Filtering Results:")
    logger.info(f"  Total documents: {len(documents)}")
    logger.info(f"  Duplicates filtered: {duplicates_count}")
    logger.info(f"  New documents to ingest: {len(new_documents)}")
    
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
        logger.info(f"Processing {len(youtube_urls)} YouTube videos...")
        try:
            youtube_documents = process_youtube_videos(youtube_urls)
            all_documents.extend(youtube_documents)
            logger.info(f"Loaded {len(youtube_documents)} YouTube documents")
        except Exception as e:
            logger.error(f"Failed to process YouTube videos: {e}", exc_info=True)

    # Scrape web URLs
    if web_urls:
        logger.info(f"Processing {len(web_urls)} web URLs...")
        try:
            url_documents = scrape_web_urls(web_urls)
            all_documents.extend(url_documents)
            logger.info(f"Loaded {len(url_documents)} web documents")
        except Exception as e:
            logger.error(f"Failed to scrape web URLs: {e}", exc_info=True)

    # Load Google Drive documents
    if drive_folder_id:
        logger.info(f"Processing Google Drive documents from folder: {drive_folder_id}")
        try:
            drive_documents = convert_drive_documents_to_markdown(drive_folder_id)
            all_documents.extend(drive_documents)
            logger.info(f"Loaded {len(drive_documents)} Google Drive documents")
        except Exception as e:
            logger.error(f"Failed to load Google Drive documents: {e}", exc_info=True)

    return all_documents
