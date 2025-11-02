"""
Constants Module

This module contains all constant values used throughout the RAG data pipeline.
Centralizing constants here makes the codebase more maintainable and easier to configure.
"""

# ===============================
# Azure OpenAI Configuration
# ===============================
AZURE_OPENAI_MODEL_DEFAULT = "gpt-4o"
AZURE_OPENAI_API_VERSION_DEFAULT = "2024-10-01-preview"
EMBEDDING_DEPLOYMENT_NAME = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# ===============================
# Document Processing Configuration
# ===============================
CHUNK_SIZE = 512
CHUNK_OVERLAP = 100


# ===============================
# YouTube Processing Configuration
# ===============================
YOUTUBE_DEFAULT_LANGUAGE = "en"
YOUTUBE_SEGMENT_LENGTH_MINUTES = 10

# ===============================
# Database Configuration
# ===============================
HNSW_M = 16
HNSW_EF_CONSTRUCTION = 64
HNSW_EF_SEARCH = 40
HNSW_DISTANCE_METHOD = "vector_cosine_ops"

# ===============================
# Web Scraping Configuration
# ===============================
WEB_SCRAPER_TIMEOUT = 15
WEB_SCRAPER_BASE_URL = "https://wso2.com"

# ===============================
# GitHub URLs for Data Sources
# ===============================
GITHUB_YOUTUBE_URLS_MD = (
    "https://raw.githubusercontent.com/RMCV-Rajapaksha/"
    "Agentic-RAG-AI/main/YouTubeURL.md"
)

GITHUB_WEBSITE_URLS_MD = (
    "https://raw.githubusercontent.com/RMCV-Rajapaksha/"
    "Agentic-RAG-AI/main/WebURLs.md"
)

#
# ===============================
# LLM Instructions
# ===============================
YOUTUBE_TRANSCRIPT_FORMAT_INSTRUCTIONS = """You are a formatter. 
Your ONLY job is to take the given text and reformat it into Markdown. 
Do not summarize, drop any content, or change the wording of the paragraph text. 
Keep all words exactly as provided for the paragraph/description. 
Generate headings only for key or important points. Only these headings should have timestamps.  

Rules:
- Generate meaningful headings based on key points in the transcript.  
- Use # for main sections, ## for subsections, ### for sub-subsections.  
- Include timestamps in headings only for very important points.  
- Timestamps should use the format [seconds.s], e.g., [4460.32s], not hh:mm:ss.  
- All other sentences remain as paragraphs under the nearest heading.  

Example:

Input:
[3.00s] retrieval augmented generation over
[5.00s] video corpus now we all know rag
[8.00s] retrieval augmented generation we put in a query then it goes and get the retrieval query asking a database
[12.00s] and we get back the retrieved text and then we construct the full prompt and we get the response

Output:
# [3.00s] Introduction to Retrieval-Augmented Generation
retrieval augmented generation over
video corpus now we all know rag

## [8.00s] Query Processing in RAG
retrieval augmented generation we put in a query then it goes and get the retrieval query asking a database
and we get back the retrieved text and then we construct the full prompt and we get the response
"""




