import uvicorn
import chromadb
import os
import time
import importlib
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# Dynamically import google.generativeai to avoid static import errors
try:
    genai = importlib.import_module("google.generativeai")
except ImportError:
    class _GenAIShim:
        def configure(self, *args, **kwargs):
            raise RuntimeError(
                "google.generativeai is not installed; install it with "
                "'pip install google-generative-ai' and set GOOGLE_API_KEY."
            )
        class GenerativeModel:
            def __init__(self, *args, **kwargs):
                raise RuntimeError(
                    "google.generativeai is not installed; install it with "
                    "'pip install google-generative-ai' and set GOOGLE_API_KEY."
                )
    genai = _GenAIShim()

# --- 1. Model and Database Setup (Global) ---
try:
    embedding_model = SentenceTransformer('BAAI/bge-base-en-v1.5')
    
    # Configure the Gemini client
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    
    generation_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash" # Use this updated model
    )

    # Connect to the persistent ChromaDB
    # When running in Docker, connect to the chroma service
    # When running locally, use the local path
    try:
        # Try to connect to Docker service first
        client = chromadb.HttpClient(host="chroma", port=8000)
        collection = client.get_collection(name="shakespeare_collection")
        print("Connected to ChromaDB service in Docker")
    except Exception:
        # Fallback to local persistent client
        db_path = "./chroma_db"
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(name="shakespeare_collection")
        print("Connected to local ChromaDB")
    
    print("Embedding model, DB, and Gemini model loaded successfully.")
except Exception as e:
    print(f"Error loading models or DB: {e}")

# --- 2. System Prompt (Phase 4) ---
SYSTEM_PROMPT_TEMPLATE = """
You are an Expert Shakespearean Scholar. Your persona is academic, insightful, and clear.
Your target audience is an ICSE Class 10 student.

You MUST follow these rules:
1.  **Answer Only from Context:** You must ONLY use the provided text (CONTEXT) to answer the question. Do not use any outside knowledge.
2.  **Cite Evidence:** You must support your answer by citing the textual evidence from the context.
3.  **Stay in Persona:** Your tone should be that of a knowledgeable and helpful scholar.
4.  **Handle "I don't know":** If the answer is not in the provided CONTEXT, state that the provided text does not contain that information.

Here is the user's question and the context retrieved from "The Tragedy of Julius Caesar":

**Question:**
{question}

**CONTEXT:**
---
{context}
---

Based only on this context, provide your scholarly answer.
"""

# --- 3. FastAPI Application ---
app = FastAPI(title="Shakespearean RAG API (Gemini)")

class QueryRequest(BaseModel):
    query: str

class Source(BaseModel):
    chunk: str
    metadata: dict

class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]

@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    
    # 1. Embed the query
    query_embedding = embedding_model.encode([request.query])[0]

    # 2. Retrieve top-k chunks
    k = 3
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=k
    )

    # 3. Format context and sources
    retrieved_chunks = results['documents'][0]
    retrieved_metadatas = results['metadatas'][0]
    context_string = "\n\n---\n\n".join(retrieved_chunks)
    sources_list = []
    for i in range(len(retrieved_chunks)):
        sources_list.append(Source(
            chunk=retrieved_chunks[i],
            metadata=retrieved_metadatas[i]
        ))

    # 4. Generate the answer
    try:
        prompt_with_context = SYSTEM_PROMPT_TEMPLATE.format(
            question=request.query,
            context=context_string
        )
        response = generation_model.generate_content(prompt_with_context)
        final_answer = response.text
    except Exception as e:
        print(f"Error during Gemini generation: {e}")
        final_answer = "Error: Could not generate an answer."

    # 5. Return the final structured response
    return QueryResponse(
        answer=final_answer,
        sources=sources_list
    )

@app.get("/")
def health_check():
    """Health check endpoint to ensure the server is running."""
    return {"status": "ok", "message": "Shakespeare RAG API (Gemini) is running."}

# --- 6. Run the App ---
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)