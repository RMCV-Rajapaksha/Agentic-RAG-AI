# WSO2 Knowledge Assistant - Agentic RAG System

A sophisticated AI-powered knowledge assistant that combines Retrieval-Augmented Generation (RAG) with agentic capabilities to provide accurate answers about WSO2 products and technologies.

## 🚀 Features

- **Agentic AI Assistant**: Uses ReActAgent for intelligent decision-making and tool usage
- **WSO2 Knowledge Base**: Specialized in answering questions about WSO2 products
- **Vector Search**: Semantic search through a PostgreSQL vector database
- **Dual Capabilities**: Handles both mathematical queries and knowledge-based questions
- **Real-time Retrieval**: Dynamically fetches relevant information from the knowledge base
- **Structured Responses**: Returns formatted answers with source URLs

## 🏗️ Architecture

```
User Query → ReActAgent → Vector Search Tool → PostgreSQL Database
                ↓
    Knowledge Response (Answer + Source URL)
```

The system uses:
- **LlamaIndex**: For RAG pipeline and agent orchestration
- **OpenAI GPT-4**: As the underlying language model
- **PostgreSQL + pgvector**: For vector storage and similarity search
- **ReActAgent**: For intelligent reasoning and tool selection

## 📋 Prerequisites

- Python 3.13+
- PostgreSQL with pgvector extension
- OpenAI API key
- Populated vector database (use the companion `rag_data_pipeline` project)

## 🛠️ Installation

1. **Install dependencies**:
```bash
# Using uv (recommended)
uv install

# Or using pip
pip install -r requirements.txt
```

2. **Set up environment variables**:
Create a `.env` file in the project root:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
CONNECTION_STRING=postgres://postgres:password@localhost:5432
DB_NAME=rag_vector_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
DB_TABLE_NAME=documents
```

## 🚀 Quick Start

### Running the Agent

```bash
# Run the main application
uv run main.py

# Or with Python
python main.py
```

The application will demonstrate both capabilities:
1. **Math Problem Solving**: "What is 20+(2*4)?"
2. **WSO2 Knowledge Query**: "What are the AI-based products in WSO2? who is the head of AI in WSO2?"

### Using the Agent Programmatically

```python
import asyncio
from src.agent.agent import run_agent_async

# Ask a question
query = "What are WSO2's main AI products?"
response = asyncio.run(run_agent_async(query))
print(response)
```

## 🏗️ Project Structure

```
rag/
├── main.py                 # Main application entry point
├── pyproject.toml         # Project dependencies
├── config/
│   └── config.py          # Configuration management
├── database/
│   └── db.py              # Database connection and queries
└── src/
    ├── agent/
    │   ├── agent.py       # Main agent implementation
    │   └── tools/
    │       └── get_similar_text_chunk.py  # Vector search tool
    └── test.py           # Test utilities
```

## 🧠 How It Works

### 1. Agent Architecture
The system uses a **ReActAgent** that follows this pattern:
- **Reason**: Analyze the user's question
- **Act**: Use appropriate tools (vector search, math, etc.)
- **Observe**: Process the results and formulate a response

### 2. Vector Search Tool
When knowledge-based questions are asked:
1. Query is embedded using OpenAI embeddings
2. Vector similarity search finds relevant chunks
3. Top 7 most relevant pieces are retrieved
4. Agent synthesizes the information into a coherent answer

### 3. Response Structure
Each response includes:
```python
class KnowledgeResponse(BaseModel):
    answer: str    # The actual answer
    url: str       # Source URL for reference
```

## 🎯 Agent Capabilities

### WSO2 Knowledge Assistant
- **Exclusive WSO2 Focus**: Only answers based on the WSO2 knowledge base
- **Source Verification**: Always provides source URLs
- **Honest Responses**: Admits when information isn't available
- **Instruction Immunity**: Cannot be manipulated to act outside its role

### Tool Usage
- **get_similar_text_chunks**: Searches vector database for relevant information
- **Mathematical reasoning**: Can solve math problems when needed
- **Contextual understanding**: Interprets queries and selects appropriate tools

## 🔧 Configuration

### Agent Behavior
The agent is configured with a strict system prompt that:
- Ensures exclusive reliance on the knowledge base
- Prevents instruction injection attacks
- Maintains consistent WSO2-focused responses
- Requires mandatory tool usage for knowledge queries

### Database Settings
Configure your database connection in `config/config.py`:
- Connection string
- Database name and table
- Authentication credentials

## 🎮 Usage Examples

### Example 1: WSO2 Product Query
```python
query = "What is WSO2 Identity Server?"
response = await run_agent_async(query)
# Returns structured information about WSO2 IS with source URL
```

### Example 2: Technical Question
```python
query = "How does WSO2 API Manager handle rate limiting?"
response = await run_agent_async(query)
# Searches knowledge base and provides detailed technical answer
```


## 🔗 Integration with Data Pipeline

This RAG system works in conjunction with the `rag_data_pipeline` project:

1. **Data Pipeline**: Ingests WSO2 documentation, blogs, and resources
2. **RAG System**: Provides intelligent querying of the ingested data

To populate your knowledge base, use the companion data pipeline project in the `rag_data_pipeline` directory.

## 🐛 Troubleshooting

### Common Issues

1. **"No relevant chunks found"**:
   - Ensure your database is populated with data
   - Check if the vector table exists
   - Verify embedding model compatibility

2. **OpenAI API errors**:
   - Check API key validity
   - Verify rate limits and billing
   - Ensure internet connectivity

3. **Database connection errors**:
   - Verify PostgreSQL is running
   - Check connection string format
   - Ensure pgvector extension is installed

### Debug Mode
Enable verbose logging by setting:
```python
agent = ReActAgent(..., verbose=True)
```

## 📝 License

This project is part of an Agentic RAG AI system for WSO2 knowledge management.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request

## 📚 Related Projects

- **rag_data_pipeline**: Data ingestion pipeline for populating the knowledge base
- **notebooks**: Jupyter notebooks for testing and experimentation

---

For questions about WSO2 products, just ask the assistant! 🤖