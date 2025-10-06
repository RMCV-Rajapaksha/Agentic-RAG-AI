import asyncio
import json
from fastapi import FastAPI, Depends, HTTPException, status, Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from config.config import get_config
from src.agent.agent import run_agent_async
import os
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import secrets
from datetime import datetime, timedelta

# --- Configuration ---
config = get_config()
os.environ["OPENAI_API_KEY"] = config.openai_api_key

# --- Google OAuth Configuration ---
GOOGLE_CLIENT_ID = config.google_client_id
GOOGLE_CLIENT_SECRET = config.google_client_secret
REDIRECT_URI = config.redirect_uri

# Determine if we're in production based on redirect URI
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

# For Google OAuth, disable HTTPS requirement in development
if not IS_PRODUCTION:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# --- FastAPI App Initialization ---
app = FastAPI(title="Agentic RAG API", description="FastAPI server for Agentic RAG system", version="1.0.0")

# --- CORS Middleware - CRITICAL FIX ---
# Add your frontend URL explicitly
FRONTEND_URLS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    config.redirect_frontend_uri  # Your deployed frontend if exists
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,  # Specific origins instead of "*"
    allow_credentials=True,  # This is critical for cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# --- Session Management ---
sessions = {}

class Session:
    def __init__(self, user_info):
        self.session_id = secrets.token_urlsafe(32)
        self.user_info = user_info
        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(hours=24)

def verify_session(session_id: str = Cookie(None)):
    """Verify session from cookie"""
    if not session_id or session_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    session = sessions[session_id]
    
    if datetime.now() > session.expires_at:
        del sessions[session_id]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return session.user_info

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

# --- Event Handlers ---
@app.on_event("startup")
async def startup_event():
    print("🚀 Agentic RAG API is starting up...")
    print(f"📡 Server mode: {'PRODUCTION' if IS_PRODUCTION else 'DEVELOPMENT'}")
    print("📚 API Documentation available at /docs")
    print("✅ Application started successfully!")

# --- API Endpoints ---
@app.get("/auth/google/login")
async def google_login():
    """Initiate Google OAuth flow."""
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
            samesite="lax",  # Changed from "none" for better compatibility
            secure=IS_PRODUCTION
        )
        return response
    except Exception as e:
        print(f"Error in google_login: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate login: {str(e)}")

@app.get("/auth/google/callback")
async def google_callback(request: Request, code: str = None, state: str = None, oauth_state: str = Cookie(None)):
    """Google OAuth callback to handle user authentication."""
    print(f"Callback received - Code: {code[:20] if code else None}..., State: {state}, Cookie State: {oauth_state}")
    
    error = request.query_params.get('error')
    if error:
        print(f"OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
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
        
        session = Session({
            'email': id_info.get('email'),
            'name': id_info.get('name'),
            'picture': id_info.get('picture'),
            'sub': id_info.get('sub')
        })
        sessions[session.session_id] = session
        
        print(f"Session created: {session.session_id}")
        
        # Redirect with session token in URL as fallback
        frontend_url = f"{config.redirect_frontend_uri}?session={session.session_id}"
        response = RedirectResponse(url=frontend_url)
        
        # Try to set cookie (may not work cross-origin)
        response.set_cookie(
            key="session_id",
            value=session.session_id,
            httponly=True,
            secure=IS_PRODUCTION,
            samesite="lax",  # Changed from "none"
            max_age=86400
        )
        response.delete_cookie("oauth_state")
        
        return response
        
    except Exception as e:
        print(f"❌ Error during callback: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@app.post("/auth/logout")
async def logout(session_id: str = Cookie(None)):
    """Logout - clear session and cookie."""
    if session_id and session_id in sessions:
        del sessions[session_id]
        print(f"Session {session_id} deleted")
    
    response = JSONResponse({"success": True})
    response.delete_cookie("session_id")
    return response

@app.get("/auth/me")
async def get_current_user(
    session_id: str = Cookie(None),
    authorization: str = None
):
    """Get current user info if authenticated.
    Supports both cookie and Authorization header."""
    
    # Try cookie first
    if session_id and session_id in sessions:
        session = sessions[session_id]
        if datetime.now() <= session.expires_at:
            return session.user_info
    
    # Try Authorization header as fallback
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        if token in sessions:
            session = sessions[token]
            if datetime.now() <= session.expires_at:
                return session.user_info
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )

@app.post("/ask", response_model=QueryResponse)
async def ask_agent(
    request: QueryRequest,
    session_id: str = Cookie(None),
    authorization: str = None
):
    """Protected endpoint to interact with the agent.
    Supports both cookie and Authorization header."""
    
    user_info = None
    
    # Try cookie first
    if session_id and session_id in sessions:
        session = sessions[session_id]
        if datetime.now() <= session.expires_at:
            user_info = session.user_info
    
    # Try Authorization header as fallback
    if not user_info and authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        if token in sessions:
            session = sessions[token]
            if datetime.now() <= session.expires_at:
                user_info = session.user_info
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    print(f"Query from user: {user_info.get('email', 'Unknown')} - {user_info.get('name', 'Unknown')}")
    response_data = await run_agent_async(request.query)

    answer = response_data.answer if hasattr(response_data, 'answer') else str(response_data)
    return {"answer": answer}

@app.get("/")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Agentic RAG API is running"}

# --- Main Execution ---
if __name__ == "__main__":
    import uvicorn
    print("🔥 Starting Agentic RAG API Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)