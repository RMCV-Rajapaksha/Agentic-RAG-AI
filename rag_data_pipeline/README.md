# RAG Data Pipeline

A comprehensive LlamaIndex-based data ingestion pipeline that can scrape web content, load documents from Google Drive, chunk them intelligently, and store them in a PostgreSQL vector database with embeddings for semantic search.

## Features

- **Web Scraping**: Scrape content from URLs and convert to markdown
- **Google Drive Integration**: Load documents directly from Google Drive folders
- **Intelligent Chunking**: Use LlamaIndex's advanced chunking strategies
- **Vector Storage**: Store embeddings in PostgreSQL with pgvector extension
- **Semantic Search**: Query ingested data using natural language
- **Comprehensive Pipeline**: End-to-end data ingestion and retrieval

## Architecture

```
URLs/Google Drive → Web Scraper/Drive Reader → Document Chunker → 
Embeddings Generator → PostgreSQL Vector Store → Query Engine
```

## Prerequisites

1. **Python 3.13+**
2. **PostgreSQL with pgvector extension**
3. **OpenAI API Key**
4. **Google Service Account** (for Google Drive integration)

### Installing PostgreSQL with pgvector

```bash
# Install PostgreSQL and pgvector extension
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgresql-15-pgvector

# Or use the provided timescaledb.deb for TimescaleDB with vector support
sudo dpkg -i timescaledb.deb
```

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd rag_data_pipeline
```

2. **Install dependencies**:
```bash
pip install -e .
# or with uv
uv pip install -e .
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. **Configure Google Drive (Optional)**:
   - Create a Google Cloud Project
   - Enable Google Drive API
   - Create a Service Account
   - Download the service account key
   - Add the credentials to your .env file

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
CONNECTION_STRING=postgres://postgres:password@localhost:5432
DB_NAME=rag_vector_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
DB_TABLE_NAME=documents

# Google Drive API Configuration
GOOGLE_TYPE=service_account
GOOGLE_PROJECT_ID=your_google_project_id
GOOGLE_PRIVATE_KEY_ID=your_private_key_id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour_private_key_here\n-----END PRIVATE KEY-----"
GOOGLE_CLIENT_EMAIL=your_service_account_email@your_project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
```

## Usage

### Basic Usage

```python
from main import RAGDataPipeline

# Initialize the pipeline
pipeline = RAGDataPipeline()

# Option 1: Ingest from URLs
urls = ["https://example.com/blog1", "https://example.com/blog2"]
pipeline.ingest_from_urls(urls)

# Option 2: Ingest from Google Drive
folder_id = "your_google_drive_folder_id"
pipeline.ingest_from_drive(folder_id)

# Option 3: Combined ingestion
url_docs = pipeline.scrape_urls_to_documents(urls)
drive_docs = pipeline.load_drive_documents(folder_id)
all_docs = url_docs + drive_docs
pipeline.ingest_documents(all_docs)

# Query the data
query_engine = pipeline.create_query_engine()
response = pipeline.query("What are the main topics?", query_engine)
print(response)
```

### Using the Example Script

Run the provided example script for interactive usage:

```bash
python pipeline_example.py
```

This will give you options to:
1. Ingest data from URLs
2. Ingest data from Google Drive
3. Combine both data sources
4. Query existing data

### Custom Configuration

You can customize the pipeline behavior:

```python
from main import RAGDataPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding

# Custom chunking parameters
pipeline = RAGDataPipeline()
pipeline.chunker = DocumentChunker(chunk_size=1024, chunk_overlap=200)

# Recreate the ingestion pipeline with custom settings
pipeline.pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=1024, chunk_overlap=200),
        TitleExtractor(),
        OpenAIEmbedding(model="text-embedding-3-large"),
    ],
    vector_store=pipeline.vector_store,
)
```

## Project Structure

```
rag_data_pipeline/
├── main.py                 # Main pipeline implementation
├── pipeline_example.py     # Example usage script
├── database/
│   └── db.py              # Database connection utilities
├── src/
│   ├── scraper/
│   │   └── web_scraper.py # Web scraping functionality
│   ├── drive_reader/
│   │   └── drive_reader.py # Google Drive integration
│   ├── chunkers/
│   │   └── chunkers.py    # Document chunking utilities
│   └── embeddings/
│       └── openai_embeddings.py # Embedding utilities
├── config/
│   ├── config.py          # Configuration management
│   └── settings.py        # Application settings
├── data/
│   └── paul_graham/       # Sample data
└── .env.example           # Environment variables template
```

## Components

### 1. RAGDataPipeline
The main class that orchestrates the entire pipeline:
- `scrape_urls_to_documents()`: Scrape URLs and convert to documents
- `load_drive_documents()`: Load documents from Google Drive
- `ingest_documents()`: Process and store documents with embeddings
- `create_query_engine()`: Create a query engine for semantic search
- `query()`: Query the ingested data

### 2. Web Scraper
- Scrapes web content using cloudscraper
- Converts HTML to markdown
- Extracts metadata (title, description)
- Handles anti-bot protection

### 3. Google Drive Reader
- Uses Google Drive API
- Supports various document formats
- Maintains document metadata
- Service account authentication

### 4. Document Chunker
- Intelligent text splitting
- Configurable chunk size and overlap
- Preserves document structure
- Compatible with LlamaIndex

### 5. Database Connection
- PostgreSQL with pgvector
- Vector similarity search
- Configurable embedding dimensions
- Connection pooling and management

## Advanced Features

### Custom Extractors

Add custom metadata extractors:

```python
from llama_index.core.extractors import KeywordExtractor, QuestionsAnsweredExtractor

pipeline.pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=512, chunk_overlap=100),
        TitleExtractor(),
        KeywordExtractor(keywords=10),
        QuestionsAnsweredExtractor(questions=3),
        OpenAIEmbedding(),
    ],
    vector_store=pipeline.vector_store,
)
```

### Batch Processing

Process large datasets efficiently:

```python
# Process URLs in batches
url_batches = [urls[i:i+10] for i in range(0, len(urls), 10)]
for batch in url_batches:
    documents = pipeline.scrape_urls_to_documents(batch)
    pipeline.ingest_documents(documents)
```

### Custom Query Engine

Create specialized query engines:

```python
from llama_index.core import VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever

index = VectorStoreIndex.from_vector_store(pipeline.vector_store)
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=5,
)
query_engine = RetrieverQueryEngine(retriever=retriever)
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Ensure PostgreSQL is running
   - Check connection string in .env
   - Verify pgvector extension is installed

2. **Google Drive Access Issues**:
   - Verify service account credentials
   - Check folder permissions
   - Ensure Google Drive API is enabled

3. **OpenAI API Errors**:
   - Verify API key is valid
   - Check rate limits
   - Ensure sufficient credits

4. **Memory Issues with Large Documents**:
   - Reduce chunk_size parameter
   - Process documents in smaller batches
   - Monitor memory usage

### Performance Optimization

1. **Batch Processing**: Process multiple documents together
2. **Caching**: Cache embeddings to avoid recomputation
3. **Database Indexing**: Ensure proper indexing on vector columns
4. **Parallel Processing**: Use multiple workers for large datasets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please:
1. Check the troubleshooting section
2. Review existing issues
3. Create a new issue with detailed information

## Acknowledgments

- [LlamaIndex](https://github.com/run-llama/llama_index) for the excellent RAG framework
- [pgvector](https://github.com/pgvector/pgvector) for PostgreSQL vector support
- [OpenAI](https://openai.com/) for embedding models