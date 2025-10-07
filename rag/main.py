import asyncio
import json
from fastapi import FastAPI, Depends, HTTPException, status, Cookie, Request, Header
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
from typing import Optional

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

# --- CORS Middleware ---
FRONTEND_URLS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    config.redirect_frontend_uri
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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

def get_session_from_request(
    session_id: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None),
    x_session_token: Optional[str] = Header(None)
) -> Optional[dict]:
    """
    Extract session from multiple sources:
    1. Cookie (session_id)
    2. Authorization header (Bearer token)
    3. X-Session-Token header
    """
    token = None
    
    # Try cookie first
    if session_id:
        token = session_id
        print(f"🍪 Using session from cookie: {token[:10]}...")
    
    # Try Authorization header
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        print(f"🔑 Using session from Authorization header: {token[:10]}...")
    
    # Try custom header
    elif x_session_token:
        token = x_session_token
        print(f"📋 Using session from X-Session-Token header: {token[:10]}...")
    
    if not token:
        print("❌ No session token found in request")
        return None
    
    if token not in sessions:
        print(f"❌ Session token not found in sessions store: {token[:10]}...")
        return None
    
    session = sessions[token]
    
    if datetime.now() > session.expires_at:
        print(f"⏰ Session expired: {token[:10]}...")
        del sessions[token]
        return None
    
    print(f"✅ Valid session found for user: {session.user_info.get('email')}")
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
    print(f"🔗 Redirect URI: {REDIRECT_URI}")
    print(f"🌐 Frontend URI: {config.redirect_frontend_uri}")
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
        
        print(f"🔐 Generated auth URL: {authorization_url}")
        print(f"📝 State: {state}")
        
        response = RedirectResponse(url=authorization_url)
        response.set_cookie(
            key="oauth_state", 
            value=state, 
            httponly=True, 
            max_age=600,
            samesite="lax",
            secure=IS_PRODUCTION,
            path="/"  # Explicitly set path
        )
        return response
    except Exception as e:
        print(f"❌ Error in google_login: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate login: {str(e)}")

@app.get("/auth/google/callback")
async def google_callback(
    request: Request, 
    code: str = None, 
    state: str = None, 
    oauth_state: str = Cookie(None)
):
    """Google OAuth callback to handle user authentication."""
    print(f"📥 Callback received - Code: {code[:20] if code else None}..., State: {state}, Cookie State: {oauth_state}")
    
    error = request.query_params.get('error')
    if error:
        print(f"❌ OAuth error: {error}")
        error_url = f"{config.redirect_frontend_uri}?error={error}"
        return RedirectResponse(url=error_url)
    
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code received")
    
    if not state:
        raise HTTPException(status_code=400, detail="No state parameter received")
    
    if not oauth_state or oauth_state != state:
        print(f"⚠️ State mismatch - Cookie: {oauth_state}, Param: {state}")
        raise HTTPException(status_code=400, detail="Invalid state parameter - CSRF protection")
    
    try:
        flow = Flow.from_client_config(
            client_config=GOOGLE_CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        flow.state = state
        
        print("🔄 Fetching token...")
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        print("✅ Token fetched successfully, verifying ID token...")
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        
        print(f"👤 User authenticated: {id_info.get('email')}")
        
        session = Session({
            'email': id_info.get('email'),
            'name': id_info.get('name'),
            'picture': id_info.get('picture'),
            'sub': id_info.get('sub')
        })
        sessions[session.session_id] = session
        
        print(f"🎫 Session created: {session.session_id}")
        print(f"📊 Total active sessions: {len(sessions)}")
        
        # Return session token in URL - frontend will handle storage
        frontend_url = f"{config.redirect_frontend_uri}?session={session.session_id}"
        response = RedirectResponse(url=frontend_url)
        
        # Still try to set cookie as backup
        response.set_cookie(
            key="session_id",
            value=session.session_id,
            httponly=True,
            secure=IS_PRODUCTION,
            samesite="lax",
            max_age=86400,
            path="/"  # Explicitly set path
        )
        response.delete_cookie("oauth_state", path="/")
        
        return response
        
    except Exception as e:
        print(f"❌ Error during callback: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        error_url = f"{config.redirect_frontend_uri}?error=auth_failed"
        return RedirectResponse(url=error_url)

@app.post("/auth/logout")
async def logout(
    session_id: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None),
    x_session_token: Optional[str] = Header(None)
):
    """Logout - clear session and cookie."""
    # Find session token from any source
    token = None
    if session_id:
        token = session_id
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    elif x_session_token:
        token = x_session_token
    
    if token and token in sessions:
        del sessions[token]
        print(f"🚪 Session {token[:10]}... deleted")
    
    response = JSONResponse({"success": True, "message": "Logged out successfully"})
    response.delete_cookie("session_id", path="/")
    return response

@app.get("/auth/me")
async def get_current_user(
    session_id: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None),
    x_session_token: Optional[str] = Header(None)
):
    """Get current user info if authenticated.
    Supports cookie, Authorization header, and X-Session-Token header."""
    
    print(f"🔍 Checking authentication - Cookie: {bool(session_id)}, Auth Header: {bool(authorization)}, X-Session-Token: {bool(x_session_token)}")
    
    user_info = get_session_from_request(session_id, authorization, x_session_token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return user_info

@app.post("/ask", response_model=QueryResponse)
async def ask_agent(
    request: QueryRequest,
    session_id: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None),
    x_session_token: Optional[str] = Header(None)
):
    """Protected endpoint to interact with the agent.
    Supports cookie, Authorization header, and X-Session-Token header."""
    
    user_info = get_session_from_request(session_id, authorization, x_session_token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    print(f"💬 Query from user: {user_info.get('email', 'Unknown')} - {user_info.get('name', 'Unknown')}")
    print(f"❓ Query: {request.query}")
    
    response_data = await run_agent_async(request.query)
    answer = response_data.answer if hasattr(response_data, 'answer') else str(response_data)
    
    return {"answer": answer}

@app.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok", 
        "message": "Agentic RAG API is running",
        "active_sessions": len(sessions)
    }

@app.get("/debug/sessions")
async def debug_sessions():
    """Debug endpoint to check active sessions (remove in production)"""
    if not IS_PRODUCTION:
        return {
            "active_sessions": len(sessions),
            "sessions": [
                {
                    "id": sid[:10] + "...",
                    "email": s.user_info.get('email'),
                    "expires_at": s.expires_at.isoformat()
                }
                for sid, s in sessions.items()
            ]
        }
    return {"message": "Debug endpoint disabled in production"}

# --- Main Execution ---
if __name__ == "__main__":
    import uvicorn
    print("🔥 Starting Agentic RAG API Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)