"""
Test script to verify duplication handling in the RAG data pipeline.
"""

from database.db import DatabaseConnection
from llama_index.core import Document

def test_duplication_handling():
    """Test the duplication checking functionality."""
    
    print("=" * 60)
    print("Testing Duplication Handling")
    print("=" * 60)
    
    # Initialize database connection
    db_connection = DatabaseConnection()
    
    # Get existing data
    print("\n1. Fetching existing data from database...")
    existing_urls = db_connection.get_existing_urls()
    existing_file_paths = db_connection.get_existing_file_paths()
    
    print(f"   ✅ Found {len(existing_urls)} existing URLs")
    print(f"   ✅ Found {len(existing_file_paths)} existing file paths")
    
    if existing_urls:
        print(f"\n   Sample URLs (first 3):")
        for url in list(existing_urls)[:3]:
            print(f"   - {url}")
    
    if existing_file_paths:
        print(f"\n   Sample file paths (first 3):")
        for path in list(existing_file_paths)[:3]:
            print(f"   - {path}")
    
    # Create test documents (mix of duplicates and new)
    print("\n2. Creating test documents...")
    test_documents = []
    
    # Add a duplicate URL document if we have existing URLs
    if existing_urls:
        duplicate_url = list(existing_urls)[0]
        test_documents.append(Document(
            text="This is a duplicate document",
            metadata={
                'url': duplicate_url,
                'source': 'test',
                'title': 'Duplicate Test'
            }
        ))
        print(f"   Created duplicate URL document: {duplicate_url}")
    
    # Add a new URL document
    test_documents.append(Document(
        text="This is a new document",
        metadata={
            'url': 'https://example.com/new-test-page',
            'source': 'test',
            'title': 'New Test Document'
        }
    ))
    print(f"   Created new URL document: https://example.com/new-test-page")
    
    # Add a duplicate file path document if we have existing file paths
    if existing_file_paths:
        duplicate_path = list(existing_file_paths)[0]
        test_documents.append(Document(
            text="This is a duplicate Google Drive file",
            metadata={
                'original_file_path': duplicate_path,
                'source': 'google_drive_converted',
                'file_name': 'duplicate_test.pdf'
            }
        ))
        print(f"   Created duplicate file path document: {duplicate_path}")
    
    # Add a new file path document
    test_documents.append(Document(
        text="This is a new Google Drive file",
        metadata={
            'original_file_path': '/tmp/new_test_file.pdf',
            'source': 'google_drive_converted',
            'file_name': 'new_test.pdf'
        }
    ))
    print(f"   Created new file path document: /tmp/new_test_file.pdf")
    
    print(f"\n   Total test documents created: {len(test_documents)}")
    
    # Test duplication filtering
    print("\n3. Testing duplication filtering...")
    filtered_docs = db_connection.filter_duplicate_documents(test_documents)
    
    print(f"\n   ✅ Filtered documents: {len(filtered_docs)} out of {len(test_documents)}")
    
    # Show which documents passed the filter
    print("\n4. Documents that passed the filter:")
    for i, doc in enumerate(filtered_docs, 1):
        metadata = doc.metadata
        url = metadata.get('url', 'N/A')
        file_path = metadata.get('original_file_path', 'N/A')
        print(f"\n   Document {i}:")
        print(f"   - URL: {url}")
        print(f"   - File Path: {file_path}")
        print(f"   - Source: {metadata.get('source', 'N/A')}")
        print(f"   - Title: {metadata.get('title', metadata.get('file_name', 'N/A'))}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    duplicates_filtered = len(test_documents) - len(filtered_docs)
    print(f"✅ Successfully filtered {duplicates_filtered} duplicate(s)")
    print(f"✅ {len(filtered_docs)} new document(s) ready for ingestion")
    print("=" * 60)
    
    return filtered_docs


if __name__ == "__main__":
    try:
        test_duplication_handling()
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
