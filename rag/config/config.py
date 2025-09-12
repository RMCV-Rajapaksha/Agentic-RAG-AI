import os
from typing import Optional
import tempfile, json
from dotenv import load_dotenv

class Config:
    _instance: Optional['Config'] = None
    _initialized: bool = False

    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Load environment variables from .env file
            load_dotenv()

            # Required variables
            self._openai_api_key = self._get_required_env('OPENAI_API_KEY')
            self._db_name = self._get_required_env('DB_NAME')
            self._db_user = self._get_required_env('DB_USER')
            self._db_password = self._get_required_env('DB_PASSWORD')

            # Optional variables with defaults
            self._db_host = os.getenv('DB_HOST', 'localhost')
            self._db_port = int(os.getenv('DB_PORT', '5432'))  


            self._db_connection_string = self._get_required_env('CONNECTION_STRING')
            self._db_name = self._get_required_env('DB_NAME')
            self._db_table_name = self._get_required_env('DB_TABLE_NAME')

            self._google_drive_folder_id = self._get_required_env('FOLDER_ID')

            # Google service account credentials from env
            self._google_credentials = {
                "type": os.getenv("GOOGLE_TYPE"),
                "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n') if os.getenv("GOOGLE_PRIVATE_KEY") else None,
                "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
                "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
                "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN"),
            }

            Config._initialized = True

    # Internal helper to enforce required environment variables
    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Environment variable '{key}' is required but not set.")
        return value

    # Properties
    @property
    def openai_api_key(self) -> str:
        return self._openai_api_key

    @property
    def db_name(self) -> str:
        return self._db_name

    @property
    def db_user(self) -> str:
        return self._db_user

    @property
    def db_password(self) -> str:
        return self._db_password

    @property
    def db_host(self) -> str:
        return self._db_host

    @property
    def db_port(self) -> int:
        return self._db_port

    @property
    def db_connection_string(self) -> str:
        return self._db_connection_string

    @property
    def db_table_name(self) -> str:
        return self._db_table_name
    
    @property
    def db_name(self) -> str:
        return self._db_name
    
    @property
    def google_drive_folder_id(self) -> str:
        return self._google_drive_folder_id

    @property
    def google_credentials(self) -> dict:
        """Returns Google service account credentials as a dictionary."""
        return dict(self._google_credentials)

    def google_credentials_json_path(self) -> str:
        """Writes Google service account credentials to a temporary JSON file and returns its path."""
        
        creds_dict = dict(self._google_credentials)
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w')
        json.dump(creds_dict, temp)
        temp.close()
        return temp.name

    # General getter for any env variable
    def get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default)

    # Hide secrets in debug output
    def __repr__(self) -> str:
        return f"<Config(openai_api_key={'*' * 10 if self._openai_api_key else None}, db_password={'*' * 10 if self._db_password else None})>"

# Singleton accessor
def get_config() -> Config:
    return Config()
