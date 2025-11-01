"""
Configuration Package

This package contains configuration management, constants, logging,
and exception classes for the RAG data pipeline.
"""

from .config import (
    get_openai_api_key,
    get_db_name,
    get_db_connection_string,
    get_db_table_name,
    get_google_drive_folder_id,
    get_azure_openai_model,
    get_azure_openai_deployment_name,
    get_azure_openai_api_key,
    get_azure_openai_endpoint,
    get_azure_openai_api_version,
    get_azure_endpoint_embedding,
    get_azure_api_key_embedding,
    get_google_credentials,
    get_google_credentials_json_path,
)

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
    # Config functions
    "get_openai_api_key",
    "get_db_name",
    "get_db_connection_string",
    "get_db_table_name",
    "get_google_drive_folder_id",
    "get_azure_openai_model",
    "get_azure_openai_deployment_name",
    "get_azure_openai_api_key",
    "get_azure_openai_endpoint",
    "get_azure_openai_api_version",
    "get_azure_endpoint_embedding",
    "get_azure_api_key_embedding",
    "get_google_credentials",
    "get_google_credentials_json_path",
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
