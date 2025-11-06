"""
FastAPI Application for Agentic RAG System

This module provides a REST API with Google OAuth authentication
for interacting with an AI-powered knowledge assistant.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Cookie, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from config import config
from src.agent.agent import run_agent_async


# ============================================================================
# Configuration
# ============================================================================

os.environ["OPENAI_API_KEY"] = config.get_openai_api_key()

# --- Google OAuth Configuration ---
GOOGLE_CLIENT_ID = config.get_google_client_id()
GOOGLE_CLIENT_SECRET = config.get_google_client_secret()
REDIRECT_URI = config.get_redirect_uri()
IS_PRODUCTION = not REDIRECT_URI.startswith("http://localhost")

SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [REDIRECT_URI],
    }
}

# Disable HTTPS requirement in development
if not IS_PRODUCTION:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# --- CORS Configuration ---
FRONTEND_URLS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    config.get_redirect_frontend_uri(),
    "https://sites.google.com",
    "https://552891955-atari-embeds.googleusercontent.com",
]

ALLOWED_ORIGINS_REGEX = [
    r"https://.*\.googleusercontent\.com",
    r"https://.*\.google\.com",
]


# ============================================================================
# Application Initialization
# ============================================================================

app = FastAPI(
    title="Agentic RAG API",
    description="FastAPI server for Agentic RAG system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex="|".join(ALLOWED_ORIGINS_REGEX),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Cookie", "Set-Cookie"],
    expose_headers=["Set-Cookie"]
)


# ============================================================================
# Session Management
# ============================================================================

sessions = {}


class Session:
    """
    Represents a user session with authentication information.
    
    Attributes:
        session_id: Unique identifier for the session
        user_info: Dictionary containing user information from OAuth
        created_at: Timestamp when session was created
        expires_at: Timestamp when session expires
    """
    
    def __init__(self, user_info: dict):
        self.session_id = secrets.token_urlsafe(32)
        self.user_info = user_info
        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(hours=24)


def get_session_from_cookie(session_token: Optional[str] = Cookie(None)) -> Optional[dict]:
    """
    Retrieve and validate session from cookie.
    
    Args:
        session_token: Session token from cookie
        
    Returns:
        User information if session is valid, None otherwise
    """
    if not session_token or session_token not in sessions:
        return None
    
    session = sessions[session_token]
    
    if datetime.now() > session.expires_at:
        print(f"Session expired: {session_token[:10]}...")
        del sessions[session_token]
        return None
    
    return session.user_info


# ============================================================================
# Pydantic Models
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for agent queries."""
    query: str


class QueryResponse(BaseModel):
    """Response model for agent queries."""
    answer: str


