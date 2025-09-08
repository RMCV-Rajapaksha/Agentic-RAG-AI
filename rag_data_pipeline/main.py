# from config.config import get_config

# def main():
#     print("Hello from agentic-rag!")
    
#     # Get configuration instance
#     config = get_config()

#     # Access Database name
#     db_name = config.db_name
#     print(f"Database Name loaded: {'Yes' if db_name else 'No'}")

#     # You can also get other environment variables
#     # custom_var = config.get_env_var('CUSTOM_VAR', 'default_value')

# if __name__ == "__main__":
#     main()



# from database.db import Database
# import numpy as np

# db = Database()

# # Example 768-dim vector
# vector = np.random.rand(1536).tolist()

# chunked_text = "This is a test chunk."
# metadata = {"page": 1, "document": "sample.pdf"}
# source = "pdf"

# db.insert_embedding(vector, chunked_text, metadata, source)

# print("✅ Data inserted!")


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


# --- 4. CHUNK THE DOCUMENTS USING A NODE PARSER ---
# A Node represents a "chunk" of a source Document.
# Here, we use SentenceSplitter to chunk documents into smaller pieces.
parser = SentenceSplitter(
    chunk_size=512,  # The size of each chunk in tokens
    chunk_overlap=50 # The overlap between chunks
)

# This process creates 'Nodes' from the 'Documents'
nodes = parser.get_nodes_from_documents(documents)

print(f"--- Document Chunking ---")
print(f"Split {len(documents)} document(s) into {len(nodes)} nodes (chunks).\n")


# --- 5. INSPECT THE CHUNKS (NODES) ---
# Each node contains the chunked text and inherits the metadata from its parent document.
if nodes:
    print("--- Example Node (Chunk) ---")
    # Print the text content of the first node
    print(f"Node Content: '{nodes[0].get_content()}'")
    # Print the metadata of the first node
    print(f"Node Metadata: {nodes[0].metadata}")