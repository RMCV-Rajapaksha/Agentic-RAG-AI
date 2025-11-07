"""
Configuration Package

This package contains configuration constants, logging,
and exception classes for the RAG data pipeline.
"""

from .exceptions import (
    RAGPipelineException,
    ConfigurationError,
    DatabaseConnectionError,
    DocumentProcessingError,
    EmbeddingGenerationError,
    YouTubeProcessingError,
    WebScrapingError,
    GoogleDriveError,
    ValidationError,
)

__all__ = [
    # Exceptions
    "RAGPipelineException",
    "ConfigurationError",
    "DatabaseConnectionError",
    "DocumentProcessingError",
    "EmbeddingGenerationError",
    "YouTubeProcessingError",
    "WebScrapingError",
    "GoogleDriveError",
    "ValidationError",
]
