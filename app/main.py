import uvicorn
import chromadb
import os
import time
import importlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    
    # Configure the Gemini client (optional - will work without it)
    api_key = os.getenv("GOOGLE_API_KEY")
    generation_model = None
    
    if api_key and api_key != "AIzaSyAEfEs0RuZoNYLqcIK7YH3FcMsm0AS_e70":  # Skip leaked key
        try:
            genai.configure(api_key=api_key)
            generation_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            print("Gemini model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load Gemini model: {e}")
            print("System will work without LLM generation")

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
You are a helpful assistant answering questions about Julius Caesar.

Rules:
1. Answer ONLY from the provided context
2. Keep answers SHORT and CLEAR (2-3 sentences max)
3. Be direct and concise
4. If the answer isn't in the context, say "I don't know"

Question: {question}

Context:
{context}

Answer briefly:"""

# --- 3. FastAPI Application ---
app = FastAPI(title="Shakespearean RAG API (Gemini)")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    if generation_model:
        try:
            prompt_with_context = SYSTEM_PROMPT_TEMPLATE.format(
                question=request.query,
                context=context_string
            )
            response = generation_model.generate_content(prompt_with_context)
            final_answer = response.text
        except Exception as e:
            print(f"Error during Gemini generation: {e}")
            final_answer = f"Based on the sources, here are the relevant passages about your question."
    else:
        # No LLM available - just return a summary of sources
        final_answer = f"Found {len(retrieved_chunks)} relevant passages. Check the sources below for details."

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