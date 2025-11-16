#!/usr/bin/env python3

import os
from fastapi import FastAPI
from pydantic import BaseModel

# Simple test API without heavy models
app = FastAPI(title="Test API")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list

@app.get("/")
def health_check():
    """Health check endpoint to ensure the server is running."""
    return {
        "status": "ok", 
        "message": "Test API is running.",
        "google_api_key": "Set" if os.getenv("GOOGLE_API_KEY") else "Not set"
    }

@app.post("/query")
def query_test(request: QueryRequest):
    """Test query endpoint."""
    return QueryResponse(
        answer=f"Test response for query: {request.query}",
        sources=[]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)