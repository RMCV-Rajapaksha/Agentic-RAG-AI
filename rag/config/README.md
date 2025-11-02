# Configuration Module

A simple functional programming approach to configuration management.

## Quick Start

```python
from config import config

# Get any configuration value
api_key = config.get_openai_api_key()
db_name = config.get_db_name()
```

## Features

- ✅ **Simple**: Just functions, no classes or complex patterns
- ✅ **Functional**: Pure functions, straightforward approach
- ✅ **Type-safe**: Full type hints for IDE autocomplete
- ✅ **Validated**: Required variables checked when accessed
- ✅ **Fast**: Environment loaded once at module import

## Available Functions

### OpenAI
- `get_openai_api_key()` - OpenAI API key

### Azure OpenAI
- `get_azure_openai_model()` - Model name (default: 'gpt-4o')
- `get_azure_openai_deployment_name()` - Deployment name (default: 'gpt-4o')
- `get_azure_openai_api_key()` - API key
- `get_azure_openai_endpoint()` - Endpoint URL
- `get_azure_openai_api_version()` - API version (default: '2024-12-01-preview')

### Azure Embeddings
- `get_azure_endpoint_embedding()` - Embedding endpoint
- `get_azure_api_key_embedding()` - Embedding API key

### Google OAuth
- `get_google_client_id()` - OAuth client ID
- `get_google_client_secret()` - OAuth client secret
- `get_redirect_uri()` - OAuth redirect URI
- `get_redirect_frontend_uri()` - Frontend redirect URI (optional)

### Database
- `get_db_connection_string()` - PostgreSQL connection string
- `get_db_name()` - Database name
- `get_db_table_name()` - Table name for vectors

### Utilities
- `get_env_var(key, default=None)` - Get any environment variable

## Environment Variables Required

Create a `.env` file with:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_MODEL=gpt-4o
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Azure Embeddings
AZURE_ENDPOINT_EMBEDDING=https://...
AZURE_API_KEY_EMBEDDING=...

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
REDIRECT_URI=http://localhost:8000/auth/google/callback
REDIRECT_FRONTEND_URI=http://localhost:3000

# Database
CONNECTION_STRING=postgresql://...
DB_NAME=your_db
DB_TABLE_NAME=your_table
```

## Error Handling

Functions raise `ValueError` if required environment variables are missing:

```python
try:
    api_key = config.get_openai_api_key()
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Best Practices

1. **Import once at module level**
   ```python
   from config import config
   ```

2. **Call functions when needed**
   ```python
   api_key = config.get_openai_api_key()
   ```

3. **Use get_env_var for custom variables**
   ```python
   custom = config.get_env_var('CUSTOM_VAR', 'default')
   ```

## Implementation

- Simple and straightforward
- No caching complexity
- Environment loaded once at import time
- Each function directly reads from `os.getenv()`
- Pure functional approach
