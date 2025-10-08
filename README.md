# Agentic RAG AI System

A comprehensive Retrieval-Augmented Generation (RAG) system with agentic capabilities, designed to provide intelligent question-answering based on WSO2 knowledge base with Google OAuth authentication.

## 🏗️ Architecture

The system consists of four main components:

### 1. **RAG Data Pipeline** (`rag_data_pipeline/`)
- **Purpose**: Ingests and processes data from multiple sources
- **Sources**: YouTube transcripts, web pages, Google Drive documents
- **Features**: 
  - Converts documents to Markdown format
  - Chunks text using LlamaIndex
  - Generates embeddings with OpenAI
  - Stores in PostgreSQL with pgvector

### 2. **RAG API Server** (`rag/`)
- **Purpose**: FastAPI backend serving the AI agent
- **Features**:
  - Google OAuth 2.0 authentication
  - Session management with secure cookies
  - Agentic AI powered by GPT-4
  - Vector search capabilities
  - CORS-enabled for web frontend

### 3. **Web Frontend** (`ask-wiz-79/`)
- **Purpose**: React-based user interface
- **Tech Stack**: React + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **Features**:
  - Google Sign-in integration
  - Real-time chat interface
  - Responsive design
  - Authentication state management

### 4. **Research Notebooks** (`notebooks/`)
- **Purpose**: Jupyter notebooks for testing and development
- **Contents**: RAG experiments and LlamaIndex testing

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL with pgvector extension
- OpenAI API key
- Google OAuth credentials

### 1. Setup Data Pipeline
```bash
cd rag_data_pipeline
pip install -r requirements.txt
# Configure environment variables
python main.py  # Ingest data
```

### 2. Start RAG API Server
```bash
cd rag
pip install -r requirements.txt
# Configure environment variables
python main.py  # Start server on port 8000
```

### 3. Launch Frontend
```bash
cd ask-wiz-79
npm install
npm run dev  # Start on port 3000
```

## 🔧 Configuration

Create `.env` files in both `rag/` and `rag_data_pipeline/` directories:

```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 📊 Data Sources

- **Web Pages**: WSO2 AI-related documentation
- **YouTube Videos**: Technical tutorials and presentations (URLs in `YouTubeURL.md`)
- **Google Drive**: Documents and presentations
- **Custom Documents**: PDF, DOCX, HTML files

## 🛠️ Technology Stack

- **Backend**: FastAPI, LlamaIndex, OpenAI GPT-4, PostgreSQL, pgvector
- **Frontend**: React, TypeScript, Tailwind CSS, shadcn/ui
- **Data Processing**: pypandoc, pdfplumber, markdownify
- **Authentication**: Google OAuth 2.0
- **Deployment**: Docker support available

## 📝 Features

- **Agentic AI**: Intelligent question-answering with tool usage
- **Multi-Source RAG**: Combines web, video, and document content
- **Secure Authentication**: Google OAuth with session management
- **Real-time Chat**: Interactive web interface
- **Scalable Architecture**: Modular design for easy scaling


## 📄 License

This project is part of a research initiative for building advanced RAG systems with agentic capabilities.
