"""
Test script to verify print statements work correctly
"""

# Test basic prints
print("=" * 70)
print("Starting RAG Data Pipeline")
print("=" * 70)

# Test with variables
website_urls = ["https://wso2.ai/"]
youtube_urls = []
print(f"Found {len(website_urls)} website URLs to process")
print(f"Found {len(youtube_urls)} YouTube URLs to process")

# Test warnings
print("WARNING: No Google Drive folder ID configured")

# Test errors
try:
    raise Exception("Test error")
except Exception as e:
    print("=" * 70)
    print(f"ERROR: Unexpected error occurred: {e}")
    print("=" * 70)

print("All print statements work correctly!")
