# Core LlamaIndex imports
from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.embeddings.openai import OpenAIEmbedding

# Local imports
from database.db import DatabaseConnection
from src.scraper.web_scraper import WebScraper
from src.drive_reader.drive_reader import GoogleDriveLoader
from config.config import get_config

import os
from typing import List

# Set OpenAI API key from config
config = get_config()
os.environ["OPENAI_API_KEY"] = config.openai_api_key


class RAGDataIngestion:
    """
    RAG data ingestion pipeline - ingests web URLs and Google Drive data into database
    """
    
    def __init__(self):
        self.config = get_config()
        self.db_connection = DatabaseConnection()
        self.web_scraper = WebScraper()
        self.drive_loader = GoogleDriveLoader()
        
        # Initialize database
        self.db_connection.create_database_if_not_exists()
        self.vector_store = self.db_connection.get_vector_store()
        
        # Create ingestion pipeline
        self.pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(chunk_size=512, chunk_overlap=100),
                TitleExtractor(),
                OpenAIEmbedding(),
            ],
            vector_store=self.vector_store,
        )
        
    def scrape_urls_to_documents(self, urls: List[str]) -> List[Document]:
        """Scrape URLs and convert to Documents"""
        documents = []
        
        for url in urls:
            scraped_data = self.web_scraper.get_markdown(url)
            
            if scraped_data:
                doc = Document(
                    text=scraped_data['content_markdown'],
                    metadata={

                        'url': scraped_data['url'],
                        'title': scraped_data['metadata']['title'],
                        'description': scraped_data['metadata']['description']
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
        # Load documents from both sources
        url_documents = pipeline.scrape_urls_to_documents(urls_to_scrape)
        drive_documents = pipeline.load_drive_documents(drive_folder_id)
        
        # Combine and ingest all documents
        all_documents = url_documents + drive_documents
        pipeline.ingest_documents(all_documents)
        
        print("Data ingestion completed successfully!")
        
    except Exception as e:
        print(f"An error occurred during data ingestion: {e}")


if __name__ == "__main__":
    main()