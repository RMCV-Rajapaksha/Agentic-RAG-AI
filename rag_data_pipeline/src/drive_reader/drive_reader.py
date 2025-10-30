"""
Google Drive Document Reader Module

This module provides functionality to load documents from Google Drive using
LlamaIndex's GoogleDriveReader with service account authentication.
"""

# Standard library imports
from pathlib import Path
from typing import List

# Third-party imports
import pypandoc
import pdfplumber
from markdownify import markdownify as md

# LlamaIndex imports
from llama_index.core import Document
from llama_index.readers.google import GoogleDriveReader

# Local imports
from config.config import get_google_credentials_json_path


# ===============================
# Core Functions
# ===============================

def load_google_drive_documents(folder_id: str):
    """
    Load all documents from the specified Google Drive folder.
    
    Args:
        folder_id: Google Drive folder ID
    
    Returns:
        List of Document objects with metadata
    """
    reader = GoogleDriveReader(
        service_account_key_path=get_google_credentials_json_path()
    )
    
    documents = reader.load_data(folder_id=folder_id)

    if not documents:
        print("No documents were found in the specified folder.")
        return []

    print(f"Successfully loaded {len(documents)} document(s) from Google Drive.\n")
    return documents


def preview_document(documents, index: int = 0):
    """
    Print a content snippet and metadata of the specified document.
    
    Args:
        documents: List of documents returned by load_google_drive_documents()
        index: Index of the document to preview (default: 0)
    """
    if not documents:
        print("No documents available to preview.")
        return

    doc = documents[index]
    print("--- Example Document and Metadata ---")
    print(f"Content Snippet: '{doc.get_content()[:150]}...'")
    print(f"Metadata: {doc.metadata}\n")


# ===============================
# Document Converter Class
# ===============================
class LightweightConverter:
    """
    Converter for various document formats to Markdown.
    
    Supports conversion of DOCX, PPTX, ODT, PDF, TXT, and HTML files
    to Markdown format using lightweight libraries.
    """
    
    def convert(self, source: str) -> str:
        """
        Convert document to Markdown using lightweight libraries.
        
        Args:
            source: Path to the source document
            
        Returns:
            Converted Markdown content as string, or empty string on error
        """
        ext = Path(source).suffix.lower()

        try:
            if ext in [".docx", ".pptx", ".odt"]:
                # Use pypandoc for docx/pptx/odt
                return pypandoc.convert_file(
                    source, "md", extra_args=["--wrap=none"]
                )

            elif ext == ".pdf":
                # Extract text from PDF
                text = ""
                with pdfplumber.open(source) as pdf:
                    text = "\n".join(
                        [page.extract_text() or "" for page in pdf.pages]
                    )
                return text

            elif ext == ".txt":
                # Plain text file
                with open(source, "r", encoding="utf-8") as f:
                    return f.read()

            elif ext in [".html", ".htm"]:
                # Convert HTML → Markdown
                with open(source, "r", encoding="utf-8") as f:
                    html_content = f.read()
                return md(html_content)

            else:
                print(f"Unsupported format for {source}")
                return ""

        except Exception as e:
            print(f"Error converting {source}: {e}")
            return ""


def convert_document_to_markdown(source: str) -> str:
    """
    Convert document to Markdown using lightweight converter.
    
    Args:
        source: Path to the source document
        
    Returns:
        Markdown content as string
    """
    converter = LightweightConverter()
    return converter.convert(source)


def load_and_tag_drive_documents(folder_id: str) -> List[Document]:
    """
    Load documents from Google Drive and add metadata tags.
    
    Args:
        folder_id: Google Drive folder ID
        
    Returns:
        List of Document objects with metadata
    """
    documents = load_google_drive_documents(folder_id)
    
    for doc in documents:
        doc.metadata['source'] = 'google_drive'
        doc.metadata['folder_id'] = folder_id
    
    return documents


def convert_drive_documents_to_markdown(folder_id: str) -> List[Document]:
    """
    Load and convert Google Drive documents to markdown.
    
    Args:
        folder_id: Google Drive folder ID
        
    Returns:
        List of Document objects with converted content
    """
    documents = []
    drive_documents = load_google_drive_documents(folder_id)

    for doc in drive_documents:
        if 'file_path' in doc.metadata:
            file_path = doc.metadata['file_path']
            print(f"Converting document from Google Drive: {file_path}")
            markdown_content = convert_document_to_markdown(file_path)

            if markdown_content:
                converted_doc = Document(
                    text=markdown_content,
                    metadata={
                        'source': 'google_drive_converted',
                        'folder_id': folder_id,
                        'original_file_path': file_path,
                        'type': 'converted_document'
                    }
                )
                documents.append(converted_doc)
        else:
            doc.metadata['source'] = 'google_drive'
            doc.metadata['folder_id'] = folder_id
            documents.append(doc)

    return documents


# ===============================
# Example Usage
# ===============================
if __name__ == "__main__":
    # Replace with your actual folder ID
    folder_id = "---"  
    
    docs = load_google_drive_documents(folder_id=folder_id)
    preview_document(docs)
