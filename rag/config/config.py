"""Simple functional configuration module for RAG application."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment once at module import
if os.path.isfile('.env'):
    load_dotenv()


# OpenAI Configuration
def get_openai_api_key() -> str:
    value = os.getenv('OPENAI_API_KEY')
    if not value:
        raise ValueError("OPENAI_API_KEY is required but not set.")
    return value


# Azure OpenAI Configuration
def get_azure_openai_model() -> str:
    return os.getenv('AZURE_OPENAI_MODEL', 'gpt-4o')


def get_azure_openai_deployment_name() -> str:
    return os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o')


def get_azure_openai_api_key() -> str:
    value = os.getenv('AZURE_OPENAI_API_KEY')
    if not value:
        raise ValueError("AZURE_OPENAI_API_KEY is required but not set.")
    return value


def get_azure_openai_endpoint() -> str:
    value = os.getenv('AZURE_OPENAI_ENDPOINT')
    if not value:
        raise ValueError("AZURE_OPENAI_ENDPOINT is required but not set.")
    return value


def get_azure_openai_api_version() -> str:
    return os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')


# Azure Embedding Configuration
def get_azure_endpoint_embedding() -> str:
    value = os.getenv('AZURE_ENDPOINT_EMBEDDING')
    if not value:
        raise ValueError("AZURE_ENDPOINT_EMBEDDING is required but not set.")
    return value


def get_azure_api_key_embedding() -> str:
    value = os.getenv('AZURE_API_KEY_EMBEDDING')
    if not value:
        raise ValueError("AZURE_API_KEY_EMBEDDING is required but not set.")
    return value


# Google OAuth Configuration
def get_google_client_id() -> str:
    value = os.getenv('GOOGLE_CLIENT_ID')
    if not value:
        raise ValueError("GOOGLE_CLIENT_ID is required but not set.")
    return value


def get_google_client_secret() -> str:
    value = os.getenv('GOOGLE_CLIENT_SECRET')
    if not value:
        raise ValueError("GOOGLE_CLIENT_SECRET is required but not set.")
    return value


def get_redirect_uri() -> str:
    value = os.getenv('REDIRECT_URI')
    if not value:
        raise ValueError("REDIRECT_URI is required but not set.")
    return value


def get_redirect_frontend_uri() -> Optional[str]:
    return os.getenv('REDIRECT_FRONTEND_URI')


# Database Configuration
def get_db_connection_string() -> str:
    value = os.getenv('CONNECTION_STRING')
    if not value:
        raise ValueError("CONNECTION_STRING is required but not set.")
    return value


def get_db_name() -> str:
    value = os.getenv('DB_NAME')
    if not value:
        raise ValueError("DB_NAME is required but not set.")
    return value


def get_db_table_name() -> str:
    value = os.getenv('DB_TABLE_NAME')
    if not value:
        raise ValueError("DB_TABLE_NAME is required but not set.")
    return value


# Utility function
def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key, default)
