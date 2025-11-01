from database.db import DatabaseConnection
import json

db = DatabaseConnection()

# Get all data along with URLs and file paths
all_data, urls, filepaths = db.get_all_metadata()

# Parse metadata if it's a string
for record in all_data:
    if isinstance(record['metadata'], str):
        try:
            record['metadata'] = json.loads(record['metadata'])
        except json.JSONDecodeError:
            record['metadata'] = {}

# Extract unique URLs
unique_urls = urls if urls else {r['metadata'].get('url') for r in all_data if r['metadata'].get('url')}
print("=== UNIQUE URLs ===")
for idx, url in enumerate(sorted(unique_urls), 1):
    print(f"{idx}. {url}")

# Extract unique file paths
unique_filepaths = filepaths if filepaths else {r['metadata'].get('file path') for r in all_data if r['metadata'].get('file path')}
print("\n=== UNIQUE FILE PATHS ===")
for idx, filepath in enumerate(sorted(unique_filepaths), 1):
    print(f"{idx}. {filepath}")

print(f"\nTotal unique URLs: {len(unique_urls)}")
print(f"Total unique file paths: {len(unique_filepaths)}")