# ============================================================================
# Event Handlers
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("Agentic RAG API is starting up...")
    print(f"Server mode: {'PRODUCTION' if IS_PRODUCTION else 'DEVELOPMENT'}")
    print(f"Redirect URI: {REDIRECT_URI}")
    print(f"Frontend URI: {config.get_redirect_frontend_uri()}")
    print("API Documentation available at /docs")
    print("Application started successfully!")


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.get("/auth/google/login")
async def google_login():
    """
    Initiate Google OAuth flow.
    
    Returns:
        Redirect response to Google OAuth authorization URL
        
    Raises:
        HTTPException: If OAuth flow initialization fails
    """
    try:
        flow = Flow.from_client_config(
            client_config=GOOGLE_CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        print(f"Generated auth URL: {authorization_url}")
        print(f"State: {state}")
        
       
        response = RedirectResponse(url=authorization_url)
        response.set_cookie(
            key="oauth_state", 
            value=state, 
            httponly=True, 
            max_age=600,
            samesite="none",  # Changed for cross-site cookies
            secure=IS_PRODUCTION
        )
        return response
    except Exception as e:
        print(f"Error in google_login: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate login: {str(e)}")

@app.get("/auth/google/callback")
async def google_callback(
    request: Request, 
    code: str = None, 
    state: str = None, 
    oauth_state: str = Cookie(None)
):
    """
    Handle Google OAuth callback.
    
    Sets session cookie instead of URL redirect for security.
    
    Args:
        request: FastAPI request object
        code: Authorization code from Google
        state: State parameter for CSRF protection
        oauth_state: State stored in cookie for verification
        
    Returns:
        Redirect response to frontend with session cookie set

       
    """
    print(f"Callback received - Code: {code[:20] if code else None}..., State: {state}, Cookie State: {oauth_state}")
    
    error = request.query_params.get('error')
    if error:
        print(f"OAuth error: {error}")
        error_url = f"{config.get_redirect_frontend_uri()}?error={error}"
        return RedirectResponse(url=error_url)
    
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code received")
    
    if not state:
        raise HTTPException(status_code=400, detail="No state parameter received")
    
    if not oauth_state or oauth_state != state:
        print(f"State mismatch - Cookie: {oauth_state}, Param: {state}")
        raise HTTPException(status_code=400, detail="Invalid state parameter - CSRF protection")
    
    try:
        flow = Flow.from_client_config(
            client_config=GOOGLE_CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        flow.state = state
        
        print("Fetching token...")
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        print("Token fetched successfully, verifying ID token...")
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        
        print(f"User authenticated: {id_info.get('email')}")
        
        # Create session
        session = Session({
            'email': id_info.get('email'),
            'name': id_info.get('name'),
            'picture': id_info.get('picture'),
            'sub': id_info.get('sub')
        })
        sessions[session.session_id] = session

        print(f"Session created: {session.session_id[:10]}...")
        print(f"Total active sessions: {len(sessions)}")
        
        # Redirect to frontend WITHOUT session in URL
        response = RedirectResponse(url=config.get_redirect_frontend_uri())
        
        # Set session cookie
        response.set_cookie(
            key="session_token",
            value=session.session_id,
            httponly=True,  # Prevents JavaScript access (more secure)
            max_age=86400,  # 24 hours
            samesite="none",  # Required for cross-site (Google Sites -> your backend)
            secure=IS_PRODUCTION,  # HTTPS only in production
            domain=None  # Let browser decide
        )
        
        # Clear the oauth_state cookie
        response.delete_cookie("oauth_state")
        
        print(f"Session cookie set for user: {id_info.get('email')}")
        
        return response
        
    except Exception as e:
        print(f"Error during callback: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        error_url = f"{config.get_redirect_frontend_uri()}?error=auth_failed"
        return RedirectResponse(url=error_url)

@app.post("/auth/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    """
    Logout endpoint - clear session and cookie.
    
    Args:
        response: FastAPI response object
        session_token: Session token from cookie
        
    Returns:
        Success message with cleared session cookie
    """
    if session_token and session_token in sessions:
        del sessions[session_token]
        print(f"Session {session_token[:10]}... deleted")
        print(f"Remaining active sessions: {len(sessions)}")
    
    # Clear the session cookie
    response.delete_cookie("session_token", samesite="none", secure=IS_PRODUCTION)
    
    return {"success": True, "message": "Logged out successfully"}

@app.get("/auth/me")
async def get_current_user(session_token: Optional[str] = Cookie(None)):
    """
    Get current authenticated user information.
    
    Args:
        session_token: Session token from cookie
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If user is not authenticated
    """
    
    print(f"Checking authentication - Cookie present: {bool(session_token)}")
    
    user_info = get_session_from_cookie(session_token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    print(f"Valid session found for user: {user_info.get('email')}")
    return user_info


# ============================================================================
# Agent Endpoints
# ============================================================================

@app.post("/ask", response_model=QueryResponse)
async def ask_agent(
    request: QueryRequest,
    session_token: Optional[str] = Cookie(None)
):
    """
    Protected endpoint to interact with the AI agent.
    
    Args:
        request: Query request containing user question
        session_token: Session token from cookie
        
    Returns:
        QueryResponse containing agent's answer
        
    Raises:
        HTTPException: If user is not authenticated or agent fails
    """
    
    user_info = get_session_from_cookie(session_token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    print(f"Query from user: {user_info.get('email', 'Unknown')} - {user_info.get('name', 'Unknown')}")
    print(f"Query: {request.query}")
    
    try:
        response_data = await run_agent_async(request.query)
        answer = response_data.answer if hasattr(response_data, 'answer') else str(response_data)
        return {"answer": answer}
    except Exception as e:
        print(f"Error in ask_agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Dictionary with status and active session count
    """
    return {
        "status": "ok", 
        "message": "Agentic RAG API is running",
        "active_sessions": len(sessions)
    }


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("Starting Agentic RAG API Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)