# Core LlamaIndex imports
from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import  MarkdownNodeParser
from llama_index.core.extractors import TitleExtractor
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.schema import TransformComponent




# Docling imports
from docling.document_converter import DocumentConverter

# Local imports
from database.db import DatabaseConnection
from src.scraper.web_scraper import WebScraper
from src.drive_reader.drive_reader import GoogleDriveLoader
from config.config import get_config

import os
from typing import List
import re

# Set OpenAI API key from config
config = get_config()
os.environ["OPENAI_API_KEY"] = config.openai_api_key

class WhitespaceCleaner(TransformComponent):
    """
    A transformation that removes redundant whitespace from the text content of nodes.
    It collapses multiple spaces, tabs, and newlines into a single space.
    """
    def __call__(self, nodes, **kwargs):
        for node in nodes:
            # Use regex to replace any sequence of whitespace chars with a single space
            cleaned_text = re.sub(r'\s+', ' ', node.get_content()).strip()
            node.set_content(cleaned_text)
        return nodes


class RAGDataIngestion:
    """
    RAG data ingestion pipeline - ingests web URLs and Google Drive data into database
    """
    
    def __init__(self):
        self.config = get_config()
        self.db_connection = DatabaseConnection()
        self.web_scraper = WebScraper()
        self.drive_loader = GoogleDriveLoader()
        self.document_converter = DocumentConverter()
        
        # Initialize database
        self.db_connection.create_database_if_not_exists()
        self.vector_store = self.db_connection.get_vector_store()
        
        # Create ingestion pipeline
        self.pipeline = IngestionPipeline(
            transformations=[
                WhitespaceCleaner(),
                MarkdownNodeParser(chunk_size=512, chunk_overlap=100,include_metadata=True,include_prev_next_rel=True),
                TitleExtractor(),
                OpenAIEmbedding(),
            ],
            vector_store=self.vector_store,
        )
        
    def convert_document_to_markdown(self, source: str) -> str:
        """
        Convert a document (local path or URL) to Markdown using Docling.
        Returns the Markdown string.
        """
        try:
            result = self.document_converter.convert(source)
            return result.document.export_to_markdown()
        except Exception as e:
            print(f"Error converting document {source} to markdown: {e}")
            return ""
        

        
    def scrape_web_urls(self, urls: List[str]) -> List[Document]:
        """Scrape web URLs and return Documents with markdown content"""
        documents = []
        



        print("Scraping web URLs for markdown content...")
        for url in urls:
            scraped_data = self.web_scraper.get_markdown(url)
            if scraped_data:
                doc = Document(
                    text=scraped_data['content_markdown'],
                    metadata={
                        'url': scraped_data['url'],
                        'title': scraped_data['metadata']['title'],
                        'description': scraped_data['metadata']['description'],
                        'source': 'web_scraper'
                    }
                )
                documents.append(doc)
        
        return documents
        
    def load_drive_documents(self, folder_id: str) -> List[Document]:
        """Load documents from Google Drive folder"""
        documents = self.drive_loader.load_documents(folder_id)
        
        # Add source metadata
        for doc in documents:
            doc.metadata['source'] = 'google_drive'
            doc.metadata['folder_id'] = folder_id
            
        return documents
    
    def convert_drive_documents_to_markdown(self, folder_id: str) -> List[Document]:
        """Load documents from Google Drive folder and convert to markdown using Docling"""
        documents = []
        
        # Get document paths from Google Drive
        drive_documents = self.drive_loader.load_documents(folder_id)
        
        for doc in drive_documents:
            # If the document has a file path, convert it using Docling
            if 'file_path' in doc.metadata:
                file_path = doc.metadata['file_path']
                print(f"Converting document from Google Drive: {file_path}")
                markdown_content = self.convert_document_to_markdown(file_path)
                
                if markdown_content:
                    converted_doc = Document(
                        text=markdown_content,
                        metadata={
                            'source': 'google_drive_docling',
                            'folder_id': folder_id,
                            'original_file_path': file_path,
                            'type': 'converted_document'
                        }
                    )
                    documents.append(converted_doc)
            else:
                # Fallback to original document if no file path
                doc.metadata['source'] = 'google_drive'
                doc.metadata['folder_id'] = folder_id
                documents.append(doc)
                
        return documents
    
   
    def ingest_documents(self, documents: List[Document]) -> None:
        """Process and ingest documents into the vector database"""
        if not documents:
            return
            
        # Run the ingestion pipeline
        self.pipeline.run(documents=documents, show_progress=True)


def main():
    """
    Main function - ingests data from web URLs and Google Drive into database
    """
    # Initialize pipeline
    pipeline = RAGDataIngestion()
    
    # URLs to scrape (replace with your actual URLs)
    urls_to_scrape = [
        "https://wso2.ai/",
        "https://wso2.com/api-management/ai/",
        "https://wso2.com/integration/ai/",
        "https://wso2.com/identity-and-access-management/ai/",
        "https://wso2.com/internal-developer-platform/ai/"
    ]
   
    drive_folder_id = config.google_drive_folder_id
    
    try:
        all_documents = []
        
        # Scrape web URLs and get markdown content
        if urls_to_scrape:
            url_documents = pipeline.scrape_web_urls(urls_to_scrape)
            all_documents.extend(url_documents)
        
        # Load documents from Google Drive (with Docling conversion)
        if drive_folder_id:
            print("Loading and converting Google Drive documents...")
            drive_documents = pipeline.convert_drive_documents_to_markdown(drive_folder_id)
            print(f"-----------Loaded and converted {len(drive_documents)} documents from Google Drive.")
            all_documents.extend(drive_documents)
        
        # Ingest all documents
        if all_documents:
            print(f"Ingesting {len(all_documents)} documents...")
            pipeline.ingest_documents(all_documents)
            print("Data ingestion completed successfully!")
        else:
            print("No documents to ingest.")
        
    except Exception as e:
        print(f"An error occurred during data ingestion: {e}")


if __name__ == "__main__":
    main()