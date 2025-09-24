# Use Python 3.13 slim image as base for better performance and smaller size
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies, create requirements.txt, and install Python dependencies
RUN apt-get update && apt-get install -y \
    build-essential \ 
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && echo "aiohappyeyeballs==2.6.1" > requirements.txt \
    && echo "aiohttp==3.12.15" >> requirements.txt \
    && echo "aiosignal==1.4.0" >> requirements.txt \
    && echo "aiosqlite==0.21.0" >> requirements.txt \
    && echo "annotated-types==0.7.0" >> requirements.txt \
    && echo "anyio==4.10.0" >> requirements.txt \
    && echo "asyncpg==0.30.0" >> requirements.txt \
    && echo "attrs==25.3.0" >> requirements.txt \
    && echo "banks==2.2.0" >> requirements.txt \
    && echo "beautifulsoup4==4.13.5" >> requirements.txt \
    && echo "certifi==2025.8.3" >> requirements.txt \
    && echo "charset-normalizer==3.4.3" >> requirements.txt \
    && echo "click==8.2.1" >> requirements.txt \
    && echo "colorama==0.4.6" >> requirements.txt \
    && echo "dataclasses-json==0.6.7" >> requirements.txt \
    && echo "defusedxml==0.7.1" >> requirements.txt \
    && echo "deprecated==1.2.18" >> requirements.txt \
    && echo "dirtyjson==1.0.8" >> requirements.txt \
    && echo "distro==1.9.0" >> requirements.txt \
    && echo "fastapi==0.116.1" >> requirements.txt \
    && echo "filetype==1.2.0" >> requirements.txt \
    && echo "frozenlist==1.7.0" >> requirements.txt \
    && echo "fsspec==2025.9.0" >> requirements.txt \
    && echo "greenlet==3.2.4" >> requirements.txt \
    && echo "griffe==1.14.0" >> requirements.txt \
    && echo "h11==0.16.0" >> requirements.txt \
    && echo "httpcore==1.0.9" >> requirements.txt \
    && echo "httpx==0.28.1" >> requirements.txt \
    && echo "idna==3.10" >> requirements.txt \
    && echo "jinja2==3.1.6" >> requirements.txt \
    && echo "jiter==0.10.0" >> requirements.txt \
    && echo "joblib==1.5.2" >> requirements.txt \
    && echo "llama-cloud==0.1.35" >> requirements.txt \
    && echo "llama-cloud-services==0.6.54" >> requirements.txt \
    && echo "llama-index==0.14.0" >> requirements.txt \
    && echo "llama-index-cli==0.5.0" >> requirements.txt \
    && echo "llama-index-core==0.13.6" >> requirements.txt \
    && echo "llama-index-embeddings-openai==0.5.1" >> requirements.txt \
    && echo "llama-index-indices-managed-llama-cloud==0.9.4" >> requirements.txt \
    && echo "llama-index-instrumentation==0.4.0" >> requirements.txt \
    && echo "llama-index-llms-openai==0.5.6" >> requirements.txt \
    && echo "llama-index-readers-file==0.5.4" >> requirements.txt \
    && echo "llama-index-readers-llama-parse==0.5.1" >> requirements.txt \
    && echo "llama-index-vector-stores-postgres==0.6.6" >> requirements.txt \
    && echo "llama-index-workflows==1.3.0" >> requirements.txt \
    && echo "llama-parse==0.6.54" >> requirements.txt \
    && echo "markupsafe==3.0.2" >> requirements.txt \
    && echo "marshmallow==3.26.1" >> requirements.txt \
    && echo "multidict==6.6.4" >> requirements.txt \
    && echo "mypy-extensions==1.1.0" >> requirements.txt \
    && echo "nest-asyncio==1.6.0" >> requirements.txt \
    && echo "networkx==3.5" >> requirements.txt \
    && echo "nltk==3.9.1" >> requirements.txt \
    && echo "numpy==2.3.3" >> requirements.txt \
    && echo "openai==1.107.1" >> requirements.txt \
    && echo "packaging==25.0" >> requirements.txt \
    && echo "pandas==2.2.3" >> requirements.txt \
    && echo "pgvector==0.4.1" >> requirements.txt \
    && echo "pillow==11.3.0" >> requirements.txt \
    && echo "platformdirs==4.4.0" >> requirements.txt \
    && echo "propcache==0.3.2" >> requirements.txt \
    && echo "psycopg2==2.9.10" >> requirements.txt \
    && echo "psycopg2-binary==2.9.10" >> requirements.txt \
    && echo "pydantic==2.11.7" >> requirements.txt \
    && echo "pydantic-core==2.33.2" >> requirements.txt \
    && echo "pypdf==6.0.0" >> requirements.txt \
    && echo "python-dateutil==2.9.0.post0" >> requirements.txt \
    && echo "python-dotenv==1.1.1" >> requirements.txt \
    && echo "pytz==2025.2" >> requirements.txt \
    && echo "pyyaml==6.0.2" >> requirements.txt \
    && echo "regex==2025.9.1" >> requirements.txt \
    && echo "requests==2.32.5" >> requirements.txt \
    && echo "setuptools==80.9.0" >> requirements.txt \
    && echo "six==1.17.0" >> requirements.txt \
    && echo "sniffio==1.3.1" >> requirements.txt \
    && echo "soupsieve==2.8" >> requirements.txt \
    && echo "sqlalchemy==2.0.43" >> requirements.txt \
    && echo "starlette==0.47.3" >> requirements.txt \
    && echo "striprtf==0.0.26" >> requirements.txt \
    && echo "tenacity==9.1.2" >> requirements.txt \
    && echo "tiktoken==0.11.0" >> requirements.txt \
    && echo "tqdm==4.67.1" >> requirements.txt \
    && echo "typing-extensions==4.15.0" >> requirements.txt \
    && echo "typing-inspect==0.9.0" >> requirements.txt \
    && echo "typing-inspection==0.4.1" >> requirements.txt \
    && echo "tzdata==2025.2" >> requirements.txt \
    && echo "urllib3==2.5.0" >> requirements.txt \
    && echo "uvicorn==0.35.0" >> requirements.txt \
    && echo "wrapt==1.17.3" >> requirements.txt \
    && echo "yarl==1.20.1" >> requirements.txt \
    && echo "youtube-transcript-api==1.2.2" >> requirements.txt \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy all application files to the working directory
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the FastAPI application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
