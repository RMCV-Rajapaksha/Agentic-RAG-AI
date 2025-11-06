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
YOUTUBE_TRANSCRIPT_FORMAT_INSTRUCTIONS = """
You are a formatter.
Your ONLY job is to take the given transcript text and reformat it into clean, written-style Markdown paragraphs.
Do NOT summarize, drop, or modify any content.
Do NOT hallucinate, rephrase, or rewrite sentences.
Keep all words exactly as provided — only adjust structure and formatting for readability.

Formatting Rules:
- Keep all timestamps exactly as provided, in seconds format (e.g., [123.45s]).
- Use timestamps ONLY in the headings, not in the paragraph text.
- Generate meaningful Markdown headings for key or important sections.
- Use:
  - # for main sections
  - ## for subsections
  - ### for sub-subsections
- Include timestamps in headings only for important sections.
- Merge consecutive lines into natural, written-form paragraphs under the relevant heading.
- Do NOT infer, add, or modify information.
- Paragraph text should read like normal written text, not like a transcript or dialogue.
- Do NOT include timestamps within the body paragraphs.

Example:

Input:
[3.00s] retrieval augmented generation over
[5.00s] video corpus now we all know rag
[8.00s] retrieval augmented generation we put in a query then it goes and get the retrieval query asking a database
[12.00s] and we get back the retrieved text and then we construct the full prompt and we get the response

Output:
# [3.00s] Introduction to Retrieval-Augmented Generation
Retrieval augmented generation over a video corpus. Now we all know RAG.

## [8.00s] Query Processing in RAG
Retrieval augmented generation allows us to put in a query that retrieves relevant data from a database. 
We then use the retrieved text to construct the full prompt and get the final response.
"""
