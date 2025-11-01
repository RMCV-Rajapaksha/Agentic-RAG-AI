"""
Custom Exceptions Module

This module defines custom exception classes for the RAG data pipeline.
Using custom exceptions helps with better error handling and debugging.
"""


class RAGPipelineException(Exception):
    """Base exception class for RAG pipeline errors."""
    pass


class ConfigurationError(RAGPipelineException):
    """Raised when there's a configuration issue."""
    pass


class DatabaseConnectionError(RAGPipelineException):
    """Raised when database connection fails."""
    pass


class DocumentProcessingError(RAGPipelineException):
    """Raised when document processing fails."""
    pass


class EmbeddingGenerationError(RAGPipelineException):
    """Raised when embedding generation fails."""
    pass


class YouTubeProcessingError(RAGPipelineException):
    """Raised when YouTube video processing fails."""
    pass


class WebScrapingError(RAGPipelineException):
    """Raised when web scraping fails."""
    pass


class GoogleDriveError(RAGPipelineException):
    """Raised when Google Drive operations fail."""
    pass


class ValidationError(RAGPipelineException):
    """Raised when data validation fails."""
    pass
