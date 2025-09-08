import os
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.google import GoogleDriveReader

from config.config import get_config


    # Get configuration instance
config = get_config()

# --- 1. SET UP GOOGLE DRIVE LOADER ---
# Note: Ensure 'credentials.json' is in the same directory.
# The first time you run this, it will prompt you to authenticate in your browser.
p = GoogleDriveReader(service_account_key_path =config.google_credentials_json_path())

# --- 2. LOAD DOCUMENTS FROM A SPECIFIC FOLDER ---
# Replace 'YOUR_FOLDER_ID' with the actual ID of your Google Drive folder.
folder_id = '1fnR7uqkbfI4FaO-wiuKemfTufWBL0k5t' 
documents = p.load_data(folder_id=folder_id)

print(f"Successfully loaded {len(documents)} document(s) from Google Drive.\n")

# --- 3. INSPECT LOADED DOCUMENTS AND METADATA ---
# The loader automatically extracts metadata like file name, creation date, etc.
if documents:
    print("--- Example Document and Metadata ---")
    # Print content snippet of the first document
    print(f"Content Snippet: '{documents[0].get_content()[:150]}...'") 
    # Print all metadata for the first document
    print(f"Metadata: {documents[0].metadata}\n")
else:
    print("No documents were found in the specified folder.")

