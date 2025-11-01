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
from typing import Optional, Dict, Any

# Third-party imports
from dotenv import load_dotenv

# Local imports
from .exceptions import ConfigurationError
from .constants import ERROR_MSG_MISSING_ENV_VAR


# ===============================
# Initialize
# ===============================
load_dotenv()


# ===============================
# Helper Functions
# ===============================

def _get_env_variable(
    var_name: str,
    required: bool = True,
    default: Optional[str] = None
) -> Optional[str]:
    """
    Get environment variable with optional validation.
    
    Args:
        var_name: Name of the environment variable
        required: Whether the variable is required
        default: Default value if not found
        
    Returns:
        Environment variable value or default
        
    Raises:
        ConfigurationError: If required variable is missing
    """
    value = os.getenv(var_name, default)
    
    if required and not value:
        error_msg = ERROR_MSG_MISSING_ENV_VAR.format(var_name)
        print(f"ERROR: {error_msg}")
        raise ConfigurationError(error_msg)
    
    return value


# ===============================
# OpenAI Configuration
# ===============================

def get_openai_api_key() -> Optional[str]:
    """
    Get OpenAI API key from environment.
    
    Returns:
        OpenAI API key string or None
    """
    return _get_env_variable('OPENAI_API_KEY', required=False)


# ===============================
# Database Configuration
# ===============================

def get_db_name() -> str:
    """
    Get database name from environment.
    
    Returns:
        Database name string
        
    Raises:
        ConfigurationError: If DB_NAME is not set
    """
    return _get_env_variable('DB_NAME', required=True)


def get_db_connection_string() -> str:
    """
    Get database connection string from environment.
    
    Returns:
        PostgreSQL connection string
        
    Raises:
        ConfigurationError: If CONNECTION_STRING is not set
    """
    return _get_env_variable('CONNECTION_STRING', required=True)


def get_db_table_name() -> str:
    """
    Get database table name from environment.
    
    Returns:
        Table name string
        
    Raises:
        ConfigurationError: If DB_TABLE_NAME is not set
    """
    return _get_env_variable('DB_TABLE_NAME', required=True)


# ===============================
# Google Drive Configuration
# ===============================

def get_google_drive_folder_id() -> Optional[str]:
    """
    Get Google Drive folder ID from environment.
    
    Returns:
        Google Drive folder ID string or None
    """
    return _get_env_variable('FOLDER_ID', required=False)


# ===============================
# Azure OpenAI Configuration
# ===============================

def get_azure_openai_model() -> Optional[str]:
    """
    Get Azure OpenAI model name from environment.
    
    Returns:
        Model name string or None
    """
    return _get_env_variable('AZURE_OPENAI_MODEL', required=False)


def get_azure_openai_deployment_name() -> Optional[str]:
    """
    Get Azure OpenAI deployment name from environment.
    
    Returns:
        Deployment name string or None
    """
    return _get_env_variable('AZURE_OPENAI_DEPLOYMENT_NAME', required=False)


def get_azure_openai_api_key() -> Optional[str]:
    """
    Get Azure OpenAI API key from environment.
    
    Returns:
        API key string or None
    """
    return _get_env_variable('AZURE_OPENAI_API_KEY', required=False)


def get_azure_openai_endpoint() -> Optional[str]:
    """
    Get Azure OpenAI endpoint URL from environment.
    
    Returns:
        Endpoint URL string or None
    """
    return _get_env_variable('AZURE_OPENAI_ENDPOINT', required=False)


def get_azure_openai_api_version() -> Optional[str]:
    """
    Get Azure OpenAI API version from environment.
    
    Returns:
        API version string or None
    """
    return _get_env_variable('AZURE_OPENAI_API_VERSION', required=False)


# ===============================
# Azure Embedding Configuration
# ===============================

def get_azure_endpoint_embedding() -> Optional[str]:
    """
    Get Azure embedding endpoint URL from environment.
    
    Returns:
        Embedding endpoint URL string or None
    """
    return _get_env_variable('AZURE_ENDPOINT_EMBEDDING', required=False)


def get_azure_api_key_embedding() -> Optional[str]:
    """
    Get Azure embedding API key from environment.
    
    Returns:
        Embedding API key string or None
    """
    return _get_env_variable('AZURE_API_KEY_EMBEDDING', required=False)


# ===============================
# Google Service Account Configuration
# ===============================

def get_google_credentials() -> Dict[str, Any]:
    """
    Get Google service account credentials from environment variables.
    
    Returns:
        Dictionary containing all required Google service account fields
        
    Raises:
        ConfigurationError: If required Google credentials are missing
    """
    try:
        private_key = _get_env_variable("GOOGLE_PRIVATE_KEY", required=False)
        if private_key:
            # Replace escaped newlines with actual newlines
            private_key = private_key.replace('\\n', '\n')
        
        return {
            "type": _get_env_variable("GOOGLE_TYPE", required=False),
            "project_id": _get_env_variable("GOOGLE_PROJECT_ID", required=False),
            "private_key_id": _get_env_variable("GOOGLE_PRIVATE_KEY_ID", required=False),
            "private_key": private_key,
            "client_email": _get_env_variable("GOOGLE_CLIENT_EMAIL", required=False),
            "client_id": _get_env_variable("GOOGLE_CLIENT_ID", required=False),
            "auth_uri": _get_env_variable("GOOGLE_AUTH_URI", required=False),
            "token_uri": _get_env_variable("GOOGLE_TOKEN_URI", required=False),
            "auth_provider_x509_cert_url": _get_env_variable(
                "GOOGLE_AUTH_PROVIDER_X509_CERT_URL", required=False
            ),
            "client_x509_cert_url": _get_env_variable(
                "GOOGLE_CLIENT_X509_CERT_URL", required=False
            ),
            "universe_domain": _get_env_variable("GOOGLE_UNIVERSE_DOMAIN", required=False),
        }
    except Exception as e:
        print(f"ERROR: Error loading Google credentials: {e}")
        raise ConfigurationError(f"Failed to load Google credentials: {e}")


def get_google_credentials_json_path() -> str:
    """
    Create a temporary JSON file with Google service account credentials.
    
    This is required by some libraries that expect a file path instead of
    a dictionary for credentials.
    
    Returns:
        Path to temporary JSON file containing credentials
        
    Raises:
        ConfigurationError: If credentials cannot be written to file
    """
    try:
        creds = get_google_credentials()
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w')
        json.dump(creds, temp)
        temp.close()
        print(f"Created temporary credentials file: {temp.name}")
        return temp.name
    except Exception as e:
        print(f"ERROR: Error creating credentials file: {e}")
        raise ConfigurationError(f"Failed to create credentials file: {e}")