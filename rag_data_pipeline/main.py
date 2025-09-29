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
from src.youtube_transcripts.youtube_transcript_to_md import YouTubeTranscriptScraper
from src.scraper.web_scraper import WebScraper
from src.drive_reader.drive_reader import GoogleDriveLoader
from config.config import get_config

import os
from typing import List
import re

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
        self.document_converter = DocumentConverter()
        self.youtube_scraper = YouTubeTranscriptScraper()

        
       
        self.vector_store = self.db_connection.get_vector_store()
        

        self.pipeline = IngestionPipeline(
            transformations=[
           
                MarkdownNodeParser(chunk_size=512, chunk_overlap=100,include_metadata=True,include_prev_next_rel=True),
                TitleExtractor(),
                OpenAIEmbedding(model="text-embedding-3-small", embed_dim=1536),
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
        
        
        for doc in documents:
            doc.metadata['source'] = 'google_drive'
            doc.metadata['folder_id'] = folder_id
            
        return documents
    
    def convert_drive_documents_to_markdown(self, folder_id: str) -> List[Document]:
        """Load documents from Google Drive folder and convert to markdown using Docling"""
        documents = []
        

        drive_documents = self.drive_loader.load_documents(folder_id)
        
        for doc in drive_documents:
          
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
                
                doc.metadata['source'] = 'google_drive'
                doc.metadata['folder_id'] = folder_id
                documents.append(doc)
                
        return documents
    
    def process_youtube_videos(self, urls: List[str]) -> List[Document]:
        """Process YouTube videos and return Documents with transcript segments"""
        documents = []
        
        print("Processing YouTube videos for transcript segments...")
        for link in urls:
            try:
                video_data = self.youtube_scraper.get_transcript_segments(link)
               
                # Create a document for each segment with timestamp metadata
                for i, segment in enumerate(video_data['segments']):
                    video_doc = Document(
                        text=segment['content_markdown'],
                        metadata={
                            'url': video_data['url'],
                            'title': video_data['metadata'].get('title', ''),
                            'description': video_data['metadata'].get('description', ''),
                            'source': 'youtube_transcript',
                            'start_seconds': segment['start_seconds'],
                            'end_seconds': segment['end_seconds'],
                        }
                    )
                    documents.append(video_doc)
                    
                print(f"Processed {len(video_data['segments'])} segments from: {video_data['metadata'].get('title', link)}")
                
            except Exception as e:
                print(f"Error processing YouTube video {link}: {e}")
                
        return documents
    
   
    def ingest_documents(self, documents: List[Document]) -> None:
        """Process and ingest documents into the vector database, skipping chunks with duplicate URLs."""
        if not documents:
            return

        
        filtered_documents = []
        try:
           
            existing_urls = set()
            try:
                
                all_nodes = self.vector_store._get_all() if hasattr(self.vector_store, '_get_all') else []
                for node in all_nodes:
                    url = node.metadata.get('url') if hasattr(node, 'metadata') and node.metadata else None
                    if url:
                        existing_urls.add(url)
            except Exception as e:
                print(f"Warning: Could not fetch existing URLs from vector store: {e}")

            for doc in documents:
                url = doc.metadata.get('url') if doc.metadata else None
                if url and url in existing_urls:
                    print(f"Skipping document with duplicate URL: {url}")
                    continue
                filtered_documents.append(doc)
        except Exception as e:
            print(f"Error during duplicate URL filtering: {e}")
            filtered_documents = documents

        if not filtered_documents:
            print("No new documents to ingest after duplicate URL filtering.")
            return

        self.pipeline.run(documents=filtered_documents, show_progress=True)


def main():
    """
    Main function - ingests data from web URLs and Google Drive into database
    """

    pipeline = RAGDataIngestion()
    

    urls_to_scrape = [
        "https://wso2.ai/",
        "https://wso2.com/api-management/ai/",
        "https://wso2.com/integration/ai/",
        "https://wso2.com/identity-and-access-management/ai/",
        "https://wso2.com/internal-developer-platform/ai/"
    ]


    urls_to_videos =[
        # "https://www.youtube.com/watch?v=LtcHVLkkxjk",
        # "https://www.youtube.com/watch?v=GoYR-iK2UUk",
        # "https://www.youtube.com/watch?v=-nwIoiPB8CE",
        # "https://www.youtube.com/watch?v=X5eC3Rk9FBQ",
        # "https://www.youtube.com/watch?v=wobNffok7nc",
        # "https://www.youtube.com/watch?v=EW9BR4Gkh6Y",
        # "https://www.youtube.com/watch?v=Va9s2Gkxx9Y",
        # "https://www.youtube.com/watch?v=D9omNKy1n0M",
        # "https://www.youtube.com/watch?v=LVZHCSNrF10",
        # "https://www.youtube.com/watch?v=3GaOnj_Gsco",
        # "https://www.youtube.com/watch?v=f4wEL3yOO-g",
        # "https://www.youtube.com/watch?v=bzSgEjpcijY",
        ""
    ]
   
    drive_folder_id = "config.google_drive_folder_id"
    
    try:
        all_documents = []

        if urls_to_videos:
            youtube_documents = pipeline.process_youtube_videos(urls_to_videos)
            all_documents.extend(youtube_documents)

        if urls_to_scrape:
            url_documents = pipeline.scrape_web_urls(urls_to_scrape)
            all_documents.extend(url_documents)
        
        if drive_folder_id:
            print("Loading and converting Google Drive documents...")
            drive_documents = pipeline.convert_drive_documents_to_markdown(drive_folder_id)
            print(f"-----------Loaded and converted {len(drive_documents)} documents from Google Drive.")
            all_documents.extend(drive_documents)
        
        
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