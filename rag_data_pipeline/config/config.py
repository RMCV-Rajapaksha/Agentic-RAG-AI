"""
Configuration Module

This module manages all configuration settings for the RAG data pipeline,
including API keys, database connections, and service account credentials.
All sensitive data is loaded from environment variables.
"""

# Standard library imports
import json
import os
import tempfile

# Third-party imports
from dotenv import load_dotenv


# ===============================
# Load Environment Variables
# ===============================
load_dotenv()


# ===============================
# OpenAI Configuration
# ===============================

def get_openai_api_key():
    """
    Get OpenAI API key from environment.
    
    Returns:
        OpenAI API key string
    """
    return os.getenv('OPENAI_API_KEY')


# ===============================
# Database Configuration
# ===============================

def get_db_name():
    """
    Get database name from environment.
    
    Returns:
        Database name string
    """
    return os.getenv('DB_NAME')


def get_db_connection_string():
    """
    Get database connection string from environment.
    
    Returns:
        PostgreSQL connection string
    """
    return os.getenv('CONNECTION_STRING')


def get_db_table_name():
    """
    Get database table name from environment.
    
    Returns:
        Table name string
    """
    return os.getenv('DB_TABLE_NAME')


# ===============================
# Google Drive Configuration
# ===============================

def get_google_drive_folder_id():
    """
    Get Google Drive folder ID from environment.
    
    Returns:
        Google Drive folder ID string
    """
    return os.getenv('FOLDER_ID')


# ===============================
# Azure OpenAI Configuration
# ===============================

def get_azure_openai_model():
    """
    Get Azure OpenAI model name from environment.
    
    Returns:
        Model name string
    """
    return os.getenv('AZURE_OPENAI_MODEL')


def get_azure_openai_deployment_name():
    """
    Get Azure OpenAI deployment name from environment.
    
    Returns:
        Deployment name string
    """
    return os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')


def get_azure_openai_api_key():
    """
    Get Azure OpenAI API key from environment.
    
    Returns:
        API key string
    """
    return os.getenv('AZURE_OPENAI_API_KEY')


def get_azure_openai_endpoint():
    """
    Get Azure OpenAI endpoint URL from environment.
    
    Returns:
        Endpoint URL string
    """
    return os.getenv('AZURE_OPENAI_ENDPOINT')


def get_azure_openai_api_version():
    """
    Get Azure OpenAI API version from environment.
    
    Returns:
        API version string
    """
    return os.getenv('AZURE_OPENAI_API_VERSION')


# ===============================
# Azure Embedding Configuration
# ===============================

def get_azure_endpoint_embedding():
    """
    Get Azure embedding endpoint URL from environment.
    
    Returns:
        Embedding endpoint URL string
    """
    return os.getenv('AZURE_ENDPOINT_EMBEDDING')


def get_azure_api_key_embedding():
    """
    Get Azure embedding API key from environment.
    
    Returns:
        Embedding API key string
    """
    return os.getenv('AZURE_API_KEY_EMBEDDING')


# ===============================
# Google Service Account Configuration
# ===============================

def get_google_credentials():
    """
    Get Google service account credentials from environment variables.
    
    Returns:
        Dictionary containing all required Google service account fields
    """
    private_key = os.getenv("GOOGLE_PRIVATE_KEY")
    if private_key:
        # Replace escaped newlines with actual newlines
        private_key = private_key.replace('\\n', '\n')
    
    return {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": private_key,
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN"),
    }


def get_google_credentials_json_path():
    """
    Create a temporary JSON file with Google service account credentials.
    
    This is required by some libraries that expect a file path instead of
    a dictionary for credentials.
    
    Returns:
        Path to temporary JSON file containing credentials
    """
    creds = get_google_credentials()
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w')
    json.dump(creds, temp)
    temp.close()
    return temp.name