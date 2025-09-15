import asyncio
import json
from fastapi import FastAPI
from pydantic import BaseModel
from src.agent.agent import run_agent_async

app = FastAPI(title="Agentic RAG API", description="FastAPI server for Agentic RAG system", version="1.0.0")



class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    url: list[str]


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

    if hasattr(response, 'answer') and hasattr(response, 'url'):
        result = {
            "answer": response.answer,
            "url": response.url
        }
    else:
        result = {
            "answer": str(response),
            "url": []
        }

    return result


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Agentic RAG API is running "}


# uvicorn main:app --reload