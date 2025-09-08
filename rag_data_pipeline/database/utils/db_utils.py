#!/usr/bin/env python3
"""
Database utility script for inspecting stored embeddings
"""

import sys
import os
import argparse

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.db import Database
import json


def get_database_stats():
    """Get basic statistics about the database"""
    db = Database()
    
    # Total embeddings
    db.cursor.execute('SELECT COUNT(*) FROM embeddings')
    total_embeddings = db.cursor.fetchone()[0]
    
    # Unique sources
    db.cursor.execute('SELECT COUNT(DISTINCT source) FROM embeddings')
    unique_sources = db.cursor.fetchone()[0]
    
    # Average text length
    db.cursor.execute('SELECT AVG(LENGTH(chunked_text)) FROM embeddings')
    avg_text_length = db.cursor.fetchone()[0]
    
    print(f"📊 Database Statistics")
    print(f"{'='*50}")
    print(f"Total embeddings: {total_embeddings}")
    print(f"Unique sources: {unique_sources}")
    print(f"Average text length: {avg_text_length:.2f} characters")
    
    return {
        'total_embeddings': total_embeddings,
        'unique_sources': unique_sources,
        'avg_text_length': avg_text_length
    }


def list_sources():
    """List all unique sources in the database"""
    db = Database()
    
    db.cursor.execute('SELECT DISTINCT source FROM embeddings ORDER BY source')
    sources = db.cursor.fetchall()
    
    print(f"📋 Sources in Database ({len(sources)} total)")
    print(f"{'='*50}")
    
    for i, (source,) in enumerate(sources, 1):
        db.cursor.execute('SELECT COUNT(*) FROM embeddings WHERE source = %s', (source,))
        count = db.cursor.fetchone()[0]
        print(f"{i:2d}. {source} ({count} chunks)")


def show_sample_embeddings(limit=3):
    """Show sample embeddings with metadata"""
    db = Database()
    
    db.cursor.execute('''
        SELECT chunked_text, metadata, source 
        FROM embeddings 
        ORDER BY RANDOM() 
        LIMIT %s
    ''', (limit,))
    
    samples = db.cursor.fetchall()
    
    print(f"📝 Sample Embeddings ({limit} random samples)")
    print(f"{'='*50}")
    
    for i, (text, metadata, source) in enumerate(samples, 1):
        print(f"\n--- Sample {i} ---")
        print(f"Source: {source}")
        print(f"Metadata: {json.dumps(metadata, indent=2)}")
        print(f"Text (first 200 chars): {text[:200]}...")
        if len(text) > 200:
            print(f"... (total length: {len(text)} chars)")


def search_content(query, limit=5):
    """Search for content containing specific text"""
    db = Database()
    
    db.cursor.execute('''
        SELECT chunked_text, metadata, source 
        FROM embeddings 
        WHERE chunked_text ILIKE %s
        ORDER BY source
        LIMIT %s
    ''', (f'%{query}%', limit))
    
    results = db.cursor.fetchall()
    
    print(f"🔍 Search Results for '{query}' ({len(results)} found)")
    print(f"{'='*50}")
    
    for i, (text, metadata, source) in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Source: {source}")
        
        # Highlight the search term
        highlighted_text = text.replace(query, f"**{query}**")
        print(f"Text (first 300 chars): {highlighted_text[:300]}...")


def source_details(source_url):
    """Show details for a specific source"""
    db = Database()
    
    db.cursor.execute('SELECT * FROM embeddings WHERE source = %s', (source_url,))
    results = db.cursor.fetchall()
    
    if not results:
        print(f"❌ No data found for source: {source_url}")
        return
    
    print(f"📄 Details for: {source_url}")
    print(f"{'='*50}")
    print(f"Total chunks: {len(results)}")
    
    # Show metadata from first chunk
    if results:
        metadata = results[0][3]  # metadata is 4th column (index 3)
        print(f"\nMetadata:")
        print(json.dumps(metadata, indent=2))
    
    # Show all chunk texts
    print(f"\n📝 All Chunks:")
    for i, (chunk_id, vector, text, metadata, source) in enumerate(results, 1):
        print(f"\n--- Chunk {i} (ID: {chunk_id}) ---")
        print(f"Length: {len(text)} characters")
        print(f"Text: {text[:200]}...")


def cleanup_source(source_url):
    """Remove all data for a specific source"""
    db = Database()
    
    # First check if source exists
    db.cursor.execute('SELECT COUNT(*) FROM embeddings WHERE source = %s', (source_url,))
    count = db.cursor.fetchone()[0]
    
    if count == 0:
        print(f"❌ No data found for source: {source_url}")
        return
    
    # Confirm deletion
    response = input(f"⚠️  Are you sure you want to delete {count} embeddings for '{source_url}'? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Deletion cancelled")
        return
    
    # Delete the data
    db.cursor.execute('DELETE FROM embeddings WHERE source = %s', (source_url,))
    print(f"✅ Deleted {count} embeddings for: {source_url}")


def main():
    parser = argparse.ArgumentParser(
        description="Database utility for inspecting stored embeddings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python db_utils.py --stats                    # Show database statistics
  python db_utils.py --list-sources             # List all sources
  python db_utils.py --samples 5                # Show 5 sample embeddings
  python db_utils.py --search "API management"  # Search for specific content
  python db_utils.py --source-details "https://wso2.com/library/blogs/example"
  python db_utils.py --cleanup-source "https://wso2.com/library/blogs/example"
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--stats", action="store_true", help="Show database statistics")
    group.add_argument("--list-sources", action="store_true", help="List all unique sources")
    group.add_argument("--samples", type=int, metavar="N", help="Show N random sample embeddings")
    group.add_argument("--search", type=str, metavar="QUERY", help="Search for content containing text")
    group.add_argument("--source-details", type=str, metavar="URL", help="Show details for specific source")
    group.add_argument("--cleanup-source", type=str, metavar="URL", help="Remove all data for specific source")
    
    args = parser.parse_args()
    
    try:
        if args.stats:
            get_database_stats()
        elif args.list_sources:
            list_sources()
        elif args.samples:
            show_sample_embeddings(args.samples)
        elif args.search:
            search_content(args.search)
        elif args.source_details:
            source_details(args.source_details)
        elif args.cleanup_source:
            cleanup_source(args.cleanup_source)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
