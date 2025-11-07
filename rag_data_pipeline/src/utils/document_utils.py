"""
Document Utilities Module

This module provides utility functions for:
- Retrieving existing document identifiers from the database
- Filtering duplicate documents
- Fetching documents from multiple sources (YouTube, Web, Google Drive)
"""

import json
from typing import List, Optional, Set, Tuple

from llama_index.core import Document

from database.db import DatabaseConnection
from src.drive_reader.drive_reader import convert_drive_documents_to_markdown
from src.scraper.web_scraper import scrape_web_urls
from src.youtube_transcripts.youtube_transcript_to_md import process_youtube_videos


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
        
        print(f"Found {len(existing_urls)} existing URLs")
        print(f"Found {len(existing_filepaths)} existing file paths")
        
        return existing_urls, existing_filepaths
        
    except Exception as e:
        print(f"Error fetching existing data: {e}")
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
            print(f"Skipping duplicate URL: {doc_url}")
        
        if doc_filepath and doc_filepath in existing_filepaths:
            is_duplicate = True
            print(f"Skipping duplicate file: {doc_filepath}")
        
        if is_duplicate:
            duplicates_count += 1
        else:
            new_documents.append(doc)
    
    print(f"\n Filtering Results:")
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
        print(f"Loaded {len(youtube_documents)} YouTube documents.")

    # Scrape web URLs
    if web_urls:
        print(f"\n🌐 Processing web URLs...")
        url_documents = scrape_web_urls(web_urls)
        all_documents.extend(url_documents)
        print(f"Loaded {len(url_documents)} web documents.")

    # Load Google Drive documents
    if drive_folder_id:
        print(f"\n Processing Google Drive documents...")
        drive_documents = convert_drive_documents_to_markdown(drive_folder_id)
        all_documents.extend(drive_documents)
        print(f"Loaded {len(drive_documents)} Google Drive documents.")

    return all_documents
