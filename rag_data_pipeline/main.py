# Core LlamaIndex imports
from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.extractors import TitleExtractor
from llama_index.embeddings.openai import OpenAIEmbedding

# Local imports
from database.db import DatabaseConnection
from src.youtube_transcripts.youtube_transcript_to_md import YouTubeTranscriptScraper
from src.scraper.web_scraper import WebScraper
from src.drive_reader.drive_reader import GoogleDriveLoader
from config.config import get_config

# Standard imports
import os
from typing import List
from pathlib import Path

# External lightweight libraries
import pypandoc
import pdfplumber
from docx import Document as DocxDocument
from markdownify import markdownify as md



class LightweightConverter:
    def convert(self, source: str) -> str:
        """Convert document to Markdown using lightweight libraries."""
        ext = Path(source).suffix.lower()

        try:
            if ext in [".docx", ".pptx", ".odt"]:
                # Use pypandoc for docx/pptx/odt
                return pypandoc.convert_file(source, "md", extra_args=["--wrap=none"])

            elif ext == ".pdf":
                # Extract text from PDF
                text = ""
                with pdfplumber.open(source) as pdf:
                    text = "\n".join([page.extract_text() or "" for page in pdf.pages])
                return text

            elif ext == ".txt":
                # Plain text file
                with open(source, "r", encoding="utf-8") as f:
                    return f.read()

            elif ext == ".html" or ext == ".htm":
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


# ===============================
# Main Ingestion Class
# ===============================
class RAGDataIngestion:
    """
    RAG data ingestion pipeline - ingests web URLs, Google Drive docs, and YouTube transcripts into DB
    """

    def __init__(self):
        self.config = get_config()
        self.db_connection = DatabaseConnection()
        self.web_scraper = WebScraper()
        self.drive_loader = GoogleDriveLoader()
        self.youtube_scraper = YouTubeTranscriptScraper()

        self.document_converter = LightweightConverter
        self.document_converter = LightweightConverter()

        self.vector_store = self.db_connection.get_vector_store()

        self.pipeline = IngestionPipeline(
            transformations=[
                MarkdownNodeParser(chunk_size=512, chunk_overlap=100, include_metadata=True, include_prev_next_rel=True),
                TitleExtractor(),
                OpenAIEmbedding(model="text-embedding-3-small", embed_dim=1536),
            ],
            vector_store=self.vector_store,
        )

    def convert_document_to_markdown(self, source: str) -> str:
        return self.document_converter.convert(source)

    def scrape_web_urls(self, urls: List[str]) -> List[Document]:
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
        documents = self.drive_loader.load_documents(folder_id)
        for doc in documents:
            doc.metadata['source'] = 'google_drive'
            doc.metadata['folder_id'] = folder_id
        return documents

    def convert_drive_documents_to_markdown(self, folder_id: str) -> List[Document]:
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

    def process_youtube_videos(self, urls: List[str]) -> List[Document]:
        documents = []
        print("Processing YouTube videos for transcript segments...")
        for link in urls:
            try:
                video_data = self.youtube_scraper.get_transcript_segments(link)
                for segment in video_data['segments']:
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
                print(f"Processed {len(video_data['segments'])} segments from {link}")
            except Exception as e:
                print(f"Error processing YouTube video {link}: {e}")
        return documents

    def ingest_documents(self, documents: List[Document]) -> None:
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
                print(f"Could not fetch existing URLs from vector store: {e}")

            for doc in documents:
                url = doc.metadata.get('url') if doc.metadata else None
                if url and url in existing_urls:
                    print(f"Skipping duplicate URL: {url}")
                    continue
                filtered_documents.append(doc)
        except Exception as e:
            print(f"Error during duplicate filtering: {e}")
            filtered_documents = documents

        if not filtered_documents:
            print("No new documents to ingest after filtering.")
            return

        self.pipeline.run(documents=filtered_documents, show_progress=True)


# ===============================
# Main Entry Point
# ===============================
def main():
    pipeline = RAGDataIngestion()

    urls_to_scrape = [
        "https://wso2.ai/",
        "https://wso2.com/api-management/ai/",
        "https://wso2.com/integration/ai/",
        "https://wso2.com/identity-and-access-management/ai/",
        "https://wso2.com/internal-developer-platform/ai/"
    ]

    urls_to_videos = [
     "https://www.youtube.com/watch?v=X5eC3Rk9FBQ",
     "https://www.youtube.com/watch?v=-nwIoiPB8CE",
     "https://www.youtube.com/watch?v=GoYR-iK2UUk",
     "https://www.youtube.com/watch?v=CYii_zExySA",
     "https://www.youtube.com/watch?v=banNxyyTSI4",
     "https://www.youtube.com/watch?v=wobNffok7nc",
     "https://www.youtube.com/watch?v=bTj0h5x8W70"

    ]

    config = get_config()
    drive_folder_id = config.google_drive_folder_id

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
            print(f"Loaded and converted {len(drive_documents)} documents from Google Drive.")
            all_documents.extend(drive_documents)

        if all_documents:
            print(f"Ingesting {len(all_documents)} documents...")
            pipeline.ingest_documents(all_documents)
            print("✅ Data ingestion completed successfully!")
        else:
            print("⚠️ No documents to ingest.")

    except Exception as e:
        print(f"❌ An error occurred during ingestion: {e}")


if __name__ == "__main__":
    main()
