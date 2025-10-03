import asyncio
import json
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from config.config import get_config
from src.agent.agent import run_agent_async
import os
from google.auth.transport import requests
from google.oauth2 import id_token

config = get_config()
os.environ["OPENAI_API_KEY"] = config.openai_api_key

app = FastAPI(title="Agentic RAG API", description="FastAPI server for Agentic RAG system", version="1.0.0")

# Security scheme
security = HTTPBearer()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


GOOGLE_CLIENT_ID = config.google_client_id

async def verify_google_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Google ID token"""
    try:
        token = credentials.credentials
        print(token)
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
            
        return idinfo
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.on_event("startup")
async def startup_event():
    print("🚀 Agentic RAG API is starting up...")
    print("📡 Server is running on http://127.0.0.1:8000")
    print("📚 API Documentation available at http://127.0.0.1:8000/docs")
    print("✅ Application started successfully!")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/ask", response_model=QueryResponse)
async def ask_agent(request: QueryRequest, user_info: dict = Depends(verify_google_token)):
    """
    Protected endpoint - requires Google authentication
    """
    print(f"Query from user: {user_info.get('email', 'Unknown')} - {user_info.get('name', 'Unknown')}")
    response = await run_agent_async(request.query)

    if hasattr(response, 'answer'):
        result = {"answer": response.answer}
    else:
        result = {"answer": str(response)}

    return result

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Agentic RAG API is running "}

# uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    print("🔥 Starting Agentic RAG API Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)