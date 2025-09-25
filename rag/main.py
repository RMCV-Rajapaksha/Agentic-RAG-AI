import asyncio
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config.config import get_config
from src.agent.agent import run_agent_async
import os


config = get_config()
os.environ["OPENAI_API_KEY"] = config.openai_api_key


app = FastAPI(title="Agentic RAG API", description="FastAPI server for Agentic RAG system", version="1.0.0")

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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
async def ask_agent(request: QueryRequest):
    """
    Endpoint to query the Agentic RAG system.
    Example payload:
    {
      "query": "What are the AI-based products in WSO2?"
    }
    """
    response = await run_agent_async(request.query)

    if hasattr(response, 'answer'):
        result = {
            "answer": response.answer
        }
    else:
        result = {
            "answer": str(response)
        }

    return result


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Agentic RAG API is running "}


# uvicorn main:app --reload

#  curl -X POST "http://127.0.0.1:8000/ask"      -H "Content-Type: application/json"      -d '{"query": "What are the AI-based products in WSO2?"}'

if __name__ == "__main__":
    import uvicorn
    print("🔥 Starting Agentic RAG API Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
