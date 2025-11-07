"""
Google Drive Document Reader Module

This module provides functionality to load documents from Google Drive using
LlamaIndex's GoogleDriveReader with service account authentication.
"""

# Standard library imports
from pathlib import Path
from typing import List
import os
import json
import logging
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Third-party imports
import pypandoc
import pdfplumber
from markdownify import markdownify as md

# LlamaIndex imports
from llama_index.core import Document
from llama_index.readers.google import GoogleDriveReader

# Configure logger
logger = logging.getLogger(__name__)


# ===============================
# Google Credentials Helper
# ===============================

def get_google_credentials_json_path() -> str:
    """
    Create a temporary JSON file with Google service account credentials from environment variables.
    
    Returns:
        Path to temporary JSON file containing credentials
        
    Raises:
        ValueError: If required credentials are missing
    """
    try:
        private_key = os.getenv("GOOGLE_PRIVATE_KEY")
        if private_key:
            # Replace escaped newlines with actual newlines
            private_key = private_key.replace('\\n', '\n')
        
        creds = {
            "type": os.getenv("GOOGLE_TYPE"),
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
            "private_key": private_key,
            "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
            "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
            "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN"),
        }
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w')
        json.dump(creds, temp)
        temp.close()
        logger.info(f"Created temporary credentials file: {temp.name}")
        return temp.name
    except Exception as e:
        logger.error(f"Error creating credentials file: {e}", exc_info=True)
        raise ValueError(f"Failed to create credentials file: {e}")


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
    try:
        reader = GoogleDriveReader(
            service_account_key_path=get_google_credentials_json_path()
        )
        
        documents = reader.load_data(folder_id=folder_id)

        if not documents:
            logger.warning("No documents were found in the specified folder")
            return []

        logger.info(f"Successfully loaded {len(documents)} document(s) from Google Drive")
        return documents
    except Exception as e:
        logger.error(f"Failed to load Google Drive documents: {e}", exc_info=True)
        return []


def preview_document(documents, index: int = 0):
    """
    Print a content snippet and metadata of the specified document.
    
    Args:
        documents: List of documents returned by load_google_drive_documents()
        index: Index of the document to preview (default: 0)
    """
    if not documents:
        logger.warning("No documents available to preview")
        return

    try:
        doc = documents[index]
        logger.info("--- Example Document and Metadata ---")
        logger.info(f"Content Snippet: '{doc.get_content()[:150]}...'")
        logger.info(f"Metadata: {doc.metadata}")
    except IndexError:
        logger.error(f"Invalid document index: {index}")
    except Exception as e:
        logger.error(f"Error previewing document: {e}", exc_info=True)


# ===============================
# Document Converter Functions
# ===============================

def _convert_office_document(source: str) -> str:
    """
    Convert DOCX, PPTX, or ODT files to Markdown using pypandoc.
    
    Args:
        source: Path to the source document
        
    Returns:
        Converted Markdown content as string
    """
    return pypandoc.convert_file(source, "md", extra_args=["--wrap=none"])


def _convert_pdf_document(source: str) -> str:
    """
    Extract text from PDF files.
    
    Args:
        source: Path to the PDF document
        
    Returns:
        Extracted text content as string
    """
    try:
        text = ""
        with pdfplumber.open(source) as pdf:
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {source}: {e}", exc_info=True)
        return ""


def _convert_text_document(source: str) -> str:
    """
    Read plain text files.
    
    Args:
        source: Path to the text document
        
    Returns:
        Text content as string
    """
    try:
        with open(source, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading text file {source}: {e}", exc_info=True)
        return ""


def _convert_html_document(source: str) -> str:
    """
    Convert HTML files to Markdown.
    
    Args:
        source: Path to the HTML document
        
    Returns:
        Converted Markdown content as string
    """
    try:
        with open(source, "r", encoding="utf-8") as f:
            html_content = f.read()
        return md(html_content)
    except Exception as e:
        logger.error(f"Error converting HTML file {source}: {e}", exc_info=True)
        return ""


def convert_document_to_markdown(source: str) -> str:
    """
    Convert document to Markdown based on file extension.
    
    Supports conversion of DOCX, PPTX, ODT, PDF, TXT, and HTML files
    to Markdown format using lightweight libraries.
    
    Args:
        source: Path to the source document
        
    Returns:
        Converted Markdown content as string, or empty string on error
    """
    ext = Path(source).suffix.lower()

    try:
        if ext in [".docx", ".pptx", ".odt"]:
            return _convert_office_document(source)
        elif ext == ".pdf":
            return _convert_pdf_document(source)
        elif ext == ".txt":
            return _convert_text_document(source)
        elif ext in [".html", ".htm"]:
            return _convert_html_document(source)
        else:
            logger.warning(f"Unsupported file format: {ext} for {source}")
            return ""
    except Exception as e:
        logger.error(f"Error converting {source}: {e}", exc_info=True)
        return ""


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
            logger.info(f"Converting document from Google Drive: {file_path}")
            markdown_content = convert_document_to_markdown(file_path)

            if markdown_content:
                # Create a unique identifier using file_path or file_name
                file_name = doc.metadata.get('file_name', Path(file_path).name)
                
                converted_doc = Document(
                    text=markdown_content,
                    metadata={
                        'source': 'google_drive_converted',
                        'folder_id': folder_id,
                        'original_file_path': file_path,
                        'file_name': file_name,
                        'type': 'converted_document',
                        'url': f"gdrive://{folder_id}/{file_name}"
                    }
                )
                documents.append(converted_doc)
            else:
                logger.warning(f"Failed to convert document: {file_path}")
        else:
            # For documents without file_path, add metadata
            file_name = doc.metadata.get('file_name', 'unknown')
            doc.metadata['source'] = 'google_drive'
            doc.metadata['folder_id'] = folder_id
            # Add URL-like identifier for duplicate checking
            doc.metadata['url'] = f"gdrive://{folder_id}/{file_name}"
            documents.append(doc)

    logger.info(f"Converted {len(documents)} documents from Google Drive")
    return documents


if __name__ == "__main__":
    # Replace with your actual folder ID
    folder_id = "---"  
    
    docs = load_google_drive_documents(folder_id=folder_id)
    preview_document(docs)
