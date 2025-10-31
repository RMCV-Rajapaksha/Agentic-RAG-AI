from database.db import DatabaseConnection
import json

db = DatabaseConnection()

# Get all data along with URLs and file paths
all_data, urls, filepaths = db.get_all_metadata()

print(f"Found {len(all_data)} records in the database.")
print(f"Found {len(urls)} unique URLs.")
print(f"Found {len(filepaths)} unique file paths.")

# Parse metadata if it's a string
for record in all_data:
    if isinstance(record['metadata'], str):
        try:
            record['metadata'] = json.loads(record['metadata'])
        except json.JSONDecodeError:
            record['metadata'] = {}

print("\n" + "="*80)
print("=== UNIQUE URLs (Web Scraper Sources) ===")
print("="*80)
if urls:
    for idx, url in enumerate(sorted(urls), 1):
        print(f"{idx}. {url}")
else:
    # Extract URLs manually if not found by db method
    urls_set = set()
    for record in all_data:
        if record['metadata'].get('url'):
            urls_set.add(record['metadata']['url'])
    
    for idx, url in enumerate(sorted(urls_set), 1):
        print(f"{idx}. {url}")

print("\n" + "="*80)
print("=== UNIQUE FILE PATHS (Google Drive Sources) ===")
print("="*80)
if filepaths:
    for idx, filepath in enumerate(sorted(filepaths), 1):
        print(f"{idx}. {filepath}")
else:
    # Extract file paths manually if not found by db method
    filepaths_set = set()
    for record in all_data:
        if record['metadata'].get('file path'):
            filepaths_set.add(record['metadata']['file path'])
    
    for idx, filepath in enumerate(sorted(filepaths_set), 1):
        print(f"{idx}. {filepath}")

print("\n" + "="*80)
print("=== RECORDS WITH URLs ===")
print("="*80)
url_records = [r for r in all_data if r['metadata'].get('url')]
for idx, record in enumerate(url_records, 1):
    metadata = record['metadata']
    print(f"\n{idx}. Record ID: {record['id']}")
    print(f"   URL: {metadata.get('url')}")
    print(f"   Title: {metadata.get('title', 'N/A')}")
    print(f"   Source: {metadata.get('source', 'N/A')}")
    print(f"   Document Title: {metadata.get('document_title', 'N/A')}")

print("\n" + "="*80)
print("=== RECORDS WITH FILE PATHS ===")
print("="*80)
filepath_records = [r for r in all_data if r['metadata'].get('file path')]
for idx, record in enumerate(filepath_records, 1):
    metadata = record['metadata']
    print(f"\n{idx}. Record ID: {record['id']}")
    print(f"   File Path: {metadata.get('file path')}")
    print(f"   File Name: {metadata.get('file_name', 'N/A')}")
    print(f"   Source: {metadata.get('source', 'N/A')}")
    print(f"   Document Title: {metadata.get('document_title', 'N/A')}")
    print(f"   Page Label: {metadata.get('page_label', 'N/A')}")

print("\n" + "="*80)
print("=== SUMMARY ===")
print("="*80)
print(f"Total Records: {len(all_data)}")
print(f"Records with URLs: {len(url_records)}")
print(f"Records with File Paths: {len(filepath_records)}")
urls_count = len(urls) if urls else len({r['metadata'].get('url') for r in all_data if r['metadata'].get('url')})
filepaths_count = len(filepaths) if filepaths else len({r['metadata'].get('file path') for r in all_data if r['metadata'].get('file path')})
print(f"Unique URLs: {urls_count}")
print(f"Unique File Paths: {filepaths_count}")