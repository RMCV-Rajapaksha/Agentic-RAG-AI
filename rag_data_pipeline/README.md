# RAG Data Pipeline

A robust data ingestion pipeline for the Agentic RAG AI system. This component ingests content from multiple sources (YouTube videos, web pages, and Google Drive documents), processes them into markdown format, generates embeddings, and stores them in a PostgreSQL vector database for efficient retrieval.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Production Configuration](#production-configuration)
  - [Development Configuration](#development-configuration)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The RAG Data Pipeline is responsible for:
1. **Fetching** content from YouTube videos, web pages, and Google Drive
2. **Converting** various document formats (PDF, DOCX, PPTX, HTML) to Markdown
3. **Processing** text using LlamaIndex with intelligent chunking
4. **Generating** embeddings using Azure OpenAI's text-embedding-3-small model
5. **Storing** data in PostgreSQL with pgvector extension for efficient vector search

---

## ✨ Features

- **Multi-Source Ingestion**:
  - YouTube transcripts with time-based segmentation
  - Web scraping with HTML-to-Markdown conversion
  - Google Drive document processing

- **Intelligent Processing**:
  - Markdown-based chunking (512 tokens, 100 overlap)
  - Automatic title extraction
  - Metadata preservation

- **Document Format Support**:
  - PDF (via pdfplumber)
  - DOCX, PPTX, ODT (via pypandoc)
  - HTML (via markdownify)
  - Plain text

- **Advanced Features**:
  - Duplicate URL detection
  - Azure AI embeddings (1536 dimensions)
  - HNSW indexing for fast similarity search
  - Progress tracking

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Data Sources                          │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐       │
│  │ YouTube  │  │   Web    │  │  Google Drive  │       │
│  └────┬─────┘  └────┬─────┘  └───────┬────────┘       │
└───────┼─────────────┼─────────────────┼────────────────┘
        │             │                 │
        ▼             ▼                 ▼
┌──────────────────────────────────────────────────────────┐
│              Content Processors                          │
│  ┌──────────────────┐  ┌───────────────────────────┐   │
│  │ Transcript       │  │ Document Converter        │   │
│  │ Segmentation     │  │ (PDF, DOCX, PPTX, HTML)  │   │
│  └──────────────────┘  └───────────────────────────┘   │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│           LlamaIndex Ingestion Pipeline                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Markdown   │→│    Title     │→│    Azure     │  │
│  │   Chunking   │  │  Extraction  │  │  Embedding   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│          PostgreSQL + pgvector Database                  │
│               (HNSW Index, Cosine Similarity)           │
└──────────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

- **Python**: 3.10 or higher
- **PostgreSQL**: 12+ with pgvector extension installed
- **API Keys**:
  - Azure OpenAI API access (for embeddings and LLM)
  - Google Cloud Service Account (for Drive access)
  - OpenAI API key (for fallback/development)

- **System Dependencies**:
  ```bash
  # For pypandoc (document conversion)
  sudo apt-get install pandoc  # Ubuntu/Debian
  brew install pandoc          # macOS
  ```

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/RMCV-Rajapaksha/Agentic-RAG-AI.git
cd Agentic-RAG-AI/rag_data_pipeline
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Pandoc (for document conversion)
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y pandoc

# macOS
brew install pandoc

# Windows
# Download from: https://pandoc.org/installing.html
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `rag_data_pipeline/` directory with the required variables based on your environment.

---

### 🚀 Production Configuration

For production deployment, use the following configuration:

```bash
# Google Service Account Configuration
GOOGLE_TYPE=service_account
GOOGLE_PROJECT_ID=prime--469104-i3
GOOGLE_PRIVATE_KEY_ID=975ff019c30efcf2c48bfafb40855959a6e
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCtCWjW5BiJyQ4kt\nTwN4ZRrjwrkKH+d+7JzeCSyP\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=rag-pipeline@prime-phalanx-i3.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=118440434716
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/rag-pipeline%40prime-phalanx-469104-i3.iam.gserviceaccount.com
GOOGLE_UNIVERSE_DOMAIN=googleapis.com

# Google Drive Folder ID
FOLDER_ID=1fnR7uqkbfI4FaO-wiTufWBL0k5t

# Azure OpenAI Configuration (Production)
AZURE_OPENAI_MODEL=gpt-4o
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_KEY=your_production_azure_api_key
AZURE_OPENAI_ENDPOINT=https://ai-internal-website-prod.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION=2024-10-01-preview

# Azure Embedding Configuration (Production)
AZURE_ENDPOINT_EMBEDDING=https://ai-internal-website-prod.cognitiveservices.azure.com/
AZURE_API_KEY_EMBEDDING=your_production_azure_embedding_key

# PostgreSQL Database Configuration (Production)
# Use your production database connection string
CONNECTION_STRING=postgres://username:password@production-host:5432
DB_NAME=agentic_rag_db
DB_TABLE_NAME=agentic_rag_table
```

> **⚠️ Security Note**: Never commit API keys to version control. Use environment variables or secret management systems in production.

---

### 🔧 Development Configuration

For local development and testing:

```bash
# Google Service Account Configuration (Same as Production)
GOOGLE_TYPE=service_account
GOOGLE_PROJECT_ID=prime-phalanx-469104-i3
GOOGLE_PRIVATE_KEY_ID=975ff019c30efcf2cb18f548bfafb40855959a6e
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=rag-pipeline@prime-phalanx-469104-i3.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=118440454475759234716
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/rag-pipeline%40prime-phalanx-469104-i3.iam.gserviceaccount.com
GOOGLE_UNIVERSE_DOMAIN=googleapis.com

# OpenAI API Key (Development/Fallback)
OPENAI_API_KEY=your_openai_api_key

# Google Drive Folder ID
FOLDER_ID=1fnR7uqkbfI4FaO-wiuKemfTufWBL0k5t

# Local PostgreSQL Database (Development)
CONNECTION_STRING=postgres://postgres:newpassword@localhost:5432
DB_NAME=agentic_rag_db_ai
DB_TABLE_NAME=agentic_rag_table
```

### Environment Variable Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GOOGLE_TYPE` | Google service account type | ✅ | `service_account` |
| `GOOGLE_PROJECT_ID` | Google Cloud project ID | ✅ | `prime-phalanx-469104-i3` |
| `GOOGLE_PRIVATE_KEY_ID` | Service account private key ID | ✅ | `975ff019c30ef...` |
| `GOOGLE_PRIVATE_KEY` | Service account private key (escaped newlines) | ✅ | `"-----BEGIN PRIVATE KEY-----\n..."` |
| `GOOGLE_CLIENT_EMAIL` | Service account email | ✅ | `rag-pipeline@...` |
| `GOOGLE_CLIENT_ID` | Service account client ID | ✅ | `118440454475759234716` |
| `FOLDER_ID` | Google Drive folder ID to ingest | ✅ | `1fnR7uqkbfI4FaO...` |
| `AZURE_OPENAI_MODEL` | Azure OpenAI model name | ✅ (Prod) | `gpt-4o` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure deployment name | ✅ (Prod) | `gpt-4o` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | ✅ (Prod) | `4Dlz9LdV1aJs...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | ✅ (Prod) | `https://ai-internal...` |
| `AZURE_OPENAI_API_VERSION` | Azure API version | ✅ (Prod) | `2024-12-01-preview` |
| `AZURE_ENDPOINT_EMBEDDING` | Azure embedding endpoint | ✅ (Prod) | `https://ai-internal...` |
| `AZURE_API_KEY_EMBEDDING` | Azure embedding API key | ✅ (Prod) | `4Dlz9LdV1aJs...` |
| `OPENAI_API_KEY` | OpenAI API key (fallback) | ✅ (Dev) | `sk-proj-...` |
| `CONNECTION_STRING` | PostgreSQL connection string | ✅ | `postgres://user:pass@host:5432` |
| `DB_NAME` | Database name | ✅ | `agentic_rag_db_ai` |
| `DB_TABLE_NAME` | Vector store table name | ✅ | `agentic_rag_table` |

---

## 🎮 Usage

### Basic Usage

Run the data ingestion pipeline:

```bash
python main.py
```

This will:
1. Fetch YouTube URLs from the GitHub repository (`YouTubeURL.md`)
2. Process YouTube transcripts
3. Scrape configured web pages
4. Load documents from Google Drive
5. Convert all content to embeddings
6. Store in PostgreSQL with pgvector

### Customizing Data Sources

Edit `main.py` to customize the sources:

```python
# Web URLs to scrape
urls_to_scrape = [
    "https://wso2.ai/",
    "https://wso2.com/api-management/ai/",
    # Add more URLs...
]

# YouTube URLs (from markdown file or hardcoded)
urls_to_videos = [
    "https://www.youtube.com/watch?v=example",
    # Add more videos...
]

# Google Drive folder ID
drive_folder_id = "your_folder_id_here"
```

### YouTube Segment Length

Adjust YouTube transcript segmentation:

```python
# In main.py or youtube_transcript_to_md.py
scraper = YouTubeTranscriptScraper(
    language="en",
    segment_length_minutes=10  # Change duration (default: 10 minutes)
)
```

---

## 📁 Data Sources

### 1. YouTube Videos
- Fetches transcripts via `youtube-transcript-api`
- Segments into time-based chunks (default: 10 minutes)
- Converts to markdown with timestamps
- Processes with Azure OpenAI for formatting

### 2. Web Pages
- Uses `cloudscraper` to bypass basic protections
- Converts HTML to markdown with `html2text`
- Extracts metadata (title, description)
- Preserves source URLs

### 3. Google Drive
- Authenticates via service account
- Supports: PDF, DOCX, PPTX, ODT, HTML, TXT
- Converts to markdown using `pypandoc` and `pdfplumber`
- Preserves file metadata

---

## 🛠️ Technology Stack

### Core Libraries
- **LlamaIndex**: Document processing and embedding pipeline
- **Azure OpenAI**: Embeddings (text-embedding-3-small) and LLM (GPT-4o)
- **PostgreSQL + pgvector**: Vector database with HNSW indexing

### Document Processing
- `pypandoc`: DOCX, PPTX, ODT conversion
- `pdfplumber`: PDF text extraction
- `markdownify`: HTML to Markdown
- `python-docx`: DOCX parsing

### Web & API
- `cloudscraper`: Web scraping with JS rendering
- `beautifulsoup4`: HTML parsing
- `youtube-transcript-api`: YouTube transcript fetching
- `google-api-python-client`: Google Drive access

### Database
- `sqlalchemy`: ORM and connection management
- `psycopg2`: PostgreSQL adapter
- `pgvector`: Vector similarity search

---

## 📂 Project Structure

```
rag_data_pipeline/
├── main.py                    # Main ingestion script
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project metadata
├── README.md                 # This file
├── .env                      # Environment variables (not in git)
├── credentials.json          # Google service account (generated)
│
├── config/
│   ├── __init__.py
│   └── config.py             # Configuration loader (singleton pattern)
│
├── database/
│   ├── __init__.py
│   └── db.py                 # Database connection & vector store setup
│
└── src/
    ├── __init__.py
    ├── youtube_transcripts/
    │   ├── __init__.py
    │   └── youtube_transcript_to_md.py  # YouTube processor
    │
    ├── scraper/
    │   ├── __init__.py
    │   └── web_scraper.py    # Web scraping utilities
    │
    └── drive_reader/
        ├── __init__.py
        └── drive_reader.py   # Google Drive document loader
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. **PostgreSQL Connection Errors**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U postgres -d agentic_rag_db_ai

# Install pgvector extension
psql -U postgres -d agentic_rag_db_ai -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

#### 2. **Google Drive Authentication Fails**
- Verify service account has access to the folder
- Check `GOOGLE_PRIVATE_KEY` has proper newline escaping: `\n`
- Ensure all Google credentials are correctly set
- Share the Drive folder with the service account email

#### 3. **Pandoc Not Found**
```bash
# Install pandoc
sudo apt-get install pandoc    # Ubuntu/Debian
brew install pandoc            # macOS
```

#### 4. **YouTube Transcript Unavailable**
- Some videos don't have transcripts
- Check video is public
- Verify language code (default: `en`)

#### 5. **Azure OpenAI Rate Limits**
- Implement retry logic
- Reduce batch size
- Contact Azure support for quota increase

#### 6. **Memory Issues with Large Documents**
- Process documents in smaller batches
- Increase chunk overlap
- Use streaming where possible

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check database contents:

```sql
-- Connect to database
psql -U postgres -d agentic_rag_db_ai

-- Check table
SELECT COUNT(*) FROM agentic_rag_table;

-- View sample records
SELECT metadata->>'url', metadata->>'title' 
FROM agentic_rag_table 
LIMIT 10;
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is part of the Agentic RAG AI system research initiative.

---

## 🔗 Related Components

- **RAG API Server** (`../rag/`): FastAPI backend serving the AI agent
- **Frontend** (`../rag_test_frontend/`): React-based chat interface
- **Notebooks** (`../notebooks/`): Research and testing notebooks

---

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the main project README
- Review the troubleshooting section above

---

**Built with ❤️ for intelligent document retrieval**
