import os
import tempfile
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# OpenAI Configuration
def get_openai_api_key():
    return os.getenv('OPENAI_API_KEY')


# Database Configuration
def get_db_name():
    return os.getenv('DB_NAME')


def get_db_connection_string():
    return os.getenv('CONNECTION_STRING')


def get_db_table_name():
    return os.getenv('DB_TABLE_NAME')


# Google Drive Configuration
def get_google_drive_folder_id():
    return os.getenv('FOLDER_ID')


# Azure OpenAI Configuration
def get_azure_openai_model():
    return os.getenv('AZURE_OPENAI_MODEL')


def get_azure_openai_deployment_name():
    return os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')


def get_azure_openai_api_key():
    return os.getenv('AZURE_OPENAI_API_KEY')


def get_azure_openai_endpoint():
    return os.getenv('AZURE_OPENAI_ENDPOINT')


def get_azure_openai_api_version():
    return os.getenv('AZURE_OPENAI_API_VERSION')


# Azure Embedding Configuration
def get_azure_endpoint_embedding():
    return os.getenv('AZURE_ENDPOINT_EMBEDDING')


def get_azure_api_key_embedding():
    return os.getenv('AZURE_API_KEY_EMBEDDING')


# Google Credentials
def get_google_credentials():
    private_key = os.getenv("GOOGLE_PRIVATE_KEY")
    if private_key:
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
    creds = get_google_credentials()
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w')
    json.dump(creds, temp)
    temp.close()
    return temp.name