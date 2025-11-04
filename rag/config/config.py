"""
Configuration Module for Agentic RAG System

This module provides functional configuration accessors for all system settings
including OpenAI, Azure, Google OAuth, and database configurations.
"""

import os
from typing import Optional
from dotenv import load_dotenv


# ============================================================================
# Environment Loading
# ============================================================================

# Load environment once at module import
if os.path.isfile('.env'):
    load_dotenv()


# ============================================================================
# OpenAI Configuration
# ============================================================================

def get_openai_api_key() -> str:
    """
    Get OpenAI API key.
    
    Returns:
        OpenAI API key string
        
    Raises:
        ValueError: If API key is not set
    """
    value = os.getenv('OPENAI_API_KEY')
    if not value:
        raise ValueError("OPENAI_API_KEY is required but not set.")
    return value


# ============================================================================
# Azure OpenAI Configuration
# ============================================================================

def get_azure_openai_model() -> str:
    """Get Azure OpenAI model name (default: gpt-4o)."""
    return os.getenv('AZURE_OPENAI_MODEL', 'gpt-4o')


def get_azure_openai_deployment_name() -> str:
    """Get Azure OpenAI deployment name (default: gpt-4o)."""
    return os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o')


def get_azure_openai_api_key() -> str:
    """
    Get Azure OpenAI API key.
    
    Returns:
        Azure OpenAI API key string
        
    Raises:
        ValueError: If API key is not set
    """
    value = os.getenv('AZURE_OPENAI_API_KEY')
    if not value:
        raise ValueError("AZURE_OPENAI_API_KEY is required but not set.")
    return value


def get_azure_openai_endpoint() -> str:
    """
    Get Azure OpenAI endpoint URL.
    
    Returns:
        Azure OpenAI endpoint string
        
    Raises:
        ValueError: If endpoint is not set
    """
    value = os.getenv('AZURE_OPENAI_ENDPOINT')
    if not value:
        raise ValueError("AZURE_OPENAI_ENDPOINT is required but not set.")
    return value


def get_azure_openai_api_version() -> str:
    """Get Azure OpenAI API version (default: 2024-12-01-preview)."""
    return os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')


# ============================================================================
# Azure Embedding Configuration
# ============================================================================

def get_azure_endpoint_embedding() -> str:
    """
    Get Azure embedding endpoint URL.
    
    Returns:
        Azure embedding endpoint string
        
    Raises:
        ValueError: If endpoint is not set
    """
    value = os.getenv('AZURE_ENDPOINT_EMBEDDING')
    if not value:
        raise ValueError("AZURE_ENDPOINT_EMBEDDING is required but not set.")
    return value


def get_azure_api_key_embedding() -> str:
    """
    Get Azure embedding API key.
    
    Returns:
        Azure embedding API key string
        
    Raises:
        ValueError: If API key is not set
    """
    value = os.getenv('AZURE_API_KEY_EMBEDDING')
    if not value:
        raise ValueError("AZURE_API_KEY_EMBEDDING is required but not set.")
    return value


# ============================================================================
# Google OAuth Configuration
# ============================================================================

def get_google_client_id() -> str:
    """
    Get Google OAuth client ID.
    
    Returns:
        Google client ID string
        
    Raises:
        ValueError: If client ID is not set
    """
    value = os.getenv('GOOGLE_CLIENT_ID')
    if not value:
        raise ValueError("GOOGLE_CLIENT_ID is required but not set.")
    return value


def get_google_client_secret() -> str:
    """
    Get Google OAuth client secret.
    
    Returns:
        Google client secret string
        
    Raises:
        ValueError: If client secret is not set
    """
    value = os.getenv('GOOGLE_CLIENT_SECRET')
    if not value:
        raise ValueError("GOOGLE_CLIENT_SECRET is required but not set.")
    return value


def get_redirect_uri() -> str:
    """
    Get OAuth redirect URI.
    
    Returns:
        Redirect URI string
        
    Raises:
        ValueError: If redirect URI is not set
    """
    value = os.getenv('REDIRECT_URI')
    if not value:
        raise ValueError("REDIRECT_URI is required but not set.")
    return value


def get_redirect_frontend_uri() -> Optional[str]:
    """
    Get frontend redirect URI (optional).
    
    Returns:
        Frontend redirect URI string or None
    """
    return os.getenv('REDIRECT_FRONTEND_URI')


# ============================================================================
# Database Configuration
# ============================================================================

def get_db_connection_string() -> str:
    """
    Get database connection string.
    
    Returns:
        Database connection string
        
    Raises:
        ValueError: If connection string is not set
    """
    value = os.getenv('CONNECTION_STRING')
    if not value:
        raise ValueError("CONNECTION_STRING is required but not set.")
    return value


def get_db_name() -> str:
    """
    Get database name.
    
    Returns:
        Database name string
        
    Raises:
        ValueError: If database name is not set
    """
    value = os.getenv('DB_NAME')
    if not value:
        raise ValueError("DB_NAME is required but not set.")
    return value


def get_db_table_name() -> str:
    """
    Get database table name.
    
    Returns:
        Database table name string
        
    Raises:
        ValueError: If table name is not set
    """
    value = os.getenv('DB_TABLE_NAME')
    if not value:
        raise ValueError("DB_TABLE_NAME is required but not set.")
    return value


# ============================================================================
# Utility Functions
# ============================================================================

def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable with optional default.
    
    Args:
        key: Environment variable key
        default: Default value if not set
        
    Returns:
        Environment variable value or default
    """
    return os.getenv(key, default)
