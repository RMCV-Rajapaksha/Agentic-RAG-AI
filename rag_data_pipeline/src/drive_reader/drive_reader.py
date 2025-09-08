import os
from llama_index.readers.google import GoogleDriveReader
from config.config import get_config


class GoogleDriveLoader:
    """
    A class to load documents from a Google Drive folder using LlamaIndex's GoogleDriveReader.
    """

    def __init__(self):
        
        self.config = get_config()
        
        self.reader = GoogleDriveReader(
            service_account_key_path=self.config.google_credentials_json_path()
        )

    def load_documents(self, folder_id: str):
        """
        Loads all documents from the specified Google Drive folder.
        
        Args:
            folder_id (str): Google Drive folder ID.
        
        Returns:
            List of Document objects with metadata.
        """
        documents = self.reader.load_data(folder_id=folder_id)

        if not documents:
            print("No documents were found in the specified folder.")
            return []

        print(f"Successfully loaded {len(documents)} document(s) from Google Drive.\n")
        return documents

    def preview_document(self, documents, index: int = 0):
        """
        Prints a content snippet and metadata of the specified document.
        
        Args:
            documents (list): List of documents returned by load_documents().
            index (int): Index of the document to preview (default: 0).
        """
        if not documents:
            print("No documents available to preview.")
            return

        doc = documents[index]
        print("--- Example Document and Metadata ---")
        print(f"Content Snippet: '{doc.get_content()[:150]}...'")
        print(f"Metadata: {doc.metadata}\n")


# Example Usage
if __name__ == "__main__":
    folder_id = "1fnR7uqkbfI4FaO-wiuKemfTufWBL0k5t"  # Replace with your folder ID
    
    loader = GoogleDriveLoader()
    docs = loader.load_documents(folder_id=folder_id)
    loader.preview_document(docs)
